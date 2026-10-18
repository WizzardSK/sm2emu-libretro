# Virtua Cop Shot-Flash Timing — 2026-10-18

## Change

Imported the detector correction from upstream
`1d594ae4822a80d84d436488be971eb39953aaad`. Virtua Cop may raise its
full-screen shot mask two frames after the trigger press. The previous detector
accepted only the immediate and following frame. The shared detector now
accepts ages 0, 1 and 2, expires afterward and still preserves masks already
present before the shot (fades). Emulated tile RAM is never changed.

**Hide Shot Flash** keeps its existing visibility, Disabled default, applicability
and live application. This is a timing correction, not a new input binding or
option. Software and both hardware renderers consume the shared decision.

## Save States

The frontend-neutral history accessor exposes the press age. The existing tagged
word at offset 76 of the frontend tail uses bit 10 as the new field marker and
bits 11–12 for ages 0/1/2/expired. Bit 2 preserves the old preceding-press meaning.
Power Sled flags and output-DC history do not overlap. No machine serializer,
frontend tail size, state version or total ABI size changes.

Old states remain accepted: the preceding-press flag restores age 0; empty or
unknown history restores expired. An old state cannot recover a pending age
that its format did not store. New states preserve every latency phase. This
is not a promise of exact late-flash replay from every legacy shot-phase state.

## Verification

Evidence: `build-libretro-gpu/validation/vcop-flash-20261018/`.

- Failing-before/passing-after ROM-free two-frame-delay check for both players.
- Immediate and one-frame flash, held trigger expiry, existing fade, disabled
  option, reset, machine archive load and actual tile drawing checks pass.
- New history encoding/decoding covers all ages and legacy/empty words,
  including other occupied frontend-tail flags.
- Real Libretro Software runs, 300 frames: old/new Disabled image, PCM and
  native NVRAM hashes match. A state produced by the preceding installed core
  loads in both versions and its 300-frame continuation matches those same
  outputs. New state round-trip/deterministic replay and corrupt-state rejection
  pass; ABI state size remains 9,437,184 bytes.
- Real Apple GPU Vulkan run, 1,800 frames with scripted aim/shots and filter
  Enabled: eight-frame image/PCM state replay passes. This exercises the
  backend and state path; it does not independently qualify every visible
  in-game flash or constitute a physical-lightgun test.
- macOS core and headless builds pass; standalone build is recorded separately
  in the retained build log. No Windows/Linux runtime requalification is claimed.

The first ABI comparison used the runner's headless-reference option with an ABI
result directory; only that runner-layout comparison failed, while image/PCM
matched. Comparing the ABI result fields directly confirmed all three outputs.
Initial GPU attempts inside the sandbox could not expose a Vulkan device; the
same test outside the sandbox passed with the installed MoltenVK ICD.

## Delivery

Normal local core only, with build/install SHA-256 recorded in `summary.json`.
No dev copy, previous-binary backup, commit, push or release is created.
