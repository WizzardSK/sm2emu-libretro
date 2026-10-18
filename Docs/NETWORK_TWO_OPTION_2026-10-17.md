# Two-Option Network Integration — 2026-10-17

## Scope And References

Implements Framework 0.1.23 F05/F14 and the approved single-sheet Network Review.
The user authorized implementation without a consumption cap. No commit, push,
release, dependency installation or changes to another project's code are included.
Existing unrelated changes in this working tree are preserved.

References: `../libretro-core-framework/FRAMEWORK.md`, `REFERENCE_SOURCES.md`,
`TGPULSE_NETWORK_ADOPTION_REVIEW_2026-10-17.md` and
`outputs/01a13152-dbfa-7e30-bc9d-0477abc2cccc/Framework_Network_Review.xlsx`.
Prototypes are excluded from the new runtime matrix; Royal Ascot II is excluded
from operational qualification. GTX uses its separately validated native mapping;
its acquisition campaign is not repeated.

## Current Interface

Exactly two controls are shown for every game:

| Control | Values / Default |
| --- | --- |
| Linked Cabinets | -1 Disabled (default), accepting 0/1 aliases; 2..n total including Relay |
| Auto Network Role Settings | -1 Disabled/manual; 0 native Standalone/No Link (ordinary default); positive native IDs; r special native role with l/s aliases |

Unsupported games show Not Supported on both controls. No Network Board option
is registered. Existing per-game keys remain; old network words and semantics
are not migrated. Invalid values fall back with a notification.

Power Sled playable programs default to 1 Silver, with 2 Red, 3 Black and
4 Yellow; their Master/Slave identity follows the program. Dedicated Power Sled
and Virtual On Relay programs expose only r. The later standalone board review
supersedes the optional-board sentence: the board remains fitted in local
loopback when linking is disabled, including for the reviewed Dynamite Baseball,
Pilot Kids, Rail Chase 2 and Zero Gunner families. See
[Standalone Communication Board Review](COMM_BOARD_STANDALONE_REVIEW_2026-10-18.md).
Disabling topology never silently converts the selected native
role to No Link. Some independent role/topology combinations therefore cannot
operate; this does not change the selected role.

Virtual On requires its local communication board even when its native role is
No Link. A board-disconnected boot with a fresh SRAM can display the attract
sequence, but a delayed Coin/Start replay still yields a black picture when a
match starts. The same replay with the board present proceeds with picture and
audio; no external peer is required. The original user SRAM and a fresh SRAM
have identical operator settings and EEPROM. Their only backup-RAM differences
are ten bytes in changing counters and elapsed time (including mirrored values
at 0x38/0x244), not a saved network role. The fresh no-board run itself advances
0x38 from 0 to 6 as the repeated start inputs are attempted, then ends on the
black picture. Clearing 0x38 in a disposable copy restores the attract
sequence but does not establish playable offline operation.
Thus no SRAM migration or deletion is needed: keeping the local board fitted
is the machine configuration required for matches, while Linked Cabinets
Disabled still prevents an external link. Isolated RetroArch Software and
Vulkan runs using the original user SRAM reached the match with the local board
present. Fast Forward was not needed to reproduce the failure. Evidence is in
`build-libretro-gpu/validation/von-black-gameplay-20261018/`.
The no-board comparison used the same local source with only Virtual On's
`local_board_required` predicate temporarily disabled in a separate test
binary. That predicate was restored afterward; the installed normal core and
the final build both retain the board in local mode.

ANRS applies even with NVRAM Settings disabled. It hides and synchronizes only
its managed role/identity fields. When disabled, manual NVRAM Settings resumes
with the last applied values; stale manual selections are not restored. Native
integrity and unrelated settings remain governed by the existing NVRAM adapter.

Effective topology/role/operator changes coalesce into one reset on return to
the game. Unchanged selections and equivalent aliases do not reset. Machine
reconfiguration preserves the frontend lobby, callbacks and connected clients;
it neither unloads content nor invokes Netpacket stop/start.

## Names And Comments

Framework_Menu_Review.xlsx was read directly, including effective names,
comments, submenu and core applicability. Its Orders 034/035 still describe
old ANS/offline semantics, and 222 the former Network Board. F14 explicitly
supersedes those networking rows. Their discrepancy has been reported to the
Framework chat; the shared workbook was not edited from this project.

The GUI name is Auto Network Role Settings, matching current TGPulse (no acronym
suffix). All 32 ANRS definitions use its ROLE_HELP verbatim. All 32 supported
Linked Cabinets definitions use one shared help text covering board presence,
local loopback, native-role independence and return-to-game application.
Program-specific topology and cabinet limits remain in this document and in
the selectable values, not in per-game help suffixes.
Both registration APIs derive names/choices from the same definitions. Legacy
registration places the actual default first because that API has no separate
default field. Unrelated approved workbook wording is preserved.

Audit evidence: `wording-audit.json` records current TGPulse reference path/hash,
all 64 network definitions, comments and unsupported placeholders. It is a
registration comparison, separately corroborated by the visible RetroArch menu.
That earlier audit recorded each comment but did not assert that supported
Linked Cabinets comments were identical. Per-game help suffixes therefore
escaped the harmonization review. The later
`build-libretro-gpu/validation/linked-help-20261017/audit.json` checks the
actual 452-option registration: 32 supported Linked Cabinets definitions with
one help text, 32 Auto Network Role Settings definitions with one help text,
and no raw ROM-set identifiers in any help text. The ROM-free Save RAM check
also asserts Linked Cabinets help equality across all supported games.

## Native Mapping And Architecture

The reviewed 32 set registrations cover Daytona (including independent GTX),
Indy 500, STCC, Sega Rally, Manx TT, Motor Raid, Wave Runner, Ski Super G,
Super GT 24h, Over Rev, Virtual On and Power Sled programs/clones.
Motor Raid exposes up to five total instances on the theoretical reviewed basis;
its native Live ID stays within 1–4. The five-instance combination is not
claimed as gameplay-qualified.

Frontend-neutral machine changes are limited to configurable M2Comm presence
(default present for standalone callers) and access to mutable program ROM.
Power Sled keeps guarded linked/standalone program variants in adapter-owned
storage and switches them between frames before topology reset. No CPU/machine
code calls Libretro. Presence adds no serialized field, and existing Save State
restrictions/format are retained.

All option readers retain GET_VARIABLE_UPDATE before consuming GET_VARIABLE.
The display callback retains pending changes while paused; Resume consumes them
once. Frontend setters are published outside machine locks and tolerate a
synchronous re-entrant display callback. Native setup precedes the first frame.

## Leftover Removal

- Replaced old network parser/default choices and NVRAM Settings gating.
- Removed forced offline-role conversion and old launcher role/color preservation.
- Updated active launcher/runner, smoke, Power Sled and Save State commands to
  canonical network values. --controllers remains removed; raw relay is not r.
- Sample acquisition explicitly disables automation (-1), so new ANRS defaults
  cannot compete with native Service Menu acquisition. Dedicated Relay keeps r.
  Historical campaign manifests, sample data and pinned evidence are unchanged.
- Rewrote the active launcher guide, corrected LIBRETRO.md/LIBRETRO_DESIGN.md
  and current roadmap summaries. Dated reports are retained with supersession
  notices rather than rewritten as if they had tested the current contract.

## Verification

Evidence root (ignored, local):
`build-libretro-gpu/validation/network-two-option-20261017/`.

| Scope | Evidence / Result |
| --- | --- |
| Old-core regression | failing-before.log: paused difficulty edit is lost with consuming reads |
| Corrected F05 | Modern and legacy ABI runs retain repeated paused edits and apply exactly one reset |
| F14 native matrix | 14 playable families/programs, including GTX and both playable Power Sled programs; NVRAM OFF authority, hidden-value synchronization, handover, combined reset, unchanged aliases, explicit Restart, retained lobby callbacks and fresh Save RAM reload pass |
| Registration | All 32 pairs: labels/defaults; unsupported pair visibility; legacy default order; no Network Board |
| Transport | Netpacket C++ checks cover open offline lobby, existing/new clients, reset, staggered roster setup and topology-count changes without a new frontend start |
| Native options / Save RAM | Existing C++ Save RAM checks pass; reviewed native mappings and integrity checks retained |
| Launcher | 21 checks pass; modified Python scripts compile |
| Default boot | Twelve ordinary families run 900 frames through the core ABI without requesting shutdown; this is not gameplay/input qualification |
| Build | macOS arm64 core and headless target build; only existing duplicate-library linker warnings |
| Actual RetroArch | Nightly 1.22.2: visible System pair and native choices; NVRAM Settings OFF; paused Single → Car 1 (Master) applies on Resume, native boot displays MASTER / CAR NUMBER 1. Final wording also visibly inspected |
| Actual linked frontend | Two Daytona instances form 2/2 rosters and native board alive events for IDs 1/2; attract shows UP TO 2 RACERS WANTED. Both exit 0, no forced kill or residual processes |

The initial fitted-window attempt failed because macOS reported a 66×20 outer
frame. A CUA selection then opened an unconfigured app instance; it did not
respond to TERM and that sole owned PID was force-closed. The subsequent
isolated runner without fitting, menu checks and two-instance run succeed.
These failures are retained and not presented as core failures or successful
UI acceptance. The final isolated menu process exits normally.

Limits: reset counts, re-entry and changing-total/staggered-client preservation
are specifically ABI/transport evidence. Real frontend evidence covers paused
role application, final visible wording and the linked baseline; it does not
establish every interactive active-lobby reconfiguration, maximum theoretical
counts, synchronized racing, physical controllers or other operating systems.
No prior closed gameplay qualification is reopened by this integration.

## Local Delivery

Only the configured normal core is updated:
`/Users/andrea/Library/Application Support/RetroArch/cores/sm2_libretro.dylib`.

SHA-256: `2b2c2655c24cf2bb1248ed2cf3660229260f7fd06e9dd22de779a057ecbc2858`.
Previous installed artifact is backed up under `before/installed-sm2_libretro.dylib`;
its hash is `c3e1fcfe0df92e53a3a25cd6882fa8b522706ed679e8bc586792896b4ee9d9ed`.
Source and destination hashes match. The dev core remains absent. No support
file deployment, version change, commit or push is included.
