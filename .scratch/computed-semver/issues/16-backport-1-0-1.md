# 16 — Backport `1.0.1` and delete the `policy/` tree

Type: task
Status: ready-for-agent
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

- [ ] `1.0.1` is published on the distribution line, carrying `may-run-root-if-attested`.
- [ ] The release is cut from a maintenance branch and verifies under ticket 14's anchored regexp.
- [ ] The `1.0.1` element is in the version array with a tag and a resolved commit.
- [ ] The `policy/policies/` tree is deleted.
- [ ] No pod pinned to `1.0.0` or `2.0.0` loses a policy as a result.
- [ ] The release commit records that a widening is a patch, and why.
