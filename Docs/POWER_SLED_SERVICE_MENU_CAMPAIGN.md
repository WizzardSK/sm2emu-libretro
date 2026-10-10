# Power Sled Service Menu Campaign

## Current Service Bindings — 2026-10-09

At the user's request, Power Sled swaps the two service bindings in all three
sets and both controller ports:

| Button | Core Descriptor | Native Input | Purpose |
| --- | --- | --- | --- |
| L3 | Service B / Select | IN0 bit 0x40 (Service 2) | Advance The Operator Menu Selection |
| D-Pad Down | Service A | IN0 bit 0x08 (Service 1) | Standard Service Input; Gameplay Effect Unverified |
| R3 | Test A | IN0 bit 0x04 | Open The Test Menu |
| A | P1 Call | IN1 bit 0x02 | Confirm The Selected Operator Action |

The Test/Service controller variant exposes both service inputs; the reduced
variant exposes neither. Current per-set recipes, the complete recipe generator
and the linked runner use L3 for menu selection. Historical captures and their
original manifests below record the previous Down/Service 2 binding; their
acquired NVRAM values remain evidence from that earlier core, not new captures.

Verification: the ROM-free input suite passes for all three sets, including
both service lines, the second-port aliases, reduced-profile eligibility and
existing cabinet inputs. The complete recipe regeneration check and both
diagnostic/NVRAM catalogue audits pass. The binding-package core and both installed
macOS RetroArch copies at that step had SHA256
`367cdfcb96969a7b4866cf32a5f6d4682d3b5fe3963dec5cbdd01184eef71390`.
Backups and the installation manifest are retained under
`build-libretro-gpu/validation/power-sled-service-bindings-20261009-083134/`.
This binding change has no new gameplay or operator-menu runtime capture.


## Current Phase Gate

**Phase 1 — complete for the observed linked MAME Main/Relay/Slave topology.**
The per-set Service Menu hierarchy, labels, commands, numeric ranges, native
Use Default results and conditional Ride ID cycles are reconciled in the three
YAML files, screenshot-derived catalogue and workbook. The scope excludes
contents of diagnostic tests, bookkeeping counters, destructive actions and
calibration acquisition. All excluded root entries are listed.

**Phase 2 — core samples and field mapping validated for the agreed scope.**
The complete, resumable RetroArch recipe finishes **49 stages / 147 independent
program records**. Five Checkpoints and Motion Angle cover native defaults,
steps, limits, the relevant byte boundary and fresh reload. Country stores 0/1
while displaying Export. Main and Slave each commit and freshly reload the
color mapping **0 Silver Ride / 1 Red Ride / 2 Black Ride** in all three copies
at offsets 0x008, 0x108 and 0x208. No native factory color default is inferred.

On 2026-10-09 the user accepted reasonably established color mapping as sufficient
to move forward. Further conditional ID availability/attribution logic is
**deferred and does not block field mapping**. Calibration remains listed only.
Native block recovery and three independent complete initial images are now
verified in 11 RetroArch trials / 33 program records. Settings use three
28-byte copies; bookkeeping uses three 52-byte copies. Native recovery selects
a matching whole-block pair or writes ROM defaults; these groups have no native
checksum. Unrelated bytes and EEPROM are preserved. See
`Docs/POWER_SLED_NVRAM_INTEGRITY_2026-10-09.md`. The approved numeric fields,
Main/Slave Ride ID and independent initial templates are now implemented and
verified in five further RetroArch stages / 15 program records. Country/Relay
semantics and conditional ID assignment remain deferred. Current implementation
and installed-core hashes: `Docs/POWER_SLED_NVRAM_OPTIONS_2026-10-09.md`.

Recipe: `scripts/libretro_nvram_samples.power-sled-linked.toml`.
Generator: `scripts/generate-power-sled-recipe.py` (`--check` verifies it).
Runner: `scripts/test-retroarch-netpacket.py`, without `--sample`.
Acquired evidence: `build-libretro-gpu/validation/power-sled-phase2-20261009/campaign.json`.
Reviewed coverage: `build-libretro-gpu/validation/power-sled-phase2-20261009/coverage.json`.

**Acquisition backend restriction:** all Phase 2 samples come exclusively from
SM2-Emu Libretro in RetroArch, using each program's own SRM. MAME files remain
read-only documentary references. Core code was unchanged during field acquisition. The later Service binding
swap rebuilt and installed the core; the integrity campaign verifies that
artifact. The subsequent option/initial-template package has its own qualified
core, frontend results and matching installed copies, documented separately.

### Ride Initialization Validation

The first initializer assumed that one call from stored Ride 255 selected
Silver. On the Country 0 baseline Main and Slave instead reached Red; the gate
rejected that attempt. A second attempt committed Main Silver first, but the
Slave still reached Red in the same process group. Both attempts retain native
files, screenshots and failed `validation.json`; neither is promoted to a preset.

A cold restart with Main Silver still left the first Slave call at Red; that
attempt is also rejected. The initializer now observes the complete uninitialized
Slave cycle (Red, Black, Silver), commits Silver and verifies its later fresh
reload. These three value-line screenshots and the three native stored copies
pass validation. The setup-only Main stage retains the raw Slave 255 explicitly
as initialization evidence, never a valid preset or native default.

The fixed-color Phase 1 reference seeds initialize both Main and Slave to the
same color. Their captured cycles remain evidence for those joint configurations;
they do not independently prove that Main alone determines the Slave limit.
A subsequent all-Silver fresh restart also keeps Main Silver when called. The
recipe therefore acquires independent unassigned-core initializations for every
color, with captured cycles where successful and independent fresh reload
for every committed color. Further conditional-cycle investigation is deferred.
Repeating the same Red baseline showed Slave cycles of both two and three
colors. Fixed call counts are therefore not a reliable target-core recipe.
`RIDE_CYCLE(1)` / `RIDE_CYCLE(2)` reads the native value-line screenshot after
each call and stops at the starting color, with a strict maximum of three calls.
Every intermediate color and the closing return are recorded and revalidated.
Peers hold their values while a program's cycle is captured. The underlying
limit calculation and the cause of the varying cycle are not inferred.

Relay always shows its role label, while its persisted byte may change after
Select ID. The campaign records that byte separately and checks its exact
preservation on a later fresh reload. The two Relay repeat/reload stages record its observed stored states 0/1; no color selector or byte semantics are
invented for Relay. This remains distinct from the displayed role ID 0x100.

Black initialization is staged: initialize Slave Black from the already proven
Main-Silver/Slave-unassigned core baseline, then restart and commit Main Black.
Both programs' Black native values and fresh reload pass. An attempted extra
Black cycle failed its start-color gate; its evidence is excluded and retained.
The user then deferred further ID-logic analysis, so that extra cycle and the
final experimental return-to-Silver branch are outside the accepted recipe.
The committed/reloaded color mapping is independently established.

### Current Reload Lifecycle

The campaign acquires all three programs in parallel, then starts a fresh linked
ring for the next sample/reload. Main is also the current RetroArch host, so
restarting it ends the frontend session for its clients. Keeping two processes alive while restarting
only one program is not a verified replacement. Source review on 2026-10-09:
`netpacket.cpp::disconnected` clears the ready roster;
`M2Comm::send_frame` can change a live link to state 0x02 when transport readiness
is lost, and `M2Comm::tick` keeps that failure until native board initialization.
The live-link branch also does not repeat the initial ring enumeration. A reliable
persistent-peer procedure therefore needs separate reconnect/board-reset proof.
No core change or unverified reload optimization is used during this campaign.
This is a Power Sled/current transport constraint, not a universal rule requiring
all emulators to close every process for every acquisition.

### Authoritative Phase 1 Inventory

Evidence: `build-libretro-gpu/validation/power-sled-phase1-20261008/service-menu-observations.json`.
Five bounded menu-only runs use MAME interpreters to avoid the known SHARC DRC
abort. The already captured native numeric-range screenshots are reused.
Each program is documented independently; shared field layouts do not imply
shared templates or working Libretro linked gameplay.

| Page | Documented Settings / Commands | Default / Scope |
| --- | --- | --- |
| Test Menu | CRT Test, Scroll Test, Polygon Test, I/O Test, Sound Test, Game Assignments, Volume Setting, Bookkeeping, Backup Data Clear, Exit | Main renders all labels; Slave/Relay initially render only Exit, but Service 2 reaches operator slots 6/7. Diagnostics, counters and destructive actions are listed only. |
| Game Assignments | Country, Ride ID (Color), Time Extension, Motion Angle, Exit | Initial selection Exit; Service B / Select moves, P1 Call confirms. |
| Country | Select Country, Cancel & Exit, Set & Exit | Initial Cancel & Exit. Export remains displayed through selection cycles in all sets; no distinct region label is invented. No Use Default command. |
| Network ID (Ride Color) Setting | Select ID, Cancel & Exit, Set & Exit | Initial Cancel & Exit. Main/Slave color availability is conditional; Relay reports 0x100 in an uncommitted menu cycle. No Use Default command. |
| Time Extension Setting | Checkpoints 0, 1, 2, 3, 4, Exit | Initial Exit; five separate fields. Each 5–99 seconds, step 1; native Use Default results 49/35/35/30/30. |
| Checkpoint Editor | Increase, Decrease, Use Default, Cancel & Exit, Set & Exit | Initial Cancel & Exit. |
| Maximum Rotation Setting | Increase, Decrease, Use Default, Cancel & Exit, Set & Exit | Initial Cancel & Exit. 10.0–45.0 degrees, step 0.5; native Use Default 38.0. Operator limit, included. |
| Volume Setting | P1/P2 Right/Left Forward/Back; Cancel & Exit; Set & Exit | Eight endpoint labels documented independently on all sets. Calibration listed only; no endpoint selected or acquired. |

### Conditional Ride ID Availability

| Initial Main And Slave Choice; Main Held Fixed | Slave Visible Cycle | Relay Visible Cycle |
| --- | --- | --- |
| Silver Ride (0) | Silver Only | Relay Only |
| Red Ride (1) | Silver → Red → Silver | Relay Only |
| Black Ride (2) | Silver → Red → Black → Silver | Relay Only |

Both Main and Slave start with the indicated color; Main remains fixed
throughout each independent test. This establishes the observed Slave cycle
for those joint initial configurations and supersedes the earlier assumption that
Slave was always Silver. Simultaneous changes by peers are unsuitable for
establishing a complete cycle. Main exposes all three colors across documented
conditions; an unassigned-peer baseline with Country state 1 shows only
Silver/Red, while another initialized baseline shows Silver/Red/Black. These
observations do not prove that Country alone causes the difference. Phase 2
must hold peer configuration fixed when acquiring each conditional value.

Country and Ride ID expose no native Use Default action. Fresh 255 / missing
color values are uninitialized data, not native defaults. Relay's 0x100 is a
reported role, not a demonstrated factory preset. The numeric defaults above
come from the native Use Default actions, independently on each set.

Immediate Relay page re-entry after exploratory Set & Exit sometimes displays
color labels instead of Relay, while fresh entry reports Relay. That transient
persistence behavior is retained as a Phase 2 investigation; it is not advertised
as an additional stable Relay selector.

### Phase 2 Requirements From This Inventory

- Acquire all discrete states with native commit/reload, documenting both
  initial peer colors and the tested topology. Keep the earlier fixed-peer
  observations distinct from target-core complete-cycle acquisition.
- Country keeps the same visible label; reconcile all distinct stored states
  without assigning unsupported region names.
- Use significant numeric samples after verifying the encoding pattern,
  including defaults, limits, increments and byte boundaries where applicable.
- List calibration only. Validate integrity and complete per-variant initial
  templates separately before implementing automatic setup or overrides.

The sections below retain the earlier investigation history. Current menu
coverage and phase status are defined by this inventory, YAML and the three
Phase 1 workbook tables, rather than earlier provisional conclusions.

## Historical Discovery Coverage

Power Sled is registered in the existing Model 2 documentation campaign as three independent sets. The catalogue now includes all 87 current sets, with these three explicitly pending operator-setting acquisition. No menu, default, value cycle or complete initial image is inherited between variants without evidence.

| Set | Role / Program | Acquired Evidence | Remaining Acquisition |
| --- | --- | --- | --- |
| `powsled` | Slave | Boot/network check, Test/Service responses and network-cancel probe; `Cannot find network main` observed | Operator pages, every setting/default/value cycle and native commit sequence |
| `powsledm` | Main, patched Relay program | Test Menu with Game Assignments and Volume Setting entries; Entry/Call navigation probes | Reliable page navigation, all setting rows/defaults/value cycles and native commit sequence |
| `powsledr` | Relay | Boot/network check, Test/Service responses and network-cancel probe | Operator pages, every setting/default/value cycle and native commit sequence |

The Main Test Menu displays these entries in order: CRT Test, Scroll Test, Polygon Test, I/O Test, Sound Test, Game Assignments, Volume Setting, Bookkeeping, Backup Data Clear, Exit. Its initial cursor is Exit. Its help says to select with Entry and confirm with Call. This documents visible menu entries, not their operator-setting contents. Unrelated diagnostics and Backup Data Clear are excluded from the acquisition campaign.

Both short (0.1 s) and longer (0.6 s) Entry/Call probes were tried. The expected Game Assignments page was not reliably reached; captures return to boot/error screens. One Main screen requests entering Test Mode and changing Ride ID (color). The later linked MAME reference below reaches that page; allowed colors, native defaults and storage encoding remain unacquired. Do not infer that field's implementation from this message. The probes do not establish whether the cause is navigation semantics, emulation, network prerequisites or input delivery.

## MAME Source Review — 2026-10-08

Reviewed the local MAME checkout at `6c504efbee8342f4cbf813d066176523a720d7d5` (`src/mame/sega/model2.cpp`, `m2comm.cpp` and `m2comm.h`) and cross-checked the relevant definitions against the public MAME master sources on 2026-10-08:

- [Model 2 Driver](https://github.com/mamedev/mame/blob/master/src/mame/sega/model2.cpp): `INPUT_PORTS_START(powsled)`, `model2b_state::powsled`, `ROM_START(powsled*)`, `init_powsledm` and the game registrations.
- [Model 2 Communication Simulation](https://github.com/mamedev/mame/blob/master/src/mame/sega/m2comm.cpp): `cn_w`, `comm_tick` and `read_fg`.

These are source findings, not new runtime captures or an acquired operator-setting inventory. MAME marks all three sets `MACHINE_NOT_WORKING`.

### Programs and Link Roles

| Set | MAME Definition | Consequence for Acquisition |
| --- | --- | --- |
| `powsled` | Slave, Revision A; program EPR-19470A / EPR-19471A | An isolated Slave cannot supply the missing Main program. |
| `powsledr` | Relay, Revision A; program EPR-19472A / EPR-19473A | Test as a separate program; do not equate it with Main. |
| `powsledm` | Main, hack of Relay; original Main is explicitly not dumped | Results describe the patched Relay approximation, not a verified original Main dump. |

MAME's Main initializer changes byte `0x1571c` to `0x01` (Main mode), byte `0x1584c` to `0x89` (commented node ID `0x200`) and byte `0x1585d` to `0xfd` (inverted node ID). The current `games.xml` already carries equivalent word patches. This program node ID must not be confused with the communication simulation's enumerated link ID or an unacquired Ride ID setting.

The generic communication simulation has three roles: Master starts ring enumeration, Slave contributes a node, and Relay forwards traffic without increasing the enumerated count. It selects roles through the flip register and shared RAM byte `0x01`. This supports testing a mixed-program ring, but does not prove Power Sled's minimum unit count, required order or that a Relay can be omitted. No working Power Sled topology is documented by these driver definitions.

The isolated Slave's `Cannot find network main` and Main's `RELAY: NG` are consistent with missing units. The network prerequisite is therefore the first runtime hypothesis to test. Neither the messages nor the generic ring code establish the cause of SYSTEM SHUTDOWN.

### Communication Details and Open Issues

- Power Sled uses receive offset `0x180`; the usual Model 2 value is `0x1c0`. `Model2B` already selects `0x180` for this family.
- MAME initializes frame size to `0x0e00`, while a source TODO questions whether Power Sled should instead use `0x0c00`. This is an unresolved hypothesis, not a correction to import blindly. The current core also initializes `0x0e00`; compare actual shared RAM and transfers before changing it.
- MAME connects each instance's local receive socket to another instance through its remote endpoint, permitting a closed ring of different programs. Its communication implementation is a simulation, not complete Z80/HDLC board emulation.
- The core's default loopback supplies no missing Main/Relay program. The initial adapter lacked Power Sled eligibility and a common program family. The integration below adds both and verifies mixed content through RetroArch, separately from the emulated board link.
- `automatic_network.cpp` has no Power Sled field mapping. Do not assign existing games' role presets, cabinet limits or NVRAM offsets to it.

### Input and Sound Findings

MAME defines active-low P1 Entry/Call on `IN1` bits `0x01`/`0x02`, P2 Entry/Call on `0x04`/`0x08`, Cancel Error on `IN0:0x80`, and Cancel Network Check on `IN3:0x02`. These dedicated digital actions are already mapped in the core. Cancel Network Check is an operator action; its existence does not prove an offline gameplay mode.

An additional `IPT_SERVICE2` is defined on `IN0:0x40`. The Power Sled adapter now binds that extra service input to D-Pad Down as **Service B / Select**; L3 and R3 retain the common service/test bits. The linked MAME probe described below confirms that it advances the Test Menu cursor; the core binding and its frontend navigation are verified below. This supplies the missing acquisition control without changing Entry/Call wiring.

MAME connects P1 right/left analog inputs to channels 1/3 and P2 right/left to 5/7; channels 0/2 are commented as Motion AD. The current core maps only P1 analog inputs. Complete two-rider input and motion requirements remain unverified.

Slave uses sound program EPR-19466 and sample FPR-19459. Relay/Main use EPR-19467 and FPR-19460/FPR-19461. The different sound content is intentional in MAME and already represented in the core database; silence in one isolated unit is not enough to establish correct or broken overall system audio.

### Revised Acquisition Order

1. Establish a matching MAME reference with isolated per-instance NVRAM and endpoints. Compare Main/Slave and Main/Relay/Slave closed rings, recording startup order, configured unit IDs, shared RAM/frame sizes, native errors and service input responses. Treat these as experimental topologies, not documented valid configurations. Determine whether more Slaves are required rather than assuming three instances suffice.
2. Check the extra Service 2 input and establish reliable operator-page navigation. Preserve the original network errors and distinguish a cancelled check from a successful link.
3. Define the core's mixed-program family/transport support from the observed reference, including frontend compatibility and role/count rules. Follow the already established mixed-family approach used for Virtua On where applicable; do not infer identical topology rules.
4. Resume independent per-set menu/default/value-cycle and committed NVRAM acquisition. Only then derive Power Sled NVRAM Settings and automatic policies.

No emulation, network, input or NVRAM behavior is changed by this review. The source-review step alone did not test linked operation; the later MAME reference results below establish link checks and menu responses, with gameplay still unverified.

## Isolated MAME Reference Runner

Use `scripts/test-mame-power-sled.py` with an existing MAME binary and the same verified Model 2 ROM collection. No package installation or MAME source change is needed. The runner accepts `--sets` in ring order, including repeated Slave units, and reserves distinct localhost TCP ports. Each unit receives a fresh configuration/NVRAM/state directory; MAME configuration files and plugins are disabled. Existing user saves and application instances are not used.

```sh
python3 scripts/test-mame-power-sled.py \
  --mame /path/to/mame \
  --rom-dir /path/to/Model2/roms \
  --output /path/to/new/evidence-directory \
  --sets powsledm powsledr powsled \
  --seconds 60 --wall-timeout 150 --mode service
```

`--mode boot` only observes startup. `--mode assignments` advances six times with Service 2 to Game Assignments, confirms with P1 Call, then probes common Test and Start on the resulting page. `--mode ride-id` opens Game Assignments, advances twice with Service 2 and confirms with P1 Call to inspect Ride ID without choosing a value. `--mode service` presses common Test (`IN0:0x04`) at 25 emulated seconds, extra Service 2 (`IN0:0x40`) at 34, P1 Entry at 43 and P1 Call at 50, each for 0.6 seconds, on every unit. These are diagnostic probes, not a verified page-navigation recipe. Use a new output directory for each run; `--dry-run` prints the commands without starting MAME. In this sandbox, even the dry run needs local socket access for port reservation.

MAME runs headless with sound disabled, throttle enabled and communication frame sync disabled. Native screen PNGs and shared RAM bytes `0x00..0x1f` are captured; the final runner does not read the side-effecting communication registers. Logs, generated Lua, exact commands, owned PIDs, exit results, binary version/hash and saved NVRAM are indexed by a SHA256 manifest. The runner bounds wall time, terminates only its own process groups and waits for exit. Child processes retain Python's ignored SIGPIPE so a closing peer reports a socket failure rather than terminating a remaining instance by signal.

This establishes software-level link and service-screen evidence. It does not establish playable controls, audible sound, motion hardware, native NVRAM checksums or a complete operator-setting inventory. Successful generic ring enumeration is distinct from the game's Main/Relay checks and Ride ID validity.

## Linked MAME Reference Results — 2026-10-08

Reference binary: MAME v0.289 (`mame0289-1171-g6c504efbee8`). All three archives in the dedicated Model 2 collection pass MAME `-verifyroms`. Evidence is retained under `build-libretro-gpu/validation/mame-power-sled-20261008/`; each run has independent per-unit directories and a manifest.

| Probe | Result | Limit |
| --- | --- | --- |
| `main-slave-clean`, 30 emulated seconds, two units | Both enumerate a two-node ring; Main screen shows `MAIN: OK`, `RELAY: NG` and asks to change Ride ID | A working generic ring does not satisfy the game's Relay check. |
| `main-relay-slave-service`, 60 emulated seconds, three units | All enumerate a three-node ring; Main shows `MAIN: OK`, `RELAY: OK`; Test input opens Test Menu | Ride ID remains invalid; no gameplay is established. |
| Same three-unit run, extra Service 2 | Main Test Menu cursor moves from Exit (`screen-32.png`) to CRT Test (`screen-40.png`) after the isolated `IN0:0x40` pulse | Confirms a navigation action absent from the current core's dedicated bindings; the following targeted probe establishes P1 Call confirmation. |
| Same run, P1 Entry | Main returns to the boot/error Ride ID screen (`screen-48.png`) | The displayed Entry/Call instruction is insufficient to assume that current P1 Entry/Call wiring supplies the required operator navigation. |

The two comparison runs and both later targeted menu probes exit with code 0 on every unit. Their recorded shared RAM reaches link-alive status; the three-unit run uses enumerated link IDs 1/3 (Main), 3/3 (Relay program) and 2/3 (Slave). In this run shared role byte `0x01` is `0x02` on all units: the Relay *program* is not automatically the generic communication simulation's non-counted Relay role. Do not infer cabinet-count rules from the ROM-set name alone.

The first exploratory three-unit run (`main-relay-slave-boot-v2`) already showed the Main/Relay checks pass but ended with SIGPIPE on Main when another unthrottled instance exited first. It is retained as exploratory evidence, not a clean pass. An earlier command-syntax attempt (`main-relay-slave-boot`) exited before emulation. The completed service run uses throttle and avoids reads of the side-effecting communication registers; `main-slave-clean` repeats the two-unit comparison with the same non-intrusive RAM probe.

The targeted `main-relay-slave-assignments` run uses six Service 2 pulses from Exit to Game Assignments, then P1 Call. All three units show the Game Assignments page (`screen-45.png`) with Country, Ride ID (Color), Time Extension, Motion Angle and Exit. This verifies **Service 2 selection + P1 Call confirmation** for that transition on all three sets. It is page-access evidence, not default/value-cycle or committed-field evidence. The subsequent common Test pulse returns to Test Menu. P1 Entry is not used for selection in this verified sequence.

The `main-relay-slave-ride-id` probe confirms the next transition independently on all three sets: from Game Assignments/Exit, two Service 2 pulses select Ride ID and P1 Call opens **Network ID (Ride Color) Setting**. The page contains Select ID, Cancel & Exit (initial cursor), and Set & Exit. At 51 seconds, fresh isolated NVRAM shows `ID 255 ()` on Main and Slave, while Relay shows `ID 0x100 (RELAY)`. These are observed startup values, not validated native defaults or a complete allowed-value list. No ID value is changed or committed in this probe. Main's displayed 255 also reinforces that the patched program node ID `0x200` must not be substituted for the operator setting without runtime evidence.

All three units reach 60 emulated seconds, save their isolated NVRAM and exit with code 0. The runner's telemetry/screenshot gates pass. That acquisition is completed in the Ride ID section below; cold-start/gameplay limits remain explicit. The core-side Service 2 binding is verified in the section below.

**Conclusion:** including the Relay program changes the game's Relay check from NG to OK in the tested fresh-NVRAM topology. This is evidence of a real missing-unit prerequisite in the isolated tests. It does not establish the minimum topology for gameplay, valid Ride IDs or that link configuration alone resolves SYSTEM SHUTDOWN. The following Ride ID acquisition establishes menu access and native persistence; complete setting coverage and gameplay remain pending.

## Ride ID Cycle and Native Commit — 2026-10-08

The following observations apply to the tested `powsledm → powsledr → powsled` ring and fresh per-unit NVRAM. They do not establish native defaults, conditional availability in other topologies or a complete initial template.

| Set | Observed Select ID Behavior | Committed Value | Fresh-Process Menu Reload |
| --- | --- | --- | --- |
| `powsledm` | Selecting Select ID normalizes 255 to 0; P1 Call cycles **0 Silver Ride → 1 Red Ride → 2 Black Ride → 0 Silver Ride**, with repeated closing cycles captured | 1 Red Ride | 1 Red Ride |
| `powsled` | Selecting Select ID normalizes 255 to 0 Silver Ride; 17 P1 Call pulses leave it at 0 in this topology | 0 Silver Ride | 0 Silver Ride |
| `powsledr` | Remains 0x100 Relay through selection and 17 P1 Call pulses | 0x100 Relay retained | 0x100 Relay |

The cycle evidence is `ride-id-cycle`: Main's first reachable value is captured at 56 seconds, followed by Red at 58, Black at 60 and the return to Silver at 62. All three variants are captured independently. Merely cycling values and exiting MAME leaves the native EEPROM and Backup RAM files identical to the earlier menu-only baseline; menu display changes alone do not establish persistence.

### Commit Boundary and Parent Menus

From Select ID, advance twice with Service 2 to **Set & Exit**, then confirm with **P1 Call**. This returns to Game Assignments with **Ride ID still selected**, not Exit. `ride-id-commit` deliberately retains this intermediate menu state. The saved Backup RAM differs from the uncommitted baseline, while EEPROM is unchanged. A new three-instance run, `ride-id-reload-menu`, copies only these isolated native NVRAM files and enters Test at 10 seconds; all three Network ID pages show the committed values above at 31 seconds. This proves that **Set & Exit is sufficient for Ride ID persistence**; the upper-menu exits are not required to commit this field.

The complete native return sequence is separately captured in `ride-id-full-exit`: after Set & Exit, advance three times to Game Assignments/Exit and confirm. Test Menu retains Game Assignments selected; advance four times to Test Menu/Exit and confirm. The test traverses other entries without opening them. It reaches startup screens with Red/Silver identification and records 100 emulated seconds with clean exits. These screen labels do not substitute for a working game or prove the purpose of every unit.

The observed Backup RAM changes are not yet a verified general storage encoding or checksum. No byte patch, template, Core Option or automatic policy is produced from these samples. All other operator fields remain pending. The reviewed workbook records this bounded Ride ID acquisition on the existing Power Sled Campaign sheet; its NVRAM Mapping and Automatic Setup statuses remain Pending.

### Cold Boot and MAME CPU Limitation

A cold normal-DRC run from the Set & Exit saves (`ride-id-reload-after-set`) advances to about 14 seconds, then **all three processes abort** on:

```text
:copro_adsp: PC=000203AC: Unimplemented compute 6ABE020E0645:
F6 = F4 COPYSIGN F5, DM(0x00, I5) = R4
```

The existing MAME source implements `compute_fcopysign` in `src/devices/cpu/sharc/compute.hxx` and dispatches it in `sharcops.hxx`; `sharcdrc.cpp` routes operation 0xe0 to `generate_unimplemented_compute`. This identifies a concrete DRC limitation in the reference binary. MAME itself is unchanged.

`ride-id-reload-interpreter` uses the existing **`-nodrc`** option and copies the full-exit native saves. All three units complete 30 emulated seconds with clean exits and no COPYSIGN exception. At 24 seconds their native screenshots are black. This bypasses the observed DRC failure but does **not** establish attract mode or gameplay; the cause of the black screen remains unverified. A game-capable linked reference is still pending.

### Runner Extensions and Evidence

- `--mode ride-id-cycle` captures the per-set cycle; use `--seconds 95`.
- `--plan plan.json` accepts exactly one numbered entry per requested unit, each with `actions` (`[emulated_seconds, port_tag, bit_mask]`) and sorted `shots`. The effective plan is retained in the run manifest. Actions use the verified digital inputs and 0.6-second holds.
- `--seed-from prior-evidence-root` copies only the matching numbered unit's native NVRAM into a fresh run directory and records input hashes. It never uses or modifies user saves or the source samples.
- `--no-drc` adds MAME `-nodrc`; it changes this test invocation only.
- `ride-id-observations.json` records screenshot-backed values and the commit/reload outcome. `ride-id-acquisition-manifest.json` indexes this acquisition's completed and failed runs. Failed boot evidence remains distinct from completed menu/persistence checks.

The next NVRAM acquisition tasks are the remaining operator fields, conditional behavior, committed value samples, native integrity checks and independent per-variant templates. The MAME black-screen/reference-gameplay limitation remains a separate investigation.

## Existing Workflow Integration

- Recipes: `scripts/libretro_nvram_samples.powsled.toml`, `.powsledm.toml`, `.powsledr.toml`.
- Per-set catalogues: `data/diagnostic-menus/powsled.yaml`, `powsledm.yaml`, `powsledr.yaml`.
- Screenshot-derived reference: `GAME_SETTINGS_CATALOG.md`, generated by `scripts/generate-game-settings-catalog.rb`.
- Review workbook: `Docs/revisione_core_options_model2.xlsx`, **Power Sled Campaign** sheet. Existing reviewed option rows, decisions, formatting and native table remain intact.
- Evidence: `build-libretro-gpu/validation/power-sled-service-menu-20261008/<set>/`, including screenshots, isolated saves, retained work directories and logs. The common `manifest.json` indexes every file with its SHA256 and each sample's actual loaded set. ROMs and generated evidence remain outside Git.

Use the established runner:

```sh
export SM2_ROM_DIR='/path/to/Model 2/roms'
python3 scripts/libretro_nvram_samples.py scripts/libretro_nvram_samples.powsledm.toml --dry-run
python3 scripts/libretro_nvram_samples.py scripts/libretro_nvram_samples.powsledm.toml --sample service-discovery --keep-workdirs
```

All acquisition recipes explicitly disable Automatic Initial NVRAM Setup and NVRAM Settings and select Software rendering. Each sample uses an isolated fresh save directory. Entry/Call bindings identify cabinet wiring; their success as menu navigation remains pending. Probe names such as `game-assignments` identify the intended capture and must not be interpreted as a verified page or value. Calibration probes were removed from active recipes; any earlier calibration captures are historical only. `summary.json` is a per-invocation runner report; the campaign-wide manifest retains evidence from all invocations.

## Gates for NVRAM Features

1. Resolve the network and extra-service-input prerequisites in the revised acquisition order above, then stabilize operator-menu access independently for each set. Capture every relevant page, conditional row, native default and complete reachable value cycle, including the closing return to its initial value and any network/role settings.
2. Transcribe observed rows into the YAML and workbook before generating single-setting variation recipes. Keep native observations, review decisions and implemented options distinct.
3. Identify the native save/exit sequence, then acquire first/later boot and single-setting committed samples. Verify each value after a fresh-core import. A menu-open Save RAM difference is not proof of persistence.
4. Determine storage offsets, byte/word order, dependent effects and native integrity checks from independently committed samples. The frontend SM2SRAM header is not the game's checksum. Treat calibration separately.
5. Review fields for per-game NVRAM Settings. Validate complete templates per variant for Automatic Initial NVRAM Setup and approved safe overrides for Automatic NVRAM Settings. Reuse a parent image only after a clone-specific compatibility check. Approved automatic overrides must also define the corresponding manual selector defaults.
6. Verify preservation of existing valid user saves and unrelated bytes, then direct ABI and real RetroArch behavior. Linked-cabinet operation is a separate gate. Do not assume that NVRAM changes resolve SYSTEM SHUTDOWN.

At this stage only the documentation campaign is integrated. No Power Sled NVRAM selector, automatic override, initial template, native checksum or committed value preset is claimed implemented or validated.

## Verification

`ruby scripts/audit-diagnostic-yaml-catalog.rb` checks all 56 YAML documents against the generated catalogue. `python3 scripts/audit-nvram-core-catalog.py` checks the 87-set roster, existing option decisions and the three pending Power Sled campaign records, recipes, workbook rows and screenshot manifest. Each recipe also passes the runner's dry-run validation. Actual captures verify navigation evidence and isolated SM2SRAM containers, not game integrity or committed option values.

Core used: SHA256 `d37c1deef7ec2e7d8f0e96b52d4d839eee3cc27957c48b6fffe5ddf900485dd1`, Save State format 8. The core and both installed copies are unchanged by this documentation task. No TGPulse edits, commit or push.

## Libretro Service 2 Binding — 2026-10-08

D-Pad Down now exposes **Service B / Select**, driving only `IN0:0x40`
(active low). It follows the existing Test/Service eligibility on both ports;
the reduced controller variant neither advertises nor drives this line.
Coin, Start, Service A, Test A, Entry/Call, cancel buttons and handlebar wiring
are unchanged. The ROM-free input suite checks the bit, port-2 alias, reduced
profile, existing digital controls and analog channels for all three sets.

The per-set `service2-binding` recipe enters Test with R3, advances six times
with Down to Game Assignments, confirms with A, advances twice to Ride ID and
confirms with A. It never selects or commits a Ride ID. These are navigation
captures, separate from the linked MAME committed-value campaign above.
Evidence is retained in
`build-libretro-gpu/validation/power-sled-service2-20261008/`.

Both installed macOS cores (`sm2_libretro.dylib`, `sm2_dev_libretro.dylib`)
and the authoritative external `system/sm2-emu/games.xml` were atomically
replaced with backups and verified against the build/source SHA-256.
Core SHA-256: `68b144a681cd1f4377165a66d40a63fe11fb66408138dead24d787bc668b8b6f`.

This adds no NVRAM settings, presets or automatic policy. Remaining acquisition
covers all other operator settings, complete value cycles, native defaults,
committed samples, storage/checksum validation and per-variant templates.
Linked operation and gameplay remain separate pending gates.

### Frontend Result and Network Prerequisite

The Main (`powsledm`) screenshots verify Test Menu selection, Game Assignments
and Network ID (Ride Color) Setting, initially ID 255 with Cancel & Exit
selected. Slave and Relay complete the scripted process/save capture but the
initial 12-second recipe remains in network startup, so those runs do **not**
verify operator navigation. A second isolated recipe waits another 18 seconds
and presses Cancel Network Check before Test; Slave and Relay still show **Cannot find
network main**, not the requested page. The extra-service input is verified
for every set by the ROM-free hardware-bit tests; actual menu navigation for
Slave/Relay remains gated by their network/error state. A successful runner
exit is not treated as a successful menu-navigation result.

`manifest.json` records hashes for all five isolated runs, their screenshots,
logs, saves and retained work directories, plus the distinct navigation results.
Both catalogue audits and `git diff --check` pass after this update.

## Main Operator Inventory — 2026-10-08

Six fresh, isolated RetroArch runs record the remaining `powsledm` operator
pages, the checkpoint-0 editor and a handlebar acquisition probe. Seven
screenshots, logs, Save RAM containers and work directories are retained in
`build-libretro-gpu/validation/power-sled-main-operator-20261008/`.
`observations.json` transcribes the screens; `manifest.json` hashes 90 evidence
files. The source/built core is unchanged by this acquisition.

| Page | Setting Rows | Fresh Observed Values | Navigation / Actions |
| --- | --- | --- | --- |
| Country | Country | Export | Select Country, Cancel & Exit, Set & Exit; initial selection Cancel & Exit |
| Time Extension Setting | Checkpoint 0, 1, 2, 3, 4 | 65535 seconds on every checkpoint | Initial Exit; checkpoint 0 opens an editor with Increase, Decrease, Use Default, Cancel & Exit, Set & Exit |
| Maximum Rotation Setting | Motion Angle | 6553.5 degrees | Increase, Decrease, Use Default, Cancel & Exit, Set & Exit; initial selection Cancel & Exit |
| Volume Setting | P1 Right Forward/Back, P1 Left Forward/Back, P2 Right Forward/Back, P2 Left Forward/Back | Every endpoint FF (hex) | Initial Cancel & Exit; Set & Exit; selecting an endpoint displays the physical lever acquisition instruction |

These are **15 additional setting/calibration rows**, besides the previously
recorded Ride ID. Game Assignments order is Country, Ride ID (Color), Time
Extension, Motion Angle, Exit. Volume Setting is the separate next Test Menu
entry. The scripts visit these pages through the verified Service B / Select
and P1 Call route; unrelated diagnostics and destructive actions are excluded.

### Volume Setting Is Handlebar Calibration

This page is not an audio-volume selector. Its first selected field displays
`FRONT SEAT: SLIDE RIGHT LEVER FORWARD AND PRESS CALL BUTTON`.
Pressing P1 Call with the input resting at zero changes P1 Right Forward
from FF to 0, while the other seven endpoints remain FF. The initial live
readings are 0 for both P1 handlebars and FF for both P2 handlebars, with
Range 0 displayed for all four. This is a bounded input-acquisition probe,
not a valid calibration or persisted preset: no Set & Exit or fresh reload
was performed. P2 analog controls remain unimplemented in the adapter.

### Acquisition Gates

The large fresh time/angle values and FF endpoints are consistent with
uninitialized fields, but this is an inference, not a validated native default
or integrity diagnosis. Do not promote them to presets. Country's fresh Export
label likewise does not establish its full cycle or default. The native
Use Default actions have only been observed, not exercised yet.

Next acquire Country's closed value cycle and each numeric editor's Use Default
result and reachable range. Then establish native Set & Exit/fresh reload and
single-field committed samples. Calibration menus are listed only and excluded from acquisition, endpoint presets and campaign completion gates. The later numeric campaign below supersedes the numeric acquisition gates in this historical inventory; linked gameplay remains independent.

The Main YAML records this under `main_operator_inventory`, keeping `menus: {}`
and acquisition status pending until the catalogue is complete. The workbook
adds the native filtered green `PowerSledMainInventory` table on the existing
Power Sled Campaign sheet. Earlier rows, all three prior tables, the core-options
sheet and unrelated OOXML parts are preserved. The exported changed range was
reimported and rendered identically to the inspected authoring preview.
Both catalogue audits now reconcile this inventory with the workbook and
retained evidence. No NVRAM Core Option, automatic policy, core rebuild,
installed-core replacement, commit or push is required by this documentation step.


## Reduced Numeric Storage Campaign — 2026-10-08

Evidence: `build-libretro-gpu/validation/power-sled-settings-20261008`.
The executable analysis is `scripts/analyze-power-sled-campaign.py`; its
`operator-settings-observations.json` reconciles screenshots, native Backup RAM,
independent commits and fresh-process reloads. All results below were checked
independently on Main (`powsledm`), Relay (`powsledr`) and Slave (`powsled`) in
the linked MAME reference. This is not Libretro linked-gameplay verification.

| Setting | Allowed Values | Native Use Default | Base Offset | Encoding |
| --- | --- | --- | --- | --- |
| Checkpoint 0 | 5–99 Seconds, Step 1 | 49 | `0x000A` | Unsigned 16-Bit Little Endian Seconds |
| Checkpoint 1 | 5–99 Seconds, Step 1 | 35 | `0x000C` | Unsigned 16-Bit Little Endian Seconds |
| Checkpoint 2 | 5–99 Seconds, Step 1 | 35 | `0x000E` | Unsigned 16-Bit Little Endian Seconds |
| Checkpoint 3 | 5–99 Seconds, Step 1 | 30 | `0x0010` | Unsigned 16-Bit Little Endian Seconds |
| Checkpoint 4 | 5–99 Seconds, Step 1 | 30 | `0x0012` | Unsigned 16-Bit Little Endian Seconds |
| Motion Angle | 10.0–45.0 Degrees, Step 0.5 | 38.0 | `0x001A` | Unsigned 16-Bit Little Endian Tenths Of A Degree |

Each word has three copies at base, base + `0x100`, and base + `0x200`.
The native `backup1` image is 16,384 bytes. An angle of 38.0 is stored as
380 (`7C 01`), 38.5 as 385 (`81 01`). Native EEPROM stayed all-FF (128 bytes)
in these tests; no settings encoding is inferred for that separate device.

### Sample Reduction And Persistence

Reduction applies only to numeric fields with a demonstrated encoding pattern.
Small discrete selectors such as Country and Ride ID require every selectable
value and a complete native cycle. Repeated identical Country labels do not
prove that its storage encoding or selectable cycle is understood; that gate
remains open. The reduced numeric evidence does not close discrete-selector
acquisition gates.

Visible numeric ranges and native Use Default actions were acquired on all
three sets. The first completed exhaustive commit run already covered
Checkpoint 0 values 5–99. After the user authorized reduced sampling, the
Checkpoint 1/2 exhaustive runs were intentionally stopped and marked partial;
Checkpoint 3/4 exhaustive commit runs were not started. These partial runs are
excluded from passing assertions.

Instead, a native-committed default baseline was followed by one independent
increment per numeric field: 50, 36, 36, 31, 31 seconds and 38.5 degrees.
Every commit changes only its field's three copies relative to the preceding
same-process sample. An uncommitted Motion Angle edit leaves Backup RAM
unchanged; Set & Exit applies it. Raw final dumps match native NVRAM files.
New MAME processes reload all six edited values on each of the three sets.
Separate cold-boot bookkeeping changes outside these fields are not attributed
to a setting or checksum.

### Redundancy And Remaining Integrity Limits

Two isolated Checkpoint 0 disagreement probes started from saved value 50.
Changing only the first copy to 80 reloads 50 and repairs all copies to 50.
Changing the first two copies to 80 reloads 80 and repairs all copies to 80.
All three programs show these results, supporting majority recovery for this
field. This does not establish the complete native integrity algorithm,
three-way disagreement behavior or whole-image template compatibility.

### Country And Calibration Scope

Country displays Export throughout eight selection calls on each program and
after native commit/reload. Native images contain both 0 and 1 at the apparent
Country byte while the page still displays Export. Its general encoding and
whether other regions can be selected remain unresolved; no region selector
or default is invented from that observation.

Volume Setting is listed as handlebar calibration only. Its eight historical
endpoint rows are explicitly Excluded Calibration / Not Applicable in the
workbook; endpoint capture, full travel and calibration presets are outside
this campaign. Motion Angle remains an operator limit and is included.

The workbook adds the filtered green `PowerSledOperatorSettings` table with
21 per-set rows. Numeric acquisition and representative persistence are
complete. Remaining gates are Country encoding, general native integrity,
Slave/Relay core import verification, complete initial-image compatibility, Core Option
review and automatic policy. No new selector, automatic NVRAM behavior or
core binary change is introduced by this documentation campaign.


### Main Core Import Cross-Check

A fresh isolated RetroArch process imported the Main native `.nv` and
`.eeprom` files. The core's Time Extension page shows 50/36/36/31/31 seconds
and its Motion Angle page shows 38.5 degrees, matching MAME. Both screenshots
were visually reviewed, and the exported 16,384-byte native save preserves
all numeric words and copies. The acquisition report is
`core-native-import/summary.json` under the evidence root. Slave/Relay core
menu import remains unverified because of the existing network-startup gate.
The built core and both installed macOS copies retain their previous SHA256;
this campaign changes documentation and runners only.


## Target Core Communication Integration — 2026-10-08

The Libretro adapter now exposes **Linked Cabinets: Disabled / 3 Cabinets** for
`powsledm`, `powsledr` and `powsled`. Each program uses family `powsled`; a
Power Sled-only HELLO payload identifies its ROM program (Main / Relay / Slave).
A complete roster requires one of each. These program tags are not emulated
communication-board roles or NVRAM Ride IDs. No automatic NVRAM policy is added.

The existing MAME-derived `M2Comm` simulation is reused unchanged. The receive
offset stays `0x180` and initial frame size stays `0x0e00`, matching the inspected
MAME revision `6c504efbee8342f4cbf813d066176523a720d7d5`. No CPU, machine timing,
I/O wiring or communication-board firmware implementation is changed here.

Evidence directories under `build-libretro-gpu/validation/`:

- `power-sled-netpacket-20261008-boot`: mixed-content roster on all three units;
  Main screenshot shows `BACKUP RAM: OK`, `MAIN: OK`, `RELAY: OK` and asks for a
  Ride ID because operator settings are still uninitialized.
- `power-sled-netpacket-20261008-service`: native board alive on all three units,
  with enumerated IDs Main `1/3`, Relay program `3/3`, Slave `2/3`, matching the
  earlier MAME reference. Root Test Menu and Game Assignments screenshots are
  retained for each unit. All three roots visibly render the full menu in this
  fresh-core run, differing from the earlier initialized MAME Slave/Relay root
  presentation. Earlier MAME observations remain historical and must not be
  generalized to the target core.
- `power-sled-netpacket-20261008-final`: repeat with the final core and runner;
  success additionally requires each expected native board ID/count in the log.
  **Review correction:** the earlier Exit-only report was an incorrect visual
  interpretation. Re-reading the original PNGs shows all three root images
  have SHA-256 `d452fe587c65f5db9980e03bce46f3613ba95dba0fdba019e615b4517535354f`
  and all three Game Assignments images have SHA-256
  `5c85381346018bf24daeacbe4c353cc3e7cb47d74136131a8066f83f5bf02a97`,
  identical to the preceding service run. The original files contain the full
  white text. The inaccurate review is retained as superseded in the evidence
  JSON, rather than attributed to core behavior.
- `power-sled-menu-diagnosis-20261008`: twelve unchanged root captures and twelve
  unchanged Game Assignments captures per program. Repeated screenshots include
  RetroArch's screenshot-saved notification, so whole-image hashes vary; this
  overlay is visible in the PNGs and does not establish missing menu text. The
  isolated runner now disables screenshot notifications, widgets and font OSD.
  No emulation or video-source fix is justified by these observations.

RetroArch warns about differing content but accepts the three programs through
Netpacket. Core-side family and program-tag validation remain authoritative.
All test state is isolated; the runner closes only its own processes. Menu
navigation uses R3 (Test), six Down presses (Service B / Select), then A (Call)
to reach Game Assignments. No setting is modified, no Set & Exit is executed,
and no NVRAM sample is accepted into Phase 2.

ROM-free checks cover both the observed three-counted-node Power Sled ring and
the generic non-counted Relay variant, offset `0x180` payload delivery, required
program identities, duplicate Main rejection, and existing 2–9-node transport
checks. The generic Relay variant is a protocol test, not a claim about Power
Sled's observed program behavior.

The communication/menu prerequisite is satisfied for this local three-program
ring. Gameplay, initialized Ride ID scenarios, larger topologies and remote
host interoperability remain unverified. Main remains the known patched Relay
approximation; the original Main program is not dumped. Phase 2 must now obtain
its own core-native samples and commit/reload evidence exclusively in RetroArch,
with full menu screenshots and independent native commit/reload review.


## Phase 2 First Core-Native Batch — 2026-10-08

Recipe: `scripts/libretro_nvram_samples.power-sled-linked.toml`.
Runner: `scripts/test-retroarch-netpacket.py`, reusing the acquisition utility's
TOML action expansion, button protocol, screenshot helper and save discovery.
Only SM2-Emu Libretro loaded by RetroArch is supported by this linked workflow.

The three runs under `build-libretro-gpu/validation/power-sled-phase2-20261008/`
are `motion-native-default`, `motion-plus-step` and `motion-reload`. The first
commits native Use Default through Set & Exit. The second starts new processes,
imports each program's own SRM, confirms 38.0 on screen, increments to 38.5 and
commits. The third starts another fresh ring and confirms 38.5 without editing.
Each run retains its expanded sequence, core/recipe hashes, input-baseline path,
logs, screenshots, frontend SRM and extracted native NV/EEPROM. All nine
processes exit 0 without forced termination or residual processes.

The native Motion Angle word at `0x1a`, `0x11a`, `0x21a` is 380 after Use Default
and 385 after the increment and fresh reload on each program. This establishes
three concordant little-endian u16 copies in tenths of a degree for these two
values in target-core samples. It does not certify the entire numeric range,
all integrity behavior or initial-template eligibility.

Separate-process Backup RAM comparisons also change bytes at `0x330/0x430/0x530`
and, for Main/Slave, `0x332/0x432/0x532`. These are not assigned to Motion Angle,
its checksum or a definite counter meaning by this experiment. Preserve them
as unrelated/unresolved effects while acquiring additional same-baseline values.

`scripts/analyze-power-sled-core-motion.py` verifies nine stage/program records,
three native word copies, actual board links and clean shutdown. It compares
the visible digit region with the visually reviewed 38.0/38.5 screenshots,
including the default reloaded before the increment. Evidence summary:
`motion-summary.json` under the Phase 2 root. This is independent of the earlier
MAME sample analysis and does not consume MAME saves.

The review workbook adds `PowerSledCoreMotion`, a filtered green native table.
Main Core Options review and existing historical tables are preserved. No Core
Option, initial template or automatic NVRAM policy is implemented by this batch.

Next: remaining numeric representatives and every reachable small discrete
selector on each variant, with native commit/reload. Calibration remains listed
only. Reconcile native integrity and complete initial-image eligibility before
implementing NVRAM Settings or automatic policies.
