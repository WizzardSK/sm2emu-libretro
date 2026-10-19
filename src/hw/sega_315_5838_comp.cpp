// SPDX-License-Identifier: GPL-3.0-or-later AND BSD-3-Clause
//
// Derived from MAME's src/mame/sega/315-5838_317-0229_comp.cpp
// (BSD-3-Clause, copyright-holders David Haywood, Samuel Neves, Peter
// Wilhelmsen, Morten Shearman Kirkegaard).

#include "hw/sega_315_5838_comp.h"
#include "core/archive.h"
#include "core/log.h"

namespace sm2::hw {

void Sega3155838Comp::reset()
{
    m_tree.fill(0);
    m_dictionary.fill(0);
    m_tree_words = 0;
    m_dictionary_bytes = 0;
    m_upload_dictionary = false;
    m_source = 0;
    m_word = 0;
    m_bits = 0;
    m_output = 0xffff;
    m_abort = false;
    m_dummy = true;
}

u16 Sega3155838Comp::decipher(u16 ciphertext)
{
    // 317-0229 routing/substitution and affine masks from MAME's CIPHERS.
    static constexpr u8 routing[4] = {3, 2, 0, 1};
    static constexpr u8 sboxes[4][8] = {
        {6, 0, 5, 4, 7, 2, 1, 3}, {5, 6, 1, 3, 7, 0, 4, 2},
        {2, 6, 0, 1, 3, 4, 7, 5}, {6, 5, 7, 4, 1, 3, 0, 2}};
    static constexpr u8 affine_masks[4] = {0b10010, 0b10001, 0b00100, 0b11010};
    static constexpr u8 output_bits[4][3] = {{0, 1, 7}, {2, 5, 9}, {4, 10, 13}, {6, 11, 15}};
    static constexpr u8 affine_bits[4] = {3, 8, 12, 14};
    const auto x = [ciphertext](unsigned b) { return (ciphertext >> b) & 1u; };
    const u8 lanes[4] = {
        u8((x(5) ^ x(12)) | ((x(7) ^ x(9)) << 1) | (x(14) << 2)),
        u8(x(6) | (x(8) << 1) | (x(15) << 2)),
        u8((x(1) ^ x(8)) | (x(7) << 1) | (x(12) << 2)),
        u8(x(3) | (x(4) << 1) | (x(10) << 2))};
    const u8 affine = u8(x(0) | ((x(0) ^ x(2)) << 1) | ((x(11) ^ x(14)) << 2)
                         | ((x(4) ^ x(13)) << 3) | 16);
    u16 result = 0;
    for (unsigned group = 0; group < 4; ++group) {
        const u8 value = sboxes[group][lanes[routing[group]]];
        for (unsigned b = 0; b < 3; ++b)
            result |= u16(((value >> b) & 1u) << output_bits[group][b]);
        u8 parity = affine & affine_masks[group];
        parity ^= parity >> 4;
        parity ^= parity >> 2;
        parity ^= parity >> 1;
        result |= u16((parity & 1u) << affine_bits[group]);
    }
    return result;
}

void Sega3155838Comp::source_w(u32 data, u32 mask)
{
    m_source = ((m_source & ~mask) | (data & mask)) & 0x007fffffu;
    m_word = 0;
    m_bits = 0;
    m_abort = false;
    m_dummy = true;
    SM2_DEBUG("3170229 source %06x", m_source);
}

void Sega3155838Comp::table_w(u32 offset, u16 data)
{
    SM2_DEBUG("3170229 table %u %04x", offset & 1u, data);
    if (!(offset & 1u)) {
        m_upload_dictionary = (data & 0x80) != 0;
        if (m_upload_dictionary) m_dictionary_bytes = 0;
        else m_tree_words = 0;
    } else if (m_upload_dictionary) {
        if (m_dictionary_bytes < m_dictionary.size()) {
            m_dictionary[m_dictionary_bytes++] = u8(data >> 8);
            m_dictionary[m_dictionary_bytes++] = u8(data);
        }
    } else if (m_tree_words < m_tree.size()) {
        m_tree[m_tree_words++] = data;
    }
}

u8 Sega3155838Comp::decompress_byte()
{
    if (m_abort || m_tree_words != m_tree.size() || m_dictionary_bytes != m_dictionary.size())
        return 0xff;
    u16 code = 0;
    for (unsigned length = 1; length <= 12; ++length) {
        if (!m_bits) {
            const u16 encrypted = m_read ? m_read(m_source) : 0xffff;
            SM2_DEBUG("3170229 input %06x %04x", m_source, encrypted);
            m_word = decipher(encrypted);
            m_source = (m_source + 1) & 0x007fffffu;
            m_bits = 16;
        }
        code = u16((code << 1) | ((m_word >> --m_bits) & 1u));
        for (usize entry = 0; entry < m_tree.size(); entry += 2) {
            if ((m_tree[entry] >> 8) != length) continue;
            const u16 first = u16(m_tree[entry + 1] >> (12 - length));
            u16 limit = u16(1u << length);
            for (usize next = entry + 2; next < m_tree.size(); next += 2) {
                if (m_tree[next + 1] != m_tree[entry + 1]) {
                    limit = u16(m_tree[next + 1] >> (12 - length));
                    break;
                }
            }
            if (code >= first && code < limit) {
                const unsigned index = (m_tree[entry] & 0xffu) + code - first;
                if (index < m_dictionary.size()) return m_dictionary[index];
            }
        }
    }
    SM2_DEBUG("3170229 invalid compressed code at %06x", m_source);
    m_abort = true;
    return 0xff;
}

u16 Sega3155838Comp::data_r()
{
    m_output = u16(decompress_byte()) << 8;
    m_output |= decompress_byte();
    SM2_DEBUG("3170229 output %04x", m_output);
    return m_output;
}

u32 Sega3155838Comp::doa_read(u32 byte_offset, unsigned width)
{
    const auto halfword = [this]() -> u16 {
        if (m_dummy) { m_dummy = false; return 0; }
        return data_r();
    };
    const u32 low = halfword();
    if (width == 4) return low | (u32(halfword()) << 16);
    if (width == 1) return (low >> ((byte_offset & 1u) * 8)) & 0xffu;
    return low;
}

void Sega3155838Comp::doa_write(u32 byte_offset, u32 data, unsigned width)
{
    if (byte_offset < 4) {
        const unsigned shift = byte_offset * 8;
        const u32 mask = width == 4 ? 0xffffffffu : (width == 2 ? 0xffffu : 0xffu) << shift;
        source_w(data << shift, mask);
    } else {
        const unsigned half = (byte_offset - 4) / 2;
        table_w(half, u16(data << ((byte_offset & 1u) * 8)));
        if (width == 4) table_w(half + 1, u16(data >> 16));
    }
}

void Sega3155838Comp::serialize(Archive& ar)
{
    if (ar.format_version() < 14) {
        u32 legacy_offset = 0;
        ar.raw(legacy_offset);
        if (ar.loading()) reset();
        return;
    }
    ar.bytes(m_tree.data(), m_tree.size());
    ar.bytes(m_dictionary.data(), m_dictionary.size());
    ar.raw(m_tree_words);
    ar.raw(m_dictionary_bytes);
    ar.raw(m_upload_dictionary);
    ar.raw(m_source);
    ar.raw(m_word);
    ar.raw(m_bits);
    ar.raw(m_output);
    ar.raw(m_abort);
    ar.raw(m_dummy);
    if (ar.loading() && (m_tree_words > m_tree.size()
        || m_dictionary_bytes > m_dictionary.size() || (m_dictionary_bytes & 1u)
        || m_bits > 16 || m_source > 0x7fffff)) ar.invalidate();
}

} // namespace sm2::hw
