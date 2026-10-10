# Upstream Controls Package — 2026-10-08

## Scope and Imports

The full integrated baseline remains 0.9.13
(`5ddf84ae7970a9bce1d0a17b3900d26065de1996`). This package selectively
reconciles upstream controls with published Libretro profiles.

| Reference | Result |
| --- | --- |
| `fa88f95` | House of the Dead P2 trigger corrected to IN1 bit 1 in bundled metadata; P1 remains IN1 bit 0. All three revisions agree. |
| `902fb86` | Serial-gun on-screen coordinates map one unit inside calibrated endpoints. Native off-screen status and reload shortcuts still use the endpoint and explicit serial off-screen bit. Applies to Virtua Cop 1/2 and HOTD; positional analog guns are unchanged. |
| `cd40912` | Top Skater reverse Curving metadata was already present. Add trigger Slide aliases and D-Pad steering. Progressive response is now the approved default, with Linear selectable. |
| `54d6ff2` | Ski Super G channel 0 Inclining, channel 1 reversed Swing were already present. The user approved independent axes as the core-specific choice. Coupling is available through frontend binding in Settings > Input > Port 1 Controls; no additional core selector. |

The existing external XML `p2_trigger="in2"` declaration remains readable for
backward compatibility. Upstream removed this metadata field; the port retains
it without using it in the corrected bundled HOTD definition. An external
custom database can therefore still explicitly request the old route.

Libretro provides normalized coordinates relative to the displayed game image.
Standalone desktop/window conversion, SDL ownership, RawInput and evdev code
are not imported. Frontend-specific calibration UI and cabinet outputs remain
outside this package.

## Top Skater Contract

- Left Analog X remains Curving; Right Analog X remains Slide.
- L2/R2 add Slide Left/Right. Trigger travel is R2 minus L2. The larger absolute
  value of trigger and right-stick travel wins; the stick wins ties.
- Digital-only trigger callbacks fall back to full travel. Analog trigger
  travel retains partial pressure even when its digital callback is pressed.
- D-Pad Left/Right retains menu selection and also supplies full-lock steering,
  matching upstream. Equal left/right presses retain analog steering.
- `Top Skater Curving Response` (`sm2_top_skater_curving_response`) is visible
  for every game. Values use existing response conventions: `linear` / Linear,
  `progressive` / Progressive (Fine Center). Only Top Skater consumes it.
- The user approved Progressive as the default. It follows upstream's
  3000/32767 center deadzone and quadratic travel. Linear restores the previous
  direct curve; both preserve full lock and metadata polarity.

No machine archive, core state version, fixed state capacity, audio options,
other control profile names or TGPulse files change. Adapter policy stays in
`src/libretro/`.

## Verification

Evidence root: `/tmp/sm2-controls-package-20261008/`.

- macOS ARM64 core, headless and standalone builds pass.
- Input checks cover HOTD parent/clones, explicit legacy metadata, serial-gun
  image edges and off-screen reload, all four Top Skater revisions, preserved
  axes, trigger subtraction/cancellation/partial travel/digital fallback,
  source arbitration, D-Pad steering and Progressive/Linear half-stick values.
- Core Option checks verify the approved Progressive default and Linear reader;
  the existing all-game visibility checks include the added option.
- Linux x86_64 core/input/persistence checks and artifact audit pass, including
  25 Libretro ABI exports and three empty lifecycle cycles. No native Linux
  gameplay or physical controller qualification is claimed.
- Analog/lightgun metadata for all eight affected sets match pristine upstream
  `e1aafb7`. That reference's input source, main source and database were checked
  against the Git revision (`pristine-source-check.json`).
- Whole-machine HOTD comparison, 1800 frames: pristine upstream and adapted
  headless video, audio PCM, CPU state, cycles and NVRAM are identical.
- Separate old/new Libretro 1800-frame idle baselines for HOTD, Ski Super G and
  Top Skater preserve video, PCM and NVRAM. All three pass deterministic state
  round trips and fresh-process loads of states produced by the previous core.
  These baselines ran before the final Top Skater curve selector; final targeted
  input checks and native Top Skater replay cover that adapter-only addition.
- Final installed core, RetroArch 1.22.2 macOS, Vulkan 2x, 2300 frames: HOTD
  shot/reload replay exits cleanly, with active-game continue screen captured;
  Top Skater dedicated replay reaches an active race. Both produce valid Save
  RAM and nonzero stereo PCM. The Top Skater fixture exercises Curving,
  independent Slide, trigger aliases, D-Pad and jumps.
- Physical P2 lightgun accuracy, subjective steering feel and audible quality
  remain manual checks. Ski Super G's existing drive-board bypass limitation
  is unchanged. Independent axes are the approved core behavior; users can
  bind both virtual horizontal axes to one physical axis in Port 1 Controls
  for coupled steering. Exact upstream response and rounding equivalence
  through that GUI configuration has not been verified.

## Local Installation and Roadmap

Both local RetroArch copies were atomically replaced with backups and verified:
`sm2_libretro.dylib` and `sm2_dev_libretro.dylib`.

Core SHA-256:
`4bb61824a668a58c43befb9128e090ff29981cb3563164b4c95ae7fda4f2072e`.

Installed external `system/sm2-emu/games.xml` SHA-256:
`c25dc48d4e0436b8fd23c24b1e75563d9ec2c568d555bfb2743df537a57eef86`.

Previous installed files are in `installed-backup` under the evidence root.
Game Control Reconciliation has no pending implementation choice. It remains
Partial for physical lightgun and subjective control validation. Ski Super G
retains independent axes by user decision; no Core Option or Quick Menu
selector will be added. The roadmap records possible future reconsideration
of built-in coupling if frontend binding limitations or gameplay evidence
justify it. The adjacent mainstream
checkout remains clean. No commit or push was made.
