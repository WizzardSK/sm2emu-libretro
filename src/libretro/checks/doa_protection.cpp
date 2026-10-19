// SPDX-License-Identifier: BSD-3-Clause
#include "core/archive.h"
#include "core/log.h"
#include "hw/sega_315_5838_comp.h"
#include "hw/model2.h"
#include "hw/model2b.h"
#include "hw/machine_factory.h"
#include "hw/sound_board.h"
#include "rom/game_db.h"
#include "rom/rom_loader.h"
#include <array>
#include <cstdio>
#include <stdexcept>
#include <vector>

using namespace sm2;
using hw::Sega3155838Comp;
namespace {
void check(bool okay, const char* text) { if (!okay) throw std::runtime_error(text); }

void tables(Sega3155838Comp& chip)
{
    chip.table_w(0, 0);
    for (unsigned i = 0; i < 12; ++i) {
        chip.table_w(1, 0x0800);
        chip.table_w(1, 0);
    }
    chip.table_w(0, 0x80);
    for (unsigned i = 0; i < 256; i += 2) chip.table_w(1, u16((i << 8) | (i + 1)));
}

std::vector<u8> save(Sega3155838Comp& chip)
{
    std::vector<u8> out;
    Archive ar(out); chip.serialize(ar); return out;
}

void restore(Sega3155838Comp& chip, const std::vector<u8>& state)
{
    Archive ar(state.data(), state.size()); chip.serialize(ar);
    check(!ar.failed(), "Complete decoder state loads");
}

template<class Machine> void bus(rom::Board board, const std::array<u16,65536>& inverse)
{
    rom::GameSpec game;
    game.name = "doa"; game.board = board;
    game.protection = rom::Protection::Sega315_5838_Doa;
    rom::RomSet roms; roms.add("maincpu", std::vector<u8>(0x200000));
    Machine machine; check(machine.init(game, std::move(roms)), "DOA board initializes");
    constexpr u32 base = 0x01d80000;
    machine.write16(base, inverse[0x4142]);
    machine.write16(base + 2, inverse[0x4344]);
    machine.write32(base + 0x7ff4, 0x08000000); // mode low, first tree word high
    for (unsigned i = 1; i < 24; ++i) machine.write16(base + 0x7ff6, i % 2 ? 0 : 0x0800);
    machine.write16(base + 0x7ff4, 0x80);
    for (unsigned i = 0; i < 256; i += 2) machine.write16(base + 0x7ff6, u16((i << 8) | (i + 1)));
    machine.write16(base + 0x7ff0, 0);
    machine.write16(base + 0x7ff2, 0);
    check(machine.read32(base + 0x7ff8) == 0x41420000, "Dummy and first result use little-endian bus order");
    check(machine.read16(base + 0x7ffa) == 0x4344, "Output halfword mirror advances once");
    machine.write8(base + 0x7ff0, 1);
    check(machine.read16(base + 0x7ff8) == 0, "Byte source write rearms dummy");
    check(machine.read8(base + 0x7ff9) == 0x43, "High byte lane consumes one result");
    machine.write32(base + 0x7ff8, 0x12345678);
    machine.write32(base + 0x400c, 0x89abcdef);
    // These RAM writes do not change the decoder or its busy-status behavior.
    check(machine.read32(base + 0x400c) != machine.read32(base + 0x400c), "Busy status remains MAME-compatible");
}

void units()
{
    std::array<u16,65536> inverse{};
    std::array<bool,65536> seen{};
    u64 hash = 14695981039346656037ull;
    for (u32 n = 0; n < 65536; ++n) {
        const u16 v = Sega3155838Comp::decipher(u16(n));
        check(!seen[v], "Cipher is bijective"); seen[v] = true; inverse[v] = u16(n);
        hash = (hash ^ (v & 255u)) * 1099511628211ull;
        hash = (hash ^ (v >> 8)) * 1099511628211ull;
    }
    // Exhaustive output from pinned, separately compiled MAME decipher().
    check(hash == 0x2e38dbdf597a9525ull, "All 65536 transforms match MAME reference");
    Sega3155838Comp chip;
    unsigned calls = 0; u32 last = 0;
    chip.set_read_callback([&](u32 source) { ++calls; last = source; return inverse[0x4142]; });
    check(chip.data_r() == 0xffff && calls == 0, "Unconfigured tables do not read source");
    chip.table_w(0, 0); chip.table_w(1, 0x0800);
    const auto upload = save(chip);
    tables(chip); restore(chip, upload);
    check(chip.data_r() == 0xffff, "Mid-upload state preserves incomplete tables");
    tables(chip);
    chip.doa_write(0, 0xff, 1); chip.doa_write(1, 0xab, 1); chip.doa_write(2, 0x72, 1);
    check(chip.doa_read(0, 2) == 0 && calls == 0, "Initial bus read does not decode");
    const auto mid = save(chip);
    check(chip.data_r() == 0x4142 && last == 0x72abff, "Partial source writes merge and decode");
    restore(chip, mid); check(chip.data_r() == 0x4142, "Restored source produces same result");
    chip.source_w(0x7fffff); check(chip.data_r() == 0x4142 && last == 0x7fffff, "Last source word reads");
    check(chip.data_r() == 0x4142 && last == 0, "Source wraps at 23 bits");
    // One-bit alphabet leaves fourteen buffered bits after a pair of outputs.
    chip.table_w(0, 0);
    for (unsigned i = 0; i < 12; ++i) { chip.table_w(1, 0x0100); chip.table_w(1, 0); }
    chip.source_w(0); check(chip.data_r() == 1, "One-bit tree decodes");
    const auto buffered = save(chip); const u16 next = chip.data_r();
    restore(chip, buffered); check(chip.data_r() == next, "Buffered bits survive save/load");
    auto corrupt = buffered; corrupt[314] = 17; // buffered bit count
    Archive bad(corrupt.data(), corrupt.size()); chip.serialize(bad);
    check(bad.failed(), "Invalid buffered-bit count is rejected");
    tables(chip); chip.table_w(0, 0);
    for (unsigned i = 0; i < 24; ++i) chip.table_w(1, 0);
    chip.source_w(0); check(chip.data_r() == 0xffff, "Invalid code terminates safely");
    chip.reset(); check(chip.data_r() == 0xffff, "Reset clears uploaded tables");
    bus<hw::Model2>(rom::Board::Model2A, inverse);
    bus<hw::Model2B>(rom::Board::Model2B, inverse);
    std::puts("DOA cipher, upload, bus, bounds and state checks passed");
}
} // namespace

int main(int argc, char** argv)
{
    if (argc == 3) {
        rom::GameDatabase db; check(db.load(argv[1]), "Database loads");
        auto loaded = rom::RomLoader::load(db, argv[2]); check(bool(loaded), "ROM loads");
        auto machine = hw::create_machine(loaded->game, std::move(loaded->roms));
        check(bool(machine), "Native DOA machine initializes");
        log::set_level(log::Level::Debug);
        machine->reset();
        for (unsigned i = 0; i < 600; ++i) {
            machine->run_frame(); machine->sound_board().clear_pending_samples();
        }
        std::puts("Native DOA boot trace complete");
    } else units();
}
