// SPDX-License-Identifier: BSD-3-Clause
#include "hw/model2_video.h"
#include "core/archive.h"
#include "libretro/gun_flash_state.h"
#include <algorithm>
#include <cstdio>
#include <stdexcept>
#include <vector>
using namespace sm2;
namespace {
void check(bool okay, const char* description) {
    if (!okay) throw std::runtime_error(description);
}
}
int main() {
    hw::Model2Video video;
    std::vector<u8> ram(0x10000), chars(0x80000, 0x11);
    video.attach(ram, chars, {}, {});
    auto mask = [&](bool full) {
        std::fill_n(ram.begin() + hw::Segaic24Tile::kWindowMaskAOffset,
                    hw::Segaic24Tile::kWindowMaskABytes, full ? 0xff : 0);
        video.latch_tile_ram(); // The display sees the change at VBlank.
    };
    mask(false); video.filter_gun_flash(true, 0xff);
    mask(true); const auto untouched = ram;
    video.filter_gun_flash(true, 0xfe);
    check(video.window_mask_a_hidden(), "Immediate player-one shot flash is hidden");
    check(ram == untouched, "Filter never changes emulated tile RAM");
    const auto saved = video.gun_flash_state();
    video.filter_gun_flash(true, 0xfe);
    check(!video.window_mask_a_hidden(), "Persistent full mask is preserved as a fade");
    video.reset(); video.set_gun_flash_state(saved);
    check(video.window_mask_a_hidden(), "Presentation state restores the current hidden frame");
    video.filter_gun_flash(true, 0xfe);
    check(!video.window_mask_a_hidden(), "Restored history preserves the following fade");
    mask(false); video.filter_gun_flash(true, 0xff);
    video.filter_gun_flash(true, 0xfd);
    mask(true); video.filter_gun_flash(true, 0xfd);
    check(video.window_mask_a_hidden(), "One-frame delayed player-two shot flash is hidden");
    mask(false); video.filter_gun_flash(true, 0xfd);
    mask(true); video.filter_gun_flash(true, 0xfd);
    check(!video.window_mask_a_hidden(), "Held trigger does not hide unrelated later full masks");
    for (const u8 trigger : {u8{0xfe}, u8{0xfd}}) {
        video.reset(); mask(false); video.filter_gun_flash(true, trigger);
        video.filter_gun_flash(true, trigger);
        const auto pending = libretro::gun_flash_state_from_flags(
            libretro::gun_flash_flags(video.gun_flash_state()));
        mask(true); video.filter_gun_flash(true, trigger);
        check(video.window_mask_a_hidden(), "Two-frame delayed shot flash is hidden for either player");
        video.set_gun_flash_state(pending);
        video.filter_gun_flash(true, trigger);
        check(video.window_mask_a_hidden(), "Restored pending shot hides the two-frame delayed flash");
        mask(false); video.filter_gun_flash(true, trigger);
        mask(true); video.filter_gun_flash(true, trigger);
        check(!video.window_mask_a_hidden(), "Expired shot history does not hide a later mask");
    }
    video.reset(); mask(true); video.filter_gun_flash(true, 0xff);
    video.filter_gun_flash(true, 0xfe);
    check(!video.window_mask_a_hidden(), "Shooting during an existing fade does not remove it");
    video.reset(); mask(false); video.filter_gun_flash(false, 0xff);
    mask(true); video.filter_gun_flash(false, 0xfe);
    check(!video.window_mask_a_hidden(), "Disabled option preserves the flash");
    video.set_gun_flash_state(saved); video.filter_gun_flash(false, 0xfe);
    check(!video.window_mask_a_hidden(), "Disabling clears an active suppression");
    video.set_gun_flash_state(saved); video.reset();
    check(!video.window_mask_a_hidden() && !video.gun_flash_state().triggers_held,
          "Machine reset clears all transient flash history");
    for (const u8 age : {u8{0}, u8{1}, u8{2}, u8{0xff}}) {
        auto state = saved; state.frames_since_press = age;
        const auto flags = libretro::gun_flash_flags(state) | (1u << 5) | (1u << 7)
            | (1u << 8) | (1u << 9);
        const auto restored = libretro::gun_flash_state_from_flags(flags);
        check(restored.frames_since_press == age && restored.triggers_held == state.triggers_held
            && restored.window_mask_full == state.window_mask_full && restored.hidden == state.hidden,
            "Presentation flags retain every latency phase without overlapping other state fields");
    }
    const auto legacy = libretro::gun_flash_state_from_flags(0x47460000u | 1u | (1u << 2));
    check(legacy.triggers_held == 1 && legacy.frames_since_press == 0,
          "Legacy preceding-press flag restores pending shot history");
    check(libretro::gun_flash_state_from_flags(0).frames_since_press == 0xff
        && libretro::gun_flash_state_from_flags(0x47460000u).frames_since_press == 0xff,
          "Legacy empty history does not invent a pending shot");
    std::vector<u8> archive; Archive writer(archive); video.serialize(writer);
    check(archive.size() == 4, "Machine video archive layout remains two words");
    video.set_gun_flash_state(saved); Archive reader(archive.data(), archive.size());
    video.serialize(reader);
    check(!reader.failed() && !video.window_mask_a_hidden(), "Machine load clears transient history");
    // Exercise actual tile drawing, including the complementary window layer.
    std::vector<u32> pens(4096, 0xffaabbcc), pixels(496*384);
    video.tiles().update(); mask(true);
    video.tiles().draw(0, false, pens, pixels.data(), 496);
    check(std::all_of(pixels.begin(), pixels.end(), [](u32 p){ return p == 0; }),
          "Normal full window excludes the background layer");
    video.tiles().set_window_mask_a_hidden(true);
    video.tiles().draw(0, false, pens, pixels.data(), 496);
    check(pixels.front() == 0xffaabbcc && pixels.back() == 0xffaabbcc,
          "Hidden mask restores the background across the visible raster");
    std::fill(pixels.begin(), pixels.end(), 0);
    video.tiles().draw(2, false, pens, pixels.data(), 496);
    check(std::all_of(pixels.begin(), pixels.end(), [](u32 p){ return p == 0; }),
          "Complementary foreground window stays hidden");
    std::puts("All gun-flash detection, reset, RAM and tile-drawing checks passed");
}
