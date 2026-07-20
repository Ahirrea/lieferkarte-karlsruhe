# Vor der Veröffentlichung – Checkliste

Diese Datei hält fest, was vor dem Umstellen des Repos auf **public** (und dem
Aktivieren von GitHub Pages) zu prüfen bzw. zu entscheiden ist.

**Stand des Security-Reviews:** 2026-07-16 (Arbeitsbaum **und** komplette Git-History geprüft)
**Aktueller Status:** Repo bleibt vorerst **privat**. Punkte unten vor Livegang abarbeiten.

---

## ✅ Keine Secrets geleakt (geprüft)

- **Kein echter API-Key** im Repo. Das `AIzaSy...` in `ACTIONS_SETUP.md` ist nur
  ein Beispiel für das Key-**Format**, kein echter Schlüssel.
- **Keine** Tokens/Passwörter/Secrets im Arbeitsbaum oder in der Git-History.
- **Keine** `.env`- oder Key-Dateien wurden je committet. `.gitignore` blockt die
  üblichen Leak-Pfade (`.env`, `*.key`, `*.pem`, `places_api_key.txt`).
- **DB + JSON enthalten nur Demodaten** (`mock_001`–`mock_010`, `.example`-URLs).
  Nichts Echtes oder Sensibles.

→ Technisch keine Credentials exponiert. Die offenen Punkte sind **Datenschutz-**
und **Rechts-Entscheidungen**, keine Lecks.

---

## ✅ Datenlizenz für ein öffentliches Repo geklärt (erledigt)

Frühere Sorge: Dürfen kostenpflichtige Google-Places-Daten in einem öffentlichen
Repo liegen? **Antwort war nein** – die Google-Maps-Bedingungen verbieten
dauerhaftes Speichern (>30 Tage), öffentliche Weitergabe und das Anzeigen
außerhalb einer Google-Karte. Eine committete DB + `restaurants.json` im
public Repo hätte dagegen verstoßen.

**Gelöst durch Wechsel der Datenquelle auf OpenStreetMap (Overpass API):**
- OSM steht unter der **ODbL** → öffentliche Weitergabe ausdrücklich erlaubt.
- Einzige Auflage: **Attribution** „© OpenStreetMap-Mitwirkende" (im Footer, in
  der JSON und in `DATENSCHUTZ.md` ergänzt).
- Kein API-Key, keine Kosten, keine 30-Tage-Löschpflicht.

→ Der Lizenz-Blocker gegen „public" ist damit ausgeräumt.

---

## ✅ Frühere Livegang-Punkte – alle erledigt

### 1. E-Mail-Adresse in der Git-History (Datenschutz) — geklärt

Die komplette History (geprüft mit `git log --all`) enthält **nur GitHub-
`noreply`-Adressen** – keine `generic.de`-Adresse. Beim Public-Schalten wird
also keine private Adresse aus dem Commit-Log exponiert.

### 2. Impressum — bewusst nicht nötig (privates Projekt)

Dies ist ein **privates, nicht-kommerzielles** Projekt und wird nicht als
geschäftsmäßiger Dienst betrieben. Daher **kein Impressum** nach §5 DDG.
Statt der früheren Platzhalter-`IMPRESSUM.md` gibt es eine reine
`DATENSCHUTZ.md` **ohne personenbezogene Daten** (nur „keine Cookies/kein
Tracking", Geolocation-Hinweis, OSM-Datenquelle + Attribution). Footer und
README verlinken darauf.

### 3. Mock-Daten — ersetzt

Der wöchentliche Workflow läuft (Overpass/OSM) und hat die Mock-Daten durch
echte Karlsruher Restaurantdaten ersetzt (~883 Einträge in `main`).

---

## Optional

- `CLAUDE.md` ist committet (Dev-Tool-Anweisungen). Harmlos, nichts Geheimes –
  falls der eigene Workflow nicht öffentlich sein soll, in `.gitignore` aufnehmen.

---

## 📝 Offene Entscheidung: Filter für Abdeckung anpassen (später)

**Tatsächliche Abdeckung** (Voll-Scan, 883 aktive Restaurants):

| Tag | ja (`yes`/`only`) | nein (`no`) | ungetaggt |
|---|---|---|---|
| `delivery` (Lieferung) | 63 (7 %) | 47 (5 %) | 773 (87 %) |
| `takeaway` (Abholung) | **237 (26 %)** | 8 (0 %) | 638 (72 %) |

Aufschlüsselung getaggter Fälle: 43 bieten beides, 20 nur Lieferung,
**194 nur Abholung**.

**Kernproblem:** Die Karte filtert per Default „nur mit Lieferservice"
(`delivery=yes/only`) → es werden nur ~63 von 883 gezeigt. Die 773 ohne
`delivery`-Tag sind „unbekannt", nicht „liefert nicht" – die Karte wirkt
dadurch fälschlich leer. Abholung ist mit 26 % deutlich besser abgedeckt,
wird aber aktuell **nur als Popup-Badge** angezeigt, nicht gefiltert.

Optionen (bewusst noch **nicht** umgesetzt):

- **A – so lassen:** nur sicher getaggte Lieferdienste als Default (sauber,
  aber sehr wenige Treffer).
- **B – eigener „nur Abholung"-Filter:** die 237 Abhol-Restaurants gezielt
  filterbar machen (Daten sind da, seit `takeaway` erfasst wird).
- **C – Default entschärfen:** standardmäßig **alle** zeigen, Lieferung/
  Abholung nur als Badges markieren; optionale Filter für beide. Behebt den
  „fast leer"-Effekt am wirksamsten.
- **D – zurück beitragen:** fehlende Tags selbst in OSM ergänzen (Handarbeit,
  hilft allen).

→ Zum schnellen Nachzählen:
`SELECT delivery, takeaway, COUNT(*) FROM restaurants WHERE active=1 GROUP BY delivery, takeaway;`
auf `data/restaurants.db`.

---

## Kurz-Checkliste für den Launch-Tag

- [x] Autor-E-Mail: History nutzt nur GitHub-`noreply`-Adressen (keine private Mail)
- [x] Kein Impressum nötig (privates Projekt); `DATENSCHUTZ.md` ohne pers. Daten
- [x] Datenquelle OpenStreetMap/Overpass (kein API-Key, ODbL, öffentlich teilbar)
- [x] Echter Scan gelaufen, Mock-Daten ersetzt (~883 Restaurants in `main`)
- [ ] Repo auf **public** gestellt
- [ ] GitHub Pages aktiviert (Settings → Pages → `main` / root)
