# 24 — Agent demonstrator: one signal source → review PR

**What to build:** The bounded demonstrator from the spec: wired to one signal source, it reads a policy's advisory metadata, detects a stale-rationale condition, and opens a review PR framing the business decision — never touching enforcement. P3 acceptance: "the agent surfaces a stale-rationale business decision as a PR."

**Blocked by:** 23 — Agent governance spec.

**Status:** done

- [x] Given a policy whose rationale is contradicted/staled by the signal, the agent opens a PR/issue framing the decision in business terms
- [x] The PR proposes editorial review; no enforcement file is modified by the agent
- [x] Noise reduction demonstrable: an irrelevant signal produces no PR

## Comments

Done 2026-07-15. `governance-agent/demonstrator.sh`, run for real (user's explicit go-ahead --
opening real issues under their identity is exactly the kind of action auto-mode correctly
paused on and asked about first).

Live run against the real GitHub Security Advisories API for `kyverno/kyverno`: 27 published
advisories fetched. 26 filtered as noise (23 outside the 60-day recency window, several also
below the `high` severity floor) -- zero issues opened for any of them, satisfying the
noise-reduction criterion with real data, not a fixture. The one survivor, `CVE-2026-54523`
(critical, published the day before the run -- a real, current `NamespacedGeneratingPolicy`
privilege-escalation bug in Kyverno's engine), was surfaced and opened as 5 issues, one per
policy (all 5 depend on the same engine, per SPEC.md's relevance rule), each using the ADR-0007
decision-framing template verbatim:
https://github.com/policy-as-versioned-flux/policy/issues/1-5.

No enforcement file touched: the script's only write anywhere is `gh issue create` (and
`gh label create` for the label) -- no `git`, no policy-repo checkout, no `gh pr`. Confirmed
`pavf-policy`'s working tree and history are untouched after the run.

Found and fixed a real bug during the live run: the first pass only opened 3 of 5 issues.
`gh issue list --search "$ghsa in:body"` searches loosely across the whole repo, and all 5
issues share the same GHSA text in their body -- GitHub's search index caught up mid-run and
started matching *other* policies' issues as if they were this policy's, silently skipping
`require-rds-multi-az` and `require-s3-bucket-encryption`. Fixed by matching on exact issue
title (unique per policy+CVE by construction) fetched once per advisory and compared
client-side, not via the search API. Re-ran; dedup correctly no-opped on the 3 existing issues
and created the missing 2.
