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
fahren (`PLACES_API_KEY` nötig): `python scanner.py` → `python export.py`.

---

## Optional

- `CLAUDE.md` ist committet (Dev-Tool-Anweisungen). Harmlos, nichts Geheimes –
  falls der eigene Workflow nicht öffentlich sein soll, in `.gitignore` aufnehmen.

---

## Kurz-Checkliste für den Launch-Tag

- [ ] Autor-E-Mail auf GitHub-`noreply` umgestellt (ggf. History umgeschrieben)
- [ ] Echtes Impressum in `IMPRESSUM.md` eingetragen (Name, Anschrift, Kontakt)
- [ ] `PLACES_API_KEY` als GitHub-Secret hinterlegt (`ACTIONS_SETUP.md`)
- [ ] Budget-Alarm in Google Cloud gesetzt (`TECHNICAL.md`)
- [ ] Echter Scan gelaufen, Mock-Daten ersetzt
- [ ] Repo auf **public** gestellt
- [ ] GitHub Pages aktiviert (Settings → Pages → `main` / root)
