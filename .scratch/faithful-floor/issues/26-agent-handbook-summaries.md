# 26 — Agent plain-language summaries in the handbook

**What to build:** The last-mile attempt's human half: agent-authored plain-language summaries of each policy and its "why", woven into the generated handbook for the non-technical reader (the talk's "Cleaner"). Framed honestly per CONTEXT: an attempt at an acknowledged open problem, not a claimed solution.

**Blocked by:** 23 — Agent governance spec, 25 — Handbook generator.

**Status:** done

- [x] Each policy in the handbook carries a plain-language summary of what it requires and why, derived from its advisory metadata
- [x] Summaries regenerate with the handbook; stale summaries cannot ship
- [x] The docs state the residual last-mile problem explicitly — no over-claim

## Comments

Done 2026-07-15. `policy` repo, `handbook/generate.sh <tag> --with-summaries`: for each policy, a
real `claude -p` headless call is given that policy's exact `rationale.md` content and asked for
a 2-3 sentence non-technical summary — genuinely agent-authored per run, not hand-written text
frozen into the script. Ran live against `v1.0.1`'s two policies; both summaries read naturally
and correctly reflect Audit-vs-Deny distinctions from the source rationale without using any
policy jargon.

"Stale summaries cannot ship" made concrete, not just claimed: each summary is cached in
`handbook/.cache/<policy>-<hash of rationale.md content>.md`. `handbook/verify-fresh.sh <tag>`
recomputes the current hash per policy and fails if no matching cache file exists. Proved live:
deleted one cache entry, `verify-fresh.sh` correctly reported it `STALE` and exited 1;
regenerated, it went back to `OK` and exit 0. A rationale.md edit changes the hash the same way a
deleted cache file does, so the same gate catches real staleness, not just the simulated case.

Last-mile framing is explicit in the README (not just here): "a summary of the rationale a human
wrote, not a substitute for a human deciding whether the policy still holds" -- matching
CONTEXT.md's framing of this as an attempted mitigation of an acknowledged open problem. CI-wiring
is named as a real residual gap (needs an `ANTHROPIC_API_KEY` secret only the org owner can add),
not silently skipped.
