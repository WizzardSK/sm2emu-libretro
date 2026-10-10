# Upstream-First Libretro Porting Manifesto

Date: 2026-10-07
Scope: SM2-Emu Libretro and other emulator-to-Libretro ports maintained by the user.

## Principle

A Libretro core is a port of its emulator. Keep its emulation behavior, game
metadata, supported content and applicable improvements close to upstream.
An upstream change is an integration candidate by default when it can operate
through the Libretro API and the core's supported platforms. The date when a
change was first reviewed does not affect its priority or status.

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
