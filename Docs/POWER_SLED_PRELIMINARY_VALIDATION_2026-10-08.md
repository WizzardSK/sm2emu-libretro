# Power Sled Preliminary Validation — 2026-10-08

## Findings and Changes

Two independent defects were found during preliminary validation:

- Main and Relay share their ROM chips; Main applies three program patches. Automatic identification previously chose Main first for both archives. The frontend-neutral ROM loader now uses the archive stem only to break an exact match-score tie. Better chip matches retain precedence; explicitly selected sets retain precedence; renamed archives retain CRC identification and catalogue-order fallback for unresolved ties. No new option is added.
- The 15-byte same-process replay divergence belongs to the communication frame buffer and shared communication RAM. The in-process loopback transport retained future queued frames after restoring the machine because its queue was absent from the archive. This is emulated local state, even without external networking.

Machine Save State format **8** records the local queue and overflow flag through `M2Comm`, bounded to 64 frames of at most 4,096 bytes each. It retains formats **4/5/6/7** on read. Older states omit this queue: loading them clears future local frames, but cannot reconstruct the missing original queue. Cross-cabinet transport sessions remain outside the machine archive and frontend session restrictions remain applicable. The fixed 9 MiB Libretro capacity and 96-byte frontend tail are unchanged. No emulation scheduling, cabinet wiring, Core Option, NVRAM default or game-support status changes.

The previous Relay ABI evidence actually exercised Main. Its label must not be used as independent Relay proof. The current tests verify the loaded identity in logs: `powsled`, `powsledm`, and `powsledr` respectively. Previously created states from an automatically misidentified Relay archive carry Main identity and Main program execution; they are not valid Relay states and are not relabelled or converted by this fix. The historical-format compatibility checks below use matching game identities. No existing user files were migrated.

## Verification

Evidence directory: `/tmp/sm2-powsled-validation-20261008/`. Generated states, recordings, saves and ROM data remain outside Git.

| Check | Result |
| --- | --- |
| Power Sled, Main and Relay, 600 frames each | Correct identities; immediate round-trip, exact three-frame machine replay, corrupt-state rejection, four run-ahead cycles and reverse-order rewind pass |
| Fresh process, all three variants | Format-8 state from frame 600 plus three frames reproduces continuous frame 603 video and the corresponding complete PCM tail exactly |
| Regression: Daytona, VF2, HOTD, DOA, Top Skater | All four boards plus DSB2: round-trip/replay/run-ahead/rewind pass; old/new 600-frame video and complete PCM identical |
| Historical formats | Five real format-7 states load in fresh processes and pass replay; additional VF2 format 4, Daytona format 5 and VF2 format 6 loads/replay pass |
| Synthetic loader checks | Named Relay avoids Main patches, explicit Main selection wins, unresolved renamed tie retains catalogue order; existing BIOS precedence/split/clone checks pass |
| Synthetic local transport checks | Pending frame restoration, future-message removal, overflow restoration and rejection of excessive counts/frame lengths pass |
| macOS builds | Core, headless and standalone pass |
| Linux x86_64 | Core build, loader/transport checks and 25-export ABI/dependency/empty-lifecycle audit pass using the existing builder |

A fresh 1,800-frame comparison with pristine `e8d96c1` was retained for all three variants. NVRAM and master cycles agree; final CPU/video and PCM length do **not** match. The pristine revision predates previously integrated timing/render/audio packages, and the updated headless output has one additional silent stereo sample. This is not reported as exact upstream equivalence. Separate pre-turn/current-core comparisons preserve Power Sled/Main video, complete PCM and NVRAM; the earlier package's exact pristine comparison remains historical evidence for that earlier code only.

## Installed-Core RetroArch Results

Actual RetroArch 1.22.2, installed core, Vulkan 2×, 2,300 frontend frames, isolated fresh saves, bounded cabinet-button and P1-handlebar replay:

| Set | Captured Screen | Recorded PCM | Exit |
| --- | --- | --- | --- |
| `powsled` | SYSTEM SHUTDOWN | Silent | Clean |
| `powsledm` | 3D GAME OVER scene | Silent | Clean |
| `powsledr` | SYSTEM SHUTDOWN | Nonzero, peak 706/32767 | Clean on repeat |

Main reaching a 3D screen is not complete gameplay/input proof. Relay producing nonzero samples is not sound correctness or listening validation. Only the upstream P1 handlebar pair is currently mapped; P2 Entry/Call buttons do not establish a complete second rider. All three sets remain `preliminary="true"`. Linked-cabinet gameplay remains unverified.

The first Relay launch ended with SIGBUS. The saved macOS report identifies `image_texture_load_internal` → `gfx_display_reset_textures_list` → `ozone_context_reset` during RetroArch initialization, with an OS file-page-in error. The repeat completed cleanly. This report does not establish a core-emulation crash; the failed attempt remains in the evidence directory.

## Deployment and Remaining Work

Both local RetroArch cores were atomically replaced after backups and verified against the final build:

`d37c1deef7ec2e7d8f0e96b52d4d839eee3cc27957c48b6fffe5ddf900485dd1`

Preliminary validation remains open for actual gameplay, sound, complete controls and the shutdown condition. The separate operator-menu/NVRAM campaign remains the next planned investigation; no NVRAM values are guessed or written into user saves. No TGPulse edits, commit or push. The adjacent mainstream checkout remains clean.
