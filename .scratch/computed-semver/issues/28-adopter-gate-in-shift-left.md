# 28 — The adopter gate in `shift-left.yml`

Type: task
Status: done (2026-08-24)
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

- [x] `shift-left.yml` checks out the tag under review at the pull request head.
- [x] It verifies the resolved commit against the pinned `commit` field.
- [x] It verifies the publisher's evidence signature, identity-pinned and offline.
- [x] The expected identity is a constant held in the institution's own repo.
- [x] A platform workflow rename breaks verification.
- [x] The composed bump is computed across every party the institution consumes.
- [x] Composition inputs come from the pinned versions in the institution's own repo at the pull request head.
- [x] A composed major fails the pull request check.
- [x] A composed bump weaker than the publisher's tag prints and lowers nothing.
- [x] A retired version reaches the institution as a major.
- [x] All three institutions carry the change.

## Comments

Shipped jointly with ticket 29 in the same commits, all prefixed `cs-28-29:`, all real, all pushed: `driftwood` at `28b2e46` + `2864336` + `fe0d381`; `tuppence` at `1f0e7bc` + `246293d` + `255a1c3` + `9329f68` + `d8f695d`; `ludlow` at `7e6785d` + `1d9031f` + `4a9307d` + `edc6589` + `6ef9a2e`.
