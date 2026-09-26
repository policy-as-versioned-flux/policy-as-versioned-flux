# 150 — One adopter runs Kyverno 1.19.1 on a live cluster

Type: task
Status: open
Blocked by: 147, 148, 149, and owner steps: the adopter-gate retirement, the adopter's signed composed tag and composed-set move, and a platform tools tag that carries the 149 line

## Question

Graduated 2026-09-25 from grilling ticket 71, decision 13 (delegated). This is the first engine
bump to go through the route that ADR-0033 point 5 decides. Every earlier ticket grades policy
behaviour offline. This ticket grades it on a cluster that an adopter runs.

**The condition, from grilling ticket 152 (delegated, 2026-09-25), widened by ticket 71's
review.** No adopter moves to Kyverno 1.19.1 while a body that is served in its window does not
compile on 1.19.1. The 5.0.0 cage-tier body does not compile there. So the adopter that moves
composes only the ticket 149 line: its workloads claim that line, and 5.0.0 leaves its composed
set. Ticket 152 decided that on the drift lane an unstamped fall-closed pod keeps reading `null`
for fact 6. How facts 4, 5 and 7 read when the engine holds a body that it cannot compile is not
measured.

**Owner steps.** To drop 5.0.0 from an adopter's composed set is a retirement. The adopter's own
gate refuses a pull request that retires a version (ticket 132). The 4.0.0 retirement passed only
because the integrator merged over the refusal on the owner's authorisation (ticket 113). This
ticket needs the same authorisation. It also needs the adopter's signed composed tag and its
composed-set move (ticket 130), and a platform tools tag whose array carries the 149 line. If the
149 line is a major, the adopter's acceptance record comes first (ticket 149).

Build the following:

1. **Choose one adopter** and record the choice with its reason. Prefer an adopter none of whose
   workloads run on a cluster that another adopter uses, because a shared cluster runs one engine
   (ADR-0033 point 2). Today that is ludlow: tuppence's workload flagship runs on
   `kind-driftwood`.
2. **The adopter moves to the ticket 149 line.** Its composed set and its workloads' claims move to
   the new line only.
3. **The adopter declares 1.19.1** in `gitops/engine/kyverno.yaml` (ticket 147), and recomposes.
   Its evidence shows no engine delta, because the new line and the machinery both support 1.19.1.
4. **The hub runs the adopter's probe on the adopter's engine.** Ticket 161's
   `verify-cage-probe.sh` compares the CLI version with the adopter's declared engine. The hub runs
   it with the truth CLI, 1.18.2. Before the declaration moves, the hub gives that check the
   adopter's declared CLI from the engine table (ticket 146). Otherwise its row falls on every
   truth run.
5. **Measure the unsafe case on a throwaway KinD, never on the adopter's lane.** Install 1.19.1 and
   the 5.0.0 cage-tier body, which does not compile. Record what admission does with a pod: does it
   admit the pod without the mutation, or does it refuse the pod? If admission lets the pod in
   without the mutation, the cage fails open. That is the worst case that ADR-0033 point 3 prices.
   If admission refuses the pod, point 3 reopens. A throwaway-KinD capture is a rehearsal, not Done
   evidence (ADR-0028, lines 35-36, citing ADR-0023). Record it in this ticket as reasoning.
6. **Measure the PolicyReport effect on the lane.** `platform/oscal/result2oscal.py` drops a result
   whose policy maps to no control, so cage-netpol's report entries cannot change the OSCAL output.
   The entries that matter are `require-nonroot`'s, which map to ac-6. Drift samples record no
   PolicyReport today. So the lane first captures PolicyReports, and at least one scheduled 1.18.2
   sample carries that capture before the engine moves. Then compare it with the first 1.19.1
   sample.

## Done

A scheduled drift sample on the chosen adopter runs Kyverno 1.19.1 installed from its declared file.
It records the facts with the same values as the adopter's last 1.18.2 sample, or the ticket names
the reason for each difference. A dispatched run does not count. The admission question from item
5 has a recorded answer, and ADR-0033 point 3 is confirmed or reopened.

## Notes

- The other adopters stay on 1.18.2. Each adopter moves through its own declaration.
- If the chosen adopter's price changes, the evidence must name the reason.
