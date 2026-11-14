# D1: driftwood, the adopter (FRESH clone 2026-11-14)

## Summary
- 233 tracked files, 50,676 lines. 64.6% (32,725 lines) is tool-generated: the composed output, vendored feeds, the trivy inventory and observation logs. 12,424 lines are shared-template lines that match ludlow or tuppence. Only 5,527 lines are specific to driftwood.
- The loop's arithmetic does not run here. Quantify, compare and the tier pick run in `platform` (`compose/composition.py`, `graded/cage.py`, `wargamer/tier_pr.py`), called from driftwood's workflows through `.github/scripts/platform-tools.py`.
- driftwood declares the inputs: size (£86m turnover), tolerance (£40,000/yr), floor `isolated`, parent pins, three workload scenarios. It enacts one label, `posture.acme.io/tier` on `gitops/apps/namespace.yaml:30`.
- **Compare gives no verdict.** The priced subtotal is £1,807,493.96. The selected-tier residual total is £36,149.88 against a tolerance of £40,000, but `breaches_band: null` because the cve line is unpriced (`composed/HEADER.yaml:1368-1381`).
- **The ratchet has never moved and cannot move.** The Namespace has said `isolated` since 2026-08-28 (`git log -S` on namespace.yaml), and `overlay.floor: isolated` (`party.yaml:106`) is the top of the ladder. Every proposer PR that landed was an image-inventory update, never a tier.
- At the tightest rung the ico line alone leaves £35,743.54, about 89% of tolerance (`composed/HEADER.yaml:1385`). By the twin's own curve, running isolated costs £95,183.78 against £8,183.78 at baseline (`twin/forward-intel/v2/feed.json`).
- Evidence that runs: a daily ephemeral-cluster sample has recorded facts 1-8 true through 2026-11-13 (`drift/samples.jsonl`, `drift/workload-samples.jsonl`). Twin-sweep has written no observation since 2026-10-22, and in 39 sweeps its moved path has never fired.

## Components

| name | paths | lines | born | what it does | loop role | necessity | origin | status | cite |
|---|---|---|---|---|---|---|---|---|---|
| Party declaration | party.yaml | 133 (66 non-comment) | 2026-08-25 | Declares size, tolerance, assurance bands, baseline, parent pins, publishes[], floor and workload cages | tolerance | kernel | assistant (appetite/floor say "Owner-adopted 2026-10-23"; no quotation found) | observed_running (read by every composition) | party.yaml:42-60,66-80,104-131 |
| Selection policy package | selection-policy/* | 375 | 2026-08-28 | `select()` picks the loosest tier with residual ≤ tolerance, clamped to the floor; `select_party()` folds lines to the strictest | ratchet | duplicate (platform `graded/cage.py:select_tier` tiers the ico and threat-register lines, composition.py:3857-3858; `select_party` is a self-declared transliteration of `platform/wargamer/wargamer.py:select_party_tier`, selection_policy.py:162-165; near-copies in tuppence and ludlow differ by 6 lines) | assistant | observed_running for the twin and agent-cage lines only (evidence.json, policy_version 1.1.0) | selection-policy/selection_policy.py:83-140; platform/compose/composition.py:4246,4701 |
| Workload recovery scenarios | scenarios/*.json | 90 | 2026-10-23 | Per-workload lef/lm planning triples (marked "UNVALIDATED") that price the three workload cages | quantify | support | unknown (October epoch, no Codex trailer) | observed_running (evidence.json cages[] priced_from) | scenarios/workload-api-recovery.json:5,18-28 |
| Major-acceptance records | accepted-majors/* | 29 | 2026-09-23 | Exact records accepting platform policy majors 5.0.0, 6.0.0 and 7.0.0 | ceremony | support (gates new cage versions) | delegated ("you tell me, you control them all" 2026-10-03) | unknown | accepted-majors/platform-6.0.0.yaml:6-8 |
| Composed exposure and evidence (generated) | composed/HEADER.yaml, evidence.json, floor-change.json, HANDBOOK.md | 8,316 | 2026-08-25 | Composer output: prices[], cages[], holes, exposure aggregate, floor counterfactual, prose handbook | quantify (+compare) | kernel (the priced record the proposer reads); HANDBOOK is presentation | assistant (platform composer) | observed_running (52 commits to HEADER; last evidence change 2026-10-27) | composed/HEADER.yaml:1361-1431 |
| Vendored feed copies (generated) | composed/feeds/** | 16,710 | 2026-09-10 | Byte copies of the ico, feeds and insurer feed.json files and their converters (cve feed.json alone is 13,903 lines) | quantify | duplicate (canonical copies live in the ico, feeds and insurer repos) | assistant | observed_running | composed/feeds/feeds/cve/v3/cve/v3/feed.json |
| Cage policies (copied from platform) | composed/policies/v5.0.0,v6.0.0,v7.0.0/* | 750 | 2026-08-25 | Kyverno MutatingPolicy that reads the Namespace tier and stamps limits, priority, hardening and a WAF sidecar; GeneratingPolicy netpol; PriorityClasses | cage | kernel (duplicate of platform/distribution) | assistant | observed_running on the ephemeral CI cluster only | composed/policies/v7.0.0/cage-tier.yaml; cage-isolated.yaml |
| Composed machinery (generated) | composed/orphan-*, governed-namespace-*, bottom-rung-*, kustomization.yaml | 286 | 2026-09-23 | Orphan guard and cage, governed-namespace guard, bottom-rung netpol | cage | support | assistant | observed_running (fact 5 inventory) | composed/kustomization.yaml |
| GitOps enactment | gitops/apps/namespace.yaml, gitops/composed, gitops/flux-system, gitops/platform, gitops/engine | 534 | 2026-07-31 | Flux GitRepository {tag, commit} pins for 7 sources; the ResourceSet that installs composed/; the Kyverno engine pin; the tier label | enact | kernel (only namespace.yaml:30 and composed-set.yaml are the loop's) | inherited_2022 (Flux-pinned policy); tier label assistant | observed_running on the ephemeral CI cluster; opt-in `kubectl apply -k` (composed-set.yaml:40-50) | gitops/apps/namespace.yaml:30; gitops/composed/composed-set.yaml:72-95 |
| Served workloads | gitops/apps/{pod,api,storefront,version-configmap,nist-pin-configmap,kustomization}.yaml, deploy/pod.yaml | 259 | 2026-07-31 | The caged processes (storefront, api, checkout pod) and two advisory ConfigMaps | none (the caged subject) | support | codex (api.yaml, c9eff7a "Prepared by Codex") | observed_running (fact_8 true 2026-11-13) | drift/workload-samples.jsonl (last line) |
| Served-image inventory | inventory/* | 5,556 | 2026-10-04 | Trivy rows for 3 images (774 vulnerability rows) plus provenance; feeds the cve line | quantify / react | support (the cve line is still unpriced, amount null) | codex (aa92363 trailer) | observed_running (proposer PRs #67, #78, #93 merged) | inventory/images.json; composed/evidence.json prices[cve].amount=null |
| Twin overlay (authored) | twin/orgs/**, twin/currency.yaml, twin/signals.yaml | 532 | 2026-08-28 | Value chain, perspective (£3.2m quarterly checkout revenue), four rung responses with cost and reduction, six scenarios, pin-to-signal table | quantify / react | support (twin line priced at £758 of £1.8m) | assistant | observed_running until 2026-10-22 | twin/orgs/driftwood/perspectives/driftwood.yaml; scenarios/penalty-published-2026.yaml:21-28 (the emitter never reads scenarios/) |
| Vendored twin world | twin/world/**, twin/VENDORED.md, twin/PIN.yaml | 281 | 2026-08-28 | Byte copy of the hub's world layer; pin to twin/v0.1.0 | quantify | duplicate (hub twin/fixtures.py) | assistant | observed_running (staged by the emitter) | twin/VENDORED.md:12-19 |
| Twin emitter and feed | twin/emit-forward-intel.py, twin/forward-intel/** | 808 | 2026-08-28 | Renders the forward-intel envelope (lef null, lm triple, 4-rung curve); needs the hub `twin` package | quantify | support | assistant | observed_running until 2026-10-22 | twin/emit-forward-intel.py:44-65 |
| Twin verify scripts | verify-twin-overlay.sh, twin/verify-twin-scenarios.sh, twin/verify-twin-sweep-moved.sh | 745 | 2026-08-28 | Offline assertions on the overlay, scenarios and the sweep's moved path | ceremony | ceremony | assistant | unknown (not run, per the rules) | twin/verify-twin-sweep-moved.sh:1-10 |
| Five-fact sampler (instrument) | drift/five-facts.py, cage_probe.py, served_apps.py, oscal_lane.py, scripts/render_composed.py, verify-cage-probe.sh | 4,113 | 2026-08-29 | On an ephemeral cluster, proves the composed set is in force from signed sources, the bottom rung runs, it reaches nothing, and served workloads are caged; plus OSCAL | evidence | support | assistant (five-facts); codex (cage_probe, served_apps, oscal_lane via aa92363) | observed_running (daily to 2026-11-13) | drift/five-facts.py:1-40 |
| Observation logs | drift/samples.jsonl, workload-samples.jsonl, oscal-samples.jsonl, observations/twin-sweep.jsonl | 299 | 2026-08-10 | Append-only records: 195 five-fact samples and 39 twin sweeps (0 moved) | evidence | support | assistant (clocks) | observed_running | drift/samples.jsonl (tail); observations/twin-sweep.jsonl |
| August Flux-drift study | drift/probe.sh, forced-campaign.*, verdict.yaml, window.yaml, README.md, preconditions.yaml, api-image-note.md | 1,880 | 2026-08-07 | Pre-registered falsification of "does Flux drift"; its window.yaml is also the five-fact pre-registration | evidence (of a different question) | off_mission (except window.yaml five_fact_sample, 171-566) | assistant | observed_running 2026-08-10..13 (3 probe samples), dormant since | drift/verdict.yaml:19-23 |
| Local KinD demo bring-up | scripts/up.sh, reset.sh, lib.sh, bump-nist-pin.sh, git-server/*, kind/*, verify-reconcile.sh | 476 | 2026-07-31 | Offline touring cluster with an in-cluster seeded git server | presentation | off_mission (drift-sample.yml:11-17 says this cluster proves nothing about the org boundary) | assistant | unknown | README.md:18-27 |
| propose-tier workflow | .github/workflows/propose-tier.yml | 390 | 2026-08-25 | Daily 06:47 plus merged pin PR: recompose at today's date, run tier-propose (PR on the Namespace tier), run the inventory proposer, verify signatures, observation cage | ratchet / enact / react | kernel | assistant | observed_running (inventory PRs); tier PR never landed | propose-tier.yml:41-51,236-255 |
| shift-left workflow | .github/workflows/shift-left.yml | 557 | 2026-08-21 | Every PR: party check, kyverno version cross-check, cage probe, adopter gate, signed attestation; compose-check recompose must match committed; tier-binding check | compare / evidence | support (tier binding at :524-557 is the one compare→enact guard) | assistant | unknown (no CI logs read) | shift-left.yml:524-557 |
| Release signing | cut-release.yml, release.yml, verify-identity-regexp.yml, scripts/verify-identity-regexp.sh | 439 | 2026-08-21 | Dispatch-only gitsign tag after byte-for-byte recompose; tag push verifies identity and publishes | evidence | support (Flux pins signed tags) | assistant | observed_running (v4.0.0 Rekor entry, inventory/PROVENANCE.json:5-14) | cut-release.yml:123-151 |
| drift-sample workflow | .github/workflows/drift-sample.yml | 485 | 2026-08-29 | Daily 06:20: ephemeral kind, reconcile from the real remotes, run the sampler, append to the lane, delete the cluster | evidence | support | assistant | observed_running | drift-sample.yml:32-35 |
| twin-sweep workflow | .github/workflows/twin-sweep.yml | 579 | 2026-08-28 | Daily 07:05: re-render the twin feed; on a moved feed open a PR, else append an observation; two-job split | react | support | assistant | unknown (last observation branch run 39782231337, 2026-10-22; cause not determined) | twin-sweep.yml:72-75; observations/twin-sweep.jsonl |
| Renovate react path | renovate-run.yml, renovate.json, complete-feed-bump.sh, rederive-signals.py, refresh-twin-feed.py | 720 | 2026-08-21 | Daily 06:11 self-hosted Renovate bumps parent {tag, commit} pins; post-upgrade task recomposes composed/ and signals | react | kernel (the only parent-side trigger) | assistant | observed_running once (PR #20 merged 2026-09-01); 4 renovate branches unmerged | renovate.json postUpgradeTasks; git log |
| Observation delivery | observation-delivery.yml, .github/rulesets/* | 178 | 2026-10-17 | On clock completion, a separate App identity validates and merges observation PRs | ceremony | ceremony | unknown (October epoch, no trailer) | observed_running (bot merges through 2026-11-13) | observation-delivery.yml:5-23 |
| Adopter gate (semver acceptance) | .github/scripts/adopter-gate.py, scripts/verify-adopter-gate.sh, trusted_root.json | 2,145 | 2026-08-23 | On a platform pin bump: verifies platform's signed bump evidence with cosign, diffs version arrays, requires acceptance records for majors | evidence / ceremony | support (authenticity of cage versions) | assistant | unknown | adopter-gate.py:1-40 |
| CI helper scripts and pins | platform-tools.py, read-pins.py, verify-pinned-checkouts.py, served-workloads.py, engine_declaration.py, .github/actions/*, platform-tools-pin.yaml, requirements | 609 | 2026-09-10 | Verify and run the pinned platform compiler; read pins; assert checkouts match commits | support plumbing | support | delegated (ADR-0025, README.md:119-125) | observed_running (used by propose-tier) | platform-tools.py:2-6 |
| Tests | .github/tests/*, tests/* | 2,058 | 2026-09-10 | Unit tests of the workflow split, signing, delivery, reach, fact 4 compare | ceremony | ceremony | assistant / codex mixed | unknown (not run) | .github/tests/test_twin_sweep_split.py (368 lines) |
| Repo boilerplate | README.md, LICENSE, .gitignore | 344 | 2026-07-31 | README (stale: says compiler v4.0.0, the pin is v6.3.0), Apache licence | none | none | assistant | n/a | README.md:83; .github/platform-tools-pin.yaml:11 |

The rows sum to 50,676 lines in 233 files.

## (1) What driftwood declares (value, unit)
- **party.yaml**: party `driftwood`; roles risk-bearer, adopter, publisher. reporting_currency GBP. size: turnover 86,000,000 GBP; customers 240,000 (count); data_subjects 240,000 (count); headcount 410 (persons); as_of 2026-06-30.
  - appetite: assurance_bands GBP/yr, step_up_at 4,000.0, attest_at 40,000, no_cage_at 400,000; pricing_threshold 3 (unit not stated); tolerance 40,000 GBP (per year per HEADER basis "annual-aggregate").
  - baseline MODERATE (NIST 800-53 baseline name).
  - inherits: feeds/recovery-expense v1 (shadow, excluded from headline), platform implementations 5.0.0, nist controls 1.1.0, ico penalty-schema v3, feeds threat-register v4, feeds cve v3 (since 2026-10-03), insurer quote-driftwood v2.
  - publishes: feed exposure (path composed); feed forward-intel (path twin/forward-intel).
  - overlay: floor `isolated` (tier); workload_cages for storefront, api and checkout-svc: platform cage-tier 7.0.0, mode recovery_planning. add []; restate [].
- **selection-policy**: policy_version 1.1.0 (PIN.yaml:12, VERSION). Ladder: baseline < restricted < quarantine < isolated (+ declarable `infra`).
- **accepted-majors**: platform 5.0.0 (2026-09-23), 6.0.0 and 7.0.0 (2026-10-03); 6.0.1 superseded.
- **scenarios** (GBP; lef per year, lm GBP per event, PERT min/mode/max):
  - api: lef 0.1/0.5/2, lm 400/1,600/4,800.
  - storefront and checkout-svc: same 30-line schema. Planning assumption £100 per engineer-hour × 2 engineers × 2/8/24 h.
- **twin**:
  - perspective: checkout-revenue 3,200,000 GBP per quarter (14.88% of turnover / 4), evidence_grade 2; brand-trust unpriced (grade 5).
  - responses (GBP/yr cost; reduction fraction): baseline 5k/8k/12k, 0/0.05/0.1. Restricted 14k/20k/28k, 0.2/0.3/0.42. Quarantine 30k/42k/60k, 0.55/0.65/0.75. Isolated 70k/95k/130k, 0.82/0.9/0.95, all at grade 5 ("unmeasured calibration").
  - edge: cart-pii→checkout-revenue elasticity 2.87e-5/5.74e-5/5.74e-5, lag 30 days, grade 3.
  - feed v2.0.0, published_at 2026-10-03: lm 91.89/183.78/183.78 GBP; lef null, borrowed from threat-register. Curve net_cost_of_risk is baseline 8,183.78, restricted 20,183.78, quarantine 42,183.78, isolated 95,183.78.
  - currency.yaml GBP. twin PIN twin/v0.1.0 @ 0e353029.
- **inventory**: 3 images, 774 vulnerability rows; apps source tag v4.0.0.
- **Pins** (tag @ commit):

| Pin | Tag | Commit |
|---|---|---|
| platform | v5.0.0 | 703eff6a |
| nist | v1.1.0 | 33a05df1 |
| ico | v3.0.0 | 9d092221 |
| feeds | recovery-expense/v1.0.0 | 9e7958e9 |
| fx | fx/v1.1.0 | 974e7351 |
| insurer | v2.0.0 | 0b91e8dc |
| driftwood apps | v4.0.0 | 1cd446f6 |
| driftwood composed | v5.3.0 | 6e421617 |
| compiler tools | v6.3.0 | d0d0ace3 |

  The ResourceSet array is 5.0.0, 6.0.0, 7.0.0. Engine is kyverno 1.18.2, with install sha256 3dcd43ea…
- **Derived outputs** (composed/HEADER.yaml and evidence.json):
  - ico ALE £1,787,177.08 (tier isolated, residual £35,743.54); threat-register £19,558.55 (isolated, £391.17); cve null; twin £758.33 (isolated, £15.17).
  - insurer premium £113,403.30; agent-cage £0.00017.
  - workload cages residual £12.89, £25.78 and £7.32, all isolated.
  - breaches_band null.

## (2) What driftwood runs

| Workflow | Trigger | Purpose |
|---|---|---|
| renovate-run.yml | cron 06:11 daily, dispatch | Bump parent pins as PRs; recompose in the same commit |
| drift-sample.yml | cron 06:20 daily, dispatch | Ephemeral-cluster five/seven/eight-fact sample; observation PR |
| propose-tier.yml | cron 06:47 daily, PR closed (merged) touching tools pin, party.yaml, platform pin or nist pin, dispatch | Recompose at today's date, propose a tier PR and an inventory PR |
| twin-sweep.yml | cron 07:05 daily, dispatch | Re-render the twin feed; a PR if moved, else an observation |
| observation-delivery.yml | workflow_run of drift-sample/twin-sweep completed, dispatch | Validate and deliver observation PRs with a separate App identity |
| shift-left.yml | every pull_request | Party check, version gate, cage probe, adopter gate, attestation, compose-check, tier binding |
| cut-release.yml | dispatch only | Recompose byte-for-byte, then cut a gitsign-signed tag |
| release.yml | push tag v*.*.*, dispatch | Verify tag identity offline, kustomize build, publish the Release |
| verify-identity-regexp.yml | PR/push touching release.yml or its script | Check the identity regexp is anchored |

## (3) Generated or copied against authored (measured)
- **Tool-generated: 32,725 lines.**
  - composed/** 26,062, generated by the platform composer.
  - inventory 5,556 (trivy proposer).
  - observation logs 299; forced-campaign logs 589; twin feed.json and bump.yaml 140; requirements 79.
- **Shared template: 12,424 lines.** These are lines of non-generated files that match ludlow or tuppence line for line.
  - 76 files are byte-identical in all three adopters (19,385 lines, some of them generated).
  - Examples: drift/five-facts.py shares all but 111 of 2,471 lines; propose-tier.yml all but 70 of 390.
- **driftwood-specific: 5,527 lines.**
  - Largest: adopter-gate.py 965, test_twin_sweep_split.py 368, verify-adopter-gate.sh 337, twin-sweep.yml 284, rederive-signals.py 278, shift-left.yml 206, the window.yaml drift sections 195, verdict.yaml 132.
  - The party data inside it is small: party.yaml 89, three scenarios 90, twin overlay about 300, storefront and pod manifests 137.

## (4) What a NEW adopter writes by hand to join
- **Data, non-comment lines, about 290:**
  - party.yaml about 66.
  - namespace.yaml 9 and apps kustomization 9.
  - 5-6 GitRepository pins at about 16 each (about 90).
  - composed-set.yaml about 71; engine pin 10.
  - one scenario per caged workload, 30 each; one acceptance record per accepted major, 8 each.
- **Optional**: a twin overlay (about 530 lines here) and the selection-policy copy (375; required only if it publishes forward-intel, composition.py:4141-4145).
- **Copied and org-substituted, not designed**: 9 workflows (2,542 lines, 817 of them comment lines), renovate.json 158, and the CI helpers. Most of the 12,424 shared-template lines come with it.

## (5) Smallest adopter repo that would still run the loop
1. `party.yaml`: size, `appetite.tolerance`, floor, inherits pins.
2. `gitops/apps/namespace.yaml`: governed label plus `posture.acme.io/tier`, and the workloads it cages.
3. `gitops/flux-system/gotk-sync.yaml` plus one GitRepository pin per parent: platform cage, a pricing feed such as ico.
4. `gitops/composed/composed-set.yaml`: or reconcile the platform distribution directly.
5. `composed/`: generated, never hand-written.
6. `.github/workflows/propose-tier.yml`: compose, compare and open the tier PR.
7. `renovate.json`: the react trigger.

Everything else is evidence, ceremony or presentation: twin/, drift/, inventory/, the adopter gate, accepted-majors, observation-delivery, tests, the demo and the release signing (support).

## What the loop would lose if this area vanished
- The only place the organisation's tolerance (£40,000) and size are declared (party.yaml). The loop cannot compare without it.
- The enacted cage: the Namespace tier label, and the Flux route that installs the composed cage policies on a cluster.
- The clocks that re-run the loop daily (propose-tier) and the parent-bump trigger (Renovate).
- The only observed proof that the cage is in force and holds on a live cluster (facts 1-8 daily).
- Nothing of the arithmetic. Pricing, tier selection for the big lines, the PR writer and the cage policy source all live in `platform`, and selection_policy.py duplicates platform's rule.

## The simplest thing that would do this area's loop job
- `party.yaml` (about 25 lines): turnover, tolerance in GBP, floor, and a list of pinned feeds.
- `namespace.yaml` (about 10 lines) carrying the tier label.
- One Flux GitRepository plus Kustomization (about 30 lines) pointing at a signed platform cage tag.
- One scheduled workflow (about 80 lines). It checks out the pinned feeds, runs a single `price_and_pick()` (about 60 lines: ALE per feed, residual per tier, the loosest tier under tolerance, never below the floor, never looser than current) and opens a PR editing the label.
- Renovate config (about 30 lines) to bump feed and cage pins.
- Total about 235 lines, against 50,676 today. Optionally, one daily evidence job (about 100 lines) asserts the label is reconciled and a pod carries the tier.

## Surprises
- The floor is the top rung: `overlay.floor: isolated` (party.yaml:106) is `LADDER[-1]`. Since 2026-10-23 the selection returns isolated whatever exposure says, so quantify no longer influences the cage. floor-change.json shows the threat-register line moved baseline→isolated purely by the floor.
- Compare is undefined: `breaches_band: null` because the cve line is unpriced, even though 774 vulnerability rows sit in inventory/images.json (HEADER.yaml:1380-1381).
- By the twin's own data the cage costs more than it saves. Isolated costs £70k-£130k/yr (responses/run-the-checkout-at-isolated.yaml), its curve says £95,183.78 against £8,183.78 at baseline, and the twin line's whole exposure is £758. The insurer premium (£113,403) also exceeds tolerance.
- The tier label has not changed since 2026-08-28, and its comment is stale. namespace.yaml:22-29 says the threat-register line lands baseline; evidence now says isolated.
- The isolated rung is "no reach at all", a deny-all netpol (composed/policies/v7.0.0/cage-isolated.yaml description). Yet the storefront, api and checkout are all caged isolated and fact 8 reads true, which suggests the demo shop runs with no network reach.
- The PRs that comments say "a human merges" are merged by `pavc-other-hand[bot]` (94 bot commits). This includes proposer PRs #67, #78 and #93.
- The twin-sweep clock went silent after 2026-10-22, the day before twin/PIN.yaml moved to signed twin/v0.1.0. Its moved branch has never produced a moved=true observation.
- 64.6% of the repo is generated output committed to git. A single vendored cve feed.json is 13,903 lines, 27% of the repo.
- Enact is proven only on throwaway CI clusters. composed-set.yaml is opt-in (`kubectl apply -k`, :40-50), and no persistent cluster reconciles it.
- driftwood's own apps source pin is v4.0.0 while composed delivery is v5.3.0. The README describes compiler v4.0.0; the pin is v6.3.0.
