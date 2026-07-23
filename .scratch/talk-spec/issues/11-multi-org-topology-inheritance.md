# Multi-org topology & shared-tooling inheritance (incl. the archive-flux migration)

Type: prototype
Status: resolved
Blocked by: 02

## Question

Design how the six orgs relate — specifically how the shared discipline in
`policy-as-versioned-platform` is **inherited** by the three institutions, and how we migrate off
the existing estate. Pin:

- **Inheritance mechanism** — how does an institution consume `platform`'s tooling as a pinned,
  signed dependency? (the linting `config-base` model one level up). What's inherited (distribution
  templates, FAIR engine, ledger pattern, shift-left harness, OSCAL plumbing) vs owned per org
  (policies, risk skin, apps). Does Flux itself distribute the platform layer into each institution
  cluster?
- **Cluster shape** — one KiND cluster per institution (3), or one multi-tenant cluster? All three
  must be live (per ticket 01). Trade real-ness vs machine cost.
- **The migration** — the current `policy-as-versioned-flux` org holds the estate we're refactoring
  *from*. Plan the migration of its useful parts into `platform` + the institutions, then
  **archive `policy-as-versioned-flux` as the final step** (decided in 01). The current live
  cluster/demo must keep working until the new estate is proven — do not archive early.
- **What survives vs is rebuilt** — audit the current repos (policy, fleet, pr-gate-action,
  c2p-collector, handbook-generator, governance-agent, the apps) against the new design; decide
  keep / refactor-into-platform / rebuild / drop.

Output: the topology + inheritance design + a migration plan with archive-flux as the last step.

## Answer

- **Build fresh — no migration (2026-07-23).** The estate is fictitious; there is no real cost to
  rebuilding, so we do *not* fork `policy-as-versioned-flux` to save rework. Build the six orgs
  clean. The old estate is **research-only**: reference it like any external source, judge any
  pattern on merit, **never assume its code carries relevant value or cargo-cult it.**
- **Cluster shape:** a real KinD cluster per institution (three, separate — Q2). Per-institution
  multi-cluster (e.g. a dev cluster) is affordable and on the table for the shift-left beat.
- **Inheritance:** `platform` (the discipline) is consumed by each institution as a **pinned,
  signed dependency** — the linting-`config-base` pattern one level up; mechanism is build-detail.
- **Archive `policy-as-versioned-flux`** once the new estate stands (the last step).
- Subsystem diagram lives in [`../the-whole-model.md`](../the-whole-model.md).
