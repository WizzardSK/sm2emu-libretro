# Power Sled Handlebar And Race Validation

Date: 2026-10-09
Backend: SM2-Emu Libretro In RetroArch Only

## Qualified Results

The installed production core runs the original Main, Relay and Slave archives
through mode selection, boarding, a Semi Auto race, checkpoints, Time Extension
and Game Over. Main and Slave show changing race clocks, POSITION 1 and course
progression. Later black frames and a SEGA screen are retained as observations;
normal post-race recovery is not qualified. This is a race-cycle observation,
not proof of a finish-line crossing, final ranking or Manual-mode handling.

A separate private diagnostic build reads the existing input and work RAM once
per machine frame. Sweeping each RetroPad trigger independently during native
race state 7 verifies these responses on both Main and Slave:

| RetroArch Control | Native ADC Channel | Native Handlebar Commands |
| --- | --- | --- |
| Port 1 R2 | 1 | -160, 0, +160 |
| Port 1 L2 | 3 | -160, 0, +160 |
| Port 2 R2 | 5 | -160, 0, +160 |
| Port 2 L2 | 7 | -160, 0, +160 |

Each handle produces 44 nonzero observed responses, including both signs.
Adapter values equal the values sampled by the native program. Only the driven
handle responds: other handles and the other rider remain at zero. The Relay
receives no scripted gameplay input and its four commands stay zero.

All three programs emit PCM. Production Main / Relay / Slave peaks are
6434 / 4048 / 5672; the final diagnostic peaks are 5770 / 3945 / 6224.
PCM presence does not establish original-cabinet sound fidelity.

## Symptom, Cause And Reusable Method

The initial fixed trigger values reached the correct ADC channels but produced
no native handlebar command. The native program recognizes narrow response
zones using the existing saved calibration. The fixture's chosen values were
outside those zones. This finding requires no adapter, gain or calibration fix.

Use full-range, independent handle sweeps and observe every machine frame.
A passive observer sampling every 30 frames can miss the response zones; its
intermediate sweep was deliberately stopped and is excluded from qualification.
Its three owned instances still exited cleanly, with no forced kill or residue.
No calibration menu, endpoint acquisition campaign or calibration edit is used.
Existing saved endpoint bytes remain unchanged in all three native copies.

The native input sampler is at Main 0x0000f058 and the command decoder at
0x00015c40. The decoder stores individual commands at 0x5293c8/ca/e0/e2 and
rider sums at 0x5293cc/e4. Static inspection of the Slave program's consumer
at 0x000ba86c shows both rider sums feeding its control update. This static
consumer inspection is separate from the measured ADC/decoder responses.

## Runner And Reproduction

The existing gameplay runner now has a current race path, without the historical
Test/Service pulses. Separate BSV movies supply each program's operator inputs
and each rider's analog triggers. The shared network runner accepts
`--input-replay-map`, a JSON map from local roles to replay paths; its existing
`--input-replay` remains the fallback. Staged movie hashes are recorded.

```sh
python3 scripts/test-power-sled-gameplay.py \
  --race-qualification --handlebar-sweep \
  --output build-libretro-gpu/validation/power-sled-race-new-run
```

Use a new output directory. `--prepare-only` writes fixtures and the command
without launching. Timings are local frontend frames, not synchronized native
link clocks; runner success always requires separate visual review. The default
baseline is the previously validated original-archive audio integration run.
ROMs, configuration, saves, screenshots, ports and processes use the established
isolated runner lifecycle. The older Entry/Test probe remains historical.

## Evidence And Limits

Evidence roots under `build-libretro-gpu/validation/`:

- `power-sled-race-20261009`: installed-core race, fixed-input diagnostic,
  original source snapshot, private observer sources/binaries and audio review.
- `power-sled-handlebar-sweep-20261009`: independent movies, exact commands,
  superseded sparse observer and final `dense-run`. `review.py` / `review.json`
  verify native responses/isolation, ADC delivery, SRAM identity/CRC/colors,
  unchanged calibration, emitted PCM, clean exits and source/deployment hashes.

The three completed sessions have nine clean native-linked program exits.
The superseded observer session is retained separately as an interrupted probe.
The normal source is restored byte for byte. The build and both installed cores
remain SHA-256
`6832b2952b4689bc2e366f7dcb3e97c97da314c4ff14d69c3c0d85db0a14ced4`.
No diagnostic core is installed. No new Core Option, binding, emulation change,
ROM modification, commit or push is needed.

Physical controller delivery and handling feel, Manual-mode finish/ranking,
post-race recovery and original Main sound fidelity remain unqualified.
All three sets retain preliminary status. Deferred Country/Relay/ID work is
unchanged; this task does not use MAME or acquire NVRAM setting samples.

## Subsequent Post-Race Qualification

The later installed-core repeat session qualifies a second Semi Auto race after
Game Over and the black/SEGA sequence, without resetting or restarting any
program. See `POWER_SLED_POST_RACE_RECOVERY_2026-10-09.md` for evidence and limits.
The earlier post-race limitation above describes the original observation only.

## Manual Follow-Up

Manual / Professional selection, finish and native final placement were
subsequently qualified on 2026-10-10 in the installed core. See
[Power Sled Manual Finish And Ranking](POWER_SLED_MANUAL_VALIDATION_2026-10-10.md).
The earlier exclusions above describe the scope of this 2026-10-09 run.
