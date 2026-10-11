# Power Sled Initial Calibration Defaults

## Approved Source And Scope

The user requested the currently saved calibration as the new initial default.
The current `powsledm.srm` container was validated for identity, size and payload
CRC and copied to ignored local evidence before editing. Its three native
28-byte settings copies agree. Relative to the qualified initial image, the
only changes in that block are its first eight calibration endpoint bytes:
`FF 00 FF 00 FF 00 FF 00`.

The committed source record `data/power-sled-calibration-defaults.json` pins
these bytes and the source SRM SHA-256; the complete user save stays outside Git.
The common endpoint layout is shared by Main, Slave and Relay. The native
settings-copy layout and whole-block agreement mechanism were already qualified
in `POWER_SLED_NVRAM_INTEGRITY_2026-10-09.md`. This is the explicitly authorized
calibration-default change, separate from the excluded calibration campaign.

## Established Initialization Path

The existing `generate-power-sled-nvram.py` generator applies only these eight
bytes at each of `0x000`, `0x100`, `0x200` to each independently qualified initial
image, then recompresses and recalculates its template CRC. Regeneration retains
the approved calibration automatically. Operator settings, bookkeeping and
EEPROM retain their independent original images.

This uses Automatic Initial NVRAM Setup and its existing first-initialization
policy, matching the reference TGPulse-Next initial calibration policy. A valid
frontend save has priority; native save files also suppress initial seeding.
NVRAM Settings operator overrides do not overwrite calibration. No new option
or read-time migration is introduced. Saved user calibration remains intact.

## Verification

All three decoded templates differ from their qualified baseline only at the
24 endpoint bytes. Their payload CRCs validate, their three settings copies
agree, and existing operator defaults are preserved. The save-RAM checks verify
initial endpoint bytes on each set and preservation through all operator edits.
Evidence: `build-libretro-gpu/validation/power-sled-calibration-defaults-20261011/`.
This does not newly qualify physical cabinet mechanics or gameplay response.

The normal local RetroArch core was rebuilt and installed with backup and hash
verification: `08774535d6bb2052b67d862c76ad3940832ee825aa8ad26714d308d987591bba`.
The user source save is byte-identical after deployment. No dev copy, commit
or push. Account meter moved from 5% to 6% (integer-rounded), within the 35%
cap; reset 2026-10-18 07:47 Europe/Rome.
