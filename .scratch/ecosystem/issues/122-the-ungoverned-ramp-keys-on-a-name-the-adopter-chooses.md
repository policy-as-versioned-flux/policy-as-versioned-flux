# 122 — The ungoverned ramp keys on a name the adopter chooses

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-23 from eco-system ticket
[120](120-the-eighteen-unchecked-candidates-against-adr-0026.md). It is one of three survivors
of the eighteen loophole candidates against ADR-0026. Round 1's `loophole-2` pointed at it, and
round 2's `loophole-3` and round 3's `loophole-2` point at the same place. Reproduced by
`tests/test_loophole_adr_0026.py`, leg
`test_renaming_an_ungoverned_namespace_restarts_its_ramp_and_prints_as_governed`, against
platform origin/main `b2820d8`.

The candidate said an adopter can put off the first signed tag that names a new ungoverned
Namespace and run it unpriced meanwhile. That is false, and
`test_a_namespace_reaches_the_cluster_only_in_a_tag_whose_header_names_it` holds why: each
adopter's cluster syncs its own repo at a pinned tag and commit, the release workflow runs
`verify` before it cuts the tag, and `verify` fails on a Namespace the committed header does not
know. The first tag that can carry the Namespace to a cluster is the first one that names it.

The place is real. ADR-0026 point 4 ramps an ungoverned Namespace's price from `since`, "the
creator date of the first signed tag whose composed header names it". `_first_signed_since` in
`compose/composition.py` looks the Namespace up by its name, and nothing else.

1. **A rename restarts the ramp.** In the leg, a Namespace named in a signed tag of 2024-09-01
   holds a quarter of the institution workloads and ramps at 3.0 on 2026-09-01. Rename it, keep
   its workload, and cut the next tag: it ramps at 1.0 and its price falls to a third. The ramp
   is `feeds/to_fair_scenario.py` `eol_ramp`, 1.0 plus the years past `since`, capped at 4, so a
   rename can take up to four fifths off an aged Namespace's price.
2. **The rename prints as governance.** The old name leaves the walk, so `compute_ungoverned`
   marks it `closed` and `compute_deltas` prints a `closed-ungoverned-namespace` delta whose
   detail says it "now carries governed: \"true\"". In the leg no Namespace but `home` is
   governed. The record says a Namespace was governed when it was renamed.
3. **Ticket 15 meant the date to hold.** Its item 3 says `since` "survives a close", and the
   docstring of `_first_signed_since` says "a namespace that closes and reopens keeps its original
   since". A rename is a close and an open under two names, and it keeps nothing.

The adopter's cheapest move on an aged ungoverned Namespace is a rename, not governance. ADR-0026
rejected a flat share with the date printed beside it as "the grandfather clause". A rename is a
grandfather clause the adopter can grant itself.

What this ticket owes:

1. Decide, as delegated under ADR-0025, what carries a Namespace's age across a rename. Known
   shapes: key `since` on the workloads (the oldest signed tag in which any workload now in the
   Namespace was ungoverned), or carry the oldest open `since` of the adopter's ungoverned set to
   any Namespace that opens in the same composition as another closes.
2. Make `closed-ungoverned-namespace` say what happened: governed, or left the repo.
3. Say how `verify/priced-holes/` re-derives the new `since`. It reads `since` off the clone's
   signed tags today.

## Done

`test_renaming_an_ungoverned_namespace_restarts_its_ramp_and_prints_as_governed` flips to a
regression test of the repair: a renamed Namespace keeps its ramp, and a closed delta names why
it closed.
