# Power Sled Native Input Diagnosis — 2026-10-09

## Confirmed Test Menu Cause

The retained unexpected Test Menu transition is native program behavior. The
adapter and Sega 315-5649 reads preserve P2 Entry as IN1 bit `0x04`, while
IN0 Test bit `0x04` stays released. The native input routine packs P2 Entry
into bit 10 (`0x00000400`) of its edge field at `0x00529368`.

In the Relay-derived program used by Main and Relay:

| Program Address | Native Action |
| --- | --- |
| `0x0000eec0` / `0x0000eec8` | Read IN0 / IN1 as separate byte registers. |
| `0x0000efd0` | Write the packed rising-edge input field. |
| `0x000bd4c0`–`0x000bd4d4` | Accept operator command input only for native role `0x0100` or `0x0200`. |
| `0x000bd500`–`0x000bd508` | P2 Entry bit 10 sets outgoing command `0x1000` at `0x005293f4`. |
| `0x000bd5e0`–`0x000bd60c` | Received command `0x1000` selects state 15 at `0x0053e744`. |
| State Table `0x00014ec0` | State 15 dispatches to Test Menu handler `0x0001c0b0`. |

The diagnostic linked RetroArch run confirms both the command write and state
transition, rather than inferring the cause from a screenshot:

| Program | Native Role | Command Write | State 4 → 15 |
| --- | --- | --- | --- |
| Main | `0x0200` | Frame 2391, PC `0x000bd508`, `0x0001` → `0x1000` | Frame 2395, PC `0x000bd60c` |
| Relay | `0x0100` | Frame 2043, PC `0x000bd508`, `0x0001` → `0x1000` | Frame 2045, PC `0x000bd60c` |
| Slave | `0x0000` | No local operator-command write from this pulse | Frame 1699, PC `0x000bd5fc`, after receiving the network command |

All three programs keep raw IN0 at `ff` during this transition. The Slave
program uses nearby routines shifted by 16 bytes relative to Relay-derived
Main; its PCs must not be compared without accounting for that difference.
This explains why the earlier Slave-only P2 Entry probe did not reproduce
Test Menu: Slave role `0x0000` does not generate the special operator command.

The transition does not justify changing the I/O wiring, CPU bit operations
or existing button bindings. The original hardware labels remain available;
operator commands are role dependent and should be distinguished in gameplay
recipes from rider Entry/Call inputs.

## Operator Command Paths

The same role-gated native routine translates the four IN1 buttons as follows.
The corresponding receiver task must be active for a state transition.

| Existing Core Binding | IN1 Bit | Native Command | Confirmed Or Decoded Destination |
| --- | --- | --- | --- |
| B / P1 Entry | `0x01` | `1` | Return to state 4; not a generic race-start confirmation. |
| A / P1 Call | `0x02` | `2` | State 4 → 5, selection path. |
| Y / P2 Entry | `0x04` | `0x1000` | State 4 → 15, Test Menu. |
| X / P2 Call | `0x08` | `4` | State 5 → 6, next gameplay path; runtime qualification below. |

These commands describe the tested Main/Relay roles. They do not redefine
P1/P2 semantics on a rider Slave or establish a complete operator manual.

## Runtime Scope And Evidence

The investigation reuses `scripts/test-retroarch-netpacket.py` with direct
Network RetroPad input, separate three-process RetroArch sessions, retained
validated SRAM, ANS Main Red / Slave Silver / Relay, screenshots and frontend
PCM. Temporary logging adds native I/O reads, CPU registers and selected
work-RAM state/command writes; it does not alter game values or branch decisions.
No input movie or calibration change is used.

Evidence is retained under
`build-libretro-gpu/validation/power-sled-native-io-20261009/`:

- `run/`: native I/O reproduction with B then Y on all units.
- `commands/run/`: command and state trace, Test exit and Main-only Entry.
- `start/run/`: role-specific selection and rider confirmation.
- `start-after-confirm/run/`: repeated operator start after confirmation; state 6 reached on all units.

The source, diagnostic binaries, command arrays and recipes are retained in
that ignored evidence directory. Local program dumps are private diagnostic
artifacts and are excluded from Git. Native source analysis reads the existing
local MAME disassembler definitions; no MAME instance or acquisition script
runs outside the target core.

The diagnostic source is restored byte-for-byte after building separate test
libraries. The rebuilt normal core and both installed core copies match
SHA-256 `00738f3a3255675a6643106db942e8ef81640700bb47e7a863bb95ba211d36b1`.
No emulation or binding fix is applied for this expected native transition.

## Selection And Boarding Qualification

The `start` trace demonstrates a timing conflict in the earlier start attempt.
Main P1 Call sends command 2 and all programs enter state 5. Main P2 Call then
writes command 4 at PC `0x000bd518`, but the local mode-confirmation task
immediately overwrites it with command 3 at PC `0x00033694` in the same frame
(2683). Slave Entry likewise completes its own confirmation and writes command
3 at PC `0x00033684` (frame 2800). No program reaches state 6 in that run.

`start-after-confirm` first confirms Slave Entry, then sends Main P2 Call
twice, with a three-second release interval. The first pulse is consumed by
Main's own confirmation task; the second leaves command 4 available to the
network receiver:

| Program | State 4 → 5 | State 5 → 6 | Final Retained State |
| --- | --- | --- | --- |
| Main | Frame 2115, PC `0x000bd5a8` | Frame 2995, PC `0x000bd6e8` | 6 |
| Relay | Frame 1764, PC `0x000bd5a8` | Frame 2644, PC `0x000bd6e8` | 6 |
| Slave | Frame 1418, PC `0x000bd598` | Frame 2298, PC `0x000bd6d8` | 6 |

The screenshots independently show mode selection, local rider confirmation
and animated boarding/track introduction. No program enters Test Menu or the
next state 7 in this run. The final observation extends 42 seconds after the
second start pulse. It does not verify playable racing, steering or complete
sound accuracy.

## Precise Next Prerequisite

State 6 installs the receiver task at `0x000bd720`. That task reads the
received command, tests for **5**, and requests state 7 at `0x000bd750`.
State 7's initializer subsequently writes command 5 itself; it does not provide
an automatic way to reach state 7 from the retained state-6 sequence.

The operator command decoder also recognizes native input bit 12, corresponding
to **IN1 `0x10`**, and writes command 5 at `0x000bd528`. Current core bindings
cover IN1 `0x01`/`0x02`/`0x04`/`0x08`; no binding supplies `0x10`. The local MAME
input definition labels IN1 `0xf0` unused despite these additional role-gated
program command paths. This is a concrete candidate for an unexposed operator
input, rather than evidence that the link itself is broken.

The next integration step is to qualify that input in a temporary diagnostic
build and determine its actual runtime effect before exposing a verified
operator action. Do not force a RAM state, auto-send command 5, bypass safety
logic or infer an original cabinet label from the command number. The hacked
Main program, the physical meaning of unused inputs and any additional gameplay
prerequisites remain explicit limitations.

## Final Review

`review.json` pins all four run manifests/results, twelve program exits,
screenshots, diagnostic core hashes, native state events, SRAM identity/CRC,
three-copy Ride values, audio and source/artifact restoration. Every unit exits
0 with native link ready, no forced termination and no runner-owned residue.
Main Red / Slave Silver / Relay values remain consistent in all copies.

Recorded signed-16-bit PCM peaks, in Main / Relay / Slave order:
`0/794/0`, `0/874/0`, `0/1211/3055`, `0/1211/2987`. Slave PCM is reproduced on the
selection/boarding paths, while Main remains silent. This is output evidence,
not a fidelity or listening qualification.

The original source and both installed core hashes were rechecked after all
runs. Only documentation and roadmap findings are integrated by this diagnosis.

## Operator Start Integrated — 2026-10-09

The command 5 candidate is now qualified: Main Port 1 Start supplies native
IN1 `0x10`; all three programs advance from boarding state 6 to race state 7.
Main and Slave show the race timer, position and course movement. Start is
integrated on Main/Relay Port 1, preserving the old Start and Entry/Call wiring.
The normal installed core is checked separately. Earlier no-race findings above
remain the historical observations before this binding was available.
See `Docs/POWER_SLED_OPERATOR_START_2026-10-09.md` for evidence and outstanding
handlebar, audio and full-race qualification.
