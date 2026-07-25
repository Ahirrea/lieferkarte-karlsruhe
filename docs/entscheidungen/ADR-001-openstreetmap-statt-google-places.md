# ADR-001: OpenStreetMap über die Overpass API statt Google Places

**Status:** akzeptiert (nachträglich dokumentiert am 2026-07-25)
**Datum:** 2026-07-25

## Kontext

Das Projekt braucht Restaurantdaten für Karlsruhe: Name, Adresse, Koordinaten,
Website, Liefer-/Abholstatus, Öffnungszeiten. Die naheliegende Quelle war
zunächst die **Google Maps Platform (Places API)**.

Gleichzeitig ist das Modell dieses Projekts: **öffentliches Repo**, GitHub Pages,
und die Daten liegen als committete SQLite-DB plus `web/restaurants.json` **im
Repo** — schon deshalb, weil es keinen Server gibt, der sie ausliefern könnte
(siehe [ADR-002](./ADR-002-kein-backend-daten-im-repo.md)).

Diese zwei Dinge sind unvereinbar. Googles Maps-Platform-Bedingungen verbieten,
bezahlte Places-Daten länger als 30 Tage zu speichern, sie weiterzugeben oder sie
außerhalb einer Google-Karte anzuzeigen. Ein öffentliches Repo mit committeter DB
und JSON tut alle drei Dinge gleichzeitig. Dazu kämen kostenpflichtige
Abrufe pro Anfrage.

## Entscheidung

Datenquelle ist **OpenStreetMap über die Overpass API**, nicht Google Places.
Ein Request pro Scan, Schlüssel ist die OSM-`place_id` (`type/id`, z. B.
`node/12345`).

## Begründung

OpenStreetMap steht unter der **ODbL**, die öffentliche — sogar kommerzielle —
Weiterverbreitung ausdrücklich erlaubt, solange „© OpenStreetMap-Mitwirkende"
sichtbar genannt wird. Genau das macht das Repo-Modell zulässig, und zwar
kostenlos.

Ein angenehmer Nebeneffekt: Kartenkacheln und Restaurantdaten kommen beide von
OpenStreetMap, also deckt **eine** Attributionszeile alles ab.

## Verworfene Alternativen

- **Google Places:** verbietet genau das Nutzungsmuster, auf dem dieses Projekt
  aufbaut, und kostet pro Abruf.
- **Eigene Datenpflege von Hand:** veraltet sofort, nicht wartbar.
- **Betreiber-Websites scrapen:** rechtlich unklar, technisch brüchig, pro
  Restaurant eigener Code.

## Konsequenzen

- **Die Attribution ist Pflicht**, nicht Höflichkeit. Sie muss im
  Frontend-Footer, im JSON-Feld `attribution` und in `DATENSCHUTZ.md` stehen.
  Wer sie entfernt, macht die Weiterverbreitung unzulässig.
- **Keine Datenquelle nachrüsten, die öffentliche Weitergabe verbietet** oder
  kostenpflichtige Abrufe verlangt — das würde das Repo-Modell kippen.
- Guter Umgang mit einem kostenlosen Dienst ist Pflicht: ein Request pro Scan,
  sprechender `User-Agent`, Backoff bei 429/5xx.
- **Die Datenqualität ist die von OSM, also lückenhaft.** `delivery` ist bei 7 %
  der Restaurants getaggt, `takeaway` bei 26 %, `cuisine` bei 0 %. Das ist kein
  Fehler der Pipeline, sondern die Realität der Quelle — und der Grund für die
  offene Anforderung [A-1](../anforderungen/A-1-standardfilter-entschaerfen.md).
  „Ungetaggt" muss überall als *unbekannt* behandelt werden, nie als *nein*.
