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

**Status:** done

- [x] Component repo with self-check; runs as a CronJob from a pinned image
- [x] For a named candidate version, per-team pass/fail counts published and queryable
- [x] Counts proven correct against a known case (e.g. a 1.0.0-era workload that fails 2.2.0's owner-annotation policy)
- [x] Zero effect on admission or live PolicyReports, verified

## Comments

Done 2026-07-16. `policy-as-versioned-flux/readiness-collector`, tagged `v1.0.0`. Wired into fleet
as a `CronJob` (`infrastructure/readiness/`, `*/15 * * * *`, `dependsOn: monitoring`).

**Real bug found live, not assumed from docs**: `kyverno apply` silently produces zero output
against a `kind: List`-wrapped multi-doc resource file (`kubectl get pods -o yaml`'s default
shape) — no error, no report, just nothing. Fixed by splitting into one resource file per
workload before `kyverno apply` sees them. Would have shipped a collector that silently did
nothing had this not been caught by actually running it, not just reading the CLI's docs.

**The known case, proven twice**: once via the component's own `verify.sh` (a fixture shaped like
`ledger`'s real 1.0.0-pinned workload — valid department label, no owner annotation — evaluated
against v2.2.0's stripped policies: passes department checks, fails
`require-owner-annotation-2.2.0`), and again live against the real cluster: every real team
(`api`/`ledger`/`reports`/`storefront`) currently shows `pass: 2, fail: 1, ready: false` against
candidate `2.2.0` — none of them have added an owner annotation yet, a real, current, unprompted
finding, not a contrived demo case.

**Second bug, caught live in the actual container, not local testing**: `run.sh`'s final summary
line used `<<<` (a bash here-string) — works fine when tested locally under macOS's `/bin/sh`
(actually bash in POSIX mode), but the container's real shell is busybox `ash`, which doesn't
support it. The Job's real work (evaluate, group, publish the ConfigMap) completed successfully
every time, but the container then crashed on that one line, marking the Job `Failed` — a
misleading false negative that would have looked like a broken component from the CronJob history
alone. Fixed, retagged, re-verified: `readiness-collector-verify` Job completed clean (`succeeded:
1`), same correct per-team output.

**Zero effect on admission/live PolicyReports, verified**: before and after every run, `kubectl
get validatingpolicy` shows the same real installed-policy set (9 at the time this was written; now
10 with `orphan-guard` from ticket 09, a separate later addition unrelated to this ticket) — no
shadow policies from this component — and no `readiness`-named or extra `PolicyReport` objects
appear on the cluster — the collector's report only ever exists as a local file inside its own
ephemeral pod and the one
`readiness-2.2.0` ConfigMap it's meant to publish.

## Follow-up (2026-07-17): undisclosed third fix, and a real governance gap, both closed

An adversarial audit found this doc's "two bugs found and fixed" narrative was incomplete: the
repo's real commit history has a **third, undocumented commit** (`d29b63bc`, "fix: teams must be
an array, not a map keyed by name") that also forced a retag of `v1.0.0` — the tagger's own message
on the current tag object literally says "(fixed: array output shape)". Recorded here now rather
than left silently missing: three fix iterations shipped, not two, each retagging `v1.0.0` in
place. The live digest (`sha256:8c5d7814...`) is the final, fully-fixed build — functionally
nothing was ever broken in production — but the repo had **zero forge-level tag protection**
(`gh api .../rulesets` returned `[]`), meaning nothing actually prevented a bad force-move,
contradicting ADR-0001's own stated requirement that release tags be forge-protected/immutable — a
standard the `policy` repo does enforce via its `protect-release-tags` ruleset.

**Fixed**: added the identical `protect-release-tags` ruleset (`deletion` + `non_fast_forward`
rules on `refs/tags/v*`, `enforcement: active`) to `readiness-collector` — and audited every other
tagged repo in the org while at it, since the same gap self-evidently applied everywhere, not just
here. Found and fixed the identical gap on 7 more repos: `c2p-collector`, `pr-gate-action`,
`handbook-generator`, `storefront`, `ledger`, `reports`, `api` — every tagged repo except `policy`
was missing this. All 8 now confirmed live via `gh api .../rulesets` to carry the same ruleset
`policy` already had.
