# Dead Or Alive Protection Review

Date: 2026-10-19

Status: Implemented And Locally Verified

Scope: User-approved MAME adaptation, local validation and normal-core deployment.

## Recommendation And Concrete Benefit

Integrate MAME's recovered 317-0229 transformation and prefix decompressor in
the existing frontend-neutral device. Replace the fixed startup-string stub.
This is applicable hardware emulation for every supported Dead or Alive set.

The concrete benefit is that the response is computed from the game's encrypted
RAM data and uploaded decoding tables. Incorrect data or incomplete uploads can
then fail naturally instead of receiving an unconditional canned response.
MAME identifies this game's protection use as a startup-string check; this
review establishes no additional graphics, sound, performance or gameplay
benefit. The source still approximates the separate busy/status timing.

## Reference And Scope

Primary change:
[MAME 6743eb674d07, 2026-10-01](https://github.com/mamedev/mame/commit/6743eb674d0754dbbb0726c153d5ef49d84ef67c).
Source snapshot: `cff1e78194319737798cf24f2e106ae3e34222c1`.
The later device change in `272ed7c2767e74ecdb40b74b782e5764e3da8f4d`
adjusts initialization, without changing the transform or decompression logic.

| Board | Supported Sets |
| --- | --- |
| Model 2A | `doaa`, `doaab`, `doaae` |
| Model 2B | `doa`, `doab` |

All five use `Sega315_5838_Doa`; `doab` inherits it from `doa` in the game
database. The chip variant to select is **317-0229** on both boards. The existing
`315-5838-doa` catalogue token can remain compatible; internal comments calling
it a hack must be corrected during implementation. The Model 2A catalogue
comment implying a different 315-5881 path for Model 2B DOA is also misleading
and should be corrected: both DOA paths here use the 317-0229 device.

No additional ROM region or key dump is required by the MAME integration:
the CPU populates source RAM and uploads the decoding tables. Existing profiles,
NVRAM defaults and operator settings need no change. No selector is proposed;
the real algorithm would become the normal device behavior after validation.

## Baseline And Implemented Adaptation

Before this integration, `src/hw/sega_315_5838_comp.cpp` returned a fixed 50-byte sequence,
including two leading spaces. Its upload method was a no-op and its only saved
field was the sequential output offset. The same device is wired independently
in `src/hw/model2.cpp` and `src/hw/model2b.cpp`.

The MAME replacement requires:

1. **Device logic:** the fixed 16-bit 317-0229 word transform, followed by
   programmable prefix decompression. The game uploads a 24-halfword tree and
   256-byte dictionary. Retain the reference bounds checks and invalid-data
   termination. Keep the code independent of MAME's device framework and Libretro.
2. **Source RAM:** read encrypted words from the existing 32 KiB little-endian
   i960 buffer, using the same word addressing and wrapping as the MAME driver.
3. **Register writes:** implement the source address at `0x01d87ff0` and the
   table mode/data halves at `0x01d87ff4` / `0x01d87ff6`. Preserve partial writes
   by address and access width. Review read/write overlays: MAME's read-only
   status/output handlers coexist with underlying RAM writes, while the port's
   shared resolver previously excluded those locations in both directions.
4. **Output reads:** return the first discarded halfword without advancing the
   decoder, then decoded pairs at `0x01d87ff8`. Re-arm the discarded read on
   each source write. The old leading spaces are not verified hardware data.
   Explicitly qualify halfword order and consumption for byte/16/32-bit accesses;
   the old port's 32-bit packing must not be assumed correct for the new handler.
5. **Status:** retain the MAME-compatible toggling status at `0x01d8400c` and
   document its approximate timing. This integration does not establish exact
   cycle timing for the protection chip.
6. **Persistence:** serialize uploaded tables, upload counters/mode, source,
   buffered word/bits, output latch, decoder error state and initial-read flag.

The ST-V cartridge banking, its other cipher variants and its machine drivers
are outside this core's integration scope. Preserve MAME's BSD attribution.

## Save State Compatibility

The assessment baseline used archive format 13. The implementation writes format
14: the device now serializes 319 bytes instead of four, adding 315 bytes on
Model 2A/2B. The fixed 9 MiB Libretro container remains sufficient and unchanged.

Old DOA states contain a canned-string offset and RAM, but no uploaded tree or
dictionary. RAM alone does not establish that those missing fields can be
reconstructed. In particular, resuming a state captured during the protection
check cannot be promised equivalent behavior.

Implemented policy: reject pre-format-14 DOA states before mutating the machine.
The board declares its minimum supported format through the generic state loader;
other games keep the versioned reader for formats 4–13. Libretro displays an
explanation for legacy DOA states and a separate message for incompatible or
damaged DOA images. The existing message interface supplies extended OSD and
legacy frontend fallback. No fixed-string compatibility implementation remains.
New-format decoder upload/bit-buffer states and complete machine states pass
deterministic round-trip checks.

NVRAM/SRAM is separate from this transient protection state and needs no reset
or format migration for the proposed device change.

## Required Qualification Before Acceptance

- Compare the adapted word transform against the pinned MAME implementation
  for all 65,536 inputs; exercise table uploads, partial writes, invalid codes,
  source wrapping, reset and serialization during decoding.
- Capture the native startup transaction for every listed set. Replay against
  the reference decoder and verify the decoded 48-character check, the discarded
  read, and the expected completion without the canned string.
- Compare old/new startup, subsequent video/audio and NVRAM behavior. Run all
  five sets through boot and an attract/game entry; perform actual RetroArch
  gameplay and Save State checks on Model 2A and Model 2B representatives.
- Build standalone, headless and Libretro targets. Confirm unaffected board
  state loading, bounds/corrupt-state handling and the fixed container size.

The MAME recovery uses DOA's known plaintext plus independent Name Club 2 test
data. Its comments explicitly limit uniqueness claims to the tested function
classes and do not establish physical gate layout or exact device timing.
[Device source](https://github.com/mamedev/mame/blob/cff1e78194319737798cf24f2e106ae3e34222c1/src/mame/sega/315-5838_317-0229_comp.cpp),
[Model 2 wiring](https://github.com/mamedev/mame/blob/cff1e78194319737798cf24f2e106ae3e34222c1/src/mame/sega/model2.cpp).

## Evidence And Current Limits

Reviewed the originating patch, follow-up device history, pinned device/header
and Model 2 wiring; inspected both port machine paths, the catalogue/inheritance
and archive layout. Source evidence is retained under
`/private/tmp/sm2-doa-review-20261019/` and
`/private/tmp/sm2-mame-review-20261019/6743eb674d07.json`.

## Implementation And Verification Results

Evidence: `build-libretro-gpu/validation/doa-protection-20261019/`.

- Imported the 317-0229 transform and decoder into the existing device; retained
  the BSD attribution. No ST-V drivers or unrelated chip variants were imported.
- Connected both machine paths, source/table writes, discarded first read,
  little-endian read lanes, source RAM wrapping and writable RAM beneath
  read-only status/output overlays. The toggling status remains approximate.
- A separately compiled, pinned MAME transform produced all 65,536 expected
  words (SHA-256 `f8fd900f4737789026811c8d18ab963c19b8a5979f6733319486c5189d90cf65`).
  The permanent ROM-free check verifies their complete fingerprint and bijection.
- Captured the actual CPU uploads/source reads/output for all five sets. Replayed
  each transaction with the separately compiled MAME decoder: every one of the
  24 output words matches; every set produces the expected 48-character string.
- Before/after Libretro ABI runs: 1,500 frames with Coin/Start/actions per set.
  All five final video hashes, full PCM hashes and native NVRAM hashes match.
  New 9 MiB states restore deterministically and reject corrupt input. Genuine
  pre-change DOA states are rejected without changing the machine.
- Unit checks cover both board buses, upload/bit-buffer persistence, partial
  source writes, source wrapping, missing tables, invalid codes and corrupt
  decoder-state bounds. CI runs the new ROM-free target.
- Genuine older states from Daytona (format 12), VF2 and Virtual On (format 13)
  load and round-trip. The drive-reply check's old synthetic fixture merely
  relabelled a current image as version 11; that no longer represents an old
  Model 2B layout. Removed that synthetic legacy check, retaining current-state
  drive checks and using genuine legacy images in the ABI campaign.
- RetroArch Nightly ARM 1.22, Vulkan/MoltenVK: `doa` and `doaa`, 2,300 frames
  each, visibly in combat, recorded PCM and clean shutdown. This proves replayed
  frontend inputs; physical controllers and subjective listening were not tested.
- RetroArch Save State tests: `doa` and `doaa` with software rendering,
  synchronous threading and no replay. Both advance, restore the saved game
  region exactly, resume advancement and close without forced termination.
- The first asynchronous, active-replay frontend comparison did not restore the
  exact image. The same failure reproduces with the pre-change core; it is not
  introduced by this protection integration. Both attempts are retained. No
  claim of exact frontend replay-cursor restoration is made.
- Standalone, headless and Vulkan/OpenGL Libretro targets compile. ROM-free
  protection, audio and drive-reply checks pass. OpenGL runtime and other host
  platforms were not exercised in this local campaign.

The isolated notification probe initially reused tilde-abbreviated paths from
RetroArch's rewritten test configuration and loaded a different test image.
The corrected probe resolves those paths explicitly; the unsuccessful probe is
retained as runner evidence, not a core failure.

Commit/push was subsequently authorized; no new release is included.
See `deployment.json` for the final
installed artifact hash and `retroarch-legacy-notification-isolated/result.json`
for the frontend notification check.
