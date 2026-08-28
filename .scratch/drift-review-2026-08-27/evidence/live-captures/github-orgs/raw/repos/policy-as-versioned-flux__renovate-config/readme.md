# renovate-config

Org-level Renovate preset for `policy-as-versioned-flux`. Ticket 06 of the real-estate epic
(`policy-as-versioned-flux` hub repo, `.scratch/real-estate/issues/06-renovate-org-preset.md`).

`org-inherited-config.json` is the Mend-hosted app's org-inherited config (auto-detected from this
repo -- see [docs.renovatebot.com/config-overview](https://docs.renovatebot.com/config-overview/)).
It resolves after Renovate's own global defaults but before any repo's local `renovate.json`, so
every repo in the org gets this policy for free with zero per-repo setup:

- `config:recommended` -- includes `:dependencyDashboard` (the dashboard issue), sane defaults for
  everything else.
- `onboarding: false` -- no onboarding PR spam on repos that haven't opted in with their own
  `renovate.json`. A repo that wants Renovate adds one; a repo that doesn't stays silent.
- `automerge: false` -- every bump is a reviewed PR, no exceptions (ADR-0002 in the hub).
- `rangeStrategy: "pin"` -- exact versions everywhere, never a live range.

Repo-specific managers (e.g. fleet's `git-refs` customManager for the policy repo's
`{tag, commit}` pin pair) stay local to that repo's own `renovate.json` -- this preset only
carries what's genuinely shared across every repo in the org.
