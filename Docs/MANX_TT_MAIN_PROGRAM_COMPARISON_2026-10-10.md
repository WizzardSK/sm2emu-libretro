# Manx TT Main Program And Audio Table Selection

Date: 2026-10-10
Scope: Static Revision C/D Comparison And Retained RetroArch Evidence

## Question And Conclusion

The user requested a comparison of the main programs to investigate whether
an unimplemented cabinet or sound-board detection path selects different audio
sample tables. Revision D `manxtt` was compared with Revision C `manxttc`,
whose catalogue preserves the Twin sound ROMs.

No such additional selection path was found in the reviewed audio producers,
UART initialization/dispatch, or sound-driver lookup. C and D send the same
Slide ON/OFF command identities. Their interpretation differs in the audio
ROM data, where Deluxe aliases both to the Japanese feet-on-step warning.
This supports the cabinet/audio-ROM mismatch diagnosis; it does not establish
the original factory pairing for every Revision D Twin cabinet.

The subsequent [documentary review](MANX_TT_AUDIO_DOCUMENTARY_REVIEW_2026-10-10.md)
confirms distinct Twin/Deluxe audio configurations in Sega documentation and
MAME dump history. Revision D originated from a Deluxe setup; exact factory
D/Twin pairing remains undocumented in the reviewed sources.

## Main Program Comparison

| Path | Revision D Address | Revision C Address | Result |
| --- | --- | --- | --- |
| Three-byte host command table | `0x6c1f0` | `0x6c1b0` | All 768 compared bytes equal |
| Logical sound-index producer | `0x6e610` | `0x6e5d0` | Only the relocated table address differs |
| UART initialization | `0x6e200–0x6e257` | `0x6e1c0–0x6e217` | Byte identical |
| Slide cabinet selection | `0x3bd30–0x3be57` | `0x3bcf0–0x3be17` | Byte identical |

There are 109 aligned direct CALL/BAL references to the sound-index producer
in each image. Pairing those references in order and comparing 48-byte local
windows gives 82 byte-identical windows; the remaining 27 differ only in
reviewed code/data address relocation. This is a bounded static comparison,
not an exhaustive control-flow proof for every indirect call or distant branch.

The slide block reads the native cabinet flag at `0x51405a`: Twin chooses
logical indices 99/100 (`A0 11 5D` / `A0 11 5E`); Deluxe chooses indices
158/159 (`AE 11 20` / `AE 11 21`). The producer resolves a fixed host command
table. It does not choose a PCM pointer or inspect the audio ROM revision.

The reviewed UART routines initialize the transmitter, queue command bytes
and check transmitter readiness. Their explicit data-register references are
stores to `0x01c80000`. No audio firmware-identification response selecting a
different command table was found in these paths. The native main and sound
CPUs communicate over serial; their ROMs and sample RAM are separate.

## Audio Program Comparison

The first `0x8000` bytes of `epr-18924a.30` (Deluxe) and `epr-18826.30` (Twin)
are exactly equal, including the reviewed 68000 driver. Their first difference
is in the ROM data following that prefix.

The native sequence dispatcher at `0x6035de` reads its root from the fixed ROM
location `0x60801c`, then indexes that root using the command argument. The
roots are `0x610e92` for Deluxe and `0x612716` for Twin. The reviewed sound
memory map fixes the program ROM at `0x600000–0x67ffff`; sample banking is
separate from that ROM mapping.

Deluxe commands `4E`, `5D` and `5E` resolve to the same sequence at `0x61141a`.
Twin gives them distinct entries: Japanese warning at `0x612c9e`, slide note-on
at `0x612d10`, and slide note-off at `0x612d18`. A PCM bank change alone cannot
turn the shared Deluxe note-on sequence into the distinct Twin note-on/off pair.

The native reset/stop handlers clear voices/sequencer state and reload the
same ROM-owned channel presets. The sample-preload handler reloads headers
from the same ROM-owned sample table. No reviewed reset/preload path changes
the sequence root according to Cabinet Type.

The [official MAME driver](https://github.com/mamedev/mame/blob/master/src/mame/sega/model2.cpp)
likewise fixes the sound program ROM and gates sample banking on regions larger
than 8 MiB; Manx TT has 8 MiB. MAME retains a TODO about lower sample-control
bits. No reviewed ROM path associates those undocumented bits with Twin/Deluxe
sequence-root selection. This remains a hardware-documentation limit, not a
demonstrated missing mechanism that explains the warning.

## Retained Runtime Comparison

The previous qualified RetroArch traces already exercise both main programs:

| Configuration | Slide ON Frames | Slide OFF Frames |
| --- | --- | --- |
| D Main / Original Deluxe Audio / Twin Cabinet | 5,740; 5,772 | 5,771; 5,773 |
| C Main / Original Twin Audio / Twin Cabinet | 5,697; 5,716 | 5,714; 5,717 |
| D Main / Private Twin Audio Comparison / Twin Cabinet | 5,740; 5,772 | 5,771; 5,773 |

All transmit `A0 11 5D` / `A0 11 5E`. Native startup and race progression
differ between C and D, including their retained SRAM seeds; these frame
numbers do not establish matched physical-state repetition rates.

Changing only the audio ROMs for the same D main program preserves all 11,665
timestamped UART bytes exactly in the retained comparison. This rules out a
different observed host initialization/command sequence as the source of that
comparison's audio difference. It does not qualify every sound in either mode.

The [targeted driver observation](MANX_TT_SOUND_ROUTING_2026-10-10.md) separately
confirms that the original Deluxe audio interprets those effects as note `45`,
sample header `02ac`, the identified Japanese warning. The user's latest replay
contains one audible occurrence, despite four internal starts.

## Evidence And Production State

Private ignored root:
`build-libretro-gpu/validation/manxtt-main-program-comparison-20261010/`.
`compare.py`, reconstructed main images, reference/caller lists and
`summary.json` retain the reproducible comparison. ROM images must not be
committed. The script uses static decoding and existing target-core RetroArch
logs; no MAME or standalone emulator was run.

No new runtime campaign, source modification, rebuild or deployment was needed.
Normal build and both installed cores still have SHA-256
`44cf32065c3208eaa34b601a4a04423b1c5217e7b14fa54e0debc79b3fbd3d5b`.
The production correction remains pending. Preserve this comparison when
designing cabinet-appropriate audio configuration; do not treat native Cabinet
Type as evidence that physical ROMs could automatically change on the cabinet.
