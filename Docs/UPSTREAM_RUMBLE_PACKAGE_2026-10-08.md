# Upstream Drive Board and Rumble Package — 2026-10-08

## Integration

The full integrated baseline remains 0.9.13
(`5ddf84ae7970a9bce1d0a17b3900d26065de1996`). This package imports the neutral
shared decoder verbatim from upstream `868dce724d0406f081fbdb3290111f24833ca2e8`.
That source includes preceding decoder fixes `1502f1d`, `902fb86` and `e8aa4a2`.
Standalone wheel output, SDL ownership and cabinet-output protocols are excluded.

- Append `DriveProtocol::Indy`, preserving the existing enum numeric values.
  Parse `drive_protocol="indy"` and reuse normal parent/clone inheritance.
- Indy 500 and Over Rev families select the later board program. Enable the
  existing drive-write latch/queue for Over Rev and its clones through metadata.
  Super GT 24h metadata remains unchanged, matching upstream's current database.
- Later-board push step zero releases the effect. Indy parameter bytes retain
  the preceding effect. A later motor-off byte in a frame overrides its push.
- Daytona step zero is a real push; `0x1x` is motor-off, and `0x4x` is a Kick
  away from center. The adapter uses upstream's 2*256 center threshold to choose
  Kick direction, including the existing direction-change impact boost.
- STCC still treats streamed pushes as centering forces. Sega Rally's decoded
  brake/chop metadata and spring geometry are retained by the shared decoder;
  they do not introduce wheel force output into standard Libretro rumble.
- Push/Kick uses the existing normalized strong/weak motor model, synthetic
  cornering vibration, 12-frame tail and immediate lifecycle/disable stops.
  A release stops renewing an impact; the existing short tail can still expire.

**Gamepad Rumble keeps its name, Enabled default and existing values.** No new
Core Option, controller mapping, audio setting, state version or machine archive
field is introduced. Decoded command state is transient adapter state and is
cleared on reset/load/unload/disable. No emulation code includes Libretro headers.

## Over Rev Hardware Setting

Drive-board effects require the existing **HARDWARE TYPE = SEGA STCC** setting
in Foundational Setting or per-game NVRAM Settings. At the original package
validation, the default remained NORMAL (2in1). Synthetic steering-load vibration can still occur without
board effects; it must not be taken as proof that board commands were emitted.
The user requested SEGA STCC as the candidate future core default and as the
Automatic NVRAM override, initially conditional on rumble and gameplay regression
validation. The subsequent user-approved 2026-10-09 integration sets that default
and initial override; see `OVER_REV_HARDWARE_DEFAULT_2026-10-09.md`. Physical
rumble qualification remains open.
User NVRAM is not rewritten by this package. The frontend test uses an isolated
save directory and existing NVRAM options.

## Verification

Evidence root: `/tmp/sm2-rumble-package-20261008/`.

- macOS ARM64 core, frontend-free headless and standalone builds pass.
- The imported decoder files match upstream `868dce7` byte for byte. A separately
  compiled pristine `e1aafb7` decoder matches all decoded fields for all 256
  bytes in each of four protocols: 1024 cases, including effect, strength,
  held state, spring geometry and pulse metadata (`decoder-comparison.json`).
- Rumble callback checks cover earlier Daytona/STCC/Rally behavior, Indy fading
  pushes and parameter retention, step-zero release, same-frame motor-off,
  absent later-board Kick, Daytona step-zero force and Kick direction change,
  disable and shutdown stops. Input checks cover board/protocol metadata on all
  six Indy/Over Rev sets and unchanged Super GT metadata.
- Linux x86_64 core, rumble, input and persistence checks pass. The artifact
  audit confirms 25 Libretro exports, expected dependencies and three empty
  lifecycle cycles. This is container validation, not native Linux gameplay.
- Separate old/new 1800-frame Libretro baselines pass for Indy 500, Over Rev,
  Daytona, STCC and Sega Rally: video, PCM and NVRAM identical. Each title
  passes deterministic state round trips and fresh-process loading of a state
  produced by the previous installed core. Published format/capacity unchanged.
- Matching pristine upstream `e1aafb7` whole-machine comparisons for Indy 500
  and Over Rev pass at 1800 frames: video, PCM, CPU state, master cycles and
  NVRAM identical. Reference source verification was recorded in the preceding
  controls package; its decoder source was also checked against Git here.
- Final installed core, RetroArch 1.22.2 macOS, Vulkan 2x, 2300 frames: Indy 500
  and Over Rev reach active races with steering, pedals and sequential-shift
  fixtures. Both exit cleanly, produce valid Save RAM and nonzero stereo PCM.
- Over Rev's isolated SEGA STCC test saves byte 4 at EEPROM offsets 0x27 and
  0x5b, confirming the actual hardware selection and mirror. An additional
  neutral-steering ABI comparison of NORMAL/SEGA STCC at 3600 frames confirms
  distinct EEPROM output, but observes no nonzero rumble in that sequence.
  It therefore does not prove board-impact delivery during real gameplay.

Physical controller rumble, subjective force balance and native Windows/Linux
frontend behavior remain unqualified. Synthetic callback checks establish the
adapter response to known board commands; gameplay captures establish successful
execution, not physical actuator output. A manual Indy impact test and an
Over Rev impact test with SEGA STCC remain the concrete validation tasks.

## Deployment and Roadmap

Both installed local cores were atomically replaced with backups and verified:
`sm2_libretro.dylib` and `sm2_dev_libretro.dylib`.

Core SHA-256:
`80d6ea491fb67bb0d481d2ab38427b056140dcf4575cae290a2cdb8fdfb0ab82`.

Installed external `system/sm2-emu/games.xml` SHA-256:
`2b420ad3cf0a38cbab82306a2dc3d7a7ae5730720245847f601814b723de1abd`.

Backups are in `installed-backup` under the evidence root. Roadmap status is
Partial for the physical rumble checks; implementation and automated validation
are complete. The adjacent mainstream checkout remains clean. No commit/push,
TGPulse edit or user hardware-setting change was made.
