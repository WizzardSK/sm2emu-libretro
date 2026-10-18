# Linked Cabinet Launcher

The generic launcher uses the established isolated RetroArch runner. It does
not check game compatibility or infer another ROM from a role number.
`--game` is required; there is no default game or topology.

## Game And Controller Syntax

Use `name[:ANRS[:GAMEPAD]]`, separated by commas. A single name starts one
instance; `--cabinets N` repeats it N times. With a list, N must match its length.

| Entry | ANRS | Gamepad |
| --- | --- | --- |
| `game` | First Unused Positive ID | Automatic In List Order |
| `game:1` | 1 | Automatic In List Order |
| `game:1:2` | 1 | 2 |
| `game::2` | First Unused Positive ID | 2 |
| `game:1:` | 1 | None |
| `game::` | First Unused Positive ID | None |

Gamepad IDs are one-based (1–16). Only an explicitly empty third field assigns
no gamepad. All explicit positive IDs are reserved before missing IDs are
allocated. Assigned pads must be distinct. Dedicated `powsledr` / `vonr`
programs default to `r` when their ANRS field is omitted. The removed
`--controllers` argument is not supported.

## Current Network Convention

- Linked Cabinets: `-1` Disabled; `0` / `1` are equivalent aliases. Two or more
  instances use their total count, including Relay.
- Auto Network Role Settings (ANRS): `-1` Disabled/manual, `0` native
  Standalone/No Link, positive IDs for native cabinet roles, `r` for a special
  Relay/Live/Satellite role. `l` and `s` normalize to `r`.
- Power Sled Main/Slave: `1` Silver, `2` Red, `3` Black, `4` Yellow; the program
  fixes Master/Slave identity. Dedicated Relay programs offer only `r`.
- ANRS works with NVRAM Settings disabled. Topology does not convert a selected
  native Master or Slave role into No Link. A disabled link disconnects optional
  boards; Power Sled and Virtual On Relay retain their required board in loopback.
- Old raw words `relay` and `disabled` are not current network values. Invalid
  core values fall back with a notification; the CLI rejects invalid tokens.

The launcher allocates positive IDs when omitted, including for a single
instance. This is a launcher policy, distinct from the core's native No Link
(default `0`) for ordinary games. Use `:-1` for manual native settings or `:0`
for a supported native Standalone/No Link mode. A one-instance launch disables
frontend Netplay and writes Linked Cabinets `-1`.

## Examples

```sh
# Master Silver, Slave Red, Relay; pads allocated in order.
python3 scripts/launch-linked-cabinets.py --game powsledm:1,powsled:2,powsledr:r

# Four riders across, equally sized Relay underneath; only Master has a pad.
python3 scripts/launch-linked-cabinets.py \
  --game powsledm:1:1,powsled:2:,powsled:3:,powsled:4:,powsledr:r:

# One instance with manual native settings, no gamepad.
python3 scripts/launch-linked-cabinets.py --game daytona:-1: --cabinets 1

# Generic native roles, including a dedicated Relay program.
python3 scripts/launch-linked-cabinets.py --game von:1,von:2,vonr:r
```

The optional `--relay` flag supplies `r` to the last instance if omitted; it
never adds an instance and is ignored for Power Sled. List Power Sled programs
explicitly. Its Main/Slave/Relay triplet uses Main and Slave above Relay; larger
groups use the generic layout. Four participants plus Relay use four windows
across with Relay below. Window sizes fit the usable desktop dynamically;
`--desktop-size WIDTHxHEIGHT` overrides its detection. Actual owned window frames
are resized and read back after frontend startup.

Power Sled Relay Audio On Master is independent of running a Relay instance.
Disable it on Master when the separate Relay should supply the soundtrack.
Standalone Mode takes effect only with Linked Cabinets disabled.

## Controllers And Isolation

On macOS, pad IDs refer to the alphabetically sorted physical HID device names
captured before launching. Names and assignments are printed and retained in
the run manifest. Identical names need distinct macOS device names for reliable
reservations. Windows/Linux use frontend device indices. Each assigned pad owns
local Port 1; other ports are disabled. An unassigned instance disables all
player ports and autoconfiguration while retaining valid internal indices.
Keyboard menu/hotkey input follows focus. Physical input behavior requires
controller observation; process startup alone does not qualify it.

Power Sled P1/P2 are two riders in one cabinet; P2 is not a network Slave.
The one-pad-per-window launcher disables Port 2. No Service Menu or gameplay
input sequence is injected.

## Files And Persistence

Default sessions live under `build-libretro-gpu/linked-cabinets/<name>-<count>/`.
Use `--session PATH` for another owned session. Each launch creates
`runs/NNNN/cabinets/`, containing independent `host`, `clientN` and final
`_relay` directories. Each has its own configuration, Core Options, SRAM and
Save States. Logs, commands, PIDs, hashes and results remain in that run.

The next launch copies available SRAM and Core Options from the last successful
run, matching the program identity. Resolved ANRS IDs and topology are reapplied;
other saved Core Options, including Relay Audio On Master, persist. Omitting
ANRS does not preserve a previous GUI role/color: it requests automatic ID
allocation. Normal native-window exits can recover observed unsaved core values
from the log, with backups and later frontend saves taking precedence.

Close a cabinet or press Ctrl+C to stop the owned group. Global configuration,
normal saves and unrelated processes are untouched. `--dry-run` prepares files;
`--seconds N` runs a bounded session. `--capture-screenshots` captures each image.
A successful process-lifecycle result is separate from link or gameplay proof.

## Optional Master Archive

`powsledm.zip` may be absent or incomplete: the loader tries valid Master chips,
then sibling `powsledr.zip` for program/graphics and `powsled.zip` for rider sound.
Required CRCs still apply. The launcher creates an empty content ZIP and sibling
symlinks inside its owned run when needed, without modifying the ROM collection.
The Master keeps its own identity, patches and saves. Loading `powsledr.zip`
itself selects Relay. Relay ROM data is required even without a Relay instance.

Current implementation evidence: [Two-Option Network Integration](NETWORK_TWO_OPTION_2026-10-17.md).

## Historical Qualification

The records below describe the versions tested on their stated dates. Their
old ANS tokens and defaults are superseded by the current convention above;
do not use historical commands as current instructions.

### Original Qualification

The 2026-10-10 single-instance extension passes ten focused launcher checks,
including implicit/explicit count 1, ANS 0, explicit ANS overrides and unchanged
multi-instance mappings. An installed-core RetroArch launch with
`--game powsledm:0` creates one process, writes Linked Cabinets
Disabled / ANS 0, disables frontend Netplay and exits normally without residual
processes. Evidence: `build-libretro-gpu/validation/single-cabinet-launcher-20261010/session/runs/0002/cabinets/result.json`.
The first attempt failed macOS window positioning; the retained retry succeeds.
This checks launcher lifecycle and configuration, not standalone racing or audio.
Core binary and global RetroArch files are unchanged.

See `Docs/ANS_CONVENTION_REVIEW_2026-10-09.md` for the current convention and
CLI evidence, and `Docs/POWER_SLED_LAUNCHER_REVIEW_2026-10-09.md` for the earlier
launcher qualification. Native links and clean exits do not certify playable
Power Sled racing, motion hardware or audio correctness.

## Power Sled Master + Relay Pair (2026-10-11)

A Silver Master can run with only a Relay, without enabling Standalone Mode:

```sh
python3 scripts/launch-linked-cabinets.py --game powsledm:1,powsledr:relay
```

Both instances use Linked Cabinets = 2. Leave Power Sled Standalone Mode and
Power Sled Relay Audio on Master Disabled; the separate Relay supplies music.
Wait for native startup before Coin / Start. Master Silver is the qualified
configuration; no Silver Slave is present to satisfy another Master color.

The 2026-10-11 matched intro review corrected the previously black Main attract
screen for this pair: the single-rider program now supplies the fourth local
record required by the native intro's visual constructor. Normal-core intro and
bounded race-entry captures pass; full-course behavior remains unqualified.
This does not enable Standalone automatically. See
`POWER_SLED_POST_RACE_AND_MASTER_RELAY_2026-10-11.md` for the record/role boundary.

## Inline Gamepad Syntax — 2026-10-11

The expanded parser and no-gamepad configuration pass 14 ROM-free launcher
checks. Two end-to-end dry runs verify all-unassigned and mixed explicit/automatic
assignments, first-free ANS allocation, physical name reservations and Relay-last
ordering in generated commands and configs. RetroArch is not launched in these
checks; they do not claim new physical-controller gameplay qualification.

```sh
# Automatic pads 1 and 2; Relay has no assigned pad.
python3 scripts/launch-linked-cabinets.py \
  --game powsledm:1,powsled:2,powsledr:relay:

# Explicit pads 1, 2 and 3.
python3 scripts/launch-linked-cabinets.py \
  --game powsledm:1:1,powsled:2:2,powsledr:relay:3
```

The four-rider/Relay layout extension passes 15 launcher checks and a five-instance
configuration dry run: four equal-height positions above a left-aligned Relay,
identical window sizes, Relay-last transport order and distinct instance folders.
No new gameplay qualification is claimed.

Automatic desktop sizing passes 16 launcher checks, including several desktop
sizes and instance counts, and an actual-monitor configuration dry run. All
five equal-sized frames remain inside the reported usable monitor area. This
verifies generated geometry/configuration, not the eventual native window frame
on every operating system.

The no-default-game correction passes 17 launcher checks, including rejection
of a missing --game argument, plus a generic STCC five-instance dry run with
four windows across and Relay underneath.

## No-Gamepad Startup Crash — 2026-10-12

The user-reported five-instance run failed in the first unassigned Slave. The
macOS report `RetroArch-2026-10-12-000534.ips` locates the fault in
`cb_input_autoconfigure_connect`, before window positioning. The launcher had
written joypad index -1. That out-of-range mapping is removed: retain a valid
0..15 permutation and disable Libretro player ports for unassigned instances.
A tested null-joypad-driver candidate was rejected because this frontend
fell back to SDL; it would not guarantee absent player input.

`r` is accepted only as an ANS CLI alias and normalized before game planning
and Core Option writing. The stored core value remains `relay`.

Verification: 18 ROM-free checks pass. A fresh actual RetroArch run repeats the
reported five-instance list (Master gamepad 1, three unassigned Slaves, unassigned
Relay using :r:). All five windows start and every process exits normally without
forced termination or residual processes. Stored Relay ANS is canonical relay.
Evidence: `build-libretro-gpu/validation/launcher-relay-alias-no-pad-20261012/`; lifecycle proof
does not qualify linked gameplay or physical-input isolation by observation.

## Actual Window Sizing Correction — 2026-10-12

The user's screenshot exposed overlapping windows despite correct requested
geometry. RetroArch startup logs report 512 × 384 video initialization, overriding
the smaller configuration dimensions. Prior dry-run checks established requested
config values only, and prior lifecycle checks did not establish actual sizes.
The launcher now sets outer frames after startup and verifies actual dimensions
and position, then checks stability without resizing again in bounded diagnostic runs.
Only windows owned by the newly launched processes are changed. The fixed
16/28-point decoration allowances remain conservative layout estimates, not
a measurement of the content rectangle.

Verification: 19 launcher checks pass, including rejection of a mismatched
actual frame and a read-only stability check. Actual isolated five-window run
on the 1470 × 861 usable desktop observes five 343 × 281 outer frames at the
requested positions, four above and Relay below, all inside the usable area.
The post-settle read matches, all processes exit normally, no residuals remain.
Evidence: `build-libretro-gpu/validation/launcher-window-frame-fix-20261012/runtime2/`.
The initial attempt failed window positioning before resize; retry uses a
separate network port and leaves pre-existing user instances untouched.

## Missing Accessibility Values In Interactive Play — 2026-10-12

User run `powsledm-5/runs/0003` qualified all five initial frames, roster and
native links, but the redundant pre-interactive read raised ValueError on macOS
`missing value`. Cleanup exited all five processes normally, yet the exception
marked the run failed and prevented it from becoming the next saved baseline.
The exact UI event causing the missing value was not captured.

Interactive runs now keep the verified startup frames and skip that redundant
read once the user can interact with windows. Passive bounded reads retry
transient missing values and record only available frames; a disappeared window
is not a geometry failure. Initial resize/read-back remains required, with
bounded retries and a clear diagnostic if it cannot be established. Genuine
size mismatches remain errors in bounded diagnostics. Twenty launcher checks
pass, including missing/closed-window passive reads and required startup reads.
No historical result or user configuration was rewritten.

## Core Option Persistence On Native Window Close — 2026-10-12

User run 0004 actually queried Relay Audio Disabled after the Quick Menu change,
but its native macOS window close ended with `NS stopping draw observer` without
a final Core Options save. The per-instance file still said Enabled, so the
next launcher correctly copied a stale file. No CLI audio override caused this.

For interactive runs, after a normal exit (code 0, no forced kill), the runner
recovers changed registered `sm2_` values actually observed in GET_VARIABLE
messages after the last frontend save. It preserves unobserved options and
unknown keys, and a later frontend save always takes precedence. This is a
bounded fallback for the frontend's native close path, not a full snapshot of
unqueried in-memory options. Original per-instance files are backed up as
`core-options-before-exit-recovery.cfg`; changed values are reported in
`recovered_core_options`. Global configuration remains untouched.

Twenty-one checks pass. Replaying the user's actual 0004 log against a private
copy recovers only `sm2_power_sled_relay_audio = disabled`; an isolated next-launch
dry run retains Disabled in both options.json and the actual Core Options file.
The latest successful user baseline 0005 was backed up and its Master audio
preference restored to Disabled as requested. Historical results are unchanged.
Evidence: `build-libretro-gpu/validation/launcher-core-option-persistence-20261012/`.
