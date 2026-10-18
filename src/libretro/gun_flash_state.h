// SPDX-License-Identifier: BSD-3-Clause
#pragma once

#include "hw/model2_video.h"

namespace sm2::libretro {

// Extend the existing presentation word without changing the machine archive
// or frontend tail size. Bit 2 remains readable by older one-frame detectors.
inline u32 gun_flash_flags(const hw::Model2Video::GunFlashState& state)
{
    const u32 age = state.frames_since_press <= 2 ? state.frames_since_press : 3;
    return 0x47460000u | (state.triggers_held & 0x03u)
        | (age == 0 ? 1u << 2 : 0u)
        | (state.window_mask_full ? 1u << 3 : 0u)
        | (state.hidden ? 1u << 4 : 0u)
        | (1u << 10) | (age << 11);
}

inline hw::Model2Video::GunFlashState gun_flash_state_from_flags(u32 flags)
{
    hw::Model2Video::GunFlashState state;
    if ((flags & 0xffff0000u) != 0x47460000u) return state;
    state.triggers_held = static_cast<u8>(flags & 0x03u);
    if (flags & (1u << 10)) {
        const u8 age = static_cast<u8>((flags >> 11) & 0x03u);
        state.frames_since_press = age <= 2 ? age : 0xff;
    } else {
        // Legacy history knows only whether the preceding frame had a press.
        state.frames_since_press = flags & (1u << 2) ? 0 : 0xff;
    }
    state.window_mask_full = flags & (1u << 3);
    state.hidden = flags & (1u << 4);
    return state;
}

} // namespace sm2::libretro
