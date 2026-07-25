# ADR-007: Standardfilter ist „Liefert jetzt"

**Status:** akzeptiert
**Datum:** 2026-07-25

## Kontext

Die Karte filterte per Default „nur mit Lieferservice" (`delivery=yes/only`) und
zeigte damit **63 von 883** Restaurants. Der Grund ist die Datenlage in
OpenStreetMap, nicht das Angebot in Karlsruhe:

| Tag | ja (`yes`/`only`) | nein (`no`) | ungetaggt |
|---|---|---|---|
| `delivery` | 63 (7 %) | 47 (5 %) | 773 (87 %) |
| `takeaway` | 237 (26 %) | 8 (0 %) | 638 (72 %) |

Die 773 ungetaggten sind **„unbekannt", nicht „liefert nicht"**. Die Karte sagte
implizit „hier gibt es 63 Restaurants", meinte aber „bei 63 wissen wir es".
Diese Lücken sind die der Quelle und nicht behebbar
([ADR-001](./ADR-001-openstreetmap-statt-google-places.md)) — es ist also eine
reine Frontend- und Produktfrage. Ausgearbeitet in
[A-1](../anforderungen/A-1-standardfilter-entschaerfen.md).

Dahinter steckt eine Grundsatzfrage, die weit über den einen Filter reicht:
**Ist diese Karte ein Verzeichnis oder ein Jetzt-Werkzeug?** Ein Verzeichnis
zeigt erst mal alles und lässt einschränken. Ein Jetzt-Werkzeug zeigt, was
gerade geht, und lässt aufmachen.

## Entscheidung

Der Standardfilter ist **„Liefert jetzt"** — die Karte zeigt beim Öffnen nur
Restaurants, die als liefernd getaggt **und** gerade geöffnet sind. Sie ist
damit ein Jetzt-Werkzeug.

Weil das ein enger Default ist, ist der **Ausweg daraus Teil der Entscheidung**
und nicht verhandelbar: sichtbarer Zurücksetzen-Chip, ein Leerzustand, der die
Datenlage benennt, und ein Manifest-Shortcut „Alle Restaurants".

## Begründung

Wer die Karte öffnet, will bestellen. Ein Restaurant, das liefert, aber
geschlossen hat, ist in diesem Moment kein Treffer, sondern ein Fehlklick — und
mit 741 hinterlegten `opening_hours` ist die Öffnungszeit die am besten
abgedeckte Information im Datensatz.

Der Gegeneinwand — der Default wird dadurch **enger** statt weiter, ~25–40 statt
63 Treffer, nachts null — wurde mit Zahlen vorgelegt und bewusst verworfen. Er
ist nicht falsch, aber er misst die Karte an der Frage „wirkt sie voll?" statt an
„liefert sie eine brauchbare Antwort?". Die Antwort „gerade liefert niemand" ist
brauchbar, solange sie als das kenntlich ist, was sie ist: eine Aussage über die
Datenlage, nicht über Karlsruhe. Genau das leistet der Leerzustand.

Was aus der ursprünglichen Empfehlung **trotzdem übernommen wurde**, weil es vom
Default unabhängig richtig ist: „unbekannt" wird als eigener dritter Zustand
ausgewiesen und nie als „nein", und `takeaway` wird ein eigener Filter.

## Verworfene Alternativen

- **Alles zeigen, nur Badges** (die ursprüngliche Empfehlung): behebt den
  „fast leer"-Effekt am wirksamsten, beantwortet aber die eigentliche Frage
  „wo kann ich jetzt bestellen?" nicht und hätte Clustering erzwungen.
- **So lassen** (`delivery` allein): behält den Fehlklick auf geschlossene Läden.
- **Automatischer Rückfall** auf „alle", wenn zu wenige Treffer: ändert den
  Filterzustand hinter dem Rücken der Nutzerin; die Chips zeigen dann etwas
  anderes an als die Karte.
- **Ein einziger kombinierter Chip „Liefert jetzt"**: hätte „liefert, egal wann"
  unmöglich gemacht. Stattdessen sind es zwei Chips, deren *Vorbelegung* die
  Entscheidung abbildet.

## Konsequenzen

- Die Karte zeigt beim Öffnen tageszeitabhängig ~25–40 von 883 Restaurants,
  nachts null. Das ist gewollt.
- **Der Leerzustand darf nie wieder entfernt werden.** Ohne ihn ist ein Default,
  der regelmäßig null Treffer liefert, eine kaputte Seite.
- Damit „unbekannt" nie zu „nein" verkommt, gilt weiter: `null` fällt bei
  aktivem Filter heraus, wird im Popup aber ausdrücklich als *unbekannt*
  ausgewiesen.
- Filterzustände stehen jetzt in der URL (`?delivery=0&open=0` usw.) — reine
  Query-Parameter, nichts wird gespeichert. Das „keine Cookies"-Versprechen
  bleibt unberührt.
- [A-6](../anforderungen/A-6-clustering-oder-canvas.md) (Clustering/Canvas) wird
  dadurch **nicht** zur Voraussetzung, wie unter der verworfenen Option C
  angenommen — 883 Marker sieht nur, wer die Filter abschaltet.
- Kehrt sich die Grundhaltung „Jetzt-Werkzeug" jemals um, braucht das einen
  neuen ADR — nicht eine stille Änderung von `FILTER_DEFAULTS`.
