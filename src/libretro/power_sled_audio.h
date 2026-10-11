// SPDX-License-Identifier: BSD-3-Clause
#pragma once
#include "rom/rom_set.h"
#include <string>
namespace sm2::rom { class GameDatabase; }
namespace sm2::hw { class Model2MachineBase; }
namespace sm2::libretro {
/// Experimental Master-only music reconstruction; owns CRC-checked donor ROMs.
class PowerSledAudio {
public:
    void prepare(const rom::GameDatabase& database, const std::string& path,
                 const std::string& game, rom::RomSet& roms, bool enabled);
    void attach(hw::Model2MachineBase& machine);
    [[nodiscard]] bool active() const { return m_active; }
    [[nodiscard]] bool requested() const { return m_requested; }
    [[nodiscard]] const std::string& notice() const { return m_notice; }
private:
    rom::RomSet m_roms;
    bool m_requested = false;
    bool m_active = false;
    std::string m_notice;
};
}
