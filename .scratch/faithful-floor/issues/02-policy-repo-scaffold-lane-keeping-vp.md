# 02 — Policy repo scaffold + lane-keeping (Audit) ValidatingPolicy + fixtures

**What to build:** The versioned policy source comes to life: the policy repo layout (PRD §5.1) with its first policy — the Audit/lane-keeping `require-department-label` — authored as a CEL ValidatingPolicy (ADR-0003) with the kustomize `nameSuffix` + `policy-version` label self-selector coexistence pattern (PRD §6.4), plus `kyverno test` fixtures whose pass/fail cases double as worked examples (the **testable** "-able").

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [x] `kyverno test` runs green locally against pass and fail fixtures
- [x] The policy matches only workloads carrying its `policy-version` label (version self-scoping verified by a fixture)
- [x] Kustomize build renders the policy with the version `nameSuffix` from a single substituted version value
- [x] `validationActions: Audit` — this is the lane-keeper, not a gate

## Comments

Done 2026-07-14. `policy/` — `workloads/kyverno/require-department-label/` (CEL ValidatingPolicy +
kustomization.yaml: the `1.0.0` value in `labels:` drives the CEL `objectSelector` via
`replacements`; `nameSuffix` is a second hand-synced `1.0.0` literal in the same file, since kustomize
has no replacements target for it — see the `ponytail:` comment there), `rationale/require-department-label/rationale.md` (the "why"),
`tests/require-department-label/` (pass/fail/skip fixtures — skip proves version self-scoping).
`policy/verify.sh` is the runnable check (`kyverno test` + kustomize-substitution assertion), both
green.
