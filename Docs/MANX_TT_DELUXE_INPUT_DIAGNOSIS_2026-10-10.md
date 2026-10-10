# Manx TT Deluxe Input And Native Sound Diagnosis

Date: 2026-10-10
Scope: Native Program Inspection And Two Isolated RetroArch Probes; No Production Change

## Findings

The supported throttle, brake and bank inputs reach the native game on their
expected channels. No foot-sensor input has been identified in the manufacturer
Input Test or MAME's Manx TT input definition. This does not prove that every
physical cabinet lacks additional sensors.

A distinct Deluxe fidelity gap is confirmed: the active motion controller's
parallel feedback is not emulated. The game reads `0xff` rather than the
acknowledgements its native check expects. A bounded Deluxe boot remains on
the Active Motion Slider (AMS) checking screen. Twin mode explicitly bypasses
that response check; therefore this missing response does not directly explain
the repeated sound in the measured Twin race.

Following the user's request, an isolated
[motion acknowledgement stub](MANX_TT_MOTION_STUB_2026-10-10.md) now supplies
`0xce` / `0xcd` through the parallel callbacks. It removes that initial gate
and reaches a Revision D Deluxe race in RetroArch. The normal core remains
unchanged; the result qualifies the diagnostic stub's effect, not a complete
motion controller or a speech correction.

The repeated commands observed during the bank window belong to the native
Sound Test's Effect category. No new Voice-category command is queued in that
window or the following neutral window. The particular utterance reported by
the user has not been transcribed or matched to a command/sample. Category
membership does not prove what a mismatched sound ROM actually plays.

## Reference Hardware

- [Sega Deluxe Input Test](https://backup.segakore.fr/sauservice/Manuals/Manx%20Folder/MDhtml/MD26.html)
  documents throttle, brake and bank values and calibration.
- [Sega Deluxe Output Test](https://backup.segakore.fr/sauservice/Manuals/Manx%20Folder/MDhtml/MD34.html)
  documents the drive-board connections, motor checks and board communication.
- [Official MAME Model 2 Source](https://github.com/mamedev/mame/blob/master/src/mame/sega/model2.cpp)
  declares the three analog controls, unused second-player digital inputs and
  an extra Model 1 sound board for Deluxe. Its Model 2A wiring does not supply
  a Manx AMS controller implementation.

The missing Deluxe sound board, documented in
[the voice investigation](MANX_TT_VOICE_DIAGNOSIS_2026-10-09.md), is separate
from the motion-feedback gap. Wiring the sound board alone did not correct
the retained Twin comparison.

## Native Motion Feedback Path

Addresses below refer to the authentic parent Revision D main program.

| Native Location | Observed Function |
| --- | --- |
| `0x71420–0x714b0` | Loads settings; cabinet byte becomes `0x51405a`, matching EEPROM `0x0a`. |
| `0x2420` | Reads parallel port D at `0x01c00006` into feedback byte `0x514035`. |
| `0x2430–0x2438` | Writes output byte `0x514034` to parallel port E at `0x01c00008`. |
| `0x5f530` | Cabinet value 1 (Twin) clears the check state and marks it ready. Other values enter the motion response check. |
| Deluxe check branches | Examine `0x514035`, including expected `0xce` / `0xcd` responses and a `0xb0` high-nibble state. |

The identified motion exchange uses parallel D/E, not the two RS-422 channels.
Twin still writes parallel output commands; only the response check is bypassed.
SM2's port D callback returns the second player input port, idle `0xff` here.
The Manx metadata does not instantiate a motion device for port E. Merely
enabling the generic drive-board flag would not implement this acknowledgement
protocol: its existing handler records force-feedback commands.

## Bounded RetroArch Evidence

Both cases use the established `scripts/smoke-retroarch.py` runner, software
rendering and default 60 Hz timing. A private observer records native I/O reads,
parallel/serial writes and the sound-table producer. It is removed afterwards.

| Check | Revision D, Twin | Revision D, Deluxe Boot |
| --- | --- | --- |
| Requested frames | 6,600 | 2,300 |
| Last observed native I/O frame | 6,709 | 2,379 |
| Wall time | 113.1 seconds | 40.9 seconds |
| Process exit | 0 | 0 |
| Cabinet byte | 1 | 0 |
| Parallel D response | `0xff`, 13,199 reads | `0xff`, 4,570 reads |
| Parallel E output | Varies with native game state | `0x3d`, 2,286 writes |
| RS-422 reads / writes | 0 / 0 | 0 / 0 |
| SRAM container and native CRC | Pass | Pass |
| Complete EEPROM vs isolated seed | Unchanged | Unchanged |
| Result | Race replay and native sound tracing | AMS checking screen at the end of the window |

The Deluxe seed differs from the established isolated Twin seed only in the
cabinet byte and its repaired checksums. Calibration remains unchanged. This
is a bounded boot observation, not proof of an infinite hang or a qualified
Deluxe race. Final frames extend beyond requested advancement while the
runner captures its final image and closes the process.

Twin analog read examples, in auto-incrementing channel order:

| Frame | Throttle (0) | Brake (1) | Bank (2) | Unassigned Channels (3–7) |
| --- | --- | --- | --- | --- |
| 5,401 | `0xff` | `0x00` | `0x1e` | All `0xff` |
| 5,469 | `0xff` | `0x00` | `0xe1` | All `0xff` |
| 6,001 | `0xff` | `0x00` | `0x80` | All `0xff` |

The replay alternates bank in the first window while brake remains released,
then centers bank. These reads verify the channel routing and distinct lean
values. They do not qualify a physical controller or every calibration range.
The Twin recording's 4,931,850 PCM frames match the prior normal baseline
byte-for-byte over the full common prefix, supporting observer transparency.

## Native Sound Producer And Cabinet Routing

Routine `0x6e610` resolves a logical sound index through three-byte entries at
`0x6c1f0`. Instruction `0x6e62c` writes the first byte to `0x513fc4` before
the packet is enqueued. Recording this producer and its native return IP
identifies the caller, unlike the delayed UART drain.

The game's own Sound Test classifies Twin logical indices 5–32 as Voice and
33–125 as Effect. Deluxe splits effects into Effect_E (33–82) and Effect_P
(126–190), retaining Voice 5–32. Three frequent events change their sound
destination directly in the main program when the cabinet flag changes:

| Native Branch | Twin Index / Packet | Deluxe Index / Packet |
| --- | --- | --- |
| `0x3d2e4` | 45 / `A0 11 0C` | 134 / `AE 11 08` |
| `0x3c64c` | 63 / `A0 11 30` | 146 / `AE 11 14` |
| `0x3c5d8` | 64 / `A0 11 31` | 147 / `AE 11 15` |

The measured Twin event counts are:

| Window | Index 45 | Index 63 | Index 64 | New Voice Events |
| --- | --- | --- | --- | --- |
| Bank, 5,400–5,999 | 69 | 22 | 22 | 0 |
| Centered bank, 6,000–6,599 | 321 | 105 | 106 | 0 |

Thus repetition is not confined to the current bank being extreme. Full
throttle and internal motorcycle state continue into the neutral window.
These caller blocks inspect motorcycle state fields and cabinet/mode flags;
no direct foot input or AMS feedback read was identified in them. The precise
semantic names of those internal fields and the expected event rate remain
unqualified. No audio identity can be inferred from these counts alone.

## Later Cause Identification

The [subsequent sound-routing investigation](MANX_TT_SOUND_ROUTING_2026-10-10.md)
resolves the warning identity and specific command collision. The user reports
the Japanese feet-on-step warning in Twin, including Export / Country USA.
The Deluxe sound ROM aliases Twin Slide ON/OFF packets to Voice J; an isolated
RetroArch sound-driver observation verifies the warning sample selection.
This supersedes the unresolved cause status below. The production correction
remains pending; the latest replay contains one user-reported audible occurrence,
not four distinct phrases despite four internal starts.

## Cause Status At The Initial Input Probe

The Twin/Deluxe sound-ROM configuration remains the leading explanation for
the difference between variants. Next causal work must associate the actual
utterance with its sound sequence, active instrument and sample, then establish
why that interpretation differs. No repeated full replay, synthetic foot input
or voice filter is justified by the present evidence.

Deluxe motion support needs an actual controller protocol implementation and
separate qualification. The current MAME reference also lacks that controller;
its input definitions cannot supply the missing acknowledgements.

Private evidence: `build-libretro-gpu/validation/manxtt-deluxe-inputs-20261009/`.
`build-probe.py`, `run.py`, `run-deluxe.py`, command receipts, per-case logs,
WAV/PNG/SRAM, `native-sound-test-categories.json`, `source-review.json` and
`analyze.py` / `summary.json` preserve the observations. ROM-derived material
stays ignored and must not be committed.

Original source was restored and the normal target rebuilt to remove diagnostic
objects. The normal build and both installed cores retain SHA-256
`44cf32065c3208eaa34b601a4a04423b1c5217e7b14fa54e0debc79b3fbd3d5b`.
No production fix, option, binding, calibration change or workaround was applied.
Final process audit finds no remaining RetroArch instance from either probe.
