# Issue tracker: this repo's own backlog (local markdown)

Issues for this repo live in the repo, as markdown, under `docs/`. There are two
places, and the choice between them is not stylistic — `docs/PROZESS.md` defines
the test ("Anforderung oder Aufgabe? Der Test").

**GitHub Issues are dormant here.** The repo has issues #1–#5, all closed, from
an older numbering scheme whose `[A1]`…`[A5]` prefixes mean something different
from today's `A-1`…`A-9`. Do not open new GitHub issues and do not treat the old
ones as the tracker.

## The two places

**Task** → `docs/BACKLOG.md`. Behaviour stays the same (refactor, tests, docs,
dependencies), or the fix is obvious, or it is done in one session and nobody
will later ask *why* it was done that way.

- One checkbox item per task, under an existing priority heading
  (`## Hoch …` / `## Mittel …` / …), ordered by priority.
- Format: `- [ ] **<ID> – <short title>.** <body>`. Keep the `R…`/`P…` IDs from
  the July 2026 UI/UX review; new items may reuse that scheme.
- Done: flip to `- [x]` and append what was done and when, in place. Items are
  not deleted — the finished text is the record.

**Requirement** → `docs/anforderungen/`. Any one of: the user experience visibly
changes, a product decision is still open, it conflicts with a non-goal in
`docs/PRD.md`, or data model / persistence is affected.

- A raw idea is **one row** in the table of `docs/anforderungen/README.md` with
  status `💡 Idee` — no file.
- It earns a file only once refined: copy `docs/anforderungen/_vorlage.md` to
  `docs/anforderungen/A-<n>-<kurz-titel>.md`, then link it from the row and set
  the status to `✅ bereit`.
- **Status lives only in `docs/anforderungen/README.md`.** Never write a status
  into the requirement file — the overview is the single source.
- Numbers are stable and never reused, not even for `🗑 verworfen`.
- Lifecycle: `💡 Idee` → `✅ bereit` → `🚧 in Umsetzung` → `🏁 erledigt`, with
  `🧊 zurückgestellt` / `🗑 verworfen` as branches, each with a reason.

## When a skill says "publish to the issue tracker"

Apply the test above first. Task → append a checkbox item to `docs/BACKLOG.md`.
Requirement → add a row to the table in `docs/anforderungen/README.md`; write the
`A-<n>-….md` file only if the item is genuinely refined, not as an empty
template.

## When a skill says "fetch the relevant ticket"

Read the referenced item in place. Identifiers: `A-<n>` for a requirement (row in
`docs/anforderungen/README.md`, plus its file if one exists), `R…`/`P…` for a
backlog item. A requirement file is the full spec; the row is its status.

## Two rules that override skill defaults

- **Implementation only on an explicit green light** (`docs/PROZESS.md`, step 8).
  A pre-assigned branch name is not one. A skill that would go straight from
  ticket to code stops and asks first.
- **Items are written in German.** The project and all its docs are German; only
  the files under `docs/agents/` are English.

## Architectural decisions

A decision that fixes a lasting product or architecture stance additionally
becomes an ADR — see `docs/agents/domain.md`.
