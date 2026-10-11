# Shared VR1 Supplemental View Binding

Date: 2026-10-11
Origin: SM2-Emu Libretro
Destinations: Supermodel Libretro and TGPulse-Next Libretro project chats
Status: Approved cross-core consistency candidate; destination roadmap review only.

## User Direction

Equivalent controls should provide an experience as homogeneous as practical
across the user's Libretro cores. The user identified the new SM2 VR1 View
supplemental binding as a change to export where applicable. Record this
candidate in each destination roadmap after inspecting its existing controls.
This handoff does not authorize implementation, installation, commit or push.

## Shared Contract

VR1 means any game with exactly one View action, including shared Start/View
inputs and non-driving profiles. Include VR1 in the profile description.
For a profile with one View/VR1 game input, add D-Pad Up as a supplemental
binding to that same action, preserving existing bindings and the established
action label. Do not introduce a second camera action. Do not overwrite Up if
it already has an independent game action; document any real conflict for
review. Games with multiple independent View buttons (VR2/VR4) retain their
existing mapping. If the destination already binds View to Up, record that
coverage and do not add a redundant change. Adapt native bits per title.

## Implemented SM2 Reference

Read-only source: `/Users/andrea/dev/sm2-emu-libretro/src/libretro/input.cpp`.
Profiles Driving: 4-Speed + VR1 + Handbrake and Driving: Sequential + VR1 now
publish Up and Down as VR1 and route both to the same existing native wheel
button. Covered sets: srallyc, srallycb, srallycc, srallycdx, srallycdxa, sgt24h.
General review also adds Up to Manx TT (manxtt/manxttc/manxttdx) and Motor Raid
(motoraid/motoraiddx), using their shared Start / VR line. Sky Target and Wave
Runner already use Up. All six single-View families now have VR1 in their
profile descriptions.
Input profile checks pass; normal local RetroArch core is installed. This is
not new physical-controller or gameplay qualification in the destination.

## Destination Roadmap Entry

Inspect all applicable single-View profiles and list already-covered games,
needed aliases and genuine conflicts. Use one roadmap item for the candidate,
with pending implementation where required. Preserve unrelated work. Use this
file as retained provenance and perform future work in the destination chat.

## Destination Roadmap Confirmation

Both destination chats completed the roadmap review on 2026-10-11.
Supermodel `Docs/ROADMAP.md`, Cross-core VR1 supplemental binding review,
records all 15 single-View sets already using D-Pad Up and no missing alias
or independent Up conflict. TGPulse-Next `docs/LIBRETRO_ROADMAP.md`, Optional
Follow-Ups E3, records swa/swaj already using Up and Down for Pilot VR1.
Other Model 1 profiles have independent VR4/movement actions or no View.
No destination code change is required for the current catalogues. Both
roadmap entries were verified in their files; the handoff is closed and this
file remains provenance. Future applicable profiles retain this shared rule.
