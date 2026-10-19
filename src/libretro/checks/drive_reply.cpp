// SPDX-License-Identifier: BSD-3-Clause
#include "hw/indy_drive_reply.h"
#include "hw/model2b.h"
#include "hw/model2c.h"

#include <cstdio>
#include <stdexcept>
#include <vector>

using namespace sm2;

namespace {
void check(bool okay, const char* what)
{
    if (!okay) throw std::runtime_error(what);
}

template <typename Machine>
void check_machine(rom::Board board)
{
    rom::GameSpec game;
    game.name = "drive-reply-check";
    game.title = game.name;
    game.board = board;
    game.drive_board = true;
    game.drive_protocol = rom::DriveProtocol::Indy;
    game.analog[0].control = rom::AnalogControl::Steer;
    rom::RomSet roms;
    roms.add("maincpu", std::vector<u8>(0x200000));
    Machine machine;
    check(machine.init(game, std::move(roms)), "machine initializes");

    constexpr u32 io = 0x01c00000;
    machine.write8(io + 0x10, 0x08); // port D input, port E output
    const auto reply = [&](u8 command) {
        machine.write8(io + 0x08, command);
        return machine.read8(io + 0x06);
    };
    machine.inputs().analog[0] = 0x42;
    check(reply(0x80) == 0x42 && reply(0x83) == 0x42, "wheel ADC reply");
    check(reply(0x81) == 0xff && reply(0x82) == 0xff, "board status and DIP reply");
    check(reply(0x55) == 0x55, "unknown command echo");
    reply(0x9a);
    reply(0xc5);
    check(reply(0x84) == 0xa5, "calibrated centre reply");

    std::vector<u8> saved;
    check(machine.save_state(saved), "save drive-board centre");
    reply(0x91);
    reply(0xc2);
    check(reply(0x84) == 0x12, "centre changes after save");
    check(machine.load_state(saved.data(), saved.size()), "restore drive-board centre");
    check(machine.read8(io + 0x06) == 0xa5, "saved centre and command restored");

    // Legacy board loading is covered with genuine pre-change state images
    // in the ABI campaign. Relabelling a current image as v11 is invalid now
    // that the v14 protection payload has a different size on Model 2B.

}
} // namespace

int main()
{
    check_machine<hw::Model2B>(rom::Board::Model2B);
    check_machine<hw::Model2C>(rom::Board::Model2C);
    hw::IndyDriveReply reply;
    reply.write(0x9f);
    reply.write(0xcf);
    reply.write(0x84);
    check(reply.read(0x80) == 0x80, "invalid historic centre is neutralized");
    std::puts("Indy drive-board replies and state checks passed");
}
