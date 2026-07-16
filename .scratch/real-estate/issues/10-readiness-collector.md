# 10 — Readiness collector: "would the estate pass vNext?"

**What to build:** A new component (born in its own repo, per the extraction pattern) that answers the CIO's forward question: for a candidate policy version, which workloads would fail if the estate adopted it. Offline by construction — dumps live workload manifests, renders the candidate version's policies with the version-scope matchCondition stripped ("evaluate everyone as if opted in"), evaluates, and publishes per-team pass/fail counts to a ConfigMap for the dashboard. Never touches admission; installs no shadow policies; pollutes no PolicyReports.

**Mechanism gated on the in-flight fact-check:** primary is `kyverno apply` if the CLI supports the CEL ValidatingPolicy kind against dumped resources; fallback (known to work) is programmatically-generated `kyverno test` fixtures. The research result resolves this without another decision round — append the finding here when it lands.

**Blocked by:** 08 — the real teams exist (per-team counts need teams). Research-pending on mechanism.

**Status:** ready-for-agent

- [ ] Component repo with self-check; runs as a CronJob from a pinned image
- [ ] For a named candidate version, per-team pass/fail counts published and queryable
- [ ] Counts proven correct against a known case (e.g. a 1.0.0-era workload that fails 2.2.0's owner-annotation policy)
- [ ] Zero effect on admission or live PolicyReports, verified
