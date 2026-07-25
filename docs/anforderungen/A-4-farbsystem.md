# A-4 Farbsystem entflechten (R12)

[← Anforderungen](./README.md) · [Prozess](../PROZESS.md)
· Status siehe [Übersicht](./README.md#übersicht)

**User Story:** Als Nutzerin möchte ich Zustände (liefert / liefert nicht / geöffnet / geschlossen / unbekannt) farblich von der Markenfarbe unterscheiden können, um nicht rot mit rot zu verwechseln.

**Verfeinert am:** 2026-07-25
**Bedient PRD:** „Ziele" — Zustände auf einen Blick; Voraussetzung für „Kernschleife" Schritt 1
**Eingeschränkt durch:** [ADR-006](../entscheidungen/ADR-006-pwa-network-first.md) (`CACHE_VERSION`),
[ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md) („unbekannt" nie als „nein"),
[ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md) (deckende Overlay-Flächen)
· grundsätzlicher Teil dieser Anforderung: [ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)

## Ausgangstext (aus `backlog/IDEEN.md`, Idee 4)

> `--accent` bedeutet vier Dinge gleichzeitig: Markenfarbe (H1), Primärlink,
> „Jetzt geschlossen" bzw. „geschlossen" in der Zeitentabelle *und* Melde-Flag.
> Zustandsfarben gehören von der Markenfarbe getrennt – braucht aber erst einen
> eigenen Satz Tokens neben `--accent`.

**Nachgemessen am 2026-07-25 gegen das heutige `web/index.html` — der
Ausgangstext untertreibt.** Er stammt aus der Zeit vor
[A-1](./A-1-standardfilter-entschaerfen.md); die Filter-Chips und die
„unbekannt"-Badges gab es damals noch nicht. Korrekturen:

| Ausgangstext | Gemessen |
|---|---|
| „vier Dinge" | **Fünf Rollen auf 15 CSS-Stellen** — Marke, Interaktion, aktiver Steuerzustand, Datenzustand, Melde-Flag |
| nur `--accent` betroffen | auch **`--ok` ist doppelt belegt**: Fähigkeit „liefert" *und* Zustand „geöffnet" — und `--muted` trägt zusätzlich „unbekannt" |
| „braucht einen eigenen Satz Tokens" | dazu **16 rohe Hex-Werte außerhalb von `:root`**, u. a. eine komplett untokenisierte Amber-Familie für die Hinweisleiste |
| (kein Wort zum Kontrast) | **8 von 15 Farbpaaren unter 4,5:1** für kleinen Text, darunter *alle vier* Zustands-Badges (3,62–3,76:1) |
| (kein Wort zur Farbenblindheit) | Rot `#d64541` und Grün `#2e8b4f` haben **Kontrast 1,03** zueinander — praktisch identische Helligkeit, bei Rot-Grün-Blindheit nicht unterscheidbar |

Der letzte Punkt ist der wichtigste, weil er über die Umbenennung hinausgeht:
Ein Zustandssatz, der nur über den Farbton trennt, ist für rund 8 % der
männlichen Nutzer wertlos. Das bindet auch [A-5](./A-5-pins-nach-zustand.md).

## Andockpunkte im Code

Alles Betroffene liegt im `<style>`-Block von `web/index.html` (Zeilen 31–357).
Keine Pipeline-Datei ist berührt, kein Datenfeld, keine Persistenz.

**Die 15 `var(--accent)`-Stellen, nach Rolle sortiert:**

| Rolle | Stellen in `web/index.html` |
|---|---|
| **Marke** | 61 `header h1 .accent` · 12 `<meta name="theme-color">` (Literal) |
| **Interaktion** | 286 `.popup-link` · 349/350 `#empty button` · 201/202 `.controls button#install` · 240 `.banner .banner-close:hover` |
| **Aktiver Steuerzustand** | 92/93 `.chip[aria-pressed="true"]` · 113 `.controls button[aria-expanded="true"]` · 117 `.pill` |
| **Datenzustand** | 266 `.hours-grid .time.closed` · 275 `.badge-nodelivery` · 279 `.badge-closed` |
| **Melde-Flag** | 294 `.meld summary` |

**Zwei weitere Mehrfachbelegungen:**

- `--ok: #2e8b4f` (Zeile 38) steht in 274 `.badge-delivery` (**Fähigkeit**) und
  278 `.badge-open` (**Zustand**).
- `--muted: #6b6b6b` (37) ist sekundärer Text an 14 Stellen **und** die Farbe
  von 282 `.badge-unknown` (Zustand „unbekannt").

**Die 16 rohen Hex-Werte außerhalb von `:root`:** `#f0f0ee` (90, 112, 113) ·
`#fff` (94, 118, 351) · `#c23b37` (96) · `#fdf0ef` (205) · `#fff8e6` (213) ·
`#f0e2bd` (214) · `#6b5a1f` (217, 238) · `#d9c68f` (222) · `#fdf7e6` (231) ·
`#e6f4ea` (274, 278) · `#f4e6e6` (275, 279) · `#e7eefc` + `#2b5bb5` (276) ·
`#fff3cd` + `#856404` (277) · `#efefec` (282). Dazu zwei
`rgba(0,0,0,…)`-Schatten (140, 344).

**Was wiederverwendbar ist:** die Token-Mechanik selbst — `:root` plus `var()`
trägt schon, es fehlt nur die Rollentrennung. Die Badge-Klassen bestehen bereits
in der richtigen Granularität (ein Element pro Aussage), und `popupHtml()`
(Zeilen 764–815) unterscheidet `true`/`false`/`null` schon korrekt in drei
Zweige — die Logik bleibt unangetastet, nur die Klassennamen wandern mit.

**Was fehlt:** ein Weg, eine Tokenfarbe in JavaScript zu lesen. Zeile 1051
schreibt die Markenfarbe als Literal in `L.circleMarker` für den eigenen
Standort. [A-5](./A-5-pins-nach-zustand.md) braucht genau diesen Weg für die
Pins, also entsteht er hier: ein Einzeiler `cssVar(name)` über
`getComputedStyle(document.documentElement).getPropertyValue(name)`.

**Außerhalb von `web/index.html` betroffen:** `web/datenschutz.html` (eigener
`:root`-Block, Zeilen 12–19; `--accent` an 34, 37, 61) · `index.html` im
Wurzelverzeichnis (Zeile 19, `a { color: #d64541 }`) ·
`web/manifest.webmanifest` (`theme_color`) · `tools/make_icons.py` (Zeile 26,
`ACCENT = (0xD6, 0x45, 0x41)`, Kommentar `# --accent`).

## Spannung zu Nicht-Zielen — und Auflösung

**Zu den harten Nicht-Zielen in [`PRD.md`](../PRD.md) gibt es keine Spannung.**
Das ist hier die ehrliche Antwort und kein Übersehen: A-4 ist reines CSS, ohne
Datenquelle, ohne Backend, ohne Speicherung, ohne neue Abhängigkeit. Keine
Cookies, kein Tracking, kein `localStorage`, kein Netzverkehr.

Drei Spannungen zu bestehenden **Entscheidungen** gibt es dagegen sehr wohl:

| Spannung | Auflösung |
|---|---|
| **[ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md): „unbekannt" darf nie wie ein „nein" aussehen.** Genau das droht die naheliegende Lösung zu brechen: wird „nein/geschlossen" von Rot auf Slate-Grau umgestellt, liegt es neben dem grauen „unbekannt" — gemessener Textkontrast der beiden zueinander nur 1,65, die Badge-Flächen unterscheiden sich um 1,18. Das wäre eine Regression gegen einen erst gerade getroffenen Beschluss. | **Die beiden trennen sich über die Form, nicht über den Farbton.** „nein" wird ein **gefülltes** Badge (`#33333b` auf `#dcdce1`, 9,16:1), „unbekannt" verliert seine Füllung und bekommt einen **gestrichelten** Rahmen (`--muted` auf `--panel`, 5,33:1). Textkontrast der beiden zueinander steigt damit auf 2,35, und „kein Datum" sieht aus wie kein Datum statt wie eine Absage. Das Muster existiert im Projekt schon: `.chip-reset` ist bereits `border-style: dashed`. |
| **[ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md): alle Overlay-Elemente brauchen einen deckenden `var(--panel)`-Hintergrund**, weil Text über beliebigen Kartenkacheln keinen garantierten Kontrast hat. | Kein Token des neuen Satzes ist transparent oder halbtransparent; die Zustandsfarben sind ausschließlich Vordergrund- und Badge-Flächenfarben **innerhalb** von Panels. Als Regel in [ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md) festgeschrieben. |
| **[ADR-006](../entscheidungen/ADR-006-pwa-network-first.md): `CACHE_VERSION` hochzählen, wenn eine vorab gecachte Datei sich ändert.** `web/index.html` und `web/datenschutz.html` sind vorab gecacht. | `CACHE_VERSION` in `web/sw.js` wird hochgezählt. **Achtung Reihenfolge:** [A-3](./A-3-header-umbau.md) plant `v3` — wer A-4 zuerst baut (so entschieden), nimmt `v3` und A-3 rückt auf `v4`. Der A-3-Text ist entsprechend anzupassen. |

Ein **Nicht-Ziel im Kleinen** wird berührt: Dark Mode steht als P3 in
[`BACKLOG.md`](../BACKLOG.md) und ist in A-3 ausdrücklich ausgeschlossen. A-4
baut ihn **nicht**, macht ihn aber möglich — siehe Entscheidung 5.

## Entscheidungen (mit Begründung)

Alle fünf am 2026-07-25 von der Produktverantwortung entschieden. Die
Empfehlungen wurden durchgehend bestätigt; es gibt hier keine
Gegenentscheidung zu protokollieren.

### 1. Drei Ebenen: Marke / Interaktion / Zustand

Nicht nur die Zustandsfarbe abspalten, sondern die Rollen vollständig trennen und
die 16 rohen Hex-Werte in `:root` holen.

*Warum:* Das Minimalvorgehen (nur die drei Zustands-Stellen umhängen, ~6 Zeilen)
hätte A-5 auch entblockt, aber `--accent` weiter zwischen Marke, Interaktion und
Steuerzustand geteilt gelassen — und damit dieselbe Anforderung in einem Jahr
erneut fällig gemacht. Die dritte Option (zwei Token-Ebenen, Palette + Rolle,
`--rot-600` → `--zustand-nein`) ist in einem Ein-Datei-Projekt ohne Build-Schritt
eine Indirektion zu viel und hätte Dark Mode mit hereingezogen.

*Verworfen:* „Minimal: nur Zustand abspalten" · „Volles Token-System mit
Palette-Ebene + Dark Mode".

### 2. Die Marke behält `#d64541`, der Zustand „nein" wird Slate

*Warum:* `#d64541` steckt in den PWA-Icons, in `manifest.theme_color`, in drei
`theme-color`-Metas und in `tools/make_icons.py`. Die Marke zu verschieben hieße
Icons neu generieren und den von `tests/test_pwa.py` geprüften Gleichlauf
Manifest ↔ Meta mitziehen — Aufwand ohne Nutzen für R12, denn die Verwechslung
löst sich genauso auf, wenn *der Zustand* das Rot abgibt.

Slate statt eines dunkleren Rots, weil es **messbar** besser trägt: Slate
`#33333b` hat zu Grün `#1d6b3a` einen Helligkeitsabstand von 1,92, ein dunkleres
Rot `#a3302c` nur 1,07 — nahe am heutigen, praktisch nicht unterscheidbaren
Wert 1,03. Und Marke-Rot gegen Zustands-Rot läge bei 1,59: die Verwechslung aus
R12 wäre gemildert, nicht beseitigt.

*Verworfen:* „Zustand bleibt Rot, Marke wird neu" (teuerste Folgekosten, kein
Zusatznutzen) · „Zustand wird ein dunkleres Rot" (löst R12 nur halb und lässt das
Rot-Grün-Problem unangetastet).

### 3. Alle acht Kontrastverstöße werden mitgefixt

*Warum:* Die Token-Werte werden ohnehin angefasst. Ein zweiter Durchgang später
kostet dasselbe nochmal, und [A-5](./A-5-pins-nach-zustand.md) würde die
fehlerhaften Werte erben. Sichtbare Folge: Badges und Links werden merklich
dunkler — das ist gewollt und wird hier als Konsequenz benannt, nicht als
Nebenwirkung versteckt.

Ein Sonderfall bleibt: `header h1 .accent` erreicht mit der Markenfarbe auf Weiß
4,39:1 und verfehlt 4,5:1 um 0,11. Statt die Marke zu verschieben (Entscheidung 2
sagt nein) wächst `header h1` von 1,15 rem auf **1,2 rem**: 19,2 px fett liegt
über der WCAG-Grenze für „großen Text" (18,66 px fett), wo 3:1 genügt — 4,39:1
ist dann konform. Gleiches in `web/datenschutz.html`.

*Verworfen:* „nur die Zustandsfarben" · „getrennte Backlog-Aufgabe".

### 4. A-4 wird vor A-3 gebaut

*Warum:* A-4 ist klein und ändert **kein Layout**; A-3 schreibt denselben
`<style>`-Block strukturell um. In dieser Reihenfolge baut A-3 direkt auf den
neuen Tokens auf, statt die alten Farbnamen zu übernehmen und später zu
ersetzen. A-5 ist damit sofort entblockt.

*Verworfen:* „A-3 zuerst" (A-5 bliebe länger blockiert, und A-3 würde die
`--accent`-Mehrfachnutzung vorübergehend zementieren) · „Reihenfolge offen
lassen".

### 5. Dark Mode wird vorbereitet, nicht gebaut

*Warum:* Die P3-Notiz im Backlog ist berechtigt („wer die Tokens ohnehin
entflechtet, sollte Dark Mode gleich mitdenken") — aber A-3 hat Dark Mode
ausdrücklich ausgeschlossen, und zwei Farbumbauten gleichzeitig sind nicht
gegenprüfbar. Die Vorbereitung ist konkret und kostet nichts: **nach A-4 enthält
keine CSS-Regel außerhalb von `:root` noch einen Farbwert.** Dark Mode ist danach
ein `@media (prefers-color-scheme: dark)`-Block, der ausschließlich `:root`
überschreibt. Der Backlog-Punkt wird entsprechend präzisiert.

## Umfang / Nicht-Umfang

- **Rein:** Token-Ebenen `--marke` / `--aktion` / `--zustand-*` in
  `web/index.html` · Aufteilung von `--ok` und Herauslösen von „unbekannt" aus
  `--muted` · alle 16 rohen Hex-Werte und die zwei `rgba()`-Schatten nach `:root`
  · acht Kontrastkorrekturen auf WCAG AA · `header h1` auf 1,2 rem ·
  Badge-Klassen auf die Zustandsachse umbenannt · „unbekannt" als
  Umriss-Badge · `cssVar()`-Helfer plus Umstellung des Standort-Markers
  (Zeile 1051) · dieselbe Token-Trennung in `web/datenschutz.html` und im
  Wurzel-`index.html` · Kommentar in `tools/make_icons.py` · `CACHE_VERSION`
  hochzählen · [ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md).
- **Raus:** Pin-Farben und Pin-Formen auf der Karte
  ([A-5](./A-5-pins-nach-zustand.md) — A-4 liefert nur die Tokens) · Dark Mode
  (bleibt P3, siehe Entscheidung 5) · jede Layout-, Abstands- oder
  Strukturänderung außer `header h1`s Schriftgröße
  ([A-3](./A-3-header-umbau.md)) · Änderung der Markenfarbe, der PWA-Icons oder
  von `manifest.theme_color` · Filterlogik, `FILTER_DEFAULTS`, URL-Parameter,
  Pipeline, Datenfelder · neue Badges oder neue Aussagen im Popup · ein
  Palette-/Alias-Zweischichtsystem · Emoji-`aria-hidden` (eigener P3-Punkt).

## Spezifikation

### Der neue `:root`-Block

```css
:root {
  /* ---- Flächen und Text (Werte unverändert) ---- */
  --bg: #f7f7f5;
  --panel: #ffffff;
  --text: #1e1e1e;
  --muted: #6b6b6b;
  --border: #e3e3df;
  --flaeche-hover: #f0f0ee;     /* war 3× hart: Chip-, Button-, Panel-Hover */
  --auf-farbe: #ffffff;         /* Text auf gefüllter Fläche (war 3× #fff)  */
  --schatten-weich: 0 6px 24px rgba(0, 0, 0, 0.12);
  --schatten-stark: 0 6px 24px rgba(0, 0, 0, 0.18);

  /* ---- Ebene 1: Marke. Steckt in Icons, Manifest und theme-color.
          Wert unverändert. Nie für einen Zustand verwenden. ---- */
  --marke: #d64541;

  /* ---- Ebene 2: Interaktion. Dieselbe Rot-Familie, eine Stufe dunkler
          (H 3 statt 2, L 45 statt 55) — Weiß auf --marke erreicht nur
          4,39:1, auf --aktion 5,85:1. ---- */
  --aktion: #b8352f;
  --aktion-hover: #9c2b26;      /* war hart: #c23b37 */
  --aktion-schwach: #fdf0ef;    /* war hart: Hover des Install-Knopfs */

  /* ---- Ebene 3: Datenzustand. Nur diese drei Paare für ja/nein/unbekannt.
          Niemals ohne begleitendes Symbol (Rot-Grün-Blindheit). ---- */
  --zustand-ja: #1d6b3a;          --zustand-ja-bg: #e6f4ea;
  --zustand-nein: #33333b;        --zustand-nein-bg: #dcdce1;
  --zustand-unbekannt: #6b6b6b;   /* ohne Füllung, gestrichelter Rahmen */

  /* ---- Betriebsstatus und Hinweisleiste (Amber, je eigene Rolle) ---- */
  --status: #856404;            --status-bg: #fff3cd;
  --hinweis: #6b5a1f;           --hinweis-bg: #fff8e6;
  --hinweis-border: #f0e2bd;    --hinweis-btn-border: #d9c68f;
  --hinweis-btn-hover: #fdf7e6;
}
```

`--accent` und `--ok` **entfallen** — nach der Umsetzung darf kein `var(--accent)`
und kein `var(--ok)` mehr im Repo stehen.

### Wohin jede Stelle wandert

| Bisher | Neu |
|---|---|
| 61 `header h1 .accent` | `--marke`, dazu `header h1` auf 1,2 rem |
| 286 `.popup-link` · 294 `.meld summary` · 201/202 `#install` · 240 `.banner-close:hover` | `--aktion` |
| 92/93 `.chip[aria-pressed]` · 117 `.pill` · 349/350 `#empty button` | `--aktion` als Fläche, `--auf-farbe` als Text |
| 96 `.chip[aria-pressed]:hover` | `--aktion-hover` |
| 113 `button[aria-expanded]` | `--flaeche-hover` als Fläche, `--aktion` als Rahmen |
| 205 `#install:hover` | `--aktion-schwach` |
| 274 `.badge-delivery` + 278 `.badge-open` | **`.badge-yes`** → `--zustand-ja` / `--zustand-ja-bg` |
| 275 `.badge-nodelivery` + 279 `.badge-closed` | **`.badge-no`** → `--zustand-nein` / `--zustand-nein-bg` |
| 276 `.badge-takeaway` | entfällt als eigene Farbe → `.badge-yes` (siehe unten) |
| 282 `.badge-unknown` | bleibt `.badge-unknown`, aber `background: none` + `border: 1px dashed var(--border)` + `color: var(--zustand-unbekannt)` |
| 277 `.badge-status` | `--status` / `--status-bg` |
| 266 `.hours-grid .time.closed` | `--zustand-nein` |
| 213/214/217/222/231/238 Hinweisleiste | die fünf `--hinweis-*`-Tokens |
| 140/344 `rgba(0,0,0,…)` | `--schatten-stark` / `--schatten-weich` |
| 1051 `L.circleMarker(… "#d64541" …)` | `cssVar("--marke")` |

**Farbe trägt den Zustand, das Symbol trägt die Fähigkeit.** Deshalb verliert
`.badge-takeaway` sein Blau (`#2b5bb5` auf `#e7eefc`): „🥡 Abholung" ist ein
*Ja*, genau wie „✔ Lieferservice", und wird grün. Unterschieden werden die beiden
weiter durch ihr Symbol und ihren Text — nicht durch die Farbe, die ab jetzt für
den Zustand reserviert ist. Ohne diesen Schnitt wäre A-5 nicht baubar: ein Pin
kann nicht gleichzeitig „blau = Abholung" und „grün/slate = offen/zu" codieren.
Sichtbare Folge im Popup: bei Restaurants mit beidem stehen zwei grüne Badges
nebeneinander.

### Zustände und ihre Darstellung

| Zustand | Kommt vor bei | Farbe | Form | Symbol |
|---|---|---|---|---|
| ja | Lieferung 63 · Abholung 237 · jetzt geöffnet | `--zustand-ja` auf `--zustand-ja-bg` | gefüllt | ✔ / 🥡 / 🟢 |
| nein | Lieferung 47 · Abholung 8 · jetzt geschlossen | `--zustand-nein` auf `--zustand-nein-bg` | gefüllt | 🔴 bzw. Text |
| unbekannt | Lieferung 773 · Abholung 638 · Zeiten nicht auswertbar | `--zustand-unbekannt` auf `--panel` | **Umriss, gestrichelt** | — |

(Zahlen aus `data/restaurants.db`, 883 aktive Restaurants, Scan vom 2026-07-21.
„unbekannt" ist der häufigste Zustand — 87,5 % bei Lieferung, 72,3 % bei
Abholung. Genau deshalb darf er nicht wie eine Absage aussehen.)

`.badge-status` (Betriebsstatus, Amber) bleibt eine eigene Rolle: bei den 883
aktiven Restaurants ist `business_status` derzeit **0 mal** von `OPERATIONAL`
verschieden, gerendert wird das Badge heute praktisch nur für „nicht mehr in
OpenStreetMap gelistet" im Feed (Zeile 921). Es wird tokenisiert, nicht
umgestellt.

### Kontrast: vorher / nachher

Alle Werte gerechnet nach WCAG 2.1 (relative Luminanz). Badges sind 0,72 rem
≈ 11,5 px, also **kleiner Text** → Schwelle 4,5:1.

| Paar | Vorher | Nachher |
|---|---|---|
| Badge „ja" (Lieferung/Abholung/geöffnet) | 3,76 ❌ | **5,75** ✔ |
| Badge „nein" (keine Lieferung/Abholung/geschlossen) | 3,62 ❌ | **9,16** ✔ |
| Badge „unbekannt" | 4,63 ✔ | **5,33** ✔ |
| Aktiver Filter-Chip (Text auf Fläche) | 4,39 ❌ | **5,85** ✔ |
| Aktiver Chip, Hover | 5,28 ✔ | **7,53** ✔ |
| `.popup-link`, `.meld summary`, `#install` | 4,39 ❌ | **5,85** ✔ |
| `#empty button` | 4,39 ❌ | **5,85** ✔ |
| `.hours-grid .time.closed` | 4,39 ❌ | **8,78** ✔ |
| `header h1 .accent` | 4,39 ❌ (Schwelle 4,5) | 4,39 ✔ (Schwelle 3,0 bei 1,2 rem fett) |
| Badge „Betriebsstatus" | 4,96 ✔ | 4,96 ✔ |
| Hinweisleiste | 6,38 ✔ | 6,38 ✔ |

Und der Punkt, um den es in R12 eigentlich geht:

| Unterscheidbarkeit | Vorher | Nachher |
|---|---|---|
| „ja" gegen „nein" (Helligkeitsabstand) | 1,03 | **1,92** |
| „nein" gegen „unbekannt" | 1,65 | **2,35** + Formunterschied |
| Marke gegen Datenzustand | Marke *war* der Datenzustand | **2,00** (rot gegen slate) |

1,92 ist besser, aber nicht genug: **Farbe allein trägt einen Zustand nie.**
Deshalb steht in [ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)
die Regel, dass jeder Zustand zusätzlich ein Symbol, eine Form oder Text
mitführt — was das Popup heute schon tut (✔ / 🥡 / 🟢 / 🔴) und was A-5 für die
Pins übernehmen muss.

### Datenmodell, externe Abhängigkeiten

Keine Änderung. Kein neues Feld, keine Migration, kein `export.py`, kein
`scanner.py`, keine neue externe Abhängigkeit. `restaurants.json` bleibt Byte für
Byte identisch.

### Randfälle und Fehlerbehandlung

- **`cssVar()` liefert leer.** In einem Kontext ohne aufgelöste
  Custom-Properties (Test-Stub, sehr alter Browser) gibt
  `getPropertyValue` einen Leerstring zurück, und Leaflet würde ohne Farbe
  zeichnen. `cssVar(name, fallback)` bekommt daher einen zweiten Parameter und
  liefert bei leerem Ergebnis den mitgegebenen Literalwert. Rückgabe immer
  `.trim()`en — Browser liefern den Wert mit führendem Leerzeichen.
- **`theme-color` kann kein `var()`.** Die drei Metas und
  `manifest.theme_color` bleiben Literale. Der Gleichlauf ist durch
  `tests/test_pwa.py::test_theme_color_passt_zum_meta_tag_der_seite` abgesichert;
  ein Kommentar an `--marke` und an `ACCENT` in `tools/make_icons.py` benennt die
  Kopplung, damit niemand den Wert einseitig ändert.
- **Zwei grüne Badges nebeneinander** bei „liefert *und* holt ab" (in der DB
  aktuell 47 Restaurants mit beidem `true`). Bewusst so; die Symbole 🚴/🥡 und die
  Beschriftung trennen sie.
- **Gestricheltes Umriss-Badge auf getöntem Grund.** `.badge-unknown` steht auch
  in Popups über `--panel` und im Feed über `--bg`; auf beiden erreicht
  `--muted` 5,33 bzw. 4,97:1. Kein Fall liegt auf einer Kartenkachel — das
  verbietet ADR-008 ohnehin.
- **Halb übernommene Umstellung.** Bleibt irgendwo ein `var(--accent)` stehen,
  fällt die Eigenschaft im Browser stumm auf `initial` zurück (schwarzer
  Text, unsichtbarer Rahmen) — der Fehler ist also leise. Deshalb ist die
  Repo-weite Suche nach `--accent` / `--ok` Teil der Definition of Done.

### Barrierefreiheit

- Alle Text-/Flächenpaare erreichen 4,5:1 (kleiner Text) bzw. 3:1 (großer Text,
  UI-Rahmen) — Tabelle oben.
- Jeder Zustand ist **redundant codiert**: Farbe *und* Symbol/Form *und* Text.
  Damit bleibt die Information ohne Farbwahrnehmung vollständig.
- Der Helligkeitsabstand innerhalb des Zustandssatzes steigt von 1,03 auf 1,92 —
  bei Rot-Grün-Blindheit ist das der einzige verbleibende Farbhinweis.
- `aria-pressed` an den Chips bleibt unberührt; die Farbe ist dort schon heute
  nur die sichtbare Zweitcodierung.
- **Nicht** Teil von A-4: `aria-hidden` an den dekorativen Emoji (eigener
  P3-Punkt in `BACKLOG.md`) und die Fokus-Sichtbarkeit (kommt mit A-3).

### Testplan

Reine Frontend-Änderung, also kein Pipeline-Test betroffen — die Suite läuft
trotzdem, weil `tests/test_pwa.py` `web/index.html` liest.

1. **`python3 -m unittest discover -s tests -v`** muss grün bleiben,
   insbesondere `test_pwa.py` (`theme-color` ↔ `manifest.theme_color`,
   Precache-Liste).
2. **Repo-weite Suche:** `grep -rn -- "--accent\|--ok\b" web/ tools/ index.html`
   liefert keinen Treffer mehr außer in Prosa/Doku.
   `grep` nach `#[0-9a-fA-F]\{3,6\}` in den `<style>`-Blöcken liefert Treffer
   **nur innerhalb von `:root`** (die `theme-color`-Metas ausgenommen).
3. **Playwright mit `L`-Stub** (Vorgehen in `CLAUDE.md`), gegen synthetische
   Daten **und** die echte `web/restaurants.json`:
   - `popupHtml()` für die sechs Kombinationen aus
     `delivery`/`takeaway` ∈ {`true`,`false`,`null`} liefert die Klassen
     `badge-yes` / `badge-no` / `badge-unknown` — und **niemals** `badge-no` für
     einen `null`-Wert. Das ist der ADR-007-Test und der wichtigste hier.
     (Der Stub muss `bindPopup` als **Funktion** speichern, sonst liest jedes
     Popup `undefined`.)
   - Ein Restaurant mit nicht auswertbaren Öffnungszeiten erzeugt kein
     `badge-yes`/`badge-no` für „jetzt geöffnet".
   - `getComputedStyle` auf je ein Element pro Rolle: die aufgelöste Farbe
     stimmt mit dem Token überein (belegt, dass keine Regel auf `initial`
     zurückgefallen ist).
   - Der Standort-Marker aus `locateMe()` bekommt die Markenfarbe (`cssVar`
     aufgelöst, nicht Leerstring).
4. **Kontrast rechnerisch nachweisen:** ein Wegwerf-Skript im Scratch-Verzeichnis
   rechnet die Paare der Tabelle nach und muss alle ≥ 4,5:1 (bzw. ≥ 3:1 für
   `header h1`) bestätigen. Kein Testfall im Repo — es gibt keinen CSS-Test und
   A-4 soll keinen einführen.
5. **PWA von Hand:** über `http://localhost:8000` laden, DevTools → Application →
   Service Workers: die neue `CACHE_VERSION` erscheint, die Seite fragt vor dem
   Wechsel (kein `skipWaiting()` beim Install).
6. **`web/datenschutz.html` und `index.html`** im Wurzelverzeichnis sichtprüfen —
   beide haben eigene Farbdefinitionen und werden leicht vergessen.

### Doku- und Backlog-Auswirkungen

- **Neu:** [ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)
  (Status `vorgeschlagen`, wird mit der Umsetzung `akzeptiert`) plus Zeile in
  `docs/entscheidungen/README.md`.
- **`docs/TECHNICAL.md`:** kurzer Abschnitt „Farbrollen" mit dem Token-Satz und
  der Regel „kein Farbwert außerhalb von `:root`".
- **`docs/UMGESETZT.md`:** Eintrag nach der Umsetzung, mit der Kontrasttabelle
  vorher/nachher als Begründung.
- **`docs/BACKLOG.md`:** der P3-Punkt „Dark Mode fehlt" wird präzisiert — nach
  A-4 ist es ein `@media`-Block über `:root`, keine Suche durch alle Regeln
  mehr. Der Verweis auf A-4 bleibt.
- **[A-3](./A-3-header-umbau.md):** die `CACHE_VERSION`-Angabe in „Rein" rückt
  von `v3` auf `v4`, weil A-4 vorher `v3` verbraucht. Zusätzlich der Hinweis,
  dass A-3 die neuen Tokens verwendet und `header h1` bereits 1,2 rem ist.
- **[A-5](./A-5-pins-nach-zustand.md):** „Eingeschränkt durch" verliert die
  A-4-Abhängigkeit, sobald A-4 erledigt ist; die Regel „Farbe trägt den Zustand,
  Symbol die Fähigkeit" und der `cssVar()`-Helfer sind ab dann ihre Grundlage.
- **`docs/anforderungen/README.md`:** Statuszeile und das
  Abhängigkeitsdiagramm (A-4 → A-5 wird zur erledigten Kante).
- **`CLAUDE.md`:** ein Satz bei den Constraints, dass Farbrollen getrennt sind
  und `--accent` nicht mehr existiert.

## Definition of Done

- [ ] `web/index.html` enthält den neuen `:root`-Block; **kein `var(--accent)`
      und kein `var(--ok)`** mehr im Repo.
- [ ] **Kein Farbwert außerhalb von `:root`** in beiden `<style>`-Blöcken —
      Literale nur noch in den `theme-color`-Metas und in `manifest.webmanifest`.
- [ ] Alle 15 Stellen der Zuordnungstabelle sind umgehängt; die Rolle jeder
      Stelle ist am Tokennamen ablesbar.
- [ ] `.badge-yes` / `.badge-no` / `.badge-unknown` ersetzen die sechs alten
      Badge-Klassen; `.badge-unknown` ist Umriss + gestrichelt, **nicht** gefüllt.
- [ ] `delivery === null` / `takeaway === null` rendern `badge-unknown`, nie
      `badge-no` — per Playwright über alle sechs Kombinationen belegt
      ([ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)).
- [ ] Alle Paare der Kontrasttabelle erreichen ≥ 4,5:1, `header h1` bei 1,2 rem
      ≥ 3:1. Nachgerechnet, nicht geschätzt.
- [ ] Markenfarbe unverändert `#d64541` in Icons, `manifest.theme_color` und den
      drei `theme-color`-Metas; `tests/test_pwa.py` grün.
- [ ] `cssVar()` existiert mit Fallback-Parameter; der Standort-Marker nutzt es.
- [ ] `web/datenschutz.html` und das Wurzel-`index.html` sind mitgezogen.
- [ ] `CACHE_VERSION` in `web/sw.js` hochgezählt
      ([ADR-006](../entscheidungen/ADR-006-pwa-network-first.md)); kein
      `skipWaiting()` beim Install dazugekommen.
- [ ] „© OpenStreetMap-Mitwirkende" in der Fußzeile unverändert sichtbar und
      lesbar (die Fußzeile nutzt `--muted`, das sich nicht ändert).
- [ ] `python3 -m unittest discover -s tests -v` grün.
- [ ] Frontend gegengeprüft mit synthetischen Daten **und** der echten
      `web/restaurants.json`.
- [ ] Keine Cookies, kein Tracking, kein `localStorage` dazugekommen; keine
      Layout- oder Logikänderung außer `header h1`s Schriftgröße.
- [ ] ADR-009 angelegt und in `docs/entscheidungen/README.md` verlinkt;
      TECHNICAL/UMGESETZT/BACKLOG/A-3/A-5 nachgezogen; Status in der
      [Übersicht](./README.md#übersicht) auf 🏁.

## Umsetzungsschritte

1. **ADR-009 schreiben** (Status `vorgeschlagen`) und in
   `docs/entscheidungen/README.md` verlinken — die Regeln stehen fest, bevor CSS
   entsteht.
2. **`:root` in `web/index.html` ersetzen:** neue Tokens dazu, `--accent` und
   `--ok` weg. Danach ist die Seite absichtlich kaputt (alle alten `var()`
   fallen auf `initial`) — das ist der Beweis, dass Schritt 3 vollständig sein
   muss.
3. **Die 15 Stellen umhängen**, Tabelle „Wohin jede Stelle wandert" von oben nach
   unten abarbeiten; `grep -c "var(--accent)"` muss danach 0 melden.
4. **Rohe Hex-Werte und die zwei Schatten** in Tokens auflösen.
5. **Badge-Klassen umbenennen** — CSS *und* die sechs Fundstellen in
   `popupHtml()` (Zeilen 776–800) sowie die Feed-Stelle bei Zeile 921. Das Blau
   von `.badge-takeaway` fällt weg.
6. **`.badge-unknown` auf Umriss + gestrichelt** umstellen (die
   ADR-007-Abgrenzung gegen „nein").
7. **`header h1` auf 1,2 rem** in `web/index.html` und `web/datenschutz.html`.
8. **`cssVar(name, fallback)` einführen** und Zeile 1051 umstellen.
9. **`web/datenschutz.html`** (eigener `:root`, drei Stellen) und
   **`index.html`** im Wurzelverzeichnis nachziehen; Kommentar an
   `tools/make_icons.py` Zeile 26.
10. **`CACHE_VERSION` hochzählen.**
11. **Prüfen:** Unittests, die zwei `grep`-Belege, Playwright mit `L`-Stub gegen
    beide Datensätze, Kontrastskript, PWA von Hand.
12. **Doku nachziehen** (TECHNICAL, UMGESETZT, BACKLOG, A-3, A-5, README-Diagramm,
    CLAUDE.md), ADR-009 auf `akzeptiert`, Status auf 🏁.
