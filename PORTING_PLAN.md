# Roadmap del core SM2-Emu Libretro

## Two-Option Network Convention — 2026-10-17

Status: Implemented, verified and installed locally. The user authorized implementation in this chat without a consumption cap. See [implementation and evidence](Docs/NETWORK_TWO_OPTION_2026-10-17.md).

Virtual On local-board correction (2026-10-18): No Link does not mean the
communication board is absent. With a disconnected board, a fresh SRAM reaches
the attract sequence but starting a match gives a black picture; the existing
user SRAM is not the cause. The local board remains fitted while external
linking is disabled. Isolated RetroArch Software/Vulkan runs reached the match
with the user SRAM unchanged. See the same report for the evidence and scope.

Authoritative contract: [Framework 0.1.23, F05/F14](/Users/andrea/dev/libretro-core-framework/FRAMEWORK.md).
Adoption interchange: [TGPulse Network Integration — Cross-Core Adoption Review, 2026-10-17](/Users/andrea/dev/libretro-core-framework/TGPULSE_NETWORK_ADOPTION_REVIEW_2026-10-17.md). Apply its findings during this integration; source review and another core's results are not SM2 runtime acceptance.
Per-game review: [Network Review](/Users/andrea/dev/libretro-core-framework/outputs/01a13152-dbfa-7e30-bc9d-0477abc2cccc/Framework_Network_Review.xlsx), single sheet. This revision supersedes prior Network Board / Automatic Network Settings semantics and older network comments in Menu Review; previous delivered work is a baseline, not completion of this task.

- Exactly two always-visible controls: Linked Cabinets and Auto Network Role Settings (ANRS); both display Not Supported for unsupported games. Remove the separate Network Board option.
- Linked Cabinets: -1 Disabled/default, with 0/1 aliases; the communication board remains fitted and uses local loopback as in upstream. 2..n per-game totals; theoretical role count permitted where unknown, identified as theoretical.
- ANRS: -1 Disabled/manual; 0 native Standalone/No Link default; 1 Master; 2..n Slave/ID; r special native role with l/s aliases. Use native labels and contextual ID descriptions. When Standalone is not separately defined, Master means Standalone in loopback and Master in a network, not a converted role.
- Keep topology and role independent. ANRS overrides NVRAM Settings and works when it is disabled. Hide only the corresponding native role/ID controls while automation is active; preserve unrelated fields and integrity.
- Retain program-implied roles/identities; dedicated Relay programs have one choice, and non-Relay Virtual On must not offer Relay. Respect the reviewed per-game defaults.
- No compatibility with the previous networking model. Invalid values fall back to default with notification. Coalesce effective changes into one automatic reset on Resume; unchanged Resume does not reset.
- Acceptance: all applicable catalogue rows mapped; modern/legacy registration, labels/values/defaults/aliases, unsupported-game visibility, NVRAM priority/manual restoration, native persistence/integrity, local and representative linked behavior checked separately; verify installed artifact identity when delivery is authorized. Do not present theoretical totals as multiplayer qualification.
- Prototypes are excluded from analysis/acquisition/testing/implementation unless the user explicitly requests them. Royal Ascot II is not working and excluded from operational qualification.

### Adoption Requirements And Acceptance

Delivery: all source, native mapping, registration, ABI/transport and local deployment checks below are implemented. Actual RetroArch menu/paused-role application and a two-instance Daytona linked baseline pass. Broader interactive active-lobby permutations, theoretical maximum counts, synchronized racing and other platforms remain qualification limits, not claims of this delivery. See the report for evidence boundaries.


- **Consuming Option Reads (F05):** audit all option readers. `src/libretro/core_options.h::update_option_display` currently calls visibility reads without first retaining the update signal; frame ordering in `core.cpp` alone does not cover this paused callback. Retain pending changes before consuming `GET_VARIABLE` reads and merge them on Resume, or demonstrate an independent application path. Reuse checks that model RetroArch's consuming reads; retain failing-before/passing-after evidence for the defect. Cover repeated paused callbacks, unrelated reads, inactive/unchanged selections and operation without a display callback; verify effective application and reset notification in the frontend.
- **Independent ANRS Authority:** remove the residual NVRAM Settings dependency in `src/libretro/core.cpp::refresh_nvram_options` and its pending-application path. Verify ANRS application with NVRAM Settings Disabled, while unrelated operator settings retain their normal gate.
- **Hidden Selector Synchronization And Handover:** publish effective native role/ID values to the corresponding selectors even while hidden. Disabling ANRS hands authority to the last applied values, not stale earlier manual choices. Verify both NVRAM Settings states and preservation of unrelated fields.
- **Active Lobby Lifecycle:** review the full Resume/Restart path, preserving the frontend lobby, registered send/poll callbacks and connected clients. Do not unload content or stop/start Netpacket for machine reconfiguration. Exercise an already-open lobby, staggered peer arrival/recovery and explicit Restart with changing cabinet totals. Apply topology and native role/ID before the first native frame; clear stale machine/frame data without tearing down transport ownership.
- **Effective-Change Reset:** combined topology/role/NVRAM changes cause exactly one reset. Unchanged Resume, aliases with unchanged effect and fresh-machine initialization must not add duplicate resets. Keep actual reset/notification evidence distinct from successful registration.
- **Native Mapping And Persistence:** derive each game's roles and identities from its reviewed native settings, never from frontend host/client identity or numeric table order. Verify saved data as well as clean starts, native checksums/mirrors, unrelated-byte preservation and fresh reload. Record the effective board/topology and native role when diagnosing a failed configuration; do not silently convert roles.
- **Re-entrant Callbacks:** publish frontend option changes outside locks that callbacks can re-enter; verify re-entry safety using SM2's own architecture. Preserve its actual Save State restrictions rather than copying TGPulse's COMM policy.
- **Evidence Boundaries:** reuse the existing SM2 runners. Record modern/legacy registration, source checks, ABI/transport checks, real frontend lobby behavior, native persistence and synchronized gameplay separately. Theoretical totals and TGPulse's qualification do not establish SM2 multiplayer support. Keep the existing Framework progress-reporting requirement below.

### Progress Reporting To The Framework Chat

The user explicitly authorized this project's chat to send meaningful integration updates to Framework thread `01a13152-dbfa-7e30-bc9d-0477abc2cccc`, host `local`, using send_message_to_thread. Report implementation progress, blockers, any proposed contract changes, validation evidence/limits and local delivery with paths and hashes. Update this roadmap as work progresses. Report facts without treating findings as authorization to alter the shared contract. This reporting authorization does not itself authorize implementation or commit/push.

Model 2 Focus: include Power Sled implicit roles/colors and dedicated Relay programs. GTX's independent inventory and 58-stage native commit/reload campaign are complete, with dedicated NVRAM options and initial template delivered: LINK ID MASTER/SLAVE/SINGLE and CAR NUMBER 1–8. Reuse that verified mapping as input to the new automation; validate ANRS authority, identity selection, persistence and lifecycle separately before declaring this networking convention delivered. Do not reopen excluded prototypes or the closed Power Sled package beyond the scope of this network integration.

## User-Revised Framework Menu Wording — 2026-10-13

Approved follow-up (Order 071, Menu Review!F98) completed: Gamepad Rumble uses
exactly `Enable gamepad vibration using the game's force-feedback or rumble effects.`
Rebuilt, registration verified and normal installed core updated. Values, defaults
and behavior unchanged; the former Rumble wording exception is superseded.


| Status | Activity | Scope / Acceptance |
| --- | --- | --- |
| 🟢 | Apply The User-Revised Menu Workbook | The final workbook reconciliation and F04 ordering are implemented and registration-audited for Model 2. The final 202-row [Framework Menu Review](/Users/andrea/dev/libretro-core-framework/outputs/01a13152-dbfa-7e30-bc9d-0477abc2cccc/Framework_Menu_Review.xlsx) has SHA-256 `4ceb9be04d7ad32201c78ae53ac2b103987f8867df69675230996dab7c9c125a`; all 48 applicable non-NVRAM rows match the final V2 registration. V2 and legacy each register 452 options in identical order; complete metadata by key and System order match the pre-order baseline. Video, Audio and Input follow the user's reviewed functional groups, with Controller Profile Type first and general Gamepad Rumble second in Input; 31 positions changed against the pre-order baseline. The latest normal installed core is SHA-256 `ce1a48cd89a6ca88368cd6ccdc0348427cfee21771ce2a66ef9e1e24e9a177e7`. All four category pages were visually inspected in isolated RetroArch on 2026-10-18; the full catalogue remains covered by registration audits rather than an exhaustive visual walk of every dynamic NVRAM field. See the [wording record](Docs/FRAMEWORK_MENU_WORDING_2026-10-13.md), [ordering/interchange record](Docs/FRAMEWORK_FUNCTIONAL_GROUPS_INTERCHANGE_2026-10-17.md) and [frontend observation](Docs/FRONTEND_MENU_AUDIO_RESET_2026-10-18.md). This follow-up does not reopen completed networking integration. |

Reference mapping: existing menu review in phase 3.7 and the shared Framework wording review. This is a new wording revision, not evidence
that previous canonical-text work already implements the user's latest edits.
The user has combined formerly separate entries and changed core membership;
preserve those decisions. The workbook's `Source Options` sheet is historical
registration evidence: do not use its original split rows or Order links to
undo the reviewed table. Exclude individual per-game NVRAM operator fields
from harmonization.

`Details` distinguishes global applicability (blank), a group of games or a
specific game. For non-game-specific, non-NVRAM rows, a retained qualifier
after `—` has been moved into the comment as an applicability sentence; the
category remains in Details. Game-specific names already identify their game.
Use the reviewed text, including those applicability sentences, across the
relevant registration paths. Preserve raw option keys, saved values, defaults,
visibility and behavior; a shared label does not authorize changing emulation
or replacing native feedback with synthetic feedback.

Approved consolidation follow-up (2026-10-13): the workbook then had 203
review entries; the final 2026-10-17 workbook has 202 after Order 222 was
removed. Use Timing / FPS Overlay (Order 012) for all three cores,
including the former Frame Timing Overlay; use Gamepad Rumble (Order 071)
for all three cores, including the former Force Feedback; use one Off-Screen
Reload Shortcut (Order 088) for Model 2 and Model 3. Former Orders 200, 212
and 218 are superseded by these rows. Core flag union is authoritative; do
not recreate the removed rows or alter raw keys/behavior because labels merge.

Single-game core option labels must start with `<Game Name>: `, using exactly
one colon and one following space, then the option description in Title Case.
Apply this to the effective target label: Name (New) when populated, otherwise
Name. Group/global options do not receive a single-game prefix. Per-game NVRAM
operator parameters remain outside cross-core harmonization. Validate this
prefix and the merged labels as part of the pending wording acceptance below.

Applied in this same menu-wording activity: review final Core Option
presentation order under [Framework F04](/Users/andrea/dev/libretro-core-framework/FRAMEWORK.md)
and its [Frontend Option Ordering handoff](/Users/andrea/dev/libretro-core-framework/ROADMAP.md).
Within menus/submenus other than System, keep global options preferably first
and group `<Game Name>: ...` options last. Sort by displayed label while keeping
reviewed functional parameter groups together: Horizontal Range must be
immediately followed by Vertical Range at the Horizontal group's alphabetical
position. Examine actual related parameters before adding further groups.
Review the entire set of registered options against implementation and
references for parent/dependent controls, axes, numbered sources and native
fields. Preserve each justified group's functional order before sorting the
groups; place a controlling mode before its dependent settings when applicable.
Similar names or adjacency alone do not establish a group, and independent
controls must remain independent. TGPulse's delivered MVD Input/H/V/Gravity/
Drift/Diagnostics and LCD Display/Position/Opacity sequences are examples
verified in that core, not SM2 sequences to copy without an equivalent feature.
System retains its functional order; NVRAM Settings and native operator-field
order remain explicit exceptions. Verify the effective V2 and legacy
registration order without moving categories or changing keys, values,
defaults or workbook Order identifiers. Reuse the existing final-registration
audit with independently defined expected sequences and a baseline metadata
comparison; distinguish registration evidence from actual menu inspection.
The user approved the SM2 functional blocks on 2026-10-17. The final V2 and
legacy registration audit passes; visual option-page acceptance remains open.

Acceptance: reconcile every applicable reviewed row against current option
keys, validate modern/legacy labels and help, and inspect the resulting menu.
All applicable rows are reconciled; modern and legacy registration checks and
Save RAM checks pass. The normal installed core is updated. A later isolated
RetroArch run inspected the System, Video, Audio and Input pages directly;
the former ScreenCaptureKit failure is historical. The owned process exited
normally with no residual processes. No commit or push.

Il progetto indipendente `Zer0one/sm2-emu-libretro` sviluppa su `main` e usa
`dmanlfc/sm2-emu` come remote `upstream`. La base iniziale è SM2-Emu 0.9.4,
commit `8b3a468c5b51387093811cb16b076e6fd9289d66`. Il clone mainstream rimane
separato, per build e confronti con il codice originale. La base storica dell'importazione completa è
`5ddf84ae7970a9bce1d0a17b3900d26065de1996` (0.9.13). La copertura upstream
riconciliata arriva a `7db71083ac3419b0c17af74bc6a1640365226238` (0.9.44):
le modifiche applicabili sono integrate o adattate e le esclusioni motivate sono
registrate nei pacchetti e nel punto 9. Il core dichiara **0.9.44.0** secondo la
convenzione del [manifesto dei porting](Docs/UPSTREAM_PORTING_MANIFESTO.md).
Gli import selettivi contribuiscono alla copertura; la base storica 0.9.13 non
rappresenta più la versione upstream pubblicizzata. Il solo fetch non avanza
questa copertura. La release 0.9.13.1 aveva mantenuto erroneamente il numero
storico; 0.9.44.0 corregge versione e documentazione senza nuovi cambiamenti
all'emulazione. Vedere [release notes](Docs/RELEASE_NOTES_0.9.44.0.md).

Obiettivo: un core per RetroArch e Batocera, preservando emulazione, timing,
audio e controlli. Ogni traguardo richiede una prova eseguibile; una build
riuscita da sola non dimostra compatibilità o gameplay corretto.

Menu, profili e opzioni seguono [LIBRETRO_DESIGN.md](LIBRETRO_DESIGN.md),
che adatta le convenzioni del progetto personale Supermodel a Model 2.

## Daytona GTX Addition — 2026-10-12

| Status | Activity | Remaining Work |
| --- | --- | --- |
| 🟢 | GTX Catalog And Banked Protection | MAME-derived frontend-neutral protection, CRC-checked clone definition, bank Save State and scoped checks pass; RetroArch Vulkan 1x reaches a race in 2,300 frames with audio/SRAM and clean exit. Normal installed core and configured database updated. Set remains preliminary; see `Docs/DAYTONA_GTX_SUPPORT_2026-10-12.md`. |
| 🟢 | GTX Service Menu Inventory | Phase 1 complete in isolated RetroArch: 10 settings, 83 screenshots, all cycles closed. Native roles Master / Slave / Single; Car Number 1–8. YAML, catalogue and local workbook updated; see [inventory](Docs/DAYTONA_GTX_SERVICE_MENU_2026-10-17.md). |
| 🟢 | GTX NVRAM Settings And Initial Setup | Eight approved fields implemented after the complete 58-stage native commit/reload campaign. Dedicated GTX template; Single / Deluxe / Export initial overrides, preserving valid existing saves. Credit settings excluded. Build, Save RAM/catalog audits and three isolated RetroArch persistence trials passed; normal installed core updated. Linked gameplay remains separate. |

## Latest Shared Input Update — 2026-10-12

| Status | Activity | Evidence / Remaining Work |
| --- | --- | --- |
| 🟢 | Controller Profile Type | Implemented first in Input: Normal / Normal + Test/Service (default), global across ports; Controls no longer selects variants. Catalog/input/options checks and isolated RetroArch VF2 UI switching pass. Follow-up corrects paused-menu metadata: modern display callback updates Controls names/descriptors without Resume or reset; legacy API retains Resume refresh. Normal local core updated. Framework edition 0.1.1 records this SM2 contract and the other-core adoption candidate; destination F09 and reconciliation entries verified. Retain the interchange file; other-core implementation is not claimed. |

## Implementazioni ancora aperte

The approved TGPulse adaptation candidates are listed in section 8, and
independent upstream follow-ups in section 9. Linked topology and Netpacket
buffering have passed their bounded checks; true 3D widescreen is deferred.
Manx TT operator qualification is closed following the user’s positive tests
on 2026-10-11. Rendering and Video Options is complete within its documented scope after
the consolidated source/backend review and OpenGL context-loss correction.
Physical-device and subjective user checks retain their own status.
Existing runtime and gameplay checks that need no new implementation remain in
the final section.
The user closed the current networking test campaign on 2026-10-18; future
newly observed faults will be recorded as new activities. The remaining
implementation candidate is True 3D Widescreen, deferred in section 8.

## 0. Baseline upstream — completata nei limiti indicati

Standalone macOS arm64 compilato e avviato con Vulkan/MoltenVK su Apple M4.
Catture delle sequenze dimostrative di Daytona USA, Sega Rally e Virtua Fighter 2.
Vedere [MACOS_BUILD.md](MACOS_BUILD.md).

## 1. Macchina senza frontend — completata il 9 settembre 2026

- Separare in CMake librerie di emulazione e programma SDL: il target di prova
  deve configurarsi e compilarsi senza SDL, Vulkan/OpenGL, ImGui o glslc.
- Esporre l'audio di ogni scheda attraverso l'interfaccia comune della macchina,
  usando il sample rate effettivo e svuotando il buffer una volta per frame.
- Aggiungere `sm2-headless`: caricamento ROM, NVRAM nuova, esecuzione di N frame,
  rendering software per ogni frame, registrazione audio e immagine finale.
- Confrontare con `--boot-test` dello standalone originale: immagine finale,
  campioni audio, NVRAM, stato CPU e cicli devono coincidere.
- Ricompilare anche lo standalone, per verificare che la separazione non lo rompa.

Criterio superato: build indipendente e confronti riusciti su Daytona USA
(Model 2), Virtua Fighter 2 (2A), Virtual On (2B) e Sega Touring Car (2C),
1800 frame ciascuno. Vedere [HEADLESS.md](HEADLESS.md) per dettagli e limiti.
Questo target è uno strumento di verifica, non un core Libretro.

## 2. Primo core Libretro software — completata il 9 settembre 2026

- Aggiungere il target dinamico e l'ABI Libretro: init/deinit, load/unload,
  `retro_run`, reset, informazioni di sistema e callback del frontend.
- Usare loader e macchina esistenti; individuare `games.xml`, ROM e salvataggi
  attraverso le directory fornite dal frontend, senza percorsi locali fissi.
- Consegnare un frame per `retro_run()`: conversione esplicita dal formato
  software upstream al pixel format Libretro, geometria 496 × 384, aspect 4:3
  e timing derivato dall'hardware. Verificare colori, orientamento e pitch.
- Consegnare audio stereo al rate della scheda, gestendo correttamente i campioni
  accettati dal frontend e le transizioni tra contenuti.
- Input minimo necessario alla prova: moneta, start, comandi principali e reset.
- Dichiarare i save state non supportati finché la serializzazione non esiste.

Criterio: un titolo realmente avviato in RetroArch macOS con immagine, audio e
controlli; prove ripetute load/unload/reset e confronto con la baseline.
Criterio superato: VF2 avviato in RetroArch macOS con input da replay,
immagine di gameplay e audio stereo registrato; test ABI load/unload/reset e
confronti video/audio/NVRAM identici su tutte le quattro schede. Vedere
[LIBRETRO.md](LIBRETRO.md) per prove ripetibili, confini del supporto e limiti
rispetto a controller fisici e ascolto manuale.

Ordine aggiornato su richiesta dell'utente: dopo il punto 2 è stato anticipato
il punto 5 (GPU), prima dell'implementazione dei profili. I numeri restano stabili
per i riferimenti esistenti: **0 → 1 → 2 → 5 → 3 → 4 → 6**.
Vedere [GPU.md](GPU.md) per implementazione, prove e limiti della prima GPU macOS.

## 3. Controlli, NVRAM e opzioni essenziali

Procedere per sottopunti circoscritti, senza implementarli tutti in blocco.
Il primo definisce il catalogo; le mappature si implementano dopo la sua revisione.

### 3.1 Catalogo dei profili dai metadati — revisionato e implementato

- Inventariare i `GameSpec` dopo l'ereditarietà parent/clone.
- Definire famiglie e varianti con il criterio usato in Supermodel; per giochi
  e seguiti con controlli equivalenti conservare nome, disposizione e convenzioni
  del profilo, documentando differenze reali e lacune dei metadati.
- Separare ciò che i metadati determinano dalle eccezioni o lacune da verificare.
- Consegnare [CONTROL_PROFILES.md](CONTROL_PROFILES.md): 83 set, 14 firme
  generiche e 23 raggruppamenti di lavoro, con matrice Model 2 / Model 3 e casi da verificare.

Criterio: copertura del catalogo e revisione dei profili proposti. Nessuna
nuova mappatura, opzione o modifica alla persistenza in questo sottopunto.

### 3.2 Riconoscimento e controlli digitali — implementato e verificato localmente

- Implementare il riconoscitore secondo il catalogo revisionato, con fallback
  esplicito; registrare dispositivo e descrittori pertinenti al gioco.
- Completare Joystick (Standard), comprese Fighting/Soccer, e Joystick (Twin),
  preservando azioni e alias e verificando la permutazione Soccer in partita;
  aggiungere le varianti comuni con/senza Test/Service rimappabili.

Criterio: test del riconoscitore sui set catalogati, nessun controllo improprio,
P1/P2 indipendenti e prova dei profili digitali in RetroArch.

Il riconoscitore copre i 34 set parent/clone revisionati per i profili digitali
e rifiuta firme I/O cambiate o non catalogate. Nomi, descrizioni e posizioni
RetroPad sono quelli approvati in `Docs/revisione_profili_model2.xlsx`. Ogni
profilo espone la variante predefinita con Test/Service e quella ridotta senza
i due comandi. I controlli ROM-free verificano inoltre indipendenza P1/P2,
permutazione hardware Soccer e doppia leva Virtual On. VF2, Virtua Striker e
Virtual On sono stati avviati fino a una partita reale in RetroArch macOS;
rimane distinta la prova manuale con un controller fisico.

### 3.3 Profili di guida — implementati

- Procedere per varianti 4-Speed + VR4/VR1, Sequential e Motorcycle.
  Per Sega Rally verificare Handbrake prima di esporre il profilo completo
  condiviso con Sega Rally 2; la lacuna è documentata nel catalogo.
- Rispettare canali, calibrazioni, polarità e comandi del cabinet; aggiungere
  cambio e regolazioni di sterzo/acceleratore/freno con default trasparenti.
- Introdurre insieme alle funzioni le relative Core Options v2 e descrizioni.

Criterio: estremi/riposo degli assi, cambio e azioni coperti per variante.

Il primo gruppo copre i quattro set Daytona e i cinque set Sega Rally. Espone
`Driving: 4-Speed + VR4` e `Driving: 4-Speed + VR1 + Handbrake`, ciascuno con
la variante predefinita Test/Service e quella ridotta. L'opzione `4-Speed
Shifter` seleziona H-Gate, predefinito, oppure Standard; Neutral e Shift
Down/Up restano sempre disponibili. I test verificano assi, trigger analogici,
VR, cambio e freno a mano IN2. Le ROM parent hanno raggiunto una gara reale in
RetroArch macOS, a 300 km/h Daytona e 127 km/h Sega Rally nel frame acquisito.
I profili Motorcycle sono coperti nei gruppi Manx TT e Motor Raid descritti sotto.

Il secondo gruppo copre dieci set delle famiglie Indy 500, Over Rev e Sega
Touring Car Championship con il profilo unico `Driving: Sequential + VR2`.
Descrizioni e posizioni derivano direttamente dalle tre righe approvate del
foglio Excel. View 1/2 usano D-Pad Up/Down; Shift Down/Up usano L1/R1 e agiscono
direttamente sui due ingressi momentanei hardware; Brake, Accelerator e Steering
restano esclusivamente analogici. Il profilo espone entrambe le varianti con e
senza Test/Service.

Le tre ROM parent sono state avviate con successo in RetroArch macOS usando un
replay di avvio: Indy 500 ha raggiunto
la griglia di partenza, Over Rev la selezione modalità e STCC l'inserimento
nome. Audio e Save RAM sono risultati validi in tutte le esecuzioni.

Il terzo gruppo aggiunge il solo Super GT 24h come `Driving: Sequential + VR1`.
Rispetto alla variante VR2 espone esclusivamente `VR1` su D-Pad Down; cambio,
sterzo e pedali seguono le posizioni approvate nel foglio, con pedali analogici
e polarità invertita dichiarata dai metadata, senza correzioni aggiuntive nel
binding. MAME segnala ancora sterzo non centrato e pedali pulsanti: il limite va
indagato nell'emulazione analogica comune. La ROM parent ha raggiunto la
selezione del circuito in RetroArch macOS.

Il quarto gruppo aggiunge i tre set Manx TT come `Driving: Sequential (Manx TT
Superbike)`. Il profilo usa Bank sullo stick sinistro X, Brake/Accelerator sui
trigger analogici, Shift Down/Up su L1/R1 e l'azione combinata `Start / VR` su
Start con binding secondario su D-Pad Down. La polarità Bank segue il metadato
invertito. La ROM parent ha raggiunto il controllo iniziale del motion slider
in RetroArch macOS.

Il quinto gruppo aggiunge `motoraid` e `motoraiddx` come `Driving: Sequential
(Motor Raid)`. Il gioco non ha un cambio: Kick usa South/L1 e Punch usa East/R1,
con i dorsali come binding secondari sugli stessi due ingressi arcade. Le
posizioni corrispondono al foglio approvato. La ROM parent ha raggiunto una gara in RetroArch macOS;
audio e Save RAM sono validi.

### 3.4 Puntamento e joystick analogico

Stato: Joystick (Analog) e famiglia Gun implementati.

Criterio: calibrazione, polarità, pulsanti e cambio sorgente coperti.

L'audit preliminare dei sei parent Gun ha confermato coordinate assolute per
tutti. `vcop`, `vcop2` e `hotd` usano la lightgun seriale RS-422 a 10 bit e
supportano il reload sparando fuori dall'area calibrata; il foglio assegna
quindi `Reload Offscreen` a East. `gunblade`, `rchase2` e `bel` usano assi
posizionali a 8 bit e non espongono questa azione; BEL conserva `Missile` su
East. Queste due famiglie hardware richiedono traduzioni interne distinte.

Il primo gruppo del punto 3.4 implementa `skytargt` come `Joystick (Analog):
Sky Target`. Il profilo usa esclusivamente lo stick sinistro per gli assi X/Y,
con X invertito e Y normale secondo i metadata, South/RB ed East/LB per
`Machine Gun`/`Missile`, e D-Pad Up per `View Change`. Espone le
varianti con e senza Test/Service. I controlli ROM-free verificano firma,
descrittori, bit digitali e assi. La ROM parent
ha raggiunto una partita in RetroArch macOS; audio e Save RAM sono validi.

Il secondo gruppo implementa `bel` come `Gun: Behind Enemy Lines` per due
giocatori. Ogni port usa South/East per `Shot`/`Missile` e lo stick sinistro
per `Gun Yaw (Analog Cursor)`/`Gun Pitch (Analog Cursor)`, senza binding non
previsti dal foglio. La traduzione conserva i quattro range analogici distinti,
i bit Shot/Missile di P1/P2 e lo scambio hardware delle linee Test/Service
specifico di BEL. I controlli ROM-free coprono entrambe le varianti service,
descrittori, assi e bit digitali. La ROM ha raggiunto una partita in RetroArch
macOS; audio e Save RAM sono validi.

Il terzo gruppo completa la famiglia Gun: `gunblade`, `rchase2`, `vcop`,
`vcop2` e `hotd`, incluse le revisioni, usano il profilo `Gun`; BEL conserva il
profilo specifico. La Core Option `Gun Input Mode` riprende da Supermodel i
percorsi Standard, Lightgun, Mouse + Analog Stick, Mouse e Analog Stick e
aggiorna subito nomi e descrittori. Il core traduce il cursore virtuale nel
protocollo seriale RS-422 a 10 bit oppure nei quattro canali posizionali a 8 bit
in base ai metadata. `Reload Offscreen` è disponibile solo per Virtua Cop 1/2 e
House of the Dead; BEL espone invece `Missile` su East/LB.

Il difetto del mirino verticale di BEL con un `.srm` già inizializzato è stato
risolto estendendo il workaround hardware esistente al preset di calibrazione
incluso nell'Initial NVRAM. Build, controlli input, avvio automatico di 600 frame
e prova manuale in RetroArch macOS completati: il Service Menu riceve entrambi
gli assi e il mirino del gioco si muove in entrambe le direzioni.

La Core Option `Off-Screen Reload Shortcut`, visibile soltanto sui sei set
seriali, abilita per default RetroPad East/LB, Mouse destro e Lightgun Reload. Se
disabilitata rimuove questi descrittori e ingressi; una lightgun puntata fuori
schermo e azionata col grilletto continua a usare il gesto nativo del cabinet.
Coordinate e stato off-screen sono separati fino alla scheda seriale emulata:
Libretro usa `IS_OFFSCREEN`, mentre raggiungere il bordo con il Mouse non attiva
più implicitamente la ricarica. La Core Option `Mouse Edge Off-Screen Reload`,
Disabled per default, consente di ripristinare esplicitamente il comportamento
MAME per Mouse Left entro il 5% dei bordi.

I controlli senza ROM verificano tutti i dieci set, P1/P2, le cinque modalità,
i range e le polarità degli assi, il particolare grilletto P2 di House of the Dead e l'assenza
del reload nei cabinet posizionali. Gunblade NY e Virtua Cop 2 hanno raggiunto
una partita in RetroArch macOS con audio e Save RAM validi.

### 3.5 Cabinet speciali

Primo gruppo completato: `dynabb` e `dynabb97` espongono il profilo condiviso
`Joystick (Standard): Baseball (Dynamite Baseball)`, con joystick, due pulsanti
e `Bat Swing` su Right Analog Y verso il basso per ciascun giocatore. I
controlli ROM-free verificano firma, descrizioni, P1/P2, semiasse e varianti
Test/Service; entrambi i parent hanno raggiunto una partita in RetroArch macOS.

Secondo gruppo completato: `segawski` espone `Special: Water Ski` con Set su
South, Pitch Left/Right su L1/R1 e sui binding secondari West/East, Slide su
Left Analog X e l'alias hardware
`Start / Select Down`. Slide applica la polarità invertita dichiarata nei
metadata. `skisuprg` espone `Special: Ski Super G`
con Inclining su Right Analog X/canale 0 e Swing su Left Analog X/canale 1.
Swing applica la polarità invertita dichiarata nei metadata e
Foot Sensor attivi alti su L1/R1. I controlli ROM-free verificano
firme, descrittori, bit, assi e varianti Test/Service. Water Ski ha raggiunto
una gara reale. Ski Super G carica profilo, audio e Save RAM, ma l'emulazione
comune non risponde al controllo della Drive Board esterna e raggiunge
`DRIVE BOARD TROUBLE CODE: FF`. La Core Option specifica `Drive Board Error
Bypass (Restart Required)`, disabilitata per default, riproduce la singola
pressione di Test verificata su quella schermata. Abilitandola, la ROM parent ha
raggiunto la sequenza sciabile in RetroArch macOS; disabilitandola resta ferma
sull'errore come upstream. Il bypass non dichiara emulata la scheda o la
protezione e non modifica ROM, NVRAM o binding.

Terzo gruppo completato: `topskatr`, `topskatrj`, `topskatru` e `topskatruo`
espongono `Special: Top Skater`. Curving e Slide restano assi distinti su Left
Analog X e Right Analog X. Curving applica la polarità invertita dichiarata nei
metadata; Slide resta invariato. Select Left/Right e
Jump Front/Tail raggiungono i bit
documentati da MAME. I controlli ROM-free coprono tutte le revisioni, firme,
descrittori, assi e varianti Test/Service. Il parent ha raggiunto una sessione
di gioco in RetroArch macOS con audio e Save RAM validi.

Quarto gruppo completato: `waverunr` espone `Special: Wave Runner` con View,
Handle, Pitch, Roll e Throttle nelle posizioni approvate. I controlli ROM-free
verificano firma, descrittori, intera escursione dei quattro canali, valore di
riposo dichiarato, safety sensor non bindabile e varianti Test/Service. Il
parent ha raggiunto una sessione di gioco in RetroArch macOS con audio e Save
RAM validi.

Quinto gruppo completato: `airwlkrs` espone P1-P4 con
`Joystick (Standard): Basketball (Air Walkers)`; la matrice I/O commuta P1/P2
e P3/P4 sulle porte C/D insieme alle rispettive linee Start, mentre Coin 1-4
restano indipendenti. `rascot2` espone
`Joystick (Standard): Horse Racing (Royal Ascot II)` secondo i metadata
disponibili. Entrambi hanno firme, descrittori, bit e varianti Test/Service
coperti dai controlli ROM-free. Air Walkers raggiunge una partita reale con
audio e Save RAM validi. Royal Ascot II mostra il titolo e salva la Save RAM,
ma resta silenzioso e non supera la sequenza iniziale verso l'attesa SegaNet
nel replay standard.

Sesto gruppo completato: `desert` espone `Joystick (Analog): Desert Tank + VR3`. Il backend
Model 1 I/O esistente riceve ora dai metadata condivisi Steering, Accelerator
ed Elevation sui canali 0-2; il profilo aggiunge VR1-VR3, Machine Gun, Cannon e
Shift toggle con le posizioni approvate. I controlli ROM-free verificano firma,
descrittori, riposo e controllo relativo/assoluto di Elevation, velocità e
inversione dell'asse, toggle, alias RB/LB per Machine Gun/Cannon e varianti
Test/Service.
La build standalone compila con lo
stesso metadato e il parent ha raggiunto una missione reale in RetroArch macOS
con audio e Save RAM validi.

Settimo gruppo completato: `hpyagu98` espone `Joystick (Standard): Baseball
(Hanguk Pro Yagu 98)` a due giocatori, con D-Pad e Button 1/2/3 sul layout
elettrico VF2 documentato da MAME. I controlli ROM-free verificano entrambe le
porte, descrittori, bit e varianti Test/Service. Il parent ha raggiunto una
partita reale in RetroArch macOS con audio e Save RAM validi. Il problema di
persistenza di `FAVORITE` resta confinato alla NVRAM e non blocca il profilo
input.

- Integrare ciascun profilo con i suoi test senza estendere implicitamente le
  conclusioni agli altri cabinet o confondere input supportati e gioco funzionante.

Criterio: chiusura documentata per ogni profilo; i casi non verificati restano
indicati nel catalogo e nel frontend.

La crosshair è implementata nei backend Software, Vulkan e OpenGL. Il valore
`Automatic` segue la convenzione upstream: P1 esterno per i giochi con pistola
seriale e mirino in gioco per quelli posizionali; una selezione esplicita rende
il mirino esterno disponibile anche per questi ultimi. `Crosshair Style` offre
lo stile SM2-Emu come default e Supermodel come alternativa. Le prove sui sei giochi hanno confermato
che i valori di calibrazione nativi sono già funzionanti; per decisione
dell'utente non serve una campagna dedicata né l'iniezione di ulteriori dati nei
campioni iniziali.

### 3.6 Persistenza NVRAM/EEPROM — completata

Stato: persistenza e matrice dei parent implementate. `RETRO_MEMORY_SAVE_RAM`
contiene backup RAM ed EEPROM in formato versionato; import frontend, fallback
nativo e 289 impostazioni operatore per 35 parent più quattordici cloni con menu
specifico sono coperti da test senza
ROM e da avvii reali consecutivi in RetroArch. `Automatic Initial NVRAM Setup`
carica per questi parent un campione completo validato prima del primo frame,
soltanto in assenza di `.srm` e NVRAM native valide, quindi applica Country/Nation
USA o Export, i valori offline necessari e I/O Type C per Super GT 24h.

- Non inizializzare o modificare automaticamente i salvataggi esistenti; il
  setup automatico interviene soltanto alla creazione di una nuova Save RAM.
- Prima fase della campagna clone completata il 15 settembre 2026: tutti i 48
  cloni presenti in `games.xml` sono stati avviati senza input da una directory
  vuota e hanno prodotto backup RAM ed EEPROM native. Ventuno acquisizioni sono
  identiche al parent e 27 presentano differenze stabili; nessun avvio è fallito
  e una seconda acquisizione dei 22 parent ha escluso variabilità tra esecuzioni
  equivalenti. Il dettaglio è in `CLONE_NVRAM.md`; i dati grezzi restano esclusi
  da Git.
- Per i 21 cloni identici, l'eredità del template parent è autorizzata
  esplicitamente e coperta dalla campagna conclusiva.
- Ventuno cloni usano ora template dedicati. Tredici applicano senza modifiche
  le opzioni del parent; `daytona93`, `daytonas`, `dyndeka2`, `dyndeka2b`,
  `motoraiddx`, `stcca`, `stccb` e `stcco`
  hanno invece cataloghi specifici ricavati dal proprio Service Menu.
  `daytona93` espone solo quattro
  voci, `daytonas` aggiunge Cabinet=Special e Promote Saturn, mentre `stcca`,
  `stccb` e `stcco` usano la propria codifica Country; soltanto `stccb` conserva
  Default View. Complessivamente 494
  valori e 42 avvii RetroArch hanno verificato layout, integrità, setup pulito e
  persistenza. Con i 21 cloni byte-identici al parent, il setup automatico copre
  42/48 cloni. Il dettaglio e gli aggiornamenti successivi sono in
  `CLONE_NVRAM.md`.
- `daytonam` conserva l'identificatore upstream `protection="daytona-maxx"` e
  la relativa PIC è emulata nel solo percorso Model 2 Original. Con ROM reale
  il clone supera la schermata operatore e raggiunge Circuit Select con lo
  stesso test Coin/Start del parent; il gameplay è stato poi confermato
  manualmente in RetroArch macOS.

Criterio: persistenza e import provati con casi positivi e negativi; eventuali
campi NVRAM esposti devono avere valori e precedenza espliciti.

Aggiornamento 18 settembre: `vf2a` e `vf2o` dispongono ora di template e
cataloghi propri, riutilizzando gli otto parametri e le codifiche VF2. La
revisione del blocco è 0x13/0x12 anziché 0x18; il campo a 0x3318 è aggiornato
dal gioco e non viene trattato come firma fissa. Il setup copre 44/48 cloni.
`hotdp`, prototipo, è escluso da NVRAM Settings e setup dedicato per decisione
dell'utente. `indy500d` è ora integrato con banca da 44 byte e sette opzioni specifiche;
la copertura aggiornata è 45/48. `vstrikero` è ora integrato con il proprio
menu ridotto di dieci voci, senza One Match Mode, e con Advertise Sound al suo
offset specifico. La copertura è quindi **46/48**: `hotdp` resta escluso perché
prototipo e soltanto `srallycdxa` richiede ancora analisi.

Aggiornamento 19 settembre: anche `srallycdxa` è integrato con il proprio
layout EEPROM da 44 byte e il menu ridotto a Advertise Sound, Country, Game
Difficulty e Game Mode. Cabinet Type e Link Type non sono presenti e i relativi
byte restano invariati. Il setup automatico copre quindi **47/48 cloni**; il
solo `hotdp` rimane intenzionalmente escluso perché prototipo.

Aggiornamento successivo del 19 settembre: su richiesta è stato integrato anche
`hotdp`. Il prototipo usa due banche EEPROM speculari da 24 byte, distinte dal
layout retail, e dispone di quattro Core Options verificate: Game Difficulty,
Blood Color, Advertise Sound e Country. Blood Color espone soltanto Red/Green;
Life Setting, Gun Blowback e Cabinet Type restano documentate ma escluse secondo
la revisione concordata. Template dedicato, checksum, primo avvio e persistenza
portano la copertura della campagna a **48/48 cloni**, con 27 template dedicati
e 21 ereditati.

### 3.7 Revisione dei menu — completata

- Consolidare le opzioni introdotte nei sottopunti precedenti secondo
  LIBRETRO_DESIGN.md: categorie pertinenti, visibilità, default e riavvio richiesto.
Criterio: categorie, visibilità, default e indicazioni di riavvio coerenti con
`LIBRETRO_DESIGN.md`; le prove fisiche residue sono raccolte nella sezione finale.

### 3.8 Core Options derivate da Supermodel

Stato: `A/V Timing` e `Timing / FPS Overlay` sono implementate. Il timing nativo
57,524160 Hz resta selezionabile con `native`; `60 Hz (Default)` usa il valore
`60hz`, avanza la macchina a ogni callback e ricampiona l'audio al rate della
scheda. Le sole voci visibili sono `60 Hz (Default)` e
`57.524 Hz (Native Model 2)`. La voce corrispondente di TGPulse sarà
`57.524 Hz (Native Model 1)`.
L'overlay riutilizza il pannello Dear ImGui di Supermodel,
composto dal core nel frame Software, Vulkan o OpenGL, e riporta medie su 61
callback per macchina, video, audio, `retro_run`, frame peggiore, cadenza
effettiva e capacità stimata. `Frame Skip` è stato escluso per scelta progettuale.

**60 Hz alignment follow-up (requested 2026-10-01).** The TGPulse-Next adapter
provided the frame-per-callback and fractional-audio reference; SM2 now uses
its own per-board output rate. The Software ABI runner passed 300 frames on
all four board variants with no duplicate video callbacks, exact audio frame
counts and Save State round trips. VF2 passed a separate 1800-frame run with
nonzero PCM, deterministic Save State replay, run-ahead and rewind patterns.
Real frontend Vulkan/OpenGL presentation and subjective A/V continuity remain
separate checks before this follow-up is marked complete.

Il cambio a quattro marce `H-Gate Mode`/`Standard`, derivato da Supermodel, è
già implementato con H-Gate come default.

Opzioni legate ai controlli introdotte direttamente dal core Supermodel:

- `Driving Steering Response`: `Linear` come default, `Progressive (Fine
  Center)` e `FBNeo Logarithmic (Fine Center)`; applicazione limitata ai
  profili Driving;
- `Driving Steering Output Range`: default `100%`, con regolazione comune
  `50%`–`150%`; sotto il 100% limita l'escursione emulata e sopra il 100%
  anticipa il fondo corsa. Include il preset Supermodel `63% (30-80-D0)`, che
  produce esattamente tale intervallo ADC;
- `Driving Accelerator Output Range` e `Driving Brake Output Range`: opzioni
  indipendenti, default `100%`, con regolazione comune `50%`–`150%`. Il preset
  Supermodel `75.3% (00-C0)` produce esattamente tale intervallo ADC.

Le quattro regolazioni precedenti sono implementate, restano sempre visibili,
agiscono soltanto sui profili Driving e sono verificate con curve, saturazione,
pedali normali/invertiti e Throttle motociclistico.

`Gamepad Rumble` è implementata seguendo il decoder upstream 0.9.9.
L'interfaccia rumble Libretro pilota i motori strong e
weak del gamepad P1: i comandi della drive board producono colpi brevi e lo
scostamento dello sterzo una vibrazione più leggera. Il default è Enabled al
massimo della scala normalizzata; RetroArch applica il proprio `Input Rumble
Gain` come unico controllo dell'intensità complessiva. I giochi senza controllo
di guida restano silenziosi. Force feedback direzionale per volanti e recoil
lightgun non dispongono di un'API Libretro dedicata: eventuali backend `evdev`
specifici Linux appartengono al frontend o a componenti esterni, non al core.

Come in Supermodel, le quattro regolazioni di guida devono restare sempre
visibili e non produrre effetti fuori dai profili Driving.

`Enhanced Audio Balance` è implementata come unico interruttore globale nella
categoria Audio. Enabled applica automaticamente i profili SCSP upstream 0.9.7
a tutti i set supportati; Disabled ripristina unity gain in tempo reale. Il fix
INTENA di `overrevb`/`overrevba` resta sempre attivo perché corregge il timer
audio della macchina e non appartiene al mastering opzionale.

`Music Volume` segue la convenzione del core Supermodel: 0–200% a passi di 10,
100% per default e applicazione immediata. Regola soltanto il contributo MPEG
della scheda musicale separata, senza alterare SCSP, effetti o voci. È attiva
sulle famiglie STCC (DSB Z80) e Top Skater (DSB2); sugli altri set resta inerte.

`Aspect Ratio` è implementata con `Auto` come default globale e override `4:3`
o `16:9`. In Auto legge la configurazione attiva dalla NVRAM: Indy 500 e STCC
usano 16:9 nei rispettivi cabinati Deluxe e 4:3 in Twin; gli altri giochi usano
4:3. Il framebuffer resta 496×384 e il frontend riceve soltanto la geometria.

Renderer Model 3, PowerPC/JIT e DSP specifici di Supermodel restano esclusi
perché non applicabili.

## 4. Compatibilità e build di distribuzione

Matrice CI implementata: Linux x86_64, Linux arm64, macOS arm64/Intel e Windows
x86_64, con Software + Vulkan + OpenGL, controlli ABI senza ROM e pacchetti
corredati dal database giochi. Linux arm64 usa il runner GitHub nativo
`ubuntu-24.04-arm` e pubblica `sm2-libretro-linux-arm64`, seguendo lo stesso
percorso degli altri Linux senza cross-compilazione o emulazione. Evidenze e
limiti in [CI.md](CI.md). `sm2_libretro.info`, database e istruzioni sono già
inclusi nei pacchetti. Il controllo di distribuzione verifica inoltre licenze
del core e delle dipendenze incorporate, revisione sorgente, checksum, struttura
del pacchetto e assenza di ROM. La prima esecuzione remota del nuovo job richiede
il prossimo commit/push autorizzato.

Criterio: artefatti installabili sulle piattaforme dichiarate, con matrice di
compatibilità e limiti documentati.

## 5. Rendering GPU integrato nel frontend — Vulkan e OpenGL implementati

- Scegliere il backend dopo aver verificato i contesti realmente disponibili
  nelle build RetroArch target. Non assumere OpenGL 4.3 su macOS.
- Separare rendering da finestra, swapchain e presentazione possedute dall'OSD;
  usare il contesto fornito dal frontend e gestirne perdita e ricreazione.
- Confrontare la resa con la baseline software, compresi scaling e trasparenze.

Criterio: rendering hardware in RetroArch con recupero del contesto e
confronti visivi documentati, mantenendo il percorso software funzionante.

Stato: adattatori Vulkan e OpenGL implementati con passaggi/shader upstream condivisi,
contesto del frontend, Core Options Video e risoluzioni 1×–4×. Sono inoltre
integrati `3D Texture Filtering` (Faithful, Anisotropic 2x–16x) e
`2D Layer Upscaling Filter` (Faithful, xBR, ScaleFX): i filtri 2D operano sulle
tilemap prima della composizione col 3D e restano distinti dagli shader del
frontend. VF2 provato in
RetroArch macOS; quattro schede provate nel frontend GPU di verifica; confronto
pixel esatto con lo standalone Vulkan a 1×/4× e prove di ricreazione del dispositivo.
OpenGL 4.3/OpenGL ES 3.1 riusa i pass upstream ed è stato verificato tramite
EGL/Mesa con VF2 e Last Bronx, scale 1×/4× e perdita/ricreazione del contesto;
immagine, audio e NVRAM coincidono con la baseline software nei casi confrontati.
La modalità `60 Hz (Default)` consegna una nuova immagine dopo ogni ricreazione
del contesto, senza duplicare i callback; il percorso
framebuffer speciale è stato verificato sul title screen di Last Bronx.
Dettagli, limiti e avvio con MoltenVK aggiornato: [GPU.md](GPU.md).

## 6. Networking, save state e funzioni avanzate

### 6.1 Collegamento tra cabinet — tutti gli schemi censiti implementati

- Usare direttamente la struttura upstream 0.9.7: `M2Comm` possiede il
  `CommTransport` e conserva il protocollo della communication board Model 2.
- Adattare a RetroArch il solo trasporto, sostituendo UDP con Netpacket; la
  piccola estensione `ready()` attende il peer prima di avviare il timer del link.
- Usare l'interfaccia ufficiale Libretro Netpacket: nessun socket, discovery o
  configurazione di rete appartiene al core.
- Conservare il comportamento standalone a cabinet singolo quando la Core
  Option `Linked Cabinets` è lasciata su `Disabled`, valore predefinito.
- Esporre `Linked Cabinets` per contenuto come le opzioni NVRAM: ogni set
  supportato mostra soltanto la propria scelta e non la propaga agli altri giochi.

Il trasporto è abilitato per le famiglie Daytona USA e STCC. Daytona accetta da
due a otto partecipanti; STCC arriva a nove includendo il Relay. Riusa dal core
Supermodel handshake broadcast, verifica del
numero atteso e roster ordinato. Il payload Model 3 non viene copiato: ciascun
frame completo Model 2 viene inviato al successore del roster, conservando in
`M2Comm` il protocollo ad anello. Host e client usano lo stesso ROM set e core,
salvo il programma Relay `vonr` nella configurazione Virtual On a tre istanze;
`NVRAM Settings` imposta `Link ID=Master`/`Car Number=1` sull'host e
`Link ID=Slave`/`Car Number=2..8` sui client. Un test reale
con due istanze RetroArch 1.22.2 su macOS ha formato l'anello con ID `01/02` e
`02/02`, eseguito 3600 frame per istanza e avviato una gara condivisa. Le
catture finali mostrano l'host rosso `2nd/2`, con l'auto blu `2P` davanti, e il
client blu `1st/2`, entrambi in movimento nella stessa sessione.
I test senza ROM verificano inoltre anelli emulati da 2, 3, 4 e 8 nodi,
assegnazione univoca degli ID, conteggio, ordine predecessore/successore,
payload integro, roster incompleto, configurazioni discordanti, capacità massima
di nove partecipanti, rifiuto del decimo e disconnessione. Un test RetroArch
isolato a tre istanze ha
inoltre formato il roster reale con partecipanti 0, 1 e 2; tutti i processi si
sono chiusi con codice 0, senza terminazione forzata né residui. La gara
sincronizzata a tre auto resta una verifica separata.

`daytona93` è escluso: il suo Service Menu acquisito contiene soltanto quattro
voci e non espone `Link ID` né `Car Number`. `daytonas`, `daytonase` e
`daytonam` mantengono invece le due impostazioni e restano abilitati fino a
otto cabinet.

Il primo gruppo non-Daytona comprende `stcc`, `stcca`, `stccb` e `stcco`.
I valori NVRAM già acquisiti mappano `Car 1` sull'host, `Car 2`…`Car 8` sui
client giocabili e `Relay` sulla nona istanza. La prova RetroArch massima sul
parent ha salvato nei nove `.srm` le codifiche 1…9, formato il roster 9/9 su
tutte le istanze e chiuso tutti i processi con codice 0, senza kill forzato né
residui. La gara STCC resta nella sezione delle verifiche.

Il gruppo Sega Rally con `Car 1`…`Car 4` e `Relay` usa lo stesso schema combinato
di STCC. `Linked Cabinets` arriva a cinque contando il Relay.
Il parent ha formato il roster massimo 5/5 con `Car 1`…`Car 4` e `Relay`,
codifiche 1…5 verificate negli `.srm`; le revisioni B e C hanno formato roster
reali a due istanze. Tutte le prove sono terminate senza chiusure forzate o
processi residui.
`srallycdx` e `srallycdxa` sono esclusi perché i Service Menu acquisiti non
espongono né `Cabinet Type` né `Link Type`. Entrambi usano cataloghi NVRAM
specifici con le sole quattro voci realmente disponibili; nessuno dei due
riceve la Core Option `Linked Cabinets`. Una gara Sega Rally sincronizzata
resta nella sezione delle verifiche.

Le integrazioni successive vengono organizzate per meccanismo di collegamento,
così l'adattamento e le prove del titolo base coprono nello stesso gruppo anche
i giochi compatibili. Il gruppo con ruoli `Master`/`Slave` e `Cabinet ID`
separato comprende `indy500`, `indy500d`, `indy500to`, `motoraid`,
`motoraiddx`, `waverunr` e `skisuprg`. Indy 500 ammette fino a otto cabinet;
Motor Raid, Wave Runner e Sega Ski Super G fino a quattro. La voce `Live` di
Motor Raid rappresenta il Relay/live monitor: conta nel totale, è ammessa una
sola volta e non viene equiparata a un normale client giocabile.

Le prove a due istanze hanno formato il roster per tutti questi set salvo
`motoraiddx`: il clone DX stabilisce la connessione frontend 2/2 e salva
correttamente ruolo e ID, ma non porta la communication board al polling del
roster, coerentemente con il suo stato upstream non funzionante. Tutti i sette
set hanno prodotto `.srm` con `Master/ID 1` sull'host e `Slave/ID 2` sul client,
incluse le copie speculari e il layout dedicato di `indy500d`. La verifica in
gara di Sega Ski Super G utilizzava il bypass opzionale della schermata
`DRIVE BOARD TROUBLE CODE: FF`. Dal 2026-10-11 lo stub di risposta della Drive
Board supera il controllo senza premere Test; la meccanica non è emulata.

Motor Raid ha inoltre formato un roster reale 3/3 con `Master`, `Slave` e
`Live`. Gli `.srm` conservano i valori nativi 1, 2 e 3 e gli ID progressivi in
entrambe le copie EEPROM; tutti i processi sono terminati con codice 0, senza
forzature o residui. Il runner espone `--include-relay` per usare Live come
ultima istanza, sempre incluso nel totale selezionato.

Super GT 24h usa `Link Type=Car No.1 Master` sull'host e `Car No.2`…`Car No.4
Slave` sui client; `Link Max` fissa il totale da due a quattro. La prova reale
a due istanze ha formato il roster su entrambe le communication board e gli
SRM conservano `Master/Link Max 2` e `Slave Car No.2`.

Over Rev usa `Link Max=2/3/4 Links` e un `Link Type` che include ruolo e numero.
Il parent e i due cloni `overrevb`/`overrevba` hanno formato roster reali a due
istanze; in tutti e tre i casi le due copie EEPROM contengono rispettivamente
`Master CarNo.1/2 Links` e `Slave CarNo.2/2 Links`.

Manx TT non usa un numero cabinet separato: a due istanze assegna `Master` e
`Slave`; a tre aggiunge `Relay`. Sia `manxtt` sia `manxttc` hanno formato roster
reali 3/3 e salvato rispettivamente i valori NVRAM 1, 2 e 3. `manxttdx` resta
escluso perché il suo Service Menu acquisito non contiene `Cabinet Type` né
`Link Type`.

Virtual On usa `Network Link Attribute=Master/Slave` sui due programmi Twin e
il set dedicato `vonr` come terzo partecipante Relay. Poiché il Relay è un ROM
set distinto, l'adattatore identifica la famiglia Netpacket `von` invece del
nome esatto del set, seguendo la separazione tra famiglia e ruolo già usata dal
core Supermodel. Le prove reali hanno formato sia il roster Twin 2/2 sia il
roster 3/3 con `von`, `von` e `vonr`; gli `.srm` conservano Master, Slave e il
valore No Link nativo del programma Relay. Tutte le istanze si sono chiuse senza
forzature o residui. Le prove distribuite macOS/Batocera hanno inoltre mostrato
il live monitor di Motor Raid e del programma `vonr`, oltre alla schermata Relay
di Manx TT e alle visuali Relay di STCC e Sega Rally. La partita sincronizzata
con input reali resta nella sezione delle verifiche.

### 6.2 Save state — implementato

L'upstream 0.9.8 ha già introdotto `Archive`, la serializzazione delle quattro
varianti di scheda e il ripristino transazionale: magic, versione, gioco e board
sono verificati prima di modificare la macchina e un payload troncato ripristina
lo snapshot precedente. Il frontend standalone aggiunge file e slot propri;
questa parte non va portata nel core, perché RetroArch possiede slot e file.

Sono importati la serializzazione frontend-neutral e i fix-up delle quattro
schede. Il core usa un'immagine in memoria versionata, un buffer Libretro fisso
da 9 MiB compatibile con l'interrogazione anticipata di RetroArch 1.22.2 e non
introduce un secondo sistema di slot. Dopo il caricamento invalida le risorse
video derivate e ripulisce code audio, cadenza, rumble e latch input del
frontend. Stati corrotti, troncati o appartenenti a gioco/board diversi vengono
rifiutati senza alterare la macchina. Save/load viene rifiutato durante una
sessione `Linked Cabinets` perché il peer Netpacket esterno non è serializzabile.

Round-trip e riesecuzione deterministica sono verificati con ROM reali su Model
2, 2A, 2B e 2C. Il core conserva in una coda separata lo stato runtime Libretro
necessario a cambio, controlli relativi, puntamento e cadenza, mantenendo intatto
il formato macchina upstream. RetroArch macOS ha caricato uno stato VF2 nei
renderer Software e Vulkan; la prova manuale dell'utente ha inoltre confermato
save/load su Indy 500 (Model 2B). Il controllo CI impedisce di distribuire
nuovamente un binario serializzabile con
`savestate = "false"`. Venti cicli per ciascuna board verificano inoltre i
pattern run-ahead e rewind; Daytona supera la prova anche a 60 Hz.

## 7. Integrazioni derivate dall'upstream 0.9.8–0.9.13

L'analisi è allineata al commit upstream
`5ddf84ae7970a9bce1d0a17b3900d26065de1996`, tag 0.9.13 del 26 settembre
2026 nel fuso dell'autore. La versione dichiarata a quel traguardo era 0.9.13.0;
la release corrente dichiara 0.9.44.0. Resta conservata la provenienza della
base iniziale 0.9.4.

| Integrazione applicabile | Stato nel core |
| --- | --- |
| Save state 0.9.8 | Integrati serializzatori delle quattro board, contenitore transazionale e adattamento all'API Libretro; file e slot restano al frontend. |
| Daytona `start_gear=4` | Integrato con la Core Option globale `Automatic Start Gear`, abilitata per default. |
| FPS toggle standalone | Coperto da `Timing / FPS Overlay`; tasto e UI SDL esclusi. |
| Configurazione SDL dei volanti | Esclusa: dispositivi, mapping e conversione degli assi appartengono a RetroArch. |
| Drive command 0.9.9 | Integrati coda per frame, protocolli Daytona/STCC/Rally e adattamento Gamepad Rumble. |
| Metadata `games.xml` | Integrati `start_gear`, `drive_protocol`, correzioni `drive_board`, clone Daytona MAXX e aggiornamenti approvati. |
| Bilanciamento audio e timer INTENA | Integrati tramite `Enhanced Audio Balance` e fix macchina permanente. |
| Filtri xBR/ScaleFX | Integrati come filtri dei livelli 2D prima della composizione 3D. |
| Presentazione Software 0.9.10 | Esclusa: corregge la scelta OpenGL/Vulkan nel ciclo SDL; in Libretro la presentazione appartiene al frontend. |
| Fast path ROM/Work RAM 0.9.11 | Integrato sulle quattro board preservando la protezione locale Daytona MAXX. |
| Renderer Software asincrono 0.9.11 | Integrato come percorso predefinito del renderer Software, con opzione sincrona, doppio buffer e sincronizzazione per reset e Save State. La selezione automatica dei core efficienti resta interna e opera soltanto sui sistemi Linux big.LITTLE riconosciuti. |
| Logging atomico inline 0.9.12 | Integrato senza adattamenti funzionali. |
| `std::bit_cast` e definizioni Windows 0.9.13 | Integrati senza adattamenti funzionali: sostituisce quattro reinterpretazioni basate su `__builtin_memcpy` e neutralizza le macro Windows `min`/`max`; non cambia l'emulazione. |
| Link Winsock 0.9.13 | Escluso: serve a `core/net.cpp` dello standalone. Il core usa Libretro Netpacket e non apre socket di sistema. |
| SDL statico, icona/risorsa `.exe` e installazione Windows 0.9.13 | Esclusi: appartengono all'eseguibile standalone; RetroArch possiede finestra, icona, SDL e distribuzione del core. |
| GUI Lightgun Windows 0.9.13 | Esclusa: descrive Mouse e pulsanti nella UI ImGui dello standalone. Il core espone Lightgun, Mouse e RetroPad tramite le API e le Core Options Libretro già implementate. |
| CI e documentazione standalone Windows 0.9.13 | Escluse: il progetto possiede già una matrice Libretro separata con Windows x86_64 e packaging del core. |

Correzione locale completata e mantenuta opzionale: la Core Option
`i960 Round-to-Nearest-Even Fix (Restart Required)`, disabilitata per default,
può applicare a `roundr`, `roundrl`, `cvtri` e `cvtril` il comportamento
ties-to-even documentato da Intel. `Disabled` conserva esattamente il percorso
upstream; il flag resta frontend-neutral nel core i960 e viene impostato
dall'adattatore soltanto al caricamento del contenuto.

Tutte le integrazioni applicabili fino alla 0.9.13 sono recepite o escluse
esplicitamente. L'allineamento upstream non è una voce generica della roadmap:
quando `upstream/main` avanzerà, ogni modifica
applicabile diventerà una specifica voce di implementazione; le modifiche già
integrate resteranno nella cronologia e quelle non applicabili saranno indicate
esplicitamente come escluse.

## 8. TGPulse-Next Libretro Adaptation Candidates

These are SM2 follow-ups approved on 2026-10-07 after inspecting the separate
TGPulse-Next Libretro project. Its adapter code and reference workflow provide
behavioral examples; each implementation must use SM2's own machine interfaces,
game metadata and verified operator values. Existing SM2 functionality remains
the baseline. Stato: 🟢 Completato · 🟡 Parziale · ⚪ Da iniziare · 🔵 Rinviato.

Validation update, 2026-10-08: the user reports completing all requested tests
for the preceding change batch except networking. This closes the non-network
user checks for that batch. The latest Gain label correction has separate build
and automated option-check evidence; it is not attributed to that earlier user
session. TGPulse changes remain assigned to its own project chat through the
interchange file.

| Stato | Attività | Cosa resta |
| --- | --- | --- |
| 🟢 | **Frame-Per-Callback 60 Hz** | Implemented and checked through the ABI and RetroArch. User reports the preceding batch's non-network tests complete. Uses `60 Hz (Default)` and `57.524 Hz (Native Model 2)`; saved `native` remains supported. No remaining SM2 checks for this batch. |
| 🟢 | **Shared Device BIOS Lookup** | Implemented and verified in isolated RetroArch with the external device BIOS. No remaining checks for this batch. |
| 🟢 | **Per-Source Audio Gain and Mute** | Previous batch's user audio tests complete. Canonical choices are Auto, Mute, 10%–100%, with Auto default and Mute stored as `0`; old values remain readable. Latest label correction removes Absolute/Relative suffixes. Build and automated option checks pass; both installed local cores are updated. |
| 🟢 | **Shared Frontend Option Wording and Mute Format** | SM2 conventions corrected and checked: shared source names, selector ordering and saved-value format. The previous batch's user checks are complete. The latest suffix correction passed automated label checks. TGPulse timing and Gain label changes are handed off through `Docs/TGPULSE_INTERCHANGE_2026-10-07.md` for its own project chat; they are not claimed as implemented there. |
| 🟢 | **Queued Frontend Notifications** | ABI negotiation/fallback checks and isolated RetroArch evidence pass. User reports the preceding batch's non-network checks complete; the requested user notification checks are closed on that basis. |
| 🟢 | **Linked Topology on Restart and Resume** | Actual Daytona Quick Menu return and `2 Cabinets → Disabled → 2 Cabinets` transitions pass, including native offline SRAM fields and coordinated Restart. Known-peer roster recovery repaired in NetBoard v3; both installed local cores updated. Individual reboot requires coordinated native Restart. No synchronized-gameplay claim. See `Docs/NETWORK_VALIDATION_2026-10-09.md`. |
| 🟢 | **Netpacket Queue Stress Audit** | Existing burst/overflow/recovery gates pass. Isolated Daytona 2/20-second stalls show no overflow; closing/reopening the Slave and coordinated Restart recover the native link with clean process exits. Shared protocol advanced to v3; all peers must update together. Broader gameplay/platform qualification remains outside these bounded checks. |
| 🟢 | **Automatic Linked-Cabinet Presets** | Bounded preset checks pass for the qualified cases: 17 original matrix cases, the longer Motor Raid Master/Slave/Live repeat and Motor Raid Deluxe's approved automatic Twin default. Existing saves retain precedence and Deluxe remains selectable. Manx TT Relay initialization is now qualified separately in section 9 for the parent and Revision C; synchronized gameplay remains outside this bounded preset qualification. SRAM fields, native handshake and gameplay remain distinct. See `Docs/NETWORK_VALIDATION_2026-10-09.md`. |
| 🔵 | **True 3D Widescreen** | Consider an opt-in expansion of the 3D view after a renderer and per-game native-widescreen review. Define 2D composition, Software behavior and performance checks before implementation. |

## 9. Upstream Integration Candidates

Reviewed against `upstream/main` at `3c9e79a76272b736e720377e8ec67c2b1c599ce6`
on 2026-10-10. Treat all open changes as one candidate set under the
[Upstream-First Libretro Porting Manifesto](Docs/UPSTREAM_PORTING_MANIFESTO.md).
The historical full-import base is 0.9.13; current reconciled upstream coverage
is 0.9.44. The latest review adds CPU/coprocessor,
SCSP and gun candidates from 12 additional commits; standalone GUI/localization
changes are excluded. See [Upstream Review](Docs/UPSTREAM_REVIEW_2026-10-10.md). The user approved all compatible candidates on 2026-10-07. Integrate
them after validation, adapting frontend-facing parts to Libretro. Place work
requiring additional comparison with port-specific behavior at the end. Ask for
a choice only after documenting a real conflict with published settings or a
useful local behavior. Status: 🟢 Complete · 🟡 Partial · ⚪ Not Started · 🔵
Deferred.

Exclude MAME TCP/Windows cabinet outputs, standalone SDL/ImGui controls, Raw
Input/evdev device ownership and wheel-specific force-feedback output without
a supported Libretro equivalent. Do not treat upstream behavior changes as
port regressions solely because old hashes differ.

| Stato | Attività | Cosa resta |
| --- | --- | --- |
| 🟢 | **ROM Loader and Game Support** | Split-BIOS metadata/diagnostics `600f1c8` and preliminary Power Sled support `e8d96c1` integrated. System/sibling/embedded precedence and existing Daytona/Desert Tank I/O preserved. macOS/Linux checks, three-game old/new and embedded/split video/PCM comparisons pass; all 87 sets recognized. Power Sled/Master boot matches pristine upstream. Both installed cores and games.xml updated. Gameplay/network limits remain explicit; the subsequent Power Sled validation resolves Main/Relay identification and local replay defects; see `Docs/UPSTREAM_ROM_LOADER_PACKAGE_2026-10-08.md`. |
| 🟢 | **Sound 68000 Timing** | Required sample-locked scheduler from `def088c`, stall evaluation-order fix `8e1e7c3` and fixed waits `71a81e3` integrated. Exact isolated sound-board traces match pristine upstream; four-board Libretro/headless video/PCM/NVRAM and five-title old/new state tests pass. That package introduced format 5; the current writer is format 8 and reads formats 4–8, with fixed Libretro size unchanged; see Save State Compatibility. macOS/Linux checks and installed-core VF2 RetroArch gameplay pass; both local copies updated. Whole-machine pristine comparisons still reflect other unintegrated changes and are not claimed identical. See `Docs/UPSTREAM_SOUND_TIMING_PACKAGE_2026-10-08.md`. |
| 🟢 | **i960 and Bus Wait-State Reconciliation** | Integrated CPU/SHARC fixes `8a49096`, Virtual-On tile/texture waits `7080210` / `e36f757`, and Sega per-area wait decoding `1987d82` on all four boards. Published Round-to-Nearest-Even option keeps its label, values and disabled default; no additional selector needed. Opcode/rounding/wait checks and five-title old/new state replay pass. Pristine Virtual-On CPU, cycles, PCM and NVRAM match; all frame differences fit the previously integrated gamma correction. macOS/Linux builds and checks pass; installed-core Virtual-On RetroArch Vulkan 2x gameplay is verified. Both installed cores and games.xml updated. See `Docs/UPSTREAM_I960_PACKAGE_2026-10-08.md`. |
| 🟢 | **Audio Balance Reconciliation** | Integrated upstream flat SCSP profiles, original-board attenuation and Top Skater DSB2 balance. Enhanced Audio Balance remains Enabled by default, with every Gain defaulting to Auto. Auto follows the enabled game profile; manual percentages bypass it for that source, while Music Volume and hardware mixer routes remain applicable. Removed obsolete VF2 per-slot rebalance without changing the published state layout. macOS/Linux checks, synthetic SCSP/MultiPCM/MPEG tests, pristine sound/Daytona comparisons and five-title state tests pass. Installed-core Top Skater RetroArch Vulkan 2x gameplay verified. Both installed local cores updated. See `Docs/UPSTREAM_AUDIO_BALANCE_PACKAGE_2026-10-08.md`. |
| 🟢 | **Virtua Cop Save State Replay Review** | Fixed the first/repeated Software mismatch and six normalized MultiPCM bytes. Format 7 saves persistent geometry registers/RAM; fixed Libretro capacity is unchanged and formats 4/5/6 remain readable (their missing geometry state cannot be recovered). Strict 910-frame sweeps, fresh-process Virtua Cop gameplay video, five-title old/new video/PCM and state checks, historical loads and macOS/Linux builds pass. Installed-core RetroArch gameplay round-trip restores the complete image exactly, resumes and exits cleanly. Runner now verifies pause state and uses three comparison steps for 30 Hz geometry plus asynchronous presentation. Both local core copies updated. See `Docs/VIRTUA_COP_SAVE_STATE_REPLAY_2026-10-08.md`. |
| 🟢 | **Rendering and Video Options** | Approved upstream renderer changes are accounted for and integrated. Consolidated four-board Software/Vulkan/OpenGL/GLES review passes with actual frontend SRAM/CRC evidence; Mesa GL/GLES match pixels, PCM and NVRAM. Fixed geometry-buffer abandonment after OpenGL context loss; both VF2 API loss/recreation cases match uninterrupted baselines. Old/new Vulkan control and VF2 RetroArch Vulkan 2× gameplay pass. Both installed local cores updated. Cross-rasterizer/driver pixel differences and small cross-platform PCM differences are quantified separately; no Windows/Batocera requalification claim. See `Docs/RENDERING_REVIEW_2026-10-09.md`. |
| 🟢 | **Save State Compatibility** | Compatibility audit complete: current writer 8, reads 4–8, unchanged 9 MiB buffer and 96-byte frontend tail. Retained four-board/DSB2 round-trip, replay, run-ahead/rewind and historical fresh-process loads pass; three Power Sled video/PCM continuations rechecked exactly. Current installed-core Virtua Cop RetroArch slot round-trip restores the game region exactly, resumes and exits cleanly. Legacy omissions, platform dependence and external Linked Cabinets restrictions remain explicit. Manual/design corrected; both installed cores already match the build. See `Docs/SAVE_STATE_COMPATIBILITY_REVIEW_2026-10-09.md`. |
| 🟢 | **Power Sled Launcher Ride Defaults And Relay Order** | Launcher correction originally qualified Main Red / Slave Silver after the prior Silver/Red startup failure; the subsequent Master Silver Identity integration now qualifies both color orders. Relay now follows Slave and uses `_relay`; controller indices and visible layout remain role-based. Old-session config/SRM lookup matches the ROM, and launcher-only resume tolerates absent SRMs while preserving available saves. Six ROM-free mapping/resume checks and fresh installed-core startup pass. Bounded resumed RetroArch replay reaches advancing races on Main and Slave and LIVE camera on Relay; all three final SRMs exist, clean exits and no residual processes. Original user saves/options preserved. Physical-controller proof remains separate. See `Docs/POWER_SLED_LAUNCHER_CORRECTION_2026-10-10.md`. |
| 🟢 | **Power Sled Network Roles And Linked Launcher** | Current F14 convention: playable programs use -1 manual or colors 1 Silver / 2 Red / 3 Black / 4 Yellow (default 1); dedicated Relay uses r. Generic launcher uses name[:ANRS[:GAMEPAD]], canonical r with l/s aliases, one-based pads and explicit empty pad fields for no assignment. Roles follow ROM identity; resolved automation/topology replace saved network selections while other Core Options and SRAM persist. Generic fitting, Relay-last folders, no default game and no compatibility checks retained. See `Docs/LINKED_CABINET_LAUNCHER.md` and the current network report; dated 2026-10-09 reports retain historical tokens only. |
| 🟢 | **Upstream v0.9.44 Cornering Rumble Deadzone** | User-approved Libretro adaptation implemented on 2026-10-11. Cornering rumble uses frontend-processed steering. Following user review, the former 7000-unit threshold is replaced by a deliberate 5% rumble-only minimum; remaining travel is rescaled to the existing peak strength. Existing peak strength, impact/kick behavior, 12-frame tail and stop/disable behavior are preserved. Small travel, zero, symmetry, negative full travel and existing decoder checks pass; normal core rebuilt and installed. Stick/wheel/aim deadzone configuration stays in the frontend; no duplicate Core Options. Standalone v0.9.44 GUI/config changes were reviewed, not imported. Cross-core candidate retained in `Docs/RUMBLE_FRONTEND_DEADZONE_INTERCHANGE_2026-10-11.md`. |
| 🟢 | **SCSP, MultiPCM and Music** | Audio implementation and native Batocera qualification pass: VF2 SCSP filter on/off preserves pixels/SRAM and attenuates 10–20 kHz output by 10.93 dB; Daytona MultiPCM and Top Skater mixed audio pass. Top Skater Sound Test BGM 1 runs 312.912 seconds with SCSP Mute, sustained output and nine waveform passages repeating after 262.908 seconds; repeated PCM is not bit-identical and no decoder-branch trace is claimed. All eight frontend runs exit 0; tested files remain unchanged. EAB Enabled and Gains Auto retained. Following positive listening checks, SCSP Output Low-Pass Filter now defaults to Enabled by user decision on 2026-10-11; explicit saved Disabled remains respected. The user confirms the requested listening checks successful on 2026-10-11; audio operator qualification is closed. Subsequent Windows/Batocera qualification in the open-verifications section supersedes the former platform test gate; no further platform-specific technical check remains. See `Docs/NATIVE_BATOCERA_AUDIO_VALIDATION_2026-10-09.md` and `Docs/UPSTREAM_AUDIO_PACKAGE_2026-10-08.md`. |
| 🟢 | **Ski Super G Drive Board Startup** | Missing PE-command/PD-response wiring identified from the program. Stationary acknowledgements now pass the native startup check without Test; obsolete timed bypass removed. Command/reply, reset, saved-latch restoration and fresh native boot pass. Real RetroArch Vulkan startup qualified separately; normal core deployed. Full drive firmware and mechanical emulation remain outside scope. See `Docs/SKI_SUPER_G_DRIVE_BOARD_STUB_2026-10-11.md`. |
| 🟢 | **Game Control Reconciliation** | House of the Dead P2 trigger and serial gun edge corrections integrated. Top Skater keeps its independent axes, adds trigger aliases/D-Pad steering and approved Progressive default with Linear selectable. Ski Super G channel order/polarity already match upstream. Independent Swing/Inclining axes are retained as requested. Inclining adds LT/RT secondary bindings on 2026-10-11, proportional travel, RT-minus-LT and strongest-input arbitration matching Top Skater. No coupling option is planned. Exact upstream response equivalence remains unverified. macOS/Linux input checks, three-title baseline/state comparisons and pristine HOTD comparison pass. Normal installed core and games.xml updated; the dev copy remains absent. The user confirms the requested remaining control checklist successful on 2026-10-11: House of the Dead, Top Skater and Ski Super G. Operator control qualification is closed; exact pristine response equivalence remains a documented limit, not a further test gate. Native frontend results and limits: `Docs/UPSTREAM_CONTROLS_PACKAGE_2026-10-08.md`. |
| 🟢 | **Drive Board and Rumble Reconciliation** | Imported neutral upstream decoder `868dce7` with Daytona/Rally prerequisites; Indy 500 and Over Rev families select the later board protocol. Libretro Push/Kick adaptation preserves existing Gamepad Rumble labels/defaults, cornering vibration, lifecycle stops and state layout. Exhaustive pristine decoder comparison, five-title old/new state/baseline tests, pristine Indy/Over Rev machine comparisons and macOS/Linux checks pass. Both installed cores and games.xml updated. Native frontend evidence and remaining physical rumble validation: `Docs/UPSTREAM_RUMBLE_PACKAGE_2026-10-08.md`. Over Rev board effects require HARDWARE TYPE = SEGA STCC. SEGA STCC is now the Hardware Type core default and Automatic Initial NVRAM Setup override for Over Rev and both clones (2026-10-09). Native acquired defaults, existing saves and explicit saved option choices remain preserved. EEPROM mirror/checksum, manual selection and installed-core fresh/existing-save checks pass; a fresh automatic setup reaches an active race. User confirms physical rumble checks successful on 2026-10-11; rumble operator qualification is closed. See `Docs/OVER_REV_HARDWARE_DEFAULT_2026-10-09.md`. |
| 🟢 | **Power Sled Main Audio ROM Reconciliation** | Integrated matched Slave sound program/samples for Main: search Main first, then split parent fallback with CRC verification; obsolete Relay audio chips removed from Main requirements. Known-name selection requires matching maincpu chips, preserving existing Main archives; incompatible names retain CRC-based fallback. ROM-free parent/local precedence, missing/corrupt rejection, Relay and recognition checks pass; normal core/headless build. Installed-core triplet using original archives reaches race HUD on Main/Slave with audio on all units (PCM peaks 4391/3033/4309). Main emits sustained late-race PCM. Native links, three clean exits and SRAM/ANS integrity pass. Both cores and configured/fallback system databases updated with backups and matching hashes. Original Main sound fidelity and pre-change Main Save State audio remain unqualified; physical/full-race checks stay in preliminary validation. See `Docs/POWER_SLED_MAIN_AUDIO_INTEGRATION_2026-10-09.md`. |
| 🟢 | **Power Sled Automated Handlebar and Race-Cycle Checks** | Installed-core Semi Auto race reaches checkpoints, Time Extension and Game Over. Independent trigger sweeps in a private passive RetroArch diagnostic verify channels 1/3/5/7, opposite native responses and handle/rider isolation on Main and Slave; Relay stays neutral. Three completed sessions / nine clean native-linked exits, ADC delivery, SRAM/ANS integrity, unchanged calibration and PCM pass. Sparse observation was superseded by per-frame reads. Normal source and both installed cores retain their original verified hashes. Physical handling and original sound fidelity remain in preliminary validation; post-race recovery and Manual finish/ranking are qualified in the separate entries below. See `Docs/POWER_SLED_HANDLEBAR_AND_RACE_VALIDATION_2026-10-09.md`. |
| 🟢 | **Power Sled Post-Race Recovery** | Installed-core Main / Relay / Slave session reaches Game Over and black/SEGA, then a second Semi Auto race on Main and Slave with changing clocks, course movement and Time Extension. Three clean exits, native links, SRAM/ANS integrity and unchanged calibration pass. No reset or core change required. Runner window wait is bounded at 15 seconds after the first launch attempt timed out at 3. Manual finish/ranking is now qualified separately; broader post-race paths remain preliminary. See `Docs/POWER_SLED_POST_RACE_RECOVERY_2026-10-09.md`. |
| 🟢 | **Power Sled Manual Finish And Ranking** | Installed-core Main / Relay / Slave session selects Manual / Professional through the previously measured handlebar zone, completes the course and displays `1st` on Main/Slave plus Relay ranking `1ST 02:13:67 SILVER`, followed by Game Over. Dense end-sequence captures resolve the brief result missed by the first sparse run. Native links, clean exits, uninterrupted replay, PCM, SRAM/ANS integrity and unchanged calibration pass. No emulation change required. Reusable Manual replay and isolated coexistence flag added to the existing RetroArch runners. Physical handling and acoustic fidelity remain outside this qualification. See `Docs/POWER_SLED_MANUAL_VALIDATION_2026-10-10.md`. |
| 🟢 | **Power Sled Preliminary Validation** | Fixed ambiguous Main/Relay ROM identification and local communication queue restore (format 8; reads 4/5/6/7; fixed buffer unchanged). All three distinct sets pass exact replay, run-ahead, rewind and fresh-process video/PCM checks. Five-title regressions, historical loads and macOS/Linux builds pass. Both installed cores updated. Installed-core RetroArch Vulkan 2×: parent and Relay show SYSTEM SHUTDOWN; Main reaches a 3D GAME OVER scene; parent/Main are silent, Relay emits some PCM. Linked RetroArch probe on 2026-10-09: Main Red / Slave Silver reaches mode selection and boarding/track introduction; Relay/Slave emit PCM. Twelve program exits and native links pass. A playable race, steering response and sound correctness remain unverified; all sets stay preliminary. P2 Entry/Call and independent handlebar channels 5/7 are now implemented and checked; disabled Port 2 restores native rest values. Follow-up replay entered Test Menu unexpectedly; direct input reached mode selection, but no playable race was confirmed. The normal launcher runs no Test/Service automation. Four further direct-input runs pass native links, 12 clean exits, SRAM CRCs and ANS Red/Silver persistence. No playable race verified. A temporary adapter trace confirms correct P1/P2 Entry and Test masks; simultaneous program inputs can return to Test Menu before any explicit Test pulse, while Slave-only input does not reproduce that screen in the retained window. Original source and both installed-core hashes restored exactly. Native program diagnosis now resolves unexpected Test: role-gated Main/Relay P2 Entry sends command 0x1000 and deliberately selects Test state 15; I/O and adapter bits are correct. Four further diagnostic sessions / 12 clean exits qualify selection state 5 and boarding state 6 on all units; a start pulse during local confirmation is overwritten in the same frame. No race verified. Operator command 5 now qualified and integrated: Port 1 Start on Main/Relay adds native IN1 0x10 while retaining existing bindings. A three-unit diagnostic run advances all programs to race state 7; Main and Slave show the race timer, position and course movement. Normal installed-core verification passes the same operator sequence without instrumentation: race HUD, changing timer and advancing course on Main/Slave. Both runs pass native links, six clean exits and SRAM/ANS integrity. Subsequent Main audio diagnosis and production integration are complete: corrected files load Main first with Slave parent fallback, and the installed-core original-archive triplet emits Main/Relay/Slave PCM during the race. Main archive recognition, native links and SRAM/ANS integrity pass. Automated follow-up now verifies independent ADC/handlebar command responses and the Semi Auto race cycle through checkpoints, Time Extension and Game Over; see `Docs/POWER_SLED_HANDLEBAR_AND_RACE_VALIDATION_2026-10-09.md`. Follow-up installed-core session also qualifies a second Semi Auto race after Game Over and black/SEGA without resetting or restarting any program; see `Docs/POWER_SLED_POST_RACE_RECOVERY_2026-10-09.md`. Manual / Professional selection, course completion and native final placement are now qualified on Main/Slave, with a matching Relay ranking; see `Docs/POWER_SLED_MANUAL_VALIDATION_2026-10-10.md`. Remaining: physical-controller handling and sound fidelity; broader post-race paths remain outside this bounded qualification. Earlier no-race results are historical. See `Docs/POWER_SLED_OPERATOR_START_2026-10-09.md`. Source restored exactly; normal build and installed cores match. See `Docs/POWER_SLED_NATIVE_INPUT_DIAGNOSIS_2026-10-09.md`. See `Docs/POWER_SLED_PRELIMINARY_VALIDATION_2026-10-08.md` and `Docs/POWER_SLED_LINKED_GAMEPLAY_2026-10-09.md`.  Current roadmap closure: the user considers the entire Power Sled package closed on 2026-10-11, superseding the earlier pending checks above. Retain evidence/limits; reopen only for a newly reported issue. |
| 🟢 | **Power Sled Main/Relay/Slave Communication** | Libretro mixed-program family and distinct Main/Relay/Slave handshake integrated; Disabled / 3 Cabinets offered. Actual RetroArch ring verified on all units with native IDs Main 1/3, Relay program 3/3, Slave 2/3, matching the MAME reference. Test Menu and Game Assignments accessible on all three; isolated processes exit 0 without forced cleanup or residue. Existing MAME-derived protocol and offset 0x180 reused unchanged. Communication/menu prerequisite for Phase 2 passed; gameplay and remote/larger topologies remain unverified. See `Docs/POWER_SLED_SERVICE_MENU_CAMPAIGN.md`. |
| 🟢 | **Power Sled NVRAM Settings and Initial Setup** | Approved fields implemented: five Checkpoints and Motion Angle on all three programs, Ride ID Silver/Red/Black on Main and Slave; native defaults and existing per-game conventions retained. Three independently qualified initial templates integrated; existing SRAM/native files keep precedence. Every selector value, three-copy writes, blank/discordant rejection, idempotence and unrelated-byte/EEPROM preservation pass direct checks. Five RetroArch stages / 15 program records verify initial seeding, manual overrides, fresh SRAM reload, native import and SRAM precedence over conflicting native files. YAML, catalogue and workbook reconciled; both installed local cores updated. Country/Relay semantics and conditional ID assignment are deferred separately; linked gameplay remains in preliminary validation. See `Docs/POWER_SLED_NVRAM_OPTIONS_2026-10-09.md`. |
| 🟢 | **Power Sled Country Semantics** | Closed by user direction on 2026-10-11 with the current implementation. No further interpretation work is scheduled. Reopen only for a newly reported issue. |
| 🟢 | **Power Sled Factory ID Assignment Logic** | Closed with the Power Sled package by user direction on 2026-10-11. Current four-color selectors, native encoding and separate roles are retained. Historical factory-policy reconstruction is not required; reopen only for a newly reported issue. |
| 🟢 | **Power Sled Main Program Reconstruction Review** | Built a private Slave-derived Main with adapted mode/role/complement/index initialization. Paired installed-core RetroArch replays reach advancing Main/Slave races, Relay LIVE and nonzero PCM on all units. Six clean exits, native links, SRAM identity/CRC/ANS, unchanged paired calibration/EEPROM and no runtime reset pass. Extended program comparison attributes remaining observed differences to initializer, address relocation and trailing ROM fill; no extra Slave-only Main logic or improvement is demonstrated. Keep the current production Main; the diagnostic candidate is retained. Factory fidelity and cross-base saved-state compatibility are not qualified. Bounded analysis complete; see `Docs/POWER_SLED_MAIN_RECONSTRUCTION_REVIEW_2026-10-10.md`. |
| 🟢 | **Power Sled Main Ride Caption** | Both Main identity selectors now read the native NVRAM Ride color, displaying `THIS IS <COLOR> RIDE` while preserving the separate native role. Silver, Red and Black captions verified in RetroArch; nine clean native-linked exits, Main role and SRAM identity/CRC/three-copy Ride checks pass. Staged and both installed databases updated with backups and matching hashes; core binary unchanged. Caption qualification complete; restart linked instances to load the database. See `Docs/POWER_SLED_MAIN_RIDE_CAPTION_2026-10-10.md`. |
| 🟢 | **Power Sled Main First-Person Sled Color** | Main's first-person resource selectors now read NVRAM Ride color while retaining its original race index and native role. Paired RetroArch observation reproduces black with Main Red before the change and red after it; advancing races, nine native-linked clean exits, Main role, SRAM identity/CRC/Ride, unchanged paired calibration/EEPROM and PCM pass. Requested Slave-derived Main comparison also reproduces black with Ride ID Red; changing program base does not solve the color issue. That extra color observation does not qualify timer behavior. Staged and both installed databases updated with backups/hash checks; core binary unchanged. Remote/third-person appearances are outside this qualification. See `Docs/POWER_SLED_MAIN_SLED_COLOR_2026-10-10.md`. |
| 🟢 | **Power Sled Relay-Derived Master** | Approved simplification implemented: Relay is the sole Main basis; donor selector and alternate Slave loader/patch adapter/check target removed. Current patched comparison supports identical aligned routines with different initializer layout; Relay needs fewer initializer modifications. Caption/color/selection patches, audio fallback, roles and NVRAM retained. Actual V2 registration removes only the donor option; 300-frame old/new image/PCM/native files match even with obsolete saved slave value. State round-trip, legacy Relay load and pre-mutation rejection of Slave-derived development states pass. Both installed cores updated with backups/hash checks; actual installed ABI matches the tested build and all four databases remain equal/unchanged. Existing linked-race/recovery evidence applies to the unchanged Relay program; no new gameplay campaign claimed. See `Docs/POWER_SLED_RELAY_ONLY_2026-10-10.md`. |
| 🟢 | **Power Sled Master Routine Analysis** | Followed native mode/FG, Master operator admission and main-loop scheduling, Master packet pointers, roster and state callbacks in both donors. Eleven anchored instruction walks and 38 callback entries match after relocation; 595 changed control targets verified exactly. Current initialization already selects the inspected Master paths; no additional dormant Master-only engine is identified. Two unbound shared operator commands are documented without assigning unverified control labels. Static analysis only; no new runtime qualification or core change. See `Docs/POWER_SLED_MASTER_ROUTINES_2026-10-10.md`. |
| 🟢 | **Power Sled Main Color-Dependent Presentation** | Reproduced the missing mode-selection 3D scene: Master `0x0200` selects no native drawing callback. Main now reads NVRAM Ride only at that visual selector in both donors. Paired private RetroArch captures restore the scene and Red sled while preserving sampled Master role/count/index; both normal installed-core donor sessions reach linked races. Twelve clean exits, native links/roster, SRAM identity/CRC/three-copy Ride, paired calibration/EEPROM and PCM pass; focused ROM-free checks and exact candidate/production patch maps pass. Both installed cores and staged/configured/fallback databases updated with backups and matching hashes. Other placement selectors show no demonstrated defect and remain unchanged; no new options/bindings or state format. Bounded activity closed; Red visually qualified, factory fidelity remains unqualified. See `Docs/POWER_SLED_MAIN_PRESENTATION_2026-10-10.md`. |
| 🟢 | **Power Sled Operator Commands And Display Layout Analysis** | Native input qualifies `0x0100` Emergency Stop and existing B Entry recovery on Main/Slave/Relay; separate original-race recipe qualifies `0x0300` exit flag and state-4 return after 180 sampled machine frames on all three programs. Six normal qualifying exits, native links/roster, preserved role/count, SRAM identity/CRC/Ride, unchanged calibration/EEPROM and PCM pass. Provisional fixture errors retained and excluded; no shutdown in qualifying sessions. Remaining selectors feed roster-derived geometry projection/window placement; no further visible defect or dormant Master-only engine is demonstrated. Production sources restored exactly; normal and both installed cores retain qualified hashes. No new options/bindings or production patches. State-4 return is qualified; final captures are black on all three programs, so this short session does not demonstrate a Master-specific failure or qualify title/attract recovery and another race. Subsequent recovery/donor qualification is recorded separately. Original switch labels, physical devices and factory fidelity remain outside qualification. Bounded analysis closed; see `Docs/POWER_SLED_OPERATOR_AND_LAYOUT_ANALYSIS_2026-10-10.md`. |
| 🟢 | **Power Sled Patched Donor Residuals And Native Recovery** | Current Relay/Slave Main patches compared: relocated addresses and equivalent initializer storage/helper layout, with no unexplained aligned difference or Slave-exclusive Master routine found; not a formal whole-program proof. Two isolated RetroArch sessions qualify native first race, exit, state-4 return, fresh selection/boarding and second advancing race with both donors. Longer Slave-donor session also captures Main POWER SLED title before selection. Six native-linked clean exits, preserved roles/count, SRAM identity/CRC/Ride, calibration/EEPROM and PCM pass. Prior short final captures were black on all three programs; no permanent Master-specific defect is demonstrated and no additional production patch is justified. Normal/installed cores and all databases unchanged; no new options/bindings. Factory fidelity, all colors/layouts and full-course completion outside qualification. Bounded analysis closed; see `Docs/POWER_SLED_DONOR_RESIDUALS_2026-10-10.md`. |
| 🟢 | **CPU And Coprocessor Performance** | Imported `760a556`: direct i960 ROM/work-RAM fetch on all boards, direct MB86235 program fetch/empty-FIFO wait skipping and SHARC settled host-flag wait skipping. Previous/new headless ports each match their pristine revision on all seven checks for Daytona, VF2, Sega Rally and HOTD at 1,800 frames. All four ABI state round-trips and old format-10 state continuations pass; state format unchanged. Matched 1,800-frame ABI replay process times decrease 6.9% (VF2) and 41.1% (HOTD); these include callbacks/startup and are not frontend FPS. VF2 RetroArch gameplay passes; both installed cores updated/hash/ABI checked. Local package closed. See `Docs/UPSTREAM_CPU_SCSP_PACKAGE_2026-10-10.md`. |
| 🟢 | **SCSP Pitch Modulation Accuracy** | Imported `ec9c3ac` depth-index-3 correction (6 → 8); unused `FM_FRAC_DIV` was already absent. ROM-free depth 0/2/3/4 PCM matches both pristine revisions exactly; only depth 3 changes. Sega Rally boot audio changes exactly as its pristine reference; other matched output and old-state continuations pass. Existing Gain/EAB/filter conventions preserved; LFO state continuation and corrected legacy sound-timing fixture pass. Both local installed cores updated. Local package closed. See `Docs/UPSTREAM_CPU_SCSP_PACKAGE_2026-10-10.md`. |
| 🟢 | **Gun Aim And Reload Reconciliation** | BEL upstream tables integrated and legacy RAM calibration seed removed. Initial calibration now uses the operator-verified MIN 00 / DEL FF preset; existing saves retain precedence and need recalibration if based on the old mapping. RC2/Rev. A expose Custom (SM2-Emu) / Linear (MAME); HOTD Prototype exposes Custom (SM2-Emu) / Linear (MAME). Both selectors default to Custom (SM2-Emu) per latest approval. Core/headless/input/save checks pass; BEL RetroArch Vulkan 2,300-frame scripted gameplay passes. Normal installed core and configured games.xml updated with verified hashes. BEL, RC2 and HOTDP are closed by user direction on 2026-10-11; no additional operator check is scheduled. Retain automated/runtime evidence and its limits. On 2026-10-11 the configured personal RetroArch save/state directories were checked: no BEL SRM, native NVRAM or old save state remains, so a fresh launch can seed the new calibration. Upstream calibration evidence and isolated validation saves are retained. Existing 5% Mouse-only reload policy retained. See `Docs/GUN_MAPPING_INTEGRATION_2026-10-11.md`. |
| 🟢 | **Manx TT Relay And Gameplay Qualification** | Counted role-3 Relay now has a positive native ID and includes its own status slot while preserving the received slot train; pure forwarding passed boot but blocked race selection. Normal-core parent triplet and Revision C pair/triplet qualify two-rider races, Time Up/ranks, LIVE camera and subsequent attract/race progression at the default 60 Hz cadence. Eight final linked instances exit cleanly; native IDs/count, persisted presets/CRC and no board restart pass. Installed-core DX single program passes the operation tutorial and reaches an 8-rider race using normal bank/brake/Start/throttle inputs; no extra mapping, setting or calibration edit. Generic/Power Sled rings, core/headless/standalone builds and exact old/new 600-frame offline image/PCM/native files/CPU/cycles pass. Both installed cores updated with backups/hash checks. An initial Revision C pair timer anomaly did not recur in the bounded repeat or final triplet; its cause is not claimed fixed by the Relay change. Bounded local campaign closed; physical-device/audio fidelity, every-course full-lap completion and extended stress remain outside this qualification. See `Docs/MANX_TT_GAMEPLAY_VALIDATION_2026-10-09.md`. |

| 🟢 | **Manx TT Cabinet Audio And Deluxe Sound Board** | Implemented the approved always-visible Enabled / Disabled selector (Enabled default). Revision C/D follows validated current NVRAM, loads only CRC-checked audio regions from the selected archive or adjacent Manx TT sets, and retains original audio with a notification when donors are incomplete. Additional M1 audio follows Deluxe; `manxttdx` always connects it when available. No set split or main-program change. Focused checks cover committed/partial EEPROM changes, serial fanout, one populated MultiPCM, mixing, Gain and exact Save State continuation. Production D/Twin and private-stub D/Deluxe RetroArch replays pass at 6,600 frames; the additional board receives native commands and generates PCM. Format 9 keeps formats 4–8 readable. Both local installed cores are updated and hash/ABI checked; the system database matches. See `Docs/MANX_TT_CABINET_AUDIO_2026-10-10.md` for evidence, installation and limits. |
| 🟢 | **Manx TT Deluxe AMS Acknowledgement Stub** | Production stub follows current native NVRAM Deluxe for Revision C/D; Twin retains P2 input. The Deluxe-only program always connects it. Reset, cabinet transitions and incomplete-handshake Save State restore pass. Normal-core RetroArch: D Deluxe reaches a race at 6,600 frames; C Deluxe and original DX reach the title at 2,300 frames. EEPROM/container CRCs pass and C/D EEPROM is unchanged. Twin old/new image, PCM and NVRAM are identical. Format 10 reads 4–9; previous installed format-9 state and all four board round-trips pass. Both installed core copies updated with backups/hash/ABI verification. This acknowledges native boot; mechanics/feedback are not emulated. See `Docs/MANX_TT_MOTION_STUB_2026-10-10.md`. |
| 🟢 | **Manx TT Native Service Menu Cabinet Transitions** | Installed-core Revision C/D each complete Twin → Deluxe → Twin through native Game Assignments, with fresh-process load between directions. Menu values, normal return, matching audio/additional-board transitions and native/container CRCs pass. Only Cabinet Type, native counter and checksum change in EEPROM. Parent recipe/YAML corrected to current R3 Test / L3 Service; clone bindings preserved. No emulation change or calibration acquisition. See `Docs/MANX_TT_SERVICE_TRANSITIONS_2026-10-10.md`. |
| 🟢 | **Power Sled Master Silver Identity** | Reconstructed Main now publishes rider color separately from native command role `0x0200`; shared roster, both distribution counts and rider-packet mapping use it, and Main's local index/panorama follow Ride ID. Initial prototypes passed state 7 but failed with black 3D/Reverse; correcting the inconsistent cabinet counts restores visible racing. Main Silver / Slave Red / Relay and Main Red / Slave Silver / Relay both qualify in bounded RetroArch replay with correct first-person colors and progressing countdowns. Original boarding constructs four panoramic actors; Black 03 in multiple views does not alone establish duplicate riders. Eighteen observer and nine normal-core program records preserve roles, native links, valid SRAM/three-copy Ride and calibration/EEPROM; final runs exit cleanly. Exact tested XML patches deployed with backups; normal installed core is unchanged and the dev copy remains absent. Other games/options/controls are unchanged. Factory Master fidelity, unrestricted colors/topologies, full-course and physical-device proof remain outside this qualification. See `Docs/POWER_SLED_MASTER_COLOR_2026-10-10.md`. |
| 🟢 | **Power Sled Four Rider Topologies And Physical Layout** | Silver / Red / Black / Yellow Service Menu and NVRAM Settings are implemented for Main, Slave and Relay after independent Phase 1 cycles and one complete Phase 2 recipe: eight clean native commit/reload stages / 24 records. Main/Slave ANS adds 4 Yellow; Relay retains only relay. Production registration accepts 2/3/4/5 instances and the roster accepts one Main, one to three Slaves and optional final Relay. Focused transport checks cover four riders with/without Relay; diagnostic reporting uses the actual count. Normal installed-core four-rider replay reaches a visible linked race without Relay and verifies ANS 1–4, distinct native colors, count 4, clean exits and preserved calibration/EEPROM; absent Master content fallback is exercised. Normal core and both databases updated with backups/hash checks; dev remains absent. Previous private linked races qualify both topologies. Physical four-screen Silver / Red / Black / Yellow panorama alignment remains for user review; larger groups keep the generic two-column layout. Standalone and full-course/factory fidelity remain unqualified. See `Docs/POWER_SLED_YELLOW_AND_MASTER_ARCHIVE_REVIEW_2026-10-10.md`.  Current roadmap closure: the user considers the entire Power Sled package closed on 2026-10-11, superseding the earlier pending checks above. Retain evidence/limits; reopen only for a newly reported issue. |
| 🟢 | **Power Sled Optional Master Archive** | Implemented frontend-neutral rom_fallback metadata: valid Master chips retain precedence, Relay supplies missing program/graphics, Slave supplies missing corrected audio. Master identity, patches, saves and required chip CRCs are preserved. The established launcher creates an owned empty content entry when powsledm.zip is absent and writes nothing into the ROM collection. Actual RetroArch Phase 1/2 runs omit Master; focused loader/launcher checks cover empty/missing Master, corrupt or missing donor data and ordinary missing-game rejection. No donor selector or development-core deployment. See `Docs/POWER_SLED_YELLOW_AND_MASTER_ARCHIVE_REVIEW_2026-10-10.md`. |
| 🟢 | **Power Sled Two Cabinet Launch** | Corrected omitted Linked Cabinets value 2 and stale minimum 3; registration/parser now accept 2–5. Existing roster already supports one Master and one Slave without Relay. Normal installed-core replay with ANS 1 Silver / 2 Red reaches visible races on both units, native count 2, ready roster, valid save identity/CRC and three-copy colors, unchanged EEPROM and clean exits without residual processes. Save RAM/Netpacket and eight launcher checks pass. Normal core updated with backup/hash verification; dev remains absent. Same user command is valid. See `Docs/POWER_SLED_TWO_CABINET_FIX_2026-10-10.md`. |
| 🟢 | **Power Sled Music Routing Diagnosis** | Matched installed-core Master–Slave and Master–Slave–Relay recordings qualify races and audio on all five instances. Relay alone reproduces the earlier retained race soundtrack: normalized waveform correlation 0.978823 versus at most 0.0392 on riders. Main/Slave retain their rider sound ROMs/effects; Relay-specific sound tasks and ROMs are not automatically transferred when Relay is omitted. Relay is optional for racing; its soundtrack requires that instance when Relay Audio On Master is Disabled. The subsequent optional Master integration is tracked below. Source Gains Auto and frontend mute/volume are correct; Music Volume only scales MPEG hardware and is inapplicable here. Normal core/database unchanged; valid SRAM/three-copy Ride, native links and clean exits/no residue pass. Diagnosis closed; the optional two-instance music integration is now qualified separately. See `Docs/POWER_SLED_MUSIC_ROUTING_2026-10-10.md`. |
| 🟢 | **Single Instance Launcher** | One listed game starts one instance; optional --cabinets 1 remains accepted and maps to Linked Cabinets Disabled. ANS 0 is accepted; omitted single-instance presets default to 0 except dedicated Relay programs. Explicit presets override defaults. --cabinets N repeats one ROM; lists determine their own count and --relay does not change it. Single-instance RetroArch starts without frontend Netplay. Ten focused launcher checks and an installed-core bounded launch pass, with isolated configuration/saves and clean exit/no residue. First macOS window-position attempt failed; retained retry succeeds. No core build/deployment. Standalone gameplay/audio are separate from launcher qualification. See `Docs/LINKED_CABINET_LAUNCHER.md`. |
| 🟢 | **Power Sled Optional Master Music** | Added Power Sled family-only Relay Audio On Master selector, Enabled default, Master-only and requiring content reload. CRC-checked Relay audio runs on a second existing SCSP/68000 board; guarded native scene/race music tasks and stop/volume routes preserve rider audio, camera, role and network. Corrected two-instance RetroArch replay qualifies advancing races and music during racing, with waveform correlation 0.785878 against retained Relay audio; the first intro-only prototype is excluded from race qualification. SRAM identity/CRC/Ride, calibration/EEPROM, clean exits and no residue pass. Disabled old/new image/PCM and legacy format-10 continuations match; Enabled state replay and incompatible-setting rejection pass. Writer 11 reads 4–10 without the extra board. Normal installed core updated with backup/hash checks; dev remains absent. Boarding silence also occurs in the unmodified Relay and is confirmed by the user; preserved. Full-course/factory acoustic fidelity remain outside this bounded experiment. See `Docs/POWER_SLED_MASTER_MUSIC_EXPERIMENT_2026-10-10.md`. |
| 🟢 | **Power Sled Linked Master Arm Animation** | Cause reproduced: Master Call confirms/sends arm sound, but the native scene listens only for Entry. Four Master-only masks now match native confirmation. Silver observer and normal Red qualification show moving arm/camera, boarding and racing with audio; six instances exit cleanly. Slave/Relay programs and operator timing preserved. Both local system-file copies updated with backups/hash checks; normal core hash unchanged, dev absent. Black/Yellow masks reviewed; factory Master fidelity unqualified. Authorized account ceiling 25%; final verified usage 21%. See `Docs/POWER_SLED_BOARDING_ANOMALY_2026-10-10.md`. |
| 🟢 | **Power Sled Complete Departure Sequence Timing** | Native model boundary 380 frames and sound sequence beyond 400 ticks confirmed. The isolated reference delays only the second operator pulse to 480 frames / eight seconds after confirmation: Master reaches moving c0=479, both riders complete departure and enter racing with audio, valid SRAM and clean exits. User confirms the sequence now looks correct. Manual recipe documents at least seven seconds at default 60 Hz; emulation timing and core remain unchanged. Factory duration remains independently unqualified. Final account usage 21%, cap 25%. See `Docs/POWER_SLED_BOARDING_ANOMALY_2026-10-10.md`. |
| 🟢 | **Power Sled Experimental Standalone Mode** | Power-Sled-family-only experimental Disabled / Enabled selector, Enabled default, active only with Linked Cabinets Disabled. Master gameplay and Relay Attract are separate adaptations; the Relay extension is documented below. Four rotated native owners, four self-published records, full native race constructor/countdown and three AI tasks; independent Relay Audio preserved. Immediate end traced to the reduced one-node dispatcher. Startup now recognizes local Silver AI for a non-Silver human. All native count cases are 4/4; omitted enum-6 cases caused the failed Red intro/black-scene candidate. Attract loops include all four owners; HUD/finish order include AI while physical rider count stays one. Corrected normal Red run qualifies advancing attract/race scenes, native timer/time extension and rank changes through 4th. Red reaches a 4th result and GAME OVER; Yellow has four advancing race records; its earlier lever movie did not qualify steering and is superseded by the calibrated Silver follow-up below. The boarding constructor now creates all four local tasks, restoring Yellow course rendering and native 3 / 2 / 1 / GO. Final normal Yellow run captures 4th, GAME OVER and automatic return to moving attract; persisted Ride copies/CRC and clean shutdown pass. Audible/recorded repeat confirms CoreAudio, nonzero PCM and Relay race music correlation 0.6427 at 77.4864 seconds; the silent visual runs used the runner null-audio default. Bounded experimental integration closed; physical devices, every color/difficulty and factory camera/title fidelity remain unqualified. ABI round-trip/replay/mismatched-state rejection pass; Disabled video/PCM/native files match the prior baseline. Qualified normal core installed with backup/hash verification; dev remains absent. Authorized account ceiling 20%; last verified 19%. See `Docs/POWER_SLED_STANDALONE_EXPERIMENT_2026-10-10.md`. No factory standalone fidelity claimed. |
| 🟢 | **Power Sled Relay Standalone Attract** | Existing Enabled-default Standalone selector now applies to powsledr only with Linked Cabinets Disabled. Relay retains its role and native presentation/audio; four local attract actors and an inert Master view provide missing prerequisites without selection/race inputs. RetroArch captures and PCM qualify the continuous presentation; normal ABI state round-trip and Master/Relay-Disabled video/audio/NVRAM baselines pass. Local Test/Exit returns to Attract. Normal core installed with backup/hash verification; dev absent. Factory fidelity and every linked topology are not requalified. See `Docs/POWER_SLED_RELAY_ATTRACT_2026-10-11.md`. |
| 🟢 | **Power Sled Relay Standalone B_CRX Diagnostic** | Count the single real Relay B-CRX board in the isolated startup diagnostic after preserving its Relay flag. Startup also uses THIS IS RELAY SATELLITE instead of the communication-Master label, without changing local link initiation or program role. Guarded Standalone-only patches; linked programs and virtual actor layout unchanged. Normal RetroArch captures B_CRX ONE and advancing Attract; matched 1,800-frame video/audio/NVRAM hashes unchanged, state round-trip/replay and save-RAM checks pass. Normal core installed with backup/hash verification; dev absent. See `Docs/POWER_SLED_RELAY_ATTRACT_2026-10-11.md`. |
| 🟢 | **Power Sled System Option Order** | Standalone Mode, Relay Audio On Master, Relay Commands On Master and AI Finish Speed Fix appear in System before NVRAM Settings, only for Power Sled sets. All four switches default Enabled; existing saved choices are preserved. |
| 🟢 | **Power Sled Standalone Color Camera** | User approves retaining the current uniform intro, identified as Silver, for all four Ride colors. Controlled eight-run RetroArch matrix confirms prior native values 780 / 260 / -260 / -780 and current value 1 for every color. Same copied-user-save baseline, ANS 0, Vulkan, database and replay; valid Ride/CRC/calibration and clean exits/no residue pass. User identifies the previous Silver / Red / Black / Yellow runs as Yellow / Silver / Red / Black intros; retained as visual observations. Accepted Standalone port presentation, not an original single-screen-mode claim. Existing installed override retained; no additional build/test/deployment. Earlier History-session discrepancy remains unexplained; boarding/racing camera fidelity is outside this scope. Account ceiling 25% reached. See `Docs/POWER_SLED_COLOR_CAMERA_REVIEW_2026-10-10.md`. |
| 🟢 | **Power Sled Start Sequence Analysis** | Native operator decoder, local confirmation overwrite and countdown readiness reviewed against retained RetroArch inputs. Documented game-input sequence: Master Call P1, mode selection, Call P2 confirmation, released second Call P2 for boarding, then Start; each Slave confirms with Entry P1. Standalone uses the same Master path. Optional departure viewing wait is preserved without an enforced delay. No new emulator run, core change or deployment. Original Master panel/factory fidelity remain unqualified. See `Docs/POWER_SLED_START_SEQUENCE_2026-10-10.md`. |
| 🟢 | **Power Sled Standalone Service Exit** | Reproduced Call on Exit returning to Test after native restart. Passive trace confirms stale outgoing command 0x1000 is echoed by the one-node ring. Guarded standalone-only detour clears that command and preserves native Exit cleanup. Matched isolated RetroArch replay now returns to moving attract (phase 4) without re-entering Test; clean exit/no residual processes. Input checks pass; normal core rebuilt and installed with backup/hash verification; dev remains absent. Account usage 28%, authorized cap 29%. See `Docs/POWER_SLED_STANDALONE_EXPERIMENT_2026-10-10.md`. |
| 🟢 | **Power Sled Controller Assignment And Test Menu** | P1/P2 Entry, Call and handlebars retain their respective controllers 1/2. User-requested P1 West/North now additionally supply P2 Entry/Call, including with P2 disabled (2026-10-11; descriptor/native-bit checks pass for all three sets; normal core rebuilt and installed with backup/hash verification). Entry uses physical Xbox A (RetroPad B) and Call uses physical Xbox B (RetroPad A) on both ports (2026-10-11; normal core rebuilt and installed; input checks pass). Left/Right Stick Y supply inverted signed centered axes (polarity corrected on 2026-10-11; corrected from X on 2026-10-11; normal installed core rebuilt; Y endpoints and ignored X inputs pass checks); triggers removed; P1 secondary digital bindings restored as explicitly requested. Native Master/Slave comparison and observer confirm operator commands 1/2 interfere with Test selection; final Master/Relay patch gives phase-15 inputs to the native Test handlers. CRT grid and normal-core Color Test progression pass without gameplay selection. Input checks cover all three sets, endpoints, neutral and port isolation. Linked-mode native Exit remains unchanged; Standalone Exit/restart is verified in the adjacent roadmap item. Physical devices remain separately unqualified. Normal core and both system databases updated with backups/hash checks; dev absent. See `Docs/POWER_SLED_CONTROLS_2026-10-11.md`. |
| 🟢 | **Power Sled Relay Commands On Master** | Approved experimental Disabled / Enabled selector, default Enabled, visible in System for the Power Sled family only. Coin or Start opens selection; Entry confirms; native departure sound-task completion automatically enters pre-race; Start or Entry starts the race; Call uses native Emergency Stop. Coin/Start recovers a stop. Standalone two-race/recovery sequence, Disabled ABI baseline, state mismatch rejection and option checks pass. Final Start/Entry P2 linked replay without Relay reaches racing on both units; Call P2 propagates Emergency Stop. Clean exits, link/roster readiness, native save CRC and nonzero PCM pass. Normal core rebuilt/installed with backup/hash checks; dev absent. Integration complete; physical-pad/factory fidelity remain unqualified. Account meter 28%, cap 35%. See `Docs/POWER_SLED_RELAY_COMMANDS_ON_MASTER_2026-10-11.md`. |
| 🟢 | **Power Sled Physical Pad Isolation And Axis Travel** | Reported shared Main/Relay Service Menu input. Per-process device enumeration reproduced duplicate physical pad assignment despite distinct indices. macOS launcher now resolves one alphabetic HID-name list and reserves each pad for its own Port 1; all three reservations verified in RetroArch, 12 launcher checks pass. Manual three-pad menu operation remains pending. Current saved handlebar calibration is now the approved initial default for all three sets; physical-pad travel remains for user review. Native I/O prints raw hexadecimal ADC bytes; adapter range 00–FF, neutral 80, mechanical endpoints defined by calibration. The approved calibration-default update is documented in `Docs/POWER_SLED_CALIBRATION_DEFAULTS_2026-10-11.md`. See `Docs/POWER_SLED_CONTROLS_2026-10-11.md`.  Current roadmap closure: the user considers the entire Power Sled package closed on 2026-10-11, superseding the earlier pending checks above. Retain evidence/limits; reopen only for a newly reported issue. |

| 🟢 | **Power Sled System Visibility, Relay Gain And Control Layout** | User-requested visibility: Master shows all four Power Sled System switches, Relay only Standalone Mode, Slave none. NVRAM Settings and ANS retain existing rules. Separate Relay Audio Gain in Audio uses Auto / Mute (`0`) / 10%..100%, independent of rider SCSP Gain. P1 retains Service A / Select and Test A; P2 uses North for Shutdown, L3 for Cancel Error, R3 for Cancel Network Check, without Service/Test aliases. Both ports add D-Pad Up/Down Entry aliases; existing Entry/Call and Y-axis polarity retained. Input, option/save-RAM and independent dual-SCSP checks pass; bounded actual-core ABI load and state replay pass. Normal core rebuilt and deployed; physical-pad qualification unchanged. See `Docs/POWER_SLED_CONTROLS_2026-10-11.md`. |

| 🟢 | **Power Sled Standalone Startup Diagnostic** | The common Main program counts the real Master board once as a rider while retaining its Master flag. Relay remains excluded; local CPU sleds do not become fake boards. Native range checks and strings retained. Standalone accepts the shared program word; the same count also addresses the no-Slave Master + Relay diagnostic after roster arrival. RetroArch captures B_CRX ONE, NETWORK OK and Silver Ride, then advances into attract. Clean exit/no residue and ABI state round-trip/replay pass. Normal core rebuilt and installed. See `Docs/POWER_SLED_STANDALONE_EXPERIMENT_2026-10-10.md`. |
| 🟢 | **Power Sled Post-Race Audio** | Result callback discarded its music request when the native 64-byte MIDI queue was full. Relay Audio on Master now keeps that callback pending until enqueue succeeds. Isolated RetroArch repeat sends the native result music command and keeps an active auxiliary SCSP voice; clean exit and production ABI state round-trip/replay pass. Normal core installed with backup/hash verification, dev absent. Linked-session and factory acoustic fidelity remain unqualified. See `Docs/POWER_SLED_POST_RACE_AND_MASTER_RELAY_2026-10-11.md`. |
| 🟢 | **Power Sled Master + Relay Without Slave** | Integrated roster support and corrected the black attract scene. Matched Master + Slave / Master + Relay comparison located a null fourth intro record: the latter has only three native field records, but its visual constructor always reads four. Main now initializes/publishes the fourth record only during attract with one physical rider; Main/Relay map it, retaining separate role/color and native ownership in later phases or multi-rider sessions. User confirms the corrected intro; normal-core captures show intro and bounded race entry, and Standalone intro still passes. Shared B_CRX counts the playable Main after roster arrival. Normal core/database installed with backups and matching hashes, dev absent. Full-course and physical-controller proof remain outside this qualification. See `Docs/POWER_SLED_POST_RACE_AND_MASTER_RELAY_2026-10-11.md`. |

| 🟢 | **Power Sled Relay Countdown Audio On Master** | Existing visual countdown role gates now emit native cues on Master with Relay Audio Enabled. Tagged group 62 routes only to the added Relay SCSP; untagged rider group 12 remains primary. Local human camera filtering avoids four copies in Standalone without changing native timing. Normal-core isolated Silver recording qualifies three countdown pulses, final cue and continuing race music; observer confirms their ordered commands. Routing/partial-state checks pass; exact qualified normal core rebuilt and installed, dev absent. Musical command tables contain ten complete valid entries; phase-6 stops are explicit, with no skipped music pointer identified in reviewed paths. Other colors/topologies and factory fidelity remain outside this bounded qualification. See `Docs/POWER_SLED_PRE_RACE_AUDIO_REVIEW_2026-10-11.md`. |
| 🟢 | **Power Sled Result Sequence Interruption** | With Relay Commands On Master Enabled, Start or Select (Coin) in results requests the existing native return-to-attract command. All three programs accept that command in their result task table so linked peers can follow it; natural completion and other phase mappings remain native. User-reported result/intro overlap corrected with native auxiliary-sequence stop, since ordinary note-off ignores the result one-shot voice. The added Master board and separate Relay stop those sequences before return. User-state observer qualifies result note 1 followed by intro note 3 alone; normal-core state-based repeat, exclusive routing checks and clean exits pass. External Relay linked audio transition is not requalified. Normal core built and installed with database backups/hash checks. Isolated Standalone Start replay ends in attract with clean exit/no residue; linked interruption and physical Select remain outside this runtime qualification. See `Docs/POWER_SLED_RELAY_COMMANDS_ON_MASTER_2026-10-11.md`. |
| 🟢 | **Power Sled Pre-Race Relay Audio Review** | Native phase-6 entry explicitly stops selection and attract/race music. Selection music belongs to phase 5 and is successfully delivered in the retained Relay trace; phase 6 has no additional identified music initializer. Countdown and race audio resume later. Other scene callbacks share the theoretical enqueue-failure vulnerability, but it is not demonstrated as the cause of this interval. Code/table/retained-trace analysis only; production unchanged and factory acoustic fidelity unqualified. See `Docs/POWER_SLED_PRE_RACE_AUDIO_REVIEW_2026-10-11.md`. |

| 🟢 | **Power Sled Arrival Rank Audio Separation** | Added Master Relay board no longer receives the two per-rider finish/control stops. Native scene stops and result-to-intro cleanup remain. Race music is retained through immediate rank display; result music keeps its native later initializer. Its callback retries native auxiliary stop and then start in separate scheduler stages to prevent race/result overlap and queue starvation. Observer confirms one result voice; normal user-state repeat and return to intro pass. Normal core installed with backup/hash verification. See `Docs/POWER_SLED_POST_RACE_AND_MASTER_RELAY_2026-10-11.md`. |
| 🟢 | **VR1 Supplemental View Binding** | General review: all 13 single-View sets in six families expose D-Pad Up. Added the shared Start / VR alias to Manx TT and Motor Raid; Sega Rally, Super GT 24h, Sky Target and Wave Runner already comply. Profile descriptions identify VR1 as one View action, including shared Start/View. Existing aliases and multi-View layouts remain available. Cross-core handoff reviewed in both destination chats: Supermodel single-View and TGPulse-Next SWA profiles already have Up, so no destination implementation remains. See Docs/VR1_VIEW_BINDING_INTERCHANGE_2026-10-11.md. |
| 🟢 | **Standard Gun Input Fallback** | Fixed idle Lightgun off-screen status monopolizing Standard and suppressing Mouse/Analog Stick movement. Existing input regression checks cover positional BEL and serial Virtua Cop, retaining real Lightgun trigger/off-screen reload checks. Physical Mouse behavior in the reported RetroArch session remains to confirm. See Docs/GUN_STANDARD_FALLBACK_2026-10-11.md. |
| 🟢 | **Country Default Priority** | Approved priority Export → Europe → U.S.A. applied to Country/Nation selector defaults and Automatic Initial NVRAM Setup. Over Rev (`overrev`, `overrevb`, `overrevba`) and Super GT 24h now prefer Europe; Export remains the default where supported. Existing saved Core Option choices and valid frontend/native NVRAM retain their existing precedence. Value order, native labels and encodings remain intact. Catalog audit passes for 87 sets / 332 options; initial-selection and persistence checks pass. |
| 🟢 | **NVRAM Reset Notification Reference Alignment** | Fixed the silent automatic reset after changed operator options: Info logging alone did not reach the frontend. SM2 now sends the exact TGPulse-Next notification "Applied NVRAM Settings; machine reset" through queued SET_MESSAGE_EXT (5 seconds), with SET_MESSAGE fallback (300 frames). Actual-core VF2 callback checks verify exactly one notification for a changed persisted option and no repeats during unchanged frames, for both interfaces. Existing startup logs stay silent; reset/persistence behavior is unchanged. |
| 🟢 | **Network Role Settings Reference Alignment** | Superseded by current F14: exactly Linked Cabinets and Auto Network Role Settings, with Not Supported placeholders. ANRS works with NVRAM Settings OFF; managed native selectors are hidden and synchronized. Native role and topology are independent. Shared wording follows the revised reference; obsolete Menu Review networking comments are not restored. |
| 🟢 | **Standalone Communication Board Review** | The communication board stays fitted in local loopback with Linked Cabinets Disabled, matching upstream. Two-instance RetroArch trials for Dynamite Baseball, Baseball ’97, Pilot Kids, Rail Chase 2 and Zero Gunner formed frontend rosters but all native boards stayed disabled; no cabinet-link options were added for them. Matched board-present/absent ABI boot paths, including reviewed clone variants, preserved video, PCM and saves. Those observations are retained as limited evidence, not a reason to remove the board. See `Docs/COMM_BOARD_STANDALONE_REVIEW_2026-10-18.md`. |
| 🟢 | **Power Sled Initial Calibration Defaults** | Approved current saved endpoint data seeds all three independent initial images via Automatic Initial NVRAM Setup. Existing frontend/native saves retain priority; operator settings preserve calibration. See Docs/POWER_SLED_CALIBRATION_DEFAULTS_2026-10-11.md. |
| 🟢 | **Power Sled System Defaults And Order** | All four switches default Enabled. Standalone precedes Relay Audio On Master, Relay Commands and AI Finish Speed Fix, before NVRAM Settings. Standalone remains inactive with Linked Cabinets enabled. Existing saved choices preserved. |
| 🟢 | **Power Sled Relay B_CRX** | Relay counts the reconstructed Main's rider board while preserving its separate role. Master + Relay observer reports ONE on both boards with ready links and Standalone inactive. No forced success flag. |
| 🟢 | **Power Sled Native AI Finish Slowdown Review** | Native AI clamps velocity magnitude to 3.0 game-world units after course index 773, then fixes course indices to 842 and stops movement when position field +0x138 exceeds 839. The speed-clamp block is byte-identical in Slave (16-byte address shift) and untouched by Standalone. Consistent with the reported late-race slowdown; exact finish geometry and measured speed curve are not mapped. User-approved experimental AI Finish Speed Fix selector bypasses only the late-course clamp; Enabled is the approved core default; Disabled restores the native clamp and the final stop is retained. Guarded for Main/Slave/Relay and requires content reload. Matched Standalone user-state velocity traces verify the bypass; linked runtime is not requalified. See `Docs/POWER_SLED_STANDALONE_EXPERIMENT_2026-10-10.md`. |

| 🟢 | **Manx TT Deluxe Motion And Audio Fidelity** | Cabinet audio selection, additional sound board and AMS boot acknowledgement are integrated. Native Service Menu transitions and fresh-load persistence pass on C/D. User reports the requested Manx TT checks successful on 2026-10-11; operator qualification is closed. Full motor/position-feedback emulation remains outside the acknowledgement stub. C-main/Deluxe-audio and D-main/Twin-audio pairings remain documented reconstructions, not factory dumps. See `Docs/MANX_TT_CABINET_AUDIO_2026-10-10.md` and `Docs/MANX_TT_MOTION_STUB_2026-10-10.md`. |

## Modalità di lavoro

Facilitare gli aggiornamenti upstream è un requisito trasversale: adattatore
isolato in `src/libretro/`, accessi neutrali minimi alla macchina, layout
originale conservato e nessuna duplicazione del motore. Seguire la sezione
architetturale di [LIBRETRO_DESIGN.md](LIBRETRO_DESIGN.md), mantenendo traccia
dei punti modificati e verificando ogni import rispetto alla stessa revisione
originale, oltre al confronto tra baseline precedente e nuova.

Un punto alla volta, con modifiche circoscritte e verifiche ripetibili. Non
estendere automaticamente il lavoro alle milestone successive. Segnalare
quando un passaggio beneficia di un modello più capace, spiegando il motivo;
non cambiare modello o delegare ad altri agenti senza autorizzazione.

`git fetch upstream` recupera riferimenti senza modificare i sorgenti. Gli
aggiornamenti si valutano e integrano su `main` con patch, cherry-pick o merge,
secondo il caso e le istruzioni correnti. Il mainstream si aggiorna separatamente.

## Verifiche ancora aperte

Networking update, 2026-10-18: the user considers the requested networking
checks closed. The board-fitted loopback review is complete for its documented
scope. Its bounded roster/native-link evidence does not claim synchronized
gameplay for every game or configuration; those limits are evidence, not an
outstanding test request. Reopen only for a newly reported issue.

Closure update, 2026-10-11: the user closes the full Power Sled package,
including Country semantics, and BEL / RC2 / HOTDP. Prior pending statements
for those activities are historical and impose no further test gate. Any newly
reported issue will be recorded as a new roadmap activity. Rumble operator
checks are closed following the user’s positive verification on 2026-10-11.

Operator control update, 2026-10-11: the user confirms the remaining
House of the Dead / Top Skater / Ski Super G control checklist successful.
Game Control Reconciliation is closed. The user also confirms the separate
audio listening checks successful; SCSP / MultiPCM / DSB2 qualification is closed; former Windows/Batocera technical gates are superseded by the
later completed platform qualification recorded below.

Operator update, 2026-10-11: the user reports the requested Manx TT tests
completed successfully. No further Manx TT operator check is required for
the integrated package. BEL personal frontend saves and states are already
absent in the configured directories; the calibrated upstream reference
and isolated test evidence are preserved.

Questa sezione raccoglie soltanto attività di verifica. Le implementazioni
mancanti restano nei rispettivi punti della roadmap.

User validation of the preceding non-network change batch is complete.
The 2026-10-09 isolated RetroArch package closes the bounded Daytona
Resume/Restart, topology-change, stall and reconnection checks in section 8,
with coordinated Restart required for native recovery. The formerly open Manx TT Relay initialization also passes for the parent and
Revision C, as recorded in section 9. Subsequent normal-core gameplay also closes
the bounded local Manx TT two-rider/LIVE investigation: Time Up/ranks and further
race progression pass on the parent triplet and Revision C pair/triplet.
Motor Raid Deluxe's verified Twin configuration
is now the approved automatic-initialization and selector default. Its manually
selected Deluxe drive-board precondition remains separate. Synchronized
gameplay remains distinct from the verified roster/native handshakes.
The latest Gain label correction passed build and automated option checks;
both local RetroArch core copies have been updated. TGPulse work is tracked
through the project interchange file, not as completed SM2 runtime evidence.

Il 25 settembre 2026 il controllo
incrociato automatico ha confrontato tutti gli 84 set del catalogo screenshot
con le NVRAM Settings realmente risolte dal core: selezione, ordine,
descrizioni, valori, default e routing parent/clone. Il controllo ha aggiunto
il riferimento diagnostico mancante per `manxttdx` e corretto `sfight`, che ora
preserva il proprio default nativo `Automatic = Off` tramite un catalogo
dedicato anziché ereditare il default del parent.

Completate il 20 settembre 2026: la verifica strutturale di menu e opzioni cambia
set, parent/clone e profilo senza rilevare voci per gioco residue; la regressione
generale copre le quattro board, parent e clone, ZIP e 7z, input sintetico,
video/audio, cicli load/unload/reset, Save RAM e rifiuto controllato di archivi
mancanti o invalidi. Nessun crash, blocco o salvataggio corrotto è emerso.
Save State, rewind e run-ahead sono inoltre verificati localmente sulle quattro
board con 20 cicli per scheda; il precedente scarto Daytona è risolto salvando
lo stato runtime dell'adattatore Libretro. La qualifica Windows usa l'artifact
CI esatto della revisione `1d8a1ab`: RetroArch 1.22.2 su Radeon Vega 11 completa
VF2 in Vulkan e OpenGL a 1×/4×, con una ripetizione Vulkan dopo il cambio di
backend, uscita regolare, SRAM, audio e screenshot verificati. Restano fuori
dalla prova controller fisici, ascolto soggettivo e GPU/driver differenti. Gli
artifact CI macOS arm64 e Windows x86_64 della stessa revisione hanno inoltre
formato via LAN una gara Daytona 2/2 e un roster STCC 3/3 con il Relay Windows;
tutte le istanze hanno salvato SRAM e screenshot e sono uscite senza forzature
o residui. Una verifica Daytona in gara ha inoltre confermato la corretta ombra
retinata: la dominante bluastra osservata sul televisore era prodotta dalla
modalità Luce notturna di Windows, non dal core o dal backend grafico.
Il worktree corrente è stato infine compilato per Linux x86_64 e provato in una
directory isolata di Batocera 43.1: Daytona ha completato 2300 frame di gara con
OpenGL Core 4.6, audio e SRAM validi, mentre 20 cicli Save State hanno coperto
round-trip, replay deterministico, run-ahead, rewind e rifiuto degli stati
corrotti. Non restano quindi verifiche tecniche specifiche di Windows o
Batocera nella roadmap corrente.

## Vincolo esterno prima della pubblicazione

L'audit di distribuzione è concluso: il pacchetto contiene 15 file previsti,
licenze delle dipendenze, revisione sorgente e checksum completi, senza ROM o
contenuti inattesi. Rimane una decisione del titolare upstream, non una verifica
tecnica locale: `LICENSE` dichiara BSD-3-Clause, mentre 114 intestazioni vietano
l'uso commerciale senza permesso. Prima di un PR o di una pubblicazione esterna
va chiarito quale dei due testi governi quei file.


## Audio Recovery After Reset — Framework Follow-Up 2026-10-18

Status: Complete. The user confirmed audio playback is satisfactory on 2026-10-18.
Reference: [Framework F12/F14, edition 0.1.37](/Users/andrea/dev/libretro-core-framework/FRAMEWORK.md).

The source audit and installed-core VF2 trials on 2026-10-18 found no reset
recovery defect. Native and 60 Hz runs produced sample-identical PCM at
startup, after an option-triggered reset and after two explicit resets. A
separate RetroArch/CoreAudio recording confirms PCM returns after two real
frontend resets; the user subsequently confirmed the audio sounds correct. The full
evidence and limits are in [Frontend Menu And Audio Reset Review](Docs/FRONTEND_MENU_AUDIO_RESET_2026-10-18.md).

- [x] Inspect this core’s audio startup, reset and flush paths. This adapter has pending sample vectors rather than a packet queue with read/write indices or a blocked producer. Repeated resets clear both native and frontend pending samples and restore timing/DC-filter state.
- [x] Compare PCM before and after repeated explicit and option-triggered resets in native and 60 Hz execution. No defect was reproduced and no production code change was made.
- [x] Verify physical speaker listening and subjective fidelity. The isolated Software/Asynchronous RetroArch run used CoreAudio and recorded resumed PCM after two explicit resets; the user confirmed the audio sounds correct on 2026-10-18. Networked two-peer audio/gameplay remains a separate qualification.
- [x] Record destination findings and evidence limits here and in the linked report. No new shared behavior or interface convention emerged, so this destination-specific result is not added to the Framework.

Supermodel reference: [Audio Recovery During Machine Reset](/Users/andrea/dev/libretro-supermodel-modern/Docs/NETWORK_TWO_OPTION_2026-10-17.md). Its fix reuses startup initialization with two silent packets to avoid a queue-specific producer/consumer position ambiguity. **Do not copy two-packet priming or any Supermodel queue implementation:** SM2's own reset path was reviewed and no corresponding defect was reproduced.
