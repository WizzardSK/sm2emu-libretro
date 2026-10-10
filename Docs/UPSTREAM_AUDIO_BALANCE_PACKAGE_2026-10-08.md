# Upstream Audio Balance Package — 2026-10-08

## Default and Source Gain Contract

**Enhanced Audio Balance is Enabled by default. Every source Gain defaults to Auto.**

| Setting | Effective source level |
| --- | --- |
| Auto, EAB Enabled | Current upstream game profile |
| Auto, EAB Disabled | Unity gain, without the optional game profile |
| Manual 10%–100% | Selected percentage of the unprofiled source reference level |
| Mute | Zero output, with chip execution and timers still advancing |

Auto is now represented separately from numeric 100% in the neutral SoundBoard
setter. Manual percentages replace the optional profile for that source.
Hardware mixer routes and game-programmed levels still apply. In particular,
MultiPCM uses its existing 50% hardware routes and YM3438 its 30% route;
Music Volume remains a separate control on MPEG music. No new menu selector,
labels or choices were introduced. Raw values remain `auto`, `0` and bare
percentages. Recognized old textual mute and 110–200% values remain readable.
The existing optional SCSP output low-pass filter is independent of these gains.

## Upstream Imports

The full integrated baseline remains 0.9.13
(`5ddf84ae7970a9bce1d0a17b3900d26065de1996`). Profile data matches the reviewed
upstream `e1aafb7` / current inspected main audio tables.

- `abb42bb`: remove VF2's old per-slot music/effects/announcer/voice rebalance
  and use its flat SCSP level; update Dead or Alive profiles.
- `88d5557`: House of the Dead anti-clipping levels.
- `cb57c0a`: revised per-game SCSP levels and original-board attenuation.
  MultiPCM unclamped summation was already integrated in the audio package.
- `3a71c1d`: Top Skater SCSP level 232/256 and DSB2 music level 64/256.
  The earlier intermediate DSB2 218/256 value is not used.

Examples of current SCSP profiles, in units of 1/256:

| Family | SCSP Gain |
| --- | ---: |
| VF2 | 840 |
| Dead or Alive | 500 |
| House of the Dead / older revision | 1400 |
| House of the Dead prototype | 1100 |
| Virtual-On | 1042 |
| Top Skater | 232 |

Original Model 2 board attenuation is Daytona 117/256, Desert Tank 111/256 and
Virtua Cop 181/256, including the explicitly listed upstream clones. The two
MultiPCM and YM3438 Auto contributions are summed before applying that board
level, matching upstream rounding with all sources in Auto. Manual contributions
are summed separately and bypass the optional profile before the final clamp.

## State Compatibility and Ownership

No archive version, field count or fixed Libretro capacity changes. The old
VF2 balance fields are retained in the serialized layout for published state
compatibility. Loading a state reapplies current profile metadata and restores
the current frontend Gain preferences rather than reactivating obsolete VF2
per-slot processing. New automatic/manual flags and derived board/DSB2 levels
are frontend policy or metadata, excluded from machine archives.

The machine remains frontend-neutral. No TGPulse files, user option files,
commits or remote repositories were changed.

## Verification

Evidence: `/tmp/sm2-balance-package-20261008/`.

- macOS ARM64 core, headless and standalone builds pass.
- Synthetic real-chip SCSP tests cover VF2, Dead or Alive, House of the Dead,
  Virtual-On and Top Skater: upstream Auto gain applied once, manual 100%
  independent of EAB, manual 50% attenuation and Mute.
- Synthetic MultiPCM samples test Daytona, Desert Tank and Virtua Cop: original
  board Auto level, manual bypass, independent mixed Auto/manual sources and
  Mute. Both MultiPCM engines execute once per chunk, with one final clamp.
- A generated 440 Hz MPEG Layer II tone tests the actual Top Skater SCSP/DSB2
  path: Auto 64/256, manual 100% bypass, Mute and Music Volume zero. The fixture
  CPU writes the FIFO commands; the run includes encoder startup silence.
  The generated MPEG file is external evidence, not a game ROM or Git asset.
- Core Options checks verify EAB Enabled default, all Gain Auto defaults,
  unchanged choice order/labels/raw values and distinct Auto/manual 100%.
- Existing audio and Save RAM/Core Options checks pass.
- Exact isolated sound CPU/sample/PCM comparison against pristine `e1aafb7`
  passes for synthetic eight-slot FM/PLFO with the House of the Dead profile
  and VF2, Sega Rally, House of the Dead and Top Skater sound programs with
  their profiles configured.
- Complete Daytona 1,800-frame pristine `e1aafb7` standalone versus port
  headless comparison passes video, PCM, audio format, CPU state, cycles and
  NVRAM. This validates the automatic original-board attenuation in context.
- Previous/current cores each pass 1,800-frame runs and exact state replay on
  Daytona, VF2, House of the Dead, Top Skater and Dead or Alive. Fresh-process
  loads of each previous-core state pass. Published format-4 VF2 and format-5
  Top Skater state loads and replay are also checked separately.
- Linux x86_64 existing Debian 12/Rosetta builder: core build, synthetic
  SCSP/MultiPCM balance checks, existing audio and Core Options checks pass.
  ABI audit passes 25 exports, dependencies and three empty lifecycle cycles.
  The optional generated MPEG fixture was run on macOS; it is not required
  in ROM-free CI. CI now includes the balance-check target but was not invoked.
- Installed-core RetroArch 1.22.2 Top Skater, Vulkan 2x, EAB Enabled and Gain
  defaults: 2,300 frames, inspected gameplay capture, non-silent stereo audio
  (peak 11,603) and clean exit. Subjective listening and native Windows/Batocera
  gameplay remain separate validation; no subjective fidelity claim is made.

## Local Installation

Both local RetroArch cores were replaced atomically with backups. Matching
SHA-256: `01a9a58554836b606081055aedcb77b0625f63d20e8a3fd4f07c4abc8cb088b3`.

Backups: `/tmp/sm2-balance-package-20261008/installed-backup/`.
The game database is unchanged by this package.
