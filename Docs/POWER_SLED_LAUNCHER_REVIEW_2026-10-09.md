# Power Sled ANS And Linked Launcher Review

This records the initial launcher qualification. The later unified ANS values
and game-list CLI supersede its initial Red/Silver defaults and implicit Power
Sled selection. See `Docs/ANS_CONVENTION_REVIEW_2026-10-09.md` and the current
`Docs/LINKED_CABINET_LAUNCHER.md` for the active contract.

## Implemented Scope

- Main and Slave Automatic Network Settings selects Silver, Red, Black or
  Disabled. It manages only the reviewed Ride field; the loaded ROM retains
  its native role. Disabled is the core default, preserving manual settings.
- The generic `scripts/launch-linked-cabinets.py` reuses the established
  RetroArch runner. Power Sled embeds Main / Relay / Slave programs and ignores
  the optional `--relay` flag. There are no CLI role or color selectors.
- Display order is Main / Slave above Relay. Initial colors are Red / Silver;
  subsequent launches preserve per-instance SRAM and Core Options.
- Different physical pad indices map to local Port 1 in each window. Other
  local ports are disabled. P2 is a second rider in the same cabinet, not the
  linked Slave. The adapter now supports P2 Entry/Call and handles 5/7.
- The normal launcher runs no Test/Service, replay or acquisition sequence.

## Targeted Qualification

Input checks cover all three programs, independent P1/P2 routing and releasing
P2 handles when the port is disabled. Save RAM checks cover published option
definitions, reviewed color values, rejection of role presets for Power Sled
and native per-option patch integrity. Both check executables pass. Python
compilation and `git diff --check` pass. Generic Daytona dry-run configuration
passes; this is not a new generic-game runtime qualification.

Actual RetroArch evidence is retained under
`build-libretro-gpu/validation/power-sled-launcher-20261009/`:

| Run | Verified Result |
| --- | --- |
| `session/runs/0001/cabinets` | First three-program launch, native link IDs Main 1/3, Relay 3/3, Slave 2/3; clean exits. |
| `session/runs/0002/cabinets` | Interactive resume from run 0001, `--relay` ignored, native links ready, Ctrl+C closes all three with exit 0 and no forced cleanup or residual processes. |
| `interactive-positions.json` | Actual Main `(24,40)`, Slave `(552,40)`, Relay `(24,468)` window positions. |
| `persistence-review.json` | Both launches retain Main Red and Slave Silver in all three native Ride copies; SRAM container CRCs pass. Original global configuration remains byte-identical. |
| `final-deployment.json` | Both installed macOS core copies match the final build. |

Native runner order maps controller indices to Main 0 / Relay 2 / Slave 1,
matching displayed order Main 0 / Slave 1 / Relay 2. Configuration confirms
Port 1 assignment and other ports disabled. No controllers were connected to
the Mac during this review, so physical/background input delivery is pending.

The final build SHA256 is
`238a858597819f23e00cfada13905d28efa77cfe5757a9fb7c13c9dfa624e353`.
Both `sm2_libretro.dylib` and `sm2_dev_libretro.dylib` in the established
RetroArch cores directory were atomically updated with backups. Project and
installed `games.xml` match SHA256
`547020f175a54f7a0183237ef266084f0ce7c75de82b9f5d541fd348bca79833`.
The first run used the preceding build `5449427f...`; the interactive run
qualifies the final build including disabled-port release handling.

## Gameplay Limit

Autonomous gameplay attempts remain inconclusive. Entry-only replay attempts
unexpectedly entered Test Menu; direct input reached mode selection, but the
follow-up did not confirm a playable race. The cause is not established. See
`Docs/POWER_SLED_LINKED_GAMEPLAY_2026-10-09.md` for retained observations.

Power Sled stays preliminary. Native links, option writes and clean frontend
exits do not certify race progression, steering, motion hardware or sound.
The Main program remains the existing patched Relay approximation. No new
MAME execution, NVRAM sample campaign or changes to another project occurred.
