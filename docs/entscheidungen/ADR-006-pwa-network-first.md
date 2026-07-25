# ADR-006: PWA — `restaurants.json` immer network-first

**Status:** akzeptiert (aus `UMGESETZT.md` herausgezogen am 2026-07-25)
**Datum:** 2026-07-25

## Kontext

Die Seite ist als PWA installierbar und offline nutzbar (`web/sw.js`,
`web/manifest.webmanifest`, ohne Build-Schritt). Ein Service Worker kann Dateien
cache-first ausliefern — das ist schneller und der übliche Standardgriff.

Für **diese** Daten wäre es falsch. `web/restaurants.json` wird wöchentlich
ersetzt. Cache-first hieße: die Nutzerin sieht Öffnungszeiten und Lieferstatus
von letzter Woche, ohne zu wissen, dass sie alt sind — bei einer Karte, deren
Kernaussage „hat jetzt offen" ist, eine falsche Antwort.

## Entscheidung

- `restaurants.json` ist **network-first**. Der Cache ist ausschließlich ein
  Offline-Fallback und wird in der Oberfläche **als solcher gekennzeichnet**
  (sichtbarer Stand).
- Dasselbe für HTML und Manifest.
- **`CACHE_VERSION` in `web/sw.js` wird bei jeder Änderung einer vorab
  gecachten Datei hochgezählt.**
- **Kein `skipWaiting()` beim Install** — die Seite fragt, bevor sie auf die neue
  Version wechselt.

## Begründung

Veraltete Daten still auszuliefern ist schlimmer, als kurz zu warten. Und wenn
offline nur der alte Stand verfügbar ist, muss man das sehen — dann kann man
selbst entscheiden, ob man sich darauf verlässt.

Das „kein `skipWaiting()`"-Verhalten verhindert, dass sich die Seite unter den
Händen der Nutzerin austauscht, während sie sie benutzt.

## Verworfene Alternativen

- **Cache-first für die Daten:** schneller, aber liefert wöchentlich veraltete
  Öffnungszeiten aus. Ausgeschlossen.
- **Gar kein Offline-Betrieb:** die Karte ist unterwegs nützlich, gerade dort ist
  das Netz unzuverlässig.
- **`skipWaiting()` beim Install:** tauscht die laufende Seite ohne Vorwarnung aus.

## Konsequenzen

- **Nie auf cache-first umstellen** — auch nicht „nur zum Testen".
- Wer eine vorab gecachte Datei ändert und `CACHE_VERSION` vergisst, liefert
  alten Code aus. Das gehört in die Definition of Done jeder Frontend-Änderung.
