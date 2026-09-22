# 114 — An unobserved party does not leave the walk green

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-21 from [the Laya and loophole map](../../laya-loophole/map.md), ticket 08.
It is the second survivor of ticket 07's loophole round. Reproduced by
`tests/test_cage_ladder_holes.py`.

`platform/shift-left/tier_binding.py` returns 3, could-not-look, when a party declares two
governed Namespaces, because which one carries the party's tier is not the check's guess to make
(ADR-0020). That is right, and ticket 78 built it on purpose.

The hub's estate walk then throws it away. `verify/tier-binding/tier_binding_estate.py` prints
the party's SKIP line, `continue`s, and returns `1 if failed else 0`. A skipped party is neither
looked at nor failed, so the script exits 0 while one party's cage is unobserved.
`talk/verify-all.sh` grades a script by its exit code alone, so the gate reads PASS.

Measured 2026-09-21 on a planted estate of two bound parties: adding a second governed Namespace
document to one of them produces `SKIP: driftwood`, `PASS: ludlow`, and exit 0.

This is the estate's own defect class, eco-system ticket 98 and the Laya map's call 6: a tool
that cannot report its own failure is not measured, it is trusted.

Two things bound the blast radius, and neither closes it:

- Each adopter's own `shift-left.yml` turns exit 3 into a failed pull request by name, so the
  ambiguity cannot arrive through a pull request that runs that job. It can arrive any other way,
  and the hub's report of the estate is wrong either way.
- The cage the cluster serves does not change. This is a hole in the observation, not in the
  cage.

What this ticket owes:

1. An unobserved party does not leave the walk at exit 0. The likely shape is that a SKIP on a
   party that HAS both a composed artefact and a governed Namespace manifest is a could-not-look
   for the whole walk, distinct from a party that has neither.
2. A selfcheck leg that plants the ambiguous estate, so the repair cannot regress silently.
3. Check the same shape elsewhere. Any hub walk that iterates parties and folds per-party
   verdicts into one exit code can lose a could-not-look the same way.

## Done

The planted ambiguous estate does not exit 0. The selfcheck holds it. The
`adopter-silences-its-own-binding-observation` row in `twin/ecosystem-misuse-catalogue.yaml`
stops waiting on this ticket and names the built mechanism by path.

## Build, 2026-09-22

Hub only. Platform's `shift-left/tier_binding.py` was read at platform origin/main `3d7f098`
(PR 28 merged) and is unchanged: its exit 3 for two governed Namespace declarations is right.

### What was built

1. **An unobserved party no longer leaves the walk at exit 0.**
   `verify/tier-binding/tier_binding_estate.py` gains `owed()`. A party is owed a binding
   observation when its party.yaml claims the `adopter` role or it has a `composed/evidence.json`.
   A SKIP from platform's check on an owed party is recorded. After the walk, a FAIL still
   returns 1. Otherwise any owed-and-unobserved party returns 3, and the last line names each one
   and why it is owed. A party that is neither (platform today) prints its SKIP and holds nothing
   back. The new check runs before the old "no party has both" line, so an estate where every
   adopter is ambiguous no longer falls through to that line.
2. **The walk reads who the adopters are.** `walked()` walks the fixed `PARTIES` tuple and then any
   other directory whose party.yaml claims the adopter role. Before this, a fourth adopter was
   never walked at all. Roles are read by hand (flow and block lists), because the walk runs
   under whatever `python3` the runner has.
3. **The selfcheck holds it.** New legs plant a second governed Namespace document on driftwood
   beside a bound tuppence (exit 3), add an observed loose adopter on top (exit 1, FAIL
   outranks), make every owed party ambiguous (exit 3, and the last line is not the declared
   `waits:` line), and plant an adopter-role party with nothing composed (exit 3). Mutation check:
   with the new `if unobserved:` branch disabled, the selfcheck fails on its first new assertion
   with rc 0. The wrapper already runs the selfcheck before it believes a 0 or 1.
4. **The wrapper.** `verify-tier-binding.sh` comments name the fourth could-not-look. Its PASS
   line no longer says a skipped party is "graded by nothing here". It now says each SKIP line on
   a PASS is a party owed no observation or a package with no party fold.
5. **The regression tests.** `tests/test_cage_ladder_holes.py` leg B flips from "exits 0" to
   "exits 3". It also judges the wrapper's last line with the gate's own reader
   (`talk/truth_manifest.py` `judge`) against `talk/verify-manifest.txt`. That line is not
   declared, so the gate grades it red.
6. **The catalogue row.** `adopter-silences-its-own-binding-observation` drops `waits_on: 114`
   and anchors `def owed`, `def walked` and two tests by path. The version goes 4 to 5.

### Item 3: the sweep

Read every hub script that iterates parties or units and folds per-party verdicts into one exit
code. Method: `grep -rnE "for (\w+) in .*(PARTIES|ADOPTERS|UNITS|adopters|parties|units|driftwood)"`
over `*.py` and `*.sh` in the hub, plus `grep -rnE "return 1 if \w+ else 0"`. Then I read the fold
in each hit.

- **Same shape, fixed here: `verify/handbook/handbook_check.py`.** An adopter whose page could not
  be read beside one that passed was a `??` line, and `run()` returned 0. An adopter that deleted
  `composed/HANDBOOK.md` would go unseen. Now any unread ref with no FAIL returns 3 and names it.
  The line avoids the declared `waits:` phrase "serves a handbook this check could read", so the
  gate reads it red. Selfcheck leg added: it copies the planted adopter, removes one page, and
  expects 3. It was red first (the old code graded 0) and is green now: 28 planted cases pass.
- **Already FAIL > SKIP > PASS, no change:** `pound-seam/pound_seam.py`, `priced-holes/priced_holes.py`,
  `branch-refs/branch_refs.py`, `supersede/supersede.py` (all `3 if "SKIP" in LINES`),
  `twin-per-adopter/twin_per_adopter.py`, `unreviewed-major/unreviewed_major.py`,
  `fold-agreement/fold_agreement.py`, `real-signature/real_signature.py`, `trust-root/trust_root.py`
  (a `grade()` that returns SKIP on any unlooked leg), `provenance/verify-release-evidence-reaches-main.sh`
  (`skipped` becomes exit 3), `e2e/verify-e2e-step5-twin-forecasts.sh` (collects skips),
  `sampler-wait-order/verify-sampler-wait-order.sh` (a missing unit exits 3 at once),
  `disclaimer/disclaimer.py` and `map-surface/map_surface.py` (a missing file or unit is a finding).
- **Not the shape:** `renovate/verify-renovate-merged-feed-pr.sh` asks whether ANY adopter has a
  merged Renovate feed PR, so passing on one adopter is its claim. `cited-truth`, `can-record` and
  `talk/truth_manifest.py` return 1-or-0 but walk no parties.
- **Residual, recorded rather than fixed:** `real_signature`, `trust_root`, `fold_agreement` and
  `unreviewed_major` filter adopters with `if (estate / u).is_dir()`, so an adopter whose clone is
  absent from `.estate-clone` is silently not walked. That is the clone's state, not a move an
  adopter can make in its own repository, so it is out of this ticket.

### Measured

- Real estate at origin/main (detached worktrees of platform `3d7f098`, driftwood `c96c412`,
  tuppence `7009ea9`, ludlow `32d5696`, assembled as symlinks under the scratchpad):
  `ESTATE_CLONE=<that> bash verify/tier-binding/verify-tier-binding.sh` exits 0. Three adopters
  PASS and platform SKIPs, owing no observation. The repair does not turn today's gate row red.
- The same wrapper over `_plant(..., ambiguous="driftwood")` exits 3. Its last line is
  `SKIP: 1 party/parties owed a binding observation could not be looked at (driftwood), ...`.
- `PAVC_ESTATE_CLONE=<that> bash verify/handbook/verify-handbook-is-a-compose-time-render.sh` exits 0,
  with 3 of 3 adopters serving a page at origin/main.
- Tests ran in the hub worktree with `.estate-clone` pointed at the origin/main estate above (the
  shared `.estate-clone/platform` checkout is 56 commits behind and lacks what PR 28 and PR 17
  landed). After rebasing onto origin/main, which by then carried PR 85:
  - `.venv/bin/python -m pytest tests/test_cage_ladder_holes.py -n0 -q`: 24 passed, 10 skipped.
    The 10 skips are ticket 113's engine legs: kyverno on PATH is 1.19.1, not the pinned 1.18.2.
  - Before the repair, 7 of the 8 leg-B tests failed and the clean control passed. The
    gate-reader test first failed on a loader bug in the test itself. Once that was fixed it
    failed on the walk's exit 0.
  - `.venv/bin/python -m pytest tests/test_misuse.py -n0 -q`: 43 passed.
  - `bash verify/misuse/verify-misuse.sh` prints
    `PASS adopter-silences-its-own-binding-observation: 5 anchor(s) resolve`.
  - `verify/handbook/handbook_check.py --selfcheck` with platform origin/main's
    `compose/handbook.py`: 28 planted cases pass.
- mypy over `twin tests conftest.py`: no issues in 194 source files.

### Decisions (delegated, ADR-0025)

- **"Owed an observation" means the adopter role or composed evidence, not "has both inputs".**
  The ticket suggested "has both a composed artefact and a governed Namespace manifest". That
  leaves a second exit: an adopter that deletes its evidence or un-labels its Namespace drops to
  "has neither" and goes quiet again. The adopter role is signed in party.yaml, so it is the
  harder claim to drop. Platform is neither, and it still skips harmlessly.
- **FAIL outranks the unobserved could-not-look.** This matches every other hub walk. An observed
  loose cage is the answer, and the unobserved party's SKIP line is still printed above it.
- **The new could-not-look is not declared in `talk/verify-manifest.txt`.** An adopter silencing
  its own observation is not the estate still arriving. It should go red, and the test asserts
  that through the gate's own reader.
- **The walk reads the adopter role, not only the fixed tuple.** A fixed list is the same silent
  drop for a fourth adopter.
- **The handbook check gets the same repair.** All three adopters serve a page today, so one that
  stops is a regression. The declared `waits:` stays for the "no adopter serves a page" case.

### Merge notes

Hub PR 85 (ticket 113) merged to main while this was being built. This branch is rebased onto it
with no conflict. Both PRs bumped the catalogue from `version: 4` to `version: 5`, and git applied
the identical line silently, so this branch bumps it again to `version: 6`.

### What remains

Nothing waits on the owner. The integrator closes the ticket after merge.
