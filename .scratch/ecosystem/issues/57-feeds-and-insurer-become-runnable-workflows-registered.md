# 57 — feeds and insurer become runnable: workflows registered, first signed tags cut

Type: task (HITL)
Status: resolved
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

**2026-09-03, closing round (wave 1 of the everything-open build).** Re-verified every claim
in the Progress section against the real remotes rather than the record, then closed on the
registration and the tags as the 2026-09-02 review (R8, M1) and the map both say. Evidence,
decisions and what still waits are in the Answer below. Nothing in an estate unit changed; the
hub change is this file alone.

## Answer — 2026-09-03, closed on registration and tags

### What was built (2026-09-01, owner-instructed; re-verified live 2026-09-03)

1. Default branch renamed to `main` on both repos (was `ecosystem/thin-slice`, born from a
   pushless ref creation that GitHub's workflow indexer never saw).
2. A commit touching `.github/workflows/` pushed to each repo; GitHub registered all three
   workflows per repo within seconds. An empty commit had registered nothing, which confirmed
   the diagnosis by cure.
3. Feeds `cut-release.yml` repaired to check platform out for its release gate (feeds 69c89b0).
4. First signed tags cut by `cut-release.yml` dispatch and verified by each repo's own
   `release.yml` (identity-pinned `gitsign verify-tag`, offline Rekor bundle).

### Evidence, all from the real remotes on 2026-09-03

Workflows and default branch (`gh api repos/<r>` and `.../actions/workflows`):

```
policy-as-versioned-feeds/feeds     default=main   cut-release active, fetch active, release active
policy-as-versioned-insurer/insurer default=main   cut-release active, fetch active, release active
```

Tags (`git ls-remote --tags`; tag objects via `gh api repos/<r>/git/tags/<sha>`), each an
annotated tag carrying a `-----BEGIN SIGNED MESSAGE-----` (gitsign, PKCS7) signature by
`policy-as-versioned release bot`, and each verified by a green `release.yml` run whose step
`gitsign verify-tag, identity-pinned, offline Rekor bundle` concluded `success`:

```
feeds   threat-register/v1.0.0  tag fba1154 -> 69c89b0  cut run 33481362587, release run 33481557286
feeds   threat-register/v2.0.0  tag 5d2ee40 -> 69c89b0  cut run 33486753913, release run 33487519188 (ticket 61)
insurer v1.0.0                  tag d45005c -> 632db22  cut run 33480939175, release run 33481030227
```

GitHub's own `verification.verified` is `false, reason=no_user` on all three: GitHub cannot
attribute a Sigstore certificate to a user account. That is expected for gitsign and is not a
signature failure; the identity-pinned verification in `release.yml` is the check that counts.

Scheduled `fetch` runs (`gh run list -R <r> --workflow fetch.yml --event schedule`): three per
repo, one each day since registration, so the cron is in GitHub's scheduler.

```
feeds   33488014777 2026-09-01T08:37Z  33605912295 2026-09-02T07:54Z  33731176177 2026-09-03T08:02Z   all failure
insurer 33496526156 2026-09-01T10:16Z  33615860064 2026-09-02T09:45Z  33741719807 2026-09-03T09:57Z   all failure
```

Why they are red, read from the run logs, and who owns each:

- feeds (all six `fetch (<feed>)` jobs): the fetch itself succeeds and even stages a real patch
  bump (`staged threat-register/v2/feed.json at 2.0.1, threat-register/bump.yaml declares
  patch`); the job then dies in its own cage step `the observation cage -- a clock appends
  observations, never a declaration` because `?? __pycache__/bump.cpython-312.pyc` and
  `?? fetch/__pycache__/lib.cpython-312.pyc` sit outside the lane. Ticket 85 item 1.
- insurer (`fetch` job succeeds; all three `requote (<adopter>)` jobs fail): `REFUSED: missing
  instrument: .adopters/<adopter>/composed/HEADER.yaml carries no exposure section -- there is
  no signed exposure to attach a layer to`. The adopter tag v1.1.0 the insurer pins has no
  exposure section. Ticket 77 item 2. This is the ADR-0020 refusal working as designed.

The gate check that grades this ticket, `verify/feed-contract/verify-feed-contract.sh`, flipped
the three adopter SKIPs ("waiting for tag threat-register/v1.0.0 on feeds") to PASS on citable
TRUTH run 21 (2026-09-02T10:11Z, hub 7b92990) and again on run 22 (2026-09-03T10:24Z, hub
14cc731), read from the hub's `truth.yml` run 33742398518 log:

```
verify/feed-contract/verify-feed-contract.sh                           PASS
TRUTH 2026-09-03T10:24Z run=22 hub=14cc731 units=[... feeds=69c89b0 ... insurer=632db22 ...] pass=57 fail=7 skip=18 excluded=2 total=84
```

Run locally from the hub worktree on 2026-09-03 (`bash verify/feed-contract/verify-feed-contract.sh`, exit 0), the lines that this ticket converted:

```
PASS: driftwood pins feeds/feed/threat-register@v2: tag threat-register/v2.0.0 on feeds
PASS: driftwood pins insurer/feed/quote-driftwood@v1: tag v1.0.0 on insurer
PASS: ludlow pins feeds/feed/threat-register@v1: tag threat-register/v1.0.0 on feeds
PASS: tuppence pins feeds/feed/threat-register@v1: tag threat-register/v1.0.0 on feeds
PASS: every published feed is one envelope, and every subscription names a tag that exists on the publisher's real remote (existence, not signature -- step 6 checks the signature)
```

`verify/schedules/verify-schedules.sh` now sees both clocks (locally, exit 1 with five reds
none of which is a registration fault; in CI still SKIP for the `gh auth` reason ticket 56 owns):

```
PASS: feeds/fetch.yml: daily clock at 17 3 * * * -- feeds publishes threat-register, cve, eol, fx, market-moves, news
FAIL: feeds/fetch.yml: last scheduled run 11h ago concluded 'failure' -- a clock whose run dies records no observation
PASS: insurer/fetch.yml: daily clock at 31 5 * * * -- insurer publishes quote-driftwood, quote-tuppence, quote-ludlow
FAIL: insurer/fetch.yml: last scheduled run 9h ago concluded 'failure' -- a clock whose run dies records no observation
```

Done, as the Question defines it: both repos show scheduled runs, each has at least one signed
tag, and the adopter subscriptions' could-not-looks converted on a citable run. The clocks being
red is not this ticket's done condition and is owned by 85 and 77, whose done conditions name
these exact runs.

### Decisions

1. **Close on registration and tags, not on green clocks** -- delegated (ADR-0025). Reason: the
   Question's done condition is "a scheduled run" and "one signed tag each" and the SKIP-to-PASS
   conversion; all three are observed on the real remotes and on TRUTH runs 21 and 22. The
   reds have different causes (a stray `.pyc` in a cage; a pinned tree lacking a section) that
   tickets 85 and 77 were charted for on 2026-09-02, and keeping this ticket open would record
   the same fact twice under two owners. The 2026-09-02 review R8 and M1 recommend the same.
2. **The other five feeds (cve, eol, fx, market-moves, news) get no first signed tag yet** --
   delegated (ADR-0025). Reason: no adopter pins them. Read on 2026-09-03 from the four party
   artefacts, every `inherits[]` entry on `feeds` names `threat-register` (driftwood v2,
   tuppence v1, ludlow v1; the insurer pins nothing on feeds). A tag nobody resolves converts
   no check and would be a release for its own sake. The trigger is the first party artefact
   that pins one of them; that ticket dispatches the cut, and the dispatch stays the owner's.
   Their `bump.yaml` files are `bump: none` and validate (feed-contract PASS lines for all
   twelve feed files), so nothing needs queueing before that day.
3. **The observation-lane push ruleset is not applied; the client-side cage carries the load**
   -- delegated (ADR-0025). Reason: GitHub allows a push ruleset, the only kind that carries
   `file_path_restriction`, on private or internal repositories only, and every estate repo is
   public. Recorded in each repo's `.github/rulesets/README.md` on 2026-09-01; `verify-schedules`
   says the same in its SKIP line for every unit. Ticket 70 owns the detective control and the
   ADR-0023 note; the revisit trigger is the repos going private.
4. **GitHub's `verified: false, reason: no_user` on the tag objects is not a defect** --
   delegated (ADR-0025). Reason: GitHub attributes signatures to accounts and a Sigstore
   certificate names an OIDC identity, not an account. The check that matters is the
   identity-pinned `gitsign verify-tag` in `release.yml`, which passed on every tag.

### Not done here, on purpose

- No estate unit file changed: `feeds` and `insurer` sit at 69c89b0 and 632db22 on
  `ecosystem/build-2026-09-03`, unchanged. Every push to those repos remains the owner's.
- No verify script or test changed: the ticket's seams are the existing `feed_contract.py
  selfcheck` and `schedules.py selfcheck`, both run and both `ok` on 2026-09-03; the grading
  check already exists. No new code, so no red-then-green cycle and no mypy run.
- `verify-schedules` still SKIPs in CI for the `gh auth` reason; ticket 56.
- The tuppence and ludlow workflow refs that still name the deleted `ecosystem/thin-slice`
  branch (comment of 2026-09-01 above) are ticket 62's.

## Waits on the owner

- A `cut-release.yml` dispatch on feeds for any of cve, eol, fx, market-moves or news, when an
  adopter first pins one (decision 2). Nothing waits on it today.
- Any further push to `policy-as-versioned-feeds` or `policy-as-versioned-insurer`. This round
  needs none.

Map line: 57 resolved 2026-09-03 -- feeds and insurer runnable: default branches `main`, six workflows active, signed tags feeds threat-register/v1.0.0 (and v2.0.0 via 61) and insurer v1.0.0 verified by identity-pinned gitsign, daily fetch crons firing since 2026-09-01, three adopter feed-contract SKIPs converted to PASS on TRUTH runs 21 and 22; clock reds owned by 85 (feeds `__pycache__` in cage) and 77 (insurer pin lacks exposure); other five feeds untagged until an adopter pins one (delegated).
