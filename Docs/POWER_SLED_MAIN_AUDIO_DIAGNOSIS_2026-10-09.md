# Power Sled Main Audio Diagnosis — 2026-10-09

## Finding

The patched Main requests rider sound commands that the Relay audio ROM does
not implement. Its MIDI transport and sound CPU run normally, but those
requests are rejected before any SCSP voice starts. The normal Main therefore
produces zero PCM on the qualified selection, boarding and race path.

Replacing both Main audio regions with the existing Slave sound program and
matching samples in an isolated diagnostic configuration produces Main audio,
including during race state 7. The i960 Main patches and role `0x0200` are
unchanged. This confirms the ROM/command mismatch as the cause on this path.

## Source and Program Comparison

The production definitions in `data/games.xml` follow the local MAME reference:
Main and Relay use EPR-19467 plus FPR-19460/FPR-19461. Slave uses EPR-19466 plus
FPR-19459. MAME's `init_powsledm` changes only Main mode and node ID in the i960
program; it does not replace the Relay sound definitions. The original Main
unit remains undumped. The reference is the local
`../mame-my/src/mame/sega/model2.cpp`, including ROM_START(powsledm) and
init_powsledm; MAME is not executed by this diagnosis.

The first `0x3000` bytes of the two sound programs are identical. The common
68000 dispatcher at `0x00601b1a` interprets `A0 group value` commands. For groups
at least `0x10` and below `0x60`, it subtracts `0x10`, looks up the table pointer
stored at `0x0060801c`, and checks the maximum group index. An out-of-range
request branches at `0x00601b3c` to the return at `0x00601b66`. It similarly
checks the subcommand bound at `0x00601b4c`.

| Sound Program | Table Address | Maximum Group | Group `0x11` Maximum Value | Groups `0x13` / `0x14` |
| --- | --- | --- | --- | --- |
| Relay EPR-19467 | `0x00608508` | `0x12` | `0x05` | Absent |
| Slave EPR-19466 | `0x006085d4` | `0x14` | `0x0f` | Present: values through `0x03` / `0x04` |

Main sends `A0 13 03`, `A0 13 01`, `A0 14 00/01/02` on selection/boarding and
`A0 11 0f` on the race path. These are outside the Relay tables but supported
by the Slave sound program. Native Relay sound tasks explicitly gated to role
`0x0100` instead use its own `0x11` command range. The shared emulation code
contains no missing Main-specific audio enable switch to activate.

The sound data tables and associated sample set are the portion requiring
reconciliation. A speculative extra branch patch in the i960 is not required
to obtain audio in the tested candidate.

## RetroArch Evidence

Evidence root: `build-libretro-gpu/validation/power-sled-audio-20261009/`.
Temporary, passive tracing logs UART MIDI bytes and periodic sound CPU, SCSP,
sample-ROM and PCM counters. Both qualified runs use the existing three-unit
runner and the same verified operator recipe exclusively in the target core.
The diagnostic binary is a private copy; installed cores are not instrumented.

| Run | Main PCM Peak | Main SCSP Voice Starts | Relay PCM Peak | Slave PCM Peak |
| --- | --- | --- | --- | --- |
| Original Sound Definitions | 0 | 0 | 2929 | 4382 |
| Slave Sound Regions on Main | 4581 | 8 | 2975 | 4384 |

PCM peaks are signed-16-bit magnitudes from the recorded frontend output.
The Main SCSP peak before frontend processing reaches 4641 with the candidate;
three voices are active in the retained late race snapshots. In the original
run, MIDI is received, the sound CPU executes, and SCSP register writes continue,
but voice starts, sample-ROM reads and PCM peak remain zero.

The original and candidate Main send 709 and 705 MIDI bytes respectively. All
705 common bytes match in order; the original has a four-byte observation tail.
The i960 requests therefore remain the same through the shared observation.
Only the candidate sound ROM regions differ. All three programs reach state 7;
Main shows the race HUD and course in the candidate screenshot. Each qualified
run passes native links, three clean exits, SRAM identity/CRC and all three
ANS Ride copies. No forced termination or runner-owned residue remains.

## Discarded Probe and Identification Requirement

The first candidate changed only Main audio metadata while retaining the
original Main archive. The loader consequently selected the complete Relay
match, so this run is discarded as Main evidence. It failed native-link
qualification and all three processes exited cleanly. `INVALID.txt` records
this issue.

The qualified retry uses a private Main archive containing the original Main
program/common chips, removes its Relay audio chips and adds the complete Slave
audio pair. This selects `powsledm` with Main role `0x0200` and the candidate
sound definitions. Original archives and production metadata are untouched.
This private archive is a diagnostic fixture, not a deployment requirement.

Production integration must preserve identification of existing Main archives
and use CRC-checked parent/sibling lookup for the candidate sound regions.
Changing the Main XML audio region alone is insufficient. Avoid distributing
ROMs, rewriting user archives or applying the Slave audio to the Relay.

## Integration Status and Limits

Diagnosis is complete; production integration of the candidate is a separate
roadmap activity. The tested Main approximation can use the existing Slave
sound program and matching samples. Its original undumped sound hardware/content
cannot be authenticated by this experiment. Listening, full-race sound events
and physical gameplay remain unqualified; this is not an original-cabinet audio
accuracy claim.

Source `src/hw/model2b.cpp` is restored byte for byte. The rebuilt normal core
and both installed copies still match the prior SHA-256
`29be97fa659d0818ca9150e0cf78d8fd5a331862d80e26883d8eecc555de4daa`.
Production games.xml is unchanged. `review.json` records manifests/results,
trace events, MIDI sequences, PCM, SRAM, discarded-run cleanup and artifact
restoration. No calibration change, NVRAM sample acquisition, commit or push.

## Production Main Audio Integration Completed

The correction is now integrated with the user-requested local-first policy:
Main looks for EPR-19466 and FPR-19459 in its own archive, then uses the split
Slave parent as fallback. Old Relay audio files are removed from the Main
requirements. Existing Main archives retain their identity through CRC-checked
main-program recognition. The installed-core original-archive session produces
Main audio during the race; both cores and local system databases are updated.
See `Docs/POWER_SLED_MAIN_AUDIO_INTEGRATION_2026-10-09.md` for current evidence.
Earlier pending-integration and silence observations above are historical.
