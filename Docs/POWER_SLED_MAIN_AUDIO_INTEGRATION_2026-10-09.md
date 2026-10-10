# Power Sled Main Audio Integration — 2026-10-09

## Implemented Behavior

The Main `powsledm` definition uses the matched rider sound board:

| Region | File | CRC32 |
| --- | --- | --- |
| Audio CPU | `epr-19466.31` | `c42892a5` |
| Samples | `fpr-19459.32` | `a424743f` |

Each file is looked up in the Main archive first. Only missing required chips
cause the existing loader to open the split parent `powsled.zip` or `.7z` beside
it. CRC verification remains enabled. The old Relay files EPR-19467 and
FPR-19460/FPR-19461 are removed from the Main definition and are not requested
for Main identification or loading. Relay keeps its original sound regions.

A known archive name now selects its definition when every declared maincpu
chip matches by CRC. This preserves Main recognition for existing
`powsledm.zip` archives whose old audio chips are unused. If the name is unknown
or its program chips do not match, the existing complete-set scoring applies.
Explicit preferred-game selection keeps precedence. Main and Relay share
program chips, so a renamed archive containing their common Relay chips cannot
be distinguished as Main purely from that program; use the Main set name or
explicit preferred-game selection when the distinction matters.

The change reuses normal parent lookup and assembly. No new metadata fields,
Core Options, roles, operator automation, i960 patches, sound-engine branch or
frontend callback is added. Original ROM archives are read only and never rewritten.

## Verification

The extended ROM-free loader checks cover:

- Original Main program recognition despite missing corrected audio locally.
- Parent sound fallback and preservation of the Main program patch.
- Local corrected audio loading without old Relay chips or a parent archive.
- Local corrected audio precedence over a corrupt parent.
- Rejection of absent/corrupt required parent chips by CRC, with no silent
  fallback to unsupported Relay audio.
- Unchanged Relay audio and rejection of filename preference for the wrong
  program chips.
- Existing system/sibling/embedded BIOS, explicit-selection and renamed-content
  checks.

The normal macOS Libretro core and frontend-free headless target build.
Installed-core RetroArch runs Main/Relay/Slave using the original user archives
and deployed production metadata. Main loads as `powsledm`; its log confirms
parent `powsled.zip` fallback. Main and Slave show the race timer, position and
course. All units pass native links, clean exit and SRAM identity/CRC; all
three copies of Main Red / Slave Silver remain valid. No forced kill or owned
residual process remains.

Recorded PCM peaks in Main / Relay / Slave order are **4391 / 3033 / 4309**.
Main audio remains active in the final ten seconds: peak 2120 and 880140
nonzero channel samples. This establishes output through the actual frontend
during the race observation, not original-cabinet sound fidelity or physical
controller behavior.

Evidence root:
`build-libretro-gpu/validation/power-sled-audio-integration-20261009/`.
The exact command, recipe, original source snapshots, loader gate log,
screenshots, PCM, SRAM, result, deployment backups/hashes and `review.json`
are retained. No diagnostic native tracing is present in this runtime core.

## Deployment and Remaining Limits

Both local RetroArch core copies are updated, as are the configured external
SM2 system database and the Library fallback database. SHA-256:

- Core: `6832b2952b4689bc2e366f7dcb3e97c97da314c4ff14d69c3c0d85db0a14ced4`.
- games.xml: `8b07fd0041ce5aeed55ee325db44da74fff57ec6469ce8a28c971a46648d8f19`.

The normal change uses the existing Slave sound content for the undumped Main
approximation, as established by
`Docs/POWER_SLED_MAIN_AUDIO_DIAGNOSIS_2026-10-09.md`. Authentic original Main
sound content, subjective listening and complete race sound events remain
unqualified. The SRAM layout and Save State writer are unchanged; audio from
Main Save States predating the sound-ROM change has not been qualified.
Physical handlebars and complete-race qualification remain in the preliminary
support activity. No calibration, NVRAM sample acquisition, commit or push.
