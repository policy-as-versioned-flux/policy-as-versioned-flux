---
status: accepted
---

# An unclaimed pod is caged, not denied; a governed namespace requires a claim at CREATE

`CONTEXT.md` said the orphan guard denies a workload whose `policy-version` label is "missing or not
in" the installed version set. The committed guard does not. Its `matchConditions` carry a single
`has-policy-version-label` test, so an unlabelled pod is skipped. Three artefacts agree with the code
and disagree with the prose: the `ResourceSet` template in
`estate/platform/distribution/versions.yaml`, its offline twin
`estate/platform/distribution/render-orphan-guard.py`, whose docstring states "Unlabeled pods are out
of scope (they claim no version)", and the beat
`estate/platform/distribution/verify-orphan-guard.sh`, which asserts `skip: 1` for the unversioned pod
as a **pass** condition. One of the two had to be wrong.

**The code is right about the guard, and the prose is right that a hole exists.** They are not the
same statement, and resolving this needed both halves.

**Absence of a label is not one thing.** It covers three situations that the guard cannot tell apart:
infrastructure that never claims and never should (`kube-system`, `flux-system`, Kyverno itself); a
workload the platform deliberately stripped; and a workload that should claim and does not. The guard
is cluster-scoped with no namespace selector, and matches every `Pod` on `CREATE` and `UPDATE`. Denying
on absence would therefore deny CoreDNS, Flux and the policy engine that hosts the guard. So **absence
alone is never the deny trigger**. The guard judges a claim, and only a claim.

**De-posturing depends on the skip, and de-posturing is the estate's own cage.**
`estate/platform/currency-controller/currency.py` settles a workload whose version was retired by
removing **both** the posture label and the version claim in one patch. Its docstring names the reason
that works: "orphan-guard is out of scope". It calls the result "Keep running but caged", priced into
TCoR. That is this map's standing preference in miniature — deny is the bottom rung, reached by the £,
and there is never an exemption. A guard that denied on absence would deny that `UPDATE` and break the
only durable re-patch the controller has.

**The hole is real, and a sibling policy closes it.** A workload that simply omits the label is matched
by no versioned policy at all, gates included. So the gate tier is an opt-in door, not the locked door
`CONTEXT.md` claimed. A second `ValidatingPolicy`, **beside** the orphan guard and not inside it,
denies an unclaimed pod inside a **governed namespace**, marked by
`policy-as-versioned.dev/governed: "true"`. It matches **`CREATE` only**. `UPDATE` is excluded
deliberately, so the de-posture patch still passes and the caged workload keeps running. The workload
cannot return unclaimed, because its controller recreates it and `CREATE` denies it — the same lever
`currency.py` already uses for its `--action evict` path.

## Considered options

**Which side of the contradiction is correct**

- **The committed guard (chosen).** The cluster-wide, all-`Pod` match makes deny-on-absence a cluster
  brick, and it would break de-posturing. Two independent reasons, either sufficient.
- **`CONTEXT.md` as written.** Rejected on the facts above. It also had no owner for the three
  meanings of absence.

**What closes the silence hole**

- **A sibling namespace-scoped policy, `CREATE` only (chosen).** One policy, no new machinery, and the
  scope boundary is a namespace label the cluster already understands. `CREATE`-only is what keeps
  de-posturing legal.
- **Widen the orphan guard itself.** Rejected: it conflates judging a claim with requiring one, and the
  guard's allow-list is rendered from the version array, which has nothing to say about silence.
- **Match `CREATE` and `UPDATE`.** Rejected: it re-breaks the de-posture patch, which is an `UPDATE`.
- **An exemption list for infrastructure namespaces.** Rejected on the map's standing preference.
  Exemptions are banned. A namespace label is a match constraint that says where the rule applies, not
  a carve-out for a named party that cannot meet it.
- **Name the hole and stop.** Rejected: it hands the `platform` repo a complaint and no design.

## Consequences

- **`platform` must build one new `ValidatingPolicy`.** It is a fifth named gap for that repo, joining
  the four this map's ticket 01 found. This map names it. It does not fix it.
- **Every governed namespace must be labelled before that policy goes to Deny.** An unlabelled
  namespace silently exempts every workload in it, which is the same hole moved one level up. A
  brownfield estate should start the policy in Audit and promote by editorial PR, exactly as the orphan
  guard's own entry already allows.
- **The locked-door claim is narrowed, and the narrowing is recorded.** The guard locks the door
  against claiming a version the fleet does not run. It does not lock the door against silence. The
  `CONTEXT.md` **Orphan guard** entry now says so.
- **A de-postured workload is a first-class state, not an accident.** `CONTEXT.md` gains
  **De-postured** and **Governed namespace** terms, because both are load-bearing and neither was
  written down.
- **`verify-orphan-guard.sh` stays as it is.** Its `skip: 1` assertion is correct and now has a stated
  reason. The new policy needs its own beat, with its own fixture namespaces.
- **The composition inherits the boundary.** A parent's rules apply to a child's workloads only inside
  the child's governed namespaces, so the namespace label is part of what an adopter declares.
