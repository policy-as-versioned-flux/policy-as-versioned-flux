# 08 — Remaining four teams + archive the apps monorepo

**What to build:** The other four team repos down storefront's proven road: `ledger` (Java, Log4Shell-era log4j 2.14, run live on KiND — deliberate; policy 1.0.0, the laggard whose old dependencies correlate with old policy), `reports` (Python/Flask, moderately old, policy 2.0.0), `api` (Go, current dependencies, policy 2.2.0 — the good citizen), and `datastore` (owns the Crossplane claims, which move out of fleet's platform-planted collection into this team's repo under policy 2.2.0 — infrastructure requested by a team, not planted by the platform). Fleet wiring per team; the old `apps` monorepo is archived — never deleted.

**Blocked by:** 04 — c2p-collector extraction (the claims move touches what that directory carries), 07 — storefront (the proven path).

**Status:** ready-for-agent

- [ ] Four repos live, each admitted under its declared version, live-verified per team
- [ ] Cloud claims live in datastore's repo; the platform-planted exemplars are gone from fleet; the OSCAL finding still reports (now attributable to a team)
- [ ] ledger runs its vulnerable build on KiND; reports/api reconcile clean
- [ ] `apps` repo archived; fleet no longer references it
- [ ] Every team visible in per-version dashboard data with its own reconcile cadence
