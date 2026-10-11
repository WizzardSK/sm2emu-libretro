# Power Sled Pre-Race Relay Audio Review

## Finding

The reviewed Relay program explicitly stops both musical sequences when it
enters boarding / pre-race (phase 6). No additional Relay music-start callback
was found for that phase. The retained native Relay trace delivers both stop
packets and remains silent until the race countdown and race music begin.
This explains the observed gap in the emulated dump; it does not establish
factory-cabinet acoustic fidelity.

## Native Program And Sound Tables

The phase dispatcher at `0x14ec0` maps phase 5 to `0x32f50` and phase 6 to
`0xbfad0`. Selection's task list includes `0x33820`; its Relay-only initializer
installs callback `0x33800`, which requests index `0x66` / `A0 11 02`.
This is selection music, not a boarding music callback.

The command-4 receiver at `0xbd6c0` sets phase 6. On the Relay branch it calls
`0x127c0`, which requests indices `0x67` and `0x69`: `A0 11 03` and `A0 11 05`.
The Relay sound table at `0x608508` resolves these commands as follows:

| Packet | Native Sequence Instruction | Use In The Reviewed Path |
| --- | --- | --- |
| `A0 11 02` | `C0 DF 02 7F` | Start selection sequence |
| `A0 11 03` | `C0 DF 02 00` | Stop selection sequence |
| `A0 11 04` | `C0 DF 03 7F` | Start attract / race sequence |
| `A0 11 05` | `C0 DF 03 00` | Stop attract / race sequence |

All five direct calls to indexed helper `0x127a0` in the reviewed main program
are at `0x28da8`, `0x28dc8`, `0x309d8`, `0x33808`, and `0x3b788`.
They request indices `0x65`, `0x64`, `0x68`, `0x66`, and `0x68`, respectively.
Phase 6's task list at `0xbfb10` does not install another music initializer.
Its Relay-specific child at `0xbfc10` is a camera task; its continuation at
`0xbfc00` calls `0xe72f0`, rather than the music packet helper.

## Retained Runtime Evidence

The previously acquired native Relay trace at
`build-libretro-gpu/validation/power-sled-audio-20261009/run/client1.log`
provides a concrete comparison without repeating a gameplay campaign:

- Frames 1775–1777 deliver `A0 11 02` during phase 5. SCSP playback is active
  in that phase, so the selection request was not lost in this run.
- Frames 2644–2649 deliver both music stops on entry to phase 6.
- Frames 2650–2652 deliver `A0 14 02`. The Relay sound program supports groups
  `10`, `11`, and `12`, not `14`; this is not a supported hidden Relay track.
  Rider sound hardware has its own group-14 table.
- Phase-6 samples at frames 2760–3360 have zero active voices, zero PCM peak,
  and no additional sample reads.
- Countdown packets `A0 12 00` and then `A0 12 01` precede `A0 11 04` at
  frames 3888–3890, when the race soundtrack resumes.

## Comparison With The Result-Screen Bug

Selection callback `0x33800`, attract callback `0x309d0`, and race callback
`0x3b780` also clear themselves without checking enqueue success. They therefore
share the theoretical full-queue vulnerability demonstrated at results.
However, the retained Relay run successfully delivers selection music and
both pre-race stops. There is no evidence here that queue overflow causes this
particular silent interval. Retrying the selection callback would not create
a new phase-6 soundtrack or undo the deliberate stop commands.

No production source, ROM patch, installed core, or audio timing is changed by
this review. No new runtime qualification is claimed.

## Countdown Waveform And Master Audio Coverage

Follow-up analysis of the retained Relay recording confirms that countdown
commands are audible in that reference configuration. The three nonzero
intervals are approximately 61.73–61.94, 62.73–62.95, and 63.73–63.95 seconds:
short pulses one second apart, followed by roughly 0.78 seconds of digital
silence. The final countdown signal and race music follow. These are discrete
cues, not holes within a continuously playing musical track.

In 100-ms windows, retained attract/selection audio from 18–44 seconds has no
entirely zero window, as does race music from 65–79 seconds. Boarding from
46–61 seconds is entirely zero. This is limited to the reviewed recording;
it does not rule out pauses elsewhere in every possible sequence.

Relay sound commands `A0 12 00` and `A0 12 01` select `C0 DF 04 7F` and
`C0 DF 05 7F`. Rider hardware maps them to different sequences, `DF 0E/0F`.
The active visual countdown callback emits these packets through `0x12810`
at native timer checkpoints 180, 120, 60 and 0. Its four role checks at
`0xcfc48`, `0xcfc6c`, `0xcfc90` and `0xcfcb0` permit only Relay (`0x0100`).
The previous review incorrectly identified `0x3b2e0` / `0x3b350` as this
countdown: that separate task requests indices `0x6e` onward, which map to
group `70`, not the group-12 cues. It is not activated by this fix.

## Integrated Countdown Fix

With Relay Audio Enabled on Master, the four guarded checks accept Master
(`0x0200`). A guarded callback detour at `0x1f0740` preserves the native
checkpoint logic and emits audio only for the local human camera's sled index.
This avoids four copies in Standalone without modifying visual tasks, camera
selection, network identity or timer progression. Command indices `0x6a/0x6b`
are tagged `A0 62 00/01`; the frontend-neutral sound router sends them only to
the auxiliary Relay SCSP as native `A0 12 00/01`. Untagged rider group-12
packets remain on the primary board. Disabled does not apply these patches.

The normal-core RetroArch recording isolates the Relay board by muting rider
SCSP Gain and keeping Relay Gain at 100%. Three cues occupy 44.22–44.43,
45.20–45.42 and 46.20–46.42 seconds. The final cue and subsequent race music
produce continuous nonzero output from 47.20 through 65.75 seconds. An isolated
observer repeat confirms ordered packets `A0 62 00` three times, `A0 62 01`,
`BF 57 7F`, then `A0 61 04`. The latter two are native volume and race music.
No extra pause, playback timer or prerecorded audio is inserted.

A preliminary threshold-based reading incorrectly suggested race music had
been lost. Inspection of the full PCM and command trace disproved that;
no additional race-music patch was needed. Final normal rebuild matches the
qualified candidate hash. Audio checks cover exclusive countdown routing,
unchanged rider routing and exact partial-packet state continuation. Runtime
exits cleanly with no owned residual process. The capture shows an advancing
race. This qualification is Standalone Silver; other colors/topologies and
factory acoustic fidelity are not claimed.

Evidence: `build-libretro-gpu/validation/power-sled-countdown-fix-20261011/`.
The normal installed core is updated; the development copy remains absent.

## Musical Event And Address Progression

The Relay driver at `0x601b1a` selects a sequence by command group/subindex.
The group-11 table at `0x608512` declares six entries; group 12 at `0x608520`
declares four. All ten relative pointers resolve inside the sound ROM to
complete eight-byte scripts, including their explicit `FF 2F 00` terminator:

| Packet | Script Address | Event | Meaning In Reviewed Main Program |
| --- | --- | --- | --- |
| `A0 11 00` | `0x60852a` | `DF 00 7F` | Alternative music request |
| `A0 11 01` | `0x608532` | `DF 01 7F` | Result music |
| `A0 11 02` | `0x60853a` | `DF 02 7F` | Selection music |
| `A0 11 03` | `0x608542` | `DF 02 00` | Stop selection music |
| `A0 11 04` | `0x60854a` | `DF 03 7F` | Attract / race music |
| `A0 11 05` | `0x608552` | `DF 03 00` | Stop attract / race music |
| `A0 12 00` | `0x60855a` | `DF 04 7F` | Countdown pulse |
| `A0 12 01` | `0x608562` | `DF 05 7F` | Final countdown cue |
| `A0 12 02` | `0x60856a` | `DE 06 7F` | Other cue, not activated by this fix |
| `A0 12 03` | `0x608572` | `DE 07 7F` | Other cue, not activated by this fix |

These addresses are lookup alternatives, not a playlist that must increment
from one address to the next. The extended event handler at `0x6025ae`
normalizes the event status and consumes the two data bytes. The interpreter
advances its stream pointer as bytes are consumed; `0x602646`–`0x602666`
decodes a wait and retains the next pointer. `FF 2F` reaches the native end
handler at `0x60266c`; list continuation/loop sentinels are handled separately
at `0x60267a`–`0x6026d2`. There is no missing entry between the reviewed start,
stop or countdown scripts. Phase 6 actually selects the two stop scripts;
it does not attempt to progress to a nonexistent next music address.

The retained selection/race recordings contain no entirely zero 100-ms window
within their sampled musical intervals. That supports the reviewed command
and pointer analysis but does not prove every compressed sample stream,
all loops or every possible track are flawless. No exhaustive sample decoding
or original-cabinet comparison is claimed, and no speculative music patch is
introduced.
