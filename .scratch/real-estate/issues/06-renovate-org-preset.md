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

**Status:** ready-for-agent

- [ ] Preset repo exists; fleet's config extends it and keeps its local customManager
- [ ] No onboarding PRs appear on un-configured repos
- [ ] The dependency dashboard issue appears on at least one configured repo after a live Renovate run
- [ ] Live-Renovate seam note recorded: the next signed policy tag should yield a real bump PR against fleet — closing faithful-floor issue 11's fixture-only item; observe and record when it happens
