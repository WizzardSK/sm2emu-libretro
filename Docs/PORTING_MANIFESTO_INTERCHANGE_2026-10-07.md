# Porting Manifesto Interchange

Date: 2026-10-07
Origin: SM2-Emu Libretro project chat
Destinations: the user's other emulator-to-Libretro project chats

## User Direction

The user wants every port to remain as close as practical to its emulator
upstream. Integrate all compatible upstream changes by default, adapting
frontend-facing behavior to Libretro. Investigate concrete collisions with
port-specific changes and published settings; use a selector only when both
behaviors are useful and the conflict cannot be resolved cleanly. Exclude
standalone features with no supported Libretro equivalent, including external
cabinet-output protocols. Preserve isolated Libretro quality-of-life features.

## Reference and Adoption

Read [Upstream-First Libretro Porting Manifesto](UPSTREAM_PORTING_MANIFESTO.md)
in full before applying this direction. In each destination project, inspect
its own upstream relationship, hardware, supported Libretro interfaces,
published options and current roadmap. Record adopted rules there and resolve
project-specific conflicts in that project's chat. This interchange file does
not authorize edits to another repository from the SM2-Emu chat.
