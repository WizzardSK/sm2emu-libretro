# Upstream Gun Shot Flash Package — 2026-10-08

## Behavior and Scope

Backport: `96e0f0ef79ad211bf7c69cc8c27932c5ef9acc74`.

**Hide Shot Flash** is an Input Core Option, visible for every game, with
Disabled / Enabled values (`disabled` / `enabled`) and default Disabled.
It takes effect immediately. The filter runs only where game metadata declares
a lightgun interface: Virtua Cop, Virtua Cop 2 and House of the Dead and their
applicable variants. Other games are unaffected.

The upstream detector recognizes a newly full pair-A window mask associated
with a new trigger press, including a one-frame delay. Existing full masks
remain visible so fades are preserved. Software draws as though that mask were
clear. Vulkan and OpenGL clear it only in the uploaded RAM copy, and refresh
that copy when suppression changes even if the emulated RAM generation did not.
Emulated tile RAM is never modified.

The detector and tile drawing/upload changes are imported from the selected
upstream patch. Standalone configuration, menu and frame-loop changes are
adapted to the existing baseline. The complete baseline remains upstream
0.9.13 plus recorded backports; no full-upstream 0.9.40 equivalence is claimed.
The exact detector and upload algorithm are source-aligned with the selected
patch; a complete pristine `96e0f0e` runtime comparison was not performed.

## State Compatibility Adaptation

Upstream does not archive this detector's presentation history. This port adds
a frontend-neutral history accessor, clears history on reset/machine load,
and stores four tagged bytes at offset 76 of the existing 96-byte Libretro tail.
Old reserved bytes are zero and load as empty history. The machine video archive
remains two 16-bit words; the Libretro state remains 9,437,184 bytes.

Saving during an actively suppressed flash preserves that frame's history and
following-frame behavior when restored. No eager configuration migration or
external migration script is involved.

## Verification

Evidence root: `/tmp/sm2-flash-package-20261008/`.

| Check | Result |
| --- | --- |
| macOS core, headless and standalone | Builds passed |
| Linux x86_64 core and EGL host | Build passed with existing dependencies |
| ROM-free shared detector/tile checks | Immediate and delayed shots, player two, held triggers, persistent fades, disable, reset, history restore, unchanged RAM and archive length passed |
| Core Options checks | Label, Disabled default, runtime getter and visibility with VCOP, VCOP2, HOTD, VF2, Virtual-On and no content passed; existing Gain/NVRAM checks pass |
| Virtua Cop, paired Software sweeps | 910 frames per measured sweep; nine suppressed shot frames, with image changes limited to those frames; machine archive bytes and PCM identical between modes |
| Virtua Cop 2, paired Software sweeps | 1,200 frames per measured sweep; 13 suppressed shot frames; machine archive bytes and PCM identical between modes |
| House of the Dead, paired Software sweeps | 1,200 frames per measured sweep; eight suppressed shot frames; machine archive bytes and PCM identical between modes |
| Active-flash Save States, all three titles | Exact immediate state restore and deterministic three-frame continuation passed |
| Legacy reserved bytes | Zero-filled extension accepted on the tested titles; comparison uses the same loader normalization on both paths |
| Actual previous-build VCOP2 state in a fresh updated process | Loaded, advanced 180 frames; round-trip, replay, corrupt rejection, ten stress cycles, run-ahead and rewind checks passed |
| Non-lightgun VF2 | Enabled/disabled images, machine state and PCM identical; no suppression |
| Virtua Cop 2 Vulkan / Mesa GLES / desktop GL | Paired shot frame 1170, 1,171 frames each: Enabled images match exactly across all APIs; Disabled Vulkan/GLES images also match; Enabled differs from Disabled while complete PCM is identical |
| GPU context recreation | Vulkan and GLES recreated at frame 1000 before the shot; next hardware frame submitted correctly |
| Previous-build Vulkan versus updated Disabled | Exact image, PCM and NVRAM comparison passed at the same shot frame |
| Installed core in RetroArch Nightly 1.22.2, Vulkan 2× | Two 2,300-frame input replays passed, non-silent audio, 16,576-byte Save RAM, exit 0; captures inspected, including an active 3D scene with the reload prompt |

The first RetroArch capture showed the reload tutorial, so the second replay
adds late coin/Start events after the gun title's boot. These frontend captures
verify runtime rendering with the installed option; the direct paired shot
captures establish the flash effect. They do not prove physical gun delivery,
subjective audio quality, or all gameplay cases.

### Existing Virtua Cop Replay Difference

The first Software replay from the baseline differs from its repetition at
frames 1988 and 1989 (326 pixels at frame 1988 in the diagnostic capture).
Six serialized machine bytes also normalize on loading the baseline.
**Both observations reproduce in the previous core, which lacks this option.**
The old control is `vcop-old-verified/result.json`; the updated run is
`vcop-verified/result.json`.

The final runner reports this first-replay drift separately and compares the
repeated sweep for each option mode. Under those matched conditions, the only
image changes are the nine recognized flashes, machine bytes/PCM match, and
active-flash state continuation passes. The existing discrepancy is recorded
as an additional-analysis item at the end of the roadmap. Its underlying cause
has not been established; no unrelated emulator correction is included here.

### Reusable Checks

- `sm2-libretro-gun-flash-checks`: ROM-free detector and actual tile drawing.
- `scripts/test-libretro-gun-flash.py`: isolated synchronous Software sweeps,
  machine/PCM comparison, active-flash replay, legacy tail and first-replay
  diagnostics. Output directory must be new; ROMs stay external.
- GPU runners support `--gun-inputs --hide-shot-flash enabled|disabled`.
- RetroArch runner records the selected filter and supports late gun-title
  coin/Start events.

## Local Installation and Convention

Both local RetroArch copies (`sm2_libretro.dylib`, `sm2_dev_libretro.dylib`)
were atomically replaced, with backups in the evidence root, and match:

`69b74b563cc5dd5c68e342d78f19ffbfba270e7b4751341bb38664f5bb3f7d5f`

The mandatory all-game option visibility convention is recorded in `AGENTS.md`,
`Docs/UPSTREAM_PORTING_MANIFESTO.md` and the user's persistent notes. Previously
explicit exceptions such as per-game NVRAM remain valid. No TGPulse files were
changed. The adjacent mainstream checkout is clean. No commit or push was made.
