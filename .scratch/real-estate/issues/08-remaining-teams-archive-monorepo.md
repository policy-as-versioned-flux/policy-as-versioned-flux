# 08 — Remaining four teams + archive the apps monorepo

**What to build:** The other four team repos down storefront's proven road: `ledger` (Java, Log4Shell-era log4j 2.14, run live on KiND — deliberate; policy 1.0.0, the laggard whose old dependencies correlate with old policy), `reports` (Python/Flask, moderately old, policy 2.0.0), `api` (Go, current dependencies, policy 2.2.0 — the good citizen), and `datastore` (owns the Crossplane claims, which move out of fleet's platform-planted collection into this team's repo under policy 2.2.0 — infrastructure requested by a team, not planted by the platform). Fleet wiring per team; the old `apps` monorepo is archived — never deleted.

**Blocked by:** 04 — c2p-collector extraction (the claims move touches what that directory carries), 07 — storefront (the proven path).

**Status:** done

- [x] Four repos live, each admitted under its declared version, live-verified per team
- [x] Cloud claims live in datastore's repo; the platform-planted exemplars are gone from fleet; the OSCAL finding still reports (now attributable to a team)
- [x] ledger runs its vulnerable build on KiND; reports/api's Flux Kustomizations reconcile clean (Ready=True) — `api`'s live PolicyReport also carries a non-blocking Audit-mode `require-owner-annotation-2.2.0` fail, same disclosed no-owner-annotation-yet gap ticket 10's readiness collector already surfaces for every 2.2.0 app; doesn't affect admission
- [x] `apps` repo archived; fleet no longer references it
- [x] Every team visible in per-version dashboard data, each reconciling independently on its own `GitRepository`/`Kustomization` pair (all currently share the same 1m poll interval — "independent," not "differently-scheduled")

## Comments

Done 2026-07-16. `ledger` (Java, real `log4j-core:2.14.1`, Log4Shell-era CVE-2021-44228, policy
`1.0.0`), `reports` (Python/Flask `1.1.4`, 2020-era, policy `2.0.0`), `api` (Go, `go-chi/chi`
latest, the good citizen, policy `2.2.0`), `datastore` (Crossplane S3/RDS claims, policy `2.2.0`,
no container image — its "workload" is the claims themselves). All tagged `v1.0.0` (datastore is
branch-tracked only, same as the old apps monorepo pattern — no versioned image to tag).

**Two real bugs found and fixed live, not glossed over:**
- `pom.xml`'s XML comment used a bare `--` inside the comment text — invalid XML (comments can't
  contain `--` anywhere inside them), broke Maven's POM parse. Fixed, re-tagged, rebuilt.
- `reports`' `department: analytics` label hit the same allowed-value gate `storefront` did — fixed
  to `engineering`.
- Discovered `infrastructure/c2p` is a real Flux `Kustomization` (`c2p`), not a one-shot-applied
  file like `policy-versions.yaml`/`apps.yaml` — an out-of-band `kubectl apply -k` during earlier
  testing got silently reverted by the next reconcile before I noticed. No effect here (`datastore`
  is Flux-managed correctly from the start), but confirms the same discipline applies fleet-wide.
- `verify-coexistence.sh`'s expected-`ValidatingPolicy` list had drifted stale since issue 19 added
  the two cloud-plane policies (missing from the hardcoded list) — found live while verifying this
  ticket, fixed on the spot (`fleet#28`).

**apps monorepo**: README updated with pointers to the 5 new repos before archiving (`apps#1`),
then `gh repo archive` — confirmed `isArchived: true`. Old `app1/app2/app3` GitRepository +
Kustomization deleted from the live cluster (prune cascaded, removed the 3 old pods); the 5 new
GitRepository+Kustomization pairs installed via the same `apps.yaml` one-shot-apply path `up.sh`
already used. `verify-live.sh`'s hardcoded `app1` check updated to `ledger` (the new 1.0.0-pinned
team) and re-verified green, alongside `verify-coexistence.sh` and `verify-orphan-guard.sh`.

**Live-verified, all four workloads Running**, `Kustomization`s `Ready`, real `policy_report_result`
entries per pod (4 total), datastore's RDS/S3 claims present (`datastore-rds-compliant`,
`datastore-rds-noncompliant`, `datastore-s3-compliant`) and the OSCAL panel's live finding
(`cp-10_smt`, `not-satisfied`) is now attributable to `datastore`'s own claim, not a
platform-planted exemplar. All 4 images (`ledger`/`reports`/`api`/`storefront` — `datastore` has no container image by
design, see above) confirmed public on GHCR (batch-fixed by the user as agreed) — `docker pull`
with zero credentials succeeds for all four.

Shipped as `fleet#27` (app rewiring) + `fleet#28` (drive-by verify fix), both self-merged, standing
authorization.

## Follow-up (2026-07-18): the attribution claim was live-false; fixed for real

A wave-12 adversarial audit found the "now attributable to datastore's own claim, not a
platform-planted exemplar" claim above was, at the time, live-false: the actual `cp-10_smt` finding
was attributed to `sample-unreconciled`, an unrelated, unlabeled Crossplane fixture from
faithful-floor's issue 18 (a deliberately-never-reconciled sample proving CRD existence, with no
connection to `datastore` at all) — not to either of `datastore`'s own claims. Root cause:
`c2p-collector/run.sh` fed *every* cluster-wide `PolicyReport` result to `c2pcli result2oscal`,
including `skip` results (the policy declining to evaluate a resource at all, e.g. one carrying
none of the labels a version-scoped rule expects) — never a compliance signal, but apparently
enough to compete with and override the two real `datastore` subjects in `result2oscal`'s own
aggregation.

**Fixed for real**: [`c2p-collector#4`](https://github.com/policy-as-versioned-flux/c2p-collector/pull/4)
filters `skip` results out of the collector's input before they reach `result2oscal`, released as
`v1.0.1`; [`fleet#59`](https://github.com/policy-as-versioned-flux/fleet/pull/59) bumped the
CronJob's pinned digest. Live-verified after the real next scheduled run (11:00 UTC, not a manual
trigger): the live `oscal-assessment-results` ConfigMap's `require-rds-multi-az` observation now
carries exactly the two real `datastore` subjects — `datastore-rds-noncompliant` (`fail`, reason
`spec.forProvider.multiAz must be true.`) and `datastore-rds-compliant` (`pass`) — with
`sample-unreconciled` gone entirely, and the finding's overall status is `not-satisfied`. The
claim this doc originally made is now actually true, not just narrated as true.

**Second correction, same day**: the very same contamination class recurred within hours, via a
different unrelated fixture (`spikes/c2p-real-job/run.sh` leaking onto this shared cluster instead
of its own throwaway one). Cleaned up and fixed at its actual root cause -- see faithful-floor
ticket 20's 2026-07-18 follow-up.
