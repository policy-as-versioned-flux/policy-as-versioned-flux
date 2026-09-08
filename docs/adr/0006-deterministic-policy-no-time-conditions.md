---
status: accepted
---

# Policy code is deterministic — no time-conditional state

> **Note, 2026-09-08 (eco-system ticket 84, delegated under ADR-0025).** The £ now has a date, and
> the policy bodies still do not. Composition prices "as of" one date: the newest SIGNED date among
> its own inputs (every pinned envelope's `published_at`, every edge's own `since`), or the caller's
> `compose --as-of`. The feeds module's `eol` converter ramps to it and a pin behind a newer signed
> major is surcharged by the same ramp from the day that tag was cut. None of this reaches a
> `ValidatingPolicy`, a `MutatingPolicy` or a `GeneratingPolicy`: composition's own selfcheck proves
> the rendered policy files are byte-identical across every signature state and every as-of, and
> that the module reads no clock. The composition an adopter SIGNS passes no `--as-of`, so it
> re-derives from signed facts alone; only the scheduled proposer passes the day it runs on, and it
> commits nothing (ADR-0024). So the rule this ADR states -- the same manifest against the same
> policy version always produces the same verdict -- stands untouched; what moves with the date is
> a price beside the verdict, printed with both of its dates.

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

## Later extension: timed nudges to humans are not timed enforcement

[ADR-0010](0010-sunset-scheduled-proposals-not-application.md) draws the boundary this ADR implies
but doesn't name explicitly: a date may trigger a *reminder to a human* (a dashboard countdown, an
escalating issue, a machine-opened proposal PR) without becoming *time-conditional policy state* —
as long as nothing timed ever changes an admission verdict on its own, and every resulting change
still lands via a reviewed, human-merged PR. Fleet-side sunset scheduling uses exactly this
pattern.
