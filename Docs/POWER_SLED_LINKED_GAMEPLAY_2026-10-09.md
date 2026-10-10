# Power Sled Linked Gameplay Probe

## Result

The installed macOS core was exercised through three isolated RetroArch
instances: Main (`powsledm`), Relay (`powsledr`) and Slave (`powsled`). The
Main Red / Slave Silver configuration reaches mode selection and animated
boarding/track introduction scenes. A controllable race, race progression
and complete rider controls are **not verified**. Preliminary validation
remains open.

No SYSTEM SHUTDOWN screen was observed in the retained linked captures. This
is limited to the tested three-program configurations and observation window.
The earlier standalone shutdown captures remain valid historical evidence.

## Method And Reproduction

`scripts/test-power-sled-gameplay.py` reuses the existing
`scripts/test-retroarch-netpacket.py` lifecycle, isolated saves and screenshot
commands. Its input movie uses the established `smoke-retroarch.py` RetroArch
1.22 format. The same existing reader parses recorded frontend WAV/PCM.
Only SM2-Emu Libretro in RetroArch acquires runtime evidence.

The starting SRAM files come from the accepted NVRAM-options campaign's
`initial` stage. Manual NVRAM Settings are enabled for the explicit Ride
choices; checkpoint and angle values retain native defaults. User saves
are not used as destinations. No calibration menu or calibration field is
changed. Seven screenshots and PCM are retained per program per run.

```sh
python3 scripts/test-power-sled-gameplay.py \
  --output build-libretro-gpu/validation/power-sled-gameplay-new-run \
  --main-ride red --slave-ride silver --both-riders
```

The output directory must be new. The script defaults to the installed local
core and records its hash, actual command, input pulses, movie hash, capture
hashes and lifecycle results. Runner success is never promoted automatically
to gameplay success: the summary explicitly requires visual review.

The input sequence enters/leaves Test, supplies ordinary entry/call/start
attempts and alternates the mapped P1 handlebars near the native endpoint
range. `--both-riders` adds repeated P1/P2 Entry and Call buttons during the
later observation period. It does not implement P2 analog channels.

## Observations

| Main / Slave Ride | Additional Inputs | Observed Result |
| --- | --- | --- |
| Red / Black | P1 Entry/Call, P1 Handlebars | Startup Ride error; Main/Relay OK, SILVER RIDE 0, Main THIS IS ????????. Slave reports Black. |
| Silver / Red | Same | Startup Ride error remains; SILVER RIDE 0. Slave reports Red. Main's operator color alone does not establish a Silver ride in this topology. |
| Red / Silver | Same | Reaches Semi Auto / Manual selection and boarding animation. No confirmed race. |
| Red / Silver | Repeated P1/P2 Entry/Call | Mode selection, boarding and track introduction advance; later captures return to Manual selection/introduction. No retained racing HUD/progression or independent steering response proof. |

All twelve program instances establish the expected native communication
IDs (Main 1/3, Relay program 3/3, Slave 2/3), exit with code 0 and require
no forced cleanup. No runner-owned RetroArch process remains. Every final
SRAM container passes identity/CRC checks; all three Ride field copies
match the selected values.

### Audio Recording Correction

The first two runs inherited disabled audio from the communication runner.
Appending enabled audio settings created duplicate keys and did not replace
the earlier settings. Their silent recordings are excluded from audio
conclusions. The optional `--record-audio` path now replaces those settings
and selects CoreAudio on macOS; the ordinary communication-test defaults
remain unchanged.

The last two runs have successful CoreAudio initialization on all programs
and no `failed_to_start_audio_driver` marker. Recorded PCM peaks:

| Program | Red / Silver | Repeated P1/P2 Entry/Call |
| --- | --- | --- |
| Main | 0 | 0 |
| Relay | 1030 | 1073 |
| Slave | 2996 | 3073 |

These are signed 16-bit PCM magnitudes. Relay/Slave emit nonzero audio on
this path; Main remains silent. Sound accuracy and listening validation
are not established. The last run's initial summary used an overly narrow
audio-start log matcher for Main; the reviewed manifest verifies its actual
`[Audio] Started synchronous audio driver` records. The matcher is corrected
for subsequent runs without altering the retained initial evidence.

## Evidence And Core Identity

Evidence directories under `build-libretro-gpu/validation/`:

- `power-sled-gameplay-20261009`
- `power-sled-gameplay-silver-red-20261009`
- `power-sled-gameplay-red-silver-20261009`
- `power-sled-gameplay-both-riders-20261009`

The last directory's `review.json` pins all four summaries and records
validated Ride copies, audio initialization, PCM peaks and the explicit
`gameplay_verified: false` conclusion. Each run retains its plan, input
movie, recipe, options, logs, screenshots, recordings and final saves.
Screenshot hashes were rechecked during review.

All runs use core SHA256
`f1e93586bf051c85b648b96dc2b956f3f3afca00a97b6ff4547081a2b1fe7928`,
the already deployed NVRAM integration build. This probe changes scripts
and documentation; it requires no new core build or deployment.

## Remaining Investigation

Diagnose the transition from boarding/introduction to a playable race with
a targeted input/reference comparison. The follow-up below completes the
second rider's adapter inputs without establishing playable racing.
The Main program remains the existing patched Relay approximation:
the local MAME source documents Main mode/node ID 0x200 in
`init_powsledm` and marks all three variants MACHINE_NOT_WORKING. Neither
limitation has been established as the cause of the remaining race issue.

These observations do not establish general conditional ID rules, larger
topologies, remote interoperability or motion-platform emulation. The
separately deferred Country/Relay/ID work remains deferred. No emulation
code, upstream checkout, TGPulse project, commit or remote was changed by
the original probe described above.

## Launcher And Input Follow-Up — 2026-10-09

The adapter now exposes local P2 Entry/Call and independent right/left
handlebar channels 5/7, matching the MAME input wiring. P1 aliases and Service
bindings are retained. Port 2 Disabled releases its handles to the native
rest values. This addresses an input coverage gap; it is not evidence that
the gap caused the boarding-to-race issue.

Two Entry-only replay attempts (`power-sled-entry-only-20261009` and
`power-sled-entry-fresh-20261009`) entered Test Menu unexpectedly, including
with fresh launcher SRAM. Those attempts are invalid gameplay evidence;
the reason for entering Test Menu has not been established. NVRAM Settings
was already implemented and does not require entering Test Menu.

The direct-button follow-up (`power-sled-direct-entry-20261009`) retained a
WAITING YOUR ENTRY mode-selection image outside Test Menu. Its instructions
identify Entry as mode confirmation and Call as the attendant switch. The
later direct attempt (`power-sled-direct-decide-20261009`) retained black /
SEGA-logo images rather than a confirmed mode screen before the Entry pulse;
therefore it does not demonstrate a valid confirmation or playable race.
All native links and exits passed in these runs. They used core SHA256
`5449427f70d7f9d0e38b7620ff9a2d0190e80a6638dea345a676936ecea6d220`.

The ordinary interactive launcher has no replay, Test/Service automation or
operator recipe. Final launcher, color persistence and installed-core evidence
is in `Docs/POWER_SLED_LAUNCHER_REVIEW_2026-10-09.md`. Playable race, steering,
physical-controller delivery and subjective audio remain unverified.

## Targeted Native Input Diagnosis — 2026-10-09

Four further bounded runs reused `test-retroarch-netpacket.py`, its direct
Network RetroPad buttons, isolated SRAM, screenshots and PCM recording. No
input movie was used. The tested ANS selections were Main `2` (Red), Slave `1`
(Silver), Relay `relay`, retaining the previously successful color topology.
The first run reused the validated initial NVRAM stage; later runs reused its
final isolated SRAM. No calibration setting was changed.

| Run Under `build-libretro-gpu/validation/` | Scope And Observation |
| --- | --- |
| `power-sled-gameplay-adaptive-20261009` | Installed core; persistent three-instance observation and direct Entry. Main/Slave captures show black, white and SEGA-logo scenes; Relay progresses through tutorial scenes. A single explicit Test/Exit control confirms direct button delivery. No race verified. |
| `power-sled-gameplay-entry-confirm-20261009` | Installed core; Test/Exit control followed by Entry, confirmation and P2 Entry. Main captures return to Test Menu after the P2 Entry stage. No race verified. |
| `power-sled-input-trace-20261009` | Separate temporary diagnostic core; Entry, P2 Entry, then explicit Test, Call and Entry. Test Menu is already visible after P2 Entry, before the explicit Test pulse. Adapter I/O tracing records the expected distinct input bits and their releases. |
| `power-sled-slave-only-input-20261009` | Same diagnostic core; only Slave receives Entry/Call/P2 Entry. Main/Relay remain neutral in the input trace. Retained Slave captures remain black and do not reproduce the Test Menu within this observation window. No race verified. |

All twelve instances establish native links, exit with code 0 and require no
forced termination; no owned process remains. Every final SRAM passes game
identity and container CRC checks. Main Red and Slave Silver remain concordant
in all three Ride field copies. Audio peaks in Main / Relay / Slave order:
`0/3990/0`, `0/795/0`, `0/876/0`, `0/880/0`. Relay emits nonzero PCM; these
particular runs do not reproduce the earlier nonzero Slave audio. Different
input paths and scenes prevent treating that observation alone as a sound
regression. Sound fidelity remains unqualified.

### Input Trace Finding

The temporary trace runs immediately after the existing adapter polls input;
it adds logging only. The three-program trace records:

| Requested Button | IN0 | IN1 | IN3 |
| --- | --- | --- | --- |
| Released | `ff` | `ff` | `ff` |
| P1 Entry / B | `ff` | `fe` | `ff` |
| P2 Entry / Y | `ff` | `fb` | `ff` |
| Test / R3 | `fb` | `ff` | `ff` |
| P1 Call / A | `ff` | `fd` | `ff` |

Each pulse returns to released values. In the Slave-only run, IN0 stays `ff`
throughout the complete trace and Main/Relay record only neutral input.

This narrows the earlier unexpected-Test observation: it can occur without
a movie, while the adapter's P2 Entry mask is correct and the Test bit remains
released before the later explicit Test pulse. Sending the same buttons to all
three programs is a separate variable; the Slave-only run does not establish
the same response. The native I/O reads, firmware menu dispatch and program-role
handling still require analysis before changing bindings or emulation. The
existing patched Main program remains a limitation, not a proven cause.

### Evidence And Restoration

Each run retains its recipe, overrides, manifest, PIDs, logs, SRAM, captures,
PCM and `review.json`. The adaptive run additionally records timestamped
direct actions in `adaptive-actions.jsonl`. The trace directory contains
`input-review.json`, the temporary source/binary snapshots and
`followup-review.json`, which pins all four reviews. Reproduction uses the
same linked runner with the retained recipe, options and baseline paths,
plus `--sample observe`, `entry-confirm`, `trace` or `slave-only` as applicable.
Trace runs set `SM2_POWER_SLED_INPUT_TRACE=1` and use the retained diagnostic
binary; screenshots/lifecycle success remain separate from gameplay proof.

Installed-core runs use SHA-256
`00738f3a3255675a6643106db942e8ef81640700bb47e7a863bb95ba211d36b1`.
The temporary logging build uses
`afa8a1c409597feb9a8b081a053d6ea09ed3a56f619fe8eae51397c7b4b0da02`.
The original source was restored byte-for-byte and rebuilt; the normal build
and both installed copies again match the first hash. Diagnostic instrumentation
was not installed in the normal core paths. No permanent core change, additional
NVRAM acquisition campaign, MAME execution or other-project edit occurred.

Playable racing, steering response and physical-controller qualification stay
open. Next: inspect native I/O reads and role-specific firmware input handling
using this retained reproduction before another gameplay qualification run.

## Native Program Diagnosis Completed — 2026-10-09

The role-specific native input analysis resolves the unexpected Test Menu
transition: Main/Relay P2 Entry is intentionally translated into command
`0x1000`, which requests native state 15 on all linked units. Raw Test stays
released; I/O wiring and adapter masks are correct for this reproduction.
Slave-only input does not generate that operator command.

A separate start sequence qualifies selection and boarding states 5 and 6 on
all three programs. The first Main P2 Call can be overwritten by mode
confirmation in the same frame; repeating it after confirmation preserves
command 4 and reaches state 6. The next receiver task requires command 5,
which the operator decoder associates with unbound IN1 bit `0x10`. MAME calls
that input unused; its physical meaning and actual gameplay effect still need
qualification before adding a verified binding. Playable racing remains open.

Four additional diagnostic sessions / twelve clean native-linked exits,
SRAM CRCs and ANS colors are pinned in
`build-libretro-gpu/validation/power-sled-native-io-20261009/review.json`.
The temporary source is restored exactly; normal build and both installed
cores remain SHA-256 `00738f3a3255675a6643106db942e8ef81640700bb47e7a863bb95ba211d36b1`.
See `Docs/POWER_SLED_NATIVE_INPUT_DIAGNOSIS_2026-10-09.md` for instruction
addresses, commands, runtime state transitions, reproduction and limits.

## Operator Start Integrated — 2026-10-09

The command 5 candidate is now qualified: Main Port 1 Start supplies native
IN1 `0x10`; all three programs advance from boarding state 6 to race state 7.
Main and Slave show the race timer, position and course movement. Start is
integrated on Main/Relay Port 1, preserving the old Start and Entry/Call wiring.
The normal installed core is checked separately. Earlier no-race findings above
remain the historical observations before this binding was available.
See `Docs/POWER_SLED_OPERATOR_START_2026-10-09.md` for evidence and outstanding
handlebar, audio and full-race qualification.

## Automated Handlebar And Race-Cycle Follow-Up

The current installed core now passes a Semi Auto race-cycle observation through
checkpoints, Time Extension and Game Over. Full-range independent trigger sweeps
in a private passive RetroArch diagnostic verify ADC delivery and both native
response signs for all four handles on Main and Slave, without cross-rider input.
The earlier fixed-value fixture was outside the native response zones. No input
adapter or calibration change is required. Normal source and installed hashes
are preserved. See `POWER_SLED_HANDLEBAR_AND_RACE_VALIDATION_2026-10-09.md` for
the current command, observer evidence and remaining physical, Manual-mode,
post-race and sound-fidelity limits. Earlier unverified steering/race statements
above are historical observations; only the stated automated scope is closed.
