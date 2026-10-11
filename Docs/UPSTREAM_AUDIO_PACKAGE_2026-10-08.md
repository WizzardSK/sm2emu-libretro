# Upstream Audio Package — 2026-10-08

## Scope

Selective imports from upstream; the full integrated baseline remains 0.9.13
(`5ddf84ae7970a9bce1d0a17b3900d26065de1996`).

- SCSP FM address/fraction modulation (`def088c`), unmapped MADRS register
  correction (`abb42bb`), and PLFO depth/fractional FM blending (`e1aafb7`).
- MultiPCM voice summation without premature per-chip clipping (`cb57c0a`),
  retaining the port's source Gain, final board clipping and existing balance.
- DSB2 deferred loop windows and looping playback (`830f751`). Out-of-range
  MPEG windows remain rejected. Per-game gain tables are not imported here.
- Upstream 5 Hz DC blocker (`5e77a08`): upstream SDL implementation for the
  standalone target, frontend-neutral output processing in the Libretro adapter.
  Queued samples are filtered once, including the resampled 60 Hz path.

## SCSP Output Low-Pass Filter

Upstream `e1aafb7` initializes an 8 kHz two-pole Butterworth output filter and
serializes its history, but does not apply it to the generated samples. The
user explicitly requested a selector to enable it in this port.

| Property | Contract |
| --- | --- |
| Category / Label | Audio / SCSP Output Low-Pass Filter |
| Key | `sm2_scsp_output_low_pass_filter` |
| Choices, in order | `disabled` / Disabled; `enabled` / Enabled |
| Default | Enabled (user-approved 2026-10-11) |
| Application | Immediate; switching clears the old filter history |
| Visibility | All games; no effect without SCSP |
| Scope | SCSP output after master gain; separate MPEG music is unaffected |

The output filter runs inside the frontend-neutral SCSP implementation, reached
through a neutral SoundBoard setter. Machine and chip code do not depend on
Libretro headers. The selector is a frontend preference; it is reapplied on
content load, option updates and Save State load. Applying the same preference
does not clear restored filter history. Standalone behavior remains unfiltered.

This optional 8 kHz low-pass is distinct from the standard 5 Hz DC blocker at
the final audio output.

## Save States

Machine format 6 reads formats 4, 5 and 6. Format 4 retains the previous sound
scheduler conversion. Four SCSP filter-history floats add 16 bytes to applicable
machine payloads; old formats initialize them to zero. Non-finite SCSP filter
history is rejected. DSB2 reads the old playing boolean as stopped or one-shot
playing; the old payload does not encode a reliable loop state. New states
preserve stopped/playing/looping explicitly.

Libretro capacity remains 9,437,184 bytes. The existing 96-byte frontend tail
uses its last 16 bytes for stereo DC-filter input/output history, with a presence
bit. Older tails initialize that history to zero. Older cores safely reject
format 6. No option file migration is required for the new disabled default.

## Verification

Evidence: `/tmp/sm2-audio-package-20261008/`.

- macOS ARM64 core, headless and standalone builds pass.
- ROM-free audio, sound-timing and Core Options/Save RAM checks pass.
- Actual SCSP mixer tones verify preserved 1 kHz energy and attenuated 15 kHz
  energy; enabled-filter Save State continuation is sample-exact; switching
  off restores identical bypass output. Invalid filter history is rejected.
- Isolated sound-board comparison against pristine upstream `e1aafb7` passes
  exact CPU/sample/PCM traces for synthetic eight-slot FM/PLFO activity and
  booted VF2, Sega Rally, House of the Dead and Top Skater sound programs.
  This is not a whole-machine or subjective playback comparison.
- Ten fresh-process loads of format-4/5 states pass, with deterministic replay,
  for Daytona, VF2, Sega Rally, House of the Dead and Top Skater, filter enabled.
- VF2 60 Hz Full Frames, filter enabled, backpressure and state replay pass.
- Synthetic valid MPEG Layer II frames verify DSB2 loop continuation, restored
  decoder/loop state, stop and invalid-window rejection.
- DC tests cover both board sample rates, stereo independence, settling,
  callback chunking and restored history.
- Installed-core RetroArch 1.22.2 VF2 run with Vulkan 2x and filter enabled
  passes: 2,300 frames, gameplay capture inspected, stereo audio peak 16,382,
  clean exit. This does not replace subjective listening. The sandboxed app
  launch exited before logging; the authorized native launch passed.
- Core Option tests verify exactly two choices, disabled default, enabled
  selection and visibility across the game catalog.

## Deployment and Remaining Review

Both installed macOS cores were replaced atomically with backups and matching
SHA-256: `66284f6a588bf0ba0da192d661d2d0e777fe68b663798cbe106701d3a9374dec`.

Backups: `/tmp/sm2-audio-package-20261008/installed-backup/`.
CI includes the new ROM-free audio checks. Subsequent i960 package validation
passes the Linux x86_64 build, audio/timing checks and ABI audit; see
`Docs/UPSTREAM_I960_PACKAGE_2026-10-08.md`. Remote CI, native Batocera and Windows
runtime validation have not been run for this package. Subjective sound and
real-game long-duration music looping remain listening checks. The later
per-game Audio Balance analysis remains open. No other project was edited.

## Subsequent Native Qualification — 2026-10-09

Per-game Audio Balance reconciliation is complete; see
`UPSTREAM_AUDIO_BALANCE_PACKAGE_2026-10-08.md`. The current Linux core now passes
actual Batocera SCSP/filter, MultiPCM and sustained/repeated real-content DSB2
output checks. See `NATIVE_BATOCERA_AUDIO_VALIDATION_2026-10-09.md` for artifact
identity, the native Sound Test path and non-bit-exact repetition limits.
Subjective listening and current Windows frontend qualification remain pending.

## Default Update — 2026-10-11

Following successful user listening checks, the user chooses Enabled as the
Libretro default to approximate the board's analogue output response. Missing
saved values also enable the filter. Explicit saved Disabled remains respected;
no user configuration is rewritten. This changes only the frontend default,
not the filter coefficients or standalone behavior.
