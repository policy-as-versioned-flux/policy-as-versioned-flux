# Live GitHub state — hub + 8 units + 2 org settings

Captured 2026-09-02 ~12:55 UTC (current wall clock: `date -u` → `Wed 2 Sep 2026 12:54:31 UTC`).
Method: `gh api` / `gh run list` / `gh pr list` GET calls, plus `git tag -v` / `gitsign verify-tag` against the fresh unit clones under `scratchpad/units/`. Raw JSON dumps are saved at `scratchpad/review/understand/raw/<repo>/*.json` for every repo — anything summarized below can be re-checked against those files.

Auth: `gh auth status` → token scopes `delete_repo, gist, read:org, repo, workflow`. **No `admin:org`.**

## Coverage gaps (could not look)

- **Org Actions permissions** (`gh api orgs/<org>/actions/permissions`): 403 "You must be an org admin or have the actions policies fine-grained permission" on both `policy-as-versioned-flux` and `policy-as-versioned-platform`; `gh` itself says this needs `admin:org` scope, which the token doesn't have. Not checked for any of the 9 repos' orgs. This is a genuine token limitation, not a "nothing to see" result.
- **Repo Actions permissions** (`repos/O/R/actions/permissions`) — not queried at all (ran out of scope budget after the org-level call failed; same 403/needs-scope risk applies at repo level too, untested).
- **`repos/O/R/installation`** (GitHub App installation check) — every repo returned `401 {"message":"A JSON web token could not be decoded"}`. This endpoint needs GitHub App JWT auth, which a PAT-based `gh` session cannot provide; it is not evidence Renovate is or isn't installed. Renovate's actual presence is inferred instead from bot-authored PRs (see below), which is solid positive evidence for platform/nist/ico/driftwood/tuppence/ludlow but there is no direct "app is installed" confirmation and no negative evidence was sought for feeds/insurer.
- **Mend/Renovate dashboard issue** — not checked (would require opening a dashboard issue on GitHub if one exists; not searched for).
- Did not open `talk/captures/*` off `origin/main` for the hub (the task's "newest citable truth line" pointer) — this survey stayed at the GitHub-API/Actions-run layer per the assigned scope; the truth-log content itself is out of scope here.
- Did not check the two extra orgs' members, teams, webhooks, or security settings beyond the `orgs/<org>` GET already shown in the org-level fields below (billing email, 2FA requirement, default permissions) — only `policy-as-versioned-flux` and `policy-as-versioned-platform` orgs were queried for settings; the other 7 unit orgs' `orgs/<org>` settings were not fetched (only their repo lists).
- Did not inspect the ludlow/tuppence/driftwood-only `twin-sweep` design in code, nor read the propose-tier/drift-sample/fetch workflow bodies beyond `grep cron:` and one log tail each — full workflow YAML wasn't read end-to-end for every workflow, only enough to find the cron line and one failing job's error line.

## Org settings (2 extra orgs)

| org | 2FA required | members can create repos | default repo perm | billing email | public repos |
|---|---|---|---|---|---|
| policy-as-versioned-flux | false | true | read | chris@cns.me.uk | 16 |
| policy-as-versioned-platform | false | true | read | chris@cns.me.uk | 1 |

(The other 7 unit orgs' `orgs/<org>` settings were not fetched — only confirmed to exist and to each contain exactly one repo, via `gh repo list`.)

Note: `policy-as-versioned-flux` org contains **16 repos**, not just the hub — it also holds all 14 original-2022-thesis legacy repos (`reports, c2p-collector, api, fleet, storefront, policy, readiness-collector, ledger, governance-agent, handbook-generator, apps, datastore, pr-gate-action, renovate-config, cloud`) plus `policy-as-versioned-flux` itself. These legacy repos were not surveyed here (out of this task's scope — task named only the hub + 8 units).

## Per-repo table

| repo | default branch | workflows (state) | runs last 7d | open PRs | tags | rulesets | branch protection |
|---|---|---|---|---|---|---|---|
| policy-as-versioned-flux/policy-as-versioned-flux | main | truth.yml (`47 5 * * *`), twin.yml (`17 5 * * *`) — both active | 46 (all truth/twin) | 0 | **none** (404 on refs/tags) | `[]` | `{"message":"Branch not protected"...}` (404) |
| policy-as-versioned-platform/platform | main | cut-release.yml, fetch.yml (`23 1 * * *`), release.yml — all active | 19 | 1 (Renovate "Configure Renovate") | 11: policy/v2.0.0, policy/v2.0.1, policy/v3.0.0, policy/v4.0.0, v0.1.0, v0.1.1, v1.0.0, v1.1.0, v1.1.1, v2.0.0, v2.0.1 | `[]` | not protected |
| policy-as-versioned-nist/nist | main | cut-release.yml, fetch.yml (`41 2 * * *`), release.yml — active | 5 | 1 (Renovate) | v1.0.0, v1.1.0 | `[]` | not protected |
| policy-as-versioned-ico/ico | main | cut-release.yml, fetch.yml (`09 4 * * *`), release.yml — active | 5 | 1 (Renovate) | v1.0.0, v3.0.0 | `[]` | not protected |
| policy-as-versioned-driftwood/driftwood | main | cut-release.yml, drift-sample.yml (`20 6 * * *`), propose-tier.yml (`47 6 * * *`), release.yml, renovate-run.yml (`11 6 * * *`), "shift-left policy check" (PR-triggered, no cron), twin-sweep.yml (`5 7 * * *`), verify-identity-regexp.yml — all active | 50 | 0 | v1.0.0, v1.1.0 | `[]` | not protected |
| policy-as-versioned-tuppence/tuppence | main | cut-release.yml, drift-sample.yml (`22 8 * * *`), propose-tier.yml (`49 8 * * *`), release.yml, renovate-run.yml (`13 8 * * *`), shift-left — active | 31 | 0 | v1.0.0, v1.1.0 | `[]` | not protected |
| policy-as-versioned-ludlow/ludlow | main | cut-release.yml, drift-sample.yml (`16 9 * * *`), propose-tier.yml (`43 9 * * *`), release.yml, renovate-run.yml (`07 9 * * *`), shift-left — active | 25 | 0 | v1.0.0, v1.1.0 | `[]` | not protected |
| policy-as-versioned-feeds/feeds | main | cut-release.yml, fetch.yml (`17 3 * * *`), release.yml — active | 7 | 0 | threat-register/v1.0.0, threat-register/v2.0.0 | `[]` | not protected |
| policy-as-versioned-insurer/insurer | main | cut-release.yml, fetch.yml (`31 5 * * *`), release.yml — active | 4 | 0 | v1.0.0 | `[]` | not protected |

**Anomaly across all 9 repos: zero rulesets and zero branch protection on `main`, hub included.** Every merge below (all 46 non-Renovate merges across the fleet) is a self-merge with no possibility of a blocking required review — there is no branch rule that could have required one.

## Tag signing (gitsign / sigstore x509)

All 24 tags across the 8 unit repos verified with `git -c gpg.format=x509 -c gpg.x509.program=gitsign tag -v <tag>` against the fresh clones. Every single one returned `gitsign: Good signature from [.../.github/workflows/cut-release.yml@refs/heads/main](https://token.actions.githubusercontent.com)` — i.e. signed by the repo's own `cut-release.yml` GitHub Actions OIDC identity, Rekor-logged (`Validated Rekor entry: true`). `Validated Certificate claims: false` appears on every tag but that's expected/inert — it only means no `--certificate-identity`/`--certificate-oidc-issuer` was passed to the verify call, not a signature defect. **No unsigned or bad-signature tags found.** (Plain `git tag -v` without the gitsign config fails with `gpgsm: can't open '-'` on every tag — that's a local-git-config artifact, not a signature problem; the gitsign-aware invocation is the correct check and it's clean.)

The hub itself has no tags at all (confirmed via 404, not just an empty list).

## PR merge-authorship

Every human-authored, human-merged PR across all 9 repos (46 total closed PRs surveyed, minus Renovate-authored ones) was **authored by `chrisns` and merged by `chrisns`** — the same identity both ways, on every single one, with no exception found. E.g. driftwood #22, #21, #19, #18, #16, #15, #14, #12, #11, #6; tuppence #14, #13, #12, #11, #9, #8, #5; ludlow #12, #11, #10, #8, #7, #4; platform #8 through #2; nist #3, #2; ico #2; hub #1. Combined with the "no branch protection" finding above, nothing in these repos' GitHub configuration could have stopped any of these self-merges, or required a second reviewer, even in principle.

Several "test:" PRs (driftwood #10, #9, #8, #7, #4; tuppence #7, #6, #3, #2; ludlow #6, #5) show `mergedBy: null` / `mergedAt: null` while `state=closed` — these were **closed without merging** (throwaway verification branches), not silently-merged. Renovate's own `Configure Renovate - autoclosed` PR (#1 in platform/nist/ico/driftwood/tuppence/ludlow) is likewise closed-not-merged by design.

## Renovate presence

Direct app-installation check unavailable (see Coverage gaps). Indirect evidence:
- `app/renovate` opened PR #1 "Configure Renovate" and it is **still open** in platform, nist, and ico (created 2026-08-21T07:39). In driftwood/tuppence/ludlow the equivalent PR was auto-closed and Renovate has since opened real dependency-bump PRs (e.g. driftwood #17, #13, #5 "Update dependency ... to v2"/platform pin bumps; #20 merged by chrisns).
- driftwood/tuppence/ludlow additionally run a self-hosted `renovate-run.yml` on cron (driftwood `11 6`, tuppence `13 8`, ludlow `07 9`) — i.e. these three units have **two** Renovate mechanisms (hosted app + self-hosted cron action). This matches the already-known ticket 61 "exactly one Renovate acts on this repo" (driftwood #19, merged 2026-09-01) — a fix for exactly this duplication, already landed on driftwood; tuppence/ludlow still show both mechanisms present as of this survey and were not confirmed fixed.
- feeds and insurer show **no** Renovate PR at all (open or closed) in the pulled data — either Renovate was never configured there, or its onboarding PR predates the window queried (`--limit 50` on closed PRs, but feeds/insurer both showed 0 total closed PRs, so it's a clean "not present," not a truncation artifact).

## Cron vs actual firing delay

GitHub Actions is well known to delay `schedule` triggers under load; this fleet's delay is on the high side and directionally consistent with the "Clock first firings" memory (~5h delay, three real bugs). Using the two most recent `schedule`-triggered runs of each cron per repo, delay = actual UTC time of run minus the cron's UTC time (same day):

| repo | workflow | cron (UTC) | most recent 2 fires (UTC) | delay |
|---|---|---|---|---|
| hub | truth | 05:47 | 09:54 (09-02), 10:27 (09-01) | 4h07m, 4h40m (worst seen in 6 samples: 17:42 on 08-28, **11h55m**) |
| hub | twin | 05:17 | 09:36 (09-02), 10:05 (09-01) | 4h19m, 4h48m (worst: 17:25 on 08-28, **12h08m**) |
| platform | fetch | 01:23 | 06:00 (09-02), 06:20 (09-01) | 4h37m, 4h57m |
| nist | fetch | 02:41 | 07:18 (09-02), 07:58 (09-01) | 4h37m, 5h17m |
| ico | fetch | 04:09 | 08:43 (09-02), 09:21 (09-01) | 4h34m, 5h12m |
| feeds | fetch | 03:17 | 07:54 (09-02), 08:37 (09-01) | 4h37m, 5h20m |
| insurer | fetch | 05:31 | 09:45 (09-02), 10:16 (09-01) | 4h14m, 4h45m |
| driftwood | drift-sample | 06:20 | 11:20 (09-02, success), 11:41 (09-01, **failed**) | 5h00m, 5h21m |
| driftwood | renovate-run | 06:11 | 11:12 (09-02), 11:34 (09-01) | 5h01m, 5h23m |
| driftwood | propose-tier | 06:47 | 11:43 (09-02), 12:01 (09-01) | 4h56m, 5h14m |
| driftwood | twin-sweep | 07:05 | 12:04 (09-02, **failed**), 12:31 (09-01, **failed**) | 4h59m, 5h26m |
| tuppence | drift-sample | 08:22 | 12:49 (09-02, success), 13:32 (09-01, **failed**) | 4h27m, 5h10m |
| tuppence | renovate-run | 08:13 | 12:46 (09-02), 13:29 (09-01) | 4h33m, 5h16m |
| tuppence | propose-tier | 08:49 | 13:42 (09-01, **failed**); no 09-02 fire yet as of capture (12:54 UTC now, expected ~13:49) | 4h53m (not a miss — not yet due) |
| ludlow | drift-sample/propose-tier/renovate-run | 09:16/09:43/09:07 | last schedule fires all on 09-01 ~14:05-14:18; no 09-02 fire yet as of capture | not a miss — cron+~5h still ahead of current 12:54 UTC |

No cron was found to have been *skipped entirely* (missed a whole day) — every gap above is explained by the ~4.5-5.5h delay pattern plus the current-time cutoff, not a dropped firing. One outlier pair (hub truth/twin on 2026-08-28, ~12h delay) is well beyond the fleet's normal 4.5-5.5h band and worth flagging on its own.

## Failing workflows nobody has fixed (with root cause read from logs)

1. **Hub `twin.yml`: 25/25 (100%) of runs in the pulled window (back to 2026-08-16) are `failure`.** Latest run 2026-09-02T09:36 fails on three separate steps: `typecheck` (`twin/feed_signal.py:232: error: Unused "type: ignore" comment`), `invariants`, and `tests` — the `tests` failure is `AssertionError: flux_coverage_floor_is_still_reachable: the pre-registered coverage floor of 90% can no longer be reached: 3/1966 sa...` citing "build ticket 70's finding 1," i.e. this is the already-known, already-recorded drift-floor-unreachable finding (matches the "Flux verdict closes unmeasured" memory) — **not new**, but it does mean the workflow's raw CI conclusion is failure on every run, continuously, and that state is being treated as an accepted/recorded finding rather than something anyone is trying to turn green.
2. **Hub `truth.yml`: 17 consecutive failures** out of 21 pulled, including the very latest run (2026-09-02T09:54, immediately following run=21's 10:11Z truth-line capture). Failure reason: `::error::the scheduled truth run staged a declaration outside the observation lane` / `::error::the scheduled truth run left a change outside the observation lane`. One lone `workflow_dispatch` success exists at 2026-08-28T04:34:15 sandwiched between failures — i.e. someone manually re-ran it once and it passed, but the *scheduled* path has not passed since.
3. **`feeds/fetch.yml` (market-moves): both runs in the window fail** with `::error::the scheduled fetch left a change outside the observation lane`, and the log shows the actual stray files: `__pycache__/bump.cpython-312.pyc`, `fetch/__pycache__/lib.cpython-312.pyc` — i.e. Python bytecode caches generated during the run are outside the declared `OBSERVATION_LANE` (`talk/truth.log drift/samples.jsonl talk/captures observations`) and the workflow's own guard correctly refuses to let them through, but nobody has added a `.gitignore`/cleanup step to stop generating them. Same defect class as #2 above (a "declaration outside the observation lane" guard tripping), independently in two different repos.
4. **`insurer/fetch.yml` (requote): both runs fail, across all three matrix legs** (`requote (tuppence)`, `requote (ludlow)`, `requote (driftwood)`) with `::error::the scheduled re-quote left an uncommitted change on main` — same guard-class bug as #3, third independent occurrence.
5. **`driftwood/twin-sweep.yml`: both scheduled runs in the window fail**, both with `::error::the sweep could not render the overlay at all (exit ${rc})` — a rendering failure, not the observation-lane guard; distinct root cause from #2-#4, and not yet linked to a known ticket in what I read.
6. **`tuppence/propose-tier.yml` scheduled run (2026-09-01T13:42:57) fails at checkout**: `##[error]A branch or tag with the name 'ecosystem/thin-slice' could not be found`. This means the workflow (or its trigger config) is pinned to a branch ref, `ecosystem/thin-slice`, that has since been deleted/merged away — a stale-ref bug distinct from the observation-lane class. Worth checking whether `ludlow`'s and `driftwood`'s propose-tier crons carry the same stale-ref risk (not individually re-checked here beyond driftwood's own propose-tier runs currently showing success).
7. **`driftwood/drift-sample.yml` scheduled run (2026-09-01T11:41) fails during tool install**: `install the pinned tools (binary + checksum, no marketplace action)` → `exit code 23` — looks like a transient download/checksum failure (curl exit 23 = "write error", commonly a truncated download); the very next `workflow_dispatch` re-run at 20:41 the same day succeeded, consistent with transient flakiness rather than a persistent defect, but it's still an unexplained failure nobody has annotated.

Findings #3 and #4 in particular look like the same unaddressed bug class ("scheduled write-back job generates untracked/uncommitted artefacts and its own after-the-fact guard correctly blocks them") appearing independently in three repos (hub, feeds, insurer) — a good candidate for a single shared fix (e.g. add cache/pycache cleanup or `.gitignore` entries before the git-status check) rather than three separate patches.

## Not covered / explicitly out of scope for this pass

- Legacy 2022-thesis org repos (14 of them) — not surveyed at all, per the task's repo list.
- Repo-level Actions permissions API — not attempted after the org-level 403 (same missing-scope risk untested at repo scope).
- Full historical run list beyond `--limit 50` per repo (older failures/successes before the 7-day-ish window shown here were not pulled).
- Full workflow YAML review beyond the cron line and one failing step's error text per workflow — e.g. concurrency groups, permissions blocks, and non-cron trigger conditions were not audited.
