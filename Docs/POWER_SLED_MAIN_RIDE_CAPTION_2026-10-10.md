# Power Sled Main Ride Caption

## User Convention

The Main's identity line must show `THIS IS <COLOR> RIDE`, as Slave does,
following the current operator Ride ID in NVRAM. The communication role is
shown separately. Do not replace the color with `MAIN` or `MASTER`.

## Cause And Correction

The Relay-derived Main uses native role `0x0200`; its original identity
selectors recognize Relay `0x0100` and rider colors 0–3, so Main falls through
to `THIS IS ????????`. The program contains two separate copies of this
selector and caption table: one at `0x152d4`, another at `0x245ac`.

Only `powsledm` receives four ROM-database word patches. In both selectors,
replace the load of the role word at `0x005293f0` with an unsigned byte load
from the native settings Ride field at `0x01d00008`. The native helper at
`0x000ed900` returns settings base `0x01d00000`; Slave's role initializer also
reads byte 8. Settings recovery and the existing NVRAM integration validate
the three native copies before these displays.

The original caption tables now select Silver (0), Red (1) or Black (2).
Labels, unknown-value fallback, role storage, communication, operator inputs
and the subsequent state logic remain intact. Both routines overwrite `g4`
with a separate state/index read after selecting the caption. No code address,
Save State layout, ROM archive or Core Option changes.

The correction is carried in `data/games.xml`, alongside the existing Main
mode/node patches. It requires reloading content with the updated database;
the core binary can remain the currently installed build.

## Verification

Evidence root:
`build-libretro-gpu/validation/power-sled-main-caption-20261010/`.

`color-static-review.json` confirms that only the two caption-load instruction
pairs differ from the current patched Main program, that original text tables
are intact and that native role stores are unchanged.

Three isolated RetroArch observations select Main Silver, Red and Black while
retaining Slave Red. The intentionally missing Silver Slave keeps the native
startup diagnostic visible for caption review. This is a display check, not
an attempted correction of the game's Silver Ride requirement.

Visual review confirms `THIS IS SILVER RIDE`, `THIS IS RED RIDE` and
`THIS IS BLACK RIDE` on Main. `color-runtime-review.json` verifies nine clean
exits with native links, Main's unchanged native role, SRAM identity/CRC and
the three-copy Ride values for each observation.

The staged system database and both installed RetroArch database copies are
updated, with previous copies retained under `installed-before/`.
`deployment.json` records all three matching SHA-256 values:
`bb3877446efa421a9fac92b84f72f566348c0f984d42a60984ca45ca64ac1fc8`.
The installed core binary remains unchanged at SHA-256
`abda589c10b47acfe472f41bc2e57ec5682edd512b469bbbef490ef6ac6f15fe`.
Restart the linked group to load the updated database. This qualification
covers caption selection, not new gameplay or communication behavior.

## Superseded Probe

An initial private experiment changed one fallback string to `MAIN`. Its
startup capture still showed question marks because that screen uses the
second selector. The user's clarified color requirement supersedes that
proposal. Its private root `run/` remains diagnostic evidence; its string
patches are absent from production and from the color observations.
