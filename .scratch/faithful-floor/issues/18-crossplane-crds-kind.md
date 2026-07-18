# 18 — Crossplane v2 provider CRDs in KiND + dependsOn Established

**What to build:** The cloud-as-CR admission surface, free and KiND-only (CONTEXT proof posture): current Crossplane v2 + AWS provider-family CRDs installed — no ProviderConfig, no cloud auth, no reconcile — with the cloud-policy `Kustomization` wired to `dependsOn` the provider CRDs being Established, so the admission webhook is registered before any cloud policy needs it (PRD §6.5 ordering).

**Blocked by:** 05 — KiND + Flux Operator + Kyverno.

**Status:** done

- [x] Provider-family CRDs install declaratively via Flux and reach Established
- [x] A sample RDS/S3 CR applies and simply sits unreconciled (no auth on the critical path)
- [x] Cloud-policy ordering gates on CRDs-Established, verified by a fresh-cluster bring-up

## Comments

2026-07-15: `fleet` repo PR #6 (open, awaiting review, not self-merged): Crossplane v2 core
(2.3.3) + the AWS S3/RDS provider-family packages (v2.6.0, not the monolithic `provider-aws` --
this cluster only needs two services' CRDs) as three chained Kustomizations
(`crossplane` -> `crossplane-providers` -> `crossplane-sample`) via `dependsOn`/`healthChecks`.

Deliberately did NOT wire in the two real cloud ValidatingPolicies from the policy repo here --
they only exist on `main` at pending version 2.2.0, not yet a signed tag, and deploying from an
untagged branch would violate ADR-0001's whole point (signed tags are the transport). That's
ticket 19's job once ticket 08's blocker (new signed tags) clears, and it's correctly still
blocked. Instead proved the ordering primitive with something real and permanent that doesn't
touch unsigned content: a genuine `Instance` CR (`crossplane-sample`) whose successful apply is
only possible once `instances.rds.aws.m.upbound.io` is Established -- the exact same dependsOn
issue 19 will reuse for its own cloud-policy Kustomizations.

Confirmed empirically (not just asserted) that the ordering is load-bearing: dry-running the
Provider/Instance manifests against this cluster today (Crossplane not yet installed) fails
outright with `no matches for kind "Provider"/"Instance" ... ensure CRDs are installed first`.
That failure is exactly what `dependsOn` makes unreachable on a real bring-up.

**2026-07-15:** PR #6 merged. `verify-crossplane.sh` run for real against the live cluster: all
three Kustomizations Ready, both CRDs (`instances.rds.aws.m.upbound.io`,
`bucketserversideencryptionconfigurations.s3.aws.m.upbound.io`) Established, sample `Instance` CR
applied and sitting unreconciled (`Synced` never `True`, no `ProviderConfig` anywhere). Also found
live (not by this ticket's own checklist, but load-bearing for issue 19 on top of it): Kyverno's
background/reports controllers need explicit RBAC to list/watch arbitrary CRDs -- fixed via an
aggregated `ClusterRole`, see issue 19.

**Follow-up (2026-07-18)**: the `crossplane-sample` Kustomization managing this ticket's own
`sample-unreconciled` fixture now shows `Ready: False` as a live consequence of issue 09's
2026-07-18 cloud-plane orphan-guard extension -- the fixture is genuinely unaffected (untouched
since 2026-07-15), only its Flux health status changed. See issue 09's own follow-up for the full
explanation of why this is the governance design working as intended, not a regression.
