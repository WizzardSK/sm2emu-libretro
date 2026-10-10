# Manx TT Deluxe And Twin Sound Routing Comparison

Date: 2026-10-10
Scope: Private RetroArch Diagnostics; Japanese Warning Command Collision Identified

## Qualified Replay Results

The same Revision D main program and 6,600-frame controlled input replay were
run with Twin NVRAM and with Deluxe NVRAM plus the previously qualified motion
acknowledgement stub. Original Deluxe sound ROMs were used in both cases.
The observer records native sound-table producers, transmitted bytes and
SCSP slot starts with fingerprints and private copies of their PCM source data.

| Check | Twin | Deluxe With Stub |
| --- | --- | --- |
| RetroArch process exit | 0 | 0 |
| Wall time | 112.8 seconds | 112.3 seconds |
| Complete EEPROM vs isolated seed | Unchanged | Unchanged |
| Native and SRAM container CRCs | Pass | Pass |
| PCM vs preceding same-mode baseline | Exact common prefix | Exact common prefix |
| PCM frames compared | 4,917,150 | 4,905,390 |
| New native Voice-category commands in frames 5,400–5,999 | 0 | 0 |
| New native Voice-category commands in frames 6,000–6,599 | 0 | 0 |

Exact PCM prefix comparisons support observer transparency in these cases.
They do not identify speech or establish correct sound fidelity.

## Confirmed Cabinet Routing

The same native caller selects different logical indices and destinations:

| Native Return IP | Twin Logical Index / Packet | Deluxe Logical Index / Packet |
| --- | --- | --- |
| `0x3d324` | 45 / `A0 11 0C` | 134 / `AE 11 08` |
| `0x3c66c` | 63 / `A0 11 30` | 146 / `AE 11 14` |
| `0x3c5f8` | 64 / `A0 11 31` | 147 / `AE 11 15` |

All belong to the game's Sound Test effect categories. The Twin bank window
has 69, 22 and 22 events respectively; Deluxe has different counts as its native
progression differs. The same input schedule does not preserve the same
motorcycle state or race time across cabinet modes, so those counts must not
be used to infer a faulty repetition rate.

Deluxe also queues Voice indices 27 and 31 (`A0 11 49` / `A0 11 4D`) during
its pre-race sequence, at native frames 3,484 and 3,601. They are absent in
that part of the Twin trace. This is consistent with a cabinet-specific
operation sequence. Native labels identify index 27 as the English AMS
introduction and index 31 as the English feet-on-step warning. Neither is the
Japanese warning identified by the user during Twin racing.

## Sound Program Data

The command `A0 11 30` resolves to note-on channel E, note `0x2c`, with velocity
127 in the Deluxe sound program and 120 in Twin. The effect and voice sequences
are distinct entries, although they use the same MIDI channel. For example:

| Logical Index | Category | Packet | Deluxe Sequence Note |
| --- | --- | --- | --- |
| 45 | Effect | `A0 11 0C` | `0x0a` |
| 63 | Effect | `A0 11 30` | `0x2c` |
| 8 | Voice | `A0 11 1E` | `0x1a` |
| 27 | Voice | `A0 11 49` | `0x40` |
| 31 | Voice | `A0 11 4D` | `0x44` |

Static sound-ROM inspection also confirms different initial channel preset
IDs: channel E starts with ID 8 in Deluxe and ID 5 in Twin. These are data
differences, not proof of an incorrect active instrument or a warning sample.
Later native commands may alter channel state.

## Sample Correlation Limits And Rejected Direct Scans

The race observer retains PCM fingerprints, but independent music sequencing
continues between host commands. A slot starting after the nearest UART packet
cannot be attributed to that packet without a verified sound-driver path.
The race slot trace has a chip sample clock, not an explicit native frame;
holding the last UART frame across silent command intervals does not give an
exact slot frame. Do not use such temporal proximity as a causal mapping.

A separate short diagnostic attempted six native-table Sound Test packets,
with normal host audio traffic suppressed after frame 600. Each command was
preceded by the native category reset packet, logical index 3 (`A0 00 03`).
Two first scans delivered packet bytes together; two follow-ups paced each
byte separately and added explicit native frame stamps to slot observations.
All four processes exited normally, their EEPROM remained unchanged and CRCs
passed. However, the observed slot responses did not isolate the intended six
sounds from ongoing music. The stimulus itself remains unqualified, including
sound-driver initialization and reset prerequisites. These scans provide no
evidence that the warning was reproduced, changed or corrected.

Do not retain the direct injection as an established Sound Test runner, infer
a production FIFO bug from it, or substitute its output for the game's own
menu sequence. Further stimulus work requires a concrete driver-state gate.

## User Identification And Confirmed Command Collision

The user identified the offending sample through the native Sound Test in
Revision D `manxtt`, Cabinet Type Twin: **When riding please place feet on
stepJ**. They additionally confirmed the Japanese version is heard with both
Export and Country USA. Their same-set comparison confirms that the unwanted
voice is absent during Deluxe gameplay, while other sounds are missing there.
These listening results are user evidence, separate from the automated traces.

The main-program label pointer table at `0x6dcc0` resolves the following entries:

| Logical Index | Native Label | Host Packet |
| --- | --- | --- |
| 31 | When riding please place feet on stepE | `A0 11 4D` |
| 32 | When riding please place feet on stepJ | `A0 11 4E` |
| 99 | SE_Slide1_ON | `A0 11 5D` |
| 100 | SE_Slide1_OFF | `A0 11 5E` |

In the Deluxe sound program `epr-18924a.30`, all three packet arguments
`4E`, `5D` and `5E` point to **the same sequence at `0x61141a`**:
`80 9E 45 55 00 FF 2F 00`. Consequently Slide ON and Slide OFF both launch
MIDI note `0x45`, the Japanese warning. The OFF packet does not stop the
intended slide effect with this sound program; it launches the warning again.
This alias is present in the ROM data itself. It does not require a wrong
region selector, a missing foot sensor, or corrupted frontend input.

The Twin sound program `epr-18826.30` distinguishes these packets:

| Argument | Twin Sequence | Action |
| --- | --- | --- |
| `4E` | `0x612c9e` | Note on `0x45`, Japanese warning |
| `5D` | `0x612d10` | Note on `0x4f`, slide effect |
| `5E` | `0x612d18` | Note off `0x4f`, slide effect |

This resolves the earlier sound-ROM/cabinet mismatch hypothesis for the
identified warning: the native Twin game code sends a legitimate slide effect
pair, while the Deluxe audio program maps that pair to Japanese speech.
Changing Country alone cannot repair that command-table collision.

## Targeted Runtime Proof

One additional 6,600-frame isolated RetroArch replay observes the actual sound
68000 sample-header selection, without injecting commands or changing its
execution. The normal Twin input schedule and original Deluxe sound ROMs are
retained. Four relevant events occur:

| Native Frame | Main Producer | Packet | Sound Selection |
| --- | --- | --- | --- |
| 5,740 | `SE_Slide1_ON`, return IP `0x3bda8` | `A0 11 5D` | Note `45`, header `02ac` |
| 5,771 | `SE_Slide1_OFF`, return IP `0x3be30` | `A0 11 5E` | Note `45`, header `02ac` |
| 5,772 | `SE_Slide1_ON`, return IP `0x3bda8` | `A0 11 5D` | Note `45`, header `02ac` |
| 5,773 | `SE_Slide1_OFF`, return IP `0x3be30` | `A0 11 5E` | Note `45`, header `02ac` |

The active instrument is `0x78`, and the driver resolves sample header `0x2ac`
through its copied instrument table at `0xa6f2`. The corresponding ROM header
contains source `0xcf65a6` and length `0xe26c`. Its first 512 PCM bytes also
match three previously retained Twin streaming-slot buffers. This buffer match
is corroboration; the sequence alias and actual driver selection provide the
causal mapping, independently of nearest-packet timing.

The user heard **one audible occurrence during this latest replay**. Four
internal starts must not be described as four complete audible warnings:
the final three requests are only one native frame apart. The controlled replay
establishes the wrong sample selection, not an exhaustive repetition rate or
four separate spoken phrases.

Process exit was 0; wall time was 113.3 seconds. Full EEPROM equality and both
native/container CRCs pass. PCM matches the preceding Twin observation for all
4,917,150 common frames, supporting observer transparency. No Voice-category
command is queued in the bank or centered race windows.

Private evidence root: `build-libretro-gpu/validation/manxtt-warning-j-20261010/`.
The build/run scripts, command receipt, native producer/driver log,
`static-sample-report.json`, `analyze.py` and `summary.json` retain the proof.
ROM binaries and extracted PCM remain ignored private data.

## Missing Deluxe Sounds And Correction Scope

The native Deluxe code directs additional effects to the Model 1 sound board;
for example Slide ON/OFF become `AE 11 20` / `AE 11 21`. The SCSP sound program
explicitly excludes this destination from ordinary sequence dispatch at
`0x6035a6–0x60361e`. Production `Model2` currently owns the SCSP sound board
without attaching or mixing the optional Manx TT Model 1 board.

The user's same-set Deluxe comparison is consistent with this routing: the
Slide commands no longer reach the SCSP sequence that aliases Voice J, while
their intended Model 1 audio destination is not connected. This supports two
specific integration gaps: cabinet-appropriate command mapping in Twin and
the additional sound board in Deluxe. Absence of the unwanted voice in Deluxe
does not demonstrate that its overall audio is complete.

The reference MAME configuration attaches that additional board for both
`manxtt` and `manxttdx`, with host serial TX fanned out to it. See the
[official MAME driver](https://github.com/mamedev/mame/blob/master/src/mame/sega/model2.cpp).
This explains a concrete missing Deluxe audio path. It does not yet establish
that every missing sound reported by the user belongs to that board.

The next correction must provide cabinet-appropriate audio: the Twin command
mapping in Twin mode and both native boards in Deluxe mode. Choosing and
loading those sound-ROM variants requires preserving ROM provenance and the
existing save/configuration lifecycle. No warning muting, command suppression,
voice rate limit, or production sound-ROM substitution has been applied.

## Main Program Selection Follow-Up

The [Revision C/D main-program comparison](MANX_TT_MAIN_PROGRAM_COMPARISON_2026-10-10.md)
checks the user's alternative hypothesis of missing cabinet/audio-table
selection. The main command tables and slide cabinet-selection code match;
all 109 paired direct sound-dispatch callers have equal local behavior modulo
address relocation. The reviewed audio driver prefix is identical across sound
ROMs, with fixed ROM-owned sequence roots. Both main programs transmit the same
slide pair in retained RetroArch traces. No additional detection/table-selection
mechanism was found in these paths. Undocumented hardware and exact Revision D
Twin factory pairings remain outside this static comparison's proof.

The [documentary review](MANX_TT_AUDIO_DOCUMENTARY_REVIEW_2026-10-10.md)
adds Sega Twin manual ROM-layout evidence and primary MAME history: Twin uses
EPR-18826 / MPR-18827, while the Revision D dump originated from a Deluxe
configuration with its additional Model 1 sound board. Exact factory D/Twin
pairing remains unproven. Native Cabinet Type selection alone does not establish
compatibility of the physical sound-ROM configuration with both cabinet modes.

## Evidence And Production State

Private ignored root: `build-libretro-gpu/validation/manxtt-sound-routing-20261010/`.
`build-probe.py`, `run.py`, per-case logs/receipts/WAV/PCM/SRAM, direct-scan
scripts, and `analyze.py` / `summary.json` preserve successes and rejected
stimuli. PCM dumps and ROM-derived data remain private and must not be committed.

Source files `model2.cpp` and `scsp.cpp` were restored exactly and the normal
target rebuilt. Normal build and both installed cores retain SHA-256
`44cf32065c3208eaa34b601a4a04423b1c5217e7b14fa54e0debc79b3fbd3d5b`.
No sound ROM substitution, synthetic motion controller or voice filter was
installed into the production core.
