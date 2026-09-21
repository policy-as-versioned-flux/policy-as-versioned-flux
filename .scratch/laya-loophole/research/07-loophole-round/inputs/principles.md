These are the estate's own normative claims about the cage. Every line is quoted
or paraphrased from `CONTEXT.md` (the "Cage" and "Exemption" entries) and from
ADR-0022's own notes. Nothing here is invented for this run.

1. There is no gate. Everything is always caged. A workload, a human, a device,
   a model action and the twin itself each run inside a cage. The cage spec is
   the only variable, and the price (the "£") selects the spec.

2. Nothing is denied; a workload that does not fit its cage does not run. In the
   owner's words: the estate is a mutating admission controller more than a
   validating one. A workload can be unable to run only because it does not fit
   its cage, never because it is deliberately denied.

3. An exemption is a banned concept. There are none, ever, at any scope, in any
   file, under any name. An exemption is a carve-out for a named workload, and
   the everything-is-codified rule admits no exceptions to itself.

4. The first legitimate alternative to an exemption is conditional policy: "you
   may do X if you meet conditions C", so anyone meeting C is treated
   identically and nobody asks a favour.

5. The second is to let the cage implement the control on the workload's behalf
   and price the residual.

6. A workload that can satisfy neither is caged tighter until the cage is
   untenable. The bottom rung is "too expensive to run or not functional",
   reached by the price, never by a carve-out, and never a refusal.

7. An unknown or unlabelled tier fails closed to `isolated`. Silence buys
   nothing anywhere. Silence is not an exemption and it is not a refusal
   either; silence is the bottom rung.

8. The cage mutation is tighten-only. It never writes a security field looser
   than the workload declared.

9. The tier attaches to a governed Namespace, not to a workload. The pod label
   is an output only, because a pod label is forgeable.

10. The tier selection is over the party, not the price line. One Namespace
    carries one tier for every pod in it, so the declaration can never be looser
    than the party's worst-priced regime.

11. An adopter may declare one tighten-only floor. Lowering the floor is priced,
    never refused.

12. Only a party holding the `platform` role may declare a Namespace at `infra`.
    A declaration from any other party renders to `isolated`.

13. Disagreement with a rule is resolved by a pull request to the policy, in the
    open, under review. It is never resolved by a favour, a ticket or a silent
    edit.
