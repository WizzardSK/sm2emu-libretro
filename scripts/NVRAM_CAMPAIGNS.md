# Campagne NVRAM dei cloni

## Power Sled Implemented Options And Initial Images

The approved fields and all three qualified initial templates are implemented.
Generate only their marked data sections with
`python3 scripts/generate-power-sled-nvram.py`; the retained independent-image
qualification manifest is required. Existing game data is preserved.

The separate integration verification reuses the linked RetroArch runner:

```sh
/Users/andrea/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  scripts/test-power-sled-nvram-options.py \
  --output build-libretro-gpu/validation/power-sled-options-20261009
```

Its complete five-stage recipe verifies first-run seeding, manual overrides,
fresh SRAM reload, native-save precedence and SRAM precedence over conflicting
native files on all three programs. Accepted runs are validated before reuse;
failed attempts remain separate. Use a new output when the core or recipe
changes. The runner's optional `--core-options-override` JSON map and
`--native-nvram-baseline` role directories affect only isolated test files.
The original acquisition recipe still disables automatic setup and overrides.
Calibration remains excluded. See `Docs/POWER_SLED_NVRAM_OPTIONS_2026-10-09.md`.

I 27 cloni validati con template dedicato hanno una campagna permanente
`libretro_nvram_samples.<set>.toml`. I risultati restano nel workspace sotto
`build-libretro-gpu/validation/nvram-campaigns`; ROM e risultati non vanno in Git.

La tabella TOML opzionale `[core_options]` permette di disattivare esplicitamente
Automatic Initial NVRAM Setup e NVRAM Settings, conservando i default nativi
nelle acquisizioni. Le campagne precedenti senza tale tabella mantengono il
comportamento originario. Ogni variazione riparte dal baseline del clone.
I suffissi `step-N` indicano N pressioni dal default nativo, senza presumerne
il valore. `cycle-NNN` identifica una ricetta della campagna parent: anche qui
il nome non promette il valore del parent. Le campagne includono i parametri
selezionabili del menu, anche se non sono esposti come Core Options.

## Uso

```sh
python3 scripts/libretro_nvram_samples.py scripts/libretro_nvram_samples.indy500d.toml --dry-run
python3 scripts/libretro_nvram_samples.py scripts/libretro_nvram_samples.indy500d.toml
```

Il catalogo ricavato dagli screenshot e i 57 YAML diagnostici si controllano
con:

```sh
ruby scripts/audit-diagnostic-yaml-catalog.rb
```

Il controllo confronta righe visibili, ordine, default dichiarati e valori
acquisiti. Offset, codifiche e algoritmi d’integrità restano responsabilità dei
singoli YAML e dei controlli Save RAM.

## Sequenze e verifica

Tutte le 27 campagne hanno superato il controllo preliminare del generatore;
è stata verificata anche la disattivazione esplicita dei setup del core.
Non è stata ripetuta l'estrazione: le sequenze derivano dai menu e dalle
acquisizioni archiviati. I cicli completi dei nuovi file non sono tutti stati
rieseguiti dopo il consolidamento.

I binding sono R3=Test e L3=Service; Daytona usa START per selezionare.
HP Password ed Engine Volume Out of Use vengono saltati. VF2 attraversa
INITIALIZE senza selezionarlo. Le campagne terminano uscendo dai menu.
`motoraiddx` conserva l'attesa prudenziale per il prompt Driveboard Error /
Press Test e il doppio Test. In modalità interattiva attendere il prompt
prima delle due pressioni.

## Catalogo

| Set | Campioni configurati |
|---|---:|
| `daytona93` | 12 |
| `daytonas` | 33 |
| `daytonase` | 29 |
| `doaa` | 41 |
| `doaab` | 41 |
| `doaae` | 41 |
| `doab` | 41 |
| `dynamcopb` | 46 |
| `dynamcopc` | 46 |
| `dyndeka2` | 46 |
| `dyndeka2b` | 46 |
| `hotdp` | 29 |
| `indy500d` | 28 |
| `indy500to` | 35 |
| `manxttc` | 60 |
| `manxttdx` | 60 |
| `motoraiddx` | 25 |
| `sfight` | 60 |
| `srallycdx` | 22 |
| `srallycdxa` | 14 |
| `stcca` | 37 |
| `stccb` | 39 |
| `stcco` | 37 |
| `vf2a` | 30 |
| `vf2b` | 30 |
| `vf2o` | 30 |
| `vstrikero` | 11 |

Tutti i cloni dei precedenti 84 set dispongono di una campagna dedicata o di un’eredità parent
verificata. I tre nuovi set Power Sled sono registrati separatamente come acquisizione incompleta. Per `hotdp` i 29 campioni permanenti coprono i valori distinti; due
acquisizioni aggiuntive archiviate confermano il ritorno ciclico Red/Green di
Blood Color.

## Acquisizioni mirate per il catalogo Game Settings

Le seguenti campagne brevi completano la struttura dei menu senza duplicare i
cicli dei valori già acquisiti per i parent:

| Configurazione | Scopo |
|---|---|
| `libretro_nvram_samples.overrevb.toml` | Foundational Setting e Optional Game Setting del clone |
| `libretro_nvram_samples.overrevba.toml` | Foundational Setting e Optional Game Setting del clone |
| `libretro_nvram_samples.vonr.toml` | Test Menu e Game Assignments dopo il timeout della rete Relay |
| `libretro_nvram_samples.rascot2.toml` | Diagnostica SegaNet, avvio locale con Button 1 e ritorno della diagnostica con Test |

I risultati verificati sono archiviati sotto
`build-libretro-gpu/validation/game-settings-gap-fill-20260920`. `vonr` richiede
che il comando Test venga inviato soltanto dopo l’inizializzazione Relay;
`rascot2` non espone un normale menu Game Settings nel percorso acquisito.


## Power Sled Service Menu Documentation

Phase 1 is documented independently for `powsled`, `powsledm` and `powsledr`
in linked MAME: root entry rendering, menu order, eight operator settings per
set, commands, numeric ranges/native Use Default and conditional Ride ID cycles.
The authoritative current inventory is in the three diagnostic YAMLs,
`GAME_SETTINGS_CATALOG.md`, and the Phase 1 workbook tables.
See `Docs/POWER_SLED_SERVICE_MENU_CAMPAIGN.md` for the matrix and evidence.

Phase 2 uses the complete linked recipe described below, generated from the completed
inventory, then collect native committed samples. Earlier saves are exploratory,
not phase completion. Keep Main fixed for Slave color samples. Capture every
small discrete variant; use significant numeric samples only after establishing
the encoding pattern. Calibration menus are listed only. The menu-only phase
uses the existing MAME runner with no Backup RAM snapshots and no Set & Exit;
no sample acquisition is started by that documentation work.

Phase 2 acquisition is restricted to the target core running in RetroArch.
Use `libretro_nvram_samples.py`; do not generate acquisition plans for MAME or
standalone emulators. Reference-emulator saves are not core samples. Keep
Slave/Relay samples pending while their operator pages are unreachable in the
target core; resolve that prerequisite before acquisition.


## Power Sled Linked Phase 2

Phase 1 inventory is complete for the reviewed scope. The Main/Relay/Slave
communication/menu gate is verified in the target core through RetroArch.
The earlier Exit-only target-core report was an incorrect visual interpretation
of identical full-menu PNGs, not an established rendering defect.

Generate the **whole recipe once** from the three completed YAML inventories:

```sh
python3 scripts/generate-power-sled-recipe.py
python3 scripts/generate-power-sled-recipe.py --check
```

Run `scripts/test-retroarch-netpacket.py` with the three distinct ROM programs,
`--set-name powsledm --cabinets 3`, `--operator-recipe
scripts/libretro_nvram_samples.power-sled-linked.toml` and a persistent `--output`.
**Omit `--sample` to execute the complete campaign.** Repeating the same invocation
resumes validated results. `--sample` is only for diagnosing a concrete failure.

The 49-stage recipe reuses the three previously validated Motion stages. It
covers five time fields (native default, increment, lower and upper limits,
fresh reload), Motion limits and the 255/260 stored-word boundary, Country's
stored cycle while the visible label remains Export, and all documented Ride
color mapping with fixed peers and independent initializations. The user
accepted the proven 0/1/2 mapping on Main/Slave as sufficient to move forward;
further ID assignment/conditional-cycle logic is deferred (2026-10-09). Main/Slave cycles
are closed by value-line screenshot feedback (`RIDE_CYCLE(1/2)`, maximum three
native calls), because the observed core cycle can vary even from the same
saved baseline. Relay's visible role and hidden stored byte are kept separate;
fresh reload must preserve the stored byte exactly. Calibration is excluded.

The runner records the entire expanded plan before launch. `campaign.json`
records each stage, source core/recipe hashes, baseline images, sample hashes,
screenshots, validation failures, and which later fresh process verifies each
committed value. Each role keeps its own SRM. It verifies native values against
independently read menu digits/labels, all three redundancy copies, native
three-program link, valid frontend containers and clean process shutdown.

A failed gate stops dependent acquisition. Correct the failure and repeat the
same command: validated unchanged stages are checked and reused; retries get
new evidence directories. Never overwrite failed evidence. A container CRC,
native redundant copies, complete acquisition and a usable initial template
remain distinct checks. Integrity, whole-image suitability, Core Option review
and actual gameplay require their own evidence.

Do not pass `--service-menu` or `--automatic-network` with an operator recipe.
No MAME or standalone execution, reference-save baseline, calibration acquisition
or generated reference-emulator plan is authorized by this workflow.

### One Recipe, One Campaign

After Phase 1 is complete, generate one complete acquisition recipe from its
verified inventory before starting Phase 2. Run that recipe as one campaign,
validating each sample as it is acquired. Use a persistent manifest to record
coverage, validation failures, native commit and fresh reload evidence; resume
from validated results without reacquiring them. Do not substitute ad hoc
single-option probes or arbitrary small batches for the complete campaign, and
do not ask the user to authorize every sample or continuation. Pause only for a
concrete failed validation, missing prerequisite, or an actual user decision.
Fix routine runner failures and resume the same campaign autonomously. Keep
numeric representative sampling and complete small-selector cycles as agreed.

### Power Sled Native Integrity And Initial Images

After the complete field-mapping campaign, run the whole bounded native
integrity recipe through the same linked RetroArch lifecycle:

```sh
python3 scripts/test-power-sled-nvram-integrity.py \
  --output build-libretro-gpu/validation/power-sled-integrity-20261009
```

Use the bundled Python runtime with Pillow where system Python lacks it.
`--dry-run` generates the complete plan without launching an emulator. The
runner retains 11 trials / 33 program records, exact injected copies, matching
SRM container CRCs, native field/recovery checks and fresh-menu evidence.
It resumes validated stages and pins the core hash; select a new output folder
if the core changes. Only target-core RetroArch acquisitions are supported.
Native ROM data is read to identify block lengths, recovery routines and
fallback constants. No acquisition or generated plan runs in MAME. Calibration
menus remain listed only. See
`Docs/POWER_SLED_NVRAM_INTEGRITY_2026-10-09.md` for the limits and the independent
initial-image gate. Payloads and ROM-derived diagnostics stay in the ignored
build directory; no saves or ROMs belong in Git.

## Daytona USA GTX — Approved Inventory And Qualified Acquisition

Independent GTX inventory was acquired in SM2-Emu Libretro/RetroArch on
2026-10-17: ten operator fields and complete cycles, including native network
roles and IDs. See `Docs/DAYTONA_GTX_SERVICE_MENU_2026-10-17.md` and
`data/diagnostic-menus/daytonagtx.yaml`. Eight Game System fields are approved and acquired through the complete recipe below; both credit fields are excluded. A dedicated GTX template and the approved overrides are implemented.

### Review Workbook Row Banding

Use the native table style with row stripes enabled. Do not apply alternating
direct cell background fills; filtering must preserve the table's alternation.
Preserve reviewer edits and distinguish observation, approval and implementation.

## Daytona GTX Approved Campaign — 2026-10-17

Run `python3 scripts/run-daytona-gtx-nvram-campaign.py scripts/libretro_nvram_samples.daytonagtx.toml`
with the bundled Python/Pillow runtime. The whole 58-stage recipe resumes only
validated stages from its pinned core/recipe manifest. It captures all 28 values
of the eight approved Game System fields, each followed by native commit and
fresh-process visible reload. Boot diagnostic screens cannot qualify as menu
evidence. Keep attempts, raw saves, logs, screenshots and the manifest in the
ignored validation directory. No calibration endpoints are acquired.
