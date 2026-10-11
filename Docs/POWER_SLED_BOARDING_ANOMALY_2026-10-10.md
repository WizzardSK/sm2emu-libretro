# Power Sled Linked Master Arm Animation — 2026-10-10

## Symptom And Cause

The user observed that, in linked Master–Slave play, mode confirmation starts
mechanical-arm audio on the reconstructed Master but its scene appears to skip
the sled/platform movement before boarding. This concerns linked play.

The passive reference reproduces the discrepancy. Native mode confirmation
accepts input mask `0x0f00` and sends sound command 9. The four color-specific
scene tasks accept only Entry (`0x0500`) to switch from their static callbacks
to the existing moving-arm callbacks. The Master uses operator Call to confirm;
its confirmation and sound therefore succeed without starting that movement.
The later native operator command 4 removes the static scene, making the missing
movement look like an interrupted sequence. The Slave's Entry confirmation
already starts its arm animation.

## Correction

Only the reconstructed `powsledm` program receives four mask replacements in
`data/games.xml`, from `0x0500` to the same `0x0f00` used by native confirmation:

| Ride | Mask Instruction | Static Callback | Moving Callback |
| --- | --- | --- | --- |
| Red | `0xe5a4c` | `0xe5770` | `0xe44c0` |
| Black | `0xe5dd8` | `0xe5ab0` | `0xe4830` |
| Silver | `0xe6150` | `0xe5e40` | `0xe4f60` |
| Yellow | `0xe64a4` | `0xe61a0` | `0xe4bf0` |

The ROM bytes on disk are untouched. Role/color identity, bindings, phase
commands, native motion/camera routines, audio commands and timing are retained.
No selector or artificial delay is added. Slave and Relay programs are unchanged.

## Reproduction And Evidence

Reuse `scripts/test-retroarch-netpacket.py`, the existing manual input movies,
isolated configuration/SRAM/ports, and explicit `--play-audio --record-audio`.
Private passive observer builds restore the exact source and normal binary after
building and are never installed. Evidence is under
`build-libretro-gpu/validation/power-sled-boarding-20261010/`:

- `baseline-command.json`: Master Silver / Slave Red before correction. After
  the confirmation pulse beginning at movie frame 2880, Master retains static `0xe5e40`, with `c6=0`, until
  the phase-6 transition. The Slave leaves its static callback on Entry.
- `candidate-command.json`: the same input movies with the four changes. Master
  enters moving `0xe4f60`: frame 2895 has counters `c0=14`, `c4=193`, `c6=1`;
  frame 3180 has `c0=299`, `c4=478`, `c6=1`. The camera passes through its native
  segments. Separate screenshots show the sled moving away from the platform.
  Slave moving `0xe44b0` also advances. Both enter phases 6 and 7; later captures
  show the racing course. Both recordings contain PCM and both instances exit
  cleanly with no residual processes.
- `patch-review.json`: all four original instructions are checked against the
  donor dump; the XML comparison changes only `powsledm`.
- `paired-review.json`: runtime phases, counters, PCM peaks and lifecycle checks.
  The first observer did not record moving callback addresses, so its null Slave
  moving fields do not mean that Slave movement was absent.
- `normal-red-command.json`: a second qualification uses the normal core and
  Master Red / Slave Silver, covering the other native animation path.
  Reviewed captures show platform departure and later racing; PCM peaks are
  4,603 / 4,577. Both instances and the link pass with no residual processes.

This qualifies the diagnosed missing animation. It does not establish factory
Master fidelity: its original program remains undumped. Black and Yellow share
the reviewed correction but are not separately exercised in this linked probe.
An operator can still advance to boarding early with command 4, as before.

## Budget

Work paused at the previous absolute 20% ceiling. The user authorized an absolute
25% ceiling and analysis resumed at 20%, with Sol High. Final verified account usage is 21%, from the 20% starting point, below the 25%
ceiling. Reset: 17 October 2026, 15:30:48 Europe/Rome.

## Local Deployment

`installation.json` records backups and matching hashes for both local
`games.xml` destinations: the configured RetroArch system directory on the
external volume and the Application Support system directory. The normal core
was rebuilt after removing passive instrumentation; its SHA-256 remains
`f3d8c8f6dab73304d922d893500dfeba382333869a14de30d71126c371101017`.
The installed normal core matches; the dev core remains absent. No commit/push.


## Duration Follow-Up

The user reports that the restored departure still feels short. Static analysis
of all four native moving callbacks gives a concrete timing reference: each
passes its local counter to a model-animation table through frame 380
(`0x17c`). Beyond 380 it repeats the last 69 frames, indices 312–380, instead
of advancing into a new animation. Silver uses this branch at `0xe5078` /
`0xe50a0`; equivalent Red, Black and Yellow branches are present. This is a
model-animation boundary, not evidence of a factory-enforced scene duration.

At the default 60 machine frames per second, 380 frames are approximately
6.33 seconds; at native cadence approximately 6.61 seconds. The retained test
movie confirms at frame 2880 and issues the next command-4 pulse at frame 3180:
about 300 frames / 5 seconds later. The observer records moving `c0=299` at
frame 3180 before the scene is removed. Thus that test does not qualify the
last approximately 80 departure frames (1.33 seconds at 60 Hz). Native command
4 can remove the scene without waiting for counter 380.

No original-cabinet video/manual fixing an exact duration was found in this
bounded search. The user's own operator timing has not been measured. A future
complete-sequence reference should wait at least seven seconds after mode
confirmation before command 4, retaining the existing animation speed. No new
ROM/core changes are made on the basis of duration alone.


## Complete-Sequence Reference

The reference at `build-libretro-gpu/validation/power-sled-boarding-duration-20261010/`
moves only the second Master X/command-4 pulse from movie frames 3180–3215 to
3360–3395. Mode confirmation stays at 2880, yielding an eight-second / 480-frame
wait at 60 Hz; all other inputs, the Slave movie and race-start pulse are retained.
The passive trace records Master moving `c0=479` at frame 3360, with camera
segment `c2=3`. Thus the scene remains active beyond the native model frame-380
boundary. The native sound task advances to `c0=388` at frame 3270, then ends
before the later boarding command, consistent with its command-11 branch after
400 ticks. The first observer samples every 15 frames, not every audio command.

Separate retained images show the final departure view and its repeating end
pose. The user watched this run and confirmed that the sequence now appeared correct. The
manual operator recipe now recommends at least seven seconds after confirmation
at default 60 Hz; the validated movie allows eight seconds. No emulation speed,
ROM timing, automatic delay or controller mapping is changed in this follow-up.


Final `review.json` passes: both riders cross frame 380 before boarding and enter
race phase 7; later screenshots show an advancing racing course. PCM peaks are
4,433 / 4,368, SRAM Ride copies and CRCs are valid, both owned instances exit
cleanly and no residual processes remain. Normal build and installed core hashes
remain unchanged. Duration verification is closed with the user confirmation;
this does not claim an independently measured factory-cabinet duration.
Account usage remains 21%, below the authorized absolute 25% ceiling.
