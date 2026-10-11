# Menu e controlli: riferimento Supermodel

Linee guida per le milestone 2 e successive di [PORTING_PLAN.md](PORTING_PLAN.md).
Il primo core software della milestone 2 è implementato: vedere [LIBRETRO.md](LIBRETRO.md).
Sono implementate anche le Core Options Video dei renderer Vulkan/OpenGL, SRAM,
NVRAM, profili di controllo, Netpacket sperimentale, rumble e bilanciamento
audio. Le funzioni ancora aperte sono indicate nella roadmap.

## Struttura per gli aggiornamenti upstream

Requisito dell'utente: facilitare l'integrazione delle versioni future di
`dmanlfc/sm2-emu`, mantenendo la struttura originale e riducendo le divergenze.
Applicare anche il [manifesto generale dei porting](Docs/UPSTREAM_PORTING_MANIFESTO.md):
integrare per default ogni modifica upstream compatibile, adattare al frontend
Libretro e richiedere una scelta solo quando emerge una collisione concreta.

- Concentrare il futuro adattatore in `src/libretro/`, con target CMake proprio:
  ABI e ciclo di vita, callback, opzioni, input e persistenza del frontend.
  Separare questi compiti in file quando serve, evitando un unico file enorme
  oppure un framework generico anticipato.
- Riutilizzare loader, macchina, audio e renderer. L'adattatore dipende dalle
  interfacce della macchina; CPU e hardware restano indipendenti da Libretro.
  Aggiungere solo gli accessi neutrali indispensabili, senza copiare il motore
  né distribuire condizioni `LIBRETRO` nei sorgenti di emulazione.
- Conservare nomi, percorsi e formattazione upstream. Limitare gli agganci al
  build system; preferire impostazioni CMake per target. Tenere le dipendenze
  del frontend fuori dai target condivisi e preservare la build standalone.
- Usare i metadati originali dei giochi; tenere descrittori e preferenze del
  frontend nell'adattatore, senza duplicare l'intero database upstream.

Punti di integrazione introdotti dalla milestone 1: opzioni e condizioni CMake
per separare standalone/headless; accesso neutrale `sound_board()` su
`Model2MachineBase` e implementazioni nelle quattro varianti. Il runner vive
in `src/headless/` e il confronto in `scripts/compare-headless.py`. Mantenere
questo inventario aggiornato quando cambia la superficie modificata del motore.
The 2026-10-10 CPU package imports upstream direct i960 ROM/work-RAM fetch,
MB86235 program-RAM fetch and settled coprocessor wait skipping. Machine init
binds the existing allocations; reset and state loading retain those allocations.
Host fetch pointers are excluded from serialization, with bus fallback outside
the bounded windows. No Libretro dependency enters CPU/machine code and the
state format stayed 10 for that package. The SCSP depth-index-3 correction is an upstream synthesis
change. See `Docs/UPSTREAM_CPU_SCSP_PACKAGE_2026-10-10.md` for reference revisions,
pointer/state checks and platform limits.
La milestone 2 aggiunge `src/libretro/` e due agganci CMake (opzione e
subdirectory). La persistenza frontend aggiunge alla macchina soltanto viste
neutrali su backup RAM ed EEPROM; formato, import e opzioni restano nell'adattatore.
L'opzione diagnostica Libretro per il controllo CRC aggiunge al loader neutrale
un solo parametro `verify_crc`, abilitato per default: lo standalone e il
runner headless conservano quindi invariato il confronto CRC, mentre il core
può richiedere esplicitamente il fallback per nome senza introdurre header o
callback Libretro nel loader.
The shared-device BIOS follow-up adds one optional, frontend-neutral device
directory argument to `RomLoader::load`. Only the Libretro adapter supplies its
System directory; standalone and headless callers keep the previous default.
The loader keeps the selected device archive separate so device firmware takes
precedence over a copy embedded in the game ZIP without changing parent/game
identification.
The linked-network preset maps only reviewed operator values through the
existing NVRAM adapter; the communication transport remains frontend-neutral.
`SoundBoard` exposes source presence and output gain for the loaded hardware.
The Libretro adapter owns menu values and visibility, while each board applies
gain after its source advances. These gains are frontend settings and are not
serialized as emulated machine state.
La GPU aggiunge `render/vk/pass_context.h`, implementato dal contesto standalone
e dall'adattatore. I passaggi tilemap/poly3D dipendono da questa interfaccia
anziché dal contesto con finestra; shader e algoritmi restano condivisi.
CMake abilita gli shader anche per Libretro Vulkan/OpenGL e compila i passaggi
con entry point risolti dal frontend. Nessun nuovo accesso alla macchina/CPU.
OpenGL riusa i passaggi upstream GL e riceve dal frontend funzioni e framebuffer;
non introduce una finestra SDL né una copia dei renderer nell'adattatore.
The OpenGL abandonment path also clears the whole-polygon geometry buffer
record before destroying the old renderer. This keeps teardown after an
unannounced context loss from unmapping/deleting dead-context buffer names;
normal shutdown still releases the live geometry buffer. See
`Docs/RENDERING_REVIEW_2026-10-09.md` for the source audit and lifecycle evidence.
Gli enhancement GPU del commit upstream `ce59cf5` restano nei passaggi e negli
shader condivisi: l'adattatore espone le scelte tramite Core Options e passa
solo gli identificatori ai renderer. xBR/ScaleFX opera sulle tilemap 2D prima
della composizione col 3D; aspect, scaling finale e shader dell'immagine
completa restano responsabilità del frontend.
Il collegamento tra cabinet usa l'interfaccia neutrale upstream `CommTransport`.
`M2Comm` possiede sia il trasporto sia il protocollo ad anello; la macchina
espone soltanto la communication board comune alle quattro varianti hardware.
`src/libretro/netpacket.*` adatta i frame completi all'interfaccia ufficiale
Libretro Netpacket. L'unica estensione al contratto upstream è `ready()`, che
impedisce al timer di collegamento di partire prima che sia completo il roster
dei cabinet richiesti. L'adattatore riusa dal core Supermodel handshake,
conteggio atteso e roster ordinato; ogni frame Model 2 viene inviato soltanto al
successore, lasciando a `M2Comm` il protocollo hardware ad anello. Per i
trasporti standalone `ready()` coincide con `connected()`. Il motore non
include header Libretro e il core non apre socket. Senza trasporto esterno resta
attivo il `LoopbackTransport` dello standalone per un solo cabinet.

NetBoard v3 distinguishes identity requests from Hello replies. A known peer
must answer a new request after another frontend resets its local roster;
ordinary replies never trigger another reply. Pending copies of both packet
types are deduplicated. This repair stays in `src/libretro/netpacket.cpp` and
does not alter native board enumeration, frame payloads or machine state.
Every participant must update together. The separate native Daytona recovery
procedure is coordinated Restart after a cabinet reboot or disconnection;
transport roster recovery does not itself restart native FF/FE enumeration.
See [network validation](Docs/NETWORK_VALIDATION_2026-10-09.md) for evidence.
The frontend-neutral `M2Comm::role_inputs()` accessor reports the existing FG
and shared role bytes without advancing the flip gate or changing shared RAM.
It extends native link diagnostics only. The attempted Manx TT role-3
adaptation did not pass real frontend qualification and was reverted; native
role predicates and machine save-state layout remain unchanged.

Eccezione hardware condivisa con lo standalone: il workaround BEL in
`src/hw/model2c.cpp` mantiene i parametri temporanei della calibrazione anche
quando la NVRAM contiene già il preset prodotto dal workaround stesso. Senza
questo riconoscimento, `Automatic Initial NVRAM Setup` rende i byte persistenti
validi ma impedisce al percorso precedente, limitato ai byte `0xff`, di
inizializzare la trasformazione usata dal mirino durante la partita. Valori di
calibrazione differenti dal preset non vengono sostituiti.

Correzioni hardware selettive riprese dall'upstream 0.9.7 senza aggiornare la
baseline completa: `b93e73c` lascia scollegati i canali analogici non dichiarati
su Model 2A/2B/2C, affinché restituiscano il valore aperto `0xff`; il solo hunk
Model 2B di `f415009` completa in ordine le scritture INTENA differite usate da
`overrevb` e `overrevba`. Il bilanciamento dello stesso commit resta nel motore
audio condiviso: `Model2Sound` conserva i coefficienti upstream e l'accessore
neutrale `SoundBoard::set_audio_balance_enabled()` consente all'adattatore di
ripristinare unity gain senza introdurre dipendenze Libretro nell'hardware.
L'opzione globale non duplica la tabella e si applica a tutte le schede SCSP.

Il core i960 può correggere il rounding mode `00` secondo il manuale Intel:
`roundr`, `roundrl`, `cvtri` e `cvtril` arrotondano al più vicino con gli exact
half verso il vicino pari. La `round()` ereditata da MAME arrotonda invece gli
exact half lontano da zero. La Core Option globale è disabilitata per default,
così standalone, headless e Libretro conservano il comportamento upstream finché
il frontend non abilita esplicitamente il fix al caricamento. La scelta resta
isolata in `I960::round_to_int()` e va sostituita con l'eventuale soluzione
upstream quando MAME o SM2-Emu la integreranno.

I metadata di guida sono allineati alle aggiunte upstream fino alla 0.9.9:
`start_gear=4` consegna Daytona e i suoi cloni alla partenza lanciata in quarta
quando la Core Option globale `Automatic Start Gear` è abilitata; disabilitandola
i giochi con cambio a quattro marce partono in prima. L'opzione è abilitata per
default per seguire il comportamento upstream. `drive_protocol` distingue
Daytona, STCC e Sega Rally senza modificare i
profili RetroArch. Il parser conserva entrambi in `GameSpec`; l'adattatore usa
`start_gear` durante l'inizializzazione dell'input e `drive_protocol` nel decoder
frontend-neutral importato dall'upstream. La macchina conserva tutte le scritture
drive-board del frame e il rumble Libretro riceve l'effetto decodificato senza
dipendere da SDL o da un dispositivo specifico.

Il clone `daytonam` mantiene il metadato upstream `protection="daytona-maxx"`.
Il parser lo traduce in un tipo di protezione neutrale e `Model2Original`
decodifica la sola finestra PIC/ROM a `0x00240000`, seguendo la macchina a stati
documentata da MAME. Il frontend non contiene condizioni specifiche per MAXX.

### Versioni locali che distinguono parent e clone

`games.xml` integra versioni descrittive ricavate dai commenti e dalle
registrazioni MAME per evitare che parent e clone risultino indistinguibili:

- `daytona`: `Revision A`; `daytona93`: `1993, Deluxe`;
- `stcc`: `Newer`; `stcco`: `Original`;
- `vstriker`: `Revision A`; `vstrikero`: `Original`.

Questi campi sono una personalizzazione locale dei soli metadata di
presentazione. Se l'upstream introdurrà una distinzione equivalente, adottare la
soluzione upstream; diversamente conservarli durante i futuri allineamenti.

Per ogni aggiornamento, registrare il commit upstream integrato e i riferimenti
dei submodule, rivedere API e metadati modificati e risolvere i conflitti nel
minor numero di punti possibile. Quando autorizzati, tenere distinti i commit
di import upstream, degli accessi generici e dell'adattatore. Lavorare su `main`
rimane compatibile con questa separazione delle modifiche.

Confrontare il port con una build originale della **stessa revisione upstream**:
build standalone e headless, frame/audio/NVRAM sulle quattro varianti e, quando
disponibile, prove reali in RetroArch. Conservare anche il confronto tra vecchia
e nuova baseline: una correzione upstream può cambiare legittimamente gli hash.
La separazione limita i conflitti, ma ogni aggiornamento richiede comunque
revisione e validazione.

On 2026-10-08, upstream `1a60affc251dd9992044013650dbe24075221593` was
backported verbatim into the frontend-neutral M68000 wrapper. It rebinds host
pointers after a state load without changing the serialized format. The full
baseline remains 0.9.13; pending SCSP/DSB2 serializer changes belong with their
audio implementations. See [the verification report](Docs/UPSTREAM_SAVE_STATE_PACKAGE_2026-10-08.md).

On 2026-10-08, renderer fix `277a482` was adapted with upstream geometry
binding 5 retained and the absent replacement-texture binding omitted from
Vulkan descriptor allocation. Shared polygon interpolation remains upstream;
no frontend menus changed. See [the renderer report](Docs/UPSTREAM_TEXTURE_WARP_PACKAGE_2026-10-08.md).

Upstream geometry fix `d0db61c` and shadow-detail fix `2c4e9e2` were
backported on 2026-10-08. The geometry serializer retains two discarded legacy
words to preserve its layout. Five-title legacy-state and replay checks pass;
no menu options changed. See [the package report](Docs/UPSTREAM_GEOMETRY_SHADOW_PACKAGE_2026-10-08.md)
for exact revisions and the controlled upstream reference construction.

## Riferimento verificato

Su richiesta dell'utente, usare il progetto personale
`Zer0one/Libretro-Supermodel`, ramo `supermodel-modern`, come riferimento di
organizzazione e usabilità. Consultato il 9 settembre 2026 al commit
`c99444be536a09f27a1f3dec2731b9ef42b99cdf`, nel checkout adiacente
`../libretro-supermodel-modern`. Il progetto rimane separato e si consulta
in sola lettura; non diventa una dipendenza di SM2.

Fonti nel checkout Supermodel:

- `Src/OSD/libretro/libretro_core_options.h`: categorie, nomi, valori iniziali
  e spiegazioni delle opzioni.
- `Src/OSD/libretro/libretro.cpp`: registrazione Core Options v2, visibilità
  contestuale e descrittori dei dispositivi.
- `Docs/CONTROL_PROFILES.md`: profili per gioco, guida, lightgun e Test/Service.
- `Config/Games.xml` e `Src/OSD/libretro/LibretroInputProfiles.h`: firme dei
  giochi e nomi effettivi dei profili usati nel confronto fra le generazioni.
- `Docs/README.md`: salvataggi gestiti dal frontend e impostazioni NVRAM.

I nomi dei comandi originali e gli alias aggiuntivi riprendono preferenze
esplicite dell'utente. Le altre convenzioni osservate in Supermodel sono
una guida da adattare alle capacità effettive di Model 2.

## Organizzazione delle opzioni

Adottare Core Options v2 con l'ordine di categorie di Supermodel:
**System, Video, Audio, Input, CPU**. Pubblicare una categoria solo quando
contiene opzioni implementate e utili; il primo core software può averne meno.
Usare nomi coerenti per funzioni equivalenti e chiavi proprie con prefisso
`sm2_`, stabili dopo la prima pubblicazione. Verificare il comportamento sui
frontend target quando categorie o visibilità dinamica non sono disponibili.

Equivalent frontend controls must use the same labels, choices, ordering and
saved-value convention across cores. Source Gain follows TGPulse: Auto as the
default (`auto`), Mute (`0`), then 10% through 100% (`10` through `100`).
Use source labels such as `MultiPCM 1 Gain`, `FM (YM3438) Gain` and
`DSB (MPEG) Gain`, without Absolute/Relative suffixes: the final output also
depends on the reference mix and other volume controls.
Auto preserves each machine's reference mix; SM2 resolves Auto to its existing
100% source output. Keep published numeric behavior and keys compatible.
Register saved legacy values before reading them, then expose only an active
legacy value alongside the canonical selector. Do not rewrite frontend files
on read or require an external migration script.

| Categoria | Direzione per SM2 | Quando |
| --- | --- | --- |
| System | Persistenza per gioco; eventuale inizializzazione della sola NVRAM nuova e override espliciti dei campi verificati | Milestone 3; nessun preset prima della validazione |
| Video | Risoluzione nativa 496 × 384; aspect automatico 4:3/16:9 dalla NVRAM con override; selezione dei mirini; scala interna 1×–4×, filtro texture 3D e xBR/ScaleFX sulle tilemap solo con GPU integrata | Implementato |
| Audio | Riproduzione fedele al rate della scheda; eventuali regolazioni specifiche solo se il mixer le supporta e sono utili | Nessuna opzione obbligatoria nel primo core |
| Input | Profili per gioco, modalità delle sorgenti di puntamento, cambio e regolazioni separate di sterzo/acceleratore/freno | Milestone 3 |
| CPU | Soltanto scelte di esecuzione effettivamente disponibili e verificate | Rinviata; nessun overclock o JIT presunto |

Ogni descrizione deve spiegare effetto, giochi/dispositivi interessati e
applicazione immediata oppure dopo riavvio del contenuto. I valori iniziali
devono preservare fedeltà e comportamento della macchina. Le funzionalità
sperimentali vanno indicate come tali, con i limiti verificati.

Supermodel mantiene le regolazioni di guida visibili per prevedibilità,
applicandole soltanto ai profili Driving. Tutte le opzioni non NVRAM restano
sempre visibili; la descrizione dichiara gli eventuali giochi o profili ai quali
si applicano. Soltanto i campi NVRAM sono filtrati per gioco. I descrittori dei
controlli devono sempre corrispondere al gioco caricato e una voce non
applicabile non deve alterare altri profili.

`Aspect Ratio` è una Core Option Video globale con default unico `Auto`.
L'adattatore legge il tipo di cabinato dalla EEPROM attiva per le famiglie
Indy 500 e STCC e comunica 4:3 o 16:9 al frontend con
`RETRO_ENVIRONMENT_SET_GEOMETRY`; 4:3 e 16:9 restano override manuali. Questa
logica appartiene all'adattatore perché riguarda la presentazione del frame,
senza modificare renderer, macchina emulata o formato della NVRAM.

## Controlli e preferenze da conservare

Il catalogo proposto per il punto 3.1 è in [CONTROL_PROFILES.md](CONTROL_PROFILES.md),
con firme risolte, varianti, copertura dei set e lacune da verificare.

- Per giochi Model 2 e seguiti Model 3 con controlli equivalenti, conservare
  lo stesso profilo Supermodel: nome, posizioni sul pad e convenzioni delle
  opzioni. Differenze reali aggiungono o rimuovono solo le azioni pertinenti;
  bit e canali diversi si traducono nell'adattatore. Consultare la matrice in
  CONTROL_PROFILES.md, inclusi Soccer e il caso Handbrake di Sega Rally.
- Ricavare i profili dai metadati SM2 in `data/games.xml`, compresi cablaggio,
  polarità, riposo e calibrazione. Non trasferire maschere o valori ADC Model 3:
  in Model 2 anche i canali di sterzo e pedali cambiano tra giochi.
- Nomi basati sulla funzione del comando originale; preservare i comandi
  canonici e aggiungere alias senza sostituirli. Identificare i pulsanti del
  pad anche per posizione South/East/West/North, evitando ambiguità A/B.
  Le etichette Star Wars Trilogy restano un esempio di precisione, non un
  insieme di azioni da introdurre nei giochi Model 2.
- Usare il remapping nativo del frontend. Come riferimento Supermodel,
  prevedere Service su L3 e Test su R3 rimappabili, con variante del dispositivo
  senza questi slot. Il Model 2 attualmente supportato espone soltanto Service A
  e Test A sul Player 1. Verificare eventuali conflitti per ogni profilo.
- Per la guida, il cambio H-Gate/Standard è disponibile dove esiste il selettore
  a quattro marce, mantenendo i comandi sequenziali pertinenti. Lo sterzo resta
  rimappabile e offre risposta Linear/Progressive/FBNeo; sterzo, acceleratore e
  freno hanno intervalli indipendenti con default 100%. Le trasformazioni
  preservano la calibrazione del gioco. I preset numerici particolari di
  Supermodel non sono copiati senza misure SM2.
- Per le pistole, prevedere modalità Standard con sorgenti combinate,
  Lightgun, Mouse, Mouse + Analog Stick e Analog Stick, una volta verificate.
  Distinguere coordinate assolute, movimento relativo e arbitraggio degli
  assi; combinare con OR soltanto pulsanti della stessa azione. Evitare
  suffissi che attribuiscano a un solo dispositivo un'azione condivisa.
- Tenere P1/P2 indipendenti. Ricarica fuori schermo, fuoco secondario e
  calibrazione dipendono dal titolo: non generalizzare il comportamento
  di The Lost World o Star Wars di Supermodel ai giochi Model 2.
- Un profilo sconosciuto richiede fallback esplicito e avviso nel log, senza
  assegnare per somiglianza i controlli di un altro cabinet.
- Una porta 2 limitata a Coin/Start mantiene invariato il profilo del gioco; i
  descrittori disponibili sulla porta esprimono la limitazione senza creare una
  famiglia di profilo separata.
- Air Walkers pubblica quattro porte con lo stesso profilo approvato. Il backend
  mantiene quattro ingressi logici e riproduce la matrice reale: la porta F
  seleziona P1/P2 oppure P3/P4 sulle porte C/D e sulle due linee Start. Questo
  adattamento resta frontend-neutral; l'adattatore Libretro si limita a
  raccogliere le quattro porte RetroPad.

## Persistenza e responsabilità del frontend

La memoria persistente è esposta come SRAM Libretro in un contenitore versionato
che identifica il set e protegge il payload con checksum. Il `.srm` corrente ha
precedenza; in sua assenza il core importa le memorie native senza riscriverle.
La directory save restituita dal frontend viene usata direttamente: il core non
aggiunge un proprio livello `sm2-emu/<gioco>`. Il `.srm` gestito dal frontend e
gli eventuali `<gioco>.nv`/`<gioco>.eeprom` nativi condividono quindi la stessa
directory, anche quando RetroArch l'ha già organizzata per nome del core.
Questo non equivale ai save state.

I save state riusano la serializzazione frontend-neutral upstream 0.9.8. Le
macchine espongono la stessa immagine `SM2STATE` sia su file sia in memoria;
l'adattatore Libretro implementa soltanto `retro_serialize_size`,
`retro_serialize` e `retro_unserialize`, lasciando slot e nomi dei file al
frontend. Il buffer Libretro è fisso a 9 MiB: RetroArch 1.22.2 interroga la
dimensione prima del caricamento del contenuto e considera uno zero come
funzione assente. Il payload reale resta più piccolo ed è completato con zeri.
Il core negozia inoltre `RETRO_ENVIRONMENT_SET_SERIALIZATION_QUIRKS` per
dichiarare la dipendenza da piattaforma ed endianness; il rifiuto del comando
da parte di un frontend precedente costituisce il fallback e non modifica il
formato né i callback di serializzazione.

Magic, supported version, game identity and board are validated before loading.
Truncated/invalid machine payloads roll back to the preceding machine snapshot.
The current machine writer uses format 8; the reader accepts formats 4–8.
Format 4 carries the port's serial lightgun/P3–P4/EAB fields; later formats add
sound scheduler conversion (5), audio history (6), persistent geometry (7)
and local communication queues (8). Data absent from an older archive cannot
be reconstructed merely by accepting its format. The fixed 9 MiB buffer
includes a 96-byte frontend runtime tail. The next save writes format 8 without
rewriting the file that was loaded.

After loading, derived renderer state and queued audio are invalidated and
rumble is stopped; saved cadence, audio delivery remainder, input runtime,
gun-flash state and output DC history are restored from the frontend tail.
An external `Linked Cabinets` session refuses save/load because the peer
Netpacket session is outside the machine archive. Platform/endianness dependence
and Musashi pointer rebinding preclude treating cross-process raw archive
identity as a portable semantic test. Current and historical qualification
scopes are recorded in `Docs/SAVE_STATE_COMPATIBILITY_REVIEW_2026-10-09.md`.

`Automatic Initial NVRAM Setup` è Enabled per default. In assenza sia del `.srm`
sia di NVRAM native valide, i parent supportati ricevono un campione completo
validato prima del primo frame; il core vi applica Country/Nation Export, con
USA come fallback quando Export non è disponibile, e
i valori offline necessari; il core imposta inoltre Daytona su Cabinet=Deluxe e
Super GT 24h su I/O Type=C, senza attribuire questo valore al default originale
del gioco. Motor Raid Deluxe likewise uses Cabinet Type=Twin for automatic
initialization and as the matching NVRAM selector default. Its native acquired
template remains Deluxe; saved NVRAM takes precedence over automatic setup,
and an explicit Deluxe selection remains available. The Twin compound fields,
mirrors and checksum use the existing validated NVRAM writer. Il campione
stabilisce subito un layout integro e
non richiede una modifica tardiva seguita da riavvio. I salvataggi esistenti
restano sempre prioritari; le successive scritture ordinarie del gioco
continuano a essere esportate dal frontend.

I primi override verificati sono `VF2 Difficulty`, `VF2 Country`, `VF2 Display
Type` e `VF2 Drink`, visibili soltanto per `vf2` e autonomi. Come in Supermodel, un interruttore generale `NVRAM Settings`
è Disabled per default; quando è Enabled, ogni parametro mostra soltanto i valori
reali e viene applicato al caricamento. La descrizione di Country documenta
l'effetto collaterale del menu Service originale senza imporlo nel core. Gli
override aggiornano il CRC e non toccano altri campi o calibrazioni.

La scheda lightgun seriale riceve coordinate e stato off-screen come segnali
distinti. L'adattatore Libretro alimenta il secondo esclusivamente da
`RETRO_DEVICE_ID_LIGHTGUN_IS_OFFSCREEN` o dalle scorciatoie di ricarica
esplicite; un Mouse arrivato al bordo resta quindi on-screen. La deduzione MAME
basata sul 5% degli estremi calibrati resta confinata all'adattatore standalone,
che non dispone del segnale Libretro. Nel core Libretro la Core Option
`Mouse Edge Off-Screen Reload`, disabilitata per default, può applicare la stessa
soglia esclusivamente a un colpo Mouse Left; non converte in off-screen gli assi
RetroPad né le sole coordinate al bordo.

Affidare al frontend remapping, opzioni per gioco, shader, volume generale,
pausa, screenshot e sincronizzazione della presentazione. Il core comunica
per default la modalità `60 Hz (Default)`. Questa esegue un nuovo frame
macchina per ogni callback a 60 Hz, accelerando gioco e suono di circa il 4,3%,
e ricampiona l'audio al rate dichiarato dalla scheda. La frazione usata per il
conteggio dei campioni resta nello stato Libretro. Evitare una seconda
interfaccia ImGui o nuovi parametri EmulationStation per funzioni già gestite da
RetroArch. Le prove frontend GPU restano indicate nella roadmap.

The timing menu follows the user's cross-core convention: `60 Hz (Default)`
and `57.524 Hz (Native Model 2)`. The stored `sm2_av_timing = "60hz"` value
selects one new machine frame per callback, including when read from an
existing option file; the next save keeps that value. An explicit `native`
setting continues to select the Model 2 cadence. The earlier duplicate-frame
behavior is removed. TGPulse-Next adopts the corresponding Model 1 wording in
its own project chat.

## Power Sled NVRAM Adapter

Power Sled's reviewed per-program NVRAM fields and independent initial images
use the existing adapter engines. The layout gate waits for three concordant
native 28-byte settings blocks and valid numeric ranges; manual writes update
only their proven field copies. No machine implementation or native checksum
is added. Existing SRAM/native saves retain precedence over initial seeding.
Country and conditional ID assignment are not automatically overridden. See
`Docs/POWER_SLED_NVRAM_OPTIONS_2026-10-09.md`.

## Funzioni da valutare separatamente

PowerPC/JIT, New3D/Legacy3D, DSB, widescreen, threading e collegamento tra
cabinet di Supermodel non dimostrano la disponibilità degli equivalenti SM2.
Anche il supporto standalone SM2 a Vulkan, periferiche SDL/evdev, bordi Sinden
e feedback richiede un adattamento alle API e ai driver del frontend.
Rumble e forza direzionale del volante sono capacità distinte: non promettere
force feedback completo da una sola interfaccia di vibrazione.

Il gamepad rumble usa un adattatore isolato in `src/libretro/rumble.*`. Legge
il comando della drive board tramite l'accessore neutrale della macchina e lo
sterzo già acquisito dal frontend, quindi invia strong/weak tramite
`RETRO_ENVIRONMENT_GET_RUMBLE_INTERFACE`. La macchina non include header
Libretro e non conosce il dispositivo del frontend. Il modello delle intensità
relative e della durata replica upstream 0.9.7 sulla scala normalizzata
Libretro; il guadagno complessivo resta di RetroArch. La gestione SDL degli effetti temporanei non è
necessaria perché il frontend riceve direttamente lo stato persistente dei due
motori. Reset, unload, errore e disattivazione azzerano sempre entrambi.

Il recoil delle lightgun `evdev` resta una funzione futura specifica della
piattaforma. Non viene mescolato con il gamepad rumble né con i descrittori di
input, perché Libretro non espone un comando recoil lightgun equivalente.

## Verifica prima di dichiarare il supporto

Provare in RetroArch categorie, cambi di opzione, riavvii richiesti,
load/unload tra profili diversi e override per gioco. Confermare che i valori
iniziali mantengano la baseline e che i salvataggi esistenti siano preservati.
Verificare comandi canonici e alias, calibrazione e indipendenza P1/P2 con
dispositivi reali sui frontend dichiarati. Una build o un menu correttamente
visualizzato non dimostrano il funzionamento dei controlli.

## Internal Resolution Extension (2026-10-08)

Upstream `609c3c53f0d8b48555a992df9d4e6fe7da3a86de` is backported for the
shared maximum scale and standalone configuration/menu. The Libretro adapters
expose 1×–8×, default 1×, reusing the common dimension-clamp helper. They keep
requested and effective scale separate, return the effective scale after GPU
initialization, and notify the frontend when the base geometry changes.
The maximum geometry remains sized for the request so context recreation can
restore the requested resolution on a more capable device. No emulated machine,
CPU timing, audio, input mapping or Save State layout changes are required.
See `Docs/UPSTREAM_RESOLUTION_PACKAGE_2026-10-08.md` for verification and limits.

## Shot-Flash Presentation History (2026-10-08)

The `96e0f0e` detector and tile drawing/upload changes are shared with
standalone. The Libretro adapter calls the detector after each emulated frame
for games whose metadata declares a lightgun interface. Hide Shot Flash remains
visible for every game, default Disabled; it is a no-op on other games.

A frontend-neutral `Model2Video::GunFlashState` accessor exposes presentation
history. Machine reset/archive load clears that transient history. Libretro
saves a tagged four-byte representation at offset 76 in its existing 96-byte
frontend tail, restoring it after machine load. Legacy zero-filled reserved
bytes mean empty history. The marker is `0x47460000`, low bits 0–1 store held
triggers, bit 2 the previous press, bit 3 the previous full window and bit 4 the
current suppression. Neither the machine archive nor the 9,437,184-byte ABI
size changes. The tail version remains 1 because older readers ignore this
previously reserved field.

Standalone keeps the upstream transient presentation behavior across loads;
only Libretro uses the reserved frontend extension. No emulated RAM is altered.
See `Docs/UPSTREAM_GUN_FLASH_PACKAGE_2026-10-08.md`.

### Split Device Firmware and Power Sled — 2026-10-08

Upstream `600f1c8` supplies Daytona/Desert Tank device-set metadata without
changing their I/O. Preserve frontend system-BIOS priority over embedded
firmware when adapting upstream's conditional archive lookup. Power Sled
`e8d96c1` reuses existing `Inputs::in3` for port E and sets its link offset
to 0x180; it adds no serialized fields or Core Options. The new profile maps
upstream cabinet actions through Libretro and retains preliminary status.
See `Docs/UPSTREAM_ROM_LOADER_PACKAGE_2026-10-08.md` for tests and limitations.

### Sample-Locked Sound Timing and State Versioning — 2026-10-08

Upstream timing patches `def088c` (scheduler/stall/cache subset), `8e1e7c3`
and `71a81e3` now drive the shared sound machine. Frontend gains remain in
the established output stages. No new option or visibility change is needed.
Machine Save State format 5 distinguishes the new scheduler units, while
Archive carries source version 4 during legacy reads so Model2Sound converts
its clock carries without changing field widths. Old cores reject version 5;
new saves retain the fixed Libretro capacity and existing frontend tail.
See `Docs/UPSTREAM_SOUND_TIMING_PACKAGE_2026-10-08.md` for the isolated pristine
reference, four-board adapter comparisons and fresh-process compatibility tests.


### Selective i960 and Area Timing Imports — 2026-10-08

`8a49096`, `7080210`, `e36f757` and `1987d82` add CPU/SHARC corrections,
Virtual-On tile/texture waits and per-area data waits on all four boards.
The existing optional ties-to-even rounding implementation and published
frontend contract are unchanged. Timing remains frontend-neutral; instruction
fetch guards are transient, while existing CPU-control registers already belong
to the machine archive. No new serialized fields or frontend selector are
needed. Original Model 2 retains the port's Daytona Maxx protection branches.
See `Docs/UPSTREAM_I960_PACKAGE_2026-10-08.md` for imports, pristine comparison,
old/new state checks, Linux verification and installed-core RetroArch evidence.


### Audio Balance and Source Auto — 2026-10-08

The upstream SCSP profiles (`abb42bb`, `88d5557`, `cb57c0a`, `3a71c1d`),
original-board output attenuation and Top Skater DSB2 level are derived from
metadata. Enhanced Audio Balance remains Enabled by default. Source Gain Auto
is conveyed separately from manual 100% through the frontend-neutral SoundBoard
setter. Auto uses the enabled game profile; manual percentages replace it for
that source. MultiPCM automatic contributions are summed before the upstream
board-level attenuation, while manual contributions retain the hardware routes.
The obsolete VF2 per-slot profile is removed. Its serialized fields remain in
the published archive layout for compatibility; current metadata and frontend
preferences reapply the new profile on load. No archive-size/version change is
needed. See `Docs/UPSTREAM_AUDIO_BALANCE_PACKAGE_2026-10-08.md`.

## Upstream Control Reconciliation — 2026-10-08

The adapter integrates corrected House of the Dead trigger metadata and
upstream serial-gun endpoint handling. Libretro normalized screen coordinates
already refer to the game image, so standalone window/desktop conversion,
RawInput and evdev ownership are excluded. Native off-screen status remains
independent of on-screen coordinates. Legacy explicit P2 IN2 metadata remains
readable, while the bundled database now uses IN1 bit 1 for every HOTD set.

Top Skater preserves published independent Curving/Slide axes and adds upstream
trigger aliases and D-Pad steering. The user approved Progressive as the
Curving default, retaining Linear through a universally visible Core Option.
Response and alias policy live exclusively in `src/libretro/`; no machine or
archive layout changes. Ski Super G channel corrections
were already present. The user approved independent Swing/Inclining axes as
the core-specific behavior, with optional coupling through frontend binding
in Settings > Input > Port 1 Controls. Do not add a Core Option or Quick Menu
selector. Built-in coupling is only a future reconsideration if frontend
binding limitations or gameplay evidence justify it; exact equivalence of
upstream response and rounding is not established.

## Drive Board and Rumble Reconciliation — 2026-10-08

The neutral shared `src/osd/drive_command.*` decoder is imported verbatim from
upstream `868dce7`, including preceding Daytona spring/Kick and Rally brake/chop
metadata fixes. `DriveProtocol::Indy` is appended to retain the existing enum
values. `drive_protocol="indy"` is parsed and inherited; Indy 500 and Over Rev
metadata select it, with Over Rev drive-board writes now enabled for its family.
No control mappings, audio defaults, Core Option names or archive layout change.

The adapter maps Push/Kick to existing gamepad impacts, including upstream's
Kick direction threshold at 2*256 steering units. Spring geometry and Rally
chop metadata are preserved by the shared decoder for upstream compatibility;
wheel force output is outside the standard rumble adapter. The existing generic
cornering vibration, 12-frame tail and lifecycle stop behavior are preserved.
All new decoded effect fields remain adapter state and are cleared on reset,
load, unload and disable; they are not added to machine archives.

Over Rev's game-side board traffic requires the existing HARDWARE TYPE setting
SEGA STCC. This is the approved Hardware Type core default and automatic initial
override for Over Rev and its parent-compatible clones. The override is applied
to newly seeded templates only, through the existing generic patch/checksum
engine. Keep the acquired native NORMAL (2in1) template unchanged. Existing
frontend/native NVRAM retains precedence, and explicit saved Core Option values
remain respected by NVRAM Settings. See
`Docs/OVER_REV_HARDWARE_DEFAULT_2026-10-09.md` and
`Docs/UPSTREAM_RUMBLE_PACKAGE_2026-10-08.md` for evidence and physical controller
qualification limits.


### Persistent Geometry State and LFO Restore — 2026-10-08

Machine Save State format 7 adds the geometry engine's persistent register and RAM
snapshot (texture/log RAM, polygon RAM, matrices, clip planes, lighting,
texture and window parameters). These values persist across display lists and
cannot be rebuilt from the current buffer RAM alone. Keep this fix frontend-neutral
in Geometrizer; generated polygon/depth pools remain transient. Formats 4/5/6
remain readable without claiming recovery of RAM absent from their archives.
The fixed 9 MiB Libretro buffer and 96-byte frontend tail are unchanged.
MultiPCM restores archived pitch/amplitude LFO steps after rebuilding pointers,
preserving the effect of zero register writes. No Core Option is added.
See `Docs/VIRTUA_COP_SAVE_STATE_REPLAY_2026-10-08.md` for the isolated pristine
serializer probe, exact replay campaign, compatibility evidence and limitations.


### Local Communication State and Set Identification — 2026-10-08

Format 8 includes bounded pending loopback frames and its overflow flag, preserving
single-cabinet communication state independently of external networking. Formats
4/5/6/7 remain readable; their missing queue is cleared on load instead of retaining
future traffic. External transport sessions are not serialized. Libretro's fixed
9 MiB capacity remains unchanged. Keep this fix in the frontend-neutral transport
and M2Comm rather than frontend callbacks.

ROM identification still prefers chip match quality. Resolve exact score ties by
archive stem to distinguish sets with identical chips and different patches, such
as Power Sled Main/Relay. Explicit standalone set selection retains precedence;
renamed ambiguous archives retain catalogue-order fallback. No game-specific
Libretro option or duplicate ROM loader is introduced. See
`Docs/POWER_SLED_PRELIMINARY_VALIDATION_2026-10-08.md` for evidence and limits.


### Power Sled Mixed-Program Netpacket Ring — 2026-10-08

The adapter adds the three Power Sled sets to Linked Cabinets with Disabled /
3 Cabinets only. They share family `powsled`. An optional one-byte HELLO payload
identifies the ROM program: 1 Main, 2 Relay, 3 Slave. A Power Sled roster requires
all three distinct program tags; these are independent of communication RAM,
FG, link ID and operator Ride ID. Existing games keep their empty HELLO payload
and wire version 2. Power Sled had no prior linked-session contract.

`M2Comm`, its MAME-derived ring protocol, Power Sled receive offset `0x180`, and
initial frame size `0x0e00` are unchanged. All new transport identity validation
and native board transition logging live in `src/libretro/`. No upstream-facing
machine modification is needed for this integration. No unverified Automatic
Network Settings or NVRAM offsets are exposed. Actual RetroArch evidence shows
Main 1/3, Relay program 3/3, Slave 2/3 and access to all three Service Menus.
See `Docs/POWER_SLED_SERVICE_MENU_CAMPAIGN.md` for evidence and acquisition gates.


### Power Sled Color Presets And Second Rider — 2026-10-09

Automatic Network Settings manages reviewed Ride ID colors on `powsledm`
and `powsled`: Silver, Red, Black, Disabled. The new selector defaults to
Disabled to preserve existing manual Ride selections. The ROM program fixes
the native role; frontend host/client status does not change it. `powsledr`
retains its native Relay identity and has no color selector. This reuses
`automatic_network.cpp` and the existing NVRAM apply/write-back path; no
communication protocol, hardware role or unreviewed field is modified.

Power Sled Port 2 now supplies independent P2 Entry/Call and analog
handlebars. MAME defines P1 on mux 1/3 and P2 on 5/7. P1 bindings and Test/Service conventions are retained. P1 West (RetroPad Y)
and North (RetroPad X) supply secondary P2 Entry/Call as requested on
2026-10-11, including when Port 2 is disabled. Appended neutral
`AnalogControl` identifiers and metadata parsing activate the existing machine
I/O callbacks for 5/7; no Libretro callback is added to machine code.
P2 is a rider in the same cabinet, not the Slave network instance. Save State
version 8 and frontend buffer size remain unchanged.

The generic manual launcher reuses `test-retroarch-netpacket.py`; see
`Docs/LINKED_CABINET_LAUNCHER.md`. Native roles are embedded. Power Sled always
starts Main, Relay and Slave programs, displaying Main/Slave above Relay;
its optional Relay CLI switch is ignored.

## Unified ANS Values And Explicit ROM Lists — 2026-10-09

Automatic Network Settings uses one raw-value convention: `0` Disabled,
`1` Master / Cabinet 1, `2` first Slave, subsequent sequential numbers for
other cabinets, and `relay` where supported. Visible labels retain their
reviewed game-specific meanings. Power Sled Main/Slave use `1` Silver,
`2` Red and `3` Black. Core defaults remain Disabled (`0`) for those programs
and Master (`1`) for generic playable sets. Dedicated `powsledr` and `vonr`
offer only `relay`; Power Sled Relay manages no color, while Virtual On Relay
retains its reviewed No Link operator attribute. ROM identity still determines
fixed program roles. No aliases or migration for old development ANS values
are implemented, as explicitly directed by the user. Native NVRAM keys and
values, emulation, communication and save formats are unchanged.

The launcher accepts a repeated ROM name, comma-separated per-instance names,
and optional per-instance `:ANS` suffixes. Its transport receives the explicit
ROM list; it does not infer a different ROM from a numeric suffix. An explicit Power Sled
Main/Slave/Relay triplet retains the native Main/Relay/Slave transport order
while preserving declared controller mapping and role-based window positions.
Other lists and repeated names are passed through literally. Per the user's
KISS instruction, the launcher does not check game compatibility, native
program combinations or game-specific cabinet limits; the core/frontend own
connection behavior. Process-lifecycle success is separate from network proof.
Explicit suffixes override saved values. Without suffixes, valid Power Sled
session colors persist; fresh sessions select Silver for Main and Red for
Slave. The optional Relay flag remains ignored for Power Sled.

### Power Sled Main Audio Regions — 2026-10-09

The Main approximation now declares the matched Slave audio program
EPR-19466 and sample FPR-19459. The existing frontend-neutral loader searches
the selected archive first and opens the split parent `powsled.zip` / `.7z`
only when required chips are missing. CRC lookup remains enabled. The old
Relay audio chips are absent from the Main definition; Relay retains them.

The small generic loader adjustment gives a known archive name precedence
when all maincpu chips match by CRC, preserving `powsledm` selection after its
audio definition changes. Otherwise the existing whole-set scoring remains.
An incompatible program cannot be selected by filename alone. This also makes
known split sets identifiable before their parent supplies missing regions.
No new metadata schema, emulation branch, Core Option, audio callback or
serialization layout is introduced. Imported changes are limited to the ROM
loader and Main ROM metadata; sound synthesis is unchanged. See
`Docs/POWER_SLED_MAIN_AUDIO_INTEGRATION_2026-10-09.md` for evidence and limits.

### Power Sled Main Ride Caption — 2026-10-10

The Main database patches its two identity-caption selectors to read the
native NVRAM Ride byte instead of the internal role word. Display the same
`THIS IS <COLOR> RIDE` labels as Slave, keeping Main's role and operator/network
behavior intact. Original text/fallback tables and code addresses remain.
This is a Main-only metadata adaptation; no machine or Libretro callback
change. See `Docs/POWER_SLED_MAIN_RIDE_CAPTION_2026-10-10.md`.

### Power Sled Main First-Person Sled Color — 2026-10-10

The Main database selects first-person sled resources from the native NVRAM
Ride byte, preserving the race object index and Main role. Three resource
reads call a byte-load helper in an existing twelve-byte zero gap; neighboring
functions and resource tables remain intact. Paired RetroArch captures verify
Red instead of black with Ride ID Red. Remote/third-person selection paths
are outside this qualification. See
`Docs/POWER_SLED_MAIN_SLED_COLOR_2026-10-10.md`.

### Power Sled Main Mode-Selection Scene — 2026-10-10

The native mode-selection drawing initializer handles rider colors and Relay,
but selects no drawing callback for Master role `0x0200`. Main therefore shows
the mode overlay on a black background. Read the native NVRAM Ride byte only
at this visual selector: two database patch words for Relay-derived Main and
two guarded adapter patch words at the relocated Slave site. Existing drawing
callbacks and assets are reused; Master identity, network/operator paths and
race index are preserved. Paired RetroArch observation demonstrates the missing
scene and its restoration; both normal installed-core donor runs pass linked
race entry and save integrity. Related placement selectors have no demonstrated
defect and are unchanged. See `Docs/POWER_SLED_MAIN_PRESENTATION_2026-10-10.md`.

### Power Sled Master Donor — 2026-10-10

The always-visible System option `sm2_power_sled_master_donor` chooses Relay
(default) or Slave for `powsledm` at content load; other games ignore it.
The adapter loads only CRC-verified Slave maincpu from the current archive or
adjacent `powsled`, validates all patch sites before writing, and adapts its
initializer to Main. Both program bases include the native Ride caption and
first-person sled color fixes, plus the subsequent mode-selection scene fix.
Missing/incompatible requested donors fail
loading. Main identity, I/O, assets, audio, network role and SRAM are preserved.
Save States tag Slave in an unused frontend flag and reject donor mismatches
before machine mutation; legacy untagged states remain Relay. No machine/CPU
frontend dependency or state-size change. Reload content to change the donor.
See `Docs/POWER_SLED_MASTER_DONOR_2026-10-10.md`.

### Manx TT Counted Relay — 2026-10-09

The native Manx TT boot program requires every node, including shared role 3,
to have an ID in 1..count. A frontend-neutral `M2Comm` configuration, enabled
only by the Manx TT family in the Model 2A machine, counts that Relay during
enumeration and assigns a positive ID. Subsequent gameplay qualification also
requires transmitting its own native status slot before the received slot train;
pure forwarding passed boot but blocked race selection. Both vblank and FG-read
paths use the existing shared-RAM send path for this counted node.
The generic role-0 Relay remains uncounted. This content-load configuration
does not add serialized mutable state, frontend callbacks, options or bindings.
See `Docs/MANX_TT_RELAY_INITIALIZATION_2026-10-09.md` for native code evidence,
reference limits, exact old/new baseline and RetroArch qualification.
The race-selection correction, normal-core two-rider races, LIVE camera,
Time Up/ranking/re-entry and unchanged serialization/UI are recorded in
`Docs/MANX_TT_GAMEPLAY_VALIDATION_2026-10-09.md`.


### Manx TT Cabinet Audio And Additional Board — 2026-10-10

The always-visible frontend selector and committed EEPROM policy live in
`src/libretro/manxtt_audio.*`; owned alternate audio regions outlive the machine.
The generic `RomLoader::load_regions` reuses archive lookup, CRC verification
and assembly without loading donor main programs or EEPROMs. It requires every
requested chip even for otherwise optional regions.

`Model2Sound` adds frontend-neutral optional ROM banks and the existing M1
board, with shared host UART fanout, native board clocks, one populated PCM,
existing Gain controls and exact-rate stereo resampling. These shared machine
changes contain no Libretro headers/callbacks. Format 9 persists bank identity,
auxiliary CPU/chips/UART and resampler history while retaining formats 4–8 on
read. Missing required banks/board reject state restoration and trigger rollback.
The main CPU and physical input definitions are unchanged. See
`Docs/MANX_TT_CABINET_AUDIO_2026-10-10.md`.

### Manx TT Deluxe AMS Acknowledgement — 2026-10-10

`src/hw/manxtt_ams.h` owns the minimal acknowledgement state, independently of
the generic drive-board latch. `Model2` connects it through existing parallel
D/E callbacks for the three Manx TT sets only. The native EEPROM Cabinet Type
at byte `0x0a` selects Deluxe (0) or Twin (1) for Revision C/D; the Deluxe-only
program always connects it. Twin keeps its original P2 input. Each I/O access
observes the current cabinet selection; transitions and machine reset clear
the handshake. No frontend callback, Core Option, ROM patch or calibration
write is introduced by this stub. Cabinet audio selection is independent.

Format 10 appends the enable/response bytes to Model 2A serialization and
validates their domain on load. Formats 4–9 have no AMS state and initialize
it to idle; the original legacy file is not rewritten. The fixed Libretro buffer
and other board payloads retain their layouts. This implements native boot
acknowledgements only; motors, position feedback, diagnostic error simulation
and a complete drive-board protocol remain outside its scope. See
`Docs/MANX_TT_MOTION_STUB_2026-10-10.md`.

### Power Sled Master Role And Color — 2026-10-10

The Relay-derived Main retains command role `0x0200` and publishes its native
Ride color separately. ROM-database adaptations in all three Power Sled programs
use that color for the roster, both cabinet counts and rider packet selection;
Main's local race index and native panorama offset follow Ride ID. Command scans
retain the original role identities. The shared native boarding introduction
still constructs four color actors independently of local Ride selection.
Main Silver / Slave Red and the inverse order qualify in bounded RetroArch races.
No generic machine/renderer change, new option or binding is required. These
patches extend an undumped-Main reconstruction and do not authenticate factory
firmware or mixed old/new peer programs. See `Docs/POWER_SLED_MASTER_COLOR_2026-10-10.md`.

### Power Sled Four-Color Menus And Optional Master Archive — 2026-10-10

The ROM database supplies narrow i960 Service Menu patches for Main, Slave
and Relay. The Ride selector always cycles Silver / Red / Black / Yellow,
independently of detected rider count. Main and Relay commit their selected
color to native NVRAM while retaining command roles `0x0200` and `0x0100`.
Relay's value line displays its stored color rather than its fixed role label.
All three per-game NVRAM menus use the same four values; ANS adds `4` Yellow
for Main and Slave only. Relay still offers only ANS `relay`.

The production Power Sled transport accepts one Main, one to three Slaves and
an optional final Relay, with two to five total instances and at most four
riders. The role tags and existing wire format are unchanged. The runner checks
the actual native total instead of assuming three. Existing non-Power-Sled
registration and transport rules remain unchanged.

Frontend-neutral `GameSpec::rom_fallback` names an adjacent donor archive.
The database declares `powsledm` fallback `powsledr`, retaining parent `powsled`.
`RomLoader` preserves primary-chip precedence, opens the donor only for missing
data, then uses parent fallback. Required regions/chips and CRC checks remain
mandatory. A declared fallback fixes the requested game identity even when its
primary archive is absent; ordinary file/CRC identification is unchanged.
Invalid existing archives still fail. Valid empty ZIP entries are recognized.
The Libretro launcher supplies an owned empty content entry when RetroArch
needs an existing file; machine code has no frontend dependency.

Phase 1 documents four-value cycles independently for all three programs;
Phase 2 uses the existing complete, resumable RetroArch recipe and validates
every discrete commit and fresh reload before generating the extended options.
Calibration is not acquired. Details and evidence are retained in
`Docs/POWER_SLED_YELLOW_AND_MASTER_ARCHIVE_REVIEW_2026-10-10.md`.

### Optional Power Sled Master Music — 2026-10-10

`src/libretro/power_sled_audio.*` owns the Power-Sled-family-only, Disabled-default
Relay Audio selector, CRC donor lookup, guarded in-memory i960 patches and
native music-task activation. Only Master content is affected; reload is
required. Original rider/camera/network construction is retained. Generic
`Model2Sound` adds a second existing SCSP/68000 board, tagged serial routing and
an exact-clock PCM mixer, without Libretro headers or frontend callbacks.
EAB and the output filter propagate to the additional board. The adapter
applies an independent Relay Audio Gain after primary SCSP Gain configuration.
Native state writer 11 stores both boards, routing and queue; formats 4–10 stay
readable without the added board. The frontend rejects Master states from a
mismatched Relay Audio setting before mutation. Disabled old/new output and
format-10 continuations match exactly; Enabled ABI replay and a linked RetroArch
race with music pass. Boarding silence follows the original Relay stop/start
sequence and was confirmed by the user. Missing donors/unsupported patch guards
retain original rider audio. See `Docs/POWER_SLED_MASTER_MUSIC_EXPERIMENT_2026-10-10.md`
for the native addresses, qualified recordings, deployment and fidelity limits.

### Experimental Power Sled Standalone Mode — 2026-10-10

The Relay extension keeps native role `0x0100`, runs continuous Attract with
four local native actors and an inert Master status view, and never requests
selection or racing. Its local link initiates a one-node ring independently of
the program role. Guarded Test/Exit support returns to native Attract.
The isolated Relay B_CRX diagnostic counts its single real board after setting
the Relay-presence flag; it does not fabricate rider peers. This guarded
adaptation applies only to Relay Standalone with Linked Cabinets Disabled. See
`Docs/POWER_SLED_RELAY_ATTRACT_2026-10-11.md` for failed candidates, native
addresses, final normal-core verification and deployment boundaries.

`src/libretro/power_sled_standalone.*` contains an adapter-owned, guarded
Master gameplay reconstruction and a separate Relay continuous-Attract
adaptation for one-node loopback. Its family-only System selector defaults to
Enabled and applies only with Linked Cabinets Disabled. Slave and linked
sessions are unchanged; Relay Audio On Master remains independent. The Master
reconstruction rotates four native ownership entries, adapts every race-count
case and maps four self-published competitor records. It redirects the reduced
one-node race dispatcher to the full native constructor, includes all four
owners in attract physics and recognizes local Silver ownership during startup.
The boarding/countdown constructor allocates all four local color tasks instead
of halving the field; this restores Black/Yellow camera and countdown updates.
Native human, AI and physics tasks supply movement; no frontend position
simulation or synthetic Slave packets are used. Only HUD/finish-order filters
include AI as competitors; physical human-node count stays one.
A guarded Standalone-only Exit detour at `0x1c4a0` clears the outgoing Test
command at `0x5293f4`, replays the displaced phase load and resumes native Exit
at `0x1c4a8`. Helper space and instruction/operand guards are checked before
mutation. This prevents one-node loopback from reopening Test after restart;
native cleanup and linked programs retain their original path. A matched
isolated RetroArch replay confirms return to attract.
Content reload is required to switch the patched program or enter linked play;
active standalone retains one-node transport until that reload. Frontend state
flag bit 8 rejects mismatched Standalone configurations before mutation. ABI checks pass;
corrected Red runtime confirms advancing scenes, timer/time extension and
AI-aware ranks, result and GAME OVER. Yellow's normal-core capture confirms
course rendering, 3 / 2 / 1 / GO and an advancing race. The normal installed core
is updated with backup/hash checks; dev remains absent. Yellow also reaches
a 4th result, GAME OVER and moving attract again, with valid persisted color/CRC
and clean process shutdown. An audible repeat confirms native Relay race music
in recorded PCM. Bounded experimental integration is complete; physical devices,
every color/difficulty and factory camera/title fidelity remain unqualified.
See `Docs/POWER_SLED_STANDALONE_EXPERIMENT_2026-10-10.md` for guarded addresses,
retained failed candidates, runtime evidence and deployment status.


### Power Sled Standalone Camera Boundary

The recently installed experimental override branches from `0x18c30` to
`0x18c40`, forcing native camera value 1 for every Ride color. This must not be
called an original single-screen mode. The controlled four-color comparison
confirms the prior color-specific panorama and shows that the override removes
that distinction. The user approves this uniform intro, identified as Silver, for every
Standalone Ride color. This is the accepted port presentation; the installed
binary is retained. Ordinary linked programs and Disabled mode
retain their existing panorama path. See
`Docs/POWER_SLED_COLOR_CAMERA_REVIEW_2026-10-10.md` for evidence and limits.

### Experimental Power Sled Relay Commands On Master — 2026-10-11

`src/libretro/power_sled_commands.*` owns the guarded Master-only operator
remap. System option visible for the Power Sled family only defaults to Enabled and requires reload;
Standalone and Relay Audio remain independent. Native Coin/Start opens selection,
Entry confirms and the original departure sound-task completion emits boarding
command 4 after the model motion ends. Pre-race Entry/Start emits native race
command 5. Call emits Emergency Stop `0x100`; Coin/Start recovers through native
command 1 before reopening selection. The existing Test ownership guard and
native receivers remain. Helpers use verified empty program space; no production
RAM scan, frontend delay or machine-to-Libretro dependency is introduced. Save
State flag bit 9 rejects mismatched command modes before mutation. See
`Docs/POWER_SLED_RELAY_COMMANDS_ON_MASTER_2026-10-11.md` for native addresses,
replay evidence and limits.

### Power Sled System Visibility And Auxiliary SCSP Gain

Explicit user exception: Master (`powsledm`) shows all four Power Sled System
switches; Relay (`powsledr`) shows only Standalone Mode; Slave (`powsled`) and
other sets show none. NVRAM Settings and ANS retain their existing rules. The new Audio option
`sm2_power_sled_relay_audio_gain` uses Auto / Mute (`0`) / 10%..100% and the
usual visible/no-op convention. After configuring primary sound sources, the
adapter applies this separate gain only to the auxiliary SCSP. A frontend-neutral
mutable auxiliary-board accessor mirrors the existing const accessor; no Libretro
headers or callbacks enter the machine. Relay balance is configured from
`powsledr`. Mixer routing, native sound commands, timers and serialization layout
are unchanged. Current bindings are listed in
`Docs/POWER_SLED_CONTROLS_2026-10-11.md`.

### Standalone B_CRX Diagnostic Reconciliation

The native physical-board scan excludes Master/Relay packet headers. In
Standalone, Master also hosts the human rider; the guarded branch at 0x24e8c
retains Master presence and counts this existing board once. Relay and the
three local AI are not additional physical boards. Native zero/excess-count
errors remain possible. The original review retained the native linked program when Standalone
is Disabled. See the startup diagnostic section of
`Docs/POWER_SLED_STANDALONE_EXPERIMENT_2026-10-10.md` for RetroArch evidence.

### Power Sled Single-Rider Attract Records — 2026-10-11

The matched two-rider reference and Main + Relay pair enter the same phase-4
constructor. A single physical rider has three native field records, whereas
`0x45400` always creates four visual actors. The fourth null mapping reads ROM
header bytes as geometry, including `0xfffff980` from address `0x10`.
Database helpers at `0x1f1200` and `0x1f1280` initialize/publish and map the fourth
local attract record only in phase 4 with one physical rider. Later phases and
multi-rider ownership retain native behavior. Master role and announced color
remain separate. Standalone's existing explicit four-record map already covers
this access; its additional AI/race changes remain separate.

B_CRX's Main-board count now belongs to the common reconstructed Main program,
with the Standalone guard expecting that shared word. It counts a real rider
board after its packet arrives, never a fabricated Slave or local AI board.
See `Docs/POWER_SLED_POST_RACE_AND_MASTER_RELAY_2026-10-11.md` for failed candidates,
matched runtime evidence, deployment hashes and remaining qualification limits.

### Power Sled Auxiliary Countdown Routing

The optional Master Relay Audio adapter additionally tags the native countdown
indices as `A0 62 xx`. `Model2Sound` translates this frontend-neutral routing
tag to auxiliary `A0 12 xx`; untagged group 12 stays on rider SCSP. No new
serialization fields or emulation/frontend dependency are introduced. The
adapter's guarded native callback checks the existing local camera index to
avoid duplicate Standalone cues and preserves native countdown checkpoints.
See `Docs/POWER_SLED_PRE_RACE_AUDIO_REVIEW_2026-10-11.md`.

### Power Sled Interrupted Result Sequence Audio

Auxiliary tag `A0 63 xx` maps to native Relay group-zero control. The adapter
uses `A0 63 03` to stop auxiliary audio sequences before switching scenes.
Native result playback ignores ordinary note-off; the driver's group-zero
control ends those one-shot voices without a board reset or gain change.
The separate Relay program uses the same native command on result return.
The three-byte packet buffer and state layout are unchanged; rider MIDI
continues to the primary board. See
`Docs/POWER_SLED_POST_RACE_AND_MASTER_RELAY_2026-10-11.md`.

### Optional Power Sled AI Finish Speed Fix

The Disabled-default experimental System option bypasses only the known native
late-course AI speed-clamp branch in all three Power Sled programs. Program
word guards preserve unknown revisions; the final stop remains unchanged.
Implementation stays in `src/libretro/power_sled_standalone.cpp`, applied once
to the assembled program at load. It introduces no machine/frontend coupling,
archive change or mutable runtime patch. The explicit family-only visibility
exception covers this Power Sled-specific switch.

Per-rider finish/control sound stops remain on the primary rider board. Only
scene-wide stops are adapted to stop the optional auxiliary Relay board.

Result music on the auxiliary board uses a two-callback native stop/start
handoff: retry the stop until accepted, then retry only the start. This keeps
accepted stop packets from starving the start under queue pressure; no
frontend delay, hardware reset or prerecorded music is used.

### Reference ANS Visibility And Power Sled Defaults — 2026-10-11

The user's latest instruction aligns ANS with the current TGPulse-Next
reference: register reviewed per-set ANS only for networking titles, and
hide it when NVRAM Settings is Disabled. Exactly the loaded network title's
entry is visible. This supersedes the briefly requested generic non-network
no-op; that candidate was removed and is not deployed. All playable network
sets default to raw 1; fixed-role Relay sets retain their only permitted
value, relay. Existing raw keys and saved selections are preserved.

Current TGPulse-Next code gates ANS by NVRAM Settings and restores offline
fields with Linked Cabinets OFF. Supermodel documents ANS as pending in its
roadmap. Existing SM2 offline policy is retained; Power Sled ANS selects Ride
color independently of its fixed program role.

Power Sled System order is Standalone, Relay Audio On Master, Relay Commands
On Master, AI Finish Speed Fix, followed by NVRAM Settings. All four default
Enabled and remain family-only under the explicit user visibility exception.
Standalone is ignored in linked sessions. Explicit saved Disabled values are
not rewritten. Relay Audio On Master remains user-controlled with a separate
Relay; mute/disable one source if both instances would otherwise play music.

### Reference Help Text Alignment — 2026-10-11

ANS and NVRAM Settings help now reuse the applicable TGPulse-Next wording for
managed selectors, NVRAM gating, return-to-game application and automatic reset
when persisted values change. SM2's `apply_pending_option` already resets the
machine after a Changed result; this is a description correction, not a new
reset policy. Power Sled help retains its distinct program-selected role and
color selection even with Linked Cabinets Disabled. Fixed Relay help retains
the manual Power Sled Ride ID and Virtual On No Link behavior. Supermodel's
current NVRAM description requires restart and its ANS implementation is pending;
those lifecycle claims are not copied into SM2. The manifesto now explicitly
includes descriptions/help text in mandatory reference comparisons. This
review covers ANS and NVRAM Settings; it does not certify every Core Option's
help text across all projects.

Verification: normal core rebuilt, save-RAM checks passed and only
`sm2_libretro.dylib` deployed with backup/hash verification. Installed SHA-256
`57de11b44496abe3436e30ace2277d9e959b4ad690046b6521c54462f0598850`.
No emulation behavior changed and no new gameplay run was needed for this
text-only correction. Usage meter remains 5% (integer-rounded).

### Upstream Gun Mapping Integration (2026-10-11)

The shared AnalogChannel point schema/parser and standalone interpolation follow upstream `b4c0931`; Model 2C removes the old BEL calibration seed rather than retaining frontend-specific RAM overrides. The Libretro adapter adds optional RC2 and HOTDP mappings with Custom (SM2-Emu) default and Linear (MAME) selectable, as approved. These frontend selectors do not alter machine code. BEL initial-template calibration is generated separately from source provenance in `data/bel-calibration-defaults.json`; valid saves remain authoritative. See `Docs/GUN_MAPPING_INTEGRATION_2026-10-11.md`.

### Country Default Priority (2026-10-11)

For reviewed Country/Nation selectors, choose the first supported region in this order: Export, Europe, U.S.A.; preserve the existing default if none is supported. Automatic Initial NVRAM Setup uses the same Option default. Preserve native value encodings/order and explicit saved selections. `scripts/update-country-defaults.py` reapplies this policy after regenerating older diagnostic-derived option data; the catalog audit enforces it. This changes Over Rev (including both inherited clones) and Super GT 24h from USA to Europe.

## Ski Super G Drive Board Acknowledgements — 2026-10-11

Ski-specific command/response wiring belongs in Model2C, independent of the
frontend. PE stores the command in the existing archived drive-board latch;
PD returns the stationary startup acknowledgement (`CE` for zero, `FF` for
nonzero). Reset clears this latch for Ski. Other games keep their previous
callbacks and rumble handling. No archive fields or version changes are needed.
The adapter's obsolete timed Test injection and its Core Option are removed.
See `Docs/SKI_SUPER_G_DRIVE_BOARD_STUB_2026-10-11.md` for program evidence,
qualification and limits; this is not mechanical or full firmware emulation.

## Cornering Rumble Frontend Deadzone — 2026-10-11

Synthetic cornering vibration now consumes the frontend-processed steering
callback with a deliberate 5% rumble-only onset threshold requested in the
subsequent user review. Remaining travel is rescaled to preserve peak strength. It retains its existing full
travel intensity and left/right symmetry, with signed endpoint clamping.
Native impact/kick decoding and its own direction threshold are unchanged;
12-frame tail, disable/reset/unload stops and archive layout are preserved.
No frontend settings query or new Core Option is introduced. See
`Docs/RUMBLE_FRONTEND_DEADZONE_INTERCHANGE_2026-10-11.md`.
