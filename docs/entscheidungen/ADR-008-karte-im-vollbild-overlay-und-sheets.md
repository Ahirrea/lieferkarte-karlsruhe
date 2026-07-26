# ADR-008: Karte im Vollbild — Bedienung als Overlay und Bottom Sheets

**Status:** akzeptiert
**Datum:** 2026-07-25

Mit der Umsetzung von [A-3](../anforderungen/A-3-header-umbau.md) am 2026-07-26
von `vorgeschlagen` auf `akzeptiert` gesetzt — die beschriebene Oberfläche
existiert seitdem.

## Kontext

Auf dem Handy war die Bedienleiste größer als geplant und wuchs mit jeder
Funktion weiter. Gemessen (Playwright mit `L`-Stub, echte `web/restaurants.json`,
883 Restaurants, Standardfilter aktiv):

| Viewport | Header | Anteil | Karte |
|---|---|---|---|
| 393 × 851 | 203,7 px | 23,9 % | 605,5 px (71,2 %) |
| 393 × 851, mit Install-Knopf | 220,1 px | 25,9 % | — |
| 360 × 740, mit Install-Knopf | 259,1 px | **35,0 %** | 463,1 px (62,6 %) |

Die Ursache ist strukturell, nicht kosmetisch: `.controls` ist ein
`flex-wrap`-Container, in dem Suche, drei Filter-Chips, Reset-Chip, „In meiner
Nähe", „Diese Woche", der Install-Knopf und die Trefferzahl **gleichwertig**
konkurrieren. Jede neue Funktion kostet eine weitere Zeile — und
[A-1](../anforderungen/A-1-standardfilter-entschaerfen.md) hat gerade zwei
Checkboxen zu vier Chips gemacht. Dazu ist jedes Element 32,4 px hoch, also unter
dem empfohlenen 44-px-Touch-Target.

Dasselbe Muster beim Änderungs-Feed: das schwebende Panel verdeckt 77 % (393 px)
bzw. 88 % (360 px) der Kartenhöhe. Sein `bottom: 4rem` unter 640 px existiert
schon aus genau einem Grund — die Fußzeile mit der ODbL-Pflichtangabe darf nicht
darunter verschwinden.

Dahinter steht eine Grundsatzfrage, die über die eine Leiste hinausreicht:
**Ist das eine Seite mit einer Karte darauf oder eine Karten-App?** Eine Seite
stellt Kopf, Inhalt und Fuß untereinander. Eine Karten-App zeigt die Karte und
legt die Bedienung darüber.

## Entscheidung

Unter 640 px ist die Karte das Vollbild. Die Bedienung liegt als Overlay darüber:
eine Zeile mit Suche, Filter-Knopf (samt Trefferzahl) und Feed-Knopf, ein
Standort-Knopf unten rechts auf der Karte, und alles Weitere in **Bottom Sheets**
mit gemeinsamer Mechanik. Über 640 px bleibt der bisherige Aufbau.

Zwei Dinge sind Teil der Entscheidung und nicht verhandelbar:

1. **„Ohne Header" heißt nicht „ohne Fußzeile".** Die `<footer>` mit
   „© OpenStreetMap-Mitwirkende" bleibt im Fluss, und jedes Sheet endet oberhalb
   von ihr. Vollbild endet dort, wo die Attribution beginnt.
2. **Overlay-Elemente sind Geschwister von `#map`, niemals Kinder.** Nur so
   erreichen ihre Pointer-Events Leaflet nicht.

## Begründung

Vollbild ist das erwartete Muster für Kartenanwendungen. Wer die Seite auf dem
Handy öffnet, vergleicht sie nicht mit ihrer Vorversion, sondern mit den
Karten-Apps, die er kennt — und dort läuft die Karte unter der Suchleiste durch.

Der Gewinn ist ausdrücklich **nicht** primär in Pixeln zu messen, und das gehört
ins Protokoll: gegenüber der empfohlenen Alternative (eine Ein-Zeilen-Kopfzeile
im normalen Fluss) bringt das Overlay auf 393 × 851 rund **12 px mehr sichtbare
Kachelfläche und 5 px weniger unverdeckte Karte** — beide Wege sparen gegenüber
heute etwa 140 px (16,5 %). Der Unterschied zwischen ihnen ist optisch, nicht
funktional. Diese Zahlen wurden vorgelegt; die Produktverantwortung hat sich
bewusst für das Overlay entschieden, weil die Seite wie eine Karte wirken soll
und nicht wie ein Formular mit Karte darunter.

Die drei Risiken des Overlays sind damit übernommen und konstruktiv aufgelöst,
nicht weggeredet:

- **Kontrast über beliebigen Kacheln** → alle Overlay-Elemente haben einen
  deckenden Panel-Hintergrund; kein Text liegt direkt auf Kacheln.
- **Marker im obersten Streifen nicht antippbar** → Popups öffnen mit
  Auto-Pan-Padding, das die Zeilenhöhe kennt.
- **Gesten-Konflikte mit Leaflet** → gelöst durch die Struktur (Geschwister von
  `#map`, nicht Kinder), nicht durch `disableClickPropagation`. Das hat den
  Nebeneffekt, dass die Frontend-Tests mit dem `L`-Stub aus `CLAUDE.md` weiter
  funktionieren, der kein `DomEvent` kennt.

Die Beschränkung auf ≤ 640 px ist Absicht: am Desktop ist der Header mit 13,6 %
kein Problem, und direkt anklickbare Filter-Chips sind dort besser als ein Klick
mehr für alles. Platznot ist die Begründung für den Umbau — wo sie fehlt, fehlt
auch der Grund.

## Verworfene Alternativen

- **Ein-Zeilen-Kopfzeile im Fluss + zwei Sheets** (die Empfehlung aus A-3):
  funktional gleichwertig bis minimal besser, ohne Overlay-Risiken — verworfen,
  weil das Ergebnis weiter wie eine Seite mit Karte aussieht statt wie eine Karte.
- **Nur den Header verdichten, kein Sheet** (`<details>` zum Aufklappen): löst
  das Feed-Panel-Problem (77–88 % Verdeckung) nicht und schiebt beim Aufklappen
  die Karte nach unten.
- **Ein Sheet mit Tabs** („Filter" | „Diese Woche" | später „Liste"): eine
  Navigationsebene mehr, und der Zähler neuer Restaurants müsste durch den Tab
  hindurch sichtbar bleiben.
- **Attribution ins Overlay statt in eine Fußzeile**: sie wäre bei offenem Sheet
  verdeckbar. Unter der ODbL ist das kein Gestaltungsspielraum
  ([ADR-001](./ADR-001-openstreetmap-statt-google-places.md)).
- **Sheets mit mehreren Rastpunkten** (peek/halb/voll): Trägheits-Physik von Hand
  in einem Projekt ohne Build-Schritt — der Ertrag rechtfertigt das nicht.
- **Sheet-Zustand in der URL oder im `localStorage`**: `localStorage` ist ein
  hartes Nicht-Ziel; ein URL-Parameter würde geteilte Links auf ein offenes
  Filterpanel statt auf die Karte öffnen lassen.
- **Modale Sheets mit Scrim und Fokus-Käfig**: die Filter wirken sofort, man
  *soll* die Karte dahinter sehen. Ein Scrim würde die Rückmeldung verdecken, die
  das Sheet gerade auslöst.

## Konsequenzen

- **Die Fußzeile mit „© OpenStreetMap-Mitwirkende" ist ab jetzt ein
  Struktur-Element, kein Zierrat.** Kein Overlay, kein Sheet, kein Karten-Control
  darf sie verdecken; das ist eine Prüfzeile im Test, nicht eine Absicht.
- **`100dvh` und `viewport-fit=cover` sind Voraussetzung, nicht Feinschliff.**
  Mit `100vh` liegen auf Android Chrome Fußzeile und untere Controls unter der
  URL-Leiste — beim alten Header war das ein Schönheitsfehler, beim Overlay ist
  es ein Lizenzproblem.
- **Neue Bedienelemente gehören ab jetzt ins Sheet, nicht in die Zeile.** Die
  Zeile ist auf drei Elemente fest; sie darf nicht wieder zum Wachstumsort
  werden. Genau daran ist der alte Header gescheitert.
- **Die Sheet-Mechanik ist geteilte Infrastruktur.** Filter und Feed sind ihre
  ersten beiden Nutzer, die Ergebnisliste aus
  [A-2](../anforderungen/A-2-ergebnisliste.md) wird der dritte — sie braucht
  keinen eigenen Panel-Entwurf mehr.
- Es gibt unter/über 640 px **zwei Layout-Pfade**. Jede künftige UI-Änderung ist
  in beiden zu prüfen; der Testplan von A-3 hat dafür einen festen Desktop-Punkt.
- `header` darf niemals `transform`, `filter` oder `will-change` bekommen — sonst
  wird es zum Containing Block und die `position: fixed`-Sheets richten sich an
  ihm statt am Viewport aus.
- Kehrt sich „die Karte ist das Vollbild" jemals um, braucht das einen neuen ADR
  — nicht eine stille Änderung der Media-Query.
