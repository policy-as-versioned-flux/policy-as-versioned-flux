# A5: the October to November work (mostly Codex) and the calibration programme

## Summary
- Since 2026-09-27 the hub took 194 authored commits (all dated 2026-10-03 to 2026-10-31) and 77 bot `truth: record` commits. Hub files born since then hold 65,722 lines (`wc -l` at HEAD), plus a 1,336,397-line research and patch dump. Across the other repos: +21,044 platform, +80,910 feeds (74,082 of it captured KEV/HMRC data), +9,914 nist, +1,748 ico, +1,261 insurer, and +30,430 / +29,015 / +25,549 in Driftwood / Tuppence / Ludlow, mostly vendored composed feeds. The last authored commit is dated 2026-10-31. Local files carry mtimes of 11-03/04. Since then only bots commit: the daily TRUTH record in the hub and the daily drift samples in the adopters.
- Only two October changes moved the loop's numbers.
  - (a) The 2026-10-04 delivery of September's Claude work changed every adopter's money figure. It added size, policy7, CVE v3 and `pricing_threshold: 3`. Tuppence went from £9.50M to £102.87M. Driftwood and Ludlow went from a stated breach (`breaches_band: true`) to no verdict at all (`null`): their CVE line is unpriced (`amount: null`) and so untiered.
  - (b) The owner adopted three policies on 2026-10-23. For Driftwood this moved two lines from `baseline` to `isolated` and cut the residual from £49,965 to £36,150. The composed policy YAML bodies did not change.
- The calibration programme (2026-10-30/31, 49,334 hub lines) tries to qualify Qwen3-4B on the twin's six judgement "skills". The bar is ADR-0029's ten conditions: about 326 items per skill and strictly better than a constant answer. Tracked files show a single demonstrated developmental reference case, and the commissioned dataset is unreadable. `twin/qualification-registry.json` is empty, and none of the code has a caller outside bench/, tests/ or a refusing gate check.
- PDF, ELF and Linux tooling come in because the model's inputs are publisher documents. To prove that an extracted excerpt really came from the PDF, the programme instruments Xpdf, builds it on Linux CI, pins its ELF/SONAME runtime closure and traces its file reads with ptrace. On top sits a privileged "tiny Linux lease" that would cage the model process. All of it is source-only or TEST_ONLY by its own statement.
- The local untracked calibration material is hollow: 25 files, and 28,073 directories of which 21,541 are empty. The resume directories from 10-17 on contain only `.DS_Store`. All 215 directories under `.scratch/worktrees` contain zero regular files. 31 local branch tips (all calibration, PDF or Linux, 10-30/31) are not reachable from the remote main.

## Components

Lines are `wc -l` at HEAD of files born on or after 2026-09-27, unless the row says `+N ins` (git diff insertions since the last commit before 09-27). Born dates come from `git log --diff-filter=A`. "Cage residual" means `selected_tier_residual_total` in `composed/HEADER.yaml`.

| # | name | paths | lines | born | what it does | loop role | necessity | origin | status | cite |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Claude handoff dump | hub/.scratch/ecosystem/research/resume-2026-10-0{3,4}, patches/resume-2026-10-0{3,4}, research/resume-20261025 | 1,336,397 (1,887 files) | 2026-10-03/04 | Commits every intermediate JSON, log, review and .patch from resuming the September Claude work into git | ceremony | ceremony | codex | unknown (records, nothing runs) | hub 6ed89616, d06f0485 (empty bodies) |
| 2 | Ticket/map/ADR record edits, including "assurance closure" | .scratch/ecosystem/issues/162-169 (born), edits to 27/46/97/142/151/155/156 and others, map.md, ADR-0037, ADR-0038 | 452 born + ~2,450 ins | 10-04 to 10-27 | Dated reconciliations, roll-up counts ("157 resolved / 2 claimed...") and "recorded regression" acknowledgements. "Assurance closure" (64d6e15c) is a 143-line record-only commit closing ticket 27 | ceremony | ceremony | codex (text says "Codex integrator") | unknown (records) | hub .scratch/ecosystem/map.md:371; issues/67:452; 64d6e15c (2026-10-23) |
| 3 | Observation delivery controller | talk/observation_delivery.py (994), talk/truth_delivery.py, truth_integration.py, .github/workflows/truth-delivery.yml (147), tests/test_observation_delivery*.py, test_truth_*.py | 6,734 (22 files) | 10-05, 10-17 | Moves bot-signed clock observations onto protected main through a PR and a second reviewer identity, because required review rejected direct pushes (GH013) | evidence | support | delegated (ADR-0037 "Decided 2026-10-17 by the assistant") | observed_running | hub docs/adr/0037:7-15; merge fc37a668 (PR #315, TRUTH run 491, 2026-11-12) |
| 4 | Daily TRUTH record churn | talk/truth.log, talk/captures/* | +8,812 ins net (77 bot commits, about 288k churn) | daily | Rewrites ~50 capture files and appends one TRUTH line each day | evidence | support | assistant (earlier epoch) | observed_running | hub 5392b30a; talk/truth.log run 491: pass=117 fail=0 skip=26 |
| 5 | Twin cage aggregation, local clock receipt, twin release route, development renewal | verify/twin-cage, talk/twin_release.py (188), tests/test_twin_cage.py, test_twin_release.py, twin/ENACT_MODE.why | 1,885 born + ~1,211 ins | 10-22/23 | Fails the twin-cage aggregate on an unmeasured proof, admits a native local-clock receipt, adds a signed twin release route, renews development mode | ceremony | ceremony | owner_words (renewal) + codex | tested_offline | ticket 97:218, "agree to renew this until the end of the year" (2026-10-22); hub b307a2ae, 3fa9c32c |
| 6 | Cloud plane admission (ticket 151) | tests/test_cloud_plane_contract.py, verify/cloud-plane, platform cloud 1.0.1, tuppence cloud-crds | 1,105 hub + platform/tuppence share | 10-17 to 10-23 | Admits independent OSCAL revisions and restores cloud cages over unclaimed Crossplane resources in Tuppence | cage/enact | support | assistant (ticket 151, Sept) carried by codex | observed_running per record (KinD admission on citable TRUTH 450), not re-verified | hub dd7a3c18, b7d77b7f; platform "Restore cloud cages for unclaimed governed resources" (10-22) |
| 7 | Engine/compiler maintenance and consumer retirement (147-150, ADR-0038) | hub engine/compiler tests; adopters compiler v5.1 to 6.3 bumps; ludlow composed/policies | 1,362 hub born | 10-17/18 | Retires Ludlow's v5/v6 policy windows ahead of a Kyverno engine change; re-pins compiler tools | cage/enact | support | delegated (ADR-0038:7) | unknown (ticket says measured; not re-verified) | ludlow ce5213f (deletes composed/policies/v5.0.0/*, v6.0.0/*) |
| 8 | Inventory, CVE pricing and served workloads (153/155/161) | platform inventory composer; adopters inventory/images.json (+5,447 DW, +1,630 LU); hub test_workload_lane_*.py, verify/served-workloads | 668 hub born + platform/adopter share | 10-04 to 10-23 | Prices CVEs from each adopter's own scan and repairs inventory IDs. CVE is priced only for Tuppence (£437,107); Driftwood and Ludlow show `amount: null` | quantify | support | assistant (Sept tickets) carried by codex | observed_running (fact5 sample) | hub 820b8091; map.md:310 (run 39882342142, "two missing risk joins/empty risks"); driftwood composed/HEADER.yaml:1420-1424 |
| 9 | Publisher reliability / monetary publisher price (ticket 46) | nist report machinery (+9,914 ins repo-wide), feeds/ico adapters (+1,492/+1,748), hub verify/publisher-reliability, tests/test_publisher_*.py | ~1,850 hub + ~13k cross-repo | 10-17/18, 10-23 | Scores publisher forecasts against outcomes ("authenticated monetary publisher accuracy") | quantify (weight on Q) | off_mission today (no enrollment, no outcomes) | assistant (ticket 46, Sept) carried by codex | tested_offline; nist "Bind the empty source report to its observed October 18 UTC cutoff" | hub a8c36d32 "without asserting publisher price accuracy"; map.md:318 |
| 10 | Recovery-expense shadow pilot | feeds/recovery-expense (~4,400 ins), platform recovery collector, nist SDK admission, hub tests/test_recovery_expense_signal.py, fixtures/recovery-expense-v1.0.2.json | ~4.4k feeds + ~180 hub | 10-23/24 | A prospective 2027 GBP recovery-expense forecast per institution, explicitly kept out of prices | quantify (prospective) | off_mission now | delegated after recorded owner acceptance (not verbatim) | tested_offline; signed feed tag pinned (feeds=838abe5@recovery-expense/v1.0.2 in TRUTH 491); no data | driftwood party.yaml "excluded from ordinary headline pricing"; feeds 9b8f059 body |
| 11 | Owner-adopted party policy (assurance bands, `floor: isolated`, workload_cages) | adopters party.yaml (+17 to 33), scenarios/workload-*-recovery.json (30 each), platform party/assurance_bands.py, break-glass/ | ~300 adopter + platform share | 10-21 to 10-23 | Declares GBP assurance cutoffs, raises the cage floor to isolated, adds workload cage declarations | tolerance + ratchet | kernel (floor/tier), support (bands) | owner acceptance recorded, not verbatim | tested_offline; delivered in signed releases DW v5.2.0, TU v4.3.0, LU v5.3.0 | driftwood d2c6f83; driftwood party.yaml:53-58; issues/27:184-189 |
| 12 | Insurer quote disclosure (37/162) | insurer quote (+1,261), platform quote conditions | ~1.3k + platform share | 10-17 to 10-21 | States on the quote that the insurer is illustrative | presentation | ceremony | assistant (ticket 75 A4) carried by codex | tested_offline (delivered) | insurer "quote: disclose illustrative scope through the versioned payload" |
| 13 | Pound-seam, can-record, default record (163/166/167) | verify/pound-seam, verify/can-record, tests/test_can_record.py, test_pound_seam_*.py | ~1,600 ins | 10-05, 10-26 | Gate checks on the gate's own SKIP reasons and on which ref the records are written to | ceremony | ceremony | codex (branch `codex/...`) | tested_offline | merges #271, #277, #279 |
| 14 | Skill basis, ICO regime price, causal grade, decay day (164/165/168/169) | twin/causal_claims.py, ethics_gate.py, signal_classify.py, tests/test_causal_claims.py, test_skill_basis_boundary.py, test_pound_seam_feed_presence.py | ~1,100 born + edits | 10-26/27 | Stops over-grading of causal evidence (the grade sets a price width); requires a regime price for a declared ICO feed; fixes the date a signal decays | quantify / react | support | codex | tested_offline | issues/168:9 ("These grades may reach price eligibility"); merges #272, #273, #282, #283 |
| 15 | Cal: reference admission, pinned smoke, qualification actor binding | twin/qualification.py (1,809), reference_cases.py, development_capture.py, bench/pinned-candidate/smoke.py, README, bench/qualification_controls.py, reference_case_admission.py | 4,605 | 10-30 | Freezes an "Actor" (model, config, host) and population; admits one developmental case; runs a Qwen smoke probe | none (model qualification) | off_mission | codex (inferred); one owner approval inside it | tested_offline; registry empty | docs/reference-case-admission.md ("one measured item ... not-measurable, passed=false"); twin/qualification-registry.json `"entries":[]` |
| 16 | Cal: source metadata, signal inputs, substrate | twin/source_metadata.py, source_metadata.schema.json (808), source_metadata_migration.py (1,064), signal_inputs.py, signal_candidate.py, substrate_generation.py, basis_assessment.py, tests | 8,115 | 10-30/31 | Custody-bound metadata about publisher sources (dates, excerpts, spans) as model input | none | off_mission | codex (inferred) | tested_offline | docs/source-metadata-migration.md:1-20 |
| 17 | Cal: four judgement-task contracts, inputs, sessions | twin/task_contract/* (4,042; schema 3,513), task_inputs.py, task_sessions.py, task_contracts.py, qualified_tasks.py, tests | 7,963 | 10-30 | Closed schemas and lifecycle for the evolution, causal, gameplay and ethics tasks | none | off_mission | codex; owner "Approve stronger plant checks" covers the substrate scorer only | tested_offline | twin/task_contract/contract.md:21 ("No model output grants sensing, signoff, pricing, override, enactment or merge") |
| 18 | Cal: Linux Qwen backend | twin/linux_candidate.py (777), bench/pinned-candidate/qwen_backend.py (503), tests/test_remaining_backend_profiles.py | 2,044 | 10-30 | Six CPU profiles for Qwen3-4B (bf16, 12 GiB cap, offline) | none | off_mission | codex | written_never_run ("No Linux model execution ... is established") | bench/pinned-candidate/LINUX-BACKEND.md:3-6 |
| 19 | Cal: tiny Linux lease, CI controls, ELF closure, network denial | bench/pinned-candidate/linux_lease_control*.py (1,305+1,590), linux_guardian.py (1,587), linux_network.py, linux_runtime_filter.py, tests/test_linux_lease_control_ci*.py, test_xpdf_linux_*.py, .github/workflows/twin.yml (+183) | 9,615 + 183 | 10-30/31 | Root-installed source that would lease a Linux host to the model process with memory, network and teardown controls; CI resolves ELF NEEDED/SONAME identities | cage (of the AI agent, not the adopter) | off_mission | codex | wired into twin.yml ubuntu rows; outcome could not be determined | twin.yml:136 "native tiny lease controls; no model"; hub 83ce5964, 5c3e8d22 |
| 20 | Cal: source-native observation (ptrace) | twin/source_native_observation.py (1,720), tests | 2,438 | 10-31 | Bounded Linux x86_64 tracing of the exact files one converter run opens | evidence (of a model input) | off_mission | codex | tested_offline (TEST_ONLY replay) | twin/source_native_observation.py:1-5 |
| 21 | Cal: PDF origin, comparison, remap, native bridge, Xpdf build | twin/pdf_comparison_capture.py (1,144), pdf_output_origin.py (413), pdf_remap_resources.py (601), pdf_native_bridge.py (259), bench/pinned-candidate/xpdf-origin, tests/test_pdf_*.py, tests/fixtures/TEST_ONLY-pdf-output-origin, TEST_ONLY-xpdf-build | 14,834 | 10-31 | Instruments Xpdf so each output byte can be traced to its PDF origin; compares pristine and patched builds over 18 invented PDFs | evidence (of a model input) | off_mission | codex | tested_offline; "All actual native questions remain unrun" | docs/pdf-comparison-capture.md:3 |
| 22 | Local calibration-programme scaffolding | LOCAL/.scratch/calibration-programme | 4,162 (25 files, all in one subdirectory) | 2026-11-03/04 mtime | One contract packet for a Linux Xpdf build ("PROPOSAL ONLY ... unimplemented and unexecuted"); 396 directory names: 152 implementation, 100 review, 64 proposal, 57 integration, 23 repair | ceremony | ceremony | codex (inferred: "Root must independently review") | written_never_run | .../source-native-pdf-linux-build-contract-revision01/CONTRACT.md:3 |
| 23 | Local hollow worktrees and branches | LOCAL/.scratch/worktrees (215 dirs), local branches | 0 (no regular files in any of the 215 dirs) | 10-17 to 10-31 | See section 4 below | ceremony | ceremony | codex | unknown (stale; 214 of 215 registered worktrees prunable) | `git worktree list` |
| 24 | Daily adopter drift samples (bot) | driftwood/tuppence/ludlow drift/, composed/evidence | could not determine (blobless clone) | daily through 2026-11-13 (start predates the window) | "drift sample: five facts on an ephemeral cluster" | evidence | support | assistant (earlier epoch) | observed_running | driftwood log 2026-11-13 |
| 25 | Feeds 10-03 captured inputs | feeds KEV/HMRC captures, FX snapshot | +74,082 / +722 ins | 10-03/04 | Captured KEV, HMRC and FX source data | quantify | support | codex (handoff) | unknown (data only) | feeds 37dfe4a, d62f74e |
| 26 | Adopter vendored composed feeds and evidence | driftwood/tuppence/ludlow composed/feeds (+15,494 / +15,385 / +15,505), composed/evidence.json (+3,423 / +1,047 / +1,687) | ~52,500 ins | 10-04 to 10-24 | Copies of the signed parent feeds and the per-composition evidence ledger, regenerated on each recompose | evidence | duplicate (the copy of feeds/ico/insurer sources) | assistant/codex | tested_offline (CI-composed) | adopter `git diff --numstat` since the last pre-09-27 commit |
| 27 | Adopter CI, tests, drift probes, cloud CRDs | adopters .github/tests (+1,036 to +1,233 each), .github/workflows (+600 to +633), drift/five-facts.py, drift/cage_probe.py (+391 each), tuppence composed/cloud-crds (+4,295) | ~14,000 ins | 10-03 to 10-25 | Signature, release and pointer tests; the sampler; Tuppence's Crossplane cloud cage CRDs | enact / evidence | support | codex | observed_running (drift samples) | tuppence fd034c0 "Render the verified cloud 1.0.1 composition" (2026-10-22) |
| 28 | Platform October changes | platform party/, break-glass/, compose (quote conditions, monetary context, tier-move explanation), cloud 1.0.1, recovery collector, inventory CLI | +21,044 ins | 10-17 to 10-25 | Composer and tool changes that support rows 6, 8, 9, 10, 11 and 12 | quantify / cage | support | codex | tested_offline | platform log 2026-10-17..25 |

Accounting: hub born-file lines are 49,334 (born on or after 10-30) + 13,588 (10-05 to 10-29) + 2,800 (09-27 to 10-04) = 65,722. Rows 15-21 sum to 49,614 (path buckets cross the date cut slightly), and the remaining hub rows cover most of the 16,388 Oct lines. The dump (row 1) is separate. Cross-repo figures are diff insertions.

## Per-workstream answers

**(1) Workstreams.** "Finished" means the record says resolved or the PR merged. It does not mean the loop changed.
- **Claude handoff resume (10-03/04).** Codex resumed Claude's September eco-system work and delivered it to the adopters. Trigger: "you tell me, you control them all, you don't need me to answer" (owner, 2026-10-03; quoted in issues/153:30 and 148:72). Lines: 1.34M dump, plus feeds +74k data. Finished (delivered 10-04).
- **Observation delivery (10-05, 10-17).** Bot observations reach protected main through a PR. Trigger: GH013 on the producers' direct pushes on 2026-10-16 (ADR-0037:11-13). Lines: 6,734. Finished and running daily.
- **Assurance closure / record reconciliations (10-17 to 10-27).** Records that tickets 27, 46, 141-161 match the delivered work. Trigger: the standing whole-build authorisation (issues/165:5). Lines: ~2.9k of records. Ongoing as ceremony.
- **Owner policies (10-21 to 10-23).** Assurance bands, isolated floor and workload cages for each adopter. Trigger: "The owner accepted all three recommendations" (issues/27:184; recorded acceptance, not a quotation). Finished: signed releases plus pointer PRs DW100/TU110/LU102.
- **Publisher reliability (ticket 46).** Scoring of publisher forecast accuracy. Trigger: ticket 46 (September). Lines: ~15k across repos. Not finished: "monetary cohorts remain open" (map.md:318).
- **Recovery-expense (10-23/24).** A 2027 shadow forecast of recovery spend. Trigger: owner accepted the "prospective 2027 direct-recovery-expense shadow pilot" (map.md:356). Lines: ~4.6k. Software is finished. Data and outcomes do not exist and cannot exist before 2027.
- **Cloud plane 151, engine 147-150, inventory 153/155, incumbent 156.** Delivery of September tickets. Lines: ~4k hub plus repo shares. 151 and 156 are resolved. 155 was claimed (open) on 10-23.
- **Pound-seam / can-record / skill basis / ICO / causal / decay (163-169, 10-26/27).** Gate and heuristic fixes. Trigger: review findings. 168's own text: "The user resumed implementation after delegating a labelled evaluation corpus and a dedicated pilot custodian". Lines: ~2.7k. Resolved.
- **The calibration trigger cannot be read verbatim anywhere.** What survives is a trail:
  - local directory names from 10-27/28: `resume-20261027-causal-improvement`, `-noncausal-development`, `-semantic-expansion`, and `resume-20261028-dataset-commission`, `-case-admission`, `-heldout-mechanics`, `-independent-label-sources`, `-post-dataset-audit-001..003`, all now empty;
  - ticket 168:9, "delegating a labelled evaluation corpus and a dedicated pilot custodian";
  - the programme's own numbering in `implementation-20261030/` (ticket01 reference admission, 02 pinned smoke, 03 actor binding, 04 population custody, 05 Linux backend and signals, 13 protected consumer and role history).
- **Calibration, qualification and task sessions (10-30).** Plain sentence: software that freezes a model, its configuration and its population, then scores the model on four judgement tasks so it could earn a permission. Trigger: could not determine (trail above). The only owner words are "Approve stronger plant checks" (2026-10-30, docs/qualification-bindings.md:60), approving one scorer change inside the programme. Lines: 12,568 (rows 15 and 17). Merged (PRs #287, #288, #290, #295, #296). Unfinished: no population, no capture, no permission.
- **Source-native observation and PDF comparison (10-31).** Plain sentence: prove which PDF bytes produced each byte of extracted text by tracing the converter's file reads and comparing an instrumented Xpdf against a pristine one. Trigger: could not determine. It serves the task inputs' "exact member/UTF-8 span lineage" (contract.md:11). Lines: 17,272. Partly merged (PRs #299, #301-#303). 19 branch tips are unmerged (16 PDF, 3 native observation).
- **Linux lease and ELF closure (10-30/31).** Plain sentence: a root-installed harness that would run the model process on a Linux host with memory, network and teardown limits, plus CI code that identifies the exact shared libraries (ELF NEEDED/SONAME) such a process loads. Trigger: could not determine. LINUX-BACKEND.md says the Mac smoke is historical and Linux is the target. Lines: 11,659 incl. backend. Partly merged (#289, #298, #300). 12 tips are unmerged.

**(2) "Because" chains back to the loop.**
- **Observation delivery: 3 links, intact for evidence only.** Observations exist, because the clock samples the enacted cage; delivery lands them past branch protection; X can read them. It never changes Q, C or R ("conserves measurements without changing prices, grades, policy", ADR-0037:20).
- **Owner policies: 2 links, intact.** Floor raised to isolated, so R; the residual is recomputed, so C. Driftwood's residual fell £13,815. At E the cost is zero rather than broken. d2c6f83 touched only HEADER, HANDBOOK, evidence and floor-change. The 10-23 gitops pointer commits (beaeeb9, 89a2535) select the new signed releases, but the policy bodies in them are unchanged, because the namespace was already isolated ("Namespace remains isolated", party.yaml).
- **Recovery-expense: 4 links, broken at the first.** Recovery cost is real money, so it belongs in Q, so T/C would see it. But it is "excluded from ordinary headline pricing" (party.yaml) until 2027 outcomes exist.
- **Publisher reliability: 4 links, broken at link 2.** A score would weight publisher prices, which would change Q. No enrollment and no outcomes exist, so no weight is applied (hub a8c36d32).
- **Causal grade fix (168): 3 links, intact.** Grade sets price width, which sets Q. It may move widths ("A corrected unsupported grade may change its grade-derived width", issues/168:17). Measured effect: could not determine.
- **CVE pricing (153): 2 links. It harmed C for two adopters.** A CVE from the adopter's own scan is priced into Q, and it is in Tuppence (£437,107). For Driftwood and Ludlow the CVE amount is `null`, so the line is unpriced and untiered, and the aggregate becomes a "PARTIAL sum and no verdict can be given" (driftwood composed/HEADER.yaml:1369-1381).
- **Cloud plane 151: 3 links, intact.** Crossplane resources are part of what Tuppence runs, so cloud cages constrain them (R/E). Admission was observed in KinD on TRUTH 450. Whether this moves Q could not be determined: no cloud line appears in Tuppence's aggregate.
- **Engine 147-150: 2 links, intact for E only.** The cage must compile on the engine that enforces it, so the incompatible windows are retired and Kyverno is advanced to 1.19.1 for Ludlow (2115b34). No Q or C change.
- **Inventory 155 and incumbent 156: 3 links, broken at link 3.** Served workloads are what the cage must cover, so inventory joins risks to workloads. The 10-23 sample still has "two missing risk joins/empty risks" (map.md:310). Incumbent archiving (156) has no loop link: it retires old repositories.
- **Twin cage, clock and release: 2 links, broken.** The twin agent runs in its own cage, and the twin cage aggregate fails on an unmeasured proof. This cages the assistant, not the adopter, so it does not join the loop.
- **Insurer disclosure 162: 0 links.** It states that the quote is illustrative.
- **Pound-seam, can-record, default record (163/166/167): 0 links.** These check the gate's own SKIP lines and the ref that records land on.
- **The dump: 0 links.**
- **Calibration: 7 links, broken at link 1.**
  1. A qualified model could replace the heuristic in a skill.
  2. That skill's output feeds the twin's forward-intel feed or a causal grade.
  3. Forward-intel is a priced line.
  4. Price moves Q.
  5. Q goes to C.
  6. C drives R.
  7. R goes to E.

  The chain breaks at link 1 (the registry is empty; one developmental case is demonstrated; ADR-0029 wants about 326 per skill). It also breaks at link 2, structurally: no non-test caller imports qualification, pdf_*, linux_candidate or task_sessions. Only bench/, tests/, `.claude/skills/classify-and-judge/assets/validate_claim.py` and `verify/model-permission` do, and that check resolves the empty registry. No adopter or platform file imports any of them. The task contract itself denies link 6 and onward: "No model output grants ... pricing, override, enactment" (contract.md:21). Task sessions (row 17) sit at link 1. Native observation (row 20) sits below it (see the next chain).
- **PDF / ELF / native observation: 10 links, broken at link 6. No link has run.** This chain sits below calibration link 1.
  1. A text excerpt was extracted from a PDF with `pdftotext`.
  2. To trust it as model input, its bytes must trace to the PDF.
  3. So Xpdf is patched with `TwinOrigin` to emit origin events.
  4. The patched build must be compared with a pristine build to show the patch changes nothing else.
  5. Both builds must happen on pinned Linux.
  6. The binaries' shared-library closure (ELF NEEDED/SONAME) must be pinned.
  7. The converter's actual file reads must be traced (ptrace).
  8. The excerpt then becomes admissible metadata.
  9. The metadata goes into a task input.
  10. That joins calibration link 1.

  "All actual native questions remain unrun until separately authorized genuine Linux builds" (docs/pdf-comparison-capture.md:3).
- **Tiny Linux lease: 4 links, broken at link 2.**
  1. A qualified model must run caged.
  2. So a root-installed lease limits its memory, network and lifetime.
  3. The model can then run on a Linux runner.
  4. Its answers can then be captured for qualification.

  Link 2: "No Linux model execution ... is established" (LINUX-BACKEND.md:3-6). The CI step runs the controls with "no model" (twin.yml:136).

**(3) What calibration calibrates.**
- The subject is the six twin skills: signal-classify, causal-claims, evolution-judge, substrate-generator, gameplay-lens and ethics-gate (twin/skills.py docstring). Four are task-contracted: evolution, causal, gameplay and ethics (twin/task_contract/prompts.json).
- The candidate is Qwen/Qwen3-4B-Instruct-2507 at revision cdbee75f, run on CPU and offline (profiles.json).
- The yardstick is ADR-0029 point 10. The candidate must hold a permission on all ten conditions, on a corpus it was not fitted on and large enough to be falsifiable ("ticket 03 derived 326 items per skill"). It must score strictly above the best constant answer, with pinned weights and runtime, entering through `twin/skills.py`.
- The only corpus visible in tracked files is the offline demonstration in docs/reference-case-admission.md: one developmental case, a Wardley map coordinate of 0.27 from Piffio's map. Of its 46 selection decisions, four were admitted and 42 withheld. Measured against the twelve-item floor it reports "not-measurable, passed=false". The commissioned labelled dataset (resume-20261028-dataset-commission) is not readable: the directory is empty.
- Why PDF, ELF and Linux are involved:
  - The task inputs carry publisher metadata, excerpts and spans (contract.md:11).
  - Publisher documents include PDFs, extracted with Xpdf `pdftotext`.
  - To claim an excerpt's bytes really came from the PDF, the programme patches Xpdf with `TwinOrigin` and compares pristine and patched builds.
  - That needs a Linux build (CONTRACT.md: `xpdf-4.06.tar.gz`, `/usr/bin/gcc`, a 31-minute CI step), an ELF/SONAME closure for the converter binary and ptrace file observation.
  - The "tiny Linux lease" is a separate privileged cage for running the model itself (cgroup memory, network denial, guardian teardown).
- Map.md "Out of scope", for the reader to set beside this: "A corpus bought or built to support a specialised fit of a candidate model ... the zero-shot number is at or below a constant answer on five of six metrics, so a fit has nothing to improve on."

**(4) Branches and worktrees.**
- Local branches: 293 in total, 182 not merged into local main (78fdf0a2, 2026-10-23). 134 have tips dated on or after 09-27, and 105 of those are not merged locally: calibration/* 53, source/* 27, impl/* 14, fix/* 9, integrate 1, ci 1.
- Checked against the FRESH remote main, 74 of those 105 are merged there (71 tips are ancestors of FRESH HEAD, 3 match by commit subject), and 31 tips are not reachable. Revision chains supersede one another, so "not reachable" does not mean lost. All 31 are 10-30/31 calibration work: 12 tiny Linux lease control revisions and integration or merge-proof branches, 16 PDF / native bridge / capture-storage / remap, and 3 native observation.
- Registered git worktrees: 215, of which 214 are prunable. 74 sit under LOCAL/.scratch/worktrees, 52 of them calibration.
- Directories under .scratch/worktrees: 215 in all, holding zero regular files between them. 128 contain a `.git` directory skeleton (hooks, info, logs, objects, refs, with no files). Their repo identity cannot be read. The other 87 have no `.git`, including all 52 calibration directories.
- Grouped by name:

  | workstream | worktree dirs |
  |---|---|
  | calibration | 53 (52 + ci-macos15) |
  | observation delivery, clock, twin-cage | 33 |
  | engine/compiler | 32 |
  | inventory/CVE/workloads | 28 |
  | ticket records | 15 |
  | publisher reliability | 14 |
  | owner policies + feeds 4.1 | 14 |
  | cloud 151 | 12 |
  | insurance | 11 |
  | incumbent | 1 |
  | other | 2 |

**(5) What changed the money figure, tolerance, cage or enactment.**

| adopter | money figure (10-04) | verdict (10-04) | tiers / residual (10-23) |
|---|---|---|---|
| Tuppence | total £9.50M → £102.87M | `true` → still `true`; residual £190k → £2.06M against £15k tolerance | unchanged |
| Ludlow | total £10.13M → `null`; priced subtotal £3.07bn | `true` → `null` | unchanged |
| Driftwood | total £3.70M → `null`; priced subtotal £1.81M | `true` → `null` | threat-register and forward-intel baseline → isolated; residual £49,965 → £36,150 |

- **Money figure, 2026-10-04.** The handoff delivery ("adopt authenticated policy7 and primary inventory inputs") produced the changes in the table: tuppence c70edb1, ludlow 4f81da7, driftwood aa92363. The same commits added `pricing_threshold: 3` to all three appetite blocks (`git log -S`). Ticket 168 (10-27) may have changed grade-derived widths; the size of that effect could not be determined.
- **Tolerance.** Never changed. The diffs of all three party.yaml files since 09-27 show no `tolerance:` change (40k / 15k / 5k). The new `assurance_bands` are read only by platform party/ (assurance_bands.py, party_artefact.py, schema) and break-glass/ (break-glass.py:79-86, :135), in offline access decisions. A full grep of platform, hub and the adopters found no other reader.
- **Cage, 2026-10-23.** Owner policy set `floor: isolated` everywhere. Only Driftwood's tiers and residual moved (shown in the table).
- **Enactment** (gitops/ plus composed/, excluding feeds, evidence and HEADER) changed on these dates:
  - 10-03/04 in all three: digest-pinned apps, then policy7 and composition B.
  - 10-17 and 10-22 in Tuppence: the signed cloud composition and cloud 1.0.1 route (fd034c0, 057bd08).
  - 10-17 in Ludlow: retirement of the v5.0.0/v6.0.0 policy windows (ce5213f) and Kyverno advanced to 1.19.1 (2115b34).
  - 10-21 in Driftwood: promotion to the signed v5 release (598a838).
  - 10-23 in all three: pointers to the new signed releases. The policy bodies in those releases were not changed by the owner adoption.
- **No change at all from:** calibration, PDF, Linux, observation delivery, publisher reliability and recovery-expense left all four untouched.

## What the loop would lose if this area vanished
- **The 10-23 isolated floor and workload cage declarations** (row 11). This is the one October R step. Driftwood's threat-register and forward-intel lines would fall back to baseline, and its residual would rise by £13,815.
- **The 10-04 delivery of size, policy7 and CVE inputs.** This is September's work, but Codex landed it. The current money figures would revert, and the null verdicts would go with them.
- **Observation delivery** (row 3). Daily observations would stop landing on protected main. TRUTH is the only evidence that the enacted cage is sampled.
- **The causal grade fix.** Over-graded evidence would again narrow price widths.
- **Nothing else.** Calibration, PDF, ELF, Linux, publisher reliability and recovery-expense have no operational caller and changed no number. The 1.34M-line dump and the reconciliation records feed nothing.

## The simplest thing that would do this area's loop job
These are proposals, not existing files.
- **`floors.yaml`, about 20 lines.** One file per estate holding each adopter's tolerance and floor tier, as owner-signed data. It replaces rows 11, 2 and 5.
- **Compose change, about 30 lines.** When a line's amount is `null` (CVE for Driftwood and Ludlow), print `verdict: unknown because <line> has no price` next to the partial residual, and add a `verdict_if_excluded: within/above` field. The owner then sees that Driftwood's priced residual (£36,150) is under £40,000. Better still, fix the input that leaves the CVE amount null. Why it is null could not be determined.
- **`observe.yml`, about 60 lines.** One workflow that writes the daily sample to a dedicated `observations` branch, or to an artifact, instead of protected main. It replaces the 6,734-line delivery controller and ADR-0037's second identity.
- **Model qualification, about 150 lines, only if the owner still wants it.**
  - A CSV of at least 326 human-labelled items per skill.
  - A `score.py` of about 100 lines that runs the existing `skills.evaluate`, then compares the result with the constant baseline.
  - Run it locally with `sandbox-exec` (macOS) or `unshare -n` (Linux) to deny network.
  - Store input excerpts by SHA-256 of the source PDF plus page and offset, and have a human spot-check them.
  - That replaces rows 15-22 (49k lines). Instrumented Xpdf, ELF closure and ptrace tracing are not needed when the excerpt is pinned by hash and reviewed.

## Surprises
- **Authored work stopped on 2026-10-31.** Since then only bots have committed: 11 TRUTH records in the hub between 11-01 and 11-12 (merged as PRs #305 to #315) and daily drift samples. The local `calibration-programme/current-state`, `issues` and `review` directories are empty. The 10-17 to 10-28 resume directories contain only `.DS_Store`. The programme's charter, ticket list and owner ask cannot be read anywhere.
- **Tuppence's biggest line is the twin's own forward-intel feed:** £84.2M of £102.9M, and a residual of £1.68M of £2.06M even at isolated. Tuppence breaches its £15k tolerance at the strictest tier. The ratchet is exhausted, and no October work addressed it.
- **The 10-04 delivery turned two adopters' explicit breach into "no verdict".** That came from adding a CVE line whose amount is `null` (unpriced, so untiered). It is recorded as a could-not-look, not treated as a regression.
- **The new verdict fields are inconsistent.** Driftwood's residual (£36,150) is now under its £40,000 tolerance, but `breaches_band` is `null`. The one adopter that might be inside tolerance cannot say so.
- **The calibration code hardens a gate around an empty registry.** About 49k lines of protected custody and authority code (HMAC refusal keys, noncopyable capabilities, 8 GiB suite ledgers) serve a qualification that has one case and no population.
- **The calibration contract packet runs to 4,162 lines and calls itself "PROPOSAL ONLY ... unimplemented and unexecuted".** It specifies a single unauthenticated GET of `xpdf-4.06.tar.gz` down to header byte caps.
- **The handoff dump commits about 1.34M lines of agent intermediate files into git.** That is about 20 times all the code written in the period.
- **Origin cannot be read from git.** Every authored commit is "Chris". Codex shows only through `codex/...` branch names (10-24 to 10-27) and the phrase "Codex integrator" in records.
- **The tiny lease CI step is described inconsistently.** TINY-CI-CONTROL.md calls it "TEST_ONLY source", LINUX-LEASE-CONTROL.md says "No workflow is changed by this source", yet `.github/workflows/twin.yml:136` runs "native tiny lease controls; no model" on both Ubuntu rows.
