# Upstream Reconciliation Through 0.9.51

Historical source import: `5ddf84ae7970a9bce1d0a17b3900d26065de1996` (0.9.13).
Previous reconciled coverage: `7db71083ac3419b0c17af74bc6a1640365226238` (0.9.44).
New reconciled release: `90110c7ce2043960dac485a7305e6b56cacab11b` (0.9.51).
Core release: **0.9.51.1**, following `UPSTREAM_VERSION.PORT_REVISION`.

Port revision 0 was tagged but not released after a Windows CRLF packaging
failure. Revision 1 corrects checkout conversion without changing upstream
coverage; the original tag remains intact.

All 48 commits in this release interval are classified below. Merge commits inherit
their reviewed constituent changes; standalone version strings are not the port's
build version. Detailed integration, evidence and qualification limits remain in
[PORTING_PLAN.md](../PORTING_PLAN.md) and the dated reports it links.

| Upstream Commit | Change | Disposition | Port Rationale |
| --- | --- | --- | --- |
| `d15874f` | outputs: publish game state (recoil, ammo, life, wins, credits) from work RAM | Excluded | Standalone cabinet-output destinations have no corresponding Libretro output API here; extra XML output fields remain unused. |
| `a52cee6` | Merge pull request #14 from juniorterin/outputs/game-state | Accounted | Merge of changes classified individually in this interval; no additional independent core change. |
| `f21329d` | update to v0.9.45 | Accounted | Standalone release/version metadata; port release metadata follows the reconciled version convention. |
| `05acaf9` | compose the tile layers from tile RAM latched at the start of vblank - fixes pilot kids insert coins | Adapted | VBlank tile-RAM latch in all four boards and all core renderers; state/ABI and pristine-upstream evidence in the roadmap. |
| `091bf6a` | Drive boards: Sega Rally's board, as its EPROM reads it | Integrated | Native Sega Rally drive-board replies retained; gamepad feedback stays within Libretro rumble capabilities. |
| `34b9334` | Find clones inside merged romsets, from --game and the game picker | Excluded | Standalone clone picker / --game archive resolution; content selection belongs to the frontend, existing core parent/device extraction retained. |
| `acefe1c` | Wheel: an H shifter on buttons | Adapted | Approved virtual H-gate/direct-position/sequential/neutral profiles and frontend remapping replace standalone wheel-button setup. |
| `2509c4f` | Wheel: pedals on half an axis | Adapted | Frontend-normalized virtual pedal travel, independent ranges and reverse polarity; no SDL physical-axis ownership. |
| `0ab3b02` | Wheel: a moment of neutral between gears | Adapted | Gear Shift Neutral Time: upstream 100 ms default, 0–500 ms in 10 ms steps; existing frontend tail retains pending interval. |
| `2feef4d` | Input: read wheels and gamepads in the background, an option | Excluded | Standalone background SDL polling is frontend-owned; core polls only through Libretro callbacks. |
| `4044807` | Merge pull request #15 from njz3/pr/merged-romset-clones | Accounted | Merge of changes classified individually in this interval; no additional independent core change. |
| `b3ae26c` | Merge pull request #16 from njz3/pr/wheel-half-axis-pedals | Accounted | Merge of changes classified individually in this interval; no additional independent core change. |
| `61d4970` | Merge pull request #17 from njz3/pr/wheel-h-shifter | Accounted | Merge of changes classified individually in this interval; no additional independent core change. |
| `c771934` | Merge pull request #18 from njz3/pr/wheel-shift-neutral | Accounted | Merge of changes classified individually in this interval; no additional independent core change. |
| `32497ea` | Merge pull request #19 from njz3/pr/input-background | Accounted | Merge of changes classified individually in this interval; no additional independent core change. |
| `6d41c4f` | Merge pull request #20 from njz3/pr/drive-board-sega-rally | Accounted | Merge of changes classified individually in this interval; no additional independent core change. |
| `e700c39` | Drive boards: Indy 500's board, shared by Touring Car, Over Rev, Super GT | Adapted | Indy-family port-D replies on the applicable board variants; retained centre in the port state format. |
| `abf667c` | Drive boards: Daytona's board works out its own forces | Adapted | Daytona native IN2 board replies; supported gamepad rumble retained, physical-wheel torque not advertised. |
| `a68af19` | Merge pull request #21 from njz3/pr/drive-board-indy | Accounted | Merge of changes classified individually in this interval; no additional independent core change. |
| `945e641` | Merge pull request #22 from njz3/pr/drive-board-daytona | Accounted | Merge of changes classified individually in this interval; no additional independent core change. |
| `e0eced8` | tidy up after the wheel and drive board PRs | Adapted | Drive helper/centre/reply behavior preserved in shared machine interfaces; standalone cleanup and native file-state API reshuffling excluded. |
| `83c6690` | Super GT 24h: its pedals as its I/O TYPE reads them | Adapted | Native A/B/C pedal polarity on Model 2B; user-approved B defaults and B Auto 16:9 presentation. |
| `653c851` | Merge pull request #23 from njz3/pr/sgt24h-pedals | Accounted | Merge of changes classified individually in this interval; no additional independent core change. |
| `9c810a3` | tidy super gt 24h io type | Adapted | I/O TYPE normalization/mux handling and consumed XML imported while preserving approved port bindings. |
| `36d8518` | add per-game gamepad layouts | Excluded | SDL layout persistence and GUI are frontend-owned; approved per-game core profiles retained. |
| `cec4404` | update to v0.9.46 | Accounted | Standalone release/version metadata; port release metadata follows the reconciled version convention. |
| `233a61d` | don't double a bound shoulder as button 3/4 | Excluded | Fix to standalone hardwired shoulder aliases; those SDL aliases are not executed by the adapter. |
| `18eb76e` | stop a shoulder doubling once button 3/4 is rebound | Excluded | Further standalone shoulder/remap collision fix; port-native actions and frontend remaps already own this path. |
| `338ce10` | add an experimental 16:9 widescreen aspect mode - 3D viewports grow into the side columns while the HUD layers stay 4:3 - The back layers fill the sides from a game's own panorama, looping map rows, or a mirror of the screen edge, or black on menu-style games. - Light guns can shoot into the sides. | Adapted | Optional hardware-renderer expansion with shared geometry, background fill and gun reach; native widescreen/software and published state contracts retained. |
| `ea7acf7` | update to v0.9.47 | Accounted | Standalone release/version metadata; port release metadata follows the reconciled version convention. |
| `b6e2a98` | don't take a light gun's joystick as a wheel | Excluded | Standalone SDL lightgun/joystick device classification; Libretro receives devices by frontend port. |
| `1d594ae` | hide virtua cop's late shot flash | Adapted | Two-frame flash latency in shared detector; presentation history retained in the existing state tail. |
| `67ece21` | open the audio device in its own format | Excluded | SDL audio-device format negotiation belongs to the frontend; core retains its native PCM callback contract. |
| `5ffe64f` | latch the interrupt mask two cycles after the write | Integrated | Deferred i960 interrupt-mask timing across all boards replaces port-specific write shortcuts; matched pristine baselines. |
| `e7692b6` | fix last bronx character flicker | Integrated | Last Bronx one-word geometry 0x1a no-op; matched pristine headless baseline. |
| `e573ee1` | update to v0.9.48 | Accounted | Standalone release/version metadata; port release metadata follows the reconciled version convention. |
| `5366b5c` | stop one light gun driving player 2 through the mouse pointer | Adapted | Independent per-port Lightgun/Mouse/Stick arbitration already covers core responsibilities; preserve Standard fallback and mixed-device use. |
| `043a880` | run on gpus without vulkan | Excluded | Standalone Windows loader/SDL backend fallback; the core resolves Vulkan from the frontend and does not link vulkan-1.dll. |
| `df14ed4` | update to v0.9.49 | Accounted | Standalone release/version metadata; port release metadata follows the reconciled version convention. |
| `1c1f6d8` | stop one sinden driving both players on batocera | Excluded | Sinden udev/evdev node discovery is OS/frontend ownership, absent from the core adapter. |
| `ec5a68c` | update to v0.9.50 | Accounted | Standalone release/version metadata; port release metadata follows the reconciled version convention. |
| `8bd0f2b` | relicense to gpl-3.0-or-later | Adapted | GPL-3.0-or-later plus upstream NOTICE terms, retained BSD provenance, distinct modified-port display identity and complete source/dependency packaging. |
| `7f6b343` | bundle dylibs and moltenvk into the macos app | Excluded | Standalone macOS app-bundle dylibs/MoltenVK; the Libretro core owns neither the frontend app nor its driver distribution. |
| `0f13da1` | show why a game failed to start | Excluded | Standalone structured ROM-failure GUI/report plumbing; existing core ROM validation/logs and frontend error notification retained, no change to ROM assembly semantics. |
| `2916529` | launch a rom archive dropped on the window | Excluded | Window drag-and-drop content loading is frontend ownership. |
| `c36828a` | add the rewind branch now that i'm happy with it! Enjoy!!! | Excluded | Standalone rewind controller and its memory-checkpoint/file-state API refactor. Libretro already exposes native machine serialization to frontend rewind/run-ahead with its validated continuation tail; no second rewind engine or replacement state format. |
| `7c4968c` | add gamepad shortcuts on guide | Excluded | Standalone Guide-button menus/shortcuts and GUI diagrams; frontend hotkeys and approved core profiles retained. |
| `90110c7` | update to v0.9.51 | Accounted | Standalone release/version metadata; port release metadata follows the reconciled version convention. |

`ac373ee` after the release tag updates standalone translation strings and is
excluded from the core; it does not introduce another upstream release number.

## Compatibility And Limits

Keep core binary/runtime/save/system identifiers, published controls, initial-save
precedence and per-game selector exceptions. Widescreen is experimental and GPU-only;
native widescreen families retain their native behavior. The optional Daytona
Drive Board readback investigation is not a missing upstream integration or release
gate. Physical lightgun/Sinden and exhaustive game/topology/platform qualification
are not inferred from source reconciliation. No ROMs or private campaign data ship.

Dependency pins are recorded recursively in each corresponding-source archive.
Reconciling the applicable changes does not require wholesale source replacement.
