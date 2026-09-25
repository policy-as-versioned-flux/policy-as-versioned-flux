# 158 — The baseline rung writes runAsNonRoot false

Type: task (AFK)
Status: open
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
