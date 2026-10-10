// SPDX-License-Identifier: BSD-3-Clause
// Synthetic 68000 code and sound-board clock checks; no game ROMs required.
#include "core/archive.h"
#include "cpu/m68000/m68000.h"
#include "hw/model2_sound.h"
#include "hw/save_state_io.h"
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>

using namespace sm2;
namespace {
void check(bool okay, const char* message)
{
    if (!okay) throw std::runtime_error(message);
}
struct Memory final : cpu::Bus {
    std::array<u8, 8192> bytes{};
    cpu::m68000::M68000* cpu = nullptr;
    unsigned wait = 0, reads = 0;
    u8 read8(u32 a) override { return bytes[a % bytes.size()]; }
    u16 read16(u32 a) override {
        if (a == 0x1000) { ++reads; cpu->stall(static_cast<s32>(wait)); }
        return static_cast<u16>((read8(a) << 8) | read8(a + 1));
    }
    u32 read32(u32 a) override { return (u32(read16(a)) << 16) | read16(a + 2); }
    void write8(u32 a, u8 v) override { bytes[a % bytes.size()] = v; }
    void write16(u32 a, u16 v) override { write8(a, u8(v >> 8)); write8(a+1, u8(v)); }
    void write32(u32 a, u32 v) override { write16(a, u16(v >> 16)); write16(a+2, u16(v)); }
};
std::vector<u8> program()
{
    std::vector<u8> rom(512, 0);
    const std::array<u8, 8> vectors{0x00,0x07,0xff,0x00, 0x00,0x60,0x01,0x00};
    std::copy(vectors.begin(), vectors.end(), rom.begin());
    // MOVE.W $1000,D0; BRA.S back to MOVE.W.
    const std::array<u8, 8> loop{0x30,0x39,0x00,0x00,0x10,0x00,0x60,0xf8};
    std::copy(loop.begin(), loop.end(), rom.begin()+256);
    return rom;
}
template<class T> T tail(const std::vector<u8>& data, usize from_end)
{
    T value{}; std::memcpy(&value, data.data()+data.size()-from_end, sizeof(value));
    return value;
}
}
int main()
{
    try {
        Memory memory;
        cpu::m68000::M68000 cpu(memory); memory.cpu = &cpu;
        memory.write32(0, 0x1f00); memory.write32(4, 0x100);
        const auto rom = program();
        std::copy(rom.begin()+256, rom.end(), memory.bytes.begin()+256);
        cpu.reset(); cpu.stall(100); check(cpu.cycles()==0, "Out-of-run stall must be inert");
        cpu.run(128); memory.reads=0;  // Consume Musashi's reset exception first.
        const auto used_fast = cpu.run(4096); const auto reads_fast = memory.reads;
        cpu.reset(); cpu.run(128); memory.reads=0; memory.wait=12;
        const auto base_cycles = cpu.cycles();
        const auto used_slow = cpu.run(4096);
        std::printf("Synthetic CPU: fast=%d slow=%d reads=%u/%u\n", used_fast, used_slow, reads_fast, memory.reads);
        check(used_fast >= 4096 && used_slow >= 4096 && used_slow < 4150,
              "Consumed cycles include bus stalls after execute returns");
        check(memory.reads > 0 && memory.reads < reads_fast,
              "Bus contention reduces completed instructions");
        check(cpu.cycles()==base_cycles+u64(used_slow), "Cycle counter includes waits");

        hw::Model2Sound sound; sound.attach(rom, {}); sound.reset();
        u64 frames=0;
        for (unsigned i=0; i<1000; ++i) {
            sound.run(25'000); frames += sound.pending_samples().size()/2;
            sound.clear_pending_samples();
        }
        check(frames >= 44'100 && frames <= 44'101, "SCSP sample clock is crystal locked");
        check(sound.cpu().cycles() >= 11'289'600 && sound.cpu().cycles() < 11'289'700,
              "Sound CPU retains full crystal clock including bus waits");
        sound.write16(0x100000, 0x1800);
        check(sound.active_voices()==1, "Key-on updates cached contention slots");
        std::vector<u8> saved; Archive save(saved); sound.serialize(save);
        sound.reset(); check(sound.active_voices()==0, "Reset clears contention slots");
        Archive load(saved.data(), saved.size()); sound.serialize(load);
        check(!load.failed() && sound.active_voices()==1, "Load rebuilds contention slots");

        // A version-4 tail has three u64 fields: half-rate carry, overshoot, sample carry.
        saved.clear();
        Archive legacy_save(saved, 5); sound.serialize(legacy_save);
        const std::array<u64,3> legacy{15'624,3,125'000};
        std::memcpy(saved.data()+saved.size()-sizeof(legacy), legacy.data(), sizeof(legacy));
        Archive old(saved.data(), saved.size(), 4); sound.serialize(old);
        check(!old.failed(), "Published version-4 sound state loads");
        std::vector<u8> converted; Archive again(converted,6); sound.serialize(again);
        check(converted.size()==saved.size()+16, "Legacy SCSP history adds exactly 16 bytes");
        check(tail<u64>(converted,24)==15'623 && tail<s64>(converted,16)==-5
                  && tail<u64>(converted,8)==128, "Legacy carries convert to new scheduler units");
        const auto serialize = [&](Archive& ar) { sound.serialize(ar); };
        std::vector<u8> image;
        check(hw::save_state_to_buffer(image,"fixture",1,false,serialize), "Current-format state saves");
        state::Header header; usize offset=0;
        check(state::read_header(image.data(),image.size(),header,offset) && header.version==state::kFormatVersion,
              "New state format is distinguishable to older binaries");
        std::vector<u8> before; Archive before_ar(before); sound.serialize(before_ar);
        check(image.back()==0,"Fixture has no auxiliary sound board");
        const u64 invalid_phase=1'000'001;
        std::memcpy(image.data()+image.size()-9,&invalid_phase,8);
        check(!hw::load_state_from_buffer(image.data(),image.size(),"fixture",1,false,serialize),
              "Invalid scheduler phase rejects and rolls back");
        std::vector<u8> after; Archive after_ar(after); sound.serialize(after_ar);
        check(after==before, "Rejected state leaves machine untouched");
        std::puts("Sound timing checks passed"); return 0;
    } catch (const std::exception& e) {
        std::fprintf(stderr,"Sound timing check failed: %s\n",e.what()); return 1;
    }
}
