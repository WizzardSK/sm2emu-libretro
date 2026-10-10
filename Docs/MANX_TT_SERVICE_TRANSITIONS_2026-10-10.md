# Manx TT Native Cabinet Transitions

Date: 2026-10-10
Backend: Installed SM2-Emu Libretro In RetroArch Only

## Result

Revision D (`manxtt`) and Revision C (`manxttc`) each complete a native
Twin → Deluxe → Twin cycle through Game Assignments. Each direction uses an
isolated fresh process, so the second direction also qualifies loading the
first committed Deluxe save before changing back to Twin. No NVRAM Settings
or Automatic Initial NVRAM Setup override is active.

The menu displays the requested Cabinet Type, exits normally and returns to
the native game. The adapter log switches to matching audio on native commit,
connects the additional board for Deluxe and selects Twin audio on return.
Both EEPROM and frontend SRAM CRCs pass. Only Cabinet Type, the native update
counter and checksum bytes change in EEPROM. All other EEPROM bytes are
preserved. No calibration menu, endpoint write, ROM patch or personal-save
change is used. The Deluxe-only program has no Cabinet Type selector.

These checks complete the native Service Menu integration gate. They do not
qualify acoustic fidelity, the physical speaker layout or mechanical motion.

## Reusable Recipe

Reuse `scripts/libretro_nvram_samples.py` with an isolated standard SRM and
the documented Game Assignments sequence:

1. R3 opens Test Menu; L3 advances five times; R3 enters Game Assignments.
2. L3 advances three times to Cabinet Type; R3 toggles the value.
3. L3 advances eleven times to submenu Exit; R3 confirms.
4. L3 advances five times to Test Menu Exit; R3 confirms.
5. Observe the native game, close normally, validate the committed SRM.
6. Start the reverse direction from that SRM in a fresh RetroArch process.

The parent recipe and YAML still used historical L3 Test / R3 Service labels.
They now match the current frontend R3 Test / L3 Service binding. The clone
recipes already had those current bindings and retain them. The parent recipe
also uses the current GPU-capable build/system paths, matching the clone
recipes. Historical samples and their original scripts/logs are retained.

## Evidence

Ignored root: `build-libretro-gpu/validation/manxtt-service-transition-20261010/`.
Four TOML recipes, per-case screenshots, logs, isolated configurations and
native/container saves retain the exact cycle. `review.json` records CRCs,
EEPROM changes and audio transition/fresh-load checks. The initial old-binding
case reached Memory Test and left Cabinet Type unchanged; it is excluded.
Its dependent case was interrupted, and the corrected cycle resumed.

Production build and both installed cores remain SHA-256
`5597cb0b98748757e9de48d359efe760c1d397dc02fcfcfaf909fa0498db3253`.
No emulation change or core deployment is required by this validation.
