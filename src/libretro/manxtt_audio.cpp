// SPDX-License-Identifier: BSD-3-Clause
#include "manxtt_audio.h"
#include "nvram_settings.h"
#include "hw/model2_machine_base.h"
#include "hw/model2_sound.h"
#include "rom/game_db.h"
#include "rom/rom_loader.h"

namespace sm2::libretro {
void ManxTtAudio::prepare(const rom::GameDatabase& database, const std::string& path,
                        const std::string& game, hw::Model2MachineBase& machine)
{
    m_applicable = game == "manxtt" || game == "manxttc" || game == "manxttdx";
    if (!m_applicable) return;
    auto* sound = dynamic_cast<hw::Model2Sound*>(&machine.sound_board());
    if (!sound) { m_applicable = false; return; }
    m_dx_only = game == "manxttdx";
    static constexpr std::array<std::string_view, 3> siblings{
        "manxttc", "manxtt", "manxttdx"};
    static constexpr std::array<std::string_view, 2> scsp{"audiocpu", "samples"};
    if (!m_dx_only) {
        for (unsigned bank = 1; bank <= 2; ++bank) {
            const auto* source = database.find(bank == 1 ? "manxttc" : "manxtt");
            if (!source) continue;
            auto loaded = rom::RomLoader::load_regions(*source, path, scsp, siblings);
            if (!loaded) continue;
            m_roms[bank] = std::move(*loaded);
            m_available[bank] = true;
            sound->set_configuration(bank, m_roms[bank].region("audiocpu"),
                                           m_roms[bank].region("samples"));
        }
    }
    static constexpr std::array<std::string_view, 2> auxiliary{
        "m1audio:sndcpu", "m1audio:pcm1"};
    const auto* source = database.find(m_dx_only ? "manxttdx" : "manxtt");
    if (source) {
        auto loaded = rom::RomLoader::load_regions(*source, path, auxiliary, siblings);
        if (loaded) {
            m_roms[0] = std::move(*loaded);
            sound->attach_m1(m_roms[0].region(auxiliary[0]), m_roms[0].region(auxiliary[1]));
            sound->set_m1_enabled(game != "manxttc");
        }
    }
}

ManxTtAudio::Update ManxTtAudio::update(hw::Model2MachineBase& machine, bool enabled)
{
    Update result;
    if (!m_applicable) return result;
    auto& sound = static_cast<hw::Model2Sound&>(machine.sound_board());
    if (m_dx_only) m_last_cabinet = 0;
    else if (nvram::valid_layout("manxtt", machine.backup_ram(), machine.settings_eeprom())) {
        const u8 cabinet = machine.settings_eeprom()[0x0a];
        if (cabinet <= 1) m_last_cabinet = cabinet;
    }
    if (m_last_cabinet < 0) return result;  // Do not react to an unfinished EEPROM write.
    const unsigned requested = !enabled || m_dx_only ? 0 : m_last_cabinet == 1 ? 1 : 2;
    const unsigned selected = m_available[requested] ? requested : 0;
    const unsigned previous = sound.configuration();
    const bool auxiliary_before = sound.m1_enabled();
    (void)sound.select_configuration(selected);
    sound.set_m1_enabled(m_last_cabinet == 0);
    result.changed = previous != sound.configuration() || auxiliary_before != sound.m1_enabled();
    if (!m_available[requested] && m_missing_notice != static_cast<int>(requested)) {
        m_missing_notice = static_cast<int>(requested);
        result.notice = "Manx TT: matching cabinet audio ROMs unavailable; using selected set audio";
    } else if (m_last_cabinet == 0 && !sound.auxiliary_m1() && !m_auxiliary_notice) {
        m_auxiliary_notice = true;
        result.notice = "Manx TT: Deluxe additional sound ROMs unavailable";
    } else if (m_last_request != static_cast<int>(requested) || result.changed) {
        result.notice = std::string("Manx TT audio: ")
            + (selected == 1 ? "Twin" : selected == 2 ? "Deluxe" : "Selected Set")
            + (sound.m1_enabled() ? "; additional Deluxe board connected" : "");
    }
    m_last_request = static_cast<int>(requested);
    return result;
}
}
