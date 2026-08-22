# 10 — Render the mandatory members into every version tree

Type: task
Status: split
Blocked by: none

**Split on 2026-08-22 into implementation tickets.** This ticket holds the reasoning. The work lives in
[12](12-render-mandatory-members-into-a-version-tree.md).

## Question

Spun out of [ticket 07](07-platform-version-under-the-same-rule.md), which settled the design.
[Ticket 09](09-repair-release-and-pinned-delivery.md) is blocked by this one, because the trees it
publishes are this renderer's output.

Ticket 07 chose **one version mechanism**. Every claim-wide policy becomes a per-version copy,
self-scoped on the claim value, exactly as `require-nonroot` already is. A human must not be able to
omit one, so a renderer writes them.

**The job:** one authoring copy stays under `graded/` and `posture/`. The renderer emits the
per-version copies, and **the emitted copies are committed**. Git and the gate both read real files,
which cs-06 needs, because it parses the YAML.

**The members to render**, for each version in the array:

- `cage-tier` (MutatingPolicy), `cage-netpol` (GeneratingPolicy)
- `stamp-posture` (MutatingPolicy), `posture-trust-boundary` (ValidatingPolicy, the only content `Deny`)
- the three PriorityClasses from `graded/policies/priorityclasses.yaml`, with versioned names such as
  `cage-baseline-1-0-0`, and `cage-tier` naming its own

**A version is four coordinated edits, not a directory.** Emit all four: the directory, `metadata.name`
(`require-nonroot-1-0-0` is the pattern), the `policy-version` label, and the `matchConditions`
self-scope. Put the self-scope in `matchConditions` and never in `matchConstraints.objectSelector`.
`distribution/policies/v1.0.0/require-nonroot.yaml` carries the comment that records why: Kyverno
flattens `objectSelector` into one shared webhook configuration, last-reconciled-wins, which silently
breaks multi-version coexistence.

**Follow `render-orphan-guard.py`.** It is the pattern this estate already owns: a live path, an offline
twin the verify scripts run, and a self-check that fails when the two disagree.

**Do not re-render released trees.** Render only the tree being cut. Re-rendering everything and failing
on any diff would freeze the dial table for ever.

**Keep the one truth `verify-graded.sh` protects.** It already cross-checks `cage-tier.yaml`'s dial table
against `cage.py`'s `TIERS`. The authoring copy stays the subject of that check.

**Out of scope:** the orphan guard. It is the aggregate over the array, cannot self-scope to one claim,
and is numbered by the platform tag. Ticket 11 gives it the identity `platform-machinery`.

## Comments

Raised 2026-08-22 from ticket 07's grilling. See that ticket's section 1 for the reasoning, including
why the anti-forgery pair is rendered rather than exempted, and why a per-version copy does not race.
