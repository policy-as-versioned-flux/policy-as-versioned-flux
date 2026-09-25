# 87 — The forge enforces the review

Type: task (HITL)
Status: open
Blocked by: 88

## Question

Principles 4 and 5 say policy is bumped only by reviewed PR and a human merges. Nothing on GitHub enforces either. Zero rulesets, zero branch protection, zero tag protection on all nine repositories, verified live. Every merged PR in the estate has author equal to merger. Every identity pin accepts a tag signed from `release/<M>.<m>.x`, platform has such a branch, and nothing guards it. Anyone with push access can rewrite `cut-release.yml`, push it unreviewed, dispatch it, and produce a tag every consumer accepts. The 2022 org still has tag protection; the successor has none.

Under ticket 75 Q6:

1. If it binds: apply a ruleset on `main` and `release/*.x` in all nine repos requiring a pull request and one approving review from an identity other than the author, plus tag protection matching each repo's release pattern. Name the second identity. Add an assertion to the identity-regexp verify family that every branch the accepted pattern admits is protected, so the pin and the protection cannot drift apart.
2. If it does not bind for this build: record the single-operator state in NORTH-STAR §6, and stop presenting principle 5 as enforced.
3. Either way: `twin/ENACT_MODE` is a file the agent writes. Replace it with a declaration in a repo the agent cannot push to, with a price attached, or record why not.

Done = `gh api repos/<org>/<repo>/rulesets` is non-empty on nine repos and the verify family asserts it, or §6 carries the dated decision.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R9. Findings: security/SS-04, SS-05, scope/F8, engineering/EQ-08. Ticket 65 (the `--git-dir` hole) is the guard's own half. Ticket 74's definition of done cannot be written until Q6 is answered.

**2026-09-05.** Item 3 gained a narrower sibling, ticket 97, charted a day earlier without
noticing this item. 97 keeps the declaration where it is and pairs it with a record of the commit
that authorised it, so an unrecorded flip goes red. This item is the stronger answer and 97 says
so. Answer them together; if item 3 lands, 97 closes as covered.

**Live state as of 2026-09-04, for item 1.** The `pavc-other-hand` installation carries
`contents:write, metadata:read, pull_requests:write` on all nine organisations and no `workflows`
permission. That already bites: insurer pull request 3 could not be merged by the app because it
changes `.github/workflows/fetch.yml`, while five sibling merges carrying workflow changes were
admitted the same day. Whatever ruleset item 1 applies has to be reachable by the second identity,
or the identity stops being able to merge at all. Record: ticket 62, "Waits on the owner".

## Comments

**2026-09-02, ticket 75 resolved.** Q6 is (a), owner-reasoned: principle 5 binds for the demonstration. Item 1 applies. The second identity is the machine identity ticket 88 creates for the assistant, which reviews and merges during the development window while the owner authors and pushes (the owner's word: theatre). Item 3: `twin/ENACT_MODE` flips to `development` only after ticket 88 lands, with a dated docstring line; the declaration the agent cannot write is the ruleset itself, which requires the second identity's review. Blocked by 88 now, not 75.

**2026-09-03, ticket 88 resolved.** The second identity is the GitHub App `pavc-other-hand` (App ID 4819564), installed on all nine orgs. Item 1's ruleset requires one approving review from an identity other than the author; the app's review counts as that identity. Item 3: `twin/ENACT_MODE` reads `other-hand`, and the admitted merge shape is one that mints the app's token inline; the declaration the agent cannot write is the ruleset itself. Unblocked.

**2026-09-24, item 3 answered through ticket 97.** Item 3 allows "or record why not". This is the
reason. No declaration on GitHub is out of the assistant's reach while it holds three credentials:

- The owner's `gh` token. The assistant pushes with it.
- The owner's signing key, `~/.ssh/id_ed25519`. It signs every commit that the assistant makes,
  and no prompt stops it.
- The key of `pavc-other-hand`. The assistant approves and merges with it.

So a ruleset that requires one review from a second identity stops nothing that the assistant does
alone. The assistant can author under the owner's name and approve as the app. A declaration out of
its reach needs a credential that it does not hold, for example a signing key that needs a physical
touch. The owner did not ask for that. Ticket 97 Q1 (a), delegated on 2026-09-24, says that the
alarm catches accidents only. So ticket 97 takes the weaker answer: a record beside
`twin/ENACT_MODE` that a gate check compares with the mode.

**Correction, 2026-09-24.** The comments of 2026-09-02 and 2026-09-03 say that "the declaration
the agent cannot write is the ruleset itself". That is false, for the reason above.

**2026-09-24, the rulesets that exist.** At 17:51 +01:00 on 2026-09-24, the hub
`policy-as-versioned-flux/policy-as-versioned-flux` got three rulesets. None of them has a bypass
actor.

| Ruleset | Target | Rules |
|---|---|---|
| `main-keeps-its-history` | the default branch | `deletion`, `non_fast_forward` |
| `release-branches-are-reviewed` | `refs/heads/release/**` | `creation`, `deletion`, `non_fast_forward`, `pull_request` with one approving review |
| `release-tags-hold` | every tag | `update`, `deletion` |

The eight unit repositories have no rule on `main`, from a ruleset or from classic branch
protection. The hub has no classic branch protection either. So item 1 is not applied. `main` has
no pull-request rule in any of the nine repositories. On 2026-09-24 the assistant said that the
owner made the three rulesets, and the owner did not object. No tracked file in the hub named them
before this entry.

NORTH-STAR §6 has a "development-window theatre" bullet. It says that "ticket 87 protects `main`
and `release/*.x` with a required review from a different identity". On 2026-09-24 that is false.
The ticket 97 build adds a dated correction.

## Build, 2026-09-22

Built 2026-09-24 and 2026-09-25 under the owner's instruction of 2026-09-24: items 1 and 2 now,
item 3 out of scope (the comment of 2026-09-24 above answers it through ticket 97). Hub branch
`ticket-87-the-forge-enforces-the-review`. No unit repository's files changed; the rulesets are
settings, applied with `gh api`.

**Correction to the comment above, "the rulesets that exist".** The three hub rulesets were not
made by the owner. This build applied them at 2026-09-24T16:51Z (17:51 +01:00), with the owner's
token, under the owner's instruction of 2026-09-24 that allowed rulesets for this ticket only.
The eight unit repositories got theirs at 2026-09-25T11:04Z, below.

### What was measured first

Measured on 2026-09-24 with `gh api repos/<r>/rulesets`, `git log --first-parent origin/main`
in the hub and each `.estate-clone/<unit>`, `gh api repos/<r>/events` (PushEvent and CreateEvent
actors), `gh api repos/<r>/actions/workflows/cut-release.yml/runs`, and a grep of every
workflow for `git push`, `token:` and `secrets.`.

- Before this build all nine repositories had 0 rulesets and no protected branch.
- Every repository is public, on the organisation free plan, default branch `main`.
- Since 2026-09-05 the only commits on any `main` whose committer is not GitHub's merge identity
  are clock and release commits:
  - hub: 56 `truth surface`, pushed by truth.yml;
  - driftwood: 19 `drift sampler` and 19 `twin sweep`;
  - tuppence: 19 `drift sampler` and 14 `twin sweep`;
  - ludlow: 19 `drift sampler` and 14 `twin sweep`;
  - platform: 2 `policy-as-versioned release bot`, the evidence commit cut-release.yml pushes;
  - nist, ico, feeds, insurer: none.
- The owner's last direct push to a `main` was 2026-09-04 (platform). Everything since is a
  merge by `pavc-other-hand[bot]`.
- Every one of those pushes uses the checkout's `GITHUB_TOKEN`. The event feed shows the pusher
  as `github-actions[bot]`. No workflow in the estate uses an app token or any secret other than
  `GITHUB_TOKEN`.
- Tags are pushed only by cut-release.yml with `GITHUB_TOKEN`. The owner dispatches it. The
  latest platform tags v3.4.0 and v3.4.1 were cut on 2026-09-24.
- The publishers' `observations` branches and the `fetch/*`, `requote/*` and `renovate/*`
  branches take pushes too. None is `main` or `release/**`.
- One release branch exists: platform `release/2.0.x`. Its tip is contained in `main`, and
  cut-release ran on it once, on 2026-08-24.
- No workflow pushes with `--force`.
- The identity pins: 11 distinct anchored patterns name an estate repository. Eight cut-release
  pins admit `refs/heads/(main|release/[0-9]+\.[0-9]+\.x)`. Three propose-tier pins admit
  `main` only.
- The app merges without an approval on the units. The newest three merged PRs on nist, ico
  and feeds, and two of three on insurer, carry no review. The hub's newest three carry a
  `pavc-other-hand[bot]` APPROVED review.

### What GitHub refused

The ticket's shape had the GitHub Actions integration (app id 15368) as the one bypass actor, so
the clocks could keep pushing. GitHub refused it on the hub:

    POST repos/policy-as-versioned-flux/policy-as-versioned-flux/rulesets
    422 "Actor GitHub Actions integration must be part of the ruleset source or owner organization"

That refusal was measured at 2026-09-24T16:48Z, and nothing was applied by that call. Public
reports say the same for other organisation-owned repositories. So no ruleset here can let
`GITHUB_TOKEN` through, and a `pull_request` rule on a branch a clock pushes to would stop that
clock.

### What was applied

Four rulesets, declared in `.github/rulesets/` in the hub, none with a bypass actor:

- `release-branches-are-reviewed`, on `refs/heads/release/**`: `creation`, `deletion`,
  `non_fast_forward`, and `pull_request` with one approving review. All nine repositories.
- `release-tags-hold`, on every tag: `update` and `deletion`. All nine repositories.
- `main-is-reviewed`, on the default branch: `deletion`, `non_fast_forward`, and
  `pull_request` with one approving review. nist, ico, feeds and insurer, where nothing pushes
  `main`.
- `main-keeps-its-history`, on the default branch: `deletion` and `non_fast_forward`. hub,
  platform, driftwood, tuppence and ludlow, where a clock or cut-release pushes `main`.

Ruleset ids (from the POST responses):

| Repository | Ruleset | id |
|---|---|---|
| hub | main-keeps-its-history | 23950610 |
| hub | release-branches-are-reviewed | 23950611 |
| hub | release-tags-hold | 23950612 |
| platform | main-keeps-its-history | 23993294 |
| platform | release-branches-are-reviewed | 23993296 |
| platform | release-tags-hold | 23993299 |
| driftwood | main-keeps-its-history | 23993301 |
| driftwood | release-branches-are-reviewed | 23993303 |
| driftwood | release-tags-hold | 23993304 |
| tuppence | main-keeps-its-history | 23993306 |
| tuppence | release-branches-are-reviewed | 23993307 |
| tuppence | release-tags-hold | 23993309 |
| ludlow | main-keeps-its-history | 23993310 |
| ludlow | release-branches-are-reviewed | 23993311 |
| ludlow | release-tags-hold | 23993313 |
| nist | main-is-reviewed | 23993314 |
| nist | release-branches-are-reviewed | 23993315 |
| nist | release-tags-hold | 23993317 |
| ico | main-is-reviewed | 23993320 |
| ico | release-branches-are-reviewed | 23993321 |
| ico | release-tags-hold | 23993322 |
| feeds | main-is-reviewed | 23993323 |
| feeds | release-branches-are-reviewed | 23993324 |
| feeds | release-tags-hold | 23993327 |
| insurer | main-is-reviewed | 23993329 |
| insurer | release-branches-are-reviewed | 23993330 |
| insurer | release-tags-hold | 23993331 |

The hub went first. The eight followed only after the hub's clock recorded under its rulesets:
scheduled truth run 335 wrote `truth: record run 335` (8a07087, committer `truth surface`) to
`main` at 2026-09-25T11:01Z, and its record and cage steps read `success`. The merge path held
too: `pavc-other-hand[bot]` approved and merged hub PR 130 (9364767) at 2026-09-24T18:17Z and
f1c26a3 at 19:26Z, both after the hub rulesets. Read with `gh run view 36124673628`,
`git log origin/main`, `gh api repos/<r>/pulls/130` and its `/reviews`.

The unit clocks that push `main` all pushed under their rulesets on 2026-09-25, read with
`gh api repos/<r>/actions/workflows/<w>/runs`, `gh api repos/<r>/commits?sha=main` and the event
feed (pusher `github-actions[bot]`):

| Clock | Run | Commit on `main` |
|---|---|---|
| driftwood drift-sample | 36131807139, success | e809caf, 11:54Z |
| driftwood twin-sweep | 36136509267, success | 155db9e, 12:43Z |
| tuppence twin-sweep | 36137002585 | 1e4254d, 12:48Z |
| ludlow twin-sweep | 36137280568 | 3c7197a, 12:50Z |
| tuppence drift-sample | 36144143886, success | 5deffe6, 13:57Z |
| ludlow drift-sample | 36148474351, success | b8e14f7, 14:36Z |

The tuppence and ludlow twin-sweep runs read `failure`. That is their own step "Preserve the
recorded could-not-look or review-required result" exiting 3 after the push, the same as their
2026-09-24 runs before any unit ruleset (run 36000990663). No push was refused. The publisher
fetch clocks push only `observations`, which no ruleset covers; their 2026-09-25 runs ran before
11:04Z, so they first run under the rulesets on 2026-09-26. No ruleset was removed.

### The assertion item 1 names

`verify/forge-review/verify-forge-review.sh`, a hub check, graded in the gate. It reads every
anchored identity pattern the estate serves (11 today, read out of the workflows, gitops pins and
scripts, with tests, fixtures, captures and records left out). It works out every branch each
pattern admits, from the live branches and a fixed probe sample. It asks GitHub's
`rules/branches/<name>` for the effective rules on each, so the forge resolves includes,
excludes and `~DEFAULT_BRANCH` itself. An admitted branch must carry `pull_request` with one
approving review, `non_fast_forward` and `deletion`, and `creation` off the default branch. It
also grades a floor on all nine repositories and a tag ruleset over every tag. truth.yml's
`clocks` job collects the facts (`forge_review.py collect`, artifact `forge-facts`), and the
gate grades them holding no credential.

Red first, twice:

- `tests/test_forge_review.py` before the module existed: 17 errors and 1 failure. After: 20
  passed.
- Branch truth run 333 (2026-09-24T17:31Z), before the eight were applied: `FAIL: 64 forge
  protection(s) observed missing`, gate `fail` 7 to 8.
- A local collect and check at 2026-09-25T11:05Z, after all nine: 4 FAIL, 5 PASS. The four are
  `main` on platform, driftwood, tuppence and ludlow: each is admitted by that repository's
  cut-release pin (and propose-tier pin on the adopters) and lacks `pull_request`.

Those four reds are real. A signed tag cut from an unreviewed push to one of those four `main`
branches is still accepted by every consumer. The check stays red until they close.

Ceilings, stated: the probe sample is finite; a pattern split across several string literals in
code is not read (each one found today duplicates a single-literal pattern); bypass lists are
only visible to an admin token, so in CI the PASS line says they were not graded.

### Decisions (delegated, ADR-0025)

1. **No bypass actor on any ruleset.** GitHub refused the GitHub Actions integration (HTTP 422
   above). The only other ways to let the clocks through are a deploy key or an app used by the
   lanes. Both are new credentials. Those are the owner's.
2. **`main` gets `pull_request` only where nothing pushes it.** That is nist, ico, feeds and
   insurer, measured above. On the hub, platform, driftwood, tuppence and ludlow `main` gets
   `deletion` and `non_fast_forward`, which every measured clock push satisfies. The instruction
   was to remove any ruleset that blocks a clock, so a rule that would block one was not applied.
3. **Release branches get `creation`.** The pins admit any `release/<M>.<m>.x`. Without
   `creation`, anyone with push access could create one from an unreviewed commit and dispatch
   cut-release on it. The cost: cutting a maintenance branch means lifting that ruleset for a
   moment. That is rare. The README says how.
4. **Tags get `update` and `deletion`, over every tag, not `creation`.** cut-release creates
   tags with `GITHUB_TOKEN`, which cannot bypass. A hand-pushed tag carries no cut-release
   signature, so no pin accepts it. `~ALL` covers every release pattern (`v*`, `policy/v*`,
   `<feed>/v*`) with nothing to keep in step.
5. **The assertion is one hub check, not nine unit scripts.** It reads the pins where they are
   served and asks the forge, so one change in a pin or a ruleset reddens it. It runs in the
   gate on the scheduled clock, which is where the other live facts already come from.
6. **A repository the collector cannot read is a could-not-look, never hidden by the others'
   passes**, and two review rules on one branch count as the strictest (found in review).

### What the build found on the way

- The app merges on the units without an approval. Under `main-is-reviewed` that no longer
  works on nist, ico, feeds and insurer: the merging shell must approve first, as it already
  does on the hub. Renovate PRs nist #1 and ico #1 read `REVIEW_REQUIRED` on 2026-09-25.
- The app still has no `workflows` permission (the note of 2026-09-05). A ruleset does not
  change that.

### What remains, and who owns it

- **Waits on the owner:** one push identity the rulesets can let through, for example a GitHub
  App installed on the nine organisations and used only by truth.yml, drift-sample, twin-sweep
  and cut-release. With it, the four red `main` branches and the hub's `main` get
  `main-is-reviewed` with that app as the one bypass actor, and tags get `creation`. Creating an
  identity and its key is the owner's (ADR-0025).
- **Waits on the integrator:** merging this PR adds the forge check to the gate as a FAIL, so
  `fail` rises by one on the run that records the merge. A `talk/verify-falls.txt` line naming
  that run is needed. The merge shell must approve before merging on nist, ico, feeds and
  insurer.
- Done is not met. `gh api repos/<org>/<repo>/rulesets` is non-empty on nine repositories and
  the verify family asserts it, but the assertion is red on four, and §6 cannot carry "enforced"
  until they close.


### Review round, 2026-09-25

The review blocked on one finding and raised four minor ones. All five are answered here.

1. **Blocking: "all nine" was asserted, never derived.** A facts file naming two repositories
   graded PASS, and so did a repository whose checkout the gate never read. Fix: `forge_review.py`
   now holds the nine as a fixed map, `ESTATE_REMOTES`, of name to remote. `collect` asks the forge about
   exactly those nine. `grade` walks the nine, not the facts file. A repository the facts file
   does not name, or names with a different remote, is a SKIP by name. A unit whose clone is
   missing, has another origin, or cannot be read by `git grep` is left out of the pin map, and
   `grade` prints a SKIP by name for it. The wrapper's PASS line now counts the PASS lines instead
   of saying "nine". Red first: 7 new tests, 5 failed on the old code, then 27 passed. A test also
   holds `ESTATE` to the remotes of the clones under `.estate-clone`. The reviewer's two plants,
   rerun on a facts file collected live today: two repositories only now exits 3 with a SKIP
   naming each missing one; platform's checkout dropped now prints a SKIP naming platform. The
   live check still reads 5 PASS and 4 FAIL, the same four `main` branches.
2. **Minor: three SKIP texts were undeclared.** The manifest row now declares the local
   no-gh path, the unasked branch, and the facts file from another run. `truth_manifest.judge`
   reads all three as declared. Two new texts stay undeclared on purpose: a facts file missing one
   of the nine, and a gate checkout missing one. Both jobs clone all nine under `set -e`, so
   either is a broken pipeline and should grade FAIL. The row's note says so.
3. **Minor: NORTH-STAR §6 still said ticket 87 protects `main`.** This PR adds a dated
   correction to the bullet. It names the four repositories where `main` carries a review, the
   five where it does not, and the four the check reads red. Measured with `gh api
   repos/<r>/rules/branches/main` on all nine on 2026-09-25. The comment above says the ticket 97
   build would add this correction. It did not, so this build added it.
4. **Minor: the README missed platform's backfill push.** Platform's cut-release has a
   `backfill_evidence_only` mode that pushes an evidence commit to the branch it runs on. On a
   `release/**` branch the pull request rule now refuses that push. The README says so and says
   how to do a backfill there. A normal cut-release on a release branch pushes tags only.
5. **Minor: this section's heading reads 2026-09-22.** The workflow that runs this build sets that
   heading, so it stays. The build happened on 2026-09-24 and 2026-09-25, as the first line says.

This round ran the repo's /code-review skill on 4c6ec7d, both axes in turn, because this session
has no subagent tool. Spec found nothing. Standards found two judgement calls, both fixed: the
word `estate` meant a directory in one function and a name-to-remote map in another (now
`ESTATE_REMOTES` and `remotes`), and the hub's checkout was set in two places (now one).

Done, re-read: rulesets are non-empty on nine repositories and the check asserts them over a
fixed nine. §6 now carries the dated state. The check stays red on four `main` branches until
the owner creates a push identity a ruleset can let through.

**2026-09-25, correction from eco-system ticket 30.** This ticket says `pavc-other-hand` has no
`workflows` permission (lines 28-30 and 269-270). Read live on 2026-09-25 with
`gh api orgs/policy-as-versioned-<org>/installations`: the installation grants `workflows: write`
on eight of the nine orgs (driftwood, tuppence, ludlow, flux, platform, feeds, ico, insurer). Only
the nist installation lacks it. Ticket 30 also decided (ADR-0031) that the push identity this
ticket waits on serves writer jobs only: the twin code runs in a read-only job and never holds it.
