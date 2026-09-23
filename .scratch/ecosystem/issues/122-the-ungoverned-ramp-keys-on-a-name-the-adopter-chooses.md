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

## Build, 2026-09-22

Built on platform branch `ticket-122-ramp-survives-rename` (platform PR 34, on origin/main
`f5213df`) and hub branch `ticket-122-ramp-survives-rename`. Merge platform first, then hub.

### What changed

- **Platform, `compose/composition.py`.** `_signed_since` dates an ungoverned Namespace from the
  first signed tag that names it, or that names as ungoverned a Namespace X where, in that tag's
  tree, X held a workload (`Kind/name`) that this Namespace holds now and X no longer holds. The
  price carries `since_by`, which names the tag and, for a carried age, X and the workload.
  `compute_ungoverned` takes the governed set and gives each closed entry `closed_by`:
  `governed` or `left-repo`. The `closed-ungoverned-namespace` delta says which. The
  `new-ungoverned-namespace` detail no longer says "carries the institution label", which
  ticket 119 made untrue, and it names the carried `since`. `_first_signed_since` stays as a
  wrapper. The selfcheck plants a rename, a copy and a governed close.
- **Hub, `verify/priced-holes/priced_holes.py`.** It works out the new `since` by itself from
  the clone and does not import the composer. `_signed_since` reads each signed tag's header,
  then reads the tagged tree (`git ls-tree`, then `git show` for each YAML file) for the
  workloads in the Namespaces that header names. It applies the same rule to the checkout's
  current workloads. Check d3 FAILs a closed entry with no `closed_by`, or with a
  `closed_by` the recount contradicts. The selfcheck plants three cases.
- **Hub, the leg.** `test_renaming_an_ungoverned_namespace_restarts_its_ramp_and_prints_as_governed`
  is now `test_a_renamed_ungoverned_namespace_keeps_its_ramp_and_the_closed_delta_says_why`. It
  checks that a renamed Namespace keeps `since` 2024-09-01, ramp 3.0 and the same amount (7500.0 of
  a 10000.0 base). It checks that the old name closes `left-repo` with no "governed" in its
  detail, and that governing closes `governed`. It checks that a copy beside the original starts
  at ramp 1.0, and that renaming every workload as well still restarts. The last is the
  residual, below. The verdict rows keep `survivor`, because the survival rate counts what the
  rounds found.
- **Hub, the record.** ADR-0026 gains a dated note. CONTEXT.md's **Ungoverned namespace** entry
  gains the carried `since` and the two closes. `twin/ecosystem-misuse-catalogue.yaml` gains the row
  `adopter-renames-an-aged-ungoverned-namespace-to-restart-its-ramp`, and `tests/test_misuse.py`
  names it.

### Decisions (delegated, ADR-0025)

1. **The age follows the workloads, keyed `Kind/name`, next to the name rule.** Reason: a rename
   moves workloads to a new Namespace name, so the workloads are what stays. `Kind/name` is how
   a workload is identified inside the adopter's repo. It is also the shape the walk already
   counts. The ticket's other shape was to carry the oldest `since` to a Namespace that opens in
   the same composition as another closes. It was rejected. It dates an unrelated new Namespace
   from an unrelated close. An adopter can also get round it in two tags: add the new name, then
   delete the old one.
2. **A copy is not a move.** The age carries only from a Namespace that no longer holds the
   workload. Reason: common names such as `app` would otherwise pass one Namespace's age to an
   unrelated Namespace while both run. A consequence was measured when a selfcheck draft failed.
   A workload that left an aged Namespace and now runs in two Namespaces gives its age to both.
3. **The oldest date wins for the whole Namespace.** Reason: ADR-0026 point 4 prices share ×
   ramp per Namespace, and the verifier checks the same formula. A per-workload ramp would change
   both. This rule can over-ramp a young workload that sits beside an aged one. A too-high price
   pushes toward governing, and governing is the cure.
4. **`closed_by` goes on the entry, and the delta reads it.** Reason: the entry is the record,
   and the verifier grades it against the recount. `compute_ungoverned`'s new `governed` argument
   is optional. A caller that passes nothing gets no `closed_by` and a neutral detail, so the
   function never guesses a reason.
5. **The verifier FAILs a close with no `closed_by`.** Reason: this follows ticket 119. Evidence
   written under the old rule fails by name. Measured: no adopter's committed evidence has a
   closed `ungoverned[]` entry today, so this adds no red.
6. **`since_by` on the price.** Reason: a carried date has to say where it came from. Otherwise
   a reader sees 2024-09-01 on a Namespace that was first named in 2026.

### How it was measured

- **Red first.** The flipped leg against platform origin/main `f5213df` failed with
  `TypeError: compute_ungoverned() got an unexpected keyword argument 'governed'`. The three new
  `tests/test_priced_holes.py` legs ran against the unchanged grader: 2 failed, 1 passed. The
  copy leg already held under the name rule.
- **Green.** The hub worktree's `.estate-clone` pointed at a scratch estate: the platform
  worktree plus symlinks to the other units. Result:
  `pytest tests/test_loophole_adr_0026.py tests/test_priced_holes.py -n0 -q` gave 39 passed.
  `tests/test_misuse.py tests/test_map_surface.py tests/test_build_deck.py` passed. mypy gave
  "no issues found in 199 source files".
- **Platform selfcheck.** Run on a scratch estate of `git clone --local` copies of each unit at
  its origin/main. A symlinked estate fails the review F2 path-leak assert on origin/main too, so
  that failure is not this change. origin/main gave exit 0 with 89 OK lines. The branch gave exit
  0 with 90 OK lines. The only difference is the new ticket 122 line. tuppence-reset still prices
  at 7003870.77 GBP, 3 of 4 workloads, ramp 1.0082 from since 2026-08-25.
  `compose/verify-composition.sh` exits 3 at step 2 on both, with the same SKIP.
- **The grader on the real estate.** Same scratch estate. `priced_holes.py check` wrote the same
  output byte for byte before and after (`diff` empty). Exit 1 both times, from ticket 119's three
  known tuppence FAILs (the `openbao` recount). The carried rule reads the same `since`,
  2026-08-25, for tuppence-reset. Each adopter has two signed tags, v1.0.0 (2026-08-21) and v1.1.0
  (2026-08-25). No workload has moved between ungoverned Namespaces across them.
- `priced_holes.py selfcheck` exit 0. `verify/misuse/verify-misuse.sh` PASS, 6 of 8 rows resolve
  by path. `verify/adr-supersession/verify-adr-supersession.sh` PASS.

### The residual

If an adopter renames every workload along with the Namespace, the ramp still restarts. The leg
holds this. A workload's kind and name are the adopter's to choose, just as a Namespace name is.
The repair makes the cheap move cost more: it takes a rename of every workload, not of one
Namespace. It does not close the move. No key written in the adopter's repo can close it: a name,
an image repository or a spec hash can each be changed by the adopter. This is a candidate for the
next loophole round against ADR-0026 (ADR-0030).

### What waits on the owner

- A signed platform tools release that carries platform PR 34.
- Moving each adopter's tools pin to that release, then recomposing and pushing. Only tuppence
  has an ungoverned Namespace today. Its evidence will then carry `since_by`, and any close will
  carry `closed_by`.
