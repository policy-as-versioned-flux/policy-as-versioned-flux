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

## Build, 2026-09-22

**Which 111 was later.** The Question says the cage ticket is the later one. The record says the
opposite, so the record wins. Measured with
`git log --diff-filter=A --format='%h %aI' -- <file>` on `origin/main` and on PR 83's head:

- `111-the-cage-names-priority-classes-...` was added by `e0374f2`, authored
  2026-09-21T08:15:34+01:00, and merged to main by PR 82 at 07:16Z the same morning.
- `111-a-green-that-rests-on-luck-may-not-promote` was added by `f22282e`, authored
  2026-09-21T08:55:41+01:00. Its parent is `04411e1`, the PR 82 merge, and
  `git ls-tree` of that parent already holds the cage 111. It reached main with PR 83 on
  2026-09-22.

So the luck ticket took a number that was already on main. It is now
[118](118-a-green-that-rests-on-luck-may-not-promote.md). 118 is the next free number:
`ls .scratch/ecosystem/issues | sort -n | tail -3` ended at 117, and no file on `origin/main`
matched `ecosystem/issues/118-`.

**How the collision happened.** The trdrbot research note
(`.scratch/laya-loophole/research/10-trdrbot-prior-art.md`) says "next free number; highest
present is 99". `printf '99-a\n100-b\n' | sort | tail -1` prints `99-a`: a plain sort hides
every number from 100 up. Tickets 100 and 110 were already on main (added 2026-09-05 and
2026-09-10). The note's 100 and 101 became 111 and 112 when landed, and 111 was taken by then.

**References updated.**

- The luck ticket's own heading, plus a line saying it was renumbered and why.
- `.scratch/ecosystem/map.md`: the Laya paragraph links 118, not 111. `verify-map-surface.sh`
  grades that every relative link resolves.
- `.scratch/laya-loophole/map.md`: the graduation line and ticket 10's entry.
- `.scratch/laya-loophole/issues/10-what-the-trdrbot-prior-art-teaches.md` and its research
  note: a dated correction. Their "ticket 100" and "ticket 101" pointed at two real, unrelated
  tickets. The correction says to read them as 118 and 112.
- `twin/ecosystem-misuse-catalogue.yaml` has no `waits_on: 111` row. Its four `waits_on` rows
  name 46, 46, 113 and 114. Each resolves to exactly one file, read by calling
  `ecosystem_ticket_status()` on every row in this worktree.
- `git grep -n -w 111` found no `Blocked by:` line naming 111, and no other link to the luck
  ticket's file.

**The lookup refuses an ambiguous number.** `twin/misuse.py`'s `ecosystem_ticket_status()` now
raises `AmbiguousTicketNumber` when a number names more than one file. The message names every
file. `grade_entry()` catches it and grades the row FAIL:
`waits on a number that names more than one ticket: ticket 111 resolves to 2 files: ...`.
A FAIL wins over could-not-look, as it already did for an unknown number.

**The gate refuses a reused number.** `verify/derived-status/derived_status.py` has a new
`number_findings()`. The `record` leg of `verify-derived-status.sh` runs it on every file in
`.scratch/ecosystem/issues/`. Two files with one number are one finding naming both. A file
with no leading number is a finding too. `docs/agents/issue-tracker.md` now says how to find the
next free number and that a reused one is refused.

**Red, then green.**

- Before the fix, on this branch: `tests/test_derived_status.py` failed 6 new tests
  (`AttributeError: number_findings`), and `tests/test_misuse.py` failed to import
  `AmbiguousTicketNumber`.
- After the code change and before the rename,
  `.venv/bin/python verify/derived-status/derived_status.py record` exited 1 on the real record:
  `ticket number 111 names 2 files: 111-a-green-that-rests-on-luck-may-not-promote.md,
  111-the-cage-names-priority-classes-its-own-delivery-does-not-deliver.md`.
  `test_every_number_in_the_real_record_resolves_to_exactly_one_file` failed the same way.
- After the rename: `pytest tests/test_derived_status.py tests/test_misuse.py -n0 -q` gave
  96 passed with no `.estate-clone` in the worktree. With the estate clone linked in it gave
  95 passed and 1 failed: `test_the_four_rows_grade_against_this_checkout`, on the standing
  red named below. `derived_status.py record` exited 0 over 118 tickets.
  `verify-derived-status.sh` exited 0 (PASS). `verify-map-surface.sh` exited 0.
  `verify-cited-truth.sh` exited 0 over 118 ticket files. mypy ended
  "Success: no issues found in 194 source files".
- `verify-misuse.sh` still exits FAIL on one row,
  `regulator-data-mispriced-downstream` (`price_supersede`). That is the standing red named in
  `test_the_four_rows_grade_against_this_checkout`'s docstring. It is not this ticket's.

**Decisions.**

- Delegated (ADR-0025): renumber the luck ticket, not the cage ticket, because git history shows
  it landed second. The Question guessed the other way from the content.
- Delegated: the lookup raises a named exception instead of returning a sentinel string. A
  string would read as an open status and grade could-not-look, which is the silence this ticket
  removes.
- Delegated: the gate compares numbers as integers, so `01-` and `1-` collide. A reader treats
  them as one ticket. `ecosystem_ticket_status()` still matches the literal prefix; no row today
  writes a leading zero.
- Delegated: the collision check lives in the `record` leg, which needs no run. A reused number is
  a FAIL on any day, with or without a grade table.
- Delegated: old dated text in the Laya effort is corrected by an appended dated paragraph, not
  rewritten, so the record keeps what was said and when.

**Not this ticket's, recorded so it is not lost.** `twin/invariants/harness.py`'s
`build_ticket_status()` resolves `.scratch/twin/build/` by the same first-match glob. That
directory holds 92 files and 0 shared numbers today (counted with
`ls | sed -nE 's/^([0-9]+)-.*/\1/p' | awk '{print $1+0}' | sort -n | uniq -d`). Nothing refuses one there yet.

**Waits on the owner.** Nothing. Hub-only, no tag, release or authorisation needed.
