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

**2026-09-04, ticket 83.** The contract to build against is written and committed: the module
docstring of `talk/truth_manifest.py`, section **CONTRACT FOR TICKET 59 (the fall-checker)** —
read it there, it is the only copy, and ticket 83's Answer only summarises it. In short: read two
consecutive TRUTH lines with `parse_truth()` and compare class by class; a FALL is any class's
pass count falling, `fail` rising, `ceiling` falling with no manifest change in the same commit,
or `total` falling with no exclusions change — and a pass that became a skip *inside one class* is
a fall even when `fail` is unchanged. The escape hatch is a committed `talk/verify-falls.txt` of
`run=N | reason` lines, validated the way `talk/verify-exclusions.txt` is. Read classes through
`load_manifest()`; never re-derive one from a script header at check time. `truth_manifest.py`
implements `parse_truth()` and deliberately none of the comparison.

Two things ticket 83 learned that this checker inherits. **`ceiling` moves for two different
reasons** and only one is a fall: a script re-classed `never` lowers it (manifest change, same
commit — not a fall), and an exclusion lowers `total` as well (exclusions change — not a fall);
compare against the diff, not the numbers alone. **There are two `never` counts**: the skip
split's, which counts only the never-classed scripts that skipped, and the ceiling's population,
`total - excluded - ceiling`. Use the second wherever the question is "how many can never pass".
Runs 65 and 70 are a usable pair to build against: `pass=59 [observed=13 self=37 simulated=6
meta=3] ... ceiling=77` then `pass=61 [observed=13 self=37 simulated=6 meta=5] ... ceiling=80`.
The two extra passes are both `meta` and both real: `verify/truth-line/verify-truth-line.sh` is
new on run 70, and `verify/demo/verify-demo.sh` turned green when ticket 90 regenerated the deck.
No class fell between the two, which is what a fall-checker should say about that pair.
