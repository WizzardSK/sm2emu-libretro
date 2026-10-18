# Framework Menu Wording — 2026-10-13

## Scope And Source

Applied the current user-revised Framework workbook, Menu Review sheet:
`/Users/andrea/dev/libretro-core-framework/outputs/01a13152-dbfa-7e30-bc9d-0477abc2cccc/Framework_Menu_Review.xlsx`.
Selected `Core: SM2-Emu = True` and `Per-Game NVRAM = False`; used Name (New)
when populated, otherwise Name, and the exact reviewed Comments. Historical
Source Options rows do not override the reviewed merges. Framework F04/F05/F08
and REFERENCE_SOURCES.md were inspected read-only.

48 reviewed rows map to 108 registrations, including 31 Linked Cabinets and
31 Automatic Network Settings keys. The 332 individual NVRAM registrations
remain byte-for-byte identical in the ABI catalogue. All 440 registered keys,
raw values, value labels, defaults, categories and registration order remain
unchanged. Only option labels/help changed; no input mapping, visibility,
persistence, emulation or feedback behavior was modified.

Single-game labels now use the approved `<Game Name>: ` prefix. Timing / FPS
Overlay, Gamepad Rumble and Off-Screen Reload Shortcut retain the approved
shared labels. Automatic Initial NVRAM Setup now carries the workbook's
(Restart Required) suffix. Existing native per-game networking restrictions
remain in the implementation and project documentation; the UI comment is the
one consolidated workbook text.

## Evidence

Evidence directory: `build-libretro-gpu/validation/framework-menu-20261013/`.
- `review.json`, `mapping.json`, `before.json`, `after.json`, `audit.json`:
  complete row/key reconciliation and modern registration comparison.
- Legacy SET_VARIABLES registration independently checked: all 440 labels and
  raw value sequences match the modern catalogue.
- macOS core and Save RAM check target rebuilt successfully; all Save RAM checks
  pass. Existing link-rule checks now inspect the unchanged native rule helper,
  rather than requiring superseded help paragraphs. The mouse fallback check
  retains its registered-name/default assertion without superseded prose.
- The normal installed RetroArch core was updated with hash verification and a
  backup; no dev copy was created. See `deployment.json`.

Core SHA-256: `a97aad91e25060a3a08afc909a659b0942e835e72d97eb46736bd24641ebce83`.
Workbook SHA-256: `72b96114c437313fef061c3517a2812daa7563be0e9b15b1d270e14a375e374a`.

## Remaining Visual Acceptance And Reference Notes

An isolated VF2 RetroArch 1.22.2 run loaded the core but failed window positioning
(the runner reported automation/accessibility permission requirements); CUA app
selection also timed out. The runner terminated its owned instance normally,
with no residual processes. `frontend/result.json` records failure. No visual
menu acceptance or new gameplay/input/audio correctness is claimed. Resume the
bounded menu inspection when native window access is available.

The workbook's Gamepad Rumble help matches SM2's synthetic vibration behavior;
it must not be generalized literally to cores forwarding native feedback.
The reviewed text is retained verbatim, including `lightun` in Crosshair Style
(Order 084) and `from the select cabinet configuration` in Manx TT Cabinet Audio
(Order 077). These are source wording notes, not emulation changes; the shared
workbook was not edited. No factual behavior incompatibility was found for SM2.

No commit or push was performed. Pre-existing work remains separate.

## Approved Rumble Comment Follow-Up — Delivered

Verified Menu Review!F98, Order 071, directly in the saved workbook and applied:

> Enable gamepad vibration using the game's force-feedback or rumble effects.

This supersedes the earlier cross-core Rumble wording exception. The core was
rebuilt and its actual V2 registration captured in `after-final.json`: only this
help string differs from the previous delivered catalogue; all other fields and
registrations are identical. Normal installed core updated and hash verified in
`deployment-final.json`, with a backup of the prior installed binary.

Final core SHA-256:
`012c98c749f3cf37cb50ee9197f01c5d60fa9da3a580236c821461ee8769dc0f`.

The second isolated VF2 session successfully reached Quick Menu and the Core
Options category list (System, Video, Audio, Input). Subsequent CUA actions lost
the window and then returned ScreenCaptureKit error -3811, audio/video capture
failed. Individual option-page visual acceptance therefore remains open. The
runner was stopped through its own session and exited normally with no forced
kill or residual processes; see `frontend-final/result.json`. No screenshots
were saved locally. No unrelated RetroArch instances were controlled.

The earlier workbook fingerprint remains the original implementation snapshot.
Other reference notes remain valid. No commit or push.

## Final Category-Page Visual Acceptance — 2026-10-18

A later isolated VF2 / RetroArch ARM 1.22.2 run inspected the actual System,
Video, Audio and Input option pages. Renderer immediately precedes Software
Renderer Threading; 2D filtering precedes 3D filtering. Audio begins with
Music Volume, Enhanced Audio Balance, the applicable source Gain and SCSP
Output Low-Pass Filter. Input begins with Controller Profile Type and Gamepad
Rumble. VF2 shows the unsupported network controls explicitly as Not
Supported. The complete catalogue remains supported by the prior registration
audit; the visual pass did not individually inspect every dynamic NVRAM field.
No screenshots were saved as files. The isolated runner exited normally with
no residual process. See `Docs/FRONTEND_MENU_AUDIO_RESET_2026-10-18.md`.
