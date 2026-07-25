# Ideen & Backlog

Was aus der Karte noch werden soll – und was schon geworden ist. Kein Zeitplan:
die Reihenfolge sagt, was als Nächstes sinnvoll wäre.

| Stufe | Bedeutung |
|---|---|
| 💡 **Ideen** | Richtung steht, Umsetzung nicht – braucht erst eine Entscheidung oder einen Entwurf. |
| 🔨 **Ready for Dev** | Problem, betroffene Datei und Lösung sind benannt – kann direkt gebaut werden. |
| ✅ **Umgesetzt** | Fertig und live; bleibt als Kurzprotokoll der Design-Entscheidungen stehen. |

**Inhalt:** [💡 Ideen](#-ideen) · [🔨 Ready for Dev](#-ready-for-dev) ·
[✅ Umgesetzt](#-umgesetzt)

Die Kürzel R…/P… stammen aus dem UI/UX-Review vom Juli 2026 (Mobil-Screenshot,
Android/Chrome, 1080 × 2340, im Abgleich mit `web/index.html`). Sie bleiben
erhalten, damit Rückfragen zuordenbar sind.

---

# 💡 Ideen

Noch nicht baubar: hier fehlt jeweils eine Produktentscheidung oder ein Entwurf.

### 1. Standardfilter entschärfen (Entscheidung offen)

Die Karte filtert per Default „nur mit Lieferservice" (`delivery=yes/only`) und
zeigt damit **63 von 883** Restaurants (7 %). Die 773 ungetaggten sind
„unbekannt", nicht „liefert nicht" – die Karte wirkt fälschlich leer. Abholung
ist mit 26 % deutlich besser abgedeckt, wird aber nur als Popup-Badge gezeigt.

Vier Optionen (A: so lassen, B: eigener „nur Abholung"-Filter, C: Default auf
„alle" und Liefer-/Abholstatus nur als Badge, D: Tags selbst in OSM ergänzen)
stehen samt Abdeckungstabelle in
[`VOR-VEROEFFENTLICHUNG.md`](VOR-VEROEFFENTLICHUNG.md), Abschnitt „Filter für
Abdeckung anpassen". **Blockiert Idee 5** – und macht R7 dringlicher, weil dann
883 statt 63 Marker gezeichnet werden.

### 2. Ergebnisliste neben der Karte (R6)

Die Karte ist für Tastatur und Screenreader leer: die `L.marker(…)` tragen kein
`alt`/`title`, die Popup-Inhalte existieren nur im Marker. Vorschlag: dieselben
gefilterten Daten zusätzlich als schlichte `<ul>` unter bzw. neben der Karte.
Löst gleichzeitig „was ist in der Nähe?" und macht „In meiner Nähe" nach
Entfernung sortierbar. Offen ist die Struktur – wo die Liste sitzt und ob sie
auf Mobil einklappbar ist.

### 3. Header-Umbau: eine Zeile + Bottom Sheet (R9)

Der Header frisst 23 % des Bildschirms: Suche, zwei Checkboxen, zwei Buttons und
die Trefferzahl konkurrieren gleichwertig über drei Zeilen, die Zahl landet per
`margin-left: auto` als Waise neben „Diese Woche". Auf Mobil besser: eine Zeile
(Suche + „Filter"-Knopf mit Trefferzahl), der Rest in ein Bottom Sheet. Nebenbei
sind die Buttons ~34 px hoch – unter den empfohlenen 44 px Touch-Target.

Gehört zusammen mit dem **Feed-Panel**, das auf Mobil fast die ganze Karte
verdeckt: als Bottom Sheet mit Griff angenehmer als das schwebende Panel. Beides
ist derselbe Umbau und sollte in einem Rutsch entworfen werden.

### 4. Farbsystem entflechten (R12)

`--accent` bedeutet vier Dinge gleichzeitig: Markenfarbe (H1), Primärlink,
„Jetzt geschlossen" bzw. „geschlossen" in der Zeitentabelle *und* Melde-Flag.
Zustandsfarben gehören von der Markenfarbe getrennt – braucht aber erst einen
eigenen Satz Tokens neben `--accent`.

### 5. Pins nach Zustand unterscheiden (R13)

Ob ein Restaurant liefert, abholen lässt oder gerade geschlossen ist, sieht man
erst nach dem Antippen. Farb- oder Formcodierung (z. B. blass = jetzt
geschlossen) bringt viel pro Blick. Hängt an **Idee 1**: erst mit entschärftem
Standardfilter lohnt die Unterscheidung wirklich, und erst dann steht fest,
welche Zustände überhaupt nebeneinander vorkommen.

### 6. Marker-Clustering oder Canvas-Renderer

Der zweite Teil von R7 (der erste ist ready, siehe unten). Mit entschärftem
Standardfilter zeichnet die Karte 883 statt 63 Marker. Ob Clustering
(`markercluster`, wäre eine zusätzliche Abhängigkeit) oder ein Canvas-Renderer
(`L.canvas()`, ohne neue Lib) besser passt, ist offen – und sinnvoll erst zu
entscheiden, wenn Idee 1 entschieden ist.

### 7. Telefonnummer in die Pipeline

Die OSM-Tags `phone`/`contact:phone` kommen beim Scan kostenlos mit; eine
Nummer im Popup wäre für „schnell bestellen" mindestens so nützlich wie die
Website. Die Spalte existiert in `restaurants` noch nicht. Vor dem Bau: Abdeckung
zählen und entscheiden, ob Änderungen protokolliert werden sollen (Vorsicht,
siehe „Massen-Ereignisse" beim Änderungs-Feed).

### 8. Küchenstil: Abdeckung prüfen

Die `cuisine`-Pipeline ist fertig, aber in `data/restaurants.db` sind nach vier
Scans (letzter: 2026-07-21) **0 von 883** aktiven Restaurants getaggt – während
`opening_hours` bei 741 gefüllt ist. Für Karlsruhe sind null Küchenstil-Tags
unplausibel; das deutet eher auf ein Pipeline-Problem als auf fehlende
OSM-Daten. Der Filter bleibt so lange versteckt (das ist gewollt), aber der
Befund gehört nachgesehen:

```bash
python3 -c "import sqlite3; c=sqlite3.connect('data/restaurants.db'); \
print(c.execute('SELECT cuisine, COUNT(*) FROM restaurants WHERE active=1 \
GROUP BY cuisine ORDER BY 2 DESC LIMIT 20').fetchall())"
```

### 9. Ausbau von bereits Umgesetztem

Drei bewusst zurückgestellte Erweiterungen – jeweils erst nötig, wenn der
aktuelle Kompromiss nicht mehr reicht:

- **`opening_hours.js` vendoren** (lokal, kein CDN) für die volle
  `opening_hours`-Abdeckung. Aktuell nicht nötig: ~90 % der getaggten Fälle
  wertet der eigene Mini-Parser schon eindeutig aus.
- **Leaflet lokal ins Repo legen** – macht die Offline-Fähigkeit unabhängig vom
  CDN. Bisher genügt der „best effort"-Precache.
- **Küchenstil-Synonyme gruppieren** (`sushi` unter `japanese`, `doner` unter
  `kebab`). Wäre Interpretation der OSM-Daten; erst sinnvoll, wenn die
  Auswahlliste zu lang wirkt.

---

# 🔨 Ready for Dev

Spezifiziert und direkt baubar. Es geht ausschließlich um das Frontend –
Pipeline und Datenmodell bleiben unberührt.

## Hoch – die Pflicht-Attribution ist auf dem Handy unsichtbar

Diese drei Punkte gehören zusammen: sie betreffen alle die ODbL-pflichtige
Angabe „© OpenStreetMap-Mitwirkende" im Footer. Deshalb Vorrang vor allem
anderen.

- [ ] **R2 – `100dvh` statt `100vh`.** `body { height: 100vh }`
  (`web/index.html:49`) meint auf Android Chrome die *große* Viewport-Höhe (ohne
  URL-Leiste). Der `<footer>` mit Attribution und Datenschutz-Link liegt dadurch
  unter der Browserleiste, ebenso Leaflets eigenes Attribution-Control unten
  rechts. Fix: `height: 100dvh` mit `100vh` als Fallback davor.
- [ ] **R3 – `viewport-fit=cover` im Viewport-Meta.** Die
  `env(safe-area-inset-*)`-Regeln für `display-mode: standalone` wirken ohne
  `viewport-fit=cover` nicht; als installierte iOS-App klebt der Header unter
  der Statusleiste.
- [ ] **P3 – Fußzeile zu klein.** `0.72rem` (≈ 11,5 px) ist für eine
  Pflichtangabe zu wenig – mindestens `0.8rem`.

## Mittel – Bedienbarkeit, Struktur, Performance

- [ ] **R4 – Suchfeld ohne Label, Text abgeschnitten.** Das
  `<input type="search">` hat nur ein `placeholder` (kein `<label>`/`aria-label`)
  – assistiv also namenlos. Sichtbar ist außerdem nur „Restaurant oder Adresse
  sucl", weil `flex: 1 1 200px` (`web/index.html:71`) neben der Checkbox
  zerdrückt wird. Unter 640 px sollte die Suche eine eigene, volle Zeile bekommen.
- [ ] **R5 – Trefferzahl wird nicht angekündigt, 0 Treffer sind ein Loch.**
  `#count` braucht `aria-live="polite"`; `render()` braucht einen Empty State
  („Keine Treffer – Filter zurücksetzen") statt einer stumm leeren Karte.
- [ ] **R14 – `alert()` für Geolocation-Fehler ersetzen.** `locateMe()` nutzt
  zwei `alert()` (`web/index.html:899` und `:912`); der Banner-Mechanismus
  (`showBanner`) existiert bereits.
- [ ] **R8 – Der Pitch verschwindet nach dem Laden.** `$meta` wird von
  „Restaurants mit eigenem Lieferservice – direkt bestellen, ohne
  Provisions-Plattformen" auf „883 Restaurants · zuletzt aktualisiert am …"
  überschrieben; die Anzahl steht damit doppelt (Sub-Zeile + `#count`). Claim
  stehen lassen, Datum in die Fußzeile oder hinter ein „ⓘ".
- [ ] **R11 – Popup hat zwei rote Primäraktionen.** „Zur Website & bestellen →"
  und „⚑ Falsche Angabe melden" sind beide `var(--accent)`, fett, gleich groß und
  stehen direkt untereinander. Die Bestellaktion als gefüllter Button, den
  Melde-Link klein und `--muted` unter die Fakten.
- [ ] **R7 – Suche drosseln, Popups faul bauen.** `render()` läuft ungedrosselt
  bei jedem `input` und baut für **jeden** Marker vorab das komplette Popup-HTML
  inklusive `openStateNow()`-Parsing (`web/index.html:891`). Fix: ~150 ms
  Debounce und `bindPopup(() => popupHtml(r))` – Leaflet akzeptiert eine
  Funktion. (Clustering/Canvas ist Idee 6.)

## Niedrig – Feinschliff

- [ ] **P3 – Emoji-Icons dekorativ auszeichnen.** 🍽️ 📍 🆕 📲 🥡 ⚑ werden
  mitgelesen und rendern plattformabhängig unterschiedlich – mindestens
  `aria-hidden="true"` auf die rein dekorativen.
- [ ] **P3 – Kopier-Feedback im Fehlerfall.** Schlägt
  `navigator.clipboard.writeText()` fehl, ändert sich am Melde-Link nichts, der
  OSM-Tab öffnet aber trotzdem – dann „Text bitte von Hand markieren" zeigen.
- [ ] **P3 – Fokus-Verwaltung im Feed-Panel.** Beim Öffnen wandert der Fokus
  nicht in das Panel (Escape schließt immerhin schon).
- [ ] **P3 – Dark Mode fehlt.** Über die CSS-Variablen (`:root`) wäre
  `prefers-color-scheme: dark` ein kleiner Eingriff; abends ist die Seite grell.
- [ ] **„Heute" in der Öffnungszeiten-Tabelle hervorheben.** Bei „Di–Fr / Sa, So
  / Mo" muss man selbst suchen, was gerade gilt – `berlinNow()` kennt den
  Wochentag schon.
- [ ] **„Jetzt geschlossen – öffnet wieder um 16:30".** Die Intervalle sind in
  `parseIntervals()` bereits geparst; die Zusatzinfo entscheidet, ob jemand bleibt.
- [ ] **Filterzustand teilbar und wiederherstellbar machen.** Bisher gibt es nur
  `?open=1` / `?nearby=1`; `?delivery=0&cuisine=thai` passt ins bestehende Muster
  und verletzt das „keine Cookies"-Versprechen nicht (reine URL-Parameter, keine
  Speicherung).

---

# ✅ Umgesetzt

Fertig und live. Die Abschnitte bleiben als Kurzprotokoll stehen – interessant
ist jeweils **der Haken**: warum es so gelöst ist und nicht anders.

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
auswertbar; ~10 % bleiben „unbekannt".

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
Aussagekraft; der aktuelle Wert genügt. (Zur Abdeckung siehe Idee 8.)

## Änderungs-Feed „Diese Woche neu …" ✅

**Was:** Zeigen, was sich seit dem letzten Scan geändert hat – neue Restaurants,
verschwundene, geänderte Liefer-/Abhol-/Adressangaben.

**Umsetzung:** `export.py` (`build_feed()`) schreibt den Block `feed` nach
`web/restaurants.json`, `web/index.html` zeigt ihn über den Knopf „🆕 Diese
Woche" in einem Panel – gruppiert nach Änderungsart; ein Klick zentriert die
Karte auf das Restaurant und öffnet das Popup (auch wenn der Marker gerade
weggefiltert ist). Datenquelle ist die `changes`-Tabelle, die `scanner.py`
ohnehin füllt – reine Export- und Anzeigearbeit, kein neuer Request.
Feldbeschreibung: `TECHNICAL.md`.

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
  `?nearby=1`).
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
  „best effort" mit. Vendoren wäre der nächste Schritt (Idee 9).
- **Keine Push-Nachrichten, keine Background-Sync-Registrierung** – das würde
  dem „kein Tracking, keine Datenerfassung"-Versprechen widersprechen. Der
  Worker cacht ausschließlich, er sendet nichts.
