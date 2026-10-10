# Power Sled Manual Finish And Ranking

Date: 2026-10-10
Backend: Installed SM2-Emu Libretro In RetroArch Only

## Qualified Result

The Main / Relay / Slave triplet selects **Manual Power Sled / Professional**,
starts a race, passes checkpoints and Time Extension, crosses the finish area
and displays final placement. Main and Slave show **1st**; Relay displays
**1ST 02:13:67 SILVER** beneath the Finish / Arrive sign. Game Over follows.

The first run used 15-second observations. It captured the race and Game Over
but missed the short placement screen. A second run preserves exactly the
same recorded inputs and observes the end sequence densely. No emulator,
native RAM, calibration endpoint, Service/Test setting or ROM patch is changed.

Both sessions use the production build and installed core SHA-256
`5597cb0b98748757e9de48d359efe760c1d397dc02fcfcfaf909fa0498db3253`.
Both completed sessions pass runtime integrity review, with six clean owned
process exits and no residual peers. Checks are separate from the screenshots: native links,
clean exits, active input movies, no runtime i960 reset, PCM on each role,
SRAM identity/container CRC, ANS colors and unchanged calibration bytes.

This qualifies the tested recorded-input finish and placement. It does not
qualify physical controller feel, every rider/course/color combination or
original-cabinet sound fidelity. The final passive post-race screenshot is black; broader post-race timing
is outside this finish/ranking gate. The three sets retain their preliminary
support status for the remaining limits.

## Reusable Method

The existing race replay now accepts `--manual-mode`. Before local frame 3300,
the right-handle raw ADC is 112 and the left is 128 on both rider ports of
Main and Slave. Thereafter all four handles are 128. These values reuse the
native response zones measured by the previous independent handlebar sweep;
they do not edit calibration. Relay receives no scripted input.

The native mode selector at `0x0051ac84` selects Manual for a negative handle
command. The operator pulses are unchanged: Slave Entry, Main P1 Call,
two Main P2 Calls and Main Start. Inputs are local frontend callbacks,
not synchronized link clocks. No motion hardware is simulated by this test.

```sh
python3 scripts/test-power-sled-gameplay.py \
  --race-qualification --manual-mode --allow-existing-retroarch \
  --port 55573 \
  --output build-libretro-gpu/validation/power-sled-manual-new-run
```

Use a fresh output directory and free ports. Manual observation waits
115 seconds after the linked screenshot, takes 100 rounds separated by
0.5-second waits, then waits 90 seconds for a final post-race screenshot.
Screenshot creation adds time; this is an observation window, not an exact
frame schedule. The movie retains 21600 frontend frames.

`--allow-existing-retroarch` permits these isolated peers alongside an already
open RetroArch. Cleanup targets only the PIDs started by the runner. The
default guard remains active when the flag is omitted. The user's already
open instance was retained. A first preflight refusal launched no peers and
is excluded from gameplay results.

## Evidence

Ignored root: `build-libretro-gpu/validation/power-sled-manual-20261010/`.

- Root `plan.json`, movies, options, recipe and `run/`: initial sparse session.
- `end-sequence/plan.json`, recipe and `run/`: dense finish observation using
  exactly those same movies, core, options and native calibration baseline.
- `review.py` and per-run `runtime-review.json`: lifecycle, audio,
  SRAM/calibration and production/installed-core hashes.
- Dense `client2/screenshots/end-070.png`–`end-073.png`: finish approach and
  passage; `end-080.png`: final 1st; `end-085.png`: Game Over.
- Dense `host/screenshots/end-080.png`: final 1st.
- Dense `client1/screenshots/end-080.png`: Relay ranking, time and Silver.
- `visual-review.json`: retained conclusions and qualification limits.

The native decoder used for the read-only mode-selection comparison uses
local MAME i960 mnemonic tables. MAME was not executed; all runtime input and
captures belong to the target core in RetroArch. No further gameplay probes
are needed to close this bounded finish/ranking gate.
