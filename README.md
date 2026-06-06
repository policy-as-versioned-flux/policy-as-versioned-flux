# Policy as Versioned Code, on Flux

A faithful-to-intent re-implementation of Chris Nesbitt-Smith's *[Policy as [Versioned] Code](https://talks.cns.me/PolicyAsVersionedCode.html)* [thesis](https://blog.cns.me/posts/policy-versioned-code-mea-culpa-technical-argument-nesbitt-smith-pedef/)
on Flux CD — policy as a semver, signed, versioned dependency, governed by one Kyverno engine across
a Kubernetes workload plane and a Crossplane cloud plane, with reviewed upgrades, multi-version
runtime coexistence, ground-truth compliance, and an agent-assisted human-governance layer.

## Start here

| Document | What it is |
|---|---|
| [docs/PRD.md](docs/PRD.md) | **The product requirements** — the faithful-to-intent build, phased P1→P2→P3 |
| [docs/north-star-modern-reference.md](docs/north-star-modern-reference.md) | The fuller **modern reference** the floor grows into |
| [CONTEXT.md](CONTEXT.md) | The **ubiquitous language** (glossary) — read this to speak precisely |
| [docs/adr/](docs/adr/) | The **decisions** and why (ADR-0001…0008) |
| [docs/upstream/](docs/upstream/) | Upstream **project actions** (the gitsign/Flux #1068 effort) |
| [research/](research/) | The **research dossiers** the design is built on (originals, Flux, synthesis) |

## The decisions, in one breath

Signed git tags (gitsign, keyless) · pinned everywhere + Renovate PR · Kyverno CEL `ValidatingPolicy`
(Audit = lane-keeping, Deny = gate) · cloud plane by forking ControlPlane **collie** (Crossplane +
OSCAL/Lula) · ControlPlane **Flux Operator** + `ResourceSet` matrix · **deterministic** policy (no
time conditions) · **editorial** governance + an **AI agent** layer · **layered ground-truth**
compliance · catch-all **orphan guard** · **no bespoke tooling** · proven **free on KiND**.

## Project actions queued

1. Rework + post the gitsign revival comment on [fluxcd/source-controller#1068](https://github.com/fluxcd/source-controller/issues/1068).
2. Fork + uplift [`controlplaneio/collie`](https://github.com/controlplaneio/collie) (ADR-0004).

## References

See [docs/references.md](docs/references.md) for the full citation registry.
