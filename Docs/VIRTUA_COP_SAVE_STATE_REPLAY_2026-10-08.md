# Virtua Cop Save State Replay — 2026-10-08

## Scope and Findings

The current pre-fix core reproduced the existing first/repeated Software replay
mismatch at frames 1990–1991 (the older gun-input sequence reported 1988–1989).
Full machine snapshots were identical at frames 1986–1994. The below/above 2D
layers also matched; generated polygon texture coordinates differed. At frame
1990, 313 output pixels differed within x=436–495, y=202–217.

The geometry engine retains texture-coordinate/header RAM across display lists,
but its serializer omitted that RAM. A load therefore retained texture data
from the future execution. Saving/restoring this RAM removes the observed
difference. A fresh-process gameplay probe additionally exposed omitted
viewport/projection state; format 7 therefore saves all persistent geometry
registers and RAM, including matrices, lighting/texture parameters, clip
planes, texture/log RAM and both polygon RAM banks. No rendering algorithm or normal execution path was changed.

The six normalized bytes were the pitch/amplitude LFO steps of MultiPCM 0 slots
4, 15 and 21 (zero-based). In the original archive their offsets were 0x8ceb,
0x8cf2, 0x918f, 0x9196, 0x9417 and 0x941e, each changing from 9 to 0. Loading
recomputed the steps while rebuilding table pointers. A zero register write can
retain a previous step, so the archived step must be preserved independently of
the pointers. The loader now rebuilds pointers and restores both saved steps.

## Upstream Reference

The pristine e1aafb7 source used by the preceding audio package contains both
serializer behaviors. A ROM-free geometry probe submits a Texture Data Write,
saves, changes the value, and restores. The pristine serializer emits 16 bytes
and cannot distinguish the two RAM contents. The initial texture-only probe emits
131088 bytes, distinguishes the writes, and restores the original snapshot.
This is isolated serializer evidence; no complete pristine-upstream gameplay
replay comparison is claimed.

## State Compatibility

Machine format 7 adds 427395 bytes of persistent geometry state after the
existing geometry registers. The complete geometry serializer emits 427411
bytes (including the old 16-byte prefix). The fixed Libretro buffer remains 9437184 bytes, including the existing
96-byte frontend tail. Formats 4, 5 and 6 remain readable. Their omitted geometry
RAM cannot be recovered; this correction restores the persistent geometry state for
new format-7 snapshots. Older cores reject format 7. SRAM/NVRAM is unaffected.

Generated polygons and depth buckets remain transient. This change addresses
the reproduced Virtua Cop geometry issue; it is not an exhaustive audit of
every other machine device or every game's Save States.

## Verification

- Strict Virtua Cop campaign: 910 frames per sweep, first/repeated video exact
  with Hide Shot Flash Disabled and Enabled; machine and PCM comparisons pass;
  zero normalized machine bytes; active-flash restore/replay passes.
- Unchanged campaign PCM hash:
  `6a59655ce8a0d1193a23fff4e8f10c781624f64ec282aa7c05a2b13ea2807e1a`.
- Five-title previous/new 600-frame video/PCM comparisons pass: Daytona,
  Virtua Fighter 2, House of the Dead, Dead or Alive and Top Skater.
- Fresh-process format-6 loads, exact round-trip, three-frame replay, three
  stress cycles, rewind/run-ahead patterns and corrupt-state rejection pass on
  those five titles, covering all four board types plus DSB2.
- Real historical format-4 VF2 and format-5 Daytona snapshots load in fresh
  processes and pass subsequent round-trip/replay checks.
- macOS standalone, headless and core builds pass, as do input/audio checks.
- Linux x86_64 core build, input/audio checks and artifact ABI/lifecycle audit
  pass in the existing Debian 12 builder. This is not a native Batocera test.

## Reproduction and Deployment

Evidence root: `/tmp/sm2-vcop-replay-20261008/`. It contains separate pre-fix,
texture-only and final campaigns, diagnostic frame/component dumps, historical
state loads, old/new comparison JSON, probe sources/results and frontend logs.
Temporary diagnostic instrumentation was removed before the final build.

Run the persistent regression gate with the external ROM path:

```sh
python3 scripts/test-libretro-gun-flash.py \
  --core build-libretro-gpu/libretro/sm2_libretro.dylib \
  --system build-libretro-gpu/libretro/system --rom /external/roms/vcop.zip \
  --frames 2010 --strict-state-replay --output /tmp/new-vcop-state-check
```

Both local RetroArch core copies were atomically updated with backups:
`sm2_libretro.dylib` and `sm2_dev_libretro.dylib`.
SHA-256: `8e2a1822d1c993a04948ab02ba877caec0288f3d048947a87349d1217241e6e3`.

## Native RetroArch Round-Trip and Runner Diagnosis

The initial texture-only artifact passed the attract-scene screenshot test,
but gameplay captures failed with both initial and complete geometry snapshots,
in both asynchronous and synchronous Software modes. Those failures are kept
as diagnostic evidence, not counted as successful frontend tests.

A separate instrumented core correlated machine frame numbers with runner
commands. RetroArch had automatically paused at input-movie EOF. The runner's
unconditional initial Pause Toggle resumed execution: its state was saved at
frame 2460, while the reference image was captured around frame 2620. After
loading frame 2460, the two intended comparison steps produced frame 2462.
The test therefore compared different points in time.

The runner now queries GET_STATUS, requests a pause toggle only when necessary,
and verifies PAUSED / PLAYING before proceeding. The Original Model 2 board
rebuilds geometry every other frame; the asynchronous Software renderer adds
one presentation frame. The comparison therefore advances both sides by three
frames, not two. Frame Advance uses a configured key event directed only at
the owned RetroArch process. The diagnostic trace confirmed effective key
steps; no claim is made that UDP Frame Advance itself is defective. The frontend interface is
confirmed in [RetroArch 1.22.2 command.c](https://github.com/libretro/RetroArch/blob/v1.22.2/command.c#L972).
The default remains asynchronous Software; an explicit threading argument also
allows controlled synchronous checks. Diagnostic instrumentation was removed,
and the rebuilt clean core still matches both installed copies by SHA-256.

### Fresh-Process Validation

The ABI runner now completes first-frame SRAM import/seeding before loading an
external snapshot. That initialization can reset the machine; the former order
could test a reset boot rather than the requested snapshot. Format-4/5/6 and
format-7 load/replay checks above were repeated after this runner correction.
Requested frame counts exclude the bootstrap frame.

A fresh process restores the final Virtua Cop format-7 baseline and reproduces
the frame-1171 gameplay shot image exactly with the original input sequence.
See `fresh-vcop/` and `fresh-vcop.log`.

An additional Daytona uninterrupted-603-frame versus restored-600-plus-3 check
produces identical final video and exact matching final three-frame PCM. Raw
archives differ by 320 bytes (39 with the preceding core). Musashi serializes
host pointers and rebinds them on load, so cross-process raw byte equality is
not itself a portable semantic comparison. No cross-process raw-archive
identity is claimed; any broader audit must classify such fields first.
Evidence: `fresh-603-daytona/`, `restore-603-daytona/`, their `.state` files and
`daytona-cross-session-review.json`.

### Final Installed-Core Frontend Result

`retroarch-vcop-three-steps/result.json`: RetroArch 1.22.2, macOS ARM64,
installed final core, default asynchronous Software rendering, actual Virtua Cop
gameplay reached with the existing gun replay. Pause state is verified; three
identical comparison steps cover geometry rebuild and renderer latency. The
complete saved/restored PNGs match exactly (not only the OSD-free game region).
The scene changes during advancement, resumes after restoration, and exits with
code 0 without forced termination. No subjective audio or physical controller
validation is claimed.

Complete saved/restored PNG SHA-256:
`ac8a5d0052eb527018e92bad6ca055d72d01e987abdfa95adf0bb9abe3decbb3`.
Game-region SHA-256:
`1d1ef857b85b412ef4d817ecfa4b138ae2c96ff6c9459aacbed4859328520365`.

The corrected runner passed; the earlier mismatches are retained to document
why blind pause toggling and a two-step pipeline warm-up are invalid here.
