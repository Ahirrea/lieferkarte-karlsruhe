# Ideen & Feature-Backlog

Geplante, noch **nicht umgesetzte** Features. Kein Zeitplan – hier wird
festgehalten, was als Nächstes sinnvoll wäre.

---

## Öffnungszeiten anzeigen (+ Bonus: „jetzt geöffnet")

**Ziel:** Zu jedem Restaurant die Öffnungszeiten im Popup anzeigen. ✅ **umgesetzt**
**Bonus:** sichtbar machen (und ggf. filtern), was **gerade jetzt** geöffnet hat.
✅ **umgesetzt** (siehe „der Haken" unten – bewusst konservativ gelöst).

> **Stand:** Das *Anzeigen* der Öffnungszeiten ist umgesetzt: `scanner.py` liest
> das OSM-Tag `opening_hours` (DB-Spalte `opening_hours TEXT` + Migration),
> `export.py` exportiert `openingHours`, und das Popup zeigt die Zeiten als Text
> (Wochentags-Kürzel eingedeutscht, eine Regel pro Zeile).
>
> **„jetzt geöffnet" ist jetzt auch umgesetzt** – rein clientseitig in
> `web/index.html` (`openStateNow()`), ohne externe Lib und ohne Request. Es
> gibt ein Badge im Popup („🟢 Jetzt geöffnet" / „🔴 Jetzt geschlossen") und
> den optionalen Filter „nur jetzt geöffnet". Die Uhrzeit wird über `Intl` in
> **Europe/Berlin** berechnet (unabhängig von der Zeitzone des Nutzers, inkl.
> Sommer-/Winterzeit). Abdeckung der 741 Restaurants mit Zeiten: ~90 % sind
> eindeutig auswertbar, ~10 % bleiben „unbekannt" (kein Badge).

**Datenquelle:** OSM-Tag `opening_hours` – kommt beim Overpass-Scan kostenlos
mit (der Query holt bereits alle Tags). Die Abdeckung in Karlsruhe ist noch
nicht gemessen; wie bei `delivery`/`takeaway` vermutlich lückenhaft. Vor dem Bau
einmal zählen, sobald das Feld erfasst wird.

**Umsetzung – Pipeline (klein):**
- `scanner.py`: in `normalize_osm()` `opening_hours` aus `tags` lesen; DB-Spalte
  `opening_hours TEXT` ergänzen (+ Migration `ALTER TABLE ADD COLUMN`, wie bei
  `takeaway`).
- `export.py`: Feld `openingHours` in `restaurants.json`.
- `web/index.html`: Öffnungszeiten im Popup ausgeben (als Text).

**Bonus „jetzt geöffnet" – der Haken (so gelöst):** Das OSM-`opening_hours`-
Format ist mächtig und komplex, z. B.
`Mo-Fr 11:00-14:30,17:00-23:00; Sa 17:00-23:00; PH off`.
Gewählt wurde der **eigene Mini-Parser** (Option 1) statt der Lib – leicht­
gewichtig, keine Abhängigkeit. Er deckt die häufigen Muster ab
(Tagesbereiche/-listen, mehrere Zeitintervalle, Über-Mitternacht wie
`Fr 20:00-04:00`, `off`/`closed`, `24/7`) und ist **bewusst konservativ**:
alles Unsichere ergibt „unbekannt" (kein Badge), statt eine falsche Aussage zu
riskieren. Konkret nicht ausgewertet:

- **Offene Zeiten** ohne Ende (`18:30+`) – Schließzeit unbekannt → „unbekannt".
- **Feiertage/Ferien** (`PH`/`SH`) – ob heute Feiertag ist, lässt sich
  clientseitig nicht ermitteln → solche Regeln werden ignoriert.
- **Monats-/Wochenregeln** (`May-Sep …`), Freitext (`"by appointment"`),
  `sunrise`/`sunset` → „unbekannt".
- **Zeitzone/Sommerzeit**: über `Intl` fest in **Europe/Berlin** gerechnet,
  unabhängig von der Zeitzone des Nutzers. Läuft komplett im Browser (passt zum
  „kein Server, keine Datenerfassung"-Prinzip).

Falls später die volle Abdeckung gewünscht ist, bliebe als Ausbau die
**vendored `opening_hours.js`** (lokal eingebunden, kein CDN) – aktuell aber
nicht nötig, da ~90 % der getaggten Fälle schon eindeutig auswertbar sind.

**Aufwand:** war wie erwartet – *anzeigen* klein, „*jetzt geöffnet*" mittel
(Parsing). Beide Schritte sind jetzt erledigt.

---

## Filter nach Küchenstil (Pizza, Thai, Burger, …) ✅ **umgesetzt**

**Ziel:** Die Karte nach Küchenstil filtern können und den Stil im Popup zeigen.

**Datenquelle:** OSM-Tag `cuisine` – kommt beim Overpass-Scan kostenlos mit
(der Query holt bereits alle Tags).

**Umsetzung – Pipeline:**
- `scanner.py`: `_osm_cuisine()` normalisiert das Tag, `normalize_osm()` liest es;
  DB-Spalte `cuisine TEXT` inkl. Migration (`ALTER TABLE ADD COLUMN`, wie bei
  `takeaway`/`opening_hours`).
- `export.py`: Feld `cuisines` in `restaurants.json` – immer eine **Liste**
  (`["pizza","italian"]`), leere Liste = nicht getaggt.
- `web/index.html`: Auswahlliste „🍽️ Alle Küchen" im Kopf, Küchenzeile im Popup,
  Küchenstil zusätzlich im Suchfeld auffindbar („thai", „Italienisch").

**Normalisierung (der Haken):** `cuisine` ist ein Freitext-Tag mit Mehrfachwerten
und wechselnder Schreibweise: `pizza;italian`, `Pizza; Kebab`, `burger, american`,
`Ice Cream`, `coffee-shop`. `_osm_cuisine()` macht daraus eine kanonische,
`;`-getrennte Liste aus kleingeschriebenen Schlüsseln mit `_` statt
Leerzeichen/Bindestrich, verwirft Dubletten und nichtssagende Werte
(`yes`, `no`, `unknown`, `fixme`, `other`). Die Reihenfolge aus OSM bleibt
erhalten (der erste Wert ist meist der Hauptstil).

**Deutsche Bezeichnungen** liegen bewusst im Frontend (`CUISINE_LABELS`), nicht in
der DB: die DB bleibt roh und verlustfrei, Übersetzungen sind Anzeige-Sache. Für
nicht übersetzte Werte greift ein Rückfall (`ice_cream` → „Ice Cream"), damit auch
seltene Stile filterbar bleiben statt zu verschwinden.

**Auswahlliste** baut sich aus den tatsächlich vorhandenen Werten – häufigste
zuerst, mit Anzahl („Pizza (148)"). Ohne getaggte Küchenstile bleibt der Filter
komplett versteckt; die Karte sieht damit unverändert aus, bis der nächste Scan
die Werte einträgt. Bei aktivem Filter fallen ungetaggte Restaurants heraus
(„unbekannt" ist kein Treffer – wie beim Lieferfilter).

**Bewusst nicht gemacht:**
- **Kein `CUISINE_CHANGED` im Änderungsprotokoll.** Umtaggen in OSM
  (`pizza` → `pizza;italian`) ist häufig und für den Änderungs-Feed
  ohne Aussagekraft – der aktuelle Wert genügt.
- **Keine Synonym-Gruppierung** (`sushi` unter `japanese`, `doner` unter `kebab`).
  Das wäre Interpretation der OSM-Daten; die Liste zeigt, was getaggt ist. Falls
  die Auswahl später zu lang wirkt, ist Gruppieren der nächste Schritt.

**Abdeckung:** noch nicht gemessen – die Spalte ist erst nach dem nächsten
Voll-Scan gefüllt. Zum Nachzählen dann:
`SELECT cuisine, COUNT(*) FROM restaurants WHERE active=1 GROUP BY cuisine ORDER BY 2 DESC;`
---

## Änderungs-Feed („Diese Woche neu …") ✅ **umgesetzt**

**Ziel:** Zeigen, was sich seit dem letzten Scan geändert hat – neue
Restaurants, verschwundene, geänderte Liefer-/Abhol-/Adressangaben.

> **Stand:** umgesetzt. `export.py` (`build_feed()`) schreibt den Block `feed`
> nach `web/restaurants.json`, `web/index.html` zeigt ihn über den Knopf
> „🆕 Diese Woche" in einem Panel – gruppiert nach Änderungsart, ein Klick
> zentriert die Karte auf das Restaurant und öffnet das Popup (auch wenn der
> Marker gerade weggefiltert ist). Feldbeschreibung: `TECHNICAL.md`.

**Datenquelle:** die `changes`-Tabelle, die `scanner.py` ohnehin bei jedem Scan
füllt – es war also reine Export- + Anzeigearbeit, kein neuer Request.

**Die drei Haken (so gelöst):**

1. **Der Erstimport ist keine Neuigkeit.** Der allererste Scan protokolliert
   *jedes* gefundene Restaurant als `NEW` (hier: 883 Zeilen). Ungefiltert hätte
   der Feed „883 neu diese Woche" gemeldet. Der Feed blendet daher alles aus,
   was am Zeitstempel des ersten `scan_runs`-Eintrags protokolliert wurde.
2. **Massen-Ereignisse.** Kommt ein Feld neu in die Pipeline, ändern sich auf
   einen Schlag hunderte Werte (bei `takeaway`: 245 × „unbekannt → ja"). Pro
   Änderungsart landen deshalb nur `FEED_MAX_PER_TYPE` Einträge in der JSON;
   die vollständige Zahl steht in `counts`, die Anzeige ergänzt „… und N
   weitere".
3. **Zeitfenster ab Scan, nicht ab „jetzt".** Sonst wäre der Feed leer, sobald
   der Export einmal Tage nach dem Scan läuft (oder die Seite länger nicht neu
   gebaut wurde). Anker ist der jüngste `scan_runs`-Zeitstempel.

**Bewusst nicht gemacht:** „neu" heißt *neu in OpenStreetMap erfasst*, nicht
„neu eröffnet" – das lässt sich aus OSM-Daten nicht unterscheiden. Ein Hinweis
dazu steht im Panel, statt eine Aussage zu treffen, die die Daten nicht tragen.

---

## PWA („zum Homescreen hinzufügen") ✅ **umgesetzt**

**Ziel:** Die Karte lässt sich wie eine App auf den Homescreen legen, startet im
Vollbild und funktioniert auch ohne Netz (unterwegs im Funkloch ist eine
Lieferkarte sonst wenig wert).

**Umgesetzt mit drei statischen Dateien** – kein Build-Schritt, keine
Abhängigkeit, passend zum Rest des Projekts:

- `web/manifest.webmanifest` – Name, Icons, `display: standalone`, Farben und
  zwei App-Verknüpfungen („Jetzt geöffnet" → `?open=1`, „In meiner Nähe" →
  `?nearby=1`; die Parameter wertet `web/index.html` beim Start aus).
- `web/sw.js` – Service Worker mit Precache (Karte, Icons, Datenschutzseite,
  `restaurants.json`) und pro Inhalt passender Strategie.
- `web/icons/*.png` – erzeugt von `tools/make_icons.py` (nur Standardbibliothek,
  zeichnet Teller + Besteck in der Projektfarbe; kein Pillow nötig).

Dazu im Frontend: `📲 App installieren`-Button (nutzt `beforeinstallprompt`, auf
iOS stattdessen die Anleitung übers Teilen-Menü) und eine Hinweisleiste für
„Offline – gespeicherte Daten vom …" bzw. „Neue Version verfügbar".

**Der Haken – wöchentlich neue Daten (so gelöst):** Ein naiver „cache first"-
Worker hätte die installierte App auf dem Datenstand des Installationstags
eingefroren. Deshalb:

- `restaurants.json` läuft **network first** – der Cache greift nur ohne Netz und
  wird dann sichtbar als Offline-Stand ausgewiesen (Datum aus `lastScanAt`).
- Auch HTML/Manifest kommen network first, damit neue Versionen der Seite nicht
  hinter einem alten Cache hängen bleiben.
- Eine neue Worker-Version übernimmt **nicht** von selbst (kein `skipWaiting`
  beim Installieren): Die Seite fragt erst („Jetzt neu laden"), damit nicht
  mitten im Betrieb die halbe App getauscht wird.
- Bei jeder Rückkehr zur App wird nach Updates gesucht – eine installierte App
  wird oft wochenlang nicht neu geladen.

**Bewusste Einschränkungen:**

- **Kartenkacheln** werden nur *nachträglich* gecacht (max. 400, cache first) –
  bereits besuchte Gegenden funktionieren offline, es wird aber nichts auf Vorrat
  heruntergeladen (Rücksicht auf die kostenlosen OSM-Tile-Server).
- **Leaflet kommt weiterhin vom CDN** (mit `integrity`-Hash). Der Worker legt es
  beim Installieren mit in den Cache, aber „best effort": Ist unpkg gerade nicht
  erreichbar, gelingt die Installation trotzdem und die Datei wird beim nächsten
  erfolgreichen Laden nachgecacht. Wer die Offline-Fähigkeit ganz unabhängig
  machen will, müsste Leaflet lokal ins Repo legen (vendoren) – bisher nicht
  nötig.
- **Keine Push-Nachrichten, keine Background-Sync-Registrierung** – das würde dem
  „kein Tracking, keine Datenerfassung"-Versprechen widersprechen. Der Worker
  cacht ausschließlich, er sendet nichts.

**Aufwand:** wie geschätzt mittel. Geprüft wird das Zusammenspiel von Manifest,
Icons und Precache-Liste durch `tests/test_pwa.py`.

---

## UI/UX-Review (Juli 2026) – offene Punkte

Ergebnis eines UI/UX-Reviews auf Basis eines Mobil-Screenshots (Android/Chrome,
1080 × 2340) im Abgleich mit `web/index.html`. Die Nummern (R…) entsprechen der
Nummerierung im Review, damit Rückfragen zuordenbar bleiben. Es geht ausschließlich
um das Frontend – Pipeline und Datenmodell bleiben unberührt.

Nicht in diesem Backlog: der entschärfte Standardfilter (steht in
`VOR-VEROEFFENTLICHUNG.md`, Abschnitt „Filter für Abdeckung anpassen"), eine
Telefonnummer in der Pipeline und die Frage nach der `cuisine`-Abdeckung.

### Layout: Fußzeile & Attribution auf dem Handy (hoch)

- [ ] **R2 – `100dvh` statt `100vh`.** `body { height: 100vh }` meint auf Android
  Chrome die *große* Viewport-Höhe (ohne URL-Leiste). `<footer>` mit
  „© OpenStreetMap-Mitwirkende (ODbL)" und Datenschutz-Link liegen dadurch unter
  der Browserleiste, ebenso Leaflets eigenes Attribution-Control unten rechts in
  der Karte. Da die Attribution ODbL-Pflicht ist, hat der Punkt Vorrang.
  Fix: `height: 100dvh` mit `100vh` als Fallback davor.
- [ ] **R3 – `viewport-fit=cover` im Viewport-Meta.** Die `env(safe-area-inset-*)`-
  Regeln für `display-mode: standalone` wirken ohne `viewport-fit=cover` nicht;
  als installierte iOS-App klebt der Header unter der Statusleiste.
- [ ] **P3 – Fußzeile ist mit `0.72rem` (≈ 11,5 px) zu klein** für eine
  Pflichtangabe. Mindestens `0.8rem`.

### Bedienbarkeit & Barrierefreiheit

- [ ] **R4 – Suchfeld ohne Label, Text abgeschnitten.** Das `<input type="search">`
  hat nur ein `placeholder` (kein `<label>`/`aria-label`) – assistiv also namenlos.
  Sichtbar ist außerdem nur „Restaurant oder Adresse sucl", weil `flex: 1 1 200px`
  neben der Checkbox zerdrückt wird. Unter 640 px sollte die Suche eine eigene,
  volle Zeile bekommen.
- [ ] **R5 – Trefferzahl wird nicht angekündigt, 0 Treffer sind ein Loch.**
  `#count` braucht `aria-live="polite"`; `render()` braucht einen Empty State
  („Keine Treffer – Filter zurücksetzen") statt einer stumm leeren Karte.
- [ ] **R6 – Karte ist für Tastatur und Screenreader leer.** Die `L.marker(…)`
  tragen kein `alt`/`title`, die Popup-Inhalte existieren nur im Marker. Vorschlag:
  eine schlichte Ergebnisliste (dieselben gefilterten Daten als `<ul>`) unter bzw.
  neben der Karte. Löst gleichzeitig „was ist in der Nähe?" und macht „In meiner
  Nähe" nach Entfernung sortierbar.
- [ ] **R14 – `alert()` für Geolocation-Fehler ersetzen.** `locateMe()` nutzt zwei
  `alert()`; der Banner-Mechanismus (`showBanner`) existiert bereits.
- [ ] **P3 – Emoji-Icons dekorativ auszeichnen.** 🍽️ 📍 🆕 📲 🥡 ⚑ werden
  mitgelesen und rendern plattformabhängig unterschiedlich – mindestens
  `aria-hidden="true"` auf die rein dekorativen.
- [ ] **P3 – Kopier-Feedback im Fehlerfall.** Schlägt `navigator.clipboard
  .writeText()` fehl, ändert sich am Melde-Link nichts, der OSM-Tab öffnet aber
  trotzdem – dann einen Hinweis „Text bitte von Hand markieren" zeigen.
- [ ] **P3 – Fokus-Verwaltung im Feed-Panel.** Beim Öffnen wandert der Fokus nicht
  in das Panel (Escape schließt immerhin schon).

### Struktur & visuelle Hierarchie

- [ ] **R8 – Der Pitch verschwindet nach dem Laden.** `$meta` wird von
  „Restaurants mit eigenem Lieferservice – direkt bestellen, ohne
  Provisions-Plattformen" auf „883 Restaurants · zuletzt aktualisiert am …"
  überschrieben; die Anzahl steht damit doppelt (Sub-Zeile + `#count`). Claim
  stehen lassen, Datum in die Fußzeile oder hinter ein „ⓘ".
- [ ] **R9 – Header frisst 23 % des Bildschirms.** Suche, zwei Checkboxen, zwei
  Buttons und die Trefferzahl konkurrieren gleichwertig über drei Zeilen; die
  Zahl landet per `margin-left: auto` als Waise neben „Diese Woche". Auf Mobil
  besser: eine Zeile (Suche + „Filter"-Knopf mit Trefferzahl), Rest in ein Bottom
  Sheet. Nebenbei sind die Buttons ~34 px hoch – unter den empfohlenen 44 px
  Touch-Target.
- [ ] **R11 – Popup hat zwei rote Primäraktionen.** „Zur Website & bestellen →"
  und „⚑ Falsche Angabe melden" sind beide `var(--accent)`, fett, gleich groß und
  stehen direkt untereinander. Die Bestellaktion als gefüllter Button, den
  Melde-Link klein und `--muted` unter die Fakten.
- [ ] **R12 – Rot bedeutet vier Dinge.** `--accent` ist Markenfarbe (H1),
  Primärlink, „Jetzt geschlossen", „geschlossen" in der Zeitentabelle *und*
  Melde-Flag. Zustandsfarben von der Markenfarbe trennen.
- [ ] **R13 – Alle Pins sehen gleich aus.** Ob ein Restaurant liefert, abholen
  lässt oder gerade geschlossen ist, sieht man erst nach dem Antippen. Farb- oder
  Formcodierung (z. B. blass = jetzt geschlossen) bringt viel pro Blick – und wird
  wichtig, sobald der Standardfilter entschärft ist.
- [ ] **P3 – Dark Mode fehlt.** Über die CSS-Variablen (`:root`) wäre
  `prefers-color-scheme: dark` ein kleiner Eingriff; abends ist die Seite grell.

### Performance

- [ ] **R7 – Suche drosseln und Popups faul bauen.** `render()` läuft ungedrosselt
  bei jedem `input` und baut für **jeden** Marker vorab das komplette Popup-HTML
  inklusive `openStateNow()`-Parsing. Bei entschärftem Standardfilter sind das 883
  Popups pro Tastendruck. Fix: ~150 ms Debounce, `bindPopup(() => popupHtml(r))`
  (Leaflet akzeptiert eine Funktion) und Marker-Clustering bzw. Canvas-Marker.

### Inhaltliche Feinheiten (P3)

- [ ] **„Heute" in der Öffnungszeiten-Tabelle hervorheben.** Bei „Di–Fr / Sa, So /
  Mo" muss man selbst suchen, was gerade gilt – `berlinNow()` kennt den Wochentag
  schon.
- [ ] **„Jetzt geschlossen – öffnet wieder um 16:30".** Die Intervalle sind in
  `parseIntervals()` bereits geparst; die Zusatzinfo entscheidet, ob jemand bleibt.
- [ ] **Filterzustand teilbar und wiederherstellbar machen.** Bisher gibt es nur
  `?open=1` / `?nearby=1`; `?delivery=0&cuisine=thai` passt ins bestehende Muster
  und verletzt das „keine Cookies"-Versprechen nicht (reine URL-Parameter, keine
  Speicherung).
- [ ] **Feed-Panel verdeckt auf Mobil fast die ganze Karte** – als Bottom Sheet mit
  Griff angenehmer als das aktuelle schwebende Panel.

---

## Weitere offene Punkte

- **Lieferung/Abholung filtern:** Details + echte Abdeckungszahlen stehen in
  `VOR-VEROEFFENTLICHUNG.md` (Abschnitt „Filter für Abdeckung anpassen").
