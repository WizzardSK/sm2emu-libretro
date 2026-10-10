# Upstream Geometry and Shadow Detail Package — 2026-10-08

## Imported Changes

- `d0db61cf14cb50454cfd60ada6687d0fadc53c22`: Top Skater skinning matrix
  correction. Command 0x1b supplies the second matrix used by compact vertices
  whose raw X low bit selects the next joint. Removes the previous character
  ROM-range backface-culling exemption.
- `2c4e9e2e4d273d17d03951940e41c4d911507ca4`: black point changes from 64 to 40
  in both the Software renderer and the shared video tone curve, retaining
  detail previously crushed in shadows.

`geometrizer.cpp` and `.h` match upstream `d0db61c` byte-for-byte;
`model2_video.cpp` and `model2_softrender.cpp` match upstream `2c4e9e2`
byte-for-byte. The corresponding six-line Top Skater exemption is removed
from `model2c.cpp`, preserving the port's existing sound-board integration.
No Core Options, saved option values, dependency pins or controls were changed.
The complete baseline remains 0.9.13 with the explicitly recorded backports.

## Scope and Dependencies

Virtual-On changes `7080210` and `e36f757` add i960 bus wait cycles across the
boards and per-game texture timing. They remain with the CPU timing review,
including the later per-area wait-table implementation `1987d82`, rather than
being presented as a shader-only correction. Their integration is still open.

The geometry change preserves the two serialized words formerly used for the
removed culling range, reading and discarding them when loading. State layout
and the 9,437,184-byte Libretro ABI buffer remain unchanged. Legacy-state and
deterministic replay checks below qualify this behavior on the tested titles.

## Verification

Evidence root: `/tmp/sm2-geometry-package-20261008/`.

| Check | Result |
| --- | --- |
| macOS Release core, headless and standalone | Build passed |
| Linux x86_64 core and EGL test host | Build passed with the existing builder and dependencies |
| Old/new Software core, Daytona, VF2, STCC, Virtual-On and Top Skater | 1,800 frames each; complete PCM unchanged, rendered images changed |
| Save State on the same five titles | Round-trip, deterministic replay, corrupt-state rejection, 20 stress cycles, run-ahead and reverse rewind patterns passed |
| Old states loaded by the updated core in fresh processes | All five loaded, advanced 180 frames and passed the same 20-cycle state checks |
| Headless versus controlled upstream reference | All five titles match video, PCM format/data, NVRAM, frame/cycle counts and CPU state at 1,800 frames |
| Top Skater Vulkan | 1,800 hardware frames completed |
| Top Skater Mesa desktop GL versus GLES | 600 frames each; image, PCM and NVRAM match exactly |
| Installed core in RetroArch Nightly 1.22.2 macOS, Vulkan 2× | 2,300 frames, inspected gameplay capture, non-silent recorded audio, 16,576-byte Save RAM, exit 0 |

Aggregate machine/state evidence: `matrix-result.json`. Renderer evidence is
in `vulkan-topskatr`, `gles`, `gl` and `retroarch-topskatr`.

### Reference Construction

The controlled standalone reference is an upstream 0.9.13 Git archive
(`5ddf84ae7970a9bce1d0a17b3900d26065de1996`) with precisely the two imported
patches applied, excluding their version-number bumps. It has matching pinned
submodules and no Libretro adapter. This is an explicitly patched upstream
reference, **not a pristine checkout of the complete later upstream revision**.
Using the complete later revision would also introduce pending CPU/audio/game
changes and would not isolate this package. The earlier pristine 0.9.13 and
texture-interpolation comparisons are documented in the preceding reports.
No whole-upstream 0.9.40 equivalence is claimed.

These checks establish the selected changes on the tested frames and boards.
The RetroArch capture confirms gameplay and a connected character model in
that scene; it is not an exhaustive audit of every animation. Windows and
Batocera gameplay and subjective audio quality were not requalified here.

## Local Installation

Both local RetroArch cores (`sm2_libretro.dylib`, `sm2_dev_libretro.dylib`)
were atomically replaced and verified against the final build. SHA-256:
`d54354e5bd80669a6b0ea428c5ca454c7928cc3176a24d0a26ca85df2a8e14f2`.
Previous copies are in `installed-backup` under the evidence root.
The adjacent mainstream checkout remains clean. No commit or push was made.
