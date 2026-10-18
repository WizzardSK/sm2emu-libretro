# Daytona GTX Support

Date: 2026-10-12
Status: Implemented; Preliminary Runtime Qualification

## Reference And Adaptation

MAME source: https://github.com/mamedev/mame/blob/master/src/mame/sega/model2.cpp
The imported contract is model2o_gtx_state::gtx_r and ROM_START(daytonagtx),
BSD-3-Clause with original authors attributed in NOTICE and source.

GTX inherits Daytona's unchanged shared regions, I/O and four-speed/VR4 profile.
It replaces the two main program chips and adds bank0.bin/bank1.bin in a 3 MiB
FF-filled prot_data region, word-interleaved on upper lanes. CRC-verified parent
and split-device lookup are retained. No ROM bytes are included in Git.

A GTX-only 1 MiB read overlay at 0x02c00000 uses read-triggered banks. Offsets
FF000, FF00C/F0003 and FFFFC select bank 1, bank 0 and erased bank 2 respectively.
The disabled bank follows MAME's FF contents; its comment's possible data-ROM
fallback is not implemented as a guess. Byte, halfword, dword, flagged and fetch
paths preserve byte-lane side effects, area waits and burst behavior.

The bank begins at zero and resets to zero. Only this newly supported set stores
an additional bank byte in Save States; published game layouts and the fixed
Libretro state buffer are unchanged. Invalid restored bank values are rejected.

## Verification

- Actual RetroArch 1.22.2 macOS ARM64, Vulkan 1x, corrected replay reader 1.22:
  2,300 frames reach a race (lap/position/time HUD and GTX TURBO display),
  non-silent stereo audio, valid 16,576-byte SRAM and exit code 0. Gas input
  cancels the native code-entry screen; no protection bypass is added.
  This bounded race does not qualify full-course completion or multiplayer.
- Normal installed core matches the checked build, with backup retained. Only
  the GTX entry was added to the configured system games.xml; other entries
  were preserved and the dev core remains absent.

- ROM-free checks verify catalog inheritance, all trigger paths, access widths,
  lane-3 switching, erased bank, reset, state restoration and isolation from
  ordinary Daytona/MAXX data access and state round trips. Check added to CI.
- macOS core and headless build; input recognition covers all 88 sets.
- Real ROM Libretro ABI: 1,800 frames, input replay and Save State continuation
  checks pass. Screenshot reaches the GTX code-entry menu, which offers Gas
  to cancel; no fabricated protection response or ROM patch is used.
- NVRAM/YAML audits pass. GTX's Service Menu inventory is explicitly pending;
  no inherited parent operator overrides or initial template are exposed.

Private evidence: build-libretro-gpu/validation/daytona-gtx-20261012/.
The first ABI invocation used the wrong system directory, then was corrected.
The first frontend replay used the older reader format and was rejected; it is
not qualification evidence. The corrected runner uses --replay-reader 1.22.
Full-course gameplay, native networking and physical rumble are not established by
source/build or the ABI checks; retain the preliminary flag.

## Service Menu Inventory Update — 2026-10-17

The pending Phase 1 inventory is now complete in target-core RetroArch: ten
operator selectors, all discrete cycles and native defaults, 83 screenshots.
Native Link ID is Master / Slave / Single; Car Number is 1–8. No Relay value
was observed. Actual linked operation remains unverified. See
[the independent inventory](DAYTONA_GTX_SERVICE_MENU_2026-10-17.md).
Field review, binary mapping, sample campaign, templates and overrides remain
pending; GTX continues to inherit no parent operator overrides.

## NVRAM Integration Update — 2026-10-17

The independent Service Menu inventory and the complete 58-stage target-core
campaign are qualified. Eight approved Game System fields, a dedicated GTX
initial template and Single / Deluxe / Export overrides are implemented.
Existing valid user saves retain precedence. Credit fields remain excluded;
no new networking model is included. See `DAYTONA_GTX_SERVICE_MENU_2026-10-17.md`.
