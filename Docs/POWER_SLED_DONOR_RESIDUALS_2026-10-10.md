# Power Sled Patched Master Donors And Native Recovery

## Result

The previous short race-exit session ended with black captures on Main, Slave
and Relay. It did not establish a permanent or Master-specific display failure.
Two subsequent isolated RetroArch sessions now qualify native exit, selection,
boarding and a second advancing race with both Master donors. The longer
Slave-donor session also captures the restored POWER SLED title on Main before
the next selection. No additional production patch is justified by this case.

The comparison concerns two programs adapted to Main, not an original Slave
versus an original Relay. Both adapted programs retain Master role `0x0200`.
An original factory Master ROM remains unavailable.

## Residual Program Differences

Apply the current 15 Relay database patch words and 27 guarded Slave adapter
patch words to the retained original 2 MiB CPU regions, in private evidence
files only. Compare corresponding words and verified direct control targets.
The Slave program is 16 bytes earlier after the shorter initializer.

| Remaining Difference | Effect |
| --- | --- |
| ROM addresses after the initializer | Branch/call displacements and absolute ROM addresses are relocated by 16 bytes. The inspected targets correspond to the same routines. |
| Patched initializer storage | Relay stores the local index and returns at the end of its initializer; Slave branches back to the preceding 12-byte zero gap for that store and return, preserving the next function. |
| Initializer helper call | Calls equivalent relocated settings helpers: Relay `0xed900`, Slave `0xed8f0`. |
| ROM fill boundary and tail | Four aligned words differ at a fill boundary. The unmatched final 16 bytes are excluded; these are not an additional Master engine. |
| Save State program addresses | Existing donor identity checking prevents cross-donor restore. This does not change native SRAM identity or reuse. |

Both patched initializers read the same **signed** communication-count byte,
set role/complement to `0x0200` / `0xfdff`, and set local race index to count
minus one. Both mode patches select native Main mode 1. Both apply the same
NVRAM Ride caption, first-person color and mode-selection scene corrections at
their respective addresses. Both use the Main game definition's same audio,
assets, I/O, network adapter and persistence path.

The aligned patched comparison contains 520,238 identical words, 593 verified
control-target relocations, 3,428 relocated ROM values, two calls to the respective
initializer at the shared entry `0x15840`, and four fill-boundary differences.
No unclassified difference remains in those ranges. The initializer window
`0x15834..0x15880` is inspected separately; the final unmatched 16 bytes are
excluded. This is not a formal whole-program control-flow equivalence proof.
The preceding anchored Master-path/callback analysis remains applicable.

## Why The Short Exit Captures Were Black

The race exit receiver sets `0x00544c20`. The race update returns the group to
global state 4 after its native delay. State-4 initialization resets drawing
and task state, then installs its timed waiting/attract callbacks. The main
loop increments `0x0053e6f0` each iteration. State-4 callbacks consume the Silver
packet command/counter and progress through timed graphics stages; the title
drawing activation includes a counter milestone of `0x0ce4` (3300).

Thus state 4 does not mean that the title is already drawn. The later title
capture and subsequent race demonstrate recovery under the tested native
sequence. They do not authenticate every original physical cabinet transition
or establish identical timing for all display roles.

## Bounded RetroArch Qualification

Reuse `scripts/test-retroarch-netpacket.py`, original archives, isolated config
and SRAM, and the existing qualified Manual race movies. A private diagnostic
dylib adds only passive observation and the already used temporary operator
L/R input lines. Production input/source files and the normal binary are
restored byte for byte before launching; the diagnostic dylib is never installed.
No MAME/standalone emulator is launched, and no RAM, calibration or ROM archive
is forced or modified.

After the existing first race, apply only native exit `0x0300`, fresh Slave
Entry and native Main Mode / Boarding / Start inputs. The Slave-donor recipe
waits longer before those inputs to observe the native title. Their differing
waits mean this is not a frame-aligned performance or visual equality comparison.

| Master Donor | Main First Race | Exit Flag | State-4 Return | New Selection | New Boarding | New Race |
| --- | --- | --- | --- | --- | --- | --- |
| Relay | 4095 | 4620 | 4800 | 6720 | 7920 | 8820 |
| Slave | 4095 | 4620 | 4800 | 8715 | 9810 | 10620 |

Numbers are first observed native machine frames at 15-frame sampling, not
wall-clock times or exact transition cycles. Slave and Relay peers follow each
sequence. The race initializer clears the previous exit flag; the initial
state-dispatch sample may precede that clear. Main/Slave final captures show
advancing races with Red/Silver sleds; Relay shows its race camera. In the longer
session Main `host-02.png` displays the POWER SLED title, followed by the mode
scene and a second race.

All six programs exit normally with native link/roster readiness, preserved
role/count, no sampled shutdown or runtime CPU reset, valid SRAM identity/CRC
and three-copy Ride, unchanged calibration/EEPROM versus the prior qualified
normal session, and nonzero PCM. PCM presence does not establish sound fidelity.

Evidence: `build-libretro-gpu/validation/power-sled-donor-residuals-20261010/`.
Retain exact options/commands/movies and plans, original/private source snapshots,
patched CPU comparison and initializer disassembly, anchored counter/exit windows,
logs, separate per-program images, `runtime-review.json`, `visual-review.json`
and `production-integrity.json`.

The private observer's `silverCommand` / `silverCounter` fields are invalid
work-RAM reads of communication-RAM pointers. Their zero values are explicitly
excluded from qualification; native packet use is established by static code
and the actual group transitions. No packet-counter measurement is claimed.

## Production And Roadmap

Only documentation and private diagnostics change. Normal/both installed cores
retain SHA-256 `598e9864c4858f60b15a07e91e0d8cb684188d2e16fff47ac51305daccaed296`.
Source, staged, configured and fallback databases retain SHA-256
`080181ab494c3c3889ab4f173985e31c43dce11ef45bb1b9b135c85a7549b8f9`.
No deployment, new option or input binding is needed. No commit or push occurs.

Close this bounded donor/recovery question in the roadmap. Factory Master
fidelity, all colors/layouts, physical devices, full-course completion and
extended stress are not qualified by these two sessions.

## Subsequent Simplification

The user selected the less-modified Relay base and removed donor selection.
The comparison evidence above remains valid as historical research. Current
production uses only Relay; see `POWER_SLED_RELAY_ONLY_2026-10-10.md`.
