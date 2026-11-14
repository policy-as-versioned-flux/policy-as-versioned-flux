# H6 - twin capabilities, invariants, README, release docs (hub/twin)

## Summary
- Area: 22 files, 10,749 lines (wc -l). 7,353 are the invariant suite, 666 are capability checklists, 3,210 are twin/README.md, 186 are calibration + release docs.
- None of it quantifies, compares, ratchets or enacts. It is a verification and self-description layer about the twin code that lives elsewhere (twin/*.py, not in this area).
- 13 capability files = 13 checklists of acceptance criteria copied from decision tickets; all 13 (76 criteria) are ticked. 16 invariants in manifest.yaml, all state: live, 0 pending.
- "Grade" = twin/grades.py (245 lines, outside area): a capability is stub/partial/full by counting ticked criteria against the owning decision ticket in .scratch/twin/issues. Consumed by invariant every_capability_depth_graded and stamped into every emitted artefact. Self-referential: it grades build progress, not risk.
- Loop relevance is thin: ~4 invariants (ruin_class_absent_not_priced, prefilter_precedes_pricing, grade_5_only_path_never_prices, price_levels_never_probabilities) guard how money figures are produced; calibration.md is the only tolerance/quantify-adjacent document. No file here holds an appetite or tolerance value.
- The README itself records the suite as red: 2 failing checks, one of them "unreachable since 2026-08-16" (twin/README.md:2671-2678).

## Components
Counts: wc -l. Born: first-add commit date. "Grade met" is per ticked checkboxes in file; I did not re-run grades.py or verify against .scratch/twin/issues.

| name | paths | lines | born | what it does | loop role | necessity | origin | status | cite |
|---|---|---|---|---|---|---|---|---|---|
| Invariant harness (79 checks) | twin/invariants/harness.py | 4935 | 2026-08-12 | 79 `@harness_check` functions behind `twin verify`: manifest completeness, hash pinning, ~60 behavioural checks on skills, forecast book, enactment, flux drift window, substrate, ethics gate | evidence | ceremony | assistant | tested_offline (README says 70 pass, 2 fail, 2 skip) | twin/invariants/harness.py:121; twin/README.md:2671 |
| Invariant checks (25 fns) | twin/invariants/checks.py | 1426 | 2026-08-11 | Bodies of the 16 manifest invariants, SHA-pinned by manifest | evidence | support | assistant | tested_offline | twin/invariants/checks.py; manifest.yaml:10 |
| Invariant manifest | twin/invariants/manifest.yaml | 170 | 2026-08-11 | Names 16 invariants, activating ticket, body hash, authorising decision ticket | ceremony | ceremony | assistant | tested_offline | twin/invariants/manifest.yaml:8-170 |
| Invariants package + digests | twin/invariants/__init__.py, golden-digests.json | 156 | 2026-08 | Shared banned-word constants; golden byte digests for determinism | evidence | support | assistant | tested_offline | twin/invariants/__init__.py |
| Capability checklists (13) | twin/capabilities/*.yaml | 666 | 2026-08-05..16 | One file per capability: criteria text copied from the owning decision ticket, each with checked + evidence prose + ticked_by | ceremony | ceremony | assistant | tested_offline (all 76 ticked) | twin/capabilities/causal-layer.yaml:1; grades.py:123 |
| Twin README | twin/README.md | 3210 | 2026-08-12 | Per-feature narrative: loop, pre-filter, propagation, backtests, forecast book, ethics, enactment, "what is honestly built", "what is not built" (L2846-3128), layout | presentation | ceremony | assistant | unknown (prose) | twin/README.md:88,2184,2671,2846,3129 |
| Calibration procedure | twin/calibration.md | 69 | 2026-08-06 | Five-step discipline for authoring PERT min/mode/max as a 90% interval; artefacts pin its digest | quantify | support | assistant (build ticket 23 from decision tickets 08/09; no owner quote found) | written_never_run as a human procedure; code pinning not checked | twin/calibration.md:1-69 |
| twin release doc | twin/RELEASE.md | 47 | 2026-08-29 | Version = twin/VERSION; tag twin/v0.1.0 "not cut yet"; adopter PIN.yaml | ceremony | ceremony | assistant | written_never_run (tag state as of file; docs/twin-release.md of 2026-10-23 describes the cut workflow) | twin/RELEASE.md:21-24 |
| Signed-release doc | docs/twin-release.md | 70 | 2026-10-23 | gitsign tag cut via cut-release.yml; certificate subject pinned | evidence | ceremony | codex (Oct recovery/assurance era; commit author not checked) | could not determine whether cut ran | docs/twin-release.md:1-30 |

## Capabilities (one line each; all 13 checklists fully ticked; "graded met" = every criterion checked in file)
| capability | owning decision ticket | criteria | loop role | graded met |
|---|---|---|---|---|
| domain-model | 07 | 7/7 | quantify (ontology the exposure sits on) | yes |
| sense-move | 11 | 8/8 | react (signals bound to components) | yes |
| causal-layer | 08 | 5/5 | quantify (edges with elasticity triples; counterfactual do/observe) | yes |
| currency-regimes | 09 | 6/6 | quantify (the money unit, ruin/forbidden constraint class) | yes |
| scenario-engine | 13 | 7/7 | compare/react (fast-forward, rewind, play) | yes |
| forecast-book | 21 | 6/6 | evidence (blind pinned forecasts, scoring) | yes |
| synthetic-substrate | 12 | 7/7 | evidence (fake world to test detection) | yes |
| enactment | 18 | 5/5 | enact (propose-only; verdict on policy-as-versioned-dependency) | yes |
| ethics-gate | 15 | 5/5 | none (sensor admission, DPIA; a constraint on the twin) | yes |
| provenance | 14 | 4/4 | evidence (attestation, actor identity) | yes |
| twin-inside-twin | 10 | 5/5 | ceremony (twin models itself, threat model) | yes |
| honest-build | 20 | 4/4 | ceremony (skill vs code inventory) | yes |
| demo-slice | 22 | 4/4 | presentation | yes |

## Invariants (16 in manifest, all `live`)
| invariant | activating ticket | asserts | loop role | graded met |
|---|---|---|---|---|
| store_rebuildable_from_git | 01 | derived index rebuilds from repo | evidence | live; TWIN verify says pass (README 2671) |
| identical_pins_identical_bytes | 02 | same pins give same bytes | evidence | live |
| every_artefact_marked | 03 | authored/derived mark on all artefacts | ceremony | live |
| every_capability_depth_graded | 03 | depth grade is computed, never typed | ceremony (this is the grading consumer) | live |
| world_never_references_overlay | 04 | layer direction | none (model hygiene) | live |
| no_collapse_mechanism | 06 | multiple forecasts never collapsed to one | none (anti-scalar stance; cuts against a single exposure number) | live |
| no_recommended_action_field | 06 | no recommended-action field | none; note: forbids the ratchet step R being output | live |
| derived_never_human_signed | 11 | derived artefact refuses human signature | evidence | live |
| only_as_consumed_scores | 08 | only as-consumed forecasts are scoreable | evidence | live |
| no_special_category_slot | 12 | no schema slot for special-category data | none (privacy) | live |
| grade_5_only_path_never_prices | 19 | weak-evidence-only causal path gets no price | quantify (guard) | live |
| ruin_class_absent_not_priced | 28 | ruin option removed, not priced | compare/cage (guard) | live |
| prefilter_precedes_pricing | 28 | constraints filter before pricing | cage (guard) | live |
| as_consumed_admits_no_post_T_fact | 36 | no post-T fact in as-consumed run | evidence | live |
| price_levels_never_probabilities | 59 | market prices enter as signals | quantify (guard) | live |
| standing_library_covers_committed_classes | 69 | scenario library covers every class | evidence | live |
Note: the harness enforces further ~60 checks beyond the manifest (e.g. enactment_is_propose_only_at_both_layers, flux_coverage_floor_is_still_reachable, honest_build_inventory_matches_files_and_owning_tickets).

## What "grade" machinery consumes these
- twin/grades.py:123 `_load_one` reads each capabilities/*.yaml; :170 `_validate_against_ticket` re-checks criterion text against `.scratch/twin/issues/<n>-*.md` (grades.py:21) when the ticket tree exists; stub/partial/full derived from checked count; `worst()` (:244) rolls up.
- Invariant every_capability_depth_graded refuses a typed grade; manifest.yaml:37.
- Grep shows grades referenced in registration.py, sensor_admission.py, synthetic.py, retrospective_sweep.py, ingest.py, does_not_do.py, skills.py, benchmark.py (they stamp depth grade into emitted artefacts). I did not read these.
- A SEPARATE meaning of "grade" is the 1-5 evidence ladder on causal edges (grade_5_only_path_never_prices); do not conflate. That one is loop-relevant (quantify); the capability depth grade is not.

## What the loop would lose if this area vanished
- Q/T/C/R/E/X: nothing runs. No file here computes exposure, stores a tolerance, compares, ratchets or enacts.
- It would lose: four guards on how money is produced (ruin not priced, pre-filter before pricing, weak evidence unpriced, market price not a probability), the determinism and as-consumed leakage checks (trust in any back-test), and calibration.md's interval discipline for the inputs.
- Everything else (11 other manifest invariants, 13 checklists, the README, release docs) is trust-in-the-build and narration; the loop would be unaffected, though the owner would lose the 70-pass/2-fail status reading.

## The simplest thing that would do this area's loop job
One file, `twin/checks.py` (~150 lines), of about six assertions run in CI: (1) same inputs give same exposure bytes; (2) exposure artefact has a money field and a confidence interval from a triple; (3) a ruin-class option is absent not priced; (4) an exposure figure cites evidence grade <=2 or is flagged unpriced; (5) no fact dated after T enters a back-test; (6) a tolerance record exists and compare() output references it. Keep calibration.md as is (69 lines). Replace 13 capability YAMLs and the README with a ~100-line README of the loop. Drop the manifest hash-pinning and depth grading. Total ~300 lines versus 10,749.

## Surprises
- Capability checklists are graded "full" by ticked checkboxes whose evidence is prose written by the same agents who built it; the checkbox is a claim, not a measurement (e.g. causal-layer criterion 5 ticked by build ticket 81).
- The manifest records an authorisation ceremony: every changed check body needs `authorised_by` citing a decision ticket, with SHA-256 pins (manifest.yaml:1-10). The code polices its own edits more than it polices exposure vs tolerance.
- no_recommended_action_field and no_collapse_mechanism forbid the twin emitting a single answer or an action, which structurally forbids a ratchet-recommendation. The ratchet is not in the twin's remit by design. Enactment is propose-only (harness check name; capabilities/enactment.yaml).
- README is 3,210 lines, with "What is not built" alone ~280 lines (L2846-3128) and a section titled "The confirmatory audit was not confirmatory" (L2598).
- README records 2 red checks as expected, including flux_coverage_floor_is_still_reachable "red since 2026-08-16" (L2671-2678); the "verify" figures (70 pass) are stale versus the 79 harness functions now present (I counted function defs by @harness_check lines: could not reconcile exactly).
- Release: RELEASE.md (2026-08-29) says tag twin/v0.1.0 is not cut; docs/twin-release.md (2026-10-23) describes a signed cut workflow. Whether the tag exists: could not determine (read-only, no git ls-remote).
- twin.yml runs the invariant suite as a CI job requiring a clone of six unit repos (twin.yml:24-40): the verification of the twin depends on the estate repos.
