# 12 — Estate staleness dashboard: both kinds of staleness, one view per team

**What to build:** A new, second dashboard (same ConfigMap/sidecar mechanism as the CIO dashboard, which stays one-question-shaped and untouched beyond ticket 01's additions). One row per team, joining: the policy version they're pinned to and its sunset countdown (ticket 09's field), their dependency staleness (live Renovate data), and their vulnerability counts (ticket 11's metrics), plus ticket 10's readiness verdict for the candidate version. This is the epic's thesis-strengthening payoff: a policy version is a dependency like any other, so both kinds of staleness belong in one estate view — and the ledger row (old policy AND old deps) shows the correlation the roster was designed to expose.

**Blocked by:** 08 — teams exist; 09 — sunset field; 10 — readiness counts; 11 — vulnerability metrics.

**Status:** ready-for-agent

- [ ] New dashboard, sidecar-discovered, one row per team joining all four signals
- [ ] Every panel verified by querying through the Grafana query API and asserting real rows — no screenshot-only verification
- [ ] ledger visibly worst-in-class on both staleness axes; api visibly clean — the contrast reads at a glance
- [ ] Existing CIO dashboard unchanged (beyond ticket 01)
