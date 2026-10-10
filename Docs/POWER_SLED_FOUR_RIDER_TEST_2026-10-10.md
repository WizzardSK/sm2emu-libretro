# Power Sled Four Rider Test

## Scope

Test one reconstructed Master (`powsledm`) and three original Slaves
(`powsled`) in SM2-Emu Libretro running in RetroArch. Compare the same four
riders with an optional final Relay (`powsledr`). No MAME or standalone
emulator is launched.

## Qualified Result

The four-program session **without Relay** reaches native race state 7 on all
four programs. Separate screenshots show advancing race views and Silver,
Red, Black and Yellow sleds. The native roster configuration is 6, the
four-rider configuration without Relay. Relay is therefore not required for
this tested race with the current reconstructed Master.

The five-program comparison with an optional final Relay also reaches native
race state 7 on all programs, with roster configuration 7. Separate Relay
screens show the native LIVE race camera. All nine linked program records exit
cleanly without forced termination or residual processes; 126 separate PNGs
are retained. Native IDs/count, SRAM CRC/identity and unchanged calibration /
EEPROM pass the focused review.

This is bounded qualification of the reconstructed program, not proof of the
factory Master program, original cabinet installation rules, full-course
completion, physical controller response or sound fidelity.

## Production Boundary

The installed normal core still exposes a maximum of three Power Sled
instances and ANS values 1 = Silver, 2 = Red, 3 = Black, plus Disabled.
This experiment uses a private build; **the expanded topology is not yet
available with the normal installed core**. Production source files, staged
and installed dylibs remain byte-identical. The dev core remains absent.

The private build changes only frontend topology limits and validation:

- Raise Power Sled maximum instance count from 3 to 5.
- Register the additional Linked Cabinets values instead of exposing only 3.
- Replace the exact Main / Relay / Slave triplet gate with one Main, one to
  three Slaves, at most one Relay and at most four rider programs.
- Retain the existing passive native-state observer. It does not force state,
  inputs, packet data or game execution. No new CPU ROM patch is introduced.

The native program already distinguishes rider identities 0 through 3. Its
roster diagnostic at Relay offset `0x249c0` assigns configuration codes 0–7
for one through four colors without / with Relay, with 8 denoting an invalid
roster. The current Master color publication and distribution fixes are
unchanged from `POWER_SLED_MASTER_COLOR_2026-10-10.md`.

## Isolated Inputs And Saves

Master uses native color 0 and the three Slaves use 1, 2 and 3. The optional
Relay retains its role `0x0100`; Master retains `0x0200`.

Each instance has its own configuration, controller index, native-save
container, input movie and capture directory. Experimental fixtures are
copies of qualified target-core saves. Only Ride bytes 8, 264 and 520 are
changed, and the outer SM2SRAM CRC is recalculated. NVRAM overlays and ANS are
disabled for rider programs so they preserve the isolated fixtures.
Calibration and EEPROM are unchanged.

**Yellow is an experimental native fixture value, not an acquired Service
Menu sample or an implemented NS / ANS option.** Its acceptance in this race
does not replace the agreed Phase 1 inventory and Phase 2 acquisition workflow
needed before extending the operator setting catalogue.

Reuse the previously qualified Manual race input movies. Master sends the
existing mode / boarding / start commands. Each Slave receives its own copy
of the qualified Slave registration input movie. No test/service input is
injected in the race sequence.

## Failed Preliminary Fixtures

`without-relay/run` used the previous private observer with the normal
three-instance limit. The requested value 4 was rejected, leaving the Main
in one-node loopback and Slaves waiting. No network or four-rider pass is
claimed. Main reached mode selection while alone; this does not qualify a
standalone race.

`without-relay/run-enabled` widened the parser and transport gate, but the
registered Core Option still exposed only 3. RetroArch substituted Disabled.
The owned runner was interrupted and cleaned up its instances. This is a
fixture preparation failure, not evidence that Relay is necessary.

`without-relay/run-registered` corrects all three frontend constraints and
passes native linking and four-rider race qualification.

## Evidence And Review

Evidence directory:
`build-libretro-gpu/validation/power-sled-four-riders-20261010/`.

`prepare.py`, `build-probe.py`, private/original source snapshots, fixtures,
commands, replays, logs, separate screenshots and `review.json` retain the
experiment. `review.py` checks exact native IDs/count, frontend roster,
advancing race-state samples, roles/local indices, SRAM identity/CRC and
three-copy Ride values, unchanged calibration/EEPROM and clean process exits.

The legacy runner's `native_link_ready` field recognizes only the original
triplet with `count=3` and is not a valid expanded-topology verdict. The review
checks actual `Native board ... alive=1 ... count=4/5` log markers independently.
A process-lifecycle `status=ok` alone is not treated as a gameplay pass.

## Roadmap Follow-Up

Refresh the conditional Service Menu color inventory, extend the persistent
acquisition manifest for Yellow where available, then integrate ANS 4, the
reviewed NVRAM value, expanded frontend topology rules and the runner's native
link diagnostics. Keep Relay as an optional final instance in `_relay`, use
separate saves per Slave, and arrange rider windows by physical Ride color
order. The user verified a coherent joined view with Master Silver followed
by Slave Red; the expected Silver / Red / Black / Yellow order for four
screens follows the native projection table and still needs joined-view
verification. Retain controller/save ownership when positioning windows.
Verify/deploy the normal core before providing the public four-rider launcher
command.
