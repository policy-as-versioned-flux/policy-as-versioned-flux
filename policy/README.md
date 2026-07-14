# policy

The versioned policy source (PRD §5.1). Tagged semver releases of this repo
*are* the dependency consumers pin — see the hub repo's
[CONTEXT.md](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/main/CONTEXT.md) and
[ADR-0001](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/main/docs/adr/0001-transport-signed-git-tags-gitsign.md)/[ADR-0002](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/main/docs/adr/0002-adoption-pinned-plus-renovate-pr.md).

```
workloads/kyverno/<policy-name>/   ValidatingPolicy (CEL) + kustomization.yaml
                                    (nameSuffix + policy-version self-selector,
                                    substituted from one value — PRD §6.4)
rationale/<policy-name>/            the "why": rationale.md
tests/<policy-name>/                kyverno test fixtures (pass/fail/skip =
                                    worked examples — the "testable" -able)
```

Two worked examples, one per enforcement tier (CONTEXT.md, lane-keeping vs
gate):

- `require-department-label` — `validationActions: Audit`, the lane-keeper.
- `require-known-department-label` — `validationActions: Deny`, the gate.

Run `./verify.sh` to check out both policies end-to-end (`kyverno test`
fixtures + kustomize version substitution) — no cluster needed. Run
`./verify-live.sh` against a live cluster (`fleet/up.sh`) to see the
enforcement-action difference for real: the Audit policy reports a failure
but admits the pod, the Deny policy refuses admission outright.
