# ADR-010: Pin-Grammatik — Farbe trägt die Lieferung, Größe das „jetzt geschlossen"

**Status:** akzeptiert
**Datum:** 2026-07-26

Mit der Umsetzung von [A-5](../anforderungen/A-5-pins-nach-zustand.md) am
2026-07-26 gebaut und direkt auf `akzeptiert` gesetzt.

## Kontext

Bis heute war jeder Marker das blaue Leaflet-Standard-Icon: **885 identische
Tropfen**. Ob ein Restaurant liefert, abholen lässt oder gerade geschlossen ist,
stand ausschließlich im Popup — sichtbar erst nach dem Antippen. Das ist der
Befund R13 aus dem UI/UX-Review vom Juli 2026.

[ADR-009](./ADR-009-farbrollen-marke-aktion-zustand.md) hat die Voraussetzung
geschaffen (`--zustand-ja` / `-nein` / `-unbekannt`, dazu `cssVar()`) und
gleichzeitig drei Regeln gesetzt, die den Lösungsraum eng machen: Pins dürfen
nur diesen Satz benutzen, Farbe allein darf nie einen Zustand tragen (der
Helligkeitsabstand ja/nein liegt bei 1,92), und „unbekannt" trennt sich von
„nein" über die **Form**, nicht über den Farbton.

Vier Kräfte haben die Entscheidung geformt. Alle Zahlen sind am 2026-07-26 gegen
`data/restaurants.db` und die echte `web/restaurants.json` gemessen (885 aktive
Restaurants):

| Kraft | Befund |
|---|---|
| **Ein Pin hat wenige Kanäle** | Farbe, Füllung, Strichart, Größe. Mehr geht auf 20 px nicht — jede Achse, die man belegt, ist für die nächste weg. |
| **„unbekannt" ist der Hauptfall** | Lieferung 64 ja / 47 nein / **774 unbekannt** (87,5 %), Abholung 238 / 8 / 639. Bei 609 Restaurants (68,8 %) ist **beides** ungetaggt. |
| **Öffnungszeiten sind lückenhaft** | 427 sicher offen, 248 sicher geschlossen, **210 nicht auswertbar** (143 ohne `opening_hours`, 67 mit unklarem Format). |
| **Der Untergrund ist beliebig** | Ein Pin liegt auf hellen Straßen, Parkgrün, Wasser oder Gebäudeflächen. Für grafische Objekte gilt 3:1 (WCAG 1.4.11). |

## Entscheidung

Der Pin ist ein **SVG-Kreis** (`L.circleMarker`) und trägt genau **zwei
Achsen** — nicht mehr:

| Achse | Kanal | Werte |
|---|---|---|
| **Lieferung** | Farbe **und** Strichart | `--zustand-ja` gefüllt · `--zustand-nein` gefüllt · `--zustand-unbekannt` mit **gestricheltem** Umriss |
| **jetzt geschlossen** | Größe **und** Füllstärke | Radius 10 → 7 px, Füllung 0,85 → 0,2. Der **Umriss bleibt voll deckend.** |

Dazu drei bindende Festlegungen:

- **Abgewertet wird nur, was sicher geschlossen ist.** Die 210 Restaurants mit
  unklaren oder fehlenden Zeiten sehen aus wie die offenen. Der Pin behauptet
  damit nie „offen", nur „nicht bekannt zu".
- **Abholung steht nicht auf dem Pin.** Sie behält Chip, Badge und Popup.
- **Eine Legende ist Pflicht**, und sie wird aus **derselben** Funktion erzeugt
  wie die Pins (`pinStyle()` → `pinSwatch()`), damit Karte und Erklärung nicht
  auseinanderlaufen können.

## Begründung

**Die Farbe trägt die Lieferung, nicht „Lieferung oder Abholung".** Die
Sammelachse wäre optisch attraktiver — 258 grüne statt 64, also 29 % statt
12,5 % unterscheidbare Pins. Aber **194 dieser 258 liefern nicht**, sie lassen
nur abholen. Auf einer Karte, die „Lieferkarte" heißt und deren Standardfilter
„Liefert jetzt" ist, würde Grün dann das Falsche sagen — und zwar dreiviertel
der Zeit. Ein Pin, der drei von vier Mal in die Irre führt, ist schlechter als
einer, der zugibt, nichts zu wissen. Die 774 grauen, gestrichelten Pins sind
kein Schönheitsfehler, sondern der ehrliche Zustand der OSM-Abdeckung — dieselbe
Aussage, die schon der Leerzustand und die Filter-Hinweise machen.

**„Blass = geschlossen" — die Idee aus dem Ausgangstext — funktioniert nur
halb.** Sie zielt richtig (Helligkeit statt Farbton, also auch bei
Rot-Grün-Blindheit lesbar), aber reine Deckkraft reißt den Kontrast:
`--zustand-ja` bei 60 % auf einer hellen Kachel erreicht **2,59:1**, bei 70 %
auf Parkgrün 2,75:1 — beides unter den geforderten 3:1. Deshalb bleibt der
**Umriss voll deckend** (gemessen: `--zustand-ja` 4,07–6,53:1, über alle drei
Zustandsfarben 3,32–12,52:1, schlechtester Fall „unbekannt" auf Wasser) und
blass wird nur die Füllung. Die zweite Hälfte der Aussage trägt die **Größe** —
ein Kanal, der überhaupt keinen Kontrast kostet.

**Nur sicher geschlossen wird abgewertet**, weil
[ADR-007](./ADR-007-standardfilter-liefert-jetzt.md) bindend bleibt: 210
Restaurants mit unklaren Zeiten kleiner und blasser zu zeichnen hieße, ein
„unbekannt" als Absage darzustellen. Das ist derselbe Fehler, den die Badges
schon nicht machen (bei `null` erscheint gar kein Öffnungs-Badge).

**`L.circleMarker` statt `L.divIcon`.** Der gestrichelte Umriss — der Mechanismus,
mit dem sich „unbekannt" von „nein" trennt — ist in SVG ein Attribut
(`dashArray`) und kostet nichts. Ein `divIcon` bräuchte dafür eigenes Markup,
erzeugt 885 DOM-Knoten statt 885 Pfade und macht aus
[A-6](../anforderungen/A-6-clustering-oder-canvas.md) (Canvas-Renderer) wieder
eine große Sache. Mit Vektor-Pins ist A-6 künftig `preferCanvas: true` — eine
Zeile.

**Die Legende ist kein Beiwerk.** Ein Farbcode, den man nur durch Antippen
lernt, ist Dekoration — und Antippen war genau das, was A-5 abschaffen soll. Sie
steht im Filter-Sheet (unter 640 px) bzw. als eigene Zeile in der Bedienzeile
(darüber): ein Knoten, beide Pfade, und die Drei-Elemente-Regel der Bedienzeile
aus [ADR-008](./ADR-008-karte-im-vollbild-overlay-und-sheets.md) bleibt heil.

## Verworfene Alternativen

- **Farbe = „Lieferung oder Abholung"** (258/18/609): mehr Unterscheidung, aber
  194 der grünen Pins liefern nicht. Auf einer Lieferkarte ist das die teurere
  Lüge.
- **Symbol im Pin** (🚴 / 🥡 per `divIcon`): würde die Fähigkeitsachse mitnehmen,
  aber Emoji sind mehrfarbig (die Farbrollen aus ADR-009 wären hinfällig), bei
  20 px unlesbar und plattformabhängig — dazu 885 DOM-Knoten.
- **Dreistufige Öffnungsachse** (offen / zu / unbekannt): 3 × 3 = neun
  Pin-Varianten und eine Legende, die niemand mehr liest.
- **Reine Deckkraft für „geschlossen"**: gemessen 2,59:1, unter der 3:1-Grenze.
- **Keine Legende**: spart eine Zeile Bedienfläche und macht den ganzen Rest
  wertlos.
- **Karten-Overlay für die Legende**: kostet dauerhaft Kartenfläche — genau das,
  was [ADR-008](./ADR-008-karte-im-vollbild-overlay-und-sheets.md) gerade
  zurückgewonnen hat.

## Konsequenzen

- **Der Pin ist jetzt voll.** Zwei Achsen sind belegt; eine dritte (Abholung,
  Küchenstil, Preis …) braucht einen **neuen ADR**, keinen Feinschliff. Wer eine
  hinzufügt, muss sagen, welche der beiden dafür weicht.
- **Der eigene Standort musste die Form wechseln.** Seit die Restaurants Kreise
  sind, reicht „rot" nicht mehr zur Unterscheidung: Marken-Rot gegen
  Zustands-Grün hat 1,03 Helligkeitsabstand, bei Rot-Grün-Blindheit wäre der
  Standort ein „liefert"-Pin. Er ist deshalb ein deutlich größerer, dünn
  gefüllter Ring (Radius 13, Füllung 0,15) — Form statt Farbe, wieder einmal.
- **Die Trefferfläche schrumpft** von 25 × 41 px (Leaflet-Standard-Icon) auf
  20 px, bei geschlossenen Restaurants auf 14 px. Bewusst in Kauf genommen: auf
  einer Karte mit 885 Punkten stehlen große Trefferflächen einander die Klicks,
  und die 44-px-Regel aus ADR-008 gilt für Bedienelemente, nicht für
  Datenpunkte. Die barrierefreie Alternative ist nicht ein größerer Pin, sondern
  [A-2](../anforderungen/A-2-ergebnisliste.md) (Ergebnisliste).
- **Legende und Pins hängen an einer Funktion.** Wer `pinStyle()` oder die
  `PIN`-Tabelle anfasst, ändert automatisch die Legende mit. Das ist gewollt —
  eine zweite, handgepflegte Legende wäre binnen eines Feinschliffs falsch.
- **Beim Standardfilter sehen alle Pins gleich aus** (grün, volle Größe), weil
  „Liefert jetzt" genau danach filtert. Die Grammatik zahlt sich beim Aufweiten
  aus — also nach „Alle Restaurants zeigen", was nach ADR-007 der übliche Weg
  aus dem nächtlichen Leerzustand ist. Das ist kein Fehler und kein Grund, den
  Default anzufassen.
- **Die drei Leaflet-Marker-Grafiken sind aus dem Service-Worker-Cache raus**
  (`marker-icon.png`, `-2x`, `-shadow`): `L.marker` wird nirgends mehr erzeugt.
  Entsteht wieder einer, holt die `cacheFirst`-Regel für unpkg das Bild zur
  Laufzeit nach.
- **`--zustand-*` hat jetzt drei Fallback-Kopien in JavaScript**
  (`pinTokens()`), analog zum bestehenden `--marke`-Fallback in `locateMe()`.
  Wer die Tokens in `:root` ändert, zieht sie mit — `cssVar()` fällt sonst
  stumm auf einen alten Wert zurück.
- **A-2 erbt die Pflicht zur Textfassung**: die Ergebnisliste muss dieselben
  drei Lieferzustände in Worten sagen, weil die Kreise für Screenreader nicht
  existieren.
