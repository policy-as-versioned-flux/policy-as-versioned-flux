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

## Build, 2026-09-22

### Diagnosis: the grader is stale, the composer is right

- The composer's rule. Platform `compose/composition.py` at v3.4.0 (0ceb549, also platform
  origin/main today) prices as of `_composition_as_of()`. That is the newest of every edge's own
  `since` and every pinned envelope's `published_at` (`_composition_as_of_source`, lines
  3027-3049). Ticket 84 added the edge `since` on 2026-09-08. ADR-0006's note of that date
  records the same rule. ADR-0026 point 4 names `since` for the ramp and says nothing about
  `as_of`, so it does not contradict either side.
- The grader's rule. The hub's `_as_of()` took the newest `published_at` only. It ignored every
  edge `since`.
- The measurement on tuppence at origin/main (6c0c38a). Read with the grader's own
  `_feed_path()` against the shared `.estate-clone`: penalty-schema v3 published
  2026-08-28, threat-register v1 published 2026-07-31, cve v2 published 2026-07-31. The
  vendored copies under `composed/feeds/<party>/<name>/<version>` carry the same three dates
  (`jq .published_at` on each `feed.json`). The edges' sinces are 2026-08-28 three times and
  2026-09-08 for cve@v2 (`party.yaml`). So the grader found every file; the layout was not the
  cause. It derived 2026-08-28 and the composer's evidence says 2026-09-08 on both entries.
- The same two FAIL lines reproduce. I ran origin/main's `priced_holes.py check` against the
  shared estate clone. It printed exactly the two lines this ticket quotes.
- Two platform docstrings (`composition.py` lines 244 and 1764) still said "the newest pinned
  feed". That wording is probably where the grader's rule came from. The code is right.

### What changed

- Hub `verify/priced-holes/priced_holes.py`. `_as_of()` now takes the composer's rule: the
  newest of every edge's `since` and every pinned envelope's `published_at`. `_feed_path()`
  reads the adopter's vendored envelope first, at
  `composed/feeds/<party>/<name>/<version>/<path>/<major>/feed.json`, and falls back to the
  publisher's tree and then the two pre-envelope files. The FAIL line now names the rule.
- Hub `tests/test_priced_holes.py`. Four new tests plant a second feed of one publisher
  (threat-register@v1 since 2026-08-28, cve@v2 since 2026-09-08). Two check the grader alone.
  One pair runs the composer's own `_composition_as_of` (loaded from
  `.estate-clone/platform`) on the vendored copies with the publisher absent. It checks the
  grader derives the same date. One case has the since winning and one has an envelope winning.
- Hub `CONTEXT.md`. The ungoverned Namespace entry now states the composer's rule.
- Platform PR 42. The two stale docstrings now state the rule. No code changes, so no tools
  release is needed.

### Decisions (delegated, ADR-0025)

1. The grader moves, not the composer. Reason: ticket 84 decided the composer's rule and
   ADR-0006's note records it. The grader copied an older docstring.
2. The grader reads the adopter's vendored envelope before the publisher's tree. Reason: the
   vendored bytes are the ones the adopter's signature digested (`PROVENANCE.json`). A
   publisher that republishes after the adopter signed must not change a signed price. With the
   publisher absent the composer reads the same copy (ticket 137), and the agreement test
   checks that case.
3. Every edge's `since` counts, not only feed edges. Reason: the composer counts every edge
   in `inherits`.
4. The platform change is a separate docs-only PR. Reason: the stale wording misled one reader
   already. It changes no behaviour, so the adopters need no new tools tag.

### Tests run

- Red: the four new tests failed against the old grader
  (`.venv/bin/python -m pytest tests/test_priced_holes.py -n0 -q -k "as_of or since_as or vendored"`,
  4 failed). The composer-side assertion inside the agreement test already passed.
- Green: `.venv/bin/python -m pytest tests/test_priced_holes.py -n0 -q`, 32 passed.
- `priced_holes.py selfcheck` passes.
- `verify/priced-holes/verify-priced-holes.sh` against the shared estate clone exits 0 with 20
  lines, none FAIL or SKIP. Tuppence's two lines now read PASS, as of 2026-09-08.
- `mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores`: no issues in
  199 source files.

### Seen, not changed

- tuppence's `openbao` price has `since` 2026-09-24 and `as_of` 2026-09-08. The since is
  later than the as-of, so the ramp holds at 1.0. The grader's `expected_ramp` gives 1.0 too, so
  the grade passes. A since later than the composition's own as-of is odd but not wrong under
  either rule. No ticket charted.

### What remains

- Merge the platform PR, then the hub PR. No tools release, no recompose and nothing for the owner.
- The next truth run on hub main should grade `verify-priced-holes.sh` PASS for tuppence.
