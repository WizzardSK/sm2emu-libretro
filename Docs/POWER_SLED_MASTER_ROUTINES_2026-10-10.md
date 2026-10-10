# Power Sled Master Routine Analysis

## Result

The deeper static analysis finds shared Master-capable paths in both the Slave
and Relay programs. The current Main initialization already selects the native
Master communication branch, enables the operator decoder and publishes the
Master identity used by the other nodes. No additional dormant Master-only
engine or Slave-exclusive Master routine is identified in the inspected paths.

There are narrower leads: color-dependent presentation routines which do not
handle identity `0x0200`, and two operator commands without a Libretro binding.
At this static checkpoint neither finding establishes a new gameplay defect
or justifies forcing an unknown branch. The subsequent paired RetroArch probe
demonstrates the missing Main mode-selection 3D scene and integrates its focused
NVRAM-color correction for both donors. See
`Docs/POWER_SLED_MAIN_PRESENTATION_2026-10-10.md`. Other placement selectors have
no demonstrated defect. The operator follow-up qualifies Emergency Stop, Entry recovery and controlled race exit; see `Docs/POWER_SLED_OPERATOR_AND_LAYOUT_ANALYSIS_2026-10-10.md`. No production binding is added.

## Method And Evidence

Private evidence directory:
`build-libretro-gpu/validation/power-sled-master-routines-20261010/`.

- Reuse the retained, original 2 MiB Slave and Relay CPU-region dumps from
  `power-sled-native-io-20261009`; no ROM archive is modified.
- Decode i960 instructions using the existing diagnostic decoder and the local
  MAME disassembler's opcode/operand definitions. No MAME instance is launched.
- Map absolute role, complement, mode, local-index and node-count accesses.
- Follow boot calls, the main loop, role comparisons, received-packet selection,
  operator commands, state dispatch and registered task callbacks.
- Verify changed direct branch/call targets against the actual address mapping,
  rather than accepting a displacement merely because it differs by 16 bytes.
- Walk eleven anchored instruction ranges and compare four callback tables.

`analyze.py`, `references.json`, the named disassembly windows and
`verify_paths.py` / `verified-paths.json` retain the steps and results. Addresses
below are Relay program offsets. Corresponding Slave addresses after the role
initializer are 16 bytes earlier; earlier addresses are unchanged.

| Original Program | CPU Region SHA-256 |
| --- | --- |
| Relay | `b90bab4c013732329c6decc7b655ba5d04610ea65e90eb16bf794a390fe39792` |
| Slave | `5c3c307f68098b1e74577a8c4de1660c9e2883ba2080f971dda867655e40f44a` |

The aligned ranges exclude the different initializer bodies and the final fill
tail. They contain 520,241 identical words, 595 changed control instructions
whose mapped targets match, 3,428 relocated absolute ROM values and four ROM-fill
boundary differences. No other difference remains in those ranges. All eleven
anchored walks and all 38 callback-table entries match after relocation.

Each program has 79 candidate absolute accesses to the role field
`0x005293f0`, three to its complement and two to the native mode byte. This
scan is not a proof against indirect aliases or every possible execution path.
Linear disassembly windows can include data or padding; control-flow conclusions
below use identified code entries and their callers/tables.

## Master Paths Already Selected

| Path | Concrete Evidence | Current Main Behavior |
| --- | --- | --- |
| Communication Master | Mode initializer `0x1571c`; comparison at `0x11d20`; Master branch `0x11d48` | Patched mode 1 takes the existing branch, writes FG = 1 at `0x01a04002` and selects `THIS IS MASTER CONTROLLER`. |
| Operator Admission | Decoder `0xbd4c0`; role checks `0xbd4cc` / `0xbd4d4` | Accepts Relay `0x0100` or Master `0x0200`; current Main passes. |
| Operator Scheduling | Main loop calls `0xbd4c0` at `0x15fa0` | Decoder is already called each loop; no missing scheduler callback is found. |
| Master Packet Selection | `0xcd2b0` scans received roles; `0xcd2e0` stores the selected packet pointer | Role `0x0200` identifies the command source stored at `0x00529464`. |
| Full Packet Map | `0xcd5c8` / `0xcd5e8` / `0xcd6b0` | The second packet-map routine also recognizes Master and stores the same command pointer. |
| Native Roster | Role scans around `0x24658` and `0x249c0` | Master and Relay are recognized separately from rider identities 0–3. |
| Reinitialization | `0x24450` calls the role initializer, then packet-map routines | A native reinitialization path exists; a Service Menu role write alone is not evidence that Master identity remains lost. |

The original mode byte and application role are different fields. Relay's
original mode is 2, while its application role is `0x0100`. Do not equate that
mode with an uncounted communication relay. Similarly, the communication-board
role printed in runtime logs is not the i960 application word `0x0200`.

Previously retained normal-core RetroArch runs qualify operator Start and races
with both donor choices. This analysis adds static reachability evidence; it
does not repeat those runs or extend their gameplay/fidelity qualification.

## Additional Operator Commands

The same decoder in both donors contains the following unbound input paths:

| Native Input Word Bit | Command | Followed Effect | Qualification |
| --- | --- | --- | --- |
| 13, native IN1 `0x20` | `0x0100` | Receiver `0xbd760` selects global state 14; dispatcher `0x2c350` installs its task list from `0x2c390`. | Follow-up RetroArch qualification identifies Emergency Stop and B Entry recovery. Original physical switch label remains unresolved; see the operator/layout report. |
| 15, native IN1 `0x80` | `0x0300` | Receiver `0xbd7c0` sets flag `0x00544c20`; race update `0x372fc` follows a counter path and returns to global state 4 at `0x37380`. | Follow-up isolated RetroArch race qualifies the exit flag and state-4 return after 180 sampled machine frames on all three programs. Original switch label and a fresh subsequent race remain unqualified. |

Both are accepted by Relay and Master; neither is a hidden Master-only
activation switch. Existing Power Sled adapter bindings do not clear those
IN1 bits. The state-14 task list includes the existing Test, state-4 and
shutdown command receivers. The same race-exit flag can also be set by the
received service-status path at `0xbd8f8`.

## Color-Dependent Presentation Leads

The previously integrated Ride caption and first-person sled corrections cover
their specific selectors. Other original routines still use application role:

- The mode-selection task table at `0x32f90` registers `0x33790`. That routine
  chooses drawing callbacks `0xe5e40`, `0xe5770`, `0xe5ab0` or `0xe61a0` for
  rider identities 0–3; Relay selects the identity-0 callback. Master `0x0200`
  reaches `0x337ec` without replacing that task's callback. The targets write
  graphics commands, so this is a presentation candidate, not an audio fix.
- `0x18c30` selects per-identity offsets for several configuration counts. Its
  role-dependent branches return without a new offset for `0x0200`.
- A related graphics path at `0xc2bc8` selects signed offsets for identities
  0–3 and has no dedicated Master case.

These paths are shared by both donors. Switching donor cannot supply a missing
color case. A future presentation correction should use validated NVRAM Ride
only at the demonstrated visual selector, preserve native Master/network
identity, and establish the visible before/after effect. The meanings of all
offsets and their relevance to Main are not yet qualified; broad role
substitution would be unjustified.

## Scope And Roadmap

The later user decision removes donor selection and uses Relay only. The
recommendation below belongs to the historical analysis checkpoint; see
`POWER_SLED_RELAY_ONLY_2026-10-10.md` for current production behavior.

The deeper Master-path analysis is complete within this bounded scope. Retain
the Relay / Slave donor selector and existing corrections. Record the narrower
color-dependent presentation investigation in the roadmap; unbound operator
commands remain research findings, not promised new controls.

Only documentation and private static-analysis artifacts were added at this
checkpoint. Production source, ROM database, options, saves and installed cores
were unchanged. Both installed copies then retained SHA-256
`1447f4bedda679d8da3b22e616b19ece999513dd4551683f9d30d42f54c0dfe1`.
The subsequent presentation correction and deployment are recorded separately
in the report linked above.
No original Master ROM or factory behavior is authenticated by this analysis.
