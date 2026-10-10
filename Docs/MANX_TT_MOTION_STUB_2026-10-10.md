# Manx TT Technical References And Motion Stub

Date: 2026-10-10
Scope: Production Deluxe AMS Acknowledgement And Historical Diagnostic Evidence

## Production Integration

The acknowledgement stub is now part of the normal core. It is connected only
for Manx TT Deluxe: `manxtt` and `manxttc` follow native EEPROM Cabinet Type
byte `0x0a` (0 Deluxe / 1 Twin); `manxttdx` always connects it. Twin retains
the existing second-player input on parallel D. Cabinet changes take effect
on the next relevant I/O access, including changes saved through Service Menu.
No additional frontend selector is required. Cabinet Audio does not control AMS.

`src/hw/manxtt_ams.h` owns the response instead of reusing the generic force
latch. Command `0x3d` returns `0xce`; the following parameter returns `0xcd`.
Other commands retain the response. Reset and any cabinet transition start
from `0xff`. This acknowledges the native controller initialization; it does
not simulate physical movement, position feedback or the complete AMS protocol.

Save State format 10 preserves enable/response, including a pending parameter,
and rejects invalid state bytes. Formats 4–9 remain readable with absent AMS
state reset to idle. A legacy snapshot already stalled at a missing-controller
wait has no prior handshake to reconstruct; restart that content to run the
new initialization. The fixed 9 MiB Libretro buffer is unchanged.

### Production Validation

| Check | Result |
| --- | --- |
| ROM-Free I/O And State | Twin P2 preserved; Deluxe command/parameter, pending-parameter save/load, reset, cabinet changes, DX-only connection, legacy initialization and invalid state rejection pass |
| Revision D Deluxe, RetroArch | 6,600 frames; exits 0 in 114.84 seconds; race HUD 8/8, time 21, lap 37.65 |
| Revision C Deluxe, RetroArch | 2,300 frames; exits 0 in 42.57 seconds; title sequence beyond AMS check |
| Original Deluxe, RetroArch | 2,300 frames; exits 0 in 42.57 seconds; title sequence beyond boot check |
| Twin Old/New ABI Replay | 180 frames; image, PCM and native NVRAM identical |
| C Deluxe Save State | Exact replay, run-ahead, rewind, corruption rejection and rollback pass |
| Prior Installed Format-9 State | Read by new core; current-format deterministic restore/stress passes |
| Other Board Formats | VF2, Virtual On, Sega Rally and Daytona current-format round-trips pass |
| Builds | Normal GPU-capable Libretro core and frontend-free headless target compile |

The complete EEPROM remains identical to the isolated initial seed on both
Revision C/D cases. Native EEPROM and frontend SRAM container CRCs pass on all
three cases. Their mixed PCM is nonzero; acoustic correctness is not established
by the boot test. No ROM, NVRAM calibration or personal-save edit was used.

Private ignored evidence root:
`build-libretro-gpu/validation/manxtt-ams-20261010/`. It retains commands,
RetroArch logs/images/PCM/SRAM, ABI results, old/new comparison and `summary.json`.
Installation receipts and previous-core backups are in `installation.json`
and `sm2*_libretro.dylib.before`. Both normal local core copies are updated
atomically and verified by SHA-256 and Libretro API version.

Production core SHA-256:
`5597cb0b98748757e9de48d359efe760c1d397dc02fcfcfaf909fa0498db3253`.
Installed files are `sm2_libretro.dylib` and `sm2_dev_libretro.dylib` in the
user's RetroArch cores directory. The configured system database still matches
the source SHA-256 and needed no replacement. Restart RetroArch to load the
updated library.

The sections below retain the earlier private diagnostic investigation and
its original restoration receipts; their private-only status is historical.

## Manufacturer References

The Sega Deluxe owner's manual includes technical service sections, not only
player instructions. The catalogue identifies manual 420-6207-01 (1995).
The preserved Sega USA service site also supplies a motor-feedback bulletin.

- [Deluxe Power On Check](https://backup.segakore.fr/sauservice/Manuals/Manx%20Folder/MDhtml/MD13.html):
  the bike moves left/right and centers before attract mode; the check establishes
  the movement response. An irregularity produces an error.
- [Deluxe Troubleshooting](https://backup.segakore.fr/sauservice/Manuals/Manx%20Folder/MDhtml/MD21.html):
  failed initialization or drive-board/motor connections can prevent normal
  movement and unlocking at the start of a game.
- [Deluxe Output Test](https://backup.segakore.fr/sauservice/Manuals/Manx%20Folder/MDhtml/MD34.html):
  checks the game/drive board connection, potentiometers and motors. Operational
  drive-board DIP switches should all be off.
- [Sega Motor Feedback Bulletin, 1996-04-17](https://backup.segakore.fr/sauservice/Manuals/Manx%20Folder/Bulletins/4-15sb-pg1.html):
  documents absent/incorrect feedback and failed motor power-on checks caused
  by the physical bracket/harness arrangement on Deluxe machines.
- [Deluxe Gameplay](https://backup.segakore.fr/sauservice/Manuals/Manx%20Folder/MDhtml/MD19.html):
  the bike unlocks after the operation tutorial and locks/centers after a game.
- [Manual Catalogue](https://arcade.segakore.fr/m/manual_38.html):
  identifies the Deluxe manual edition and number.

These establish the controller's role. They do not specify the parallel byte
protocol or identify the reported female utterance. The wiring diagram is
listed in the manual, but its graphics were not inspected in this investigation.
The byte responses below are derived from the native Revision D program,
not claimed to come from a published controller specification.

## Historical Private Stub

The user authorized a stub to return the expected motion-board response.
The candidate is intentionally limited to parent `manxtt` in Deluxe mode.
Twin retains its existing player-port input path. The native program is not
patched; it receives the response through the existing parallel D/E callbacks.

| Event | Synthetic Response |
| --- | --- |
| Initial controller state | `0xff` |
| Parallel E command `0x3d` | `0xce` |
| Following parameter write while response is `0xce` | `0xcd` |
| Other commands | Retain the response; no additional protocol emulated |

The native check at `0x5f530` accepts `0xce`, sends its parameter and then
expects `0xcd`. The retained isolated seed sends parameter `0x7f`; this is the
native game's parameter, not an implemented DIP-switch response. The stub
acknowledges the exchange without modelling what that parameter configures.

The private candidate temporarily uses the existing drive latch as a response
byte and checks the loaded cabinet flag to limit its scope. This is a probe,
not a proposed final device architecture. Actual motion, position feedback,
motor timing, error states, reset/save-state fidelity and other ROM revisions
are outside its implementation.

## Boot Result

Using the same isolated Deluxe seed and runner as the preceding `0xff`
baseline, the stub produces:

1. Frame 94: command `0x3d`, response `0xff` to `0xce`.
2. Frame 96: parameter `0x7f`, response `0xce` to `0xcd`.
3. Native main state leaves 0 (AMS check), advances through 1 and 2 to 3.
4. Frame 102: a further `0x3d` command returns response to `0xce`.
5. The final image shows the Manx TT title sequence instead of the AMS check.

The 2,300-frame RetroArch boot exits normally. Source/build/installed cores
are restored and verified separately. The second command `0x3d` demonstrates
why passing the first check does not establish a complete controller protocol.
This result proves that an acknowledgement stub removes the initial gate; it
does not establish correct Deluxe mechanics, sound or the cause of Twin speech.

## Extended Input Replay Result

A second isolated run advances the same recorded input sequence to 6,600
frames. It exits 0 after 112.4 seconds. The native game enters main state 8,
substate 9; the final image visibly shows a race, position 8/8, a 22-second
remaining timer and a 36.77-second lap timer. A subsequent command `0x3f`
at frame 3,775 changes the retained response from `0xce` to `0xcd`.

This qualifies race entry in Revision D Deluxe with the synthetic response.
It does not qualify a complete race, physical controls or simulated mechanics.
PCM is present (4,905,390 frames; peak 20,034), but speech identity and sound
fidelity remain unverified. The identical input schedule is not a matched
sound comparison between cabinets: cabinet mode changes native timing and
sound routing, and the utterance has not yet been identified.

Both completed cases preserve the complete EEPROM against the isolated seed;
native EEPROM and SRAM container CRCs pass. The initial gate is causal for
the Deluxe boot failure; no causal claim about Twin speech follows from it.

## Historical Evidence And Restoration

Private ignored root: `build-libretro-gpu/validation/manxtt-motion-stub-20261010/`.
`build-probe.py` creates `motion-stub-probe.dylib` and restores source in a
`finally` block. `stub-candidate.patch` retains only the stub for review.
`run.py` uses the established `scripts/smoke-retroarch.py`; `run-race.py`
extends the same recorded input sequence to examine the next gate. Per-case
receipts, logs, PCM/image/SRAM and `analyze.py` / `summary.json` retain results.

The first sandboxed application launch aborted before producing a core log;
its receipt is retained as `d-deluxe-stub-launch-abort`. The isolated boot was
then launched outside that restriction and completed normally. This is an
application-launch failure, not a demonstrated emulation failure.

The normal target is rebuilt after removing diagnostic code. The normal build
and both installed cores retain SHA-256
`44cf32065c3208eaa34b601a4a04423b1c5217e7b14fa54e0debc79b3fbd3d5b`.
No private core is installed into the user's normal RetroArch core directory.
No ROM substitution, voice suppression or calibration edit is included.
