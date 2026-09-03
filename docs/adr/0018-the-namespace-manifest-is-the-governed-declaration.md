---
status: accepted
---

> **Superseded in part, 2026-09-03 (ticket 38, built).** Point 3's refusal of a new ungoverned namespace is gone: every ungoverned namespace is priced as a ramped workload share of the uncaged residual from the first signed tag naming it, and a new one prints as a delta. The rest of point 3 (repo-only walk, cluster drift owned elsewhere) stands. The ADR recording the supersession is ticket 39's (ADR-0026).

> **Superseded in part, 2026-08-28.** §4, the narrowed CREATE claim rule is superseded by [ADR-0022](0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md). The rest stands.

# The Namespace manifest is the governed declaration; the composed artefact carries no namespace list

ADR-0014 made the **governed namespace** the boundary where an inherited rule reaches a workload.
ADR-0015 made it the proposer's scan boundary. Ticket `03` put the baseline name in the adopter's
risk-bearing declaration. So three decisions lean on a namespace set that nothing yet declares. The
question was whether the composed artefact declares it.

## What was already there

Each adopter has exactly one namespace, and it is already a manifest in the adopter's own signed
repo: `driftwood/gitops/apps/namespace.yaml`, and the same for `tuppence` and `ludlow`. Each
carries `policy-as-versioned.dev/institution: <party>`. Flux reconciles it. The gitsign tag that
ADR-0012 reuses for the composed artefact already covers it. Nothing in the estate carries
`policy-as-versioned.dev/governed: "true"` yet.

Two members follow the pod, not any list. `cage-netpol` generates into `object.metadata.namespace`.
The orphan guard is cluster-scoped over every `Pod`. `wargamer.py` scans no manifests at all today.

## The decision

1. **The `governed: "true"` label on the Namespace manifest is the declaration.** The adopter
   writes it, signs it and Flux reconciles it. The composed artefact carries **no namespace list**.
   It records the set only as advisory metadata, next to the parent SHAs, so a verifier can
   re-derive it from the adopter's own manifests.
2. **The two risk-bearing selections live apart.** The baseline name sits in the party artefact.
   The namespace set sits in the Namespace manifest. Both are under the same signed tag. A mirror
   of one into the other is duplicated state.
3. **Composition refuses an ungoverned adopter namespace, and only a new one.** A Namespace
   manifest in the adopter's repo that carries the `institution` label and not `governed: "true"`
   silently exempts every workload in it. That is ADR-0014's hole moved up one level. The rule is
   ticket `03`'s: refuse on a new one, record a pre-existing one, comparing against the last signed
   composed artefact. Cluster drift on the label is Flux drift, owned by the estate's drift tooling.
   Nothing at merge time can see a namespace created by hand.
4. **The governed set narrows the `CREATE` claim rule and nothing else.** The guard reaches every
   claim anywhere. `cage-netpol` follows the pod. No inherited member changes reach.
5. **Only the adopter adds a namespace, by hand, in its own repo.** The proposer never proposes
   one. A new namespace is a scope change, not a priced verdict, and ADR-0015 gives the proposer
   nothing to price it with.

## Considered options

- **The Namespace manifest is the declaration (chosen).** It is already signed, already reconciled
  and already the object the cluster reads. No new format, no new store.
- **The composed artefact lists namespaces and the label is rendered from it.** Rejected. It
  restates a signed fact in a second place. ADR-0013 rejected duplicated state for the catalogue
  prefix, and the reason holds here.
- **Derive the set from the cluster at reconcile time.** Rejected. It cannot be signed, so the
  scope an inherited rule reaches would sit outside the chain ADR-0012 built.
- **Mirror the set into the party artefact next to the baseline name.** Rejected. Duplicated state
  again, and the manifest is the thing the cluster reads.
- **Refuse a composed artefact that names a namespace with no manifest.** Moot. The composed
  artefact names none.

## Consequences

- **The three adopter Namespace manifests must gain `policy-as-versioned.dev/governed: "true"`.**
  Until they do, the first composition records three ungoverned namespaces and refuses on none.
  That first signed artefact is the comparison point from then on.
- **The refusal is a lint over the adopter's own manifests.** It needs no cluster and no
  composition engine. It needs a composition only for the new-versus-recorded comparison.
- **ADR-0015's scan boundary now has a source.** The proposer reads the governed set from the
  adopter's Namespace manifests, which sit in the repo it already runs in.
- **A composed artefact's advisory metadata grows one block**, the governed namespace names. Strip
  it and the file underneath is unchanged. Kyverno never reads it.
- **The fifth named gap is now fully specified.** `platform` builds the `CREATE`-only
  `ValidatingPolicy` from ADR-0014. The adopters label their namespaces. The composition lints for
  the label. Nothing else is needed.
