# Power Sled Master Role And Rider Color

## Request And Baseline

Make the reconstructed Main retain its command role while participating as the
rider selected by native Ride ID. The requested topology is Main Silver / Slave
Red / Relay, with ANS `1`, `2`, `relay` respectively. The factory Main program
has not been dumped; this work extends the Relay-derived reconstruction rather
than authenticating factory behavior.

The unchanged baseline passes native communication but stops in game state 3
with the mandatory Silver Ride diagnostic. Main's caption and first-person
resources already use its NVRAM color, whereas the original roster counts only
ordinary rider identities. Native Master `0x0200` and Relay `0x0100` are separate
roles. Original Slave derives its identity and local index from Ride ID.

## Focused Program Changes

Use database ROM patches, retaining original archives, chip CRCs, sound routing,
Master command lookup, Relay role and all original routines outside the patch
sites. Peers must use the same updated Power Sled program definitions.

| Path | Relay/Main Address | Change |
| --- | --- | --- |
| Main TX header | `0x28b0` | Retain role `0x0200` and its complement; publish `0x434d0000 | Ride ID` at header offset 8. This is a reconstruction extension, not a documented factory field. |
| Main initializer | `0x15844`, `0x15868` | Use native settings byte 8 for the local rider index, retaining the separate command role. |
| Roster | `0x24a24` | Retain the Master-present flag and count its announced rider color. |
| Rider packet selection | `0xcd414`, `0xcd46c` | Read Main's announced color for rider matching; ordinary rider and Relay identities retain their original interpretation. |
| Cabinet counts | `0x14f90`, `0x14ffc` | Include colored Main in both counts used to distribute race records. |
| Main panorama selection | `0x18c50`, `0x18c80`, `0x18cbc` | Select the native panorama offset from Ride ID rather than command role. |

Slave sites after its initializer are 16 bytes earlier than the Relay addresses.
The two cabinet-count sites precede that relocation and have identical addresses.
Helpers occupy verified empty ROM space at `0x1f0000`–`0x1f0357`; branch and call
targets are decoded and retained. Only the Master writes the additional header
word. Both rider-count and rider-mapping adaptations apply to all three programs.
The startup diagnostics remain active; CLI colors are not substituted.

## Failed Initial Variants And Cause

The first private variant clears the startup diagnostic and reaches native race
state 7, with advancing counters. Main and Slave nevertheless show a black 3D
scene; the user also reports duplicate Black 03 sleds and Reverse at race entry.
The inverse color combination fails visually as well. Restoring Main's original
local index alone does not resolve this failure.

The roster includes Main, but the original two additional counts still exclude
it. Race initialization consequently prepares two rider cabinets while record
ownership/distribution uses one. Aligning the counts makes the course render
and the race advance on both riders. This is a program-data correction, not a
renderer workaround or a skipped diagnostic.

The user independently observes the restored intro, race entry and a progressing
Main countdown, which previously remained at 1.

## Bounded RetroArch Evidence

Evidence root:
`build-libretro-gpu/validation/power-sled-master-color-prototype-20261010/`.
Reuse `scripts/test-retroarch-netpacket.py`, the established Manual input movies,
original user archives and isolated per-program configs/SRAM. No MAME or
standalone emulator is launched. A private passive observer records native
roles, packet identities, local indices, commands, counters and state changes;
its source and normal build binary are restored byte for byte.

| Observation | Outcome |
| --- | --- |
| Unchanged Main Silver / Slave Red | Native links pass; game-level startup fails. |
| Initial color extension, both color orders | State 7 and counters pass; black Main/Slave 3D fails qualification. |
| Initial extension with original Main index | Black 3D persists. |
| Corrected counts, Main Silver / Slave Red | Main Silver and Slave Red visibly race; Relay shows the live race camera. |
| Corrected counts, Main Red / Slave Silver | Inverse combination also visibly races with the corresponding colors. |
| Normal core, corrected counts | Nine capture rounds show boarding, countdown and advancing racing; race colors are Silver/Red. Original boarding panorama remains under separate visual interpretation. |

`runtime-review.json` checks 18 observer program records, clean exits, native
links/rosters, preserved application roles, announced Main color, race counters,
SRAM identity/container CRC, three-copy Ride values and unchanged calibration /
EEPROM against the isolated baseline. Truncated duplicate log fragments are
excluded by requiring complete eight-digit color words, rather than interpreting
a partial log token as packet data. `normal-runtime-review.json` adds nine
normal-core records and 96 separate captures across the counts-only comparison
and the final two panorama/color orders. All nine exit normally with no forced
kills or residual peers and valid SRAM/calibration checks. One overlapping launch
is rejected before starting. One final inverse attempt fails at macOS window
positioning before peers start; a retained retry completes the comparison.

## Pre-Race Sleds And Countdown

The native state-6 task table registers the boarding actor initializer at
`0xd0980`. It constructs four actors with indices 0–3 and selects their original
models from `0xce000 + index * 0xa8`, independently of the local NVRAM Ride ID.
The update at `0xd05f0` retains those object/model identities. This is a shared
panoramic introduction, not four newly discovered network riders. Seeing Black
03 from more than one cabinet therefore does not alone demonstrate duplicated
race identities. Historical original-Slave boarding captures also include Black
and Red sleds despite a local Silver setting. The exact user-reported pair of
Black 03 views is not frame-matched to those older captures; no claim of complete
intro asset fidelity is made.

The native offset selector at `0x18c30` handles rider identities but leaves Main
`0x0200` outside its cases when multiple riders are counted. The final Main-only
six-word change reads Ride ID at its three visual selectors, preserving the
native offset cases. Final Silver Main captures show a shifted panorama with
Yellow 04 and Black 03; the inverse run also shows the Red mode-selection sled,
progressing countdowns and advancing Red Main / Silver Slave races. The scene's
other sleds are not forcibly recolored into the local rider. Countdown and local
racing color are independently visible in the retained captures.

## User Observation: Physical Display Order

The user reports that Master Silver followed by Slave Red produces a coherent
single view when the two screens are placed side by side. Record this as user
runtime evidence of the panoramic display arrangement, separately from the
automated per-program race qualification.

Ride color therefore also selects the cabinet's position in the shared
panorama. This agrees with the native identity-dependent projection offsets
at `0x18c30`, documented in
`POWER_SLED_OPERATOR_AND_LAYOUT_ANALYSIS_2026-10-10.md`. Changing Master / Slave
assignment does not by itself change the required display order for a given
color arrangement.

Use Silver then Red for the observed two-screen arrangement. The expected
four-screen order is Silver, Red, Black, Yellow, inferred from the native
identity/offset table; joined four-screen alignment has not yet been verified.
The expanded launcher follow-up should arrange rider windows by this physical
color order while retaining each instance's game, controller, save directory
and network identity. The optional Relay remains separate and last.

## Qualification Limits And Deployment

Production `data/games.xml` matches the tested final candidate's exact patch map:
114 new words across Main/Slave/Relay; every existing patch and every other game
remain unchanged. There is no emulator-machine, renderer or ABI implementation
change. Database backups, deployed paths and hashes are retained in
`deployment.json`.

- Source/staged/configured/fallback database SHA-256:
  `7502de258343a33d6bd5d2f05cd934a53496dfe532432b3a0e1015b1a258d8b1`.
- Normal build and installed core remain SHA-256:
  `8d9dfa8dcb7c812b89d67944a4108d6751e460888b17a47e1b5ca9d1ac4c2e6d`.
- Only the main installed core exists; the removed dev core is not recreated.
- User saves and ROM archives are not rewritten. Restart the linked group to
  load the new database. No commit or push is performed.

The initial failed prototypes remain retained evidence; only the corrected
counts/panorama candidate is integrated.

This bounded work qualifies the two Silver/Red orders only. It does not establish
unrestricted colors/topologies, mixed old/new peer programs, complete-course
behavior, physical controller operation or original undumped Master fidelity.
The native roster still requires the corresponding ordinary rider colors.
No new menu option, controller binding or persistence format is introduced.
