# Frontend Menu And Audio Reset Review — 2026-10-18

## Scope And Artifact

Reviewed the installed normal SM2-Emu 0.9.44.0 core, SHA-256
`ce1a48cd89a6ca88368cd6ccdc0348427cfee21771ce2a66ef9e1e24e9a177e7`,
with VF2 in an isolated RetroArch ARM 1.22.2 session. The runner copied the
user's base configuration into its own directory and owned only its process,
Core Options and Save RAM. No installed core or emulation source was changed.

## Visible Core Options

Actual Ozone pages were observed through native-window screenshots:

- System: ROM CRC Verification, i960 fix, Automatic Initial NVRAM Setup,
  Linked Cabinets, Auto Network Role Settings and NVRAM Settings appear in
  functional order. Both network controls say Not Supported for VF2.
- Video: Renderer is followed immediately by Software Renderer Threading;
  2D Layer Upscaling Filter precedes 3D Texture Filtering.
- Audio: Music Volume, Enhanced Audio Balance, SCSP Gain and SCSP Output
  Low-Pass Filter appear in the approved sequence, followed by the
  applicable later audio controls.
- Input: Controller Profile Type is first, Gamepad Rumble second, followed
  by the lightgun and gear groups.

This closes the formerly missing **category-page visual acceptance**. The
complete 452-definition V2/legacy and 48-row workbook audits remain the
source of full option coverage; this visual pass did not scroll and inspect
every individual dynamic NVRAM entry. No screenshots were saved as files.
One isolated menu value was temporarily toggled and restored before exit.
The runner reported exit 0, no forced kill and no residual process in
`build-libretro-gpu/validation/framework-menu-audio-20261018/frontend/result.json`.

## Audio Reset Architecture

SM2 has no asynchronous frontend audio packet queue or producer thread to
prime. Each `retro_run` collects stereo samples from the machine sound board
into `Content::audio` and passes them to the Libretro audio callback. The
vector's length represents pending samples; a short callback acceptance
leaves the remainder for the next run. A one-second bound catches a stalled
frontend. A configured machine reset clears native pending samples and the
adapter vector, resets its DC filter and audio timing counters. The native
sound-board reset also clears its own pending vector and restarts the sound
CPU/chips. Save-state load clears derived pending samples while restoring the
serialized timing state. There are no read/write packet indices, ambiguous
empty/full state or blocked producer to repair with Supermodel's two-packet
startup procedure.

## Reset Evidence

`scripts/smoke-libretro.py --audio-reset-test` now exercises the installed
core with the reviewed VF2 Difficulty setting. It captures 360 frames at
startup, after changing Difficulty to Hard with NVRAM Settings enabled, and
after each of two explicit resets. The option path emitted the automatic
machine-reset notification. At native 57.524 Hz, all four segments delivered
275,989 stereo frames through 360 batch calls, with 288,182 nonzero samples
and the same PCM SHA-256. At 60 Hz, all four delivered 264,600 stereo frames
through 360 batch calls, with 276,279 nonzero samples and another shared PCM
SHA-256. Results are in `build-libretro-gpu/validation/audio-reset-20261018/`
under `abi-native2/result.json` and `abi-60hz/result.json`.

An independent isolated RetroArch run used the CoreAudio output driver and
its WAV recorder with the normal installed core, Software/Asynchronous and
60 Hz options. Two actual **Command → Reset** actions visibly restarted VF2.
The finalized recording contains 5,142,060 stereo frames at 44.1 kHz
(116.6 seconds). PCM is active before each reset and resumes after the
approximately two-second native sound-initialization interval on both
resets. The normalized WAV and three short before/after excerpts are under
`build-libretro-gpu/validation/audio-reset-20261018/frontend2/host/`.
The runner's `result.json` reports exit 0, no forced kill and no residual
process. Its first window-positioning attempt was discarded as a runner
failure; the successful second run supplies the frontend audio evidence.

## Conclusion And Limit

No SM2-specific audio reset defect was reproduced. No queue priming or core
fix is justified by these results. Callback progression, nonzero PCM, real
frontend reset/video continuation, CoreAudio driver activation and WAV
recording are separate established observations. This agent cannot hear the
physical output in this environment; speaker fidelity and a user's subjective
listening judgment remain unverified. The local technical review is complete;
retain that listening limit when reporting broader audio qualification.
The existing Framework F12 criterion already covers this outcome; the
destination-specific results do not introduce a new shared convention.
