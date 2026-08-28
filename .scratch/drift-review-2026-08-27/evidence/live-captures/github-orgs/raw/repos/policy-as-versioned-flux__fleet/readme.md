# fleet

The config repo Flux reconciles (PRD §5.1). A KiND cluster running the
ControlPlane Flux Operator (`FluxInstance`,
[ADR-0005](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/main/docs/adr/0005-controlplane-flux-operator-resourceset.md)),
the Kyverno engine (`>=1.18`,
[ADR-0003](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/main/docs/adr/0003-kyverno-validatingpolicy-cel.md)),
**three policy versions coexisting side by side** (`v1.0.3`, `v2.0.3`,
`v2.2.0`, ADR-0001 + ADR-0005's `ResourceSet` matrix, issue 08), the
**orphan guard** (issue 09, the deterministic Deny catch-all that makes the
gate tier a locked door), **the cloud plane at admission** (issue 19 --
`v2.2.0`'s two Crossplane-targeting policies ride the same coexistence
matrix as first-class versions), a second, narrower cluster profile
(issue 10, `cluster2`, `>=2.0.0` only, proving per-cluster narrowing and
live retirement), and three consumer apps (one per version) — all
reconciling live from git, not one-shot `kubectl apply`.

**Issue 08/09, resolved:** the version self-scoping mechanism was corrected
from `matchConstraints.objectSelector` to `matchConditions` (see the policy
repo's `1466fdc` and this hub's ADR-0003) after finding Kyverno flattens
every installed ValidatingPolicy's `objectSelector` into one shared webhook
-- only the most-recently-reconciled version's workloads were ever
evaluated at all. `v1.0.0`/`v1.0.1`/`v2.0.0`/`v2.0.1`/`v2.1.1` were already
tagged and immutable with the old pattern baked in, so this repo now points
at `v1.0.3`/`v2.0.3` (new, zero-verdict-impact patch tags carrying just the
fix into the two older lines) and `v2.2.0` (a real content release: same
fix + issue 17's cloud-plane policies) instead. (`v1.0.2`/`v2.0.2` also
exist but are skipped -- their commits weren't reachable from any branch,
a documented Flux/go-git shallow-fetch-by-tag limitation, not a broken
tag; see `clusters/cluster1/policy-versions.yaml`'s comment for the full
story and why `policy`'s `release-pins/v1.0.3`/`release-pins/v2.0.3`
branches are load-bearing, not cleanup candidates.)

## Admission-only semantics

**Retirement never evicts.** Removing a version from `policy-versions.yaml`
(or letting a `sunset:` date's retirement PR merge) stops that version's
policies from being installed -- it does not touch any workload already
running under it. A retired-version workload keeps running, unaffected,
right up until its *next recreation* (a rollout, a manual delete, a node
eviction -- anything that re-submits it to admission). At that moment the
orphan guard (issue 09's deterministic Deny catch-all) refuses it, because
no policy is left willing to opt it in. Governance debt is therefore always
visible, but only *becomes* visible at the next churn, never as a
retroactive mass eviction nobody asked for. This is a deliberate consequence
of ADR-0003 (Kyverno admission-time enforcement, not a controller that
reconciles existing objects) and ADR-0006 (no time-conditional policy
state) -- see `verify-orphan-guard.sh`'s "pre-existing orphans reported not
evicted" proof and `verify-retirement.sh` for the live version of this
claim.

```
flux-instance.yaml            FluxInstance -- pinned Flux 2.9.2, upstream-alpine variant
infrastructure/kyverno/       Kyverno engine: Namespace + HelmRepository + HelmRelease
infrastructure/monitoring/    issue 14: kube-prometheus-stack + Policy Reporter (both pinned) --
                                PolicyReport results as Prometheus metrics, Policy Reporter's own
                                pre-built Grafana dashboards auto-discovered by the sidecar.
                                Issue 15: kube-state-metrics customResourceState config (the
                                flux2-monitoring-example pattern, trimmed to the 3 Flux kinds
                                this repo uses) exposing gotk_resource_info; a combined
                                Flux-revision + PolicyReports dashboard, same ConfigMap +
                                sidecar mechanism, sharing one cluster+policy-version variable
clusters/cluster1/
  bootstrap.yaml               self-referential GitRepository+Kustomization: this repo
                                syncs itself, so infrastructure/kyverno/ becomes a real
                                Kustomization ("kyverno") other Kustomizations dependsOn
  policy-versions.yaml          the crux (PRD §6.4): one ResourceSet, one input carrying
                                a nested {version, commit, policies} array; the
                                resourcesTemplate ranges over it to generate a
                                GitRepository + one Kustomization per policy, per version.
                                Adding/removing an array element is the only change needed
                                to install/retire a version.
  apps.yaml                     ticket 07/08 (real-estate): five real team repos, each its own
                                GitRepository+Kustomization pair, branch-tracked -- storefront
                                (old Angular/npm, policy 2.2.0), ledger (Log4Shell-era log4j
                                2.14, policy 1.0.0, the laggard), reports (moderately old Flask,
                                policy 2.0.0), api (current Go deps, policy 2.2.0, the good
                                citizen), datastore (Crossplane claims, team-requested not
                                platform-planted, policy 2.2.0). Replaces the old apps monorepo
                                (app1/2/3, three identical nginx pods) -- archived, not deleted.
renovate.json                   issue 11: one customManager (git-refs datasource) bumps every
                                {tag, commit} pin to the policy repo -- the only pin surface in
                                this design, see the file's own description field for why
up.sh / down.sh                one command sequence, idempotent, clean teardown+recreate
verify-live.sh                 proves the admission verdicts: compliant admits, gate
                                violation refused, lane-keeper violation admits+reported,
                                unlabelled workload untouched
verify-coexistence.sh          proves issue 08: three versions live side by side,
                                collision-free, each judging only its own opted-in workloads
verify-orphan-guard.sh         proves issue 09: no label denied, unknown version denied,
                                allow-list tracks the installed set, pre-existing orphans
                                reported not evicted
verify-renovate.sh             proves issue 11: the customManager correctly targets each
                                element of the real multi-version array independently (a
                                fixture, not the live cluster -- no kubectl/KiND needed)
infrastructure/notifications/  issue 16, communicable's push half: Provider + Alert
                                broadcasting policy-source revision changes, scoped via
                                matchLabels to exactly the GitRepository objects
                                policy-versions.yaml's ResourceSet generates. address points
                                at an in-cluster echo receiver (receiver.yaml) since this repo
                                has no real chat-webhook credential -- a real deployment swaps
                                provider.yaml's address for a real Slack/Teams/etc webhook.
verify-notifications.sh        proves issue 16: the receiver already holds a real delivered
                                event for a currently-installed policy source's own revision --
                                proven live the moment that source last genuinely changed, not by
                                forcing a fresh reconcile of already-current, immutable content
verify-monitoring.sh           proves issue 14: PolicyReport metrics for every installed
                                version reach Prometheus; a non-compliant Audit workload
                                shows failing there without being evicted
verify-flux-dashboard.sh       proves issue 15: gotk_resource_info covers every installed
                                version; selecting a version resolves both "where is it
                                installed" and "is it passing" panel queries
infrastructure/crossplane*/    issue 18: Crossplane v2 core + AWS provider-family (S3, RDS)
                                CRDs, free and KiND-only -- no ProviderConfig, no cloud
                                credentials anywhere. Three Kustomizations
                                (crossplane -> crossplane-providers -> crossplane-sample)
                                chained by dependsOn + healthChecks so the provider CRDs
                                reaching Established gates everything downstream -- issue 19's
                                real cloud-policy Kustomizations (blocked on issue 08) will
                                carry the same dependsOn once unblocked.
verify-crossplane.sh           proves issue 18: CRDs Established, the ordering held, and the
                                sample RDS CR sits unreconciled (no auth on the critical path)
.github/workflows/pr-gate.yml   issue 12, extracted per ticket 03 (real-estate): invokes the
                                pinned policy-as-versioned-flux/pr-gate-action, digest-pinned --
                                gitsign verify-tag + tag-resolves-to-commit + kyverno test +
                                flux build --dry-run + rendered-version cross-check for every
                                array entry in a bump PR, required by a branch ruleset before
                                merge. The gate's own logic (and its self-check) now lives in
                                that repo, not here -- the gate that verifies pins is itself
                                pinned.
clusters/cluster2/              issue 10: a second, independent cluster profile from the SAME
                                fleet repo, >=2.0.0 only -- proves per-cluster narrowing.
                                Workload-plane only, minimal on purpose (no monitoring/
                                crossplane/notifications -- cluster-agnostic concerns already
                                proven once on cluster1).
up2.sh / down2.sh               cluster2's up.sh/down.sh
verify-retirement.sh            proves issue 10 against BOTH live clusters at once: a workload
                                pinned to 1.0.0 is refused on cluster2, admits on cluster1;
                                retiring 2.0.0 from cluster2's array prunes it and the orphan
                                guard refuses that version in the same reconcile
infrastructure/c2p/              issue 21: a real, continuously-running (*/15 * * * *) C2P
                                result2oscal CronJob against the live fleet's own PolicyReports
                                (not the issue 20 spike's throwaway cluster). Ticket 04
                                (real-estate): pins policy-as-versioned-flux/c2p-collector by
                                digest -- c2pcli/kyverno-plugin/kubectl baked in at release
                                time, run time down from ~4 minutes (cold git clone + go build)
                                to seconds-to-start. Writes OSCAL output to a ConfigMap, served
                                over plain unauthenticated in-cluster HTTP by a tiny nginx pod
                                (oscal-file-server) for Grafana's infinity datasource to read --
                                avoids needing a Grafana ServiceAccount token/RBAC grant. Ticket
                                08 (real-estate): the cloud exemplars that used to live here
                                (cloud-exemplars.yaml) moved to the datastore team's own repo,
                                team-requested claims instead of platform-planted -- the job
                                still has real findings, now attributable to a team.
```

## Run it

```sh
./up.sh                  # KiND -> Flux Operator -> Kyverno -> 3 policy versions -> guard -> 3 apps
./verify-live.sh         # admission verdicts against what's live
./verify-coexistence.sh  # multi-version coexistence claims against what's live
./verify-orphan-guard.sh # orphan guard claims against what's live
./verify-renovate.sh     # Renovate customManager against a fixture -- no cluster needed
./verify-notifications.sh # communicable claims against what's live
./verify-monitoring.sh   # PolicyReport -> Prometheus claims against what's live
./verify-flux-dashboard.sh  # Flux-revision + PolicyReports dashboard claims against what's live
./verify-crossplane.sh   # Crossplane CRD install + ordering claims against what's live
                          # PR gate: see policy-as-versioned-flux/pr-gate-action's own verify.sh
./up2.sh                 # second cluster: KiND -> Flux Operator -> Kyverno -> >=2.0.0 only
./verify-retirement.sh   # issue 10 claims against BOTH live clusters (needs up.sh AND up2.sh)
./down.sh                # tear down cluster1; ./up.sh again recreates cleanly
./down2.sh                # tear down cluster2; ./up2.sh again recreates cleanly
```

Grafana (`kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80`,
`admin`/`admin`) ships three Policy Reporter dashboards out of the box: "PolicyReports"
(cluster-wide, filterable by the `policy` variable -- which carries the version suffix),
"PolicyReport Details", "ClusterPolicyReport Details" -- plus the "Flux Revision + PolicyReports"
dashboard (issue 15, completed by issue 21 into the full four-panel CIO story): "which version,
where" (`gotk_resource_info`), "is it passing" (`policy_report_result`), "are controls satisfied"
(issue 21 -- OSCAL assessment-results via the infinity datasource, live from the `c2p-collector`
CronJob), and "adoption velocity" (issue 21 -- real Renovate PR state on this repo, infinity
querying GitHub's public API). `cluster` is a single fixed value today (one Prometheus per
cluster) -- real cross-cluster querying (Thanos, federation, or a per-cluster datasource this
variable picks between) is still open: `cluster2` (issue 10) exists now, but doesn't run
monitoring (deliberately minimal, see that section above), so there's still no second Prometheus
to actually query across. The OSCAL and Renovate panels aren't filtered by `policy_version` --
PRs bump multiple array elements at once and OSCAL findings are control-level, not per-version;
forcing that filter would misrepresent the data, so they're left unfiltered instead.

Prereqs: docker, kind, kubectl, helm, flux, jq. Readiness is gated by native
`kubectl wait --for=condition=Ready` throughout, never a jsonpath polling
loop.
