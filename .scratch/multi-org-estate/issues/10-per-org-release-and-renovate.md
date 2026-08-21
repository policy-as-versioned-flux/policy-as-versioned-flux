# 10 — Signed releases per org and cross-org Renovate bumping

Type: task
Status: partial (2026-08-21) — signed releases, per-org release workflows, Renovate config, and the
  cross-org shift-left gate (now closing with a signed cosign attestation, not just a status badge)
  are all proven live; the org-level "Actions can create PRs" toggle is still off on the three
  institutions, and that remains the real open gap (see Comments)
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

---

**2026-08-21 — correction: the `enact_guard.py` requirement above was a misunderstanding, and the real
fix is a signed attestation, not a commit mechanism.**

(a) The "Renovate commits must be git push, not the Contents/git-data API, to satisfy
`enact_guard.py`" requirement stated above is wrong, and it was wrong from the start. `enact_guard.py`
is a Claude Code `PreToolUse` **session hook**, registered in this repo's own `.claude/settings.json`.
It screens tool calls made inside a Claude Code agent session — this repo's `twin/` agent, in
particular. Renovate's `renovate-run.yml` runs entirely inside GitHub Actions' own infrastructure, on
GitHub's runners, outside any Claude Code session. `enact_guard.py` has no reach into that surface at
all, and never did. It could not have screened Renovate's bump commits regardless of whether Renovate
built them with `git push` or the Contents API — there was never a hook in the loop to satisfy either
way. The `platformCommit` chase in the section above was accordingly chasing a requirement that did
not hold. It is not being re-attempted.

(b) The real fix, shipped this session: a signed attestation after the shift-left gate, not a
commit-construction rule. `.github/workflows/shift-left.yml` on all three institutions
(`driftwood`, `tuppence`, `ludlow`) now adds steps, after `platform/shift-left/ci-check.py` passes,
that install pinned `cosign` (binary + published sha256, no marketplace action — the same convention
`cut-release.yml` already uses for `gitsign`), build a small JSON attestation (PR number, head sha,
gate name, result, run id/url), sign it keyless via the run's own GitHub Actions OIDC identity
(Fulcio certificate, logged to the public Rekor transparency log), and post the attestation plus the
signed Rekor bundle as a PR comment via `gh pr comment`. This is the same keyless-signing pattern
`cut-release.yml` already proves out for release tags, applied to the shift-left gate. Trust in an
automated check now comes from a verifiable signed record a reviewer can independently check, not
from which mechanism produced the commit, and not from a green status badge alone. Verified live: a
real test PR against `driftwood` (#4) ran the full chain end to end — cosign installed against its
checksum, the attestation built, signed keylessly (a genuine Fulcio certificate bound to that run's
OIDC identity, a real Rekor `tlogEntries` inclusion proof), and posted as an actual PR comment. A
second test PR against `tuppence` (#3) confirmed the converse: because `tuppence` (and `ludlow`) have
no `deploy/pod.yaml` fixture yet, `ci-check.py` fails there, and every step after it — including the
new attestation steps — is correctly skipped rather than posting a false "pass". Both test PRs are
closed, unmerged, and their branches deleted; they existed only to trigger the workflow live.

(c) The Renovate `platformCommit` mystery (Renovate's bump commits still land via the Contents API,
committer `github-actions[bot]`/`web-flow`, even with `"platformCommit": "enabled"` set) is
unchanged and still unexplained. It is now a non-blocking curiosity rather than a governance gap:
trust in a bump PR no longer depends on how its commit was constructed, because the shift-left gate
that runs on that PR now produces its own independently verifiable signed attestation regardless. A
focused follow-up on the `platformCommit` root cause remains worth doing for its own sake (the leads
listed above still apply), but nothing in this project's governance story is blocked on it.

This does not change the Status line's "partial" framing. The real remaining gap is unchanged and is
still the org-level "Actions can create PRs" toggle being off on the three institutions — an owner
action item, named above, not touched by this correction.
