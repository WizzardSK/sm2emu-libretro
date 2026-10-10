# Power Sled Native NVRAM Integrity And Initial Images

## Scope

This step verifies the native recovery rules for operator settings and
bookkeeping, and the suitability of complete, independent initial images for
`powsledm`, `powsledr` and `powsled`. Acquisition uses only SM2-Emu Libretro in
isolated RetroArch processes. Existing MAME code and reference screenshots are
read-only sources. Calibration menus are not visited or acquired.

Core: SHA256 `367cdfcb96969a7b4866cf32a5f6d4682d3b5fe3963dec5cbdd01184eef71390`.
No core implementation is changed by this verification step.

## Native Program Rules

The program's Backup RAM compare, recovery and write routines establish two
independent groups. Addresses below are i960 program offsets. Main uses the
known patched Relay approximation, whose patches lie outside these routines.

| Group | Copy Bases In Backup RAM | Compared And Written Bytes | Slave Compare / Recovery | Relay And Main Compare / Recovery |
| --- | --- | --- | --- | --- |
| Operator Settings | 0x000, 0x100, 0x200 | 28 (0x1C) | 0xED8B0 / 0xEDC20 | 0xED8C0 / 0xEDC30 |
| Bookkeeping | 0x300, 0x400, 0x500 | 52 (0x34) | 0xED9E0 / 0xEDD30 | 0xED9F0 / 0xEDD40 |

The recovery rule compares **complete blocks**, in this order:

1. If copies 0 and 1 agree, copy 0 replaces copy 2.
2. Otherwise, if copies 0 and 2 agree, copy 0 replaces copy 1.
3. Otherwise, if copies 1 and 2 agree, copy 1 replaces copy 0.
4. If no pair agrees, the program writes its embedded defaults to all copies.

This is whole-block agreement, not a vote on individual fields or bytes. The
routines do not calculate or store a checksum for these groups. The adapter's
SM2SRAM container CRC is a separate frontend check and is recomputed only to
make the isolated injected input readable by RetroArch/the core.

The final compared settings byte is 0x1B. Its comparator uses `cmpinci` with
27, compares the old index, then increments: bytes 0 through 27 are included.
The bookkeeping comparator increments before comparing against 52. The write
routines cover precisely 28 and 52 bytes respectively. No entire-16-KB checksum
or integrity claim is inferred from these two groups.

The full native settings default contains Checkpoints **49, 35, 35, 30, 30**,
Motion Angle **380 tenths (38.0 degrees)**, Country byte **0** and Ride byte
**0**. Ride 0 is the established Silver mapping for Main/Slave. Relay's displayed
role remains 0x100 and must not be named Silver on that basis. These are native
fallback bytes; Country/Ride still have no Use Default menu action. Country's
region interpretation and conditional ID assignment remain deferred.

A matching set of all-FF blocks passes the native agreement check. Agreement
alone therefore does not identify an initialized or semantically suitable
first-run image. Existing user saves must retain precedence, including saves
that the game's own recovery can repair. The existing frontend initialization
path imports a valid matching SRM first and suppresses automatic seeding when
native save files already exist. This source review does not claim a new
Power Sled automatic-seeding implementation.

## Complete RetroArch Recipe

Runner: `scripts/test-power-sled-nvram-integrity.py`.
Generated recipe, plan, input copies, process logs, native samples, screenshots,
SRM files and per-stage validation are retained under:
`build-libretro-gpu/validation/power-sled-integrity-20261009/`.
The recipe is complete before acquisition and the journal resumes validated
runs. Each program receives a copy of its own earlier target-core SRM; personal
saves, ROM archives and the original field-mapping evidence remain untouched.

The complete campaign comprises 11 trials on each of the three programs:

- Unchanged committed image.
- Each of the three single-copy disagreements.
- Each of the three matching-pair alternatives.
- Three different settings/bookkeeping blocks, exercising native fallback.
- Disagreement at each group's final compared byte.
- Differences immediately outside each compared/written group.
- Fresh reload of a complete independent initial image for each program.

Both groups are exercised together in each applicable trial. A settings marker
changes Checkpoint 0 between 49 and 80. A stable bookkeeping byte independently
marks the agreeing group. The no-pair trial uses three different markers.
Every run verifies the native selection, repaired copies, visible Checkpoints,
SRM identity/CRC, native extraction, live board link and clean process exit.
Changes outside the two groups and any EEPROM change reject the run. Native
bookkeeping time counters may advance inside their 52-byte group.

All 147 earlier operator-field records also pass file-hash verification and
whole-block agreement for both groups. The new campaign's `coverage.json` is
the authoritative runtime validation summary; `native-routines.json` pins ROM
files, routine hashes, offsets and embedded defaults without publishing ROMs.

## Independent Initial Images

The no-pair trial obtains settings initialized by the native program. The
initial-image reload uses each variant's own complete image and resets only
its three bookkeeping blocks to the proven native ROM defaults (zero). This
avoids seeding captured test time. The exact complete input payload is retained
as the candidate and verified by fresh-process reload. Its layout is 16,384
bytes of Backup RAM plus 128 bytes of EEPROM, matching the existing initial
NVRAM template interface. The candidate is not a serialized frontend header.

The runtime gate requires native settings defaults, whole-block agreement,
unchanged unrelated bytes/EEPROM and the expected menu values after reload.
Three independent payloads are retained in `initial-images/`, with their hashes
and exact reload source in the summary. Parent-template reuse is not claimed.
The factory block includes native startup bytes, but no cabinet calibration
measurements or universal calibration presets are derived from them.

These images qualify as NVRAM initialization candidates for the tested local
Main/Relay/Slave topology. They do not establish playable controls, motion
hardware, audible sound or linked gameplay. No Core Option, automatic override
or embedded initial template is implemented by this step.

## Next Integration Step

**Completed subsequently:** the approved fields and all three initial templates
are implemented and verified in RetroArch. Current evidence and deployment are
recorded in `Docs/POWER_SLED_NVRAM_OPTIONS_2026-10-09.md`. This document retains
the earlier native-integrity qualification snapshot.

Review the proven numeric fields and Main/Slave color mapping for per-game
NVRAM Settings, then implement the approved fields and independent initial
templates using the existing adapter boundaries. Country's region semantics,
Relay's hidden byte and conditional ID assignment remain separate questions.
Preserve valid user saves and unrelated settings/bookkeeping bytes. A future
manual override must synchronize the complete settings block across all three
copies; it must not fabricate a checksum or overwrite the bookkeeping group.

## Verification Result

The accepted campaign completes **11 trials / 33 program records**. All native
recovery, boundary, visible-value, SRM, EEPROM-preservation, unrelated-byte and
process/link gates pass. The final initial-image probe uses zeroed native
bookkeeping defaults; the earlier probe with captured elapsed time is retained
as superseded evidence. The three independently acquired and reloaded initial
payloads are byte-identical, SHA256
`447fbd4f9d1c81d442a1658a108475fe02038c3385e772f111b393434fd9792f`.
They remain documented per set; no unchecked clone/parent substitution occurs.

The three diagnostic YAML records, generated Game Settings catalogue and
roadmap are reconciled with the coverage hash. The review workbook retains
all earlier tables and its primary Core Options sheet unchanged, adding native
filtered green tables `PowerSledNativeIntegrity` (33 records) and
`PowerSledInitialImages` (three records). Reimport, formula-error inspection and
visual review pass. Diagnostic YAML audit (56 files), NVRAM catalogue audit
(87 sets / 311 existing options), complete field-recipe regeneration check and
`git diff --check` pass. No campaign process remains running. The build and
both installed core hashes match; this verification does not rebuild the core.
