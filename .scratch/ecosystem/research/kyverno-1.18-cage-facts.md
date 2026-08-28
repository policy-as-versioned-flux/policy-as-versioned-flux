# Kyverno 1.18.2 cage facts (MutatingPolicy / ValidatingPolicy / GeneratingPolicy)

Researched 2026-08-28 against kyverno.io (v1.18 build at release-1-18-0.kyverno.io), the `release-1.18` branch of kyverno/kyverno, GitHub issues/PRs, and deepwiki/context7 for orientation only (every claim below re-checked against source). v1.18.0 published 2026-04-29, v1.18.2 published 2026-07-10 (GitHub releases API).

Note: the policies API group in `release-1.18` is `policies.kyverno.io/v1beta1` (listers, CRDs); `v1alpha1` is the older served version. Check `kubectl api-versions` on the target cluster before pinning.

## 1. `namespaceObject` and `matchConstraints.namespaceSelector` in MutatingPolicy

**Fact.** Both exist in 1.18.
- `namespaceObject` is a bound CEL variable. The CRD description lists `'namespaceObject' - The namespace object that the incoming object belongs to`, and the compiler binds it: `cel.Variable(compiler.NamespaceObjectKey, compiler.NamespaceType.CelType())` (`pkg/cel/policies/mpol/compiler/compiler.go:128`) and injects it at eval (`eval.go:60`). This was fixed by PR #15625 "fix: inject namespaceObject into MutatingPolicy CEL context", milestone 1.18.0, closed 2026-04-15 (before 1.18.0 cut); the v1.18.0 release notes carry "Inject namespaceObject into MutatingPolicy CEL context". Before 1.18.0 it compiled but was not populated.
- `matchConstraints.namespaceSelector` is in the CRD schema. Engine resolves the namespace via `nsResolver` and passes it to `matcher.Match(...)` and `CompiledPolicy.Evaluate(ctx, attr, namespace, ...)` (`pkg/cel/policies/mpol/engine/engine.go:148-151, 181-189`). Namespace is `nil` when `request.Namespace == ""`; write expressions null-safe (`namespaceObject != null && ...`).

**Confidence.** High (source + release note).
**Citations.** https://github.com/kyverno/kyverno/pull/15625 ; https://github.com/kyverno/kyverno/releases/tag/v1.18.0 ; https://raw.githubusercontent.com/kyverno/kyverno/release-1.18/config/crds/policies.kyverno.io/policies.kyverno.io_mutatingpolicies.yaml ; https://github.com/kyverno/kyverno/blob/release-1.18/pkg/cel/policies/mpol/engine/engine.go ; https://release-1-18-0.kyverno.io/docs/policy-types/mutating-policy/

## 2. Issues #9975 / #13605 and offline namespace evaluation in the CLI

**Fact.**
- #9975 "[Bug] [CLI] Errors upon using `namespaceObject` in Kyverno CEL expressions" — closed, milestone 1.12.1, fixed by PR #9977 (ClusterPolicy CEL subrule era).
- #13605 "[Bug] [CLI] Panic when using `namespaceSelector` in ValidatingPolicies" — closed, fixed by PR #13636, milestone 1.15.0.
- 1.18 CLI offline path: `kyverno apply`/`test` build the mpol engine with `mpolengine.NewEngine(provider, p.Variables.Namespace, matching.NewMatcher(), ...)` (`cmd/cli/kubectl-kyverno/processor/policy_processor.go:321`). `Variables.Namespace(name)` returns a `corev1.Namespace` from the values file: first the `namespaces:` list (full Namespace objects), then `namespaceSelector:` entries (name + labels synthesised into a Namespace) (`cmd/cli/kubectl-kyverno/variables/variables.go:46-70`; fields in `apis/v1alpha1/values_spec.go:18-22`). So `namespaceObject` and `namespaceSelector` evaluate offline **only via the values file**, not by putting a `kind: Namespace` in `--resource`. The `namespaceCache` in `apply/command.go:521` is a separate map used for ClusterPolicy/cleanup label lookups, not the mpol resolver. `--cluster` swaps in a live client.

Minimal values file:
```yaml
apiVersion: cli.kyverno.io/v1alpha1
kind: Values
namespaces:
  - apiVersion: v1
    kind: Namespace
    metadata: {name: prod, labels: {tier: gold}}
```

**Confidence.** High on issue status; high on mechanism (read from release-1.18 source); medium that `kyverno test` wires identically (same processor, not separately traced).
**Citations.** https://github.com/kyverno/kyverno/issues/9975 ; https://github.com/kyverno/kyverno/issues/13605 ; https://github.com/kyverno/kyverno/blob/release-1.18/cmd/cli/kubectl-kyverno/processor/policy_processor.go ; https://github.com/kyverno/kyverno/blob/release-1.18/cmd/cli/kubectl-kyverno/variables/variables.go ; https://github.com/kyverno/kyverno/blob/release-1.18/cmd/cli/kubectl-kyverno/apis/v1alpha1/values_spec.go ; https://kyverno.io/docs/kyverno-cli/reference/kyverno_apply/

## 3. Tighten-only (conditional) mutation

**Fact.** Yes. Mutations are CEL expressions; the v1.18 MutatingPolicy doc uses `has()` and ternaries in `applyConfiguration` (e.g. `has(object.metadata.labels) && has(object.metadata.labels.environment) ? Object{...} : Object{...}`). CEL optional types (`?.`, `orValue()`) are available since Kubernetes 1.29 and used in Kyverno's own library docs (`object.spec.?initContainers.orValue([])`). JSONPatch entries may evaluate to `null` and be filtered (`.filter(p, p != null)`), which is the idiom for "do nothing".

Tighten-only JSONPatch (set `readOnlyRootFilesystem: true` only when unset or `false`; never downgrade an existing `true`):
```yaml
mutations:
  - patchType: JSONPatch
    jsonPatch:
      expression: >-
        object.spec.containers.map(c, c)
          .filter(c, !c.?securityContext.?readOnlyRootFilesystem.orValue(false))
          .map(c, JSONPatch{
            op: "add",
            path: "/spec/containers/" + string(object.spec.containers.indexOf(c)) + "/securityContext/readOnlyRootFilesystem",
            value: true
          })
```
`add` on a missing `securityContext` parent fails in JSON Patch; guard with a preceding patch that adds `securityContext: {}` when `!has(c.securityContext)`, or use ApplyConfiguration, which merges:
```yaml
  - patchType: ApplyConfiguration
    applyConfiguration:
      expression: >-
        Object{spec: Object.spec{containers: object.spec.containers.map(c,
          Object.spec.containers{name: c.name,
            securityContext: Object.spec.containers.securityContext{readOnlyRootFilesystem: true}})}}
```
ApplyConfiguration is server-side-apply semantics: it always writes `true`, so it can never write `false` over `true`; it is tighten-only by construction. Guard with `matchConditions` if you also want to skip pods that already have `true`.

**Confidence.** High on mechanism; medium on exact snippet syntax (not executed here; `indexOf` on a list of objects is not standard CEL, prefer iterating by index via `range` or ApplyConfiguration).
**Citations.** https://release-1-18-0.kyverno.io/docs/policy-types/mutating-policy/ ; https://kyverno.io/docs/policy-types/cel-libraries/ ; https://kubernetes.io/docs/reference/using-api/cel/ ; https://kubernetes.io/docs/reference/access-authn-authz/mutating-admission-policy/

## 4. Admission order

**Fact.** MutatingPolicy is served from a `MutatingWebhookConfiguration` (`buildPolicyMutatingWebhookConfiguration`, `pkg/controllers/webhook/controller.go:786`) and ValidatingPolicy from a `ValidatingWebhookConfiguration` (`:527`). Kubernetes runs all mutating webhooks first, then validating: "Mutating admission webhooks are invoked first... After all object modifications are complete... validating admission webhooks are invoked". Kyverno's own doc: "all mutations happen first followed by all validations". So a ValidatingPolicy sees the mutated object on the same request. Order *among* MutatingPolicies is not guaranteed (v1.18 doc); use `reinvocationPolicy: IfNeeded` if one mutation depends on another.

**Confidence.** High.
**Citations.** https://github.com/kyverno/kyverno/blob/release-1.18/pkg/controllers/webhook/controller.go ; https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/ ; https://kyverno.io/docs/introduction/admission-controllers/

## 5. GeneratingPolicy: per-label output and sync teardown

**Fact.** `generate` is a CEL expression that calls `generator.Apply(namespace, [resources])`; a ternary or `variables` keyed on `object.metadata.labels['tier']` can build a different NetworkPolicy per tier in one policy. On trigger UPDATE with `synchronize` enabled, the webhook creates an UpdateRequest with `Synchronize: true` (`pkg/webhooks/resource/gpol/handler.go:115-125`); the background controller then calls `watchManager.DeleteDownstreams(policyKey, trigger)` **before** re-evaluating and regenerating (`pkg/background/gpol/generate_controller.go:91-92`). The doc's sync table states "Modify trigger: Downstream deleted" (with sync). So a label change deletes the old NetworkPolicy and generates the new one; without sync the old one is left in place. Note: 1.18.2 added "enforce namespace boundary in generator.apply()".

**Confidence.** High (source + doc); medium that regeneration succeeds atomically (delete-then-create, brief gap).
**Citations.** https://kyverno.io/docs/policy-types/generating-policy/ ; https://github.com/kyverno/kyverno/blob/release-1.18/pkg/webhooks/resource/gpol/handler.go ; https://github.com/kyverno/kyverno/blob/release-1.18/pkg/background/gpol/generate_controller.go ; https://github.com/kyverno/kyverno/releases

## 6. `paramKind` / `params` in MutatingPolicy

**Fact.** No. The 1.18 MutatingPolicy CRD has no `spec.paramKind` (nor does ValidatingPolicy); the CEL variable description still mentions `params` as "Only populated if the policy has a ParamKind", inherited from the upstream MAP text, but nothing populates it. The CLI's `--parameter-resource` flag is documented as "resource files that act as ValidatingAdmissionPolicy/MutatingAdmissionPolicy parameters" and in the processor `ParameterResources` are added only for VAP/MAP (`policy_processor.go:248-254`), not for MutatingPolicies (`:358+`). Use `variables` + `globalcontext`/`resource.Get()` (`--context-file` offline) instead of params.

**Confidence.** High.
**Citations.** https://raw.githubusercontent.com/kyverno/kyverno/release-1.18/config/crds/policies.kyverno.io/policies.kyverno.io_mutatingpolicies.yaml ; https://github.com/kyverno/kyverno/blob/release-1.18/cmd/cli/kubectl-kyverno/processor/policy_processor.go ; https://github.com/kyverno/kyverno/blob/release-1.18/docs/user/cli/commands/kyverno_apply.md
