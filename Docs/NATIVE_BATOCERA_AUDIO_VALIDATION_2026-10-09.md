# Native Batocera Audio Validation — 2026-10-09

## Result And Scope

The current Linux core passes native RetroArch audio checks on Batocera for
SCSP/filter selection, original-board MultiPCM and Top Skater DSB2 music.
A separate Sound Test recording establishes sustained real-content playback
and identifiable repeated music. Subjective listening and current Windows
frontend qualification remain separate pending checks; the overall audio
roadmap row remains Partial.

No audio/emulation source, Core Option, dependency or installed core changed.
The existing frontend runner was extended to prevent premature replay EOF in
long tests and to accept an explicit existing input replay. ROMs, captures,
saves and generated bundles remain outside Git.

## Artifact And Host

- Batocera 43.1 x86_64, kernel 6.18.16, glibc 2.40.
- RetroArch 1.22.2, GCC 13.3.0 frontend build; native Vulkan 1× rendering.
- Existing Pulse/PipeWire HDMI sink; recording is frontend PCM, not a physical
  speaker/listening measurement.
- Tested Linux core SHA-256:
  `a7572a2865e757d5cc6eb17717428fa9216312c83c5f88a367ab9d032da5d80f`.
  This is the existing rendering-review artifact, exported without rebuilding.
  Audio/machine/adapter source hashes from the Linux snapshot match this checkout.
- Native `ldd` resolves all dependencies: baseline libc/libm and loader.
- The full integrated baseline remains 0.9.13
  (`5ddf84ae7970a9bce1d0a17b3900d26065de1996`) plus documented packages.

## Procedure

Reused `batocera-remote-core-test/scripts/remote-core-test` for read-only probe,
checksum-verified staging, bounded foreground execution and result retrieval.
Reused `scripts/smoke-retroarch.py` for replay, isolated configuration, screenshot,
PCM capture, Save RAM and normal frontend exit. The three ROMs already on
Batocera were read-only. Test data stays below marked
`/userdata/system/codex-core-tests/sm2-audio*-20261009` roots.

All runs use native timing, Faithful filters, Music Volume 100%, EAB Enabled
and source Gains Auto except SCSP Mute (`0`) in the isolated DSB2 probes.
No acquisition script or alternative emulator was used.

| Run | Frontend Frames | Stereo Rate | Recorded Frames | Peak / 32767 | Exit |
| --- | ---: | ---: | ---: | ---: | ---: |
| VF2, SCSP Filter Disabled | 2,300 | 44,100 Hz | 1,763,260 | 19,781 | 0 |
| VF2, SCSP Filter Enabled | 2,300 | 44,100 Hz | 1,763,260 | 19,012 | 0 |
| Daytona, MultiPCM | 2,300 | 44,642 Hz | 1,784,964 | 29,920 | 0 |
| Top Skater, Mixed Audio | 2,300 | 44,100 Hz | 1,763,260 | 12,704 | 0 |
| Top Skater, Gameplay With SCSP Mute | 18,000 | 44,100 Hz | 13,799,420 | 8,392 | 0 |
| Top Skater, Sound Test BGM 1 With SCSP Mute | 18,000 | 44,100 Hz | 13,799,420 | 8,311 | 0 |

Two additional 2,300-frame native menu probes verify Test Menu and Sound Test
navigation. All eight runs exit normally with code 0. The primary five SRAM
containers and final Sound Test SRAM have valid container CRCs. Gameplay
screenshots were inspected for VF2, Daytona and Top Skater. No physical
controller or audible-quality correctness is inferred from these captures.

## SCSP Filter Comparison

The VF2 captures have identical sample counts/rates, image pixels and complete
SRAM. Only output PCM changes. Hann-windowed 32,768-sample spectra from seconds
22, 26, 30 and 34 show:

| Band | Enabled Versus Disabled Power |
| --- | ---: |
| 100–1,000 Hz | −0.001 dB |
| 1,000–6,000 Hz | −0.183 dB |
| 10,000–20,000 Hz | −10.930 dB |

This verifies the enabled filter acts on actual native-frontend audio. It is
not a complete transfer-function measurement or a subjective sound review.
No samples at either signed 16-bit saturation limit occur in these captures.
The same saturation check also passes Daytona and both Top Skater long captures.

## DSB2 Coverage Diagnosis And Repeat

The first 312.912-second isolated gameplay recording contains music around
seconds 7–23 and 26–91, then returns to the start prompt and is silent. It passes
launch/capture/exit checks but does **not** qualify sustained music or a loop.
This observation is not classified as an emulation defect.

The native menu probe established Test A on RetroPad R3 and Service A on L3.
From the root EXIT selection, four Service steps select SOUND TEST, then Test
enters it. Two Service steps select BGM; Test changes BGM 0 to BGM 1. This is
recorded in the generated operator replay and its action/checksum manifest.
Only Sound Test commands are exercised; no calibration or NVRAM settings are
changed or acquired.

The final 312.912-second recording stays in Sound Test with BGM 1 selected.
Every complete one-second window from second 25 onward contains DSB2 output:
287 active windows, no silent windows. Nine four-second waveform passages from
seconds 26–42 reappear at the same sample offset of **262.908004535 seconds**.
Five of those passages are non-overlapping. Raw normalized correlations range
from **0.976855 to 0.982669**; simple fractional-sample alignment raises them to
0.981301–0.986017. Their common long offset identifies repeated musical content.

The exploratory strict correlation threshold above 0.99 was not met; it is
retained as false in the receipt. No bit-exact repeated PCM or decoder-branch
trace is claimed, and the precise cause of the residual waveform difference is
not established. The existing synthetic DSB2 exact loop, restore, stop and
invalid-window gates retain their separate qualification. This native check
adds sustained/repeated actual-content output evidence.

## Runner Changes

- Generate at least `max(2400, max_frames + 100)` replay frames so a bounded
  long test does not pause at the old 2,400-frame EOF.
- Accept `--input-replay PATH`, mutually exclusive with `--initial-state`;
  copy the explicit replay into the isolated output and record its SHA-256.
  Without this flag the established generated fixture remains in use.
- The operator probe derives releases and timed button presses from the existing
  replay-v1 96-entry fixture with RetroArch 1.22 padding. No new input format.

Python compilation and `git diff --check` pass. Native long runs verify that
replay EOF no longer interrupts the capture. No product menu or option changes.

## Preservation And Evidence

Local evidence root:
`build-libretro-gpu/validation/audio-batocera-20261009/`.

- `remote-results/`: primary five runs, matrix, preflight and initial preservation.
- `sound-probe-results/` and `sound-menu-results/`: native menu qualification.
- `sound-loop-results/`: final actual-content DSB2 recording and screenshot.
- `source-receipt.json`, `audio-review.json`, `sound-loop-review.json`,
  `final-preservation.json`: provenance, measured results and explicit limits.
- Local ignored bundles retain executable commands, staged hashes and replays.

The final read-only remote check confirms unchanged installed core/info,
global RetroArch configuration, all three ROMs and the existing VF2 SRAM;
no owned test process remains. Remote isolated bundles are retained for review.
The installed Batocera core was not replaced by the staged test artifact.

Both installed macOS copies still match the existing build SHA-256
`3200f0e99a527d186def9cced15f82e70e564c39e8e70881f02fae083dbc3d05`;
no rebuild or deployment is needed for runner/document changes. Manx TT remains
the final roadmap activity. No commit or push.
