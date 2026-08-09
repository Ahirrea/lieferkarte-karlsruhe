# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those
roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the
corresponding label string from this table.

Edit the right-hand column to match whatever vocabulary you actually use.

## Where the label is written

There is no label mechanism in a markdown tracker. Write the label as a
`Triage: <label>` line at the top of the item's body (backlog item or
requirement file).

## The Status column wins

Triage labels do not replace the requirement lifecycle in
`docs/anforderungen/README.md`. Where they would say the same thing
(`wontfix` ↔ `🗑 verworfen`, `ready-for-agent`/`ready-for-human` ↔ `✅ bereit`),
set the Status column and omit the label — never keep both, or the two drift.
Use a label only for something the lifecycle has no word for, above all
`needs-info`.
