# Manx TT Repeated Voice Diagnosis

Date: 2026-10-09
Scope: Published References And Isolated RetroArch Command/Sound Comparisons; No Production Core Modification

## Symptom And Conclusion

The user reports a female voice repeating during racing, apparently on stronger
leans, with a variant/mode behaving differently. A closely matching symptom is
documented in Model 2 Emulator's own release notes: version 0.9 replaced Manx TT
Deluxe sound ROMs with Twin sound ROMs and required Twin cabinet mode to correct
Japanese speech during braking. This establishes a historical speech problem
associated with cabinet/sound-ROM configuration. It does not prove that the
current report has the same cause, identify the faulty emulated instruction or
device, or establish the expected frequency in every program.

The current parent Revision D has the same significant mismatch: the retained
normal-core race uses Twin NVRAM while its sound program/sample region is Deluxe.
Revision C uses Twin sound ROMs and Twin NVRAM. This is the leading explanation
for the user's difference between variants. It remains a source-supported
diagnosis, not a newly qualified fix or an auditory identification of the user's
particular utterance.

## Published Evidence

- [ElSemi's official homepage, archived 2012-07-16](https://archive.ph/WuIR):
  Model 2 Emulator 0.9 release notes explicitly associate the Japanese speech
  defect with Deluxe sound ROMs, a two-board setup, and the change to Twin sound
  ROMs plus Twin cabinet mode. The live original homepage was unavailable when
  checked; the archived page is the author's primary report.
- [Official MAME source](https://github.com/mamedev/mame/blob/master/src/mame/sega/model2.cpp):
  labels the parent's `epr-18924a.30` / `mpr-18763.31` as DX sound program/samples
  and Revision C's `epr-18826.30` / `mpr-18827.31` as Twin. The Deluxe machine
  adds a separate Model 1 sound board and fans UART transmission to it.
- [Firsthand real-PCB report, 2019-03-15](https://www.ukvac.com/forum/threads/manx-tt-model-2-sound-error.56980/):
  a Manx TT PCB in a Sega Rally cabinet repeats a Japanese request to keep feet
  on the pedals once steering passes a threshold in either direction. A full
  cabinet owner reports no foot sensors and no such repeated announcement.
  The thread has no verified resolution and does not document the sound ROMs
  or cabinet setting; it corroborates the symptom, not its cause.
- [Sega Twin owner's manual](https://manualzz.com/doc/46753791/sega-manx-tt-twin-type-superbike-owner-s-manual):
  specifies Twin for Cabinet Type, distinguishes voice and player braking sound
  in Sound Test, and documents bank/throttle/brake calibration. It does not
  establish the expected frequency of this particular voice.

The feet/pedals identification comes from the firsthand report. It is plausible
for the user's voice, but no local speech transcription has confirmed it. The
historic developer report describes braking; the user and PCB report describe
steering. Do not silently equate those predicates or invent an overlean warning.

## Verified Local Configuration

| Set | Sound Program | First SCSP Sample ROM | Retained Race Configuration |
| --- | --- | --- | --- |
| `manxtt` Revision D | `epr-18924a.30`, CRC `ad6f40ec` (DX) | `mpr-18763.31`, CRC `1bcb2283` (DX) | Twin, EEPROM `0x0a = 1` |
| `manxttc` Revision C | `epr-18826.30`, CRC `ed9fe4c1` (Twin) | `mpr-18827.31`, CRC `58d78ca1` (Twin) | Twin, EEPROM `0x0a = 1` |
| `manxttdx` Original DX | `epr-18746.30`, CRC `d7e21774` (DX only) | `mpr-18763.31`, CRC `1bcb2283` (DX) | Dedicated DX program; no Twin cabinet selector |

`data/games.xml` preserves MAME's authentic set definitions. Changing Cabinet
Type in NVRAM does not switch loaded sound ROMs: `Model2::init()` attaches the
catalogue's `audiocpu` and `samples` directly to `Model2Sound` and routes UART
transmission to that board. The optional `m1audio:*` regions are declared but
the separate DX Model 1 sound board is not instantiated by this machine.
Missing that board is a separate confirmed fidelity gap; it has not been shown
to be the sole cause of the repeating voice, particularly in Twin mode.

Enhanced Audio Balance uses the same flat gain (799) for all three sets. It
scales output and has no Manx-specific voice triggering logic. The adapter has
no rate limiter or repeated-announcement generator for this game.

## Reproducible Read-Only Audit

```sh
python3 build-libretro-gpu/validation/manxtt-voice-diagnosis-20261009/review.py
```

The audit checks current sound metadata, the CRCs of every referenced SCSP sound
program/sample file against the user's existing local archives, retained SRAM
container/native EEPROM CRCs, and the parent/C cabinet byte. Results are in
`build-libretro-gpu/validation/manxtt-voice-diagnosis-20261009/review.json`.
No ROM data is written or committed. Existing normal-core gameplay recordings
remain available through `MANX_TT_GAMEPLAY_VALIDATION_2026-10-09.md`; their PCM
presence is not proof of speech identity, frequency or fidelity.

The initial audit was read-only. The subsequent comparison below runs only
private diagnostic cores in RetroArch, with isolated SRAM and system assets.
Production source, the normal build and both installed cores are restored and
unchanged. No fix is claimed verified.

## Investigation Policy

The user clarified on 2026-10-09 that the objective is to identify and correct
an actual cause, or document the defect and its limits. A workaround is a last
resort after alternatives have been evaluated. Replacing Deluxe ROMs with Twin
ROMs is a diagnostic comparison here; it is not an automatically approved
production fix. Do not mute, debounce, rate-limit or filter a native sound
command to conceal the symptom.

## Isolated Runtime Comparisons

All cases use the established `scripts/smoke-retroarch.py` runner in real local
RetroArch, software rendering and the default 60 Hz option. Each advances
8,700 frames with the same recorded inputs, then exits cleanly. The diagnostic
recipe contains a first bank-only phase (frames 5,400–5,999), a neutral phase,
then brake-only and combined phases. Strong bank alternates between +/-25,000
every 60 frames; brake is zero in the first bank-only phase. Later phases are
input windows, not proof that the game stays in the same racing state:
Time Up/attract transitions limit any frequency comparison.

The previous validated native SRAM seeds were copied privately and only Link
Type was set to Not Link, with checksums updated. Calibration was preserved.
Final SRAM container/native CRCs pass and the complete EEPROM remains identical
to the corresponding isolated seed in every case.

The private observer records host UART bytes, immediate UART writes and SCSP
slot starts. The Deluxe-board probe also attaches the existing M1Audio module
with the authentic local program/sample ROMs, fans host UART TX to it and clocks
it alongside SCSP. Its own PCM is discarded. This tests one possible serial
feedback mechanism; it does not implement or qualify complete Deluxe audio,
mixing, persistence or motion hardware.

| Case | Program / Sound | UART Bytes | SCSP Slot Starts | Result |
| --- | --- | ---: | ---: | --- |
| Original D In Twin Mode | D / Deluxe | 11,665 | 5,026 | Baseline |
| Original C In Twin Mode | C / Twin | 14,668 | 4,811 | Different main revision; reference only |
| D With Extra-Board Probe | D / Deluxe + M1 serial/clock probe | 11,665 | 5,026 | Identical host TX, SCSP slot events, PCM and final image to D baseline; no M1 RX bytes observed |
| D With Twin Sound ROMs | D / Twin | 11,665 | 5,059 | Identical host TX, audio frame count and final image; SCSP events and PCM change |

Each case records 6,395,235 stereo frames at 44,100 Hz. Total runtime is about
593 seconds (four bounded sessions). Final D captures show attract, while C
shows Course Select. They do not establish matched race progression across
revisions or prove that every later input phase ran during a race.

The last comparison changes only the parent D `audiocpu` and `samples` region
definitions in a private system XML, using the verified Twin files from the
existing `manxttc.zip` archive. All other ROM regions, the D main program,
inputs and isolated EEPROM remain unchanged. There is no production catalogue,
archive or loading-policy edit. Equal UART bytes include their frame/cycle
timestamps; equal PCM in the extra-board case is a complete PCM hash match.

## Command Path And ROM Interpretation

During the first bank-only input phase, the D game sends `A0 11 30` and
`A0 11 31` 22 times each with brake zero. The same phase in C sends each
27 times. D also repeatedly sends the pair during the following neutral-input
window. These are observations about native commands, not a measured count of
the reported voice or evidence that its repetition is intended.

Immediate UART writes locate the D serial queue drain at `0x0006e1d0`
(observer next IP `0x0006e1d8`; C next IP `0x0006e198`). It reads the native
ring at `0x005bb670` and writes the UART data register at `0x01c80000`.
The delayed TX callback's current CPU IP is not the command's origin; neither
trace identifies the higher-level game routine that enqueued it.

Static decoding of the authentic SCSP sound programs follows the `A0`
dispatcher and ROM command tables:

| Native Command | D Sequence Address / Bytes | C Sequence Address / Bytes |
| --- | --- | --- |
| `A0 11 30` | `0x611330`: `80 9e 2c 7f 00 ff 2f 00` | `0x612bb4`: `80 9e 2c 78 00 ff 2f 00` |
| `A0 11 31` | `0x611338`: `80 8e 2c 00 ff 2f 00` | `0x612bbc`: `80 8e 2c 00 ff 2f 00` |

These sequences encode MIDI note on/off on channel `0xE`, note `0x2C`, with
different note-on velocity (127 versus 120). The programs also have different
initial channel presets. This demonstrates different ROM-level interpretation
data for a shared command path. It does **not** establish that note `0x2C` is
the female warning, a brake sound or a skid sound. SCSP RAM addresses may be
reused after uploads; slot address/count alone does not identify speech.

## Conclusion And Current Cause Status

The initial diagnosis above did not identify the utterance. That evidence gap
was resolved on 2026-10-10: the user identifies the Japanese feet-on-step
warning in `manxtt` Twin, including Export and Country USA. The
[completed sound-routing investigation](MANX_TT_SOUND_ROUTING_2026-10-10.md)
now demonstrates the specific cause: the Deluxe audio ROM maps native Twin
Slide ON and OFF commands to the same sequence as Voice J. One targeted
RetroArch driver observation verifies that both effects select its sample
header `0x2ac`. The user hears one occurrence in that latest replay; four
internal starts are not four distinct spoken phrases.

This is a proven wrong sample selection for the identified warning, with no
production correction yet. The next correction needs cabinet-appropriate
audio configuration, preserving ROM provenance and persistence lifecycle.
It must also address the separately missing Deluxe Model 1 audio-board path.
The earlier serial/clock-only probe was run in Twin and discarded that board's
PCM; it does not qualify its Deluxe output or rule out the missing audio path.

The separate [motion acknowledgement stub](MANX_TT_MOTION_STUB_2026-10-10.md)
qualifies isolated Revision D Deluxe boot/race and remains a private diagnostic.
No complete motion-device emulation, warning filter, or sound-ROM substitution
has been installed. Original DX program/board fidelity remains separate.

## Evidence And Cleanup

Private, ignored evidence root:
`build-libretro-gpu/validation/manxtt-voice-origin-20261009/`.
`recipe.json`, command receipts, `same-program-rom-selection.json`, per-case
`result.json`/`run.log`/WAV/PNG/SRAM and `summary.json` retain the comparisons.
`summarize.py` checks exact TX/slot comparisons, SRAM/native integrity, unchanged
EEPROM, unchanged other D ROM regions, removal of diagnostic source markers and
all three normal-core hashes. ROM-derived disassembly/data remain private and
must not be committed.

After restoring source, the normal target was rebuilt to remove diagnostic
objects. Its SHA-256 and both installed RetroArch core hashes remain
`44cf32065c3208eaa34b601a4a04423b1c5217e7b14fa54e0debc79b3fbd3d5b`.
No production fix, workaround, option, binding, calibration change or save
migration has been applied.
