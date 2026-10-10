# Upstream Save State Package — 2026-10-08

## Imported Change

Imported upstream `1a60affc251dd9992044013650dbe24075221593` (cross-session
68000 Save State crash fix) without changes to `src/cpu/m68000/m68000.cpp`.
The resulting file matches that upstream revision byte-for-byte, SHA-256
`4853574681bc1ca94aec1f350b89589769c259168edca7132f077d32a7075456`.

Musashi's serialized context contains host callback and cycle-table pointers.
On load, those pointers are rebound to the current process and the refreshed
context is copied back before applying IRQ state. Emulated registers and the
serialized layout are preserved. The integrated baseline remains
`5ddf84ae7970a9bce1d0a17b3900d26065de1996` (0.9.13), plus this explicit backport;
this is not an import of all upstream changes through 0.9.17 or 0.9.40.
Submodule pins are unchanged, including Musashi
`313ebf1bd9f4d0d93341eb5ce21fd8a119e9dbdd`.

## Dependency Review

The newer SCSP serializer stores the output low-pass filter history and
recomputes the cached active-slot count. Those members belong to the pending
SCSP audio implementation. DSB2 changes `m_playing` to `m_mp_state` to preserve
its new playback/loop state; this belongs to upstream `830f751` and the pending
Top Skater loop fix. Both serializer changes must ship with their owning audio
changes and receive a format compatibility/rejection review then. No unused
fields or incomplete audio behavior are introduced in this package.

## Verification

Evidence directory: `/tmp/sm2-state-package-20261008/`.

- Release builds: Libretro, headless and standalone macOS arm64 passed.
- Pristine upstream 0.9.13 was built from a Git archive in the evidence
  directory using the existing dependencies at matching pins. The adjacent
  mainstream checkout was not modified.
- `scripts/compare-headless.py`: 1,800 frames each for Daytona, VF2, STCC,
  Virtual-On and Top Skater. Updated headless matches pristine upstream in
  video, PCM format/data, NVRAM, frame/cycle counts and CPU state.
- Old versus updated Libretro: the same five titles cover all four Model 2
  boards, the early MultiPCM board, SCSP, DSB and DSB2. Each runs 1,800 native
  frames and 20 Save State stress cycles. Video, PCM and NVRAM match; corrupt
  states are rejected; run-ahead and reverse-order rewind patterns pass.
- Cross-process compatibility: each title produces a state with both the old
  and new core. Separate processes load those files with the updated core,
  advance 180 frames, and repeat 20 stress cycles. The resumed video, PCM and
  NVRAM match for old/new input states. All ABI buffers remain 9,437,184 bytes.
  Aggregate evidence: `matrix-result.json`.
- `scripts/smoke-libretro.py` now accepts `--state-input PATH` to reproduce
  cross-process loads; `--state-output PATH` supplies the producer file.

## Local Installation

Both `sm2_libretro.dylib` and `sm2_dev_libretro.dylib` under the configured
RetroArch cores directory are updated; SHA-256:
`090fe9ea9247197ffdb097fd04358e7fe2735377fba0373add58be3532f5a889`.
The external `system/sm2-emu/games.xml` already matches the source copy.

An initial in-place overwrite caused macOS to report CODESIGNING Invalid Page
although disk signature verification passed. Replacing each library with a
fresh temporary file and atomic rename resolved the launch failure. The crash
also triggered macOS's reopen-windows dialog, which blocked a subsequent
runner before RetroArch initialized. The test-owned app was launched with
Don't Reopen. Test configuration, saves and results use separate directories;
RetroArch still emitted global history/runtime-log updates.

## Frontend Validation and Runner Diagnosis

Passed with installed macOS arm64 core, RetroArch Nightly 1.22.2
(`9be7ec92`), VF2, Software renderer with its default asynchronous threading.
Evidence: `retroarch-vf2-roundtrip-fixed/result.json` in the evidence directory.
The state file is 9,437,208 bytes (including RetroArch's wrapper).

- Save and load are both confirmed in the frontend log.
- The game region changes after saving and advancing.
- Saved/restored regions match exactly after two controlled frame steps on
  each path: SHA-256
  `a2c1b767604ee0a196242fd4ec90a4496bf7ffd1f5b23ebbeb75d0b2ce13d6e4`.
- A further screenshot proves the game advances after loading and resuming.
- Exit code 0; no forced termination.

The earlier failure was a runner race. RetroArch's screenshot task creates the
PNG before marking itself finished on a later task-queue iteration. The runner
immediately requested loading after seeing the PNG. Both screenshot and load
are blocking tasks; `task_queue_push` refuses a new blocking task while one is
still running. `content_load_state` does not propagate that rejection, and the
slot command's response is therefore not proof of a completed load. Waiting
before the load request resolved the missing load confirmation. Longer waits
*after* the rejected request, disabling the task thread, and bypassing the core
metadata check did not resolve it; those diagnostic overrides were removed.

Source reference at the installed frontend revision:
[task_screenshot.c](https://github.com/libretro/RetroArch/blob/9be7ec92/tasks/task_screenshot.c),
[task_queue.c](https://github.com/libretro/RetroArch/blob/9be7ec92/libretro-common/queues/task_queue.c),
and [task_save.c](https://github.com/libretro/RetroArch/blob/9be7ec92/tasks/task_save.c).

The runner now waits one second after the advanced screenshot, uses the explicit
`LOAD_STATE_SLOT 0` command, and requires log and image evidence in addition to
its acknowledgement. Both comparison paths advance two frames because loading
resets the asynchronous Software renderer's pipeline; capturing its first frame
would compare a temporary empty buffer against a rendered image. The test also
checks advancement using cropped game pixels, excluding notification changes.

A separate timing race in `wait_while_alive` could pass a negative duration to
Python's sleep when the deadline expired between checks; the duration is now
clamped to zero. Test configuration disables history/runtime-log writes and
achievements, and selects English log messages. User configuration is unchanged.

This proves one real frontend slot round-trip for VF2 on the installed macOS
artifact. The five-title ABI matrix above supplies the separate board coverage;
this frontend result does not imply all games or platforms were tested.

No commit or push was performed. These checks qualify macOS arm64; new Windows
and Linux artifacts have not been built or tested for this package.
