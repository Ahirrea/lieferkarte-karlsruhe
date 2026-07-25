# ✅ Umgesetzt

Fertig und live. Die Abschnitte bleiben als Kurzprotokoll stehen – interessant
ist jeweils **der Haken**: warum es so gelöst ist und nicht anders.

Die Architekturentscheidungen, die in diesen Haken stecken, sind zusätzlich als
ADRs herausgezogen: [ADR-004](./entscheidungen/ADR-004-oeffnungszeiten-eigener-parser.md)
(Öffnungszeiten-Parser, Europe/Berlin), [ADR-005](./entscheidungen/ADR-005-cuisine-nicht-protokollieren.md)
(Küchenstil wird nicht protokolliert), [ADR-006](./entscheidungen/ADR-006-pwa-network-first.md)
(PWA network-first). Der Text hier bleibt unverändert.

**Doku:** [PRD](./PRD.md) · [Anforderungen](./anforderungen/README.md) ·
[Entscheidungen](./entscheidungen/README.md) · [Backlog](./BACKLOG.md) ·
✅ Umgesetzt · [Technik](./TECHNICAL.md)

> Hieß bis 2026-07-25 `backlog/DONE.md`. Inhaltlich unverändert bis auf diesen
> Kopf und die aktualisierten Querverweise.

---

## Öffnungszeiten + „jetzt geöffnet" ✅

**Was:** Öffnungszeiten im Popup, dazu ein Badge „🟢 Jetzt geöffnet" / „🔴 Jetzt
geschlossen" und der optionale Filter „nur jetzt geöffnet".

**Umsetzung:**
- `scanner.py` liest das OSM-Tag `opening_hours` (DB-Spalte `opening_hours TEXT`
  inkl. Migration), `export.py` exportiert `openingHours`.
- `web/index.html` zeigt die Zeiten als Text (Wochentags-Kürzel eingedeutscht,
  eine Regel pro Zeile) und wertet sie in `openStateNow()` aus.

**Der Haken:** Das OSM-Format ist mächtig und komplex
(`Mo-Fr 11:00-14:30,17:00-23:00; Sa 17:00-23:00; PH off`). Gewählt wurde ein
**eigener Mini-Parser** statt einer Lib – leichtgewichtig, keine Abhängigkeit,
kein Request. Er deckt die häufigen Muster ab (Tagesbereiche/-listen, mehrere
Intervalle, Über-Mitternacht wie `Fr 20:00-04:00`, `off`/`closed`, `24/7`) und
ist **bewusst konservativ**: alles Unsichere ergibt „unbekannt" (kein Badge),
statt eine falsche Aussage zu riskieren. Nicht ausgewertet werden offene Zeiten
ohne Ende (`18:30+`), Feiertags-/Ferienregeln (`PH`/`SH` – clientseitig nicht
ermittelbar), Monats-/Wochenregeln, Freitext und `sunrise`/`sunset`.

Die Uhrzeit wird über `Intl` fest in **Europe/Berlin** gerechnet – unabhängig von
der Zeitzone des Nutzers, inklusive Sommer-/Winterzeit, komplett im Browser
(passt zum „kein Server, keine Datenerfassung"-Prinzip).

**Abdeckung:** 741 Restaurants haben Zeiten, davon sind ~90 % eindeutig
auswertbar; ~10 % bleiben „unbekannt". (Volle Abdeckung wäre
[Ausbau von bereits Umgesetztem](./BACKLOG.md#ausbau-von-bereits-umgesetztem).)

## Filter nach Küchenstil ✅

**Was:** Nach Küchenstil filtern und den Stil im Popup zeigen. Datenquelle ist
das OSM-Tag `cuisine`, das beim Scan kostenlos mitkommt.

**Umsetzung:**
- `scanner.py`: `_osm_cuisine()` normalisiert das Tag, DB-Spalte `cuisine TEXT`
  inkl. Migration.
- `export.py`: Feld `cuisines` in `restaurants.json` – immer eine **Liste**
  (`["pizza","italian"]`), leere Liste = nicht getaggt.
- `web/index.html`: Auswahlliste „🍽️ Alle Küchen" im Kopf, Küchenzeile im
  Popup, Küchenstil zusätzlich über das Suchfeld auffindbar.

**Der Haken – Normalisierung:** `cuisine` ist ein Freitext-Tag mit
Mehrfachwerten und wechselnder Schreibweise (`pizza;italian`, `Pizza; Kebab`,
`burger, american`, `Ice Cream`, `coffee-shop`). `_osm_cuisine()` macht daraus
eine kanonische, `;`-getrennte Liste kleingeschriebener Schlüssel mit `_` statt
Leerzeichen/Bindestrich, verwirft Dubletten und nichtssagende Werte (`yes`, `no`,
`unknown`, `fixme`, `other`). Die OSM-Reihenfolge bleibt erhalten (der erste Wert
ist meist der Hauptstil).

Die **deutschen Bezeichnungen** liegen bewusst im Frontend (`CUISINE_LABELS`),
nicht in der DB: die DB bleibt roh und verlustfrei, Übersetzungen sind
Anzeige-Sache. Für nicht übersetzte Werte greift ein Rückfall (`ice_cream` →
„Ice Cream"), damit auch seltene Stile filterbar bleiben.

Die Auswahlliste baut sich aus den tatsächlich vorhandenen Werten – häufigste
zuerst, mit Anzahl („Pizza (148)"). Ohne getaggte Küchenstile bleibt der Filter
komplett versteckt. Bei aktivem Filter fallen ungetaggte Restaurants heraus
(„unbekannt" ist kein Treffer – wie beim Lieferfilter).

**Bewusst nicht gemacht:** kein `CUISINE_CHANGED` im Änderungsprotokoll –
Umtaggen in OSM (`pizza` → `pizza;italian`) ist häufig und für den Feed ohne
Aussagekraft; der aktuelle Wert genügt. (Zur Abdeckung siehe
[A-8](./anforderungen/README.md#übersicht).)

## Änderungs-Feed „Diese Woche neu …" ✅

**Was:** Zeigen, was sich seit dem letzten Scan geändert hat – neue Restaurants,
verschwundene, geänderte Liefer-/Abhol-/Adressangaben.

**Umsetzung:** `export.py` (`build_feed()`) schreibt den Block `feed` nach
`web/restaurants.json`, `web/index.html` zeigt ihn über den Knopf „🆕 Diese
Woche" in einem Panel – gruppiert nach Änderungsart; ein Klick zentriert die
Karte auf das Restaurant und öffnet das Popup (auch wenn der Marker gerade
weggefiltert ist). Datenquelle ist die `changes`-Tabelle, die `scanner.py`
ohnehin füllt – reine Export- und Anzeigearbeit, kein neuer Request.
Feldbeschreibung: [`TECHNICAL.md`](./TECHNICAL.md).

**Die drei Haken:**

1. **Der Erstimport ist keine Neuigkeit.** Der allererste Scan protokolliert
   *jedes* Restaurant als `NEW` (hier: 883 Zeilen). Ungefiltert hätte der Feed
   „883 neu diese Woche" gemeldet. Er blendet daher alles aus, was am Zeitstempel
   des ersten `scan_runs`-Eintrags protokolliert wurde.
2. **Massen-Ereignisse.** Kommt ein Feld neu in die Pipeline, ändern sich auf
   einen Schlag hunderte Werte (bei `takeaway`: 245 × „unbekannt → ja"). Pro
   Änderungsart landen deshalb nur `FEED_MAX_PER_TYPE` Einträge in der JSON; die
   vollständige Zahl steht in `counts`, die Anzeige ergänzt „… und N weitere".
3. **Zeitfenster ab Scan, nicht ab „jetzt".** Sonst wäre der Feed leer, sobald
   der Export Tage nach dem Scan läuft. Anker ist der jüngste
   `scan_runs`-Zeitstempel.

**Bewusst nicht gemacht:** „neu" heißt *neu in OpenStreetMap erfasst*, nicht „neu
eröffnet" – das lässt sich aus OSM-Daten nicht unterscheiden. Ein Hinweis dazu
steht im Panel, statt eine Aussage zu treffen, die die Daten nicht tragen.

## PWA „zum Homescreen hinzufügen" ✅

**Was:** Die Karte lässt sich wie eine App auf den Homescreen legen, startet im
Vollbild und funktioniert auch ohne Netz (unterwegs im Funkloch ist eine
Lieferkarte sonst wenig wert).

**Umsetzung – drei statische Dateien**, kein Build-Schritt, keine Abhängigkeit:
- `web/manifest.webmanifest` – Name, Icons, `display: standalone`, Farben und
  zwei App-Verknüpfungen („Jetzt geöffnet" → `?open=1`, „In meiner Nähe" →
  `?nearby=1`). *(Die Verknüpfungen sind mit
  [A-1](./anforderungen/A-1-standardfilter-entschaerfen.md) neu belegt worden –
  siehe „Standardfilter „Liefert jetzt"" unten.)*
- `web/sw.js` – Service Worker mit Precache und pro Inhalt passender Strategie.
- `web/icons/*.png` – erzeugt von `tools/make_icons.py` (nur Standardbibliothek).

Dazu im Frontend der `📲 App installieren`-Button (`beforeinstallprompt`, auf iOS
stattdessen die Anleitung übers Teilen-Menü) und eine Hinweisleiste für „Offline
– gespeicherte Daten vom …" bzw. „Neue Version verfügbar". Geprüft wird das
Zusammenspiel von Manifest, Icons und Precache-Liste durch `tests/test_pwa.py`.

**Der Haken – wöchentlich neue Daten:** Ein naiver „cache first"-Worker hätte die
installierte App auf dem Datenstand des Installationstags eingefroren. Deshalb:

- `restaurants.json` läuft **network first** – der Cache greift nur ohne Netz und
  wird dann sichtbar als Offline-Stand ausgewiesen (Datum aus `lastScanAt`).
- Auch HTML/Manifest kommen network first, damit neue Versionen nicht hinter
  einem alten Cache hängen bleiben.
- Eine neue Worker-Version übernimmt **nicht** von selbst (kein `skipWaiting`
  beim Installieren): die Seite fragt erst („Jetzt neu laden").
- Bei jeder Rückkehr zur App wird nach Updates gesucht – eine installierte App
  wird oft wochenlang nicht neu geladen.

**Bewusste Einschränkungen:**
- **Kartenkacheln** werden nur *nachträglich* gecacht (max. 400, cache first) –
  besuchte Gegenden funktionieren offline, es wird aber nichts auf Vorrat
  geladen (Rücksicht auf die kostenlosen OSM-Tile-Server).
- **Leaflet kommt weiterhin vom CDN** (mit `integrity`-Hash), der Worker cacht es
  „best effort" mit. Vendoren wäre der nächste Schritt
  ([Ausbau von bereits Umgesetztem](./BACKLOG.md#ausbau-von-bereits-umgesetztem)).
- **Keine Push-Nachrichten, keine Background-Sync-Registrierung** – das würde
  dem „kein Tracking, keine Datenerfassung"-Versprechen widersprechen. Der
  Worker cacht ausschließlich, er sendet nichts.

---

## Standardfilter „Liefert jetzt" ✅

**Was:** Der Default „nur mit Lieferservice" ist ersetzt durch **„Liefert
jetzt"** — liefert **und** hat gerade geöffnet. Die zwei Checkboxen sind drei
Chips geworden (🚴 Lieferung · 🥡 Abholung · 🕒 Jetzt geöffnet), „unbekannt" ist
ein sichtbarer dritter Zustand, und der Filterzustand steht in der URL.

Anforderung: [A-1](./anforderungen/A-1-standardfilter-entschaerfen.md) (mit der
Abdeckungstabelle und den verworfenen Optionen) und
[A-8](./anforderungen/README.md#übersicht). Grundsatz:
[ADR-007](./entscheidungen/ADR-007-standardfilter-liefert-jetzt.md).

**Umsetzung:**
- `web/index.html` — `FILTER_DEFAULTS` (`delivery` und `open` an, `takeaway`
  aus), Chips mit `aria-pressed` statt Checkboxen, `takeaway` als eigener
  Filter, Zurücksetzen-Chip, Leerzustand `#empty`,
  `readUrlState()`/`writeUrlState()` über `history.replaceState`.
- Popup: `delivery`/`takeaway` werden als **drei** Zustände gezeigt — ja / nein /
  „unbekannt" (blasses `badge-unknown`). Der Meldetext für die OSM-Notiz nennt
  jetzt auch „ist gar nicht getaggt", damit sich fehlende Tags melden lassen.
- `web/manifest.webmanifest` — „Jetzt geöffnet" (`?open=1`) entsprach dem neuen
  Default und ist ersetzt durch „Alle Restaurants" (`?delivery=0&open=0`) und
  „Abholung jetzt" (`?delivery=0&takeaway=1`); `CACHE_VERSION` → `v2`.
- Mitgenommen: **R7** (150 ms Debounce auf die Suche, `bindPopup(() => …)` statt
  vorab gebautem Popup-HTML) und der `aria-live`/Leerzustand-Teil von **R5**.

**Der Haken:** Der neue Default ist **enger** als der alte, nicht weiter — statt
63 zeigt er tageszeitabhängig etwa 25–40 von 883, nachts null. Das ist die
bewusste Antwort auf die Frage, ob diese Karte ein Verzeichnis oder ein
Jetzt-Werkzeug ist: wer sie öffnet, will bestellen, und ein geschlossenes
Restaurant ist kein Treffer, sondern ein Fehlklick. Der Gegenvorschlag „alles
zeigen, nur Badges" war die Empfehlung der Analyse und wurde mit Zahlen
vorgelegt und verworfen.

Der Preis dafür wird nicht versteckt, sondern bedient: der Zurücksetzen-Chip ist
sichtbar, sobald irgendein Filter greift, und bei null Treffern erscheint kein
stummes Loch, sondern der Satz, dass „gerade liefert niemand" eine Aussage über
die **Datenlage** ist — bei 87 % der Läden steht in OpenStreetMap gar nicht, ob
sie liefern — plus ein Knopf „Alle Restaurants zeigen". Ein *automatischer*
Rückfall auf „alle" wurde abgelehnt: er hätte den Filterzustand hinter dem
Rücken der Nutzerin geändert.

„Liefert jetzt" ist deshalb **kein eigener Filter**, sondern die Vorbelegung von
zwei getrennten Chips. Ein einziger kombinierter Chip hätte „liefert, egal wann"
unmöglich gemacht.

**Zahlen (echte `web/restaurants.json`, Playwright mit `L`-Stub):** Default 35,
nur Lieferung 63, nur Abholung 237, ohne Filter 883 von 883 in 197 ms.

---

## Farbsystem entflechten ✅

**Was:** Farbe hat jetzt **drei getrennte Rollen** — Marke, Interaktion,
Datenzustand — mit je eigenem Token-Satz. `--accent`, das fünf Bedeutungen
gleichzeitig trug, und `--ok`, das zwei trug, existieren nicht mehr. „Nicht
geöffnet / liefert nicht" ist **Slate statt Rot**, „unbekannt" ein gestrichelter
Umriss ohne Füllung, und kein Farbwert steht mehr außerhalb von `:root`.

Anforderung: [A-4](./anforderungen/A-4-farbsystem.md) (mit der vollständigen
Zuordnungstabelle aller 15 Stellen). Grundsatz:
[ADR-009](./entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md). Löst
**R12** aus dem UI/UX-Review vom Juli 2026.

**Umsetzung:**
- `web/index.html` — neuer `:root`-Block mit `--marke` / `--aktion*` /
  `--zustand-*` plus neutralen Tokens (`--flaeche-hover`, `--auf-farbe`,
  `--schatten-weich`/`-stark`) und den beiden Amber-Rollen `--status*` und
  `--hinweis*`. Die 15 `var(--accent)`-Stellen sind nach Rolle umgehängt, die 16
  rohen Hex-Werte und die zwei `rgba()`-Schatten sind Tokens.
- Badge-Klassen laufen auf der **Zustandsachse**: `.badge-yes` / `.badge-no` /
  `.badge-unknown` ersetzen die sechs alten (`badge-delivery`, `-nodelivery`,
  `-takeaway`, `-open`, `-closed`). `.badge-status` bleibt eine eigene Rolle.
- `cssVar(name, fallback)` liest ein Token in JavaScript; der Standort-Marker in
  `locateMe()` nutzt es statt eines Farbliterals. Der Fallback ist nötig, weil
  `getComputedStyle` ohne aufgelöste Custom-Properties einen Leerstring liefert.
- `header h1` von 1,15 auf **1,2 rem** — auch in `web/datenschutz.html`.
- Mitgezogen: `web/datenschutz.html` (eigener `:root`), das Wurzel-`index.html`,
  ein Kopplungs-Kommentar an `ACCENT` in `tools/make_icons.py`,
  `CACHE_VERSION` → `v3`.

**Der Haken:** „Geschlossen" verliert die gewohnte Signalfarbe Rot. Das ist der
Preis für zwei Dinge, die schwerer wiegen. Erstens war *keine* Farbe für „Zustand"
frei: solange Markenfarbe und „geschlossen" derselbe Wert `#d64541` waren, hätte
ein roter Pin gleichzeitig „geschlossen" und „das ist unsere Farbe" bedeutet —
und genau das blockierte [A-5](./anforderungen/A-5-pins-nach-zustand.md).
Zweitens, und wichtiger: Rot `#d64541` und Grün `#2e8b4f` haben zueinander einen
Helligkeitskontrast von **1,03**, sind also praktisch gleich hell. Bei
Rot-Grün-Blindheit (rund 8 % der Männer) war die Unterscheidung damit nicht schwer,
sondern unmöglich — es blieb keine Rückfallebene. Slate `#33333b` bringt den
Abstand auf 1,92.

Die Marke behält das Rot, weil der Zustand es billiger abgeben kann: `#d64541`
steckt in den PWA-Icons, im Manifest, in drei Metas und in `make_icons.py`. Die
Verwechslung löst sich genauso auf, wenn der *Zustand* wechselt — nur ohne
Icon-Neugenerierung. Ein dunkleres Rot für den Zustand wurde geprüft und
verworfen: 1,07 zu Grün und 1,59 zur Marke hätten R12 halb gelöst und das
Rot-Grün-Problem gar nicht.

1,92 ist besser, aber nicht genug, deshalb die bindende Regel: **Farbe allein
trägt einen Zustand nie.** Jeder Zustand führt Symbol, Form oder Text mit
(✔ / 🥡 / 🟢 / 🔴). Und weil „nein" jetzt ebenfalls im Graubereich liegt, trennt
sich „unbekannt" davon über die **Form** statt über den Farbton — gefüllt gegen
gestrichelten Umriss. Das war kein Detail, sondern Pflicht: „unbekannt" ist mit
87,5 % bei Lieferung der häufigste Zustand, und
[ADR-007](./entscheidungen/ADR-007-standardfilter-liefert-jetzt.md) verbietet, ihn
wie eine Absage aussehen zu lassen. Der gestrichelte Rahmen nutzt
`--zustand-unbekannt` (5,33:1) statt `--border` (1,15:1) — ein unsichtbarer
Rahmen hätte die Formtrennung als Mechanismus wertlos gemacht.

Sichtbare Nebenwirkung, gewollt: Badges und Links sind **merklich dunkler**, weil
alle acht Kontrastverstöße im selben Schritt behoben wurden statt in einem
zweiten Durchgang, den A-5 sonst mit den falschen Werten geerbt hätte. Und wer
liefert *und* abholen lässt (47 Restaurants), hat jetzt **zwei grüne Badges**
nebeneinander — Farbe codiert den Zustand, Symbol und Text die Fähigkeit.

**Kontrast vorher / nachher** (WCAG 2.1, Badges sind 0,72 rem ≈ 11,5 px → kleiner
Text, Schwelle 4,5:1):

| Paar | Vorher | Nachher |
|---|---|---|
| Badge „ja" (Lieferung / Abholung / geöffnet) | 3,76 ❌ | **5,75** ✔ |
| Badge „nein" | 3,62 ❌ | **9,16** ✔ |
| Badge „unbekannt" | 4,63 ✔ | **5,33** ✔ |
| Aktiver Filter-Chip | 4,39 ❌ | **5,85** ✔ |
| Aktiver Chip, Hover | 5,28 ✔ | **7,53** ✔ |
| `.popup-link` / `.meld summary` / `#install` | 4,39 ❌ | **5,85** ✔ |
| `#empty button` | 4,39 ❌ | **5,85** ✔ |
| „geschlossen" in der Zeitentabelle | 4,39 ❌ | **12,52** ✔ |
| `header h1 .accent` | 4,39 ❌ (Schwelle 4,5) | 4,39 ✔ (Schwelle 3,0 bei 1,2 rem fett) |

Und der Punkt, um den es in R12 eigentlich ging — die Unterscheidbarkeit
untereinander:

| Unterscheidbarkeit | Vorher | Nachher |
|---|---|---|
| „ja" gegen „nein" | 1,03 | **1,92** + Symbol |
| „nein" gegen „unbekannt" | 1,21 | **2,35** + Formunterschied |
| Marke gegen Datenzustand | Marke *war* der Datenzustand | **2,85** |

**Geprüft:** 59 Unittests grün · 82 Browser-Prüfungen (Playwright mit `L`-Stub)
gegen synthetische Daten **und** die echte `restaurants.json` — alle neun
Kombinationen `delivery` × `takeaway`, jedes der 773 `delivery === null` rendert
`badge-unknown` und keines `badge-no`, jede Rolle über `getComputedStyle`
nachgewiesen (kein `var()` fällt auf `initial` zurück) · Kontrastwerte
nachgerechnet, nicht geschätzt · PWA-Update `v2` → `v3` durchgespielt: der neue
Worker wartet, die Seite fragt, erst der Klick schaltet um, danach sind die
`v2`-Caches aufgeräumt.
