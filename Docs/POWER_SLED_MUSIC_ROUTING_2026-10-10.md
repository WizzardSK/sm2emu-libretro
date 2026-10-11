# Power Sled Music Routing — 2026-10-10

## Finding

This diagnosis describes the default behavior with Relay Audio Disabled. The
subsequent optional Master music experiment is implemented and qualified in
[Power Sled Master Music Experiment](POWER_SLED_MASTER_MUSIC_EXPERIMENT_2026-10-10.md).

The current emulation keeps rider audio on Main/Slave and the separate Relay
sound program on Relay. Omitting Relay still permits a two-rider race, but also
omits its audio. No automatic transfer of Relay audio to Main is implemented.

The user's remembered race recording contains an audio stream that matches
the present Relay output, rather than either rider's output. This identifies
the source of the missing soundtrack in the two-instance configuration. It
does not establish original undumped Main audio hardware or factory fidelity.

## Code And Sound Program Evidence

- Main and Slave use EPR-19466 plus FPR-19459. Relay uses EPR-19467 plus
  FPR-19460/FPR-19461. These production definitions were not changed here.
- Native Relay code at `0x28de0` tests the program role against `0x0100` before
  installing its musical continuation. Its child task `0xc7b80` manages the
  Relay camera; that child is not the audio generator. Related music tasks use
  the same role gate, and the race constructor allocates its music task only
  on the Relay branch.
- Native sound command indices `0x64` through `0x69` encode `A0 11 00` through
  `A0 11 05`. The Relay sound program's table at `0x608508` maps these to its
  own `DF` sequences. The rider sound program's table at `0x6085d4` maps the
  same group to different `DE` sequences; copying those commands alone would
  not reproduce Relay sound from the rider ROMs.
- `SoundBoard::set_music_volume_percent` only scales separate MPEG music
  hardware where implemented. Power Sled has no separate MPEG path. Its
  registered Music Volume value therefore does not individually control its
  soundtrack. Checked source Gains are Auto, frontend mute is off, and the
  frontend volume is 0 dB.

This follows the existing Main sound-ROM reconciliation rather than reversing
it: replacing Main's rider sound pair with Relay's pair previously silenced
Main's unsupported rider commands. That is not a suitable music-only fix.

## Matched RetroArch Runs

Both runs use the installed normal core
`1e72cd27afd311a767e460477f252868303f286b2915a5d225dff085c54e0a87`, the existing
validated input replays, Main Silver / Slave Red, isolated config/SRM/ports,
and RetroArch's per-instance WAV recording driver. Screenshots qualify racing.

| Topology | Main PCM Peak | Slave PCM Peak | Relay PCM Peak |
| --- | ---: | ---: | ---: |
| Main / Slave | 4402 | 4370 | Absent |
| Main / Slave / Relay | 5318 | 6010 | 3346 |

Nonzero PCM alone is not evidence of music. An additional waveform comparison
uses seconds 67–75 of the retained Relay recording from the previous Main audio
integration, with mean removal and normalized sliding cross-correlation after
8:1 sample decimation. Its match in the current Relay recording starts at
62.438 seconds and has correlation **0.978823**. Maximum absolute correlations
against Main/Slave in either current run are **0.0328–0.0392**. The spectrum
comparison separately shows the Relay's changing tonal pattern and the rider
noise/effect output. The recordings are not asserted to be bit-identical;
different startup lengths and emulation schedules affect alignment.

All five qualifying instances report roster/native readiness, exit cleanly,
retain valid SRAM identity/container CRC and three concordant Ride values,
and leave no owned process. There are no shutdowns or unhandled instructions.
The first pair attempt failed at macOS window positioning before the second
instance launched; its files are retained and excluded from qualification.

## Canonical Launch With Relay Audio

```sh
python3 /Users/andrea/dev/sm2-emu-libretro/scripts/launch-linked-cabinets.py \
  --game powsledm:1,powsled:2,powsledr:relay --controllers 0,1,2
```

Relay is optional for the linked race. With the default Relay Audio Disabled,
its soundtrack requires that instance. The subsequent optional integration
runs the Relay sound program, samples and native event scheduling inside Master;
this is not a gain, ANS or Linked Cabinets setting adjustment. No production
change was made by this original diagnosis.

## Retained Evidence

`build-libretro-gpu/validation/power-sled-music-20261010/` contains:

- `pair-qualified-command.json` and `triplet-command.json` plus options/replays.
- Per-instance original/normalized WAV, runtime reports, screenshots and SRAM.
- `audio-review.json`, `historical-relay-comparison.json` and
  `rider-audio-comparison.json`.
- `native-sound-routines.txt`, historical/current spectrum comparisons.
- Fifteen-second `Relay-Race-Audio.wav` and `Main-Race-Audio.wav` excerpts.

The installed core/database, controls, calibration and ROM archives are
unchanged. Listening on the user's speakers and subjective original-cabinet
sound fidelity are outside this technical qualification.
