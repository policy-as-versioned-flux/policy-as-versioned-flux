# 04 — Whether an unlabelled pod is denied

Type: grilling
Status: resolved
Blocked by: none

Graduated from the map's Not yet specified: "Whether an unlabelled pod is denied." `CONTEXT.md:129`
says the orphan guard denies a pod with a *missing* label. The committed guard's `matchConditions`
skip unlabelled pods entirely, and nothing else denies them. One of the two is wrong.

## Question

Should an unlabelled pod be denied by the orphan guard? Decide which side is correct, `CONTEXT.md`'s
description or the committed guard's behaviour, and what must change to bring the other into line.

## Answer

**The committed guard is correct. `CONTEXT.md` was wrong about the guard and right that a hole
exists.** Those are two different statements, and the question only resolves once both are separated.
Recorded as [ADR-0014](../../../docs/adr/0014-unclaimed-is-caged-governed-namespace-requires-claim.md),
with an amended **Orphan guard** entry and new **Governed namespace** and **De-postured** terms in
`CONTEXT.md`.

### The code is not a lone dissenter

Three committed artefacts agree with each other and disagree with the prose.

1. `estate/platform/distribution/versions.yaml` — the live `ResourceSet` renders a single
   `has-policy-version-label` matchCondition.
2. `estate/platform/distribution/render-orphan-guard.py:40` — the offline twin says "Unlabeled pods are
   out of scope (they claim no version)".
3. `estate/platform/distribution/verify-orphan-guard.sh` — the beat asserts
   `pass: 1, fail: 1, warn: 0, error: 0, skip: 1`. The skip of the unversioned pod is a **pass**
   condition, not an oversight.

### Two independent reasons the prose could not be implemented

**The guard is cluster-scoped and matches every `Pod`.** `matchConstraints` names `apiGroups: [""]`,
`resources: ["pods"]`, `operations: ["CREATE", "UPDATE"]`, and there is no namespace selector. A deny
on a missing label denies CoreDNS, Flux and the Kyverno webhook hosting the guard. It bricks the
cluster on install.

**De-posturing depends on the skip.** `estate/platform/currency-controller/currency.py:20-31` settles a
workload on a retired version by removing **both** the posture label and the version claim in one
patch. It names the reason that patch works: "orphan-guard is out of scope". Remove only the posture
and `stamp-posture` re-clobbers it. Remove only the claim and `posture-trust-boundary` denies the
update. Removing both is called "the ONLY durable re-patch". A guard that denied on absence would deny
that `UPDATE`.

### Absence of a label is three different things

The guard sees one absence and cannot distinguish them.

| situation | example | correct settlement |
|---|---|---|
| infrastructure that never claims | `kube-system`, `flux-system`, Kyverno | out of scope, always |
| a workload the platform stripped | any pod `currency.py` de-postured | **caged**, keeps running |
| a workload that should claim and does not | an evader | **denied**, but at `CREATE` |

Because absence cannot tell them apart, absence alone is never the deny trigger. The guard judges a
**claim**, and only a claim.

### The de-postured pod is the map's own preference in miniature

`currency.py` calls the de-postured state "Keep running but caged", priced into TCoR. The workload
loses its posture SVID and its OpenBao secret, and the residual prices against its party's appetite
band. That is exactly this map's standing preference: never an exemption, and deny is the bottom rung
reached by the £. Denying the de-posture patch would replace a priced cage with a hard stop, which
inverts the preference.

### The hole is real, and the locked-door claim was false

`CONTEXT.md:161` claimed the guard "is what makes the gate tier a locked door rather than an opt-in
door". Under the committed behaviour that sentence is **false, not merely narrow**. Every versioned
policy self-scopes on the claim label, so a workload that omits the label is matched by no policy at
all, gates included. The true, narrower statement is that the guard locks the door against *claiming a
version the fleet does not run*. It does not lock the door against silence.

### What closes the silence: a sibling policy, `CREATE` only

The specified mechanism, for the `platform` repo to build:

- One new `ValidatingPolicy`, **beside** the orphan guard, never folded into it. The guard's allow-list
  is rendered from the version array, and the array has nothing to say about silence.
- Scoped by a namespace label, `policy-as-versioned.dev/governed: "true"`. The prefix matches the
  estate's existing `policy-as-versioned.dev/policy-version` and `policy-as-versioned.dev/policy`. **No
  such namespace-label convention exists in the estate today.**
- Matches **`CREATE` only**. This is the load-bearing detail. De-posture is an `UPDATE`, so it still
  passes and the caged workload keeps running.
- The workload cannot return unclaimed, because its controller recreates it and `CREATE` denies it.
  That is the same lever `currency.py:35-37` already uses for `--action evict`.
- A namespace scope is a match constraint, not an **exemption**. It states where a rule applies. It is
  not a carve-out for a named party that cannot meet the rule.

### Honesty note

A plain reader of `CONTEXT.md` and the guard side by side finds this contradiction. Composition was not
needed to find it. What composition adds is the last consequence: a parent's rules reach a child's
workloads only inside the child's governed namespaces, so the namespace label becomes part of what an
adopter declares.

### Handed to `platform`

Building the policy is a fifth named gap for the `platform` repo, joining the four from ticket
[`01`](01-does-composition-hold-up.md). Every governed namespace must be labelled before the policy
goes to Deny, because an unlabelled namespace silently exempts every workload in it. That is the same
hole moved one level up. Start it in Audit and promote by editorial PR, as the orphan guard's own entry
already allows.
