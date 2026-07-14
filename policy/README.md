# policy

The versioned policy source (PRD §5.1). Tagged semver releases of this repo
*are* the dependency consumers pin — see [CONTEXT.md](../CONTEXT.md) and
[ADR-0001](../docs/adr/0001-transport-signed-git-tags-gitsign.md)/[ADR-0002](../docs/adr/0002-adoption-pinned-plus-renovate-pr.md).

```
workloads/kyverno/<policy-name>/   ValidatingPolicy (CEL) + kustomization.yaml
                                    (nameSuffix + policy-version self-selector,
                                    substituted from one value — PRD §6.4)
rationale/<policy-name>/            the "why": rationale.md
tests/<policy-name>/                kyverno test fixtures (pass/fail/skip =
                                    worked examples — the "testable" -able)
```

Run `./verify.sh` to check out a policy end-to-end (`kyverno test` fixtures +
kustomize version substitution).
