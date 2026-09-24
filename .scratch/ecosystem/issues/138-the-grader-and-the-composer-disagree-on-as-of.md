# 138 — The grader and the composer disagree on as-of

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator. Truth run 324 graded `verify/priced-holes/verify-priced-holes.sh`
FAIL with two lines that no earlier run carried:

```
FAIL: tuppence ungoverned openbao: as_of '2026-09-08' but the newest pinned feed was published '2026-08-28'
FAIL: tuppence ungoverned tuppence-reset: as_of '2026-09-08' but the newest pinned feed was published '2026-08-28'
```

Ticket 119's three intended FAILs on tuppence are gone: tuppence now prices `openbao`. These two
replaced them after tuppence recomposed under platform tools v3.3.0 and then v3.4.0 with its
`feeds/cve@v2` edge, whose `since` is 2026-09-08 (ticket 84).

The hub grader's `_as_of()` (`verify/priced-holes/priced_holes.py`) takes the newest
`published_at` among the adopter's pinned feeds. The composer writes `as_of: 2026-09-08` on the
ungoverned prices. So the two derive `as_of` by different rules, or the grader cannot find the
cve feed's file under the layout ticket 136 introduced.

What this ticket owes:

1. Find which rule is right, from the composer's own code and ADR-0026 point 4, and which side
   is stale. Measure on tuppence at origin/main.
2. Fix the wrong side. If it is the grader, it reads the composer's rule and the vendored layout
   `composed/feeds/<party>/<name>/<version>`. If it is the composer, the fix ships in a tools
   release.
3. A test that plants a second feed of one publisher with a later `since` and checks both sides
   agree.

## Done

The grader and the composer derive one `as_of` for tuppence, and the check grades tuppence's
ungoverned prices without these two lines.
