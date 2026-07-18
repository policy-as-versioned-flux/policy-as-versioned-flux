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

## Follow-up (2026-07-18): a real, systemic broken cross-reference, fixed on `main` only

A wave-4 skeptic found the `policies.kyverno.io/description` annotation's rationale.md
cross-reference had a broken relative path in 3 of 5 policies (`require-department-label`,
`require-known-department-label`, `require-owner-annotation` -- the `cloud/*` two were already
correct, one directory shallower) -- undetected by 9+ prior audit waves since none actually
resolved the path. Fixed on `main`:
[`policy#19`](https://github.com/policy-as-versioned-flux/policy/pull/19), plus a real check added
to `verify.sh` that resolves this cross-reference for every policy going forward.

**Deliberately not rolled into a new patch tag for the currently-pinned versions.** This is a
metadata-only annotation, referenced by nothing the CEL validation logic or any admission verdict
reads -- zero verdict impact, the same class of change that earlier justified v1.0.1/v1.0.3/etc as
CI-only-fix patches. Unlike those (which fixed things actively broken in impactful ways -- an
unresolvable git tag blocking installation entirely, a security-relevant signature leaking into
public release notes), this is a cosmetic doc link with no functional consequence for anyone
running the currently-installed `v1.0.3`/`v2.0.3`/`v2.2.0`. Cutting three coordinated patch tags
and re-pinning fleet for this specific fix was judged disproportionate to its actual stakes;
`main` is the correct, fixed source of truth, and the next real content release for each line will
naturally carry it forward. Recorded as a real, considered gap, not silently left unmentioned.
