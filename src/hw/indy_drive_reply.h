//  ____  __  __  ____         _____ __  __ _   _
// / ___||  \/  ||___ \       | ____|  \/  | | | |
// \___ \| |\/| |  __) |_____ |  _| |\/| | | | |
//  ___) | |  | | / __/|_____|| |___| |  | | |_| |
// |____/|_|  |_||_____|      |_____|_|  |_|\___/
//
// A Sega Model 2 arcade emulator.
// Copyright (c) 2025+ Daniel Martin (dmanlfc)
// SPDX-License-Identifier: GPL-3.0-or-later
//
// This header must not be removed. sm2-emu is licensed under the GNU General
// Public License, version 3 or later, with additional terms under section 7 of
// that licence. See LICENSE and NOTICE.
//
// Adapted from upstream e700c39: EPR-18261 drive-board replies.
#pragma once

#include "core/types.h"

namespace sm2::hw {

struct IndyDriveReply {
    u8 command = 0;
    u8 centre = 0x80;

    void write(u8 value)
    {
        command = value;
        if ((value & 0xf0) == 0x90) {
            centre = static_cast<u8>((centre & 0x0f) | (value << 4));
        } else if ((value & 0xf0) == 0xc0) {
            centre = static_cast<u8>((centre & 0xf0) | (value & 0x0f));
        }
    }

    [[nodiscard]] u8 read(u8 wheel) const
    {
        switch (command) {
            case 0x80:
            case 0x83: return wheel;
            case 0x81:
            case 0x82: return 0xff;
            case 0x84: return centre == 0xff ? u8{0x80} : centre;
            default: return command;
        }
    }
};

}  // namespace sm2::hw
