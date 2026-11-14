# P2 — platform money engine and cage ladder

Area: `platform/{risk,fair,tcor,engine,currency-controller,graded,implementations,policy,break-glass,recovery-expense,party,docs}` plus `party.yaml`, `CONTEXT.md`, `README.md`. FRESH clone of 2026-11-14. 106 files, 16,993 lines (`wc -l`). Paths below are relative to FRESH unless they start with `platform/`.

## Summary

- The whole loop kernel in this area is about 310 lines of live code, docstrings included, inside four files (1,407 lines with selfchecks): `fair/fair.py`, `fair/severity.py`, `risk/enforce.py`, `graded/cage.py`, plus 202 non-comment lines of Kyverno/PriorityClass YAML in `graded/policies/`. That is about 3% of the area by live lines, 11% counting the whole files.
- Money = Monte-Carlo ALE of `frequency x magnitude` (beta-PERT, 10,000 years, seed 42). Selection = loosest of four rungs whose `ALE x (1 - reduce)` fits the party's one declared tolerance, clamped up to a declared floor.
- The four `reduce` numbers (0.30 / 0.70 / 0.92 / 0.98) are the only link between a rung and money. The file itself says they are "evidenced by nothing but this comment" (`platform/graded/cage.py:71-72`). The first three date from the automated estate build of 2026-07-31 and have not changed.
- In the served estate the ratchet is at its end stop and has not moved since it was set: all three adopter Namespaces have declared `isolated` since 2026-08-28, all three declare `overlay.floor: isolated` since 2026-10-23, and at that rung tuppence's residual is GBP 2,057,390 against a GBP 15,000 tolerance (`breaches_band: true`) and ludlow's is GBP 61,725,982 against GBP 5,000. Driftwood's is GBP 36,150 against GBP 40,000 with no verdict given.
- Maximum reduce is 0.98, so no rung can fit any line whose uncaged ALE exceeds 50 x tolerance. There is no gate and no further action when the bottom rung does not fit.
- Tightening the cage changes only a derived "residual" figure through those constants. Nothing observed on a cluster feeds back into the money.
- 7,723 lines (45% of the area) do nothing for the loop: a cloud (RDS/S3) cage package with 3,511 vendored CRD lines, a 2027 recovery-expense ledger, break-glass, TCoR and demo material. A further 4,823 lines (28%) are checks and fixtures around the kernel.

## Components

| # | name | paths | lines | born | what it does | loop role | necessity | origin | status | cite |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FAIR money engine | `platform/fair/fair.py`, `fair/severity.py` | 516 | 2026-07-31 (severity 2026-08-28) | Samples beta-PERT frequency and magnitude over 10,000 simulated years; returns ALE, VaR95, TVaR, carried. Optional lognormal-GPD tail. About 130 lines are selfcheck. | quantify | kernel | owner_words (grounding controls in the fine; the FAIR/PERT/TVaR method is the assistant's) | observed_running (its output is the composed evidence in each adopter) | `platform/fair/fair.py:133-175,200-227`; owner 2026-07-23T15:29, eight days before the build, at `hub/.scratch/drift-review-2026-08-27/evidence/AMBITION_TIMELINE.json:324` |
| 2 | FAIR fixtures and tail check | `platform/fair/scenarios/*`, `fair/verify-fair-tail.sh` | 87 | 2026-07-31 / 2026-08-28 | Two illustrative scenarios and a script proving the heavy tail is heavier. | evidence | support | assistant | tested_offline | `hub/talk/captures/_grades.tsv:57` |
| 3 | Appetite reader and Audit/Deny verdict | `platform/risk/enforce.py` | 223 | 2026-07-31 | `tolerance_for()` reads `appetite.tolerance` from the party's own `party.yaml` and refuses when absent (42 lines, kernel). `decide()` is an older second comparator: Deny when `ALE_warn - ALE_deny > tolerance`; reached only from wargamer and the reflexive self-check. | tolerance | kernel (reader only; `decide()` is a duplicate comparator, see cage.select_tier) | owner_words for "risk appetite" as a concept (2026-07-23, `hub/.scratch/drift-review-2026-08-27/evidence/AMBITION_TIMELINE.json:338`); the number, the band and the comparison are the assistant's; moving it onto party.yaml was delegated (hub ADR-0021) | observed_running (reader, via composition); tested_offline (`decide`) | `platform/risk/enforce.py:65-98,101-109`; callers `platform/wargamer/wargamer.py:104`, `platform/honesty/reflexive.py:64` |
| 4 | Audit-to-Deny demo material | `platform/risk/PR.md`, `risk/verify-risk-tuned.sh`, `risk/scenarios/*` | 103 | 2026-07-31 | A sample PR text, a tightened scenario and a script showing the flip. | presentation | ceremony | assistant | tested_offline | `hub/talk/captures/_grades.tsv:70` |
| 5 | Cage ladder table and selector | `platform/graded/cage.py` | 668 | 2026-07-31 | Lines 82-131 the tier table; 294-383 `caged_residual`, `select_tier`, `clamp_to_floor`, `select` (kernel, about 140 lines). Lines 133-291 a second "twin agent" dial table priced at about GBP 0-19. Lines 386-459 an OSCAL risk object. Lines 473-640 selfcheck. | ratchet | kernel | owner_words for a degraded, resource-constrained state instead of a refusal (2026-07-31T09:30Z, seven hours before the first commit); assistant for the four named rungs, every number in the table and the threshold rule | observed_running (called by composition; tiers recorded in served evidence) | `platform/graded/cage.py:82-127,313-348`; `hub/.scratch/drift-review-2026-08-27/evidence/AMBITION_TIMELINE.json:1005`; first commit 7a36bf7, 2026-07-31 16:22 +0100 |
| 6 | Cage admission policies (authoring copies) | `platform/graded/policies/*` | 502 (202 non-comment) | 2026-07-31 | `cage-tier` MutatingPolicy stamps the rung's fields on every pod that claims a policy version; `cage-netpol` GeneratingPolicy creates three NetworkPolicies; four PriorityClasses. These are the authoring copies; served copies are frozen per version in `distribution/policies/v*/` (43 lines each) and copied into each adopter's `composed/policies/`. | cage | kernel | owner_words ("contrained iops, cpu, memory, network etc, or maybe have more waf rules applied", 2026-07-31T09:30Z) | observed_running at the bottom rung only | `platform/graded/policies/cage-tier.yaml:225-304`; `hub/.scratch/drift-review-2026-08-27/evidence/AMBITION_TIMELINE.json:1005`; `hub/talk/captures/verify_e2e_verify-e2e-step4-flux-reconciles-cage.out` (fact 7) |
| 7 | Cage Kyverno test fixtures | `platform/graded/tests/**` | 1,214 | 2026-07-31 | Pod fixtures and expected patched output for `kyverno test`. | evidence | support | assistant | tested_offline | `platform/graded/tests/cage-tier/kyverno-test.yaml` |
| 8 | Cage verify script | `platform/graded/verify-graded.sh`, `check-netpol-generation.py`, `graded/scenarios/*` | 883 | 2026-07-31 (check 2026-10-03) | Offline: selfcheck, kyverno tests, table-vs-CEL drift guard. Live tail: creates real pods and probes reach. | evidence | support | assistant | tested_offline (live tail SKIP at truth run 491) | `hub/talk/captures/_grades.tsv:60` |
| 9 | Demo-path installer | `platform/graded/up.sh`, `prune-retired.py`, `waf-placeholder/Dockerfile` | 221 | 2026-07-31 / 2026-08-29 | `kubectl apply` twin of the Flux delivery, a pruner for retired versions, and a busybox image that stands in for the WAF sidecar. | enact | duplicate (Flux delivery in `platform/distribution/`) | assistant | unknown | `platform/graded/prune-retired.py:1-6`; `platform/graded/waf-placeholder/Dockerfile:14-19` |
| 10 | TCoR four-move crossover | `platform/tcor/tcor.py`, `scenarios/*`, `verify-tcor.sh` | 566 | 2026-07-31 | Prices fix, cage, transfer and deny for one risk and picks the cheapest. The only place the cage `cost` column is weighed against its benefit. Called only by wargamer and wardley. | compare | off_mission (not a step of the loop; nothing on the composed path calls it) | owner_words ("go deep on the balance sheet", 2026-07-23T15:50) | tested_offline | `platform/tcor/tcor.py:100-179`; `hub/.scratch/ecosystem/review-2026-09-02/evidence/purpose/PURPOSE.md:84-85`; callers `platform/wargamer/wargamer.py:137` |
| 11 | Reference engine install | `platform/engine/{kyverno,flux-operator}/helmrelease.yaml`, `namespaces.yaml`, `up.sh`, `verify-engine.sh` | 235 | 2026-08-20 | Installs Kyverno and flux-operator on the demo cluster. Adopters now declare their own engine in their own repo. | enact | support | assistant | tested_offline (live tail SKIP at run 491) | `hub/talk/captures/_grades.tsv:55` |
| 12 | Engine version table and declaration reader | `platform/engine/engine_table.py`, `kyverno/engine-table.yaml`, `install-kyverno-engines.sh`, `declaration.py` | 422 | 2026-09-26 / 2026-10-03 | Lists two Kyverno versions with checksums; reads an adopter's declared engine. | enact | support | delegated (hub ADR-0033) | tested_offline | `platform/engine/kyverno/engine-table.yaml:1-20` |
| 13 | Currency controller | `platform/currency-controller/currency.py`, `manifests/*`, `up.sh` | 675 | 2026-07-31 (rewritten 2026-09-05) | A one-minute CronJob that moves any pod whose claimed policy version has been retired to `isolated`. The trigger is version retirement, not money. Not in any adopter's `gitops/`. | react | support | assistant (the owner's 2026-07-31 sentence about an application that "falls behind on patching" describes the behaviour, not this controller) | tested_offline | `platform/currency-controller/currency.py:171-242`; `manifests/cronjob.yaml:64`; `_grades.tsv:47` |
| 14 | Currency verify script | `platform/currency-controller/verify-currency.sh` | 596 | 2026-07-31 | Grades the controller against planted pod lists and the served bodies. | evidence | support | assistant | tested_offline | `_grades.tsv:47` |
| 15 | Cloud cage package | `platform/implementations/cloud/{policies/*,crossplane-dials.yaml,render.py,composition.py,provider_schema.py,package.yaml,VERSION,component-definition.json,cloud-rbac.yaml,provider-crds.yaml}` | 554 | 2026-10-03 | The same four rung names applied to Crossplane RDS and S3 custom resources. No reduce number, no provider, no AWS resource. | cage | off_mission | codex ("Prepared by Codex", commit 9ddd6a2) | observed_running (server dry-run on KinD only) | `platform/implementations/cloud/crossplane-dials.yaml:7-11`; `hub/talk/captures/verify_cloud-plane_verify-cloud-plane.out` |
| 16 | Vendored Crossplane CRDs | `platform/implementations/cloud/vendor-crds/*` | 3,511 | 2026-10-03 | Two upstream CRD documents, used as replay schema. | evidence | off_mission | codex | tested_offline | `platform/implementations/cloud/README.md:24-27` |
| 17 | Cloud replay, trigger and tests | `platform/implementations/cloud/{replay,release_check,trigger,test_*}.py`, `verify-cloud-package.sh`, `tests/*` | 747 | 2026-10-03 to 2026-10-22 | Replays fixtures on two Kyverno versions; `trigger.py` checks that a signed step-4 record exists before the cloud plane may be graded. | evidence | off_mission | codex | tested_offline | `_grades.tsv:64` |
| 18 | Conditional-policy test | `platform/policy/verify-conditional.sh`, `tests/conditional/*`, `scenarios/*` | 197 | 2026-07-31 | Tests one "non-root, or root if attested and hardened" rule that lives in `distribution/`. | evidence | support | owner_words ("be a privilaged container under certain circumstances, e.g. if your container is signed or has some attestation", 2026-07-31T09:30Z) | tested_offline | `hub/.scratch/drift-review-2026-08-27/evidence/AMBITION_TIMELINE.json:1005`; `_grades.tsv:68` |
| 19 | Break-glass access bands | `platform/break-glass/break-glass.py`, `assurance-bands.json`, `scenarios/*`, `verify-break-glass.sh` | 423 | 2026-07-31 | A second money-to-band selector for human access: carried loss against three cutoffs picks OIDC, passkey or attested device. Offline fixture; enforces nothing. | cage | duplicate (second money-to-rung selector; the loop's is `cage.select_tier`) | assistant | tested_offline | `platform/break-glass/break-glass.py:73-86`; `_grades.tsv:34` |
| 20 | Break-glass band tests | `platform/break-glass/test_*.py` | 422 | 2026-10-17 to 2026-10-21 | Unit tests for band validation and the party-declared bands reader. | evidence | duplicate (tests a duplicate) | codex (by date and style; not stated in a commit) | unknown | commits e845469, c7e65e7 |
| 21 | Recovery-expense ledger | `platform/recovery-expense/{collection.py,collection.schema.json,pilot-2027.json,test_collection.py}` | 1,176 | 2026-10-23 | Hash-chained ledger for real 2027 incident recovery costs, to score a forecast feed. Explicitly excluded from prices; holds no records. | none | off_mission | codex (by date and style) | written_never_run | `platform/recovery-expense/pilot-2027.json:26-28`; `README.md` last two paragraphs |
| 22 | Party artefact schema and checker | `platform/party/{party_artefact.py,schema.json,verify-party-artefact.sh,assurance_bands.py,test_publisher_reliability.py}` | 1,635 | 2026-08-25 (two files October) | Validates a party's `party.yaml`: roles, pins, size, `appetite.tolerance`, floor, publish capability. The appetite part is `_appetite_errors` (about 95 lines); the rest is distribution and publishing checks. | tolerance | support | delegated (hub ADR-0019, ADR-0021) | tested_offline | `platform/party/party_artefact.py:368-463`; `_grades.tsv:67` |
| 23 | Pin-content rule | `platform/party/pin_content.py` | 211 | 2026-09-04 | Checks that a pinned tag's tree really contains the section the pin is used for. | evidence | support | assistant | unknown | `platform/party/pin_content.py:1-12` |
| 24 | Platform's own party declaration | `platform/party.yaml` | 127 | 2026-08-28 | Declares the platform's own GBP 10,000 tolerance and what it publishes. 101 of 127 lines are comment or blank. | tolerance | support | delegated | tested_offline | `platform/party.yaml:108-109` |
| 25 | Prose | nine `README.md` files, `platform/README.md`, `CONTEXT.md`, `docs/adr/0001-*.md` | 1,079 | 2026-07-31 to 2026-10-18 | Explanations. `CONTEXT.md` and the one ADR concern insurer quote conditions, not this area's code. | none | support | assistant / codex | unknown | `platform/CONTEXT.md:1-15` |

Component lines sum to 16,993; files to 106.

## 1. The money formula as implemented

One priced line (`platform/graded/cage.py:363-364`, called from `platform/compose/composition.py:3812,3831`):

```
uncaged = mean over 10,000 simulated years of
          sum over round(PERT(lef)) events of sum over sources of PERT(lm)
```

- `lef` = (min, mode, max) loss events per year. `lm` = (min, mode, max) money per event, or a list of such triples added within one event, or a lognormal-GPD spec. `platform/fair/fair.py:133-175`.
- beta-PERT with lambda 4 (`fair.py:56,96-103`). Iterations 10,000, seed 42 (`fair.py:54-55`).
- The yearly event count is rounded to an integer (`fair.py:160`), so any frequency below 0.5 simulates to exactly zero. A closed form `expected_ale` exists for that case (`fair.py:111-130`).
- Other outputs: VaR95, TVaR, `carried = TVaR + 0.06 x (TVaR - ALE)` (`fair.py:57,211-225`). The cage path uses ALE only.
- For a regulator line the amount is then scaled by the share of that regime's controls the adopter has not implemented (`composition.py:3848-3858`).
- Unit: the publisher's currency per year, converted to the party's reporting currency through an FX feed.

Three different money figures meet three different thresholds, and they are not the same quantity:

| consumer | money figure | threshold |
|---|---|---|
| `cage.select_tier` | ALE x (1 - reduce) | `appetite.tolerance` |
| `enforce.decide` | ALE_warn - ALE_deny | `appetite.tolerance` |
| `break-glass.decide` | carried (TVaR + load) | `assurance_bands` (three cutoffs) |

Inputs on the served path, read from each adopter's `composed/evidence.json` `prices[]`:

| input | value seen | source | measured, published or assumed |
|---|---|---|---|
| lef, regulator fine | [1, 2, 4] for every adopter | `ico/schema/to_fair_scenario.py:69` `DEFAULT_WARN_LEF` | assumed. The entry says "warn/deny lef are editorial (schema doesn't carry frequency)" |
| lm, regulator fine | scaled to turnover | ICO public fines x the party's declared turnover | published fines; declared turnover |
| lef and lm, threat register | [2,4,9] driftwood, [4,9,20] tuppence, [1,2,5] ludlow | `feeds` repo | assumed. The entry says "editorial midpoint COULD NOT LOOK" |
| lef, CVE | EPSS-derived, tuppence only | CISA KEV, FIRST EPSS | published. Driftwood and ludlow have no priced CVE |
| lef, EOL | ramp since end-of-life date, ludlow only | endoflife.date | published date, assumed ramp |
| lm, twin forward-intel | adopter twin | adopter repo | modelled; lef borrowed from the threat register |
| turnover | GBP 86m, GBP 862m, USD 197.6bn | each adopter's `party.yaml` | declared; a comparable real firm's filing for a fictional party |
| tolerance | GBP 40,000 / 15,000 / 5,000 / 10,000 | each party's `party.yaml` | declared. Same numbers as the 2026-07-31 fixture `risk/appetite.json` (commit 7a36bf7) |
| reduce per rung | 0.30 / 0.70 / 0.92 / 0.98 | `platform/graded/cage.py:82-111` | assumed |

Nothing in the formula is measured from the running system. The composed header says so itself: the total is "an ordinal, auditable comparison under one perspective; not an expected annual loss ... not as a number to reserve against" (`driftwood/composed/HEADER.yaml:1371-1372`).

## 2. The cage ladder

Source of truth `platform/graded/cage.py:82-127`; fields set by `platform/graded/policies/cage-tier.yaml:225-304` and `cage-netpol.yaml:106-134`. Scope: only pods carrying a `policy-as-versioned.dev/policy-version` label. The rung is read from the pod's Namespace label `posture.acme.io/tier`; a missing or unknown value gives `isolated` (`cage-tier.yaml:188-218`).

Written at every rung: labels `posture.acme.io/caged=true` and `posture.acme.io/tier`; `spec.hostNetwork`, `hostPID`, `hostIPC` = false; `preemptionPolicy: Never`; every container `allowPrivilegeEscalation: false`, `privileged: false`; limits are the minimum of the pod's own and the rung's.

| rung | reduce | cost GBP/yr | cpu / memory limit | priorityClassName / priority | readOnlyRootFilesystem, runAsNonRoot, capabilities drop ALL | WAF sidecar | NetworkPolicy |
|---|---|---|---|---|---|---|---|
| baseline | 0.30 | 500 | 500m / 256Mi | cage-baseline / -10 | not forced (kept if the pod declared them) | none | none generated |
| restricted | 0.70 | 2,000 | 250m / 128Mi | cage-restricted / -100 | forced | 100m / 128Mi | ingress from own namespace; egress UDP 53 to kube-system |
| quarantine | 0.92 | 6,000 | 100m / 64Mi | cage-quarantine / -1000 | forced | 250m / 256Mi | identical to restricted |
| isolated | 0.98 | 15,000 | 100m / 64Mi | cage-isolated / -10000 | forced | 250m / 256Mi | Ingress and Egress with no rules |
| infra | 0 | 0 | none | system-cluster-critical | none | none | not a rung; no policy body reads it (`cage-tier.yaml:39-48`) |

Does any number say how much exposure a rung removes? Yes, `reduce`. Where it comes from: the table's own comment, "They are the PLATFORM's, self-declared, evidenced by nothing but this comment" and "calibration knobs" (`cage.py:68-72`). The first three values and all three original costs are in the first commit of the file (7a36bf7, 2026-07-31); 0.98 and 15,000 were added with the `isolated` rung on 2026-08-28.

Served bodies checked: the rung-to-dial table is identical in the v5.0.0, v6.0.0 and v7.0.0 `cage-tier` bodies in each adopter's `composed/policies/` (driftwood and tuppence serve all three, ludlow v7.0.0 only), apart from version-suffixed PriorityClass names. v7.0.0 equals the authoring copy. v5.0.0 reads the tier from any Namespace, governed or not, and lacks the pod-level `runAsNonRoot` fallback; v5.0.0 and v6.0.0 lack one `string()` cast.

Things the table claims that the enacted fields do not deliver:

- The WAF sidecar image is `ghcr.io/acme/coraza-waf:cage`, which is a busybox running `sleep infinity` (`platform/graded/waf-placeholder/Dockerfile:14-19`). "light" and "heavy" WAF differ only in the sidecar's resource limits.
- restricted and quarantine have identical network reach (`cage-netpol.yaml:19-23`). They differ in cpu and memory limits, the WAF sidecar's limits and the priority integer, and that difference carries 22 points of reduction.
- initContainers are not hardened by `cage-tier` (`platform/distribution/cage_body.py:17-21`); a hostPath volume cannot be removed (`cage-tier.yaml:100-104`).
- `cost` is never used on the composed path. Only `tcor.py` and the wargamer read it.

A second table, for the "twin agent" (`cage.py:155-206`), uses the same rung names with dials "what may it write". Its reduce is derived from which misuse paths a rung closes rather than typed, and the priced amounts are GBP 0.0002, 18.70 and 2.98 for the three adopters.

A third table, for cloud resources (`platform/implementations/cloud/crossplane-dials.yaml:7-11`), has no reduce number at all, and its `isolated` equals `quarantine`.

The adopter's own twin publishes a different set of numbers for the same four rungs: reductions 0.05 / 0.30 / 0.65 / 0.90 and costs 8,000 / 20,000 / 42,000 / 95,000, each at evidence grade 5 (`driftwood/twin/orgs/driftwood/responses/run-the-checkout-at-*.yaml:6-14`). Grade 5 is the grade that may never price. Composition uses the platform table.

## 3. How a tier is selected from money and appetite

It is a calculation over a four-row table, not a band table (`platform/graded/cage.py:334-348`):

```
for tier in [baseline, restricted, quarantine, isolated]:
    if ALE * (1 - reduce[tier]) <= tolerance: pick it and stop
else: isolated
then: never looser than the party's overlay.floor
```

- Tolerance is one number per party, `appetite.tolerance` on its own `party.yaml`, read by `platform/risk/enforce.py:81-98`.
- Selection is per priced line. The Namespace then takes the strictest line (adopter `selection-policy/selection_policy.py`, `select_party`). The twin line is selected by the adopter's own copy of the same rule; the three copies differ only in the party's name.
- A ceiling follows from the table: with reduce at most 0.98, no rung fits when ALE exceeds 50 x tolerance. That is GBP 2.0m for driftwood, GBP 750k for tuppence, GBP 250k for ludlow.

What the served artefacts show (composed 2026-10-27):

| adopter | tolerance | uncaged lines (GBP/yr) | tier each line gets | residual total at isolated | verdict |
|---|---|---|---|---|---|
| driftwood | 40,000 | fine 1,787,177; threat 19,559; twin 758; CVE unpriced | all isolated | 36,150 | `breaches_band: null`, because the CVE line is unpriced |
| tuppence | 15,000 | fine 17,907,951; twin 84,198,283; CVE 437,107; threat 326,139 | all isolated | 2,057,390 | `breaches_band: true` |
| ludlow | 5,000 | fine 3,071,757,724; twin 13,435,901; EOL 787,228; threat 318,230; CVE unpriced | all isolated | 61,725,982 | `breaches_band: null` |

Sources: `driftwood/composed/HEADER.yaml:1373-1393`, `tuppence/composed/HEADER.yaml:1340-1348`, `ludlow/composed/HEADER.yaml:1401-1409`, and each `composed/evidence.json` `prices[]`.

- Lines whose residual fits the tolerance at `isolated`: driftwood 3 of 3, tuppence 2 of 4 (threat register and CVE fit; the fine and the twin line do not), ludlow 0 of 4.
- Driftwood's threat line (19,559) and twin line (758) would select `baseline` on price, as would all three twin-agent lines. They show `isolated` because of the floor. So on real inputs the price selects a rung other than the bottom only for those small lines, and the floor overrides it.
- Driftwood's fine line fits at isolated only because reduce is 0.98. At the adopter's own 0.90 the residual would be GBP 178,718, 4.5 times the tolerance.
- A breach is "priced and shown, never denied" (`platform/compose/composition.py:5197-5199`). Nothing follows from `breaches_band: true`.

## 4. Does tightening the cage change the money figure?

- The uncaged amount: no. It depends on feeds, turnover and implemented controls only.
- The residual: yes, by arithmetic. `residual = amount x (1 - reduce[tier])` (`cage.py:313-315`), summed into `selected_tier_residual_total` (`composition.py:5214-5222`). The composition labels this "selection evidence, not an enacted Namespace tier; platform reductions are self-declared calibration, not measured effectiveness" (`composition.py:5176`).
- Nothing reads the cluster to learn which rung a workload is really on, or whether a rung reduced anything, before computing money.
- One real feedback exists outside the cage: marking a regulator's control as implemented removes its share from the fine line (`composition.py:3848-3858`).

Ratchet history: each adopter's `gitops/apps/namespace.yaml` has three commits, and the tier line was written once, by hand, on 2026-08-28 (driftwood 348b97c, tuppence b257966, ludlow 85cc202). It has not changed since, in either direction. The recorded proof that a price crossing the band opens a tightening PR uses "a SYNTHETIC residual ... not driftwood's real priced position" on throwaway copies with "nothing opened" (`hub/talk/captures/verify_e2e_verify-e2e-step3-price-crosses-band-pr-opens.out`).

## 5. Relation to the hub twin's pricing

Different jobs, joined by one JSON payload.

- `hub/twin/pricing.py` (514 lines, born 2026-08-07): `price = a perspective's declared valuation of a component x propagated influence along a graded causal path`. It has no frequency and no severity slot, and it refuses to price below an evidence grade (`hub/twin/pricing.py:8-18,199-324`). It also grants mitigation credit only when the claim is graded and the enactment is corroborated (`pricing.py:327-407`).
- `hub/twin/valuation.py` (66 lines, born 2026-10-03): checks a declared valuation against the signed turnover and converts currency.
- `platform/fair/fair.py`: annualises a (frequency, magnitude) pair. The twin's output enters as `lm`; frequency is borrowed from the threat register (`composition.py:4210-4239`).

Real duplication around this seam:

1. Two reduction tables for the same rungs: `platform/graded/cage.py:82-111` and each adopter twin's `responses/*.yaml`. A hub check (`verify/pound-seam`) exists to grade their disagreement.
2. Two mitigation rules: the twin refuses credit for an ungraded claim; the platform grants 30 to 98% on an unevidenced constant. The stricter rule is not the one that prices the cage.
3. `select_tier` exists three ways: `cage.py:334`, three adopter `selection_policy.py` files (291 lines each, differing in two lines), and `platform/wargamer`'s party fold. Hub checks compare them.
4. `fair.py` and `severity.py` are vendored byte-identical in `nist/publisher-reliability/vendor/fair/`.
5. Three money-to-threshold comparators in this area alone (section 1).

## 6. Smallest subset that prices an adopter and selects a tier

Whole files, as they stand: `fair/fair.py` (436) + `fair/severity.py` (80) + `risk/enforce.py` (223) + `graded/cage.py` (668) = 1,407 lines. Run as `cage.py select <scenario.json> --org <party>`. Needs PyYAML, one scenario JSON with `lef` and `lm`, and one `party.yaml` with `appetite.tolerance`.

Live code inside those files, without selfchecks, CLI, the twin-agent table and OSCAL: about 310 lines (`fair.py:96-227` less `sum_prices`; `enforce.py:57-98`; `cage.py:82-131,294-383`).

To put the selected rung on a cluster add `graded/policies/` (502 lines, 202 non-comment).

Limit: that subset prices one scenario somebody hands it. Turning feeds into scenarios for a real adopter is `platform/compose/composition.py` (10,142 lines) plus converters in the `ico` and `feeds` repos, all outside this area.

## What the loop would lose if this area vanished

- Q: the only code that turns a frequency and a magnitude into money (component 1).
- T: the reader for the declared tolerance (42 lines of component 3).
- C and R: the only comparison of money to tolerance and the only rung table (140 lines of component 5).
- The cage itself: the admission mutation and the NetworkPolicies (component 6).
- X, partly: the one in-cluster controller that tightens after admission, on version retirement (component 13).

It would lose nothing of the loop if components 4, 9, 10, 15, 16, 17, 19, 20 and 21 vanished (7,723 lines, 45% of the area). Components 2, 7, 8, 14, 18, 22, 23 are checks and fixtures around the kernel (4,823 lines).

## The simplest thing that would do this area's loop job

One Python file and one YAML file, about 300 lines together.

`loop.py`, about 150 lines:

- `ale(lef, lm)`: closed-form PERT mean x PERT mean (the existing `expected_ale`, 20 lines), or the existing 40-line simulation when a tail figure is wanted.
- `RUNGS`: a four-row table of `name, reduce, basis`, where `basis` must name a measurement or say "assumed".
- `exposure(lines, rung) = sum(ale(line) * (1 - reduce[rung]))` over all the party's lines, so the comparison is against the aggregate the tolerance is declared for.
- `next_rung(exposure, tolerance, current)`: one notch tighter if over, else hold. Returns "bottom rung, still over by GBP n" as an explicit outcome.
- `tolerance(party_yaml)`: the existing 15-line reader.

`cage.yaml`, about 150 lines: the existing `cage-tier` mutation (95 non-comment lines) and four PriorityClasses, with the three NetworkPolicies written as static manifests per governed Namespace instead of a GeneratingPolicy.

What this drops: the second and third comparators, TCoR, the twin-agent and cloud tables, per-line selection followed by a strictest-line fold, the floor (a floor of `isolated` makes selection moot), and the separate selfcheck harnesses.

## Surprises

1. The loop does not converge and nothing reacts. At the bottom rung tuppence is 137 times over its tolerance and ludlow about 12,000 times over, on the estate's own signed artefacts. The only verdict printed is tuppence's `breaches_band: true`.
2. Tolerance and exposure are not on the same scale. Ludlow declares GBP 5,000 tolerance against a turnover of USD 197.6bn and a single fine line of GBP 3.07bn a year. The tolerances are the 2026-07-31 fixture values; tuppence's and ludlow's turnovers were later replaced with comparable real firms' filings (ticket 144, per the comments in their `party.yaml`).
3. The floor makes the selector decorative. All three adopters declare `floor: isolated`, so `select_tier` can only ever return `isolated` for them.
4. The ratchet has not moved on real data since 2026-08-28. One hand-written label per adopter that day; the only recorded movement since is a synthetic dry run.
5. Whether driftwood is inside tolerance rests on one unevidenced constant. 0.98 gives GBP 35,744; the adopter's own published 0.90 gives GBP 178,718.
6. The WAF that separates the rungs is `sleep infinity`.
7. restricted and quarantine enact the same network reach, yet are priced 22 points of reduction apart.
8. Per-line selection hid an aggregate breach. The code comment records driftwood at GBP 87,387 against GBP 40,000 "that no signed artefact stated" (`composition.py:5186-5190`).
9. `platform/policy/README.md:28,64` still says "Deny — bottom rung, it does not run", which the code retired on 2026-08-28. `platform/README.md:55-56` says the platform's appetite sits "next to `size`"; its `party.yaml` declares no size.
10. `platform/CONTEXT.md` and `platform/docs/adr/0001` are about insurer quote conditions. Neither mentions the money formula or the ladder.
11. The frequency rounding at `fair.py:160` makes any event rarer than once in two years simulate to zero. The twin-agent line was priced through a separate closed form to get round it.
12. The currency controller, described as "the estate's only post-admission re-caging mechanism" (`platform/party.yaml:78`), is in no adopter's `gitops/` and its live tail was a SKIP at truth run 491.

## Could not determine

- Whether the October components other than `implementations/cloud` were written by Codex. Every commit carries the owner's name; only commit 9ddd6a2 and two `codex/` branch merges say so.
- Whether any pod has run on a cluster at `baseline`, `restricted` or `quarantine` since the Namespaces were set to `isolated`. The step-4 capture observes the bottom rung only; `verify-graded.sh`'s live tail was a SKIP at run 491.
- Whether the recovery-expense and break-glass unit tests pass. No capture of them was found and no test was run in this review.
- A dated owner quotation asking for FAIR, beta-PERT, TVaR, the four rung names, the reduce values, the three tolerance values, or a comparison of exposure against appetite that selects the rung. None was found. The owner's 2026-09-02 sentence about a mutating admission controller (`hub/NORTH-STAR.md:54`) ratifies the cage after it was built.
