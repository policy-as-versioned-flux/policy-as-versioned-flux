# 145 — The platform prices the twin agent's cage

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-25 from grilling ticket 30, decisions 3, 10, 11, 12 and 15 (delegated), and
ADR-0031.

1. **A dial table for the twin-agent class**, beside `graded/cage.py` `TIERS`, with the four rows
   of ticket 30 decision 11 and a reduction and a cost for each rung.
2. **The reductions are derived from the misuse paths each rung closes** (decision 15), each path
   named as a twin-agent row in `twin/ecosystem-misuse-catalogue.yaml`:
   - the writer job pushes a looser declaration: closed at `isolated` only;
   - the writer job merges or tags through REST: closed at `isolated`;
   - a misleading proposal PR is merged by a human: closed at `quarantine`;
   - a model step writes a wrong binding or forecast: closed at `restricted`; about £0 on price,
     because model claims are grade 5 and `price_eligible: false`.
   The run cost of every rung is £0 in cash, and cost stays out of selection.
3. **The scenario** (decision 12): loss magnitude is the gap between the adopter's residual at the
   loosest rung and at the selected rung, over the window until the gate detects the act;
   frequency is a threat-register row feeds publishes.
4. **A new `prices[]` kind** for a subject that is not a pod. The tier fold
   (`wargamer/wargamer.py:249-258`) must key on the subject, so this line never folds into a
   Namespace tier. `verify/pound-seam/pound_seam.py` (exactly one `source: twin` line, known
   sources only) and the handbook's kind list learn the kind.
5. **The adopter's selection policy selects the rung**; the proposer proposes it; a human merges.
   The twin never prices or selects its own cage.

## Notes

The platform release and the adopter recomposes wait for the owner's authorisation. Ticket 143
reads the selected rung.
