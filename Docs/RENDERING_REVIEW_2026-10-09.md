# Rendering and Video Options Review — 2026-10-09

## Scope and Source Audit

This closes the renderer review of the already approved upstream candidate
group at `2e056f29109d319fe8eb58e6a7fbd323b531ced7`. The full integrated
baseline remains `5ddf84ae7970a9bce1d0a17b3900d26065de1996` (0.9.13), with
the documented selected backports. It is not a new upstream fetch or a claim
that the complete later emulator has been imported.

| Upstream Change | Implementation and Existing Evidence |
| --- | --- |
| `277a482` Whole-Polygon Texture Interpolation | Shared geometry, shader and Vulkan/OpenGL buffers; `UPSTREAM_TEXTURE_WARP_PACKAGE_2026-10-08.md` |
| `609c3c5` Resolution Through 8× | Existing Libretro scale choices and device dimension guard; `UPSTREAM_RESOLUTION_PACKAGE_2026-10-08.md` |
| `d0db61c` Top Skater Skinning | Neutral geometrizer correction; `UPSTREAM_GEOMETRY_SHADOW_PACKAGE_2026-10-08.md` |
| `2c4e9e2` Shadow Detail | Black point 40 in Software and shared GPU tone curve; same geometry/shadow report |
| `96e0f0e` Hide Shot Flash | Existing universally visible Input option, default Disabled; `UPSTREAM_GUN_FLASH_PACKAGE_2026-10-08.md` |
| `7080210`, `e36f757` Virtual On Water and Texture Timing | Integrated with CPU/bus waits; `UPSTREAM_I960_PACKAGE_2026-10-08.md` |

No further shared renderer correction was identified in that reviewed range.
`29620d3` also guards the standalone VulkanBackend ImGui artwork descriptor
pool. Libretro does not instantiate that SDL/swapchain backend; its per-game
volume feature is already adapted through Core Options. Other changes to
standalone GUI/device controls retain their documented port adaptations.
The current Software rasterizer matches the reviewed upstream file byte for
byte. `source-audit.json` records revisions and hashes of the inspected sources.

## OpenGL Context-Loss Correction

`Poly3DPass::abandon_context()` reset its vertex and polygon buffer records but
omitted the geometry buffer introduced by the texture-interpolation import.
The Libretro context-reset path abandons the old context before destroying its
renderer object. An uncleared geometry handle could therefore reach
`destroy_persistent_buffer()` and request an unmap/delete of a buffer belonging
to the dead context, potentially colliding with a name in the new context.

The correction adds `m_geometry_buffer = {}` alongside the other abandoned
buffers. It does not issue OpenGL calls against the lost context, change the
geometry algorithm, or alter machine timing, audio, inputs, states or options.
The risk is established from the teardown path; this report does not claim a
reproduced old-build crash on every driver.

## Frontend Save RAM Evidence

The older GPU smoke runners hashed the native save directory, which remains
empty when Libretro exposes frontend-managed Save RAM. Thus GPU reports with
`"nvram": {}` did not prove NVRAM equality. Their image/audio and lifecycle
results remain separate evidence.

All three existing runners now use one shared `capture_save_ram()` helper in
`smoke-libretro.py`. It reads `RETRO_MEMORY_SAVE_RAM` before unloading, validates
the 16,576-byte version-1 container, native lengths, game identity and payload
CRC, retains a `.srm`, and reports actual Backup RAM/EEPROM hashes. No Service
Menu campaign or user save is modified. Existing empty GPU references must be
reacquired when a comparison needs NVRAM proof.

## Verification Method

Evidence root: `build-libretro-gpu/validation/rendering-review-20261009/`.
The bounded matrix uses Daytona (original Model 2), VF2 (2A), Virtual On (2B)
and Top Skater (2C/DSB2), 1,800 frames per case, native cadence, 1×, Faithful
filters and isolated fresh automatic NVRAM. It reuses `smoke-libretro.py`,
`smoke-vulkan.py` and `smoke-opengl.py`.

Software pixel comparisons explicitly use
`sm2_software_renderer_threading=synchronous` and require that choice in the
log. Initial probes accidentally used an unrecognized shorthand key and
therefore retained the default asynchronous, previous-frame presentation.
Those captures remain diagnostic evidence; only the corrected synchronous
runs are used for the aligned pixel review.

Linux uses the existing Debian 12 amd64/Rosetta builder, GCC 12, LTO and the CI
renderer flags, with Mesa `EGL_PLATFORM=surfaceless LIBGL_ALWAYS_SOFTWARE=1`.
The first EGL launch omitted those documented variables and failed at
`eglInitialize`; that attempt is retained separately. ROMs are streamed only
to `/tmp` inside a disposable container and never stored in its image or the
reusable build volume. Windows/Batocera gameplay is not requalified here.

## Results

Software and Vulkan pass all four macOS cases. Complete PCM and native NVRAM
match exactly for each title. The corrected aligned images differ by 2,192
pixels for Daytona, 2,390 for VF2, 6,221 for Virtual On and 1,242 for Top Skater
out of 190,464 pixels. Mean absolute channel errors are respectively 0.142,
0.092, 0.238 and 0.062 on the 0–255 scale. These are distinct rasterizers;
cross-backend pixel identity is not an acceptance requirement.

The old/new macOS Vulkan VF2 control matches exactly in final pixels, complete
PCM and actual NVRAM. Core, headless and standalone macOS builds pass; the
Linux core/EGL host build and ABI/dependency audit pass. Existing gun-flash and
Save RAM checks pass. The final matrix and independent receipts are retained
in `final-review.json`, `linux-results/linux-results.json` and the per-run
directories.

| Final Check | Result |
| --- | --- |
| Four titles, Software/Vulkan/Mesa desktop GL/GLES | All 16 runs complete 1,800 frames; native SRAM identity, lengths and CRC are valid |
| Native NVRAM across all four paths | Exact payload equality for each title |
| Same macOS core, Software/Vulkan PCM | Exact for all four titles |
| Same Linux core, desktop GL/GLES | Exact final pixels, entire PCM and actual NVRAM for all four titles |
| VF2 GLES and desktop GL unannounced context loss at frame 900 | Both deliver a valid hardware frame after recreation and match uninterrupted pixels, PCM and NVRAM; no duplicate frames |
| Previous/current core, macOS Vulkan VF2 | Exact pixels, PCM and NVRAM |
| VF2 Linux Software control | Exact PCM/NVRAM against the same Linux OpenGL core |
| Actual macOS RetroArch VF2 Vulkan 2× | 2,300 frames, gameplay, audio, SRAM and normal exit |

MoltenVK versus Mesa differs by 214 pixels for Daytona, 389 for VF2, 447 for
Virtual On and 129 for Top Skater out of 190,464 pixels. All four cross-platform
PCM comparisons have the same sample count and maximum sample error 1.
These observations do not establish pixel/audio identity across drivers and
toolchains, or a performance benchmark. Existing matched upstream and old/new
package comparisons remain the separate source-import qualification.

### Cross-Platform Audio Control

VF2's Linux PCM differs from macOS at 3,384 of 2,759,884 signed 16-bit samples,
with maximum absolute error 1 and the same sample count/rate. A Software control
using the exact same Linux core matches Linux OpenGL PCM and NVRAM byte for
byte. This identifies a cross-platform difference independent of choosing
OpenGL versus Software. The specific compiler/arithmetic cause was not proven;
no audio correction is included or required to close this renderer review.
`vf2-cross-platform-audio-review.json` retains that separate result.

### Actual RetroArch

RetroArch Nightly 1.22.2 macOS arm64 runs VF2 with the candidate core, Vulkan 2×,
native cadence and isolated input replay for 2,300 frames. The capture shows
gameplay; the recording is non-silent (peak 19,781), Save RAM is 16,576 bytes,
and exit status is 0 after 45.4 seconds. This is frontend evidence on macOS,
not a physical-controller or subjective listening qualification.

## Installed Artifacts and Roadmap

Both installed local cores, `sm2_libretro.dylib` and `sm2_dev_libretro.dylib`,
were replaced atomically after verification and match the tested macOS SHA-256:
`3200f0e99a527d186def9cced15f82e70e564c39e8e70881f02fae083dbc3d05`.
The tested Linux artifact SHA-256 is
`a7572a2865e757d5cc6eb17717428fa9216312c83c5f88a367ab9d032da5d80f`.
`deployment.json` retains previous hashes and backup paths. No test-owned
RetroArch process remains running; the shared Colima profile is left available.

Rendering and Video Options is complete for the approved candidate group and
the bounded verification above. Physical-device, subjective audio and deferred
feature work retain their existing roadmap status. Manx TT Relay remains the
final activity by user request. No Core Option label, key, ordering, saved value
or default changed, and no other project was edited. No commit or push was made.
