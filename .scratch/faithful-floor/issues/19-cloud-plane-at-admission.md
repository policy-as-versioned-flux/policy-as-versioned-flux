# 19 — Cloud plane at admission: one engine, both planes

**What to build:** Close the gap the 2022 talk admitted on stage: the same versioned Kyverno engine that judges workloads judges Crossplane CR specs at admission. Cloud policies from 17 ride the coexistence matrix as first-class versions; a compliant and a non-compliant exemplar per plane prove the verdicts (the non-compliant one admitted under an Audit-mode policy, so a PolicyReport exists to attest later — a Deny gate leaves nothing on-cluster to report). Any Deny gate scopes to CREATE/UPDATE, excluding provider-authored status updates.

**Blocked by:** 08 — ResourceSet coexistence matrix, 17 — Cloud policies, 18 — Crossplane CRDs in KiND.

**Status:** in-progress -- 3 of 4 checklist items proven via throwaway KiND (not the live fleet); the
4th genuinely needs issue 08's signed-tag blocker to clear, see Comments

- [x] A non-compliant S3 CR (e.g. unencrypted) is denied at admission by the versioned gate
- [x] A non-compliant exemplar under an Audit-mode cloud policy admits and appears in a PolicyReport
- [ ] Cloud policies coexist across versions and honour the same `policy-version` opt-in and orphan guard
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

**What's still genuinely blocked (item 3):** cross-version coexistence + the orphan guard for the
cloud plane needs the cloud policies actually templated into `fleet/clusters/cluster1/policy-versions.yaml`'s
`ResourceSet` array pointing at real tags -- which needs both a new signed release (the cloud
policies only exist on `policy`'s `main`, unreleased) and issue 08's `matchConditions` fix to
actually be live and stable across 2+ coexisting versions. No shortcut available here that doesn't
either fake a signature or bypass the GitOps path -- correctly left open.
