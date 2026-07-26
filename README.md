# Lieferkarte Karlsruhe

Kostenlose Lieferkarte für Karlsruhe: Restaurants mit eigenem Lieferservice, direkter Link zur Website – ohne Provisionen-Plattformen wie Wolt oder Uber Eats.

🗺️ **Website:** [ahirrea.github.io/lieferkarte-karlsruhe](https://ahirrea.github.io/lieferkarte-karlsruhe/)

## Was ist das?

Statt durch Wolt, Uber Eats oder anderen Apps zu bestellen (die Restaurants oft 20–30% Provision nehmen), zeigt Lieferkarte Karlsruhe direkt, welche Restaurants in Karlsruhe ihr eigenes Liefersystem haben. Ein Klick → direkt zur Restaurant-Website oder zum Bestellformular.

**Für Kunden:**
- Übersichtliche Karte statt App-Chaos
- Direkt beim Restaurant bestellen, keine Provisionen
- Zeigt beim Öffnen, was **jetzt** liefert – Filter für Lieferung, Abholung,
  Öffnungszeit und Küchenstil, teilbar als Link
- „🆕 Diese Woche": was seit dem letzten Scan neu ist oder sich geändert hat
- Als App zum Homescreen hinzufügbar, funktioniert auch offline
- Jede Woche aktualisiert

**Für Restaurants:**
- Kostenlose Listung
- Keine versteckte Provision
- Direkte Kontrolle über die eigenen Daten

## Wie nutze ich das?

1. Website öffnen: https://ahirrea.github.io/lieferkarte-karlsruhe/
2. Suche nutzen oder auf der Karte durchschauen
3. Restaurant anklicken → zur Website und bestellen

Die Seite hat keine Cookie-Banner, kein Tracking, keine Ads. Punkt.

### Als App aufs Handy (optional)

Die Karte lässt sich wie eine App zum Homescreen hinzufügen – ohne App-Store:

- **Android/Chrome:** Button „📲 App installieren" auf der Seite (oder Menü ⋮ →
  „App installieren").
- **iPhone/Safari:** Teilen-Symbol ⬆ → „Zum Home-Bildschirm".

Danach startet die Karte im Vollbild und funktioniert **auch ohne Netz** – dann
mit den zuletzt geladenen Daten (mit Hinweis, von wann sie sind). Gespeichert
wird alles nur lokal im Browser: keine Cookies, kein Tracking, keine Anmeldung.
Es gibt außerdem zwei App-Verknüpfungen (langes Tippen auf das Icon):
„Jetzt geöffnet" und „In meiner Nähe".

## Fehler melden? Restaurant fehlt?

**Fehler auf der Karte (falsche Adresse, Lieferstatus stimmt nicht):**
→ [GitHub Issue öffnen](../../issues/new)

**Restaurant sollte hier sein, aber fehlt:**
→ Wenn es in OpenStreetMap eingetragen ist (mit `amenity=restaurant`/`fast_food`), wird es beim nächsten wöchentlichen Scan erfasst (normalerweise sonntags).
→ Falls es dort gar nicht gelistet ist, kann es [hier als Issue vorgeschlagen werden](../../issues/new) – oder direkt in [OpenStreetMap](https://www.openstreetmap.org) eingetragen werden.

**Du bist ein Restaurant und möchtest deine Info korrigieren?**
Aktualisiere deine Daten in OpenStreetMap (Adresse, Website, `delivery=yes` fürs Liefer-Tag) – der Scan greift die Infos von dort. Änderungen dort kommen allen Karten- und App-Diensten zugute, nicht nur dieser Seite.

## Technisches

Daten werden wöchentlich automatisch per GitHub Actions gescannt:
- **Quelle:** OpenStreetMap (Overpass API)
- **Speicher:** SQLite (im Repo)
- **Karte:** Leaflet + OpenStreetMap (kostenlos)
- **Hosting:** GitHub Pages (kostenlos)

Kosten: **0 €.** Die Overpass-API ist kostenlos, kein API-Key nötig. Und weil
OpenStreetMap unter der ODbL steht, dürfen die Daten (mit Attribution) frei
weitergegeben werden – deshalb kann das Repo öffentlich sein und die Daten
direkt ausliefern.

### Für Entwickler

Das Projekt ist **Open Source** (MIT-Lizenz) – alle Komponenten sind einsehbar:
- `scanner.py` – Overpass-Abfrage (OpenStreetMap), Change Detection
- `export.py` – JSON-Export für die Karte
- `web/index.html` – Frontend (Leaflet, Suche, Filter)
- `web/sw.js` + `web/manifest.webmanifest` – PWA (installierbar, offline-fähig)
- `tools/make_icons.py` – erzeugt die App-Icons (nur bei Design-Änderung nötig)

Vollständiges Setup: siehe [`docs/TECHNICAL.md`](docs/TECHNICAL.md)

Produktziel und Nicht-Ziele: [`docs/PRD.md`](docs/PRD.md) ·
was als Nächstes gebaut wird: [`docs/anforderungen/`](docs/anforderungen/README.md) ·
warum es so gelöst ist: [`docs/entscheidungen/`](docs/entscheidungen/README.md)

### Lokale Entwicklung / Test

```bash
# Tests (nur Standardbibliothek, keine Installation nötig)
python3 -m unittest discover -s tests -v

# Scan + Vorschau
python3 scanner.py            # Voll-Scan über Overpass (ein Request, kein Key)
python3 export.py
cd web && python3 -m http.server 8000
# -> http://localhost:8000
```

## Attribution & Datenschutz

**Datenschutz:**
- Keine Cookies, kein Tracking
- Geolocation nur im Browser, nicht serverseitig
- Keine Formulare, keine Datenerfassung

**Datenquellen:**
- Restaurants & Lieferstatus: © [OpenStreetMap](https://www.openstreetmap.org/copyright)-Mitwirkende (ODbL)
- Kartenkacheln: © [OpenStreetMap](https://www.openstreetmap.org/copyright)-Mitwirkende (ODbL)
- Kartensoftware: Leaflet (BSD-2-Clause)

**Datenschutz & Hinweise:**
→ [siehe hier](DATENSCHUTZ.md)

## Lizenz

MIT – du darfst den Code nutzen, ändern und weitergeben. Siehe [`LICENSE`](LICENSE).

## Roadmap (Karlsruhe)

Die Doku liegt in [`docs/`](docs/PRD.md):

| Was | Wo |
|---|---|
| Produktziel, Ziele, **Nicht-Ziele** | [`docs/PRD.md`](docs/PRD.md) |
| Was als Nächstes gebaut wird (Status lebt dort) | [`docs/anforderungen/`](docs/anforderungen/README.md) |
| Warum es so gelöst ist (ADRs, append-only) | [`docs/entscheidungen/`](docs/entscheidungen/README.md) |
| Technische Aufgaben und Fixes | [`docs/BACKLOG.md`](docs/BACKLOG.md) |
| Was schon umgesetzt ist, mit Begründung | [`docs/UMGESETZT.md`](docs/UMGESETZT.md) |
| Von der Idee zur umsetzungsreifen Anforderung | [`docs/PROZESS.md`](docs/PROZESS.md) |

**Bereits umgesetzt:**

- [x] Öffnungszeiten im Popup + „jetzt geöffnet"-Anzeige und -Filter (siehe
  [`docs/UMGESETZT.md`](docs/UMGESETZT.md))
- [x] „In meiner Nähe"-Button (zentriert die Karte auf den eigenen Standort)
- [x] Filter nach Küchenstil (Pizza, Thai, Burger, …) – OSM-Tag `cuisine` läuft
  durch die komplette Pipeline (siehe [`docs/UMGESETZT.md`](docs/UMGESETZT.md)). Die
  Auswahlliste baut sich aus den vorhandenen Daten und bleibt versteckt, solange
  kein Restaurant getaggt ist – die Werte füllt der nächste wöchentliche Scan.
- [x] Änderungs-Feed („Diese Woche neu …") – Knopf „🆕 Diese Woche" öffnet die
  Änderungen der letzten sieben Tage, gruppiert nach Art; ein Klick springt zum
  Restaurant auf der Karte (siehe [`docs/UMGESETZT.md`](docs/UMGESETZT.md))
- [x] **PWA (zum Homescreen hinzufügen)** – Manifest, Icons, Service Worker mit
  Offline-Betrieb und Update-Hinweis (siehe [`docs/UMGESETZT.md`](docs/UMGESETZT.md)
  und [`docs/TECHNICAL.md`](docs/TECHNICAL.md))

- [x] **Standardfilter „Liefert jetzt"** – die Karte startet mit dem, was gerade
  liefert (Lieferung **und** jetzt geöffnet), statt mit allem, was irgendwann
  liefert. Dazu Filter-Chips, ein eigener Abholung-Filter, „unbekannt" als
  sichtbarer dritter Zustand und teilbare Filter-Links. Entscheidung samt
  verworfener Alternativen:
  [`ADR-007`](docs/entscheidungen/ADR-007-standardfilter-liefert-jetzt.md) und
  [`docs/anforderungen/A-1`](docs/anforderungen/A-1-standardfilter-entschaerfen.md).

- [x] **Farbsystem entflochten** – Marke, Interaktion und Datenzustand haben je
  eigene Farbtokens; „geschlossen" ist Slate statt Rot, „unbekannt" ein
  gestrichelter Umriss
  ([`ADR-009`](docs/entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)).
- [x] **Karte im Vollbild** – unter 640 px liegt die Bedienung als eine Zeile
  über der Karte, Filter und Feed sind Bottom Sheets; die Karte wuchs von 70,9 %
  auf 96,6 % des Bildschirms
  ([`ADR-008`](docs/entscheidungen/ADR-008-karte-im-vollbild-overlay-und-sheets.md)).
  Damit ist auch die Fußzeile mit Attribution und Datenschutz-Link nicht mehr
  unter der Browserleiste versteckt (`100dvh`).
**Offen:**

- [ ] **Zustand ohne Antippen sichtbar machen** – am 2026-07-26 einmal über
  farbige Pins gebaut und am selben Tag zurückgenommen: die eingefärbten Kreise
  sahen schlechter aus als Leaflets blaue Tropfen, und im Standardbild „Liefert
  jetzt" sind alle sichtbaren Pins ohnehin gleich
  ([`ADR-011`](docs/entscheidungen/ADR-011-pins-wieder-einheitlich.md) kehrt
  [`ADR-010`](docs/entscheidungen/ADR-010-pin-grammatik-lieferung-und-geschlossen.md)
  um). Die Pins bleiben zustandslos; gelöst wird die Frage über die
  Ergebnisliste, also in Worten statt in Farbe.
- [ ] **UI/UX-Feinschliff** – Punkte aus dem Review vom Juli 2026, gesammelt in
  [`docs/BACKLOG.md`](docs/BACKLOG.md).
- [ ] **Größere UX-Umbauten** als Anforderungen: Ergebnisliste neben der Karte
  (macht die Karte für Tastatur und Screenreader zugänglich), Telefonnummer in
  der Pipeline, Marker-Clustering — siehe
  [`docs/anforderungen/`](docs/anforderungen/README.md).

*Bewusst gestrichen:* Manuelle Einträge für Restaurants ohne
OpenStreetMap-Eintrag – OSM ist bereits eine gepflegte, kostenlose Datenbank;
eine zweite Datenbank zu pflegen ist nicht das Ziel. Fehlende Restaurants
werden stattdessen direkt in OpenStreetMap eingetragen (siehe oben).

---

**Fragen?** → [GitHub Issues](../../issues) oder [Diskussionen](../../discussions)
