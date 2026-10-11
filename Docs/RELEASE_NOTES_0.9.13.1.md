# SM2-Emu Libretro 0.9.13.1

This release retains the integrated upstream 0.9.13 baseline and adds selective
upstream improvements plus Libretro-specific controls and cabinet support.
It is not a complete upgrade to upstream 0.9.44.

## Power Sled

- Reconstruct the undumped Master from the Relay program; make its archive
  optional when the required donor files are available.
- Separate cabinet role from Ride Color, including Yellow in Service Menu,
  NVRAM Settings and Automatic Network Settings.
- Support linked riders with an optional Relay, Master + Relay, experimental
  Master Standalone play and Relay Standalone Attract mode.
- Add experimental Relay Audio on Master with its own gain, Relay Commands on
  Master and AI Finish Speed Fix. Master options are shown only on the Master;
  the Relay exposes its Standalone option.
- Correct boarding, countdown, race/results transitions, audio routing,
  startup diagnostics and Relay identification.
- Adopt validated operator settings and approved calibration defaults;
  retain existing saves and manual settings precedence.
- Use A for Entry, B for Call, independent vertical lever axes, P2 inputs,
  and the approved supplementary bindings.

## Controls, Audio And Operator Settings

- Align Manx TT cabinet audio selection and Deluxe controller responses.
- Adopt calibrated upstream Behind Enemy Lines aiming; expose Linear (MAME)
  and Custom (SM2-Emu) conversion for Rail Chase 2 and HOTD prototype.
- Make Standard lightgun input fall back to mouse/stick when no active gun
  input is supplied; keep Lightgun Only explicit.
- Add D-Pad Up View aliases for games with a single view button.
- Add Ski Super G drive-board responses and independent Inclining aliases.
- Apply frontend-aware synthetic cornering rumble with a 5% minimum threshold.
- Enable SCSP low-pass filtering by default and retain per-board Auto / Mute /
  10%–100% gain conventions.
- Align region default priority to Export, Europe, U.S.A. where supported and
  report applied NVRAM settings with the established reset notification.

## Linked-Cabinet Launcher

- Accept game[:ANS[:GAMEPAD]], with one-based gamepad IDs and r as a relay alias.
- Assign omitted IDs in order; an explicitly empty gamepad field disables
  gamepad input for that instance. Support a single instance and ANS 0.
- Keep the tool generic: no default game or topology and no game-compatibility
  checks. Place playable windows in a row and a trailing Relay beneath them.
- Fit windows to the usable desktop and verify their actual dimensions.
- Reuse per-instance saved options and SRAM; recover queried core-option
  changes after a clean native macOS window close when RetroArch did not save.

## Validation And Limits

The local release gate includes ROM-free input, audio balance, Save RAM,
Netpacket and rumble checks, 21 launcher tests and the NVRAM/YAML catalogue
checks. Earlier documented RetroArch tests and the user's positive gameplay,
audio and control checks cover the corresponding changes. CI builds and checks
Linux x86_64/arm64, macOS arm64/x86_64 and Windows x86_64; successful builds do
not establish physical-controller or gameplay correctness on every platform.

Power Sled reconstruction and optional convenience behavior remain experimental.
Existing save states from older builds may be incompatible: create new states.
ROMs, private recordings and raw acquisition evidence are not packaged.
The packages retain LICENSE, NOTICE and dependency notices, including upstream
source-header terms; the existing licence ambiguity documented in CI.md remains.
