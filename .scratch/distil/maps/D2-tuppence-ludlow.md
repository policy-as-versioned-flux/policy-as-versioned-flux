# D2 map: the adopters tuppence and ludlow, compared with driftwood

Snapshot: FRESH clones of 2026-11-14. Area = tuppence (254 files, 48,228 lines, 14.6 MB) + ludlow (205 files, 43,854 lines, 6.9 MB) = 459 files, 92,082 lines. Driftwood (233 files, 50,676 lines) is a comparator only. Line counts are `wc -l` newline counts; JSONL lines are enormous (tuppence `drift/oscal-samples.jsonl` is 10.7 MB in 35 lines), so lines understate bytes there. Component lines below are tuppence + ludlow and sum to 92,082.

## Summary

- Loop finding: all three adopters sit at the tightest rung, `isolated`. The Namespace label was written once, on 2026-08-28 (tuppence b257966, ludlow 85cc202, driftwood 348b97c), and has never changed (`git log -G` on `gitops/apps/namespace.yaml`). The ratchet has never moved a notch in any adopter.
- The owner-adopted `overlay.floor: isolated` (2026-10-23) changes nothing in tuppence or ludlow. Each line's `floor_change` residual_delta is 0.0, and every line already fails closed to `isolated` because no tier fits under tolerance (tuppence/composed/evidence.json `floor_change`, ludlow same).
- Only tuppence gets a compare verdict, and it is a breach with no notch left. At the tightest rung the residual is £2,057,389.61 against a £15,000 tolerance (tuppence/composed/HEADER.yaml:1343-1347). Ludlow reads £61,725,981.64 against £5,000 but gives `breaches_band: null` because the cve line is unpriced (ludlow/composed/HEADER.yaml:1404-1409). Driftwood reads £36,149.88 against £40,000, also no verdict.
- Real exposure and real enactment, but not a converging loop. The cage is enacted and observed daily (7 of 7 facts true in the latest sample of all three, runs through 2026-11-13). Per-rung effectiveness is "self-declared calibration, not measured effectiveness" (evidence.json `floor_change.limit`).
- Only about 4.9% of the area is kernel (4,521 lines). 36% is vendored feed copies of other repos (33,593 lines). About 5.9% is three separately written adopter-gate scripts and their relatives.
- 76 files / 19,385 lines are byte-identical across all three adopters, and 13,903 of those lines are one vendored `cve/v3/feed.json`.
- Per-adopter hand-authored facts are about 600 lines (party.yaml, twin overlay, scenario, workload manifest); most of that is itself boilerplate.

## Components

Columns: lines = tuppence + ludlow (T / L in the "what it does" cell where they differ; driftwood noted as D). Origin and status rules: see "Method and caveats" at the end.

| name | paths | lines | born | what it does | loop role | necessity | origin | status | cite |
|---|---|---|---|---|---|---|---|---|---|
| C01 party.yaml declaration | `party.yaml` | 180 (89/91; D 133) | 2026-08-25 | The one per-adopter declaration: size, `appetite.tolerance`, three assurance bands, `overlay.floor`, parents (`inherits`), `workload_cages`, `publishes`. | tolerance | kernel | assistant (July fixture copied from platform/risk/appetite.json; bands/floor say "owner-adopted 2026-10-23" in the file, no verbatim quote found) | observed_running | tuppence/party.yaml:20-34,60-70; ludlow/party.yaml:23-35,62-72 |
| C02 twin overlay declarations | `twin/orgs/<name>/**` (22 files each) | 767 (378/389; D 402) | 2026-09-04 | The org's own loss model: one monetised component (fee income) from a grade-3 comparable filing, one grade-5 unpriced component, 6 scenarios, 4 response files (one per rung, each only the tier name and reduce/cost differ), people, edges. | quantify | kernel | assistant | tested_offline | tuppence/twin/orgs/tuppence/perspectives/tuppence.yaml:1-33; responses/run-the-payments-api-at-quarantine.yaml:1-23 |
| C03 twin vendored world | `twin/world/**` (30 files) | 334 (167/167, byte-identical to D) | 2026-09-04 | Byte copy of the hub twin's shared world layer, so an overlay in the adopter repo can resolve `world_ref`. | quantify | support | assistant | tested_offline | tuppence/twin/VENDORED.md:1-25 |
| C04 twin emitter and pricing | `twin/emit-forward-intel.py`, `scenario_pricing.py`, `signals.yaml`, `ladder.yaml`, `currency.yaml`, `PIN.yaml`, `VENDORED.md`, `forward-intel/**` | 2,264 (1,108/1,156) | 2026-09-04 | Renders the adopter's forward-intel feed from the overlay, deterministically, or refuses and names the missing instrument. It is the largest price line (tuppence £84.2M of £102.9M). | quantify | support | assistant | observed_running (sweep recorded "byte-identical" renders 2026-10-21/22) | tuppence/twin/emit-forward-intel.py:1-28; tuppence/observations/twin-sweep.jsonl (last line) |
| C05 workload loss inputs | `scenarios/*.json`, `inventory/**`, `.github/scripts/served-workloads.py` | 2,135 (315/1,820; D 6,084) | 2026-09-06 (scenario 2026-10-23, inventory 2026-10-04) | Per-workload recovery scenario (£100/h x 2 engineers x 2-24 h; LEF 0.1-2; LM 400-4,800) plus Trivy scan output of the served images (feeds the CVE price). | quantify | support | codex (epoch Oct; unverifiable) | observed_running (bot inventory commits to 2026-10-27) | tuppence/scenarios/workload-ledger-recovery.json:1-30; tuppence/inventory/images.json |
| C06 vendored feeds | `composed/feeds/**` (cve, threat-register, recovery-expense, penalty-schema; L adds eol) | 33,593 (16,489/17,104; D 16,710) | 2026-09-24 | Byte copies of other repos' signed feed releases (feeds, ico) so composition can run offline; `cve/v3/feed.json` alone is 13,903 lines identical in all three. | quantify | duplicate (same bytes live in feeds and ico repos, pinned by tag in `gitops/flux-system/gotk-sync-*.yaml`) | assistant | observed_running | tuppence/composed/HEADER.yaml:1291-1327 (shas); tuppence/composed/feeds/feeds/cve/v3/cve/v3/feed.json |
| C07 composed HEADER.yaml | `composed/HEADER.yaml` | 2,899 (1,431/1,468) | 2026-08-25 | The compare output: parents, selected tier, exposure and aggregate vs tolerance. The compare itself is lines 1329-1400 (72 lines, 5%); the rest is NIST control lists (`holes` 285 lines, `selected-controls` 288, `comparison-inputs` 663). | compare | support | assistant | observed_running (bot updates to 2026-10-27) | tuppence/composed/HEADER.yaml:1329-1363; ludlow/composed/HEADER.yaml:1389-1425 |
| C08 composed evidence.json | `composed/evidence.json` | 8,810 (4,173/4,637; D 6,615) | 2026-08-25 | Machine record of the composition. Tuppence: `holes` 2,558 lines, `prices` 590, `members` 308, `cages` 140; per-line tiers, `floor_change` counterfactual. | evidence | support | assistant | observed_running | tuppence/composed/evidence.json (keys outcome..cloud; `floor_change`) |
| C09 composed HANDBOOK and floor-change | `composed/HANDBOOK.md`, `composed/floor-change.json` | 533 | 2026-09-06 | Rendered prose handbook and the floor-only counterfactual record. | presentation | ceremony | assistant | observed_running | tuppence/composed/HANDBOOK.md; tuppence/composed/floor-change.json |
| C10 cage policy v7 and guards | `composed/policies/v7.0.0/*`, `bottom-rung-*`, `governed-namespace-*`, `orphan-*`, `composed/kustomization.yaml` (17 files each) | 1,020 (510/510, identical to D) | 2026-08-25 | The cage itself: four rung policies (16 lines each: baseline, restricted, quarantine, isolated), `cage-tier` mutating policy (43 lines), netpol (45), nonroot, guards. | cage | kernel | assistant | observed_running (facts 4, 6, 7 true, daily) | tuppence/composed/policies/v7.0.0/cage-tier.yaml; tuppence/drift/samples.jsonl (last record) |
| C11 cage policy v5 v6 window versions | `composed/policies/v5.0.0/*`, `v6.0.0/*` (tuppence + driftwood only; ludlow retired them) | 526 (T only) | 2026-09-23 | Older served versions of the same cage policies, kept while platform's window still lists them. | cage | ceremony | assistant | observed_running | tuppence/accepted-majors/platform-7.0.0.yaml; ludlow/implementation-retirements/platform.yaml:12-20 |
| C12 tuppence cloud datastore lane | `composed/cloud*/**`, `composed/cloud-crds/**` (4,295 lines of vendored upstream RDS/S3 CRDs), `gitops/cloud/**`, `tests/test_cloud_*.py`, `composed/CLOUD-PARENT.json` | 5,140 (T only) | 2026-10-04 | Prepared claims, guards and OSCAL mapping for an RDS and an S3 datastore. Its own README says "This remains opt-in and unactivated"; no provider or credentials. | cage | off_mission | delegated (ADR-0025 era, tickets 151-156 per hub map; no owner quote) | tested_offline | tuppence/gitops/cloud/README.md:14 |
| C13 tuppence reset flagship | `reset/**` | 691 (T only) | 2026-07-31 | Istio/OpenBao/SPIRE demo: a caller loses reach and its secret when its SVID posture is not the current policy version. A second cage mechanism that is not on the ladder. | cage | off_mission | assistant (README names tickets 08, 14-17) | unknown | tuppence/reset/README.md:1-10 |
| C14 selection policy | `selection-policy/**` (4 files each) | 750 (375/375, identical to D after names) | 2026-10-04 (in this repo; ADR-0021/22 earlier) | The ratchet rule. `select()`: loosest tier whose residual is <= tolerance, else fail closed to `isolated`, then clamp up to floor. `select_party()`: strictest line, tighten-only. About 25 lines of logic in 291. | ratchet | kernel | assistant | tested_offline (selfcheck; HEADER records `selection-policy: 1.1.0`) | tuppence/selection-policy/selection_policy.py:83-140,143-197; tuppence/composed/HEADER.yaml:1328 |
| C15 gitops enact wiring | `gitops/flux-system/*`, `gitops/platform/*`, `gitops/composed/*`, `gitops/engine/kyverno.yaml`, `engine_declaration.py` + test | 1,409 (709/700) | 2026-07-31 | Flux GitRepository pins (tag + commit, gitsign identity), the ResourceSet that installs `composed/`, and the engine declaration. | enact | kernel | assistant | observed_running (facts 1-3 true daily) | tuppence/gitops/platform/platform-pin.yaml:28-34; tuppence/gitops/composed/composed-set.yaml |
| C16 gitops apps and namespace tier | `gitops/apps/*`, `deploy/pod.yaml` | 395 (203/192) | 2026-07-31 | The thing enacted: Namespace carries `posture.acme.io/tier: "isolated"`; the served workload (ledger / reports); three configmap mirrors (tolerance, NIST pin, version). | enact | kernel | assistant | observed_running | tuppence/gitops/apps/namespace.yaml:28; tuppence/gitops/apps/risk-appetite-configmap.yaml:1-19 |
| C17 drift sampler | `drift/**`, `drift-sample.yml`, `verify-cage-probe.sh`, `verify-reconcile.sh`, `scripts/render_composed.py`, `tests/test_{composed_reach,fact_four_compare,inventory_*}.py`, `.github/tests/test_probe_cleanup.py` | 12,770 (6,659/6,111; D 7,498) | 2026-07-31 (sampler 2026-08-29) | Daily ephemeral KinD cluster from the real remotes; checks seven facts (pin, signature, applied revision, byte-equal render, inventory, bottom-rung workload runs, it reaches nothing); appends signed observations via PR. | evidence | support | assistant | observed_running (daily merged PRs 2026-10-20 to 2026-11-13; 204/192 records) | tuppence/drift/five-facts.py:1-40; tuppence/.github/workflows/drift-sample.yml:1-30 |
| C18 adopter gate and retirement | T: `adopter-gate.py` 1,245, `scripts/verify-adopter-gate.sh` 937, `verify-identity-regexp.sh` 196, 3 helper scripts 169, `accepted-majors/*`. L: `adopter_gate.py` 1,691, root `verify-adopter-gate.sh` 855, `verify-certificate-identity-regexp.sh` 81, `implementation-retirements/platform.yaml`, `test_consumer_retirement_gate.py` | 5,443 (2,577/2,866; D 2,200) | 2026-08-22 | Gate on the Renovate PR that moves the platform pin: verify the publisher's signed evidence, fold its computed semver bump, refuse an unaccepted major. Written three times (1,245 / 1,691 / 1,514 lines), none touches money. | ceremony | ceremony | assistant (accepted-majors cites the owner's 2026-10-03 delegation: "you tell me, you control them all, you don't need me to answer") | tested_offline | tuppence/.github/scripts/adopter-gate.py:1-30; ludlow/.github/scripts/adopter_gate.py:1-30; tuppence/accepted-majors/platform-7.0.0.yaml:1-9 |
| C19 twin sweep clock | `twin-sweep.yml`, `twin-sweep.py`, `.github/requirements/*`, `observations/twin-sweep.jsonl`, `test_twin_sweep_moved.py`, `twin/verify-twin-sweep-moved.sh`, `tests/test_twin_clock.py` | 3,164 (1,553/1,611; D 1,254) | 2026-09-10 | Daily check that the emitter's render is unchanged; two jobs (read-only, writer). It re-renders the same overlay; it does not fetch new world data. | react | support | assistant (ADR-0024) | observed_running to 2026-10-22; after that could not determine | tuppence/.github/workflows/twin-sweep.yml:1-30,38-40; tuppence/observations/twin-sweep.jsonl |
| C20 twin overlay verifiers | `verify-twin-overlay.sh`, `twin/verify-twin-scenarios.sh`, `tests/test_scenario_pricing.py`, `.github/tests/test_twin_tag.py` | 1,627 (813/814) | 2026-09-04 | Offline checks that the overlay, ladder, currency and tag agree. | evidence | ceremony | assistant | tested_offline | tuppence/twin/ladder.yaml:1-22 |
| C21 propose-tier ratchet proposer | `propose-tier.yml`, `test_proposal_signing.py` | 1,058 (525/533) | 2026-08-25 | Daily job that would open a PR editing the Namespace tier from `composed/evidence.json`. No tier-changing PR appears in history of any adopter; at the top rung the tighten-only rule leaves nothing to propose. | ratchet | support | assistant | tested_offline (no observed tier PR) | tuppence/.github/workflows/propose-tier.yml:1-30; tuppence/selection-policy/selection_policy.py:143-197 |
| C22 shift-left PR gate | `shift-left.yml`, `render-evidence-comment.py` (T only), `test_party_validator_route.py` | 1,740 (1,093/647) | 2026-08-21 | PR check: platform ci-check plus composition verify, then a signed JSON attestation posted as a PR comment. | evidence | ceremony | assistant | tested_offline | tuppence/.github/workflows/shift-left.yml:1-30 |
| C23 compiler tools runner | `platform-tools.py`, `read-pins.py`, `verify-pinned-checkouts.py`, `platform-tools` action, `platform-tools-pin.yaml`, `tests/test_platform_tools.py` | 952 (482/470) | 2026-09-04 | Thin wrapper that fetches platform's tools tag (v6.3.0), checks commit and signing identity, then runs platform's `compose` and `verify`. The compare and tier arithmetic live in platform, not here. | compare | support | assistant | observed_running | tuppence/.github/platform-tools-pin.yaml:1-12; tuppence/README.md:11-45 |
| C24 release and signing | `release.yml`, `cut-release.yml`, `install-gitsign`, `trusted_root.json`, 2 tests | 1,122 (560/562) | 2026-08-21 | Signs the adopter's own tags (gitsign, Rekor) so composed artefacts are authentic. | evidence | support | assistant | observed_running | tuppence/.github/workflows/cut-release.yml; tuppence/.github/scripts/trusted_root.json |
| C25 renovate bumps | `renovate.json`, `renovate-run.yml`, `complete-feed-bump.sh`, 1 test | 733 (373/360; D 577) | 2026-08-21 | Daily Renovate run proposing pin bumps (the only automated re-price trigger). 4 `renovate/*` branches exist on each; zero merged Renovate PRs in `git log --merges`; recent pin moves are hand PRs. | react | support | assistant (ADR-0024) | observed_running (branches opened, e.g. 3ee6521 2026-10-23), never merged | tuppence/.github/workflows/renovate-run.yml:1-25 |
| C26 observation delivery | `observation-delivery.yml`, `.github/rulesets/*`, `test_observation_delivery.py` | 686 (343/343) | 2026-08-28 | Delivers clock observations through reviewed unique refs and a ruleset lane. | ceremony | ceremony | codex (epoch Oct 17; unverifiable) | observed_running (41 / 37 observation PRs merged) | tuppence/.github/workflows/observation-delivery.yml; tuppence/.github/rulesets/README.md |
| C27 local cluster scaffolding | `scripts/{up,reset,lib}.sh`, `kind/*`, `git-server/*`, `tests/test_apps_dependencies.py` | 716 (358/358) | 2026-07-31 | Brings up a local KinD cluster with an in-cluster git server. Per drift-sample.yml it is not what the daily sample uses. | enact | support | assistant | unknown | tuppence/.github/workflows/drift-sample.yml:14-20 |
| C28 repo boilerplate | `LICENSE`, `README.md`, `.gitignore` | 625 (311/314) | 2026-07-31 | Licence and a README that mostly describes the tools runner and twin sweep, not the loop. | none | support | assistant | observed_running | tuppence/README.md:11-45 |

Lines by necessity (T+L): kernel 4,521 (4.9%); support 37,582; duplicate 33,593; ceremony 10,555; off_mission 5,831. Total 92,082.

## Question 1. What is identical across the three adopters

Measured by SHA-1 and by whitespace-exact line counts (`diff -rq -x .git`: tuppence v ludlow 84 files differ, 33 "Only in" entries; tuppence v driftwood 106 / 51; ludlow v driftwood 86 / 48). "Names/numbers only" = equal after replacing the adopter names, digits and 40/64-hex strings. "Near-identical" = at least 90% of lines match after that normalisation. Same-job files with different paths are counted as rewrites, not as unique (adopter gate: tuppence/driftwood `.github/scripts/adopter-gate.py`, ludlow `.github/scripts/adopter_gate.py`).

Three-way classes (lines are per adopter):

| class | files | tuppence | ludlow | driftwood |
|---|---|---|---|---|
| A. byte-identical in all three | 76 | 19,385 | 19,385 | 19,385 |
| B. all three, names/numbers only | 27 | 1,214 | 1,214 | 1,214 |
| C. identical in tuppence+ludlow, absent from driftwood | 6 | 567 | 567 | 0 |
| D. names/numbers only in tuppence+driftwood (ludlow retired v5/v6 policies) | 18 | 526 | 0 | 526 |
| E. near-identical code/config (copy-paste drift) | 16 | 4,998 | 4,855 | 4,428 |
| F. genuinely different (<90%), including same-job rewrites | 35 | 7,814 | 5,316 | 7,819 |
| G. generated or observed data, differs | 14 | 6,593 | 8,566 | 14,366 |
| H. exists in one adopter only (by path) | 145 | 7,131 | 3,951 | 2,938 |
| total | | 48,228 | 43,854 | 50,676 |

Of class A, 13,903 lines are the single file `composed/feeds/feeds/cve/v3/cve/v3/feed.json`; the other 5,482 lines are three further feed/converter files, CI scripts and tests, the twin world layer and the cage probe (`drift/cage_probe.py` 391, `drift/served_apps.py` 255).

Tuppence against ludlow, by job (the pair this area is):

| class | files | tuppence lines | ludlow lines |
|---|---|---|---|
| identical | 87 | 20,365 | 20,365 |
| names/numbers only | 34 | 1,881 | 1,881 |
| near-identical (>=90%) | 23 | 7,266 | 7,164 |
| different, same job (shift-left, oscal_lane, tools tests, renovate.json, VENDORED, signals, engine pin, ...) | 13 | 2,090 | 1,927 |
| generated or observed data | 14 | 6,593 | 8,566 |
| tuppence only | 83 | 10,033 | 0 |
| ludlow only | 34 | 0 | 3,951 |

Split of the "only" rows after pairing by job: per-adopter declarations (twin overlay, scenario, workload manifest, kind file) are 501 tuppence / 500 ludlow lines; the adopter gate rewrite is 2,547 / 2,836 lines; truly adopter-only residue is tuppence 7,154 (cloud lane 5,140, reset 691, v5/v6 policies 526, evidence-comment renderer 426, inventory tests 202, 3 helper scripts' share of 169 counted with the gate) and ludlow 824 (eol feed 615, retirement record and its test 209).

Copy-paste drift is real. `drift/five-facts.py` is 2,536 lines in tuppence and 2,396 in ludlow; the 140-line difference is an `InventoryEvidence` class that exists only in tuppence (149 lines of the normalised diff are tuppence-only, 9 ludlow-only). `drift/oscal_lane.py` is 384 vs 300, `twin/verify-twin-sweep-moved.sh` is identical in T and L but 190 lines (10% similar) in D.

## Question 2. Declared values that differ

| declared value | tuppence | ludlow | driftwood | cite |
|---|---|---|---|---|
| turnover | £861,741,000 (as of 2026-03-31) | USD 197,584,000,000 (as of 2025-12-31) | £86,000,000 (as of 2026-06-30) | party.yaml:22 / :23 / :43 |
| customers / headcount | 4,900,000 / 3,902 | 45,232,000 / 97,100 | 240,000 / 410 (+ data_subjects 240,000) | party.yaml size block |
| reporting currency | GBP | GBP (for a USD filer) | GBP | party.yaml |
| tolerance per year | £15,000 | £5,000 | £40,000 | party.yaml:34 / :35 / :60 |
| tolerance as share of turnover | 0.0017% | 0.0000025% (currencies unconverted) | 0.047% | computed |
| assurance bands step_up / attest / no_cage | 1,500 / 15,000 / 150,000 | 500 / 5,000 / 50,000 | 4,000 / 40,000 / 400,000 | party.yaml:30-32 / :31-33 / :56-58 |
| band ratios to tolerance | 0.1x / 1x / 10x | 0.1x / 1x / 10x | 0.1x / 1x / 10x | derived |
| pricing_threshold, baseline, floor, roles | 3, MODERATE, isolated, risk-bearer+adopter+publisher | same | same | party.yaml |
| regulators (prose only) | FCA + PCI + GDPR | HIPAA | PCI + GDPR | README.md:13 |
| regimes actually priced | uk-gdpr only (ico penalty-schema v3) | uk-gdpr only | uk-gdpr only | HEADER.yaml:1365 / 1427 / 1396 |
| risk skin (prose, configmap) | toward-strict | Deny-heavy (strictest) | Audit-heavy (loosest) | risk-appetite-configmap.yaml |
| extra priced feed | cve (priced, £437,107) | eol v2 (£787,228); cve unpriced | insurer quote-driftwood v2 (premium £113,403); cve unpriced | party.yaml inherits |
| shared pins | platform implementations 5.0.0, nist 1.1.0, ico v3.0.0, feeds threat-register v4, recovery-expense v1.0.0 | same | same | gitops/flux-system, platform-pin.yaml |
| fx pin | fx/v1.1.0 | fx/v2.0.0 | fx/v1.1.0 | gotk-sync-fx.yaml |
| Kyverno engine | 1.18.2 | 1.19.1 | 1.18.2 | gitops/engine/kyverno.yaml |
| platform-tools / selection policy / twin | v6.3.0 / 1.1.0 / twin/v0.1.0 | same | same | platform-tools-pin.yaml, PIN.yaml |
| cage-tier workload version / accepted majors | 7.0.0 / 5, 6, 7 | same | same | party.yaml, accepted-majors |
| served workloads | ledger | reports | storefront, api, checkout-svc | party.yaml workload_cages |
| Namespace tier | isolated (2026-08-28) | isolated (2026-08-28) | isolated (2026-08-28) | gitops/apps/namespace.yaml:28 |
| compare outcome | residual £2,057,390 vs £15,000: breach | £61,725,982 vs £5,000: no verdict (partial) | £36,150 vs £40,000: no verdict (partial) | HEADER.yaml aggregate |

No regulator, risk skin or tier is a declared variable that the selection reads. The rule reads one number (tolerance) and the residuals.

## Question 3. Do the three adopters reach different cage tiers?

No. All three Namespaces are `isolated`, the tightest rung of `baseline < restricted < quarantine < isolated` (selection_policy.py:43-44; `isolated` is the rung the drift facts call the bottom rung and verify the workload reaches nothing).

Why, per adopter, from `floor_change.lines` (the floor-only counterfactual that composition records) and `forward-intel.residuals`:

- Tuppence: every priced line already picks `isolated` with no floor. Penalty-schema residual at `isolated` is £358,159 against a £15,000 tolerance, so no rung fits and the rule "fails closed" to the tightest. Rung residuals for forward-intel run baseline £58.9M, restricted £25.3M, quarantine £6.7M, isolated £1.68M. Even the tightest rung leaves 137x the tolerance.
- Ludlow: identical mechanism. Penalty-schema residual at `isolated` is £61,435,154 against £5,000 (12,287x); forward-intel residual £268,718. The floor is a no-op (residual_delta 0.0 on every line).
- Driftwood: the only adopter where the choice is a real selection. Without a floor, threat-register and forward-intel would pick `baseline` (residuals £13,691 and £531, both under £40,000). Penalty-schema residual at `isolated` is £35,744 (89% of tolerance) and at quarantine would be about four times higher, so only `isolated` fits. The Namespace takes the strictest line, so it is `isolated` anyway.
- Rung effect is the same publisher table everywhere. From driftwood's forward-intel the rungs leave 70%, 30%, 8% and 2% of uncaged loss (£530.83, £227.50, £60.67, £15.17 of £758.33), at £6,000/yr for quarantine in the twin response file. Tuppence's own response file says these numbers are "calibration knobs evidenced by nothing but this comment", grade 5, and "earns no pound credit" (tuppence/twin/orgs/tuppence/responses/run-the-payments-api-at-quarantine.yaml:9-20). Composition still uses them to pick the tier.

What differs between adopters is therefore not tier but verdict and gap: whether a verdict can be given (only tuppence, because only its ledger image carries a priceable CVE: log4j-core 2.14.1, CVE-2021-44228 in tuppence/inventory/images.json; ludlow/driftwood scan images produce a null cve price, cause not read from code), and how far above tolerance the tightest rung stays.

## Question 4. How much could be a shared template plus one small declaration file?

Judgement, with the measured basis in brackets.

- Per-adopter declaration (irreducible): party.yaml size, tolerance, floor, workload subject, parent pins (about 35 lines); one recovery scenario (30-line JSON of about 10 numbers); one valuation (amount + basis, about 15 lines); workload image and name. That is about 100 lines a repo; the repo today holds 590 (tuppence) and 591 (ludlow) hand-authored declaration lines in party.yaml, twin/orgs, scenarios, apps manifest, kind file, much of which restates the shared rung table.
- Template-able as-is (identical, names-only, near-identical, same-job-rewritten): tuppence 20,365 + 1,881 + 7,266 + 2,001 + 2,378 = 33,891 lines (70%); ludlow 20,365 + 1,881 + 7,164 + 1,836 + 2,627 = 33,873 lines (77%).
- Should not be in an adopter at all: vendored feed copies (tuppence 16,489, ludlow 17,104), fetched by pinned tag at compose time instead.
- Regenerable: HEADER, evidence, HANDBOOK, floor-change, feed PROVENANCE, inventory, samples (tuppence 6,593, ludlow 8,566).
- Genuinely adopter-only extensions: tuppence 7,154 (cloud lane, reset, old window versions, evidence-comment renderer, inventory tests), ludlow 824.

## What the loop would lose if this area vanished

The loop would lose its only enactment and its only tolerance input. There is no `tolerance` anywhere else in the estate that a cage reads (party.yaml:34 / :35), no Namespace tier label (gitops/apps/namespace.yaml:28) and no cage policy objects (composed/policies/v7.0.0), and the daily observation that the cage is in force (drift samples, 7 of 7 facts true) would stop. It would not lose a convergence mechanism, because none runs here: the per-rung reductions are self-declared and the tier has been at the ceiling since 2026-08-28.

## The simplest thing that would do this area's loop job

One shared template repo and one declaration per adopter.

- `adopter.yaml` per adopter, about 40 lines: name, currency, turnover (with currency and as-of), tolerance, floor, parent pins (platform tag, feeds tags), workload name and image, recovery assumptions (LEF and LM triples). Roughly 100 lines with one valuation and the scenario. The assurance bands become `tolerance * (0.1, 1, 10)`.
- Shared template (one repo or reusable workflow, about 2,500 lines): `select()` (about 25 lines, selection_policy.py:83-140 with the strictest-line fold at :143-197, 291 lines with docs), the v7 cage policies (510 lines, C10), the daily drift sampler (`five-facts.py`, `cage_probe.py`, `drift-sample.yml`, about 1,500 lines after de-duplicating the three diverged copies), and a compose step that calls platform's tools tag.
- Output: one `exposure.json` (the 72-line aggregate, not the 2,899-line header) and one Namespace label.
- Rough total: about 2,500 shared lines plus about 150 per adopter, against 92,082 today (tuppence + ludlow). Feeds, ICO and NIST stay pinned by tag and are not copied.

## Surprises

1. The ratchet has never moved. Tier `isolated` was declared on 2026-08-28 in all three repos in one commit each; the owner floor of 2026-10-23 changed no residual in tuppence or ludlow.
2. The loop does not close in tuppence or ludlow. The tightest rung leaves residual at 137x (tuppence) and about 12,300x (ludlow) of tolerance, and the ladder has no rung or lever beyond that. Driftwood is the only adopter near its tolerance, and only by a partial sum.
3. Ludlow's tolerance is £5,000 against a USD 197.6 billion turnover (2.5e-8 of turnover, currencies unconverted); the four owner-adopted band numbers in each adopter are a single number times 0.1, 1 and 10.
4. Two of three adopters give no verdict. `breaches_band` is null in ludlow and driftwood because the cve feed is unpriced, and the file itself says "a partial sum reads 'within the band' however large the excluded lines are" (ludlow/composed/HEADER.yaml:1409).
5. The compare result is 72 lines inside a 1,431-line header and 4,173-line evidence file whose bulk is NIST control lists (tuppence evidence `holes`: 2,558 lines).
6. The adopter gate (computed-semver acceptance of platform bumps) exists in three independently rewritten versions of 1,245, 1,691 and 1,514 lines, plus 937, 855 and 506 line verify scripts, and has nothing to do with money.
7. The "regulator" is not a variable. Tuppence (FCA, PCI, GDPR), ludlow (HIPAA) and driftwood are all priced only against the UK ICO penalty schema; a US health plan's exposure is a UK GDPR fine scaled to USD turnover.
8. Reductions per rung are self-declared and, in the twin's own words, earn no pound credit (grade 5), yet the estate's tier selection consumes them (`residual_basis: platform-cage-tiers@1.0.0`).
9. Automated reaction has not produced a merged change. No merged Renovate PR in either repo (4 unmerged branches each, newest 2026-10-23), no tier-change PR, the war-gamer commits are inventory refreshes only, and the twin-sweep observation line stops at 2026-10-22 despite a daily cron (cause could not be determined from tracked content; the 2026-10-23/24 commits changed the pin and tag resolution, not the append step). The one daily clock that keeps running is the drift sampler.
10. Ludlow alone ran the consumer-retirement path (2026-10-17: retired platform policy versions 5.0.0 and 6.0.0, moved Kyverno 1.18.2 to 1.19.1), so it has no v5/v6 policy directories and an engine different from the other two.
11. Tuppence carries a 5,140-line cloud datastore lane that says it is unactivated, and a 691-line SPIRE/OpenBao demo from July that no ticket in the loop depends on.
12. 36% of the area (33,593 lines) is vendored copies of other repos' signed releases, and 73% of tuppence's bytes are one JSONL file of OSCAL samples.

## Method and caveats

- Origin: commit authors are the owner for nearly everything (190 of 405 tuppence commits, the rest bots), so assistant and codex cannot be separated by author. I used the epoch and branch names: born before 2026-10-01 is `assistant`; born in October is `codex` only where the branch or message says so (one `codex/` branch merge per repo), else the rows say "epoch, unverifiable". The one owner quotation found is the 2026-10-03 delegation in `accepted-majors/platform-*.yaml`; "owner-adopted 2026-10-23" in party.yaml and the hub map (`FRESH/hub/.scratch/ecosystem/map.md:354`) is a document claim, not a dated quotation.
- Status `observed_running` rests on bot commits and merged PRs in git history (drift sampler, observation PRs, war-gamer inventory) and on the latest drift sample's facts; I did not run anything. `tested_offline` means a test or verify script exists in the repo; I did not run them.
- Born date = first commit adding any file of the component (`git log --diff-filter=A`), so imports from earlier splits show as 2026-07-31.
- Not read: why cve prices to null in ludlow and driftwood, the platform-side arithmetic that computes residuals (it is in the platform repo), and the hub copies of any adopter file in LOCAL.
