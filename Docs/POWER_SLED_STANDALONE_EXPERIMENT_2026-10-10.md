# Power Sled Standalone Experiment — 2026-10-10

## Contract And Current Status

The Power-Sled-family-only **Power Sled Standalone Mode (Restart Required)** System
option is experimental, uses Disabled / Enabled and defaults to Enabled.
It applies to the reconstructed `powsledm` Master loaded with Linked Cabinets
Disabled. The Master target is one human and three distinct native AI sleds.
The Relay now supports a separate continuous Attract presentation with no race
start inputs; see `POWER_SLED_RELAY_ATTRACT_2026-10-11.md`. The Slave and linked
sessions retain their ordinary program. Reload content to
apply the choice or switch between standalone and linked play. Relay Audio is
independently selectable. System order is Standalone Mode, Relay Audio On Master, Relay Commands On
Master and AI Finish Speed Fix, all before NVRAM Settings. Keys, choices and defaults are unchanged.

The candidate now constructs the full native race, initializes its timer and
creates three moving AI tasks. The original immediate GAME OVER was traced to
the reduced one-node race dispatcher. Additional qualification covers all four
local owners during attract, non-Silver startup and AI-aware rankings. Yellow
now has its native boarding camera and complete 3 / 2 / 1 / GO countdown. The
normal installed core is updated; native result, GAME OVER and return to a
moving attract scene are qualified. No factory
single-cabinet hardware fidelity is claimed.

## Native Reconstruction

`src/libretro/power_sled_standalone.*` owns guarded, in-memory program edits.
The adapter invokes it only for the Master and isolated one-node loopback.
It adds no Libretro dependency to machine code and modifies no ROM archive.

- Replace ownership initialization at `0x24370` with a four-entry rotation
  beginning with the current native Ride color. Preserve the original tail
  clearing `0x5030d4` and `0x51aca8`; clear unused ownership entries.
- Change both owned-count instructions at `0xcd1f8` / `0xcd248` and all
  race-count cases at `0xcd284` / `0xcd28c` / `0xcd294` to four. Native ownership
  count lives at `0x503428`, total race count at `0x51ac38`.
- Replace record mapping at `0xcd350`: all four competitors use the existing
  outgoing four-record train, returned by loopback, beginning at `0x1a021d0`
  with stride `0x30`. The local packet pointer table is `0x505530`; command
  owner pointers and Master command pointer target local header `0x1a02180`.
- Appended helpers occupy verified empty space at `0x1f0800` and `0x1f0880`;
  the rotated ownership table starts at `0x1f0a00`, followed by the local
  roster helper. They do not overlap the
  independent Relay Audio helpers. Validate every original instruction and
  the entire appended area before applying any edit; unsupported programs
  retain their ordinary behavior with a notice.

- Replace the one-node dispatch comparison at `0x43e74` with a branch to
  `0x43e78`. The original one-node task at `0x43840` never calls the full race
  constructor `0x438e0`, initializes neither the race timer nor AI tasks, and
  therefore produces the immediate end reported by the user. Standalone uses
  the existing full countdown/constructor path without falsifying node count.
- At startup roster evaluation `0x24a90`, use the four local ownership colors
  (one owner each), a real Master and no separate Relay. Resume native checks
  and diagnostics. This includes Silver as an AI when the human chose Red,
  Black or Yellow; it does not relabel the Master or change persisted Ride ID.
  The helper occupies `0x1f0a40` through `0x1f0a73`; its space is guarded.
- The native four-color configuration is enum 6. Its ordinary count case owns
  two sleds per node and expects eight overall. The first roster adaptation
  omitted those count cases, leaving frozen actors and absent course data.
  All count cases are now four; the failed Red run is retained.
- Finish-order filter `0x41744` and HUD-rank filter `0x417a0` include all four
  competitors. Physical rider count `0x52949e` stays one, preserving native
  input/collision semantics rather than pretending that AI are human nodes.
- Attract actor construction, collision and physics loops at `0x44240`,
  `0x44334`, `0x45510`, `0x45618`, `0x45650` and `0x45810` include the last
  owned slot. It is a real fourth sled in this mode, not a reserved slot.
- Boarding/countdown construction at `0xd0498` and `0xd0588` no longer halves
  the local competitor count. The original two-task limit omitted Black and
  Yellow (`2` and `3`), including their native camera and countdown updates.
  The user-reported Yellow ocean-only scene and stuck `1` were independently
  captured. All four native boarding/countdown tasks are now allocated;
  their counters, readiness handshake and race transition are unchanged.

The native race constructor retains the human task `0x3cfe0`, AI task builder
`0x3d5c0`, physics builder `0x3e270` and their normal tasks. AI builder
`0x3d5c0` allocates `0x3d1f0` for ownership entries after the human. The passive native trace confirms that
these builders execute and all four course positions advance independently.
No synthetic Slave packet or frontend-generated AI motion is introduced.

## Persistence And Lifecycle

The frontend state trailer uses reserved flag bit 8 for active standalone
reconstruction. A mismatched Master state is rejected before machine mutation,
independently of the Relay Audio flag. Same-configuration round trips remain
supported. Native state format 11 is unchanged. Existing NVRAM is preserved;
the option does not persist fabricated peers or alter calibration.

An active patched program retains one-node communication until content reload,
even if the user changes the Linked Cabinets option. The frontend reports the
reload requirement; it cannot safely turn patched code into a linked program
using only Restart.

## Retained Verification And Limits

Evidence root: `build-libretro-gpu/validation/power-sled-standalone-20261010/`.

- `abi-off`: Disabled image/PCM hashes match the prior ordinary baseline.
- `abi-enabled` and `corrected-abi`: same-configuration round trip,
  deterministic replay and corrupt-state rejection pass. An ordinary Master
  state is rejected without mutation. The corrected build restores the
  native ownership tail omitted in the first prototype.
- `prototype-run`, `race-observe` and `corrected-race`: existing RetroArch
  runner, one owned process, isolated configuration/SRAM/content, retained
  Manual input movie and screenshots/audio. All finish cleanly without
  residual owned processes. They reach selection, boarding, a rendered course
  and GAME OVER. This does not qualify the intended race.
- Corrected snapshots show four distinct owners, four competitors and four
  distinct local record pointers. The native phase at `0x53e744` reaches 7
  then 8, but AI coordinates remain at their start and initial race ticks
  `0x51acd4` remain zero. The first snapshot decoder incorrectly labeled
  outgoing command `0x5293f4` as phase; corrected reports use `0x53e744`.
- The retained input movie sends Start at local frame 4080, independently of
  boarding readiness. Native race constructors gate initialization on
  `0x51ac64`, set by boarding completion. `delayed-start` tests a single
  concrete hypothesis by moving only Start to frame 5400. The run exits cleanly without residue. Snapshots at 103 / 113 seconds still
  have phases 7 / 8 respectively and zero course positions; initial race ticks at 113 seconds
  are zero. Delaying Start alone does not resolve the initialization failure.

## Current Bounded Qualification

- `diagnosis`: a passive instruction observer confirms that the initial
  prototype selects `0x43840`, leaves initial ticks at zero and does not enter
  the full race/AI builders. Production source and core are restored exactly.
- `full-race`: the dispatch fix enters `0x438e0`, loads 2,940 initial ticks from
  native NVRAM, invokes `0x3d5c0` and advances four distinct course positions.
  It reaches native race phase 7 and end phase 8. AI were still excluded from
  the HUD ranking; that limit is addressed separately above.
- `red-normal`: the original roster rejects a lone Red Master because no
  physical Silver packet exists. The later roster adaptation records local
  Silver ownership while preserving the human's Red identity.
- `red-race`: the first four-color adaptation selected enum 6 but retained
  native 2/8 ownership/race counts. Intro moved only one actor; later course
  rendering became black with REVERSE. A changing HUD rank and 2nd result
  do not qualify that failed run. The user closed the owned test window; its
  nonzero runner exit is retained as an interrupted failed candidate.
- `red-corrected`: the exact normal candidate records owners `[1,2,3,0]`,
  counts 4/4, role `0x200`, physical riders 1 and four advancing attract
  positions `[97,96,95,94]`. Manual selection, boarding/countdown, visible
  advancing race, changing ranks 2nd through 4th, checkpoint time extension,
  4th result and GAME OVER are captured. The owned process exits cleanly
  without residue. Repeated snapshot 4 is not counted as a new native sample;
  native sample 3 is the last distinct saved payload. Recovery/input
  observations continue in the separate Yellow run.
- `final-abi-off`: video, audio and persisted native files match the retained
  Disabled baseline exactly; state round-trip/replay/corruption checks pass.
- `final-abi-on`: same-configuration state round-trip/replay and incompatible
  Master-state rejection pass. The empty Master content fixture has no audio
  donor archive for this direct ABI invocation, so this check does not claim
  a second sound board is active. Actual RetroArch uses staged donor content.
- `yellow-controls`: the passive observer confirms human color 3 and four
  independently advancing race positions, through native end phase 8. The input
  movie retains ordinary Entry/Call/Start actions and adds separate right/left
  lever intervals. Those original lever values are outside the retained native
  calibration windows and do not qualify steering; the later calibrated Silver
  repeat below supersedes that input claim. The field labeled `yaw` actually samples object offset
  `0x164` and is not used as steering evidence. Disk exhaustion interrupted
  the runner after 17 captures; process cleanup was independently verified.
  This run does not qualify automatic recovery or a clean runner completion.
- `yellow-countdown`: the exact normal build visibly renders Yellow's course
  and 3 / 2 / 1 / GO in captures 10 / 11 / 12 / 13. Captures 16–20 show an
  advancing race. Normal exit, no forced kill and no residual owned process
  pass. `review.json` records the artifact hash and visual observations.
- `yellow-recovery`: the final normal-core run captures the Yellow 4th result
  (10), GAME OVER (11–12), and subsequent moving attract (13–20) in the same
  session. Native Ride remains 3 in all three persisted copies, SRAM CRC is
  valid, exit is clean and no owned process remains. This qualifies automatic
  recovery, not factory title timing or panoramic camera fidelity.
- `countdown-abi-off` / `countdown-abi-on`: state round-trip, deterministic
  replay and corrupt-state rejection pass after the two countdown-loop edits.
  Disabled video, PCM and native saved files match `abi-off` exactly.

The focused countdown and recovery runs omit recording to limit disk usage.
The established runner consequently selects null audio unless `--play-audio` is
provided. The user correctly reported their silent output; this is an isolated
runner configuration, not evidence of silent core synthesis. `yellow-audible`
uses `--play-audio` and recording for a focused audible repeat. Its 88.88-second
recording has PCM peak 4,555 and matches the eight-second Relay race reference
with correlation 0.6427 at recording time 77.4864 seconds. CoreAudio initializes,
the owned process exits normally and no process remains. Normal RetroArch
settings are not modified. Human-observed tests must explicitly use
`--play-audio`; otherwise declare their silent configuration before launching.

Completed test logs are losslessly compressed as `.log.gz` after the disk-full
incident. Original screenshots, movies, audio and reports are retained.

The bounded experimental integration is complete: native three-AI racing,
non-Silver startup, pre-race countdown, ranking/result/GAME OVER, moving attract
recovery and Relay music are qualified. Physical controller feel, every color
and difficulty, and original factory camera/title/single-cabinet fidelity remain
outside this qualification. No such factory behavior is claimed.

## Budget And Deployment Boundary

The earlier prototype stopped at the authorized 15% ceiling. The user authorized
continuation to an absolute 20% ceiling. That checkpoint recorded account usage at 19%;
Sol High remains adequate after locating the concrete native dispatch/count
failures. Reset: 2026-10-17 15:30:48 Europe/Rome.

The installed normal core is the qualified countdown build
`f3d8c8f6dab73304d922d893500dfeba382333869a14de30d71126c371101017`.
Its previous music build
`8ef1a63894c91fb6288f1bd260c1910270b0ab57e7d8ee439bc3194c83fd06eb`
is backed up. `installation.json` records the paths and verified hashes.
No commit, push or development-core recreation is authorized by this work.


## Silver Intro And Input Follow-Up

Evidence: `build-libretro-gpu/validation/power-sled-standalone-input-20261010/`.
The user reported a wrong Silver intro and apparent CPU control after opening
Master from History. The core-level options and existing save all select Silver;
the saved Ride copies are `[0,0,0]`, SRAM container CRC is valid and the retained
calibration/EEPROM match the test baseline. History is not demonstrated as a cause.

Passive isolated RetroArch observation confirms Silver's native human task
`0x3c2d0` and AI task `0x3d1f0` for the other three colors. The original input
movie's racing lever values produced zero native commands because they fall
outside the narrow calibration windows. `silver-valid-controls` changes only
those intervals to measured valid ADC values, obtains separate right/left native
commands and changes Silver's course progression. This establishes native input
acceptance and human task assignment, not physical controller feel. All three
input runs exit cleanly without residual owned processes. No calibration or
user configuration is changed. A passive snapshot attempt retained screenshots
but no states and is not counted as state evidence.

The isolated runner used Software; normal RetroArch uses Auto with Vulkan.
A copied-user-save Auto/Vulkan intro run reproduces the wrong framing despite
Silver identity. The first Auto attempt forced OpenGL through the runner and
failed before gameplay; it is retained and excluded. A private wrapper changes
only that isolated renderer setup and selects the established MoltenVK runtime.

The native four-color roster selects panorama configuration 6. Routine `0x18c30`
therefore offsets Silver's camera as one of four physical displays although
Standalone has only one display. A guarded branch at `0x18c30` to `0x18c40`
selects the existing single-screen path, retaining four competitors, Ride color,
human task, scene timers and audio. The private `single-camera` RetroArch
candidate reaches the intro and selection, exits cleanly without residue, and
the user confirms the Silver intro is correct. The adapter now applies this
instruction only while preparing Standalone; the production XML is unchanged.
Linked sessions and Standalone Disabled keep their previous camera paths.
This qualifies the reported Silver framing fix, not every color or factory
single-cabinet fidelity.

The final normal build passes short ABI Enabled/Disabled state round-trip,
deterministic replay and corruption checks. Disabled image, PCM and native save
hashes match the previous normal build at the same 120-frame baseline. These ABI
checks qualify lifecycle/regression, not race gameplay. The final installed
normal core is `d10e39ad1ed04609c9f3ad06fac26de818d6214b472c0dcdf199acd8d0025de9`;
`silver-intro-installation.json` records backup and verified hashes. The menu
order is verified from actual Core Options V2 registration in `menu-review.json`.
The development core remains absent. Reload Master content to use the new code.

This follow-up uses the subsequently authorized absolute 25% ceiling: account
usage moved from 22% to 24%. Reset remains 2026-10-17 15:30:48 Europe/Rome.


## Superseding Color Camera Review

`Docs/POWER_SLED_COLOR_CAMERA_REVIEW_2026-10-10.md` supersedes the preceding
Silver camera qualification. Controlled four-color comparisons confirm that
the override forces the same framing value for every color. Calling it an
original single-screen mode was unsupported; the previous path assigns distinct
panorama values to Silver / Red / Black / Yellow. The user subsequently approves retaining the uniform intro identified as
Silver for all four colors; the camera item is closed for this accepted scope.
The installed override is unchanged by this verification-only work. The earlier
History-versus-isolated-session difference is still not causally explained.

## Service Exit Follow-Up — 2026-10-11

The user reported that Call on Exit does not return Standalone to the game.
An isolated RetroArch replay reproduces the failure. A passive i960 observer
confirms native Exit at 0x1c4a0 runs at frame 2402, advances phase 15 to 16,
and completes restart through phase 19 at frame 2585. At frame 2592 the game
enters Test again: the outgoing operator command at 0x5293f4 remains 0x1000
through Exit and is received again through the one-node ring.

A detour, only in guarded Master Standalone reconstruction, clears
that command, replays the displaced phase load and resumes native Exit at
0x1c4a8. Native cleanup/restart, NVRAM and input bindings are preserved.
Helper space 0x1f0a80..0x1f0a93 and the displaced instruction/operand are
verified before mutation. ROM archives and linked-mode programs are unchanged.

Evidence and canonical bounded runner:
`build-libretro-gpu/validation/power-sled-service-exit-20261011/run-review.py`.
Baseline and trace runs use isolated options/saves/assets and clean up their
owned processes with exit 0, without forced kill or residual processes.
After the user raised the cap to 29%, the matched candidate replay confirms
native Exit at frame 2402, cleared command at frame 2403, and phase 4 (attract)
by frame 2610. It remains outside Test through the final samples beyond frame
3300; the final screenshot shows the moving attract sequence with four sleds.
The process exits with code 0, without forced termination or residual processes.
See `candidate/result.json`, `candidate/host.log`, `candidate-transitions.json`
and `candidate/host/screenshots/host.png` in the evidence directory.

The normal production core was rebuilt after removing passive instrumentation;
ROM-free input checks pass. Deployment backs up the previous installed binary,
verifies matching build/install SHA-256 and rejects observer markers. Installed
normal core SHA-256:
`79c1d3a0a9f765543e0769718164eafe57a5a029350ed4a588474acc9d0c6894`.
See `installation.json` and `normal-build.log`. The development core remains
absent. Existing loaded RetroArch instances need a content/core reload to use
the correction. Physical pad operation and linked-mode Exit were not qualified
by this one-node replay. Account usage is 28%, within the authorized 29% cap.
No commit or push.

## Startup B_CRX Diagnostic — 2026-10-11

B_CRX denotes Model 2B-CRX CPU boards. In the boot program this particular row
is a network roster count, not a processor or ROM integrity test: routine
0x24e40 reads packet count 0x52940f and scans 0x180-byte records at 0x1a02180.
Headers 0x0200 (Master) and 0x0100 (Relay) set separate presence flags; only
other rider headers increment the B_CRX counter. The jump table at 0x24eb8
accepts 1..4 riders; zero or more than four yields configuration code 8. The
renderer uses string B_CRX at 0x24e00 and ERROR at 0x24e38 (branch 0x250c8).

Standalone retains one physical Master record and locally owns four sleds. Its
existing synthetic local-ownership roster adjustment targets 0x249c0 through
0x24a90; it does not adapt this separate 0x24e40 physical-packet diagnostic.
Thus a loopback containing only Master produces zero rider-board headers and
the native B_CRX ERROR label. This explains the user-observed row without
claiming the emulated CPU board failed its hardware test. Correct reconciliation
of this diagnostic with local ownership remains pending; do not simply replace
the ERROR text or claim that additional physical boards exist.

Analysis used the retained Master program snapshot and the existing local i960
decoder. No production code, ROM, controller mapping or installed core changed.

### B_CRX Correction Completed

User approved correction. The guarded Standalone patch now checks the original
branch word at 0x24e8c (0x08000014), then replaces it with a branch to 0x24e9c
(0x08000010). A Master packet still sets the native Master presence flag; its
real board is now included once in the B_CRX counter, because it also hosts the
human rider in Standalone. Relay headers remain excluded. The scan, range check,
configuration classification and original strings/rendering are retained. Empty
or excessive roster counts can still produce native ERROR. There is no text
substitution, fabricated Slave packet, extra board or change to the four local
ownership records. The other ownership reconciliation remains independent.

This patch is applied only by prepare_power_sled_standalone; with Standalone
Disabled the original linked-game diagnostic is untouched. All original opcode
guards are checked before any mutation, including the additional branch guard.

Evidence: `build-libretro-gpu/validation/power-sled-standalone-bcrx-20261011/`.
The normal candidate core in isolated RetroArch captures **B_CRX ONE**,
**NETWORK OK**, and **THIS IS SILVER RIDE** in host-05.png. Subsequent captures
reach the SEGA presentation and advancing attract course. The single process
exits normally, without forced termination or residual processes. A bounded
actual-core ABI run also passes Save State round-trip, deterministic replay and
corrupt-state rejection. No new complete gameplay or physical-pad qualification
is claimed for this diagnostic-only change.

Normal installed SHA-256: `adf1d97a727a7db8c10143afdaf4a0f8eaf9b77a26592445558bdb81a1e1aab6`,
matching the candidate build; backup retained and dev core absent. Sol High,
forecast 0.5–1.5 points; account meter remains 1% before/after, cap 35%.
Reset: 18 October 2026 07:47 Europe/Rome.

## Native AI Slowdown Near The Finish — 2026-10-11

The reported late-race slowdown has a concrete native-code explanation. Relay
AI callback `0x3d1f0` computes velocity magnitude from fields `+0x20/+0x24/+0x28`.
Once course index `+0x130` exceeds `0x305` (773), code `0x3d278`–`0x3d320`
limits that magnitude to 3.0 game-world units by rescaling all three components,
but only when it already exceeds that limit. This is a native end-of-course
cap, not a new Standalone speed rule or an adjustment based on the human rank.

The callback separately tests position field `+0x138` against `0x347` (839).
Beyond that threshold, `0x3d220`–`0x3d248` fixes three course indices to 842
and clears position increments and velocity. This is consistent with stopping
the sled at the finish, although the exact finish-line geometry has not been
independently mapped. The slowdown and final stop use distinct thresholds and
position fields; 773 is not the final stop.

The entire reviewed speed-clamp block is byte-identical in the Slave program
at `0x3d268` (16 bytes earlier). The Standalone adapter does not patch this AI
callback. The evidence establishes native behavior and plausibly explains the
user's observation; it does not establish design intent or a matched measured
speed curve. No AI modification is made. Private evidence:
`build-libretro-gpu/validation/power-sled-result-stop-20261011/ai-review.json`.

## Optional AI Finish Speed Fix — 2026-10-11

User-approved System option **Power Sled AI Finish Speed Fix (Restart Required)**
is experimental and defaults to Enabled. It is visible only for the Power Sled
family, consistent with the explicit family visibility exception. Enabled
replaces the conditional branch at `0x3d288` with an unconditional branch to
`0x3d324` in reconstructed Master/Relay, and the equivalent `0x3d278` to
`0x3d314` in Slave. This bypasses only the late-course 3.0 speed normalization.
Preceding magnitude calculation and subsequent ordinary AI updates remain.
The separate native stop beyond index 839 is untouched.

Expected instruction words, course threshold and destination instructions
are checked before mutation; an unknown program retains native behavior and
logs a notice. No ROM archive, NVRAM or state format changes. Reload content
for a changed selection; loading an existing state does not reapply ROM patches.
In linked play, use the same selection on each instance owning AI. No change
is applied to other games. The option is also usable outside Standalone.

Private evidence: `build-libretro-gpu/validation/power-sled-finish-review-20261011/`.
The initial enabled-labelled run omitted the per-instance `host` override;
it is excluded from enabled qualification and retained as a runner error.

Matched user-state runtime confirms the option is applied and alters native
AI velocity at the same observed frame/index (Red, frame 9180, index 789):
squared velocity is 10.13805623 with native limit and 12.28108397 with the
bypass. Subsequent ordinary updates mean these post-frame measurements are
not an instantaneous 3.0-clamp measurement. This qualification is Standalone;
linked multi-owner behavior is not newly runtime-qualified. Static guards
and branch targets are verified on all three known program variants.

## Enabled Defaults And Linked Bypass — 2026-10-11

The user enabled the four Power Sled System switches by default and ordered
Standalone before Relay Audio On Master, Relay Commands and AI Finish Speed Fix.
Standalone is applied only to Main with Linked Cabinets Disabled; linked sessions
keep native distributed ownership even when the selector says Enabled. Its
state is checked against changed link settings and requests content reload when
the loaded program adaptation no longer matches the requested configuration.
Explicit saved Disabled selections remain valid; no configuration migration.
