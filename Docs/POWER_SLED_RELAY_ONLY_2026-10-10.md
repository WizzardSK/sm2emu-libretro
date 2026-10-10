# Power Sled Relay-Derived Master

## Decision And Implementation

Use the Relay program as the single basis for `powsledm`. The patched-program
comparison found equivalent aligned code/data outside the initializer and
documented relocation/fill boundaries. Relay reaches the reconstruction with
three initializer patch words, while Slave needs fifteen. Both required twelve
additional presentation patch words. This favors the less-modified base; it
does not authenticate the unavailable factory Master program.

Remove `sm2_power_sled_master_donor`, its menu definition and runtime lookup.
Remove the alternate Slave CPU loader/patch adapter, its header and synthetic
check target from the Libretro build. Main always uses the existing Relay-derived
definition and patches in `data/games.xml`. Native role, caption, first-person
color, selection scene, operator commands, audio donor fallback, assets and
NVRAM persistence retain the previously qualified Relay behavior. The user ROM
archives and database are unchanged. Obsolete saved selector values are ignored.

## Save State Compatibility

State size and frontend trailer format remain unchanged. New states leave the
former Slave-donor bit clear. Untagged legacy and Relay-derived states remain
loadable. Retain pre-mutation rejection of development states bearing the old
Slave-donor bit: their CPU/ROM addresses differ, so loading them into Relay would
be incorrect. Native SRAM/NVRAM remains reusable without donor selection.

## Verification And Installation

Evidence root:
`build-libretro-gpu/validation/power-sled-relay-only-20261010/`.

- Release macOS arm64 Vulkan/OpenGL core build succeeds.
- Actual Core Options V2 registration differs only by removing the donor
  selector. All other registered option names, help, categories, values and
  defaults match the pre-change binary exactly.
- Existing ABI runner compares 300-frame previous Relay with the new core
  given an obsolete saved `slave` value. Video, PCM, native NVRAM/EEPROM, timing
  and sample-rate results match exactly.
- Existing deterministic state round-trip/corruption checks pass. A previous
  Relay state loads; a retained Slave-derived state is rejected without changing
  the current machine.
- Both installed local core copies are replaced with backups and verified
  against the tested build. Source, staged, configured and fallback databases
  are verified unchanged and equal.
- The actual installed library passes a separate 300-frame ABI/state round-trip
  with the obsolete `slave` setting; image/PCM/native saves match the tested build.

Installed core SHA-256:
`8d9dfa8dcb7c812b89d67944a4108d6751e460888b17a47e1b5ca9d1ac4c2e6d`.

Database SHA-256:
`080181ab494c3c3889ab4f173985e31c43dce11ef45bb1b9b135c85a7549b8f9`.

`verify-abi.py`, `abi-commands.json`, logs/results, `abi-review.json`,
`check-options.py`, `option-review.json`, `deploy.py` and `deployment.json`
retain reproduction and deployment evidence. Original sources and the previous
binary are retained in the ignored evidence directory. No ROM is added to Git.

This change simplifies donor selection and leaves the previously qualified
Relay program intact. It does not repeat the linked RetroArch gameplay campaign;
its first/second-race evidence is retained in
`POWER_SLED_DONOR_RESIDUALS_2026-10-10.md`. ABI proof and installation hashes are
distinct from a new frontend gameplay observation. Restart already-loaded
content to use the new core. No commit or push is performed.
