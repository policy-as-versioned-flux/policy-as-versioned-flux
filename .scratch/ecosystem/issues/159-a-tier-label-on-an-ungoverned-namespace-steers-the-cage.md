# 159 — A tier label on an ungoverned namespace steers the cage

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

ADR-0022 says that a tier attaches to a governed Namespace. The **Governed namespace** entry in CONTEXT.md says that the tier is declared on the signed governed manifest. The served 5.0.0 `cage-tier` body does not read the `governed` label. It reads `posture.acme.io/tier` from any Namespace (ludlow `composed/policies/v5.0.0/cage-tier.yaml:31-34`). So a claiming pod in a Namespace that carries `posture.acme.io/tier: baseline` without `governed: "true"` lands on the `baseline` rung. `platform/shift-left/tier_binding.py` finds declarations by the governed label, so it never sees that Namespace.

Decide under ADR-0025 and record which of these holds, then build it:

- (a) The body reads the tier only when `governed: "true"` is present. Any other Namespace falls to `isolated` for a claiming pod. This is a new policy version, and the computed-semver engine computes the bump.
- (b) The doctrine changes: the governed label bounds the price and the proposer only, and a tier label bounds the cage wherever it is written. Then each adopter's `gitops/apps/namespace.yaml` comment and the CONTEXT.md entry are corrected.

Ticket 152's review recommended (a). Option (a) keeps "a tier is declared on the signed governed Namespace" true, and it only tightens.

## Notes

Graduated 2026-09-25 from ticket 152, Q11. Found by the offline proof in [research/ticket-152-fact-7-reference/](../research/ticket-152-fact-7-reference/README.md): candidates RA (governed, tier `baseline`) and RC (tier `baseline`, not governed) render identical pods.

A Namespace created at run time is not checked against the signed manifests at admission. That is the same gap, seen from the other side. Definition of done: a check in `talk/verify-all.sh` grades the chosen rule on the served bodies. A new signed policy tag needs the owner's authorisation.

## Implementation prepared, 2026-10-03

**Delegated decision under ADR-0025: (a).** A claiming pod may read a tier only from a
Namespace carrying `policy-as-versioned.dev/governed: "true"`. A tier label alone falls to
`isolated`. This preserves the signed governed Namespace as the tier declaration and tightens
the previously loose case. No doctrine change was chosen.

The public cage-tier fixture observed the old body fail the ungoverned-baseline case, then
observed the corrected body pass. The uncut6.0.0 candidate carries this and ticket158's pod-level
non-root fallback; the uncut6.0.1 candidate carries their same behavior with ticket149's engine
compatibility changes. Full pairwise-spine comparison computesmajor for5.0.0 ->6.0.0.
The current signed5.0.0 body and adopter artefacts remain unchanged. Signed release, owner major
acceptance, adoption and the served-body truth check remain outstanding.

Evidence and durable platform diff: [engine report](../patches/resume-2026-10-03/engine-report.md).

## Answer

**Delivery reconciled, 2026-10-18.** Delegated option(a), already recorded above under ADR-0025, is built and delivered in signed [policy 7.0.0](https://github.com/policy-as-versioned-platform/platform/releases/tag/policy/v7.0.0). The [new platform body](https://github.com/policy-as-versioned-platform/platform/blob/2f9c6b2ea1757e4a1053b60a4e1766c5f14de4c3/graded/policies/cage-tier.yaml) reads a Namespace tier only when `policy-as-versioned.dev/governed` equals `"true"`; an ungoverned baseline label falls to isolated for a claiming pod. The [ungoverned-baseline corpus case](https://github.com/policy-as-versioned-platform/platform/blob/2f9c6b2ea1757e4a1053b60a4e1766c5f14de4c3/graded/tests/cage-tier/kyverno-test.yaml) and [Namespace values](https://github.com/policy-as-versioned-platform/platform/blob/2f9c6b2ea1757e4a1053b60a4e1766c5f14de4c3/graded/tests/cage-tier/values.yaml) grade that distinction. Existing computed-semver, signature and authorized adoption receipts are retained; 6.0.1 was an earlier candidate, not the final adopted release. No option(b) doctrine change is made.

The selected 7.0.0 bodies are served by [Driftwood](https://github.com/policy-as-versioned-driftwood/driftwood/blob/5a1b9a1ae85f88dfe91a71aca8eeb308349097ff/composed/policies/v7.0.0/cage-tier.yaml), [Tuppence](https://github.com/policy-as-versioned-tuppence/tuppence/blob/e7e2969cd50ab3e88fa11afe61d5bee5d1db30d4/composed/policies/v7.0.0/cage-tier.yaml) and [Ludlow](https://github.com/policy-as-versioned-ludlow/ludlow/blob/e65acc95bd107e0ba2864b2ca2f23b51714dc4c1/composed/policies/v7.0.0/cage-tier.yaml). The existing registered checks `.estate-clone/driftwood/verify-cage-probe.sh`, `.estate-clone/tuppence/verify-cage-probe.sh`, `.estate-clone/ludlow/verify-cage-probe.sh` and `.estate-clone/platform/computed-semver/verify-cage-engine.sh` all have PASS in the unchanged [recorded run 432 table](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/d096cd2f0515a8aa2f9de1b671f5f227beba5478/talk/captures/_grades.tsv). The actual 7.0.0 body corpus already passed for all three adopters. This is the requested served-body rule proof, not a new claim about a Namespace created at runtime or live actor enforcement. Frozen historical bodies and observations remain intact.
