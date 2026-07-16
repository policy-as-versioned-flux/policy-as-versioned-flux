# 10 — Readiness collector: "would the estate pass vNext?"

**What to build:** A new component (born in its own repo, per the extraction pattern) that answers the CIO's forward question: for a candidate policy version, which workloads would fail if the estate adopted it. Offline by construction — dumps live workload manifests, renders the candidate version's policies with the version-scope matchCondition stripped ("evaluate everyone as if opted in"), evaluates, and publishes per-team pass/fail counts to a ConfigMap for the dashboard. Never touches admission; installs no shadow policies; pollutes no PolicyReports.

**Mechanism: RESOLVED — `kyverno apply`.** The fact-check (2026-07-16, verified live against the real
CLI 1.18.2 and the real `require-department-label` policy + fixtures, not just docs) confirmed
`kyverno apply` fully supports the CEL `ValidatingPolicy` kind: single-file and directory-batch
`--resource` both work offline; stripping `matchConditions` via `yq del` leaves a valid policy; and
`--policy-report --output-format json` emits an `openreports.io/v1alpha1 ClusterReport` with a
top-level `summary: {pass, fail, warn, error, skip}` plus per-resource `results[]`
(`source: "KyvernoValidatingPolicy"`) — machine-parseable, no text scraping. The docs' own CEL
migration guide uses `kyverno apply` as the canonical test command. No fallback needed.
**Implementation note from the live test:** `kyverno apply` exits 1 on any fail (CI-gate semantics)
— the collector must capture and parse the JSON regardless of exit code, not treat exit 1 as a
script failure.

**Blocked by:** 08 — the real teams exist (per-team counts need teams).

**Status:** ready-for-agent

- [ ] Component repo with self-check; runs as a CronJob from a pinned image
- [ ] For a named candidate version, per-team pass/fail counts published and queryable
- [ ] Counts proven correct against a known case (e.g. a 1.0.0-era workload that fails 2.2.0's owner-annotation policy)
- [ ] Zero effect on admission or live PolicyReports, verified
