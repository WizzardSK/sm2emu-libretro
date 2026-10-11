# Power Sled Controls — 2026-10-11

## Current System Visibility, Relay Gain And Input Revision

The three Power Sled System options (Relay Audio, Standalone, Relay Commands
On Master) are shown only for `powsledm`, `powsled` and `powsledr`, by explicit
user request. Their Master-only applicability remains unchanged.

Audio adds **Power Sled Relay Audio Gain** with Auto, Mute, 10% through 100%,
in that order; Mute is raw `0`. Auto uses the Relay sound-board profile under
Enhanced Audio Balance, otherwise unity gain. This controls only the auxiliary
SCSP created by Relay Audio on Master. Rider **SCSP Gain** remains independent
and Master Volume applies to the resulting mix. It updates immediately, is
visible under the default Audio option convention and is a no-op without the
auxiliary board. No sound program or timer is disabled by Mute.

| Controller | Physical Binding | Game Input |
| --- | --- | --- |
| P1 | A / Cross | Entry P1 |
| P1 | B / Circle | Call P1 |
| P1 | D-Pad Up Or Down | Entry P1 |
| P1 | West | Entry P2 (Secondary) |
| P1 | North | Call P2 (Secondary) |
| P1 | L3 | Service A / Select |
| P1 | R3 | Test A |
| P2 | A / Cross | Entry P2 |
| P2 | B / Circle | Call P2 |
| P2 | D-Pad Up Or Down | Entry P2 |
| P2 | North | Shutdown Button |
| P2 | L3 | Cancel Error |
| P2 | R3 | Cancel Network Check |

P2 no longer duplicates Service A, Service B or Test A. Shutdown retains the
old Service A hardware line with its new user-facing name. Cancel no longer
uses P1 shoulders. Service A / Select and Test A remain subject to P1's
Service-enabled controller variant. All four handle Y axes retain their
inverted polarity, center 0x80 and 00..FF range.

Verification: existing input, option/save-RAM and audio-balance checks pass.
The synthetic two-SCSP fixture confirms independent mute and 50% Relay scaling;
a 60-frame actual-core ABI load with Relay Audio and 50% Relay gain passes
Save State round-trip and deterministic replay. This is not a new physical-pad
or gameplay qualification. Evidence and normal-core deployment are retained in
`build-libretro-gpu/validation/power-sled-input-gain-20261011/`.

Installed normal-core SHA-256 for this revision:
`ccf6e961fa5c41bd95d87b7c2c676e6be977815029245f63eaa76d0fda4c7a3a`.
A backup is retained in the evidence directory; the dev core remains absent.
Recommended setting: Sol High, forecast 1–3 percentage points. The account meter
remains at 0% (integer resolution; no measurable increment), cap 35%; reset
18 October 2026 at 07:47 Europe/Rome.

Earlier sections below document historical bindings and builds.

## Physical A/B Binding Correction

The requested A = Entry / B = Call refers to physical Xbox buttons. The installed
Xbox HID/SDL2 autoconfig labels RetroPad B as physical A and RetroPad A as
physical B. The earlier A/B update used RetroPad names and reversed the intended
physical layout. All three sets now use RetroPad B for Entry and RetroPad A for
Call, on both ports. DualSense defaults correspond to Cross Entry / Circle Call.
Inverted Left/Right Stick Y polarity is preserved. Current recipes follow the
corrected RetroPad bindings; earlier sections below record their historical builds.
Evidence: `build-libretro-gpu/validation/power-sled-physical-ab-20261011/`.
Build and input checks pass for all sets and both ports. Normal-core installation
uses a verified backup and hash: `84ab2770e78a346b9672bce6abf1f0290618b98701724d3c25702b4c6a176d48`.
The development core remains absent. Physical-pad gameplay has not been rerun.
Restart existing RetroArch instances.

## Y Axis Polarity Update

All three sets invert Left Stick Y and Right Stick Y on both controller ports,
as requested by the user. Positive frontend travel now produces lower native
ADC values; negative travel produces higher values. Neutral remains 0x80,
with full 0x00..0xff travel. Saturation prevents -32768 from wrapping during
inversion. Entry A and Call B remain the current button bindings.
The qualified race replay compensates the frontend inversion to preserve its
native command sequence; historical movies retain their original context.
Evidence: `build-libretro-gpu/validation/power-sled-axis-polarity-20261011/`.
The normal build and input checks pass for all three sets, including both
controller ports, neutral and signed extremes. Normal-core installation retains
a backup and verifies SHA-256 `185db58099d2d51d88ba081b4f9f27e404929988e8c4e7e7a62ec95b253d364d`.
The development core remains absent. Restart existing RetroArch instances.
Physical-pad/gameplay behavior was not rerun for this polarity correction.

## A/B Binding Update

At the user's request, all three Power Sled sets now map Entry to RetroPad A
and Call to RetroPad B on both controller ports. Native input bits and
Left/Right Stick Y mappings are unchanged. Current replay and sample recipes
use the new bindings; historical captures retain their original context.
Build, input checks and installation evidence are recorded in
`build-libretro-gpu/validation/power-sled-buttons-ab-20261011/`.
The normal core builds and all input-profile checks pass, including A/B
descriptors and native P1/P2 bit isolation. The normal installed core is
SHA-256 `7fbe5c27cfdbe6001f338d743e3ffa5036eeb1e124c04c03eee859315b197de4`; backup/hash verification passes and
the development core remains absent. Existing RetroArch instances must restart.
Physical-pad/gameplay behavior has not been rerun for this binding change.

## Y Axis Correction

The initial implementation selected X incorrectly. The current core exposes
and reads **Left Stick Y / Right Stick Y** for Left/Right handles on both P1
and P2. X axes and old trigger inputs do not contribute. The signed byte-range
conversion, neutral value, native mux channels and button bindings are unchanged.
The current linked race replay generator supplies Y records.

Evidence: `build-libretro-gpu/validation/power-sled-axis-y-20261011/`.
The normal core builds and input checks pass for all three sets, including Y
endpoints, independent rider channels, Y descriptors and ignored X movement.
The normal installed core for the Y-only correction was SHA-256
`117dc8a91b71d1a03cb9b041a3f6f0c55a4bf70cd622c71ea595cbc75a153850`.
Installation retains a backup and verifies the binary hash; the development
core remains absent. Existing RetroArch processes must reload the core to use
the new mapping. No physical-input/gameplay run is claimed for this correction.
Older runtime evidence and hashes below describe their original builds.

## Controller Assignment

| Game Input | Controller | Default Frontend Binding |
| --- | --- | --- |
| Entry P1 | 1 | RetroPad B (Xbox A / Cross) |
| Call P1 | 1 | RetroPad A (Xbox B / Circle) |
| Left P1 | 1 | Left Stick Y |
| Right P1 | 1 | Right Stick Y |
| Entry P2 | 2; secondary on 1 | P2 RetroPad B (Xbox A / Cross); P1 West / RetroPad Y (Xbox X / Square) |
| Call P2 | 2; secondary on 1 | P2 RetroPad A (Xbox B / Circle); P1 North / RetroPad X (Xbox Y / Triangle) |
| Left P2 | 2 | Left Stick Y |
| Right P2 | 2 | Right Stick Y |

Both handles are centered signed axes with inverted frontend Y polarity: ADC neutral 0x80, endpoints 0x00 and
0xff. P1 uses native mux channels 3/1 for Left/Right; P2 uses 7/5. P1 West/North also supply P2 Entry/Call, including when controller 2 is disabled. Triggers no longer supply these axes. Coin, Start,
Test/Service and cabinet cancel inputs retain their existing scope.
Disabled controllers return their handles to the configured neutral value.
Controller 2 must be enabled in the frontend to operate P2 inputs.

## Master And Slave Test Menu Comparison

Both programs use the same selection mask 0x0540 (Entry P1, Entry P2,
Service B) and confirmation mask 0x0a80 (Call P1, Call P2, Cancel Error).
Relay-derived code reads these in the Test Menu callback at 0x1c320;
the Slave callback is displaced by 16 bytes. The masks are equal, not inferred
from different button labels.

The independent operator decoder accepts native roles 0x0100 (Relay) and
0x0200 (Master). It skips the Slave role 0x0000. Call P1 also emits command 2
from that decoder, which requests gameplay mode selection. This explains why
the suspected extra gameplay action is specific to Master/Relay despite equal
Test Menu masks. The frontend itself supplies only one Call P1 bit.

The runtime observer also shows Entry P1 leaving Test phase 15 for attract
phase 4 via operator command 1. The Call-P1-only candidate is therefore
insufficient. The production database skips the separate operator decoder
while global phase 0x53e744 is 15. Local Test selection, Call confirmation and
Exit remain in their original callbacks. Outside Test the decoder receives
the original edge field and follows the original path. Slave code is unchanged.

The detour at 0xbd4d8 uses reviewed empty donor space 0x1f0400–0x1f041b.
Original instruction, branch targets and unique patch offsets are verified.
ROM archives remain unchanged.

## Verification

Evidence root: `build-libretro-gpu/validation/power-sled-controls-20261011/`.
The input-profile checks pass for all three sets, including P2 isolation,
signed axis endpoints, independent rider channels, neutral/release behavior
and ignored legacy triggers. The normal core builds. Native mask comparison
and decoded production detour are retained in JSON reports. The gameplay
replay generator now routes Call P2 to controller 2 and uses signed stick axes;
historical input movies retain their original evidence and cannot validate
the new assignment without regeneration.

The initial runtime attempt failed before Test because the runner selected
OpenGL; an import-path retry and a guard against an existing user instance also
prevented startup. The retained Vulkan retries use isolated configurations,
saves and ports alongside the existing user process and clean up only owned
processes. Runtime results and deployment are recorded separately below.

## Runtime Outcome And Deployment

The rejected Call-only observer records phase 15 before Entry P1, then phase
4 at frame 1530 and later selection phase 5. The final Test-owner observer
keeps phase 15 through Entry/Call and captures the native CRT grid. The normal
core repeat processes further Call activations inside CRT Test and captures
Color Test, rather than gameplay selection. The repeat directory is named
`normal-exit-vulkan`, but its screenshot qualifies CRT progression, not a
complete Test Menu exit. The native Exit callback at 0x1c4a0 remains unchanged
and increments phase 15 to 16, beyond the patch condition.

All completed isolated runs exit cleanly without forced termination or owned
residual processes. Physical sticks, frontend remaps and a complete native
Exit/reboot remain separate from this bounded menu proof. Normal deployment
is recorded in `installation.json`, with backups and SHA-256 verification for
the installed core and both configured system-database destinations. The
normal installed core is
`56d91afd312b8fe47be2bea52dd03c9b02bbf9caee6ecf525813ef2a6b28f3eb`.
The development core remains absent. No commit or push.

## Physical Pad Follow-Up

Previous generated-input checks did not qualify the user's three physical pads.
The installed core matches the reported session hash. Distinct per-process SDL
indices were not a common physical-device identity: the logs enumerate the pads
differently. A bounded HID comparison, which distinguishes Xbox Black/White,
selected the same Black Xbox for all three local Port 1 mappings: host index 0,
Slave index 1, Relay index 2. This reproduces an assignment failure, not manual
menu scrolling. Native Test callback `0x1c320` advances local cursor `0x544ba0`
from local input edges `0x529368`; it does not broadcast cursor movement.

The runner now captures an alphabetically sorted list of physical HID names
once and reserves each selected name for its instance's Port 1. It uses the HID
joypad driver in isolated macOS configurations, clears other port reservations,
and writes a permutation of all indices for RetroArch's reservation swaps.
Configuration keys occur once. Identical physical pad names require distinct
macOS names. Windows/Linux keep numeric frontend indices.

Evidence: `build-libretro-gpu/validation/power-sled-pad-routing-20261011/`.
The final `native-hid-reserved-3` logs and `reservation-review.json` confirm
DualSense Purple reserved for host, Xbox Black for Slave and Xbox White for
Relay, each on local Port 1. Twelve launcher checks pass. The initial SDL probe
failed at window placement. Subsequent bounded probes reuse the runner with
UI positioning omitted by a private wrapper; they do not qualify manual input,
window layout or gameplay. No core/global configuration changes are required.

The RetroArch source matching installed revision `9be7ec92` supports device-name
reservations and preserves custom indices when no reservation exists:
https://github.com/libretro/RetroArch/blob/9be7ec92/tasks/task_autodetect.c
Ordinary autoconfig messages alone did not prove index reassignment; the
per-process enumeration difference is the supported finding.

## Axis Range From The Program

Native ADC reader `0xeea0` selects channel 0 at `0xf040`, then reads all eight
bytes at `0xf058` into `0x529370..377` without scaling/filtering. Rider I/O
callback `0x1d370` prints the handle bytes directly: `0x529371/373` for P1 and
`0x529375/377` for P2, using hexadecimal formatting. The frontend maps signed
stick endpoints to `00/FF`, neutral `80`, without a `67..90` restriction.

The electronic byte range differs from mechanical calibration. Volume Setting
records Forward/Back endpoints. The program derives centers, spans and
tolerances from those bytes; for example, `0x15c40` compares the P1 Right reading
against calibrated endpoints. This does not prove original handles traversed
the entire ADC range. No fixed expected `67..90` mechanical range was identified
in this path. Physical travel remains unqualified; calibration is unchanged.

## Entry And Call Evidence

The native Test Menu says to select with Entry and confirm with Call. Slave
mode selection uses the handles to select and Entry to decide. Outside Test,
Main/Relay decode Entry P1 as attract, Call P1 as mode selection, Entry P2 as
Test, Call P2 as boarding/pre-race. See `POWER_SLED_START_SEQUENCE_2026-10-10.md`
for the qualified reconstructed Main sequence.

The local MAME driver documents Entry/Call names and bits, but not their
physical cabinet purpose. A bounded web search did not locate a Sega operator
manual explaining it. No factory operator workflow is inferred from the
reconstructed Main program.

## Standalone Service Exit Follow-Up

The separate matched replay on 2026-10-11 qualifies Call on Exit completing
native restart and returning to attract in Standalone. A guarded detour clears
the stale outgoing Test command before resuming native Exit. This supersedes
the earlier pending Exit/reboot qualification for Standalone only; linked-mode
Exit and physical pad operation remain separate. The normal core is installed
with backup/hash verification; dev remains absent. See the Service Exit section
of `POWER_SLED_STANDALONE_EXPERIMENT_2026-10-10.md` for root cause, trace and
deployment evidence.

## Secondary P2 Digital Bindings — 2026-10-11

At the user's request, P1 West / RetroPad Y supplies P2 Entry and P1 North /
RetroPad X supplies P2 Call on all three sets. The original controller-2
Entry/Call and handle axes remain available. Secondary digital bindings work
with controller 2 disabled; controller-2 West/North have no added function.

The existing input checks verify descriptors, individual native IN1 bits
(`0x04` Entry P2, `0x08` Call P2), P2-disabled operation and retained P2 primary
bindings on Master, Slave and Relay. Build and checks pass. The normal core
is installed with backup/hash verification, SHA-256
`7f24c5b0071a2f91c71c0aef991ec8ecb9f76f35e06e11192a84571bd78a79c8`.
Evidence: `build-libretro-gpu/validation/power-sled-secondary-bindings-20261011/`.
Deployment reuses the previous bounded installation procedure. Dev remains
absent. No new gameplay or physical-pad run is claimed; reload the core to use
the new descriptors/mapping.

Entry P1 returning from pre-game to intro is the current reconstructed
Master's native operator command 1, not a binding duplication. The undumped
original Master prevents a factory-fidelity claim. See
`POWER_SLED_START_SEQUENCE_2026-10-10.md` for the reviewed decoder and commands.

## Experimental Master Command Convention

The digital bindings above retain the same native I/O bits. With the new
Relay Commands On Master selector Enabled, the Master program interprets Coin
or Start as selection from intro, Entry as confirmation / pre-race start, and
Call as native Emergency Stop. Departure completion automatically issues the
boarding command. Test Menu retains its Entry/Call handlers. With Disabled,
the original operator commands documented above remain. Slave bindings and
program are unchanged. See `POWER_SLED_RELAY_COMMANDS_ON_MASTER_2026-10-11.md`.
