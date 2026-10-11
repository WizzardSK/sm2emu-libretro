# Power Sled Two Cabinet Fix — 2026-10-10

## Symptom And Cause

The user's `--game powsledm:1,powsled:2 --controllers 0,1` session
remained black on Main and at the network boot counter on Slave. Both processes
exited cleanly, but neither reported a ready roster or native link. The old
installed core was `2429a518ba4d36cb2b579329030004d44e66954ab195d46bd2c7e82b3842cb27`.

The launcher correctly requested two participants. Power Sled Core Options
registration omitted `2`, and its parser required at least three. RetroArch
therefore supplied `disabled` to the core, as confirmed by the user's retained
logs. The transport already permitted one Main and one Slave without Relay.

## Correction

Register Disabled / 2 / 3 / 4 / 5 and accept the same totals for each Power Sled
program. Keep the existing roster requirement: exactly one Main, one to three
Slaves, and at most one Relay. Align the runner's maximum with five; the
specialized three-program NVRAM acquisition recipe remains unchanged.

No ROM patch, communication protocol, input mapping or NVRAM layout change is
needed. Relay retains its manual color and fixed automatic Relay value. The
launcher continues to pass literal game lists without compatibility checks.

## Verification

Core, save RAM and Netpacket targets build. Save RAM checks cover registration,
accepted totals and rejection of invalid values. Netpacket checks cover the
valid pair, duplicate Main rejection and a pair with no Slave rejection, while
retaining four/five-participant checks. Eight launcher checks pass.

The normal RetroArch core was updated with a backup and matching build/install
SHA256 `1e72cd27afd311a767e460477f252868303f286b2915a5d225dff085c54e0a87`.
The removed development core remains absent.

Evidence: `build-libretro-gpu/validation/power-sled-pair-20261010/` contains
commands, installation record, check logs, isolated runtime reports, screenshots
and save integrity review. Initial bounded replay qualifies both native links
with count 2, selection and boarding, clean exits and no residual processes.
SRM identity/CRC and all three Silver/Red copies pass; EEPROM is unchanged.
The longer replay (`runtime-race/result.json`) captures both riders racing with
positions 1 and 2, visible Silver/Red first-person sleds and advancing race
clocks. Both participants report a ready roster and native count 2, then exit
cleanly without residual processes, shutdowns or unhandled instructions. Save
identity/CRC, three-copy colors and unchanged EEPROM pass again.

## Canonical Launch

```sh
python3 /Users/andrea/dev/sm2-emu-libretro/scripts/launch-linked-cabinets.py \
  --game powsledm:1,powsled:2 --controllers 0,1
```

Existing launcher sessions can be reused; explicit ANS values remain
authoritative. Physical controller behavior and factory Master fidelity remain
outside this bounded correction.
