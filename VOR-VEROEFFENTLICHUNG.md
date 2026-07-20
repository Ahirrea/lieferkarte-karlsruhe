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
  der JSON und im Impressum ergänzt).
- Kein API-Key, keine Kosten, keine 30-Tage-Löschpflicht.

→ Der Lizenz-Blocker gegen „public" ist damit ausgeräumt.

---

## ⚠️ Vor Livegang entscheiden

### 1. E-Mail-Adresse steckt in der Git-History (Datenschutz)

In einem öffentlichen Repo ist die Commit-Autorschaft für alle sichtbar und wird
gescraped. In der History stehen:

```
Katharina Fröhling <katharina.froehling@generic.de>
Ahirrea <54145949+Ahirrea@users.noreply.github.com>
```

Die `generic.de`-Adresse wäre dann dauerhaft im Commit-Log öffentlich.
Der zweite Contributor nutzt bereits eine GitHub-`noreply`-Adresse (gut).

**Optionen:**
- Ab jetzt eine GitHub-`noreply`-Adresse verwenden
  (GitHub → Settings → Emails → „Keep my email addresses private" + lokal
  `git config user.email "<ID>+<user>@users.noreply.github.com"`).
- Optional die bestehende History **vor** der Veröffentlichung umschreiben
  (History-Rewrite + Force-Push – bewusste, destruktive Aktion).

### 2. Public + Pages = echte Anschrift muss veröffentlicht werden (Recht)

`IMPRESSUM.md` enthält aktuell nur Platzhalter (`[Dein Name]`, `[Deine Adresse]`,
`kontakt@example.de`) – **jetzt** wird also nichts geleakt. Aber ein öffentlicher
deutscher Dienst braucht ein echtes Impressum nach **§5 DDG**: echter Name +
**ladungsfähige (physische) Anschrift** + Kontakt.

→ Livegang bedeutet, Name und Adresse bewusst zu veröffentlichen. Viele nutzen
eine Geschäfts-/Service-Adresse statt der Privatadresse. **Vor** dem Launch klären,
nicht danach.

### 3. Die Live-Seite zeigt 10 Fake-Restaurants

Pages liefert die Mock-`restaurants.json` aus, bis der erste echte Scan läuft.
Kein Sicherheitsproblem – nur kosmetisch. Rund um den Launch einen echten Scan
fahren (kein API-Key nötig): `python scanner.py` → `python export.py`.

---

## Optional

- `CLAUDE.md` ist committet (Dev-Tool-Anweisungen). Harmlos, nichts Geheimes –
  falls der eigene Workflow nicht öffentlich sein soll, in `.gitignore` aufnehmen.

---

## 📝 Offene Entscheidung: `delivery`-Abdeckung prüfen (später)

**Zu klären, sobald echte Daten sichtbar sind** (erster Scan lieferte ~883
Restaurants in Karlsruhe):

Das OSM-Tag `delivery` ist von der Community **lückenhaft** gepflegt. Aktuell
zeigt die Karte per Default nur Restaurants mit `delivery=yes/only` (Frontend:
Checkbox „nur mit Lieferservice", standardmäßig an). Wenn nur wenige Einträge
das Tag gesetzt haben, wirkt die Karte fälschlich leer.

Zu entscheiden, wenn ich mir die tatsächliche Abdeckung angesehen habe:

- **Option A – so lassen:** nur sicher getaggte Lieferdienste zeigen (sauber,
  aber evtl. sehr wenige Treffer).
- **Option B – Filter lockern:** zusätzlich `takeaway=yes` einbeziehen oder
  Restaurants mit ungetaggtem `delivery` als „Lieferung unbekannt" listen
  (mehr Treffer, dafür unschärfer).
- **Option C – zurück beitragen:** fehlende `delivery`-Tags selbst in OSM
  ergänzen (verbessert die Datenlage für alle, aber Handarbeit).

→ Bewusst noch **nicht umgesetzt**. Nach Sichtung der Daten hier entscheiden.
Zum schnellen Zählen: `SELECT delivery, COUNT(*) FROM restaurants GROUP BY delivery;`
auf `data/restaurants.db`.

---

## Kurz-Checkliste für den Launch-Tag

- [ ] Autor-E-Mail auf GitHub-`noreply` umgestellt (ggf. History umgeschrieben)
- [ ] Echtes Impressum in `IMPRESSUM.md` eingetragen (Name, Anschrift, Kontakt)
- [x] Datenquelle OpenStreetMap/Overpass (kein API-Key, ODbL, öffentlich teilbar)
- [ ] Echter Scan gelaufen (`python3 scanner.py`), Mock-Daten ersetzt
- [ ] Repo auf **public** gestellt
- [ ] GitHub Pages aktiviert (Settings → Pages → `main` / root)
