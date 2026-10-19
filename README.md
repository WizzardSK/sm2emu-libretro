# SM2-Emu Libretro

[![CI](https://github.com/Zer0one/sm2-emu-libretro/actions/workflows/libretro-ci.yml/badge.svg)](https://github.com/Zer0one/sm2-emu-libretro/actions/workflows/libretro-ci.yml)
[![Latest release](https://img.shields.io/github/v/release/Zer0one/sm2-emu-libretro)](https://github.com/Zer0one/sm2-emu-libretro/releases/latest)
[![License](https://img.shields.io/github/license/Zer0one/sm2-emu-libretro)](LICENSE)

SM2-Emu Libretro is a Libretro port of
[SM2-Emu](https://github.com/dmanlfc/sm2-emu), an emulator for Sega Model 2
arcade hardware. It keeps the original source layout and history while placing
the frontend integration in `src/libretro` to simplify future upstream updates.

The core is playable across the Model 2, Model 2A, Model 2B, and Model 2C board
families. Automated release builds are available for Linux, macOS, and Windows.

## Download

Download the current platform package from
[GitHub Releases](https://github.com/Zer0one/sm2-emu-libretro/releases/latest).

Each package contains:

- the Libretro core and matching `.info` file;
- `system/sm2-emu/games.xml`;
- licence notices, checksums and a matching-source archive reference.

The release also provides the complete source archive, including pinned submodules.

ROMs are not included. Use legally obtained sets that match the game definitions
shipped with the core.

## Installation

1. Copy `sm2_libretro` to the frontend's core directory.
2. Copy `sm2_libretro.info` beside the core when the frontend uses Libretro
   information files.
3. Copy the packaged `system/sm2-emu` directory into the frontend's system
   directory. The resulting path must be:

   ```text
   <system directory>/sm2-emu/games.xml
   ```

4. Load the core, then open a supported `.zip` or `.7z` ROM set.

Save RAM is managed by the frontend as a normal `.srm` file.

## Features

- Optional experimental widescreen expansion with native HUD proportions and
  automatic background side fill on hardware renderers. Disabled by default.

- Software rendering plus Vulkan and OpenGL hardware rendering at 1x–8x
  internal resolution.
- 60 Hz (Default) and 57.524 Hz (Native Model 2) timing.
- Game-aware RetroPad, analog, mouse, and lightgun profiles.
- Per-game operator settings backed by validated NVRAM layouts.
- Automatic first-boot NVRAM setup for required cabinet and region defaults.
- Save RAM and Libretro Save State support.
- Crosshairs, mouse-edge off-screen reload, gamepad rumble, and service controls.
- Optional upstream 2D enhancement filters, per-board audio gains, and SCSP low-pass filtering.
- Experimental linked-cabinet play through the Libretro Netpacket interface.
- In-frame timing overlay for repeatable performance diagnostics.

Rendering, input, NVRAM, and networking options are exposed through RetroArch's
Core Options menu. Options that represent operator settings are shown only for
the loaded game.

## What This Port Adds To Upstream

Beyond importing upstream emulation fixes, this project adds the following
Libretro integration and cabinet-specific extensions. Upstream rendering and
sound emulation remain the foundation; the features below describe the port's
frontend behavior and additional game support.

### Frontend Integration And Controls

- **Frontend-owned rendering and persistence:** software, Vulkan and OpenGL
  output through Libretro, frontend-managed Save RAM and Save States, and
  presentation at 60 Hz or native Model 2 timing. The core does not create an
  SDL window or manage physical input devices.
- **Game-aware controller profiles:** RetroPad mappings for driving, fighting,
  flight, twin-stick, gun and special cabinet controls. **Controller Profile
  Type** selects Normal or Normal + Test/Service globally; the latter is the
  default. Single-view-button games also accept D-Pad Up.
- **Combined gun input:** Standard mode combines lightgun, mouse and analog
  stick input, retaining mouse/stick fallback without an active gun. Dedicated
  source modes, crosshairs and off-screen reload shortcuts are available.
  Gunblade NY, Rail Chase 2 and HOTD prototype expose **Linear (MAME)** and
  **Custom (SM2-Emu)** aiming conversion choices; Behind Enemy Lines includes
  a validated initial calibration preset for the integrated upstream aiming.
- **Gamepad feedback:** native cabinet outputs and synthetic steering feedback
  are adapted to Libretro rumble. Synthetic cornering feedback respects the
  frontend-processed input and a minimum threshold to avoid center noise.

See [control profiles](CONTROL_PROFILES.md) and the
[core manual](LIBRETRO.md) for bindings, options and verification limits.

### Operator Settings And Linked Cabinets

- **Automatic Initial NVRAM Setup:** validated first-boot settings and approved
  calibration presets, while valid existing saves retain priority.
- **NVRAM Settings:** game-specific operator settings in Core Options, with
  native checksums/mirrors preserved and a reset notification when changes
  require restarting the machine. Region defaults prefer Export, Europe, then
  U.S.A. where those choices exist.
- **Linked Cabinets and Auto Network Role Settings:** frontend Netpacket
  transport and native cabinet identity are configured independently. Disabled
  linked play retains local communication-board loopback where upstream uses
  it. Linked sessions remain experimental; support is qualified per game.
- **Generic multi-instance launcher:** per-instance saved options and SRAM,
  one-based gamepad assignments or explicit no-gamepad selection, and windows
  fitted to the desktop. Rider windows occupy a row, with a trailing Relay
  below. The launcher has no fixed game or default cabinet topology.

See the [settings catalog](GAME_SETTINGS_CATALOG.md) and
[launcher guide](Docs/LINKED_CABINET_LAUNCHER.md).

### Power Sled — Experimental Reconstruction

- **Undumped Master reconstructed from the Relay program:** `powsledm` is
  identified as **Master, Undumped: Relay-Derived Version**. A dedicated Master
  archive is optional when the required donor ROMs are available. No original
  Master dump or factory-equivalent behavior is claimed.
- **Cabinet roles and colors:** Master/Slave/Relay roles remain separate from
  Silver, Red, Black and Yellow ride colors. Yellow is available in the Service
  Menu and NVRAM settings. Supported configurations include Master with up to
  three Slaves and an optional Relay, and Master + Relay without a Slave.
- **Standalone Mode:** the Master can run a local race with one player and
  three native computer opponents. The Relay can instead run its continuous
  attract sequence without simulated race-start input. This option applies
  only when Linked Cabinets is Disabled.
- **Relay Audio On Master:** an additional emulated sound board runs Relay
  music alongside rider effects, with a separate Relay Audio Gain.
- **Relay Commands On Master:** mode selection, boarding confirmation,
  race-start and emergency-stop commands can be handled from the Master.
  Start/Select can return from results to attract mode.
- **AI Finish Speed Fix:** an optional bypass of the native computer-opponent
  speed limit near the finish. This intentionally changes game behavior.

These options default to Enabled, with role-specific visibility: Master-only
features appear on the Master, the Relay exposes Standalone Mode, and the
Slave exposes none of these four switches. See the
[standalone implementation](Docs/POWER_SLED_STANDALONE_EXPERIMENT_2026-10-10.md),
[Relay attract mode](Docs/POWER_SLED_RELAY_ATTRACT_2026-10-11.md) and
[Master command integration](Docs/POWER_SLED_RELAY_COMMANDS_ON_MASTER_2026-10-11.md).

### Cabinet Audio And Additional Game Adaptations

- **Manx TT cabinet audio:** select Twin/Deluxe sound ROMs from the native
  Cabinet Type, including the additional Deluxe sound board when donor ROMs
  are present. A Deluxe controller acknowledgement stub passes initialization;
  cabinet motors and position feedback are not simulated.
- **Audio source controls:** per-board Auto/Mute/manual gains and a separate
  Power Sled Relay gain expose the sound sources through Core Options. SCSP
  output low-pass filtering is enabled by default.
- **Cabinet-specific controls and presentation:** independent Power Sled lever
  inputs, supplementary Ski Super G Inclining bindings, Super GT 24h View 1/2,
  and Auto 16:9 for Super GT's native Input Type B. The optional upstream
  widescreen expansion is integrated with the core's aspect-ratio selection.
- **Daytona GTX 2004:** preliminary set support with MAME-derived protection
  handling and reviewed initial operator settings.

See [Manx TT cabinet audio](Docs/MANX_TT_CABINET_AUDIO_2026-10-10.md),
[GPU integration](GPU.md) and the [roadmap](PORTING_PLAN.md) for details.

## Development Changes — Not Yet Released

- **MAME audio corrections:** SCSP MIDI FIFO status/data handling and 68000
  byte-lane reads; MultiPCM envelope/AM register handling and exponential note
  attack. Existing NVRAM retains precedence. Save State format 14 preserves the
  fixed Libretro container size and older-format reading for other games; legacy
  Dead or Alive states are incompatible. Older core builds cannot read new states.
  See [scope and verification](Docs/MAME_AUDIO_INTEGRATION_2026-10-19.md).
- **Dead or Alive protection:** real MAME-derived 317-0229 decryption and
  decompression replaces the fixed startup response for all five Model 2A/2B
  revisions. No new ROMs or NVRAM reset required. Legacy DOA Save States are
  rejected with an on-screen explanation; new states store the complete decoder.
  See [implementation and verification](Docs/DOA_PROTECTION_REVIEW_2026-10-19.md).
- **Linked Cabinets:** the single-cabinet choice is labelled **1 Cabinet / Disabled**,
  following the shared Framework convention. Saved values and network behavior
  are unchanged.
- **Crosshair Style:** Auto searches user PNGs and falls back to SM2-Emu;
  SM2-Emu and Supermodel force their built-in styles; Custom requires a PNG
  and reports missing or invalid artwork. The existing SM2-Emu default remains.
- **Crosshair Inactivity Timeout:** Disabled by default, or a configurable
  1–60 second timeout, independently for each player. Native game reticles and
  game inputs are unaffected.

Put custom PNGs in `<system directory>/sm2-emu/crosshairs/`, named
`<game>-p1.png`, `<game>-p2.png` or `<game>.png`. Parent and `default` names are
fallbacks. PNG alpha is supported; maximum dimensions are 1024×1024. Reload
content after changing files. See [implementation and verification](Docs/CROSSHAIR_CUSTOM_AND_TIMEOUT_2026-10-19.md).

## Latest Update — 0.9.51.2

This release reconciles the applicable upstream changes through **SM2-Emu
0.9.51**, with port revision **2**. The historical full-source import remains
0.9.13; selective integrations and documented frontend exclusions establish
the current coverage. See the [reconciliation ledger](Docs/UPSTREAM_RECONCILIATION_0.9.51.md).

- **Experimental Widescreen Mode:** Disabled by default, or Expand 3D View Only
  with Aspect Ratio Auto/16:9. Forced 4:3 suppresses expansion; native-widescreen
  titles retain their existing behavior.
- **Super GT 24h:** native A/B/C pedal handling, View 1/2 controls, Type B initial
  defaults and Auto 16:9 presentation for B. Valid existing saves retain priority.
- **Machine corrections:** Pilot Kids VBlank tile-RAM latch, Last Bronx geometry,
  deferred i960 interrupt-mask timing, drive-board replies and Virtua Cop's late
  shot-flash filtering.
- **Gear Shift Neutral Time:** 100 ms default, configurable from 0 to 500 ms for
  four-speed sequential steps; direct gear selection bypasses the interval.
- **Gunblade NY aiming:** Custom (SM2-Emu) and Linear (MAME) selector.
- **Daytona GTX 2004:** preliminary protection, content and initial NVRAM support.
- **Frontend conventions:** independent Linked Cabinets / Auto Network Role
  Settings, upstream loopback, global Controller Profile Type and reviewed menu
  wording/order. Existing Power Sled and other approved control integrations remain.
- **Distribution:** GPL-3.0-or-later with upstream NOTICE terms, retained MAME BSD
  credits, complete dependency notices and matching source archives with submodules.

Read the [release notes](Docs/RELEASE_NOTES_0.9.51.2.md),
[roadmap](PORTING_PLAN.md) and
[linked-cabinet launcher guide](Docs/LINKED_CABINET_LAUNCHER.md) for scope and limits.
Widescreen and reconstructed Power Sled features remain experimental. Source,
ABI and bounded frontend checks do not establish every game/device combination.

## Platform notes

| Platform | Release target | Notes |
| --- | --- | --- |
| Linux x86_64 | `sm2_libretro.so` | LTO-enabled release build; tested on Batocera |
| Linux arm64 | `sm2_libretro.so` | Native CI build |
| macOS Apple Silicon | `sm2_libretro.dylib` | Vulkan uses MoltenVK |
| macOS Intel | `sm2_libretro.dylib` | Vulkan uses MoltenVK |
| Windows x86_64 | `sm2_libretro.dll` | MinGW release build |

Vulkan requires a Vulkan 1.3-capable driver with the features requested by the
core. OpenGL requires desktop OpenGL 4.3; supported ARM builds may use OpenGL ES
3.1. The software renderer uses the frontend's standard video output.

## Build from source

Clone the repository with its submodules:

```sh
git clone --recurse-submodules https://github.com/Zer0one/sm2-emu-libretro.git
cd sm2-emu-libretro
```

Configure and build the core with CMake and Ninja:

```sh
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DSM2_BUILD_STANDALONE=OFF \
  -DSM2_BUILD_TESTS=OFF \
  -DSM2_BUILD_LIBRETRO=ON \
  -DSM2_LIBRETRO_VULKAN=ON \
  -DSM2_LIBRETRO_OPENGL=ON \
  -DSM2_LIBRETRO_CHECKS=ON

cmake --build build --parallel
```

For Linux x86_64 release builds, add `-DSM2_LTO=ON`. The exact dependencies and
commands used for every supported platform are recorded in
[the CI workflow](.github/workflows/libretro-ci.yml).

## Documentation

- [Core build, configuration, and validation](LIBRETRO.md)
- [Control profiles](CONTROL_PROFILES.md)
- [Game Settings catalog](GAME_SETTINGS_CATALOG.md)
- [NVRAM Settings audit](NVRAM_SETTINGS_AUDIT.md)
- [Architecture and frontend boundaries](LIBRETRO_DESIGN.md)
- [Continuous integration and release packages](CI.md)
- [Roadmap](PORTING_PLAN.md)

The NVRAM acquisition and linked-cabinet test tools are documented under
[`scripts/`](scripts/). Detailed validation evidence remains in the technical
documents instead of this project overview.

## Upstream relationship

This is an independent repository rather than a GitHub fork. The original
SM2-Emu project remains the upstream source reference:

```sh
git remote add upstream https://github.com/dmanlfc/sm2-emu.git
git fetch upstream
```

Please confirm that an emulation issue also occurs in the current standalone
SM2-Emu build before reporting it to the upstream project.

## Licence

SM2-Emu Libretro is a modified version based on
[sm2-emu](https://github.com/dmanlfc/sm2-emu), copyright (c) 2025+ Daniel Martin
(dmanlfc) and contributors. It is distributed under GPL-3.0-or-later with the
additional terms in [NOTICE](NOTICE). See [LICENSE](LICENSE), the retained
[MAME BSD licence](licenses/BSD-3-Clause.txt), source headers and third-party
licences for full terms and attribution. Earlier releases retain their
published terms. Matching binary releases include a complete source archive
with pinned submodules; see [CI.md](CI.md).

No ROMs, game data, or other copyrighted arcade assets are distributed by this
repository.
