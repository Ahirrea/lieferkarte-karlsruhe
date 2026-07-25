# 🔨 Ready for Dev

Spezifiziert und direkt baubar: Problem, betroffene Datei und Lösung sind jeweils
benannt. Es geht ausschließlich um das Frontend – Pipeline und Datenmodell
bleiben unberührt. Ist ein Punkt gebaut und live, zieht er als Kurzprotokoll nach
[`DONE.md`](DONE.md).

**Backlog:** [💡 Ideen](IDEEN.md) · 🔨 Ready for Dev ·
[✅ Done](DONE.md) · [Übersicht](README.md)

---

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
  Funktion. (Clustering/Canvas ist
  [Idee 6](IDEEN.md#6-marker-clustering-oder-canvas-renderer).)

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
