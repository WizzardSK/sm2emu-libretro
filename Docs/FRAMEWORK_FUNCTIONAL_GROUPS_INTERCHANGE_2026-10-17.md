# Functional Core Option Groups — SM2-Emu To Framework

## User-Approved Ordering Criteria

Group controls by the task the player expects to find together, as well as by
implementation dependencies. A control for the whole group comes first, followed
by its related settings in a meaningful order. Preserve clearly distinct
subgroups as consecutive blocks rather than interleaving their members. These
rules complement Framework F04's global-before-game-specific presentation rule;
they do not move native operator fields or change workbook Order IDs.

Apply the principle only where a destination core has equivalent controls. A
shared word such as `Gain`, `Gear`, or `Renderer` does not establish equivalent
hardware or behavior by itself. Review the actual user task and dependencies in
each destination before adopting the specific sequence.

The user reviewed these SM2 blocks:

- **Video:** Renderer, Software Renderer Threading, Internal Resolution, 2D Layer
  Upscaling Filter, 3D Texture Filtering. Threading is immediately after
  Renderer; the hardware image controls remain together, with 2D before 3D.
- **Audio:** Music Volume, Enhanced Audio Balance, SCSP Gain, DSB (MPEG) Gain,
  MultiPCM 1 Gain, MultiPCM 2 Gain, FM (YM3438) Gain, SCSP Output Low-Pass
  Filter. The general music level heads this group, followed by balance,
  source gains and the SCSP filter. These controls retain their distinct
  effects and existing raw values.
- **General Input:** Controller Profile Type remains first as previously
  approved. Gamepad Rumble, a general Input setting, follows it before the
  specialized Lightgun and Driving blocks. This is a discoverability rule for
  broadly applicable controls, not a dependency between the two settings.
- **Lightgun:** Hide Shot Flash, Show Crosshair, Crosshair Style, Gun Input Mode,
  Off-Screen Reload Shortcut, Mouse Edge Off-Screen Reload. Keep the existing
  order. Game-specific aim mappings remain in the game-prefixed section.
- **Driving:** Steering Response then Steering Output Range form one subgroup;
  Accelerator Output Range then Brake Output Range form the next consecutive
  subgroup. This grouping does not imply that one setting controls the other.
- **Gear:** 4-Speed Shifter then Automatic Start Gear form a discoverable Gear
  block. The reason is the player's common task, despite their separate effects.

The same task-oriented grouping criterion should be considered for equivalent
controls in TGPulse-Next, Supermodel and future Libretro cores. Do not infer
their concrete member order from this Model 2 sequence without inspecting each
core. Preserve user-approved category placement, native field order, labels,
values, defaults and behavior.

## SM2 Implementation And Evidence

The sequence above is registered in `src/libretro/core_options.h`. System and
its native NVRAM field order are unchanged. The game-prefixed Audio and Input
options remain after global options and follow displayed game-name order.
Modern and legacy registration have the same key sequence.

Final evidence: `build-libretro-gpu/validation/framework-menu-order-20261017/rumble-order-audit.json`
and `registered-menu-after-rumble.json`. The audit compares the new core against the captured
pre-order baseline by key, including complete labels/help, categories, raw
values, displayed value labels and defaults. It also checks the independently
specified expected Video/Audio/Input sequences and 48 applicable non-NVRAM
rows of the final Framework Menu Review workbook. Results: 452 V2 definitions,
452 legacy definitions, 48/48 reviewed rows matched, 31 positions changed in
each registration path, all per-key metadata identical, System order identical,
no audit errors. Supported networking help is compared separately from the two
unsupported no-effect placeholders. The final Rumble move changes seven Input
positions relative to the initial ordering delivery. Save RAM checks pass.

The normal macOS RetroArch core was updated after confirming no RetroArch
process was running. `deployment-after-rumble.json` records matching
source/installed hashes, with no previous-binary backup. The removed
development copy was untouched. The initial `audit.json`, `registered-menu.json`
and `deployment.json` remain as the prior delivery record.

Core SHA-256: `ce1a48cd89a6ca88368cd6ccdc0348427cfee21771ce2a66ef9e1e24e9a177e7`.
Workbook SHA-256: `4ceb9be04d7ad32201c78ae53ac2b103987f8867df69675230996dab7c9c125a`.

The registration audit proves option presentation order and metadata. It does
not establish visible frontend acceptance or gameplay correctness; those remain
separate evidence boundaries. This SM2 work changed no other core, workbook
Order ID, commit or remote; Framework policy is owned by its destination chat.

## Requested Framework Adoption

Record the task-oriented group criterion and the general-before-specialized
Input placement in F04 as reusable rules or explicit clarifications. Review
existing destination menu groups against their own
implementation and user decisions. Preserve documented exceptions, and report
adoption per core instead of assuming this SM2 delivery applies elsewhere.
