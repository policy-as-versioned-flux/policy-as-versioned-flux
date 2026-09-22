# 117 — Two tickets share the number 111, and `waits_on` resolves it silently

Type: task
Status: open
Blocked by: none

## Question

Found 2026-09-21 by [the Laya and loophole map](../../laya-loophole/map.md), ticket 08, and
graduated 2026-09-22 by its ticket 09. It is unfixed.

`.scratch/ecosystem/issues/` holds **two tickets numbered 111**:

- `111-a-green-that-rests-on-luck-may-not-promote.md`
- `111-the-cage-names-priority-classes-its-own-delivery-does-not-deliver.md`

`twin/misuse.py`'s `ecosystem_ticket_status()` resolves a number with
`sorted(glob(f"{number}-*.md"))[0]`, so a `waits_on: 111` row in
`twin/ecosystem-misuse-catalogue.yaml` reads whichever file sorts first, **silently**. Its own
docstring says a missing ticket "grades as a FAIL upstream, never as a quiet skip", and a
duplicate is the case the docstring did not consider: the lookup succeeds, on the wrong ticket.

**It is harmless today and will not stay harmless.** Both tickets are `open` on 2026-09-22, so
both spellings of the answer agree. The first one to close flips a `waits_on` row to a state its
own ticket never reached, and nothing says so.

Two defects, not one:

1. **The resolution is ambiguous.** `ecosystem_ticket_status()` must refuse an ambiguous number
   rather than pick one. A refusal is a FAIL upstream, which is what the function already
   promises for a number it cannot resolve.
2. **The number was reused at all.** Nothing stopped a second ticket taking a number that was
   taken. `docs/agents/issue-tracker.md` says issues are "numbered from `01`" and no check reads
   the directory for a collision.

What this ticket owes:

1. Renumber one of the two. The later of the two by content is the cage-priority-classes ticket;
   confirm that from the record rather than from the file name, and update every reference to it.
2. Make `ecosystem_ticket_status()` refuse a number that resolves to more than one file, with the
   reason on the failure line.
3. Add the collision to whatever already grades the ticket record.
   `verify/derived-status/verify-derived-status.sh` reads every `.scratch/ecosystem/issues/*.md`
   and already refuses a `Status:` field it cannot derive, so it is the cheapest home for "every
   ticket number resolves to exactly one file".

## Done

Every ticket number in `.scratch/ecosystem/issues/` resolves to exactly one file, a duplicate is
a FAIL on the gate rather than a silent first-match, and no `waits_on` row points at a ticket it
did not mean.
