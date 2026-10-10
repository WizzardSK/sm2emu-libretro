// SPDX-License-Identifier: BSD-3-Clause
// External native reference probe; see scripts/compare-sound-timing.py.
#include "hw/model2_sound.h"
#include "rom/game_db.h"
#include "rom/rom_loader.h"
#include <array>
#include <cstdio>
#include <vector>
using namespace sm2;
int main(int argc, char** argv) {
    std::vector<u8> rom(512,0);
    const std::array<u8,8> vectors{0,7,255,0,0,96,1,0};
    const std::array<u8,8> loop{0x30,0x39,0,0,0x10,0,0x60,0xf8};
    std::copy(vectors.begin(),vectors.end(),rom.begin());
    std::copy(loop.begin(),loop.end(),rom.begin()+256);
    std::vector<u8> samples_rom;
    if(argc==4) {
        rom::GameDatabase db; if(!db.load(argv[1]))return 2;
        const auto loaded=rom::RomLoader::load(db,argv[2],argv[3]);
        if(!loaded)return 3;
        const auto code=loaded->roms.region("audiocpu");
        const auto data=loaded->roms.region("samples");
        rom.assign(code.begin(),code.end()); samples_rom.assign(data.begin(),data.end());
    }
    hw::Model2Sound board; board.attach(rom,samples_rom); board.reset();
    board.configure_balance(argc==4 ? argv[3] : "hotd");
    u64 samples=0, pcm=0; unsigned max_voices=0;
    for (unsigned block=0;block<1000;++block) {
        if(block==100 && argc==1) {
            board.write16(0x100400, 0x000f);
            for(unsigned i=0;i<256;++i)
                board.scsp_write_word(0x4000+i*2,static_cast<u16>((int(i%64)-32)*64));
            for(unsigned slot=0;slot<8;++slot) {
                board.write16(0x100006+slot*32,0xffff); // Long sample end.
                board.write16(0x100002+slot*32,0x4000);
                board.write16(0x10000e + slot*32,0xa000);
                board.write16(0x100012+slot*32,0x0040);
                board.write16(0x100016+slot*32,0xe000);
                board.write16(0x100008+slot*32,0x001f); // Fast attack.
                board.write16(0x100000+slot*32,0x1820); // Key on / execute.
            }
        }
        board.run(25000);
        max_voices=std::max(max_voices,board.active_voices());
        samples+=board.pending_samples().size()/2;
        for(const auto v:board.pending_samples())pcm=pcm*31+static_cast<u16>(v);
        board.clear_pending_samples();
        if(block%100==99)std::printf("%u %llu %llu %u %llu %s\n",block,
            static_cast<unsigned long long>(samples),static_cast<unsigned long long>(board.cpu().cycles()),
            board.active_voices(),static_cast<unsigned long long>(pcm),board.cpu().state_string().c_str());
    }
    return max_voices || argc==4 ? 0 : 1;
}
