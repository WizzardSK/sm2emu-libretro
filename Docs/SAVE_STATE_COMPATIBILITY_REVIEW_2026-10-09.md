# Save State Compatibility Review — 2026-10-09

## Closure

Save State Compatibility is complete for the reviewed integration scope. This
review reconciles successful package evidence with the current source contract
and adds one actual RetroArch round-trip on the current installed core. No
emulation, serialization layout, Core Option, dependency or user-save change
was required. Failed historical probes remain diagnostics, not passes.

The integrated baseline remains `5ddf84ae7970a9bce1d0a17b3900d26065de1996`
(0.9.13) plus documented imports and corrections.

## Current Contract

| Property | Current Behavior |
| --- | --- |
| Machine Format Written | 8 |
| Machine Formats Read | 4, 5, 6, 7 and 8 |
| Libretro Buffer | Fixed 9,437,184 bytes (9 MiB), available before content load |
| Frontend Tail | 96 bytes inside that buffer |
| Legacy Save | The next successful save writes format 8; loading does not rewrite the original file |
| Identity | Machine magic, supported version, game and board must match |
| Failed Load | Invalid headers are refused; a truncated/invalid machine payload rolls back the machine snapshot |
| Portability | Platform and endianness dependent; raw cross-process byte identity is not a semantic comparison |
| Linked Cabinets | External Netpacket session is not archived; save/load is refused while active |

| Format Introduced | Compatibility Handling |
| --- | --- |
| 5: Sound Scheduler | Format-4 scheduler carries are converted during reading |
| 6: Audio History | SCSP filter and DSB2 playback/loop state are saved; older missing history uses the documented fallback. The frontend tail also preserves output DC-filter history |
| 7: Persistent Geometry | New snapshots restore persistent geometry RAM/registers; data absent from formats 4–6 cannot be recovered |
| 8: Local Communication | Pending local loopback frames and overflow are restored; older snapshots clear future queued frames but cannot reconstruct the omitted queue |

After loading, derived renderer resources and queued audio are invalidated and
rumble is stopped. Saved frontend cadence, audio delivery remainder, input
runtime, gun-flash state and output DC history are restored from the tail.
Older cores do not gain support for format 8 through this compatibility path.
SRAM/NVRAM is a separate persistence contract.

## Retained Evidence Audited

Successful result files and raw state headers were read directly. The receipt
records their paths and SHA-256 hashes.

- Format-8 same-process round-trip, exact three-frame machine replay, corrupt
  input rejection, four run-ahead cycles and reverse-order rewind patterns pass
  on Daytona, VF2, HOTD, DOA, Top Skater and the three distinct Power Sled sets.
  These cover all four board types and DSB2.
- Eight historical fresh-process loads pass: five real format-7 snapshots and
  representative VF2 format-4, Daytona format-5 and VF2 format-6 snapshots.
  Each result confirms external loading and subsequent round-trip/replay/
  rejection success. The audio package retains its additional ten format-4/5
  loads with the SCSP filter enabled.
- For all three Power Sled variants, the retained uninterrupted 603-frame and
  restored 600-plus-3-frame outputs were rechecked directly: final image and
  complete three-frame PCM tail match exactly.
- The original 68000 package covers cross-session host-pointer rebinding on
  all four boards plus DSB2. Musashi pointers are rebound to the loading process;
  differing raw pointer bytes do not establish emulation divergence.

These ABI runs belong to their documented package artifacts and were not
repeated with the latest binary. Historical NVRAM result fields are excluded
from this compatibility audit.

Reports: [68000](UPSTREAM_SAVE_STATE_PACKAGE_2026-10-08.md),
[sound timing](UPSTREAM_SOUND_TIMING_PACKAGE_2026-10-08.md),
[audio](UPSTREAM_AUDIO_PACKAGE_2026-10-08.md),
[geometry](VIRTUA_COP_SAVE_STATE_REPLAY_2026-10-08.md), and
[local communication](POWER_SLED_PRELIMINARY_VALIDATION_2026-10-08.md).

## Current Installed-Core RetroArch Check

RetroArch Nightly 1.22.2, macOS ARM64, Virtua Cop, default asynchronous Software
renderer, existing gameplay input replay, isolated configuration/saves/states.
The existing `scripts/test-retroarch-savestate.py` runner verifies pause status,
waits for screenshot task completion, and advances both comparison paths by
three frames to cover geometry cadence and presentation latency.

- Save/load messages are present in the frontend log.
- The scene changes after advancement; the restored game region matches exactly.
- Restored game-region SHA-256:
  `8902496c438f89f642bcc46d42e1e32f12c5f7034978dbf6feca4958798bd157`.
- The game resumes after restoration; exit code 0, no forced termination.
- Full screenshot hashes differ; only the OSD-free game region is claimed exact.
- The actual file is 11,161,912 bytes. Its parsed RetroArch wrapper contains an
  `RPLY` chunk of 1,724,692 bytes, a `MEM ` chunk of exactly 9,437,184 bytes
  containing machine format 8, and `END `. The replay chunk accounts for the
  larger file; the core's fixed capacity did not change.

Evidence directory:
`build-libretro-gpu/validation/save-state-closure-20261009/`.
`audit.json` retains source/result hashes, actual state versions, the parsed
frontend wrapper, coverage and limitations. The owned frontend process exited
normally. No rebuild or replacement was needed: the build and both installed
local cores already match SHA-256
`3200f0e99a527d186def9cced15f82e70e564c39e8e70881f02fae083dbc3d05`.

## Qualification Limits

This closes the integration's known compatibility work, not an exhaustive
all-game/device audit. Readability cannot recover data absent from older
snapshots. No portable cross-platform state-file format, synchronized external
cabinet restoration, new frontend run-ahead/rewind UI proof, physical input,
subjective audio, or current Windows/Batocera frontend requalification is
claimed. Existing platform results retain their own artifact/date scope.
Power Sled gameplay and Manx TT Relay remain separate roadmap activities;
Manx TT stays last as requested. No commit or push.
