# Cornering Rumble And Frontend Deadzone

Date: 2026-10-11
Origin: SM2-Emu Libretro
Destinations: Supermodel Libretro and TGPulse-Next Libretro project chats
Status: Destination roadmap reviews completed; destination implementation remains pending where applicable.

## Shared Contract

Use steering from the frontend analog callback, after its deadzone and scaling,
for synthetic cornering rumble. For the user-requested minimum, SM2 selects a small 5% onset threshold for synthetic cornering
vibration on that processed value, replacing larger legacy thresholds. Rescale
remaining travel to preserve the existing peak intensity. This threshold
affects rumble only, not steering delivered to the game. A frontend-zero steering value should
produce no new cornering vibration; positive and negative travel should have
the same magnitude and retain the existing maximum intensity.

Do not read RetroArch configuration files or query a frontend-specific deadzone
setting. Preserve native impacts, kick direction thresholds, motor mixing,
existing intensity controls, persistence and lifecycle stop/tail behavior.
This candidate concerns synthetic cornering vibration, not native force feedback
or drive-board torque thresholds. A destination without such an effect should
record not applicable rather than add an invented rumble effect.

## SM2 Implementation And Qualification

Read-only references: `src/libretro/core.cpp`, `rumble.cpp` and `checks/rumble.cpp`
in `/Users/andrea/dev/sm2-emu-libretro/`.
The adapter already reads the processed left-stick X callback. Its 7000-unit
cornering threshold is replaced by a 5% minimum (1638 units). Absolute travel
is clamped to 32767, and cornering strength is
`26214 * max(0, travel - 1638) / (32767 - 1638)`; the existing weak motor ratio,
12-frame tail and impact decoder remain unchanged. Very small values still
quantize to zero at motor-output precision.

Checks pass for frontend-zero input, travel below/above the new minimum,
left/right symmetry, negative full travel and existing impact/release/disable
behavior. The normal macOS core is built and installed; this is not a new
physical-controller qualification. Evidence:
`build-libretro-gpu/validation/rumble-frontend-deadzone-20261011/`.

## Destination Review

Inspect existing source of steering and synthetic cornering behavior. Record
already-covered cases, applicable gaps or not applicable in the destination
roadmap. This handoff does not authorize implementation, build, install, commit
or push. Return the roadmap section for origin confirmation.

## Destination Roadmap Confirmation

Verified in both destination files on 2026-10-11:

- Supermodel `Docs/ROADMAP.md`, **Cross-core synthetic cornering rumble review**:
  not applicable; the adapter translates native drive-board effects and has no
  synthetic steering-based cornering vibration.
- TGPulse-Next `docs/LIBRETRO_ROADMAP.md`, **Optional Follow-Ups, E5**:
  applicable, integration pending for VR/VFormula. Current synthetic cornering
  uses native steering with an additional 20% threshold, after the Libretro
  input path's 15% centre filter. The future adaptation must supply the
  frontend-processed axis to the synthetic effect with the new deliberate 5% rumble onset, without changing the shared
  standalone helper's policy or native emulated steering/calibration.

The origin handoff is complete. Future implementation belongs in TGPulse-Next's
chat and roadmap; there is no remaining cross-project activity in SM2's roadmap.

## Subsequent User Review — Minimum Rumble Threshold

The user requests a minimum threshold after the initial integration. SM2 uses
5% of frontend-processed travel solely for synthetic cornering, with rescaling
above it. This supersedes the initial zero-additional-threshold wording; it is
not an upstream game-input deadzone. Destination roadmap review should retain
the same rumble-only distinction and existing standalone boundaries.

TGPulse-Next E5 was updated and verified with the revised 5% rumble-only
minimum on 2026-10-11; implementation remains pending in that project.
