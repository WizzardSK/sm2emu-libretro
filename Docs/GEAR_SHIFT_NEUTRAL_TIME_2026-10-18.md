# Gear Shift Neutral Time — 2026-10-18

## Contract And Source

The user approved adapting upstream
`0ab3b02d0429794d60d097fd5ae9378333ba227c`, superseding its initial exclusion
from the input bug review. Existing Supermodel/TGPulse reference options were
searched for an equivalent neutral interval; none supplied a shared selector
name to reuse. The control joins the existing Gear functional group.

- **Identity:** `sm2_gear_shift_neutral_time`, **Gear Shift Neutral Time**, Input,
  immediately after **4-Speed Shifter** and before **Automatic Start Gear**.
- **Values:** raw `0` through `500` in 10 ms steps, displayed as `N ms`;
  default and invalid/missing-value fallback `100`, matching upstream's range,
  GUI steps and default. Zero restores immediate shifting.
- **Scope:** four-speed gearbox profiles and their clones (Daytona/Sega Rally
  families). Always visible; no effect on other profiles. Native two-button
  sequential shifters such as Indy 500/Manx TT are not converted into timed
  four-speed gearboxes.
- **Application:** live when gameplay resumes, without machine reset or reload.
  New nonzero values affect subsequent shifts. Selecting zero also cancels a
  pending interval. Existing frontend option/persistence ownership is preserved.

Shift Up/Down edges retain the destination gear but emit native neutral for
ceil(ms*57.5245/1000) machine frames, using upstream's rounding expression.
100 ms occupies six native frames; 500 ms occupies 29. Frontend 60 Hz pacing
does not change native-frame counting. Holding a shift does not repeat it.
Direct gear selection takes priority and cancels pending crossing; explicit
neutral does the same. Entering/leaving neutral does not add a synthetic delay.
Direct H-gate/Standard stick binding positions remain unchanged.

## Save States

Remaining frames use reserved bits 8–12 of the existing frontend tail's first
flags word, at offset 16. They do not overlap held-input/Desert Tank flags,
gun-flash history or audio state. The fixed state size remains 9,437,184 bytes;
no machine serializer or tail version changes. Legacy states have zero in
those bits and resume with no pending crossing. Reset clears the counter.
Older cores ignore the field and cannot reproduce a pending crossing from a
new state; no new reverse-compatibility promise is made.

## Verification

Evidence: `build-libretro-gpu/validation/gear-neutral-20261018/`.

- Full ROM-free input and Save RAM/Core Options suites pass. Both modern and
  legacy registration use the shared definitions. Option tests cover the
  endpoints, every registered value, default, invalid tokens and Gear ordering.
- Synthetic Daytona/Sega Rally step tests cover every 10 ms value through
  500 ms, exact interval length, held-input edge behavior, pending target gear,
  direct-position priority, explicit neutral, leaving neutral and zero applied
  during a pending interval.
- Actual Libretro Software runs save/replay an active 100 ms crossing on
  Daytona and Sega Rally. The frontend state retains five remaining frames
  after the first neutral frame; round-trip and deterministic replay pass.
  Daytona also verifies reset clears the interval, then restores that state.
- The first Rally probe selected first gear to neutral, which correctly has
  no crossing. The corrected probe selects first to second and passes.
- The preceding installed core's Daytona state loads and its 300-frame
  continuation matches image, PCM and native NVRAM. A 0 ms idle comparison
  also matches the preceding core. This is bounded ABI evidence, not physical
  controller or all-course gameplay qualification.
- Core rebuild and 25-export/dependency/empty-lifecycle artifact checks pass.
  Production adapter changes do not require a standalone machine-code import;
  device enumeration remains frontend-owned.

Normal local core updated; build/install hash is recorded in `summary.json`.
No development copy, binary backup, commit, push or release is created. No new
operator campaign is required by this bounded upstream adaptation.
