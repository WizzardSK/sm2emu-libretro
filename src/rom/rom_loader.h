//  ____  __  __  ____         _____ __  __ _   _
// / ___||  \/  ||___ \       | ____|  \/  | | | |
// \___ \| |\/| |  __) |_____ |  _| | |\/| | | | |
//  ___) | |  | | / __/|_____|| |___| |  | | |_| |
// |____/|_|  |_||_____|      |_____|_|  |_|\___/
//
// A Sega Model 2 arcade emulator.
// Copyright (c) 2025+ Daniel Martin (dmanlfc)
// SPDX-License-Identifier: BSD-3-Clause
//
// This header must not be removed. The source files in this project may not be
// used to contribute to commercial projects or for monetary gain without the
// express written permission of the author.
//
#pragma once

#include "core/types.h"
#include "rom/game.h"
#include "rom/rom_set.h"

#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace sm2::rom {

class GameDatabase;

struct LoadResult {
    GameSpec game;
    RomSet   roms;
};

/// Reads a zip archive and assembles the ROM regions for whichever game it
/// holds.
///
/// Games are identified by CRC32-checked chips. A known archive name selects
/// its set when all declared main-program chips match, even if other regions
/// need a split parent. Unknown/renamed archives use the best whole-set score.
/// Diagnostic callers may disable CRC verification and match filenames instead.
class RomLoader {
public:
    /// Load only the requested regions, with every declared chip required.
    /// Search the selected archive first, then the supplied sibling sets.
    /// Used for optional alternate hardware without changing game identity.
    [[nodiscard]] static std::optional<RomSet> load_regions(
        const GameSpec& game, const std::string& archive_path,
        std::span<const std::string_view> regions,
        std::span<const std::string_view> sibling_sets);

    /// Assemble the ROMs in `archive_path`.
    ///
    /// When `preferred_game` is non-empty only that set is considered, which is
    /// how a specific revision inside a merged archive is selected. Otherwise
    /// a known archive name with matching main-program chips takes precedence;
    /// otherwise every definition is tried and the best whole-set match wins.
    ///
    /// Parent ROMs missing from a clone's archive are looked for in
    /// `<parent>.zip` beside it, matching the usual split-set layout.
    /// Device archives may additionally be read from `device_directory` before
    /// the sibling directory; the standalone default keeps the sibling-only
    /// search. The path is supplied by the caller, not inferred from a frontend.
    /// `verify_crc=false` is a diagnostic fallback; ordinary callers retain
    /// the verified default.
    [[nodiscard]] static std::optional<LoadResult> load(const GameDatabase& database,
                                                        const std::string&  archive_path,
                                                        const std::string&  preferred_game = {},
                                                        bool verify_crc = true,
                                                        const std::string& device_directory = {});

    /// Assemble one region from already-extracted file contents.
    ///
    /// Exposed so the interleaving can be tested directly, without a zip: it is
    /// the part most likely to be subtly wrong, and getting it wrong produces
    /// plausible-looking but scrambled data.
    [[nodiscard]] static std::optional<std::vector<u8>> assemble_region(
        const RegionSpec&                         region,
        const std::vector<std::vector<u8>>&       file_contents);

    /// Size a region needs in order to hold every file it declares.
    [[nodiscard]] static usize computed_region_size(const RegionSpec&         region,
                                                   const std::vector<usize>& file_sizes);

    /// Write every assembled region to `directory` as a raw binary file.
    ///
    /// For cross-checking against MAME, whose debugger can dump the equivalent
    /// region. An interleaving mistake produces data of exactly the right size,
    /// so comparing bytes against a known-good reference is the only way to be
    /// certain the layout is right.
    [[nodiscard]] static bool dump_regions(const RomSet&      roms,
                                           const std::string& directory);
};

}  // namespace sm2::rom
