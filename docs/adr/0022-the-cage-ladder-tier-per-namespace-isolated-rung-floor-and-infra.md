---
status: accepted
---

# The cage ladder: tier per Namespace, tighten-only cage, an `isolated` rung, one floor, `infra` by role

The cage was the only enforcement in vocabulary but not in code (findings H2-01, H2-03, H2-12,
H2-13, H8-03). The tier label was forgeable, an unknown tier fell to the loosest cage, the bottom
rung was a GitHub issue, and the baseline cage wrote `readOnlyRootFilesystem: false` over pods that
set `true`. Decided 2026-08-28 in `.scratch/ecosystem/issues/09`. Provisional: the owner agreed
without a reason.

## The decision

- A tier attaches to a governed **Namespace**. It is declared on the Namespace manifest next to
  `governed: "true"` (ADR-0018), rendered from the signed composed artefact. `cage-tier` reads it
  through `namespaceObject` and writes it onto every pod. The pod label is an output only. A
  governed Namespace with no tier fails closed to `isolated`.
- The cage is **tighten-only**. It never writes a security field looser than the workload declared.
  This lands in every served copy of `cage-tier`, and the computed-semver engine treats "writes
  false over true" as a loosening.
- The ladder is `baseline, restricted, quarantine, isolated, infra`. **`isolated`** is the bottom
  rung: quarantine dials, no ingress, no egress, first eviction. Everything still runs. The £
  selects `isolated` where it selected `deny`. `cage-netpol` generates per-tier reach.
- An adopter may declare one tighten-only **floor** on its party artefact. Selection clamps to the
  floor. Lowering the floor is priced, never refused.
- Only a party with the `platform` role may declare a Namespace at **`infra`**. A declaration
  from any other party renders to `isolated`. The platform's `infra` declaration lands, and the
  truth surface asserts it, before the default for an unlabelled Namespace flips to `isolated`.

## Alternatives

- Tier per workload, on the pod manifest, as `tier_pr.py` does. Rejected: the pod label is the
  forgeable object reversal 13 moved away from.
- Tier baked into the adopter's rendered policy copy. Rejected: it breaks `render_is_faithful` and
  ADR-0018's "no namespace list in the artefact".
- A `replicas: 0` bottom rung. Rejected: that is a refusal under another name.
- A hub-signed allowlist of infra namespaces. Rejected: a second declaration path.

## Consequences

Supersedes ADR-0014's CREATE deny, ADR-0015's "a proposed Deny opens an issue", ADR-0016 §3 (the
artefact carries no tier and no floor) and ADR-0018 §4. The offline test needs a `Values` file
carrying the Namespace; `kyverno apply` 1.18.2 evaluates `namespaceObject` from it (proven
2026-08-28). H8-03 closes when the pod label is an output.
