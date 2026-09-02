# 57 — feeds and insurer become runnable: workflows registered, first signed tags cut

Type: task (HITL)
Status: claimed
Blocked by: none

## Question

GitHub registers zero workflows in feeds and insurer (0 runs ever) despite files on the default branch with Actions enabled, so their crons never fire and cut-release cannot be dispatched — the only route to a gitsign-signed first tag. Diagnose the registration failure (the unconventional default branch ecosystem/thin-slice is the prime suspect; renaming or pushing a registering commit are the candidate fixes), then the owner dispatches cut-release once per repo to cut the first signed feed and quote tags, queues bump.yaml so releases can follow, and we confirm the next day's cron fires. HITL because the branch decision and every dispatch are the owner's. Done = both repos show a scheduled run and at least one signed tag each, and the adopter subscriptions' could-not-looks convert on a citable run.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M1 (feeds/insurer unrunnable, 2 confirmed findings), the zero-signed-tags leg of M10, minor stale feeds tree on platform (once first tag exists).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Held round — 2026-09-01

Diagnosed AFK. The dispatches and the branch decision are the owner's, so this round is held.

### Diagnosis

The workflow files are present on the default branch of both repos, and Actions is enabled
(`enabled: true, allowed_actions: all`). GitHub still lists **0 workflows**, 0 runs, 0 tags on both.

The cause is visible in the events API. Each repo's entire event history is **one `CreateEvent`**
for `ecosystem/thin-slice` (feeds 2026-08-31T07:57:15Z, insurer 07:57:22Z) and **no `PushEvent`**,
although the five commits are dated 2026-08-28/29. Every sibling repo shows `PushEvent` entries —
including driftwood pushing to a branch of the same name. GitHub registers workflows from push
events; these repos never received one, so nothing registered. An unregistered workflow cannot be
dispatched (404) and its cron never enters the scheduler. The survey of all 24 estate repos is
total: every repo with `default=main` and workflow files registers them; only these two
(`default=ecosystem/thin-slice`, born from a pushless ref creation) register zero.

A second, independent fault makes the branch name matter anyway: both `release.yml` files pin
`EXPECTED_IDENTITY_REGEXP` to `cut-release.yml@refs/heads/(main|release/N.M.x)`. A tag cut by
`cut-release.yml` running on `ecosystem/thin-slice` would fail its own release verification. So
the branch must become `main` (or both regexps must be edited); rename is the smaller change.

Blast radius of a rename: checked and empty. No file in either repo mentions `thin-slice`; each
repo has exactly one branch, no open PRs, no applied rulesets; nothing in the hub, `talk/`,
`verify/` or `estate/` references the branch for these repos.

Release-gate readiness: run 16 grades `verify-feeds.sh`, `verify-market-and-news.sh`,
`verify-insurer-party.sh` and `verify-insurer-quote.sh` all PASS, so the dispatch-time gates
will pass. `bump.yaml` is `bump: none` on every feed already — nothing to queue by hand; the
fetch clock rewrites it in the PRs it opens.

What converts: run 16 shows three SKIPs in `verify-feed-contract` — driftwood, tuppence and
ludlow each "waiting for tag threat-register/v1.0.0 on feeds". `verify-schedules` will also start
seeing both clocks.

### Decision for the owner

Rename the default branch to `main` on both repos. The alternative (keep the branch, edit both
`release.yml` regexps, still push a registering commit) is more edits for a worse end state.

### Checklist (owner; step 2 I can run on your word)

1. Rename (needs admin):
   `gh api -X POST repos/policy-as-versioned-feeds/feeds/branches/ecosystem%2Fthin-slice/rename -f new_name=main`
   `gh api -X POST repos/policy-as-versioned-insurer/insurer/branches/ecosystem%2Fthin-slice/rename -f new_name=main`
2. Registering push — a rename is not a push event. Push one empty commit to `main` on each repo
   (`git commit --allow-empty -m "register workflows"`), or edit the README in the web UI (a web
   commit is a push event). Verify: `gh api repos/<r>/actions/workflows --jq .total_count` shows 3.
3. Dispatch feeds (version has NO leading v):
   `gh workflow run cut-release.yml -R policy-as-versioned-feeds/feeds -f feed=threat-register -f version=1.0.0 -f message="first signed release of the threat-register feed"`
   This cuts `threat-register/v1.0.0` and converts the three adopter SKIPs. The other feeds
   (cve, eol, fx, market-moves, news) can follow at leisure; nothing waits on them.
4. Dispatch insurer (version HAS a leading v — the two workflows differ):
   `gh workflow run cut-release.yml -R policy-as-versioned-insurer/insurer -f version=v1.0.0 -f message="first signed insurer release: three quotes at v1"`
5. Optional: dispatch `release.yml` with the new tag on each repo to publish the GitHub Release —
   the tag push from cut-release cannot auto-trigger it (documented in the file).
6. Apply the observation-lane ruleset on both repos before the first cron commits to
   `observations` (ticket 28's server-side half, currently unapplied — see
   `.github/rulesets/README.md` in each repo).
7. Next day: feeds cron 03:17 UTC, insurer 05:31 UTC. Done when both repos show a scheduled run,
   one signed tag each, and the citable TRUTH run flips the three feed-contract SKIPs to PASS.

## Progress — 2026-09-01, owner round answered and executed

The owner agreed the rename and instructed the assistant to run the checklist.

1. **Renamed**: both default branches are `main`.
2. **Cause confirmed by cure**: an empty commit pushed to `main` registered nothing. A commit
   that TOUCHES the workflow files registered all three on each repo within seconds. GitHub's
   indexer wants a push that modifies `.github/workflows/`; the pushless ref creation of
   2026-08-31 never gave it one. Pushes went through the guard's sanctioned route:
   `twin/ENACT_MODE` flipped to `development` and restored per push (hub commits fd9b779,
   a79261b, 7ee4f4f, bba9ec5, c40887c, 245e5b4), scope one registering/repair push at a time.
3. **Defect found and fixed on the first-ever dispatch**: feeds `cut-release.yml` ran
   `verify-feeds.sh` with no platform checkout, so the release gate exited 3. Fixed by checking
   out platform `v2.0.1` into `.platform` (feeds commit 69c89b0), the path the script already
   probes.
4. **Tags cut, both signed by the Actions identity and verified by each repo's own
   `release.yml` identity-pinned gitsign verification**:
   - feeds `threat-register/v1.0.0` (cut run 33481362587, release run 33481557286, success)
   - insurer `v1.0.0` (cut run 33480939175, release run 33481030227, success)
5. **All six workflows are `active`**, including both `fetch` crons (feeds 03:17 UTC,
   insurer 05:31 UTC).
6. **Ruleset note**: the observation-lane push ruleset cannot be applied — GitHub allows push
   rulesets only on private/internal repos and these are public. Documented in each repo's
   `.github/rulesets/README.md`; the client-side cage step carries the load (ticket 70's
   territory).

Still open before resolution (tomorrow):
- the first scheduled `fetch` run on each repo (2026-09-02, 03:17 and 05:31 UTC);
- the next citable TRUTH run converting the three `verify-feed-contract` SKIPs
  ("waiting for tag threat-register/v1.0.0") to PASS.

## Comments

**2026-09-01, found while working ticket 61.** The rename in step 1 removed
`ecosystem/thin-slice` from both repos, and GitHub does not redirect a deleted
branch name. Twelve workflow checkout refs in tuppence and ludlow (shift-left,
cut-release, propose-tier -- two each) and six in driftwood still pointed at
it, so every compose-check in every adopter has failed at checkout since the
rename. Driftwood's six are fixed on ticket 61's branch
(`ticket-61-renovate-completes-step-2`, local, waiting on the owner's push).
Tuppence and ludlow still carry theirs: repair them with ticket 62's re-pin,
or as a small follow-up PR per repo before any other PR there can go green.

**2026-09-02, review.** Claimed and mostly done: workflows registered, first signed tags cut on feeds and insurer. Both clocks are red for new reasons: feeds' fetch dies in its own cage on stray __pycache__ files (ticket 85 item 1); the insurer's requote refuses because the adopter tag it pins has no exposure section (ticket 77 item 2). Close this ticket on the registration and tags; the reds are owned elsewhere. Record: REVIEW-2026-09-02.md R8.
