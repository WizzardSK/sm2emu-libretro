# Power Sled Post-Race Audio And Master + Relay Review

## Scope

Investigate silence after race completion and the feasibility of Master + Relay
with Standalone Mode disabled. All experiments use isolated RetroArch copies,
configurations, saves and private cores. The audio correction and reviewed roster change are deployed. The reopened Master + Relay intro investigation and its deployed correction are documented below.

## Post-Race Audio

The Relay program includes a result-screen initializer at `0x28de0` and a
continuation at `0x28da0`. The continuation requests sound-table index `0x65`,
native packet `A0 11 01`. Relay Audio on Master already adapts the initializer
and routes that packet as `A0 61 01` to the auxiliary board.

The first isolated Standalone Master recording reached native phase 8 after a
race. Race music stopped before the result screen. The result initializer sent
`BF 57 7F`, but the expected music-start packet was absent, and auxiliary SCSP
active voices remained zero. Attract later restarted music. This reproduces the
reported silence in the experiment; it does not establish original-cabinet
behavior or qualify the linked-session result path.

A diagnostic follow-up confirms that the result music task is retired, rather
than remaining suspended. Native packet helper `0x12700` returns 0 if its 64-byte
queue cannot fit a three-byte packet. Callback `0x28da0` ignores that return value
and clears itself even when the packet was rejected. A private candidate keeps
that callback pending on failure and retires it only after successful enqueue;
the controlled repeat sends `A0 61 01`, raises auxiliary MIDI bytes from 57 to
60, and maintains one active auxiliary SCSP voice throughout the result phase.
The three guarded instruction edits are now integrated in Relay Audio on Master.
The queue size, scene timing, command tables and Disabled path are preserved.
The private repeat exits cleanly; the production 60-frame ABI state round-trip,
deterministic replay and malformed-state rejection also pass.
The first run exited normally before its requested final collection interval;
its runner status is failed, so it is retained as trace evidence, not a fully
completed runtime qualification.

## Master + Relay Without Slave

The previous transport roster rejected every session without a Slave. The
reviewed change permits exactly one Master and one Relay without Slaves,
retaining duplicate-role, total-count and four-rider limits.

The first linked captures were black. Delaying the automated operator inputs
allowed racing, but did not demonstrate that input timing caused the black intro. A diagnostic repeat records
phase 4 / attract, then phase 5 / selection, phase 6 / boarding and phase 7 /
racing after delaying the input sequence by 1800 replay frames. Three race
captures show advancing Master geometry/timer and the Relay LIVE camera.
Both instances have a ready roster/native link, exit normally and leave no
owned processes. This corrects the preliminary inference that a further native
race patch was required: only the transport roster restriction is changed.

The qualified arrangement is Master Silver (`powsledm:1`) plus Relay
(`powsledr:relay`), Linked Cabinets = 2, Standalone Disabled and Relay Audio on
Master Disabled. Native startup requires a Silver rider; other Master colors
without a Silver Slave are not qualified. No fake Slave, local four-owner
Standalone patch or extra audio board is used. Full-course completion and
physical controller response are outside this bounded qualification.

The first isolated run accidentally inherited Linked Cabinets = Disabled;
its captures are excluded from the linked-session comparison.

## Evidence And Deployment

- `build-libretro-gpu/validation/power-sled-post-race-audio-20261011/`
- `build-libretro-gpu/validation/power-sled-master-relay-20261011/linked-runtime/`

Private build scripts restore the source files and normal build artifact after
creating diagnostic cores. After the verified audio correction, the normal build and installed core both
have SHA-256 `073e95157905d8528cf4b6cb19732bba40279a3d769459dfa09ade9f91b189b3`.
The previous installed core is retained in the audio evidence directory.
The dev core remains absent. The reviewed roster change is included in the final normal build.
No ROM bytes are added to the repository. No commit or push is performed.

## Usage

Sol High retained. The account meter remained at 1% between the current review
baseline and final check (integer-rounded display), below the approved absolute
35% ceiling. Reset: 2026-10-18 07:47:24 Europe/Rome.

## Reopened Intro Qualification

The user reports that Master + Relay shows a persistent black Master intro,
whereas Master + Slave + Relay and Standalone work. Previous captures qualified
racing and Relay LIVE only; the blanket support claim was too broad. The roadmap
item is reopened. Native phase 4 is insufficient proof of a rendered intro.
A no-input diagnostic pair is now used to inspect its native intro conditions.

## Matched Intro Comparison And Correction

The requested comparison uses the same passive observer, neutral game-input
replay, isolated baseline and normal program patches for Master Silver + Slave
Red and Master Silver + Relay. Both enter phase 4 through `0x2f3c0`, construct
the attract tasks, and run their scheduler. The difference is record preparation:

| Configuration | Physical Riders | Native Field Records | Fourth Intro Record |
| --- | --- | --- | --- |
| Master + Slave | 2 | 6 | Valid incoming record |
| Master + Relay, unchanged | 1 | 3 | Null pointer |
| Standalone | 1 | 4 local | Explicitly mapped local record |

Routine `0x45400` always constructs four visual actor callbacks at `0x44900`.
The unchanged single-rider mapping at `0xcd350` fills only three record pointers
in `0x505530`. Its fourth pointer stays zero. The fourth actor then reads ROM
address `0x10` as a coordinate: word `0xfffff980` enters the SHARC from i960
instruction `0x44960`. Subsequent invalid geometry contaminates the ordinary
rider records. The renderer is not the origin of that coordinate, and changing
the camera initializer does not fix it. Skipping only the null drawing callback
is also insufficient: the collision path at `0xb9990` still consumes the missing
record. Those failed private candidates are retained, not deployed.

The reviewed correction initializes and publishes a fourth local record on Main
only when native phase is 4 and the physical rider count is one. Main and Relay
map that record from the Silver packet header + `0xe0`, the native fourth-record
position. The ordinary field count of three is retained; the additional record
completes the four-actor attract presentation. Selection/racing phases retain
native Main ownership, and multi-rider configurations bypass this change.
It does not fabricate a Slave, change the Master network role, replace the
separate color field, or enable Standalone gameplay implicitly.

The Standalone source explains why its intro already works without Slaves:
its explicit four-owner assignment and four-record mapping cover this access.
Its additional AI, race and finish-order adaptations remain specific to that
experimental mode. This pair fix reuses the relevant record-layout principle,
not the complete Standalone gameplay behavior.

The private corrected pair has finite coordinates and a rendered intro, also
confirmed live by the user. Evidence:
`build-libretro-gpu/validation/power-sled-intro-pair-20261011/`:
`record-runtime`, `master-slave-runtime`, `origin-runtime`, `four-runtime`, and
the final normal-core runs. Private diagnostic source and build copies are
restored after every observer build. No diagnostic core is installed.

### B_CRX And Result Controls

The reconstructed Main also hosts a real rider, so its common program now counts
that board once in B_CRX after retaining the separate Master-presence flag.
Relay remains excluded, and an empty/incomplete handshake remains a pending
native network condition. Standalone accepts this shared diagnostic word instead
of requiring the older Standalone-only version.

With Relay Commands On Master enabled, Call P1 or Call P2 requests the native
Emergency Stop in result phase as well. After release, Coin or Start recovers
from Emergency Stop into attract. This is source-confirmed emergency/recovery
behavior, not a dedicated ordinary skip-results input; a phase-8 runtime proof
of this exact input sequence has not been added.

### Final Normal-Core Verification And Deployment

The final normal-core pair captures the rendered intro, subsequent selection /
boarding and a visible racing scene after delayed game inputs. The separate
normal-core Standalone run logs successful experimental program preparation and
captures its intro with no Slave. Both finish with exit code zero, no forced
termination and no residual processes. The matched two-rider reference bypasses
the one-rider helper condition. Complete-course behavior is not certified.

Only `powsledm` and `powsledr` receive the reviewed program-definition changes;
all other game patch maps are unchanged. Helper ROM space and branch targets are
verified, and all passive diagnostic source is restored. Program/runtime reviews
and installation backups are retained in the evidence directory.

- Built/installed normal core SHA-256:
  `6167258683c223688450412408f970c31a32a3a2f4fe0956128f11b082656d25`.
- Source/staged/configured/fallback database SHA-256:
  `3f725bac042ffa1de33a328cc6c29ad826cd12f6f60bdadda55c99401c8d4856`.
- Normal core installed, dev absent. No user saves or ROM archives are rewritten.
- No commit or push performed.

The expanded investigation and correction moved the integer-rounded account
meter from 1% to 3% (approximately two percentage points), within the authorized
35% absolute cap. Sol High retained; no Astra escalation was needed. Reset:
2026-10-18 07:47:24 Europe/Rome. This exceeded the initial under-one-point forecast.

## Interrupted Results Audio — 2026-10-11

Start / Select returning from results to attract exposed a separate overlap:
the existing Relay music-stop helper stops selection/race notes 2/3, but not
result note 1. The first proposed note-1 zero-velocity stop was rejected by
runtime verification. Result playback sets native voice flags `0x5d`, including
bit 4; the native ordinary note-off filter at `0x600f34`–`0x600f4e` excludes
that one-shot voice. A retained state-based observer still showed the result
voice alongside the new attract voice. That prototype is not installed.

The corrected helper uses native packet `A0 00 03`. Its dispatcher reaches
`0x602206`, clears auxiliary sequence slots and stops their sample voices
(marked with bit 3), through the existing native stop routine `0x60053c`.
It does not reset the hardware, change the volume or touch the rider board.
Master Relay Audio tags this control `A0 63 03`; the sound router translates
it only on the added Relay board. Its scene-stop helper retains rider stops
and existing selection/race stops. The separate Relay's result return call
at `0xbd698` uses the same native control before its previous stop helper,
via verified empty space at `0x1f1340`. Other sets retain their own audio.

The user's `powsledm.state` is copied into an isolated session; the original
file and configuration are preserved. Initial runner attempts did not load
it because core-specific state sorting and duplicate configuration keys were
not accounted for; they are excluded from state-based qualification. The
corrected run explicitly confirms state loading before following race,
results and return to attract. Private evidence is retained under
`build-libretro-gpu/validation/power-sled-result-stop-20261011/`.

Final state-based observer: result voice key `0001` is active in phase 8;
after return, phase 4 contains only attract key `0003`, with no residual result
voice. The normal-core repeat confirms visible attract and clean shutdown.
Exclusive routing checks match the auxiliary SCSP state to direct native
`A0 00 03` delivery and leave primary MIDI untouched. The installed normal
core and both system databases are updated with backups/hash verification;
the dev copy is absent. The separate Relay uses the verified native command,
but a linked results/intro audio transition is not newly runtime-qualified.

## Arrival Rank Screen Audio Separation — 2026-10-11

The user reports silence while the immediate finishing rank (1st/2nd) is shown,
before the subsequent result presentation starts its music. A state-based
auxiliary-board observer reproduces zero active voices from frame 10200 to
10740, about nine seconds at 60 Hz. Result music starts in phase 8 through
`0x28de0` / `0x28da0`, not at the individual rider's arrival.

Review identifies an adapter error: the broad primary-stop detours at
`0x3c3d8` and `0x3cecc` also stop the added Relay board. These calls belong to
the rider's finish/control task. On physical separate boards they affect
rider sound only; the Relay race-music task remains independent. The adapter
now leaves those two native calls unchanged. Scene-wide transitions still
stop both boards, including the result-to-intro sequence correction. This
keeps race music during the immediate rank display until the native result
initializer replaces it; it does not move the result-music callback earlier.

No additional hidden arrival track was found in the reviewed path. Indexed
Relay requests are explicit table alternatives, not sequential playlist
addresses. The isolated auxiliary trace has no other music-start request in
the former gap. This finding does not establish original-cabinet acoustics or
rule out every rider effect. Evidence is retained under
`build-libretro-gpu/validation/power-sled-finish-review-20261011/`.

The first arrival candidate correctly retained race music, but the user heard
race/result overlap. Its observer confirms two auxiliary voices after the
result start. The prior scene stop could fail under native queue pressure.
The final result callback explicitly enqueues native auxiliary sequence stop
before the result-start request, checking both enqueue results. On failure
it remains pending for the next native scheduler pass. This preserves the
later result initializer, with no frontend timer or earlier music trigger.
The guarded helper occupies verified empty program space at `0x1f0780`.

A first stop/start retry prototype was also rejected: when only one packet
fit, repeatedly enqueueing the stop prevented the following start from ever
fitting. The final helper uses two native scheduler callbacks. Once the stop
is accepted, it changes the task callback to a start-only retry; accepted
stops are not repeated. The task retires only after the result start fits.
The helper is guarded through `0x1f07d0`, below Standalone's `0x1f0800` region.
This bounded native scheduler handoff is essential to avoid queue starvation.

Final observer qualification from the same user state keeps one auxiliary
voice through finish states 1/2 and phase-8 entry. After the result sequence
starts, only result key `0001` is present; race key `0003` is absent. Both
queue stages complete and the run exits normally without owned residue.
The immediate rank gap is therefore corrected without advancing result music.
Qualification is Standalone Silver with the optional Master Relay board;
a separate Relay linked finish transition is not newly runtime-qualified.

Normal-core repeat loads the isolated user state, applies the AI selector,
reaches results and returns to the visible attract sequence after Start.
Exit is clean with no residual owned processes. Normal core SHA-256
`a09d462ffda9fa454b44681eddb8be2ec1f25a31a7d7043a2cffff27bc0d56a5` is installed with backup/hash verification; the dev core remains absent.
Databases require no change for these adapter-only corrections. Roadmap updated;
no commit/push. Account meter remains 5% before/after (integer-rounded), within
the authorized 35% cap. Reset: 2026-10-18 07:47 Europe/Rome.

## Relay B_CRX Count — 2026-10-11

User-reported B_CRX ERROR on Relay in the one-Main/one-Relay arrangement has a
specific diagnostic cause. Native `0x24e40` counts ordinary rider headers but
excludes both role `0x0200` Main and `0x0100` Relay. Reconstructed Main also
hosts a rider. Main already counts itself through the branch at `0x24e8c`;
Relay now uses the same branch to count Main once after retaining its separate
Master-presence flag. Relay itself is still excluded. This does not inject a
Slave, change Ride color, silence errors or force a success flag.

Native diagnostic type `0x51aca4` becomes 1 (one rider plus Relay); display code
`0x25060`–`0x250dc` maps 0/1 to ONE, 2/3 to TWO, 4/5 to THREE and 6/7 to FOUR;
8 displays ERROR. Incomplete startup can remain pending. The passive linked
observer reports type 1 on both boards in phase 4, Standalone false, ready
native links and clean exits. Evidence:
`build-libretro-gpu/validation/power-sled-defaults-bcrx-20261011/`.

Final reference-aligned build passes all Libretro save-RAM checks, including
per-network-set ANS visibility with NVRAM Settings OFF/Enabled and the four
Power Sled defaults/order. The normal linked repeat has ready native links on
both instances and clean process cleanup. That runtime build preceded removal
of the temporary non-network ANS registration; no emulation code changed in
the final UI-only rebuild. Final installed normal core SHA-256:
`914c9cc4aacb05560f58c09c93ba2ae611b9672016b20f65bcb5e6e3fc198a27`.
Both configured system databases contain the Relay count patch, verified by
hash with backups. The dev core remains absent. Deployment evidence is in
`deployment.json` under the evidence directory above. Existing saved option
values were preserved. No commit/push. Account usage remains 5% before/after
(integer-rounded), within the authorized 35% cap; reset 2026-10-18 07:47
Europe/Rome.
