# 60 — The scheduled observations land in the citable number, and steps 3–4 happen once for real

Type: task (AFK)
Status: open
Blocked by: none

## Question

The conversion machinery merged 2026-08-31 but the gate cannot consume it: verify-reconcile calls need_substrate before its cluster-free five-fact sample grading, so it SKIPs in CI before reading drift/samples.jsonl, and verify-e2e-step4 has no sample-reading path. Rewire both so a lane-committed sample grades in the citable run without a cluster. Then watch the first firings (drift-sample 06:20Z, propose-tier 06:47Z, renovate-run, twin-sweep from 2026-09-01): confirm the post-fix propose-tier composes, and when a residual really crosses a band, let the proposal PR open and be human-merged once — the first real step 3. Correct ticket 40's Answer, which cites a four-of-five-facts observation no citable record supports, with a dated note. Done = step 4 and the three verify-reconcile checks grade from a real scheduled sample on a TRUTH line, and one proposal PR has opened and merged.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M7 (gate cannot convert, 2 confirmed findings incl. ticket 40's uncitable citation), M9 (step 3 never real).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).
