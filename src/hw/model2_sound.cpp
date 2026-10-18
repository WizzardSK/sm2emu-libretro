//  ____  __  __  ____         _____ __  __ _   _
// / ___||  \/  ||___ \       | ____|  \/  | | | |
// \___ \| |\/| |  __) |_____ |  _| | |\/| | | | |
//  ___) | |  | | / __/|_____|| |___| |  | | |_| |
// |____/|_|  |_||_____|      |_____|_|  |_|\___/
//
// A Sega Model 2 arcade emulator.
// Copyright (c) 2025+ Daniel Martin (dmanlfc)
// SPDX-License-Identifier: GPL-3.0-or-later AND BSD-3-Clause
//
// This header must not be removed. sm2-emu is licensed under the GNU General
// Public License, version 3 or later, with additional terms under section 7 of
// that licence. See LICENSE and NOTICE.
//
//
// See model2_sound.h.

#include "hw/model2_sound.h"

#include "core/archive.h"
#include "core/log.h"

#include <algorithm>
#include <array>
#include <unordered_map>

namespace sm2::hw {
namespace {

// ---------------------------------------------------------------------------
// Memory map
// ---------------------------------------------------------------------------
// MAME's model2_snd, region for region.

constexpr u32 kAddressMask = 0x00ffffff;  ///< The 68000 has 24 address lines.

constexpr u32 kRamBase     = 0x000000;
constexpr u32 kRamSize     = 0x080000;  // 512 KB, shared with the SCSP
constexpr u32 kScspBase    = 0x100000;
constexpr u32 kScspSize    = 0x001000;
constexpr u32 kSndCtrl     = 0x400000;  // sample banking, write only
constexpr u32 kProgramBase = 0x600000;
constexpr u32 kProgramSize = 0x080000;
constexpr u32 kSamplesBase = 0x800000;  // samples + 0x000000, 2 MB
constexpr u32 kSamplesSize = 0x200000;
constexpr u32 kBank4Base   = 0xa00000;  // samples + 0x200000, 4 MB
constexpr u32 kBank4Size   = 0x400000;
constexpr u32 kBank5Base   = 0xe00000;  // samples + 0x600000, 2 MB
constexpr u32 kBank5Size   = 0x200000;

/// The SCSP's own view of memory is 20 bits wide, of which the Model 2 sound
/// board wires up the low 512 KB.
constexpr u32 kScspAddressMask = 0x000fffff;

/// 68000 clock over host clock, exactly. 45.1584 MHz / 4 over 25 MHz reduces to
/// 7056/15625, and 5^6 shares no factor with 2^4 * 3^2 * 7^2, so this is lowest
/// terms and the remainder has to be carried rather than rounded away.
constexpr u64 kCpuClockNumerator   = 7056;
constexpr u64 kCpuClockDenominator = 15625;

/// The 68000 and the SCSP share the 45.1584 MHz crystal, so one 44100 Hz sample
/// is exactly 256 68000 cycles.
constexpr u64 kCyclesPerSample = 256;

/// Wait states on a 68000 access to RAM or the SCSP: a fixed two, plus up to
/// kContentionCycles more as the SCSP's own sample fetches take the RAM bus.
/// The contention term is fitted to a board capture of House of the Dead. The
/// fixed two keep the music near the hardware's tempo: House of the Dead's
/// attract music runs +0.5% against a cabinet recording with them, +1.33%
/// without; Sega Rally's +0.48% against its soundtrack with them, +1.45%
/// without.
constexpr u32 kBusWaitCycles    = 2;
constexpr u32 kContentionCycles = 12;

/// The SCSP is clocked at half the 45.1584 MHz crystal on the video board, which
/// divided by 512 is 44100 Hz exactly.
constexpr u32 kScspClock = 22'579'200;

/// Longest run of audio kept while nothing is draining it, in frames. Four video
/// frames is far more than a healthy consumer needs and small enough that a
/// headless run does not accumulate a gigabyte of samples.
constexpr usize kMaxPendingFrames = 4 * 800;

/// The reset vector, 16 bytes, is copied from the start of the sound ROM into
/// RAM. MAME's reset_model2_scsp does the same, with the note that the hardware
/// presumably arranges it in some way that amounts to this.
constexpr usize kResetVectorBytes = 16;

}  // namespace

Model2Sound::Model2Sound() : m_cpu(*this), m_scsp(*this, kScspClock)
{
    m_ram.assign(kRamSize, 0);
    m_pending.reserve(kMaxPendingFrames * 2);

    // The SCSP's interrupts go to the sound 68000, and only there: on Model 2 the
    // main_irq callback, which on a Saturn would reach the SH-2, is left unwired,
    // as MAME leaves it. The host's sound interrupt comes from the UART instead.
    m_scsp.set_irq_handler([this](int level, bool assert) {
        if (level <= 0) {
            m_cpu.clear_irq_lines();
            return;
        }
        m_cpu.set_irq_line(level, assert);
    });
}

Model2Sound::~Model2Sound() = default;

void Model2Sound::attach(std::span<const u8> program_rom, std::span<const u8> samples)
{
    m_program_rom = program_rom;
    m_samples     = samples;
    m_configurations[0] = {program_rom, samples};
    m_configuration = 0;
}

void Model2Sound::set_configuration(unsigned bank, std::span<const u8> program,
                                    std::span<const u8> samples)
{
    if (bank > 0 && bank < m_configurations.size())
        m_configurations[bank] = {program, samples};
}

bool Model2Sound::select_configuration(unsigned bank)
{
    if (bank >= m_configurations.size() || m_configurations[bank].program.empty()
        || m_configurations[bank].samples.empty()) return false;
    if (m_configuration != bank) {
        m_configuration = bank;
        m_program_rom = m_configurations[bank].program;
        m_samples = m_configurations[bank].samples;
        reset();
    }
    return true;
}

void Model2Sound::attach_m1(std::span<const u8> program, std::span<const u8> samples)
{
    if (program.empty() || samples.empty()) return;
    m_m1 = std::make_unique<M1Audio>();
    m_m1->attach(program, samples, {});  // Deluxe populates only one MultiPCM.
    m_m1->set_rxd_handler(m_midi_out_handler);
    m_m1->reset();
}

void Model2Sound::reset_m1_mixer()
{
    // A small fixed delay accommodates independently quantised sound slices.
    m_m1_samples.assign(32, 0);
    m_m1_phase = 0;
}

void Model2Sound::set_m1_enabled(bool enabled)
{
    enabled = enabled && m_m1 && m_m1->present();
    if (enabled == m_m1_enabled) return;
    m_m1_enabled = enabled;
    m_m1->reset();
    reset_m1_mixer();
}

void Model2Sound::attach_dsb(std::span<const u8> dsb_program, std::span<const u8> dsb_mpeg)
{
    m_dsb.attach(dsb_program, dsb_mpeg);
}

void Model2Sound::attach_dsb2(std::span<const u8> dsb_program, std::span<const u8> dsb_mpeg)
{
    m_dsb2.attach(dsb_program, dsb_mpeg);
}

void Model2Sound::set_midi_out_handler(Scsp::MidiOutHandler handler)
{
    m_midi_out_handler = handler;
    if (m_m1) m_m1->set_rxd_handler(handler);
    m_scsp.set_midi_out_handler(std::move(handler));
}

void Model2Sound::attach_auxiliary_scsp(std::span<const u8> program,
                                      std::span<const u8> samples)
{
    m_aux_scsp = std::make_unique<Model2Sound>();
    m_aux_scsp->attach(program, samples);
    m_aux_scsp->reset();
    m_aux_scsp_samples.assign(32, 0);
    m_aux_midi_count = 0;
}

void Model2Sound::midi_in(u8 value)
{
    if (!m_aux_scsp) { midi_primary(value); return; }
    if (!m_aux_midi_count && value != 0xa0 && value != 0xbf) {
        midi_primary(value);
        return;
    }
    m_aux_midi[m_aux_midi_count++] = value;
    if (m_aux_midi_count != 3) return;
    const bool tagged = (m_aux_midi[0] == 0xa0
        && (m_aux_midi[1] == 0x61 || m_aux_midi[1] == 0x62
            || m_aux_midi[1] == 0x63))
        || (m_aux_midi[0] == 0xbf && m_aux_midi[1] == 0x57);
    if (tagged) {
        SM2_DEBUG("auxiliary SCSP: %02x %02x %02x", m_aux_midi[0],
                  m_aux_midi[1] - 0x50, m_aux_midi[2]);
        if (m_aux_midi[0] == 0xa0 && m_aux_midi[1] == 0x63) {
            // Native group-zero sequence control; the result track is one-shot
            // and ignores ordinary note-off. No hardware reset or gain change.
            m_aux_scsp->midi_in(0xa0);
            m_aux_scsp->midi_in(0);
            m_aux_scsp->midi_in(m_aux_midi[2]);
        } else {
            m_aux_scsp->midi_in(m_aux_midi[0]);
            m_aux_scsp->midi_in(static_cast<u8>(m_aux_midi[1] - 0x50));
            m_aux_scsp->midi_in(m_aux_midi[2]);
        }
    } else {
        for (u8 byte : m_aux_midi) midi_primary(byte);
    }
    m_aux_midi_count = 0;
}

void Model2Sound::midi_primary(u8 value)
{
    // The host serial link drives both the SCSP's MIDI port and, on the sets
    // that carry one, the DSB. MAME fans the same txd out to both.
    m_scsp.midi_in(value);
    m_dsb.write_txd(value);
    m_dsb2.write_txd(value);
    if (m_m1_enabled) m_m1->write_txd(value);
}

void Model2Sound::reset()
{
    std::fill(m_ram.begin(), m_ram.end(), u8{0});

    m_bank4_offset = 0x200000;
    m_bank5_offset = 0x600000;

    m_cycle_debt      = 0;
    m_cycle_budget   = 0;
    m_sample_phase   = kCyclesPerSample;
    m_counters        = Counters{};
    m_pending.clear();

    m_scsp.reset();
    m_dsb.reset();
    m_dsb2.reset();
    if (m_m1) m_m1->reset();
    reset_m1_mixer();
    if (m_aux_scsp) m_aux_scsp->reset();
    m_aux_scsp_samples.assign(m_aux_scsp ? 32 : 0, 0);
    m_aux_midi_count = 0;

    // Seed the vector table. Without this the 68000 would fetch its stack
    // pointer and entry point out of cleared RAM and immediately run off into
    // nothing.
    const usize copy = std::min(kResetVectorBytes, m_program_rom.size());
    if (copy != 0) {
        std::copy_n(m_program_rom.begin(), copy, m_ram.begin());
    }

    m_cpu.reset();
}

void Model2Sound::serialize(Archive& ar)
{
    if (ar.format_version() >= 11) {
        bool auxiliary = m_aux_scsp != nullptr;
        ar.raw(auxiliary);
        if (ar.loading() && auxiliary != (m_aux_scsp != nullptr)) {
            ar.invalidate(); return;
        }
        if (auxiliary) {
            m_aux_scsp->serialize(ar);
            ar.deque_u32(m_aux_scsp_samples);
            ar.raw(m_aux_midi_count);
            ar.bytes(m_aux_midi.data(), m_aux_midi.size());
            if (ar.loading() && (m_aux_scsp_samples.size() > 128 || m_aux_midi_count > 2)) {
                ar.invalidate(); return;
            }
        }
    } else if (m_aux_scsp) { ar.invalidate(); return; }
    if (ar.format_version() >= 9) {
        unsigned bank = m_configuration;
        ar.raw(bank);
        if (ar.loading()) {
            if (bank >= m_configurations.size()
                || (bank && m_configurations[bank].program.empty())) {
                ar.invalidate();
                return;
            }
            m_configuration = bank;
            m_program_rom = m_configurations[bank].program;
            m_samples = m_configurations[bank].samples;
        }
    } else if (ar.loading()) {
        m_configuration = 0;
        m_program_rom = m_configurations[0].program;
        m_samples = m_configurations[0].samples;
        m_m1_enabled = false;
        if (m_m1) m_m1->reset();
        reset_m1_mixer();
    }
    ar.bytes(m_ram.data(), m_ram.size());
    m_cpu.serialize(ar);
    m_scsp.serialize(ar);
    m_dsb.serialize(ar);
    m_dsb2.serialize(ar);
    ar.raw(m_balance_profile_active);
    ar.raw(m_audio_balance_enabled);
    ar.raw(m_flat_gain);
    ar.raw(m_music_gain);
    ar.raw(m_sfx_gain);
    ar.raw(m_announcer_gain);
    ar.raw(m_voice_gain);
    ar.raw(m_bank4_offset);
    ar.raw(m_bank5_offset);
    ar.raw(m_cycle_debt);
    if (ar.loading() && ar.format_version() == 4) {
        // Version 4 used a half-rate CPU and an independent sample accumulator.
        u64 overshoot = 0, sample_debt = 0;
        ar.raw(overshoot);
        ar.raw(sample_debt);
        if (m_cycle_debt >= kCpuClockDenominator || overshoot > 1'000'000
            || sample_debt >= 250'000) {
            ar.invalidate();
            return;
        }
        m_cycle_budget = -static_cast<s64>(overshoot * 2);
        m_cycle_debt *= 2;
        m_cycle_budget += static_cast<s64>(m_cycle_debt / kCpuClockDenominator);
        m_cycle_debt %= kCpuClockDenominator;
        m_sample_phase = kCyclesPerSample - sample_debt * kCyclesPerSample / 250'000;
    } else {
        ar.raw(m_cycle_budget);
        ar.raw(m_sample_phase);
        if (ar.loading() && (m_cycle_debt >= kCpuClockDenominator
            || m_cycle_budget < -1'000'000 || m_cycle_budget > 1'000'000
            || m_sample_phase > 1'000'000)) ar.invalidate();
    }
    if (ar.loading() && !ar.failed()) configure_balance(m_balance_game_name);
    if (ar.format_version() >= 9) {
        bool auxiliary = m_m1 != nullptr;
        ar.raw(auxiliary);
        if (auxiliary) {
            if (!m_m1) { ar.invalidate(); return; }
            ar.raw(m_m1_enabled);
            m_m1->serialize(ar);
            ar.deque_u32(m_m1_samples);
            ar.raw(m_m1_phase);
            if (ar.loading() && (m_m1_samples.size() > 128
                || m_m1_phase >= u64{560} * sample_rate())) ar.invalidate();
        } else if (ar.loading()) {
            m_m1_enabled = false;
            if (m_m1) m_m1->reset();
            reset_m1_mixer();
        }
    }
}

void Model2Sound::run(u32 host_cycles)
{
    if (!present()) {
        if (!m_warned_no_program) {
            m_warned_no_program = true;
            SM2_WARN("sound: no 'audiocpu' region, the sound board will stay silent");
        }
        return;
    }

    m_cycle_debt += static_cast<u64>(host_cycles) * kCpuClockNumerator;
    m_cycle_budget += static_cast<s64>(m_cycle_debt / kCpuClockDenominator);
    m_cycle_debt %= kCpuClockDenominator;


    // The 68000 runs a sample at a time with the SCSP one sample ahead, so a
    // timer interrupts at the start of the sample it expires in and a reload
    // counts from the next one. The sequencers' tempo depends on it.
    const usize offset = m_pending.size();
    while (m_cycle_budget > 0) {
        if (m_sample_phase >= kCyclesPerSample) {
            generate_sample();
            m_sample_phase -= kCyclesPerSample;
            continue;
        }
        const s64 slice = std::min<s64>(m_cycle_budget,
                                        static_cast<s64>(kCyclesPerSample - m_sample_phase));
        const s32 used = m_cpu.run(static_cast<s32>(slice));
        m_sample_phase += static_cast<u64>(used);
        m_cycle_budget -= used;
    }
    const u32 frames = static_cast<u32>((m_pending.size() - offset) / 2);

    // The DSB (music board, DSB titles only) runs its Z80 over the same host
    // interval and mixes its decoded MPEG audio into the frames the SCSP just
    // produced. Inert -- and free -- for the sets without one.
    if (m_dsb.present()) {
        m_dsb.run(host_cycles);
        m_dsb.mix(m_pending.data() + offset, static_cast<u32>(frames),
                  m_scsp.sample_rate(), m_music_volume_percent * m_dsb_output_gain / 100);
    }
    if (m_dsb2.present()) {
        m_dsb2.run(host_cycles);
        m_dsb2.mix(m_pending.data() + offset, static_cast<u32>(frames),
                   m_scsp.sample_rate(), m_music_volume_percent * m_dsb_output_gain / 100);
    }
    if (m_m1_enabled) mix_m1(offset, host_cycles);
    if (m_aux_scsp) mix_auxiliary_scsp(offset, host_cycles);

    const usize limit = kMaxPendingFrames * 2;
    if (m_pending.size() > limit) {
        const usize excess = m_pending.size() - limit;
        m_counters.samples_dropped += excess / 2;
        m_pending.erase(m_pending.begin(),
                        m_pending.begin() + static_cast<std::ptrdiff_t>(excess));
    }
}

void Model2Sound::mix_auxiliary_scsp(usize offset, u32 host_cycles)
{
    m_aux_scsp->run(host_cycles);
    const auto input = m_aux_scsp->pending_samples();
    for (usize i = 0; i + 1 < input.size(); i += 2)
        m_aux_scsp_samples.push_back(u32{static_cast<u16>(input[i])}
            | (u32{static_cast<u16>(input[i + 1])} << 16));
    m_aux_scsp->clear_pending_samples();
    for (usize i = offset; i + 1 < m_pending.size() && !m_aux_scsp_samples.empty(); i += 2) {
        const u32 pair = m_aux_scsp_samples.front();
        m_aux_scsp_samples.pop_front();
        for (unsigned channel = 0; channel < 2; ++channel) {
            const s32 sample = static_cast<s16>(pair >> (channel * 16));
            m_pending[i + channel] = static_cast<s16>(std::clamp<s32>(
                m_pending[i + channel] + sample, -32768, 32767));
        }
    }
}

void Model2Sound::mix_m1(usize offset, u32 host_cycles)
{
    m_m1->run(host_cycles);
    const auto input = m_m1->pending_samples();
    for (usize i = 0; i + 1 < input.size(); i += 2)
        m_m1_samples.push_back(u32{static_cast<u16>(input[i])}
            | (u32{static_cast<u16>(input[i + 1])} << 16));
    m_m1->clear_pending_samples();
    // Exact native rate is 25 MHz / 560, not the rounded rate reported by M1.
    const u64 denominator = u64{560} * sample_rate();
    for (usize i = offset; i + 1 < m_pending.size(); i += 2) {
        if (m_m1_samples.size() < 2) break;
        for (unsigned channel = 0; channel < 2; ++channel) {
            const unsigned shift = channel * 16;
            const s64 first = static_cast<s16>(m_m1_samples[0] >> shift);
            const s64 second = static_cast<s16>(m_m1_samples[1] >> shift);
            const s64 value = first + (second - first) * static_cast<s64>(m_m1_phase)
                / static_cast<s64>(denominator);
            m_pending[i + channel] = static_cast<s16>(std::clamp<s64>(
                m_pending[i + channel] + value, -32768, 32767));
        }
        m_m1_phase += 25'000'000;
        while (m_m1_phase >= denominator) {
            m_m1_phase -= denominator;
            if (!m_m1_samples.empty()) m_m1_samples.pop_front();
        }
    }
}

void Model2Sound::generate_sample()
{
    const usize offset = m_pending.size();
    m_pending.resize(offset + 2);
    m_scsp.generate(m_pending.data() + offset, 1);
    if (m_scsp_output_gain != 100) {
        for (usize i = offset; i < m_pending.size(); ++i) {
            const s32 scaled = static_cast<s32>(m_pending[i])
                * static_cast<s32>(m_scsp_output_gain) / 100;
            m_pending[i] = static_cast<s16>(std::clamp(scaled, -32768, 32767));
        }
    }
}

// ---------------------------------------------------------------------------
// Address decode
// ---------------------------------------------------------------------------

Model2Sound::Window Model2Sound::resolve(u32 address)
{
    // A helper for the read-only sample windows, which differ only in where they
    // start in the sample ROM.
    const auto sample_window = [this](u32 offset, u32 span) -> Window {
        if (offset >= m_samples.size()) {
            return {};
        }
        Window result;
        result.base     = const_cast<u8*>(m_samples.data()) + offset;
        result.size     = std::min<usize>(span, m_samples.size() - offset);
        result.writable = false;
        return result;
    };

    if (address < kRamBase + kRamSize) {
        return Window{m_ram.data() + address, kRamSize - address, true};
    }

    if (address >= kProgramBase && address < kProgramBase + kProgramSize) {
        const u32 offset = address - kProgramBase;
        if (offset >= m_program_rom.size()) {
            return {};
        }
        return Window{const_cast<u8*>(m_program_rom.data()) + offset,
                      m_program_rom.size() - offset, false};
    }

    if (address >= kSamplesBase && address < kSamplesBase + kSamplesSize) {
        const u32 offset = address - kSamplesBase;
        return sample_window(offset, kSamplesSize - offset);
    }
    if (address >= kBank4Base && address < kBank4Base + kBank4Size) {
        const u32 offset = address - kBank4Base;
        return sample_window(m_bank4_offset + offset, kBank4Size - offset);
    }
    if (address >= kBank5Base && address < kBank5Base + kBank5Size) {
        const u32 offset = address - kBank5Base;
        return sample_window(m_bank5_offset + offset, kBank5Size - offset);
    }

    return {};
}

void Model2Sound::bus_wait(u32 address)
{
    if (address < kRamBase + kRamSize
        || (address >= kScspBase && address < kScspBase + kScspSize)) {
        const u32 contention = (kContentionCycles * m_scsp.active_slots() + 16) / 32;
        m_cpu.stall(static_cast<s32>(kBusWaitCycles + contention));
    }
}

void Model2Sound::snd_ctrl_write(u16 value)
{
    ++m_counters.snd_ctrl_writes;

    // Sample banking, and only for the handful of games whose sample region is
    // larger than 8 MB. Everything below that, Virtua Fighter 2 included, has
    // its whole sample ROM permanently visible and this register does nothing;
    // MAME guards it the same way.
    if (m_samples.size() <= 0x800000) {
        return;
    }
    if ((value & 0x20) != 0) {
        m_bank4_offset = 0x200000;
        m_bank5_offset = 0x600000;
    } else {
        m_bank4_offset = 0x800000;
        m_bank5_offset = 0xa00000;
    }
}

// ---------------------------------------------------------------------------
// The 68000's bus
// ---------------------------------------------------------------------------
// read16/write16 are the primitives: the 68000's bus is 16 bits wide, so a
// longword access really is two word accesses, and building the wider ones out
// of them keeps accesses that straddle two regions correct for free.

u16 Model2Sound::read16(u32 address)
{
    address &= kAddressMask;
    bus_wait(address);

    if (const Window window = resolve(address); window.base != nullptr) {
        if (address >= kSamplesBase) {
            ++m_counters.sample_reads;
        }
        if (window.size >= 2) {
            return static_cast<u16>((window.base[0] << 8) | window.base[1]);
        }
        return static_cast<u16>(window.base[0] << 8);
    }

    if (address >= kScspBase && address < kScspBase + kScspSize) {
        ++m_counters.scsp_reads;
        return m_scsp.read((address - kScspBase) >> 1);
    }

    // The banking register is write-only. MAME maps no reader at all, so a read
    // is an open bus; zero is as good a guess as any and is what an unmapped
    // read gives elsewhere.
    if (address >= kSndCtrl && address < kSndCtrl + 2) {
        return 0;
    }

    ++m_counters.unmapped_reads;
    SM2_TRACE("sound: unmapped read16 at %06x", address);
    return 0;
}

void Model2Sound::apply_flat_gain(u16 gain)
{
    std::array<u16, 32> gains;
    gains.fill(gain);
    m_scsp.set_slot_gains(gains.data());
}

void Model2Sound::configure_balance(const std::string& game_name)
{
    m_balance_game_name = game_name;
    static const std::unordered_map<std::string, u16> kFlatGain = {
        {"airwlkrs", 793},
        {"bel", 902},
        {"desert", 254},
        {"doa", 500}, {"doaa", 500}, {"doaab", 500}, {"doaae", 500}, {"doab", 500},
        {"dynabb", 1751},
        {"dynabb97", 1029},
        {"dynamcop", 705}, {"dynamcopb", 705}, {"dynamcopc", 705},
        {"dyndeka2", 705}, {"dyndeka2b", 705},
        {"fvipers", 403}, {"fvipersa", 403}, {"fvipersb", 403},
        {"gunblade", 1000},
        {"hotd", 1400}, {"hotdo", 1400}, {"hotdp", 1100},
        {"hpyagu98", 925},
        {"indy500", 2110}, {"indy500d", 2110}, {"indy500to", 2110},
        {"lastbrnx", 2095}, {"lastbrnxj", 2095}, {"lastbrnxu", 2095},
        {"manxtt", 799}, {"manxttc", 799}, {"manxttdx", 799},
        {"motoraid", 1239}, {"motoraiddx", 1239},
        {"overrev", 3892}, {"overrevb", 4022}, {"overrevba", 3852},
        {"pltkids", 2673}, {"pltkidsa", 2673},
        {"rchase2", 745}, {"rchase2a", 745},
        {"schamp", 403}, {"sfight", 403},
        {"segawski", 1095},
        {"sgt24h", 2319},
        {"skisuprg", 953},
        {"skytargt", 927},
        {"srallyc", 739}, {"srallycb", 739}, {"srallycc", 739},
        {"srallycdx", 739}, {"srallycdxa", 739},
        {"stcc", 384}, {"stcca", 384}, {"stccb", 384}, {"stcco", 384},
        {"topskatr", 232}, {"topskatrj", 232}, {"topskatru", 232}, {"topskatruo", 232},
        {"vcop", 321}, {"vcopa", 321},
        {"vcop2", 641},
        {"vf2", 840}, {"vf2a", 840}, {"vf2b", 840}, {"vf2o", 840},
        {"von", 1042}, {"vonj", 1042}, {"vonr", 1042}, {"vonu", 1042},
        {"vstriker", 899}, {"vstrikero", 899},
        {"waverunr", 1181},
        {"zerogun", 1912}, {"zerogunj", 1912},
        {"zeroguna", 2824}, {"zerogunaj", 2824},
    };

    const auto it = kFlatGain.find(game_name);
    m_flat_gain = it == kFlatGain.end() ? 256 : it->second;
    m_dsb_balance_gain = game_name == "topskatr" || game_name == "topskatrj"
        || game_name == "topskatru" || game_name == "topskatruo" ? 64 : 256;
    m_balance_profile_active = false;
    m_music_gain = m_sfx_gain = m_announcer_gain = m_voice_gain = 256;
    apply_balance();
}

void Model2Sound::apply_balance()
{
    apply_flat_gain(m_audio_balance_enabled && m_scsp_gain_automatic ? m_flat_gain : u16{256});
    m_dsb2.set_gain(m_audio_balance_enabled && m_dsb_gain_automatic ? m_dsb_balance_gain : u16{256});
}

void Model2Sound::set_audio_balance_enabled(bool enabled)
{
    if (m_aux_scsp) m_aux_scsp->set_audio_balance_enabled(enabled);
    m_audio_balance_enabled = enabled;
    if (m_m1) m_m1->set_audio_balance_enabled(enabled);
    apply_balance();
}

void Model2Sound::set_output_low_pass_enabled(bool enabled)
{
    if (m_aux_scsp) m_aux_scsp->set_output_low_pass_enabled(enabled);
    m_scsp.set_output_low_pass_enabled(enabled);
}

void Model2Sound::set_music_volume_percent(unsigned percent)
{
    m_music_volume_percent = std::min(percent, 200u);
}

bool Model2Sound::has_audio_source(AudioSource source) const
{
    return source == AudioSource::Scsp ? present()
        : source == AudioSource::Dsb ? (m_dsb.present() || m_dsb2.present())
        : source != AudioSource::MultiPcm2 && m_m1 && m_m1->has_audio_source(source);
}

void Model2Sound::set_audio_source_gain(AudioSource source, unsigned percent, bool automatic)
{
    if (m_aux_scsp) m_aux_scsp->set_audio_source_gain(source, percent, automatic);
    if (!has_audio_source(source)) return;
    if (m_m1 && m_m1->has_audio_source(source)) {
        m_m1->set_audio_source_gain(source, percent, automatic);
        return;
    }
    if (source == AudioSource::Scsp) {
        m_scsp_output_gain = automatic ? 100 : std::min(percent, 200u);
        m_scsp_gain_automatic = automatic;
    }
    if (source == AudioSource::Dsb) {
        m_dsb_output_gain = automatic ? 100 : std::min(percent, 200u);
        m_dsb_gain_automatic = automatic;
    }
    apply_balance();
}

void Model2Sound::write16(u32 address, u16 value)
{
    address &= kAddressMask;
    bus_wait(address);

    if (const Window window = resolve(address); window.base != nullptr) {
        if (!window.writable) {
            // ROM. Discarded, as MAME's .rom() does.
            return;
        }
        window.base[0] = static_cast<u8>(value >> 8);
        if (window.size >= 2) {
            window.base[1] = static_cast<u8>(value);
        }
        return;
    }

    if (address >= kScspBase && address < kScspBase + kScspSize) {
        ++m_counters.scsp_writes;
        m_scsp.write((address - kScspBase) >> 1, value, 0xffff);
        return;
    }

    if (address >= kSndCtrl && address < kSndCtrl + 2) {
        snd_ctrl_write(value);
        return;
    }

    ++m_counters.unmapped_writes;
    SM2_TRACE("sound: unmapped write16 at %06x = %04x", address, value);
}

u8 Model2Sound::read8(u32 address)
{
    // Byte lane 0 of the word is the high half on a big-endian bus.
    const u16 word = read16(address & ~1u);
    return (address & 1) != 0 ? static_cast<u8>(word) : static_cast<u8>(word >> 8);
}

void Model2Sound::write8(u32 address, u8 value)
{
    const u32 masked = address & kAddressMask;
    bus_wait(masked);

    // Plain memory takes the byte directly; anything with side effects has to be
    // told which lane was driven, because a byte write to a 16-bit register must
    // not clear the other half.
    if (const Window window = resolve(masked); window.base != nullptr) {
        if (window.writable) {
            *window.base = value;
        }
        return;
    }

    if (masked >= kScspBase && masked < kScspBase + kScspSize) {
        ++m_counters.scsp_writes;
        const u16 mask = (masked & 1) != 0 ? u16{0x00ff} : u16{0xff00};
        const u16 wide = (masked & 1) != 0 ? static_cast<u16>(value)
                                           : static_cast<u16>(value << 8);
        m_scsp.write((masked - kScspBase) >> 1, wide, mask);
        return;
    }

    if (masked >= kSndCtrl && masked < kSndCtrl + 2) {
        snd_ctrl_write(value);
        return;
    }

    ++m_counters.unmapped_writes;
    SM2_TRACE("sound: unmapped write8 at %06x = %02x", masked, value);
}

u32 Model2Sound::read32(u32 address)
{
    const u32 high = read16(address);
    const u32 low  = read16(address + 2);
    return (high << 16) | low;
}

void Model2Sound::write32(u32 address, u32 value)
{
    write16(address, static_cast<u16>(value >> 16));
    write16(address + 2, static_cast<u16>(value));
}

// ---------------------------------------------------------------------------
// The SCSP's bus
// ---------------------------------------------------------------------------
// MAME gives the SCSP a 20-bit big-endian space of its own and maps the same
// "soundram" into it, which is how a slot's sample address reaches data the 68000
// loaded. Only the low 512 KB is wired, so anything above that reads as nothing.

u8 Model2Sound::scsp_read_byte(u32 address)
{
    address &= kScspAddressMask;
    if (address < m_ram.size()) {
        return m_ram[address];
    }
    // Addresses above the 512 KB RAM window read from the sample ROM, which is
    // where the SCSP finds PCM data that the 68000 did not copy into RAM. On
    // Model 2 the SCSP's 20-bit address space maps RAM at 0x00000–0x7FFFF and
    // the first 512 KB of sample ROM at 0x80000–0xFFFFF. This is what MAME's
    // device_rom_interface provides as a fallback behind the scsp_map RAM.
    const u32 rom_offset = address - static_cast<u32>(m_ram.size());
    if (rom_offset < m_samples.size()) {
        return m_samples[rom_offset];
    }
    return 0;
}

u16 Model2Sound::scsp_read_word(u32 address)
{
    address &= kScspAddressMask & ~1u;
    if (address + 1 < m_ram.size()) {
        return static_cast<u16>((m_ram[address] << 8) | m_ram[address + 1]);
    }
    // Fall through to sample ROM for addresses above the RAM window.
    const u32 rom_offset = address - static_cast<u32>(m_ram.size());
    if (rom_offset + 1 < m_samples.size()) {
        return static_cast<u16>((m_samples[rom_offset] << 8) | m_samples[rom_offset + 1]);
    }
    return 0;
}

void Model2Sound::scsp_write_word(u32 address, u16 value)
{
    address &= kScspAddressMask & ~1u;
    if (address + 1 >= m_ram.size()) {
        return;  // Writes above RAM are discarded (ROM is read-only).
    }
    m_ram[address]     = static_cast<u8>(value >> 8);
    m_ram[address + 1] = static_cast<u8>(value);
}

}  // namespace sm2::hw
