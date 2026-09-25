# 152 — Fact 7 cannot pass as registered

Type: grilling (HITL)
Status: open
Blocked by: none

## Question

Fact 7 of the drift lane asks whether the bottom rung reaches nothing while the control reaches. Ticket 86's resolution (2026-09-24) says it cannot pass as registered: under policy 5.0.0 the cage puts the fall-closed pod and the control on the same rung, `isolated`. So there is no bottom rung distinct from the loosest one, and every sample records fact 7 as `null`.

A `null` fact, with no fact observed false, makes the sample COULD-NOT-LOOK. On 2026-09-25 every line in all three adopters read that verdict. So each adopter's `verify-reconcile.sh` and `verify-e2e-step4` SKIP with "the lane sample cannot stand in". Fact 7 is not the only null: fact 2 is `null` on driftwood's and tuppence's own composed source.

Decide how fact 7 is re-registered: which pod is the control, on which rung, and what the pre-registered question becomes. Re-registering the section restarts the scores taken against the old wording (ticket 86's rule).

## Notes

Graduated 2026-09-25 from ticket 35, round 2 Q8. Definition of done includes wiring its check into `talk/verify-all.sh`.

This ticket blocks ticket 151, and the fleet, policy and governance-agent row of ticket 156's register. It relates to ticket 27, the cage ladder round 2, which owns the meaning of the rungs but whose question does not cover fact 7. The rung order, baseline loosest and isolated bottom, is ADR-0022's. Ticket 30 does not own fact 7.
