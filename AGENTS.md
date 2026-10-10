# SM2-Emu Libretro workspace

## Scope and repositories

- `sm2-emu-libretro/`: independent Git repository; develop on `main`.
- `../sm2-emu-mainstream/`: separate, clean upstream clone on `main`.
- They have independent Git metadata and submodules; they are not linked worktrees.
- In the Libretro repository, `upstream` points to
  `https://github.com/dmanlfc/sm2-emu.git` for source reference and future updates.
- Preserve the original Git history for provenance and comparisons. This does not
  require a GitHub fork relationship. The user wants a new standalone repository,
  not a GitHub fork. Do not create a fork.
- `origin` is `https://github.com/Zer0one/sm2-emu-libretro.git`, the standalone
  project repository. Keep `upstream` as the original emulator reference.
- Libretro `main` does not track `upstream/main`; development belongs here.
  Mainstream `main` continues to track its own `upstream/main`.
- Verify branch, status, remotes and submodules before editing. Keep conversion
  changes in the Libretro repository and upstream baseline builds in mainstream.
- Do not commit, push or create a remote repository unless the user asks.

## Working agreement

Cross-project changes use an interchange file and the destination project's own
chat. The user's standing instruction authorizes sending approved handoffs to
the appropriate existing project chats without asking again. Prepare the file,
identify and read the destination chat, request the matching roadmap update,
then verify that the destination roadmap records the requirement before removing
its activity from the originating roadmap. Retain the interchange file as a
reference. Roadmap handoff alone does not authorize implementation, commit or
push; pass through only the scope the user approved. If the destination chat is
missing or ambiguous, resolve that destination before sending.

Use small, reviewable changes and preserve emulation accuracy, timing, audio
and existing controls. Ask before installing/upgrading software or dependencies
unless already authorized in the current session. Never add ROMs to Git.

Current state: upstream macOS baseline built and exercised; frontend-free
`sm2-headless` build verified against upstream on all four board variants.
The first software Libretro core is implemented and verified through ABI
comparisons and VF2 gameplay in RetroArch macOS. See HEADLESS.md and LIBRETRO.md
for evidence and limits. The user then prioritized GPU ahead of profile
implementation: the Vulkan adapter and Video options are implemented and tested
on macOS, including real RetroArch gameplay; see GPU.md. CI now builds Linux
x86_64, Windows x86_64 and macOS arm64/Intel. The Linux CI core was verified
on Batocera 43.1 with VF2, software and Vulkan 1x/2x; see CI.md for evidence
and the fixed callback lifetime issue. Complete profiles,
Input options and SRAM remain milestone 3.
Follow the current user request for scope; PORTING_PLAN.md lists later work.

Distinguish compilation, application launch and actual gameplay verification.
Do not claim runtime input/audio correctness from a successful build.

## Local RetroArch Deployment

For now, deploy local builds only to `sm2_libretro.dylib` in the configured
RetroArch cores directory. The user removed `sm2_dev_libretro.dylib` and its
matching core-info file on 2026-10-10. Do not recreate or update the dev copy
unless the user explicitly asks to restore it. Older reports mentioning two
installed copies describe the previous setup.

## Upstream integration

Future upstream updates are an explicit architectural requirement. Keep the
original source layout and minimize edits to imported files. Put Libretro ABI,
callbacks, options, input adaptation and frontend persistence in `src/libretro/`
with its own CMake target. Dependencies point from adapters to emulation;
machine/CPU code must not include Libretro headers or use frontend callbacks.
Reuse existing machine interfaces; add small frontend-neutral accessors only
when required. Do not duplicate emulation or scatter Libretro conditionals
through upstream code. Avoid unrelated renames, formatting and abstractions.

Keep required upstream-facing changes documented in LIBRETRO_DESIGN.md.
Separate adapter work, generic machine changes and upstream imports when
commits are authorized. Record the integrated upstream revision and submodule
pins; fetch alone does not update that baseline. Before accepting an update,
review upstream API/data changes, build standalone and headless targets, and
compare against a matching pristine upstream build. Compare old and new
baselines separately so upstream behavior changes are not mistaken for port
regressions. Add actual RetroArch checks once the core exists.

## Libretro interface reference

Use the user's `../libretro-supermodel-modern` project as a read-only guide
for menu organization, control profiles and established preferences.
Follow LIBRETRO_DESIGN.md for applicability, defaults and validation rules.
Milestone 3 is split into bounded substeps in PORTING_PLAN.md. Start from the
proposed CONTROL_PROFILES.md catalog (3.1); review it before implementing
recognition/mappings. Metadata gaps are explicit, not guessed profiles.
Preserve canonical actions and add aliases; use frontend remapping and
per-game options. Adapt to SM2 metadata and hardware rather than copying
Model 3 hardware mappings or advertising unimplemented features.
For equivalent controls in Model 2 games and Model 3 sequels, retain the
Supermodel profile name, physical layout and option conventions. Translate
hardware bits/channels per game; expose only verified actions. Follow the
cross-generation matrix in CONTROL_PROFILES.md, including Soccer's bit
permutation and Sega Rally's unresolved Handbrake metadata gap.

## Build

Run `./scripts/build-upstream-macos.sh` to rebuild the adjacent mainstream.
The script does not install packages or change upstream sources.
Use `SM2_BUILD_STANDALONE=OFF` and `SM2_BUILD_HEADLESS=ON` for the
frontend-free runner. Keep it free of SDL/GPU dependencies and compare changes
with `scripts/compare-headless.py` when they affect machine integration.

Use `SM2_BUILD_LIBRETRO=ON` to build the isolated adapter;
`SM2_LIBRETRO_VULKAN=ON` adds the frontend-owned GPU path. Preserve the shared
upstream shaders/passes and keep SDL/swapchain ownership out of Libretro.
The macOS RetroArch build needs the newer MoltenVK selected by the launcher;
never overwrite its app bundle. GPU.md lists lifecycle/comparison tests.
`SM2_LIBRETRO_CHECKS=ON` adds ROM-free input checks. Keep emulator code free of
frontend dependencies. Run `scripts/smoke-libretro.py` for ABI regressions and
see LIBRETRO.md for the separate RetroArch runtime test.

The upstream revision initially checked out is
`8b3a468c5b51387093811cb16b076e6fd9289d66` (version 0.9.4).

## Core Option Visibility — Mandatory User Convention

Show Core Options for every game by default. Do not automatically hide an
option because the current game cannot use it; make it a no-op where it does
not apply and explain applicability in its help text. Restrict visibility only
when the user explicitly requests it. Preserve previously explicit exceptions,
such as the agreed per-game NVRAM settings. Do not ask the user to repeat this
convention or infer new exceptions from hardware metadata.

## Service Menu Campaigns

Use two ordered phases. Phase 1 completes the Service Menu documentation:
menu hierarchy/order, applicable settings, visible labels, defaults, complete
discrete value cycles, numeric ranges and conditional behavior for each set,
reconciled in YAML and the review workbook. Apply the user's agreed exclusions
and numeric simplifications. Phase 2 implements/adapts and runs the sample
acquisition script from that completed inventory. Do not start or expand Phase
2 while Phase 1 has unresolved coverage. Existing exploratory saves are evidence,
not proof that Phase 1 is complete.

Phase 2 sample acquisition is authorized exclusively through the target
Libretro core running in RetroArch. Do not use the acquisition script or its
generated plans with MAME, standalone emulators or other emulator runners.
Reference-emulator evidence is not a target-core sample. If a variant cannot
reach its menus in RetroArch, keep its acquisition pending and document the
target-core prerequisite instead of substituting another emulator.

Choose sampling coverage per field. For selectors with few discrete variants,
capture every selectable value and the complete native cycle. For numeric
fields with a demonstrated regular encoding, derive the format and retain
representative samples covering defaults, limits, increments and relevant byte
boundaries, with native commit/reload checks. Reduced numeric sampling must
not be applied to small discrete selectors. Calibration exclusions still apply.

Calibration menus are listed only. Do not acquire calibration endpoints, value
cycles or presets unless the user explicitly requests dedicated calibration work.
Keep prior exploratory calibration evidence outside the active settings campaign.

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
