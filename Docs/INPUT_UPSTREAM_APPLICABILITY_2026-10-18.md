# Upstream Input Applicability — 2026-10-18

This review explains the previously broad roadmap row. It is not authorization
to replace approved controls or a finding that the Libretro core has these bugs.

1. **Shoulder duplication — `233a61d`, `18eb76e`.** Standalone had hardwired
   LB/RB aliases for Button 3/4 in addition to configurable SDL bindings. A
   remapped shoulder could therefore activate two game inputs. These commits
   suppress that fallback alias. Libretro has its own approved profiles and
   reads the frontend's remapped virtual actions in `src/libretro/input.cpp`;
   it does not execute this SDL binding code. Review equivalents by profile
   only if a collision is demonstrated; do not remove agreed aliases globally.
2. **Per-game layouts — `36d8518`.** Standalone stores SDL gamepad layouts by
   game. RetroArch already owns per-game remaps; this port owns the canonical
   game profiles and descriptors. No duplicate SDL layout store is needed.
3. **Half-axis pedals / H shifter / neutral transitions — `2509c4f`,
   `acefe1c`, `0ab3b02`.** These configure standalone's physical wheel inputs.
   Libretro already scales virtual pedal channels and has four-speed H-gate,
   sequential and neutral handling. The final source review below resolves the equivalent game-input behavior. Device enumeration and
   physical-wheel setup remain frontend ownership; no wheel-support project
   is being reopened.
4. **Sinden duplication — `1c1f6d8`.** Standalone deduplicates raw and tagged
   evdev gun nodes on Batocera. Libretro receives ports from the frontend and
   does not enumerate udev/evdev devices. That enumeration fix has no direct
   core import. A physical frontend issue would need frontend evidence.
5. **Gun / mouse cross-player duplication — `5366b5c`.** Standalone stops
   falling back to the system mouse for P2 when one gun also drives that
   pointer. The core polls lightgun and mouse by Libretro port and Standard
   intentionally combines available sources. Port indexing is visible in
   `input.cpp`; it does not prove what a frontend driver sends for every
   physical device configuration. Review source arbitration and existing
   checks before proposing any change. Preserve the approved Standard mouse
   fallback and mixed-input use unless a concrete defect requires a decision.

No new operator campaign is requested by this explanatory review. Remaining
source checks must distinguish frontend behavior from game-input translation.

## Operator Follow-Up

The user reports performing the requested gamepad/mouse checks for the listed
representative titles, without reporting a fault. No repeat campaign is
scheduled. The user has no physical lightgun; physical Sinden/gun isolation
verification is unperformed and optional. The source review and automatic checks below complete the applicability work.

## Completed Source Review

Status: Complete within the scope below. No repair was required by that review; the subsequent user-approved timed-neutral addition is recorded separately below.

| Upstream Change | Port Disposition |
| --- | --- |
| `233a61d` / `18eb76e`, shoulder aliases after remapping | Standalone SDL binding fix. The core does not execute those fallback aliases; approved native profiles and RetroArch remaps remain authoritative. User pad checks reported no collision. |
| `36d8518`, per-game SDL layouts | Frontend-owned remap storage already covers the equivalent requirement; no second layout store is added. |
| `2509c4f`, full/half pedal axis | Standalone converts physical SDL -32768..32767 axes to normalized travel. Libretro receives already-mapped positive virtual trigger travel 0..32767. The core maps that normalized fraction to the same native range and reverse polarity. Existing checks cover intermediate travel, endpoints, independent pedal ranges and reversed Super GT pedals. A full physical axis must be bound/normalized by the frontend, not reinterpreted by the core as SDL hardware. |
| `acefe1c`, button-per-gear H shifter | Standalone physical-device binding extension. The core already provides direct four-speed positions, H-gate/standard virtual-stick selection, sequential steps and explicit neutral. Retain the approved gear descriptors and frontend remapping rather than adding SDL wheel buttons. |
| `0ab3b02`, timed neutral crossing | This also affects pad LB/RB, despite its Wheel setting location. Initially excluded to preserve the published direct-step default; the user subsequently requested alignment. It is now integrated as Gear Shift Neutral Time, 100 ms default, 0–500 ms in 10 ms steps, with direct selection bypass and state retention. See `GEAR_SHIFT_NEUTRAL_TIME_2026-10-18.md`. |
| `1c1f6d8`, duplicate Sinden evdev nodes | OS/frontend enumeration, absent from the Libretro adapter. No direct import. |
| `5366b5c`, gun also moving system pointer for P2 | Standalone originally initializes both players from the same global pointer. The core queries callbacks by port and arbitrates Standard sources independently. It cannot identify physical devices or distinguish a frontend intentionally routing one pointer to both ports. Do not suppress P2 merely because P1 has gun activity; that would break the approved mixed-device fallback. |

## Automatic Verification

Extended the existing `sm2-libretro-input-checks` target with mixed-source
callbacks on Virtua Cop and House of the Dead, covering both serial P2 trigger
routes, and with the gun on either P1 or P2:

- Gun movement/Shot does not steal the other port's Mouse or duplicate Shot.
- Gun trigger release and the other player's Mouse Shot remain independent.
- Lightgun Only ignores Mouse on either port.

The complete existing input suite passes, including Standard idle-offscreen
fallback, both players' gun coordinates and off-screen rules, pedal ranges and
reverse polarity, four-speed/H-gate/neutral mappings and sequential profiles.
This is callback-level evidence, not physical Sinden/lightgun qualification.
No fake device-presence inference is introduced. Existing operator observations
remain separate evidence; no repeated physical campaign is requested.

Evidence: `build-libretro-gpu/validation/input-applicability-20261018/`.
The original review changed only checks and documentation. The subsequent
timed-neutral implementation rebuilds the core while preserving the state layout. Newly reported hardware/frontend faults may reopen a specific issue;
there is no general input integration gate left open by this review.
