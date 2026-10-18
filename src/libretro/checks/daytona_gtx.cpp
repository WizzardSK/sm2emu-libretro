// SPDX-License-Identifier: BSD-3-Clause
#include "hw/model2_original.h"
#include "rom/game_db.h"
#include <cstdio>
#include <stdexcept>
#include <vector>
using namespace sm2;
namespace {
void check(bool ok, const char* message) { if (!ok) throw std::runtime_error(message); }
rom::RomSet fixture() {
    rom::RomSet roms;
    roms.add("maincpu", std::vector<u8>(0x200000, 0));
    roms.add("main_data", std::vector<u8>(0x2000000, 0x55));
    std::vector<u8> banks(0x300000, 0xff);
    for (unsigned i=0; i<0x100000; ++i) {
        banks[i] = static_cast<u8>(i);
        banks[0x100000+i] = static_cast<u8>(i ^ 0x80);
    }
    roms.add("prot_data", std::move(banks));
    return roms;
}
}
int main() {
    try {
        rom::GameDatabase db;
        check(db.load(SM2_GTX_GAME_DB), "GTX catalog parses");
        const auto* game = db.find("daytonagtx");
        check(game && game->parent == "daytona" && game->protection == rom::Protection::DaytonaGtx,
              "GTX catalog identity and protection");
        check(game->analog[0].control == db.find("daytona")->analog[0].control
                  && game->analog[1].control == db.find("daytona")->analog[1].control
                  && game->analog[2].control == db.find("daytona")->analog[2].control, "GTX inherits native Daytona I/O");
        hw::Model2Original machine;
        check(machine.init(*game, fixture()), "GTX machine initializes");
        machine.reset();
        constexpr u32 base=0x02c00000;
        check(machine.read8(base+0x42)==0x42, "Initial bank zero");
        check(machine.read8(base+0xff000)==0x80, "Bank one trigger returns new bank byte");
        check(machine.read16(base+0x42)==0xc3c2, "Halfword uses current bank");
        check(machine.read32_flags(base+0x42)==std::pair<u32,u16>{0xc5c4c3c2,cpu::kBusFlagBurst},
              "Burst dword uses current bank");
        std::vector<u8> saved;
        check(machine.save_state(saved), "GTX state captures bank one");
        machine.read32(base+0xffffc);
        check(machine.read8(base+0x42)==0xff, "Disabled overlay is erased bank two");
        check(machine.load_state(saved.data(), saved.size()), "GTX state restores");
        check(machine.read8(base+0x42)==0xc2, "GTX state restores bank selection");
        check(machine.read32(base+0xff00c)==0x0f0e0d0c, "Dword bank zero trigger");
        machine.read8(base+0xff000);
        check(machine.fetch32(base+0xf0000)==0x03828180, "Byte-lane three trigger preserves earlier lanes");
        check(machine.read8_flags(base+0x42)==std::pair<u8,u16>{0x42,cpu::kBusFlagBurst},
              "Flagged byte reads preserve bank and burst semantics");
        machine.read8(base+0xff000); machine.reset();
        check(machine.read8(base+0x42)==0x42, "Reset returns initial bank");
        for (const char* name : {"daytona", "daytonam"}) {
            check(machine.init(*db.find(name), fixture()), "Existing Daytona variant initializes");
            machine.reset(); machine.read8(base+0xff000);
            check(machine.read32(base+0x42)==0x55555555, "GTX overlay does not affect Daytona/MAXX data");
            check(machine.save_state(saved) && machine.load_state(saved.data(), saved.size()), "Existing Daytona state round trip");
        }
        std::puts("Daytona GTX protection/catalog/state checks passed");
        return 0;
    } catch (const std::exception& e) { std::fprintf(stderr,"%s\n",e.what()); return 1; }
}
