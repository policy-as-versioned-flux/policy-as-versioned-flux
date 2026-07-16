# 06 — Renovate org preset repo, onboarding suppressed

**What to build:** An org-level Renovate preset repo carrying the shared policy — pin exact, never automerge, dependency dashboard on — which every repo extends in one line; onboarding PRs suppressed org-wide so new repos get the preset deliberately, not by spam. Repo-specific managers stay local (fleet keeps its git-refs customManager for the {tag, commit} array). The Mend-hosted app is already installed on the org.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Preset repo exists; fleet's config extends it and keeps its local customManager
- [ ] No onboarding PRs appear on un-configured repos
- [ ] The dependency dashboard issue appears on at least one configured repo after a live Renovate run
- [ ] Live-Renovate seam note recorded: the next signed policy tag should yield a real bump PR against fleet — closing faithful-floor issue 11's fixture-only item; observe and record when it happens
