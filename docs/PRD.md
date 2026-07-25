# PRD – Lieferkarte Karlsruhe

**Kostenlose Karte der Karlsruher Restaurants mit eigenem Lieferservice —
direkter Link zur Website, ohne Provisions-Plattformen.**

| | |
|---|---|
| Status | live (öffentliches Repo, GitHub Pages, wöchentlicher Scan) |
| Stand | 2026-07-25 |
| Website | <https://ahirrea.github.io/lieferkarte-karlsruhe/> |

Verfeinerte Anforderungen: [`anforderungen/README.md`](./anforderungen/README.md) ·
Entscheidungen: [`entscheidungen/README.md`](./entscheidungen/README.md) ·
Technische Aufgaben: [`BACKLOG.md`](./BACKLOG.md) ·
Umgesetzt (mit Begründung): [`UMGESETZT.md`](./UMGESETZT.md) ·
Implementierungs-Spec: [`TECHNICAL.md`](./TECHNICAL.md)

> Neu angelegt am 2026-07-25. Das Produktziel stand bis dahin nirgends
> geschlossen: der Pitch im `README.md`, die harten Randbedingungen in
> `CLAUDE.md`, die offene Filter-Entscheidung in `VOR-VEROEFFENTLICHUNG.md`. Dieses
> PRD führt sie zusammen; die Quelltexte sind unverändert erhalten
> ([Launch-Checkliste im Archiv](./archiv/VOR-VEROEFFENTLICHUNG.md)).

---

## 1. Problem

Wer in Karlsruhe etwas liefern lassen will, landet bei Wolt, Uber Eats oder
ähnlichen Apps — die den Restaurants **20–30 % Provision** abnehmen. Viele
Restaurants liefern selbst, aber das erfährt man nur, wenn man ihre Website schon
kennt. Es gibt keine Übersicht, welche Läden im eigenen Umkreis direkt bestellbar
sind.

Für die Restaurants ist es die Kehrseite desselben Problems: Sichtbarkeit gibt es
praktisch nur über die Plattformen, die an jeder Bestellung mitverdienen.

## 2. Zielnutzer:in

Eine Person in Karlsruhe, die heute Abend etwas bestellen will und die Provision
nicht mitbezahlen möchte. Sie öffnet die Seite auf dem Handy, sucht im eigenen
Umkreis, will wissen, wer **jetzt geöffnet** hat, und klickt dann direkt zum
Restaurant. Kein Konto, keine App-Installation als Voraussetzung.

## 3. Ziele

- Auf einen Blick zeigen, welche Restaurants in Karlsruhe **selbst** liefern oder
  Abholung anbieten — mit direktem Link zur Website oder zum Bestellformular.
- Im eigenen Umkreis suchbar: Suche, „In meiner Nähe", Filter nach Lieferstatus,
  Öffnungszeit („nur jetzt geöffnet") und Küchenstil.
- „🆕 Diese Woche": was seit dem letzten Scan neu ist oder sich geändert hat.
- Als App zum Homescreen hinzufügbar und offline nutzbar.
- Wöchentlich aktualisiert, Stand sichtbar.
- **Kostenlose Listung** für Restaurants, ohne versteckte Provision.

## 4. Nicht-Ziele (bewusst ausgeschlossen)

- **Keine Cookies, kein Tracking, keine Analytics, keine serverseitige
  Datenerfassung.** Das ist ein hartes Produktversprechen (`README.md`,
  `DATENSCHUTZ.md`), keine Absichtserklärung. Geolokalisierung bleibt im Browser.
- **Kein Backend, kein Server, keine laufenden Kosten.** Siehe
  [ADR-002](./entscheidungen/ADR-002-kein-backend-daten-im-repo.md).
- **Keine Bestellabwicklung, keine Zahlung, kein Warenkorb.** Die Karte führt zum
  Restaurant, sie ist keine Plattform — sonst wäre sie das, was sie ersetzt.
- **Keine Datenquelle, die öffentliche Weiterverbreitung verbietet** oder
  kostenpflichtige Abrufe verlangt. Siehe
  [ADR-001](./entscheidungen/ADR-001-openstreetmap-statt-google-places.md).
- **Keine Bewertungen, keine Kommentare, keine Nutzerinhalte.** Bräuchte
  Moderation und Speicherung — beides widerspricht dem Rest.
- **Keine anderen Städte.** Die Overpass-Abfrage ist auf Karlsruhe zugeschnitten.

## 5. Kernschleife

1. Seite öffnen → Restaurants auf der Karte, Trefferzahl sichtbar.
2. Suchen oder „In meiner Nähe" → Ansicht verengt sich auf den Umkreis.
3. Restaurant antippen → Popup mit Öffnungszeiten, Liefer-/Abholstatus und
   direktem Link → bestellen beim Restaurant.

Schritt 1 muss ohne Interaktion nützlich sein. **Genau hier liegt heute das
größte Produktproblem:** der Standardfilter „nur mit Lieferservice" zeigt 63 von
883 Restaurants, weil 87 % in OpenStreetMap ungetaggt sind — die Karte wirkt
fälschlich leer. Das ist die offene Kernentscheidung
[A-1](./anforderungen/A-1-standardfilter-entschaerfen.md).

## 6. Erfolgskriterien

- Jemand mit Lieferwunsch findet in unter 30 Sekunden ein Restaurant im eigenen
  Umkreis, das direkt bestellbar ist.
- Die Seite verursacht **null laufende Kosten** und braucht keine Wartung außer
  dem wöchentlichen automatischen Scan.
- Die Daten sind nie älter als der letzte Sonntags-Scan, und der Stand ist sichtbar.
- Ein Restaurant, das seine OSM-Tags korrigiert, erscheint nach dem nächsten Scan
  korrekt — ohne dass jemand etwas von Hand nachträgt.

## 7. Rahmenbedingungen

- **Datenquelle:** OpenStreetMap über die **Overpass API**, ein Request pro Scan,
  Schlüssel ist die OSM-`place_id` (`type/id`, z. B. `node/12345`). Siehe
  [ADR-001](./entscheidungen/ADR-001-openstreetmap-statt-google-places.md).
- **Lizenz Daten:** **ODbL**. „© OpenStreetMap-Mitwirkende" **muss** sichtbar
  bleiben — im Frontend-Footer, im JSON-Feld `attribution` und in
  `DATENSCHUTZ.md`. Nicht verhandelbar, das ist die Bedingung, unter der das
  öffentliche Repo überhaupt zulässig ist.
- **Lizenz Code:** MIT (siehe `LICENSE`).
- **Hosting:** GitHub Pages aus `main`/Wurzel; der wöchentliche Scan läuft als
  GitHub Action und committet selbst. Deshalb sind DB und JSON im Repo.
- **Kosten:** null. Overpass, Nominatim und die OSM-Kacheln sind kostenfrei;
  guter Umgang damit ist Pflicht (ein Request pro Scan, sprechender
  `User-Agent`, Backoff bei 429/5xx).
- **Kein Impressum** — privates, nicht-kommerzielles Projekt. `DATENSCHUTZ.md`
  ist stattdessen eine Hinweisseite ohne personenbezogene Daten.
- **Sprache:** Deutsch — es ist ein öffentliches Angebot für Karlsruhe. UI-Texte,
  Commits und neue Dokumente auf Deutsch.
- **Abdeckungsrealität:** Die OSM-Tags sind lückenhaft. `delivery` ist bei 7 %
  gesetzt, `takeaway` bei 26 %, `cuisine` bei 0 %, `opening_hours` bei 741 von
  883. Das Frontend **muss** `null` („unbekannt") von `false` („nein")
  unterscheiden und beides tragfähig darstellen.
