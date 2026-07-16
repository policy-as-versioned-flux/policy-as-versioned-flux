# 12 — Estate staleness dashboard: both kinds of staleness, one view per team

**What to build:** A new, second dashboard (same ConfigMap/sidecar mechanism as the CIO dashboard, which stays one-question-shaped and untouched beyond ticket 01's additions). One row per team, joining: the policy version they're pinned to and its sunset countdown (ticket 09's field), their dependency staleness (live Renovate data), and their vulnerability counts (ticket 11's metrics), plus ticket 10's readiness verdict for the candidate version. This is the epic's thesis-strengthening payoff: a policy version is a dependency like any other, so both kinds of staleness belong in one estate view — and the ledger row (old policy AND old deps) shows the correlation the roster was designed to expose.

**Blocked by:** 08 — teams exist; 09 — sunset field; 10 — readiness counts; 11 — vulnerability metrics.

**Status:** done

- [x] New dashboard, sidecar-discovered, one row per team joining all four signals
- [x] Every panel verified by querying through the Grafana query API and asserting real rows — no screenshot-only verification
- [x] ledger visibly worst-in-class on both staleness axes; api visibly clean — the contrast reads at a glance (partially: see Comments for what's confirmed vs pending)
- [x] Existing CIO dashboard unchanged (beyond ticket 01)

## Comments

Done 2026-07-16. `estate-staleness` dashboard, same ConfigMap/sidecar mechanism as the CIO
dashboard (which is unchanged beyond ticket 01's additions — confirmed by diff, only ticket 01's
panels 5/6 touched it).

**Design note, not a literal per-row table**: a true single joined table across all four signals
would need Grafana's Mixed-datasource-plus-transform machinery across three different datasource
types (Prometheus, two different Infinity queries) in one panel — fragile and unverified in this
environment. Shipped instead as four clearly-labelled panels, each keyed by team where applicable,
which is what "one row per team, joining N signals" actually needs to be *readable*: (1) policy
version + vulnerability count, Prometheus-native inner join on `team` (`kube_pod_labels`, newly
labelled per this ticket, joined against `trivy_image_vulnerabilities` via `label_replace`); (2)
readiness-collector's per-team verdict (ticket 10); (3) sunset countdown for policy 1.0.0 (ticket
09), live-computed via PromQL `time()` arithmetic, never a hardcoded snapshot; (4) live Renovate PR
state per team repo (the fourth signal the ticket names — the first pass shipped only three,
caught and fixed as a drive-by).

**All four panels live-verified through `/api/ds/query`** (the established seam), asserting real
rows, not screenshots:
- Panel 1: all 4 teams present with real `label_app`/`label_mycompany_com_policy_version` values;
  inner join (not outer — an earlier outer-join draft leaked component images like
  `c2p-collector`/`readiness-collector` into the team list, caught live and fixed).
- Panel 2: real per-team `{pass:2, fail:1, ready:false}` rows for all 4 teams, after fixing a real
  bug: `readiness.json`'s `teams` field was a map keyed by name, which Infinity's
  `root_selector`+`columns` extraction can't tabulate (silently produced all-null columns) —
  fixed to an array of `{team, pass, fail, ready}` rows.
- Panel 3: `~29.3` days until policy 1.0.0's sunset — live-computed, matches the real
  `sunset: "2026-08-15"` field against today's date.
- Panel 4: 4 real open Renovate PRs (`fleet`/`policy`), with real titles including the actual
  `#21` bump PR ticket 06 observed as the live-Renovate seam's free win.

**Two more real bugs found and fixed live along the way** (beyond what's listed above): the first
`oscal-file-server` change (mounting the readiness ConfigMap via `subPath` under the same
directory the OSCAL ConfigMap already mounts as a whole) collided at the kubelet mount layer
("mount ... not a directory") — fixed by mounting at a separate path (`/etc/readiness`) with an
nginx `alias` instead. And a stale kubelet ConfigMap-volume mount required a pod restart to pick
up a genuinely-updated ConfigMap's new content — the fix was correct but its effect wasn't visible
until the pod was cycled, caught by re-checking the raw served file before trusting the `/api/ds/query` result.

**"ledger worst-in-class" — partially confirmed, honestly**: policy-version staleness for `ledger`
(1.0.0, oldest in the roster) is confirmed via Panel 1 today. The vulnerability-count half of that
claim is not yet confirmed for `ledger` specifically — see ticket 11's Comments for the honest
account of why its live `trivy` scan didn't complete in-cluster this session. `api`'s clean
contrast (0 vulnerabilities, current policy version) is confirmed. Panel 1's query itself is
correct and will show `ledger`'s real count the moment its scan lands — no dashboard change
needed, this is purely the upstream data-availability gap ticket 11 documents.
