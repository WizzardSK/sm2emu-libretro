# Power Sled Operator Commands And Display Layout Analysis

## Scope And Result

Follow up the shared Master-capable paths and the remaining role-dependent
selectors documented in `POWER_SLED_MASTER_ROUTINES_2026-10-10.md`.
The inspected paths identify native operator functions and graphics layout;
they do not identify another dormant Master-only engine. The current Master
initialization already admits these operator commands.

No production emulation, ROM database, Core Option or input binding changes are
made in this analysis. The previously qualified Main mode-selection scene,
Ride captions, sled-color corrections and donor selector remain in place.

## Native Operator Commands

All addresses below use the Relay program. The equivalent Slave addresses after
the role initializer are 16 bytes earlier, as covered by the retained program
comparison. Runtime qualification here uses Relay-derived Main, an original
Slave and an original Relay in the target core running in RetroArch.

| Native IN1 | Command | Effect | Evidence |
| --- | --- | --- | --- |
| `0x20` | `0x0100` | Emergency Stop: global state 14 displays `EMERGENCY STOP` and `PLEASE WAIT FOR THE ATTENDANTS INSTRUCTIONS`. | Native input, passive trace and separate screenshots on all three programs. |
| Existing P1 Entry, `0x01` | `1` | Leaves Emergency Stop and returns the group to global state 4. | Actual Joypad B, ID 0, through the existing mapping; no RAM or ROM forcing. |
| `0x80` | `0x0300` | Sets the race-exit flag; the original race update contains a delayed return to state 4. | Isolated native-input race and trace confirm return to state 4 on all three programs. |

Decoder `0xbd4c0` accepts native Relay `0x0100` and Master `0x0200`.
Receiver `0xbd760` selects state 14. Its dispatcher `0x2c350` registers the
native drawing task `0x2d040`, which selects `0x2cbb0` and audio command `0x4d`.
The native screen establishes the Emergency Stop function; an original physical
switch label or cabinet wiring diagram is not authenticated. MAME's local
`model2.cpp` Power Sled input definition marks the IN1 high nibble unused and
provides no names for these two commands.

State 14 registers the existing Test, Entry, shutdown and service-status
receivers. Entry reaches `0xbd650` and returns to state 4. The combined probe
confirms that return; it does not qualify a fresh race after Emergency Stop.
That probe does not re-register the Slave rider after the stop, and its later
boarding/start pulses leave the group in selection state 5. No automatic
race-resume behavior or fix is claimed.

Command `0x0300` is received at `0xbd7c0`, which sets `0x00544c20`. The race path
at `0x372fc` increments a counter and, after its threshold, writes state 4 at
`0x37380`. A separate normal-race recipe isolates this command from Emergency
Stop and rider registration. Neither command changes native Master identity or
activates an additional Master scheduler.

## Remaining Graphics Selectors

Field `0x0051aca4` is a roster-derived configuration code. The scan at `0x24e40`
counts ordinary rider identities, detects Relay separately and excludes Master
`0x0200` from that ordinary-rider count. Valid codes group one, two, three or
four rider identities with or without Relay; code 8 represents the unmatched
case. This is distinct from communication node count and local race index.

The role-dependent selector at `0x18c30` writes horizontal placement and a
cleared secondary offset to `0x00529358` / `0x0052935c`:

| Roster Configuration Code | Rider-Specific Placement Values |
| --- | --- |
| 0 / 1 | `1`, independent of role |
| 2 / 3 | identity 0: `+260`; identity 1: `-260` |
| 4 / 5 | identity 0: `+521`; identity 1: `1`; identity 2: `-519` |
| Other branch | identities 0–3: `+780`, `+260`, `-260`, `-780` |

The original three-rider negative constant is `0xfffffdf9`, hence **-519**;
retain the actual word instead of assuming a symmetric -521 value.
The multi-rider branches return without a new placement for Master. That fact
alone does not demonstrate a visual defect. Selection initialization clears
these fields, and the previously qualified missing-scene fix restores Main's
scene without altering these offsets.

Consumers at `0x18590` and `0xc22d8` feed graphics window/projection parameters.
The related selector at `0xc2bc8` supplies signed per-identity placement in the
same graphics path. The inspected writes go to geometry function/data ports
`0x00800030`, `0x00800090` and `0x00804000`; the emulator's Window Data handling
in `src/hw/geometrizer.cpp` interprets viewport and center coordinates. This
supports a display-layout interpretation. It does not establish every physical
cabinet arrangement or every possible indirect use of the fields.

No further visible layout defect is demonstrated in this bounded analysis.
Broadly replacing application role with NVRAM Ride would also affect roster
and operator semantics and is not justified by these graphics observations.

## Diagnostic Method And Corrections

Evidence directory:
`build-libretro-gpu/validation/power-sled-operator-analysis-20261010/`.

Use the existing linked RetroArch runner, original user archives, isolated
configuration/SRAM and the previously qualified Manual race movies. Build a
private dylib with a passive native-state observer and temporary operator-line
mappings. Restore `core.cpp`, `input.cpp` and the normal built dylib byte for byte
before launching it; never install the diagnostic dylib.

Retained provisional probes are not used to qualify the isolated race-exit
command:

- `run/`: the initial temporary Down mapping also activated the existing native
  Service A line, producing `SYSTEM SHUTDOWN`. It is a confounded fixture.
- `run-corrected/` and `run-final/`: the recovery pulse used Joypad A, ID 8,
  which correctly decodes as command 2. Entry is Joypad B, ID 0. The emergency
  screen is observed, but recovery is not qualified by those recipes. The earlier
  query-order explanation was not demonstrated and is withdrawn.
- `run-qualified/`: correct B Entry proves the Emergency Stop recovery on all
  three units. It does not prove the later race-exit operation because no new
  race begins after the stop.
- `run-exit/`: reuse the original, qualified normal-race recipe and add only
  the isolated operator exit pulse.

The final private mapping reuses the existing L/R queries: L drives native
IN1 `0x20`, R drives `0x80`, only in the private probe. It preserves the normal
query sequence and avoids the Down / Service A overlap. The production L/R
bindings remain Cancel Error / Cancel Network Check. Replays must use the actual
Libretro button IDs and validate each resulting native command/state; comments
or informal button names are insufficient.

`build-probe.py`, `prepare-run.py`, input plans, exact commands, original/private
source snapshots, traces and separate per-program PNGs retain reproducibility.
`state-14-display.txt`, `race-exit-command.txt`, `projection-offsets.txt`,
`roster-configuration.txt` and `placement-references.json` retain the anchored
static walks and references. No MAME or standalone emulator is launched.

## Runtime Review And Production Boundary

Both final sessions pass the focused runtime review: six normal program exits,
native link/roster readiness, preserved sampled identities/count, SRAM integrity,
calibration/EEPROM equality and nonzero PCM. No sampled global state 13
(`SYSTEM SHUTDOWN`) or runtime CPU reset occurs.

The Emergency Stop probe reaches state 14 at Main frame 2415 and returns to
state 4 at 2775 after B Entry. Slave and Relay follow the same state sequence.
The isolated race-exit probe observes Main command `0x0300` with exit flag 1 at
frame 4620 and state 4 at 4800. Slave and Relay also return after 180 observed
machine frames. At the native cadence this is approximately 3.1 seconds;
15-frame sampling does not establish the exact first transition frame or an
accurate wall-clock duration.

The exit captures include the flyby/race views and blackened scenes. The final
state-4 captures are black on **Main, Slave and Relay**, not only Main. This
bounded session qualifies state-4 return, but does not establish a Master-specific
failure or permanent loss of display. Its duration does not qualify a restored
title/attract screen or another race after this operator command. The subsequent
donor comparison and longer native-input recovery are documented in
`POWER_SLED_DONOR_RESIDUALS_2026-10-10.md`. Original physical button naming is unresolved.


Runtime qualification and selected image observations are recorded separately
in `runtime-review.json` and `visual-review.json` in the evidence directory.
The runtime review checks native transitions, roles/count, link readiness,
normal exits, lack of runtime CPU reset, SRAM identity/container CRC/three-copy
Ride, unchanged calibration/EEPROM against the previous normal-core session,
and nonzero PCM. Nonzero PCM does not qualify audio fidelity.

`production-integrity.json` verifies byte-identical restored source and matching
normal/installed core SHA-256:
`598e9864c4858f60b15a07e91e0d8cb684188d2e16fff47ac51305daccaed296`.
The ROM database is unchanged. No deployment is required for this documentation
and private analysis; both installed cores already contain the previously
qualified scene fix.

Factory Master firmware, original switch labels, physical controllers, emergency
motion hardware, every color/layout and a fresh full race after Emergency Stop
remain outside qualification. No new production binding is exposed by this
analysis. No commit or push is performed.
