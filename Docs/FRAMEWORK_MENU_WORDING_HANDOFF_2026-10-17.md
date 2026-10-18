# Framework Menu Wording Handoff — 2026-10-17

## Reason

The SM2-Emu F14 integration appended game-specific text to the shared Linked
Cabinets help. Its earlier registration audit captured all comments but did not
assert full-text equality. This missed the user's established unified-menu
wording contract. The Power Sled help also exposed raw ROM-set identifiers;
Virtual On had the same class of wording defect.

## Corrected SM2 Contract

All 32 supported Linked Cabinets registrations now use exactly this help:

> Select the total number of linked cabinets, including a Relay where supported. Disabled disconnects optional communication boards or keeps required boards in local loopback; it does not change the selected native role. Supported totals and role combinations depend on the game. Effective changes reset automatically when returning to the game.

Per-game topology stays in the project documentation and available values. The
unsupported placeholder keeps its distinct no-effect help. All 32 supported
Auto Network Role Settings registrations retain their existing identical help.

The current ROM-free Save RAM check asserts equality across all supported
Linked Cabinets definitions. The actual V2 registration audit at
`build-libretro-gpu/validation/linked-help-20261017/audit.json` covers 452
options, 32 linked definitions, 32 role definitions and raw identifier scans
against all 88 catalogued ROM sets. The legacy registration has the same 32
Linked Cabinets and role labels.

## Framework Follow-Up

1. Reconcile Menu Review Order 035 against F14 using one common Linked Cabinets
   comment for each applicable core. Record actual hardware differences in the
   relevant core documentation; do not regenerate per-game help suffixes.
2. Correct the reviewed wording typos at Order 077, Manx TT Cabinet Audio:
   `from the select cabinet configuration` -> `based on the selected cabinet
   configuration`; and Order 084, Crosshair Style: `lightun` -> `lightgun`.
   These two corrections are already applied in SM2's registered Core Options.
3. Add a full registered-help equality check to future cross-core wording
   reviews. Counting registrations or comparing only a shared prefix is
   insufficient.

This is a wording and review handoff. It does not request changes to other
cores' behavior, values, roles or networking topology.

## Implementation Feedback For Other Cores

The defect was introduced after the earlier wording review: the F14 network
integration appended per-game suffixes at option-registration time. The audit
counted registrations and collected their strings, but did not compare the
complete registered help against the reviewed text. A source-level search of
the common prefix was therefore insufficient. The old C++ check expected the
suffixes and unintentionally protected the divergence.

For an equivalent option in another core, review the *final registered* V2
definitions for every supported game, not only the template or generator:

- Compare the complete name, help, raw values, displayed value labels, order
  and default against the current Framework contract. Require identical text
  for identical behavior; document real hardware or lifecycle differences.
- Check all applicable game registrations, including dynamically constructed
  definitions. Keep explicitly different unsupported/no-effect placeholders
  separate from the supported group.
- Scan registered user-facing strings for raw ROM-set identifiers and stale
  reviewed wording. Test the legacy registration's labels and values where its
  API does not carry help text.
- Run this audit again after integration work that changes option construction,
  even if an earlier menu review passed. Assert the desired reviewed wording;
  do not encode generated per-game suffixes as expected results.

These are adoption candidates for TGPulse-Next and Supermodel only where they
have equivalent dynamically registered options. No evidence in this handoff
establishes that either core currently has the SM2 wording defect.
