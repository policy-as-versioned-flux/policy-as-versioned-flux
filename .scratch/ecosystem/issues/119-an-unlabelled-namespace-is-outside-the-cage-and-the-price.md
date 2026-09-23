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
