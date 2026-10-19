# YM3413 Hardware Applicability Review

Date: 2026-10-19

Status: Excluded — User Approved On 2026-10-19

Scope: Applicability assessment only; no emulator, Core Options or deployment changes.

## Recommendation

The user approved excluding the external YM3413 integration from the current Model 2 work scope:
the reviewed sources do not identify a supported Sega sound-board configuration
using this device. Reopen if board documentation or firmware analysis establishes
its presence and connections. This is a source-based applicability finding,
not a claim that every physical board revision has been inspected.

The earlier candidate list was too broad: a new external-DSP interface in the
MultiPCM implementation establishes a chip capability, not its use by Sega.
The directly applicable MultiPCM register and attack corrections remain separate
and already integrated.

## Sources And Findings

MAME reference: `cff1e78194319737798cf24f2e106ae3e34222c1`.
The originating change is
[d65391dcfab3](https://github.com/mamedev/mame/commit/d65391dcfab3d372887ad865521ffc76a8081956).

1. **The new active YM3413 integration is in the Yamaha TG100.**
   Its driver describes the sound generator, external effect memory, serial
   audio and control connections. It enables MultiPCM's DSP send, connects
   its control callback, configures the DSP clock and delay RAM, and routes
   the effect return into the stereo output.
   [TG100 source](https://github.com/mamedev/mame/blob/cff1e78194319737798cf24f2e106ae3e34222c1/src/mame/yamaha/tg100.cpp).
   A repository code search also returned commented YM3413 configurations in
   `ymsy35.cpp` and `ympsr400.cpp`; neither establishes Sega applicability.

2. **The Sega Model 1 sound board used by early Model 2 games has a different
   configured signal path.** MAME instantiates a 68000, two MultiPCM devices,
   YM3438 and UART. Stereo outputs go directly to the speakers; there is no
   YM3413 instance, enabled DSP send or DSP control callback. Its MultiPCM
   memory windows expose offsets 0–3, while the new TG100 effect-control
   interface is at device offset `0x0d`.
   [Sega sound-board source](https://github.com/mamedev/mame/blob/cff1e78194319737798cf24f2e106ae3e34222c1/src/mame/shared/segam1audio.cpp).
   The local counterpart is `src/hw/m1audio.cpp`; catalogue families using
   these ROM regions include Daytona USA, Desert Tank and Virtua Cop.

3. **Manx TT's additional Deluxe sound board uses the same Sega device.**
   MAME's `manxttdx` configuration adds `SEGAM1AUDIO` alongside the SCSP board.
   This does not introduce a YM3413 exception.
   [Model 2 configurations](https://github.com/mamedev/mame/blob/cff1e78194319737798cf24f2e106ae3e34222c1/src/mame/sega/model2.cpp).
   The local catalogue retains its additional audio ROM regions, and the
   machine's existing Manx TT board handling is outside this review's changes.

4. **The SCSP already has its own effects DSP in this core.**
   `src/hw/scsp.cpp` accepts coefficients and microprogram writes, feeds samples
   to `ScspDsp`, steps it and mixes its effect outputs. Its state is serialized.
   The YM3413 addition does not replace or complete that existing DSP path.

5. **The new MAME YM3413 implementation has documented accuracy limits.**
   Its source lists assumptions about arithmetic, program alignment, memory
   latency and serial channels, and explicitly records that output has not
   been verified against the real chip. Reference-model impulse-response
   agreement in the commit is not hardware-output validation.
   [YM3413 implementation](https://github.com/mamedev/mame/blob/cff1e78194319737798cf24f2e106ae3e34222c1/src/devices/sound/ym3413.cpp).

## What Would Justify Integration

Before implementation, identify a supported board with the physical device,
its clock, delay RAM, audio routing and control connections. Then establish
how its firmware supplies the DSP microprogram, coefficients and effect levels.
These may be uploaded by existing firmware; a separate program ROM must not be
assumed necessary without evidence.

An applicable integration would keep the device frontend-neutral, add its
machine wiring and serialization, compare arithmetic with the pinned MAME
reference, then validate the affected game's audio and Save State behavior.
Adding a preset reverb to the current stereo output would instead be a new
audio effect with no established hardware basis for these boards.

## Verification And Limits

- Read the originating MAME patch and pinned TG100, YM3413, Sega audio-board
  and Model 2 configurations; searched the MAME repository for YM3413 users.
- Inspected the local MultiPCM, M1 audio-board, SCSP DSP and game catalogue paths.
- Source copies are retained in
  `/private/tmp/sm2-ym3413-review-20261019/`; the originating patch is retained in
  `/private/tmp/sm2-mame-review-20261019/d65391dcfab3.json`.
- No physical Sega board or manufacturer schematic was inspected. MAME's
  configured devices provide implementation evidence, not exhaustive hardware
  certification.
- No runtime change was made; compilation, gameplay and audio retesting were
  unnecessary for this documentation-only assessment.
- No commit, push, release or installed-core update is included.

The next implementation candidate remains Dead or Alive's real protection
algorithm, subject to its own applicability and integration review.
