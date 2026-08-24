# 12 — Render the mandatory members into a version tree

Type: task
Status: done (2026-08-24)
Blocked by: none

Source: [`spec.md`](../spec.md), *Pinned delivery and rendering*. Replaces
[ticket 10](10-render-mandatory-members.md).

## What to build

A publisher cuts a version and gets every enforcement surface in the tree, without hand-editing four
places. One authoring copy stays under `graded/` and `posture/`. A renderer writes the per-version
copies. The emitted copies are committed, because Git and the gate both read real files.

The mandatory members are `cage-tier`, `cage-netpol`, `stamp-posture`, `posture-trust-boundary` and the
three priority classes from `graded/policies/priorityclasses.yaml`. The priority classes are included
because they are the enforcement dial.

A version is four coordinated edits, not a directory. The renderer emits the directory, the
`metadata.name`, the `policy-version` label and the `matchConditions` self-scope.

Follow `render-orphan-guard.py`. It gives a live path, an offline twin and a self-check of runnable
asserts.

The orphan guard is out of scope. It is the aggregate over the array and cannot self-scope to one
claim. [Ticket 22](22-pairing-rules-and-platform-machinery.md) gives it the `platform-machinery`
identity.

## Acceptance criteria

- [x] The renderer emits all seven mandatory members for a named version.
- [x] Each emitted policy carries a versioned `metadata.name`, following the `require-nonroot-1-0-0` pattern.
- [x] Each emitted policy carries the `policy-version` label.
- [x] The self-scope lives in `matchConditions` and never in `matchConstraints.objectSelector`.
- [x] The priority classes carry versioned names, such as `cage-baseline-1-0-0`, and `cage-tier` names its own.
- [x] The renderer renders only the tree being cut. It never re-renders a released tree.
- [x] A `--selfcheck` flag runs asserts and fails when the live path and the offline twin disagree.
- [x] `verify-graded.sh` still cross-checks `cage-tier.yaml`'s dial table against `cage.py`'s `TIERS`, on the authoring copy.
- [x] A comment in the emitted tree records why `objectSelector` is banned. Kyverno flattens it into one shared webhook configuration, and last-reconciled-wins breaks multi-version coexistence.

## Comments

Shipped in `platform` at `51924e0` (cs-12).
