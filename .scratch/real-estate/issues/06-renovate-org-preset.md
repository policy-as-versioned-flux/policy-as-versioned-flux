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

- [x] Preset repo exists; fleet's config extends it and keeps its local customManager
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

**Live-Renovate seam, the free win, observed:** fleet PR #21, opened by Renovate against the real
multi-version array, proposing `policy` `1.0.3`/`2.0.3` → `2.2.0` -- a genuine live bump PR, not a
fixture, closing the exact gap faithful-floor issue 11 left open ("customManager proven only
against a throwaway fixture, never a real upstream release"). One real finding worth recording:
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

**Correction to this ticket's original "zero-line" claim, stated honestly:** whether a bare
local file is genuinely required for Mend-hosted Renovate to activate a *brand-new* repo (versus
an already-established one) could not be confirmed within this session — no PR or Dependency
Dashboard issue appeared on any of the 4 repos even ~90 minutes after adding the local files, an
external SaaS scan-schedule dependency this project's own testing philosophy already names as
"observable, not controllable" (see the epic spec's Testing Decisions). The org-inherited
mechanism itself (repo `renovate-config`, `metricLabelsAllowlist`, `repository_selection: all`)
remains verified correct by direct inspection; only the *empirical* "zero lines needed even for a
brand-new repo" claim is walked back to "not confirmed live" rather than left standing unproven.
