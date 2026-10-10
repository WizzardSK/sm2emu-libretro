# ANS Convention And Game-List CLI Review

## Contract

Automatic Network Settings has one raw convention: `0` Disabled, `1` Master,
`2` first Slave, subsequent sequential numbers for other cabinets, and `relay`
for Relay. Menus keep descriptive labels. Power Sled Main and Slave use
`1` Silver, `2` Red, `3` Black. Its dedicated Relay offers only `relay`, with no
color override. Virtual On's dedicated Relay likewise offers only `relay`,
retaining native No Link. Defaults are `0` for Power Sled playable programs,
`relay` for dedicated Relay programs and `1` for other supported linked games.

As directed by the user, old development ANS values are neither accepted nor
migrated. Native NVRAM keys/values, other published option compatibility,
communication, emulation and save formats are unchanged.

The launcher supports all three forms:

```sh
--game daytona
--game vonj,vonu
--game daytona:1,daytona:2
```

One name repeats the same ROM. A list selects each instance's ROM. A suffix
sets ANS without changing the ROM name and takes precedence over saved values.
The Power Sled triplet is explicit:

```sh
--game powsledm:2,powsled:1,powsledr:relay --controllers 0,1,2
```

The script performs no game compatibility checks, required-program validation
or per-game cabinet-limit validation. It passes the requested names and values
to the core/frontend. A recognized Power Sled Main/Slave/Relay triplet gets the
native transport order and dedicated window layout; bare names remain literal.
Unknown-to-the-runner ROM names are also passed through with generic presets.
The historical network qualification runner retains its separate test gates;
launcher runs use explicit ROM lists and report process lifecycle separately
from observed native links. They do not turn a core connection rejection into
a script compatibility policy.

## Verification

- Core build and Save RAM checks pass. Every canonical registered ANS value
  is accepted; old textual names are rejected. Native role/color mappings,
  reviewed managed fields and dedicated Relay behavior are checked directly.
- Four ROM-free launcher checks pass: literal repeated names, per-instance
  selection, colon parameters, ignored Power Sled Relay flag and malformed
  syntax. Mixed and unknown-to-the-runner game names are accepted.
- Five dry-run configurations verify the three CLI forms, generic Relay,
  Power Sled and `0` Disabled. Additional KISS dry-runs pass mixed
  `daytona:1,stcc:2,vf2:0`, literal repeated `powsled` and three repeated `von`.
- An explicit `powsledm:2,powsled:1,powsledr:relay` dry-run resumes the successful
  session and overrides saved ANS values. It does not re-acquire NVRAM samples.
- One actual installed-core RetroArch session with the new `:ANS` syntax
  verifies Main Silver, Slave Red and Relay, all three native links,
  Main / Slave above Relay and clean Ctrl+C exits without forced cleanup.
  SRAM container CRC and all three Ride copies pass. Global configuration
  remains byte-identical and the temporary macOS preference is restored.
  The subsequent removal of script compatibility policies is checked through
  generated configurations; no unrelated games were launched for that change.

Evidence is retained under
`build-libretro-gpu/validation/ans-convention-20261009/`:

| Artifact | Evidence |
| --- | --- |
| `deployment.json` | Both installed core paths and final hashes. |
| `cli-review.json` | Five generated ROM/ANS mappings. |
| `kiss-review.json` | Mixed/literal lists and explicit values overriding saved colors. |
| `runtime/runs/0001/cabinets/result.json` | Actual three-instance frontend/native link and exit records. |
| `runtime-review.json` | Native Ride copies, positions, CRC and configuration/preference assertions. |

Final core SHA256:
`2ba119449eb4fd5400c0f52cd5cd5c111c09a5615fe6fa70e6984403ae150f61`.
Both established macOS installed copies, `sm2_libretro.dylib` and
`sm2_dev_libretro.dylib`, match this build; backups are retained. The change
requires no games.xml or native-template update.

Playable Power Sled racing, steering, physical/background controller delivery
and subjective audio remain unverified. Existing preliminary-game limits are
unchanged. No changes to another project, commit or push were made.

## Launcher Correction — 2026-10-10

The earlier Silver-Main/Red-Slave link-only test did not qualify native startup
or gameplay. The recommended launch and fresh-session defaults are corrected
to Main Red / Slave Silver. Explicit ANS color meanings are unchanged. The
launcher now orders Main / Slave / Relay and gives Relay its own `_relay`
folder. See `POWER_SLED_LAUNCHER_CORRECTION_2026-10-10.md` for current evidence.
