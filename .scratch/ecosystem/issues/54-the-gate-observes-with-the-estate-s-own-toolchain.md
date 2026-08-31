# 54 — The gate observes with the estate's own toolchain

Type: task (AFK)
Status: open
Blocked by: none

## Question

truth.yml pins kyverno 1.19.0 by accident (db47f88 was a URL fix) while the estate is authored against 1.18.2, so cage-tier 4.0.0 fails CEL compilation and reds verify-graded, verify-shift-left and verify-render-version-tree in every citable run. Either fix the expression (e.g. string(variables.tier)) so the policy loads on >=1.19 — cut through the release machinery if the engine computes a bump — or pin 1.18.2 with a written reason in the workflow; if the choice needs the owner, raise it inside ticket 58's round rather than assuming. Also: add jsonschema to the pip line (or build the .venv the scripts probe for) so e2e-step1, e2e-step6, feed-contract and twin-overlay can look; pin cosign by version and sha256 like gitsign. Done = the three CEL reds and four jsonschema SKIPs convert on a scheduled TRUTH run, and the toolchain pins each carry a reason.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: C1 (kyverno skew, 4 confirmed findings), M5 (jsonschema, 2 confirmed findings), minor cosign-unpinned.
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).
