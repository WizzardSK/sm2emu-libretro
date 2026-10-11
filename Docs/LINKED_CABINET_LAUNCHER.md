# Linked Cabinet Launcher

## Default Layout

`--game` is required. There is no default game or cabinet combination; this is
a generic launcher. Four playable instances plus a trailing Relay use four
windows in one horizontal row, with Relay below the first window. All windows
have the same size. Lists without Relay use one row of playable instances.
The existing Power Sled triplet retains its two-above/one-below layout.

```sh
# Example: four participants and Relay, without an assigned Relay gamepad.
python3 scripts/launch-linked-cabinets.py \
  --game stcc:1,stcc:2,stcc:3,stcc:4,stcc:relay:

# The same arrangement for Power Sled.
python3 scripts/launch-linked-cabinets.py \
  --game powsledm:1,powsled:2,powsled:3,powsled:4,powsledr:relay:
```

On macOS, the launcher reads the usable monitor area in logical points,
excluding the menu bar and Dock, and reduces all windows uniformly to fit.
Native 496 × 384 content size is the upper limit; spacing and frame overhead
are included. For the current 1470 × 861 usable area, the five-window layout
uses 327 × 253 content per window. Requested positions and dimensions are recorded in the run manifest.
On macOS, after initialization the launcher also applies the actual outer
window size through the existing process-owned accessibility path and reads
it back. Bounded diagnostic runs additionally read the final frame. Interactive runs
retain the startup measurement and do not recheck windows after the user can
open menus, minimize or close them. `actual_window_frames` contains observed frames;
a dry run only contains requested geometry.

Override the usable area with `--desktop-size 1920x1080`; this also provides
an explicit sizing path on Windows/Linux. The override uses origin (0, 0).
No desktop or global RetroArch configuration is modified.

## Game Selection

```sh
# Repeat the same ROM in two instances.
python3 scripts/launch-linked-cabinets.py --game daytona --cabinets 2

# Select the ROM of each instance in list order.
python3 scripts/launch-linked-cabinets.py --game vonj,vonu

# Select each ROM and its Automatic Network Settings value.
python3 scripts/launch-linked-cabinets.py --game daytona:1,daytona:2

# Start one instance with Automatic Network Settings disabled.
python3 scripts/launch-linked-cabinets.py --game powsledm:0
```

A single name starts one instance; no different program is substituted implicitly.
A comma-separated list defines the instance count and each instance's ROM.
`--cabinets N` repeats a single name N times; with a list it must match its
length. The syntax is `name[:ANS[:GAMEPAD]]`; suffixes never change the ROM filename.
Gamepad IDs are **one-based (1..16)**. The internal RetroArch index remains
zero-based. `--controllers` has been removed.

| Entry | ANS | Gamepad |
| --- | --- | --- |
| `game` | First Unused Positive ID | Automatic In List Order |
| `game:1` | 1 | Automatic In List Order |
| `game:1:2` | 1 | 2 |
| `game::2` | First Unused Positive ID | 2 |
| `game:1:` | 1 | None |
| `game::` | First Unused Positive ID | None |

Only an **explicitly empty third field** disables gamepad assignment. Automatic
IDs reserve all explicit IDs in the whole list before assigning the first free
ID in list order. ANS `0` and `relay` remain supported; `r` is a CLI alias normalized to `relay`; explicit ANS values may
repeat. Assigned gamepad IDs must be distinct; multiple no-gamepad entries are
allowed. A repeated single entry is expanded before automatic IDs are assigned.
The generic `--relay` flag supplies `relay` to the last instance when its ANS
field was omitted; it remains ignored for Power Sled.
One instance (implicit or explicit `--cabinets 1`) launches without RetroArch Netplay and sets Linked
Cabinets to Disabled (local loopback). Omitted ANS receives the first unused
positive ID, including for a single instance; use `:0` to disable ANS explicitly.
Use `:relay` for dedicated Relay programs (specify this explicitly in the game list). The new automatic allocation overrides a resumed session's ANS;
other saved options and SRAM remain retained as before.

The script starts the requested ROMs without checking compatibility between
games, game-specific cabinet limits or required program combinations. The core
and frontend own connection behavior. Launcher success describes clean process
lifecycle; network observations remain separate in its report.

## One ANS Convention

| Saved Value | Generic Games | Power Sled Main / Slave |
| --- | --- | --- |
| `0` | Disabled; Manual NVRAM Selectors Apply | Disabled; Manual Ride ID Applies |
| `1` | Master / Cabinet 1 | Silver |
| `2` | First Slave / Cabinet 2 | Red |
| `3`… | Subsequent Slaves | `3` = Black; `4` = Yellow |
| `relay` | Relay, Where Supported | Fixed Relay ROM Only |

The dedicated Power Sled and Virtual On Relay programs offer only `relay`.
Power Sled Relay has no automatic color override, but its Service Menu and
manual NVRAM Settings expose Silver / Red / Black / Yellow. Its color does not
change its Relay role. Virtual On Relay retains native No Link. Menu labels
remain descriptive. Old development ANS names are not accepted or migrated.

## Start Power Sled

### macOS Controller Assignment

The third `--game` field identifies one alphabetically sorted list of physical HID pad
names, captured before launching any instance. The runner prints each chosen
name and reserves it exclusively for that instance's Port 1, using RetroArch's
HID driver. Other Libretro ports remain disabled. Virtual compatibility devices
without a hardware transport are excluded. If physical pads have identical
names, give them distinct names in macOS Bluetooth settings before launching.
The names are retained in the run manifest. Configuration changes belong only
to the isolated instances.

With the three pads connected on 2026-10-11, this order is:

| Gamepad ID | Physical Pad |
| --- | --- |
| 1 | DualSense Wireless Controller (Purple) |
| 2 | Xbox Wireless Controller (Black) |
| 3 | Xbox Wireless Controller (White) |

Raw per-process SDL/HID indices can enumerate the same physical pad at different
positions. Numeric indices alone previously failed to isolate cabinets; the
new named reservations prevent that dependence. Windows/Linux retain their
frontend device-index convention. Actual stick travel and manual menu operation
are separate from checking successful named reservations in RetroArch logs.

### Launch

```sh
python3 scripts/launch-linked-cabinets.py \
  --game powsledm:1,powsled:2,powsledr:relay
```

| Position | ROM Program | Controller Index | ANS |
| --- | --- | --- | --- |
| Top Left | `powsledm.zip` — Main | 0 | `1` — Silver |
| Top Right | `powsled.zip` — Slave | 1 | `2` — Red |
| Bottom Left | `powsledr.zip` — Relay | 2 | `relay` |

The three listed Power Sled programs get the Main / Slave above Relay layout.
The fresh-session default is Main Silver / Slave Red. The reconstructed Main
publishes its color separately from its Master role, so it can supply the Silver
ride. Both Silver / Red and Red / Silver qualify in bounded linked races. ANS
values retain their color meanings and explicit values are never replaced.
`--relay` is ignored for Power Sled. Roles are selected by the ROM, while ANS on Main and Slave
selects the color. The launcher defaults to this three-ROM list without suffixes.
To retain colors selected through the GUI on subsequent launches, omit suffixes:

```sh
python3 scripts/launch-linked-cabinets.py --game powsledm,powsled,powsledr
```

A bare `--game powsled` starts one instance of that ROM; no other program is
substituted and no compatibility check is performed. Controller indices follow
the declared list with transport order Main / Slave / Relay. Window
positions remain fixed by the Power Sled program role.

Two riders can use Main and Slave without Relay:

```sh
python3 scripts/launch-linked-cabinets.py \
  --game powsledm:1,powsled:2
```

Linked Cabinets supports 2–5 total instances. Four riders can use one Main and three Slaves; an optional final Relay makes
five total instances. Use distinct rider colors; Relay's manual color is not
a rider identity. The script passes the list through without topology checks:

Relay is optional for racing, but its separate soundtrack is only produced
while that instance is running. A pair retains rider effects without the Relay
audio; the core does not move that sound program into Main automatically. See
`Docs/POWER_SLED_MUSIC_ROUTING_2026-10-10.md` for the recorded comparison.

```sh
python3 scripts/launch-linked-cabinets.py \
  --game powsledm:1,powsled:2,powsled:3,powsled:4
```

Append `,powsledr:relay` to include Relay with the next automatic gamepad,
or `,powsledr:relay:` to include it without a gamepad. More than
three windows use the generic two-column layout; panoramic physical alignment
remains a separate review item.

## Optional Master Archive

`powsledm.zip` may be absent or incomplete. The loader prefers valid chips in
an existing Master archive, then reads program/graphics from sibling
`powsledr.zip` and sound from sibling `powsled.zip`. Required chip CRCs still
apply. Master patches, set identity and its own save files remain `powsledm`.

For an absent Master archive, the runner writes a valid empty ZIP content entry
inside the owned run's `content/` directory and symlinks sibling archives there.
It writes nothing into the ROM collection. The GUI can also load a deliberately
created empty `powsledm.zip` placed alongside the donors; loading
`powsledr.zip` itself continues to select Relay. Missing ordinary game archives
still fail. Relay ROM data is needed even when no Relay instance is launched.

## Generic Relay Examples

```sh
python3 scripts/launch-linked-cabinets.py --game stcc:1,stcc:2,stcc:relay
python3 scripts/launch-linked-cabinets.py --game stcc --cabinets 3 --relay
python3 scripts/launch-linked-cabinets.py --game von:1,von:2,vonr:relay
```

`--relay` assigns Relay to the final instance by default without changing the
instance count. Counts include Relay. The explicit Virtual On example includes its dedicated `vonr` program;
this is a recommended working combination, not a script validation rule.
NVRAM Settings is enabled for launcher sessions so ANS applies.

## Controllers And Riders

Each instance maps its assigned physical pad to local Port 1. Other local
ports are disabled to prevent another cabinet's pad controlling that instance.
Duplicate assigned gamepad IDs are rejected. An explicitly empty gamepad
field keeps all joypad indices within 0..15, clears device reservations,
disables gamepad autoconfiguration and sets all Libretro player ports to None.
Those instances receive no player controls; RetroArch keyboard menu/hotkeys
remain available. It does not use index `-1` or a `null` joypad driver. SDL background joystick events are
enabled for these child processes, and inactive windows keep running. Keyboard
input follows the focused window. Physical/background delivery still requires
connected-controller qualification; assigning an index alone does not prove it.

Power Sled P1/P2 are riders within one cabinet; P2 is not the Slave instance.
The core supports separate P2 Entry/Call and handlebars on Port 2. Existing
P2 Entry/Call aliases on Port 1 remain. The one-pad-per-window launcher disables
Port 2. There is no automated Test/Service or gameplay input sequence.

## Paths, Session Persistence And Exit

Defaults use the installed `sm2_libretro.dylib`, existing local RetroArch Nightly,
project system assets and the documented external Model 2 ROM directory. Path
arguments support other installations without installing dependencies or
including ROMs. The launcher reuses the established RetroArch network runner.

Launcher instances use `host`, `client1` and `_relay` for the Power Sled
Main / Slave / Relay order. A final Relay in a larger group also uses `_relay`.
Each contains independent configurations, Core
Options, SRAM and Save States. Old sessions are resumed by matching the ROM
program in their manifest, preserving old files and avoiding a Slave/Relay mix-up.

Sessions live under `build-libretro-gpu/linked-cabinets/`; use `--session PATH`
for a separate one. Each launch creates a numbered run, retaining older files
and copying the last successful run's available SRAM and Core Options.
If that launcher run did not produce an SRM for a program, its next instance
starts without an imported save and follows the normal automatic initial setup.
Existing saved files are preserved; acquisition runners retain their strict
baseline requirement. Topology and NVRAM
Settings are reapplied. Explicit `:ANS` values override saved selections;
omitted Power Sled suffixes retain valid saved colors in multi-instance sessions.
Other multi-instance games regenerate native role presets when suffixes are
omitted. Single-instance sessions default to ANS `0`, except dedicated Relay
programs. No old ANS aliases are translated.

Close one cabinet or press Ctrl+C to stop the group. The runner sends QUIT,
waits for owned processes and records forced cleanup. Global configuration,
normal saves and unrelated processes remain outside the session. Its temporary
macOS application-state preference is restored.

`--dry-run` prepares files only. `--seconds N` runs a bounded session;
`--capture-screenshots` captures each frontend image. Configuration, commands,
PIDs, core hash, logs and final link/lifecycle results are retained per run.

## Qualification

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
