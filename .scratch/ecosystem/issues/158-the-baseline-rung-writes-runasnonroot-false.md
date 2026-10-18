# 158 — The baseline rung writes runAsNonRoot false

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

At the `baseline` rung, the served 5.0.0 `cage-tier` body writes the container field `runAsNonRoot: false` over a pod that declared `runAsNonRoot: true` at pod level. In Kubernetes the container field overrides the pod field. So the cage makes the workload looser than it declared. ADR-0022 says that the cage "never writes a security field looser than the workload declared" (`:47`).

The expression is at ludlow `composed/policies/v5.0.0/cage-tier.yaml:40`:

    runAsNonRoot: variables.dial.harden == 'true' || (has(c.securityContext) && c.securityContext.?runAsNonRoot.orValue(false))

It reads only the container's own field, with `false` as the default. It does not read the pod-level field.

Fix the body so that the container value falls back to the pod-level value, in platform, as a new policy version. The computed-semver engine computes the bump. Add a corpus entry that a pod which declares `runAsNonRoot: true` at pod level keeps it at every rung.

## Notes

Graduated 2026-09-25 from ticket 152, Q11. Found by the offline proof in [research/ticket-152-fact-7-reference/](../research/ticket-152-fact-7-reference/README.md): candidates RA and RC render the app container with `"runAsNonRoot": false`.

`require-nonroot-5-0-0` reads only the pod-level field, so it does not see this. Definition of done: the new body is served by each adopter and a check in `talk/verify-all.sh` grades the corpus entry. A new signed policy tag needs the owner's authorisation.

This does not touch ticket 161. The cage does not mutate the reference workload.

## Resume implementation, 2026-10-03

The uncut security candidate preserves a pod-level runAsNonRoot declaration when the container does not override it. The original fixture was red on that case and the new fixture passes all 18 assertions on 1.18.2. Frozen 5.0.0 is unchanged. The measured generated corpus computes a major security bump; per-adopter exact acceptance records are prepared under the owner’s delegated instruction. Publication and adoption remain pending.

The owner delegated the implementing decisions on 2026-10-03: "you tell me, you control them all, you don't need me to answer". This is recorded as delegated, not as an invented institution signature.

## Answer

**Delivery reconciled, 2026-10-18.** The signed [policy 7.0.0 release](https://github.com/policy-as-versioned-platform/platform/releases/tag/policy/v7.0.0) and all three reviewed adoptions deliver the new body. The [platform expression](https://github.com/policy-as-versioned-platform/platform/blob/2f9c6b2ea1757e4a1053b60a4e1766c5f14de4c3/graded/policies/cage-tier.yaml) falls back from the container's own `runAsNonRoot` to the pod-level value before false. The [registered corpus](https://github.com/policy-as-versioned-platform/platform/blob/2f9c6b2ea1757e4a1053b60a4e1766c5f14de4c3/graded/tests/cage-tier/kyverno-test.yaml) contains pod-nonroot cases at baseline, restricted, quarantine and isolated. Existing genuine computed-semver/release receipts supply the new version and signature; the rejected 6.0.1 compatibility candidate is not final-release evidence. The owner's delegation recorded above is preserved, without inventing per-institution signatures.

The selected 7.0.0 body is present in each served composed set: [Driftwood](https://github.com/policy-as-versioned-driftwood/driftwood/blob/5a1b9a1ae85f88dfe91a71aca8eeb308349097ff/composed/policies/v7.0.0/cage-tier.yaml), [Tuppence](https://github.com/policy-as-versioned-tuppence/tuppence/blob/e7e2969cd50ab3e88fa11afe61d5bee5d1db30d4/composed/policies/v7.0.0/cage-tier.yaml) and [Ludlow](https://github.com/policy-as-versioned-ludlow/ludlow/blob/e65acc95bd107e0ba2864b2ca2f23b51714dc4c1/composed/policies/v7.0.0/cage-tier.yaml). Frozen 5.0.0 and historical coexistence bodies are not rewritten. The actual 7.0.0 body corpus already passed 18 assertions for each adopter.

The existing truth manifest registers `.estate-clone/driftwood/verify-cage-probe.sh`, `.estate-clone/tuppence/verify-cage-probe.sh`, `.estate-clone/ludlow/verify-cage-probe.sh` and `.estate-clone/platform/computed-semver/verify-cage-engine.sh`. All four are PASS in the unchanged [recorded run 432 table](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/d096cd2f0515a8aa2f9de1b671f5f227beba5478/talk/captures/_grades.tsv). Their corpus/served-document evidence meets the requested source and check delivery; this reconciliation runs no new cluster or policy experiment and does not claim every historical policy line changed.
