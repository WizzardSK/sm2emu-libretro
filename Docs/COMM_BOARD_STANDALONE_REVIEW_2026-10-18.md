# Standalone Communication Board Review — 2026-10-18

## Decision And Scope

The native program, rather than RetroArch or the launcher, enables the fitted
Model 2 communication board through its control register. A frontend peer roster
only proves that RetroArch's transport connected. The native `enabled` and
`alive` fields are separate evidence for game use of the board.

The standalone emulator keeps the board fitted in local loopback when external
linking is off. This core now does the same for every set. `Linked Cabinets =
Disabled` still prevents an external link and does not rewrite the selected
native role.

Daytona and Indy 500 are included in this board-fitted local-loopback rule.
They are not part of the five-set exploratory group below: earlier linked
RetroArch runs observed their native boards reach `enabled=1, alive=1` with
two-cabinet IDs and counts. The same positive result was observed for Indy 500
Deluxe. These linked results establish native communication activity, not
complete synchronized gameplay for every variant.

No native link was observed for Dynamite Baseball, Dynamite Baseball ’97,
Pilot Kids, Rail Chase 2 or Zero Gunner in two-instance RetroArch trials.
Those programs left the board at `enabled=0, alive=0` on both peers, even after
the frontend roster connected. They remain `Not Supported` for the two network
Core Options. The board stays fitted for them in local loopback: the bounded
results below do not justify removing upstream hardware configuration.

## Evidence

Evidence root: `build-libretro-gpu/validation/other-link-audit-20261018/`
(ignored local files; no ROMs are committed).

| Check | Result |
| --- | --- |
| Two-instance RetroArch | Both peers started for each of the five sets. The host logged `Slave cabinet connected (2/2)`; each native board logged `enabled=0, alive=0`. The runner's `roster_ready` flag remained false because its marker did not match the actual frontend message; that flag is not native-link evidence. |
| Board-present versus board-absent ABI | Fresh, 700-frame Coin/Start/action paths produced matching final video and audio hashes and matching native save hashes for the five sets. |
| Clone/alternate board paths | Pilot Kids A, Rail Chase 2A, Zero Gunner A, Zero Gunner J and Zero Gunner AJ produced matching board-present/absent video, audio and save hashes through the same 700-frame path. |
| Supported local-loopback regression | Daytona completed an 1800-frame ABI path with the fitted board in local loopback. A separate isolated single-instance RetroArch launch exited normally. This qualifies startup, not a full race. |
| Native-link positive controls | Earlier linked RetroArch logs show `enabled=1, alive=1, count=2` for Daytona, Indy 500 and Indy 500 Deluxe. This distinguishes them from the five exploratory sets that remained at `enabled=0`. |

The positive-control logs are under
`build-libretro-gpu/validation/network-two-option-20261017/frontend-linked/`
for Daytona and `build-libretro-gpu/validation/network-suite-20261009/`
for Indy 500 / Indy 500 Deluxe.

The board-present ABI baseline was the previously installed normal core; the
board-absent baseline was a temporary local build with experimental network
registration used solely to switch board presence. That experiment was not
adopted. The final core removes the experimental registration and keeps the
board fitted in local loopback, following upstream. The earlier local build
with the board-absence rule had hash
`47d1004a4fc697df6c264f0641c79efe954b1193d72d100acae4ff596227925d`;
it is retained only as a historical test identifier.

The final build repeats the five parent-set ABI paths with video, audio and
save hashes matching the earlier board-present baseline. Build and installed
normal-core hashes match at
`199d2a0016c46fb4b459dec2f7953a4c2fe1c73ca1628ea6d107f28d86b90fcf`.
The installed file was replaced atomically while RetroArch was open; an already
running session continues with its previously loaded core until content reload.

These checks establish the tested startup paths, not complete gameplay or proof
that every operator configuration of these games lacks a cabinet-link mode. A
future observed native `enabled=1` or documented link selector should reopen the
corresponding family's classification and role mapping. No unrelated game was
reclassified by this review.
