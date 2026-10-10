# Upstream i960 and Bus Timing Package — 2026-10-08

## Imports and Frontend Contract

The full integrated baseline remains 0.9.13
(`5ddf84ae7970a9bce1d0a17b3900d26065de1996`). This package selectively imports:

- `8a49096`: i960 extended-real `movre` encoding/conversion, interrupt priority
  mask, `subc` carry/borrow handling and signed modulo sign detection without
  overflowing an operand product. Includes the associated SHARC circular-buffer
  correction at the exact upper boundary.
- `7080210`: slow tile RAM accesses, used by Virtual-On water clearing.
- `e36f757`: texture RAM access waits on Model 2B/2C and `texture_wait=37` for
  Virtual-On; the clone inherits the metadata value.
- `1987d82`: per-area data-access waits decoded from Sega CPU-control registers
  on Original Model 2, 2A, 2B and 2C. Instruction fetches bypass these area waits;
  DRAM and external-ready behavior follow upstream.

These imports do not change `round_to_int`. The existing
**i960 Round-to-Nearest-Even Fix (Restart Required)** option retains its key,
Disabled / Enabled values, disabled default and existing implementation.
Synthetic positive and negative half-integer conversions pass in both modes.
There is no demonstrated collision requiring an additional selector. Tile,
texture and area waits are normal upstream machine behavior.

Original Model 2's area timing was adapted around the port's existing Daytona
Maxx protection read path; protection branches are preserved. Other applicable
machine patches were imported directly. `GameSpec` insertion was adapted to
preserve the port's existing start-gear documentation. No Libretro dependencies
were introduced in machine or CPU code, and no control profiles were changed.

## Save States

No serialized fields, header versions or fixed Libretro capacity changed in
this package. The instruction-fetch guard is transient and clear between
accesses. CPU-control registers were already serialized. Existing format-6
states remain readable, alongside the audio package's format-4/5 support.
Loading an old state preserves the saved registers but future execution uses
the new CPU/timing behavior; identical future playback across core versions is
not promised when emulation fixes intentionally change execution.

## Verification

Evidence root: `/tmp/sm2-i960-package-20261008/`.

- macOS ARM64 core, headless and standalone builds pass.
- ROM-free i960, input, Save RAM/Core Options, audio and sound-timing checks pass.
- New i960 checks exercise both rounding conventions, carry and borrow,
  both `movre` encodings and the Intel extended-real register image, signed
  modulo with a formerly overflowing operand product, all ten programmed memory
  areas, DRAM bypass and all wait codes. A synthetic load loop retires fewer
  instructions with waits enabled while instruction fetch remains separate.
- The same opcode/timing test program passes against unmodified pristine
  `1987d82` CPU/archive/log sources with the upstream rounding default. The
  enabled port-specific rounding mode is tested separately in the port.
- Catalog checks verify `von` and `vonr` both acquire 37 texture wait cycles.
- Old and new cores each run 1,800 frames with exact Save State replay on
  Daytona, VF2, Virtual-On, House of the Dead and Dead or Alive. The new core
  loads each old-core state in a fresh process and repeats its replay test.
- A separate pristine `1987d82` standalone build is compared with port headless
  Virtual-On for 1,800 frames: CPU state, master cycles, PCM, audio format and
  NVRAM are identical. Raw final video differs. Every one of its 571,392 color
  channels is compatible with the already integrated `2c4e9e2` gamma change
  (black point 64 to 40); zero channels fall outside that mapping. The result is
  not reported as a byte-identical image.
- Installed-core RetroArch 1.22.2 Virtual-On test, Vulkan 2x: 2,300 frames,
  inspected gameplay capture with the sea visible, non-silent stereo audio
  (peak 27,330), clean exit. Full physical twin-stick control and subjective
  audio fidelity are not established by this automated run.
- Linux x86_64, existing Debian 12/Rosetta builder: core build and i960, audio,
  sound-timing, input and Save RAM checks pass. Artifact audit passes 25 ABI
  exports, dependency inspection and three empty lifecycle cycles. This also
  covers the recent audio package's new checks on Linux. It is not a native
  Batocera gameplay or Windows test; remote CI was not invoked.

The new ROM-free i960 checks are added to the existing CI check step.

## Local Deployment

Both local RetroArch cores were replaced atomically with matching SHA-256:
`518afce7b44b0a5ca2ebe446e6796a970270acfa7ce65034dc3d30a8ea4dc4e6`.

The installed system `sm2-emu/games.xml` was updated for Virtual-On texture wait
metadata, SHA-256:
`532bb0a3187113188538cc2d19348b71a23cfdd42ca3e3f033475a37bbc4ab7c`.

Backups: `/tmp/sm2-i960-package-20261008/installed-backup/`.
No commits, pushes, dependency installation or changes to other projects.
