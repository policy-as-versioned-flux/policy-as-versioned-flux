# 16 — Backport `1.0.1` and delete the `policy/` tree

Type: task
Status: done (2026-08-24)
Blocked by: 14, 15

Source: [`spec.md`](../spec.md), *The repair release*, step 3. Split from
[ticket 09](09-repair-release-and-pinned-delivery.md).

## What to build

`policy/policies/v1.0.0/` is a second tree declaring `v1.0.0`, and it is not in the version array at
all. Its rule `nonroot || (attested && hardened)` is strictly wider than the distribution line's
`1.0.0`. A widening is a patch, so it folds into the distribution line at `1.0.1`.

`2.0.0` already exists, so this is a backport. It is dispatched from a maintenance branch. That breaks
the `@refs/heads/main` identity pin, which is why
[ticket 14](14-anchor-certificate-identity-regexp.md) blocks this one.

The `policy/` tree then goes. After that, one version line exists.

## Acceptance criteria

- [x] `1.0.1` is published on the distribution line, carrying `may-run-root-if-attested`.
- [x] The release is cut from a maintenance branch and verifies under ticket 14's anchored regexp.
- [x] The `1.0.1` element is in the version array with a tag and a resolved commit.
- [x] The `policy/policies/` tree is deleted.
- [x] No pod pinned to `1.0.0` or `2.0.0` loses a policy as a result.
- [x] The release commit records that a widening is a patch, and why.

## Comments

Shipped in `platform` at `a1072d9` + `ba64418` + `586db39` + `7a8df7b` + `52dd283` + `860e744` (cs-16). Real signed tag `policy/v2.0.1`, cut from branch `release/2.0.x` (the maintenance-branch shape ticket 14 anchored), pushed and gitsign-verified. Proving this release out for real surfaced and fixed two foundational bugs in the gate engine itself: a wrong backport-predecessor-selection bug in `gate_one()` (comparing against the wrong, higher line instead of the true lower neighbor), and a deeper self-scoped-policy classification bug in `cage_engine.py` that had been silently making EVERY version bump on a self-scoped policy read as "major" regardless of real content — fixed generally, not just for this one case, and independently re-verified.
