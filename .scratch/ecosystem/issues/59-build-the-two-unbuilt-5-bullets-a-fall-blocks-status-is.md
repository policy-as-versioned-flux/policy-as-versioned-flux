# 59 — Build the two unbuilt §5 bullets: a fall blocks, Status is derived

Type: task (AFK)
Status: open
Blocked by: none

## Question

(a) truth.yml diffs the new TRUTH line against the previous one and raises a distinct, unmissable failure on any fall in pass or rise in fail — including a pass-to-skip degradation with zero fails — with a committed-reason escape hatch mirroring the exclusions-file pattern; decide in the ticket what it blocks (release dispatch is the natural candidate). (b) Build the checker GAPS 2.9 already specifies: map each resolved ecosystem ticket to its named gate check and flag Status from the scheduled run, as the twin harness already does for its own tracker; normalise the 16 free-typed 'Status: open' lines to the issue-tracker vocabulary. Done = both mechanisms run in the gate and a synthetic fall demonstrably fires.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M14 (fall-is-blocking and derived-Status, 2 confirmed findings), minor pass-to-skip-goes-green.
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-02, review.** Still unbuilt. Run 17 to 18 fell from 59 pass to 57 and nothing fired; 17 of 21 truth runs fail at the same step so the signal is saturated. Ticket 83 puts a class manifest and a published ceiling on the TRUTH line; build the fall-checker over that manifest so a fall is compared class by class. Record: REVIEW-2026-09-02.md R3, truth-surface/TS-M4.
