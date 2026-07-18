# 19 — Cloud plane at admission: one engine, both planes

**What to build:** Close the gap the 2022 talk admitted on stage: the same versioned Kyverno engine that judges workloads judges Crossplane CR specs at admission. Cloud policies from 17 ride the coexistence matrix as first-class versions; a compliant and a non-compliant exemplar per plane prove the verdicts (the non-compliant one admitted under an Audit-mode policy, so a PolicyReport exists to attest later — a Deny gate leaves nothing on-cluster to report). Any Deny gate scopes to CREATE/UPDATE, excluding provider-authored status updates.

**Blocked by:** 08 — ResourceSet coexistence matrix, 17 — Cloud policies, 18 — Crossplane CRDs in KiND.

**Status:** done -- all 4 items proven on the real, live fleet 2026-07-15

- [x] A non-compliant S3 CR (e.g. unencrypted) is denied at admission by the versioned gate
- [x] A non-compliant exemplar under an Audit-mode cloud policy admits and appears in a PolicyReport
- [x] Cloud policies coexist across versions and honour the same `policy-version` opt-in and orphan guard
- [x] Everything runs on KiND with zero cloud credentials

## Comments

2026-07-15: this ticket is formally "Blocked by: 08, 17, 18" because *wiring the real cloud
policies into the live, Flux-GitOps-reconciled `fleet` cluster as first-class versioned entries*
needs a new signed tag (ADR-0001: signed tags are the transport) -- that part genuinely can't
happen without the same gitsign re-auth 08 is waiting on, and wasn't attempted here. But 3 of the
4 checklist items don't actually require the live fleet or multi-version coexistence, only the
real policy content on *some* KiND cluster -- proven directly, same throwaway-cluster idiom as the
existing spikes (nothing pushed/signed, nothing wired into policy/fleet/apps/cloud):

- **Deny-gate refusal (item 1):** applied the real, byte-identical
  `pavf-policy/cloud/require-s3-bucket-encryption/policy.yaml` (unmodified -- still `Deny`, not
  patched to Audit) on a throwaway KiND cluster against the real `bucket-fail`/`bucket-pass`
  fixtures. Refused: `admission webhook ... denied the request: Policy
  require-s3-bucket-encryption failed: spec.forProvider.rule[].applyServerSideEncryptionByDefault.sseAlgorithm
  must be set`. Compliant bucket admitted cleanly straight after, same policy, same cluster.
- **Audit-mode PolicyReport (item 2):** the C2P job built for issue 20 (`spikes/c2p-real-job/`)
  already exercises exactly this for `require-rds-multi-az` (real Audit-mode lane-keeper): the
  non-compliant `instance-fail` fixture admits and shows up as a `cp-10` not-satisfied finding in
  the emitted OSCAL, sourced from a real `result=fail source=KyvernoValidatingPolicy` PolicyReport
  entry. Re-used that evidence rather than re-proving it.
- **Zero cloud credentials (item 4):** trivially true throughout both of the above -- no
  ProviderConfig, no AWS credentials, anywhere.

**2026-07-15, item 3 (the remaining blocker) closed for real:** once `v2.2.0` was signed and
`policy-versions.yaml` repointed at the fixed tags (issue 08), wired the cloud plane in for real.
`policies` array items changed from bare strings to `{name, plane}` objects so the
`resourcesTemplate` can pick the right fetch path (`workloads/kyverno/<name>` vs `cloud/<name>`)
and, for cloud, add `dependsOn: crossplane-providers` on top of the usual `dependsOn: kyverno`
(issue 18's CRDs-Established ordering). Applied live, then found and fixed a real gap: Kyverno's
background/reports controllers have zero RBAC on arbitrary CRDs by default, so the two new cloud
`ValidatingPolicy`s were created but stuck `RBACPermissionsGranted=False` -- same gap the issue 20
spike already hit and fixed; ported the identical aggregated `ClusterRole` (get/list/watch only,
scoped to exactly the two Crossplane resource types this project targets) into real fleet infra.

All 10 `ValidatingPolicy`s (8 workload + 2 cloud, across the 3 coexisting versions) now report
`Ready=true` live. Proved all three items against the real cluster, not a spike:
- A real, unmodified `require-s3-bucket-encryption-2.2.0` (`Deny`) refused a schema-valid,
  policy-non-compliant `BucketServerSideEncryptionConfiguration` (empty `sseAlgorithm`) at
  admission; a compliant one admitted straight after, same cluster, same policy.
- A real, unmodified `require-rds-multi-az-2.2.0` (`Audit`) admitted a non-compliant `Instance`
  (`multiAz: false`) and it showed up as a `result=fail source=KyvernoValidatingPolicy`
  PolicyReport entry within seconds.
- Both exemplars were labelled `mycompany.com/policy-version: "2.2.0"`, going through the exact
  same coexistence/orphan-guard machinery as the workload plane -- one engine, both planes, live,
  not simulated.

## Follow-up (2026-07-18): "same orphan-guard machinery" was true only for labelled exemplars

A wave-1 audit of the faithful-floor epic found the checklist's "honour the same policy-version
opt-in and orphan guard" claim was narrower than it read: it held for the two deliberately-labelled
exemplars above, but orphan-guard's own `matchConstraints.resourceRules` only ever matched core
`v1` Pods -- a Crossplane CR carrying no label at all (e.g. issue 18's `sample-unreconciled`) was
structurally invisible to the guard and admitted with a `skip` PolicyReport result, not denied,
unlike an unlabeled Pod. This directly contradicted orphan-guard's own documented purpose in
`policy-versions.yaml`: "the guard is what makes the gate tier a locked door rather than an
opt-in door."

**Fixed for real**: [`fleet#60`](https://github.com/policy-as-versioned-flux/fleet/pull/60)
extends orphan-guard's `resourceRules` to also cover the two Crossplane CRD types
(`s3.aws.m.upbound.io/bucketserversideencryptionconfigurations`,
`rds.aws.m.upbound.io/instances`), matching the two cloud policies' own scoping exactly.
Live-verified after merge and reconcile: a dry-run of an unlabelled RDS `Instance` is now denied
at admission with the same message a Pod gets; all three real, labelled `datastore` cloud
exemplars still pass unaffected; `sample-unreconciled` now correctly shows `orphan-guard: fail` in
its background `PolicyReport` while remaining un-evicted (still running, 3 days old) -- reported,
never evicted, exactly the documented invariant.

**Third correction, same day**: shortly after the orphan-guard fix above, a wave-1 audit found 3
stray unversioned duplicate `ValidatingPolicy`s and 2 fixture Crossplane CRs sitting live on this
same shared cluster, outside GitOps control -- leaked by `spikes/c2p-real-job/run.sh` applying
directly to the ambient context instead of its own throwaway KiND cluster. Cleaned up and fixed at
the actual root cause (a hard context guard, not a one-off cleanup) -- see faithful-floor ticket
20's 2026-07-18 follow-up for the full story and live proof.
