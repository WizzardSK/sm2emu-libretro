# Manx TT Gameplay Validation

Date: 2026-10-09
Scope: Bounded Native RetroArch Gameplay And Relay Qualification

The subsequent repeated-voice investigation is recorded separately in
`MANX_TT_VOICE_DIAGNOSIS_2026-10-09.md`. Gameplay/link qualification does not
qualify audio fidelity: parent Twin mode currently uses DX sound ROMs, matching
a historically documented speech defect. No audio correction is claimed here.

## Linked Gameplay Result

The parent and Revision C now advance from native link initialization through
selection, a two-rider race, Time Up/ranks and subsequent attract/race progression.
The counted Relay displays the native LIVE camera and follows the racers. It
does not become a third player. The retained normal-core sessions qualify:

| Case | Native Result | Visible Result |
| --- | --- | --- |
| `manxtt`, Master / Slave / Relay | IDs 1/3, 3/3, 2/3 | Course/transmission selection, two moving racers, exchanged positions, LIVE camera, Time Up and return to title. |
| `manxttc`, Master / Slave | IDs 1/2, 2/2 | Two moving racers, Time Up and subsequent race start. Timing overlay shows 60 FPS. |
| `manxttc`, Master / Slave / Relay | IDs 1/3, 3/3, 2/3 | Two moving racers, LIVE camera, Time Up, distinct 1st/2nd ranks and a second race. Timing overlays show approximately 60 FPS. |

All eight instances in these final linked sessions exit 0 without forced
termination or residual owned processes. The existing suite verifies persisted
ANS fields, SRAM identity/container CRC, distinct positive native IDs/count and
no communication-board restart after establishment. Captures and frontend PCM
are retained separately from those machine/persistence checks.

## DX Single-Program Result

`manxttdx` has a dedicated native Service Menu without Link Type and no ANS.
It is qualified as a single game, not forced into the parent link scheme.
An initial movie kept throttle fully pressed through the Active Motion Slider
operation tutorial and retained that screen at countdown zero. The corrected
normal input recipe sweeps bank in both directions, releases throttle with full
brake, supplies Start pulses, then accelerates. No Core Option, native settings
or input mapping change was needed.

The installed normal core completes the tutorial and reaches the native race:
position 8/8 against CPU riders, race HUD, elapsed clock, speed and 3D course.
The 11,000-frame default-60-Hz session exits 0, produces frontend PCM with peak
19173 and preserves valid SRAM/native EEPROM CRCs and bytes outside the settings
area. This qualifies tutorial-to-race entry, not a skilled full-lap finish or
physical motion hardware. No individual input is claimed as an isolated cause;
the retained complete normal-input sequence is the reproducible solution.

## Race-Selection Defect And Correction

The first three-node gameplay session reproduced a real defect after successful
boot: Master/Slave stayed in course/transmission selection with countdown zero,
while Relay remained in attract. The initial counted-Relay implementation had
assigned its own ID but merely forwarded the incoming payload unchanged.

The native frame carries a train of status/data slots. A counted node must
include its local slot before the received slots. `M2Comm::tick()` and
`read_fg()` now use the existing shared-RAM send path for the Manx TT counted
role-3 Relay. Other nodes' data remain in the subsequent slots; the generic
uncounted role-0 Relay continues to forward the incoming packet unchanged.
There is no new player, Core Option, binding, NVRAM field or Save State layout.

The ring regression check now verifies both the Relay's distinct local status
and the preserved Slave/Master slot train. Its former assertion that counted
Relay should omit its local slot was incomplete and is superseded. All existing
generic cabinet and Power Sled ring checks pass. Core, headless and standalone
builds pass. The established 600-frame offline image, complete WAV, native files,
CPU state, master cycles and audio-frame count match the preceding normal build
exactly. Full original communication-firmware equivalence is not claimed.

A first Revision C pair did enter a race but showed an irregularly progressing
timer in the retained window. A bounded repeat with the existing timing overlay
completes Time Up and enters a subsequent race at 60 frontend FPS. The anomaly
did not recur in that repeat or the final Revision C triplet. Its precise cause
was not established; it is retained as historical evidence, not silently
discarded or claimed fixed by the Relay-only payload change.

## Installed Core

The tested normal binary is installed in both local RetroArch destinations,
with the previous files backed up before replacement:

- `~/Library/Application Support/RetroArch/cores/sm2_libretro.dylib`
- `~/Library/Application Support/RetroArch/cores/sm2_dev_libretro.dylib`

Build and both copies have SHA-256
`44cf32065c3208eaa34b601a4a04423b1c5217e7b14fa54e0debc79b3fbd3d5b`.
No temporary observer is in this binary. No commit/push or dependency installation
was performed.

## Reusable Campaign And Evidence

`scripts/test-manxtt-gameplay.py` composes the existing linked-cabinet runner
and single-game smoke runner. It generates padded RetroArch 1.22 BSV records,
isolates files/ports/processes and stores exact commands/replay hashes. The
script's successful exit means captures were collected; gameplay requires
visual review and native/persistence gates before qualification.

```sh
python3 scripts/test-manxtt-gameplay.py \
  --output build-libretro-gpu/validation/manxtt-gameplay-new-run
```

Use the established Python runtime with Pillow and a fresh output directory.
The default matrix is parent triplet, Revision C pair and the DX single program.
`--case` selects one case; `--prepare-only` writes commands/replays without
launching. DX has a dedicated catalogue without Link Type/ANS and is not forced
into a parent linked configuration. Its replay includes a normal bank sweep,
throttle release/full brake and Start pulses for the operation tutorial.
No Test/Service, calibration acquisition, native RAM forcing or MAME runtime
is used.

Linked evidence is under
`build-libretro-gpu/validation/manxtt-gameplay-20261009/`:

- `plan.json`, per-case commands/replays/logs and all original screenshots/PCM.
- `relay-payload-candidate-command.json`, corrected parent triplet.
- `revision-c-final-commands.json`, final Revision C pair/triplet.
- `initial-review.json`, `final-network-review.json`, `review.py` / `review.json`, contact sheets and offline
  command/build logs.
- `relay-payload-before/`, preceding source/binary snapshots.
- `deployment/deployment.json`, backups and installed hashes.

The initial parent selection failure and initial Revision C timing anomaly
remain distinguishable from the final qualified sessions. All ROM analysis,
runtime saves/PCM and backups remain in ignored local evidence, never in Git.
The first DX capture is retained in
`build-libretro-gpu/validation/manxtt-gameplay-dx-20261009/`; the installed-core
tutorial/race qualification is in
`build-libretro-gpu/validation/manxtt-gameplay-dx-tutorial-20261009/`, with exact
plan/command/replay hash, original/finalized PCM, screenshot, saves and result.

## Limits

This closes the bounded local linked-gameplay/Relay and DX-entry campaign. It does not
certify every course, skilled full-lap completion, real cabinet firmware,
motion hardware, controller feel, sound fidelity, all platforms or extended
stress. Physical controller/rumble/listening qualification remains in the
existing general roadmap; it does not block this local network correction.
The upstream preliminary metadata is preserved.
