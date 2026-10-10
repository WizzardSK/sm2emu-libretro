# TGPulse-Next Interchange — Audio Gain Option Migration

Date: 2026-10-07
Origin: SM2-Emu Libretro frontend consistency review
Destination: the TGPulse-Next Libretro project chat

## User request and ownership

The user wants changes to TGPulse-Next made and reviewed in its own project chat, using this interchange file to transfer the requirement and evidence. This SM2 chat must not edit the TGPulse-Next repository for this follow-up.

Latest user decision: keep this KISS. Read legacy `Mute`/`mute` as the same effective mute, but use canonical `0` whenever the option is subsequently written through the frontend. Do not force a file rewrite simply because the core read an old value. Keep the visible order Auto, Mute, 10% through 100%, with Mute represented by `0`.

## Observed state

- `crates/tgpulse-libretro/src/lib.rs`: `gain_option()` reads legacy `Mute`/`mute` as zero. The registered selector now uses `auto`, `0`, `10` through `100`, displaying `0` as `Mute`.
- The core does not currently rewrite a saved `.opt` file, ask the frontend to replace its stored option, or reload that file.
- `tools/migrate_audio_gain_options.py` is an external offline tool. It scans supplied option files, previews changes by default, and with `--apply` replaces selected legacy Gain values after making `.bak` copies. The README instructs the user to close RetroArch first.
- The TGPulse checkout already contains local, uncommitted changes. Inspect its status and preserve unrelated changes before working.

## Work for the TGPulse project chat

1. Inspect the current TGPulse adapter and RetroArch Core Options lifecycle. Verify that saved legacy `Mute`/`mute` actually reaches the core on load; the frontend may reject a value removed from the registered selector. Preserve the user's effective mute setting across upgrade.
2. Register canonical `0` for new selections and use it whenever the option is later written. Avoid direct writes to the frontend-owned `.opt` file and avoid eager migration on read. Use a frontend callback only if necessary to preserve the requested read-old/write-new behavior.
3. Verify old `Mute`/`mute`, new `0`, `Auto`, unrelated options, and per-game versus global option files in isolated RetroArch configurations. Check the effective output and saved value after a user change and reload.
4. Reconcile the README, roadmap, and need for the external script with the verified behavior. Complete changes and verification in the TGPulse chat before requesting any publication step.

## Related SM2 state

SM2's newly added source Gain selectors store displayed `Mute` as `0`; these Gain keys were absent from its last published revision. SM2 now uses `60 Hz (Default)` and `57.524 Hz (Native Model 2)` for timing, with raw values `60hz` and `native`. An existing SM2 `60hz` option selects a new machine frame per callback and retains that raw value on its next save. This supersedes the earlier three-choice SM2 draft. Its Section 8 roadmap tracks the shared frontend wording review.

## A/V Timing Convention for the TGPulse Project Chat

The user approved the same two-value timing convention for TGPulse-Next:
`60 Hz (Default)` and `57.524 Hz (Native Model 1)`, in that order. Model 1 uses
`CPU_HZ = 16,000,000` and `CYCLES_PER_FRAME = 656 × 424`, yielding
57.524160147... Hz; the three-decimal display value is therefore 57.524 Hz.
Keep `60hz` and `native` as the raw values. Change the default from `native` to
`60hz` in both Core Options V2 and the legacy frontend fallback; an existing
saved `native` must still select native timing. Preserve one new machine frame
per callback at 60 Hz, the current audio resampling behavior and Save State
continuity. Verify the two visible values, default, explicit saved `native` and
`60hz`, and a bounded RetroArch run in the TGPulse project chat. Do not edit
that repository from this SM2 chat.

The TGPulse Gain menu and legacy-value behavior remain a separate follow-up in
its own project chat until verified there.

## Source Gain Labels — 2026-10-08 Correction

Remove the misleading ` (Absolute)` suffix from all source Gain labels, in
both Core Options V2 and the legacy fallback. Use `MultiPCM 1 Gain`,
`MultiPCM 2 Gain`, `FM (YM3438) Gain` and `DSB (MPEG) Gain`. The source Gain
is a scaling factor; final output also depends on the mix and Master Volume.
Keep Auto, Mute, 10% through 100%, their order, default and saved values.
Update label assertions and documentation. SM2 already applies this correction.
Implement in the TGPulse project chat; this file does not change that checkout.
