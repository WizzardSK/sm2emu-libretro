# Upstream-First Libretro Porting Manifesto

Date: 2026-10-07
Scope: SM2-Emu Libretro and other emulator-to-Libretro ports maintained by the user.

## Principle

A Libretro core is a port of its emulator. Keep its emulation behavior, game
metadata, supported content and applicable improvements close to upstream.
An upstream change is an integration candidate by default when it can operate
through the Libretro API and the core's supported platforms. The date when a
change was first reviewed does not affect its priority or status.

## Mandatory Frontend References

The shared reference is the user's Libretro Core Framework at
`/Users/andrea/dev/libretro-core-framework/FRAMEWORK.md`, with its inspected
sources in `REFERENCE_SOURCES.md`. Consult the current Framework contracts
before adopting shared guidelines, tools, menu structures or equivalent behavior.
Explicit user instructions and approved core-specific exceptions take precedence;
an observed difference or pending Framework item is not permission to change a
published core contract. See [Framework Adoption And Solution Exchange](LIBRETRO_FRAMEWORK_REFERENCE.md).

Before changing menu organization, equivalent option names, descriptions/help text,
choices, defaults or application behavior, inspect the current Supermodel Libretro and TGPulse
Libretro reference implementations read-only. Compare their actual code and
runtime evidence rather than relying on older chat descriptions. Record any
pending feature or differing implementation explicitly. Adapt hardware-specific
semantics while preserving the user's shared frontend conventions and explicit
exceptions; the latest approved user instruction takes precedence. Reuse the
reference wording for equivalent behavior, adapting only hardware, applicability
and actual lifecycle differences. Descriptions must state when changes apply
and whether they reset the machine; do not claim behavior absent from this core.

Equivalent frontend improvements, including supplemental bindings, should be
reviewed for transfer to the other reference cores. Use an interchange file and
the destination chat to record applicable candidates in its roadmap. Verify
that the destination records the requirement before closing the originating
handoff; implementation requires its own approved scope.

Transferable SM2 solutions must also be considered for the Framework; Framework
solutions must be reviewed for applicability to SM2. Use the Framework's own
chat for its changes and this project's chat for SM2 implementation. Retain the
interchange file, source evidence, compatibility impact and validation limits.
Framework adoption does not imply that every core already implements a solution.

## Single-View Input Convention

VR1 denotes any game with exactly one action that changes the view, including
non-driving games and actions sharing a native input with Start. Include VR1
in the profile description and bind D-Pad Up to that existing action in addition
to the established bindings. Preserve the native shared-input behavior and the
existing action label. Do not invent another camera input. Review a genuine
conflict with an independent Up action before changing that binding. Multiple
independent View actions retain their VR2/VR3/VR4 layouts. Catalogue reviews
must cover all profiles and clones, not just profiles already named VR1.

## Integration Rules

1. **Import compatible emulator changes.** Bring in CPU, timing, audio,
   rendering, input-hardware, loader, game-data and Save State fixes, as well as
   supported games, with the smallest practical divergence from upstream.
   Review upstream source and behavior before adapting a change.
2. **Translate frontend ownership.** Keep machine behavior in shared emulator
   code. Implement windows, devices, menus, configuration, persistence,
   presentation, audio delivery and networking through the relevant Libretro
   interfaces where available. Do not copy an SDL, ImGui, OS-specific or
   standalone output path into a core simply because upstream changed it.
3. **Resolve proven collisions.** Compare an upstream change with the port's
   existing behavior and published settings. Prefer an upstream-compatible
   default when it can preserve user data and the agreed frontend conventions.
   Add a selector only when both behaviors have a meaningful use and the
   difference cannot be resolved cleanly. Keep old stored values readable when
   a published option changes. Ask the user about a concrete unresolved choice,
   showing the affected games, defaults and compatibility impact.
4. **Exclude unsupported destinations.** Do not import cabinet-output protocols,
   standalone windows, device drivers or similar facilities that have no
   supported Libretro equivalent. Reuse machine-side decoding only when it
   serves a real Libretro feature, such as standard gamepad rumble.
5. **Keep useful port improvements.** Preserve isolated quality-of-life
   features, accessibility controls, diagnostics and per-game options that fit
   Libretro, even when upstream lacks them. Avoid duplicating upstream
   emulation logic or adding unnecessary switches.
6. **Verify before closing.** Record the upstream revision and dependency pins.
   Review API and data changes; build standalone, headless and core targets as
   applicable. Compare the port with pristine upstream at the same revision,
   and compare old and new baselines separately. Test affected boards and games,
   including video, PCM, NVRAM, Save States and real RetroArch behavior when
   relevant. A successful build does not establish runtime correctness.

## Release Version Convention — Mandatory Cross-Project Rule

Use `UPSTREAM_VERSION.PORT_REVISION`: the first components identify the latest
upstream release whose applicable changes have been reconciled with the core;
the final component identifies subsequent port-only releases. For example,
upstream 0.9.44 becomes core 0.9.44.0; a later port-only release becomes
0.9.44.1. Reset the port revision to zero when advancing the upstream version.

Reconciliation means every change through that upstream revision is recorded as
integrated, adapted, or excluded with a concrete reason under this manifesto.
Selective imports and cherry-picks count: neither the Git merge strategy nor
the last wholesale source import determines the advertised version. Excluded
standalone/frontend changes do not prevent advancing the upstream component.
An unresolved applicable change does prevent claiming that release; fetch or
review alone never qualifies it.

Before publishing, verify the integration ledger through the intended upstream
revision. Distinguish the historical source base from the reconciled upstream
coverage, and align the runtime version, core-info metadata, release tag/title,
README, release notes and current roadmap status. Do not retain an obsolete
upstream component merely because imports were documented separately.

For SM2-Emu, the approved correction is 0.9.44.0 after reconciliation through
0.9.44, replacing the mistaken 0.9.13.1 release numbering. Recording this rule
does not itself change an existing release or authorize rewriting public tags.

## Applying This Manifesto Elsewhere

Each port applies these rules in its own repository and project chat. Adapt to
its emulator hardware, existing options, published compatibility contract and
available Libretro interfaces. Use this document as an interchange reference;
do not edit a different project from the SM2-Emu chat.

### Cross-Project Handoff And Roadmap Ownership

For existing and new projects, prepare an interchange file for approved work
belonging to another project. The user's standing instruction authorizes sending
that handoff to the appropriate existing project chat without renewed approval.
Identify and read that chat, request the destination roadmap update, and verify
the resulting file. Remove the originating roadmap activity only after the
destination roadmap records it; retain the interchange file as a reference.
Transfer the user's approved scope exactly: adding a roadmap item does not by
itself authorize implementation, commit or push. Resolve a missing or ambiguous
destination chat before sending. Each project's own chat owns its changes and
verification.

## Core Option Visibility — Mandatory Cross-Project Convention

Core Options are visible for all games by default. An option that is irrelevant
to a particular game has no effect there; its help text explains applicability.
Game metadata alone is not authorization to hide options. Restrict visibility
only on the user's explicit instruction, preserving already agreed exceptions
such as per-game NVRAM settings. Apply this rule to existing and new emulator
ports without asking the user to repeat it. For Hide Shot Flash, visibility is
universal while the filter only operates on games with a lightgun interface.

## Service Menu Campaign Phases

Phase 1: complete the Service Menu documentation, including hierarchy/order,
settings, labels, defaults, discrete cycles, numeric ranges and conditional
behavior per set. Reconcile the inventory in YAML and the review workbook,
applying agreed exclusions and simplifications.

Phase 2: implement/adapt and use the sample acquisition script from the completed
Phase 1 inventory. Do not begin or expand sample acquisition while documentation
coverage remains unresolved. Retain exploratory evidence without treating it as
completion of either phase.

The sample acquisition script is restricted to the target Libretro core running
in RetroArch. MAME and standalone emulators must not be used as alternative
acquisition backends. Their reference evidence does not qualify as target-core
samples. Unreachable target-core menus remain pending until the core prerequisite
is resolved; do not bypass that prerequisite with another emulator.

## Calibration Menu Campaign Rule

### Sampling Coverage

Choose coverage separately for each setting. Selectors with few discrete
variants require all selectable values and a complete native cycle. Numeric
fields with a demonstrated regular encoding may use representative committed
samples covering defaults, limits, increments and relevant byte boundaries,
plus fresh reload verification. A numeric sampling optimization never reduces
coverage of small discrete selectors. Calibration menus remain subject to the
exclusion below.

List calibration menus and their purpose when inventorying native service menus.
Do not acquire their endpoint values, calibration cycles or calibration presets
unless the user explicitly requests a dedicated calibration task. Keep historical
exploratory captures separate from the active NVRAM setting campaign.

### One Recipe, One Campaign

After Phase 1 is complete, generate one complete acquisition recipe from its
verified inventory before starting Phase 2. Run that recipe as one campaign,
validating each sample as it is acquired. Use a persistent manifest to record
coverage, validation failures, native commit and fresh reload evidence; resume
from validated results without reacquiring them. Do not substitute ad hoc
single-option probes or arbitrary small batches for the complete campaign, and
do not ask the user to authorize every sample or continuation. Pause only for a
concrete failed validation, missing prerequisite, or an actual user decision.
Fix routine runner failures and resume the same campaign autonomously. Keep
numeric representative sampling and complete small-selector cycles as agreed.

## New Set Review Continuity

Adding a set must reuse the established inventory, review, acquisition, native
validation, implementation and delivery workflow. Inspect the same-family sets
before defining defaults or exceptions. Carry applicable existing conventions
into the review, including core selector defaults and Automatic Initial NVRAM
Setup overrides, while retaining independently observed native defaults. A menu
inventory alone is not the complete review. Record implementation status
explicitly; shared conventions do not establish binary mappings or validate a
parent template for a new set. Preserve native table banding and reviewer edits.
