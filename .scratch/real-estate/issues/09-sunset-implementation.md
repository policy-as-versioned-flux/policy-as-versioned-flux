# 09 — Sunset implementation: scheduled proposals in practice

**What to build:** The mechanism the ADR (ticket 02) sanctions. Fleet array entries gain an optional `sunset:` date; the governance agent gains sunset-proximity as a signal source (extending its existing ADR-0007 contract: escalating issues as the date nears, decision-framed like its CVE issues); on the date, a machine opens a retirement PR against fleet — removing that array element — which a human must merge; if nobody merges, nothing changes, provably. Verified live with a synthetic near-past sunset date: the escalation issue exists, the retirement PR exists, the cluster is untouched until merge.

**Blocked by:** 02 — the ADR merges first.

**Status:** done

- [x] `sunset:` on an array entry produces escalating governance issues as the date approaches
- [x] On the date, a retirement PR is machine-opened, never merged by machine — live-verified with a synthetic date
- [x] Cluster state provably unchanged while the PR sits unmerged; merging it retires the version through the existing prune + guard-tighten path — **now proven with a real merge, not just simulated** (see 2026-07-17 follow-up)
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

## Follow-up (2026-07-17): "merging retires the version" was never actually tested — now it is

An adversarial audit found a real, previously-unflagged gap: the "merging retires the version
through the existing prune path" checkbox above was **only ever simulated**. `fleet#31` was
deliberately closed unmerged (the real 2026-08-15 date hadn't arrived), and no PR removing an
array element had ever actually been merged in this repo's history. Worse, the audit found the
*reason* this mattered: `clusters/cluster1/policy-versions.yaml` and `apps.yaml` were one-shot
`kubectl apply`'d by `up.sh` only — never wired into a continuously-reconciled Flux Kustomization.
So even a real merge wouldn't have retired anything on the live cluster without an undocumented
manual re-apply step, directly contradicting the checkbox's "through the existing prune... path"
framing. The audit also caught this gap's live consequence: the cluster's `ResourceSet` had
drifted out of band (hand-edited outside git), causing a real admission-control failure for two
running apps — see ticket 07's follow-up.

**Both fixed for real, not patched around:**
1. Added a `cluster-state` Flux Kustomization (fleet, `bootstrap.yaml`) that continuously
   reconciles `clusters/cluster1/policy-versions.yaml` + `apps.yaml` from git, the same
   git-drives-cluster guarantee every other resource in this cluster already has. `up.sh` updated
   to wait on it instead of `kubectl apply`-ing these files directly.
2. **Re-ran the retirement proof for real**, with two actually-merged PRs, not a closed-unmerged
   simulation:
   - `fleet#56`: added a throwaway 4th version (`v2.1.1`, a real, already-tagged, signed, unused
     release — not a fixture) to the array. **Merged.** Within one Flux reconcile interval, with
     zero manual `kubectl` commands: a new `GitRepository/policy-2.1.1` appeared, its three
     `Kustomization`s went Ready, and `orphan-guard`'s CEL allow-list picked up `'2.1.1'` —
     confirmed live via `kubectl get gitrepository`/`kustomization`/`validatingpolicy`.
   - `fleet#57`: removed that same array element. **Merged.** Within one reconcile interval, again
     zero manual steps: `GitRepository/policy-2.1.1` and its three `Kustomization`s were gone
     (Flux's own prune, not a `kubectl delete`), and `orphan-guard`'s allow-list was back to
     exactly `['1.0.0', '2.0.0', '2.2.0']` — the pre-test state, byte-for-byte.

"Merging retires the version through the existing prune + guard-tighten path" is now a proven
fact about this cluster, not a simulated one. The real `1.0.0` retirement (via `fleet#30`'s live
escalation issue, still open, real 2026-08-15 date) will go through the identical, now-verified
mechanism when that date arrives and a human merges the machine-opened PR.
