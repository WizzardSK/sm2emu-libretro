// SPDX-License-Identifier: BSD-3-Clause
#include "power_sled_audio.h"
#include "hw/model2_machine_base.h"
#include "hw/model2_sound.h"
#include "rom/game_db.h"
#include "rom/rom_loader.h"
#include <array>
#include <algorithm>
#include <vector>

namespace sm2::libretro {
namespace {
u32 word(std::span<const u8> data, usize at) {
    return u32{data[at]} | u32{data[at+1]} << 8 | u32{data[at+2]} << 16 | u32{data[at+3]} << 24;
}
void put(std::span<u8> data, usize at, u32 value) {
    for (unsigned i = 0; i < 4; ++i) data[at+i] = static_cast<u8>(value >> (i*8));
}
u32 call(u32 from, u32 to) { return 0x09000000u | ((to-from) & 0x00ffffffu); }
struct Patch { u32 at, before, after; };
}
void PowerSledAudio::prepare(const rom::GameDatabase& database, const std::string& path,
                             const std::string& game, rom::RomSet& roms, bool enabled)
{
    m_requested = enabled;
    if (game != "powsledm" || !enabled) return;
    const auto* donor = database.find("powsledr");
    constexpr std::array<std::string_view, 2> regions{"audiocpu", "samples"};
    constexpr std::array<std::string_view, 1> siblings{"powsledr"};
    auto loaded = donor ? rom::RomLoader::load_regions(*donor, path, regions, siblings)
                        : std::optional<rom::RomSet>{};
    if (!loaded) {
        m_notice = "Power Sled Relay Audio: donor ROMs unavailable; keeping rider audio";
        return;
    }
    auto program = roms.region_mutable("maincpu");
    constexpr u32 volume = 0x1f0600, stop = 0x1f0680, race = 0x1f0700,
                  countdown = 0x1f0740, results = 0x1f0780;
    std::vector<Patch> patches{
        // Change only four musical scene tasks to accept Master role 0x200.
        {0x28dec, 0x58a81988, 0x58a81989},
        {0x309fc, 0x58a81988, 0x58a81989},
        {0x33828, 0x58a81988, 0x58a81989},
        {0x3b7a8, 0x58a81988, 0x58a81989},
        // Result music must replace the preceding track even under MIDI queue
        // pressure. The callback remains pending until stop and start enqueue.
        {0x28da4, 0x8c800065, 0x08000000u | ((results-0x28da4u)&0x00ffffffu)},
        // Skip the Relay's camera-monitor child; keep only the audio continuation.
        {0x28df4, call(0x28df4,0x120f0), 0x08000020},
        {0x30a04, call(0x30a04,0x120f0), 0x08000020},
        // The race constructor creates the music task only on its Relay branch.
        // Append that one task after the existing Master/rider construction.
        {0x43c78, 0x92f22004, 0x08000000u | ((race-0x43c78u)&0x00ffffffu)},
        // The existing visual countdown task emits cues only for Relay.
        {0xcfc48, 0x58901988, 0x58901989},
        {0xcfc6c, 0x58901988, 0x58901989},
        {0xcfc90, 0x58901988, 0x58901989},
        {0xcfcb0, 0x58981988, 0x58981989},
        {0xcfcc0, call(0xcfcc0,0x12810),
            0x08000000u | ((countdown-0xcfcc0u)&0x00ffffffu)},
    };
    for (u32 at : {0x28e24u,0x30a34u,0x33840u,0x3b7c0u})
        patches.push_back({at,call(at,0x12880),call(at,volume)});
    // Scene-wide transitions stop both boards. The per-rider finish/control
    // stops at 0x3c3d8/0x3cecc remain primary-only, as on a separate Relay.
    for (u32 at : {0x1c18cu,0x1c4ccu,0x1f2e0u,0x1f590u,0x21cb0u,0x273f0u,
                   0xbd5d0u,0xbd634u,0xbd6a0u,0xbd710u,
                   0xbd7b4u,0xbd854u,0xbd900u})
        patches.push_back({at,call(at,0x127e0),call(at,stop)});
    if (program.size() < 0x1f07d0
        || !std::all_of(program.begin()+volume,program.begin()+0x1f07d0,[](u8 b){return b==0;})
        || std::any_of(patches.begin(),patches.end(),[&](const Patch& p){return word(program,p.at)!=p.before;})) {
        m_notice = "Power Sled Relay Audio: unsupported program; keeping rider audio";
        return;
    }
    for (u32 index=0;index<2;++index) {
        const u32 at=0x12360+(0x6a+index)*3;
        if (program[at]!=0xa0 || program[at+1]!=0x12 || program[at+2]!=index) {
            m_notice = "Power Sled Relay Audio: unsupported countdown table; keeping rider audio";
            return;
        }
    }
    for (u32 index=0;index<6;++index) {
        const u32 at=0x12360+(0x64+index)*3;
        if (program[at]!=0xa0 || program[at+1]!=0x11 || program[at+2]!=index) {
            m_notice = "Power Sled Relay Audio: unsupported sound table; keeping rider audio";
            return;
        }
    }
    // Copy the native volume packet helper; tag BF/07 as BF/57 for the second board.
    std::copy_n(program.begin()+0x12880,0x48,program.begin()+volume);
    put(program,volume+0x1c,0x8ca80057); // lda 0x57,g5
    put(program,volume+0x40,call(volume+0x40,0x12700));
    put(program,stop,call(stop,0x127e0));
    // The result track ignores ordinary note-off. Native control 00/03 ends
    // the Relay's auxiliary sequences, including their one-shot sample voices.
    put(program,stop+4,0x8c803000); // lda result-stop packet,g0
    put(program,stop+8,stop+0x30);
    put(program,stop+12,call(stop+12,0x12700));
    put(program,stop+16,call(stop+16,0x127c0));
    put(program,stop+20,0x0a000000);
    put(program,stop+0x30,0x000363a0); // A0 63 03: auxiliary sequence stop
    // Stop once, then hand the task to a separate start callback. Re-enqueuing
    // a stop on each start retry would consume the queue's remaining capacity
    // and could indefinitely prevent the following music packet from fitting.
    const std::array<u32,8> result_stop{
        0x8c803000,stop+0x30,call(results+8,0x12700),
        0x3a042010, // cmpibe 0,g0,ret
        0x8ca03000,results+0x30,0x92a12004,0x0a000000};
    const std::array<u32,6> result_start{
        0x5c201610,0x8c800065,call(results+0x38,0x127a0),
        0x3a042008,0x92f12004,0x0a000000};
    for (usize i=0;i<result_stop.size();++i) put(program,results+i*4,result_stop[i]);
    for (usize i=0;i<result_start.size();++i) put(program,results+0x30+i*4,result_start[i]);
    const std::array<u32,10> race_task{
        0x92f22004,call(race+4,0x120f0),0x5c201610,0x5c801608,
        0x5c881604,call(race+0x14,0x12230),0x8c903000,0x0003b7a0,
        0x92912004,0x0a000000};
    for (usize i=0;i<race_task.size();++i) put(program,race+i*4,race_task[i]);
    // All Standalone sleds own a visual task, but only the local human camera
    // should emit audio. r4 still holds the caller's task across this branch.
    const std::array<u32,6> countdown_task{
        0x90a120d0,0x90a83000,0x0053e6f4,0x3da54008,
        call(countdown+0x10,0x12810),
        0x08000000u | ((0xcfcc4u-(countdown+0x14))&0x00ffffffu)};
    for (usize i=0;i<countdown_task.size();++i) put(program,countdown+i*4,countdown_task[i]);
    for (const auto& p : patches) put(program,p.at,p.after);
    for (u32 index=0;index<6;++index) program[0x12360+(0x64+index)*3+1]=0x61;
    for (u32 index=0;index<2;++index) program[0x12360+(0x6a+index)*3+1]=0x62;
    m_roms = std::move(*loaded);
    m_active = true;
    m_notice = "Power Sled Relay Audio: experimental music on Master; rider audio retained";
}
void PowerSledAudio::attach(hw::Model2MachineBase& machine)
{
    if (!m_active) return;
    auto* sound=dynamic_cast<hw::Model2Sound*>(&machine.sound_board());
    if (!sound) { m_active=false; return; }
    sound->attach_auxiliary_scsp(m_roms.region("audiocpu"),m_roms.region("samples"));
    sound->auxiliary_scsp()->configure_balance("powsledr");
}
}
