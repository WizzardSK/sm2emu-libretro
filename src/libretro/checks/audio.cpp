// SPDX-License-Identifier: BSD-3-Clause
#include "audio_output.h"
#include "core/archive.h"
#include "hw/model2_sound.h"
#include "hw/dsb2.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <limits>
#include <vector>
using namespace sm2;
namespace {
void check(bool okay,const char* text) { if(!okay)throw std::runtime_error(text); }
void address(hw::Dsb2& board,u8 command,u32 value) {
    for(u8 byte : {command,u8(value>>16),u8(value>>8),u8(value)})board.write8(0xe00003,byte);
}
std::vector<s16> mix(hw::Dsb2& board,unsigned frames) {
    std::vector<s16> out(frames*2);board.mix(out.data(),frames,32000,100);return out;
}
}
int main() {
    try {
        for(unsigned rate : {44100u,44642u}) {
            libretro::OutputDcBlocker dc,chunked;
            std::vector<s16> signal(rate*2);
            for(unsigned i=0;i<rate;++i) {signal[i*2]=1000;signal[i*2+1]=-2000;}
            auto split=signal;dc.process(signal,rate);
            chunked.process(std::span<s16>(split).first(2048),rate);
            chunked.process(std::span<s16>(split).subspan(2048),rate);
            check(signal==split,"DC filter is independent of callback chunking");
            check(signal[0]==1000 && signal[1]==-2000,"Stereo histories are independent");
            check(std::abs(signal[signal.size()-1])<=1,"Constant DC settles to silence");
            const auto history=chunked;
            std::vector<s16> a{1200,-900,200,300},b=a;dc=history;
            dc.process(a,rate);chunked.process(b,rate);
            check(a==b,"Restored DC history continues exactly");
            dc.reset();check(dc.previous_input[0]==0 && dc.previous_output[1]==0,"Reset clears DC history");
        }
        hw::Model2Sound memory; memory.reset();
        hw::Scsp chip(memory,hw::Scsp::kDefaultClock);chip.reset();
        chip.write(0x780/2,0x1234);chip.write(0x7c0/2,0xdead);
        check(chip.read(0x780/2)==0x1234 && chip.read(0x7c0/2)==0,
              "Unmapped SCSP writes do not overwrite MADRS");
        std::vector<u8> old,current;
        Archive old_save(old,5);chip.serialize(old_save);
        Archive save(current);chip.serialize(save);
        check(current.size()==old.size()+16,"SCSP version 6 appends four history floats");
        const std::array<float,4> history{1,2,3,4};
        std::memcpy(current.data()+current.size()-16,history.data(),16);
        Archive load(current.data(),current.size());chip.serialize(load);
        std::vector<u8> restored;Archive again(restored);chip.serialize(again);
        check(restored==current,"SCSP filter history survives save/load");
        Archive legacy(old.data(),old.size(),5);chip.serialize(legacy);
        restored.clear();Archive upgraded(restored);chip.serialize(upgraded);
        const std::array<u8,16> zero{};
        check(std::equal(zero.begin(),zero.end(),restored.end()-16),"Old SCSP states initialize absent history");

        // Exercise the actual SCSP mixer, not a duplicate filter implementation.
        auto tone = [&](unsigned cycles, bool filtered, unsigned pitch_depth=0) {
            chip.reset();
            chip.set_output_low_pass_enabled(filtered);
            for (unsigned i=0;i<256;++i)
                memory.scsp_write_word(0x4000+i*2,
                    u16(s16(12000*std::sin(2*3.141592653589793*cycles*i/256))));
            chip.write(0x400/2,0x000f);
            chip.write(0x002/2,0x4000);
            chip.write(0x006/2,256);
            chip.write(0x008/2,0x001f);
            chip.write(0x012/2,u16((24<<10)|(2<<8)|(pitch_depth<<5)));
            chip.write(0x016/2,0xe000);
            chip.write(0x000/2,0x1820);
            std::vector<s16> out(4096*2);chip.generate(out.data(),4096);
            return out;
        };
        auto energy = [](const auto& samples) {
            double sum=0;
            for (size_t i=1024;i<samples.size();++i) sum+=double(samples[i])*samples[i];
            return sum;
        };
        const auto low=tone(6,false),low_filtered=tone(6,true);
        const auto high=tone(87,false),high_filtered=tone(87,true);
        check(energy(low)>0 && energy(high)>0,"SCSP test tones are audible");
        check(energy(low_filtered)>0.9*energy(low),"SCSP low-pass preserves 1 kHz tone");
        check(energy(high_filtered)<0.1*energy(high),"SCSP low-pass attenuates 15 kHz tone");
        std::vector<u8> filtered_state;Archive filter_save(filtered_state);chip.serialize(filter_save);
        std::vector<s16> continuation(2048),replay(2048);chip.generate(continuation.data(),1024);
        Archive filter_load(filtered_state.data(),filtered_state.size());chip.serialize(filter_load);
        chip.set_output_low_pass_enabled(true); // Applying the same setting must preserve history.
        chip.generate(replay.data(),1024);
        check(continuation==replay,"Enabled SCSP filter restores sample-exact continuation");
        const auto bypass=tone(87,false);
        check(bypass==high,"Disabling SCSP filter restores exact bypass output");

        const auto modulated=tone(6,false,3);
        check(modulated!=low && energy(modulated)>0,"Depth-3 pitch modulation changes audible synthesis");
        std::vector<u8> pitch_state;Archive pitch_save(pitch_state);chip.serialize(pitch_save);
        chip.generate(continuation.data(),1024);
        Archive pitch_load(pitch_state.data(),pitch_state.size());chip.serialize(pitch_load);
        chip.generate(replay.data(),1024);
        check(continuation==replay,"Pitch-LFO phase and scale pointers restore exact continuation");

        auto invalid_history=filtered_state;
        const float nan=std::numeric_limits<float>::quiet_NaN();
        std::memcpy(invalid_history.data()+invalid_history.size()-16,&nan,sizeof(nan));
        Archive invalid_load(invalid_history.data(),invalid_history.size());chip.serialize(invalid_load);
        check(invalid_load.failed(),"Non-finite SCSP filter history is rejected");

        // Zero bit allocations make valid, silent MPEG-1 Layer II frames.
        std::vector<u8> mpeg(576*4,0),program(16,0);
        for(unsigned pos=0;pos<mpeg.size();pos+=576) {
            mpeg[pos]=0xff;mpeg[pos+1]=0xfd;mpeg[pos+2]=0x88;mpeg[pos+3]=0;
        }
        hw::Dsb2 dsb;dsb.attach(program,mpeg);dsb.reset();
        address(dsb,0x14,0);address(dsb,0x24,u32(mpeg.size()));dsb.write8(0xe00003,0x74);
        mix(dsb,128);
        check(dsb.counters().mpeg_frames>0,"Synthetic MPEG stream decodes");
        address(dsb,0x14,576);address(dsb,0x24,u32(mpeg.size()));
        std::vector<u8> state;Archive saved(state);dsb.serialize(saved);
        const auto first=mix(dsb,32000);const auto decoded=dsb.counters().mpeg_frames;
        check(decoded>4,"DSB2 continues decoding after the first play window");
        Archive reload(state.data(),state.size());dsb.serialize(reload);
        check(mix(dsb,32000)==first,"DSB2 loop state and decoder restore deterministically");
        dsb.write8(0xe00003,0x84);const auto stopped=dsb.counters().mpeg_frames;
        mix(dsb,32000);check(dsb.counters().mpeg_frames==stopped,"Stop ends looping playback");
        address(dsb,0x14,u32(mpeg.size()+1));address(dsb,0x24,u32(mpeg.size()+100));
        dsb.write8(0xe00003,0x74);mix(dsb,32000);
        check(dsb.counters().mpeg_frames==stopped,"Out-of-range MPEG play window is rejected");
        std::puts("Audio synthesis/output checks passed");return 0;
    } catch(const std::exception& e) {std::fprintf(stderr,"Audio check failed: %s\n",e.what());return 1;}
}
