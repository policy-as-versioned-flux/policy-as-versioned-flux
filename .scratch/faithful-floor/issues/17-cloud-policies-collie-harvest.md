# 17 — Cloud policies: collie harvest → hand-authored RDS/S3 CEL VPs

**What to build:** The cloud plane's policy content (ADR-0004): harvest collie's reusable IP — the NIST 800-53r5 → RDS/S3 policy intent and OSCAL catalogue — and hand-author the rules as CEL ValidatingPolicies targeting current Crossplane v2 AWS provider-family CRD groups (namespaced kinds), versioned exactly like workload policy (same nameSuffix + self-selector pattern, same repo, fixtures, rationale, NIST control mapping recorded per policy). collie's generator/Lula/bootstrap stay dropped.

**Blocked by:** 03 — Gate VP + rationale layout (the authoring pattern to follow).

**Status:** ready-for-agent

- [x] At least an S3 encryption gate (Deny) and one RDS lane-keeper (Audit), each mapped to its NIST 800-53r5 control
- [x] `kyverno test` fixtures pass/fail against Crossplane v2 CR specs
- [x] Policies follow the identical coexistence pattern as workload policies — nothing cloud-special in the versioning
- [x] Harvested OSCAL catalogue captured in-repo with provenance noted (Apache-2.0, from collie)

## Comments

Done 2026-07-14. `policy` repo, `cloud/require-s3-bucket-encryption` (Deny, NIST **sc-28**) and
`cloud/require-rds-multi-az` (Audit, NIST **cp-10**) -- same `matchConditions` version-scoping +
nameSuffix + cosmetic-label pattern as the workload plane, all hand-synced together, nothing
cloud-special (`verify.sh` extended to loop `cloud/*/` too, all 5 policies now in the tree agree on
one version).

Harvested from `controlplaneio/collie@d2486af` (Apache-2.0): the control-mapping *intent*
(`s3-bucket-server-side-encryption-enabled`, `rds-multi-az-support`), not the policy bodies --
collie targets the older, non-namespaced `s3.aws.crossplane.io`/`database.aws.crossplane.io`
provider shape. Confirmed against `crossplane-contrib/provider-upjet-aws`'s own namespaced
examples (not guessed) that current Crossplane targets `s3.aws.m.upbound.io,
kind: BucketServerSideEncryptionConfiguration` (encryption is its own resource now, not a nested
field on `Bucket`) and `rds.aws.m.upbound.io, kind: Instance` with a flat
`spec.forProvider.multiAz` (collie's own rule message described a nested `multiAZ` object that
doesn't match either the old or current schema -- corrected, not reproduced). Each rationale.md
records exactly what was kept vs. rebuilt.

Full harvested OSCAL catalogue (the real NIST SP 800-53r5 catalogue, ~7MB, plus collie's S3/RDS
component-definitions and baseline profiles) landed with provenance in the new
[`cloud`](https://github.com/policy-as-versioned-flux/cloud) repo, not duplicated into the policy
repo -- README documents what was harvested vs. dropped (ADR-0004: the generator/Lula/bootstrap).

Bundled the version bump with issue 08's `matchConditions` fix into one pending `v2.2.0` (new
policies are minor by construction; minor wins over the fix's own patch-level impact) -- not yet
tagged, same gitsign re-auth block as issue 08.
