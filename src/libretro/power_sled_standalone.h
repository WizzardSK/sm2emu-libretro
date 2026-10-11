// SPDX-License-Identifier: BSD-3-Clause
#pragma once
#include "rom/rom_set.h"
#include <string_view>

namespace sm2::libretro {
/// Guarded Master-only reconstruction. The caller supplies isolated loopback.
[[nodiscard]] bool prepare_power_sled_standalone(rom::RomSet& roms);
/// Isolated Relay presentation with local attract actors and no race commands.
[[nodiscard]] bool prepare_power_sled_relay_attract(rom::RomSet& roms);
/// Bypass only the native late-course AI speed clamp in known Power Sled programs.
[[nodiscard]] bool prepare_power_sled_ai_finish_speed_fix(rom::RomSet& roms, std::string_view game);
}
