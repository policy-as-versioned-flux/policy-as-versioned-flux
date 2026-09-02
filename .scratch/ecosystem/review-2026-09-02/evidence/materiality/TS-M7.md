# TS-M7 materiality — moving denominator

Verdict: MATERIAL, severity MINOR (down from major as filed).

## What survives
A verify script that disappears from the tree (a unit repo deleting a red check,
or a stale .estate-clone/ tree that clone-estate.sh's idempotent skip keeps)
lowers both `total` and `fail` and nothing in the instrument objects. That is an
undetected fall, and it is NOT covered by ticket 59(a), which diffs only "a fall
in pass or a rise in fail". A red check that vanishes shows as fail falling.
This is a real crack in NORTH-STAR principle 6 (the record is falsifiable).

## What does not survive
1. A moving denominator is the DESIGNED behaviour, not a defect. NORTH-STAR §5
   bullet 1 asks for glob discovery ("discovers every verify*.sh by glob"), and
   talk/verify-all.sh:47 does exactly that. An asserted expected count would
   contradict the ratified design. Every recorded jump maps to recorded growth:
   56->68 at run 9 is hub verify/ additions (units feeds/insurer are `=none` on
   that line), 68->73->83 at runs 10-12 is the estate going six units to eight
   (clone-estate.sh:23 UNITS has 8), 83->84 at run 17.
2. "No two TRUTH lines are comparable" overstates. The load-bearing figure the
   estate cites is absolute `fail`, and `fail` cannot be diluted by adding
   scripts — a new script can only add a pass, a fail or a skip, never convert
   an existing fail to a pass. fail 16 -> 0 -> 7 is a valid comparison across
   any denominator. Only a pass *rate* is incomparable, and the estate does not
   quote a rate.
3. The §5 bullet 5 citation ("a fall is a blocking event") is a restatement of a
   known, owned gap: .scratch/ecosystem/issues/59-*.md is open and explicitly
   owns fall-detection, closing the previous review's M14.
4. "Claimed ownership: none found" is not correct for the narrative half. The
   one bad cross-run comparison the finding leans on
   (.scratch/ecosystem/map.md:61, "40 pass, 16 fail of 56 to 65 pass, 0 fail of
   83") already carries a dated correction two lines below it
   (map.md:64: "The 65/0/16 figure was a local rehearsal. No TRUTH...") and is
   owned by issues/67-the-record-matches-the-surface.md, whose item (d) is
   "wire a small check into the gate: any pass/fail figure that map.md quotes
   must exist as a line in talk/truth.log". That is the fix for the stated fit
   impact.
5. Partial clone shrink is further limited: clone-estate.sh:20 `set -euo
   pipefail` aborts on a failed clone (the finding concedes this), and the TRUTH
   line prints all eight unit short-HEADs, so an absent or unresolvable unit is
   visible on the line itself (run 9 shows `feeds=none insurer=none`).

## Why minor and not housekeeping
The deletion-shrink hole is unowned and one line of gate code away from closed
(record per-unit script counts, or refuse a `total` decrease without a reason
line in the exclusions-file style). It is worth charting. It does not stop any
ambition being claimed, and no instance of it having happened is offered.
