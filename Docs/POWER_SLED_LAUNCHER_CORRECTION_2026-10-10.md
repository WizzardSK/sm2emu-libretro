# Power Sled Launcher Ride Defaults And Relay Order

## Subsequent Master Color Integration

The failure analysis and original recommendation below describe the preceding
production database. The corrected reconstruction now qualifies both Main
Silver / Slave Red / Relay and Main Red / Slave Silver / Relay. The requested
`--game powsledm:1,powsled:2,powsledr:relay` command is now supported in the bounded
three-program race observation. Role/folder/controller conventions and explicit
CLI precedence remain unchanged. See `POWER_SLED_MASTER_COLOR_2026-10-10.md` for
the exact patch scope, native panoramic intro, verification and deployment.

## Report And Cause

The previously recommended `powsledm:1,powsled:2,powsledr:relay` command selected
Main Silver / Slave Red. Native communication passed, but the game's startup
screen reported `SILVER RIDE 0` and requested changing Ride ID. Main displayed
an unknown ride identity. This combination already has a retained failure in
`POWER_SLED_LINKED_GAMEPLAY_2026-10-09.md`: link-ready flags do not establish
native startup or gameplay. The earlier ANS-convention check qualified the
saved colors and network only; its recommendation was insufficient.

The qualified three-program combination is Main Red / Slave Silver / Relay.
The current patched Main approximation does not satisfy the required Silver
ride merely through its own Silver operator setting. This describes the tested
three-program topology, not an original undumped Main ROM or larger topology.
ANS raw values still mean `1` Silver, `2` Red, `3` Black and `relay` Relay.
Explicit CLI values keep precedence. The launcher does not silently substitute
colors or validate requested game combinations.

## Role And Color: Scope Of The Current Limitation

The startup failure does not establish that a factory Master/Silver cabinet
was forbidden. The original Main program is unavailable; the production Main
is a Relay-derived reconstruction. Treat role/color independence as the target
to investigate, rather than declaring the user's selection invalid.

A focused static follow-up reuses the original retained CPU regions and decoder
in `build-libretro-gpu/validation/power-sled-native-io-20261009/`:

- Original Slave initializer `0x15840` reads settings byte 8 (Ride ID), stores
  it as local index at `0x0053e6f4`, and writes the same value as application
  identity at `0x005293f0`, with its complement at `0x005293f2`. In this
  program, Ride color also identifies a rider; it is not solely a visual field.
- Relay roster routine `0x249c0` reads each communication slot's identity.
  It handles Master `0x0200` and Relay `0x0100` separately, then counts rider
  identities 0, 1, 2 and 3. Master does not increment any rider-color count.
- Diagnostic branch `0x24c48` requires exactly one identity-0 (Silver) rider
  when riders are present. With two ordinary riders, `0x24c98` also requires
  exactly one identity-1 (Red) rider. This is a game-level roster requirement,
  distinct from communication-board link readiness.
- Current Main patches preserve the separate Master identity. Caption and
  sled presentation patches read the NVRAM color but do not add a colored
  rider identity to the communication roster.

Consequently, changing Main's displayed color cannot replace the missing
identity-0 rider in Main Silver / Slave Red / Relay. This identifies the current
mechanism, not the factory Main's intended role/color behavior. A correction
must reconcile rider identity, roster, packet selection and local race index
while preserving the Master command source. Skipping the diagnostic check
alone does not establish correct gameplay. This follow-up adds static evidence;
it makes no production patch or new runtime qualification.

## Current Command And Layout

```sh
python3 /Users/andrea/dev/sm2-emu-libretro/scripts/launch-linked-cabinets.py \
  --game powsledm:2,powsled:1,powsledr:relay --controllers 0,1,2
```

| Program | Launch Order | Folder | Controller | Position |
| --- | --- | --- | --- | --- |
| Main Red | 0 | `host` | 0 | Top Left |
| Slave Silver | 1 | `client1` | 1 | Top Right |
| Relay | 2 | `_relay` | 2 | Bottom Left |

The transport ring is Main → Slave → Relay → Main. The existing emulated
communication board assigns native IDs in descending order after Main: Main 1,
Slave 3, Relay 2, all count 3. Folder/participant indices are distinct from
these native board IDs. No protocol or emulation change is made.

Bare Power Sled names use Red/Silver for a fresh session. Saved GUI colors and
explicit suffixes retain precedence; use the explicit command above to correct
an earlier Silver/Red session. The role-specific window layout remains fixed
when names in the CLI are reordered. Optional generic Relay launches also use
`_relay` for their final instance.

## Old Session Recovery

Saved configuration and SRAM are matched to the ROM in the previous manifest,
so old `client1` Relay data is restored to `_relay`, and old `client2` Slave data
is restored to `client1`. Old directories remain intact. Repeated-ROM generic
sessions fall back to the same participant position for their renamed Relay.

The user's original run 0001 contains only the Relay SRM; Master and Slave SRMs
are absent after its reported shutdown. Their absence is observed, but the
frontend's cause is not established. Launcher sessions now import available
SRMs and let automatic initial setup handle missing saves. Strict sample and
qualification baseline requirements without `--instance-games` are unchanged.
No original user save is deleted or rewritten for this verification.

## Verification

Evidence root: `build-libretro-gpu/validation/power-sled-relay-last-20261010/`.

- Six ROM-free game selection and old-session mapping checks pass, including
  protection against swapping old Slave/Relay configuration and repeated-ROM
  Relay lookup.
- Python syntax checks and whitespace checks pass on edited tracked paths.
- `fresh/runs/0001/cabinets`: installed-core 50-second observation from a fresh
  session using the exact corrected command. All native links ready, native
  IDs 1/3/2 in Main/Slave/Relay order, three normal exits and no residual peers.
  Main/Slave capture black attract transitions; Relay shows Image Training,
  rather than the prior startup Ride error.
- The first resumed attempt stops before launching on the old strict missing
  SRM check. It is retained as failed runner evidence, not gameplay evidence.
- A second bounded resume test uses private copies of the user's original
  manifest, saved options and available Relay SRM. The Relay SRM initially
  imports byte-for-byte into `_relay`. It reuses the already qualified Manual
  input movies, remapped by program.
- `resume-missing-saves/runs/0002/cabinets/result.json`: the resumed 95-second
  run passes with Main/Slave/Relay order, controllers 0/1/2, all native links
  ready, three normal exits, no forced kills and no residual processes.
  Main and Slave both reach racing: Main screenshots advance from 44.20 to
  33.58 seconds and Slave from 44.13 to 33.46, with visibly advancing course
  views. Relay shows the active `LIVE 1P` rider camera. All three final SRMs
  exist in their corresponding folders. Original available saves and option
  files still match the isolated input baseline copies.
  This verifies automatic replay and session recovery in RetroArch; physical
  controller operation remains separate from the configured device indices.

No core binary rebuild or deployment is required: the installed core remains
`abda589c10b47acfe472f41bc2e57ec5682edd512b469bbbef490ef6ac6f15fe`.
