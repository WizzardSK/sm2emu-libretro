# Over Rev Hardware Default and Automatic Setup

## Implemented Policy

The user approved **HARDWARE TYPE = SEGA STCC** as the new core default and
Automatic Initial NVRAM Setup override on 2026-10-09. This applies to `overrev`,
`overrevb` and `overrevba`; both clones already use the reviewed parent catalog
and parent-compatible initial template.

- `sm2_nvram_overrev_hardware_type` defaults to `sega_stcc`. Its displayed value
  follows the existing Title Case formatter: **Sega Stcc (Default)**.
- Automatic initial setup selects that same catalog default for newly seeded
  NVRAM, even when ordinary NVRAM Settings is disabled.
- The generic NVRAM engine writes byte `4` at EEPROM offsets `0x27` and `0x5b`
  and updates the existing native integrity fields.
- Valid frontend SRAM and existing native saves keep their established
  precedence. Automatic setup does not replace them.
- An explicitly saved Hardware Type remains respected when NVRAM Settings is
  enabled. All four Hardware Type values remain available.

The acquired template, screenshot catalog, diagnostic YAML and review workbook
retain the observed native **NORMAL (2in1)** default. The catalog audit records
SEGA STCC as an approved core override, separately from native acquisition data.
No machine, drive-command decoder, controller binding or Save State format was
changed by this follow-up.

## Verification

Evidence root: `build-libretro-gpu/validation/overrev-default-20261009/`.

| Check | Result |
| --- | --- |
| macOS core, Save RAM checks and rumble checks build | Passed |
| Save RAM checks | Passed: registered default and default label, missing-variable fallback, explicit NORMAL selection, automatic EEPROM mirror writes, manual override validity/idempotence and frontend save round-trip |
| Existing rumble callback checks | Passed; synthetic callback qualification only |
| NVRAM catalog audit | Passed: 87 sets, 86 with NVRAM Settings, 331 options |
| Fresh installed-core RetroArch, Automatic Setup enabled, NVRAM Settings disabled, no explicit Hardware Type | Passed: EEPROM hardware bytes `4/4`, valid frontend SRAM CRC, active race visible, nonzero stereo PCM, normal process exit |
| Existing NORMAL SRAM, Automatic Setup enabled, NVRAM Settings disabled | Passed: frontend save loaded, initial setup skipped, EEPROM hardware bytes remain `0/0`, valid frontend SRAM CRC, normal process exit |
| Local deployment | Both installed core copies match the built artifact; previous binaries backed up |

The two frontend runs use the existing sequential-driving replay, RetroArch
1.22.2, Vulkan at 2x and 2300 frames each. All saves, configs, recordings and
captures are isolated. The fresh run took approximately 44 seconds.

Both installed binaries have SHA-256:

`00738f3a3255675a6643106db942e8ef81640700bb47e7a863bb95ba211d36b1`

Installed paths:

- `/Users/andrea/Library/Application Support/RetroArch/cores/sm2_libretro.dylib`
- `/Users/andrea/Library/Application Support/RetroArch/cores/sm2_dev_libretro.dylib`

`deployment.json`, `hardware-check.json`, `existing-save-check.json` and each
frontend run's `command.json`, `result.json`, `run.log`, SRAM and screenshot
retain the reproducible evidence. No personal save or option file was migrated.

## Remaining Qualification

Physical controller rumble and subjective steering/audio quality remain open.
Active race capture and nonzero PCM do not qualify physical controls, sound
fidelity or delivery of a specific drive-board impact. The earlier decoder and
rumble evidence remains in `UPSTREAM_RUMBLE_PACKAGE_2026-10-08.md`.

The roadmap now records the default/automatic override integration as completed
inside Drive Board and Rumble Reconciliation, with physical qualification still
pending.
