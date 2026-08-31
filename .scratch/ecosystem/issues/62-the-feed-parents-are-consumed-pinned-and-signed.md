# 62 — The feed parents are consumed pinned and signed

Type: task (AFK)
Status: open
Blocked by: 57

## Question

Every adopter's CI checks out ico at ref: main and feeds/insurer at ref: ecosystem/thin-slice — unpinned, unsigned consumption against §2's own definition. Move every parent checkout to the tag+commit pair party.yaml declares (ico to v3.0.0 now; feeds and insurer once ticket 57 cuts their first tags); add ico's Flux pin per GAPS 1.6; and add a verifier that refuses branch refs in composing jobs so the gate catches regression. Done = verify-feed-contract passes on a citable run (unblocked by ticket 54's jsonschema fix) and the new branch-ref check is green.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M10 (unpinned feed parents).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).
