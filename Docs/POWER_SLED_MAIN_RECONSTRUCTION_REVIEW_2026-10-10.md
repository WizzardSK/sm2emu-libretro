# Power Sled Main Program Reconstruction Review

## Conclusion

A Slave-derived Main has now been prepared and validated in a bounded paired
RetroArch experiment. It reaches advancing races and retains audio and the
Relay camera. The comparison establishes feasibility, with no demonstrated
improvement over the functioning Relay-derived Main. The present implementation
already combines Relay-derived i960 code with the matched Slave audio program
and samples. Retain that production baseline. The missing factory Main ROM is
not reconstructed or authenticated by this experiment.

## Source And Retained Program Evidence

The current database applies the same three Main changes as MAME:

| Relay Program Offset | Original | Main | Meaning |
| --- | --- | --- | --- |
| `0x1571c` | `0x02` | `0x01` | Initial mode written to `0x00529429` |
| `0x1584c` | `0x88` | `0x89` | Construct role `0x0200` instead of `0x0100` |
| `0x1585d` | `0xfe` | `0xfd` | Complement of the role |

The retained Main and Relay CPU region dumps differ at exactly these three
bytes. Both full 2 MiB regions and the Slave region were read from the existing
private target-core diagnostic evidence, without launching an emulator:
`build-libretro-gpu/validation/power-sled-native-io-20261009/`.

| Program | CPU Region SHA-256 |
| --- | --- |
| Slave | `5c3c307f68098b1e74577a8c4de1660c9e2883ba2080f971dda867655e40f44a` |
| Relay | `b90bab4c013732329c6decc7b655ba5d04610ea65e90eb16bf794a390fe39792` |
| Current Main | `44000ec5f9a4f3f77805529627a9fb45d8755de65c762d50cfa20a6c9b3af422` |

Instruction decoding reuses that directory's diagnostic `disasm.py`, based on
the local MAME i960 mnemonic definitions. These are static findings; no new
runtime or factory-cabinet equivalence is claimed.

MAME's current source still identifies Main as an undumped program approximated
through Relay patches:
[Model 2 Driver](https://github.com/mamedev/mame/blob/master/src/mame/sega/model2.cpp).

## Slave Comparison

- Both programs initialize the mode byte at `0x1571c` with the same instruction.
- Their role initialization functions at `0x15840` differ: Relay forces
  `0x0100`; Slave reads its operator identity, writes that role and its
  complement, and uses a different sequence for the related local index.
  Applying the existing three Main patches blindly to Slave would overwrite
  different instructions and operands. A Slave candidate needs its own
  validated initialization adaptation.
- Each region contains 79 candidate absolute memory instructions referencing
  the role word at `0x005293f0`. Apart from the differing initialization store,
  all corresponding instruction locations match: unchanged addresses before
  initialization and a 16-byte shift in Slave afterwards. This is a reference
  map, not proof that every surrounding function is equivalent.
- Relay's operator decoder `0x000bd4c0`–`0x000bd56f` and Slave's
  `0x000bd4b0`–`0x000bd55f` are byte-for-byte identical. Both accept role
  `0x0100` or `0x0200` and emit the operator commands already qualified in
  RetroArch, including command 5 for race start.
- The database uses identical shared data, polygon and texture ROMs for the
  three programs. Slave audio is already integrated on Main with CRC-checked
  local-first, parent-fallback loading.

The original `THIS IS ????????` startup label is also explainable from static code:
the renderer recognizes Relay `0x0100` and rider identities 0–3, but has no
dedicated label for Main `0x0200`. Both programs contain this same label logic.
This label alone does not prove communication corruption or explain the
mandatory Silver Ride check.

The subsequent Main-only caption correction reads the operator's NVRAM color
in both identity selectors, preserving the separate Main role. See
`Docs/POWER_SLED_MAIN_RIDE_CAPTION_2026-10-10.md` for implementation and
Silver/Red/Black RetroArch evidence.

## Practical Direction

Retain the functioning current Main as the baseline. Compare any proposed
correction against a specific defect: operator identity, initialization,
network role or missing audio event. The Slave-derived candidate can preserve
its rider program/audio while setting Main mode and role through an adapted
initializer; it must also account for the role complement and local index.
Whole-function transfers between programs need relocation analysis because
code addresses differ. A broad merge has no demonstrated advantage yet.

If pursued, use the existing RetroArch recipe to compare startup, operator
selection, Main/Slave race progression, Relay camera, audio commands and saved
state integrity. Start with one paired baseline/candidate observation rather
than a new acquisition campaign. The original Main's fidelity remains
unverifiable without its ROM or independent hardware documentation.

## Completed Slave-Derived Experiment

Private evidence root:
`build-libretro-gpu/validation/power-sled-main-reconstruction-20261010/`.

### Extended Program Comparison

`relocation-review.json` compares aligned 32-bit words before the initializer
and after its different-sized body. Before the initializer, 21,985 words match;
47 differences correspond to absolute ROM pointers or control displacements
shifted by 16 bytes. Afterwards, 498,256 words match; 3,976 differences follow
those same relocation patterns. Four remaining differences are the transition
between populated ROM and the region's trailing fill, at Relay offsets
`0x100000`–`0x10000c`. The initializer is inspected separately. No additional
non-relocation difference emerges in these compared ranges.

This comparison and the shared operator decoder support using either base;
they provide no evidence of extra Main logic exclusive to Slave. They are not
a formal proof of every possible execution path or of factory fidelity.

### Candidate Initialization

`prepare.py` checks the exact original Slave initializer and ROM chip CRCs,
then creates a private `powsledm` definition using Slave CPU chips. It sets
Main mode and adapts role initialization to the current Main semantics:

- Preserve the Slave settings-helper call.
- Read the same signed operator field used by current Main for the local index.
- Set native role `0x0200` and its complemented value.
- Subtract one for the local index and write it to `0x0053e6f4`.

The final index store and return use the preceding 12-byte, zero-filled gap;
a branch links that tail to the initializer. The next Slave function entry at
`0x15870` and all subsequent bytes remain unchanged. The private XML applies
15 guarded word patches after CRC-checked assembly; archived chip contents are
not patched. `candidate-initializer.txt` retains the decoded instructions.

`baseline/` and `candidate/` have separate private assets, thin Main archives,
save directories, logs, audio and captures. Slave and Relay ROMs are referenced
read-only. The candidate identifies as `powsledm`, rather than silently falling
back to the complete Slave set. Both variants use the same installed core,
initial save fixture, options and previously qualified Manual input movies.

### Paired RetroArch Results

One bounded run per variant uses the existing linked-cabinet runner with a
95-second observation and three capture rounds. Images are not frame-aligned,
so the comparison does not assert pixel equality or infer speed differences
from differing timer values.

| Variant | Main Timer, First → Third Capture | Slave Timer, First → Third Capture | Relay | PCM Peaks, Main / Slave / Relay |
| --- | --- | --- | --- | --- |
| Current Relay-Derived Main | 42.28 → 31.43 | 41.98 → 31.33 | LIVE 1P | 5651 / 6263 / 3330 |
| Slave-Derived Candidate | 45.77 → 35.13 | 45.58 → 35.05 | LIVE 1P | 6001 / 5288 / 3337 |

Both Main and Slave show advancing race views and position 1. The candidate
also shows Time Extension. PCM peaks establish nonzero frontend output, not
matched sound events, music completeness or acoustic fidelity.

`runtime-review.json` validates all six instances: native links and roster,
normal exits, no forced kills or residual processes, no runtime i960 reset,
replay active through shutdown, and valid SRAM identity, container CRC and
three-copy ANS values. Calibration fields and EEPROM match between variants.
The source baseline, installed core and system database remain unchanged.
The initial review assertion incorrectly included the normal replay-ended
message after network shutdown; it was corrected to check ordering, as in the
established review. Neither runtime session was repeated for that reviewer fix.

The experiment is complete. A base replacement offers no demonstrated benefit
and shifts code addresses, which would require separate saved-state
qualification if ever adopted. Future work should target an observed Main
defect or new original-hardware evidence. No further test is required to close
this feasibility comparison.

Only private diagnostic assets and documentation are added. User ROM archives,
installed cores, emulation source and user saves are unchanged. No commit or push.
