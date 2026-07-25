# A-5 Pins nach Zustand unterscheiden (R13)

[← Anforderungen](./README.md) · [Prozess](../PROZESS.md)
· Status siehe [Übersicht](./README.md#übersicht)

**User Story:** Als Nutzerin möchte ich auf der Karte sehen, welche Restaurants liefern, abholen lassen oder gerade geschlossen sind, ohne jeden Pin antippen zu müssen.

**Verfeinert am:** — (noch nicht verfeinert, Ausgangstext unten)
**Bedient PRD:** „Kernschleife" Schritt 1
**Eingeschränkt durch:** hängt an [A-1](./A-1-standardfilter-entschaerfen.md)

## Ausgangstext (aus `backlog/IDEEN.md`, Idee 5)

Ob ein Restaurant liefert, abholen lässt oder gerade geschlossen ist, sieht man
erst nach dem Antippen. Farb- oder Formcodierung (z. B. blass = jetzt
geschlossen) bringt viel pro Blick. Hängt an
**[A-1](./A-1-standardfilter-entschaerfen.md)**: erst mit entschärftem
Standardfilter lohnt die Unterscheidung wirklich, und erst dann steht fest, welche
Zustände überhaupt nebeneinander vorkommen.

Braucht außerdem [A-4](./A-4-farbsystem.md): solange `--accent` vier Bedeutungen
trägt, ist keine Farbe für „Zustand" frei.

---

**Nachtrag 2026-07-25 (aus der A-4-Verfeinerung), vor der eigenen Verfeinerung
zu berücksichtigen:** A-4 ist entschieden und liefert die Grundlage. Drei
Vorgaben binden A-5 damit schon jetzt
([ADR-009](../entscheidungen/ADR-009-farbrollen-marke-aktion-zustand.md)):

1. **Pins dürfen nur den `--zustand-*`-Satz benutzen** (`ja` grün, `nein` slate,
   `unbekannt` grau) — nicht `--marke` und nicht `--aktion`.
2. **Farbe allein darf den Zustand nie tragen.** Gemessen liegen die
   Zustandsfarben nur 1,92 auseinander (heutiges Rot/Grün: 1,03) — bei
   Rot-Grün-Blindheit reicht das nicht. Form, Größe oder Symbol muss mit. Die
   Idee „blass = jetzt geschlossen" aus dem Ausgangstext geht in die richtige
   Richtung, weil sie Helligkeit statt Farbton nutzt.
3. **Blau ist verbraucht:** „Abholung" verliert in A-4 seine eigene Farbe, weil
   Farbe ab dann den *Zustand* codiert und das Symbol die *Fähigkeit*. Ein Pin
   kann nicht „blau = Abholung" und „grün/slate = offen/zu" gleichzeitig sagen.

Außerdem entsteht in A-4 der Helfer `cssVar(name, fallback)` — der Weg, eine
Tokenfarbe in JavaScript zu lesen, den `L.circleMarker` für die Pins braucht.

Die Zustandsmengen aus `data/restaurants.db` (883 aktiv, Scan 2026-07-21):
Lieferung 63 ja / 47 nein / **773 unbekannt**, Abholung 237 / 8 / **638**.
„unbekannt" ist der Hauptfall, nicht der Randfall — und darf nach
[ADR-007](../entscheidungen/ADR-007-standardfilter-liefert-jetzt.md) nie wie ein
„nein" aussehen.

---

> **Noch nicht verfeinert.** Der Abschnitt oben ist der unveränderte Ausgangstext
> aus `backlog/IDEEN.md` (Idee 5) — Bestandsaufnahme, Optionen, Entscheidungen
> und Definition of Done fehlen noch. Der Weg dorthin steht in
> [`PROZESS.md`](../PROZESS.md), der Slash-Command `/anforderung` fährt ihn. Die
> Kürzel `R…`/`P…` stammen aus dem UI/UX-Review vom Juli 2026 (Mobil-Screenshot,
> Android/Chrome, 1080 × 2340) und bleiben erhalten, damit Rückfragen zuordenbar sind.
