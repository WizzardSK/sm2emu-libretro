// SPDX-License-Identifier: BSD-3-Clause
#pragma once
#include "rom/rom_set.h"
#include <array>
#include <string>

namespace sm2::rom { class GameDatabase; }
namespace sm2::hw { class Model2MachineBase; }
namespace sm2::libretro {

/// Own only alternate audio ROMs; main-program identity and saves are untouched.
class ManxTtAudio {
public:
    void prepare(const rom::GameDatabase& database, const std::string& path,
                 const std::string& game, hw::Model2MachineBase& machine);
    struct Update { bool changed = false; std::string notice; };
    Update update(hw::Model2MachineBase& machine, bool enabled);
private:
    std::array<rom::RomSet, 3> m_roms;
    std::array<bool, 3> m_available{true, false, false};
    bool m_applicable = false;
    bool m_dx_only = false;
    int m_last_request = -1;
    int m_last_cabinet = -1;
    int m_missing_notice = -1;
    bool m_auxiliary_notice = false;
};
}
