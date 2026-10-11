# Power Sled Relay Standalone Attract

## Contract

The existing **Power Sled Standalone Mode (Restart Required)** option now also
applies to `powsledr`, only with **Linked Cabinets = Disabled**. Enabled remains
the default. The Relay runs its native Attract presentation and sound tasks as
if the other cabinets supplied no selection or race-start inputs. It does not
start a standalone race. Master gameplay, Slave behavior and linked programs
remain unchanged. Existing saved Disabled choices remain respected.

Reload content to change the patched mode or switch to linked play. The existing
frontend state flag rejects states created with a different Standalone setting.
This is an experimental port adaptation, not original-cabinet fidelity proof.

## Implementation

All changes are adapter-owned in `src/libretro/power_sled_standalone.*` and
invoked from the content loader. No machine, communication-board or ROM archive
is modified. In-memory patches require known instructions, the native Relay
initializer and empty helper space before any mutation.

- At `0x11d20`, let the local communication board initiate its one-node ring.
  The game initializer remains unchanged and publishes Relay role `0x0100`.
  The link initiator and application role are separate.
- The same isolated startup branch uses the existing Relay label at `0x11920`
  instead of the communication-Master label at `0x11950` (guarded pointer at
  `0x11d58`). It now reads THIS IS RELAY SATELLITE throughout initialization.
  This changes presentation only: local link initiation and application role
  remain unchanged. Linked play and Standalone Disabled retain native labels.
- Build four local ownership entries and map four self-published actor records,
  using native attract construction, physics and presentation tasks. Account
  for the fourth actor in the relevant attract loops and field counts.
- The startup presentation layout uses configuration 7. This is an experimental
  local presentation prerequisite, not evidence of four physical rider boards.
- Supply an inert Master command/status view at `0x1f1400`, with role `0x0200`
  and zero command/status fields. No Slave process or start-game packet exists.
- Ignore the Relay operator decoder's Entry/selection/race/emergency commands
  in this mode; preserve local Test and the existing Test input-ownership guard.
- Local Test reads the Relay's own packet. Exit retires its outgoing Test
  command and resumes native phase 4 construction. The ordinary Exit advances
  phase 15 to 16; the isolated candidate remained at phase 18, so that candidate
  is not deployed. No new controller binding or NVRAM rewrite is added.

Helper addresses are `0x1f1000` (ownership), `0x1f1080` (mapping), `0x1f1180`
(layout), `0x1f11a0` (Test Exit) and `0x1f1400` (inert Master record). Existing
linked-session helpers are retained and do not overlap these regions.

## Failed Candidates And Correction

The original isolated Relay waits for another link initiator. Merely providing
local actors does not establish its ring. After enabling local initiation, a
candidate reached Attract but entered SYSTEM SHUTDOWN: it reused a Relay packet
as a Master packet, whose status fields have different meanings. A passive
instruction trace records shutdown command `0x8000` from `0xc55e0`, followed by
`0x8001` from `0xc56c8`. The final candidate uses the separate inert Master view.

An intermediate view held command 1 (return to Attract). This disrupted local
Test. The deployed view holds command 0, representing no operator input; Test
and return to Attract are qualified separately. Failed candidates remain only
in the private evidence directory.

## Verification

Evidence: `build-libretro-gpu/validation/power-sled-relay-attract-20261011/`.

- Passive observer: 9,000 native frames, Relay role `0x0100`, Attract phase 4
  throughout after startup, with no selection, race or shutdown phase.
- Actual RetroArch: 126 seconds of recorded audio and eight separate captures
  covering moving demonstration scenes and instructions. All sampled post-boot
  phases are 4; clean process exit and no residual owned processes.
- Final normal build: separate RetroArch run, 61 seconds of recorded audio and
  four captures, normal exit and no residue. Video changes and PCM are present.
  The existing decoder handles RetroArch's known padded WAV header; untouched
  originals and normalized recordings are retained.
- Final normal ABI: 9,000 frames; video/audio hashes match the observer run.
  Save State round-trip, deterministic replay and malformed-state rejection
  pass. This ABI test is separate from the actual RetroArch checks.
- Controlled native-input check: Start and Entry do not leave Attract; Test
  enters phase 15, Call on its initial Exit returns to phase 4 and stays there.
- Master unchanged: 1,200-frame video, audio and native save hashes match the
  previous installed core. Relay Disabled: same comparison over 3,600 frames.
  These bounded comparisons do not requalify every linked gameplay topology.

Runner `roster_ready` and `native_link_ready` flags describe external Netpacket
logging and are false for this single-instance run. They are not claimed as
external networking evidence; startup progression and native phase/role traces
qualify this local adaptation.

## Deployment And Scope Boundaries

Only the normal installed `sm2_libretro.dylib` was updated, with a retained
backup and matching SHA-256:
`b821e425c47e8791438ec3e8e9240cfd2a70365e65bab90bd1acdb13b4be74b0`.
The dev core remains absent; installed databases and personal saves are unchanged.

The pending Rail Chase 2/HOTD gun integration was excluded from this build by
using its retained pre-integration sources during compilation and restoring
those pending source edits afterwards. The build recipe is retained. No BEL
change, commit, push or cross-project modification is included.

## Usage

Sol High retained. Account usage moved from 7% to 8% on the integer-rounded
meter, below the approved 35% ceiling. Reset: 2026-10-18 07:47:24 Europe/Rome.

## Standalone B_CRX Diagnostic Correction

The native scan at `0x24e40` excludes Relay headers `0x0100` from its rider-board
count. A lone Relay therefore produces zero and configuration 8 (ERROR), even
though its local ring and continuous presentation work. In Relay Standalone
only, the guarded branch at `0x24e98` changes from `0x08000008` to `0x08000004`:
retain the Relay-presence flag, then include the single real Relay board in
the diagnostic count. The native renderer now reports **B_CRX ONE**. This is
an adaptation for the experimental isolated mode, not a newly discovered
factory standalone configuration.

No Master/Slave packet is fabricated, no error string is replaced, and the
four local actors do not become four physical boards. Role `0x0100`, native
range checks and the separate virtual presentation layout remain intact.
The patch is not applied with Standalone Disabled or Linked Cabinets enabled.

Evidence: `build-libretro-gpu/validation/power-sled-relay-bcrx-20261011/`.
The normal core in isolated RetroArch captures B_CRX ONE at boot, then advances
through demonstration scenes and instructions (six captures, clean exit,
no residual processes). A matched 1,800-frame before/after ABI comparison
has identical final video, accumulated audio and native NVRAM hashes.
Save State round-trip, deterministic replay, malformed-state rejection and
the existing save-RAM checks pass. Only the normal installed core is updated
with backup and SHA-256 verification; the dev core remains absent.

Sol High retained; account usage moved from 12% to 13% on the rounded meter.
Reset remains 2026-10-18 07:47:24 Europe/Rome; approved ceiling 35%.
