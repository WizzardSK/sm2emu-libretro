# Daytona GTX Network Inventory Handoff

Date: 2026-10-17
Source: SM2-Emu Libretro
Destination: Libretro Core Framework Project Chat
Scope: Update The Existing Network Review Row; No Network Implementation

## Delivered Source Evidence

Phase 1 Service Menu inventory is complete for `daytonagtx`, directly in
SM2-Emu Libretro running in isolated RetroArch 1.22.2. Ten operator fields,
83 screenshots, full native selector cycles and all first/last PNG pairs
byte-identical. No parent-menu inference, automatic NVRAM override, sample
campaign, mapping implementation or installed-core change.

- Report: `Docs/DAYTONA_GTX_SERVICE_MENU_2026-10-17.md`.
- Catalogue: `data/diagnostic-menus/daytonagtx.yaml` and `GAME_SETTINGS_CATALOG.md`.
- Local review: `Docs/revisione_core_options_model2.xlsx`, Core options rows 277–286.
- Screenshot manifest: `build-libretro-gpu/validation/daytonagtx-service-20261017/inventory.json`.
- Screenshot folder: `build-libretro-gpu/validation/daytonagtx-service-20261017/menu-run/screenshots/`.
- All paths above are relative to `/Users/andrea/dev/sm2-emu-libretro`.

## Framework Network Review, Existing Order 016

Replace Service Menu Pending with an inventory-complete status and preserve
separate implementation/runtime qualification gates:

| Item | Observed GTX Menu Evidence |
| --- | --- |
| Native Network Settings | Present On Game System |
| Role Field | LINK ID |
| Complete Role Cycle | MASTER, SLAVE, SINGLE, MASTER |
| Native Role Default | MASTER |
| Independent Identity Field | CAR NUMBER |
| Complete Identity Range | 1 Through 8, Then 1 |
| Native Identity Default | 1 |
| Native Standalone Selection | SINGLE |
| Relay | No Relay Value In The Complete Observed Role Cycle |
| Participant Limit | Eight Selectable IDs; Eight Connected Instances Not Qualified |
| Actual Multiplayer | Not Tested |
| GTX Automatic Role/ID Mapping | Not Implemented; Review And Phase 2 Pending |

The complete observations also include Country JPN/Export/USA, Cabinet
Twin/UPLIGHT/Deluxe (literal spelling), Difficulty, Advertise Sound, Game Mode,
Rival Arrow, Credit To Start and all 27 Coin/Credit settings. No generic ANRS
model was implemented or applied. The current shared workbook was not modified
from the source chat. This handoff authorizes the requested documentation/row
update only, not implementation, commit or push.
