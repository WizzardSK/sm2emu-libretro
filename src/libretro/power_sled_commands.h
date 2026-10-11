// SPDX-License-Identifier: BSD-3-Clause
#pragma once
#include "rom/rom_set.h"
namespace sm2::libretro {
/// Experimental Master-only native operator remap and departure completion.
[[nodiscard]] bool prepare_power_sled_commands(rom::RomSet& roms);
}
