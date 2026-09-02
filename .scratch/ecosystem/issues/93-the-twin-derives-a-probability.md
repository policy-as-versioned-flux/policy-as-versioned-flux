# 93 — The twin derives a probability

Type: task (AFK)
Status: open
Blocked by: 92

## Question

Ticket 75 Q10 decided (a): the twin derives a probability from signals rather than reading it from YAML. NORTH-STAR §2's "priced forecasts, scored against reality" stands as written. The model call runs through the local clock (ticket 92).

1. Design the derivation as a Claude Code skill the local clock runs: inputs are the adopter's world model, the subscribed feeds' dated series and the scenario; output is a probability with a stated basis, an evidence grade, and the signals it rested on, written to the adopter's overlay as a PR.
2. Re-open the ordinal-arithmetic and grade-5 rulings only as far as the derivation needs: decide, record with a reason, and amend the ADR that holds each ruling with a dated note. Do not re-ask the owner (ticket 75 Q11).
3. The scoring apparatus stays: every derived probability is pre-registered before the outcome date and scored under proper scoring rules; a derived probability that was not pre-registered is not scored.
4. A world model still carries a recorded belief where no signal exists; the artefact says which of the two each probability is.
5. `verify-twin-evals.sh` grades: at least one derived probability exists on a citable run, its basis names a real feed observation, and its score is computed after the outcome date.

Done = one derived, pre-registered, scored probability on a citable run, and the twin row of NORTH-STAR §2 is true as written.

## Notes

Charted by ticket 75 (Q10). Blocked by 92 for the model call. Ticket 23's rule stands: only a human-merged, tagged entry is price-eligible.
