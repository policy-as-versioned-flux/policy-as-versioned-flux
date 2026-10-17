# 151 — The cloud plane lands in tuppence

Type: task (AFK)
Status: claimed
Blocked by: 157, 161

## Question

Build the cloud plane that ticket 13 item 3 placed and ADR-0004's sequencing note describes. It was never filed until now.

1. `datastore`'s Crossplane claims become a workload in tuppence, beside ledger. They are re-labelled to `policy-as-versioned.dev/policy-version` and re-pinned to tuppence's composed artefact.
2. The RDS and S3 policies become versioned members of platform's published `implementations` package (ADR-0017), not hub fixtures.
3. The dials a Crossplane CR takes on the cage ladder are stated. Ticket 13's cross-ticket note C1 put this on ticket 09. Ticket 09 has no such item, so this ticket carries it.
4. The truth surface grades the claims at admission in KinD, as ADR-0004's proof does.
5. When the check passes, the incumbent repos `datastore` and `cloud` meet their row in the register of ticket 156.

## Notes

Graduated 2026-09-25 from ticket 35, round 1 Q4 and amendment A4. Definition of done includes wiring its check into `talk/verify-all.sh`.

The trigger is `verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh` PASS on a citable truth run. That is the measurable form of ADR-0004's "after the Pod slice runs end to end once". Steps 2 and 3 are class `simulation`, so they are not the trigger. Step 4 SKIPped on runs 339 and 343, because driftwood's lane sample reads COULD-NOT-LOOK. Step 4 grades driftwood by default (`verify-e2e-step4-flux-reconciles-cage.sh:46`). So this ticket is blocked by ticket 152 (fact 7), by fact 2 on driftwood's own composed source (no owner yet, see the note below), and then by step 4's first PASS.

Facts on 2026-09-25: `datastore` holds `README.md`, `claims.yaml` and `kustomization.yaml`, with Crossplane v2 managed resources (`s3.aws.m.upbound.io`, RDS) under the label `mycompany.com/policy-version`. `cloud` holds a README and six harvested OSCAL files: the 800-53r5 catalogue, and the RDS and S3 baseline profiles and component-definitions. The Crossplane v2 setup is in fleet (`infrastructure/crossplane*/`, `verify-crossplane.sh`), and the RDS and S3 policies are in the incumbent policy repo's `cloud/`. [corrected 2026-09-25: the first version said `cloud` holds the Crossplane setup, which is its README's claim, not its content]

**Second blocker, reported 2026-09-25 by the session that grills ticket 152.** Ticket 152 alone cannot give step 4 a PASS. On the 2026-09-25 samples, fact 2 is `null` on driftwood's and tuppence's composed source, and on driftwood falsifier 2 is not looked at on platform and nist either. Step 4 grades driftwood by default (`verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh:46`). No open ticket owns fact 2 yet. This ticket stays blocked until step 4 passes, whatever unblocks it.

**Blockers renamed, 2026-09-25.** Ticket 152 resolved as a grilling ticket and graduated the build to ticket 161. Fact 2 and driftwood's falsifier 2 went to ticket 157. Step 4 needs both, so this ticket is blocked by 157 and 161, and then by step 4's first PASS.

## Implementation, 2026-10-03

The local implementation is prepared, with activation held on the stated trigger. Platform owns
`implementations/cloud`: a separate cloud/v1.0.0 publication path, two Audit policies, RDS/S3
mutating cages, a single Crossplane dial table and its OSCAL cp-10/sc-28 claims. No frozen Pod
line or declared 6.x line was changed by this ticket. The dispatch-only cloud release preflight
requires the signed modern e2e4 clock record and every declared CLI cell before signing a tag.

Tuppence holds opt-in cloud delivery and a preparation helper that extracts an exact signed
platform cloud tag, refuses fixture CRDs as vendor schema evidence, checks real CRD field
shapes and renders only cloud/crds/workload paths. Claims carry the current 5.0.0 composed
claim label and routes consume tuppence-composed. Current tuppence v3.0.0 contains none of
these new paths, so it was not repinned to a fictional commit. Exact incumbent datastore
resource fidelity remains unmeasured because that clone was unavailable in the offline session;
the prepared claims use the locally available incumbent fleet/policy seeds.

The real Kyverno CLI replay passes 22 field/outcome/idempotency cases on exact 1.18.2 and
1.19.1. Offline preserve-unknown CRDs supply resource mapping only. `verify-cloud-plane.sh
--selfcheck` passes the trigger falsifiers and declaration checks. The default check reports
the named declared wait for a qualifying citable step-4 PASS; it contacts no cluster before
the trigger and signed delivery paths exist. It is discovered by talk/verify-all.sh and has
an estate-observation manifest row; the separate package replay is self-proof.

Limits are explicit: CLI status-only oldObject behavior and real vendor schema are not observed
by replay; isolated's available service dials equal quarantine, with no AWS network-isolation
claim; an absent S3 configuration CR is not evidence that a Bucket is encrypted. Nothing is
denied, paused or put on an Observe-only reconciliation mode. No provider, ProviderConfig,
credentials, AWS resource, tag, commit or remote branch was created. The datastore/cloud
register rows already name the admission check and remain ineligible while it skips.

This local validation is not citable estate truth. The ticket remains claimed pending the
modern citable e2e4 PASS, actual signed package/composed publication and KinD admission grade.

## Recovery and delivery repair, 2026-10-17

The unchanged signed original for run388, `087a09a7bac32fbdd20433b7e7d3c95d960d371a`,
is now ancestral to public hub main and its exact TRUTH line is recorded there. The actual
trigger reader exposed an implementation fault: the pinned gitsign0.17.1 command for a commit
is `verify`, not `verify-commit`. Correcting that command lets the real identity-pinned offline
reader accept run388's observed step4PASS. This is a recovered original, not a new historical
measurement or a fixture trigger.
The automatic lookup also needs full Git history: default path simplification hides genuine
side-parent clocks when a recovery merge retains a later capture tree. A real normal-merge
regression first reproduced the false missing-trigger wait; traversing all parents finds the
unchanged qualifying original.

The real Upbound v2.6.0 RDS/S3 CRDs are pinned to upstream commit
`857b535dd0eb9b8242ad9d7c4e54aaa3e4616d60` and their original SHA256 values. Their field
shapes match the prepared CEL; replay now uses these genuine documents. Datastore's original
commit `988e414eb01c7f768bdd9fc75a0d7e068745a9b3` contains three claims. Tuppence's replacement
ledger seeds were not a faithful lift: the repair conserves all three resource names, specs,
selectors and other labels, changing only namespace and the policy claim. The original file,
Git blob and SHA256 are retained with that workload.

Delegated under ADR0025: an optional cloud-package adapter goes through the ordinary composer
seam. A separately identity-verified cloud tag supplies the complete cloud tree, vendor schemas,
workload and receipts. This is necessary because the genuine `verify()` gate correctly rejects
cloud YAML appended after composition. No cloud pin preserves existing behavior; the separate
compiler pin can move without accepting a Pod policy major or moving Tuppence's engine1.18.2.
The compiler release is versioned from its actual interface change; the existing policy bump
oracle explicitly handles only `policy/v*` tags and does not compute compiler SemVer.

The cloud grader binds expected dials to the exact signed cloud parent in the composed artefact,
checks the live vendor CRD bodies and all three incumbent resources, and keeps AWS reconciliation
outside its proof. An opt-in TRUTH dispatch can provision only an ephemeral GitHub-hosted KinD
substrate before running this native checker. Its guard refuses local and self-hosted execution.
Only an actual subsequent native PASS and ordinary signed recording establish admission.

These source repairs do not close the ticket. Signed cloud/compiler releases, Tuppence's real
cloud/composed pins and signature gates, genuine hosted admission, and incumbent-register checks
still have to complete in that order. No future tag SHA, admission result, grade or price is filled in.
