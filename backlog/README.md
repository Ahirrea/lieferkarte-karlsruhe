# Backlog

Was aus der Karte noch werden soll – und was schon geworden ist. Kein Zeitplan:
die Reihenfolge innerhalb der Dateien sagt, was als Nächstes sinnvoll wäre.

| Stufe | Datei | Bedeutung |
|---|---|---|
| 💡 **Ideen** | [`IDEEN.md`](IDEEN.md) | Richtung steht, Umsetzung nicht – braucht erst eine Entscheidung oder einen Entwurf. |
| 🔨 **Ready for Dev** | [`READY-FOR-DEV.md`](READY-FOR-DEV.md) | Problem, betroffene Datei und Lösung sind benannt – kann direkt gebaut werden. |
| ✅ **Done** | [`DONE.md`](DONE.md) | Fertig und live; bleibt als Kurzprotokoll der Design-Entscheidungen stehen. |

## So wird der Backlog gepflegt

Ein Punkt wandert im Lauf seines Lebens von oben nach unten durch die drei
Dateien: aus einer **Idee** wird – sobald die offene Entscheidung gefallen und
die Lösung samt betroffener Datei benannt ist – ein Eintrag in
**Ready for Dev**; ist er gebaut und live, zieht er als Kurzprotokoll nach
**Done**.

- **Beim Verschieben den Text mitnehmen, nicht neu schreiben.** Die Begründung
  („warum so und nicht anders") ist der wertvollste Teil und der Grund, warum
  `DONE.md` überhaupt weiterlebt.
- **Querverweise als relative Links** zwischen den drei Dateien setzen
  (`[Idee 1](IDEEN.md#1-…)`), damit ein Verschieben nicht stillschweigend
  Verweise zerreißt.
- **Ideen bleiben durchnummeriert** (1 … n), weil in den Texten aufeinander
  verwiesen wird („hängt an Idee 1"). Wird eine Idee umgesetzt, die Nummern der
  übrigen *nicht* nachziehen – lieber eine Lücke als kaputte Verweise.

## Zu den Kürzeln R…/P…

Die Kürzel R…/P… stammen aus dem UI/UX-Review vom Juli 2026 (Mobil-Screenshot,
Android/Chrome, 1080 × 2340, im Abgleich mit `web/index.html`). Sie bleiben
erhalten, damit Rückfragen zuordenbar sind.

---

Vorher lagen alle drei Stufen zusammen in `IDEEN.md` im Wurzelverzeichnis; die
Aufteilung hat nichts an den Inhalten geändert.
