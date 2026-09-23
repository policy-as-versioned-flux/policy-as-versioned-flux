# 130 — The composed root machinery has no delivery route

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-23 by the integrator, from ticket 111's "Also named, not built" and a read-only
map of the rollout. It blocks the adopters' move to policy 5.0.0, which the owner accepted on
2026-09-23.

Platform's composer renders three kinds of machinery at the root of an adopter's `composed/`
tree, not under `composed/policies/v*/`: the orphan cage (`composed/orphan-guard.yaml`), the
governed-namespace cages, and the unsuffixed `cage-isolated` PriorityClass they name. Measured by
the rollout map at platform main:

1. Each adopter's composed ResourceSet (`gitops/composed/composed-set.yaml`) reconciles only
   `composed/policies/v*/`. The root machinery reaches no cluster.
2. At the adopters' implementations pin today (`v2.0.1`) the orphan guard renders
   `validationActions: [Deny]`, and `composed-set.yaml` installs its own inline Deny orphan guard
   (lines 115-157 in driftwood). At platform main it renders `[Audit]` beside an orphan cage.
3. So when an adopter moves its implementations pin past `v3.0.0`, one of two things happens.
   Either the inline Deny stays and the new Audit plus cage never arrive, or the inline guard is
   dropped and an orphan claim reaches no cage at all.
4. Fact 4 of the lane sample compares the live guard with the offline render, so it can read
   FALSE after the move.

What this ticket owes:

1. A delivery route for every object the composer renders at the `composed/` root, decided and
   recorded with its reason. Candidates: a second Kustomization over the root, or the composer
   rendering the machinery under the version directory it belongs to.
2. The inline orphan guard in each adopter's `composed-set.yaml` is replaced by the delivered
   machinery, with nothing left uncaged in between.
3. A check, offline, that every object under `composed/` is reached by some Kustomization the
   adopter serves, and a planted object outside every path that the check refuses.
4. It lands before, or in the same PR as, each adopter's composed-set move to the new tag.

## Done

Every object the composer renders reaches the cluster through a route the adopter serves, the
inline guard is retired without a gap, and the offline check holds it.
