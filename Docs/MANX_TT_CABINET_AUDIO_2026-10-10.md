# Manx TT Cabinet Audio

Date: 2026-10-10
Scope: Cabinet Audio Selection And Additional Deluxe Sound Board

## Approved Policy

`Manx TT Cabinet Audio` (`sm2_manxtt_cabinet_audio`) is always visible in Audio,
with Enabled / Disabled and Enabled as default. It affects only `manxtt`,
`manxttc` and `manxttdx`. No new game variants or modified ROM archives are
created. The selected main program, set identity and save names remain intact.

For Revision C/D, Enabled follows the actual committed EEPROM Cabinet Type:
byte `0x0a`, 1 Twin / 0 Deluxe. The existing native length and inverted CRC
validation must pass before a change is accepted. Partial Service Menu EEPROM
writes do not trigger a sound-bank change. The setting is read after frontend
save import, automatic initialization and pending NVRAM Settings overrides.
The adapter never changes the EEPROM itself. Disabled uses the selected set's
original SCSP program and samples.

| Effective Configuration | SCSP Program / First Sample | Additional Board |
| --- | --- | --- |
| Twin | EPR-18826 / MPR-18827, from the `manxttc` definition | Disconnected |
| Deluxe, Revision C/D | EPR-18924A / MPR-18763, from the `manxtt` definition | Connected when its ROMs are available |
| Original Deluxe `manxttdx` | Its original SCSP program and samples | Always connected when available |

The auxiliary board follows the effective cabinet independently of whether
alternate SCSP selection is enabled. The C-main/Deluxe-audio and
D-main/Twin-audio combinations are compatibility reconstructions, supported by
the command-table comparison; no factory dump of those pairings is claimed.
See [documentary provenance](MANX_TT_AUDIO_DOCUMENTARY_REVIEW_2026-10-10.md).

## ROM Lookup And Missing Files

The generic region loader searches the selected archive first, then adjacent
`manxttc`, `manxtt` and `manxttdx` archives, accepting `.zip` and `.7z`.
Only the requested sound regions are assembled using the existing loader;
the donor's main program, communication firmware and EEPROM are not loaded.
Every declared sound chip must be present. Expected catalogue CRCs are checked
even when the general diagnostic ROM-verification option is disabled. A
zero-filled optional region is not treated as an available board.

Incomplete alternate SCSP audio retains bank zero (the selected set audio) and
produces a frontend notification. Missing additional sound ROMs keep that board
disconnected and produce a notification when Deluxe is requested. Available
ROMs are assembled once at content load; reload content after adding archives.

## Frontend-Neutral Hardware Changes

`Model2Sound` supports three ROM banks and an optional existing `M1Audio`
instance. The host UART feeds both SCSP MIDI and the connected M1 receiver;
the latter's transmitter returns through the existing host RX handler, matching
MAME's `model2a_state::manxttdx` connection. The optional board is clocked only
while connected. Its single populated MultiPCM and YM3438 reuse their existing
emulation and Gain controls. MultiPCM 2 is not advertised as a populated source.

M1 output is mixed into the 44,100 Hz stereo stream with linear interpolation,
using the exact native 25 MHz / 560 rate and a 32-source-frame initial buffer.
This avoids cumulative drift from the rounded M1 sample-rate integer. Existing
native chip mixer gains are retained; no independent speaker reconstruction is
claimed. Reset clears both board and resampler histories. Switching a sound
bank resets sound hardware, leaving main CPU, inputs and NVRAM unchanged.

Save State format 9 stores ROM-bank identity, auxiliary CPU/chips/UART,
connected state and resampler phase/queue. Formats 4–8 remain readable; they
contain no additional-board history. A state requiring an unavailable ROM bank
or board is rejected, allowing the existing whole-machine rollback to restore
the previous state. ROM data and callbacks are not serialized.

## Validation

The focused ROM-free checks cover:

- ROM-bank selection and missing-bank rejection.
- Serial delivery only to a connected board and the unpopulated second PCM.
- Nonzero auxiliary synthesis reaching mixed output and MultiPCM Gain Mute.
- Sample-exact CPU/PCM/resampler continuation after Save State restoration.
- Format-8 sound-state loading.
- CRC-correct sibling lookup despite a wrong same-name chip in the main archive.
- Missing optional chips preventing an unavailable donor from being selected.
- Saved Twin selection, uncommitted EEPROM writes ignored, committed Deluxe
  selection, disabled adaptation and unchanged EEPROM bytes.

The standard audio and device-ROM checks also pass. Three 180-frame Libretro
ABI cases (Twin, Deluxe and VF2) pass deterministic Save State, three run-ahead /
rewind cycles and corrupt-state rollback. A real format-8 VF2 snapshot generated
by the preceding installed core loads in a fresh format-9 process. Additional
60-frame state gates pass on all four board variants (VF2, Virtual On, Sega
Rally and Daytona); the VF2 old/new audio and video hashes are identical. The
existing NVRAM/Core Option checks pass, including always-visible registration
of the new selector for every catalogue game. The DX-only fixture confirms the
additional board stays connected with adaptation disabled.

The production core's 6,600-frame RetroArch D/Twin replay exits 0 in 113.156
seconds; the log confirms Twin audio, and the final screenshot shows the race
at Time Up. Audio is nonzero. Listening verification is separate from this
automated evidence.

The private Deluxe run also passes 6,600 RetroArch frames, exiting 0 in
114.531 seconds; the screenshot shows race state (position 8/8, timer 21).
Its original program delivers 9,655 host bytes to the additional board, with
19,310 UART reads, 85,211 MultiPCM writes, up to 21 active voices and nonzero
auxiliary samples. The EEPROM remains identical to the Deluxe seed. The mixed
recording has 31 saturated samples out of 9,853,410 (0.000315%); it is not an
acoustic/speaker-layout qualification. This probe retains the previously
qualified motion acknowledgement and observation logs only; production sources
were restored in a finally block and the normal core rebuilt before deployment.

Private evidence is retained under
`build-libretro-gpu/validation/manxtt-cabinet-audio-20261010/` (ignored).

## Remaining Scope

The production Deluxe motion-controller boot prerequisite is now addressed
by the integrated AMS acknowledgement stub, selected by the current native
Cabinet Type for Revision C/D and always active for the Deluxe-only program.
All three Deluxe programs pass a bounded RetroArch boot; Revision D also
reaches a race using the normal production core. This supersedes the private-only
status recorded in the historical audio probe above. See
`MANX_TT_MOTION_STUB_2026-10-10.md` for reset, persistence and deployment evidence.
The native Service Menu Twin/Deluxe cycle and fresh-load persistence are now
qualified on both C/D programs; see `MANX_TT_SERVICE_TRANSITIONS_2026-10-10.md`.
No muting, warning suppression, rate limit, main-program patch or reconstructed
ROM archive is used as the correction. Acoustic fidelity and physical speaker
routing remain outside the bounded software checks.


## Local Installation

Both `~/Library/Application Support/RetroArch/cores/sm2_libretro.dylib` and
`sm2_dev_libretro.dylib` were atomically updated and checked by SHA-256 and ABI
load. Installed production hash:
`39e2a423a07afb2430f1dd9fc9f4a783e5377e6e9c615be0984472e18068b821`.
The authoritative external-system `sm2-emu/games.xml` already matches the
project database (`8b07fd0041ce5aeed55ee325db44da74fff57ec6469ce8a28c971a46648d8f19`)
and required no replacement. The private observation core was not installed.
The subsequent production AMS deployment is recorded in the motion-stub document.
Installation records and previous-core backups are in the ignored evidence
root. Reload the core in RetroArch before testing an already-open session.
