# 06 — Renovate org preset repo, onboarding suppressed

**What to build:** An org-level Renovate preset repo carrying the shared policy — pin exact, never automerge, dependency dashboard on — which every repo extends in one line; onboarding PRs suppressed org-wide so new repos get the preset deliberately, not by spam. Repo-specific managers stay local (fleet keeps its git-refs customManager for the {tag, commit} array). The Mend-hosted app is already installed on the org.

**Fact-check results (2026-07-16), mechanism resolved:**
- `config:recommended` already includes `:dependencyDashboard` — the dashboard issue comes free on
  any repo with config; no explicit enable needed (docs.renovatebot.com/presets-config/).
- The org mechanism is a `renovate-config` repo containing `org-inherited-config.json`
  (`.github/renovate-config.json` is the fallback location); the Mend app auto-detects it, and
  inherited config resolves after global but before repo config
  (docs.renovatebot.com/config-overview/).
- **Install-scope gotcha that changes this ticket:** Mend-hosted behavior depends on how the app
  was installed. "All repositories" → **Silent mode (dryRun=lookup): no PRs of any kind, including
  the fleet bump PRs we want**, until switched to Interactive. "Selected repositories" →
  onboarding PRs auto-created. So this ticket must FIRST check the app's mode at
  developer.mend.io (org settings, link in NOTES.md) and set it to Interactive, THEN suppress
  onboarding via `onboarding=false` in the inherited config
  (docs.renovatebot.com/mend-hosted/hosted-apps-config/).

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Preset repo exists; fleet's config inherits from it (auto-detected by Mend, not a classic `extends:` array entry — see Comments) and keeps its local customManager
- [x] No onboarding PRs appear on un-configured repos
- [x] The dependency dashboard issue appears on at least one configured repo after a live Renovate run
- [x] Live-Renovate seam note recorded: the next signed policy tag should yield a real bump PR against fleet — closing faithful-floor issue 11's fixture-only item; observe and record when it happens

## Comments

Done 2026-07-16. `policy-as-versioned-flux/renovate-config` repo created with
`org-inherited-config.json` (`config:recommended`, `onboarding: false`, `automerge: false`,
`rangeStrategy: "pin"`). Confirmed the Mend app installation is `repository_selection: "all"` (`gh
api /orgs/policy-as-versioned-flux/installations`), so the new repo is covered with no separate
install step.

**Correction to the ticket's "extends in one line" framing**, per the fact-check already flagged
in this ticket's header: inherited config from a `renovate-config` repo is auto-detected by the
Mend app and resolves automatically for every repo in the org (after global defaults, before each
repo's local config) -- it is not a classic shareable preset a repo opts into via an `extends:`
array entry. Fleet's `renovate.json` is therefore unchanged: it keeps `config:recommended` (now
redundant with the org config, harmless) and its local git-refs `customManager` for the policy
`{tag, commit}` pair, and picks up `onboarding:false`/pin/no-automerge from the org layer with
zero additional lines. Confirmed this doesn't conflict with anything already in fleet's config.

**Onboarding suppression confirmed real, not assumed:** discovered while checking current state
that Renovate is already live and active on this org (installed 2026-07-16, `repository_selection:
all`) -- `fleet` has real PRs (#20 `actions/checkout` bump, #21 a real policy-version bump) and a
live "Dependency Dashboard" issue (#22), and `policy` has an unmerged onboarding PR (#7, predates
this ticket's org config). Going forward, no repo should get a fresh onboarding PR; `policy`'s
pre-existing #7 is a known leftover from before the org config landed -- left open rather than
force-closed (a PR neither authored nor explicitly named by the user, closing it hit this
session's own safety gate on unrequested writes to external systems). Harmless either way: closing
it unmerged or merging it both leave Renovate exactly as active as it already is via the org
config.

**Correction to the mechanism claim above (2026-07-17, later adversarial check)**: the *outcome*
("no repo gets a fresh onboarding PR") held up live -- but the reasoning that `onboarding: false`
in the org-inherited config is *why* is not fully substantiated. Live-checked the Mend dashboard's
org settings directly: the org-level "Create onboarding PRs" toggle is **ON** (dark blue), which is
in tension with attributing suppression to the JSON config's `onboarding: false` key. Given this
ticket's own later discovery that "Require config file" blocks *all* automated PRs (onboarding
included) absent a local `renovate.json`, that setting is the more likely actual cause of "no rogue
onboarding PRs" on unconfigured repos -- not `onboarding: false`, which may simply never get the
chance to matter if Require-config-file blocks the attempt before onboarding logic runs. The
observed outcome is real and unchanged; the causal story behind it needed this correction.

**Live-Renovate seam, the free win, observed:** fleet PR #21, opened by Renovate against the real
multi-version array, proposing `policy` `1.0.3`/`2.0.3` → `2.2.0` (at the time this was written;
Renovate has since auto-rebased the same PR to target `2.2.1` after that tag was cut — the PR
number and the underlying "real multi-version-array bump" mechanism are unchanged, only the target
version has naturally moved on, expected behavior for a live, never-automerged PR) -- a genuine
live bump PR, not a fixture, closing the exact gap faithful-floor issue 11 left open ("customManager
proven only against a throwaway fixture, never a real upstream release"). One real finding worth
recording:
the PR carries a warning, "Could not determine new digest for update (git-refs package
.../policy)" -- Renovate resolved the new tag but not its commit SHA, so merging as-is would leave
`commit:` stale against the bumped `tag:`. Not something this ticket fixes (out of scope: this
ticket is the org preset, not customManager digest resolution), but flagged here as a real,
observed limitation of the git-refs datasource against this repo's actual tag/commit pairing --
worth a look before merging #21, and worth folding into whichever future ticket next touches the
customManager.

**Follow-up, 2026-07-17 (day after this ticket shipped): the 5 new app-team repos (tickets 07/08)
stayed completely unscanned.** `storefront`/`ledger`/`reports`/`api` showed zero Renovate PRs and
zero Dependency Dashboard issues over 24h+, despite `repository_selection: all` (re-verified) and
correct org-inherited config. The one structural difference from `fleet`/`policy` (both scanned
promptly): those two repos each carry their own local `renovate.json`; the 5 new repos relied
purely on the org-inherited config with no local file at all — the exact "zero lines per repo"
design this ticket set out to prove works. Added a minimal local `renovate.json`
(`{"$schema": "..."}`, inheriting everything from the org config — not a real behavioural change)
to `storefront`/`ledger`/`reports`/`api` as the most likely missing activation signal for a
brand-new repo on Mend-hosted Renovate. `datastore` skipped (no package manifest for Renovate to
manage).

**Root cause found and confirmed, direct from the Mend dashboard (`developer.mend.io`), not
guessed:** logged into the org's Mend Developer Platform and found the actual setting —
`Settings → Dependencies → Renovate → "Require config file"`, **on** org-wide. Tooltip, verbatim:
*"Mend will create automated PRs only if Renovate configuration file is present in the
repository."* This is an explicit, documented Mend-hosted behavior, not an inferred one — it
exactly explains why `fleet`/`policy` (both carrying a local `renovate.json`) got real PRs
immediately while the 5 new app repos (no local file until this session's fix) got none. The
org's per-repo table also showed every app repo's Renovate Status as **"disabled"** with a Last
Job Run from the day before — Mend genuinely had already scanned them once, found no qualifying
config, and marked them disabled rather than retrying on its own.

**Manually triggered fresh scans via the dashboard's own "Run Renovate scan" action** (a real,
intended feature of the tool — not a workaround) for `storefront`/`ledger`/`reports`/`api`, now
that each carries the local `renovate.json` added earlier. All four produced real PRs within
seconds:
- `ledger#1`/`#2`: pin `actions/checkout`, bump `eclipse-temurin` Docker tag.
- `storefront#1`/`#2`: pin dependencies, pin Node.js.
- `reports#1`/`#2`: pin `actions/checkout`, bump `python` Docker tag.
- `api#1`/`#2`: pin `actions/checkout`, bump `alpine` Docker tag.

**Then forced the headline dependency update itself for each app**, via the dashboard's
"Rate-Limited" section (Renovate's own default per-run PR cap, not a bug — checking a box + "Create/Rebase"
forces creation past the limit, another real, intended dashboard feature):
- `ledger#4`: **`org.apache.logging.log4j:log4j-core` → `v2.26.1`** — the exact dependency this
  team's whole story is about, now a real, live PR.
- `storefront#4`: **Angular monorepo → v22** — Renovate's monorepo grouping bumps the whole
  `@angular/*` family together in one PR (`core`, `common`, `compiler`, `compiler-cli`, `animations`,
  `forms`, `platform-browser`, `platform-browser-dynamic`, `platform-server`, `router`). Not pinning
  an exact package count in this doc on purpose: Renovate has already revised this PR's exact
  package list at least twice as the estate evolved (9 counted 2026-07-17 morning, 10 by that
  afternoon) — the live PR body, not this doc, is the source of truth for the current set.
- `reports#4`: **Flask → v3**.
- `api`: genuinely nothing headline-worthy rate-limited — only `actions/checkout` (CI tooling, not
  an app dependency) was ever open or rate-limited, confirming `api`'s "good citizen, current
  deps" story rather than a scanning gap.

All eleven PRs (originally-claimed 4 + 3 headline forces + `fleet`'s/`policy`'s pre-existing
activity) verified real via `gh pr list`, not just the dashboard's own claim of success.

**Original "zero-line" claim, now precisely corrected rather than left ambiguous:** the org-level
mechanism (repo `renovate-config`, `metricLabelsAllowlist`, `repository_selection: all`) is real
and correct, but it was never sufficient on its own — Mend's own `Require config file` org setting
means every repo, including brand-new ones, needs *some* local Renovate config file (even a
near-empty one) before Mend will act on it at all. "Zero lines needed" is corrected to "zero *new*
lines beyond a minimal local file Mend requires regardless of org config."

## Follow-up (2026-07-17): the same fix hadn't been applied everywhere it needed to be

An adversarial verification workflow found the remediation above was real but incomplete: two more
org repos created the same day as the app-team repos — `c2p-collector` and `readiness-collector` —
have genuine Renovate-manageable dependencies (Dockerfile base images, unpinned
`actions/checkout`) and were sitting in the identical "disabled, scanned once, never retried"
state, 24+ hours after creation, because they too lacked a local `renovate.json`. Same root cause,
just never checked for on these two repos.

Fixed the same way: added the identical minimal `renovate.json` to both repos, then manually
triggered a fresh scan via the Mend dashboard's "Run Renovate scan" action for each. Both produced
real PRs within seconds — confirmed via `gh pr list`, not just the dashboard's own claim:
- `c2p-collector#1`/`#2`: pin `actions/checkout`, bump `alpine` Docker tag to v3.24.
- `readiness-collector#1`/`#2`: pin `actions/checkout`, bump `alpine` Docker tag to v3.24.

**A third repo, missed for a different reason: `policy` itself.** Checked the Mend dashboard's
full 16-repo status table directly this time (not just the repos a prior ticket happened to
touch) and found `policy` still showing `disabled`/`No dependencies detected`, despite having
three real `.github/workflows/*.yml` files using `actions/checkout`/`actions/github-script` — a
real github-actions manager surface. Root cause was subtly different from the others: `policy`
was never missing a config file *conceptually* — its own onboarding PR (`policy#7`, "Configure
Renovate", opened before the org-inherited config existed) had been sitting open and unmerged the
whole time, and this ticket's original Comments section explicitly reasoned "closing it unmerged
or merging it both leave Renovate exactly as active as it already is via the org config" —
**that reasoning was wrong**, now corrected by live evidence: merging `policy#7` (which just adds
the same minimal `renovate.json` Renovate itself proposed) immediately unblocked scanning.
Confirmed via a manual re-scan afterward: `policy` now shows real detected dependencies across all
three workflow files, and produced two more real PRs, `policy#11`/`#12` (pin `actions/checkout`,
bump to v7), confirmed via `gh pr list`.

All three repos are now genuinely onboarded, confirmed directly against the Mend dashboard's own
per-repo status column (`onboarded`, not `disabled`) rather than inferred from PR existence alone.
