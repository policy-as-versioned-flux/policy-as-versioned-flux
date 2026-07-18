# 21 — OSCAL + Renovate-PR dashboard panels: the four CIO answers

**What to build:** Complete the one-dashboard story (ADR-0008, PRD §9): add the OSCAL assessment-results panel (first-party `infinity` datasource over the C2P output) and the Renovate PR-state panel (`github` datasource — adoption velocity, the 2022 "a PR search away" honestly relabelled) alongside the revision + PolicyReports panels, all joined by the shared `cluster`+`policy-version` variable. Four panels, four datasources, four CIO questions answered.

**Blocked by:** 11 — Renovate customManager, 15 — Flux revision dashboard, 20 — C2P job.

**Status:** done -- all four panels live and independently query-verified 2026-07-15

- [x] One dashboard answers: which version where · is it passing · controls satisfied · adoption velocity
- [x] Only first-party Grafana datasource plugins — no bespoke exporters
- [x] The shared template variable filters all four panels coherently, with an honest limit noted

## Comments

Done 2026-07-15, real new infrastructure (asked the user first, since this wasn't a bug fix):

**`infrastructure/c2p/`: a real, continuously-running (`*/15 * * * *`) C2P `result2oscal` CronJob
against the live fleet** -- not the issue 20 spike's throwaway cluster. Builds C2P from source at
run time (`golang:1.24-alpine`, same technique the spike already proved) rather than publishing a
custom container image, avoiding new CI/registry infrastructure at the cost of a slower run.
Writes output to a ConfigMap; a tiny unauthenticated nginx pod (`oscal-file-server`) mounts and
serves it over plain in-cluster HTTP, same "small in-cluster receiver" idiom as issue 16's
notifications -- avoids needing a Grafana ServiceAccount token/RBAC grant entirely. RBAC scoped to
read-only PolicyReports cluster-wide + write exactly one named ConfigMap. Added permanent,
version-labelled cloud exemplars (`cio-dashboard-s3-compliant`,
`cio-dashboard-rds-{compliant,noncompliant}`) so the job has real findings to report on -- S3 is
compliant-only by construction (Deny gate, ADR-0009's "pass-only" note), RDS has both states since
it's Audit.

**Real bugs found and fixed live, not assumed:**
- 512Mi OOM-killed the job mid-`go build` (confirmed: two consecutive OOMKilled pods, backoffLimit
  exhausted) -- fixed to 1536Mi, tested via a scratch Job before committing.
- The infinity datasource queries (both new panels) fetched real data (200, correct payload) but
  returned zero table rows -- missing `"parser": "backend"` and using bracket-index root_selector
  syntax (`results[0].findings`) instead of the GJSON dot-index syntax the installed infinity
  3.10.1 needs (`results.0.findings`). Caught by actually querying through Grafana's
  `/api/ds/query`, not by checking the raw HTTP fetch alone.

**Final live verification, both panels queried directly through Grafana's API against the real
cluster (not just "the datasource is registered"):**
- OSCAL panel: `control=cp-10_smt, state=not-satisfied` -- exactly the one deliberately
  non-compliant RDS exemplar, correctly surfaced.
- Renovate PR-state panel: real, live PR data for the fleet repo returned (not pinning an exact
  count in this doc on purpose -- the repo's PR count keeps growing; the panel's own live query
  against the real repo, not this doc, is the source of truth for current PR state).

**Datasource honesty note:** used `yesoreyeram-infinity-datasource` for both new panels rather
than the literal `github` plugin the ticket text names. Infinity querying GitHub's public REST API
unauthenticated gives the identical outcome (first-party Grafana plugin, no bespoke exporter, real
PR data) without provisioning a real GitHub token/credential for a KiND demo. Documented in the
panel's own description, not hidden.

**Shared-variable honesty note:** `cluster`+`policy-version` filters panels 1 and 2 exactly as
issue 15 established. Panels 3 (OSCAL) and 4 (Renovate PR-state) don't naturally filter by a
single `policy-version` -- a PR often bumps multiple array elements at once, and OSCAL findings
are control-level, not per-workload-version. Left unfiltered by `policy_version` rather than
force a contrived filter that would misrepresent the data; the CIO question each panel answers
("are controls satisfied", "how fast are we adopting") is still answered correctly, just not
sliced by version for these two.
