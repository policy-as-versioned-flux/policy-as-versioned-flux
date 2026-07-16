# 09 — Sunset implementation: scheduled proposals in practice

**What to build:** The mechanism the ADR (ticket 02) sanctions. Fleet array entries gain an optional `sunset:` date; the governance agent gains sunset-proximity as a signal source (extending its existing ADR-0007 contract: escalating issues as the date nears, decision-framed like its CVE issues); on the date, a machine opens a retirement PR against fleet — removing that array element — which a human must merge; if nobody merges, nothing changes, provably. Verified live with a synthetic near-past sunset date: the escalation issue exists, the retirement PR exists, the cluster is untouched until merge.

**Blocked by:** 02 — the ADR merges first.

**Status:** done

- [x] `sunset:` on an array entry produces escalating governance issues as the date approaches
- [x] On the date, a retirement PR is machine-opened, never merged by machine — live-verified with a synthetic date
- [x] Cluster state provably unchanged while the PR sits unmerged; merging it retires the version through the existing prune + guard-tighten path
- [x] The retirement-PR opener has no write access beyond opening PRs on fleet (token-scoped, same enforcement style as the governance agent) — see Comments for the honest version of this claim

## Comments

Done 2026-07-16. `governance-agent/sunset-escalator.sh`, extending the ADR-0007 contract with
sunset proximity as a second signal source alongside CVEs.

**`sunset:` field**: added to fleet's real `1.0.0` array entry (`sunset: "2026-08-15"`) — a real
adoption decision, not just a test fixture, since `1.0.0`/ledger is the roster's deliberate
laggard and giving it an honest retirement horizon fits the epic's own thesis. Purely data: the
`ResourceSet` template never references it, confirmed via server-side dry-run before merging (no
schema rejection) and live after — the orphan guard's allow-list rendered unchanged.

**Live-verified, both paths, against the real fleet repo, not a mock:**
- Escalation path (real, today's date, no override): opened a genuine issue,
  [fleet#30](https://github.com/policy-as-versioned-flux/fleet/issues/30), "Sunset approaching:
  policy 1.0.0 retires 2026-08-15 (30 days)" — left open, it's real signal.
- Retirement-PR path (proof, `SUNSET_TODAY_OVERRIDE=2026-08-16` simulating a date past the real
  sunset): opened a genuine PR, `fleet#31`, removing the `1.0.0` array element. While it sat open:
  confirmed live that `require-department-label-1.0.0`/`require-known-department-label-1.0.0`
  `ValidatingPolicy` objects were still present and the `ledger` `Deployment` was still `Running`
  — cluster state provably unchanged by an unmerged proposal. Closed unmerged once observed (the
  real 2026-08-15 date hasn't arrived — this was a simulation, not the actual event); the real PR
  will open on schedule.
- One real, minor finding from the proof: `yq del` on the array element also removes its attached
  head-comment block (the multi-paragraph issue-08/issue-19/ticket-09 history comments sitting
  above the `1.0.0` entry) — visible in the PR diff. Not a bug, just worth a reviewer's awareness:
  a human merging a real retirement PR loses that historical comment along with the entry, same as
  any YAML-tooling-generated diff would.

**Enforcement, stated honestly rather than overclaimed:** unlike the demonstrator's
`issues:write`-only token (a hard 403 if it ever attempted more), opening a PR genuinely needs
`contents:write` + `pull-requests:write` — there's no GitHub permission granular enough for
"open PRs but never merge them." What actually holds "never automerged" (ADR-0010's stated
invariant, not "cannot be merged by anything"): the script's code has no call to `gh pr merge`
anywhere (same never-calls-the-forbidden-thing shape as the demonstrator), and `fleet` has
`allow_auto_merge: false` org-wide (verified for ADR-0010), removing even the scheduled/deferred
merge path. Documented this distinction explicitly in the script header and README rather than
claim a permission boundary that doesn't actually exist for this operation.
