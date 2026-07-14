# GitHub Actions Setup – Automatische wöchentliche Scans

Diese Anleitung erklärt, wie du den Workflow `.github/workflows/weekly-scan.yml` aktivierst, damit der Scanner jeden Sonntag automatisch läuft.

## Voraussetzungen

- ✅ Repo `lieferkarte-karlsruhe` ist auf GitHub angelegt
- ✅ `.github/workflows/weekly-scan.yml` ist ins Repo committed
- ✅ Google Cloud API-Key ist vorhanden (siehe `TECHNICAL.md`)

## Schritt 1: API-Key als GitHub Secret speichern

Der Google-API-Key darf **nie** im Repo sichtbar sein. GitHub "Secrets" sind verschlüsselte Variablen, die nur in Workflows lesbar sind.

### So speicherst du den Key:

1. Gehe zu deinem Repo → **Settings**
2. Linkes Menü → **Secrets and variables** → **Actions**
3. Klick auf **"New repository secret"**
4. Feld **Name:** `PLACES_API_KEY`
5. Feld **Secret:** dein Google-API-Key (z. B. `AIzaSy...`)
6. Klick **"Add secret"**

✅ Der Key ist jetzt verschlüsselt gespeichert. Im Workflow wird er über `${{ secrets.PLACES_API_KEY }}` geladen – aber nur zur Laufzeit, nie in Logs sichtbar.

## Schritt 2: GitHub Pages aktivieren

Damit die Website öffentlich erreichbar ist:

1. Gehe zu **Settings** → **Pages** (auf der linken Seite)
2. **Source:** "Deploy from a branch"
3. **Branch:** `main` (oder `master`, je nachdem)
4. **Folder:** `/ (root)`
5. Klick **Save**

Nach ~1 Minute sollte die URL angezeigt werden:
```
Your site is published at: https://[dein-username].github.io/lieferkarte-karlsruhe/
```

## Schritt 3: Test-Lauf starten (optional, aber empfohlen)

Bevor der automatische Scan losgeht, kannst du ihn manuell testen:

1. Gehe zu **Actions** (oben im Repo)
2. Linkes Menü → **"Weekly Restaurant Scan"**
3. Klick **"Run workflow"** → **"Run workflow"** (bestätigen)

Der Workflow startet jetzt und sollte in ~2 Minuten durchlaufen. Du siehst:
- 🟡 Gelber Punkt = läuft noch
- ✅ Grünes Häkchen = erfolgreich
- ❌ Rotes X = Fehler

Klick auf den Workflow-Lauf, um die Logs zu sehen.

## Schritt 4: Automatischer Schedule aktivieren

Der Workflow läuft standardmäßig **jeden Sonntag um 06:00 UTC** (07:00 MEZ).

Falls du den Zeitpunkt ändern möchtest:

1. Datei `.github/workflows/weekly-scan.yml` im Repo öffnen (GitHub Editor)
2. Diese Zeile finden:
   ```yaml
   - cron: '0 6 * * 0'
   ```
3. **Cron-Format:** `minute hour dayofweek`
   - `0 6 * * 0` = Sonntag, 06:00 UTC
   - `0 9 * * 0` = Sonntag, 09:00 UTC
   - `0 6 * * 1` = Montag, 06:00 UTC
4. Speichern & Commit

⚠️ **GitHub-Hinweis:** Cron-Jobs haben ±5 Min. Toleranz. Falls der Workflow nicht startet: Repo muss mindestens einen Push in den letzten 60 Tagen haben, sonst deaktiviert GitHub den Schedule automatisch (Sicherheitsmaßnahme).

Die gute Nachricht: Da der Workflow selbst Commits macht (neue Daten), triggert sich der Schedule quasi selbst.

## Schritt 5: Logs & Fehlerbehebung

### Logs einsehen:
1. **Actions** → **Weekly Restaurant Scan** → aktuellster Lauf
2. Logs für jeden Schritt anschauen

### Häufige Fehler:

**"API key not found / PLACES_API_KEY is not set"**
→ Secret war nicht gespeichert. Erneut hinzufügen (Schritt 1).

**"429 Too Many Requests"**
→ Google drosselt. Ist normalerweise kurzzeitig. Script wartet bereits 1 Sec. zwischen Seiten. Nächster Lauf sollte erfolgreich sein.

**"fatal: Nothing to commit"**
→ Keine Daten haben sich geändert. Das ist OK – der Commit wird übersprungen.

**"GitHub Pages build failed"**
→ `web/index.html` hat Fehler. Prüf die HTML-Syntax oder öffne ein GitHub Issue.

## Schritt 6: Änderungs-Feed anschauen (optional)

Die `changes`-Tabelle in der DB protokolliert alle Änderungen:
- `NEW` – Restaurant neu gefunden
- `REMOVED` – nicht mehr auf Google Maps
- `ADDRESS_CHANGED` – Adresse geändert
- `DELIVERY_CHANGED` – Lieferstatus hat sich geändert
- `STATUS_CHANGED` – z. B. jetzt geschlossen

Du kannst diese später als "Diese Woche neu…" auf der Website anzeigen. Dafür `export.py` erweitern, um die letzten Changes mitzuexportieren:

```python
# in export.py hinzufügen:
recent_changes = conn.execute(
    "SELECT place_id, change_type FROM changes WHERE detected_at > datetime('now', '-7 days')"
).fetchall()
payload['recentChanges'] = recent_changes
```

## Status überwachen

Unter **Actions** siehst du jede Woche ein grünes Häkchen (oder rot bei Fehler). GitHub schickt dir auch eine E-Mail, falls ein Workflow fehlschlägt.

Für fortgeschrittene Nutzer: Mit einem **Badge** in deinem README kannst du den Status öffentlich anzeigen:

```markdown
[![Weekly Scan](https://github.com/[dein-username]/lieferkarte-karlsruhe/actions/workflows/weekly-scan.yml/badge.svg)](https://github.com/[dein-username]/lieferkarte-karlsruhe/actions)
```

## Nächste Schritte

1. ✅ API-Key als Secret gespeichert
2. ✅ GitHub Pages aktiviert
3. ✅ Workflow startet automatisch jede Woche
4. ⏭️ Website regelmäßig auf neue Restaurants & Änderungen prüfen
5. ⏭️ Frontend erweitern (Filter, Änderungs-Feed, etc.)

Fragen? Öffne ein Issue im Repo! 🚀
