# Gun Mapping Integration — 2026-10-11

## Approved Behavior

- Behind Enemy Lines uses the full-range upstream positional mapping from `b4c0931`. Remove the manufactured calibration and per-frame RAM float override from Model 2C.
- Initial BEL calibration uses the operator-verified upstream EEPROM from upstream revision `7db7108`: MIN `00`, DEL `FF` for both axes and both players. Only calibration bytes are imported into the existing template. Other settings remain intact; both EEPROM checksums and the template CRC are regenerated.
- Valid existing frontend/native saves retain precedence. They are not migrated. Existing BEL saves using the previous mapping require Service Menu recalibration; old save states also retain old volatile calibration and should not qualify the new mapping.
- Rail Chase 2 Aim Mapping: **Custom (SM2-Emu)** (default) / Linear (MAME). Applies to both revisions, preserving P1/P2 mux routing and the original linear range/polarity when Linear (MAME) is selected.
- House Of The Dead Prototype Aim Mapping: **Custom (SM2-Emu)** (default) / Linear (MAME). Expanded upstream coordinate bounds are optional; Linear (MAME) restores the published port bounds. Trigger routing and explicit off-screen handling remain unchanged.
- Both selectors stay visible for all games and are no-ops outside their stated titles. Changes take effect immediately; recalibrate RC2 after changing mapping.
- The latest user approval supersedes the earlier RC2 Linear-default decision. No new automatic border-reload policy is introduced in this package.

## Reproduction And Evidence

`data/bel-calibration-defaults.json` records operator source provenance without ROM or save contents. `scripts/update-bel-calibration-defaults.py` reapplies the approved calibration to the current embedded image using the established template encoder. Reapply after regenerating templates from older acquisition samples.

Evidence: `build-libretro-gpu/validation/gun-mapping-integration-20261011/`.

- Core compilation succeeds.
- Input checks cover BEL full-range endpoints for both players, RC2 selector branches and both revisions, HOTDP selector branches and both players, existing trigger/reload and Standard fallback checks.
- Save RAM checks pass, including template integrity and existing-save precedence.
- Physical lightgun/gamepad and subjective reticle placement remain operator checks. The upstream calibrated aiming result is user evidence, distinct from target-core verification.

Labels **Linear (MAME)** / **Custom (SM2-Emu)** were explicitly requested by the user. Stored selector values remain `previous` / `upstream`, respectively.

## Target-Core Result And Deployment

RetroArch 1.22 Vulkan/MoltenVK completes 2,300 frames with valid scripted P1 aiming/shooting, audio capture, gameplay screenshot, clean exit, and the expected full-range calibration retained in the isolated SRM. Input checks separately cover both players; exact physical reticle accuracy is not qualified by this run. The initial software capture crashed; the first Vulkan replay selected an incompatible reader and is not valid gameplay evidence. The final run explicitly uses `--replay-reader 1.22`.

Normal `sm2_libretro.dylib` and configured system `games.xml` were installed with matching SHA-256 hashes and previous-file backups. The dev core remains absent; personal saves are untouched. Frontend-free headless compilation also passes. Table values match upstream for BEL and both RC2 revisions.

## User Closure

On 2026-10-11 the user closed BEL, RC2 and HOTDP in the roadmap. No further operator test is scheduled. Retain the documented verification limits; reopen only for a newly reported issue.
