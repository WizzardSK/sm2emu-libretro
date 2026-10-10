# Linked-Cabinet Network Validation — 2026-10-09

## Scope And Evidence Boundaries

This package checks reviewed Automatic Network Settings, frontend lifecycle,
native communication-board handshakes and bounded transport stress in isolated
RetroArch Nightly 1.22.2 on macOS arm64. It does not qualify synchronized racing,
controller behavior, Internet links or mixed operating systems.

The existing `scripts/test-retroarch-netpacket.py` owns every frontend process,
configuration, port and save directory. Its new exercises extend that lifecycle;
the matrix reviewer does not implement another frontend launcher. Every retained
run records the executable, core hash, roles, logs, screenshots and cleanup.
Only SM2-Emu Libretro in RetroArch was exercised. No ROM is checked into Git.

## Known-Peer Handshake Repair

Symptom: after restarting just the Daytona Slave, its local roster disappeared.
The Master still knew the Slave and therefore ignored its repeated Hello.
The pre-fix Slave never reported another ready roster.

`src/libretro/netpacket.cpp` now distinguishes an identity request from an
ordinary Hello reply. A ready peer answers requests from known peers; replies
do not produce an echo loop. Both types retain pending-packet deduplication.
Native frame contents, ring order, NVRAM fields and machine emulation are
unchanged by this repair. The wire version and frontend protocol identifier
advance to **NetBoard v3**. Every participant must update together; v2/v3
interoperability is not supported. Saved Core Options and SRAM formats are
unchanged.

The ROM-free checks cover a known peer request, absence of reply echoes, local
reconfiguration, 1400 duplicate announcements plus 1400 duplicate requests,
early frames, ordered bursts, bounded overflow and recovery. Existing native
2/3/4/8/9-cabinet and mixed-program Power Sled ring checks pass.

In RetroArch, the repaired Slave reports a new ready roster after its individual
Restart. Its native board still requires the other Daytona cabinet to restart:
an already-established board does not repeat the FF/FE link enumeration for a
rebooted node. Coordinated Restart restores native IDs 1/2 and count 2. This
distinction also occurs after disconnecting and reopening the Slave process.
The unchanged shared protocol handles FF/FE during establishment, consistent
with [MAME's communication-board simulation](https://github.com/mamedev/mame/blob/master/src/mame/sega/m2comm.cpp).
These observations establish a Daytona recovery procedure, not a recovery claim
for every game.

## Automatic Preset Matrix

The 20-case matrix checks each program's native SRAM identity and CRC, every
masked field and mirrored copy against the generated catalogue, complete
Netpacket roster, final native link status before cleanup, agreement on native
count, valid PNG evidence and clean process exits.
The current runner additionally includes `manxttc` for 21 selectable cases;
that clone was added during the separate Relay diagnosis below.
Each program's successful CRC/field review is retained in
`network-fields-review.json`, including runs whose later native board check
fails. This preserves preset proof independently of native Relay qualification.

The original 18-second settle run verified 17 cases:

- Daytona and Daytona Special, two cabinets; Daytona, eight cabinets.
- STCC with Relay, three participants; STCCA/B/O, two; STCC, nine participants.
- Sega Rally with Relay, three participants; Sega Rally, five participants.
- Indy 500 and its Deluxe clone, two cabinets each.
- Wave Runner, Ski Super G and Super GT 24h, two cabinets each.
- Over Rev, four cabinets; Virtual On with its dedicated Relay program, three.

Motor Raid Master/Slave/Live passes the repeated 45-second settle run with
native count 3. Its retained final image reaches attract/credit display. The
shorter original run captured NETWORK ERROR and an unsettled board; the longer
run does not establish whether the difference was caused by wait duration or
runtime scheduling. It is not evidence of a synchronized race.

Motor Raid Deluxe's default Deluxe cabinet reaches a drive-board error before
native networking is established. A targeted probe setting the existing
`Cabinet Type` selector to Twin on all three participants passes native
Master/Slave/Live networking and reaches attract. All compound native Cabinet
Type fields were independently verified in the saved SRAM. Automatic Network
Settings correctly preserve this independently selected Cabinet Type; no new
drive-board bypass or automatic cabinet-type override was added.

The user subsequently approved Twin as Motor Raid Deluxe's Automatic Initial
NVRAM Setup default. The core now applies the existing verified compound Twin
encoding when creating new NVRAM and also defaults the Cabinet Type selector
to Twin. The acquired native Deluxe template and Service Menu catalogue remain
unchanged. Existing saved NVRAM takes precedence over automatic setup, and an
explicit Deluxe selection remains available.

### Motor Raid Deluxe Automatic Twin Default Qualification

The rebuilt core passes the Save RAM checks, including automatic Twin compound
fields and mirrors, native integrity, the `Twin (Default)` selector label,
missing-variable fallback and preservation of an explicit Deluxe selection.
The catalogue audit passes for 87 sets and 331 options; native Service Menu
defaults remain separate from approved core overrides.

The established RetroArch suite passes `motoraiddx-3-relay` with a 45-second
settle and no explicit Cabinet Type override in the test configuration. All
three instances apply automatic initial NVRAM, reach native link count 3 and
persist the verified Twin compound fields and mirrors with valid SRAM CRC.
They exit normally without forced termination or residual processes. This
qualifies preset initialization and native linking, not synchronized gameplay.

Evidence: `build-libretro-gpu/validation/motoraiddx-twin-default-20261009/coverage.json`.
Both installed local cores match the tested build SHA-256
`0fa6264eb5da73d74f706476e939d04471e72e77e91ef26eb76e368bf2007a72`.
The `deployment/deployment.json` receipt records both backups and hash checks.

Manx TT's three-participant Relay case still fails after a 45-second wait:
Master/Slave reach native IDs 1/2 and count 2, while the Relay stays at
CHECKING NETWORK. Its native preset fields match the catalogue. Qualification
of that native Relay remains open.

### Manx TT Native Role Investigation

Side-effect-free `M2Comm::role_inputs()` diagnostics show Master FG 1/shared
role 1, Slave FG 0/role 2 and Relay FG 0/role 3. The generic upstream/MAME
simulation recognizes Relay role 0. The original Relay momentarily reports
alive with ID 0/count 0, is disabled by the game and starts again.

A scoped candidate recognizing Manx TT role 3 passed a synthetic relay ring
and an old/new 600-frame offline comparison: software image, complete WAV,
native saves, CPU state and master cycles were identical. Standalone, headless
and core builds passed. However, actual RetroArch `manxtt` and `manxttc` still
disabled/restarted the Relay after momentarily reaching ID 0/count 2. The
candidate was **rejected and reverted**; it is not in the installed final core.
Only the read-only role diagnostics remain. Native role decoding is one gap;
the rest of the Relay protocol still needs firmware-level reference work.

The unmodified `e8d96c1` reference source retains the same role-0 predicate
(source SHA-256 `35c2eb621991b649c48e2bdeafe3be3b25f6f853e24872f9822ea7b814ee9b9b`).
Its whole-machine 600-frame offline comparison differs from the current port
in image, audio, saves and CPU state. Because the old and candidate port runs
are identical, those reference differences predate this candidate. Whole
upstream equivalence is not claimed; the complete port contains other
previously integrated changes. No runtime probe or NVRAM acquisition was
performed in MAME.

### Subsequent Manx TT Initialization Fix

The earlier Manx TT failures above are historical. Native program inspection
now identifies the rejected ID-0 boot result. A scoped counted role-3 Relay
passes the parent and Revision C 45-second RetroArch initialization checks,
with IDs Master 1/3, Slave 3/3, Relay 2/3 and no board restart after establishment.
Exact old/new offline comparisons and generic/Power Sled ring checks pass.
Both installed cores match the tested build. A subsequent read-only Revision C
session shows all three programs completing phase-2 synchronization and advancing
through the 3D demo/title/credits sequence, with eight screenshots per unit,
valid presets/CRC and three clean exits. No persistent post-link black screen
is reproduced. The private observer was not installed; production source,
build and both installed artifacts retain their exact normal identities.
Subsequent normal-core gameplay found and corrected a further counted-Relay
payload omission. The parent triplet and Revision C pair/triplet now show
two-rider races, Time Up/ranks and subsequent progression; Relay displays LIVE.
See `MANX_TT_RELAY_INITIALIZATION_2026-10-09.md` for the earlier boot evidence
and `MANX_TT_GAMEPLAY_VALIDATION_2026-10-09.md` for the current binary and limits.

## Frontend Lifecycle And Stress

Daytona Master/Slave checks on the installed v3 core establish:

- Quick Menu entry and return retain the linked session. Ordinary Pause Toggle
  is ignored by this Netplay session; menu return is the tested path.
- Actual Core Options transitions `2 Cabinets → Disabled → 2 Cabinets` apply
  through the frontend. Both offline SRAM snapshots contain the reviewed Single
  value in all native mirrored fields, with valid container CRCs. Re-enabling
  and coordinated Restart recover the expected native identities/count.
- Stopping only the owned Slave process for 2 seconds and 20 seconds, then
  continuing it, retains native link readiness without receive-queue overflow.
  Subsequent coordinated Restarts also pass.
- Closing and reopening the Slave exits the old process normally and records
  the new PID/log. Immediate native recovery is not supported in this probe;
  coordinated Restart recovers both boards. All owned processes exit normally.

The disabled phase's last logged native status can be stale: native link
diagnostics are emitted only while external linking is active. Offline preset
proof comes from the saved native fields, not that stale status.

## Reusable Commands And Artefacts

Use Python with Pillow available (the bundled workspace Python was used):

```sh
python3 scripts/test-retroarch-network-suite.py \
  --output build-libretro-gpu/validation/network-suite-new-run
```

The matrix resumes verified cases only when core/assets hashes match. Failed
attempts remain separate; a changed core requires a new output directory.
The child runner owns bounded stages and cleanup; an outer timeout must not
kill it before its `finally` block. Review excludes native link loss caused by
ordered cleanup. Screenshots must be complete valid PNGs before hashing.

Use the existing documented Netpacket command with one additional flag:
`--network-exercise resume-restart`, `stall` or `reconnect`. `options` holds
only the owned frontends for at most 420 seconds while their GUI is operated.
It publishes `options-ready.json`; local `exercise-command.json` may request
`phase`, `settle`, `expected_link`, `reset` and `finish`. The result retains every
phase and does not promote a failed native phase to successful gameplay.

Evidence is retained below `build-libretro-gpu/validation/`:

- `network-suite-20261009/coverage.json`: original 20-case matrix, core
  `f1e93586bf051c85b648b96dc2b956f3f3afca00a97b6ff4547081a2b1fe7928`.
- `network-lifecycle-before-20261009/menu-restart/`: reproduced restart defect.
- `network-lifecycle-after-20261009/`: corrected restart, GUI options, offline
  SRAM proof, stalls, reconnect and their command/result records.
- `network-suite-after-20261009/coverage.json`: targeted repeated matrix.
- `network-lifecycle-after-20261009/cabinet-preconditions.json`: diagnostic
  Cabinet Type probes with actual command, native field and board checks.
- `network-lifecycle-after-20261009/power-sled-v3/`: unchanged native
  Main/Relay/Slave SRAM baselines, confirmed native IDs 1/3, 3/3 and 2/3 on v3.
- `network-lifecycle-after-20261009/manxtt-role-diagnosis/` and
  `network-suite-final-20261009/`: native role traces and rejected candidate
  runs for the parent and Revision C. They are failure evidence.
- `manxtt-relay-fix-20261009/`: rejected candidate's offline comparison and
  separate pristine-reference comparison; no successful Relay qualification.
- `network-core-install-20261009/deployment.json`: backups and matching hashes
  for both installed `sm2_libretro.dylib` and `sm2_dev_libretro.dylib`; installed
  transport-repair hash
  `f969d2f52eba1b8f40df91882eb2dde89fee7e3e44eb73ac4399d752e15ae7e3`.
- `network-core-finalize-20261009/deployment.json`: final installation after
  rejecting the native candidate. Both local cores match the previously tested
  diagnostics build byte for byte, SHA-256
  `6bb32be377ee190fbe04ec43845238f346c2332099a984293b5b875f08a4ac4d`.

No commit or push is part of this package.
