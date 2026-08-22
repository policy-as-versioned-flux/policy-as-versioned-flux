# 28 — The adopter gate in `shift-left.yml`

Type: task
Status: ready-for-agent
Blocked by: 27

Source: [`spec.md`](../spec.md), *Solution*, *Where the gate runs, and what it compares*, and *Two live
bugs*.

## What to build

An institution merges a Renovate bump pull request and does not adopt a break by accident.

The adopter gate does not recompute the publisher's answer. A second answer to the same question has no
tie-breaker. It verifies the publisher's signed evidence against an identity the institution holds
itself. It then computes that institution's own composed bump across the parties it consumes.

**Two live bugs close here.** The three institutions' `shift-left.yml` workflows check out the
platform's default branch. They must check out the tag under review at the pull request head. They must
verify the resolved commit against the pinned `commit` field, so the pin ADR-0001 requires is
load-bearing.

**The institution holds its own expected-identity constant.** The party being checked does not supply
the identity it is trusted by. A platform workflow rename therefore breaks verification, and a human
re-decides who they trust.

**The composition inputs are the pinned versions in the institution's own repo at the pull request
head.** There is no discovery endpoint.

**A composed major fails the pull request.** A composed bump weaker than the publisher's tag prints and
never lowers anything. A local view cannot weaken a published promise. A retired version reaches the
institution as a major, so losing a pin is not silent.

Cross-party composition itself is out of scope. This ticket takes one fact from
[`policy-composition`](../../policy-composition/map.md): the bump is a property of a composition, so the
adopter gate computes after composition.

## Acceptance criteria

- [ ] `shift-left.yml` checks out the tag under review at the pull request head.
- [ ] It verifies the resolved commit against the pinned `commit` field.
- [ ] It verifies the publisher's evidence signature, identity-pinned and offline.
- [ ] The expected identity is a constant held in the institution's own repo.
- [ ] A platform workflow rename breaks verification.
- [ ] The composed bump is computed across every party the institution consumes.
- [ ] Composition inputs come from the pinned versions in the institution's own repo at the pull request head.
- [ ] A composed major fails the pull request check.
- [ ] A composed bump weaker than the publisher's tag prints and lowers nothing.
- [ ] A retired version reaches the institution as a major.
- [ ] All three institutions carry the change.
