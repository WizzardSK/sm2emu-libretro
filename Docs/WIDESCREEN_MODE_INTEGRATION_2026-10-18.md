# Widescreen Mode Integration — 2026-10-18

## Approved Contract

Video places **Widescreen Mode** immediately after **Aspect Ratio**. The choices
are **Disabled** (default, raw `stretch`) and **Expand 3D View Only** (raw
`expand_3d`). The raw Disabled token preserves the agreed historical convention
without changing saved configuration. Unknown/missing values fall back to
Disabled. Modern and legacy registration use the same values/default.

| Aspect Ratio | Disabled | Expand 3D View Only |
| --- | --- | --- |
| Auto | Preserve native aspect selection | Expand applicable GPU content and report 16:9 |
| 4:3 | Original rendering, 4:3 presentation | Expansion suppressed; original 4:3 presentation |
| 16:9 | Original rendering, whole-image stretch | Expand applicable GPU content and report 16:9 |

The option never rewrites Aspect Ratio. Changes apply on return to the game,
without a reset or content reload. Software retains original rendering and
normal Aspect Ratio behavior. Native-widescreen families Indy 500, STCC and
Super GT 24h retain Auto, cabinet/Service Menu/NVRAM selection and manual aspect
overrides regardless of Widescreen Mode. The option remains visible for all
content; those exclusions are no-ops.

This incorporates the user's latest clarification in this chat and the approved
Supermodel/TGPulse handoff: Auto and 16:9 allow expansion; forced 4:3 takes
priority. It supersedes the briefly proposed unconditional 16:9 override.

## Implementation And Provenance

Shared changes derive from upstream
`338ce10543ec91725737009faa2a3a8f0bcc12c1`, retaining original source layout:

- Wider geometry clipping/projection and screen-edge visibility tests, including
  the Model 2B i960/SHARC paths. The original 4:3 polygon count remains the
  game's load-balancing input.
- GPU tilemap composition, per-game `side_fill`, panorama tracking and the
  original Model 2 Daytona sky reader. The native picture grows from 496×384 to
  662×384 (83 columns each side) before the selected internal-resolution scale.
- Native-proportion HUD/foreground layers. Background sides use the game's sky,
  previously seen panorama pixels, wrapping, mirrored edges or black according
  to the upstream rules. This is not a 2D stretching selector.
- Expanded horizontal serial-gun ranges and positional-gun end-segment
  extrapolation with ADC saturation. Existing selectable gun mappings and
  explicit off-screen status remain authoritative; aiming at a side column
  does not itself request reload.

Libretro owns option policy, geometry reports, renderer target resizing,
frontend context lifetime, crosshairs and timing overlay. Vulkan resolves the
added buffer commands from the frontend's existing device. OpenGL/GLES use the
same upstream composition shader. The port's VBlank-latched tile RAM remains
both the composition and panorama source. Standalone-only Aspect/menu/input
ownership and unrelated upstream prerequisites are not imported.

Save State payload layouts are unchanged. Device/program visibility patches
are reapplied through the existing machine interfaces; no new compatibility
container or migration is introduced. GPU panorama caches are presentation
history, not additional machine-state payloads.

## Verification

Evidence is retained under
`build-libretro-gpu/validation/widescreen-20261018/`.

| Check | Result And Boundary |
| --- | --- |
| macOS GPU core, standalone and frontend-free builds | Pass; Vulkan and OpenGL passes compile. Software-only core also builds. |
| Linux x86_64 build | Pass through the existing Colima/Rosetta recipe, with Software/Vulkan/OpenGL and static GCC/C++ runtimes. Final option-policy checks pass after the last precedence correction. |
| Input and option/save-RAM checks | Pass on macOS/Linux. Cover labels/default/order, Auto/4:3/16:9 policy, native-family exclusions, Software exclusion, unchanged saved Aspect Ratio and expanded P1/P2 gun travel. |
| Previous core versus Disabled | VF2 Software and Vulkan image, PCM and NVRAM hashes match. Final forced 4:3, Disabled/Auto and Disabled/16:9 Vulkan runs also match the previous core's raw rendered image/PCM/NVRAM. |
| Pristine upstream comparison | Same-revision pristine standalone versus port headless at 300 frames: Daytona (original), VF2 (2A), Sega Rally (2B) and HOTD (2C) match software video, PCM, NVRAM, cycles and CPU state. This qualifies the unexpanded machine path. |
| Expanded Vulkan | Real Apple M4 GPU: 662×384 output, context destruction/recreation, synchronization-index changes and live Stretch/Expand switching pass. Final Auto and explicit 16:9 expansion pass; forced 4:3 suppresses it. |
| Native aspect exclusion | Super GT 24h remains 496×384 with Expand selected: Auto follows native Type B as 16:9; forced 4:3 remains 4:3. The other native families are covered by policy checks. |
| OpenGL and GLES | Mesa software GPU in an ephemeral Linux container: both APIs complete 600 expanded frames and context recreation. Their final image hashes match. ROMs and frontend saves are not stored in a reusable build volume/image. Renderer tests use explicit 16:9; the final shared policy is separately checked after rebuilding. |
| Save States | Old VF2 state continuation matches the previous core's image/PCM/NVRAM. Expanded VF2 and Daytona GPU Save State round-trips reproduce image and PCM. |
| Actual RetroArch | macOS Vulkan VF2 completes the 2,300-frame gameplay replay with expanded output, including the final Auto + Expand rule, screenshot, audio capture and clean exit. This is scripted gameplay evidence, not physical-controller or subjective-audio qualification. |

The first RetroArch launch stopped inside Ozone texture loading before the
first emulation frame (local filesystem page-in error). The isolated repeat
uses RGUI and passes. This local frontend incident is not a Framework rule or
an emulation correction.

Expansion remains experimental. The game may omit objects beyond its original
view, and mirrored/cached backgrounds are approximations. The bounded checks do
not establish perfect rendering for every set, extended physical lightgun
accuracy, or native Windows/Batocera frontend behavior. GPU dimension limits
can reduce the effective internal scale to accommodate the wider targets.

## Delivery

Only the configured normal macOS `sm2_libretro.dylib` is updated after checks,
with build/install SHA-256 equality recorded in `summary.json`. No dev copy or
replaced-binary backup is created. No source commit, push or release is included.
Current configured `games.xml` already contains the upstream side-fill data;
this integration does not need to replace it.
