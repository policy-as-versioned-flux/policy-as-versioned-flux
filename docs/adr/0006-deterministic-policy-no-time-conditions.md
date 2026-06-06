---
status: accepted
---

# Policy code is deterministic — no time-conditional state

Policies must evaluate **deterministically**: the same manifest against the same policy version
must always produce the same result, independent of *when* it is evaluated. We therefore forbid
embedding time-based logic in policy bodies — no expiry dates, no start dates, no "active after / 
inactive after" CEL conditions — even though the engine would let you write them. Time-conditional
policy creates non-deterministic policy states (a deploy that passed yesterday silently fails today
with no change to either the workload or the policy version), which defeats the reproducibility the
whole versioned-dependency model depends on.

## Consequence for governance ("delete-if-undefended")

The mea-culpa's "dated, reviewed, removed-if-undefended" rule is realised as an **editorial action**
on the policy file (a reviewed PR that changes or removes it), **not** as a mechanical date-triggered
behaviour. Review metadata (`created`, `lastReviewed`, rationale, risk) is **advisory input for
humans and agents**, never consumed by the engine to alter enforcement. Removal is always a
reviewed, revertible PR — the same unit of debate as any other policy change.

This supersedes the rejected expiry options (engine hard-expiry; class-aware auto-removal on a
date): all of them embed time, all of them are non-deterministic, none of them ship.
