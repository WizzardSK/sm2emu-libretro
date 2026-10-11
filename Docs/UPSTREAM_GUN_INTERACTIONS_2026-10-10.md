# Upstream Gun Interaction Analysis

Date: 2026-10-10
Upstream Change: `b4c093165b749e9714172c317f1a4bb36b4bb54e`
Status: Analysis Completed; Production Integration Pending

## Scope

Reviewed the exact upstream diff against current game metadata, Libretro input,
initial NVRAM, the BEL workaround, serial off-screen signalling, crosshairs and
the Supermodel reference. Private native-machine probes qualify one concrete
BEL collision. No production source, installed core, personal save or Service
Menu calibration was changed. These probes are not an NVRAM acquisition campaign
or a RetroArch qualification of the proposed integration.

## Interaction Matrix

| Change | Current Port Interaction | Proposed Treatment |
| --- | --- | --- |
| Positional `<point>` metadata | The current parser has no point support and `scale_fraction` is linear. Importing XML alone would silently leave the new curves unused. Upstream points replace min/max/reverse; applying reverse twice would invert Rail Chase 2 again. | Import the schema/parser and piecewise interpolation together. Use point values directly, round as upstream and clamp at the outer points. Keep the existing linear fallback when points are absent. |
| Rail Chase 2 / Revision A curves | Corrects non-central X response and Y saturation. Existing channel order is P2 X, P1 X, P2 Y, P1 Y; revisions have different raw directions. | Preserve each revision's own curve and mux channels. Keep controller sources, player routing and Shot bindings. User decision on 2026-10-11 supersedes the original selector recommendation: expose Linear / Upstream mapping, keeping Linear default. Preserve the current native reticle behavior unless Upstream is explicitly selected. Intentional depth-related reticle displacement is a hypothesis, not established evidence. Verify reticle placement with existing initial saves before claiming gameplay accuracy. |
| HOTD Prototype endpoints | Changes only prototype serial coordinates. Its dedicated initial template remains separate from retail; the P2 trigger is already corrected to IN1 bit 1. | Import prototype bounds, retaining the one-unit on-screen inset, explicit off-screen bit and both trigger routes. Check the dedicated template and an existing save; do not migrate or erase operator settings. |
| BEL curves and seed removal | New raw full-range curves conflict with the distributed calibration. The port also extends the seed to recognize that preset. Removing only the seed does not repair that mismatch. | Reconcile curve scaling with the published preset before removing the workaround. A private rescaled-curve candidate restores the center with the existing preset. Retain the narrow legacy workaround until the replacement is qualified; no unconditional save rewrite. |
| Serial 1% border reload | Upstream affects Mouse, gamepad and physical guns unconditionally. Current port treats on-screen endpoints as on-screen and receives physical off-screen status separately. Mouse-only 5% reload is an optional shared Supermodel convention. | Preserve the published frontend policy as the recommended adaptation. An exact upstream border mode would require an explicit user-approved selector and clearly stated precedence. Do not silently make disabled Mouse edge reload ineffective. |

## Concrete Coordinate Changes

These are raw input values at normalized center, calculated from each actual
metadata table, not measured screen-reticle positions:

| Set | Axis | Current Linear | Upstream Curve |
| --- | --- | ---: | ---: |
| BEL | P1 X / P2 X | 180 / 75 | 127 / 127 |
| BEL | P1 Y / P2 Y | 96 / 96 | 128 / 128 |
| Rail Chase 2 | P1 X / P2 X | 130 / 126 | 114 / 142 |
| Rail Chase 2 | P1 Y / P2 Y | 116 / 116 | 128 / 128 |
| Rail Chase 2 Rev. A | P1 X / P2 X | 128 / 128 | 153 / 102 |

The HOTD prototype changes X to `0x08b–0x27d`, rest `0x184`, and Y to
`0x027–0x1a9`, rest `0x0e8`, for both players. Retail HOTD/HOTDO endpoints and
Gunblade's positional ranges are unchanged in this commit.

## BEL Native Diagnostic

Six isolated 1,800-frame runs use the existing compiled machine libraries,
an exact decoded copy of the distributed BEL template or blank native storage,
the native game program and identical Coin/Start/Shot/aim schedules. An alternate
private library removes only the calibration-seed block from `model2c.cpp`.
The private input probe supplies the upstream curve numerically; production
metadata/parser/input code is not edited.

The distributed preset appears in native RAM as `76 0d 95 95 7e 7e 86 86`.
At frames 600, 1300, 1600 and 1800:

| Configuration | X Reference / Scale, P1/P2 | Y Reference / Scale, P1/P2 | Inspected Final Result |
| --- | --- | --- | --- |
| Current seed, preset, current linear input | 118/13; 63/63 | 175/175; -75/-75 | Reticle near screen center |
| Current seed, preset, direct upstream points | 118/13; 63/63 | 175/175; -75/-75 | Reticle near right/lower border |
| Seed removed, preset, upstream points | 118/13; 63/63 | 149/149; 67/67 | Reticle near right/lower border |
| Seed removed, blank, upstream points | 255/255; 127.5/127.5 | 255/255; 127.5/127.5 | Reticle near left/lower border |
| Current seed, preset, rescaled upstream points | 118/13; 63/63 | 175/175; -75/-75 | Reticle near screen center |

The remaining run confirms that current seed plus blank storage converges to
the same manufactured preset. All runs complete without a main CPU fault.

For the rescaled candidate, upstream X values are normalized by 255 and mapped
into the current channel interval; upstream Y values are normalized and reversed
before that mapping, retaining the existing top-to-bottom convention. This
preserves the nonlinear curve shape while using the established input ranges.
It is a candidate for the recognized legacy preset, not a validated universal
transform for arbitrary user calibration.

The native program does populate the template-derived floats without the seed.
Consequently the old explanation of a missing handshake must not be treated as
a proven root cause of this new interaction. The measured issues are incompatible
raw ranges and different derived Y parameters. Fresh setup, persisted templates,
custom calibrations, P1/P2 coverage and old mid-game states need distinct checks
during the actual integration. Keep unknown user calibration untouched.

## Reload Policy Decision

Current `Mouse Edge Off-Screen Reload` has the same label, Disabled/Enabled
values, Disabled default, Mouse-only applicability and 5% band as Supermodel.
It sends an off-screen shot only when Mouse Left is pressed. Lightgun native
off-screen status and `Off-Screen Reload Shortcut` remain independent.

Upstream instead snaps each serial coordinate outside its calibrated range
when it is strictly below 1% or above 99%, for all input sources, including
hovering without a trigger. Actual firing still requires a trigger. Importing
that block verbatim would turn an otherwise on-screen edge shot into a reload
with the current edge option disabled and would change analog/Lightgun behavior.
Crosshair off-screen state would also need to follow the selected policy.

1. **Recommended: Keep Frontend Convention.** Retain the existing options,
   values/defaults, 5% Mouse-only behavior and physical off-screen signalling.
   Treat the standalone border block as a frontend convenience requiring this
   Libretro adaptation, not as emulated hardware behavior.
2. **Optional: Selectable Upstream Border.** If explicitly desired, propose an
   always-visible `Gun Edge Reload Policy` with `Frontend` and
   `Upstream (1% Border)`; it is a no-op for positional games. Frontend mode
   preserves the existing Mouse option; upstream mode replaces that edge policy
   with the 1% all-source rule. Native off-screen and explicit shortcuts remain
   independent. Default and cross-core conventions would need an explicit
   decision before implementation; no selector is added by this analysis.

## Integration Order And Limits

First integrate schema/interpolation with Rail Chase 2 and prototype endpoints,
then qualify the BEL compatibility adaptation. Apply the chosen reload policy
without changing Shot/Missile, source modes, player bindings or shared option
labels. Metadata is not serialized, so adding curve fields alone does not require
an archive-format bump; old-state continuation still needs qualification because
it retains native calibration/work RAM.

Local evidence: `build-libretro-gpu/validation/upstream-gun-analysis-20261010/`.
It retains the mapping delta, private library/probe sources, decoded existing
template, native logs, inspected screenshots and result JSON. Production and
both installed cores remain at SHA-256
`abda589c10b47acfe472f41bc2e57ec5682edd512b469bbbef490ef6ac6f15fe`.

This is source and bounded native-machine analysis. Full-range accuracy,
arbitrary calibration compatibility, physical guns and final RetroArch behavior
are not claimed. No commit, publication or cross-project change was performed.

## User Decision — 2026-10-11

Rail Chase 2 and Revision A require optional Linear / Upstream coordinate
mapping with Linear default. Source preparation currently contains the upstream
tables, but normal RetroArch builds deliberately exclude them together with
pending HOTD prototype bounds. The installed core retains the prior linear
conversion. This decision does not qualify the new mapping or prove whether
the original reticle displacement intentionally represents depth.

## Integration Update — 2026-10-11

The operator calibrated upstream BEL successfully. Its EEPROM contains MIN 00 / DEL FF for all four axes, resolving the missing calibration prerequisite in the earlier private probes. The latest approval replaces the earlier RC2 Linear-default decision: RC2 and HOTDP now have optional mappings with Upstream default. BEL uses upstream mapping and the matching initial calibration, without the RAM seed. Existing saves are preserved. See `GUN_MAPPING_INTEGRATION_2026-10-11.md` for current behavior and verification limits.
