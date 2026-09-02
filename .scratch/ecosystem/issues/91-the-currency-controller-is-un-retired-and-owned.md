# 91 — The currency controller is un-retired and owned

Type: task (AFK)
Status: open
Blocked by: none

## Question

Ticket 13 item 2 retired the currency controller because "ticket 07's fx feed replaces it". The controller re-cages a running pod after its admitted version is retired; the fx feed is money. Ticket 75 Q13 withdrew the retirement: the controller is the estate's only post-admission re-caging mechanism.

1. Amend ticket 13's Answer item 2 with a dated comment that withdraws the retirement of the currency controller and cites ticket 75 Q13. The rest of item 2 stands.
2. Give the controller an owner: it becomes a versioned member of the platform's published `implementations` package, numbered by the platform's tag, with a `party.yaml` line naming platform as its publisher. Its CronJob keeps its schedule under ADR-0024's clock rules and may only re-cage, never loosen, consistent with tighten-only.
3. Define what it does in one sentence in CONTEXT.md (rewrite line 246's aside into a term), and make `verify-currency.sh` or its successor grade that sentence: a pod admitted under a version that is later retired is re-caged to `isolated` on the next controller pass.
4. Ticket 80 item 6 changes direction: execute the un-retirement, not the retirement.

Done = the controller is a graded, owned, versioned member and a retired version's running pod is observed re-caged on a lane sample or an offline harness run named in the gate.

## Notes

Charted by ticket 75 (Q13). Record: REVIEW-2026-09-02.md R10, legacy/L5. The owner's answer was a bare "a"; the reason recorded is the assistant's, under Q11.
