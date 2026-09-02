# 89 — Deny is not a rung: the mutating controller

Type: task (AFK)
Status: open
Blocked by: none

## Question

Ticket 75 Q5 was answered by the owner with a reason: proportionality is managed with a better cage and better mitigations; a workload can find itself unable to run only because it does not fit the cage, never because it is deliberately denied; the estate is a mutating admission controller more than a validating one. The assistant's narrower call, a surviving locked door for access control, data protection and key management, is overruled.

Make the estate say and do that:

1. Inventory every shipped `validationFailureAction: Enforce` or Deny-shaped rule in the served policy copies (the review counted two Deny policies). For each, either re-express it as a cage constraint (a mutation that renders the workload into a rung it cannot run from, or a tighten-only mutation the workload must fit) or retire it with the engine's computed bump. Record the choice per rule.
2. `verify/proportionality` derives Audit versus Deny from each party's signed band and has no shipped subject. Retire the Audit-versus-Deny derivation, or re-point it at tier selection, and update or delete the verify script so the gate does not grade a mechanism that no longer exists.
3. Reconcile the three documents that disagree about whether a Deny may ship (the review names them under principles/P2) to one sentence: nothing is denied; a workload that does not fit its cage does not run.
4. Amend CONTEXT.md's Cage entry (done by ticket 75 for the definition) and check ADR-0014, ADR-0018 and ADR-0022 carry dated notes that say the same.

Done = no served policy copy contains a Deny-shaped rule that is not a cage constraint, `verify-all.sh` grades no Audit-versus-Deny subject, and the three documents agree.

## Notes

Charted by ticket 75 (Q5). Findings: REVIEW-2026-09-02.md principles/P2, the two shipped Denys. ADR-0022 carries the owner's reason as a dated note.
