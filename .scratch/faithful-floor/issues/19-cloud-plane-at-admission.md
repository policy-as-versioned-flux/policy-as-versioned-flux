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
