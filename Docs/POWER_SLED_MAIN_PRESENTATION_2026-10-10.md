# Power Sled Main Mode-Selection Scene

## Reproduced Omission

The deeper Master-path analysis identifies the drawing-task initializer at
Relay offset `0x33790` / Slave offset `0x33780`. The native mode-selection task
list registers this initializer. It replaces its own task callback with a
color-specific drawing function for rider identities 0–3, or the Silver
function for Relay. Native Master identity `0x0200` selects none of them.

An isolated baseline in the target Libretro core running in RetroArch reproduces
this result: Main displays the Manual / Professional overlay on a black
background, while Slave displays the 3D scene and character. A passive private
observer finds the unchanged initializer in Main's task list throughout state 5,
with no selected color-specific drawing callback. Native Main role is `0x0200`,
communication count is 3 and local race index is 2.

## Focused Correction

Replace the original role read with an unsigned read of the validated native
NVRAM Ride byte at `0x01d00008`, only in Main's mode-selection drawing initializer.
Reuse the original color branches, drawing routines and assets.

| Donor | Instruction Offset | Original Read | New Read |
| --- | --- | --- | --- |
| Relay | `0x33790` / `0x33794` | `ldos 0x005293f0,g4` | `ldob 0x01d00008,g4` |
| Slave | `0x33780` / `0x33784` | `ldos 0x005293f0,g4` | `ldob 0x01d00008,g4` |

Relay-based Main uses two additional database patch words. Slave-based Main
uses the equivalent two guarded patch words in the existing Libretro adapter.
The complete Slave patch list is validated before any word is changed.
Main's native role, packet identity, operator commands, race index, graphics
routines, instruction addresses and sound path retain their existing behavior.
No option, input binding or state-format change is introduced. User ROM archives
are not modified. Other game definitions and the Slave/Relay programs themselves
are unchanged.

## Related Offset Selectors

The remaining role-dependent paths at `0x18c30` and `0xc2bc8` select placement
values consumed by graphics/display-layout code. The former's fields
`0x00529358` / `0x0052935c` feed the drawing path at `0xc22d8` and numerous
viewport/graphics consumers. Returning without a rider-specific offset for Main
is not itself a demonstrated fault. The private candidate restores the missing
scene without changing either path, so they receive no speculative patch.

The two unbound operator commands from the earlier analysis remain documented
research findings. No new binding or unknown global-state activation is needed
for this correction.

## Verification And Retained Evidence

Evidence directory:
`build-libretro-gpu/validation/power-sled-main-presentation-20261010/`.

The baseline and candidate use the existing linked RetroArch runner, the same
qualified Manual input movies, isolated saves and Main Red / Slave Silver /
Relay. The candidate changes only the two graphics-selector words in its
private database. Nine capture rounds span selection, boarding and race entry.
The passive observer source and normal binary are restored byte for byte after
building the private diagnostic core; it is never installed.

The candidate displays the 3D scene and Red sled behind the same Manual /
Professional overlay. Its task list selects the drawing callback instead of
retaining the initializer. All sampled selection records preserve native Master
role `0x0200`, count 3 and local index 2. Both baseline and candidate reach race
state 7. Six normal exits, native links/roster, SRAM identity/container CRC,
three-copy Ride values, identical paired calibration/EEPROM and nonzero PCM
pass. No runtime CPU reset or premature movie termination is detected.
Captures are not frame-aligned, so no pixel equality or speed comparison is
claimed. Nonzero PCM does not qualify acoustic fidelity.

Production XML is checked against the tested private candidate's exact patch
map. Only `powsledm` changes; every existing patch is preserved. The updated
ROM-free donor checks pass, including atomic rejection of an incompatible new
presentation patch site, CRC failures, local/sibling lookup and other-set no-op.
The normal core and focused checks build successfully.

Production runtime results and deployed hashes are recorded in the evidence
root's `runtime-review.json`, `visual-review.json` and `deployment.json`.
Only Red is visually qualified in this bounded comparison; the unchanged native
color branches remain responsible for the other supported Ride colors. Physical
controllers, original Master firmware fidelity and full-course completion are
outside this correction's qualification.

## Installed-Core Confirmation And Deployment

Two additional normal-core sessions use the original user archives, the
configured installed database and isolated saves, selecting Relay and Slave
respectively. Both reach Main/Slave race HUDs and the Relay race-camera view.
Slave-derived Main also displays the restored selection scene and Red sled.
All six normal production exits and integrity checks pass, bringing the bounded
comparison to twelve clean program records. No diagnostic observer is present
in either normal-core log.

Both installed core copies and the staged/configured/fallback databases are
updated with retained backups and verified matching hashes:

- Core: `598e9864c4858f60b15a07e91e0d8cb684188d2e16fff47ac51305daccaed296`.
- Database: `080181ab494c3c3889ab4f173985e31c43dce11ef45bb1b9b135c85a7549b8f9`.

Restart the linked group to load the new program/database. The diagnostic edits to `core.cpp`
are restored from the observer checkpoint; production emulation changes are limited to the Main graphics-selector patches described above. No commit
or push is performed.
