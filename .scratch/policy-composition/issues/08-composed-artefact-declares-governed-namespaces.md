# 08 — Does a composed artefact declare its governed namespaces

Type: grilling
Status: resolved
Blocked by: none

Graduated from the map's Not yet specified, 2026-08-25, after ticket
[`06`](06-composing-the-remaining-policies.md). Three tickets now need the namespace set declared, and
ticket `06` settled the doubt that kept this in the fog.

**Why it is sharp now.** The map held this back because it was unclear whether the namespace set is
composition business or purely `platform` machinery. Ticket `06` composed the whole live set and found
it **mixes scopes**: `policy-version-orphan-guard` is cluster-scoped over every `Pod`, and
`cage-netpol` generates a `NetworkPolicy` into the pod's own namespace. So the namespace set changes
what an inherited rule actually reaches. That is composition business, not internal machinery.

**What already depends on it.**

- ADR-0014 made the **governed namespace** the boundary where an inherited rule reaches a workload,
  and the scope of the sibling `ValidatingPolicy` that requires a claim on `CREATE`.
- ADR-0015 made it the boundary of the **proposer's** scan over the adopter's committed workload
  manifests.
- Ticket `03` already put the **baseline name** in the adopter's risk-bearing declaration. The
  namespace set sits next to it.

## Question

Does a composed artefact declare the namespace set its inherited rules reach, and what refuses when
the declaration and the cluster disagree?

**Decide:**

1. **Whether the set is declared at all**, or derived from the cluster at reconcile time. A
   declaration is auditable and signable, per ADR-0012. A derivation cannot drift, but it cannot be
   signed either.
2. **Where it lives.** Next to the baseline name in the composed artefact, or in `platform`
   machinery the adopter never writes.
3. **What refuses.** A governed namespace with no composed artefact covering it. A composed artefact
   naming a namespace that does not exist. Neither, or both.
4. **Whether the cluster-scoped members change the answer.** The orphan guard reaches every
   namespace, governed or not. Ticket `04` proved that deny-on-absence there bricks the cluster. So
   the declaration cannot narrow the guard, only the rules that self-scope on the claim.
5. **Who adds a namespace.** Adding one puts workloads under an inherited rule for the first time.
   That is a risk-bearing act, and ADR-0013 already settled that selection is the adopter's.

## Answer

**No. The `governed: "true"` label on the adopter's own Namespace manifest is the declaration, and
the composed artefact carries no namespace list.** Resolved 2026-08-25 by grilling. All five
recommendations accepted.

Facts that settled it. Each adopter has exactly one namespace, and it is already a manifest in the
adopter's signed repo (`driftwood/gitops/apps/namespace.yaml`, and the same for `tuppence` and
`ludlow`), labelled `policy-as-versioned.dev/institution: <party>`. Nothing carries the `governed`
label yet. `cage-netpol` generates into `object.metadata.namespace`, so it follows the pod. The guard
is cluster-scoped. `wargamer.py` scans no manifests today.

1. **Declared, on the manifest.** A list in the composed artefact restates a signed fact in a second
   place, which is the duplicated state ADR-0013 rejected. A derivation cannot be signed. The composed
   artefact records the set as advisory metadata only, next to the parent SHAs.
2. **The split is accepted.** Baseline name in the party artefact, namespace set on the manifest,
   both under one tag.
3. **What refuses.** An adopter namespace with the `institution` label and no `governed` label,
   new against the last signed composed artefact. Pre-existing ones are recorded. Cluster drift is
   Flux drift.
4. **The governed set narrows the `CREATE` claim rule and nothing else.** Ticket `04` already proved
   the guard cannot be narrowed.
5. **Only the adopter adds a namespace, by hand.** The proposer never proposes one. It is a scope
   change, not a priced verdict.

Recorded as [ADR-0018](../../../docs/adr/0018-the-namespace-manifest-is-the-governed-declaration.md)
and an amended **Governed namespace** entry in `CONTEXT.md`. No new tickets. No new fog.
