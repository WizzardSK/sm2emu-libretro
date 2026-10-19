# Custom Crosshairs And Inactivity Timeout

Status: Implemented Locally, Not Yet Released

Date: 2026-10-19

## Scope

Adapt upstream `9df5924` (inactive crosshairs) and `1b07067` (user PNGs) to
the existing Libretro reticle pipeline. Upstream bezels remain excluded as a
frontend facility. Wheel spring/DIP/gain changes in `1467a24` remain excluded:
they alter standalone wheel simulators, not the command decoder used by the
adapter's gamepad rumble.

## Options And Files

- **Crosshair Style:** Auto, SM2-Emu (unchanged default), Supermodel, Custom.
  Existing saved `sm2` and `supermodel` tokens remain valid. Auto falls back to
  SM2-Emu independently per player. Custom requires usable artwork and reports
  missing/invalid files once per selected player, without silent substitution.
- **Crosshair Inactivity Timeout:** Disabled (default), 1–8, 10, 15, 30 or
  60 seconds. Each player's aim/fire activity restarts its timer; an unused
  player's reticle stays hidden while this option is enabled. Visibility masks
  and off-screen rules retain priority. Native game reticles are unaffected.
- PNG directory: `<frontend system directory>/sm2-emu/crosshairs/`.
  Search game-player, game, parent-player, parent, default-player, default:
  e.g. `hotd-p1.png`, `hotd.png`, parent equivalents, `default-p1.png`,
  `default.png`. Transparent PNGs up to 1024×1024 and 16 MiB per file are accepted. Dimensions scale
  from a 1080-line reference, matching upstream. Artwork is user-supplied.
- Files are cached. Reload content after editing PNGs, or return to game with
  a built-in style before selecting Auto/Custom again. Invalid higher-priority
  candidates do not prevent trying a usable parent/default image.

Timers advance with emulated time, stop while the core is paused and advance
with fast-forward. They and user artwork are presentation state, not native
inputs, NVRAM data or Save State payload. Existing state size/layout is unchanged.
The existing local Linked Cabinets label/help edits were preserved; their
registration check now follows the shared value definition.

## Implementation

`CrosshairPresentation` in `src/libretro/crosshair.*` owns per-content artwork
and timers. Immutable images remain valid for pending asynchronous Software
frames. Normalized input activity comes from the existing source arbitration;
no SDL dependency or device ownership enters the adapter. Non-gun games do not
load artwork or emit missing-artwork notifications.

All renderers share clipped geometry. Software blends ARGB into XRGB8888;
Vulkan/OpenGL use the existing ImGui alpha-composition path for custom images,
including when the timing panel is disabled. Built-in GPU reticles retain their
existing path. No custom texture handles need rebuilding after context loss.
The existing vendored stb decoder is linked only for standalone/core targets;
the frontend-free runner remains independent. Decoder notices are included in
the binary package inventory and matching-source checks.

## Verification

- Core with Vulkan and OpenGL, frontend-free runner, input checks, Save RAM /
  Core Options checks and timing-overlay checks compile successfully on macOS
  arm64. The three ROM-free check executables pass.
- Input checks cover PNG decoding, malformed candidates, parent/player and
  default/player lookup, Auto fallback, explicit styles, missing-Custom notices,
  alpha blending, clipping/scaling and independent inactivity behavior.
- Overlay checks cover custom geometry with the timing panel disabled and
  custom geometry together with the timing panel.
- Isolated Virtua Cop Software and real Vulkan probes: 120 frames each,
  custom versus no-reticle baseline. The final custom frames match exactly
  between Software and Vulkan. All 722 changed pixels satisfy the PNG's
  128/255 alpha blend within one channel unit. Audio and NVRAM hashes remain
  identical to their respective baselines. Vulkan context recreation at
  frame 60 succeeds.

- RetroArch 1.22 Vulkan/MoltenVK: isolated 2,300-frame Virtua Cop run with
  Custom selected and a gun-input replay completes with exit code 0, captured
  frame/audio and valid 16,576-byte SRAM. The matching 1.22 replay reader was
  selected. The captured scene was inspected; this is bounded frontend playback,
  not full-game or physical-device qualification.

Evidence: `build-libretro-gpu/validation/crosshairs-20261019/`, including
`comparison.json` and the individual probe reports. Initial Vulkan attempts
inside the sandbox could not create a driver instance; the same probe succeeds
with native GPU access. The first RetroArch attempt used the wrong replay
reader format and is retained as failed evidence; it does not qualify input.

Native OpenGL runtime is not qualified on this macOS host. Physical lightguns
and a broad image/game/device campaign are not claimed by these checks.
At completion of the crosshair-only step, the installed core matched SHA-256:
`b664743eb1d1a3848d29edd95bee5a241e8a530a695d65ad3efbc2bfe189728e`.
Installed core-info matches the source. No dev copy or old-binary backup was
created. Runtime version stays 0.9.51.2 until a separately authorized release.
The subsequent MAME audio/DOA integrations supersede that installed hash. See
`build-libretro-gpu/validation/doa-protection-20261019/deployment.json` for the
combined core. Publication was subsequently authorized; no new release is
included in that commit/push request.
