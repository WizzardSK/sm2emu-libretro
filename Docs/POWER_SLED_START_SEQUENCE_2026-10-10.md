# Power Sled Start Sequence — 2026-10-10

## Experimental Alternative

The original operator sequence below applies with Relay Commands On Master
Disabled. With the experimental System selector Enabled, Coin or Start opens
selection; Entry P1/P2 confirms; native departure completion automatically
enters pre-race; Start or Entry P1/P2 requests the race. Call P1/P2 activates
Emergency Stop. Coin/Start recovers to intro, then another Coin/Start opens
selection. Test Menu preserves Entry/Call actions. See
`POWER_SLED_RELAY_COMMANDS_ON_MASTER_2026-10-11.md` for implementation, evidence
and limits; the selector defaults to Enabled and requires content reload.

## Practical Sequence Using Game Inputs

The reconstructed Master uses the Relay donor's operator decoder. Its original
factory program is undumped. Names below identify game inputs, independently
of the frontend controller bindings. Since the 2026-10-11 update,
Call/Entry P2 retain controller 2 bindings and additionally use controller 1
North/West respectively. See [Current Controls](POWER_SLED_CONTROLS_2026-10-11.md).

| Step | Master Input | Each Linked Slave | Result |
| --- | --- | --- | --- |
| 1 | Call P1 | No operator command needed | Opens mode selection |
| 2 | Select with the handlebars | Select with its handlebars | Local mode selection |
| 3 | Call P2, then release | Entry P1, then release | Confirms the mode and starts platform departure |
| 4 | Call P2 again | No second confirmation in the qualified recipe | Enters boarding / pre-race |
| 5 | Start in the pre-race phase | No operator Start needed | Requests the race; initialization waits for native countdown readiness |

To see the complete departure, allow approximately seven seconds at default
60 Hz between steps 3 and 4. The retained complete-animation reference uses
eight seconds. This is viewing guidance, not an enforced delay: command 4 can
skip the remaining animation. No input queue or automatic operator sequence
has been added. In Standalone Mode the same Master sequence applies, with
no separate Slave confirmation.

## Why Call P2 Is Used Twice

The Main/Relay operator decoder at `0xbd4c0` consumes new input edges from
`0x529368` and writes commands to `0x5293f4`. During mode selection, local
confirmation also consumes the Entry/Call mask `0x0f00` at `0x3355c`.
It sets the local confirmation flag, starts sound command 9, and writes
command 3 at `0x33694`. This can overwrite the operator command 4 generated
by that first Call P2 activation. After confirmation, that selection callback
is replaced. Release and activate Call P2 again to supply a new edge and
command 4 for the next phase.

The four Master departure masks already match `0x0f00`; thus its Call
confirmation also starts the moving-arm task. See
[Boarding Diagnosis](POWER_SLED_BOARDING_ANOMALY_2026-10-10.md).

## Operator Inputs And Native Conditions

| Master Input | Command | Native Effect |
| --- | --- | --- |
| Entry P1 | 1 | Attract / demo, phase 4 |
| Call P1 | 2 | Mode selection, phase 5 |
| Entry P2 | `0x1000` | Test Menu, phase 15 |
| Call P2 | 4 | Boarding / pre-race, phase 6 |
| Start | 5 | Race request, phase 7 |

Entry P1 returning from pre-race to the intro follows the reconstructed
Master's operator decoder: at `0xbd4e0` its input edge writes command 1,
which selects attract/demo. It is not a race confirmation on this role.
Secondary West is Entry P2 (Test), and North is Call P2 (boarding/pre-race);
they do not change those native commands. Start requests the race.
The original Master is undumped, so this explains the current donor-based
program without asserting original factory Master behavior.

The Slave role does not execute this operator decoder. Its Entry P1 confirms
the local selection rather than issuing Master command 1. P2 identifies the
second local input group; it does not mean the linked Slave. Use one operator
input at a time: several bits can overwrite the shared outgoing command in
the same update. Original physical operator-panel labels remain unknown.

Command 4 is received at `0xbd6c0`; command 5 at `0xbd720` advances to phase 7.
The countdown task sets `0x51ac64` after its counter becomes negative at
`0xcfcc4–0xcfcd0`. The full race constructor at `0x438e0` returns while that
flag is zero. Requesting the race and completing native countdown preparation
are therefore distinct conditions. Start does not replace mode confirmation
or boarding. The current Standalone implementation uses this full constructor.

## Evidence And Limits

Read-only disassembly excerpts and the source hash are retained at
`build-libretro-gpu/validation/power-sled-start-sequence-20261010/`.
The recipe in `scripts/test-power-sled-gameplay.py:race_replay` supplies Master
Call P1, Call P2, Call P2 and Start; Slave Entry P1; and no Relay inputs. Its
older five-second departure interval is superseded for complete-animation
viewing by the eight-second reference in
`build-libretro-gpu/validation/power-sled-boarding-duration-20261010/`.
Retained standalone traces progress through phases 4, 5, 6 and 7 with the same
Master sequence. Bindings were checked against `src/libretro/input.cpp`.

This review adds no emulator run, ROM patch, core build or deployment. It
documents a qualified path and its native conditions; original Master fidelity
and all alternative valid sequences remain unqualified.
