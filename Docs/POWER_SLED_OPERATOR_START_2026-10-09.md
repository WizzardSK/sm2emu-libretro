# Power Sled Native Operator Start — 2026-10-09

## Result

The previously unbound native operator input **IN1 bit `0x10`** generates
command 5 and advances the linked programs from boarding state 6 into race
state 7. A diagnostic three-unit RetroArch run reaches the race on Main and
Slave, with a visible timer, POSITION 1 and movement along the course.

The core now adds this native input to **Port 1 Start** for `powsledm` and
`powsledr`. The existing Start line, Entry/Call buttons, Service inputs and
handlebar channels are preserved. The Slave program and Port 2 receive no
additional operator input. Start is available in the reduced controller profile
as a gameplay action. No new Core Option or automatic operator sequence is added.

## Native Evidence

| Unit | Native Role | State 6 → 7 | Program Counter |
|---|---|---|---|
| Main | `0x0200` | Frame 3820 | `0x000bd750` |
| Relay | `0x0100` | Frame 3467 | `0x000bd750` |
| Slave | `0x0000` | Frame 3120 | `0x000bd740` |

Main writes command 5 at frame 3816, PC `0x000bd528`, with actual adapter
ports `IN0/IN1/IN3 = ef/ef/ff`. Relay and Slave receive the command over the
existing linked-cabinet path. No forced RAM state, injected outgoing command,
safety bypass or calibration edit is used. No Test state 15 occurs.

Main is still the upstream patched Relay approximation; the original Main
program remains undumped. The original cabinet label for the input is unknown.
The local MAME declaration calls IN1 bits `0xf0` unused, while the actual
operator decoder consumes bit `0x10` for command 5. This change follows the
qualified native program behavior. The direct command-input pulse was tested
on Main; the Relay binding follows the same decoded operator path.

## Manual Sequence Used

See [Current Start Sequence](POWER_SLED_START_SEQUENCE_2026-10-10.md) for
the explanation using game input names, separate confirmation/advance
activations, countdown readiness and local P2 versus a linked Slave.

With Main Red / Slave Silver / Relay linked and startup complete:

- Main **A / P1 Call** enters mode selection.
- Slave **B / P1 Entry** confirms its mode.
- Main **X / P2 Call** confirms its mode. Release and wait at least seven
  seconds at default 60 Hz before pressing **X** again to enter boarding,
  allowing the native arm/platform animation and its audio sequence to finish.
  The qualification on 2026-10-10 uses an eight-second wait. The first pulse
  can be overwritten by local confirmation.
- After boarding, Main **Start** begins the race.

Main/Relay **Y / P2 Entry** deliberately enters Test Menu through native
command `0x1000`. Its established hardware binding remains intact.
This sequence is a qualified operator path, not launcher automation or a claim
that it is the sole valid sequence for every cabinet configuration.

## Verification and Limits

The ROM-free input checks verify role/port isolation, retention of the old
Start line, availability without Service, disabled-controller behavior and
release handling. All existing input-profile checks pass.

Evidence root:
`build-libretro-gpu/validation/power-sled-command5-20261009/`.
The diagnostic recipe, exact commands, native logs, screenshots, PCM and SRAM
are retained. The same operator path passes using the normal installed development core,
with no trace instrumentation: Main and Slave show the race HUD, the timer
changes between captures and the course advances. Both runs pass native links,
six clean exits, no forced termination and no runner-owned residual process. `review.json` pins
both run manifests/results, exit status, native link status, SRAM identity/CRC,
all three Ride copies, PCM and deployment hashes. PCM signed-16-bit peaks
in Main / Relay / Slave order are `0/3333/4359` for the diagnostic run and
`0/3020/4350` for the normal installed core. Main remains silent; emitted PCM
alone does not establish correct sound.

Actual handlebar response, physical controller behavior, sound fidelity and a
complete race are still separate qualification work. All three sets remain
preliminary. This task neither executes MAME nor acquires NVRAM samples.

## Deployment

The original frontend-neutral machine source is restored byte for byte from
the pre-instrumentation snapshot. The normal binary contains no native trace
markers. Both local RetroArch cores are updated with backups and matching
SHA-256 `29be97fa659d0818ca9150e0cf78d8fd5a331862d80e26883d8eecc555de4daa`.
No commit or push is performed.

## Subsequent Main Audio Diagnosis

The production Main silence is now traced to unsupported rider commands in its
Relay sound ROM tables. An isolated complete Slave audio-region candidate on
the unchanged Main patch and role produces audio during the race. Integration
is tracked separately, including preservation of existing archive recognition;
original Main audio fidelity remains unknown. See
`Docs/POWER_SLED_MAIN_AUDIO_DIAGNOSIS_2026-10-09.md`.

## Production Main Audio Integration Completed

The correction is now integrated with the user-requested local-first policy:
Main looks for EPR-19466 and FPR-19459 in its own archive, then uses the split
Slave parent as fallback. Old Relay audio files are removed from the Main
requirements. Existing Main archives retain their identity through CRC-checked
main-program recognition. The installed-core original-archive session produces
Main audio during the race; both cores and local system databases are updated.
See `Docs/POWER_SLED_MAIN_AUDIO_INTEGRATION_2026-10-09.md` for current evidence.
Earlier pending-integration and silence observations above are historical.

See `Docs/POWER_SLED_BOARDING_ANOMALY_2026-10-10.md` for the restored
Master animation and its native 380-frame model / 400-frame sound boundaries.
