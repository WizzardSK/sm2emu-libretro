# Power Sled Master Music Experiment — 2026-10-10

## Result And Scope

The optional **Power Sled Relay Audio (Restart Required)** selector runs Relay
music inside the reconstructed Master, alongside its existing rider sound board.
It is experimental and now defaults to **Enabled** (user revision, 2026-10-11). With Enabled, a Master–Slave
pair reaches an advancing race with Relay music and rider effects, without
launching a Relay instance. This is an optional reconstruction, not evidence of
the undumped factory Master hardware.

The selector is visible for the three Power Sled sets under System, immediately before Power Sled
Standalone Mode and NVRAM Settings. It applies only to `powsledm`;
Slave, Relay and other games retain their existing behavior. Reload content
after changing it. A frontend Restart alone does not reload the patched program.
Leave it Disabled when a separate Relay already supplies music to avoid two
copies of the soundtrack.

## Cause And Native Event Routing

The Relay-derived Master already contains the musical scene routines, but their
role gates exclude Master. Its corrected primary sound ROMs serve rider commands
and cannot replace the Relay sound program. The adapter therefore reuses the
existing `Model2Sound` emulation for a second independent SCSP/68000 board,
with CRC-checked `powsledr` audio program and samples. Donor lookup checks the
loaded archive, then adjacent `powsledr`. No ROM archive is modified.

`src/libretro/power_sled_audio.cpp` owns guarded, in-memory program patches:

- Four music initializers (`0x28de0`, `0x309f0`, `0x33820`, `0x3b7a0`) accept
  Master role `0x0200` instead of Relay role `0x0100`.
- The first two retain their musical continuation but skip the Relay camera
  child allocation. **`0xc7b80` is a camera task, not the music generator.**
- The race constructor originally allocates `0x3b7a0` only on its Relay branch.
  A small appended task allocation preserves the complete Master/rider branch
  and adds that music task. The outer role choice, rider controls, camera and
  network role are preserved.
- Original music indices `0x64`–`0x69` are tagged for auxiliary routing. A copied
  native volume helper tags only music volume; a stop helper preserves rider
  stops and additionally issues the Relay's music stops.

The hardware routes tagged `A0 61 xx`, `A0 62 xx` and `BF 57 xx` packets to the auxiliary
board as native `A0 11 xx`, `A0 12 xx` and `BF 07 xx`; ordinary packets remain on the primary
board. Music follows native scene/race events, with no frontend playback timer
or recorded soundtrack. The second board runs on the same exact sample clock;
its PCM is mixed through a short queue with 16-bit saturation. SCSP Gain controls
the rider board; Power Sled Relay Audio Gain independently controls the added
board (2026-10-11 user revision). Master Volume controls the final output. Music Volume remains
specific to MPEG hardware. The experiment does not import Relay-specific voices
or a Relay camera into Master.

Unsupported program instructions/free patch space or missing donor regions leave
the ordinary rider program/audio intact and produce a notice. The core performs
the full guard before applying any instruction edits.

## Boarding Silence

The retained unmodified Relay trace explicitly sends `A0 11 03` and `A0 11 05`
at the transition from selection to boarding. Its state-6 samples at frames
2760–3360 have zero active voices and zero output peak. The race constructor
then starts the race sequence, with `A0 11 04` around frame 3888, after countdown
commands. The experiment preserves this stop/start interval. The user also
confirmed that the pause occurs with the separate Relay. This establishes the
behavior of the emulated dump; original-cabinet acoustic fidelity remains open.

## State Compatibility

Native state writer advances to **11**, adding auxiliary-board presence, full
board state, mixer queue and partial MIDI packet. Readers retain formats 4–10
for configurations without the extra board. Format-10 Master states load with
the selector Disabled. Enabled and Disabled Master states are deliberately
incompatible: the frontend trailer rejects the mismatched configuration before
machine mutation. The serialized buffer remains 9 MiB. External Linked Cabinets
sessions retain their existing Save State restriction.

## Verification

Evidence is retained under
`build-libretro-gpu/validation/power-sled-master-music-20261010/`:

- The first `enabled-pair` prototype qualified initial music but **failed race
  music**. It is retained as incomplete evidence; adding only role gates was
  insufficient.
- Corrected `race-task-pair`: two normal-core RetroArch instances, isolated
  config/saves/ports, existing native input replays, Master Silver / Slave Red,
  no Relay process. Three captures per rider show advancing races; roster and
  native link are ready, both exits are clean and no owned process remains.
- An eight-second reference from the earlier Relay race matches the Master
  recording at **77.4866 seconds**, correlation **0.785878**. The same match is
  present when restricting the search to recording time after 60 seconds.
  Lower correlation than the Relay-only baseline is expected from the mixed
  rider effects. Slave and previous rider-only recordings have maximum absolute
  correlation at most **0.0402**. Nonzero PCM alone was not used as music proof.
- Both final SRMs retain game identity, valid container CRC, three concordant
  Ride copies and unchanged baseline calibration/EEPROM.
- Disabled old/new ABI runs have identical image/PCM hashes. Fresh-process
  format-10 state continuations also match exactly. Enabled state round-trip,
  deterministic replay, malformed-state rejection and rejection of a Disabled
  state without mutation pass.
- ROM-free checks cover primary/auxiliary MIDI separation, partial-packet
  restoration, mismatched hardware rejection and legacy sound-state loading.
  Audio balance and Save RAM checks pass; core and headless targets build.

`Master-Race-With-Music.wav` is a 15-second excerpt of the corrected Master
recording. Original RetroArch WAV files are retained; their padded headers are
normalized for analysis without changing PCM.

This bounded qualification does not establish full-course completion, repeated
scene recovery, every color/topology, physical devices or factory sound fidelity.
The normal installed core is updated from the exact qualified build with backup
and hash verification; the removed development core remains absent. See the
local `installation.json` for artifact hashes.

## Reproduce

Enable the selector for the Master and reload its content. The established
launcher still accepts the same pair:

```sh
python3 /Users/andrea/dev/sm2-emu-libretro/scripts/launch-linked-cabinets.py \
  --game powsledm:1,powsled:2 --controllers 0,1
```

For an isolated automated comparison, reuse `scripts/test-retroarch-netpacket.py`
with `--record-audio`, the existing per-instance input replay map and an options
JSON setting `sm2_power_sled_relay_audio` to `enabled` only for `host`.
The exact invocation, overrides, runtime results and waveform review are retained
in `race-task-command.json`, `enabled-options.json`, `race-task-pair/result.json`
and `race-task-pair-audio-review.json`.

## Countdown Coverage Update — 2026-10-11

The existing visual countdown now also emits the native Relay cues under this
selector. Only the local human camera task emits audio in Standalone; no
separate camera/task or frontend timer is added. Normal-core RetroArch qualifies
three pulses followed by the final cue and race music with rider audio muted.
Group-62 routing and partial-packet restoration checks pass. See
`Docs/POWER_SLED_PRE_RACE_AUDIO_REVIEW_2026-10-11.md` for native addresses,
musical pointer analysis and qualification limits.

## Frontend Default Revision — 2026-10-11

Menu label is now **Power Sled Relay Audio On Master (Restart Required)**,
with Enabled as the default, following Standalone in System. The raw key is
unchanged. An explicitly saved Disabled value is respected. When a separate
Relay also plays audio, disable one music source or mute its board gain to
avoid playback from both instances; Enabled is not silently overridden.
