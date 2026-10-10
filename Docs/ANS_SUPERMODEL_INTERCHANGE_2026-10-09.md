# Supermodel Libretro — Unified ANS Interchange

Date: 2026-10-09
Origin: SM2-Emu Libretro project chat
Destination: Supermodel Libretro project chat
Target: `/Users/andrea/dev/libretro-supermodel-modern`
Status: Approved requirement; implementation pending in the destination chat.

## User Direction And Ownership

The user requires the same Automatic Network Settings convention in SM2-Emu,
Supermodel Libretro and TGPulse-Next Libretro. Changes to another repository
must be implemented in that project's own chat, using an interchange file.
This file does not represent completed Supermodel code changes.

## Shared Contract

| Raw ANS Value | Meaning |
| --- | --- |
| `0` | Disabled; Existing Manual NVRAM Settings Apply |
| `1` | Master / First Cabinet |
| `2` | First Slave / Second Cabinet |
| `3`… | Subsequent Slaves / Sequential Cabinet Identities |
| `relay` | Relay / Live Monitor, Where Supported |

Use the exact label `Automatic Network Settings` and descriptive Title Case
value labels. Offer only roles verified for that game. `relay` is the sole
special-role token; do not add `none`, `100`, `live` or a second convention as
new selectable raw values. Model 3 has games with 16 cabinets: handle decimal
values such as `10` and `16`, without importing SM2's nine-cabinet limit.
Frontend host/client status does not determine the native cabinet role.

ANS manages reviewed native network selectors through the existing NVRAM
Settings path. Disabled must preserve manual choices; other fields and existing
save/template precedence remain unchanged. Published manual NVRAM keys and
values must not be renamed to match the ANS tokens.

## Current Source Evidence

Read-only inspection at HEAD `4566c94`, including current local files:

- `Src/OSD/libretro/libretro.cpp`: `append_linked_cabinet_core_options()` and
  `kLinkedCabinetOptionSpecs` register Linked Cabinets for 22 ROM sets. No
  equivalent Automatic Network Settings selector was found in this adapter.
- `Src/OSD/libretro/LibretroNvramSettings.h`: reviewed Link Mode / Link ID
  fields exist, with game-specific Master/Slave/Live, Satellite, combined
  role/car identities and Virtual On seat identities.
- `Docs/ROADMAP.md`: destination implementation roadmap.

This is an ANS feature addition, not just a raw-value rename. Inspect all
current target files and preserve unrelated local changes before editing.

## Destination Implementation

1. Add per-set ANS beside Linked Cabinets, using the project's existing option
   storage, visibility and NVRAM lifecycle. Use keys
   `supermodel_automatic_network_<ROM set>` for this new feature.
2. Build explicit per-game mappings from the reviewed fields. Do not assume
   Model 2 register encodings apply to Model 3. Preserve each title's native
   meaning, including seat/team identities. Expose `relay` only when its exact
   native mapping is supported and reviewed. Do not conflate Satellite with
   Relay without establishing that relationship in this project.
3. Default the new selector to `0` to retain existing manual configurations.
   Apply active presets only through the enabled NVRAM Settings path, and
   preserve the target's restart/apply conventions. Keep communication-board
   behavior and transport validation in the core.
4. This is a new option, so it needs no legacy ANS aliases or migration.
   Existing published options retain their established compatibility rules.
5. Verify registration and role/identity mappings across the linked catalog,
   including two-digit cabinet IDs, disabled/manual behavior, supported Relay
   behavior and unchanged unrelated NVRAM. Use the existing target runner for
   one necessary bounded frontend check; distinguish it from gameplay proof.
6. Update the destination roadmap/docs and deploy the final verified local core
   to its established RetroArch paths. Do not commit or push without a request.

## Launcher Convention

When adapting/reusing the multi-instance launcher, use the shared interface:

```sh
--game gamename
--game gamename1,gamename2
--game gamename:1,gamename:2
--game gamename:1,gamename:2,gamename:relay
```

One name repeats the ROM; a list specifies each instance's ROM. `:ANS` selects
that instance's preset and never modifies its ROM name. Explicit suffixes win
over saved values. Each instance receives its own controller and isolated
configuration/saves. Reuse the destination's established process lifecycle.
The launcher performs no game-compatibility, native-program-combination or
per-game cabinet-limit validation: KISS, as explicitly instructed. The core
and frontend own connection behavior. Do not require a separate role CLI
selector or encode role meanings in frontend host/client selection.

## Reference And Acceptance

Read these current source references in `/Users/andrea/dev/sm2-emu-libretro`:

- `src/libretro/automatic_network.cpp`
- `src/libretro/core_options.h`
- `scripts/launch-linked-cabinets.py`
- `Docs/LINKED_CABINET_LAUNCHER.md`
- `Docs/ANS_CONVENTION_REVIEW_2026-10-09.md`

Reuse the convention and lifecycle, adapting native mappings and limits.
SM2's implementation is already installed and checked across its 31 linked
sets; its actual new-convention frontend probe covers Power Sled. That evidence
is not Supermodel runtime or native-mapping qualification.
