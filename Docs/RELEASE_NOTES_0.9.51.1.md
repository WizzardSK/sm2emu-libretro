# SM2-Emu Libretro 0.9.51.1 — Unpublished Attempt

The remaining ImGui submodule native-EOL mismatch prevented release packaging.
No release assets were published. See [0.9.51.2](RELEASE_NOTES_0.9.51.2.md).

Reconciled upstream **0.9.51** plus port revision **1**, following the mandatory
version convention. The historical full-source import is 0.9.13; the
[commit-by-commit ledger](UPSTREAM_RECONCILIATION_0.9.51.md) accounts for every
change since the previously reconciled 0.9.44. Earlier release tags are retained. The first tag attempt, 0.9.51.0,
passed compilation and runtime-independent checks on all five platforms, but
Windows packaging rejected CRLF-converted checkout texts against canonical LF
source. It published no release. This port revision disables checkout conversion
before cloning on Windows, including submodules, retaining exact source/package
hash validation. The original tag is not rewritten.

## Changes Since 0.9.44.0

- Experimental GPU widescreen expansion, with native HUD proportions and
  upstream background fill. Disabled default; Auto/16:9 permit Expand, forced
  4:3 blocks it. Software and native widescreen families retain their behavior.
- Super GT 24h native A/B/C pedal handling, VR2 controls, Type B initial setup
  and Auto 16:9 for B. Existing valid SRAM has priority over initial defaults.
- Pilot Kids VBlank tile-RAM latch, Last Bronx geometry command, i960
  interrupt-mask timing and native Daytona/Indy-family drive-board responses.
- Virtua Cop flash-filter latency extended to two frames, with presentation
  history retained across states and existing Disabled behavior preserved.
- Gear Shift Neutral Time: 100 ms default, 0–500 ms in 10 ms steps, for
  four-speed sequential steps. Direct gear positions/Neutral bypass it;
  0 restores immediate shifting. Native two-button shifters are unchanged.
- Gunblade NY aim mapping selector: Custom (SM2-Emu) / Linear (MAME).
- Preliminary Daytona GTX 2004 protection/content and reviewed initial NVRAM.
- Independent Linked Cabinets and Auto Network Role Settings, native loopback,
  global Controller Profile Type, canonical menu wording and functional order.
- GPL-3.0-or-later adoption with additional upstream NOTICE terms and retained
  BSD provenance; complete source/dependency packaging, including Dear ImGui.

## Compatibility And Verification

Technical core/save/system identifiers remain stable. Current fixed-size state
containers retain older supported formats; new transient presentation/gear
fields use reserved frontend-tail bits. Older cores cannot reproduce fields
they never understood. Existing valid SRAM and published control conventions
remain authoritative. Native initial defaults do not replace valid saved data.

Local evidence includes ROM-free input/options/audio/drive/CPU checks, old/new
Software and Vulkan comparisons, legacy-state continuation, active-crossing
state replay, pristine headless comparisons across four board variants, GPU
expansion/context recovery and bounded RetroArch checks. See the dated reports
linked from the roadmap. Five-platform CI rebuilds and checks the exact release
source and packages; runtime qualification is not inferred from compilation.
Physical lightguns, every game/color/network topology and driver combination
are not exhaustively qualified. Widescreen and reconstructed Power Sled modes
remain experimental. The optional Daytona Drive Board display-range inquiry
is not a release gate.

## Downloads And Source

Five binary targets: Linux x86_64, Linux arm64, Windows x86_64, macOS arm64 and
macOS x86_64. Packages include core/info/database, LICENSE/NOTICE, retained BSD
and dependency notices, source revision/reference and SHA256SUMS. The release
also publishes complete corresponding source with seven pinned submodules and
source-file hashes. Use the matching packaged games.xml. No ROMs are included.

Earlier releases retain their published licence terms. SM2-Emu Libretro is a
modified version based on https://github.com/dmanlfc/sm2-emu; see LICENSE and NOTICE.
