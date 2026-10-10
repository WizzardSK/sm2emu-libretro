# Manx TT Relay Initialization

Date: 2026-10-09
Scope: Native Model 2A Link Initialization In RetroArch

## Symptom And Native Cause

With Master, Slave and Relay selected through the existing Automatic Network
Settings, the Relay repeatedly enabled the communication board, observed an
alive result with native ID 0, disabled the board and restarted its network
check. The NVRAM selectors and frontend roster were already correct.

CRC-checked static inspection of the parent i960 program identifies the native
boot acceptance gate at 0x00009fd0..0x0000a018. It reads count from mirrored
shared byte 3 and ID from byte 2. An ID outside the positive range 1..count
returns the boot state machine to its initial state. This check also applies
when the local native role is 3, Relay. Merely recognizing role 3 as an ordinary
uncounted Relay still produces ID 0 and cannot pass this gate.

## Correction

The frontend-neutral `M2Comm::set_counted_relay()` configuration is enabled only
for the Manx TT family in `Model2::init()`, the Model 2A implementation. Shared
role 3 increments enumeration and consumes a positive ID during the ring-size
message. The first boot-qualified version forwarded packets unchanged. Subsequent
race qualification requires this counted node to transmit its own status slot
before the received slot train; it still does not supply a third player. Both
the vblank and FG-read paths recognize it. The generic shared-role-0
Relay and other games retain their existing behavior.

For the tested transport order Master / Slave / Relay, the native result is
Master 1/3, Slave 3/3 and Relay 2/3. Native enumeration order is independent of
the frontend's instance number or ANS value. Three counts physical nodes;
this does not imply three playable riders or a controller binding change.

This is game configuration rebuilt at content load, so no mutable serialized
field, state format, Core Option, binding, ROM patch or NVRAM format is added.
MAME's local simulation and the previously retained pristine upstream reference
use the uncounted role-0 predicate. The change adapts their simulation to this
host-program contract; original communication-firmware equivalence is not
claimed. Earlier pristine whole-machine differences remain documented in
`NETWORK_VALIDATION_2026-10-09.md` and are separate from this old/new comparison.

## Verification

- ROM-free checks exercise positive IDs/count and payload forwarding through
  the counted Relay, alongside the existing generic and Power Sled rings.
- Core, headless and standalone targets build successfully.
- Exact pre-change and candidate headless binaries run the established
  600-frame offline baseline. Software image, complete WAV, native files,
  CPU state, master cycles and audio frame count are identical.
- Separate 45-second native sessions for `manxtt` and `manxttc` maintain all
  three boards alive, with positive distinct IDs/count 3 and no board restart
  after establishment. Persisted native selectors, SRAM identity/CRC and clean
  process exits pass the existing suite review. Six owned instances exit 0;
  no forced cleanup or residual owned process.
- The parent Relay reaches the MANX TT SUPERBIKE title. The first Revision C
  capture was black. A subsequent read-only diagnostic session records eight
  screenshots per unit and shows the moving 3D demo, title, Isle of Man credits
  and SEGA logo. All three programs complete network boot and advance through
  normal attract substates 3, 5, 7, 9 and 13. Received synchronization phases are
  2/2/2 on all units. No persistent post-link black screen is reproduced.
  This qualifies the observed attract progression, not synchronized racing.
- Both installed local cores have backups and match the tested candidate
  SHA-256 `1cdb9966857e46e733c82616503ecbf43937af078168d9bb9b014a0537115588`.

This document records the initial boot-qualified binary. Linked gameplay and
the later normal binary are now qualified separately in
`MANX_TT_GAMEPLAY_VALIDATION_2026-10-09.md`; the historical hash above is not the
latest installed binary. Longer stress is outside this bounded qualification.
No MAME session or NVRAM acquisition campaign was
run. No commit or push was made.

## Reusable Runner And Evidence

The existing `scripts/test-retroarch-network-suite.py` now also checks Manx TT's
positive ID/count contract and rejects a board restart after establishment.
To reproduce only these cases, using a fresh evidence directory:

```sh
python3 scripts/test-retroarch-network-suite.py \
  --case manxtt-3 --case manxttc-3 --settle 45 \
  --output build-libretro-gpu/validation/manxtt-relay-new-run
```

Use a Python runtime with the existing Pillow dependency, as for the established
suite. Exact commands and results are under
`build-libretro-gpu/validation/manxtt-relay-diagnosis-20261009/`:
`wired-command.json`, `revision-c-command.json`, their runs/logs/screenshots,
`native-preset-review.json`, `offline-commands.json`, `offline-comparison.json`,
build logs and `deployment/deployment.json`. Source snapshots and private ROM
analysis remain in the ignored evidence directory, never in Git.

An initial command preflight rejected an unnecessary optional-Relay flag before
launch. The first candidate run had incorrectly placed configuration in
`Model2Original`; it is excluded because Model 2A never enabled that candidate.
Its three instances still exited cleanly. Corrected runs are the qualification
evidence. The original Model 2 source file was restored exactly.

## Revision C Post-Link Observation

The earlier single black capture did not establish a persistent blockage. To
inspect the subsequent native program states, a private temporary observer reads
work RAM and communication RAM every 60 machine frames. It changes no state,
input, ROM, timing option or packet. This interval is specific to the slow boot
and attract phases; it is not a general input-response sampling rule.

The program checks the three received slot phases at `0x1a121c4 + n * 0x1c0`:
phase 1 in the routine around `0xa1c4`, then phase 2 around `0xa528`. Observations
show all three slots at phase 2 and global state `0x5bba08` advancing from network
boot 1 to normal state 3 on Master, Slave and Relay. Local substate `0x5bba0c`
subsequently progresses through the attract sequence. The retained run has no
board restart after establishment, valid persisted presets/SRAM CRCs, three
clean exits and no residual owned process. All 24 screenshot files pass image
integrity checks and the contact sheet was visually reviewed.

The temporary observer core was never installed. Production source was restored
byte for byte and rebuilt before running the private observer. The resulting
normal build and both installed copies retain the SHA-256 stated above. No
additional emulation correction is justified by this observation. The exact
cause of the earlier single black frame is not established. Relay demo views
may differ from the player views; race synchronization remains unqualified.

Evidence is retained under
`build-libretro-gpu/validation/manxtt-relay-post-link-20261009/`: exact
`observer-command.json`, observer source/binary, build and runner logs, eight
screenshots per unit in `observer-run/`, `observer-contact.png`, and the replayable
retained-evidence review `review.py` / `review.json`. Private ROM analysis and
temporary diagnostics remain ignored and are not project payloads.

For ordinary repeated visual observation, the existing runner now supports
`--screenshot-samples` (1–20) and `--screenshot-gap` (0–60 seconds). Default
single-capture behavior is preserved. A bounded production-core command is:

```sh
python3 scripts/test-retroarch-netpacket.py \
  --retroarch '/Users/andrea/Retro/Apps/RetroArch/Nightly/RetroArch (ARM).app/Contents/MacOS/RetroArch' \
  --core '/Users/andrea/Library/Application Support/RetroArch/cores/sm2_libretro.dylib' \
  --rom '/Volumes/MacBook External Drive/Retro/_Media/Sega - _Arcade (Model 2)/roms/manxttc.zip' \
  --system-assets build-libretro-gpu/libretro/system/sm2-emu \
  --set-name manxttc --cabinets 3 --automatic-network \
  --capture-screenshots --settle 18 --screenshot-samples 8 --screenshot-gap 5 \
  --port 55576 --output build-libretro-gpu/validation/manxttc-attract-new-run
```

Use a fresh output directory and a free port. This production command captures
visual/lifecycle evidence only; internal program-state evidence belongs to the
retained private diagnostic session. No Service/Test automation or NVRAM
acquisition was performed.
