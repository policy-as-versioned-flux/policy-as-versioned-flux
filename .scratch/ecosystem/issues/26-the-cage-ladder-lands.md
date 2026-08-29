# 26 — The cage ladder lands

Type: task (AFK)
Status: resolved
Blocked by: 09, 21

## Question

Build the five decisions of ticket 09 in the estate: tier on the governed Namespace read via namespaceObject in cage-tier with the pod label as output; tighten-only mutation in all three served copies plus cage_engine classifying false-over-true as loosening; isolated rung with per-tier cage-netpol (Ingress added, synchronize gap named); overlay.floor clamp in the selection policy, priced on lowering; platform party.yaml declares kube-system, flux-system, kyverno at infra and the truth surface asserts it before the unlabelled default flips from baseline to isolated. Offline kyverno test uses a values file with namespaces. Wire the check into verify-all.sh.

## Notes

Graduated 2026-08-28 from ticket 09's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Live defects found 2026-08-28, this ticket owns them

Found while greening the truth surface. Each is observed on the live driftwood KinD cluster.

1. **BLOCKER. No pod can be created in a caged Namespace.** `cage-tier-*` sets
   `spec.priorityClassName` from a mutating webhook. The built-in Priority admission plugin has
   already stamped `priority: 0` by then, so its validating half recomputes the class value and
   the API server refuses the pod:
   `pods "teller-current-..." is forbidden: the integer value of priority (0) must not be provided
   in pod spec; priority admission controller computed -10 from the given PriorityClass name`.
   Proven with `kubectl apply --dry-run=server` against the unmodified teller template. The
   `tuppence-reset` pods survive only because they are older than the policy. Delete one and it
   never returns. This breaks NORTH-STAR §4 step 4, which says the workload keeps running.
   Fix shape: the mutation sets `spec.priority` to the class's own integer alongside
   `priorityClassName`, so the two agree; or the cage stops writing the class and the workload
   carries it. Definition of done for this item: a pod created in a caged Namespace is admitted,
   carries the tier's PriorityClass, and a verify script observes it live.
2. `verify-identity.sh` ends its PASS line with "OpenBao trusts SPIRE JWKS". Live, OpenBao's jwt
   auth method is not enabled. `identity/openbao/jwt-auth.yaml`'s Job points at
   `http://spire-spiffe-oidc-discovery-provider...`, but that Service exposes 443 only, so the Job
   has failed for 27 days. The claim must become true or leave the PASS line.
3. `tuppence/reset/verify-reach-secrets.sh` step 4 cannot mint a JWT-SVID: the `caller` container
   has no Workload API socket, because the CSI socket is mounted into `istio-proxy` only. The
   secret half of the beat is proved offline only, and the script now says so.
4. `verify-posture-projection.sh` step 6 cannot assert its clobber case: the dry-run returns empty
   without a live Kyverno mutating webhook for that version.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. The cage ladder is live on kind-driftwood at policy version 4.0.0. The tier is read from the governed Namespace through namespaceObject and written onto the pod as an output; a governed Namespace with no tier falls closed to isolated; the cage is tighten-only; the isolated rung has no reach; per-tier reach is generated. THE BLOCKER: the mutation had to write all three fields the Priority admission plugin derives (priorityClassName, priority, preemptionPolicy) or the API server refused every pod. Versions 2.0.0, 2.0.1 and 3.0.0 could never admit a pod and were RETIRED, not patched: teaching them the Namespace tier source is ADR-0022, which the engine computes as major, so it cannot ride on a patch. cage_engine.py now classifies a write of false over a workload true as a loosening.

Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it is the TRUTH line of 2026-08-29.
