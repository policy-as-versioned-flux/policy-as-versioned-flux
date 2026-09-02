# 62 — The feed parents are consumed pinned and signed

Type: task (AFK)
Status: open
Blocked by: 57

## Question

Every adopter's CI checks out ico at ref: main and feeds/insurer at ref: ecosystem/thin-slice — unpinned, unsigned consumption against §2's own definition. Move every parent checkout to the tag+commit pair party.yaml declares (ico to v3.0.0 now; feeds and insurer once ticket 57 cuts their first tags); add ico's Flux pin per GAPS 1.6; and add a verifier that refuses branch refs in composing jobs so the gate catches regression. Done = verify-feed-contract passes on a citable run (unblocked by ticket 54's jsonschema fix) and the new branch-ref check is green.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M10 (unpinned feed parents).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-01 (from ticket 60's clock watch): the defect now fails hard, not just unpinned.**
The `ecosystem/thin-slice` branch no longer exists on feeds, so every checkout that names it
dies at fetch. First observed live: tuppence propose-tier's first scheduled firing (13:42Z)
failed with "A branch or tag with the name 'ecosystem/thin-slice' could not be found". Twelve
checkouts carry the ref: tuppence and ludlow × {shift-left.yml, propose-tier.yml,
cut-release.yml} × {feeds, insurer}. Until this ticket lands, tuppence and ludlow cannot
propose, shift-left or cut a release — their step-3 path is dead on the clock, not merely
unsigned. Driftwood was re-pinned by ticket 61 and is unaffected. Note for the fix: feeds now
carries real tags (threat-register/v1.0.0, v2.0.0), so the feeds half no longer waits on
ticket 57; the insurer half still does.

**2026-09-02, review.** Confirmed live 2026-09-02: twelve `ecosystem/thin-slice` refs across tuppence and ludlow ({propose-tier, shift-left, cut-release} × {feeds, insurer}); both adopters' scheduled propose-tier runs died at checkout on 2026-09-01 and 2026-09-02. Two additions from the review: driftwood consumes ico, feeds and insurer at `ref: main` in nine places with no Flux source, and ico, insurer and feeds `release.yml` check platform out with no ref. Ticket 77 carries those with the shared content-of-pin check; land the twelve refs together with it. Record: REVIEW-2026-09-02.md R4.
