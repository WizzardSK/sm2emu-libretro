# Upstream Sound 68000 Timing Package — 2026-10-08

## Scope

Selective timing backports, with the complete baseline still at upstream
`5ddf84ae7970a9bce1d0a17b3900d26065de1996` (0.9.13):

- `def088c52408d505667e75b925b812ffa1f2641a`: the required full-clock,
  sample-locked 68000 scheduler, bus stalls and active-slot cache.
- `8e1e7c3523ec83a7e37b255fe647816dab9023ae`: execute Musashi before reading
  the stall accumulator, eliminating compiler-dependent evaluation order.
- `71a81e3508fa28c8767f666e092898200e121c2c`: fixed two-cycle RAM/SCSP bus
  waits plus the voice-dependent contention term.

The SCSP clock produces one sample per 256 sound-CPU cycles. Instruction
overshoot carries into the next budget. RAM/SCSP accesses charge two cycles
plus `(12 * active_slots + 16) / 32`; ROM/sample accesses retain the upstream
address-window rules. The cache tracks actual slot starts/stops and is rebuilt
on reset/load; it adds no serialized field.

The FM modulation changes in `def088c` are **not** included here. SCSP synthesis,
MADRS/filtering, clipping, per-game balance and music-loop changes remain in
their respective roadmap packages. Source Gain, Enhanced Audio Balance,
Music Volume, defaults, labels and Core Option visibility are preserved.
The source Gain stage still scales generated SCSP samples before DSB mixing.
The original Model 2 / Model 1 sound-board path does not acquire SCSP waits.

## Save State Compatibility

The upstream scheduler repurposes two 64-bit state fields. Merely keeping their
byte count would make old states interpret sample/cycle carries incorrectly.
This port therefore writes **machine format 5**, accepts published **format 4**,
and supplies the source version through the frontend-neutral Archive.

On reading format 4, the sound scheduler converts the half-clock cycle carry
and overshoot into full-clock units and converts the independent sample carry
into a sample phase. The phase is quantized to the new 256-cycle sample grid;
this resumes under the corrected scheduler, not the old timing algorithm.
Subsequent saves write format 5. There is no external migration script or
in-place file rewrite. Older cores reject the new header before applying it.

The payload field widths and fixed Libretro size (9,437,184 bytes) are unchanged.
The existing 96-byte frontend tail is unchanged. Invalid scheduler values fail
transactionally and restore the previous machine snapshot. These rules apply
to the existing platform/endianness-dependent format; cross-platform state
portability is not newly promised.

## Verification

Evidence: `/tmp/sm2-sound-timing-20261008/`.

| Check | Result |
| --- | --- |
| macOS core, headless and standalone | Builds passed |
| Linux x86_64 core | Existing GCC 12/LTO build passed |
| ROM-free sound timing checks, macOS and Linux | Synthetic 68000 RAM reads consume wait cycles and complete fewer instructions; one host second produces 44,100–44,101 samples at the full sound clock; slot-cache reset/load, old-field conversion, unchanged payload size and invalid-state rollback pass |
| Linux Netpacket checks | Passed with the new state envelope; this is not a linked-cabinet device test |
| Exact pristine sound-board comparison | Unmodified upstream `71a81e3`, with verified matching submodule pins; identical traces for synthetic eight-slot contention and real VF2, Sega Rally, House of the Dead and Top Skater sound programs |
| Scope of isolated trace | One host second, ten checkpoints: CPU registers/cycles, sample counts, active slots and accumulated PCM; real programs run without host game/MIDI commands, so this is boot/timer proof, not musical quality or attract-tempo proof |
| Four-board Libretro/headless comparison | Daytona (Model 2), VF2 (2A), Sega Rally (2B), HOTD (2C), 1,800 frames each: exact video, full PCM and NVRAM agreement with the updated headless machine |
| Existing original Model 2 path | Daytona previous/updated core video and full PCM identical over 1,800 frames |
| Current Save States, five titles including Top Skater/DSB2 | 1,800-frame runs pass immediate restore, deterministic replay, corruption rejection and the runner's run-ahead/rewind checks |
| Actual previous-core format-4 states, fresh updated processes | All five titles load, advance 180 frames and pass round-trip/replay checks; subsequent saves use format 5 |
| Old binary reading new state | Previous core refuses a new VF2 format-5 image correctly |
| Installed macOS core, RetroArch 1.22.2, Vulkan 2× | 2,300-frame VF2 input replay, inspected in-game capture, non-silent PCM, 16,576-byte Save RAM, exit 0 |

### Comparison Conditions and Limits

The initial whole-machine comparisons against pristine `71a81e3` differ in
video, CPU/NVRAM and/or PCM. That revision includes other upstream CPU, game
metadata, SCSP and balance changes that this selective port has not fully
imported. The individual differences have not all been localized; those runs
are not reported as passing or as proof of a port regression. The isolated
sound-board comparison establishes parity of this package independently.

Libretro/headless checks disable Automatic Initial NVRAM Setup and the port's
i960 rounding option, select synchronous Software rendering, and hide HOTD
frontend crosshairs. Without matching these conditions, initial templates,
one-frame asynchronous presentation and overlays differ by design. HOTD's
remaining image difference before disabling the overlay was exactly 160 pixels
inside the central 24 × 24 crosshair area; PCM/NVRAM already matched.
Production defaults are unchanged.

The RetroArch capture proves game progression and actual frontend audio output;
subjective sound quality, long attract-mode tempo against a cabinet recording,
and the pending synthesis/clipping corrections remain separate work.

## Reusable Checks

- `sm2-libretro-sound-timing-checks` is built with `SM2_LIBRETRO_CHECKS=ON`
  and added to the existing CI ROM-free check step. CI itself has not been run
  remotely in this package.
- `scripts/compare-sound-timing.py` builds an external probe against existing
  native Ninja link settings. It changes neither source tree and keeps all
  ROM-dependent output external. Provide `--adapted-source`, `--adapted-build`,
  `--upstream-source`, `--upstream-build`, `--rom-directory` and a new `--output`.
  Its default game list is VF2, Sega Rally, HOTD and Top Skater; the synthetic
  eight-slot trace is always included.
- Existing `smoke-libretro.py --state-output` / `--state-input` checks remain
  the published-state producer/consumer path.

## Installation

Both `sm2_libretro.dylib` and `sm2_dev_libretro.dylib` were atomically replaced,
backed up and verified against SHA256:

`0a8219078dd3a2f8939089b64fd7855d0bd680065d34ac9f8854dd5759527243`

No TGPulse changes, dependency installation, commit or push. The adjacent
mainstream checkout remains clean.
