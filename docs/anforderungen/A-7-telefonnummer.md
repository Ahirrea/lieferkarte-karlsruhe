# A-7 Telefonnummer in die Pipeline

[← Anforderungen](./README.md) · [Prozess](../PROZESS.md)
· Status siehe [Übersicht](./README.md#übersicht)

**User Story:** Als Nutzerin möchte ich direkt anrufen können, weil viele kleine Läden telefonisch schneller erreichbar sind als über ein Formular.

**Verfeinert am:** — (noch nicht verfeinert, Ausgangstext unten)
**Bedient PRD:** „Ziele" — direkter Weg zum Restaurant
**Eingeschränkt durch:** [ADR-005](../entscheidungen/ADR-005-cuisine-nicht-protokollieren.md) (Massen-Ereignisse bei neuen Spalten)

## Ausgangstext (aus `backlog/IDEEN.md`, Idee 7)

Die OSM-Tags `phone`/`contact:phone` kommen beim Scan kostenlos mit; eine
Nummer im Popup wäre für „schnell bestellen" mindestens so nützlich wie die
Website. Die Spalte existiert in `restaurants` noch nicht. Vor dem Bau: Abdeckung
zählen und entscheiden, ob Änderungen protokolliert werden sollen (Vorsicht,
siehe „Massen-Ereignisse" in
[ADR-005](../entscheidungen/ADR-005-cuisine-nicht-protokollieren.md)).

**Zusätzlich zu beachten:** `export.py` migriert die DB nicht. Nach dem Hinzufügen
einer Spalte muss `init_db()` einmal gegen die committete `data/restaurants.db`
laufen, sonst scheitert ein lokales `python3 export.py` an der fehlenden Spalte.
In CI passiert das nicht — dort läuft `scanner.py` (das migriert) zuerst.

---

> **Noch nicht verfeinert.** Der Abschnitt oben ist der unveränderte Ausgangstext
> aus `backlog/IDEEN.md` (Idee 7) — Bestandsaufnahme, Optionen, Entscheidungen
> und Definition of Done fehlen noch. Der Weg dorthin steht in
> [`PROZESS.md`](../PROZESS.md), der Slash-Command `/anforderung` fährt ihn. Die
> Kürzel `R…`/`P…` stammen aus dem UI/UX-Review vom Juli 2026 (Mobil-Screenshot,
> Android/Chrome, 1080 × 2340) und bleiben erhalten, damit Rückfragen zuordenbar sind.
