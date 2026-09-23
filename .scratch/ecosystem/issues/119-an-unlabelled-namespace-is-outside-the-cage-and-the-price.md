# 119 — An unlabelled Namespace is outside the cage and the price

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-22 from eco-system ticket
[116](116-the-twelve-unchecked-loophole-candidates.md). It is the one survivor of the twelve
loophole candidates from rounds two and three. Round two's `loophole-2` pointed at it. Reproduced
by `tests/test_loophole_rounds_two_and_three.py` under kyverno 1.18.2, the pinned version.

The candidate said the cage only reaches the Namespaces a discovery list names. There is no
discovery list. The place it pointed at is real, and three facts hold it.

1. **The cage reaches a pod through one of two labels.** `cage-tier` and `stamp-posture` match a
   pod that claims a policy version. The machinery for an unclaimed pod,
   `governed-namespace-requires-claim` and its hold and report, matches only in a Namespace
   labelled `policy-as-versioned.dev/governed: "true"`. The reach cages generate only for a pod
   already caged. A pod with neither label is touched by nothing. Measured over every policy
   document driftwood, ludlow and tuppence serve today and every one the platform delivers next
   (declared lines 4.0.0 and 5.0.0, the graded copy, and the machinery read from
   `distribution/versions.yaml`): no mutation, no failed validation. The control, the same pod
   in a governed Namespace, is refused by every adopter's served guard and caged on `isolated`
   by the next machinery.
2. **The composition prices a Namespace through a third label.**
   `platform/compose/composition.py` `ungoverned_namespaces` lists a Namespace as ungoverned,
   and so prices it as a share of the adopter's uncaged residual (ADR-0026 point 4), only when
   it carries `policy-as-versioned.dev/institution`. A Namespace without that label is called
   infrastructure. Its workloads are counted and left out of the share's denominator, so it
   carries no price at all. The adopter writes that label, and nothing checks the choice.
3. **It happens in the estate now.** On tuppence's origin/main (`7009ea9`) the composition's own
   walk counts one workload in `openbao`: the `openbao-reset-role` Job in
   `reset/openbao-role.yaml`. tuppence's repo never declares the `openbao` Namespace, and the
   Job's pod claims no version. `reset/up.sh` applies it with `kubectl`, outside Flux. Measured
   with `_namespace_facts` over a `git archive` of each adopter's origin/main: driftwood and
   ludlow have no such workload outside `flux-system`.

ADR-0022 says "silence buys nothing anywhere", and NORTH-STAR says everything is always caged.
Here a Namespace that says nothing buys no cage and no price.

The difference from ticket 113 is who decides. `infra` is declared by a party that holds the
`platform` role, and the truth surface reads it. "Infrastructure" in the composition is whatever
Namespace an adopter leaves unlabelled.

What this ticket owes:

1. Decide where the repair lives, and record it as delegated under ADR-0025. Two shapes are
   known, and they can combine:
   - **Price it.** The composition treats every Namespace an adopter's repo declares or names,
     outside the platform's own substrate list, as an institution Namespace unless something
     other than the adopter's silence says otherwise. Then an unlabelled one prices like any
     other ungoverned Namespace.
   - **Cage it.** A machinery policy puts an unclaimed pod in an ungoverned Namespace on the
     bottom rung.
2. Keep the substrate out of the cage. Ticket 113 rests CoreDNS's safety on two facts that
   `distribution/verify-infra-declaration.sh` proof 3 guards: every served body keeps its claim
   gate, and no substrate Namespace is governed. A cage shape must say how it tells kube-system,
   flux-system and kyverno from an adopter's Namespace without a label the adopter can also
   write. If it cannot, it is the wrong shape.
3. Decide tuppence's `openbao` Job: declare its Namespace, claim a version, or record why the
   tour runs it outside the estate.

## Done

The two legs in `tests/test_loophole_rounds_two_and_three.py` that reproduce this hole flip to
regression tests of the repair, or each fact is recorded as a decision with its reason. The
`adopter-runs-uncaged-and-unpriced-in-an-unlabelled-namespace` row in
`twin/ecosystem-misuse-catalogue.yaml` stops waiting on this ticket and names the built
mechanism by path.

## Build, 2026-09-22

Platform PR: https://github.com/policy-as-versioned-platform/platform/pull/32. Hub PR: branch `ticket-119-unlabelled-namespace-is-priced`. Merge the platform PR first.

### Decisions

1. **The repair is a price, not a cage.** Delegated. `platform/compose/composition.py`
   `_namespace_facts` now counts every Namespace the adopter's repo declares or a workload
   names, labelled or not. `ungoverned_namespaces` lists an unlabelled one, and
   `price_ungoverned` prices it as a workload share of the uncaged residual (ADR-0026 point 4).
   Reason: the price closes the hole without touching admission, so it cannot stop a pod. It
   also needs no new body. A served, tagged body is immutable, and a machinery policy is a new
   body too.
2. **No cage for an unclaimed pod in an unlabelled Namespace.** Delegated. At admission the only
   facts about a Namespace are its name and its labels. An adopter can write any label. A name
   list in a served body would have to name every substrate Namespace in advance. Beyond the
   `infra` three, the platform's origin/main declares six more Namespaces outside its generated
   corpus: access, currency-system, mesh-demo, spire-system, istio-system and openbao (a YAML
   walk of the platform tree). A cage that missed one would put its unclaimed pods on
   `isolated`, the hazard ticket 113's proof 3 guards. By the
   ticket's own rule this is the wrong shape. The engine leg in
   `tests/test_loophole_rounds_two_and_three.py` is now the regression test of this decision:
   `test_an_unclaimed_pod_in_an_unlabelled_namespace_stays_outside_the_cage_by_decision`.
3. **The substrate list is the platform's `infra` declaration, read from the platform tree.**
   Delegated. The new `substrate_namespaces` reads `engine/namespaces.yaml` from the platform
   checkout the composition runs from, and returns the Namespaces labelled
   `posture.acme.io/tier: infra`: kube-system, flux-system and kyverno. It never reads the
   adopter's copy of the label, so an adopter's own Namespace labelled `infra` is priced like any
   other. A missing or empty declaration raises, so a walk never runs blind. Reason: that file is
   the one the truth surface already reads to know the substrate, and only a `platform`-role
   party writes it (ticket 113). The platform's other planes are not on the list. An adopter
   workload there is the adopter's, and it is priced.
4. **A Namespace only a workload names counts.** Delegated. A workload with no namespace counts
   in `default`, as before. None of the three adopters has one today (measured below).
5. **tuppence's `openbao` Job is priced, not moved or claimed.** Delegated. `openbao` is the
   platform's identity-plane Namespace (`platform/identity/namespaces.yaml`), so tuppence cannot
   declare it. Claiming a version would put a one-shot Job under a cage whose effect on a Job
   nobody here has measured. How `reset/up.sh` applies it (kubectl, outside Flux) does not
   matter to the price: the Job is in tuppence's repo, and the walk reads the repo (ADR-0018
   point 3). So the next composition prices `openbao` as a tuppence ungoverned Namespace.
   `test_tuppence_openbao_job_is_priced_by_the_next_composition` holds it, and fails if the Job
   ever claims a version.
6. **The hub grader recounts by the same rule, and reads FAIL on tuppence until it
   recomposes.** Delegated. `verify/priced-holes/priced_holes.py` re-derives the walk, and now
   also FAILs any adopter whose committed evidence leaves an ungoverned Namespace unpriced.
   tuppence's committed evidence predates the rule, so the grade moves from PASS to FAIL on
   purpose, as ticket 113's decision 3 did for its tripwire. A PASS here would be the grader
   passing over the open hole.
7. **The walk reads paths relative to the adopter root.** Delegated. It skipped any path with
   `.work` in it, measured from the filesystem root. An adopter checked out under a `.work`
   worktree, as this estate's builders do, read as empty. The same bug made ticket 116 measure
   through `git archive`.

### What was measured, and how

- Units: detached worktrees of each unit's origin/main, not the shared checkouts. platform
  `101fe8a`, driftwood `c96c412`, ludlow `32d5696`, tuppence `7009ea9`, nist `f83126f`, ico
  `abcb3a8`, feeds `ff3ac9a`, insurer `d1c1844`. The hub worktree's `.estate-clone` pointed at
  a private estate of those, with platform swapped for the ticket branch where marked.
- Engine: `kyverno version` printed 1.18.2.
- The walk over each adopter, `_namespace_facts` on a `git archive` of its origin/main.
  driftwood and ludlow: one governed Namespace and one workload, in flux-system. No ungoverned
  Namespace before or after. tuppence before: `tuppence-reset` ungoverned, workloads
  flux-system 1, openbao 1, tuppence-reset 3. After: `openbao` and `tuppence-reset`.
- `composition.py compose` on a local clone of tuppence at `7009ea9`, platform origin/main
  against the branch. Before: `tuppence-reset` recorded, 3 of 3 workloads, share 1.0, amount
  9,262,365.33 GBP, no ungoverned delta. After: `openbao` new, 1 of 4, share 0.25, amount
  2,315,591.33 GBP, one limit (no signed tag names it yet), and one `new-ungoverned-namespace`
  delta. `tuppence-reset` recorded, 3 of 4, share 0.75, amount 7,003,870.77 GBP. Outcome
  `composed` both times.
- `verify/priced-holes/verify-priced-holes.sh` with `PAVC_ESTATE_CLONE` set. Old grader, either
  platform: exit 0. New grader, either platform: exit 1, three FAIL lines, all tuppence: the
  3/3 count, the 1.0 share, and `openbao` unpriced. New grader on an estate where tuppence's
  `composed/` is replaced by the branch composition's output: exit 0, and it prints
  `every ungoverned Namespace the repo walk finds is priced (openbao, tuppence-reset)`.

### Tests

All with `.venv/bin/python -m pytest <files> -n0 -q` and kyverno 1.18.2 on PATH.

- Red first, platform origin/main: `tests/test_loophole_rounds_two_and_three.py` 4 failed, 12
  passed. The four were the flipped price leg and the three new legs.
- Red first, platform origin/main: `tests/test_priced_holes.py` with the new legs and the old
  grader: 3 failed, 13 passed.
- Red first: the platform selfcheck with the flipped case and no implementation stopped with
  `NameError: name 'substrate_namespaces' is not defined`.
- Green, platform at the branch: `test_loophole_rounds_two_and_three.py`,
  `test_loophole_adr_0026.py`, `test_priced_holes.py`, `test_misuse.py` and
  `test_cage_ladder_holes.py` together: 124 passed.
- The same hub branch against platform origin/main: 5 failed, 42 passed over the first three
  files, which is why the platform PR merges first. `test_misuse.py` alone: 1 failed, 42 passed.
  The row's `def substrate_namespaces` anchor is not on platform main yet.
- `verify/misuse/verify-misuse.sh`, platform at the branch: PASS, 5 of 7 rows resolve by path, 2
  could-not-look by name (the two that were already so).
- `verify/adr-supersession/verify-adr-supersession.sh` and
  `verify/cited-truth/verify-cited-truth.sh`: PASS.
- `priced_holes.py selfcheck`: ok, with the new planted case.
- mypy over `twin tests conftest.py`: no issues in 199 source files.
- Platform: `test_portable_observations`, `test_floor_change`, `test_comparison_history` and
  `test_priority_classes` under `compose/`: OK each. The selfcheck: see the side finding.

### Side finding

- `composition.py --selfcheck` does not finish on this estate, on platform origin/main or on
  the branch. Both stop at the same assertion after the same 81 `OK` lines: review F2's
  path-leak check finds the estate path inside a `missing instrument` reason for driftwood's
  `twin/forward-intel/v1/feed.json` ("supplies no lef and its derived_from names 0 subscribed
  feeds that price one"). The OK lines differ in exactly two places, both this ticket's: the
  unlabelled-Namespace case, and the real tuppence-reset share (3 of 3 before, 3 of 4 after).
  Not repaired here.
- The adopters' `git-server` Deployment runs in flux-system, unclaimed. It stays outside the
  price because flux-system is substrate. That is ticket 113's row
  (`adopter-runs-uncaged-in-the-platform-substrate`), not this one.

### What changed

- platform `compose/composition.py`: `substrate_namespaces`, `SUBSTRATE_DECLARATION`,
  `TIER_LABEL`; `_namespace_facts` and `ungoverned_namespaces` by the new rule; the selfcheck
  case flipped. `compose/README.md`.
- hub `tests/test_loophole_rounds_two_and_three.py`: the engine leg renamed as the decision's
  regression test; the price leg flipped; three new legs (a Namespace only a workload names,
  the substrate list and an adopter's own `infra` label, tuppence's `openbao`). The survivor's
  verdict now names the price leg.
- hub `tests/test_loophole_adr_0026.py`: the scratch-directory leg. A directory is still not a
  Namespace, and a Job that names one now prices it. The verdict stays a discard: the
  candidates ask for an exemption by intent, and the price still moves no tier.
- hub `verify/priced-holes/priced_holes.py`, its README and `tests/test_priced_holes.py`.
- hub `twin/ecosystem-misuse-catalogue.yaml`: version 7 to 8. The row stops waiting on this
  ticket and names the mechanism by path.
- hub `CONTEXT.md` (Ungoverned namespace) and a dated note on ADR-0018.

### Waits on the owner

1. **A platform tools tag carrying this change.** Each adopter pins its platform tools to a tag
   (`.github/platform-tools-pin.yaml`), so no adopter composes under the new rule until the
   owner cuts one and the pins move.
2. **tuppence recomposes under that tag and cuts a signed composed tag.** Until then
   `verify-priced-holes.sh` reads FAIL on tuppence by name. That is the intended verdict.
