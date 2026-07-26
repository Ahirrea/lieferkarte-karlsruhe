# ADR-011: Pins tragen wieder keinen Zustand — zurück zum Leaflet-Standard-Icon

**Status:** akzeptiert
**Datum:** 2026-07-26

Kehrt [ADR-010](./ADR-010-pin-grammatik-lieferung-und-geschlossen.md) um, das
damit auf `ersetzt durch ADR-011` steht. Entscheidung der Produktverantwortung
nach Ansicht der Live-Karte, am selben Tag wie die Umsetzung von
[A-5](../anforderungen/A-5-pins-nach-zustand.md).

## Kontext

ADR-010 hat die Pins am 2026-07-26 zu SVG-Kreisen gemacht, die zwei Achsen
tragen: Farbe + Strichart = Lieferung, Größe + Füllstärke = sicher geschlossen.
Die Entscheidung war sorgfältig begründet und messtechnisch sauberer als ihr
Ausgangstext — sie hat trotzdem eine Frage nicht beantwortet, die kein Kontrast-
und kein Abdeckungswert beantworten kann: **wie die Karte aussieht.**

Die Produktverantwortung hat die Karte auf dem Telefon angesehen und die neuen
Pins abgelehnt: die dunkelgrün gefüllten Kreise wirken schwerer und
unruhiger als der vertraute blaue Leaflet-Tropfen. Das ist ein Geschmacks- und
Markenurteil, kein Messfehler — und es fällt in ihre Zuständigkeit.

Zwei Befunde geben dem Urteil zusätzlich Gewicht, weil sie schon in ADR-010
selbst stehen:

| Befund | Zahl (gemessen 2026-07-26) |
|---|---|
| **Im Standardbild ist die Grammatik wirkungslos.** „Liefert jetzt" filtert genau auf „liefert **und** offen" — jeder sichtbare Pin ist damit zwangsläufig gleich: grün, volle Größe. | **53 von 885** sichtbar, davon 53 identisch |
| **Aufgeweitet besteht die Karte fast nur aus „unbekannt".** Der Farbcode sagt dann überwiegend „dazu ist nichts eingetragen". | **774 von 885** grau gestrichelt (87,5 %) |

Der optische Preis wird also in dem Bild bezahlt, in dem der Nutzen genau null
ist, und der Nutzen zeigt sich in einem Bild, das zu 87,5 % aus Nichtwissen
besteht. ADR-010 hat beides benannt und in Kauf genommen; diese Abwägung wird
hier anders entschieden.

## Entscheidung

Ein Restaurant-Pin ist wieder **Leaflets Standard-Icon** (`L.marker`) und trägt
**keinen** Zustand: keine Farbe, keine Größenabstufung, keine Strichart, keine
Legende. Die Zustände Lieferung, Abholung und „jetzt geöffnet" stehen dort, wo
sie vor A-5 standen — in **Popup, Badges, Chips und Filtern**.

Die Pin-Achsen sind damit nicht „frei", sondern **geschlossen**: sie wieder zu
belegen — ganz oder in Teilen, farbig oder nur über die Größe — braucht einen
**neuen ADR**, keinen Feinschliff an `render()`.

## Begründung

**Das Standardbild ist das Produkt.** Jeder Aufruf beginnt im Standardfilter
([ADR-007](./ADR-007-standardfilter-liefert-jetzt.md)) — nur ein geteilter Link
mit Parametern tut es nicht — und dort trägt die Grammatik nachweislich keine
Information: 53 gleiche Pins. (Wie viele Nutzer die Filter danach aufweiten,
weiß das Projekt nicht und soll es nicht wissen: keine Analytik, keine
Messung am Nutzer. Argumentiert wird deshalb mit dem, was feststeht — dem
Bild beim Öffnen.) Eine
Gestaltung, die im Hauptbild nichts leistet und dort trotzdem als schlechter
empfunden wird, verliert diese Abwägung — unabhängig davon, wie gut sie im
Randbild funktioniert.

**Es gibt keine Barrierefreiheits-Regression.** Das ist der Grund, warum diese
Rücknahme überhaupt zulässig ist: alles, was der Pin gesagt hat, sagen Popup,
Badges und Filter weiter, und zwar **in Worten**. Die Regeln aus
[ADR-009](./ADR-009-farbrollen-marke-aktion-zustand.md) (Farbrollen, „unbekannt"
trennt sich über die Form) und [ADR-007](./ADR-007-standardfilter-liefert-jetzt.md)
(„unbekannt" ist keine Absage) gelten unverändert weiter — sie betreffen Badges
und Chips, nicht die Pins. Verloren geht genau eine Eigenschaft: **ohne Antippen
sichtbar** (Befund R13). Dieser Befund ist damit wieder offen, und das steht so
in A-5 und in der Anforderungsübersicht.

**Der bessere Weg zu R13 ist Text, nicht Farbe.** Ein 20-px-Punkt hat vier
Kanäle, eine Liste hat beliebig viele Worte.
[A-2](../anforderungen/A-2-ergebnisliste.md) (Ergebnisliste) löst „Zustand ohne
Antippen sehen" für Auge, Tastatur **und** Screenreader gleichzeitig — die Karte
ist für Screenreader ohnehin leer, farbige Kreise ändern daran nichts. A-2 ist
die nächste Verfeinerung; R13 wandert damit dorthin, statt zu verschwinden.

**Die technischen Gewinne aus A-5 bleiben.** Zurückgenommen wird nur das
Aussehen. Der einmal gebaute `Intl.DateTimeFormat` (gemessen 62,9 → 5,6 ms über
885 Auswertungen) und die Zeitauswertung **hinter** den billigen Filtern bleiben
— letztere jetzt zusätzlich kurzgeschlossen, weil nur noch der Filter das
Ergebnis braucht und nicht mehr jeder Pin. `render()` liegt im Standardfilter bei
**0,60 ms** (Median von 20 gewärmten Läufen), gegenüber 0,8 ms mit den
Zustands-Pins und 4,2 ms davor.

## Verworfene Alternativen

- **Kreise behalten, aber alle in einer neutralen Farbe:** hätte die
  Farbcodierung entfernt, aber nicht das, was beanstandet wurde — die
  Kreisoptik selbst. Ausdrücklich von der Produktverantwortung abgewählt.
- **Nur die Farbachse entfernen, „jetzt geschlossen" (kleiner + blasser)
  behalten:** im Standardbild unsichtbar (dort ist alles offen), behält aber die
  Kreisform. Beides zusammen heißt: voller Preis, kein Nutzen.
- **Nur die Größenachse entfernen, Farbe behalten:** ändert am beanstandeten
  Bild praktisch nichts, dort sind ohnehin alle Pins gleich grün.
- **Farbe erst zeigen, wenn die Filter aufgeweitet sind:** hätte den Nutzen
  genau dort gelassen, wo er entsteht — aber ein Pin, dessen Bedeutung vom
  Filterzustand abhängt, ist in keiner Legende erklärbar und widerspricht
  „Karte und Popup sagen dasselbe".
- **`L.circleMarker` mit Tropfen-Silhouette per SVG-Pfad:** hätte Optik und
  Vektorvorteil vereint, ist aber eigenes Pfad-Markup samt Anker- und
  Schatten-Nachbau — viel Aufwand für einen Nachbau dessen, was Leaflet
  mitliefert.
- **Nichts tun und auf Gewöhnung setzen:** die Beanstandung kam nach Ansicht der
  echten Karte, nicht aus einem Entwurf. Sie auszusitzen wäre keine Entscheidung,
  sondern deren Verweigerung.

## Konsequenzen

- **Befund R13 ist wieder offen** („Zustand nur nach Antippen sichtbar"). Er
  wird nicht erneut über die Pins gelöst, sondern über
  [A-2](../anforderungen/A-2-ergebnisliste.md).
- **A-5 ist `🗑 verworfen`**, nicht `🏁` — umgesetzt und am selben Tag
  zurückgenommen. Die Datei bleibt liegen: sie ist das Protokoll der Messungen
  (64/47/774, 427/248/210, die Kontrastwerte), und die sind weiter gültig und
  wiederverwendbar, auch wenn die Lösung es nicht ist.
- **Die drei Leaflet-Marker-Grafiken sind wieder im Service-Worker-Cache**
  (`marker-icon.png`, `-2x`, `-shadow`). Sie **müssen** dort stehen: ohne sie
  wäre die Karte offline pinlos, weil die `cacheFirst`-Regel für unpkg sie erst
  online nachholt. `CACHE_VERSION` steht auf `v6`.
- **A-6 (Clustering/Canvas) wird wieder teurer.** Mit Vektor-Pins war es
  `preferCanvas: true`; mit `L.marker` sind es wieder 885 DOM-Knoten und echtes
  Clustering. Bleibt „nice to have", weil der Default eng ist (53 Marker).
- **Die Trefferfläche wächst zurück** auf 25 × 41 px statt 20 px (14 px bei
  geschlossenen). Nebenwirkung zugunsten der Bedienbarkeit — auf Kosten der
  Klick-Konkurrenz bei aufgeweiteten Filtern, die ADR-010 vermeiden wollte.
- **Der Standort-Marker ist wieder ein Punkt** (`L.circleMarker`, Radius 8,
  Füllung 0,6, `--marke`). Zulässig, weil die Restaurants wieder Tropfen sind:
  Kreis gegen Tropfen ist ein **Form**unterschied und trägt auch ohne
  Farbwahrnehmung. Wären die Restaurants je wieder Kreise, müsste er erneut
  wechseln — der Grund steht in ADR-010.
- **`cssVar()` bleibt, `pinTokens()` fällt weg.** Von den Fallback-Kopien in
  JavaScript bleibt nur die eine für `--marke` in `locateMe()`. Die
  `--zustand-*`-Tokens leben weiter, aber ausschließlich in CSS (Badges) — eine
  Änderung in `:root` kann dort nicht mehr stumm auf einen alten JS-Wert
  zurückfallen.
- **Was jetzt nicht passieren darf:** die Pins wieder einzufärben, zu verkleinern
  oder zu stricheln, ohne neuen ADR. Dieselbe Bremse, die ADR-010 für eine
  *dritte* Achse gesetzt hat, gilt jetzt für die *erste*.
