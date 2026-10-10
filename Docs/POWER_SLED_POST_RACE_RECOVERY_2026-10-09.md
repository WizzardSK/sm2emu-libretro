# Power Sled Post-Race Recovery

Date: 2026-10-09
Backend: Installed SM2-Emu Libretro In RetroArch Only

## Qualified Result

One uninterrupted Main / Relay / Slave session completes a Semi Auto race to
Game Over, shows black frames followed by SEGA, then accepts the same operator
sequence and starts a second race on both Main and Slave. The second race has
changing clocks, course movement, POSITION 1 and Time Extension. No reset,
Service/Test input, RAM write or calibration change is used to restart it.

The black/SEGA observations do not prevent another race in this tested cycle.
This result does not qualify finish-line crossing, final ranking, Manual mode,
every post-race transition or comparison with the original cabinet's timing.

All three native links pass the runner checks and all three programs exit with
code 0, without forced termination or residual owned processes. SRAM identity,
CRC, ANS colors and the existing calibration bytes are checked separately.
The production build and both installed copies retain their previous hash.
No emulation, Core Option, binding or installed-core change is required.

## Reusable Method

The existing race fixture repeats its operator pulses after 18000 local
frontend frames and retains 30000 frames so the movie remains active. Main
receives P1 Call, two P2 Calls and Start; Slave receives P1 Entry. Relay receives
no input. The offsets preserve the established staggered-start sequence.
Inputs are frontend frames, not synchronized native link clocks.

```sh
python3 scripts/test-power-sled-gameplay.py \
  --race-qualification --repeat-race --port 55516 \
  --output build-libretro-gpu/validation/power-sled-post-race-new-run
```

Use a fresh directory and free ports. The runner retains 26 observation frames
per program. Success of communication and cleanup is separate from visual
review of both races.

The first launch attempt stopped at window positioning before linking; its
single owned instance exited cleanly. A retry extending the window wait from
3 to 15 seconds ran successfully without a permission change. The shared runner
now uses that bounded wait. The exact private wrapper and retry command are
retained so this verification can be reproduced; other lifecycle code is
unchanged.

## Evidence

`build-libretro-gpu/validation/power-sled-post-race-20261009/` contains:

- `plan.json`, role movies, `replays.json`, `options.json` and `recipe.toml`.
- `run/`: excluded window-positioning attempt; no gameplay qualification.
- `retry-command.json`, `runner-window-wait.py`, `retry-runner.log`.
- `retry-run/`: installed-core session, screenshots, PCM and runner result.
- `post-race-contact.png`: reviewed Main/Slave sequence, first race through
  Game Over, black/SEGA, boarding and the second race.
- `review.py` / `review.json`: lifecycle, logs, persistence and artifact checks,
  with the visual findings and remaining qualification limits recorded.

This task uses no MAME execution or NVRAM acquisition campaign. Manual-mode
finish/ranking, physical handling and original Main audio fidelity remain open.

## Manual Follow-Up

Manual / Professional selection, finish and native final placement were
subsequently qualified on 2026-10-10 in the installed core. See
[Power Sled Manual Finish And Ranking](POWER_SLED_MANUAL_VALIDATION_2026-10-10.md).
The earlier exclusions above describe the scope of this 2026-10-09 run.
