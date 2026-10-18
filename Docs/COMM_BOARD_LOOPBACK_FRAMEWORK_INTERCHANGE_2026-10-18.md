# SM2 Communication Board Loopback Evidence — Framework Handoff

Date: 2026-10-18. Source: `Docs/COMM_BOARD_STANDALONE_REVIEW_2026-10-18.md`.

Framework F14 and `NETWORK_REVIEW_GUIDE.md` already distinguish board fitting,
local loopback, frontend roster, native board state and completed gameplay. F14
normally removes the emulated board when Linked Cabinets is Disabled, retaining
it in loopback only for games requiring it. This handoff contributes SM2-specific
evidence; it does not redefine that general rule.

- Upstream keeps the Model 2 communication board fitted with local loopback when
  external linking is off. At the user's explicit request, SM2 Libretro follows
  that upstream behavior for every game, including Daytona and Indy 500.
  `Linked Cabinets = Disabled` disables external transport but does not remove
  the board or change ANRS authority. This SM2 choice is broader than F14's
  normal board-removal rule; do not copy it to another core without inspecting
  that emulator and game hardware.
- The native game enables its board through the communication control register.
  The frontend/launcher does not set that native enable bit. A two-peer RetroArch
  roster therefore does not prove the game established a cabinet link.
- Daytona, Indy 500 and Indy 500 Deluxe are positive native-link controls:
  retained linked logs show `enabled=1, alive=1, count=2`.
- Two-instance trials for Dynamite Baseball, Dynamite Baseball '97, Pilot Kids,
  Rail Chase 2 and Zero Gunner established frontend rosters but both native
  boards stayed `enabled=0, alive=0`. These games remain `Not Supported` in the
  two network Core Options. The observations do not prove they can never use
  the board under another operator configuration.
- For those five games and reviewed clones, matched 700-frame board-present and
  board-absent ABI paths had equal final video, audio and native-save hashes.
  This bounded startup evidence does not justify changing upstream board
  presence or imply complete gameplay equivalence.
- Virtual On supplied a deeper transition counterexample: an absent board could
  pass attract mode but show black video when entering a match, with audio still
  running. A fresh NVRAM alone did not establish that the board was unnecessary.

Reusable review implication: retain F14's per-game conditional board rule, and
use both native board state and a gameplay transition before classifying an
unfamiliar game's standalone hardware requirement. The five negative native-link
results do not prove that loopback is required by those games. This is evidence
for an existing Framework distinction, not a request to apply SM2's policy to
other hardware. No destination-core implementation is authorized by this file.

See the source report for runner paths, build/install hashes and evidence limits.
