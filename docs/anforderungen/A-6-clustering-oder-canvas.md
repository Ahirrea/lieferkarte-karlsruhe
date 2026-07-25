# A-6 Marker-Clustering oder Canvas-Renderer

[← Anforderungen](./README.md) · [Prozess](../PROZESS.md)
· Status siehe [Übersicht](./README.md#übersicht)

**User Story:** Als Handy-Nutzerin möchte ich, dass die Karte flüssig bleibt, auch wenn alle Restaurants gezeigt werden.

**Verfeinert am:** — (noch nicht verfeinert, Ausgangstext unten)
**Bedient PRD:** „Erfolgskriterien" — unter 30 Sekunden zum Ergebnis
**Eingeschränkt durch:** wird durch [A-1](./A-1-standardfilter-entschaerfen.md) ausgelöst

## Ausgangstext (aus `backlog/IDEEN.md`, Idee 6)

Der zweite Teil von R7 – der erste ist eine Aufgabe, siehe
[`BACKLOG.md`](../BACKLOG.md) (Abschnitt „Mittel"). Mit entschärftem
Standardfilter zeichnet die Karte 883 statt 63 Marker. Ob Clustering
(`markercluster`, wäre eine zusätzliche Abhängigkeit) oder ein Canvas-Renderer
(`L.canvas()`, ohne neue Lib) besser passt, ist offen – und sinnvoll erst zu
entscheiden, wenn [A-1](./A-1-standardfilter-entschaerfen.md) entschieden ist.

---

> **Noch nicht verfeinert.** Der Abschnitt oben ist der unveränderte Ausgangstext
> aus `backlog/IDEEN.md` (Idee 6) — Bestandsaufnahme, Optionen, Entscheidungen
> und Definition of Done fehlen noch. Der Weg dorthin steht in
> [`PROZESS.md`](../PROZESS.md), der Slash-Command `/anforderung` fährt ihn. Die
> Kürzel `R…`/`P…` stammen aus dem UI/UX-Review vom Juli 2026 (Mobil-Screenshot,
> Android/Chrome, 1080 × 2340) und bleiben erhalten, damit Rückfragen zuordenbar sind.
