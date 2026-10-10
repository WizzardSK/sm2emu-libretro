# Upstream Internal Resolution Package — 2026-10-08

## Imported Change

`609c3c53f0d8b48555a992df9d4e6fe7da3a86de` extends internal GPU rendering
from 1×–4× to 1×–8×. Its changes to `render/backend.h`, `core/config.cpp`
and `osd/gui.cpp` are imported; the standalone CLI help is adapted to the
older baseline's surrounding text. The complete integrated upstream baseline
remains 0.9.13 plus the separately recorded backports.

The Libretro Internal Resolution option adds:

| Value | Menu Label |
| --- | --- |
| `5` | 5x (2480 x 1920) |
| `6` | 6x (2976 x 2304) |
| `7` | 7x (3472 x 2688) |
| `8` | 8x (3968 x 3072) |

The existing key, labels/values 1–4, default 1×, restart requirement and
Software native resolution remain unchanged. 8× is 3968 × 3072 internally;
final display scaling and aspect remain frontend responsibilities.

## Libretro Adaptation

Both Vulkan and OpenGL use the existing upstream dimension-clamp helper.
OpenGL considers the smaller of maximum texture and renderbuffer dimensions;
Vulkan uses `maxImageDimension2D`. A device that cannot hold even native
resolution fails explicitly. A reduced scale is logged.

Renderer initialization returns the effective scale. The adapter retains the
requested scale separately, publishes changed base geometry with
`SET_GEOMETRY`, and reserves maximum geometry for the request. Context
recreation retries the requested scale. The stored Core Option is not rewritten
when device limits reduce the effective scale.

This guards target dimensions; it does not retry at a lower scale after an
allocation failure due to exhausted memory. No CPU, audio, machine state,
controls or serialization format changes are involved.

## Verification

Evidence root: `/tmp/sm2-resolution-package-20261008/`.

| Check | Result |
| --- | --- |
| macOS core, headless and standalone | Builds passed |
| Linux x86_64 Software/Vulkan/OpenGL core and EGL host | Build passed with the existing builder/dependencies |
| Registered Core Option | All eight labels/values, terminator and unchanged 1× default verified |
| Dimension-clamp helper | 61,576 request/limit combinations verify valid bounds and largest fitting scale; includes 4096→8×, 2048→4×, 1024→2× |
| VF2 Vulkan 8× | 600 hardware frames; context recreated at frame 300, sync-mask changes and three load/reset/unload cycles passed |
| VF2 Vulkan old/new 4× | 600 frames each; final image, complete PCM and NVRAM comparison identical |
| Mesa GLES/desktop GL 8× | 60 hardware frames per API; image, PCM and NVRAM identical; GLES context recreated at frame 30 |
| VF2 Software and Save State | 600 frames; round-trip, deterministic replay, corrupt-state rejection, five stress cycles, run-ahead and rewind patterns passed; PCM matches Vulkan |
| Existing Save RAM/Core Options checks | Passed, including Gain conventions and legacy values |
| Installed development core, RetroArch Nightly 1.22.2 macOS Vulkan 8× | 2,300 frames; log confirms 3968 × 3072, gameplay capture inspected, non-silent audio recording, 16,576-byte Save RAM, exit 0 in 45.7 seconds |

The imported upstream scale/configuration changes are compared directly with
the selected patch. No raster algorithm changes belong to this package; the
old/new 4× comparison checks the previous rendering range. This package does
not claim equivalence with the complete later upstream revision.

The original 600-frame Mesa run with extra lifecycle cycles was stopped because
software rendering at 8× was too costly for this bounded API check. It was
replaced by the completed 60-frame runs above with per-run 120-second limits.
These short Mesa runs qualify API setup, dimensions and context recreation;
they do not establish gameplay. Evidence is in `gles` and `gl`.

The physical GPU supports 8×, so automatic reduction was tested as helper
logic rather than on a physically dimension-limited GPU. Gameplay and audio
recording evidence comes from macOS Vulkan. Subjective sound quality, physical
controllers, Windows and Batocera gameplay were not requalified here.

## Local Installation

Both `sm2_libretro.dylib` and `sm2_dev_libretro.dylib` in the local RetroArch
cores directory were replaced atomically and match the final build:

`b1b2bc6f4b4a55219dfa5216c3ea0640239d81623062a316eb1b778e5841e5ad`

Previous binaries are preserved in `installed-backup` under the evidence root.
The adjacent mainstream checkout is clean. No commit or push was made.
The next rendering item is the optional lightgun shot-flash filter, including
input-driven and Save State validation. Virtual-On CPU wait-state changes
remain with the extra-analysis items at the end of the roadmap.
