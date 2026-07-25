# ADR-004: Öffnungszeiten mit eigenem Mini-Parser, fest in Europe/Berlin

**Status:** akzeptiert (aus `UMGESETZT.md` herausgezogen am 2026-07-25)
**Datum:** 2026-07-25

## Kontext

Das OSM-Tag `opening_hours` ist bei 741 der 883 Restaurants gesetzt — die
wertvollste gut abgedeckte Zusatzinformation. Sein Format ist aber mächtig und
komplex: `Mo-Fr 11:00-14:30,17:00-23:00; Sa 17:00-23:00; PH off`.

Es gibt eine ausgereifte Bibliothek dafür (`opening_hours.js`). Sie einzubinden
hieße: eine weitere Abhängigkeit, entweder per CDN (fragil, und es gibt schon
einen CDN-Punkt) oder vendort (mehr Gewicht im Repo).

Dazu ein zweites Problem: „jetzt geöffnet" hängt von der Uhrzeit ab. Die des
Nutzers ist die falsche Referenz — ein Restaurant in Karlsruhe öffnet nach
Karlsruher Zeit, egal wo das Handy steht.

## Entscheidung

- Ein **eigener Mini-Parser** statt einer Bibliothek — leichtgewichtig, keine
  Abhängigkeit, kein Request.
- Er ist **bewusst konservativ**: alles Unsichere ergibt „unbekannt" (kein Badge),
  statt eine falsche Aussage zu riskieren.
- Die Uhrzeit wird über `Intl` fest in **Europe/Berlin** gerechnet — unabhängig
  von der Zeitzone des Nutzers, inklusive Sommer-/Winterzeit, komplett im Browser.

Abgedeckt sind die häufigen Muster: Tagesbereiche und -listen, mehrere
Intervalle, Über-Mitternacht (`Fr 20:00-04:00`), `off`/`closed`, `24/7`.
Nicht ausgewertet: offene Zeiten ohne Ende (`18:30+`), Feiertags- und
Ferienregeln (`PH`/`SH` — clientseitig nicht ermittelbar), Monats- und
Wochenregeln, Freitext, `sunrise`/`sunset`.

## Begründung

Ein falsches „jetzt geöffnet" ist schlimmer als gar keine Angabe: es schickt
jemanden vor eine verschlossene Tür. Deshalb konservativ — ~90 % der getaggten
Fälle wertet der eigene Parser eindeutig aus, die restlichen ~10 % bleiben
sichtbar „unbekannt".

Die feste Zeitzone im Browser passt außerdem zum „kein Server, keine
Datenerfassung"-Prinzip: es braucht dafür keinen Backend-Aufruf.

## Verworfene Alternativen

- **`opening_hours.js` einbinden:** volle Abdeckung, aber eine Abhängigkeit für
  die letzten 10 % der Fälle. Bleibt als Ausbauoption im
  [Backlog](../BACKLOG.md), wenn der Kompromiss nicht mehr reicht.
- **Zeitzone des Nutzers verwenden:** falsche Antworten für jeden, der nicht in
  der deutschen Zeitzone ist.
- **Öffnungszeiten serverseitig auswerten:** es gibt keinen Server
  ([ADR-002](./ADR-002-kein-backend-daten-im-repo.md)).

## Konsequenzen

- Der Parser bleibt **konservativ**: bei jeder Erweiterung gilt weiterhin
  „unsicher → unbekannt", nie „unsicher → geöffnet".
- Die ~10 % unklaren Fälle sind eine bewusste Lücke, kein Bug.
