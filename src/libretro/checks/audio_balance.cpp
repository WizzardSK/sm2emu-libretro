// SPDX-License-Identifier: BSD-3-Clause
#include "hw/model2_sound.h"
#include "hw/m1audio.h"
#include "core/archive.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <vector>
using namespace sm2;
namespace {
void check(bool okay,const char* text) {if(!okay)throw std::runtime_error(text);}
std::vector<u8> idle_program() {
    std::vector<u8> rom(512);rom[1]=7;rom[2]=0xff;rom[3]=0;
    rom[6]=1;rom[256]=0x60;rom[257]=0xfe;return rom;
}
double energy(const std::vector<s16>& values) {
    double sum=0;for(s16 value:values)sum+=double(value)*value;return sum;
}
std::vector<s16> scsp(const char* game,bool balance,bool automatic,unsigned percent) {
    const auto rom=idle_program();hw::Model2Sound board;board.attach(rom,{});board.reset();
    board.configure_balance(game);board.set_audio_balance_enabled(balance);
    board.set_audio_source_gain(hw::AudioSource::Scsp,percent,automatic);
    for(unsigned i=0;i<256;++i)board.scsp_write_word(0x4000+i*2,u16(s16(500*std::sin(2*3.141592653589793*i/64))));
    board.write16(0x100400,15);board.write16(0x100002,0x4000);board.write16(0x100006,256);
    board.write16(0x100008,31);board.write16(0x100016,0xe000);board.write16(0x100000,0x1820);
    board.run(100000);const auto samples=board.pending_samples();
    return {samples.begin(),samples.end()};
}
std::vector<s16> dual_scsp(unsigned rider_gain, unsigned relay_gain) {
    const auto rom = idle_program();
    hw::Model2Sound board;
    board.attach(rom, {}); board.attach_auxiliary_scsp(rom, {}); board.reset();
    board.set_audio_source_gain(hw::AudioSource::Scsp, rider_gain, false);
    board.auxiliary_scsp()->set_audio_source_gain(hw::AudioSource::Scsp, relay_gain, false);
    for (auto* source : {&board, board.auxiliary_scsp()}) {
        for (unsigned i = 0; i < 256; ++i)
            source->scsp_write_word(0x4000 + i*2, u16(s16(500*std::sin(2*3.141592653589793*i/64))));
        source->write16(0x100400, 15); source->write16(0x100002, 0x4000);
        source->write16(0x100006, 256); source->write16(0x100008, 31);
        source->write16(0x100016, 0xe000); source->write16(0x100000, 0x1820);
    }
    board.run(100000);
    const auto samples = board.pending_samples();
    return {samples.begin(), samples.end()};
}
std::vector<s16> pcm(const char* game,bool balance,bool auto1,bool auto2,unsigned gain1,unsigned gain2) {
    const auto rom=idle_program();std::vector<u8> sample(0x1000);
    sample[1]=1;sample[5]=0xff;sample[6]=0;sample[8]=0xf0;
    for(unsigned i=0;i<256;++i)sample[0x100+i]=u8(s8(30*std::sin(2*3.141592653589793*i/64)));
    hw::M1Audio board;board.attach(rom,sample,sample);board.reset();board.configure_balance(game);
    board.set_audio_balance_enabled(balance);
    board.set_audio_source_gain(hw::AudioSource::MultiPcm1,gain1,auto1);
    board.set_audio_source_gain(hw::AudioSource::MultiPcm2,gain2,auto2);
    for(u32 base:{0xc40000u,0xc60000u}) {
        board.write16(base+2,0);
        auto reg=[&](unsigned index,unsigned value){board.write16(base+4,u16(index));board.write16(base,u16(value));};
        reg(0,0);reg(1,0);reg(2,0);reg(3,0);reg(5,1);reg(4,0x80);
    }
    board.run(100000);const auto samples=board.pending_samples();return {samples.begin(),samples.end()};
}
std::vector<s16> music(const std::vector<u8>& mpeg,bool balance,bool automatic,unsigned percent,unsigned volume=100) {
    const auto rom=idle_program();auto dsb_program=rom;unsigned position=256;
    const u32 end=u32(mpeg.size());
    for(u8 value:{u8(0x14),u8(0),u8(0),u8(0),u8(0x24),u8(end>>16),u8(end>>8),u8(end),u8(0x74)})
        for(u8 byte:{u8(0x13),u8(0xfc),u8(0),value,u8(0),u8(0xe0),u8(0),u8(3)})dsb_program[position++]=byte;
    dsb_program[position++]=0x60;dsb_program[position]=0xfe;
    hw::Model2Sound board;board.attach(rom,{});board.attach_dsb2(dsb_program,mpeg);
    board.reset();board.configure_balance("topskatr");board.set_audio_balance_enabled(balance);
    board.set_audio_source_gain(hw::AudioSource::Dsb,percent,automatic);board.set_music_volume_percent(volume);
    board.run(1000000);const auto samples=board.pending_samples();return {samples.begin(),samples.end()};
}
}
int main(int argc,char** argv) {
    try {
        {
            const auto rom=idle_program();hw::Model2Sound routed,native;
            routed.attach(rom,{});routed.attach_auxiliary_scsp(rom,{});routed.reset();
            native.attach(rom,{});native.reset();
            for(u8 byte:{u8(0xa0),u8(0x63),u8(3)})routed.midi_in(byte);
            for(u8 byte:{u8(0xa0),u8(0),u8(3)})native.midi_in(byte);
            std::vector<u8> actual,expected;
            Archive actual_save(actual),expected_save(expected);
            // Saving does not mutate the SCSP; the production accessor is read-only.
            const_cast<hw::Scsp&>(routed.auxiliary_scsp()->scsp()).serialize(actual_save);
            const_cast<hw::Scsp&>(native.scsp()).serialize(expected_save);
            check(actual==expected && routed.scsp().stats().midi_in_bytes==0,
                "Result stop translates exactly to native sequence control on Relay only");
        }
        {
            const auto rom=idle_program();hw::Model2Sound board;
            board.attach(rom,{});board.attach_auxiliary_scsp(rom,{});board.reset();
            for(u8 byte:{u8(0xa0),u8(0x11),u8(0x0f)})board.midi_in(byte);
            check(board.scsp().stats().midi_in_bytes==3
                && board.auxiliary_scsp()->scsp().stats().midi_in_bytes==0,
                "Rider packets stay on the primary SCSP");
            board.midi_in(0xa0); // Save midway through a tagged MIDI packet.
            std::vector<u8> state;Archive save(state);board.serialize(save);
            board.midi_in(0x61);board.midi_in(5);
            check(board.auxiliary_scsp()->scsp().stats().midi_in_bytes==3,
                "Tagged music reaches only the auxiliary SCSP");
            std::vector<u8> completed;Archive save_completed(completed);board.serialize(save_completed);
            Archive load(state.data(),state.size());board.serialize(load);
            check(!load.failed(),"Auxiliary board and partial MIDI packet restore");
            board.midi_in(0x61);board.midi_in(5);
            std::vector<u8> replayed;Archive save_replayed(replayed);board.serialize(save_replayed);
            check(board.scsp().stats().midi_in_bytes==3
                && replayed==completed,
                "Restored routing neither duplicates music nor loses rider bytes");
            const auto aux_bytes=board.auxiliary_scsp()->scsp().stats().midi_in_bytes;
            for(u8 byte:{u8(0xa0),u8(0x12),u8(0)})board.midi_in(byte);
            check(board.scsp().stats().midi_in_bytes==6
                && board.auxiliary_scsp()->scsp().stats().midi_in_bytes==aux_bytes,
                "Untagged group-12 rider cues remain on the primary board");
            board.midi_in(0xa0);board.midi_in(0x62);
            std::vector<u8> cue_state;Archive cue_save(cue_state);board.serialize(cue_save);
            board.midi_in(1);
            std::vector<u8> cue_completed;Archive cue_done(cue_completed);board.serialize(cue_done);
            Archive cue_load(cue_state.data(),cue_state.size());board.serialize(cue_load);
            board.midi_in(1);
            std::vector<u8> cue_replayed;Archive cue_again(cue_replayed);board.serialize(cue_again);
            check(!cue_load.failed() && cue_completed==cue_replayed
                && board.scsp().stats().midi_in_bytes==6
                && board.auxiliary_scsp()->scsp().stats().midi_in_bytes==aux_bytes+6,
                "Tagged countdown restores mid-packet and reaches only the Relay board");
            board.run(100000);board.clear_pending_samples();
            std::vector<u8> resumed;Archive save_again(resumed);board.serialize(save_again);
            hw::Model2Sound other;other.attach(rom,{});other.reset();
            Archive wrong(resumed.data(),resumed.size());other.serialize(wrong);
            check(wrong.failed(),"Reject auxiliary state without matching hardware");
            other.reset();std::vector<u8> legacy;Archive old_save(legacy,10);other.serialize(old_save);
            Archive old_load(legacy.data(),legacy.size(),10);other.serialize(old_load);
            check(!old_load.failed(),"Version 10 sound state remains readable without auxiliary hardware");
        }
        {
            const auto rider = dual_scsp(100, 0), relay = dual_scsp(0, 100);
            const auto mixed = dual_scsp(100, 100), half = dual_scsp(0, 50);
            check(energy(rider) > 0 && energy(relay) > 0 && energy(dual_scsp(0, 0)) == 0,
                  "Independent rider and Relay gains can mute either board without silencing the other");
            check(rider.size() == mixed.size() && relay.size() == mixed.size(), "Dual board output sizes match");
            for (size_t i = 0; i < mixed.size(); ++i)
                check(std::abs(int(mixed[i]) - int(rider[i]) - int(relay[i])) <= 1,
                      "Rider and Relay output gains remain independent in the final mix");
            check(std::abs(std::sqrt(energy(half)/energy(relay)) - 0.5) < 0.025,
                  "Relay 50 percent changes only its board output level");
        }
        for(auto [game,gain]: {std::pair{"hotd",1400}, {"vf2",840}, {"doa",500}, {"topskatr",232}, {"von",1042}}) {
            const auto raw=scsp(game,false,true,100),manual=scsp(game,true,false,100),automatic=scsp(game,true,true,100);
            check(energy(raw)>0,"SCSP fixture produces audio");
            check(raw==manual,"Manual 100% bypasses the game profile");
            check(raw==scsp(game,false,false,100),"Manual output is independent of Enhanced Audio Balance");
            const double ratio=std::sqrt(energy(automatic)/energy(raw));
            check(std::abs(ratio-double(gain)/256)<0.025,"Auto uses the upstream SCSP gain once");
            check(energy(scsp(game,true,false,0))==0,"SCSP Mute is silent");
            check(std::abs(std::sqrt(energy(scsp(game,true,false,50))/energy(raw))-0.5)<0.025,
                  "Manual SCSP 50% uses half the unprofiled level");
        }
        for(auto [game,gain]: {std::pair{"daytona",117}, {"desert",111}, {"vcop",181}}) {
            const auto raw=pcm(game,false,true,true,100,100),automatic=pcm(game,true,true,true,100,100);
            check(energy(raw)>0,"MultiPCM fixture produces audio");
            check(raw==pcm(game,true,false,false,100,100),"Manual MultiPCM 100% bypasses profile");
            check(std::abs(std::sqrt(energy(automatic)/energy(raw))-double(gain)/256)<0.025,
                  "Both MultiPCM Auto gains apply the upstream board level once");
            const auto first=pcm(game,false,false,false,100,0),mixed=pcm(game,true,true,false,100,100);
            for(size_t i=0;i<mixed.size();++i)
                check(std::abs(int(mixed[i])-((int(first[i])*gain>>8)+first[i]))<=1,
                      "Mixed Auto/manual sources retain independent levels");
            check(energy(pcm(game,true,false,false,0,0))==0,"MultiPCM Mute silences both chips");
        }
        if(argc>1) {
            std::ifstream file(argv[1],std::ios::binary);std::vector<u8> mpeg{std::istreambuf_iterator<char>(file),{}};
            check(!mpeg.empty(),"Generated MPEG tone exists");
            const auto raw=music(mpeg,false,true,100),automatic=music(mpeg,true,true,100);
            check(energy(raw)>0,"DSB2 tone produces audio");
            check(raw==music(mpeg,true,false,100),"Manual DSB 100% bypasses upstream profile");
            check(std::abs(std::sqrt(energy(automatic)/energy(raw))-0.25)<0.025,"Top Skater Auto DSB gain is 64/256");
            check(energy(music(mpeg,true,false,0))==0,"DSB Mute is silent");
            check(energy(music(mpeg,true,true,100,0))==0,"Music Volume remains authoritative with Auto");
        }
        std::puts("Audio Auto/manual balance checks passed");return 0;
    }catch(const std::exception& e){std::fprintf(stderr,"Balance check failed: %s\n",e.what());return 1;}
}
