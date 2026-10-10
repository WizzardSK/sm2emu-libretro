# Upstream CPU And SCSP Package

Date: 2026-10-10
Platform: macOS ARM64
Status: Integrated And Locally Qualified

## Imported Changes

- `760a5567e7cd805d461ef532516a87fb20071634`: bounded direct i960
  instruction/operand fetch from ROM and work RAM on all four boards; direct
  MB86235 program fetch and empty-input-FIFO wait skipping on Model 2C;
  settled SHARC host-flag wait-loop skipping on Model 2B.
- `ec9c3acc162a0b145c0a2e4b26af674ac005866a`: SCSP PLFOS depth index 3
  changes from 6 to 8. The unused `FM_FRAC_DIV` cleanup in `2da8759` was
  already present locally; no redundant source change was needed.

The CPU package is applied in its original source locations. The i960 header
hunk was placed beside the existing port rounding setter. No Libretro headers,
frontend callbacks, new Core Options or dependencies enter the machine layer.
Gain, Enhanced Audio Balance, filters, inputs and NVRAM policies are unchanged
by this package. Gun changes from `b4c0931` remain a separate roadmap candidate.

The complete integrated baseline remains `5ddf84a` (0.9.13), with these selective
imports recorded separately. The advertised core version remains 0.9.13.0.

## Reference Builds

Pristine sources were archived at `2e056f29109d319fe8eb58e6a7fbd323b531ced7`
(before) and `ec9c3acc162a0b145c0a2e4b26af674ac005866a` (after, including
`760a556`). Release ARM64 standalone builds passed with Vulkan/OpenGL disabled
for software comparisons. The canonical mainstream checkout was not changed.
Local standalone, frontend-free headless and GPU-capable Libretro builds pass.

All seven existing dependency pins match both references:

| Dependency | Revision |
| --- | --- |
| SDL | `147a8ee32dbf9ac02f3794964490687b6bbda1bc` |
| VulkanMemoryAllocator | `1d8f600fd424278486eade7ed3e877c99f0846b1` |
| ImGui | `85b2fe8486190fa9326565a2fb5fccb6caea4396` |
| Miniz | `77d0dce8627735138c51770d1799a1ef48f2117d` |
| Musashi | `313ebf1bd9f4d0d93341eb5ce21fd8a119e9dbdd` |
| Pugixml | `ee86beb30e4973f5feffe3ce63bfa4fbadf72f38` |
| YMFM | `81aec25ccbb98f4873a255f7551ac4dadac59b4a` |

## Accuracy And State Checks

The existing `compare-headless.py` runner qualifies Daytona (original), VF2
(2A), Sega Rally (2C) and HOTD (2B), each at 1,800 frames. Both the previous
port and the new port independently match their respective pristine reference
on all seven checks: final video, audio format, PCM, native NVRAM, frame count,
master cycles and main CPU state.

The Libretro ABI runner covers the same four boards in separate processes,
with synchronous software rendering, native timing, automatic initial NVRAM
disabled and EAB disabled for matched comparisons. It verifies deterministic
Save State replay, two run-ahead/rewind cycles and corrupt-state rejection.
Previous-core format-10 states load in the new core; 120-frame continuations
produce identical video and PCM on all four boards. New fetch bindings are
not serialized; state format and published state-reading compatibility remain
unchanged. MB86235 skipped stalled retries can reduce its diagnostic instruction
counter; full old/new machine-state binary equality is not required.

Old/new boot video is identical on all four boards. PCM is identical for
Daytona, VF2 and HOTD. Sega Rally PCM changes; both sides exactly match their
own pristine reference. A ROM-free SCSP probe produces 8,192 stereo samples
at depth indices 0, 2, 3 and 4: only depth 3 changes, and every port result is
byte-identical to the corresponding pristine result.

Focused i960 checks exercise short buffers, address-window limits, both windows,
bus fallback, unbinding, live RAM changes, reset and state restore into another
backing allocation. Audio checks cover depth-3 modulation and sample-exact
LFO continuation, alongside existing filter and DSB2 checks.

The sound-timing check had stale version-6 assumptions before this import,
reproduced against untouched pre-import libraries. Its legacy conversion now
explicitly targets version 6; current-format checks account for the existing
optional auxiliary-board field. The corrected check passes, including invalid
phase rejection and rollback. This changes the fixture, not serialization.

## Bounded Performance Measurement

Two 1,800-frame ABI replays with Coin/Start/action inputs were run per core,
alternating old/new order. Old/new video and PCM match in these measurements.

| Game | Previous Median | New Median | Process-Time Reduction |
| --- | ---: | ---: | ---: |
| VF2 | 5.234 s | 4.872 s | 6.9% |
| HOTD | 10.596 s | 6.245 s | 41.1% |

These are whole ABI-process times, including startup, Python callbacks and
output writes. They demonstrate a local improvement in these fixtures; they
are not RetroArch FPS measurements or a promise for other games/platforms.

## RetroArch And Installation

The existing VF2 replay completes 2,300 frames in RetroArch Nightly 1.22.2:
the inspected screenshot shows the second fight set, PCM capture contains
1,840,690 stereo frames with peak 19,781, and the process exits cleanly.
This verifies automated gameplay input and audio production; physical controls
and acoustic fidelity are not established by the replay.

Both installed local copies, `sm2_libretro.dylib` and `sm2_dev_libretro.dylib`,
were backed up and replaced atomically, then checked for matching SHA-256,
25 ABI exports, dependencies and three empty lifecycle cycles. The authoritative
external System `games.xml` already matched the repository and was verified.

- Previous core: `5597cb0b98748757e9de48d359efe760c1d397dc02fcfcfaf909fa0498db3253`
- Installed core: `abda589c10b47acfe472f41bc2e57ec5682edd512b469bbbef490ef6ac6f15fe`

## Evidence And Limits

Ignored local evidence: `build-libretro-gpu/validation/upstream-cpu-scsp-20261010/`.
It retains pre-import sources/libraries, task-only diff, pristine build logs,
comparison JSON, SCSP probes/PCM, state files, performance runs, RetroArch
replay/captures, installed backups and deployment checks. Failed initial
baseline comparisons were caused by the relocated headless executable lacking
its database; staging the unchanged database resolved them, without repeating
the successful upstream runs.

No ROM data is added to Git. Linux/Windows runtime, hardware rendering throughput,
every game and physical-device/audio fidelity are outside this local package
qualification. No commit or publication was performed.
