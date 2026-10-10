// SPDX-License-Identifier: BSD-3-Clause
#pragma once

#include "core/archive.h"

namespace sm2::hw {
// Minimal parallel D/E acknowledgement stub, derived from Manx TT's native
// Deluxe initialization routine. It does not simulate motors or feedback.
class ManxTtAms {
public:
    void reset() { m_enabled = false; m_response = 0xff; }
    bool select(bool enabled) {
        if (enabled != m_enabled) { m_enabled = enabled; m_response = 0xff; }
        return m_enabled;
    }
    void write(u8 command) {
        if (!m_enabled) return;
        if (command == 0x3d) m_response = 0xce;
        else if (m_response == 0xce) m_response = 0xcd;
    }
    u8 read() const { return m_response; }
    void serialize(Archive& ar) {
        if (ar.format_version() < 10) { if (ar.loading()) reset(); return; }
        u8 enabled = m_enabled ? 1 : 0;
        ar.raw(enabled); ar.raw(m_response);
        if (ar.loading()) {
            if (enabled > 1 || (m_response != 0xff && m_response != 0xce && m_response != 0xcd)
                || (!enabled && m_response != 0xff)) ar.invalidate();
            m_enabled = enabled == 1;
        }
    }
private:
    bool m_enabled = false;
    u8 m_response = 0xff;
};
} // namespace sm2::hw
