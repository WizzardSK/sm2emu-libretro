# Daytona USA GTX Service Menu Inventory

Date: 2026-10-17
Status: Phase 1 And Phase 2 Qualified; Approved NVRAM Settings Implemented

## Acquisition

Observed daytonagtx directly in the local SM2-Emu Libretro core running in RetroArch 1.22.2. A fresh isolated system/config/save root was created; Automatic Initial NVRAM Setup, NVRAM Settings and network presets were disabled. No user saves, ROM collection, installed core or shared Framework workbook was modified. No emulation code was changed and no new network model was implemented.

The existing linked-cabinet runner's configuration, UDP input, screenshot and owned-process shutdown functions were reused by the retained menu-only driver. Phase 1 did not include a variation-sample recipe, binary extraction, NVRAM mapping, initial-template creation or option implementation; the approved integration is recorded below. Normal RetroArch autosaves in the isolated root are disposable runtime files, not validated campaign samples.

Evidence root: `build-libretro-gpu/validation/daytonagtx-service-20261017/`. `inventory.json` lists all 83 PNGs with hashes, exact field values and cycle evidence. `menu-run/events.json` retains inputs; `session.json`, `retroarch.log` and `exit.json` retain core hash, launch and normal exit (code 0, no forced kill). The initial non-interactive-stdin attempt exited before observations; the fresh menu-run is authoritative.

All ten selector cycles close with byte-identical first/last PNG files. Every discrete value was captured. Native labels/defaults below come from GTX screenshots, not the Daytona parent. OCR was used as an aid; its imperfect transcription is not the catalogue authority.

## Root Hierarchy

1. BOOKKEEPING
1. GAME SYSTEM
1. COIN ASSIGNMENT
1. INPUT TEST
1. OUTPUT TEST
1. DRIVE BD TEST
1. SOUND TEST
1. TGP TEST
1. MEMORY TEST
1. BACKUP RAM CLEAR
1. EXIT

Game System and Coin Assignment are the two operator-setting pages. Bookkeeping, Input/Output/Drive Board/Sound/TGP/Memory tests and Backup RAM Clear are listed only; no calibration endpoints or destructive actions were acquired. An accidental navigation capture named coin-default.png shows the Output Test submenu and is excluded from operator evidence.

Controls: R3 enters Test Mode, L3 advances the cursor and Start selects/changes the highlighted item. The native screen also advertises its four colored cabinet buttons. Game System is reached from initial root EXIT with two L3 presses and Start. Submenu Exit returns to the previously selected root item; native root Exit was selected explicitly afterward.

## Observed Settings

| Page | Setting | Native Default | Complete Native Cycle |
| --- | --- | --- | --- |
| Game System | LINK ID | MASTER | MASTER, SLAVE, SINGLE |
| Game System | CAR NUMBER | 1 | 1, 2, 3, 4, 5, 6, 7, 8 |
| Game System | CABINET | TWIN | TWIN, UPLIGHT, DELUXE |
| Game System | COUNTRY | JPN | JPN, EXPORT, USA |
| Game System | DIFFICULTY | NORMAL | NORMAL, HARD, HARDEST, EASY |
| Game System | ADVERTISE SOUND | ON | ON, OFF |
| Game System | GAME MODE | NORMAL | NORMAL, GRAND PRIX, ENDURANCE |
| Game System | RIVAL ARROW | ON | ON, OFF |
| Coin Assignment | CREDIT TO START | 1 | 1, 2, 3, 4, 5 |
| Coin Assignment | COIN/CREDIT SETTING | #1 | #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11, #12, #13, #14, #15, #16, #17, #18, #19, #20, #21, #22, #23, #24, #25, #26, #27 |

CABINET literally displays UPLIGHT; it was not normalized to the parent catalogue's UPRIGHT. Coin preset #27 displays FREE PLAY for both chutes. CHUTE1 and CHUTE2 are dependent tariff displays, not separately selected fields; each complete tariff screen is retained for all 27 presets. The initial values were restored before native submenu/root exits. Country/cabinet labels changed through their complete cycles without adding rows on Game System. The Coin Assignment cycle was observed with native Country JPN; other-country tariff differences have not been separately qualified.

## Native Network Inventory

- Network configuration is present: LINK ID cycles MASTER, SLAVE, SINGLE. Native default is MASTER.
- Identity is a separate CAR NUMBER field with all values 1 through 8; native default 1.
- Native offline/standalone selection is SINGLE. Presence in the menu is verified; no separate standalone/gameplay qualification was performed.
- No Relay selector occurred in the complete Link ID cycle. Do not infer additional unobserved modes or promise relay operation.
- Eight selectable car numbers are a menu limit, not proof of eight linked RetroArch participants. Multiplayer protocol, transport/session behavior and actual linked gameplay remain unverified.
- GTX remains excluded from inherited parent NVRAM overrides/templates and from unreviewed automatic network mappings.

## Deliverables And Next Gate

- `data/diagnostic-menus/daytonagtx.yaml`: independent menu inventory; binary locations and integrity deliberately unverified.
- `GAME_SETTINGS_CATALOG.md`: independent clone cycles/defaults and documentary screenshots.
- `Docs/revisione_core_options_model2.xlsx`, Core options rows 277–286: ten observations, native default emphasis and Pending Review status. Existing sheets/values/fonts/table styles/panes were verified preserved.
- Diagnostic YAML audit: 57 files. NVRAM Core Option audit: 88 sets / 332 existing options, with GTX explicitly unreviewed.

Review the ten fields before any Phase 2 recipe/sample campaign or NVRAM implementation. Network-session implementation and whole-game qualification are separate activities. No commit/push.

## User Review Recorded — 2026-10-17

The saved local workbook now approves the eight Game System fields: Link ID,
Car Number, Cabinet, Country, Difficulty, Advertise Sound, Game Mode and Rival
Arrow. Credit To Start and Coin/Credit Setting are excluded from Core Options;
their observed inventory and screenshots remain retained. Phase 2 has not
started. Native defaults and unverified binary mapping remain unchanged.

Workbook row banding must come exclusively from its native table style with
row stripes enabled. Do not paint alternating direct cell fills: native banding
must remain correct after filtering. The user-saved GTX rows have no direct
fills and were left untouched.

## Daytona Family Defaults Review

GTX follows the same applicable frontend defaults as the existing Daytona
family, rather than treating native observations as the complete review:

| Setting | Observed Native Default | Core Selector Default | Initial Setup Override |
| --- | --- | --- | --- |
| Link ID | MASTER | SINGLE | SINGLE |
| Cabinet | TWIN | DELUXE | DELUXE |
| Country | JPN | EXPORT | EXPORT |

Car Number remains 1; Difficulty Normal, Advertise Sound On, Game Mode Normal
and Rival Arrow On retain the native values. The other validated template
fields are preserved. This matches the existing initial_values selection and
the agreed Daytona Cabinet exception / Country priority, not guessed GTX bytes.

The local workbook's Daytona GTX sheet now records Native Default, Core Option
Default, Automatic Initial NVRAM Setup, review decision and implementation
status separately, using the existing campaign-review table conventions and
native row banding only. The source observations and user's Yes/No selections
in the primary review table remain unchanged. Equivalent core_default and
default_policy fields are recorded in the GTX YAML, as in daytonas.

The approved policies are implemented after the complete acquisition/commit/reload gates described below. Initial setup runs only without existing valid saves. The template is GTX-specific.

## Approved Integration — 2026-10-17

The complete recipe `scripts/libretro_nvram_samples.daytonagtx.toml` qualified
58 stages in the target core in RetroArch: one baseline and fresh reload, then
all 28 approved field/value variants and each fresh-process reload. Every stage
checks the Service Menu heading; variants also match the independent Phase 1
value screenshot. Native CRC, mirrored banks and EEPROM word order are checked
for every save. Manifest: `build-libretro-gpu/validation/nvram-campaigns/daytonagtx/campaign.json`.

The eight Game System fields now have a dedicated GTX catalog and validated
initial template. Initial setup applies Single / Deluxe / Export only without
valid existing saves. Other fields, including calibration, remain native.
GTX's native cabinet spelling UPLIGHT maps to the established frontend UPRIGHT
label; its numeric value remains 2. Credit To Start and Coin/Credit Setting
remain excluded. Multiplayer operation is not established by this campaign.

An early runner attempt sent input during boot diagnostics. Those results were
invalidated, retained separately, and not used as qualified samples. The corrected
recipe waits for startup and requires a matching Service Menu heading.

## Integration Verification And Local Delivery

The macOS build, Libretro Save RAM checks, diagnostic YAML audit and NVRAM
catalog audit pass (88 supported sets, 340 operator options). Three isolated
RetroArch trials verify fresh initial setup, precedence of existing valid Save
RAM, and manual NVRAM Settings. Native checksums/mirrors/EEPROM and unrelated
settings bytes are preserved. The fresh native menu displays Single / Deluxe /
Export and the remaining five native defaults.

Evidence: `build-libretro-gpu/validation/daytonagtx-integration-20261017/results.json`.
Only the normal installed `sm2_libretro.dylib` was updated; its SHA-256 matches
the tested build (`c3e1fcfe0df92e53a3a25cd6882fa8b522706ed679e8bc586792896b4ee9d9ed`).
Deployment backup and report are retained alongside the trial results.
The workbook changes only the approved implementation-status cells, preserving
all other workbook parts and the original table styles, views and reviewer data.
