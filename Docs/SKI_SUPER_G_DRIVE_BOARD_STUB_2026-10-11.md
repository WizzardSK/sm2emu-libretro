# Ski Super G Drive Board Stub — 2026-10-11

## Report And Root Cause

The game stops at `DRIVE BOARD TROUBLE CODE: FF`; pressing Test permits
continuation. Previously the adapter offered an optional timed Test pulse.
The common machine had no Ski drive-board command/response wiring: port PD
returned the generic `in2` latch, normally `FF`.

The game sends commands through port PE (`0x01c00008`) and reads responses
through PD (`0x01c00006`). The native boot sequence requires:

- Command `00`: response `CE`.
- The configured centre byte (normally `80`): response `FF`.
- Then command `00` and completion of the boot check.

The program stores the received byte at `0x58823a`, the outgoing byte at
`0x588238`, and its displayed error at `0x588239`. The boot handlers at
`0x889e0`, `0x88a40`, `0x88a70`, and `0x88ab0` implement this exchange.
The polling loop at `0x88b10` sets error `FF` after its timeout; this displayed
code is therefore not proof of a particular physical fault. The unconnected
input cannot provide the initial `CE` acknowledgement.

These findings come from the user's local program image and controlled machine
observations. Current official MAME also has no Ski-specific drive-board
response callback in its machine configuration; it is a reference for the I/O
layout, not the source of this stub:
<https://github.com/mamedev/mame/blob/master/src/mame/sega/model2.cpp>.
No ROM content or extracted binary is included in the repository.

## Implementation And Limits

`Model2C::reset()` wires PE to the existing archived drive-board latch and PD
to a stationary stub for `skisuprg` only: zero command returns `CE`; nonzero
commands return `FF`. Reset clears the latch. Save/load preserves it using the
existing archive field; archive layout and version are unchanged.

This models the acknowledgement needed to pass the startup check, not the
motor, rollers, sensors, timing of a physical controller or its full diagnostic
protocol. Generic rumble decoding and other games are unchanged. It does not
patch the ROM, force the game's error flag, inject Test, or modify calibration.
The obsolete Test-pulse option is removed; old saved values are ignored and
cannot accidentally open the Service Menu after successful boot.

## Verification

Private evidence is under
`build-libretro-gpu/validation/ski-drive-board-20261011/`:

- `baseline.log`: fresh machine stalls at the initial acknowledgement, then
  sets the timeout error `FF`.
- `qualified.log`: direct command/reply checks, saved-latch restoration,
  reset to the initial reply, and 1,400-frame fresh boot without Test; error
  byte remains zero and the game reaches its skiing attract sequence.
- `save-ram-checks.log`: registered option and persistence checks after removing
  the obsolete bypass.
- `retroarch/`: isolated real RetroArch Vulkan run, 2,300 frames, no Test pulse.

The native probe is diagnostic evidence, not a Service Menu sample-acquisition
campaign. Physical cabinet movement is outside the qualification.
