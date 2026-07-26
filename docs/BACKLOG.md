# Backlog

Technische Aufgaben und Fixes — Verhalten bleibt gleich oder die Lösung ist
offensichtlich. **Ausgearbeitete Anforderungen** stehen in
[`anforderungen/README.md`](./anforderungen/README.md) und entstehen über den
festen [Refinement-Prozess](./PROZESS.md); die Trennlinie steht dort unter
„Anforderung oder Aufgabe? Der Test".

Stand: 2026-07-26. Reihenfolge = Priorität. Die Kürzel `R…`/`P…` stammen aus dem
UI/UX-Review vom Juli 2026 (Mobil-Screenshot, Android/Chrome, 1080 × 2340, im
Abgleich mit `web/index.html`) und bleiben erhalten, damit Rückfragen zuordenbar sind.

**Vor jedem Push von Pipeline-Änderungen:**
`python3 -m unittest discover -s tests -v`

## Hoch – die Pflicht-Attribution ist auf dem Handy unsichtbar ✅ erledigt

Diese drei Punkte gehören zusammen: sie betreffen alle die ODbL-pflichtige
Angabe „© OpenStreetMap-Mitwirkende" im Footer. Deshalb Vorrang vor allem
anderen — ohne sichtbare Attribution ist die Weiterverbreitung unzulässig
(siehe [ADR-001](./entscheidungen/ADR-001-openstreetmap-statt-google-places.md)).

> **Alle drei erledigt mit [A-3](./anforderungen/A-3-header-umbau.md)**
> (2026-07-26). Die Fußzeile ist seitdem ein Struktur-Element: sie liegt immer
> im Fluss, ihre gemessene Höhe steht als `--footer-h` bereit, und Sheets wie
> Karten-Controls richten sich daran aus — geprüft ist, dass sich die Rechtecke
> von Fußzeile und offenem Sheet **nicht** überschneiden. Der Abschnitt bleibt
> als Protokoll stehen.

- [x] **R2 – `100dvh` statt `100vh`.** `body { height: 100vh }`
  (`web/index.html:49`) meint auf Android Chrome die *große* Viewport-Höhe (ohne
  URL-Leiste). Der `<footer>` mit Attribution und Datenschutz-Link liegt dadurch
  unter der Browserleiste, ebenso Leaflets eigenes Attribution-Control unten
  rechts. Fix: `height: 100dvh` mit `100vh` als Fallback davor.
  **Erledigt mit [A-3](./anforderungen/A-3-header-umbau.md)** (2026-07-26):
  `height: 100vh` steht als Fallback vor `height: 100dvh`. Für das Overlay war
  das keine Kosmetik mehr, sondern Voraussetzung.
- [x] **R3 – `viewport-fit=cover` im Viewport-Meta.** Die
  `env(safe-area-inset-*)`-Regeln für `display-mode: standalone` wirken ohne
  `viewport-fit=cover` nicht; als installierte iOS-App klebt der Header unter
  der Statusleiste.
  **Erledigt mit [A-3](./anforderungen/A-3-header-umbau.md)** (2026-07-26);
  die Bedienzeile und `#mapControls` rücken zusätzlich um die Safe-Area ein.
- [x] **P3 – Fußzeile zu klein.** `0.72rem` (≈ 11,5 px) ist für eine
  Pflichtangabe zu wenig – mindestens `0.8rem`.
  **Erledigt mit [A-3](./anforderungen/A-3-header-umbau.md)** (2026-07-26):
  `0.8rem` auf allen Breiten, auf Mobil einzeilig mit Datenstand. Dass die drei
  Angaben bei 360 px nicht nebeneinander passen, ist dort gemessen und der
  Datenschutz-Link deshalb ins Sheet gewandert.

## Mittel – Bedienbarkeit, Struktur, Performance

- [x] **R4 – Suchfeld ohne Label, Text abgeschnitten.** Das
  `<input type="search">` hat nur ein `placeholder` (kein `<label>`/`aria-label`)
  – assistiv also namenlos. Sichtbar ist außerdem nur „Restaurant oder Adresse
  sucl", weil `flex: 1 1 200px` (`web/index.html:71`) neben der Checkbox
  zerdrückt wird. Unter 640 px sollte die Suche eine eigene, volle Zeile bekommen.
  **Erledigt mit [A-3](./anforderungen/A-3-header-umbau.md)** (2026-07-26):
  `aria-label="Restaurant oder Adresse suchen"`, und das Feld ist unter 640 px
  auf 181,3 px von 393 px gewachsen (vorher 251 px geteilt mit Chips und
  Reset-Chip in derselben Zeile). Die Flex-Basis ist `8rem` statt `auto` — mit
  `auto` bricht die Zeile schon bei 393 px um.
- [x] **R5 – Trefferzahl wird nicht angekündigt, 0 Treffer sind ein Loch.**
  Erledigt mit [A-1](./anforderungen/A-1-standardfilter-entschaerfen.md):
  `#count` hat `role="status"` + `aria-live="polite"`, und bei null Treffern
  erscheint `#empty` mit „Alle Restaurants zeigen" statt einer stumm leeren
  Karte. Der neue Standardfilter „Liefert jetzt" hat null Treffer zum
  Regelfall gemacht (nachts liefert niemand) – ohne Leerzustand wäre er nicht
  vertretbar gewesen.
- [ ] **R14 – `alert()` für Geolocation-Fehler ersetzen.** `locateMe()` nutzt
  zwei `alert()` (`web/index.html:899` und `:912`); der Banner-Mechanismus
  (`showBanner`) existiert bereits.
- [ ] **R8 – Der Pitch verschwindet nach dem Laden.** `$meta` wird von
  „Restaurants mit eigenem Lieferservice – direkt bestellen, ohne
  Provisions-Plattformen" auf „883 Restaurants · zuletzt aktualisiert am …"
  überschrieben; die Anzahl steht damit doppelt (Sub-Zeile + `#count`). Claim
  stehen lassen, Datum in die Fußzeile oder hinter ein „ⓘ".
  **Auf Mobil erledigt mit [A-3](./anforderungen/A-3-header-umbau.md)**
  (2026-07-26): Titel und Claim sind unter 640 px absichtlich weg
  (Entscheidung 2), das Datum steht in der Fußzeile (Entscheidung 4). **Für
  Desktop bleibt der Punkt offen** — dort überschreibt `$meta` weiter den Claim
  und die Anzahl steht doppelt (Sub-Zeile + `#count`).
- [ ] **R11 – Popup hat zwei rote Primäraktionen.** „Zur Website & bestellen →"
  und „⚑ Falsche Angabe melden" sind beide `var(--aktion)` (bis A-4:
  `var(--accent)`), fett, gleich groß und stehen direkt untereinander. Die
  Bestellaktion als gefüllter Button, den Melde-Link klein und `--muted` unter
  die Fakten. Von A-3 ausdrücklich **nicht** angefasst.
- [x] **R7 – Suche drosseln, Popups faul bauen.** Erledigt mit
  [A-1](./anforderungen/A-1-standardfilter-entschaerfen.md): 150 ms Debounce auf
  das Suchfeld, `bindPopup(() => popupHtml(r))` statt vorab gebautem HTML samt
  `openStateNow()`-Parsing. Ohne Filter zeichnet `render()` damit 883 Marker in
  ~197 ms (gemessen mit `L`-Stub). Clustering/Canvas bleibt
  [A-6](./anforderungen/A-6-clustering-oder-canvas.md) – durch den engen Default
  aber nur noch „nice to have".
  *Nachgemessen am 2026-07-26 mit
  [A-5](./anforderungen/A-5-pins-nach-zustand.md) (885 Restaurants, `L`-Stub,
  Median aus 20 Durchläufen nach 20 Aufwärmrunden, wiederholt in 5 Läufen): ohne Filter **5,6 ms**,
  mit Standardfilter **0,8 ms** – vorher 0,4 bzw. 4,2 ms. Die Pins brauchen den
  Öffnungszustand jedes Markers; bezahlt wird das dadurch, dass `berlinNow()` den
  `Intl.DateTimeFormat` nur noch einmal baut (ohne diese Änderung 62,9 ms) und
  die Zeitauswertung hinter den billigen Filtern steht. Die 197 ms von damals
  sind mit dieser Methode nicht vergleichbar – sie wurden ohne Aufwärmrunden
  gemessen.*
  *Nochmals nachgemessen am selben Tag nach dem Rückbau der Zustands-Pins
  ([ADR-011](./entscheidungen/ADR-011-pins-wieder-einheitlich.md)): mit
  Standardfilter **0,60 ms**. Beide Tempo-Änderungen sind absichtlich geblieben —
  der einmal gebaute `Intl.DateTimeFormat` und die späte Zeitauswertung, jetzt
  zusätzlich über `f.open` kurzgeschlossen, weil nur noch der Filter das Ergebnis
  braucht. Zurückgenommen wurde die Optik, nicht die Technik.*

## Niedrig – Feinschliff

- [ ] **P3 – Emoji-Icons dekorativ auszeichnen.** 🍽️ 📍 🆕 📲 🥡 ⚑ werden
  mitgelesen und rendern plattformabhängig unterschiedlich – mindestens
  `aria-hidden="true"` auf die rein dekorativen.
  **Teilweise erledigt mit [A-3](./anforderungen/A-3-header-umbau.md)**
  (2026-07-26): die Emoji in den *neuen* Bedienelementen (⚙ Filter, 🆕 Feed,
  📍 In meiner Nähe) sind `aria-hidden`, und die Icon-Knöpfe tragen ein
  `aria-label`. **Offen bleiben** die Emoji in den Filter-Chips (🚴 🥡 🕒), im
  `h1` (🍽️), im Install-Knopf (📲) und in den Popups (🍽️ ⚑ 🟢 🔴) — dort
  stecken sie mitten im sichtbaren Text und brauchen je einen eigenen `<span>`.
- [ ] **P3 – Kopier-Feedback im Fehlerfall.** Schlägt
  `navigator.clipboard.writeText()` fehl, ändert sich am Melde-Link nichts, der
  OSM-Tab öffnet aber trotzdem – dann „Text bitte von Hand markieren" zeigen.
- [x] **P3 – Fokus-Verwaltung im Feed-Panel.** Beim Öffnen wandert der Fokus
  nicht in das Panel (Escape schließt immerhin schon).
  **Erledigt mit [A-3](./anforderungen/A-3-header-umbau.md)** (2026-07-26):
  `openSheet()` setzt den Fokus auf die Sheet-Überschrift, `closeSheet()` gibt
  ihn an den Auslöser zurück – für Filter- und Feed-Sheet in einem.
- [ ] **P3 – Dark Mode fehlt.** `prefers-color-scheme: dark`; abends ist die
  Seite grell. **Die Voraussetzung steht seit A-4** (umgesetzt 2026-07-25,
  [ADR-009](./entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)): kein
  Farbwert liegt mehr außerhalb von `:root`, die vormals 16 rohen Hex-Werte sind
  Tokens. Damit ist dieser Punkt **ein `@media`-Block, der ausschließlich `:root`
  überschreibt** – keine Suche durch alle Regeln mehr. Konkret zu überschreiben
  sind die Flächen/Text-Tokens (`--bg`, `--panel`, `--text`, `--muted`,
  `--border`, `--flaeche-hover`) sowie die Hintergrundpaare der Zustände
  (`--zustand-*-bg`, `--status-bg`, `--hinweis-bg`); `--marke` bleibt, weil sie
  an Icons und `theme_color` hängt. Zwei Fallen: die Kontrastpaare müssen für
  dunkel **neu** gerechnet werden (die Werte aus A-4 gelten nur für hell), und
  `--auf-farbe` ist dann nicht mehr automatisch Weiß.
- [ ] **„Heute" in der Öffnungszeiten-Tabelle hervorheben.** Bei „Di–Fr / Sa, So
  / Mo" muss man selbst suchen, was gerade gilt – `berlinNow()` kennt den
  Wochentag schon.
- [ ] **„Jetzt geschlossen – öffnet wieder um 16:30".** Die Intervalle sind in
  `parseIntervals()` bereits geparst; die Zusatzinfo entscheidet, ob jemand bleibt.

## Datenqualität nachsehen

- [ ] **Küchenstil: Abdeckung prüfen.** Die `cuisine`-Pipeline ist
  [fertig](./UMGESETZT.md) („Filter nach Küchenstil"), aber in
  `data/restaurants.db` sind nach vier Scans (letzter: 2026-07-21) **0 von 883**
  aktiven Restaurants getaggt – während `opening_hours` bei 741 gefüllt ist. Für
  Karlsruhe sind null Küchenstil-Tags unplausibel; das deutet eher auf ein
  Pipeline-Problem als auf fehlende OSM-Daten. Der Filter bleibt so lange
  versteckt (das ist gewollt), aber der Befund gehört nachgesehen:

  ```bash
  python3 -c "import sqlite3; c=sqlite3.connect('data/restaurants.db'); \
  print(c.execute('SELECT cuisine, COUNT(*) FROM restaurants WHERE active=1 \
  GROUP BY cuisine ORDER BY 2 DESC LIMIT 20').fetchall())"
  ```

## Ausbau von bereits Umgesetztem

Drei bewusst zurückgestellte Erweiterungen – jeweils erst nötig, wenn der
aktuelle Kompromiss nicht mehr reicht:

- [ ] **`opening_hours.js` vendoren** (lokal, kein CDN) für die volle
  `opening_hours`-Abdeckung. Aktuell nicht nötig: ~90 % der getaggten Fälle
  wertet der eigene Mini-Parser schon eindeutig aus (siehe
  [ADR-004](./entscheidungen/ADR-004-oeffnungszeiten-eigener-parser.md)).
- [ ] **Leaflet lokal ins Repo legen** – macht die Offline-Fähigkeit unabhängig vom
  CDN. Bisher genügt der „best effort"-Precache. (BauWatch-KA macht das schon so,
  unter `vendor/leaflet/` – dort ist es das Muster.)
- [ ] **Küchenstil-Synonyme gruppieren** (`sushi` unter `japanese`, `doner` unter
  `kebab`). Wäre Interpretation der OSM-Daten; erst sinnvoll, wenn die
  Auswahlliste zu lang wirkt.

---

> Diese Liste ersetzt seit 2026-07-25 `backlog/READY-FOR-DEV.md` sowie die Ideen 8
> und 9 aus `backlog/IDEEN.md` — sie sind Aufgaben, keine Anforderungen. Die
> UX-Umbauten aus derselben Datei (R6, R9, R12, R13) sind zu
> [Anforderungen](./anforderungen/README.md) geworden. **R12** ist mit
> [A-4](./anforderungen/A-4-farbsystem.md) erledigt; R2/R3/R4 kamen mit
> [A-3](./anforderungen/A-3-header-umbau.md) mit. **R13** war mit
> [A-5](./anforderungen/A-5-pins-nach-zustand.md) erledigt und ist mit deren
> Rückbau ([ADR-011](./entscheidungen/ADR-011-pins-wieder-einheitlich.md))
> **wieder offen** — künftig zu lösen über
> [A-2](./anforderungen/A-2-ergebnisliste.md), nicht erneut über die Pins.
