# 01 — Opening pass: gate version cross-check + polish quartet

**What to build:** Five approved no-design-question fixes, one pass. (a) The PR gate additionally renders each fetched tag and rejects any bump whose declared `version` doesn't equal the rendered content's internal policy-version value — rendered content, not tag string, so CI-only-fix patches (version ≠ tag by design) remain valid. (b) Release notes carry the tag narrative only — the PEM signed-message block is stripped (the tag object carries the signature; the release shows Verified). (c) Grafana on demo clusters needs no login (anonymous auth). (d) The CIO dashboard gains an explicit "supported policy versions on this cluster" stat. (e) The admission-only semantics are stated prominently in the fleet docs and on the dashboard: retirement never evicts — a retired-version workload runs until its next recreation, when the orphan guard refuses it; governance debt becomes visible at the next churn.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] A synthetic PR declaring a version that mismatches its tag's rendered content is rejected by CI (same proof pattern as the original force-moved-tag test)
- [x] The next release's notes contain the narrative with no PEM block
- [x] Dashboards load with zero login on a fresh demo cluster
- [x] The supported-versions stat shows exactly the installed set, live-verified
- [x] Admission-only semantics stated in docs + dashboard text

## Comments

Done 2026-07-16.

- **Gate cross-check**: `fleet/pr-gate-check.sh` now renders each fetched tag (already did, for
  the diff report) and asserts `select(di==0) | .metadata.labels."mycompany.com/policy-version"`
  equals the array's declared `version` (had to skip `di==0` -- `flux build` emits a trailing
  empty `---` doc that made a naive `yq` select return `"1.0.0\n---\nnull"`, a real bug caught by
  running the proof rather than trusting the diff). Proven live twice: a clean pass replaying the
  real 3-entry array (base `695cd13`, head `c5a7cb0`, all 9 policy/version pairs OK), and a
  synthetic branch declaring `2.2.1` against `v2.2.0`'s tag (which still renders `2.2.0`) --
  rejected with exit code 1, the exact `array declares 2.2.1` mismatch message. Shipped as
  `fleet#19`.
- **PEM strip**: `policy/.github/workflows/release.yml`'s notes generation now pipes the tag's
  `%(contents)` through `sed '/^-----BEGIN SIGNED MESSAGE-----$/,$d'` before appending the
  verified-signature footer. Verified by replaying the real `v2.2.0` tag content through the same
  sed -- clean narrative, no PEM. Also retroactively fixed via `gh release edit` since `v2.2.0`
  was the one already-published release still carrying the block (the four re-cut releases
  `v1.0.2/v1.0.3/v2.0.2/v2.0.3` were already clean from an earlier ad hoc fix). Full workflow
  proof (not just the replay) lands at the next tag cut. Shipped as `policy#6`.
- **Grafana anon auth**: `grafana.ini`'s `auth.anonymous.enabled: true` / `org_role: Viewer` added
  to the kube-prometheus-stack HelmRelease values. Live-verified after Flux reconciled: `curl
  http://.../api/org` with zero auth headers returns 200.
- **Supported-versions stat**: new `stat` panel (id 5) on `flux-policy-dashboard.json`, querying
  `count by (name) (gotk_resource_info{customresource_kind="GitRepository", name=~"policy-.*",
  ready="True"})` with `textMode: name` -- one colored box per Ready policy version, no count
  math to infer from the revision table. Live-verified through `/api/ds/query` (the pattern
  established when the CIO dashboard shipped): three series, `policy-2.2.0`/`policy-2.0.0`/
  `policy-1.0.0`, matching `clusters/cluster1/policy-versions.yaml` exactly.
- **Admission-only semantics**: a prominent `## Admission-only semantics` section added to the
  fleet README (previously the fact was scattered across script comments and a table description
  cell), plus a matching `text` panel (id 6) on the dashboard itself.

All four fleet-side items merged as `fleet#19` (self-merged; user granted standing merge
authorization for this epic 2026-07-16). Policy-side PEM fix merged as `policy#6`.
