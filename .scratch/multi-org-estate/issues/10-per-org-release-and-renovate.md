# 10 — Signed releases per org and cross-org Renovate bumping

Type: task
Status: partial (2026-08-21) — signed releases, per-org release workflows, Renovate config, and the
  cross-org shift-left gate are all proven live; Renovate's own bump commits still bypass
  enact_guard.py, and that gap is not fixed (see Comments)
Blocked by: 08, 09, 17

## Question

Make the dependency direction real on the wire: `nist`/`ico` → `platform` → `{driftwood, tuppence,
ludlow}`, every hop a signed, versioned, Renovate-bumpable dependency.

Includes: a release workflow per org producing signed tags (gitsign keyless → Rekor, consistent with
the estate's existing provenance story); Renovate configured to open cross-org bump PRs; and the
version cross-check gate (`estate/platform/shift-left/ci-check.py`) working when the target repo and
the policy repo are separate checkouts in separate orgs.

Relevant known fact: the org-level "Actions can create PRs" setting is **on** and overrides repo and
workflow permissions — it needs `admin:org` to read, so verify it per org rather than assuming.

Prove it end to end: cut a `platform` release, watch Renovate open a bump PR against one institution,
and watch the gate run on that PR.

## Comments

Partial, 2026-08-21. Documentation-only close: no further code or config changes were attempted
against the external repos or Renovate in this pass, per instruction. What follows is a status
write-up of what an earlier pass already proved and what it left genuinely open.

**PROVEN, independently verified this pass:**

- Gitsign-signed release tags exist and are real on all six `policy-as-versioned-*` repos. Each tag's
  signature is a genuine Sigstore/Fulcio certificate bound to `cut-release.yml`'s OIDC workflow
  identity, not a self-signed or GitHub-web-flow substitute — checked directly, not assumed.
- `cut-release.yml` and `release.yml` exist on all six repos.
- `renovate.json` and `renovate-run.yml` exist on the three institutions (`driftwood`, `tuppence`,
  `ludlow`).
- The shift-left version cross-check gate (the `estate/platform/shift-left/ci-check.py` equivalent)
  ran successfully on a real PR: `driftwood` PR #2, opened by hand, run `32461086104`,
  `conclusion: success`. This proves the gate mechanism itself works when the target repo and the
  policy repo are separate checkouts in separate orgs — the specific cross-org claim this ticket asks
  for.

**NOT PROVEN / genuine open gap: Renovate's bump commits don't go through `git push`.**

On `driftwood`, `tuppence`, and `ludlow`, Renovate's version-bump commits are still constructed via
GitHub's Contents/git-data API — committer `GitHub <noreply@github.com>`, login `web-flow`, a
GitHub-owned verified signature — rather than a real `git push`. This holds even after explicitly
setting `"platformCommit": "enabled"` in each repo's `renovate.json` and re-triggering. Confirmed live
via `gh api repos/<org>/<repo>/commits/<sha>` against the current branch tips on all three repos, not
assumed from Renovate's own logs.

The practical consequence: Renovate-driven bumps on these three repos currently bypass this project's
`twin/enact_guard.py` governance guard, which only screens `git push` writes. A commit made through the
Contents API never crosses that guard. This is a real, unfixed gap in the governance story this
project exists to prove out, not a cosmetic one.

Root cause is unknown and is named here as an open question for a focused follow-up, rather than
guessed at blind. Leads worth checking first, in no particular order:

- Renovate's internal `refs/renovate/branches/*` cache surviving a ref deletion, causing a
  branch-update code path that ignores `platformCommit`.
- An interaction with `enabledManagers: ["custom.regex"]`.
- A `renovate@44.37.1`-specific behaviour (the pinned version in `renovate-run.yml`).

**Separate, unrelated blocker — an owner action item, not a code gap.** The org-level "Allow GitHub
Actions to create and approve pull requests" toggle is off for `policy-as-versioned-driftwood`,
`policy-as-versioned-tuppence`, and `policy-as-versioned-ludlow` — confirmed via the 403 GitHub Actions
gets when it tries to create a PR in each org. This needs the owner to flip it by hand in each org's
settings. No attempt was made to work around it with a different identity; it is named here as the
owner's action item, per instruction.
