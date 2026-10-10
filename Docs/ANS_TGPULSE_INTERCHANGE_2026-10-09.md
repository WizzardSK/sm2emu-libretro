# TGPulse-Next Libretro — Unified ANS Interchange

Date: 2026-10-09
Origin: SM2-Emu Libretro project chat
Destination: TGPulse-Next Libretro project chat
Target: `/Users/andrea/dev/tgpulse-next-libretro`
Status: Approved requirement; implementation pending in the destination chat.

## User Direction And Ownership

Apply the shared Automatic Network Settings convention to this core. Changes
must be made and verified in its own project chat using this file. This SM2
chat inspected the target read-only and did not modify its code or installation.

## Required Values And Native Meanings

Keep the visible `Automatic Network Settings` name and the current native
role/color meanings. Use these canonical raw values:

| Value | VR / VFormula Label And Meaning | Wing War Label And Meaning |
| --- | --- | --- |
| `0` | Disabled | Disabled |
| `1` | Red (Master) | Master |
| `2` | Orange (Slave) | Slave |
| `3` | Skyblue (Slave) | Not Offered |
| `4` | Pink (Slave) | Not Offered |
| `5` | Black (Slave) | Not Offered |
| `6` | Green (Slave) | Not Offered |
| `7` | Yellow (Slave) | Not Offered |
| `8` | Blue (Slave) | Not Offered |
| `relay` | Live (Relay) | Not Offered |

The canonical Disabled value is `0`, and `relay` is the only special-role
convention. Do not add `none`, `100` or `live` as new selectable alternatives.
Preserve the existing effective Master default, using raw `1`. Native NVRAM
field keys/values, color order, offline defaults and frontend-independent roles
remain unchanged. ANS still applies through enabled NVRAM Settings.

## Current Source Evidence

Read-only inspection at HEAD `8a66231`, including current local files:

- `crates/tgpulse-libretro/src/automatic_network.rs`: six per-set keys;
  VR/VFormula currently use `red`, `orange`, `skyblue`, `pink`, `black`, `green`,
  `yellow`, `blue`, `live`, `disabled`. Wing War uses `master`, `slave`,
  `disabled`. Preset array indices encode reviewed role/color mappings.
- `crates/tgpulse-libretro/src/netpacket.rs`: VR/VFormula total limit 9,
  Wing War variants total limit 2. Those native limits do not change.
- `crates/tgpulse-libretro/src/lib.rs`: Core Options V2 registration and legacy
  frontend API fallback both declare ANS values; help text and option tests
  refer to the current role/color selectors.
- `AGENTS.md`: use `docs/LIBRETRO_ROADMAP.md` as the implementation roadmap,
  inspect references first, and deploy verified macOS builds to the established
  non-Development core path with matching metadata/hash.

## Destination Implementation

1. Replace canonical raw ANS keys with the table above. Keep reviewed array
   ordering/index semantics so native color/role patches do not change.
2. Update both Core Options V2 and legacy frontend API registration. A legacy
   frontend API is not the same as supporting old saved ANS names. Maintain
   descriptive labels, help, visibility, adjacency and default raw `1`.
3. Retain managed-selector publishing, offline restoration, native integrity,
   unrelated-field preservation and existing reset behavior.
4. The user waived old ANS aliases specifically for the still-developing SM2
   options. Do not broaden that waiver to previously published target options
   silently: check whether these ANS keys shipped and apply the destination's
   already agreed published-option compatibility rules. If unshipped, use only
   the new raw values; if published, keep any required old-value read support
   while writing canonical values. Do not add an offline migration utility or
   eagerly rewrite frontend-owned option files.
5. Adapt existing tests to every canonical preset across all six sets, including
   Disabled, offline restoration and Live/Relay identity. Verify necessary
   frontend registration/persistence through the established runner; do not
   repeat a complete gameplay campaign just for these tokens.
6. Update the single destination roadmap/docs and install the verified final
   local core with matching metadata and SHA-256 as required by its AGENTS.md.
   Preserve unrelated work; do not commit or push without a request.

## Launcher Convention

When reusing/adapting the linked-instance launcher, use:

```sh
--game gamename
--game gamename1,gamename2
--game gamename:1,gamename:2
--game vr:1,vr:2,vr:relay
```

A single name repeats that ROM, a list assigns each instance's ROM, and `:ANS`
sets its preset without changing the ROM name. Explicit values override saved
ones. Keep one controller and isolated configuration/saves per instance. Reuse
existing runners. The script performs no game-compatibility, native-program
combination or per-game cabinet-limit checks; the core/frontend own connection
behavior. Do not copy Model 2 hardware mappings or Power Sled role rules.

## Source Reference And Acceptance

Read the current SM2 files under `/Users/andrea/dev/sm2-emu-libretro`:

- `src/libretro/automatic_network.cpp`
- `src/libretro/core_options.h`
- `scripts/launch-linked-cabinets.py`
- `Docs/LINKED_CABINET_LAUNCHER.md`
- `Docs/ANS_CONVENTION_REVIEW_2026-10-09.md`

SM2's unified convention is implemented/deployed, with mapping checks across
31 linked sets and a new-convention Power Sled frontend probe. Destination
implementation, actual native Model 1 mappings and frontend verification must
be reported separately; this handoff does not mark them complete.
