# 66 — The deck check grades the run its own TRUTH line names

Type: task (AFK)
Status: open
Blocked by: none

## Question

verify-demo's on-clock premise — the scheduled workflow rebuilds and commits the deck — is false: truth.yml has no deck step and its cage refuses talk/deck.md, so the check reds every scheduled run whose grades moved and will red again on run 14. Take the no-lane-change route: grade the committed deck against the run its own quoted TRUTH line names, not against "this run"; note the alternative (widen the observation lane to include a generated deck) for the owner if drift-by-a-run proves annoying. Rebuild and commit the deck from the newest run's captures as part of landing. Done = a scheduled run with moved grades no longer reds verify-demo falsely, proven by the next TRUTH line.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M18 (demo check's false premise), minor deck-misstates-three-steps.
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-02, review.** Two facts from the review. No workflow builds the deck: `grep -rn build_deck .github/workflows/` is empty, and `talk/deck.md` is outside OBSERVATION_LANE, so the check reds every scheduled run whose grades moved and nothing can clear it without an ADR-0024 decision to let the clock write a deck. And the deck carries no pound sign at all: none of driftwood's four real prices appears under talk/. Whether the £ beats become beats is fog on the map. Record: REVIEW-2026-09-02.md R12, truth-surface/TS-M1, completeness C7.
