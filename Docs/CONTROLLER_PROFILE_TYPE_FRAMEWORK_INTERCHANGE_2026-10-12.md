# Controller Profile Type — Framework Interchange

Date: 2026-10-12
Source: SM2-Emu Libretro, main based on b52108e with local implementation changes
Destination: Libretro Core Framework; applicable consumer cores after review
Affected Contracts: F04, F05, F07, F08, F09
Scope: Record The Approved SM2 Contract And Cross-Core Adoption Candidate

## Approved Contract

The user approves **Controller Profile Type** as the first Input option:

- **Normal**.
- **Normal + Test/Service**, default.

The selection is global across all input ports. Keep each game's native profile
and gameplay controls; omit both descriptors and polling for the supported
Test/Service slots in Normal. Controls retains remapping and None, but advertises
only the current game-specific type; it cannot choose full/reduced variants.
Apply on return to gameplay without resetting the machine in SM2.

## Implementation And Compatibility

SM2 stores `sm2_controller_profile_type = normal | test_service`; missing/unknown
values select the full default. Both modern and legacy registration use the same
contract. Historical reduced-device subclass IDs remain accepted and are mapped
to the current global choice; their per-port variant no longer governs behavior.
None remains disabled. Special cabinet commands are not removed merely because
they use the same physical slots: retain approved Power Sled command semantics.
Native Test/Service polarity and binding positions are unchanged.

## Evidence And Boundaries

- Catalog-wide supported-profile registration and descriptor checks pass.
- Existing digital/analog/gun/special input tests and Save RAM/options checks pass.
- Isolated real RetroArch 1.22.2 on macOS with VF2 confirms first Input placement,
  choices/default, Normal/full switching and Controls containing only None and
  the current profile. The owned process exits 0 without residuals.
- Normal installed core matches the checked build; dev copy remains absent.
- No new physical-controller, other-platform gameplay or other-core result.

Private evidence: `build-libretro-gpu/validation/controller-profile-type-20261012/`.

## Destination Request

Update the Framework's F09 and reconciliation register to record this delivered
SM2 exception to edition 0.1's independent-per-port selection rule. Register the
same interface as an adoption candidate for other cores, with compatibility and
lifecycle review in their own chats; no other-core implementation, commit or
publication is authorized by this handoff. Do not silently resolve the separate
L3/R3 binding discrepancy. Retain this file as provenance; the Framework owns its
documentation and each consumer owns its sole implementation roadmap.

## Menu Refresh Follow-Up

Modern Core Options display callbacks now republish profile names/descriptors
while the machine is paused. A distinct RetroArch VF2 check confirms Controls
reflects Normal without Resume/restart. Legacy frontends still refresh on return
to gameplay. The earlier full/Normal test established only the Resume path.
This correction does not change the global option values/default or gameplay
semantics; do not infer support for a callback absent in another frontend.
