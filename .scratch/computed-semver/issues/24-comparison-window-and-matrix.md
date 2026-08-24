# 24 — The comparison window and the per-institution matrix

Type: task
Status: done (2026-08-24)
Blocked by: 21

Source: [`spec.md`](../spec.md), *Where the gate runs, and what it compares*, and *What the gate
measures*.

## What to build

The gate compares against the right set of versions, and publishes where one version lands each
institution.

**Compare against every supported version lower than the declared version. The strictest result wins.**
Comparing only against N-1 hides a break for a cluster on N-2, and multi-version coexistence guarantees
that cluster exists.

**Use the window as it stood before this release.** Those are the clusters actually running. This also
makes a retirement classify as major with no special case.

**An array-only release is gated.** Retiring an element changes no policy body and still breaks every
cluster pinned to it.

**A backport compares against the line below it only**, so a version nobody adopts does not decide the
number.

**The first release records `no predecessor`.** A comparison against nothing is not dressed up as a
computed patch. The coverage checks still run in full.

**The bump is institution-relative and is tagged at worst case.** Semver is a property of the artefact,
not of the consumer. Compute against the strictest band in the estate and tag that. Publish the
per-institution matrix as the supporting evidence.

Cost is settled by measurement and is not a constraint. One CLI process costs about 0.3 seconds to
start. Three policies against 200 pods cost 2.15 seconds in one invocation.

## Acceptance criteria

- [x] The gate compares against every supported version lower than the declared one.
- [x] The strictest result decides the computed bump.
- [x] The window is the one that stood before this release.
- [x] An array-only retirement classifies as major, with no policy diff.
- [x] A backport compares against the line below it only.
- [x] A first release records `no predecessor` and still runs the coverage checks in full.
- [x] `matrix` reports the result for each of the three institutions.
- [x] The tagged bump is the strictest band, and the matrix is evidence beneath it.
- [x] A version gap in the window does not break the comparison.

## Comments

Shipped in `platform` at `41f3d3e` (cs-24).
