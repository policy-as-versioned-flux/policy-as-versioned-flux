# 159 — A tier label on an ungoverned namespace steers the cage

Type: task (AFK)
Status: open
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
