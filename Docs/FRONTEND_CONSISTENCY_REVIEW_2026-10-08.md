# Frontend Consistency Review — 2026-10-08

Reference: `/Users/andrea/dev/tgpulse-next-libretro`, inspected read-only.
Equivalent controls must share names, choices, order and saved-value conventions.

| Control | Result |
| --- | --- |
| Source Gain | Removed misleading Absolute/Relative suffixes and aligned the source names DSB (MPEG) and FM (YM3438). TGPulse suffix removal is recorded in the interchange file for its project chat. Canonical choices: Auto, Mute, 10%–100%; Auto default; raw auto, 0 and numeric percentages. SCSP follows the same pattern. SM2 retains its published source output scale and Auto preserves its reference mix. |
| Aspect Ratio | Same name, Auto / 4:3 / 16:9, Auto default and saved values. |
| Timing / FPS Overlay | Same name, Off / Auto / On (11–14 px), Off default and saved values. |
| Gamepad Rumble | Same name, Enabled / Disabled, Enabled default and saved values. Hardware feedback differs by machine. |
| Driving Steering Response | Same name, Linear / Progressive (Fine Center) / FBNeo Logarithmic (Fine Center), Linear default and saved values. |
| Driving Output Range | Same steering/accelerator/brake naming and percentage structure. SM2 retains the existing hardware-specific 63% and 75.3% ADC presets documented in the option help; they are not new generic alternatives. |
| NVRAM Settings | Same name, Disabled / Enabled, Disabled default. Only loaded-game fields are shown. Operator fields remain game-specific. |
| Linked Cabinets | Same name, Disabled then cabinet counts. Maximum counts follow the actual game hardware. |
| Automatic Network Settings | Same name. Corrected Disabled (Manual Settings) to Disabled. Role/color/car choices follow each game's native network identities. |
| A/V Timing | SM2 follows the approved 60 Hz (Default) / 57.524 Hz (Native Model 2) convention. TGPulse still has the previous labels/default in its checkout; the existing interchange file carries the requested Model 1 change for that project's chat. |
| Music Volume / Master Volume | Different controls: SM2 Music Volume adjusts the separate MPEG board; TGPulse Master Volume adjusts the complete mix. They must not be relabeled as equivalent. |
| Renderer and Filters | Available implementations differ; no unimplemented TGPulse selectors are added. |

## Compatibility and Verification

New configurations expose only the canonical Gain choices. A currently saved
legacy Gain above 100% or textual mute is retained during option registration,
so RetroArch does not silently replace it with Auto. No files are rewritten on
read. Selecting a canonical value makes subsequent frontend saves use it.

- All ROM-free Save RAM/Core Options checks passed.
- Both Core Options V2 and legacy registration were checked for canonical order
  and preservation of existing numeric/textual values.
- VF2: 1,800 callbacks each with Auto, 100% and Mute; Auto and 100% produced
  identical PCM, Mute changed only audio, and video/NVRAM matched. Save State
  round trips and deterministic replay passed in all three runs.
- Built macOS core is installed to both local RetroArch SM2 core paths and
  checked by SHA-256. games.xml already matches the project copy.
- These are ABI checks; subjective listening and a visual RetroArch menu check
  remain user checks. No commit or push.
