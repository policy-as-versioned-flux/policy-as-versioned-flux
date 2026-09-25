# 155 — The lane runs the served workloads, and collects their evidence

Type: task (AFK)
Status: open
Blocked by: none

## Question

Two changes to each adopter's drift lane.

1. **The served workloads run.** Each adopter moves its own `gotk-sync.yaml` pin to its newest signed tag by a reviewed pull request. On 2026-09-25 each still pinned `v1.0.0`, whose tree lists no lifted app. The lane reconciles `./gitops/apps`. A new fact 8, in its own pre-registered section of `drift/window.yaml`, records for each served workload whether it runs in its cage, in the API server's words. A control copy of the same workload runs outside the governed namespace on the same node. "Does not fit the cage" is graded only when the control runs and the caged copy does not. The runner size is a recorded ceiling. A separate section does not restart facts 6 and 7. A workload that does not fit its rung is a priced outcome, never a carve-out.
2. **OSCAL collection is a lane step.** After the facts, a step reads the PolicyReports on the lane cluster. It runs `result2oscal.py` from the platform tag the lane pins, and appends the assessment-results next to the sample as an observation. There is no CronJob, because the cluster lives for one run. The step prints how many served policies the component-definition maps and how many PolicyReports it read. It records a could-not-look when no PolicyReport exists before the cluster is deleted. A hub check reads each adopter's newest assessment-results and grades that each not-satisfied observation joins a cage risk. The component-definition is extended by whoever ships the implementation (ADR-0017), which is platform.

## Notes

Graduated 2026-09-25 from ticket 35, round 1 Q3 with amendment A3, and round 2 Q6 and Q7. Definition of done includes wiring its check into `talk/verify-all.sh`.

Facts on 2026-09-25: the component-definition maps two Check_Ids, `require-nonroot` and `governed-namespace-requires-claim`. Each composed set serves 4 ValidatingPolicy, 6 MutatingPolicy, 2 GeneratingPolicy and 5 PriorityClass documents. The lane waits only for the Kyverno admission controller. Nothing has measured whether a PolicyReport for a probe pod exists before teardown.

When the OSCAL check passes, the incumbent `c2p-collector` repo meets its row in ticket 156's register. Ticket 154 first is preferred, so the lane runs the image each adopter builds.
