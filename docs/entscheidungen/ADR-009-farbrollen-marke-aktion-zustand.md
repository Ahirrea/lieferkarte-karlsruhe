# ADR-009: Farbrollen getrennt — Marke, Interaktion, Zustand

**Status:** vorgeschlagen
**Datum:** 2026-07-25

Wird mit der Umsetzung von
[A-4](../anforderungen/A-4-farbsystem.md) auf `akzeptiert` gesetzt. Die
Entscheidung selbst ist getroffen; sie steht als `vorgeschlagen`, solange der
beschriebene Token-Satz noch nicht existiert.

## Kontext

Das Farbsystem der Karte war nie entworfen, es ist gewachsen. Gemessen am
2026-07-25 gegen `web/index.html`:

| Befund | Zahl |
|---|---|
| Rollen, die `--accent` gleichzeitig trägt | **5** (Marke, Interaktion, aktiver Steuerzustand, Datenzustand, Melde-Flag) |
| CSS-Stellen mit `var(--accent)` | 15 |
| weitere doppelt belegte Tokens | `--ok` (Fähigkeit „liefert" *und* Zustand „geöffnet"), `--muted` (sekundärer Text *und* „unbekannt") |
| rohe Hex-Werte außerhalb von `:root` | 16, dazu 2 `rgba()`-Schatten |
| Farbpaare unter 4,5:1 für kleinen Text | **8 von 15**, darunter alle vier Zustands-Badges (3,62–3,76:1) |

Zwei Kräfte machten das zum Problem statt zur Kosmetik.

**Erstens ist keine Farbe für „Zustand" frei.**
[A-5](../anforderungen/A-5-pins-nach-zustand.md) will Pins nach liefert /
holt ab / gerade geschlossen unterscheiden. Solange „geschlossen" und Markenfarbe
derselbe Wert `#d64541` sind, lässt sich das nicht ausdrücken — ein roter Pin
hieße gleichzeitig „geschlossen" und „das ist unsere Farbe". Das ist der
ursprüngliche Befund R12 aus dem UI/UX-Review vom Juli 2026.

**Zweitens trägt Farbton allein die Information nicht.** Rot `#d64541` und Grün
`#2e8b4f` haben zueinander einen Helligkeitskontrast von **1,03** — sie sind
nahezu gleich hell. Bei Rot-Grün-Blindheit (rund 8 % der Männer) ist die
Unterscheidung damit nicht nur schwer, sondern unmöglich, weil kein
Helligkeitsunterschied als Rückfallebene bleibt. Ein Zustandssatz, der nur den
Farbton variiert, wäre für diese Gruppe wertlos — egal wie sorgfältig die
Farbtöne gewählt sind.

Dazu kommt eine dritte, leisere Kraft: `prefers-color-scheme: dark` steht als
P3 im [Backlog](../BACKLOG.md). Solange Farbwerte über 15 Regeln verstreut sind,
ist Dark Mode eine Suche durch die ganze Datei statt ein `@media`-Block.

## Entscheidung

Farbe bekommt **drei getrennte Rollen** mit je eigenem Token-Satz, und keine
Rolle borgt sich die Farbe einer anderen:

1. **Marke** — `--marke: #d64541`, unverändert. Gilt für PWA-Icons,
   `manifest.theme_color`, die `theme-color`-Metas und das Markenwort in der
   Überschrift. **Nie für einen Zustand.**
2. **Interaktion** — `--aktion: #b8352f` (+ `--aktion-hover`,
   `--aktion-schwach`). Links, Knöpfe, aktive Filter-Chips, Melde-Flag. Dieselbe
   Rot-Familie eine Stufe dunkler, weil Weiß auf `--marke` nur 4,39:1 erreicht,
   auf `--aktion` 5,85:1.
3. **Datenzustand** — `--zustand-ja` / `--zustand-nein` / `--zustand-unbekannt`,
   je mit Flächenfarbe. „nein" ist **Slate `#33333b`, nicht Rot**.

Dazu vier bindende Regeln:

- **Kein Farbwert außerhalb von `:root`.** Jede CSS-Regel benutzt `var()`. Die
  einzigen Ausnahmen sind die `theme-color`-Metas und `manifest.webmanifest`,
  weil dort kein `var()` möglich ist.
- **Farbe trägt den Zustand, das Symbol trägt die Fähigkeit.** „🥡 Abholung" ist
  ein *Ja* und wird grün wie „✔ Lieferservice"; unterschieden werden sie durch
  Symbol und Text. Blau als „Abholung"-Farbe entfällt.
- **Ein Zustand wird nie allein über Farbe codiert.** Zu jeder Zustandsfarbe
  gehört ein Symbol, eine Form oder Text. Auch nach der Umstellung liegt der
  Helligkeitsabstand „ja" gegen „nein" nur bei 1,92 — besser als 1,03, aber
  keine tragfähige Einzelcodierung.
- **„unbekannt" trennt sich von „nein" über die Form, nicht über den Farbton.**
  „nein" ist gefüllt, „unbekannt" ist ein gestrichelter Umriss ohne Füllung.

## Begründung

**Die Marke behält das Rot, weil der Zustand es billiger abgeben kann.**
`#d64541` steckt in den generierten PWA-Icons, in `manifest.theme_color`, in drei
`theme-color`-Metas und in `tools/make_icons.py`. Die Marke zu verschieben hieße
Icons neu erzeugen und den von `tests/test_pwa.py` geprüften Gleichlauf
Manifest ↔ Meta mitziehen — für R12 ohne jeden Zusatznutzen, denn die
Verwechslung löst sich genauso auf, wenn der Zustand die Farbe wechselt.

**Slate statt eines dunkleren Rots, weil die Zahlen es entscheiden.** Slate
`#33333b` hat zu Grün `#1d6b3a` einen Helligkeitsabstand von 1,92; ein dunkleres
Rot `#a3302c` nur 1,07 — praktisch der heutige, unbrauchbare Wert. Und Marke-Rot
gegen ein Zustands-Rot läge bei 1,59: R12 wäre gemildert statt gelöst. Slate
kostet die gewohnte Signalfarbe für „geschlossen" — dafür bleibt die Aussage
auch ohne Farbwahrnehmung erhalten, und das wiegt mehr.

**Die Rollentrennung ist mehr als eine Umbenennung.** Ein Token-Satz, der nur die
drei Zustandsstellen abspaltet, hätte A-5 ebenfalls entblockt — aber `--accent`
weiter zwischen Marke, Interaktion und Steuerzustand geteilt gelassen. Beim
nächsten Element, das eine dieser drei Bedeutungen braucht, wäre dieselbe
Anforderung erneut fällig. Die Rolle muss am Tokennamen ablesbar sein, sonst
wächst die Mehrfachbelegung nach.

**Die Kontrastkorrekturen gehören in denselben Schritt.** Die Werte werden
ohnehin angefasst; ein zweiter Durchgang kostet dasselbe nochmal, und A-5 würde
die fehlerhaften Werte erben. Preis: Badges und Links werden sichtbar dunkler.

## Verworfene Alternativen

- **Nur die Zustandsfarbe abspalten** (~6 CSS-Zeilen): entblockt A-5, lässt aber
  vier Rollen auf `--accent` und 16 rohe Hex-Werte stehen — dieselbe Anforderung
  kommt wieder.
- **Zweischichtiges Token-System** (Palette `--rot-600` → Rolle
  `--zustand-nein`) samt Dark Mode: in einem Ein-Datei-Projekt ohne Build-Schritt
  eine Indirektion zu viel, und es zieht Dark Mode herein, den
  [ADR-008](./ADR-008-karte-im-vollbild-overlay-und-sheets.md) ausdrücklich
  ausschließt.
- **Zustand behält Rot, Marke wird neu**: semantisch am saubersten, aber die
  teuersten Folgekosten (Icons, Manifest, drei Metas, `make_icons.py`) für ein
  Ergebnis, das die Zustandstrennung nicht besser macht.
- **Zustand wird ein dunkleres Rot**: löst R12 nur halb (1,59 zur Marke) und
  lässt das Rot-Grün-Problem unangetastet.
- **Dark Mode gleich mitbauen**: zwei Farbumbauten in einem Schritt sind nicht
  sauber gegenprüfbar. Nach dieser Entscheidung ist Dark Mode ein `@media`-Block
  über `:root` — die Vorbereitung ist der Wert, nicht die Ausführung.

## Konsequenzen

- **`--accent` und `--ok` existieren nicht mehr.** Wer sie in einem Patch
  wiedersieht, hat einen Rückschritt vor sich. Ein übersehenes `var(--accent)`
  fällt im Browser stumm auf `initial` zurück — die Umstellung muss vollständig
  sein, eine `grep`-Prüfung gehört in die Definition of Done.
- **Neue Farben brauchen zuerst eine Rolle.** Eine Farbe ohne Rolle bekommt kein
  Token, und ein Token gehört in `:root` — nicht in die Regel, die es braucht.
  Kein Element darf sich die Markenfarbe für einen Zustand borgen und umgekehrt.
- **A-5 ist an die Zustandstokens gebunden.** Pins dürfen ausschließlich den
  `--zustand-*`-Satz verwenden, und Farbe allein darf den Pin-Zustand nicht
  tragen — Form oder Symbol muss mit. Blau als „Abholung"-Farbe ist verbraucht.
- **A-3 baut auf diesem Satz auf**, nicht daneben: A-4 wird zuerst umgesetzt,
  A-3 übernimmt die Tokens und rückt bei `CACHE_VERSION` auf `v4`.
- **Zwei grüne Badges nebeneinander** sind ab jetzt normal (liefert *und* holt
  ab — aktuell 47 Restaurants). Wer das für einen Fehler hält, liest die Regel
  „Farbe trägt den Zustand" gegen ihre Absicht.
- **Der häufigste Zustand ist „unbekannt"** — 87,5 % bei Lieferung, 72,3 % bei
  Abholung. Seine Darstellung ist deshalb kein Randfall, sondern der
  Hauptfall, und
  [ADR-007](./ADR-007-standardfilter-liefert-jetzt.md) bleibt bindend: nie wie
  ein „nein". Die Formtrennung (gefüllt gegen gestrichelten Umriss) ist der
  Mechanismus dafür und darf nicht zu „beide grau, aber verschieden getönt"
  vereinfacht werden.
- **Die Markenfarbe ist an drei Orten gekoppelt** (`--marke`, `theme-color`-Metas
  + `manifest.theme_color`, `ACCENT` in `tools/make_icons.py`). Sie zu ändern ist
  ab jetzt eine Vier-Dateien-Änderung plus Icon-Neugenerierung — das ist gewollt
  als Bremse.
