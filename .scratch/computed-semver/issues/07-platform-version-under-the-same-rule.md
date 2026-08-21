# 07 — Bind the platform's own version to the rule it distributes

Type: task
Status: open
Blocked by: 05

## Question

`CONTEXT.md` defines the rule for "the whole policy body". But `platform` ships a versioned artefact
that institutions pin, and a platform bump edits the version array — which changes which policies are
installed, which changes verdicts. Settled at charting: **the same rule binds it.**

**The job:** make a platform release compute its bump the same way a policy release does. A platform
change that adds a version to the array, retires one, or alters the orphan-guard's allow-list can flip
a workload's admission outcome, and the version number must say so.

Note this is the reflexive argument the estate already makes elsewhere — the apparatus prices its own
risk against its own £10k band and passes its own test. Exempting the distribution layer from the
versioning rule the distribution layer enforces would be precisely the self-exemption
`honesty/reflexive.py` exists to refuse.

Watch for the case where retiring a version is the *whole* change: a workload pinned to the retired
version is matched by nothing afterwards. Whether that is major (its verdict changed) or out of scope
(it was already unsupported) is exactly the sort of edge the verdict-semantics ticket should have
settled — check that it did, and raise it back there if not.

## Comments

Finding raised 2026-08-21 from [ticket 03](03-what-is-the-corpus.md). **This ticket is bigger than its
title.** It is written as "bind the platform's own *version*", but the real gap is that most of the
platform's policy carries no version at all.

`platform` holds eight live Kyverno policies. **Three carry a version:**

- `distribution/policies/v1.0.0/require-nonroot.yaml`
- `distribution/policies/v2.0.0/require-nonroot.yaml`
- `policy/policies/v1.0.0/may-run-root-if-attested.yaml`

**Five do not:**

- the orphan guard rendered from `distribution/versions.yaml`
- `graded/policies/cage-tier.yaml` (MutatingPolicy)
- `graded/policies/cage-netpol.yaml`
- `posture/policies/posture-trust-boundary.yaml`
- `posture/policies/stamp-posture.yaml` (MutatingPolicy)

Two of the five mutate **every** claiming pod. `cage-tier.yaml`'s dials live in it as a CEL map:
`baseline` stamps `cpu: 500m`, `restricted` `250m`, `quarantine` `100m`. Editing one of those numbers
changes the spec of every caged pod in the estate, and no version number says so. Under `CONTEXT.md`'s
own rule that edit is **major**, because a pod that cannot schedule under a tightened limit is
refused.

Ticket 03 settled the gate's behaviour here: the subject is **every** Kyverno policy that can reach a
pod, and when observed movement traces to a policy carrying no version the gate **fails and names the
file**. There is no version number that can describe that change. So this ticket now has a forcing
function — the gate will not go green until the unversioned five are either brought under a version
line or shown to be incapable of moving a verdict.

Note the ADR-0002 tension to settle here, not in the corpus: `versions.yaml` is simultaneously the
version *array* (data the orphan guard ranges) and an unversioned *policy* (the guard itself). Ticket
03 treats it as both, which is honest but leaves this ticket to decide whether the platform's version
covers the guard's own CEL.

Also unresolved and inherited: `distribution/policies/v1.0.0/` and `policy/policies/v1.0.0/` are
separate trees in the same repo, each declaring its own `v1.0.0`, and `versions.yaml` reconciles only
the first. Ticket 03 makes the gate refuse a same-version-different-content collision, which surfaces
the question. Deciding whether they are one version line or two belongs here.
