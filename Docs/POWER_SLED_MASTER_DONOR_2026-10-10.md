# Power Sled Master Donor

## Current Decision: Relay Only

The user removed donor selection after the patched-program comparison and native
recovery qualification. The Main program now always uses the existing
Relay-derived database definition, which needs fewer initializer modifications.
The selector, alternate Slave loader/patch adapter and its synthetic target are
removed. Old saved selector values are ignored. Native SRAM is unchanged;
Relay/legacy Save States remain supported, while development Slave-derived
states are rejected before machine mutation because their code addresses differ.
See `POWER_SLED_RELAY_ONLY_2026-10-10.md` for current verification and deployment.

The following sections retain the historical implementation and comparison
evidence; their selector interface and alternate loader are no longer current.

## Historical Interface And Loading

`System > Power Sled Master Donor (Restart Required)` offers **Relay**
(default, raw `relay`) and **Slave** (raw `slave`), using Core Option
`sm2_power_sled_master_donor`. It is visible for every game and affects only
`powsledm`. Reload content after changing it; an emulated Reset does not reload
ROMs. Linked instances must be restarted together.

Relay retains the current Main database definition and patches. Slave loads
only the CRC-verified `powsled` maincpu region, searching the selected archive
first and adjacent `powsled.zip` / `.7z` next. Missing donor chips, failed CRCs,
an unexpected program size or incompatible patch sites stop loading with an
error. The core never silently substitutes Relay for a requested Slave.

Only the assembled maincpu is replaced, before machine creation. Main's game
identity, I/O, audio, graphics, native role, network configuration, existing
NVRAM precedence and `powsledm` save filenames remain unchanged. User archives
are not modified. This does not create or authenticate a factory Main dump.

## Slave Adaptation

The adapter reuses the previously qualified Slave-to-Main initializer. It
preserves the settings helper, sets Main mode/role/complement, and derives the
local race index from communication count minus one. The tail store/return
occupies an existing twelve-byte zero gap. The next function remains intact.

Both identity captions read the native NVRAM Ride byte. The second caption and
the first-person sled resource calls/helper are relocated sixteen bytes earlier
than in Relay. All three resource calls select the NVRAM color, preserving the
race object index. This extends the prior caption and sled fixes to both donors;
remote and third-person appearance are outside that qualification.

Every replaced instruction/data word is checked before any write. A late
failure leaves the program unmodified. The implementation lives in the Libretro
adapter and uses the existing frontend-neutral region loader; imported machine
and CPU code have no new frontend dependencies.

## Save States

Offline states require the same program donor: code addresses differ between
Relay and Slave. Bit 6 of the existing frontend gun-flash flags tags Slave;
the state buffer size and trailer version stay unchanged. Untagged legacy
states are treated as Relay. Mismatches are rejected before machine mutation.
Linked-cabinet Save States remain unavailable under the existing rule. SRAM
and NVRAM can be reused with either donor.

## Verification

Evidence root: `build-libretro-gpu/validation/power-sled-master-donor-20261010/`.

- Release macOS Vulkan/OpenGL core build passes.
- ROM-free checks cover sibling and selected-archive donors, missing chips,
  CRC mismatch, wrong size, atomic patch rejection, preserved sound/assets,
  Main initialization, both caption sites and relocated resource calls.
- Actual ABI checks pass deterministic Save State round trips for both donors,
  reject cross-donor states without mutation in both directions, and load a
  previous-core Relay state. Default Relay matches the previous core's image,
  PCM and native-save hashes at 300 frames.
- Actual Core Options V2 registration adds exactly this selector; existing
  option labels, values, defaults and categories are unchanged.
- Two isolated linked RetroArch sessions use the normal Main archive, shared
  system database, saved NVRAM fixture and established Manual input movies.
  Selecting Relay or Slave through Core Options produces native Main role 2,
  count 3, Main/Slave races and Relay race-camera captures. Six normal exits, native
  links, valid SRAM identity/CRC/Ride, paired EEPROM/calibration equality and
  nonzero PCM pass. Main's directly reviewed captures show a red first-person
  sled with either donor. In the Slave run the Main timer advances from 47.38
  to 36.12 between first and third captures; the earlier color-only trial's
  nearly stationary timer is not reproduced, and its cause is not claimed fixed.
- Both installed macOS core copies match the tested Release build, SHA-256
  `1447f4bedda679d8da3b22e616b19ece999513dd4551683f9d30d42f54c0dfe1`.
  `deployment.json` records original hashes and backups. The staged and both
  installed databases already match the source and require no new XML edit.

Local qualification is complete. This bounded observation does not establish
factory Main fidelity, physical-controller behavior, remote/third-person colors
or full-course completion. No commit or push is performed.

See `POWER_SLED_MAIN_RECONSTRUCTION_REVIEW_2026-10-10.md`,
`POWER_SLED_MAIN_RIDE_CAPTION_2026-10-10.md` and
`POWER_SLED_MAIN_SLED_COLOR_2026-10-10.md` for prior evidence and limits.
