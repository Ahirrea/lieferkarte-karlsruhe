# A-3 Header-Umbau: Karte im Vollbild, Bedienung als Overlay + Bottom Sheets (R9)

[← Anforderungen](./README.md) · [Prozess](../PROZESS.md)
· Status siehe [Übersicht](./README.md#übersicht)

**User Story:** Als Handy-Nutzerin möchte ich mehr Karte und weniger Bedienleiste
sehen, um mich im eigentlichen Inhalt zu orientieren.

**Verfeinert am:** 2026-07-25 · **entschieden am:** 2026-07-25
(→ [Entscheidungen](#entscheidungen-2026-07-25),
[ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md))
**Bedient PRD:** „Kernschleife" Schritt 1 („Schritt 1 muss ohne Interaktion
nützlich sein") und Schritt 2 („In meiner Nähe")
**Eingeschränkt durch:** [ADR-001](../entscheidungen/ADR-001-openstreetmap-statt-google-places.md)
(die ODbL-Attribution muss sichtbar bleiben — sie begrenzt, wie weit die Karte
ins Vollbild darf), [ADR-006](../entscheidungen/ADR-006-pwa-network-first.md)
(`index.html` ist vorab gecacht → `CACHE_VERSION`),
[ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md)
(der Leerzustand und der Zurücksetzen-Weg dürfen nicht verschwinden),
[ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)
(die Farbrollen stehen fest — A-3 setzt keine eigenen Farbwerte)

**Nachtrag 2026-07-25: [A-4](./A-4-farbsystem.md) ist umgesetzt.** Drei Dinge
sind damit für A-3 schon erledigt oder festgelegt:

1. **Die Tokens existieren.** `--marke` / `--aktion` / `--aktion-hover` /
   `--aktion-schwach` / `--zustand-*` / `--flaeche-hover` / `--auf-farbe` /
   `--schatten-weich` / `--schatten-stark` / `--hinweis-*` stehen in `:root`.
   A-3 benutzt sie und legt **keinen** neuen Farbwert außerhalb von `:root` ab —
   das ist die bindende Regel aus ADR-009, nicht bloß ein Stilwunsch.
2. **`header h1` ist bereits 1,2 rem** (nicht mehr 1,15 rem), weil die
   Markenfarbe erst als „großer Text" die WCAG-Schwelle erreicht. Wer die
   Größe im Umbau anfasst, darf **nicht unter 1,2 rem** gehen, solange das `h1`
   auf Desktop sichtbar ist und die Markenfarbe trägt (4,39:1 < 4,5:1).
   Unter 640 px wird das `h1` ohnehin visuell versteckt — dort ist die Grenze
   gegenstandslos.
3. **`CACHE_VERSION` steht auf `v3`.** A-3 nimmt `v4`.

## Der Bestand — gemessen, nicht geschätzt

Der Ausgangstext nennt „23 % des Bildschirms". Gemessen (Playwright mit
`L`-Stub, echte `web/restaurants.json`, 883 Restaurants, Standardfilter aktiv)
ist es schlimmer, weil `.controls` mit `flex-wrap` je nach Breite unterschiedlich
oft umbricht:

| Viewport | Header | Anteil | Zeilen in `.controls` | Karte |
|---|---|---|---|---|
| 393 × 851 (1080 × 2340 @ 2,75) | 203,7 px | **23,9 %** | 4 | 605,5 px (71,2 %) |
| 393 × 851, mit „📲 App installieren" | 220,1 px | **25,9 %** | 5 | — |
| 360 × 740 | 235,1 px | **31,8 %** | 5 | 463,1 px (62,6 %) |
| 360 × 740, mit „📲 App installieren" | 259,1 px | **35,0 %** | 5 | — |
| 768 × 1024 | 139,3 px | 13,6 % | 3 | 856,9 px |

Drei Befunde, die im Ausgangstext fehlen:

1. **Der Install-Knopf ist mitzurechnen.** Er ist im Test versteckt (headless
   Chromium feuert kein `beforeinstallprompt`), auf einem echten Android-Chrome
   ist er sichtbar — und kostet eine weitere Zeile. Der schlechteste reale Fall
   ist damit **35 % Header** auf 360 px.
2. **Der Zurücksetzen-Chip ist dauerhaft da.** `anyFilterActive()` ist beim
   Standardfilter „Liefert jetzt" per Definition `true`, also zeigt
   `#resetFilters` („✕ Alle zeigen") **immer** — er ist kein Sonderfall, sondern
   ein festes Element der Leiste.
3. **Jedes Bedienelement ist 32,4 px hoch** — Suchfeld, alle drei Filter-Chips,
   der Reset-Chip, „📍 In meiner Nähe", „🆕 Diese Woche". Das sind 0,45 rem
   Innenabstand + 0,85 rem Schrift + 1 px Rahmen. Empfohlenes Touch-Target: 44 px.
   Die Trefferzahl `#count` ist 16 px hoch und damit gar kein Ziel.

Und der zweite Teil der Idee, gleich mitgemessen — das Feed-Panel:

| Viewport | Panel | Karte | verdeckte Kartenhöhe |
|---|---|---|---|
| 393 × 851 | 377 × 468 px | 393 × 606 px | **77 %** |
| 360 × 740 | 344 × 407 px | 360 × 463 px | **88 %** |

Das bestätigt „verdeckt auf Mobil fast die ganze Karte" — und die Ursache für
`bottom: 4rem` in der `@media (max-width: 640px)`-Regel ist bereits im Code
kommentiert: **die Fußzeile mit der ODbL-Attribution darf nicht verdeckt
werden.** Das ist die harte Grenze für jeden Vollbild-Entwurf.

## Andockpunkte im Code

Alles in `web/index.html` — die Pipeline ist nicht betroffen, es fließt kein
neues Datenfeld. Kein Python, keine DB-Migration, keine Tests in `tests/`.

**Wiederverwendbar, praktisch unverändert:**

- `#feed` samt `.feed-*`-CSS, `renderFeed()`, `feedItemMeta()`, `focusPlace()`,
  `FEED_GROUPS` — der Inhalt des Feed-Panels bleibt, nur seine Hülle wird zum Sheet.
- `setFeedOpen(open)` und der `Escape`-Listener sind bereits die halbe
  Sheet-Mechanik (`hidden` + `aria-expanded` am Auslöser).
- `focusPlace()` schließt auf `≤ 640 px` schon selbst das Panel
  (`window.matchMedia("(max-width: 640px)")`) — das Muster für die Breite gibt es
  also im JS bereits, nicht nur in der CSS.
- Die Filterlogik in `render()`, `currentFilters()`, `chipOn()`/`setChip()`,
  `clearFilters()`, `anyFilterActive()`, `updateEmptyState()`,
  `readUrlState()`/`writeUrlState()`, `FILTER_DEFAULTS`: **wird nicht angefasst.**
  Der Umbau verschiebt nur, *wo* die Chips stehen, nicht *was* sie tun.
- `showBanner()` / `#banner` für Update-, Offline- und iOS-Hinweise.
- `locateMe()` — bleibt, bekommt nur einen neuen Auslöser.

**Was fehlt:**

- Eine Sheet-Mechanik (öffnen/schließen, Griff, Wischen, Fokus, „nur eines
  gleichzeitig"). Es gibt sie halb, für genau ein Panel und ohne Fokus-Führung
  (offener Backlog-Punkt P3 „Fokus-Verwaltung im Feed-Panel").
- Ein Container für die Filter, der auf Mobil Sheet und auf Desktop die heutige
  Chip-Reihe ist. **Die Chips können nicht in zwei DOM-Eltern gleichzeitig
  liegen** — daraus folgt die Struktur unten.
- `aria-label` am Suchfeld (offener Backlog-Punkt R4: assistiv namenlos).
- `height: 100dvh` und `viewport-fit=cover` (R2/R3). Für den heutigen Header sind
  das Kosmetik-Bugs; für ein Overlay, das sich an den Viewport-Rändern ausrichtet,
  sind sie **blockierend** — mit `100vh` liegen Fußzeile und die untere
  Bedienspalte auf Android Chrome unter der URL-Leiste.

## Spannung zu Nicht-Zielen — und Auflösung

| Spannung | Auflösung |
|---|---|
| **ODbL-Attribution** ([ADR-001](../entscheidungen/ADR-001-openstreetmap-statt-google-places.md), PRD §7): „© OpenStreetMap-Mitwirkende" muss sichtbar bleiben. „Karte im Vollbild" könnte heißen: Fußzeile weg. | **„Ohne Header" heißt nicht „ohne Fußzeile".** Die `<footer>` bleibt im Fluss, unverdeckt, und **jedes** Sheet endet oberhalb von ihr (so wie heute schon `bottom: 4rem`). Zusätzlich bleibt Leaflets eigenes Attribution-Control aktiv. Nicht verhandelbar, eigene Zeile in der Definition of Done. |
| **Keine Cookies, kein Tracking, kein `localStorage`** (PRD §4, `CLAUDE.md`): ein Panel-Zustand lädt dazu ein, „zuletzt geöffnet" zu speichern. | Der Sheet-Zustand ist **flüchtig** — weder `localStorage` noch URL-Parameter. Begründung unter [Entscheidung 5](#entscheidungen-2026-07-25). Die Filter selbst bleiben wie bisher in der URL (A-8). |
| **Kein Backend, kein Build-Schritt** (PRD §4, [ADR-002](../entscheidungen/ADR-002-kein-backend-daten-im-repo.md)): Bottom Sheets sind der klassische Anlass, eine Komponentenbibliothek einzuziehen. | Handgeschrieben in der einen `index.html`, wie alles andere. Keine neue Abhängigkeit, kein npm, kein Framework — die Mechanik ist ~60 Zeilen JS und CSS-Transform. |
| **[ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md):** „Der Leerzustand darf nie wieder entfernt werden", der Zurücksetzen-Weg ist Teil der Entscheidung. Ein Umbau, der die Filter hinter einen Knopf legt, kann beides verstecken. | `#empty` bleibt **auf der Karte**, nicht im Sheet, und „Alle Restaurants zeigen" bleibt dort ein direkt tippbarer Knopf. Der Reset-Chip wandert ins Sheet, aber die Trefferzahl steht **außen** am Filter-Knopf — der Zustand „0 von 883" ist ohne Öffnen sichtbar. |
| **PRD §3 „Stand sichtbar"**: der Datenstand steht heute in `#meta` im Header — und der Header verschwindet auf Mobil. | Der Stand wandert in die Fußzeile („Stand 21.07.2026"). Siehe [Entscheidung 4](#entscheidungen-2026-07-25). |
| **Barrierefreiheit** (kein Nicht-Ziel, aber A-2 wartet genau darauf): Text über beliebigen Kartenkacheln hat keinen garantierten Kontrast. | Alle Overlay-Elemente haben einen **deckenden** `var(--panel)`-Hintergrund plus Schatten. Kein Text liegt direkt auf Kacheln. |

Kein Konflikt mit den Nicht-Zielen bleibt offen.

## Optionen

Vier Wege, in aufsteigendem Eingriff. Alle vier sind rein clientseitig, keiner
berührt Daten oder Pipeline.

**Option 1 — Nur Header verdichten, kein Sheet.** Suche in eigene volle Zeile,
Filter in ein `<details>` unter dem Kopf, Feed-Panel bleibt. Billigste Variante,
kein `position: fixed`, kein Fokus-Management. Header ≈ 90 px (10,6 %). Löst das
Feed-Problem (77–88 % Verdeckung) **nicht** und schiebt beim Aufklappen die Karte
nach unten.

**Option 2 — Ein-Zeilen-Kopfzeile im Fluss + zwei Sheets, eine Mechanik.**
`[Suche] [⚙ Filter · 35]` als normaler `<header>` (63 px), Filter und Feed als
getrennte Bottom Sheets mit gemeinsamer Implementierung. Karte 758 px = **89,1 %**,
vollständig unverdeckt. Löst beide Teile der Idee, ohne Overlay-Risiken.

**Option 3 — Ein Sheet mit Tabs** („Filter" | „🆕 Diese Woche" | später „Liste").
Ein Panel-Zustand, alles Sekundäre an einem Ort. Preis: eine Navigationsebene
mehr, und der `counts.NEW`-Pill muss durch den Tab hindurch sichtbar bleiben.

**Option 4 — Karten-Overlay ohne Header.** Suche und Filter als schwebende Pillen
über der Karte, kein Header-Block im Fluss. Kacheln laufen bis zum oberen Rand.
Preis: Kontrast über Kacheln, Marker unter den Pillen, Popup-Auto-Pan muss den
Streifen kennen, und die Attribution braucht eine ausdrücklich geschützte Zone.

## Empfehlung (war: Option 2) — und der Einwand gegen Option 4

Empfohlen war **Option 2**. Entschieden wurde **Option 4** (siehe unten). Der
Einwand gehört mit Zahlen ins Protokoll, einmal, dann wird gebaut wie entschieden:

Beide Optionen sparen gegenüber heute rund **140 px** (16,5 % des Viewports auf
393 × 851). Was Option 4 gegenüber Option 2 zusätzlich bringt, ist gemessen
klein — und teilweise negativ:

| 393 × 851 | heute | Option 2 (Kopfzeile im Fluss) | Option 4 (Overlay) |
|---|---|---|---|
| Kartenelement | 605 px (71,2 %) | 758 px (89,1 %) | **821 px (96,5 %)** |
| davon **unverdeckt** | 605 px (71,2 %) | **758 px (89,1 %)** | 753 px (88,5 %) |
| Kachelfläche, die man tatsächlich sieht | 605 px | 758 px | ≈ 770 px¹ |

¹ Die Pillen sind deckend; sichtbar ist im Overlay-Streifen nur, was zwischen
ihnen durchscheint (Seitenabstände + Lücken, ≈ 25 % von 68 px ≈ 17 px).

Der Overlay gewinnt also gegenüber Option 2 rund **12 px sichtbare Kachelfläche
und verliert 5 px unverdeckte Karte** — der Unterschied ist optisch, nicht
funktional. Dafür übernimmt er drei Risiken, die Option 2 nicht hat: Kontrast
über beliebigen Kacheln, Marker im obersten Streifen sind nicht antippbar, und
`focusPlace()`/`bindPopup` müssen den Streifen beim Auto-Pan kennen (sonst öffnet
ein Popup hinter der Suchzeile). Alle drei sind lösbar — die Spezifikation unten
löst sie —, aber sie sind zusätzlicher, dauerhaft zu pflegender Aufwand.

**Was den Einwand aufwiegt** und in der Entscheidung mitschwingt: Vollbild ist
das erwartete Muster für Kartenanwendungen. Wer die Seite auf dem Handy öffnet,
vergleicht sie nicht mit ihrer Vorversion, sondern mit Google Maps — und dort
läuft die Karte unter der Suchleiste durch. Der Gewinn ist nicht in Pixeln zu
messen, sondern darin, dass die Seite wie eine Karten-App aussieht statt wie ein
Formular mit Karte darunter.

Das grüne Licht zur Umsetzung gilt als Bestätigung dieser Entscheidung. Der
Rückweg bleibt billig: Option 4 → Option 2 ist ein Wechsel von
`position: fixed` auf `position: static` in einer Media-Query.

## Entscheidungen (2026-07-25)

| Nr. | Frage | Entscheidung |
|---|---|---|
| 1 | Lösungsweg | **Option 4 — Karten-Overlay ohne Header** (gegen die Empfehlung Option 2, siehe oben). Filter und Feed werden Bottom Sheets. |
| 2 | Marke/Claim auf Mobil | **Strikt eine Zeile.** „🍽️ Lieferkarte Karlsruhe" und die Claim-Zeile verschwinden unter 640 px optisch; das `<h1>` bleibt visuell versteckt im Dokument. Der Name steht im Tab und unter dem Homescreen-Icon. |
| 3 | Breiten | **Nur Mobil (≤ 640 px).** Über 640 px bleibt der heutige Header inklusive direkt anklickbarer Chips und das Feed-Panel als schwebendes Fenster. Am Desktop sind 13,6 % Header kein Problem. |
| 4 | „📍 In meiner Nähe" | **Runder Icon-Knopf unten rechts auf der Karte**, 44 px, oberhalb von Leaflets Attribution-Control. Kernschleife Schritt 2 bleibt ein Tipp. |

Vier weitere Weichen sind nicht vorgelegt worden, weil sie sich aus den obigen
und aus den Projektregeln zwingend ergeben. Sie stehen hier, damit sie
widersprechbar sind:

5. **Sheet-Zustand ist flüchtig** — kein `localStorage` (hartes Nicht-Ziel) und
   auch kein URL-Parameter. Ein geteilter Link soll die Karte zeigen, nicht ein
   offenes Filterpanel. Die Filter selbst bleiben in der URL wie in A-8.
6. **Zwei getrennte Sheets, eine gemeinsame Mechanik** (statt Option 3 mit Tabs).
   Filter und Feed haben inhaltlich nichts miteinander zu tun; getrennte Sheets
   sparen eine Navigationsebene, lassen den `counts.NEW`-Pill außen sichtbar und
   sind einzeln testbar. Die Mechanik ist bewusst wiederverwendbar — die
   Ergebnisliste aus [A-2](./A-2-ergebnisliste.md) wird ihr dritter Nutzer.
7. **Filter wirken sofort**, kein „Übernehmen"/„Abbrechen". Die Trefferzahl am
   Filter-Knopf ist die Rückmeldung; ein Formular-Modell mit Bestätigen wäre ein
   Bruch mit dem heutigen Verhalten und mit `writeUrlState()`.
8. **Die Fußzeile wird auf Mobil einzeilig** und verliert dort „Keine Cookies,
   kein Tracking" — die Attribution (Pflicht), der Stand und der
   Datenschutz-Link bleiben. Das Versprechen selbst steht unverändert in
   `datenschutz.html`, im `README.md`, in der `<meta name="description">` und im
   Sheet-Abschnitt „Mehr"; nur seine Platzierung ändert sich. Am Desktop bleibt
   die Fußzeile vollständig.

Grundsätzlicher Teil der Entscheidung:
[ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md).

## Umfang / Nicht-Umfang

- **Rein:** Overlay-Bedienzeile und Bottom Sheets unter 640 px · 44-px-Touch-Targets
  für alle Bedienelemente · Feed-Panel wird Sheet · „In meiner Nähe" als
  Karten-Control · Fokus-Führung und `Escape` für beide Sheets · Fußzeile
  einzeilig mit Stand · `100dvh` + `viewport-fit=cover` (R2/R3, weil blockierend)
  · `aria-label` am Suchfeld (R4) · Fußzeilen-Schriftgröße auf 0,8 rem (P3) ·
  ~~`CACHE_VERSION` → `v3`.~~ → **`CACHE_VERSION` → `v4`**: [A-4](./A-4-farbsystem.md)
  wird am 2026-07-25 vor A-3 eingeplant und verbraucht `v3`
  ([ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)).
- **Raus:** Ergebnisliste ([A-2](./A-2-ergebnisliste.md)) — das Sheet ist ihr
  künftiger Ort, aber sie ist eine eigene Anforderung · Farbsystem
  ([A-4](./A-4-farbsystem.md), läuft **vorher** — A-3 benutzt dessen Tokens
  `--marke`/`--aktion`/`--zustand-*` und setzt keine eigenen Farbwerte) und
  Pin-Zustände ([A-5](./A-5-pins-nach-zustand.md))
  · Clustering ([A-6](./A-6-clustering-oder-canvas.md)) · Dark Mode · Desktop-Redesign
  · Sheet mit mehreren Rastpunkten (peek/halb/voll) · Änderungen an Filterlogik,
  `FILTER_DEFAULTS`, URL-Parametern oder an der Pipeline · neue Datenfelder ·
  Leaflet lokal vendoren.

## Spezifikation

### Struktur — die eine Regel, die alles trägt

**Overlay-Elemente sind Geschwister von `#map`, niemals Kinder.** Liegt ein
Bedienelement im DOM innerhalb von `#map`, bekommt Leaflet dessen Pointer-Events
und man braucht `L.DomEvent.disableClickPropagation` — was (a) Gesten-Konflikte
zur Dauerbaustelle macht und (b) die Frontend-Tests bricht, weil der `L`-Stub aus
`CLAUDE.md` kein `DomEvent` hat. Als Geschwister sieht Leaflet die Events nie.

Die heutige Struktur erfüllt das schon (`header`, `#banner`, `#feed`, `footer`
sind Geschwister von `#map`) — sie muss beim Umbau nur erhalten bleiben.
Ausnahme bleiben `#loading` und `#empty`: die liegen bewusst *in* `#map` und sind
`pointer-events: none` bis auf den Reset-Knopf.

```
<body>                                 height: 100dvh (100vh als Fallback davor)
  <header>                             ≤640: position fixed, transparent, oben
    <h1>                               ≤640: visually-hidden
    <div id="meta">                    ≤640: display none (Inhalt → Fußzeile)
    <div class="controls">             ≤640: eine Zeile, deckende Pillen
      #search  #filterToggle  #feedToggle
      <div id="filterPanel">           ≤640: Bottom Sheet · >640: inline wie heute
        #fDelivery #fTakeaway #fOpen #cuisine #resetFilters
        + Abschnitt „Mehr": #install, Datenschutz, Stand, „keine Cookies"
      </div>
      <span id="count">                ≤640: visually-hidden (bleibt aria-live)
  <div id="banner">                    ≤640: fixed, direkt unter der Bedienzeile
  <div id="map">   #loading  #empty
  <div id="mapControls">  #nearMe      ≤640 und >640: unten rechts über der Karte
  <aside id="feed">                    ≤640: Bottom Sheet · >640: wie heute
  <footer>                             immer im Fluss, nie verdeckt
```

`#filterPanel` bleibt im DOM ein Kind von `.controls`, weil die Chips auf Desktop
inline und auf Mobil im Sheet stehen müssen und CSS keine Knoten umhängt. Daraus
folgt eine Falle, die im Code kommentiert gehört: **`header` darf kein
`transform`, `filter` oder `will-change` bekommen** — sonst wird es zum
Containing Block und das `position: fixed` des Sheets richtet sich an ihm statt
am Viewport aus.

### Bedienzeile ≤ 640 px

`[🔍 Suche …]` · `[⚙ Filter · 35]` · `[🆕 3]`

- Höhe **≥ 44 px** je Element, Zielhöhe der Zeile ≤ 72 px
  (44 px + 2 × 0,75 rem Außenabstand).
- Jedes Element: `background: var(--panel)`, `border-radius: 999px`,
  `box-shadow: 0 2px 8px rgba(0,0,0,.18)`, `pointer-events: auto`. Das `header`
  selbst ist transparent und `pointer-events: none`, damit man zwischen den
  Pillen die Karte bedienen kann.
- Suchfeld: `flex: 1 1 auto`, `min-width: 8rem`, `aria-label="Restaurant oder
  Adresse suchen"` (R4). Debounce von 150 ms bleibt.
- Filter-Knopf: `aria-expanded`, `aria-controls="filterPanel"`, Text
  „⚙ Filter" + Trefferzahl. **Zwei Zustände sichtbar machen:** aktive
  Nicht-Standard-Filter markiert der Knopf wie ein aktiver Chip (Akzentfarbe);
  bei 0 Treffern wird die Zahl nicht rot eingefärbt (das erklärt `#empty`).
- Feed-Knopf: nur wenn `data.feed` existiert (wie heute), zeigt „🆕" +
  `counts.NEW` als Pill, `aria-label="Diese Woche neu — 3 Einträge"`.
- Der Install-Knopf wandert in den Abschnitt „Mehr" des Filter-Sheets; sein
  heutiger Sichtbarkeits-Mechanismus (`beforeinstallprompt` / iOS-Erkennung)
  bleibt unverändert und steuert dort die Sichtbarkeit der Zeile.

### Trefferzahl — zwei Orte, eine Quelle

`render()` schreibt über eine neue Funktion `updateCount(shown, total)` beides:

- `#count` behält Text („35 von 883 angezeigt"), `role="status"`,
  `aria-live="polite"` — auf Mobil visuell versteckt, aber weiter vorgelesen
  (R5 und die A-1-Zusage bleiben erfüllt).
- Der Filter-Knopf zeigt die Kurzform („Filter · 35").

Beide dürfen nie auseinanderlaufen; die Übereinstimmung mit
`window.__markers.length` ist Prüfpunkt im Test.

### Sheet-Mechanik (Filter und Feed, gemeinsam)

- Eine Funktion `openSheet(name | null)`: schließt das andere Sheet, setzt
  `hidden`, `aria-expanded` am Auslöser und den Fokus.
- **Nicht modal:** `role="dialog"` + `aria-labelledby`, **kein**
  `aria-modal="true"`, kein Scrim, kein Fokus-Käfig. Begründung: die Filter
  wirken sofort, man *soll* die Karte dahinter sehen und weiter bedienen können.
- Öffnen: Fokus auf die Sheet-Überschrift (`tabindex="-1"`). Schließen: Fokus
  zurück auf den Auslöser. Damit ist der Backlog-Punkt P3 „Fokus-Verwaltung im
  Feed-Panel" erledigt.
- Schließen über: Griff antippen · ✕ · `Escape` (existiert schon fürs Feed) ·
  Auslöser erneut antippen · **Wischen nach unten** > 60 px.
  Wischen ist ein `pointerdown`/`pointermove`/`pointerup`-Delta auf dem Griff und
  dem Sheet-Kopf, **nicht** auf dem scrollbaren Körper — sonst kollidiert es mit
  dem Scrollen einer langen Feed-Liste.
- **Keine Rastpunkte.** Ein Sheet ist offen oder zu. Peek/halb/voll wären
  Trägheits-Physik ohne Bibliothek; das ist der Ertrag nicht wert.
- Animation: `transform: translateY(100%) → 0`, 200 ms, unter
  `@media (prefers-reduced-motion: reduce)` auf 0 ms.
- Geometrie: `left/right: 0`, `bottom: <Höhe der Fußzeile>`,
  `max-height: min(70dvh, 32rem)`, `border-radius: 14px 14px 0 0`, Griff als
  4 × 36 px Balken mit 44 px Trefferfläche, Körper `overflow-y: auto` +
  `overscroll-behavior: contain`.
- `z-index`: Leaflet belegt bis 800 (Popups 700, Controls 800). Daher
  Bedienzeile 950, Banner 940, `#mapControls` 930, Sheets 1000.

### Filter-Sheet: Inhalt

Überschrift „Filter" + Trefferzahl („35 von 883") + ✕. Danach:

1. **Lieferung / Abholung / Jetzt geöffnet** — dieselben drei Chips wie heute,
   `aria-pressed`, `FILTER_DEFAULTS` und `render()` unverändert. Im Sheet ist
   Platz für je eine ganze Zeile mit erklärendem Untertitel; das ist die
   Gelegenheit, „unbekannt ist kein nein" einmal auszuschreiben
   (Datenlage: `delivery` 7 % getaggt, `takeaway` 26 %).
2. **Küchenstil** — `#cuisine`, bleibt versteckt, solange nichts getaggt ist
   (aktuell 0 von 883, siehe Backlog „Küchenstil: Abdeckung prüfen").
3. **„✕ Alle zeigen"** — `#resetFilters`, unverändert `clearFilters()`.
4. **Abschnitt „Mehr"** — „📲 App installieren" (wenn möglich), Datenstand,
   „Keine Cookies, kein Tracking", Link auf `datenschutz.html`, und die
   ODbL-Attribution als Text (zusätzlich zur Fußzeile, nicht an ihrer Stelle).

### Feed-Sheet

Inhalt, Gruppierung und `focusPlace()` bleiben. Änderungen:

- Hülle wird Sheet (Griff, gemeinsame Mechanik), `max-height: min(70dvh, 32rem)`.
- `focusPlace()` schließt auf Mobil weiterhin das Sheet und gibt den Fokus
  danach an die Karte statt ins Nichts.
- Popup-Auto-Pan muss die Bedienzeile kennen, sonst öffnet das Popup dahinter:
  `L.popup({ autoPanPaddingTopLeft: [12, 80], autoPanPaddingBottomRight: [12, 60] })`
  in `focusPlace()` und dieselben Optionen an `bindPopup(fn, opts)` in `render()`.

### Karten-Control „In meiner Nähe"

- Runder 44-px-Knopf, `#mapControls` unten rechts, `aria-label="Restaurants in
  meiner Nähe zeigen"`, deckender Hintergrund + Schatten.
- Sitzt **oberhalb** von Leaflets Attribution-Control (unten rechts) und
  oberhalb der Fußzeile: `bottom: calc(<Fußzeile> + <Attribution> + 0,5rem)`.
  Leaflets Zoom-Control bleibt oben links und ist nicht betroffen.
- `attributionControl: false` ist **keine** Option, auch nicht bei Platznot.
- `locateMe()` unverändert; die beiden `alert()` sind der offene Backlog-Punkt
  R14 und bleiben hier außen vor.

### Fußzeile

- Mobil einzeilig, `font-size: 0.8rem` (P3): „© OpenStreetMap-Mitwirkende ·
  Stand 21.07.2026 · Datenschutz". Der Stand wird beim Laden aus
  `data.lastScanAt` gefüllt (heute schreibt derselbe Code `#meta`).
- Desktop unverändert vollständig.
- `height: 100dvh` am `body` (R2) und `viewport-fit=cover` im Viewport-Meta (R3),
  damit die Zeile auf Android Chrome und als installierte iOS-App wirklich
  sichtbar ist. Die `env(safe-area-inset-*)`-Regeln für `display-mode: standalone`
  müssen zusätzlich die Bedienzeile oben und `#mapControls` unten einrücken.

### Randfälle & Fehlerbehandlung

| Fall | Verhalten |
|---|---|
| `restaurants.json` lädt nicht | Wie heute: Text in `#loading`. Bedienzeile bleibt sichtbar, Filter-Knopf zeigt keine Zahl. |
| Kein `data.feed` (altes JSON) | Feed-Knopf bleibt versteckt; die Bedienzeile hat dann zwei Elemente. |
| 0 Treffer (Standardfall nachts, ADR-007) | `#empty` auf der Karte, oberhalb `padding-top: 5rem`, damit der Kasten nicht unter der Bedienzeile klebt. „Alle Restaurants zeigen" bleibt direkt tippbar. Filter-Knopf zeigt „Filter · 0". |
| Sheet offen, Gerät wird gedreht / überschreitet 640 px | `matchMedia`-Listener: beim Wechsel auf Desktop wird das Sheet geschlossen und `#filterPanel` ist wieder inline sichtbar; der Fokus geht auf den ersten Chip statt auf einen verschwundenen Auslöser. |
| Sheet offen und Feed-Eintrag angesprungen | Sheet schließt, Karte zentriert mit Auto-Pan-Padding, Fokus auf die Karte. |
| Sehr langer Suchtext | Pille wächst nicht über ihre Zeile; `text-overflow` im Feld, nicht in der Zeile. |
| Tastaturbedienung | Tab-Reihenfolge: Suche → Filter → Feed → Karte → `#nearMe` → Fußzeile. Offenes Sheet reiht sich direkt nach seinem Auslöser ein (DOM-Reihenfolge stimmt bereits). |
| Bildschirmlupe / 200 % Zoom | Bedienzeile darf umbrechen — dann zwei Zeilen statt Abschneiden. Kein `white-space: nowrap` auf dem Container. |
| Sehr breite Fußzeile bei großer Schrift | Fußzeile darf zweizeilig werden; Sheets und `#mapControls` richten sich an ihrer *gemessenen* Höhe aus (CSS-Variable, in JS gesetzt), nicht an einem festen `4rem`. |

### Barrierefreiheit

- `<h1>` bleibt im Dokument (visuell versteckt via `clip-path`-Technik, **nicht**
  `display: none`).
- Suchfeld mit `aria-label` (R4). Alle Icon-Knöpfe mit `aria-label`, Emoji darin
  `aria-hidden="true"` (der Backlog-Punkt P3 „Emoji-Icons dekorativ auszeichnen"
  wird für die neuen Elemente gleich mit erfüllt).
- `aria-expanded`/`aria-controls` an beiden Sheet-Auslösern, `role="dialog"` +
  `aria-labelledby` am Sheet, Fokus rein und zurück, `Escape` schließt.
- `#count` bleibt `role="status"` + `aria-live="polite"`.
- Fokus-Ring auf allen Overlay-Elementen sichtbar (`:focus-visible`), nicht
  wegoptimiert — über Kacheln ist er die einzige Orientierung.
- Touch-Targets ≥ 44 px, auch der Griff und das ✕.

### Datenmodell / Persistenz / externe Abhängigkeiten

Nichts davon ändert sich: keine neue Spalte, kein neues JSON-Feld, kein
Pipeline-Lauf nötig, keine neue externe Abhängigkeit (Leaflet bleibt wie es ist,
kein npm, kein Build). Persistiert wird weiterhin ausschließlich in
URL-Query-Parametern, und dort nur die Filter (A-8).

### Testplan

Playwright mit `L`-Stub nach `CLAUDE.md` (`bindPopup` bekommt eine **Funktion**),
gegen synthetische Daten **und** die echte `web/restaurants.json`:

1. **Geometrie** bei 393 × 851 und 360 × 740: Bedienzeile ≤ 72 px,
   `#map` ≥ 95 % der Viewporthöhe, unverdeckte Karte ≥ 85 %.
2. **Touch-Targets**: jedes sichtbare interaktive Element in Bedienzeile, Sheets
   und `#mapControls` hat `getBoundingClientRect().height >= 44`.
3. **Attribution** (ODbL, harte Zeile): die Fußzeile ist sichtbar und enthält
   „OpenStreetMap-Mitwirkende" — auch bei **offenem** Sheet; die Rechtecke von
   Sheet und Fußzeile überschneiden sich nicht.
4. **Filter im Sheet**: Öffnen setzt `aria-expanded="true"`; ein Chip-Tipp
   ändert `window.__markers.length` sofort; die Zahl am Filter-Knopf, der Text in
   `#count` und `__markers.length` stimmen überein; `Escape` schließt und der
   Fokus liegt wieder auf dem Auslöser.
5. **Nur ein Sheet gleichzeitig**: Feed öffnen, während Filter offen ist →
   Filter ist `hidden`.
6. **Leerzustand**: mit `?delivery=1&open=1` zu einer Zeit ohne Treffer (bzw.
   synthetisch) erscheint `#empty` sichtbar unterhalb der Bedienzeile, und
   „Alle Restaurants zeigen" ist klickbar (nicht von einem Overlay verdeckt).
7. **Desktop 1024 × 768**: `#filterToggle` ist `hidden`, die drei Chips sind
   sichtbar, `#feed` verhält sich wie heute — der Umbau ist unter 640 px eingesperrt.
8. **Ungetaggte Felder degradieren**: mit der echten JSON zeigt kein Popup
   „undefined", `delivery === null` erscheint als „unbekannt".

**Was hier nicht prüfbar ist** (Netzpolitik der Web-Session blockt unpkg): das
Verhalten mit echtem Leaflet — Gesten über den Pillen, Auto-Pan-Padding,
Attribution-Control-Position. Das ist beim grünen Licht in einem echten Browser
gegenzuprüfen; das Strukturprinzip „Overlay ist Geschwister von `#map`" hält das
Risiko klein, beseitigt es aber nicht.

### Doku-/Backlog-Auswirkungen

- **`docs/BACKLOG.md`**: R2, R3, R4, P3 (Fußzeile zu klein), P3 (Fokus-Verwaltung
  im Feed-Panel) werden von A-3 mit erledigt — als Hinweis vermerkt, abgehakt
  wird erst bei der Umsetzung. R8 (der Pitch verschwindet) wird von Entscheidung 2
  und 4 überholt: auf Mobil verschwindet er absichtlich, der Stand wandert in die
  Fußzeile; der Punkt bleibt für Desktop offen. R11 und R14 sind **nicht** Teil
  dieses Umbaus.
- **`docs/UMGESETZT.md`**: Eintrag bei der Umsetzung.
- **`docs/anforderungen/README.md`**: Status, und A-3 als Wegbereiter von A-2 im
  Abhängigkeits-Bild.
- **`web/sw.js`**: ~~`CACHE_VERSION` `v2` → `v3`~~ → **`v3` → `v4`**
  ([ADR-006](../entscheidungen/ADR-006-pwa-network-first.md)), weil
  [A-4](./A-4-farbsystem.md) vorher `v3` setzt.
- **`docs/TECHNICAL.md`**: nicht betroffen (keine Pipeline-Änderung).
- Neu: [ADR-008](../entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md),
  Status `vorgeschlagen` → `akzeptiert` mit der Umsetzung.

## Definition of Done

- Bedienzeile ≤ 640 px ist **eine** Zeile, ≤ 72 px hoch; gemessen bei 393 × 851
  **und** 360 × 740, mit und ohne sichtbaren Install-Weg.
- `#map` füllt ≥ 95 % der Viewporthöhe, davon ≥ 85 % unverdeckt (heute 71,2 %
  bzw. 62,6 %).
- **Jedes** interaktive Element in Bedienzeile, Sheets und `#mapControls` ist
  ≥ 44 px hoch — inklusive Griff und ✕.
- **„© OpenStreetMap-Mitwirkende" ist in der Fußzeile sichtbar, auch bei
  geöffnetem Sheet** (Rechtecke überschneiden sich nicht). Pflicht unter der ODbL.
- Der Datenstand ist ohne Interaktion sichtbar (Fußzeile).
- `#count` bleibt `role="status"`/`aria-live` und stimmt mit der Zahl am
  Filter-Knopf **und** mit `window.__markers.length` überein.
- Beide Sheets: `aria-expanded` am Auslöser, `role="dialog"` +
  `aria-labelledby`, Fokus rein und zurück, `Escape` schließt, nie zwei
  gleichzeitig offen.
- `#empty` und „Alle Restaurants zeigen" sind bei 0 Treffern sichtbar und
  klickbar, von keinem Overlay verdeckt (ADR-007).
- `delivery === null` / `takeaway === null` erscheinen weiter als *unbekannt*,
  nie als *nein*.
- Über 640 px ist die Seite unverändert: Chips inline sichtbar,
  `#filterToggle` versteckt.
- Frontend im Browser gegengeprüft (Playwright mit `L`-Stub) mit synthetischen
  Daten **und** der echten `web/restaurants.json`; die Leaflet-Punkte aus dem
  Testplan zusätzlich in einem echten Browser.
- Keine Cookies, kein Tracking, kein `localStorage`, kein neuer
  URL-Parameter dazugekommen.
- `CACHE_VERSION` in `web/sw.js` hochgezählt.
- Kein Python berührt; `python3 -m unittest discover -s tests -v` läuft
  unverändert grün.

## Umsetzungsschritte

1. **Fundament, für sich testbar:** `height: 100dvh` mit `100vh`-Fallback (R2),
   `viewport-fit=cover` (R3), `aria-label` am Suchfeld (R4), Fußzeile auf
   0,8 rem (P3), Fußzeilenhöhe als CSS-Variable messen und setzen.
2. **`#filterPanel` einziehen**: die drei Chips, `#cuisine` und `#resetFilters` in
   einen gemeinsamen Container legen, ohne jede Verhaltensänderung. Desktop muss
   danach pixelgleich aussehen — das ist der Zwischenstand, gegen den alles
   Weitere abgegrenzt wird.
3. **Sheet-Mechanik** bauen (`openSheet()`, Griff, Wischen, Fokus, `Escape`,
   `prefers-reduced-motion`) und das bestehende `#feed` darauf umstellen —
   `setFeedOpen()` wird ein Aufruf von `openSheet("feed")`.
4. **Bedienzeile ≤ 640 px**: `header` zum transparenten Overlay, `h1`/`#meta`
   verstecken, `#filterToggle` mit Trefferzahl einführen, `updateCount()`
   einziehen, Feed-Knopf verschlanken, Install-Knopf und „Mehr"-Abschnitt ins
   Filter-Sheet.
5. **`#mapControls`** mit `#nearMe` unten rechts, Abstände gegen Fußzeile und
   Leaflet-Attribution; Auto-Pan-Padding an `bindPopup()` und in `focusPlace()`.
6. **Randfälle**: `#empty`-Abstand, `matchMedia`-Wechsel bei 640 px,
   `env(safe-area-inset-*)` für den Standalone-Modus, Banner-Platzierung.
7. **Tests** nach Testplan; `CACHE_VERSION` → `v4` (A-4 hat `v3` verbraucht).
8. **Doku**: ADR-008 auf `akzeptiert`, `UMGESETZT.md`, Backlog-Punkte abhaken,
   Status in der [Übersicht](./README.md#übersicht) auf 🏁.

---

## Ausgangstext (aus `backlog/IDEEN.md`, Idee 3)

> Der Header frisst 23 % des Bildschirms: Suche, zwei Checkboxen, zwei Buttons und
> die Trefferzahl konkurrieren gleichwertig über drei Zeilen, die Zahl landet per
> `margin-left: auto` als Waise neben „Diese Woche". Auf Mobil besser: eine Zeile
> (Suche + „Filter"-Knopf mit Trefferzahl), der Rest in ein Bottom Sheet. Nebenbei
> sind die Buttons ~34 px hoch – unter den empfohlenen 44 px Touch-Target.
>
> Gehört zusammen mit dem **Feed-Panel**, das auf Mobil fast die ganze Karte
> verdeckt: als Bottom Sheet mit Griff angenehmer als das schwebende Panel. Beides
> ist derselbe Umbau und sollte in einem Rutsch entworfen werden.

Der Ausgangstext beschreibt „zwei Checkboxen" — das ist der Stand vor
[A-1](./A-1-standardfilter-entschaerfen.md). Heute sind es drei Chips plus
Reset-Chip, also **mehr** Elemente in der Leiste, nicht weniger. Die „~34 px"
sind gemessen 32,4 px, und „drei Zeilen" sind je nach Breite vier oder fünf.

> Die Kürzel `R…`/`P…` stammen aus dem UI/UX-Review vom Juli 2026
> (Mobil-Screenshot, Android/Chrome, 1080 × 2340) und bleiben erhalten, damit
> Rückfragen zuordenbar sind.
