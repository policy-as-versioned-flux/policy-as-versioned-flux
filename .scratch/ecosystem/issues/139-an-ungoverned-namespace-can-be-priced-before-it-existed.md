# 139 — An ungoverned Namespace can be priced before it existed

Type: task
Status: resolved
Blocked by: none

## Question

Charted 2026-09-24 by the integrator from ticket 138's review.

tuppence's `composed/evidence.json` prices `openbao` with `since: 2026-09-24` (the first signed
tag that names it, v2.0.0) and `as_of: 2026-09-08`. The ramp is measured over a negative window
and clamps to 1.0. `verify-priced-holes.sh` prints:

```
PASS: tuppence ungoverned openbao: ... ramp 1.0000 from since 2026-09-24 as of 2026-09-08
```

The composer's `as_of` counts edge `since` dates and envelope `published_at` only, never the
adopter's own tags. So a Namespace that a tag cut after the newest signed input names first is
priced as of a day before it was ungoverned. Today the ramp clamps to 1.0 and nothing is
mispriced. It will matter the day the ramp is not flat at the start.

What this ticket owes:

1. Decide whether `as_of` must be at least every `since` the composition prices, and record why
   (ADR-0026 point 4 and ticket 122).
2. Make the composer and the grader agree on the rule, with a test that plants a `since` after
   `as_of`.

## Done

No price carries a `since` later than its `as_of`, or the record says why that is correct.

## Build, 2026-09-24

Built 2026-09-24 on platform branch `ticket-139-since-after-as-of` (platform PR 43, on origin/main
7402f3c) and hub branch `ticket-139-ungoverned-namespace-born` (hub PR 125).

### How the case arises, measured on tuppence

- tuppence has three tags: v1.0.0 (2026-08-21), v1.1.0 (2026-08-25) and v2.0.0 (2026-09-24),
  read with `git for-each-ref --sort=creatordate refs/tags`.
- v2.0.0's own `composed/evidence.json` prices `openbao` with `since: null` (no signed tag named it
  yet). Commit 907392a recomposed on main after v2.0.0 was cut. It read v2.0.0 as the first tag
  naming `openbao` and wrote `since: 2026-09-24`, `as_of: 2026-09-08`, ramp 1.0.
- So a Namespace's first `since` is always the tag cut after the composition that first named it.
  The next composition keeps the older `as_of` unless an envelope or edge moved in between. So
  the window runs backwards whenever the tag is cut later than the newest signed input.

### Decisions (delegated, ADR-0025)

1. **`as_of` does not have to be at least every `since` the composition prices.** It stays the
   newest signed input the tree carries: each pinned envelope's `published_at` and each edge's
   `since` (ticket 84). Reason: a tag date is history, not an input. Counting it would move every
   price on the artefact (the eol converter, FX look-ups, the supersede ramp, switching, the other
   ungoverned ramps) each time the adopter tags. One tree over the same parents would then compose
   to two dates, which breaks the rule `_composition_as_of` states. The supersede line already
   decided the same for a later tag day (review F2 in `price_supersede`). Ticket 84's reason for
   adding the edge `since` does not carry over: an edge `since` is written in `party.yaml`, inside
   the tree the tag signs; a tag's creator date is not.
2. **The ramp holds at its start, read as `max(since, as_of)`.** Reason: at `as_of` the Namespace
   had no signed age, so its price is the unramped share. The composer's `_ramp` and the grader's
   `expected_ramp` both read the window from `since` to `max(since, as_of)`. Neither relies on
   eol_ramp's own clamp any more, so this holds the day the ramp is not flat at its start.
3. **The price says so.** `price_ungoverned` adds a limit: "as_of X precedes since Y: the
   composition's as-of is its newest signed input and a tag date is not one, so the ramp holds at
   its start until a composition as of a later day". Reason: the estate prints a named limit
   where a date cannot be used (a null `since`, a missing `as_of`, the supersede zero). A silent
   clamp was the defect.
4. **The grader FAILs a later `since` with no such limit.** Reason: it follows the null-since rule
   beside it. Evidence written by an older composer fails by name. This is one new red on
   tuppence until it recomposes, so the hub PR merges last (below).
5. **The composer changes, so it ships in a tools release.** Reason: the record belongs on the
   price, where a reader of `evidence.json` sees it, not only in this ticket.

### What changed

- Platform `compose/composition.py`: `_ramp` reads `max(since, as_of)`; `price_ungoverned` adds
  the limit; the module docstring says so; the selfcheck plants a tag cut 2026-09-24 against an
  as_of of 2026-09-08 and an on-time as_of that must print no such limit.
- Hub `verify/priced-holes/priced_holes.py`: `expected_ramp` reads `max(since, as_of)`; check d
  FAILs a `since` later than `as_of` with no limit naming it; the selfcheck plants both cases.
- Hub `tests/test_priced_holes.py`: four tests. One checks the ramp holds at its start. One
  checks the limit is required. One checks a ramp below its start fails. One runs the composer's
  own `price_ungoverned` on a fixture repo tagged after `as_of`, grades the price with the grader,
  and then grades it again with the limit removed.
- Hub ADR-0026: a dated note. Hub `CONTEXT.md`: the **Ungoverned namespace** entry says it.

### How it was measured

- **Red.** Against the unchanged grader and the shared estate's platform (0ceb549):
  `.venv/bin/python -m pytest tests/test_priced_holes.py -n0 -q -k "later_than_as_of or holds_at_its_start"`
  gave 2 failed, 2 passed. The ramp-below-start test passed already: the old grader's clamp held
  it. It stays as a guard. The agreement test also failed against platform origin/main 7402f3c
  (scratch estate `est139-base`), at the missing limit.
- **Green.** With the hub worktree's `.estate-clone` pointed at a scratch estate of
  `git clone --local` copies, platform on the branch:
  `pytest tests/test_priced_holes.py tests/test_loophole_adr_0026.py -n0 -q` gave 62 passed.
  Against the shared `.estate-clone` (platform at 0ceb549) the agreement test fails until that
  clone carries platform PR 43; the other 35 pass. `tests/test_map_surface.py` gave 60 passed.
  mypy: "Success: no issues found in 199 source files". `priced_holes.py selfcheck` exit 0.
  `verify/adr-supersession/verify-adr-supersession.sh` PASS.
- **Platform selfcheck.** `compose/composition.py --selfcheck` on scratch estates: origin/main
  7402f3c exit 0 with 102 OK lines, the branch exit 0 with 103. The only new line is ticket 139's.
- **Each adopter's recompose.** `compose/composition.py compose <adopter>` for driftwood,
  tuppence and ludlow, once under origin/main and once under the branch, over the same scratch
  estate. driftwood and ludlow: `diff -r` empty. tuppence: 4 diff lines, one added limit on
  `openbao`. No amount or ramp moves: `openbao` 2375978.79 GBP at ramp 1.0,
  `tuppence-reset` 7401336.68 GBP at ramp 1.03836, both as of 2026-09-08. These match the
  committed evidence.
- **The grader on the estate.** New grader on the shared estate: exit 1, one FAIL, "tuppence
  ungoverned openbao: since 2026-09-24 is later than as_of 2026-09-08 and no limit says the ramp
  holds at its start". New grader on the scratch estate with tuppence's branch recompose: exit 0,
  19 lines, no FAIL or SKIP. origin/main's grader on that same estate: exit 0. So the new
  evidence passes both graders, and only the new grader rejects the old evidence.

### Merge order

1. Platform PR 43. Hub CI clones platform main, so the agreement test needs it first.
2. A platform tools release carrying it, then tuppence's tools pin moves and tuppence
   recomposes and pushes. The integrator does this. driftwood and ludlow compose byte-identical,
   so moving their pins is optional.
3. Hub PR last. Merged before step 2, the truth run's `verify-priced-holes.sh` would FAIL on
   tuppence's `openbao`.

### What waits on the owner

The platform tools release is a signed tag. This build did not cut it. The task names the
integrator for it; if the tag must be the owner's, step 2 waits on the owner. Nothing else waits.

## Answer

Resolved 2026-09-24 by platform PR 43 (in tools v3.4.1), tuppence PR 40 and hub PR 125.

1. **The rule stays.** A composition's `as_of` is its newest signed input: each envelope's
   `published_at` and each edge's `since`. A tag date is history, not an input. Counting it
   would move every price whenever the adopter tags, and one tree would compose to two dates.
2. **So a `since` later than `as_of` is correct, and the price now says so.** The composer
   reads the ramp over `since` to `max(since, as_of)` and adds a limit that names both dates.
   The grader reads the same window and fails a later `since` that carries no such limit.
3. **Measured.** Recomposing driftwood and ludlow under v3.4.1 is byte-identical. tuppence gains
   one limit on `openbao`; its amount (2,375,978.79 GBP) and ramp (1.0) do not move. The hub
   grader passes on tuppence at PR 40's head, and fails by name on the old evidence.

Review: one round, pass. The platform README still describes the old ramp wording; recorded,
not fixed.
