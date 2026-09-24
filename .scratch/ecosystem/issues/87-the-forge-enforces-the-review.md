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

Built 2026-09-24 under the owner's instruction of that day: items 1 and 2 now, item 3 waits on
ticket 97. Hub branch `ticket-87-the-forge-enforces-the-review`. No unit repository changed.

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
