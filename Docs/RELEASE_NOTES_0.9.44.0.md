# SM2-Emu Libretro 0.9.44.0

This release corrects the numbering of 0.9.13.1 to follow the agreed convention:
**reconciled upstream version + port revision**. Runtime metadata, core-info,
release tag and current documentation now identify 0.9.44.0.

There are no new emulation, audio, input, NVRAM or Save State changes relative
to 0.9.13.1. Existing saves and options retain the same compatibility. The
previous release remains available as historical publication; its tag is not
rewritten. The feature summary is in the [0.9.13.1 notes](RELEASE_NOTES_0.9.13.1.md).
Their statement that upstream coverage remained at 0.9.13 is superseded here.

## Reconciled Upstream Coverage

Historical full-source import: `5ddf84ae7970a9bce1d0a17b3900d26065de1996`
(0.9.13). Current reconciled upstream: `7db71083ac3419b0c17af74bc6a1640365226238`
(0.9.44). A whole-tree merge is not required by the version convention.

- CPU/i960, SHARC and MB86235 changes, bus/texture waits, sound 68000 timing,
  SCSP corrections, MultiPCM and DSB2 fixes are integrated or adapted; the
  original sound balance and rounding conflicts retain approved selectors.
- GPU texture warping, geometry, shadows and applicable video changes are
  integrated; frontend presentation and resolution conventions remain Libretro.
- ROM loader/split BIOS support, Power Sled, controls, gun mappings, rumble,
  gun-shot-flash control and applicable state changes are integrated or adapted.
- Gun aim/reload conflicts use the approved core mappings/selectors and reload
  policy. v0.9.44 steering deadzone ownership stays in the frontend; synthetic
  cornering rumble uses processed input and the approved minimum threshold.
- Standalone SDL/ImGui menus, localization, window/display/device management,
  gamepad remapping, wheel configuration and wheel force-feedback controls are
  excluded or fulfilled through the frontend. Cabinet-output protocols without
  a supported Libretro destination are excluded. Upstream merges and standalone
  version/build changes do not create an unresolved core feature.

The integration ledger and evidence links are in sections 7 and 9 of
[the roadmap](../PORTING_PLAN.md). Dated package reports describe their original
validation snapshot; their historical 0.9.13 source base is not the current
advertised upstream coverage. Required dependency pins are unchanged.

## Publication Checks

The preceding release passed local ROM-free checks and the five-platform CI.
This release rebuilds the core and packages with matching 0.9.44.0 metadata;
CI repeats its existing ABI, input, audio, Save RAM, Netpacket, rumble and
catalogue checks. Compilation does not claim new gameplay qualification.
Packages contain matching games.xml, core-info, source commit, licences and
checksums, without ROM archives or private recordings.
