# Shared Lightgun Standard Input Selection

Date: 2026-10-11
Origin: SM2-Emu Libretro
Destinations: Supermodel Libretro and TGPulse-Next Libretro project chats
Status: Destination roadmap review completed; implementation remains owned by the destination projects.

## User Direction And Scope

The user identifies SM2 Standard gun input behavior as another cross-core
integration candidate. Review existing destination behavior and add the
applicable requirement to its roadmap. Implementation, installation, commit
and push are not authorized by this roadmap handoff.

## Shared Contract

Standard combines Lightgun, Mouse and Analog Stick input. A constant
IS_OFFSCREEN report by itself must not select Lightgun absolute aim and
suppress Mouse/Stick movement. Lightgun coordinate changes or actual
Trigger/Reload/Aux commands can select that source. Apply Lightgun off-screen
status to aim when the Lightgun source is selected; retain independent Mouse
edge reload and explicit reload rules.

Lightgun Only stays restricted to Lightgun callbacks; do not add fallback there.
Do not assume that the frontend identifies physical gun presence. This is
source arbitration inside Standard, not a claim that RetroArch supplies an
automatic device-presence fallback. Preserve each destination's existing gun
protocol, coordinate scale, calibration and supported inputs.

## Reference And Verification

Read-only references:
- `/Users/andrea/dev/sm2-emu-libretro/src/libretro/input.cpp`
- `/Users/andrea/dev/sm2-emu-libretro/src/libretro/checks/input.cpp`
- `/Users/andrea/dev/sm2-emu-libretro/Docs/GUN_STANDARD_FALLBACK_2026-10-11.md`

SM2 checks cover constant off-screen Lightgun plus moving Mouse/Stick,
dedicated gun input and off-screen firing, for positional BEL and serial
Virtua Cop paths. Do not copy Model 2 hardware mappings into other systems.

## Destination Review

Record existing coverage, gaps and actual conflicts after inspecting code.
For a destination with no supported Lightgun game, record not applicable and
retain as a future convention; do not invent a control mode or implementation.
Return the roadmap path and section so the origin can verify and close handoff.

## Destination Roadmap Confirmation

Both destination chats completed their review on 2026-10-11; the origin
verified the corresponding roadmap files before removing its handoff activity.

- Supermodel: `Docs/ROADMAP.md`, **Cross-core Lightgun Standard source arbitration**.
  Integration pending: Standard currently allows IS_OFFSCREEN alone to select
  Lightgun and suppress Mouse/Stick, affecting the five supported Gun sets.
- TGPulse-Next: `docs/LIBRETRO_ROADMAP.md`, **Optional Follow-Ups, E4**.
  Not applicable to the current Model 1 adapter; retained for future Model 2 /
  Complete Lightgun support. No new Model 1 input mode is required.

No destination code change was authorized or performed by this handoff.
