// SPDX-License-Identifier: BSD-3-Clause
// ROM-free checks for alternate sound banks, the second board and persistence.
#include "core/archive.h"
#include "hw/model2_sound.h"
#include "hw/model2.h"
#include "libretro/manxtt_audio.h"
#include "libretro/save_ram.h"
#include "rom/game_db.h"
#include "rom/rom_loader.h"
#include <miniz.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <iostream>
#include <stdexcept>

using namespace sm2;
namespace {
void check(bool value, const char* message) { if (!value) throw std::runtime_error(message); }
std::vector<u8> program(bool scsp, u8 marker) {
    std::vector<u8> result(512);
    result[1] = scsp ? 7 : 0xf0; result[2] = 0xff;
    result[5] = scsp ? 0x60 : 0; result[6] = 1;
    result[256] = 0x60; result[257] = 0xfe;
    result[128] = marker;
    return result;
}
std::vector<s16> advance(hw::Model2Sound& board, unsigned slices = 1000) {
    std::vector<s16> result;
    for (unsigned i = 0; i < slices; ++i) {
        board.run(1000);
        const auto samples = board.pending_samples();
        result.insert(result.end(), samples.begin(), samples.end());
        board.clear_pending_samples();
    }
    return result;
}
void zip(const std::filesystem::path& path, const char* data) {
    mz_zip_archive archive{};
    check(mz_zip_writer_init_file(&archive, path.string().c_str(), 0), "Zip creation");
    check(mz_zip_writer_add_mem(&archive, "chip", data, 1, 0), "Zip chip");
    check(mz_zip_writer_finalize_archive(&archive), "Zip finish");
    mz_zip_writer_end(&archive);
}
}
int main() {
    std::filesystem::path temporary;
    try {
        hw::ManxTtAms ams;
        check(ams.select(true), "Enable AMS");
        ams.write(0x3d);
        std::vector<u8> old_ams;
        Archive old_ams_save(old_ams, 9); ams.serialize(old_ams_save);
        check(old_ams.empty(), "No AMS fields in legacy format 9");
        Archive old_ams_load(old_ams.data(), old_ams.size(), 9); ams.serialize(old_ams_load);
        check(ams.select(true) && ams.read() == 0xff, "Legacy states reset absent AMS state");
        const std::array<u8, 2> corrupt_ams{2, 0xce};
        Archive corrupt_ams_load(corrupt_ams.data(), corrupt_ams.size()); ams.serialize(corrupt_ams_load);
        check(corrupt_ams_load.failed(), "Invalid AMS state rejected");
        const auto original = program(true, 0x10), twin = program(true, 0x20),
                   deluxe = program(true, 0x30), auxiliary = program(false, 0);
        std::vector<u8> samples(0x1000);
        samples[1] = 1; samples[5] = 0xff; samples[8] = 0xf0;
        for (unsigned i = 0; i < 256; ++i)
            samples[0x100 + i] = u8(s8(30 * std::sin(2 * 3.141592653589793 * i / 64)));
        hw::Model2Sound sound;
        sound.attach(original, samples);
        sound.set_configuration(1, twin, samples);
        sound.set_configuration(2, deluxe, samples);
        sound.attach_m1(auxiliary, samples);
        sound.reset();
        check(sound.select_configuration(1) && sound.read8(0x600080) == 0x20, "Twin bank");
        check(sound.select_configuration(2) && sound.read8(0x600080) == 0x30, "Deluxe bank");
        check(!sound.select_configuration(3), "Invalid bank rejected");
        sound.set_m1_enabled(true);
        auto& m1 = *sound.auxiliary_m1();
        m1.write16(0xc40002, 0);
        auto reg = [&](unsigned index, unsigned value) {
            m1.write16(0xc40004, u16(index)); m1.write16(0xc40000, u16(value));
        };
        reg(0, 0); reg(1, 0); reg(2, 0); reg(3, 0); reg(5, 1); reg(4, 0x80);
        check(!sound.has_audio_source(hw::AudioSource::MultiPcm2), "Unpopulated second PCM");
        sound.midi_in(0xae);
        check(m1.counters().bytes_from_host == 1, "Second board serial fanout");
        const auto audio = advance(sound, 10000);
        check(std::any_of(audio.begin(), audio.end(), [](s16 value) { return value != 0; }),
              "Supplemental PCM reaches mixed output");
        std::vector<u8> state;
        Archive save(state); sound.serialize(save);
        const auto expected = advance(sound);
        (void)sound.select_configuration(1);
        Archive load(state.data(), state.size()); sound.serialize(load);
        check(!load.failed() && sound.configuration() == 2 && sound.m1_enabled(), "Restore ROM bank and board");
        check(advance(sound) == expected, "Sample-exact auxiliary CPU/PCM/resampler continuation");
        sound.set_audio_source_gain(hw::AudioSource::MultiPcm1, 0);
        (void)advance(sound, 40);  // Drain samples mixed before the Gain change.
        const auto muted = advance(sound);
        check(std::all_of(muted.begin(), muted.end(), [](s16 value) { return value == 0; }), "Supplemental Gain Mute");
        sound.set_m1_enabled(false);
        const auto received = m1.counters().bytes_from_host;
        sound.midi_in(0xae);
        check(m1.counters().bytes_from_host == received, "Disconnected board receives no commands");
        std::vector<u8> legacy;
        Archive legacy_save(legacy, 8); sound.serialize(legacy_save);
        Archive legacy_load(legacy.data(), legacy.size(), 8); sound.serialize(legacy_load);
        check(!legacy_load.failed() && sound.configuration() == 0 && !sound.m1_enabled(), "Version 8 remains readable");
        hw::Model2Sound missing;
        missing.attach(original, samples); missing.reset();
        Archive missing_load(state.data(), state.size()); missing.serialize(missing_load);
        check(missing_load.failed(), "State requiring unavailable alternate ROMs rejected");

        temporary = std::filesystem::temp_directory_path() / ("sm2-audio-" + std::to_string(
            std::chrono::steady_clock::now().time_since_epoch().count()));
        std::filesystem::create_directory(temporary);
        zip(temporary / "selected.zip", "X"); zip(temporary / "donor.zip", "Y");
        const auto crc = mz_crc32(0, reinterpret_cast<const unsigned char*>("Y"), 1);
        rom::GameDatabase database;
        check(database.load_from_string("<games><game name='donor' board='model2a'><title>Fixture</title><roms>"
            "<region name='audio' size='1' required='false'><file name='chip' offset='0' crc='"
            + std::to_string(crc) + "'/></region></roms></game></games>"), "Fixture database");
        const std::array<std::string_view, 1> regions{"audio"}, siblings{"donor"};
        auto loaded = rom::RomLoader::load_regions(*database.find("donor"),
            (temporary / "selected.zip").string(), regions, siblings);
        check(loaded && loaded->region("audio")[0] == 'Y', "CRC-correct sibling overrides wrong same-name chip");
        std::filesystem::remove(temporary / "donor.zip");
        check(!rom::RomLoader::load_regions(*database.find("donor"),
            (temporary / "selected.zip").string(), regions, siblings), "Optional missing chip cannot masquerade as available audio");
        zip(temporary / "manxttc.zip", "Y");
        const std::string region_xml = "<region name='audiocpu' size='1'><file name='chip' offset='0'/></region>"
            "<region name='samples' size='1'><file name='chip' offset='0'/></region>"
            "<region name='m1audio:sndcpu' size='1'><file name='chip' offset='0'/></region>"
            "<region name='m1audio:pcm1' size='1'><file name='chip' offset='0'/></region>";
        check(database.load_from_string("<games><game name='manxtt' board='model2a'><roms>" + region_xml
            + "</roms></game><game name='manxttc' board='model2a'><roms>" + region_xml
            + "</roms></game><game name='manxttdx' board='model2a'><roms>" + region_xml
            + "</roms></game></games>"), "Cabinet fixture database");
        libretro::ManxTtAudio adapter;  // Storage must outlive the machine.
        hw::Model2 machine;
        rom::RomSet machine_roms;
        machine_roms.add("maincpu", std::vector<u8>(256));
        machine_roms.add("audiocpu", original); machine_roms.add("samples", samples);
        check(machine.init(*database.find("manxtt"), std::move(machine_roms)), "Fixture machine");
        adapter.prepare(database, (temporary / "selected.zip").string(), "manxtt", machine);
        auto eeprom = machine.settings_eeprom();
        std::fill(eeprom.begin(), eeprom.end(), 0);
        eeprom[2] = 0x38; eeprom[10] = 1;
        const auto commit = [&] {
            u16 checksum = 0xffff;
            for (u8 value : eeprom.subspan(2, 0x36)) {
                checksum ^= u16(value) << 8;
                for (unsigned bit = 0; bit < 8; ++bit)
                    checksum = u16((checksum & 0x8000) ? (checksum << 1) ^ 0x1021 : checksum << 1);
            }
            checksum = static_cast<u16>(~checksum);
            eeprom[0] = u8(checksum); eeprom[1] = u8(checksum >> 8);
        };
        commit();
        machine.inputs().in2 = 0x5a;
        machine.write8(0x01c00008, 0x3d);
        check(machine.read8(0x01c00006) == machine.inputs().player_port(1), "Twin retains P2 input instead of AMS");
        eeprom[10] = 0;
        check(machine.read8(0x01c00006) == 0xff, "Deluxe starts AMS idle");
        machine.write8(0x01c00008, 0x3d);
        check(machine.read8(0x01c00006) == 0xce, "Deluxe command acknowledgement");
        std::vector<u8> ams_state;
        check(machine.save_state(ams_state), "Save during AMS handshake");
        machine.write8(0x01c00008, 0x7f);
        check(machine.read8(0x01c00006) == 0xcd, "Deluxe parameter acknowledgement");
        check(machine.load_state(ams_state.data(), ams_state.size()), "Restore AMS handshake");
        check(machine.read8(0x01c00006) == 0xce, "Restored pending parameter");
        machine.write8(0x01c00008, 0x7f);
        check(machine.read8(0x01c00006) == 0xcd, "Restored handshake continues");
        machine.reset();
        check(machine.read8(0x01c00006) == 0xff, "Reset clears AMS acknowledgement");
        eeprom[10] = 1;
        check(machine.read8(0x01c00006) == machine.inputs().player_port(1), "Switch to Twin restores P2 immediately");
        eeprom[10] = 0;
        check(machine.read8(0x01c00006) == 0xff, "Re-entering Deluxe starts fresh handshake");
        eeprom[10] = 1;
        commit();
        (void)adapter.update(machine, true);
        check(machine.sound().configuration() == 1 && !machine.sound().m1_enabled(), "Saved Twin controls audio");
        eeprom[10] = 0;
        (void)adapter.update(machine, true);
        check(machine.sound().configuration() == 1, "Uncommitted Service EEPROM ignored");
        commit();
        const std::vector<u8> before(eeprom.begin(), eeprom.end());
        (void)adapter.update(machine, true);
        check(machine.sound().configuration() == 2 && machine.sound().m1_enabled(), "Committed Deluxe connects second board");
        (void)adapter.update(machine, false);
        check(machine.sound().configuration() == 0 && machine.sound().m1_enabled(), "Disabled retains original sound ROMs");
        check(std::equal(before.begin(), before.end(), eeprom.begin()), "Audio selection never writes NVRAM");
        libretro::ManxTtAudio dx_adapter;
        hw::Model2 dx;
        rom::RomSet dx_roms;
        dx_roms.add("maincpu", std::vector<u8>(256));
        dx_roms.add("audiocpu", original); dx_roms.add("samples", samples);
        check(dx.init(*database.find("manxttdx"), std::move(dx_roms)), "DX fixture machine");
        dx.settings_eeprom()[10] = 1;
        dx.write8(0x01c00008, 0x3d);
        check(dx.read8(0x01c00006) == 0xce, "DX-only AMS always connected");
        dx_adapter.prepare(database, (temporary / "selected.zip").string(), "manxttdx", dx);
        (void)dx_adapter.update(dx, false);
        check(dx.sound().configuration() == 0 && dx.sound().m1_enabled(), "DX-only always connects available second board");
        std::filesystem::remove_all(temporary);
        std::cout << "Manx TT AMS scope/reset/handshake/state and alternate audio checks passed\n";
    } catch (const std::exception& error) {
        if (!temporary.empty()) std::filesystem::remove_all(temporary);
        std::cerr << error.what() << '\n'; return 1;
    }
}
