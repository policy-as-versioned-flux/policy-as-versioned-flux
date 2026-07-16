# 09 — Sunset implementation: scheduled proposals in practice

**What to build:** The mechanism the ADR (ticket 02) sanctions. Fleet array entries gain an optional `sunset:` date; the governance agent gains sunset-proximity as a signal source (extending its existing ADR-0007 contract: escalating issues as the date nears, decision-framed like its CVE issues); on the date, a machine opens a retirement PR against fleet — removing that array element — which a human must merge; if nobody merges, nothing changes, provably. Verified live with a synthetic near-past sunset date: the escalation issue exists, the retirement PR exists, the cluster is untouched until merge.

**Blocked by:** 02 — the ADR merges first.

**Status:** ready-for-agent

- [ ] `sunset:` on an array entry produces escalating governance issues as the date approaches
- [ ] On the date, a retirement PR is machine-opened, never merged by machine — live-verified with a synthetic date
- [ ] Cluster state provably unchanged while the PR sits unmerged; merging it retires the version through the existing prune + guard-tighten path
- [ ] The retirement-PR opener has no write access beyond opening PRs on fleet (token-scoped, same enforcement style as the governance agent)
