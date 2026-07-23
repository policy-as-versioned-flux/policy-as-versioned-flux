# RESEARCH: enforcement engine & exemption/shift-left options under a Flux anchor

Type: research
Status: resolved
Blocked by: —

## Question

With Flux fixed as the anchor and everything else open, survey the options the architecture
decision (02), exemptions ledger (05), and shift-left check (03) wait on:

- **Enforcement engines** — Kyverno (CEL ValidatingPolicy) vs alternatives (OPA/Gatekeeper,
  Kubewarden, native ValidatingAdmissionPolicy, jsPolicy…). For each: can it (a) express
  risk-tuned proportionality, (b) run the *same* evaluation **offline** for a shift-left CI/dev
  check, (c) support a first-class, scoped, expiring exemption primitive?
- **Kyverno `PolicyException`** specifically — exact capabilities and limits: scope, expiry,
  matching, and whether it can carry/round-trip external metadata (a risk price, a ledger ref).
- **Flux's load-bearing hooks** — `ResourceSet`, `GitRepository`/`Kustomization`, image automation,
  notifications — what Flux does that makes it genuinely central to versioned distribution, drift-
  heal, prune-on-retire, and per-team cadence (so the design leans on Flux, doesn't decorate it).
- **Crossplane's possible role** — the existing cloud-plane work; could Crossplane model the
  cluster's "supported policy versions" contract, the org's cloud posture, or the risk inputs?
- **Shift-left / version-skew prior art** — briefly: kubectl client/server ±1 skew, Kubernetes API
  discovery, and any "policy compatibility check" patterns to inform 03's contract.

Findings → write to `.scratch/talk-spec/research/08-enforcement-engines.md`; link it back here.

## Answer

Full findings + citations: [`research/08-enforcement-engines.md`](../research/08-enforcement-engines.md).

- **Keep Kyverno `ValidatingPolicy` (CEL, `policies.kyverno.io/v1`, ≥1.18).** It wins on all three criteria and switching engines buys nothing when *Flux*, not the engine, is the fixed anchor — a switch would only cost a language migration (Rego/Wasm/JS) and a rewrite of the working offline shift-left path.
- **(a) Proportionality:** `validationActions` = `Deny`/`Audit`/`Warn`, set per policy, promoted Audit→Deny by editorial PR (never a timer, ADR-0006). `Warn` is an unused middle "nudge-at-deploy" tier worth adopting; numeric thresholds only if 04 needs them.
- **(b) Same eval offline:** `kyverno apply`/`kyverno test` run the *identical* CEL file with no cluster — already what `pr-gate-check.sh` uses. Caveat: the CLI is single-policy, so it can't reproduce the multi-version shared-webhook interaction (that's `verify-coexistence.sh`'s job).
- **(c) Exception:** `PolicyException` is first-class, namespace/resource-scoped, CEL-aware, and surfaces in PolicyReports — but has **no native expiry**. Close it ADR-0006-cleanly via **ledger-entry + Flux `prune` (primary)** and `cleanup.kyverno.io/ttl` label (backstop). It carries a risk price + ledger ref as plain annotations that round-trip git→Flux→cluster→report. Non-transferability (05's wedge-prevention) is native via namespace scope. Requires turning on `enablePolicyException` + `exceptionNamespace` in the Kyverno HelmRelease.
- **Alternatives judged:** OPA/Gatekeeper (good `gator` offline + scoped actions, but *no expiring exception CR* — its weakest point, which is 05's most important criterion — plus a Rego tax); Kubewarden (monitor/protect + `kwctl run` offline, but exceptions live in-policy and it fragments the CEL story with Wasm); native VAP (cleanest `paramRef` model but **no official offline CLI** and no exception object — north-star only, and Kyverno `autogen` can emit VAPs as an escape hatch); jsPolicy (dormant since ~2024 — exclude).
- **Flux is load-bearing in six real jobs:** `ResourceSet` versioning (fan-out from one `inputs.versions[]` array — reuse the same pattern for the ledger), pinned+signed `GitRepository` provenance, `prune: true` retirement, reconcile drift-heal (a real out-of-band-edit failure was caught this way), `dependsOn`+health-gated ordering, and notification-controller as the event spine. Image automation is available but unused (policy isn't a container image) — don't invent a use.
- **Crossplane:** keep as the *cloud plane* (a policy target) it already is. Do **not** promote it to model the "supported policy versions" contract — the `ResourceSet` inputs array already *is* that consumable contract. Its legitimate future lane is feeding *live cloud posture* (`status.atProvider`) into the 06 risk maths, but only if that ticket needs observed cloud state.
- **Shift-left contract (03):** adopt a kubectl-style **±1 policy-version window** (stale-by-one = warn, two = block) over exact-pin or unbounded range; the "server advertises supported versions" step is a *read* of the `ResourceSet` array (live `kubectl get resourceset` or the git file for fully-offline), no new discovery endpoint needed; the check runs the target version's *actual* action via `kyverno apply` so an Audit→Deny promotion is caught before deploy. `paramRef.parameterNotFoundAction` (Allow/Deny) is prior art for "cluster doesn't support this version".
