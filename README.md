# Lieferkarte Karlsruhe

Kostenlose Lieferkarte für Karlsruhe: Restaurants mit eigenem Lieferservice, direkter Link zur Website – ohne Provisionen-Plattformen wie Wolt oder Uber Eats.

🗺️ **Website:** [lieferkarte-karlsruhe.github.io](https://lieferkarte-karlsruhe.github.io)

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

1. Website öffnen: https://lieferkarte-karlsruhe.github.io
2. Suche nutzen oder auf der Karte durchschauen
3. Restaurant anklicken → zur Website und bestellen

Die Seite hat keine Cookie-Banner, kein Tracking, keine Ads. Punkt.

## Fehler melden? Restaurant fehlt?

**Fehler auf der Karte (falsche Adresse, Lieferstatus stimmt nicht):**
→ [GitHub Issue öffnen](../../issues/new)
oder Mail an: `kontakt@example.de` (wird später hinzugefügt)

**Restaurant sollte hier sein, aber fehlt:**
→ Wenn es auf Google Maps zu finden ist, wird es beim nächsten wöchentlichen Scan erfasst (normalerweise sonntags).
→ Falls es dort gar nicht gelistet ist, kann es [hier als Issue vorgeschlagen werden](../../issues/new).

**Du bist ein Restaurant und möchtest deine Info korrigieren?**
Aktualisiere deine Daten auf Google Maps (Adresse, Telefon, Website, Liefergebiet) – der Scan greift die Infos von dort.

## Technisches

Daten werden wöchentlich automatisch per GitHub Actions gescannt:
- **Quelle:** Google Maps API (Places)
- **Speicher:** SQLite (im Repo)
- **Karte:** Leaflet + OpenStreetMap (kostenlos)
- **Hosting:** GitHub Pages (kostenlos)

Kosten: nur die Google-API-Anfragen (~10–15 €/Monat für Karlsruhe).

### Für Entwickler

Das Projekt ist **Open Source** (MIT-Lizenz) – alle Komponenten sind einsehbar:
- `scanner.py` – Places API (New), Change Detection
- `export.py` – JSON-Export für die Karte
- `web/index.html` – Frontend (Leaflet, Suche, Filter)

Vollständiges Setup: siehe [`TECHNICAL.md`](TECHNICAL.md)

### Lokale Entwicklung / Test

```bash
# Demo ohne API-Key
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
- Restaurants & Lieferstatus: © Google Maps Platform
- Kartenkacheln: © [OpenStreetMap](https://www.openstreetmap.org/copyright)-Mitwirkende (ODbL)
- Kartendaten: Leaflet (BSD-2-Clause)

**Impressum & Datenschutzerklärung:**
→ [siehe hier](IMPRESSUM.md)

## Lizenz

MIT – du darfst den Code nutzen, ändern und weitergeben. Siehe [`LICENSE`](LICENSE).

## Roadmap (Karlsruhe)

- [ ] Filter nach Küchenstil (Pizza, Thai, Burger, …)
- [ ] Öffnungszeiten auf der Karte
- [ ] "In meiner Nähe"-Filter
- [ ] Änderungs-Feed ("Diese Woche neu …")
- [ ] PWA (zum Homescreen hinzufügen)
- [ ] Manuelle Einträge für Restaurants ohne Google-Eintrag

---

**Fragen?** → [GitHub Issues](../../issues) oder [Diskussionen](../../discussions)
