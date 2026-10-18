// SPDX-License-Identifier: BSD-3-Clause
#include "hw/model2b.h"
#include <cstdio>
#include <stdexcept>
#include <vector>

using namespace sm2;

namespace {
void check(bool okay, const char* what)
{
    if (!okay) throw std::runtime_error(what);
}

u8 pedal(hw::Model2B& machine, u32 channel, u8 raw)
{
    machine.inputs().analog[channel] = raw;
    constexpr u32 kAnalogMux = 0x01c0001e;
    machine.write8(kAnalogMux, static_cast<u8>(channel));
    return machine.read8(kAnalogMux);
}
} // namespace

int main()
{
    rom::GameSpec game;
    game.name = "sgt24h";
    game.title = "Super GT 24h pedal I/O check";
    game.board = rom::Board::Model2B;
    game.analog[0].control = rom::AnalogControl::Steer;
    game.analog[1].control = rom::AnalogControl::Accel;
    game.analog[2].control = rom::AnalogControl::Brake;
    rom::RomSet roms;
    roms.add("maincpu", std::vector<u8>(0x200000));
    hw::Model2B machine;
    check(machine.init(game, std::move(roms)), "Model 2B initializes");

    auto nvram = machine.backup_ram();
    machine.load_nvram();
    check(nvram[0x0a] == 1 && nvram[0x0b] == 0,
          "Uninitialized I/O TYPE repairs to native A");
    nvram[0] = 0x85;
    nvram[1] = 0xad;
    for (u16 type : {u16{1}, u16{3}, u16{0}}) {
        nvram[0x0a] = static_cast<u8>(type);
        nvram[0x0b] = static_cast<u8>(type >> 8);
        const bool c = type == 0;
        for (u32 channel : {1u, 2u}) {
            check(pedal(machine, channel, 0xff) == (c ? 0xff : 0x01),
                  "Pressed pedal follows native I/O TYPE polarity");
            check(pedal(machine, channel, 0x80) == (c ? 0x80 : 0x7f),
                  "Half pedal follows native I/O TYPE polarity");
            check(pedal(machine, channel, 0x00) == (c ? 0x00 : 0xff),
                  "Released pedal follows native I/O TYPE polarity");
        }
    }
    check(pedal(machine, 0, 0x42) == 0x42,
          "Unrelated analogue channels preserve their raw value");

    game.name = "indy500";
    game.title = "Other Model 2B pedal check";
    rom::RomSet other_roms;
    other_roms.add("maincpu", std::vector<u8>(0x200000));
    hw::Model2B other;
    check(other.init(game, std::move(other_roms)), "Other Model 2B game initializes");
    check(pedal(other, 1, 0x00) == 0x00 && pedal(other, 2, 0x80) == 0x80,
          "Other Model 2B pedals retain their existing I/O bytes");
    std::puts("Super GT 24h native A/B/C pedal I/O checks passed");
}
