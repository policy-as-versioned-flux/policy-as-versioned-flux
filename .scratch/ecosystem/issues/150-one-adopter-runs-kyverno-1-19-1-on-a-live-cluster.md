# 150 — One adopter runs Kyverno 1.19.1 on a live cluster

Type: task
Status: open
Blocked by: 147, 148, 149

## Question

Graduated 2026-09-25 from grilling ticket 71, decision 13 (delegated). This is the first engine
bump to go through the route that ADR-0033 point 5 decides. Every earlier ticket measures the
engine offline. This ticket measures it on a real cluster.

**The condition, from grilling ticket 152 (delegated, 2026-09-25).** No adopter moves to Kyverno
1.19.1 while a served cage-tier body that it composes does not compile on 1.19.1. The 5.0.0
cage-tier body does not compile there. So the adopter that moves composes only the ticket 149 line.
Its workloads claim that line, and 5.0.0 leaves its composed set. On the drift lane, an engine that
cannot compile the cage reads as could-not-look, never as a false pass (ticket 152).

Build the following:

1. **Choose one adopter** and record the choice with its reason.
2. **The adopter moves to the ticket 149 line.** Its composed set and its workloads' claims move to
   the new line only.
3. **The adopter declares 1.19.1** in `gitops/engine/kyverno.yaml` (ticket 147), and recomposes.
   Its evidence shows no engine delta, because the new line supports 1.19.1.
4. **Measure the unsafe case on a throwaway KinD, never on the adopter's lane.** Install 1.19.1 and
   the 5.0.0 cage-tier body, which does not compile. Record what admission does with a pod: does it
   admit the pod without the mutation, or does it refuse the pod? If admission lets the pod in
   without the mutation, the cage fails open. That is the worst case that ADR-0033 point 3 prices.
5. **Measure the PolicyReport effect live.** On 1.18.2, Kyverno writes a pass entry for each pod
   that cage-netpol does not match. On 1.19.1 it writes none (measured offline in ticket 71).
   Count the entries on both engines, and run `platform/oscal/result2oscal.py` on both sets of
   reports. Record whether the OSCAL output changes.

## Done

A scheduled drift sample on the chosen adopter records the engine fact true at 1.19.1. It records
the other facts with the same values as the adopter's last 1.18.2 sample. A dispatched run does not
count. The admission question and the PolicyReport question each have a live capture in this
ticket.

## Notes

- The other adopters stay on 1.18.2. Each adopter moves through its own declaration.
- If the chosen adopter's price changes, the evidence must name the reason.
