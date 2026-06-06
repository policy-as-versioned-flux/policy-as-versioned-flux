---
status: accepted
---

# Install & fleet layer: ControlPlane Flux Operator (`FluxInstance` + `ResourceSet`)

Flux is installed and managed via ControlPlane's **Flux Operator** (`FluxInstance`, with
distroless/FIPS-hardened image variants) rather than vanilla `flux bootstrap`, and the
multi-version coexistence matrix (clusters × policy versions — the original's `cluster1`/`cluster2`
crux) is expressed as a **`ResourceSet`** over a table of inputs rather than hand-written
source+Kustomization pairs. This fits the client (the work is for ControlPlane, and this is their
flagship Flux distribution), suits CNS's UK public-sector context (FIPS/distroless), and turns the
coexistence wiring into data.

## Guardrail (important)

The **policy-distribution thesis must remain vanilla-Flux-expressible.** The Flux Operator is the
*install + fleet-templating* layer only — not the policy mechanism. Strip the Operator and
policy-as-versioned-code still works on `flux bootstrap`; you simply hand-write the matrix that
`ResourceSet` would have generated. No ADR (ADR-0001/0002/0003) depends on Operator-only features.

## Considered options

- **Flux Operator (chosen).** FluxInstance + ResourceSet + FIPS/distroless.
- **Vanilla `flux bootstrap` (rejected for the floor).** Maximal portability, no dependency, but
  verbose coexistence wiring and no hardened-image story. Retained as the documented fallback per
  the guardrail.
- **Vanilla floor, Operator in north-star (rejected).** Defers the ControlPlane stack the client
  would want showcased.

## Consequences

- Settles the coexistence-wiring question: **`ResourceSet` matrix** (clusters × policy versions),
  superseding the "N explicit pairs" option for the floor.
- Adds the Flux Operator CRDs (`FluxInstance`, `ResourceSet`, `ResourceSetInputProvider`).
- The reference doubles as a showcase of the ControlPlane Flux stack.
