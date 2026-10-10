# Power Sled Main Sled Color

## Finding

Main's first-person sled appeared black despite Ride ID Red. The retained
baseline and new private RetroArch observation reproduce this symptom.
The current Main is derived from Relay; MAME describes the factory Main
program as undumped and adapts Relay through three initialization patches:
[Model 2 Driver](https://github.com/mamedev/mame/blob/master/src/mame/sega/model2.cpp).
These observations do not establish the original cabinet's appearance.

## Cause And Correction

The first-person object initializer at `0x3fa80` keeps the local race index in
object offset `0xd0`. Main initializes its local index at `0x53e6f4` from the
native communication count minus one. The private read-only observer verifies
Main role `0x0200`, three linked boards and local index 2 during the run.

The three resource selections at `0x3fae8`, `0x3fb0c` and `0x3fb30` originally
read this race index and select row 2 of the native model table `0x39880`,
regardless of Main's NVRAM Ride color. Row 0 is internally labeled `White`,
row 1 `Red`, and row 2 `Brue`. Those internal names alone do not authenticate
cabinet color conventions. The operator's supported values remain Silver,
Red and Black as previously measured in the service menu.

Main-only database patches replace those three resource-index reads with calls
to an unsigned NVRAM byte load at `0x01d00008`. The helper and return fit the
original twelve zero bytes at `0x3fb74`–`0x3fb7f`, before the unchanged next
function at `0x3fb80`. It changes only global `g4`, matching the replaced load's
result register. Object `0xd0`, network roles, race inputs, movement and
communication continue using the original index. The original resource tables,
model data, labels, ROM chip CRCs and instruction addresses are preserved.
No new option, core binary change or ROM archive edit is required.

This corrects the local first-person sled. Remote and third-person appearances
use other selection paths and are outside this qualification.

## Verification

Evidence root:
`build-libretro-gpu/validation/power-sled-main-sled-color-20261010/`.

One private observer baseline and one unchanged-installed-core candidate use
the established RetroArch linked runner, the same save fixture and Manual
input movies, Main Red / Slave Silver / Relay, a 95-second observation and
three capture rounds. They each show advancing races; Main's candidate sled
is red in the directly reviewed first and third captures, whereas the baseline
sled is black. Captures are not synchronized to the same race frame.

`runtime-review.json` verifies nine normal exits, native links/roster, no runtime
i960 reset, Main's native role, valid SRAM identity/CRC and three-copy Ride
values. Paired calibration and EEPROM remain identical. Every instance emits
PCM; this is not a sound-fidelity comparison. The observer source and normal
build core were restored byte for byte; no diagnostic binary is installed.
`candidate-patches.json` and `candidate-disassembly.txt` retain the exact
private patch and decoding. The production patch list is checked against
that tested candidate before deployment.

## Requested Slave-Derived Main Comparison

An additional isolated 95-second RetroArch observation uses the previously
qualified Slave-derived Main initializer, without the new sled-color patches.
The installed core, input movies, initial saves and Main Red / Slave Silver /
Relay configuration match the other observations. The Main again shows a
black first-person sled in the first and third captures. Three more normal
native-linked exits, SRAM/ANS integrity, paired calibration/EEPROM and PCM
checks pass. Changing program base does not resolve the observed color issue.

The Slave program contains the same three original resource-index reads at
`0x3fad8`, `0x3fafc` and `0x3fb20`, shifted by 16 bytes relative to Relay.
Evidence is retained under `slave-base/`. This is a color comparison, with no
new speed qualification: Main's captured timer reads 42.12 → 42.07 while the
course view changes. The cause of that timer behavior is not investigated in
this bounded color task. It does not affect the black-sled observation or the
Red-sled result in the corrected production-base candidate.

## Deployment

The staged and both installed RetroArch databases are updated with backups
and matching hashes recorded in the evidence root's `deployment.json`:
`946ccb6a389bc7912db5bcd28c3e48f27a2e641bc35283fd17d4c99a7bbcd6a4`.
The installed core remains SHA-256
`abda589c10b47acfe472f41bc2e57ec5682edd512b469bbbef490ef6ac6f15fe`.
Restart the linked group to load the updated database.
