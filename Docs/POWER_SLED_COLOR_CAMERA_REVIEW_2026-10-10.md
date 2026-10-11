# Power Sled Standalone Color Camera Review — 2026-10-10

## Result

The recently installed camera override at `0x18c30` bypasses the native color
selection and forces value 1 at `0x529358`. It does not establish an original
single-screen Power Sled mode. The previous claim that this qualified a correct
Silver intro is withdrawn. The existing color-specific panorama is confirmed.

| Ride Color | Previous Native Value | Current Override Value |
|---|---:|---:|
| Silver | 780 | 1 |
| Red | 260 | 1 |
| Black | -260 | 1 |
| Yellow | -780 | 1 |

These are native integers, not an asserted pixel count. They are observed at
machine frames 900, 1200 and 1800 in attract phase 4, configuration enum 6.
At frame 1500 this scene segment clears the value to 0 in all eight runs.
The four previous captures show distinct portions of the same scene; current
captures show the same general framing for all colors. Small animation-frame
variations remain because screenshot commands are asynchronous.

## Controlled Comparison

Eight sequential RetroArch runs: four colors with the current instruction and
four with only the original instruction restored. Each uses a passive observer
built from the same current sources. The previous observer retains the same
guards and all other standalone code; its last replacement is a no-op restoring
`0x90a03000` at `0x18c30`. No private XML camera edit is used in this matrix.

All runs use the same production database, copied-user-save baseline, Auto
renderer with Vulkan/MoltenVK, ANS 0, Relay Audio Enabled, Standalone Enabled,
Linked Cabinets Disabled and input replay. Only Ride Color and the camera
instruction under comparison vary. Four native-frame observations and separate
screenshots per run are retained. The native human index and persisted three
Ride copies agree with each selected color; owned order rotates accordingly.
Calibration remains identical. All eight SRAM container CRCs and clean process
exits pass; no owned process remains. This review covers the attract intro,
not boarding/countdown or racing camera fidelity.

Evidence root: `build-libretro-gpu/validation/power-sled-color-camera-20261010/`.
Reproduce with `python3 <evidence-root>/build-observers.py`, then
`python3 <evidence-root>/run-matrix.py` and
`python3 <evidence-root>/review-matrix.py`; these wrap the established
`scripts/test-retroarch-netpacket.py`. Commands, options, results and validated
captures are retained per color. `matrix-review.json` records numeric results.
The screenshot file initially appears before writing finishes: provisional
label copies were empty, but all original completed PNGs remained intact.
The final review copies and validates those originals and records their hashes;
empty provisional copies are excluded from evidence.

Both observers are private and were never installed. Production source bytes
and normal build artifact were restored. `boundary-review.json` verifies that
the normal installed core still has SHA256
`d10e39ad1ed04609c9f3ad06fac26de818d6214b472c0dcdf199acd8d0025de9`;
the dev core remains absent. No global configuration or original user save is
modified. Account usage reads 24% before and after this comparison, below the
25% authorized ceiling; the percentage display is rounded. Reset remains
2026-10-17 15:30:48 Europe/Rome.

## User Decision

The user approves retaining the current override: all four current-version
runs show the intro they identify as Silver, which is the desired Standalone
presentation for every Ride color. This is an explicit port preference, not
proof of an original single-screen cabinet mode. The camera item is closed
for this accepted intro behavior; boarding/racing camera fidelity is outside
this comparison.

The user's visual observations for the four runs without the override are:

| Selected Ride | Intro Identified By User |
|---|---|
| Silver | Yellow |
| Red | Silver |
| Black | Red |
| Yellow | Black |

These identifications are retained as user observations and do not replace the
measured native values. The earlier History-session discrepancy remains
unexplained; no further investigation is requested for the accepted framing.
The current override was already installed and is retained. No further build,
deployment or gameplay test is needed for this decision. Account usage now
reads 25%, reaching the authorized ceiling; additional analysis stops here.

## Separate Captures

Machine-frame target 1200; screenshots are taken just after the retained native
observation. Open the PNGs independently in the evidence root:

- Previous: `previous-silver/host/screenshots/1200.png`,
  `previous-red/host/screenshots/1200.png`,
  `previous-black/host/screenshots/1200.png`,
  `previous-yellow/host/screenshots/1200.png`.
- Current: `current-silver/host/screenshots/1200.png`,
  `current-red/host/screenshots/1200.png`,
  `current-black/host/screenshots/1200.png`,
  `current-yellow/host/screenshots/1200.png`.
