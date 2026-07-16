# 01 — Opening pass: gate version cross-check + polish quartet

**What to build:** Five approved no-design-question fixes, one pass. (a) The PR gate additionally renders each fetched tag and rejects any bump whose declared `version` doesn't equal the rendered content's internal policy-version value — rendered content, not tag string, so CI-only-fix patches (version ≠ tag by design) remain valid. (b) Release notes carry the tag narrative only — the PEM signed-message block is stripped (the tag object carries the signature; the release shows Verified). (c) Grafana on demo clusters needs no login (anonymous auth). (d) The CIO dashboard gains an explicit "supported policy versions on this cluster" stat. (e) The admission-only semantics are stated prominently in the fleet docs and on the dashboard: retirement never evicts — a retired-version workload runs until its next recreation, when the orphan guard refuses it; governance debt becomes visible at the next churn.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] A synthetic PR declaring a version that mismatches its tag's rendered content is rejected by CI (same proof pattern as the original force-moved-tag test)
- [ ] The next release's notes contain the narrative with no PEM block
- [ ] Dashboards load with zero login on a fresh demo cluster
- [ ] The supported-versions stat shows exactly the installed set, live-verified
- [ ] Admission-only semantics stated in docs + dashboard text
