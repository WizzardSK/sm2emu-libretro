# Power Sled Four Colors And Optional Master Archive

## Scope

The user's approved changes cover Yellow in the Service Menu and NVRAM Settings,
ANS `4` for Main/Slave, and an optional Master archive. The subsequent instruction
extends the same manual four-color selector to Relay even though Relay is not a
rider. Roles remain selected by the ROM program. Green placeholder entries are
not exposed. Factory Master firmware remains undumped; these patches extend the
existing Relay-derived reconstruction.

## Native Service Menu Patches

The original Relay program contains `YELLOW RIDE` at entry 3 in the table at
`0x1da94`, with 132-byte entries. Slave's corresponding code/table is displaced
by 16 bytes. Originally the selector reads detected rider count from RAM
`0x52949e`, so its cycle can depend on the running topology.

| Program | Patch Site | Purpose |
| --- | --- | --- |
| Main And Relay | `0x20634` / `0x20638` | Replace Count Load With `lda 4,g5` |
| Slave | `0x20624` / `0x20628` | Same Four-Value Limit |
| Main | `0x20480`, Helper `0x1f0500` | Preserve Master Role `0x0200` On Color Commit |
| Relay | `0x20480`, Helper `0x1f0500` | Preserve Relay Role `0x0100` On Color Commit |
| Relay | `0x205b8` | Display Stored Ride Color Instead Of Fixed Relay Value Line |

The commit helpers retain the native NVRAM write path and restore only the
program role at RAM `0x5293f0`. Their scratch register is overwritten by the next
original load. Main/Relay role captions elsewhere remain independent of color.
The original role store occupies eight bytes. A four-byte call therefore needs
an explicit branch at `0x20484` to skip the replaced address literal on return.
The first acquisition attempt exposed this omission: values were written, then
the CPU raised an unhandled instruction and requested frontend SHUTDOWN. Those
records are retained as superseded and excluded; the resumed campaign validates
clean native return as well as storage/reload and rejects any SHUTDOWN/fault.
Slave retains its native rider identity. No input binding, calibration or
communication-board implementation changes are needed for these menu patches.

## Phase 1 Before Phase 2

Phase 1 independently captures all four value lines and a closing cycle on each
program in SM2-Emu Libretro/RetroArch. Main/Relay show `0→1→2→3→0`; Slave's
initialized Red seed shows `1→2→3→0→1`. Native labels are Silver / Red / Black /
Yellow. Country and Ride have no Use Default command. The three YAML inventories
retain their historical base inventory and append the independently qualified
`ride_color_extension` record. Calibration remains listed only.

Phase 1 evidence:
`build-libretro-gpu/validation/power-sled-yellow-20261010/phase1-review.json`.
The qualifying run is `phase1-02/`. The earlier failed `phase1/` found unsupported
empty-ZIP signature sniffing; it is retained and excluded from qualification.

Phase 2 uses one complete, persistent recipe generated from those three Phase 1
records: `scripts/libretro_nvram_samples.power-sled-four-colors.toml`. It reuses
one qualified baseline, then commits and freshly reloads every discrete color:
eight new linked stages, 24 independent program records. The existing runner
validates each record before advancing and resumes from its journal after a
routine repair. It does not substitute MAME, standalone probes or inferred
numeric samples for this four-value selector.

The generated option extension is gated on the completed acquisition journal.
Expected encoding is `0 Silver / 1 Red / 2 Black / 3 Yellow` at Backup RAM offsets
`8`, `264`, `520`. The final review checks all copies, SRM identity/container CRC,
visible native labels, preserved calibration/EEPROM and unrelated setting bytes.
Bookkeeping counters are tracked separately from the color field.

Phase 2 evidence:
`build-libretro-gpu/validation/power-sled-yellow-20261010/phase2/campaign.json`.
Its status is the authoritative completion gate.

## Frontend And Topology Contract

All three per-game NVRAM menus expose the same Silver / Red / Black / Yellow
selector. Relay's manual value changes neither role nor rider count. ANS remains
`1 Silver / 2 Red / 3 Black / 4 Yellow / 0 Disabled` on Main/Slave, and solely
`relay` on Relay. Existing raw color names are preserved; Yellow is appended.

Linked Cabinets accepts Disabled / 2 / 3 / 4 / 5. The roster requires exactly one
Main, one to three Slaves and at most one Relay, with at most four riders. The
launcher accepts literal lists without compatibility checks, retains separate
controller/configuration/save ownership and names a final Relay folder `_relay`.
The three-program layout remains Main–Slave above Relay. Larger groups use the
generic two-column layout; physical panoramic alignment is still a review item.
The existing private four-rider gameplay qualification remains distinct from
production-core integration checks.

## Optional Master Archive

Every required Master chip has a declared donor:

| Master Content | Donor |
| --- | --- |
| Main Program, `epr-19472a.15` / `epr-19473a.16` | Relay, `powsledr` |
| Main Data, Polygons And Textures | Relay |
| Sound Program, `epr-19466.31` | Slave, `powsled` |
| Sound Samples, `fpr-19459.32` | Slave, `powsled` |

Frontend-neutral database metadata declares `rom_fallback="powsledr"` on
`powsledm`, retaining its Slave parent. Existing valid Master chips take
precedence, followed by Relay donor chips and Slave parent chips. All required
regions/chips and CRC validation remain mandatory. Loading through the fallback
keeps set identity `powsledm`, its patches, program role and separate saves.
Loading `powsledr.zip` normally still selects Relay. Invalid existing archives
fail; valid empty ZIP archives are supported.

When `powsledm.zip` is absent, the established runner creates a 22-byte empty ZIP
entry in its owned `content/` directory and symlinks sibling archives there.
Nothing is written into the user's ROM collection. This satisfies RetroArch's
existing-content-path requirement. A GUI-created empty Master entry alongside
its donors works too. Relay ROM data remains required when the Relay instance
is omitted; Relay alone does not provide the corrected audio.

ROM-free loader checks cover absent Master, valid empty Master, missing required
donor data, corrupt donor rejection and a complete Master that ignores an unused
corrupt donor. The qualifying Phase 1 and Phase 2 sessions deliberately omit
Master from their isolated ROM directory, providing actual RetroArch fallback
startup evidence. Launcher checks also verify owned content staging and ordinary
missing-game rejection.

## Verification Boundaries

Compilation, ROM-free checks, native menu acquisition, option application and
linked race proof are separate results. No factory Master fidelity, additional
colors, physical controller operation or full-course completion is inferred.
Normal RetroArch installation is updated after the acquisition and integration
gates; the removed development core is not recreated. The final integration
manifest records the build/installed hashes and any bounded production runtime
checks. No ROM data is committed.

## Final Integration Result

The final normal core has SHA256
`2429a518ba4d36cb2b579329030004d44e66954ab195d46bd2c7e82b3842cb27`.
It is installed in RetroArch with both configured/fallback databases updated,
backups retained and source/installed hashes matched. The development core
remains absent. Core/headless builds, device/loader, Netpacket, Save RAM, launcher,
recipe, NVRAM/YAML audits and workbook visual checks pass. Initial templates
remain byte-identical.

An additional bounded four-rider run uses that installed normal core, the missing
Master entry and acquired Red baselines. ANS 1/2/3/4 produces native Silver/Red/
Black/Yellow in all copies, preserving calibration/EEPROM. All four participants
establish native count 4, show a visible linked race and exit cleanly without
SHUTDOWN or i960 faults. This is replay-driven runtime proof, not physical-pad
or full-course qualification. Larger-group physical panoramic alignment remains
in roadmap.

Final manifest:
`build-libretro-gpu/validation/power-sled-yellow-20261010/integration.json`.
