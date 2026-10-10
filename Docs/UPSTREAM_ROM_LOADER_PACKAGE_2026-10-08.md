# Upstream ROM Loader and Game Support Package — 2026-10-08

## Imported Changes

Selected upstream revisions:

- `600f1c87f8486c2494ff6c11fabeac431d568a4f`: split Model 1 I/O firmware metadata and compatible missing-file diagnostics.
- `e8d96c114b3654f86bce72ae3cfbfa42d3039c27`: preliminary Power Sled definitions, Model 2B port-E input and link-frame offset, standalone cabinet buttons.

The complete integrated baseline remains `5ddf84ae7970a9bce1d0a17b3900d26065de1996` (0.9.13). These are selective backports, not a baseline update.

Daytona and Desert Tank now declare the `model1io` device archive. Their other XML definitions, including digital/analog I/O and ROM regions, compare identically with the previous database after removing the new device reference. Virtua Cop already declared `model1io2`; its explanatory comment is corrected. Clone inheritance supplies the corresponding metadata.

Device firmware precedence remains **frontend system directory, sibling device archive, embedded game/parent chip**. Parent game archives are searched beside the content, never in the system directory. Upstream's optimization that skips device archives when embedded firmware is complete is intentionally adapted: it would override the port's established system-BIOS preference. Missing-device warnings are now emitted only when game/parent chips are incomplete. Required missing chips still fail during assembly. No selector is necessary.

## Power Sled

The catalogue grows from 84 to 87 sets with `powsled`, `powsledm` and `powsledr`. Upstream ROM definitions and Relay-program patches are retained verbatim. All remain `preliminary="true"`, and the loader retains its preliminary warning.

The `Special: Power Sled` profile recognizes the parent/clone family only with the expected Model 2B board and accelerator/brake mux signature. One RetroPad exposes the upstream cabinet controls:

| RetroPad | Cabinet Action | Hardware |
| --- | --- | --- |
| South / B | P1 Entry | IN1 0x01 |
| East / A | P1 Call | IN1 0x02 |
| West / Y | P2 Entry | IN1 0x04 |
| North / X | P2 Call | IN1 0x08 |
| L1 | Cancel Error | IN0 0x80 |
| R1 | Cancel Network Check | IN3 0x02 |
| R2 Analog | P1 Right Handlebar | Analog Channel 1 |
| L2 Analog | P1 Left Handlebar | Analog Channel 3 |

The upstream patch only provides P1 analog handlebars; P2 Entry/Call do not imply complete two-rider controls. Cabinet-wait cancellation does not establish linked-cabinet functionality.

The machine reuses the existing `Inputs::in3` member introduced for Air Walkers. No field is added or reordered and no Save State layout changes. Port E is changed only for Power Sled, and its link frame offset is 0x180 as upstream specifies. No Core Option, default, stored value or visibility rule changes.

## Verification

Evidence: `/tmp/sm2-loader-package-20261008/`. ROM data and generated output stay outside Git.

| Check | Result |
| --- | --- |
| macOS core, headless and standalone | Builds passed |
| Linux x86_64 core | Build passed with existing toolchain/dependencies |
| Input checks on macOS and Linux | All 87 recognized sets; Power Sled six individual digital bindings, handlebar mux endpoints, release and descriptors passed; existing profiles passed |
| Synthetic device-BIOS checks on both platforms | System/sibling/embedded precedence, renamed split archive identification, required missing firmware rejection, clone inheritance/parent fallback and system-directory parent exclusion passed |
| Existing Daytona, Desert Tank and Virtua Cop, 600 frames each | Previous and updated core images/complete PCM identical |
| Real split firmware, same three games, 600 frames each | BIOS extracted into isolated system archives; images/complete PCM identical to embedded sets |
| All three Power Sled variants, Libretro ABI | Loaded and advanced 600 frames |
| Pristine `e8d96c1` versus adapted headless, Power Sled and Master | 1,800 frames each; exact software video, complete PCM, CPU state/cycles and NVRAM agreement; PCM is silent in these boot sequences |
| Installed core, actual RetroArch 1.22.2, Vulkan 2× | 2,300 frames, 16,576-byte Save RAM, clean exit; captured screen reads SYSTEM SHUTDOWN and PCM is silent. Runtime rendering is verified; gameplay is not |
| Power Sled Save State | Full runner round-trip/replay/corruption checks passed on `powsled` |
| Master/Relay Save State | Immediate restoration succeeds, but three-frame replay differs in 15 machine bytes; previous core with the new metadata also diverges (11 bytes). Existing limitation is recorded for further analysis; determinism is not claimed for these variants |

The pristine reference was extracted without source edits, built as a standalone application, and uses the exact selected revision's verified submodule pins. It contains intervening upstream changes, so a future discrepancy would require separating those changes from adapter behavior. The tested boot sequences agree exactly. This is boot/reference evidence, not complete gameplay or linked-cabinet proof.

## Local Installation

Both local RetroArch cores and the external `system/sm2-emu/games.xml` were atomically replaced with backups and hash verification.

- Core SHA256: `9b888e25994d82809998eeebfe6fa37f78995d9bb7b29b43572d5fab848c96c3`.
- Database SHA256: `43e642f32be6a56f1095e696e355076025c5abcdc553f355925b5eddaaecb769`.

`smoke-retroarch.py --power-sled-inputs` adds a bounded cabinet-button/handlebar replay. It accepts silent PCM for this explicitly preliminary scenario while still checking audio capture duration; it does not establish working sound.

No TGPulse changes, commit or push. The adjacent mainstream checkout remains clean.
