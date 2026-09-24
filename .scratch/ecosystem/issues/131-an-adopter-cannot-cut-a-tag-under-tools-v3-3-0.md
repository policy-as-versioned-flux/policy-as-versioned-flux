# 131 — An adopter cannot cut a tag under tools v3.3.0

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator. It blocks every adopter tag of the v3.3.0 rollout.

driftwood's `cut-release.yml` run 35975270740 (2026-09-24, version v2.0.0, main at 2fff19d)
refused before it created a tag:

```
MISMATCH: re-composition refused: ['comparison history does not match current source inputs'] []
```

The reviewed branch and main have identical trees (`git diff --stat` is empty), so no lane
commit caused it. The cause is the layout. `cut-release.yml` checks out platform, nist, ico,
feeds, insurer and the platform tools INSIDE the adopter's own checkout (`path: platform`,
`path: nist`, and so on) and runs `platform-tools.py ... verify . --estate-clone .`. The
comparison identity that platform tools v3.2.0 added hashes every non-hidden source file outside
`composed/`, so it hashes those parent checkouts too. `compose-check` in `shift-left.yml` puts the
adopter in a subdirectory beside its parents, and there the identity matches. No adopter has cut
a tag with tools newer than v3.0.0 before, so this never showed.

What this ticket owes:

1. Reproduce the refusal offline with the nested layout, and the pass with the sibling layout.
2. Each adopter's `cut-release.yml` (driftwood, tuppence, ludlow) uses the sibling layout that
   `compose-check` uses, so the pre-tag verify reads the same source inputs the composition did.
3. Decide whether the composer's identity should also refuse to hash a nested git checkout, and
   record why. If yes, that is a platform change for a later tools release, not this ticket.

## Done

A dispatched `cut-release.yml` on each adopter passes its pre-tag verify on the v3.3.0 rollout.
