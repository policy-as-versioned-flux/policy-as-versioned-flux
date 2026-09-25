# 160 — A fact that is never looked at is a fall

Type: task (AFK)
Status: open
Blocked by: 161

## Question

Ticket 152 Q10 made a cage fact that is null on three samples in a row read FAIL. Ticket 161 builds that rule for facts 6 and 7. Apply the same rule to the five facts of each adopter's drift lane.

The reason: the four `talk/verify-manifest.txt` rows for each adopter's `verify-reconcile.sh` and for step 4 match "the lane sample cannot stand in" anywhere in the line (`talk/truth_manifest.py:133`). So any lane could-not-look reads as a declared wait, whatever its cause. From 2026-09-24 fact 7 was null on every sample because the cage put both probe pods on one rung. Before that, fact 6 was observed FALSE and each sample read FAIL. On 2026-09-25 the gate judged fact 7's null a declared wait. A fact that stays null must become a fall, while a null that clears on the next sample stays a could-not-look.

The five facts have no registration by section today. The guard over `drift/window.yaml` reads the file's first commit, and a later commit does not move it (ludlow `drift/window.yaml:164-167`). `grade` applies no registration date to facts 1 to 5. So this ticket must either add a registration for the five facts and say that it starts a new clock, or record that the rule changes grading without moving any registration.

## Notes

Graduated 2026-09-25 from ticket 152, Q10 and Q11. Blocked by 161 so that the rule's form is settled on the cage facts first. Definition of done: `grade` reports FAIL for any of the five facts that is null on three samples in a row, a selfcheck branch proves it, and the adopters' checks under `talk/verify-all.sh` carry it.

On tuppence, fact 2 changes between null and true (ticket 157). A single null between two trues must stay a could-not-look. A run of five nulls, 2026-09-17 to 09-21, would be a fall under this rule.
