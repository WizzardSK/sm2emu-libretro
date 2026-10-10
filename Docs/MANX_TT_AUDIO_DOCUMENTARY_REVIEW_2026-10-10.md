# Manx TT Audio Documentary Review

Date: 2026-10-10
Scope: Sega Manuals And MAME Dump Provenance

## Findings

The documentary evidence supports distinct physical audio configurations for
Twin and Deluxe. A Cabinet Type setting in the main program does not itself
establish that the installed sound ROMs support both configurations.

The Revision D dump was documented as originating from a Deluxe setup. The
review found no Sega instruction establishing a factory Revision D/Twin audio
pairing or automatic switching of the sound program's sequence tables.

## Sega Twin Manual

The inspected manufacturer scan is **420-6207-03**, cover marked First Printing
FB, Twin Type. Section 16-2, printed page **50** / PDF page **55**, identifies
ROM board **834-12467**. Its ROM-layout drawing shows the Twin sound program
**EPR-18826** at IC30 and sample ROM **MPR-18827** at IC31. The drawing also
shows the main-program base numbers EPR-18822 through EPR-18825; it does not
establish the later Revision D suffix.

Source: [Sega Twin Owner's Manual](https://segaretro.org/images/0/00/ManxTT_Model2_Manual_Twin.pdf).
The [HFS mirror](https://db.hfsplay.fr/files/2018/10/06/be904fc4-e0ba-47e5-876a-49d8c71e83b4.pdf)
contains the same PDF bytes. Both downloads have SHA-256
`45942fb1834dd83d45948e1a8e82839cb5d4eb773b7f91ae57507ff5dbfbc810`.
The scan is coarse; enlargement assists reading but does not restore detail.

## Sega Deluxe Manual And Service Archive

The Sega Amusements USA [Deluxe game-board composition](https://backup.segakore.fr/sauservice/Manuals/Manx%20Folder/MDhtml/MD55.html)
identifies ROM-board assembly **834-12277**, whereas Twin lists **834-12467**.
The linked drawing was subsequently inspected in the in-app browser. Comparing
it with the Twin manual shows the same general ROM-board component placement,
connector positions and outline. The different assembly numbers alone do not
establish a different bare PCB or electrical layout. The Deluxe drawing also
explicitly shows the separate **837-12279** sound board.

Both manuals list CPU board **837-10848-01-91**, video board **837-10849-02**
and communication board **837-12396**. The exploded drawings show the same
general board-stack arrangement. These are assembly and component-placement
drawings, not copper-layer artwork or circuit schematics; they do not establish
identity of every trace, jumper or decoder connection. The coarse Deluxe scan
also limits individual ROM-label reading. A full-page browser screenshot is
retained as `deluxe-layout-browser.jpg` in the private evidence directory below.

The [Sega service index](https://backup.segakore.fr/sauservice/Manuals/Manx%20Folder/manxmenu.html)
lists cabinet hardware, billboard, communication cable and motor bulletins.
The reviewed motor-feedback and loose-hardware bulletins describe mechanical
or wiring faults. Neither provides an audio-ROM replacement instruction or a
sound-table selection protocol. This is a bounded search, not proof that no
additional service document exists.

## MAME Provenance

| Date | Primary Record | Relevant Evidence |
| --- | --- | --- |
| 2012-06-10 | [Brian Troha audio correction](https://github.com/mamedev/mame/commit/6dbf84809fa9bef501c21d5d637ef065fae6502a) | Corrected Revision C audio using the manual: EPR-18826.30 and MPR-18827.31 for Twin. MPR-18763.31 was identified as Deluxe; EPR-18924a.30 was still an unassigned variant in this record. |
| 2013-08-14 | [Revision D addition](https://github.com/mamedev/mame/commit/5d4ac9d25bbe37add7892131ca5bc01699d35bc6) | Revision D was found in a Deluxe setup. The set uses EPR-18924a.30, MPR-18763.31 and additional Model 1 audio ROMs EPR-18742.7 / MPR-18743.32. Credits: ShouTime and The Dumping Union. |
| 2022-07-19 | [Catalogue clarification](https://github.com/mamedev/mame/commit/2ff1f130c34a6ff29468d9f9d633ba13659180e3) | Marks D as DX/Twin with Deluxe default, and explicitly retains C in Twin configuration to preserve the Twin sound ROMs. |

The 2013 record identifies the Deluxe additional board as **837-12279**, using
the Model 1 sound-board design **837-8679** with **one 315-5560**. Its initial
MAME speaker routing was explicitly described as uncertain. This supports
reusing existing board emulation while checking the actual chip population and
mixing; it does not qualify every missing Deluxe sound or the final speaker mix.

The commits were inspected directly in the local MAME Git history. The 2012
record was additionally downloaded from the official GitHub API. The official
[MAME 0.150 release notes](https://www.mamedev.org/releases/whatsnew_0150.txt)
independently list the Revision D Deluxe addition and its dump credits.

## Interpretation For The Core

Combined with the [main-program comparison](MANX_TT_MAIN_PROGRAM_COMPARISON_2026-10-10.md)
and [observed sound routing](MANX_TT_SOUND_ROUTING_2026-10-10.md), the evidence
supports two separate defects in the available emulated configuration:

- Twin mode with the catalogue's Deluxe audio interprets slide effects as the
  Japanese warning. The documented Twin audio provides the appropriate effect
  mapping. The alias alone does not demonstrate an original game bug: those
  command identities need not be used with the Deluxe physical configuration.
- Deluxe has a documented additional audio board, whose production connection
  is missing in this core. This is a concrete emulation gap.

The search provides no affirmative evidence for a foot-sensor input or automatic
firmware/sample-table detection explaining this warning. That hardware question
remains bounded by the reviewed sources and paths. Exact factory D/Twin pairing
remains unproven; a D-main/Twin-audio implementation must be described as a
compatibility reconstruction supported by the code and private comparison,
unless further factory evidence is found.

The next correction should select coherent audio hardware/ROM configurations,
preserve the supplied dumps and save/configuration lifecycle, and connect the
Deluxe board. Do not silence, suppress or rate-limit the warning as a substitute.

## Evidence And Scope

Private downloaded sources and rendered manual pages are retained under
`build-libretro-gpu/validation/manxtt-documentary-20261010/` (ignored).
No ROM was downloaded or modified. This review changes documentation only;
there was no emulator run, rebuild, deployment or production correction.
