# 03 — Gate (Deny) ValidatingPolicy + rationale layout

**What to build:** The second enforcement tier: `require-known-department-label` as a Deny gate (the "locked door" — CONTEXT lane-keeping vs gate), plus the rationale layout so every policy carries its "why" (risk, purpose, threat-model grounding) as versioned files alongside the policy body. The engine never reads the rationale (ADR-0006/0007 — advisory metadata is for humans and agents only).

**Blocked by:** 02 — Policy repo scaffold + lane-keeping VP.

**Status:** done

- [x] Gate policy denies a non-compliant fixture and passes a compliant one under `kyverno test`
- [x] `validationActions: Deny`, same nameSuffix + version self-selector pattern as the lane-keeper
- [x] Each of the two policies has a rationale document carrying purpose/risk; the CEL validation logic never references it (the description annotation does, for humans/agents — ADR-0006/0007)
- [x] Fixtures demonstrate the Audit policy reports but admits, while the Deny policy refuses

## Comments

Done 2026-07-14. `policy/workloads/kyverno/require-known-department-label/` — the Deny gate:
same `nameSuffix`/`objectSelector` self-selector pattern as the lane-keeper, CEL only fails a
*present but unrecognised* `department` value (absence is the lane-keeper's job, left in Audit).
`rationale/require-known-department-label/rationale.md` — the "why", including a candid note that
this is the reference demonstrator for the Audit/Deny mechanism split (CONTEXT's own "free-text →
enum" major-bump example), not a claim that department labelling meets the gate's catastrophic-risk
bar.

`policy/verify.sh` extended to loop `kyverno test` + kustomize-substitution over both policies
(still no cluster needed). Added `policy/verify-live.sh`: applies both policies to a live cluster
(`fleet/up.sh`, reused as-is — Flux/GitOps wiring is still out of scope, lands in issue 06) and
proves the checklist's last claim directly, since `kyverno test` evaluates the CEL rule but not
admission-webhook blocking — a pod missing `department` is admitted with a Fail entry in its
PolicyReport (Audit: reports but admits), a pod with an unrecognised `department` is refused by the
admission webhook outright (Deny: refuses). Ran both scripts green against `cluster1`.
