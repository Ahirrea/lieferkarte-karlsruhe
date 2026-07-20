# Lieferkarte Karlsruhe

Kostenlose Lieferkarte für Karlsruhe: Restaurants mit eigenem Lieferservice, direkter Link zur Website – ohne Provisionen-Plattformen wie Wolt oder Uber Eats.

🗺️ **Website:** [ahirrea.github.io/lieferkarte-karlsruhe](https://ahirrea.github.io/lieferkarte-karlsruhe/)

## Was ist das?

Statt durch Wolt, Uber Eats oder anderen Apps zu bestellen (die Restaurants oft 20–30% Provision nehmen), zeigt Lieferkarte Karlsruhe direkt, welche Restaurants in Karlsruhe ihr eigenes Liefersystem haben. Ein Klick → direkt zur Restaurant-Website oder zum Bestellformular.

**Für Kunden:**
- Übersichtliche Karte statt App-Chaos
- Direkt beim Restaurant bestellen, keine Provisionen
- Filter nach Stadtteil, Öffnungszeiten, Lieferstatus
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

Vollständiges Setup: siehe [`TECHNICAL.md`](TECHNICAL.md)

### Lokale Entwicklung / Test

```bash
# Demo ohne Netz
python3 scanner.py --mock
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

Details & Specs siehe [`IDEEN.md`](IDEEN.md).

- [ ] Filter nach Küchenstil (Pizza, Thai, Burger, …)
- [ ] Öffnungszeiten im Popup + „jetzt geöffnet"-Anzeige (siehe `IDEEN.md`)
- [ ] "In meiner Nähe"-Filter
- [ ] Änderungs-Feed ("Diese Woche neu …")
- [ ] PWA (zum Homescreen hinzufügen)
- [ ] Manuelle Einträge für Restaurants ohne OpenStreetMap-Eintrag

---

**Fragen?** → [GitHub Issues](../../issues) oder [Diskussionen](../../discussions)
