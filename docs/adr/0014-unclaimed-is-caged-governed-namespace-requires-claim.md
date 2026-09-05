---
status: accepted
---
> **Superseded in part, 2026-08-28.** the CREATE deny on a governed namespace is superseded by [ADR-0022](0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md). The rest stands.
>
> **Amended 2026-09-05 (eco-system ticket 91, delegated under [ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md)).** Two things this ADR says about the currency controller are now wrong, and the `CREATE`-only decision they were used to justify is still right for a better reason.
>
> 1. *"the de-posture patch ... removing **both** the posture label and the version claim"* describes a patch that, under [ADR-0022](0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md)'s ladder, **cages nothing**. Removing the claim takes the pod permanently out of the cage mutation's scope, so a patch that names no tier leaves the pod at whatever rung admitted it, for the rest of its life. The controller now writes `posture.acme.io/tier: isolated` and asserts the caged label in the same update, so the workload actually reaches the bottom rung. It is a **re-cage**, not a de-posture; `CONTEXT.md`'s **Currency controller** entry is the term.
> 2. *"the same lever `currency.py` already uses for its `--action evict` path"* names a lever that no longer exists. Eviction is gone, and the grant carries no `delete` on pods: the estate never removes a workload (ticket 75 Q5, the owner's own reason). A recreated pod is handled by admission alone.
>
> The `CREATE`-only match on `governed-namespace-requires-claim` is unchanged and still load-bearing: the re-cage patch is an `UPDATE` that strips the claim, and a guard matching `UPDATE` would refuse it. What changed is only what the patch does afterwards. `verify-currency.sh` now asserts that `operations == ['CREATE']` off the renderer itself, so a future promotion breaks the check rather than every re-cage in the estate.
>
> Two further corrections this ADR's own reasoning needs, both found by review on 2026-09-05 and neither previously written down anywhere.
>
> 3. *"de-posturing is the estate's own cage"* is true only where a reach cage already exists. Every **served** copy of the reach-generating policy is gated on the claim (`only-this-policy-version`), and the patch removes the claim — so the re-caged pod cannot **generate** its own `cage-reach-isolated`; it can only be **selected** by one its namespace already carries. In a namespace with none, "caged" is a label and not a cage. The check derives that from the served bodies and confirms the NetworkPolicy exists **before** running a pass, because the pass strips a live pod's claim and there is no undo.
> 4. The skip this ADR grants the patch has a price, and it is the mirror of the reason it was granted. A pod outside the guard's scope is also outside the cage mutation's and the orphan guard's, so its rung is held by a label **no admission will ever re-assert** — a claiming pod's rung is re-clobbered from its Namespace on every update, a re-caged pod's is not. What holds it instead is RBAC: a workload cannot patch its own pod. Relatedly, `infra` is a role declaration and not a rung, so a pod carrying it is **overwritten** with the bottom rung rather than moved along the ladder.

> **Amended 2026-09-05 (eco-system ticket 89), after ticket 91 and agreeing with it.** The
> `Deny` this ADR's title argues against is gone from what the platform RENDERS: the rule is a
> `MutatingPolicy` (`distribution/render-governed-namespace-guard.py`) and an unclaimed pod is
> admitted onto the bottom rung, with a paired `Audit` report keeping the observation the `Deny`
> used to make. The 2026-08-28 banner above was not true of the shipped policy when it was
> written -- ADR-0022's addendum of the same day promoted this rule to `Deny`, so the record said
> the deny was gone while the code shipped it, for another eight days. It is gone from the source
> now; the copies the three adopters composed under platform `v2.0.1` still carry it until the
> owner cuts the next signed tag and each re-pins, which `verify/deny-is-not-a-rung/` grades and
> names rather than reading green over.
>
> Two consequences below are void with it. "Every governed namespace must be labelled before that
> policy goes to Deny" -- it never goes to Deny. "A brownfield estate should start the policy in
> Audit and promote by editorial PR" -- there is nothing to promote to. What replaces both: a
> brownfield estate declares `overlay.floor` and prices the move, because lowering a floor is
> priced and never refused (ADR-0022). `verify-orphan-guard.sh` did NOT stay as it was either:
> it made the denial its pass condition, and it grades the cage now.
>
> **The `CREATE`-only match is unchanged, and ticket 91's reason for it is the operative one.**
> Ticket 89 round 2 briefly put `UPDATE` on this policy, gated on `posture.acme.io/caged`, and
> that was wrong twice over: the marker is written by `cage-tier` for its whole population at
> every rung, so the gate matched a pod caged at `baseline`; and applying the bottom-rung body to
> a running pod appends a `waf-sidecar` and rewrites `priorityClassName` and `priority`, all
> immutable, which the API server refuses. It would have refused `recage_patch()` precisely --
> the patch this ADR's amendment above exists to protect. The `UPDATE` half is now a separate
> labels-only policy (`governed-namespace-cage-holds`) that re-asserts `tier` and `caged` and
> touches nothing else, so a caged pod cannot relabel its way out of its reach cage and the
> re-cage patch stays admissible. Measured, not argued: `verify-governed-namespace-guard.sh`
> step 5 runs `recage_patch()`'s own object through it.


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
