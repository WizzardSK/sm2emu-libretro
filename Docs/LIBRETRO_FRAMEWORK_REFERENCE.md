# Framework Adoption And Solution Exchange

Date: 2026-10-12
Status: Shared Reference Adopted; No Runtime Migration

## Reference Identity

- Project: `/Users/andrea/dev/libretro-core-framework`.
- Contract document: [FRAMEWORK.md](/Users/andrea/dev/libretro-core-framework/FRAMEWORK.md).
- Evidence index: [REFERENCE_SOURCES.md](/Users/andrea/dev/libretro-core-framework/REFERENCE_SOURCES.md).
- Project chat: [Definisci il framework Libretro](thread://01a13152-dbfa-7e30-bc9d-0477abc2cccc?hostId=local).
- Inspected edition: 0.1, dated 2026-10-12, Initial Reference for Review.

The user designates this project as the shared Framework reference for current
and future Libretro ports and as a reference for solution exchange to/from SM2.
Read the current documents before reuse: this adoption records an inspected
edition, not a permanently frozen copy. The Framework currently provides
documentation contracts; it is not a shared runtime library or extracted runner.

## Applying The Reference

Consult applicable F01–F20 contracts for architecture, upstream reconciliation,
GUI, input, persistence, networking, tooling, validation and release work.
Use SM2, TGPulse and Supermodel source implementations and retained runtime
evidence to establish what is delivered. Explicit user instructions, approved
hardware-specific exceptions and published compatibility remain authoritative.

Distinguish a desired convention, an observed implementation and a pending
proposal. An inconsistency in the Framework review is a candidate for evaluation,
not automatic authorization to change defaults, bindings, visibility or stored
values. In particular, the initial Test/Service slot difference is unresolved;
this adoption does not reverse SM2's existing bindings.

## Bidirectional Solution Exchange

For a transferable SM2 solution, prepare an interchange file describing the
source, affected Framework contracts, hardware boundaries, compatibility impact,
verification and limits. Read the Framework chat, then send approved work there
under the existing handoff authorization; the Framework's own chat owns its
document or tool changes. Record whether the contribution is a policy, a proven
implementation or a candidate requiring validation by another core.

For an applicable Framework solution, review its source and current SM2 behavior,
then record approved implementation work in this project's roadmap. Adapt and
verify it here. Framework registration does not establish SM2 runtime support.

For another core, retain the existing destination-chat workflow: identify and
read its chat, send the approved interchange scope, and verify that its roadmap
records the requirement before removing the originating handoff activity.
Retain the interchange file as provenance. Do not edit another project's files
from this chat; roadmap handoff alone does not authorize implementation or
publication. Do not create duplicate implementation roadmaps in the Framework.

## Adoption Boundary

The Framework chat and local contract documents were inspected read-only.
AGENTS.md, the porting manifesto and this core's design now point to them.
No emulator behavior, Core Option, binding, build dependency or external project
file is changed by this adoption. Future contributions follow the exchange
procedure above; there is no new runtime integration scheduled by this record.

## Network Contract Adoption — 2026-10-17

F05/F14 edition 0.1.23 supersedes the old network rows in Menu Review.
Current GUI label: Auto Network Role Settings (without an acronym suffix). Its
help matches TGPulse ROLE_HELP verbatim. Linked Cabinets shares the same opening
and application-point wording; Model 2 board presence, native program roles,
limits and theoretical combinations remain explicit. Menu Review Orders 034,
035 and 222 still describe the previous model; the Framework chat has been
notified to reconcile them. Do not copy their superseded semantics back.

See [the destination integration report](NETWORK_TWO_OPTION_2026-10-17.md) for
source/build/ABI/frontend/deployment evidence and remaining qualification limits.
