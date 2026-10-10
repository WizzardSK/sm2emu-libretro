# Linked Cabinet Launcher

## Game Selection

```sh
# Repeat the same ROM in every instance (two by default).
python3 scripts/launch-linked-cabinets.py --game daytona

# Select the ROM of each instance in list order.
python3 scripts/launch-linked-cabinets.py --game vonj,vonu

# Select each ROM and its Automatic Network Settings value.
python3 scripts/launch-linked-cabinets.py --game daytona:1,daytona:2
```

A single name repeats that ROM; no different program is substituted implicitly.
A comma-separated list defines the instance count and each instance's ROM.
`--cabinets N` sets the total for a single name; with a list it must match its
length. The suffix after `:` sets ANS and never changes the ROM filename.
Without a suffix, the reviewed topology presets are generated automatically;
Power Sled can retain an existing session's color selection.

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
| `3`… | Subsequent Slaves | `3` = Black |
| `relay` | Relay, Where Supported | Fixed Relay ROM Only |

The dedicated Power Sled and Virtual On Relay programs offer only `relay`.
Power Sled Relay has no color override; Virtual On Relay retains native
No Link. Menu labels remain descriptive. Old development ANS names are not
accepted or migrated. Existing NVRAM option keys/values are unchanged.

## Start Power Sled

```sh
python3 scripts/launch-linked-cabinets.py \
  --game powsledm:2,powsled:1,powsledr:relay --controllers 0,1,2
```

| Position | ROM Program | Controller Index | ANS |
| --- | --- | --- | --- |
| Top Left | `powsledm.zip` — Main | 0 | `2` — Red |
| Top Right | `powsled.zip` — Slave | 1 | `1` — Silver |
| Bottom Left | `powsledr.zip` — Relay | 2 | `relay` |

The three listed Power Sled programs get the Main / Slave above Relay layout.
The fresh-session default is Main Red / Slave Silver: this tested three-program
topology requires a Silver Slave. Main Silver / Slave Red passes the communication
checks but fails the game's Ride check; the patched Main does not provide a Silver
ride merely because its operator setting says Silver. ANS values retain their
color meanings and explicit values are never silently replaced.
`--relay` is ignored for Power Sled. Roles are selected by the ROM, while ANS on Main and Slave
selects the color. The launcher defaults to this three-ROM list without suffixes.
To retain colors selected through the GUI on subsequent launches, omit suffixes:

```sh
python3 scripts/launch-linked-cabinets.py --game powsledm,powsled,powsledr
```

A bare `--game powsled` starts three copies of that ROM; no other program is
substituted and no compatibility check is performed. Controller indices follow
the declared list with transport order Main / Slave / Relay. Window
positions remain fixed by the Power Sled program role.

## Generic Relay Examples

```sh
python3 scripts/launch-linked-cabinets.py --game stcc:1,stcc:2,stcc:relay
python3 scripts/launch-linked-cabinets.py --game stcc --relay --controllers 0,1,2
python3 scripts/launch-linked-cabinets.py --game von:1,von:2,vonr:relay
```

`--relay` chooses three instances for a single name unless `--cabinets` is
explicit, and assigns Relay to the final instance by default. Counts include
it. The explicit Virtual On example includes its dedicated `vonr` program;
this is a recommended working combination, not a script validation rule.
NVRAM Settings is enabled for launcher sessions so ANS applies.

## Controllers And Riders

Each instance maps its assigned physical pad to local Port 1. Other local
ports are disabled to prevent another cabinet's pad controlling that instance.
Duplicate controller indices are rejected. SDL background joystick events are
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
Main / Slave / Relay order. Each contains independent configurations, Core
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
omitted Power Sled suffixes retain valid saved colors. Other games regenerate
native role presets when suffixes are omitted. No old ANS aliases are translated.

Close one cabinet or press Ctrl+C to stop the group. The runner sends QUIT,
waits for owned processes and records forced cleanup. Global configuration,
normal saves and unrelated processes remain outside the session. Its temporary
macOS application-state preference is restored.

`--dry-run` prepares files only. `--seconds N` runs a bounded session;
`--capture-screenshots` captures each frontend image. Configuration, commands,
PIDs, core hash, logs and final link/lifecycle results are retained per run.

## Qualification

See `Docs/ANS_CONVENTION_REVIEW_2026-10-09.md` for the current convention and
CLI evidence, and `Docs/POWER_SLED_LAUNCHER_REVIEW_2026-10-09.md` for the earlier
launcher qualification. Native links and clean exits do not certify playable
Power Sled racing, motion hardware or audio correctness.
