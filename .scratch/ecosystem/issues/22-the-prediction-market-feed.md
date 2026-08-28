# 22 — The prediction-market feed

Type: grilling (HITL)
Status: open
Blocked by: 21

## Question

Reversal 6: ship prediction-market price moves as a signed feed under the contract, `kind: feed`, `name: market-moves`. Decide the payload: which markets, which fields (market id, question, dated price series, source), and which £ input a move is allowed to touch. Markets never price a control. Decide the schedule that fetches it without an LLM, and the skill a human runs over the result.

## Notes

Reversal 6. GAPS 3.21. Findings P031, P207, H4-13. The forecast book as credibility instrument stays in fog until ticket 08.
