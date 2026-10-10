# Upstream Review

Date: 2026-10-10
Source: `https://github.com/dmanlfc/sm2-emu.git`, `main`
Previous Reviewed Revision: `2e056f29109d319fe8eb58e6a7fbd323b531ced7`
Current Reviewed Revision: `3c9e79a76272b736e720377e8ec67c2b1c599ce6`
Upstream Version: 0.9.43

## Result

`git fetch --no-recurse-submodules upstream` retrieved 12 additional commits,
including four merges. The latest upstream commit is dated 2026-10-09.
The local branch, emulation sources and initialized dependency pins were not
changed by the fetch. The integrated baseline remains 0.9.13, with separately
documented imported packages; reviewing a revision does not integrate it.

## Core Candidates

| Candidate | Source | Scope And Required Adaptation |
| --- | --- | --- |
| CPU And Coprocessor Performance | `760a5567e7cd805d461ef532516a87fb20071634` | Direct i960 ROM/work-RAM instruction fetch on all boards; direct MB86235 program fetch and empty-FIFO wait skipping on Model 2C; settled SHARC FIFO-wait-loop skipping on Model 2B. Review pointer validity across load/reset/Save State and compare timing/output with the matching pristine upstream. Upstream author reports substantial gains, which are not a measured Libretro result. |
| SCSP Pitch Modulation | `ec9c3acc162a0b145c0a2e4b26af674ac005866a`, `2da8759` | PLFOS depth index 3 changes from 6 to 8 to correct pitch modulation. The unused `FM_FRAC_DIV` constant is already absent locally. Preserve the core's mixer, Gain, filter and Enhanced Audio Balance conventions. |
| Gun Aim And Reload Reconciliation | `b4c093165b749e9714172c317f1a4bb36b4bb54e` | Add metadata-driven piecewise positional-gun mapping for Behind Enemy Lines and Rail Chase 2 variants; adjust HOTD prototype serial-gun bounds. Upstream also removes the BEL volatile calibration seed and adds a 1% border reload zone for serial guns. Adapt mapping through Libretro input and compare existing calibration/initial templates, P2 routing, Offscreen Reload and mouse-edge options before changing behavior. Requires additional collision analysis. |

## Standalone Changes

The following belong to the standalone frontend and are excluded from direct
Libretro import:

- `ee9fc5e`: ImGui overlay sizing on low-resolution displays. The core already
  owns its separate in-game timing overlay and font controls.
- `b72dc54`: GUI localization, system fonts, text shaping and bidirectional
  layout, with HarfBuzz and SheenBidi dependencies. Libretro uses frontend menus;
  no direct requirement for these new dependencies is established.
- `c77af79`: MSVC source-encoding fix within the new standalone `i18n.cpp`.
- Version bumps, merges and associated standalone build/documentation changes.

No game-set addition is present in this delta. `games.xml` changes in this range
are gun mappings and their schema documentation.

## Integration Follow-Up

CPU/coprocessor performance and SCSP pitch modulation were subsequently imported
and locally qualified on 2026-10-10. The roadmap records their completion; see
`UPSTREAM_CPU_SCSP_PACKAGE_2026-10-10.md` for pristine before/after comparisons,
state compatibility, bounded measurements, RetroArch gameplay and installation.
The complete baseline remains 0.9.13 with these selective imports.

Gun aim/reload interaction analysis is now documented in
`UPSTREAM_GUN_INTERACTIONS_2026-10-10.md`. It demonstrates a BEL preset collision
and separates compatible mapping/endpoint imports from the reload policy decision.
Production integration remains pending. Standalone
frontend localization/display changes remain excluded.
