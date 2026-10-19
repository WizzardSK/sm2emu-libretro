// SPDX-License-Identifier: GPL-3.0-or-later AND BSD-3-Clause
//
// Derived from MAME's src/mame/sega/315-5838_317-0229_comp.cpp/.h
// (BSD-3-Clause, copyright-holders David Haywood, Samuel Neves, Peter
// Wilhelmsen, Morten Shearman Kirkegaard).
#pragma once

#include "core/types.h"
#include <array>
#include <functional>
#include <utility>

namespace sm2 { class Archive; }

namespace sm2::hw {

/// Sega 317-0229 word substitution and programmable prefix decompression.
/// Adapted from MAME 6743eb674d07. The source callback supplies little-endian
/// i960 RAM words; the decoder consumes their transformed bits MSB first.
class Sega3155838Comp {
public:
    void reset();
    void set_read_callback(std::function<u16(u32)> callback) { m_read = std::move(callback); }
    [[nodiscard]] static u16 decipher(u16 ciphertext);
    [[nodiscard]] u16 data_r();
    void source_w(u32 data, u32 mask = 0xffffffffu);
    void table_w(u32 offset, u16 data);

    /// Model 2's output bus discards an initial read after each source write.
    [[nodiscard]] u32 doa_read(u32 byte_offset, unsigned width);
    void doa_write(u32 byte_offset, u32 data, unsigned width);
    void serialize(Archive& ar);

private:
    [[nodiscard]] u8 decompress_byte();
    std::function<u16(u32)> m_read;
    std::array<u16, 24> m_tree{};
    std::array<u8, 256> m_dictionary{};
    u8 m_tree_words = 0;
    u16 m_dictionary_bytes = 0;
    bool m_upload_dictionary = false;
    u32 m_source = 0;
    u16 m_word = 0;
    u8 m_bits = 0;
    u16 m_output = 0xffff;
    bool m_abort = false;
    bool m_dummy = true;
};

} // namespace sm2::hw
