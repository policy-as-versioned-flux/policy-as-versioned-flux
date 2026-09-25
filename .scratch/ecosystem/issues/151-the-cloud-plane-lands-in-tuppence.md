# 151 — The cloud plane lands in tuppence

Type: task (AFK)
Status: open
Blocked by: 152

## Question

Build the cloud plane that ticket 13 item 3 placed and ADR-0004's sequencing note describes. It was never filed until now.

1. `datastore`'s Crossplane claims become a workload in tuppence, beside ledger. They are re-labelled to `policy-as-versioned.dev/policy-version` and re-pinned to tuppence's composed artefact.
2. The RDS and S3 policies become versioned members of platform's published `implementations` package (ADR-0017), not hub fixtures.
3. The dials a Crossplane CR takes on the cage ladder are stated. Ticket 13's cross-ticket note C1 put this on ticket 09. Ticket 09 has no such item, so this ticket carries it.
4. The truth surface grades the claims at admission in KinD, as ADR-0004's proof does.
5. When the check passes, the incumbent repos `datastore` and `cloud` meet their row in the register of ticket 156.

## Notes

Graduated 2026-09-25 from ticket 35, round 1 Q4 and amendment A4. Definition of done includes wiring its check into `talk/verify-all.sh`.

The trigger is `verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh` PASS on a citable truth run. That is the measurable form of ADR-0004's "after the Pod slice runs end to end once". Steps 2 and 3 are class `simulation`, so they are not the trigger. Step 4 SKIPs on every run today, because each lane sample reads COULD-NOT-LOOK while fact 7 cannot pass. So this ticket is blocked by ticket 152 first, and then by step 4's first PASS.

Facts on 2026-09-25: `datastore` holds `README.md`, `claims.yaml` and `kustomization.yaml`, with Crossplane v2 managed resources (`s3.aws.m.upbound.io`, RDS) under the label `mycompany.com/policy-version`. `cloud` holds the harvested OSCAL 800-53r5 catalogue and the Crossplane v2 setup. The OSCAL component-definition in platform maps two Check_Ids today.

**Second blocker, reported 2026-09-25 by the session that grills ticket 152.** Ticket 152 alone cannot give step 4 a PASS. On the 2026-09-25 samples, fact 2 is `null` on driftwood's and tuppence's composed source, and on driftwood falsifier 2 is not looked at on platform and nist either. Step 4 grades driftwood by default (`verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh:46`). No open ticket owns fact 2 yet. This ticket stays blocked until step 4 passes, whatever unblocks it.
