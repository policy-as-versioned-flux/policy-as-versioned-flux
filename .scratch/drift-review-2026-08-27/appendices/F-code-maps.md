# Appendix F — Code maps: what is real, what is thin

## twin — twin-causal-and-wardley

### Real

- twin/propagate.py:239-252 — seeded PERT Monte-Carlo draws per edge (not per path), 2000 draws, deterministic by (seed, origin, edge id) so traversal order cannot affect the sample; verified by tests/test_seam2_propagation.py::test_the_sample_is_reproducible_and_independent_of_traversal_order
- twin/propagate.py:296-332 — genuine composed (exact product) vs attenuated (schedule-scaled) vs sampled (Monte-Carlo) triple computation per path, with an overflow-of-unit-interval guard (line 304-316) that would otherwise silently invert the noisy-OR combination; verified by tests/test_seam2_propagation.py::test_the_composed_triple_is_the_point_wise_product, test_uncertainty_compounds_rather_than_being_averaged_away, test_an_influence_above_one_is_refused_where_it_would_reverse_the_combination
- twin/propagate.py:369-500 — exact shared-ancestry dependence correction via inclusion-exclusion (2^n subsets, capped at MAX_EXACT_PATHS=10) and E[X^n] raw-moment computation for edges appearing multiple times, alongside a sampled joint that also carries dependence; verified by tests/test_seam2_propagation.py::test_shared_ancestry_does_not_double_count, test_the_dependence_correction_is_exactly_the_common_cause_variance, test_the_exact_form_stops_at_its_declared_bound_and_says_so, test_the_sampled_joint_carries_the_dependence_too
- twin/propagate.py:503-579 — full graph walk with simple-path enumeration, depth cap (5), per-component path cap (32) ranked best-evidenced-first before truncation, and closed-body validation (refuse_undeclared_keys, refuse_directional_magnitudes); verified by tests/test_seam2_propagation.py::test_too_many_paths_to_one_component_are_capped_and_the_cap_is_disclosed, test_a_cycle_is_traversed_once_and_the_pruning_is_disclosed, test_the_propagation_body_is_closed
- twin/blast.py:116-202 — reverse dependency traversal (BFS/DFS, simple paths, depth cap 6) that classifies every reached component as priced / below-threshold / no-mechanism, tracking the best-ranked path per component; verified by tests/test_admission.py::test_a_reputation_impact_with_a_churn_path_prices, test_the_same_impact_without_a_path_returns_a_blast_radius, test_the_same_path_too_weakly_evidenced_does_not_price
- twin/wardley.py:83-96 — exact D/K/R Wardley formulas, bit-identical float arithmetic (no quantisation, deliberately, per module docstring); verified by tests/test_wardley.py::test_the_inherited_worked_examples_still_hold, test_differentiation_pressure_over_the_whole_grid, test_commodity_leverage_over_the_whole_grid, test_dependency_risk_over_the_whole_grid
- twin/positions.py:73-93 — pairwise belief-delta computation and proper scoring rule (Brier/log-loss, delegated to twin/scoring.py) against revealed truth; verified by tests/test_positions.py::test_pairwise_deltas_are_computed_for_every_pair, test_against_revealed_matches_the_proper_score
- twin/causal_claims.py:73-85 — shared_ancestors(): a genuine one-hop structural confounder detector over the merged graph's adjacency; verified by tests/test_causal_claims.py::test_shared_ancestors_finds_the_real_confounder_on_the_netflix_co_flagship_edge, test_shared_ancestors_finds_the_real_confounder_on_the_intel_co_flagship_edge
- twin/primitives.py:95-137 — _ancestor_paths(): real breadth-first shortest-path search bounded by depth, deliberately linear-cost rather than exponential simple-path enumeration; verified by tests/test_primitives.py::test_the_upstream_walk_handles_depth_grades_and_cycles, test_the_upstream_walk_says_where_it_stopped
- twin/primitives.py:246-267 — rewind() opens a real git commit as of a given time via ModelRepo.open_at_time, not a filtered view; verified by tests/test_primitives.py::test_rewind_produces_a_model_state_rather_than_a_filtered_view, test_rewind_composes_with_intervention_without_special_casing, test_rewinding_before_the_model_existed_fails_explicitly
- twin/evidence.py:233-262 — unrecorded_changes()/history_violations(): a real git-history walk (repo.commits_touching, read_yaml_at) that detects grade changes not covered by a recorded regrade event; verified by tests/test_evidence_ladder.py::test_an_unrecorded_grade_change_fails_the_gate, test_a_recorded_grade_change_passes_the_gate
- twin/spine.py:125-170 — reconcile()/diff_against_spine(): real presence/absence checking of dated public facts against a generated substrate, with a demonstrated non-trivial anchored/free-running split on the real Carillion fixture; verified by tests/test_spine.py::test_the_diff_attack_does_not_locate_plants, test_over_anchoring_would_have_made_the_plant_the_unique_residual
- twin/challenges.py:44-104 — claim_path validated against canon.walk_values of the real artefact body; resolve() structurally reads claim_path from the challenge doc rather than accepting one as a parameter; verified by tests/test_challenges.py::test_a_challenge_to_an_unknown_claim_is_refused, test_resolve_inherits_the_challenges_own_claim_path

### Thin or stubbed

- twin/causal_claims.py:96-165 — sign/grade/lag/elasticity are all keyword-marker heuristics (_NEGATIVE_MARKERS/_POSITIVE_MARKERS/_GRADE_MARKERS/_LAG_MARKERS), explicitly ponytail-marked at line 35-42; elasticity magnitude is a hardcoded mode (0.375) with a grade-scaled width, not fitted from data at all ('Elasticity magnitude is not even keyword-fitted', line 39); upgrade path stated as 'swap the body for a model call'
- twin/evolution_judge.py:64-98 — _infer_position() is a keyword lookup (_MATURITY_KEYWORDS) fitted to exactly the 4 backtest orgs' own component descriptions, explicitly ponytail-marked at line 18-23; default 0.5 when no keyword hits
- twin/gameplay_lens.py:16-25 — the play catalogue covers only 2 of Wardley's ~100+ named gameplay patterns (land-grab, exploit-commoditisation), explicitly ponytail-marked; the worked-example's incumbency precondition ('no incumbent holds position') is never checked because the map carries no rival-occupancy data — every land-grab reason states 'Incumbency is not checked' (gameplay_lens.py:113-114)
- twin/wardley.py:13-26 — arckit's action bands ('must invest', 'strong candidate for outsourcing') are deliberately excluded (inherited_from note says action_bands_inherited: False at line 177); arckit's £ deltas are prose-only and are explicitly not entered here ('No money enters through this module')
- twin/gameplay_lens.py:33-37 — a proposed opportunity carries a claim-shaped dict but does not round-trip through the real schema.SCHEMAS['claim'] validator; nothing exercises writing it into a model repository

### External integrations

- twin/primitives.py rewind() and twin/evidence.py history_violations()/unrecorded_changes() perform real git I/O (via twin/repo.py's ModelRepo — commits_touching, read_yaml_at, open_at_time), not simulated — the model repository itself is a git repo
- twin/wardley.py is a deliberate one-time port of formulas/bands from an installed arckit plugin (~/.claude/plugins/cache/arc-kit/arckit/6.7.5/); at runtime there is no live call into arckit — the code and constants are copied in, with the three caveats about what was NOT inherited (action bands, impact history, £ formulas) documented in the module docstring
- twin/blast.py explicitly inherits its algorithm and known limits from the /arckit:impact skill (module docstring, line 3) but again as a ported implementation, not a live invocation
- No Flux, Kubernetes, GitHub, gitsign, prediction-market, or news-feed integration appears in any of these 15 files; twin/challenges.py references human signing (twin/sign.py) for challenge/resolution artefacts but does not itself implement signing

### Fixture-only

- twin/causal_claims.py:299-331 — the whole causal-claims labelled corpus is 4 hand-authored evidence statements for netflix (streaming-displaces-dvd, cdn-capacity-lifts-streaming, price-separation-erodes-goodwill) and intel (euv-delay-slips-the-node)
- twin/evolution_judge.py:234-239 — labelled_corpus hardcodes one component and one expected evolution_position per backtest org: Carillion 0.62, NMC Health 0.55, Wirecard 0.8, Enron 0.45
- twin/gameplay_lens.py:305-331 — labelled_corpus hardcodes netflix streaming-experience (land-grab positive), intel foundry-services (negative case), pocket-org shared-database (exploit-commoditisation positive)
- twin/attenuation.yaml:26-43 — the depth-decay factors (1.0, 0.8, 0.6, 0.4) and directional_beyond_depth=4 are fixed published constants, not derived from data
- twin/evidence-ladder.yaml:25,40 — pricing_threshold=2 and path_admission_threshold=2 are fixed published constants
- twin/causal_claims.py:158 — _BASE_MODE = 0.375 is stated to be the mean of the module's own 4-item labelled corpus's real elasticity modes, i.e. a constant reverse-derived from the fixture rather than an independent model

**Notes:** This cluster is the causal/Wardley reasoning core of the twin, sitting above twin/model.py (Graph/Overlay/Edge) and twin/pert.py (PERT sampling primitives), and below twin/skills.py (the seam that runs skill_fn callables like causal_claims.propose, evolution_judge.judge/override, gameplay_lens.propose against labelled corpora with pass/fail thresholds). Three of the fifteen modules (causal_claims.py, evolution_judge.py, gameplay_lens.py) are explicitly self-described 'skills' whose classification logic is a small keyword heuristic standing in for a future model call — each says so in its own module docstring and marks the exact lines with a `ponytail:` comment, and each states the same upgrade path: swap the heuristic body for a model call with no change to the harness, tests, or callers, because the skill contract is a bare callable. The propagation/dependence machinery (propagate.py, blast.py, causal_accounts.py) and the maths/data modules (wardley.py, positions.py, evidence.py, evidence-ladder.yaml, attenuation.yaml) are genuine deterministic algorithms with dedicated, non-trivial test coverage exercising the actual numeric properties claimed (sub-additivity, exact-vs-sampled agreement, reproducibility, gate consistency). Two modules (spine.py, challenges.py) implement structural governance/audit mechanisms (fact reconciliation against a real git-derived spine; claim-path-scoped contestability) rather than statistical/optimisation algorithms, and both are exercised against real fixture data (the Carillion backtest for spine.py) rather than only synthetic inputs.

## twin — twin core model/schema/repo/CLI + provenance-and-honesty scaffolding (schema.py, model.py, repo.py, verbs.py, cli.py, __

### Real

- twin/schema.py:447-465 Schema.validate — real closed-schema validation (unknown/missing field detection), exercised by tests/test_schema.py (undeclared field, missing required field, identifier format tests)
- twin/schema.py:468-501 refuse_special_category / _article_nine — real word-boundary substring matching over a 30+ term Article 9 denylist, applied recursively to keys and values at arbitrary depth; exercised by tests/test_schema.py::test_every_article_nine_category_has_nowhere_to_go (parametrised over all SPECIAL_CATEGORY terms) and test_respelling_the_category_does_not_help (camelCase/kebab/underscore normalisation) and test_it_cannot_be_hidden_inside_a_free_form_container
- twin/schema.py:154-167 probability() — real strict-inequality gate refusing probability 0 or 1 (infinite log-score penalty), exercised by tests/test_schema.py::test_a_belief_of_certainty_is_refused
- twin/repo.py:252-290 ModelRepo.open_at_time / parse_moment — real git-history time-travel (rev-list --before) with explicit epoch-window and unparseable-date refusal to stop git's silent 'falls back to now' behaviour from producing a wrong-but-confident historical answer
- twin/repo.py:57-72 SafeLoader — real YAML-alias refusal to stop anchor-bomb memory expansion
- twin/model.py:399-421 Overlay._check_regrades / twin.evidence.check_chain — real evidence-grade immutability chain verification (a grade cannot move without a contiguous, in-repo regrade record), exercised across tests/test_evidence_ladder.py
- twin/model.py:691-770 check_direction — real recursive scan of every world-tree file (keys, values, and free prose via a compiled org-id regex) refusing any reference from the world layer into an overlay/tenant, run over every world tree an overlay actually pins, not just HEAD
- twin/canon.py:15-29 canonical_json — real deterministic serialisation (sorted keys, allow_nan=False), exercised by tests/test_repo_and_envelope.py::test_canonical_json_refuses_values_that_are_not_portable and test_canonical_json_is_stable_under_key_order
- twin/artefact.py:84-91 refuse_forbidden_keys — real arbitrary-depth key walk refusing 'recommended_action'/'consensus'/'collapsed'/etc, exercised by tests/test_repo_and_envelope.py::test_a_recommended_action_field_is_refused_at_emission and test_the_refusal_reaches_arbitrary_depth
- twin/grades.py:40-75,151-188 acceptance_criteria + DepthGrade.grade + _validate_against_ticket — real markdown-checkbox parser and a genuinely computed (never typeable) grade, cross-checked against the live decision-ticket text on every load so the checklist can't silently drift from its own yardstick; heavily exercised by tests/test_grades.py (typed-grade rejection, drift rejection, nested-checkbox rejection, aggregate arithmetic vs README)
- twin/honest_build.py:199-274 validate_inventory / validate_owning_tickets — real cross-checks tying a hand-written classification table to actual files on disk and to twin.skills' determinism predicate, catching a self-contradictory kind/reproducible_from_pins pairing; exercised by tests/test_honest_build.py including a real assertion that ethics_gate.scorer()'s source never calls classify_gameability (grounds the code/skill reclassification in the actual function body via inspect.getsource)
- twin/does_not_do.py:29-52 register() — real pure derivation from Capabilities with no authored/typed path; exercised by tests/test_does_not_do.py including a live-not-cached test (checking one more AC removes exactly one register entry) and a completeness test against the shipped capability set

### Thin or stubbed

- twin/blob.py:1-8 module docstring: 'Nothing produces substrate yet — the reference *form* exists now because every later ticket writes into it' — the whole substrate-addressing mechanism is a placeholder type with no producer; every artefact currently carries the literal fixtures.ABSENT_SUBSTRATE sentinel (see twin/repo_and_envelope test at line 49 comparing against fixtures.ABSENT_SUBSTRATE, not a real substrate hash)
- twin/model.py:344-364 Overlay.forecast_subject — explicitly documents an un-ticked acceptance criterion: an enactment claim always returns None as the forecast subject ('decision ticket 18's AC 5 ... is unticked today') so a response being enacted can never make a forecast conditional on it yet
- twin/verbs.py:6-9 module docstring: 'Every capability here sits at partial, which means at least one of its owning decision ticket's acceptance criteria, not most of them' — verbs.py's own capability grades (sense-move, scenario-engine, currency-regimes, causal-layer) are explicitly disclosed as partial in places even though tests/test_grades.py shows the shipped set has since moved several of these to full — the disclosure mechanism (does_not_do.py) is what actually reports current gaps, not this docstring, which is now stale relative to the ticked grades
- twin/grades.py itself has no ponytail — but its entire reason to exist (build ticket 03 docstring) names 'premature done' / self-declared grades as the failure it exists to prevent, implying that failure mode was real practice before this module; the guard is real, the thing it guards against is documented as having happened
- twin/honest_build.py:22-43 explicitly documents leaving stale/inconsistent prose in place rather than rewriting it: 'the seam-3 eval harness ... still scores it as one — that existing machinery is untouched by this ticket, on purpose ... rewriting the six-skills prose ... would be a large, unrequested rewrite'; i.e. a known inconsistency between this module's honest classification and five other modules' docstrings/test expectations is left standing by design
- twin/verbs.py:632-656 _price_at / spread machinery reports 'attenuated modal price' only (mode of the propagated triple) — no full distribution is carried through to the price attribution table, only min/mode/max-derived point figures per component per perspective

### External integrations

- git (via subprocess in twin/repo.py) — real I/O: every read goes through actual `git` CLI calls (rev-parse, cat-file, ls-tree, rev-list, show) against a real repository on disk, with a hardened/scrubbed environment; not simulated, but scoped to local git only — no network, no GitHub API, no Flux, no Kubernetes anywhere in these 14 files
- No Flux, Kubernetes, gitsign, arckit runtime, prediction-market, or news-feed integration appears anywhere in schema.py/model.py/repo.py/verbs.py/cli.py/artefact.py/canon.py/blob.py/index.py/ontology.py/grades.py/honest_build.py/does_not_do.py or __main__.py — 'arckit' appears only as a provenance label in honest_build.py's CAPABILITY_INVENTORY (INHERITED_KIND entries for wardley.py/blast.py/schedule.py noting they were ported from /arckit:wardley etc.), not as a live dependency or call
- twin/cli.py cmd_sign calls twin.sign.human() (module not in this cluster) which tests/test_repo_and_envelope.py shows takes a raw bytes key material — this is a real signing code path (attestation sidecar gets a signature entry) but the key-material handling and whether it is HMAC or asymmetric was not independently verified in this pass since sign.py is outside the requested file list; cli.py's role is only to load the key via sign.signing_key(), refuse signing a non-authored artefact, and write the sidecar
- twin/repo.py explicitly scrubs GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE/etc and disables core.fsmonitor/core.hooksPath — real defensive hardening against a hostile or misconfigured local git config/environment, not a simulation

### Fixture-only

- twin/fixtures.py build_netflix_org / build_and_corroborate_netflix_org (line ~4860, ~5007) — Netflix exists only as a synthetic fixture org, referenced by id (e.g. component 'streaming-experience', 'dvd-by-mail', person 'alex-rivera'/'sam-okafor') in tests/test_schema.py and elsewhere
- twin/fixtures.py build_intel_org (~5414) — Intel fixture, e.g. signal id 'foundry-segment-loss-disclosed' referenced in tests/test_repo_and_envelope.py
- twin/fixtures.py build_carillion_org (~2086), build_wirecard_org (~2577), build_enron_org (~2805), build_royal_mail_org (~4291), build_kodak_org (~5612), build_maersk_org (~5762), build_nmc_health_org (~2344), build_astrazeneca_org (~3034), build_sanofi_org (~3227), build_pocket_org (~1426), build_twin_self_org (~3656, the twin-inside-twin fixture), build_library_org/build_standing_library (~4009/4038), build_regime_org (~1764) — all named real-world corporate-collapse or industry subjects (Carillion, Wirecard, Enron, Royal Mail, Kodak, Maersk, Intel, Netflix) exist in this codebase only as deterministic synthetic fixture data, never as live-fetched or user-supplied input; the modules in this cluster (schema/model/repo/verbs/cli) treat them as opaque org ids with no special-casing of the subject itself
- No £ amounts, evidence-grade numbers, or PERT triples in the 14 mapped files are themselves hardcoded business figures — those live in fixtures.py/YAML, not in this cluster; this cluster's own hardcoded values are structural constants (evidence ladder 1-5, GIT_EPOCH_YEARS 1970-2099, COMMITTED_SCENARIO_CLASSES, SPECIAL_CATEGORY denylist, FORBIDDEN_KEYS denylist)

**Notes:** This cluster is the spine of the whole `twin` package: schema.py + model.py + repo.py define what a model repository is and how it validates/loads; verbs.py + cli.py are the entire seam-1 command surface, each command producing a byte-reproducible pinned Artefact; artefact.py/canon.py/blob.py define the artefact envelope and its serialisation/hashing primitives; index.py is a rebuildable derived store; ontology.py/grades.py/honest_build.py/does_not_do.py form a self-honesty subsystem — grades.py makes 'depth' a computed fact tied to real decision-ticket checklists rather than a self-declared label, honest_build.py applies the same discipline to the code/skill/inherited classification of every capability (including correcting the project's own prior six-skill count), and does_not_do.py turns any unchecked grade into a disclosed gap with no authoring path of its own. verbs.py itself is mostly an orchestration layer over other twin modules (propagate.py, pricing.py, scoring.py, primitives.py, admission.py, regimes.py, credibility.py, options.py, corroboration.py) that were NOT in the requested file list, so claims about e.g. PERT sampling, TVaR, or Monte-Carlo propagation being 'genuinely implemented' rest on this cluster's evidence that verbs.py calls into and gates on those modules correctly (regime requirement, use-gate thresholds, mitigation-credit gating in score()) rather than on having read those modules' own algorithms in this pass. cli.py is very large (2133 lines) but almost entirely thin per-command wrappers plus argparse wiring; the only non-trivial logic inside cli.py itself is cmd_validate's history-violation printing, cmd_sign's authored-only refusal, and the citation-gated _rehash/_bless_goldens manifest-rewriting helpers.

## twin — twin-enactment-provenance-ethics

### Real

- Multi-layer propose-only enforcement: twin/enact.py public-surface allow-list ({propose, dependency_pins}) + twin/enact_guard.py PreToolUse regex/command refusal, both asserted live by harness `enactment_is_propose_only_at_both_layers` (twin/invariants/harness.py:3440) and unit tests tests/test_enact.py:45-178
- enact_guard.decide() genuinely parses git-push targets, resolves bare remotes via `git remote get-url`, and applies a real, tested carve-out (own-repo vs sibling-repo vs unresolvable-origin fail-closed) — twin/enact_guard.py:108-225, tests/test_enact.py:75-140
- HMAC-SHA256 signing with two non-interchangeable typed signatures (human=accountability, agent=origin), role-register binding, personal-field refusal, and derived_never_human_signed enforced at both build() and check() (twin/sign.py, twin/attest.py), tested in tests/test_signing.py (real crypto verification, real tamper detection at attest.check())
- Recursive chain reproduction (reproduce.py `_replay_subject`/`replay`) that walks reliability→score-card→forecast-bundle 3 artefacts deep, re-runs verbs at pinned commits, and does byte-exact (never approximate) comparison — exercised in tests/test_reproduce.py (chain walk, tampering detection, missing-produced_by loud failure)
- Corroboration arithmetic: `corroborate()` computes evidence grade as max(strongest_rung, alone - step*(independent-1)), with real self-corroboration collapse (subject-declared channels count as 1) — twin/corroboration.py:306-362, tested tests/test_corroboration.py:145-212 and wired end-to-end into pricing via pricing._credit() (mitigation_credit_is_gated_on_corroborated_enactment... harness check, twin/invariants/harness.py:4444, backed by real Intel/pocket-org fixture data at twin/fixtures.py:569-616,1342-1388)
- Enforcement ladder validated on load with structural refusal of any numeric field anywhere in a rung (walk_values scan) and refusal of a cliff-edge ladder; posture-as-identity computed (never authored) from two facts (changes_the_outcome + stamped_by-not-subject) — twin/enforcement.py:138-274, tests/test_enforcement.py (28 tests) and harness check at harness.py:3611
- Enforcement move-chain git-history check: `history_violations` reads YAML at every commit that touched a response and detects an unrecorded rung change even before any move record exists — twin/enforcement.py:346-393, exercised by tests/test_enforcement.py:221-291
- Drift measurement: real coverage arithmetic (elapsed/cadence), gap detection bounded at both window ends, floor_reachable deadline computation with the `int(floor*total)+1` float-rounding guard — twin/drift.py:335-450, tested tests/test_drift.py (20 tests) plus two harness liveness/pre-registration guards (harness.py:3121-3305) that read wall-clock and git first-commit-date, one of which (`flux_coverage_floor_is_still_reachable`) is documented as currently RED/unreachable per project memory
- ethics_gate admission ladder that structurally stops at the first failing rung (purpose→necessity→proportionality), never evaluating later rungs even when they'd raise on bad input — twin/ethics_gate.py:194-215, proven by harness check with poison payloads (harness.py:4256-4346) and tests/test_ethics_gate.py
- DPIA triage against the ICO's named mandatory-monitoring triggers, combined with the ladder into admit() as the real gating function (ethics_gate.py:226-309), tested tests/test_ethics_gate.py:116-173
- fast-improvement flag/adjudicate split: flag_fast_improvement() computes a real rate and threshold comparison but never emits a verdict field (checked against the shared NO_ACTION_BANNED_KEYS/PHRASES scan); only adjudicate_fast_improvement(), given a registered role, turns it into a finding — ethics_gate.py:383-438, tests/test_ethics_gate.py:313-379
- misuse.py compute_attractiveness(): genuinely re-runs options.prefilter() with one constraint stripped to derive a real cost figure rather than accept a caller-supplied number — twin/misuse.py:86-152, tests/test_misuse.py:98-145
- disparate_impact.py raise_audit()/respond(): real reuse of schema.refuse_special_category to seal the channel, and a structural role check (respondent must equal the one registered role) — twin/disparate_impact.py, tests/test_disparate_impact.py (13 tests)
- affected_parties.register(): a real flatten-and-sort walk over every scenario's required, non-empty affected_parties field — twin/affected_parties.py:41-62, tests/test_affected_parties.py
- worksheet.py: a real regex-keyed reader against seven+ different artefact bodies (graph, blast, exposure, propagation, options, intervention/observation, price:*, credibility), checked to 6 decimal places against hand-computed numbers — twin/worksheet.py, tests/test_pocket_org.py, harness check worksheet_matches_the_pocket_org (harness.py:253)
- demo_slice.py boundary()/summary(): a live composition of does_not_do.published() and Capabilities.load() rather than hand-typed prose — twin/demo_slice.py:140-172, tests/test_demo_slice.py, harness check does_not_do_register_is_generated_never_typed (harness.py:4349)
- beat-sequence.sh ordering (falsifiability→governance→pricing) is asserted against the literal beat script source text by harness check the_demo_sequence_earns_credibility_before_it_spends_it (harness.py:4396) and by tests/test_beat_sequence.py, not merely narrated

### Thin or stubbed

- twin/enact.py is explicitly propose-only by design (no merge/land/ship function exists at all) — this is a deliberate structural absence documented at length in the module docstring, not a gap, but it means there is genuinely no PR-merge/dispose capability anywhere in the codebase, ever (twin/enact.py:1-51)
- twin/ENACT_MODE currently reads 'development' (twin/ENACT_MODE:1) — the enact_guard.py refusal of merges/enactment-pushes is PERMISSIVE by default right now; only 'operations' mode (or TWIN_ENACT_MODE=operations env override) restores the original refusal behaviour. Per project memory this was a deliberate 2026-08-25 owner instruction during active twin construction, but it means the merge-refusal guard is currently a no-op in the checked-in default state (twin/enact_guard.py:35-77, decide() at line 194)
- enact_guard.py's DISPOSITION_TOOL_NAME/DISPOSITION_COMMANDS are explicitly a keyword screen ('ponytail:' comment, twin/enact_guard.py:29-33, 96-101), acknowledged as catching only the shapes named — a wrapper script or hand-rolled curl+token call to the GitHub REST API is NOT matched; the module docstring names the real upgrade (a merge-incapable credential) as unbuilt
- twin/enact.py's dependency_pins() explicitly does NOT verify any signature, tag, or Rekor entry — 'NOT VERIFIED HERE' (twin/enact.py:184, 198-203); it only reads what committed GitRepository YAML declares. Also every pin in the estate names a tag with a commented-out commit line, so 'pinned' is only pinned-to-a-movable-tag, not commit-immutable (twin/enact.py:125-127, 188-191)
- twin/sign.py is explicitly HMAC-SHA256 with a shared key ('ponytail:' twin/sign.py:19-25) — proves possession, not identity; anybody holding TWIN_SIGNING_KEY can forge any role's signature. Named upgrade path is sigstore/gitsign, unbuilt
- attest.py sidecars are unsigned entirely when no TWIN_SIGNING_KEY is set — signature_status carries an explicit UNSIGNED placeholder string rather than a signature (twin/attest.py:31,92-93), and this is the ordinary/common case absent explicit key-setting
- drift.py's own verdict is explicitly None with a stated reason ('this is the instrument... writing the conclusion into the instrument is how a measurement becomes a demonstration', twin/drift.py:479-485) — no conclusion is ever computed by this module by design; build ticket 65 (not in this file set) is where the verdict lands. Per project memory the coverage floor is currently unreachable (RED), i.e. the drift falsifiability window has already failed its own pre-registered target
- enforcement-grades.yaml's 'warn' rung is explicitly named-but-unrealised: realised_by states 'Nothing in this estate' (twin/enforcement-grades.yaml:44-46) — one of four rungs on the ladder has zero real controls occupying it, present only to keep the ladder honest about vocabulary
- ethics_gate.py's classify_gameability() keyword match is explicitly fitted to one worked example (bus-factor keywords only: 'bus-factor','bus factor','knowledge spread','spread knowledge', twin/ethics_gate.py:87, 29-34 'ponytail:') — a placeholder for a real classifier model call; the module docstring states the upgrade path directly (swap for a model call)
- ethics_gate.py's labelled_corpus() is explicitly hand-authored (5 items) because 'No sensor fixture exists anywhere in twin/fixtures.py' for sensors specifically (twin/ethics_gate.py:36-39, 444-447) — unlike most other capabilities in this cluster, sensor admission has no path through the real org fixtures, only through this synthetic corpus
- misuse.py's constraint-removal logging explicitly covers only a perspective's own declared constraints, not the universal floor — 'removing' the floor is stated as 'a governance-document edit, a different and larger act this module does not cover' (twin/misuse.py:16-20)
- corroboration.py's grade computation is explicitly channel-count-based only, never volume/recency-weighted — 'ponytail:' twin/corroboration.py:48-52 states ten reconciler reports count as one channel, and per-channel recency/volume weighting is named as an unbuilt upgrade if ever needed
- reproduce.py's discount legs (score's --discount-sha256) are explicitly NOT replayable from pins — raises ReproduceError by design because discount sources carry no produced_by chain (twin/reproduce.py:228-241)
- demo_slice.py's boundary() 'absent' capabilities list is real but by definition names capabilities this demo sequence never exercises at all — the module docstring states build ticket 91 built only the rendering, not new coverage of anything
- disparate_impact.py and affected_parties.py both carry NO capability/depth grade at all — both explicitly authored-only artefacts with `depth={'grade': None, ...}` (twin/disparate_impact.py:40-44, and affected_parties.published has no capability path either) — meaning neither is measured against a decision-ticket checklist the way most other artefacts in this cluster are

### External integrations

- Flux/Kubernetes: twin/drift.py reads ONLY from a jsonl sample log (estate/driftwood/drift/samples.jsonl) and window/campaign YAML files under ESTATE_CLONE_DIR/driftwood/drift/ — no live Kubernetes or Flux API call exists anywhere in this module; sampling is done by an external probe.sh not in this file set, and the harness explicitly checks wall-clock liveness of that external process's output rather than talking to Flux itself
- GitHub: twin/enact.py reads GitRepository CRD YAML committed inside ESTATE_CLONE_DIR (a local git clone), not the live GitHub API; twin/enact_guard.py refuses `gh pr merge`/`gh api ... merge` command-line invocations by pattern-matching the command string before it runs — it does not call GitHub itself, it blocks a tool call that would have
- gitsign/keyless signing: named throughout (twin/enact.py:182-184, twin/enforcement.py:45-49) as the real upstream mechanism the estate's own repositories claim to use, but explicitly NOT VERIFIED by this codebase — twin/sign.py uses HMAC-SHA256 with a shared secret instead, and both enact.py and enforcement.py state plainly that this repository's own commits are not keyless-signed either (citing estate/verify/provenance/verify-provenance.sh, a file outside this file set)
- arckit: no reference found anywhere in this cluster's files
- prediction markets / news feeds: no reference found anywhere in this cluster's files; all 'signals' in fixtures.py (e.g. tan-14a-customer-guidance, fab-cluster-reconciled) are fixture-authored strings with fictional/fixture provenance.url fields (example.invalid), never live feed I/O
- git (local): genuinely real subprocess calls throughout — enact_guard.py's `git remote get-url`, enforcement.py's/drift.py's git-history reads via ModelRepo, the fixture builder's own commit machinery — all real local git operations against local repos, not a network integration

### Fixture-only

- Netflix: DVD-to-streaming scenario (dvd-decline-2011), fear/opportunity paths, price-separation signal, Q4 2011 letter checkpoint, propose('hold-the-bundled-price-for-one-quarter', channel=record) — all only in twin/fixtures.py build_netflix_org/build_and_corroborate_netflix_org (lines ~4860-5007) and twin/beat-netflix.sh; no other subject exercises the propose/enactment-record channel in this cluster
- Intel: 14A foundry-node scenario, EUV lithography causal edge, tan-14a-customer-guidance signal, pin-the-tooling-image-set / report-node-schedule-variance / raise-the-tooling-team-retention-award responses at specific enforcement grades (constrain/observe/none) — only in twin/fixtures.py build_intel_org (~5414-5612) and twin/beat-intel.sh; this is the ONLY subject in this cluster carrying real enforcement-ladder occupancy and enactment-channel corroboration data (self-declaration + reconciliation-state -> grade 3, one lever with no rung)
- Royal Mail: automation-shortfall scenario, would-the-twin-have-flagged-it, 2018-05-17/2018-10-01 dates, market-consensus-at-flotation world model reading 0.05 — only in twin/fixtures.py build_royal_mail_org (~4291-4860) and twin/beat-royal-mail.sh; used purely for the falsifiability/backtest beat, no enactment/enforcement data
- Carillion and Enron: used exclusively as the contamination-discount legs for Royal Mail's score (twin/fixtures.py build_carillion_org ~2086, build_enron_org ~2805) — no other role in this cluster
- pocket org: five-component toy estate whose numbers are the ONLY ones checked against a hand-computed authored source (twin/pocket-org-worksheet.md, referenced by twin/worksheet.py); its retrain-the-on-call-rota response and two enactment claims (self-declaration + merged-change -> grade 2 corroborated) are the fixture data backing the mitigation_credit_is_gated_on_corroborated_enactment harness check (twin/fixtures.py:1330-1388)
- £ figures throughout: e.g. pin-the-tooling-image-set cost min/mode/max 400000/900000/2000000 (fixtures.py:484-487), retention-award-raise 1200000/1800000/2600000 (fixtures.py:549-552) — exist only as fixture YAML, never derived from any real external source
- Enactment repository names in enact_guard.py/enact.py (policy-as-versioned-nist, -platform, -driftwood, -tuppence, -ludlow, -ico, -code) are real org repository names asserted as hardcoded constants (ENACTMENT_REPOSITORY regex + enact.py test expectations tests/test_enact.py:244-258), not fetched from any live registry
- roles.yaml's five roles (model-steward, worksheet-author, constraint-owner, challenger, challenge-resolver, disparate-impact-respondent) are a fixed, hand-authored, versioned register — every signature in this cluster binds to one of exactly these six names

**Notes:** This cluster is the most structurally self-checking part of the twin: nearly every module pairs a real algorithm with (a) a unit-test file that exercises it directly and (b) a `harness_check` in twin/invariants/harness.py that re-asserts the same property against live fixture-built repos as part of `twin verify`, so `pytest` and the invariant suite are two independent runs of largely the same assertions rather than one trusting the other. The one place this pattern currently reads as weaker than its own tests suggest is twin/ENACT_MODE, which is checked in as 'development' (permissive) — the harness check for propose-only-at-both-layers explicitly forces TWIN_ENACT_MODE=operations for its own run (harness.py:3502-3527) so the capability itself stays proven even though the day-to-day default does not enforce it; a caller of enact_guard.py today, absent that env override, gets no refusal at all. Similarly the drift/coverage-floor guard (harness.py:3225) is explicitly documented in its own docstring as expected to stay RED once the window's shortfall becomes irreversible, and per project memory (project_flux_verdict_unmeasured) that is in fact the current live state as of 2026-08-16 — i.e. one of this cluster's own harness checks is a known, accepted, currently-failing red, not a latent bug. Intel is the single fixture subject carrying real, wired enforcement-ladder + enactment-corroboration data (two enforcement rungs occupied, one lever with none, self-declaration + reconciliation-state channels corroborating to grade 3); Netflix carries the only propose()/enactment-record-channel demonstration; the pocket org carries the only data checked against a hand-authored ground truth (worksheet.py) and is also the fixture backing the mitigation-credit-gated-on-corroboration harness proof. Royal Mail/Carillion/Enron carry no enactment or enforcement data at all — they exist purely for the falsifiability/backtest beat, outside this cluster's core subject matter. No file in this list makes any live network call (no GitHub API, no Kubernetes API, no gitsign/Rekor lookup, no prediction-market or news-feed integration) — every 'real I/O' in this cluster is local git subprocess calls or local file reads.

## twin — twin-risk-engine: PERT/severity distributions, empirical anchoring, response pricing, ensemble trade-off, constraint pre

### Real

- twin/pert.py:139-147,149-175 -- exact analytic PERT/Beta moments (mean, variance, raw_moment via binomial expansion of E[B^j]) used as a yardstick against sampled figures; verified in tests/test_pert.py:37,53 (raw moments recover mean/variance and agree with the sampler)
- twin/pert.py:177-182,218-225 -- seeded Monte-Carlo Beta-variate sampling via random.Random(seed) keyed by name not draw order; tests/test_pert.py:71,92,101,111 check convergence, determinism, degenerate no-randomness-consumed, and name- vs order-independence
- twin/severity.py:81-96,128-175 -- lognormal-body/GPD-tail splice with continuity at the threshold, closed-form VaR via shared inverse-CDF, and closed-form TVaR (McNeil & Frey 2000) with a hard refusal at the xi>=1 mean-nonexistence boundary; tests/test_severity.py:39,80,99,105,115,133 cover continuity, TVaR-vs-VaR divergence on a constructed pair, monotonic TVaR>=VaR, both refusal boundaries, and Monte-Carlo convergence to the analytic TVaR
- twin/anchoring.py:41-65 -- exact closed-form two-point lognormal quantile calibration (not a numerical solve); tests/test_anchoring.py:13,21,26,32,38 verify exact recovery and every refusal path
- twin/pricing.py:135-230 -- three-gate impact pricing (path evidence grade, valuation evidence grade, causal admission) with exact point-wise magnitude x influence-triple composition, never re-sampled; tests/test_pricing.py:58,67,75,83,101 exercise all three gates and the composed-vs-attenuated dual reporting
- twin/pricing.py:233-283 -- mitigation credit double-gated on claim evidence grade AND corroborated enactment (twin/corroboration.py), refusing credit for an unenacted control even with a well-evidenced claim; tests/test_pricing.py:152,185 test differential scoring by corroborated enactment
- twin/tradeoff.py:59-74,138-207 -- net-cost-of-risk computed per rival causal account from independent pricing.price() calls, with a computed (not asserted) ranking-agreement check and mean-based default; tests/test_tradeoff.py:46,58,66,75,119,138,158 exercise cross-account credit divergence and disagreement detection
- twin/options.py:100-156,157-205 -- structurally-locked pre-filter-before-pricing invariant (sentinel construction guard + independent partition re-derivation defending against dataclasses.replace); tests/test_prefilter.py:115,190 (test_pricing_cannot_be_reached_without_the_prefilter, test_a_copy_of_an_admitted_set_cannot_price_an_excluded_option)
- twin/constraints.py:63-128 -- schema validation with required-by-name floor/positions checks (not merely 'presumably covered'); exercised implicitly by every prefilter/pricing test that calls constraints.resolve()
- twin/admission.py:65-121 -- derived (not declared) causal admission via a real graph traversal (blast.radius) gated at a distinct admission threshold from the pricing threshold; tests/test_admission.py:48,58,69,78,87,95,106 cover path-based admission, no-path refusal, weak-evidence refusal, cash-flow-as-component, and direction sensitivity
- twin/credibility.py:46-70,123-141 -- real Buhlmann-Straub Z formula with two ordered degenerate-variance special cases, and a triple-translating blend that never narrows the prior's width; tests/test_credibility.py:30,39,46,61,65,70,75,134 cover monotonicity in n/own-variance/world-variance, both degenerate cases in the specified order, and width preservation
- twin/regimes.py:78-92,133-190,193-256 -- real git-repository rewind (ModelRepo.open_at_time) for as-consumed, construction-level fact withholding (dataclasses.replace, not a flag), and a computed two-way sensing/interpretation gap; tests/test_regimes.py:110,121,138,147,175 cover post-T fact absence, monotonic admission across regimes, claim-follows-signal withholding, and gap computation
- twin/forecast_book.py:104-160 -- structural blindness gate (refuses emission at/after resolution-window-open, string-comparison based so an auditor can recompute it from the artefact alone) and a genuinely closed 3-function public surface; tests/test_forecast_book.py:51,59,111 (test_the_module_exposes_no_position_placing_function checks the module's public surface as an allow-list)
- twin/forecast_book.py:163-209 -- proper-scoring-rule delegation, never reimplemented (calls scoring.score()); co-registration enforced by reading question id/timestamps only from the emission's own pins/body; tests/test_forecast_book.py:137,142,151,161 verify bit-for-bit reproduction of scoring.py and refusal of a doctored emission
- twin/benchmark.py:139-146,191-213 -- mechanical resolvable-terms eligibility filter and deterministic sort-then-seeded-sample selection (arrival order never matters); tests/test_benchmark.py:77,85,104 verify reproducibility, sort-not-arrival-order, and the deterministic volume valve
- twin/benchmark.py:253-272 -- whole-record JSON substring scan for quarantine breach detection, catching nested-field leaks and ignoring timestamp/lag entirely; tests/test_benchmark.py:191,207 plant a nested breach and vary check order to confirm order-independence

### Thin or stubbed

- twin/severity-anchors.yaml:55-80 and twin/anchoring.py -- xi and beta (the GPD tail shape and scale) are explicitly marked anchored:false with illustrative_value only (xi=0.6, beta=15000000); no public source fits a GPD shape parameter for cyber-loss severity, self-described in the YAML as 'no defensible single-source fit at all'
- twin/severity.py:40-46 (docstring) and 159-175 -- tvar() is explicitly ponytail-marked as tail-only: it refuses whenever the requested confidence level's VaR falls inside the lognormal body, because the module does not carry the lognormal body's own partial-mean closed form; a real caller need is asserted ('every call this system makes today') rather than demonstrated against a live caller in this cluster
- twin/credibility.py:16-18 -- K is explicitly ponytail-marked as a single-org stand-in (world-layer prior's own variance substituted for a portfolio-estimated between-risk variance), described as the 'honest single-org stand-in' pending a world layer with more than one org's hypothetical means
- twin/regimes.py:340-350 -- gap()'s model_residual is explicitly computed:False; the module states plainly that nothing in the system yet infers a probability from a signal, so a third (model) failure mode cannot currently be measured, only the two structural gaps
- twin/benchmark.py:361-364,371-384 -- proportionality_verdict()'s 'resolved' scored-resolutions list is explicitly stated to be empty in practice ('this suite reaches no live venue') so resolution cadence is reported as designed, not yet measured, in every real run
- twin/pert.py:249-252 -- summarise() explicitly ponytail-marks its nearest-rank quantile as a simplification versus an interpolating estimator, deemed acceptable only because draw counts are large and fixed
- twin/options.py:44-49 -- the _FROM_THE_PREFILTER sentinel is explicitly ponytail-marked as 'a lock, not a proof': Python has no private constructor, so a determined caller could still bypass it by hand; the module relies on the separate _refuse_a_broken_partition() re-derivation as the real defense

### External integrations

- None of these 15 files touch Flux, Kubernetes, GitHub, or gitsign directly.
- twin/regimes.py:145-190 -- real I/O: ModelRepo.open_at_time() is a genuine git-repository rewind against a local model repo on disk (twin/repo.py), not simulated; reported honestly as unavailable when no commit exists at or before the cutoff.
- twin/benchmark.py:361-364 -- explicitly states 'this suite reaches no live venue' (citing twin/market_signals.py's own admission) -- prediction-market/news-feed connectivity is simulated/absent in this cluster; benchmark question pools are supplied as in-memory dicts in tests, not fetched from a real venue.
- twin/forecast_book.py and twin/benchmark.py rely on twin/artefact.py's signing machinery (twin/sign.py/attest.py, not read in this pass) for gitsign-style signing, but that machinery itself lives outside this cluster's file list.

### Fixture-only

- twin/severity-anchors.yaml:26-38 -- data-breach-loss subject figures ($600,000 median, $32,000,000 p95) cited from Cyentia Institute IRIS 2025, and illustrative xi=0.6/beta=$15,000,000 justified only by plausibility against Cyentia IRIS Xtreme's largest-100-events figures ($47M median, >1-in-4 exceed $100M) -- real published figures, but the only subject in the file (single-subject anchor set)
- tests/test_pricing.py:34-35 -- fixtures.build_pocket_org() is the only repo used to exercise pricing.py's real gates in this cluster's tests
- tests/test_tradeoff.py -- a 'netflix' fixture (fixtures.build_netflix_org, referenced in twin/tradeoff.py:151-157 docstring) is the only real-subject fixture that produces a genuine cross-account cheapest-response disagreement; the module's own docstring states no other real fixture makes two accounts disagree, and the synthetic unit test (_assemble tests) remains the primary coverage for that case
- twin/constraints.yaml -- all constraint ids, monetary-adjacent language ('ruin', ' insolvency') are structural/generic, no company-specific figures

**Notes:** This cluster is the £-engine/risk-quantification core: uncertainty (pert.py) and heavy-tailed severity (severity.py/anchoring.py) feed into pricing (pricing.py) which is reached only through the constraint pre-filter (options.py/constraints.py) and causal admission (admission.py); tradeoff.py composes pricing across rival causal accounts; credibility.py is a separate Bayesian-blending capability not wired into pricing.py in this file set (no cross-reference found between credibility.py and pricing.py/tradeoff.py); regimes.py and forecast_book.py/benchmark.py form a distinct 'epistemic honesty' subsystem (temporal information gating and blind external forecast scoring) that does not touch the £ engine at all -- both subsystems share only the pert.py/canon.py/artefact.py substrate. Every module in this cluster follows the same 'refusal is an answer, never a silent zero/default' discipline, enforced by closed-vocabulary body checks (walk_keys) rather than convention.

## twin — twin sensing/ingest pipeline, decay+retrospective pool, planter/detector/scorer synthetic-substrate harness, proper scor

### Real

- Exponential decay with a validated half-life/threshold parameter file and computed crossing dates: twin/unbound_pool.py:92-113 (weight/is_decayed/decayed_on), exercised by tests/test_unbound_pool.py:57-95
- Proper scoring rules (Brier, log-loss) with a refusal on certainty claims and fixed-precision quantisation for cross-platform reproducibility: twin/scoring.py:47-64, tested for properness/orientation in tests/test_scoring.py:36-93
- Reliability-diagram binning over a pooled forecast population, every bin (incl. empty) reported with None (not fabricated 0.0) averages: twin/scoring.py:129-167, tests/test_scoring.py:111-159
- Enron-vs-obscure memorisation-leakage discount measured (not hardcoded) as a mean-loss gap, optionally folded with hindsight-resistance legs: twin/scoring.py:74-126, tests/test_scoring.py:172-248
- Structural (not merely documented) planter/detector isolation: detector.py has zero import of planter, ignores a spliced-in ground-truth key, proven by an AST-scan harness guard referenced in module docstrings and exercised by tests/test_detector.py:17-86
- Timely/late/missed scoring against a per-plant actionability horizon with day-string comparison, near-zero (not zero) late score: twin/scorer.py:84-105, tests/test_scorer.py:28-97
- Deterministic, seeded substrate generation (random.Random(seed), no external entropy) proven byte-for-byte reproducible across two calls, vs. a genuinely non-reproducible os.urandom-seeded stand-in, both exercised: twin/substrate.py:118-139, tests/test_substrate.py:69-84,141-155
- Substrate fidelity eval across 7 real, computed dimensions (signal_to_noise, plant_difficulty, plant_difficulty_spread, spine_consistency, reporting_asymmetry, mundanity, contamination) each against a declared target band, with genuine positive/negative control batches per dimension and a real iterative tuning loop (tune()) that measurably raises reporting_asymmetry from a balanced start until it clears its target: twin/substrate_eval.py:151-469, tests/test_substrate_eval.py (24 tests) including a hard contamination refusal (refuse_if_contaminated)
- Token-overlap classification (signal_classify) proven to discriminate between multiple real-world-fixture candidates and pass a labelled corpus pooled from 4 real backtest orgs (Carillion/NMC/Wirecard/Enron): twin/signal_classify.py:77-202, tests/test_signal_classify.py
- Unattended ingest pipeline structurally proven to have no human-gate parameter anywhere in its call graph (checked by test names, not just docstring assertion), with measured (not assumed) throughput from wall-clock timing: twin/ingest.py:83-165, tests/test_ingest.py:93-129
- Retrospective rescue that refuses a rubber-stamp bind (requires nonzero best_match score) and computes real lead-time-to-recognition per rebound signal: twin/retrospective_sweep.py:59-120, tests/test_retrospective_sweep.py (13 tests incl. a worked multi-year quantum-signal-rescued-by-crypto-dependency case)
- Scheduled sweep across a list of repositories with deliberately no staleness/hash-skip (to avoid selection bias) and per-scenario failure isolation, proven to emit identical forecast volume on repeated unchanged runs: twin/schedule.py:61-136, tests/test_schedule.py:47-58
- Skill-eval harness with threshold (not exact-match) scoring, append-only score log, and per-distinct-model-version regression detection that correctly dedupes re-evaluated versions: twin/skills.py:140-263, tests/test_skills.py (14 tests) and tests/test_record_skill_scores.py
- Price-move (derivative) computation from raw price-level observations, structurally forbidding any level-to-probability conversion (as_probability always raises, cited bias evidence embedded in the refusal), quarantine exclusion applied before classification: twin/market_signals.py:119-257, tests/test_market_signals.py (18 tests)

### Thin or stubbed

- signal_classify.classify's STEEP/binding logic is an explicit keyword+word-overlap heuristic standing in for a real model call, proven only against 'political' and 'economic' signals ('makes no claim about social, technological or environmental') -- twin/signal_classify.py:14-21,55
- detector.detect's anomaly heuristic ('shares little vocabulary with its surroundings') has 'no claim to be a good anomaly detector'; it exists to prove structural blindness, not detection quality -- twin/detector.py:15-22
- substrate_eval.classify_polarity is a bare keyword scan ('the same stand-in-for-judgement shape'), not a sentiment model -- twin/substrate_eval.py:24-28,92-100
- substrate.generate_deterministic/generate_non_reproducible are explicitly named 'toy generators'; the real generator (build ticket 49, an actual LLM call) is 'not yet built' per twin/ingest.py's own docstring -- twin/substrate.py:10-31, twin/ingest.py:34-39
- substrate_generator.py is a 'heuristic reference implementation' explicitly because 'no provider is reachable from this suite' -- not a live model call -- twin/substrate_generator.py:11-13
- No CLI verb for ingest_run, market_signal_run, or record_skill_scores.py -- each is a typed function/standalone script only, by explicit design choice recorded as 'ponytail:' notes -- twin/ingest.py:41-47, twin/market_signals.py:34-37, twin/record_skill_scores.py:21-24
- unbound_pool.py's own body field states the rescue mechanism is 'not implemented here' (deferred to retrospective_sweep.py) -- twin/unbound_pool.py:218-221
- planter/detector share the same model family and priors by construction (SHARED_PRIOR_LIMITATION), an acknowledged, unfixed limitation published on every scorer result rather than solved -- twin/planter.py:12-16,57-62, twin/scorer.py:18-19
- schedule.py explicitly does not build 'the actual cron/CI cadence that calls sweep() on a clock' nor the standing-library curation (admissibility, precondition triggers) -- twin/schedule.py:33-38
- market_signals.py is built against 'a caller-supplied fixture price series' only; 'no live venue connection is reachable from this suite' -- a real Polymarket/Kalshi adapter is future work -- twin/market_signals.py:16-20
- substrate_report.py explicitly cannot be replayed by 'twin verify': 'what is not automated is re-running the derivation from the envelope alone' -- twin/substrate_report.py:27-32
- detect() 'always proposes its single best candidate per eligible channel' even with no real plant present -- a forced guess, not a confidence-gated detection -- twin/detector.py:60-64

### External integrations

- GitHub/Kubernetes/Flux: none touched by this cluster.
- gitsign/arckit: not touched directly; module docstrings reference arckit's refresh-loop design (twin/schedule.py:9-14) as inherited design ancestry only, no code dependency.
- Prediction markets: twin/market_signals.py explicitly does NOT connect to any live venue (Polymarket/Kalshi) -- built entirely against caller-supplied PriceObservation fixture data; 'no live venue connection is reachable from this suite' (line 18-20). Simulated/fixture-only.
- News/model-provider feeds: substrate generation (twin/substrate.py, twin/substrate_generator.py) explicitly does not call any live LLM provider; generate_non_reproducible uses os.urandom purely as an honest stand-in for unpindable model entropy, not a real API call.
- No network I/O, cloud API, or external service call exists anywhere in this cluster's 20 files; all 'external' behavior is either pure computation over local YAML/JSONL fixtures or explicitly-labelled simulation.

### Fixture-only

- twin/netflix-substrate-recipe.yaml: 24 templates + 4 planted signals, all authored fiction about 'free-running' 2011 Netflix operational chatter, seed 20111024 -- exists only as this one committed YAML file
- twin/plant-horizons.yaml: 4 authored horizon dates/reasons/strengths keyed to the netflix-2011-operational recipe id -- fixture-only, explicitly 'not facts about Netflix'
- twin/substrate_eval.py KNOWN_REAL_ORGS blocklist: Carillion, Enron, Wirecard, NMC Health, Kodak, Netflix, Intel, Maersk, AstraZeneca, Sanofi, Royal Mail (lines 231-234); KNOWN_REAL_PEOPLE: Jeffrey Skilling, Markus Braun, Richard Howson (line 240) -- hardcoded contamination blocklist
- twin/signal_classify.py _POLITICAL_KEYWORDS = ('liquidation','bafin','administrative act') fitted specifically to the Carillion/Wirecard fixture text -- line 55
- twin/signal_classify.py's labelled_corpus() and _ORGS dict hardcode component ids/names for Carillion ('carillion-uk-construction'), NMC ('uk-listed-hospital-group'), Wirecard ('third-party-acquiring-business'), Enron ('energy-trading-book') -- lines 144-161
- twin/scoring.py measure_discount() is computed against caller-supplied Enron/obscure score lists but the Enron-as-contamination-control concept itself is fixture-derived from twin/fixtures.py (outside this cluster)
- twin/decay.yaml: half_life_days=180 is a declared starting point, explicitly 'not yet retuned against real backtest lead times'
- twin/skill-scores.jsonl: 7 fixed committed entries, all dated 2026-08-13, all model_version 'heuristic-0.1.0', all score 1.0 -- static snapshot, not live telemetry
- twin/substrate_generator.py FOCUS_POOL (project-atlas, project-kestrel, etc.) and _MUNDANE_TEMPLATES/_PLANTED_SIGNALS in labelled_corpus() are hardcoded fixture text

**Notes:** This cluster forms a coherent pipeline: substrate.py/substrate_generator.py generate synthetic multi-channel corpora -> planter.py seals ground truth (with strength+horizon) -> detector.py finds candidates blind -> scorer.py grades timely/late/missed -> substrate_eval.py measures 7 fidelity dimensions and tunes the generator -> substrate_report.py packages both readings into one artefact. In parallel, ingest.py/market_signals.py run signal_classify.classify() unattended at volume over substrate lines and market price moves respectively, both explicitly ungated at entry and both grade-5-by-construction; unbound_pool.py/retrospective_sweep.py handle what signal_classify fails to bind (decay + rescue). schedule.py is the volume-forcing scheduler for the *forecast* side (twin run/scenarios), separate from ingest volume. scoring.py provides the proper scoring rules and reliability diagram used to grade forecasts elsewhere in the twin. skills.py/skill-thresholds.yaml/skill-scores.jsonl/record_skill_scores.py form the third evaluation seam that treats every heuristic (signal-classify, substrate-generator, etc.) as a non-deterministic 'skill' scored against a threshold rather than asserted correct by construction. Every heuristic module is candid in its own docstring about being a stand-in for a real model call ('ponytail:' notes), and every such note names an explicit upgrade path (swap the function body, harness/tests unchanged) -- this is a deliberate, well-documented pattern across the cluster rather than a hidden gap.

## estate — platform/identity, platform/posture, platform/currency-controller, platform/access, platform/break-glass, platform/eud

### Real

- platform/identity: SPIRE→Istio SDS integration is real (mounts csi.spiffe.io socket into Envoy per Istio's documented spire integration pattern); live-tail proof of a real signed spiffe://acme.internal SVID and a 200 over mTLS is asserted, not just claimed.
- platform/identity: STRICT mesh-wide mTLS via PeerAuthentication is a real Istio object, not narrated.
- platform/posture: the Kyverno mutate-then-validate trust boundary is real and independently `kyverno test`-proven offline (not merely described) — clobber and deny behaviours are asserted against real CEL expressions in the policy YAML.
- platform/posture: render-and-prove.py in up.sh independently proves the rendered Kustomization with `kubectl kustomize`, a second builder distinct from the renderer being tested — genuine cross-check, not the renderer judging itself.
- platform/currency-controller: currency.py's core logic (select_stale, deposture_patch) is pure, tested stdlib code that actually runs and asserts; the urllib in-cluster glue talks the real k8s API with no client library dependency, a real design choice not a stub.
- platform/access: access.py's graded decision engine (ALLOW/STEP_UP/DENY) is real, tested logic with proportionality and monotonicity asserted, not hardcoded per-scenario outputs.
- platform/access: Pomerium Core + Dex are real, versioned open-source Helm charts wired via Flux HelmRelease, not mocked.
- platform/break-glass: break-glass.py genuinely imports and calls ../fair/fair.py's simulate/summarize (verified live: bg.fair is fair, an identity check, not a copy) — the £ figures come from a real Monte-Carlo-ish TVaR calc over the scenario JSON triples, not hardcoded.
- platform/eud: qcow2 disk creation via `qemu-img create` is a real, executed step (state/*.qcow2 files exist on disk, ~196KB sparse files, consistent with an empty disk image having been created, not a fabricated claim).
- platform/eud: the tpm-devid-enroll.sh template-render is real and offline-tested to produce a valid ClusterStaticEntry on the correct SPIFFE root.

### Thin or stubbed

- platform/identity/openbao/helmrelease.yaml:31-34 — OpenBao runs in `dev` mode with a hardcoded `devRootToken: root`, in-memory/ephemeral storage; README states explicitly 'demo-only — not production HA'.
- platform/identity/openbao/jwt-auth.yaml:20-23 — uses `image: openbao/openbao:latest` (unpinned) and BAO_TOKEN=root hardcoded as an env var in a Job spec.
- platform/access/pomerium/helmrelease.yaml:48,68-69,75,95 — clientSecret 'pomerium-oidc-secret' hardcoded inline (marked `ponytail: demo secret`), the allowed identity is a single hardcoded email (operator@acme.internal), and `signingKey: ""` is an empty placeholder (marked `ponytail: chart mounts a demo key; supply a real EC key at a venue`) — the JWT-signing key that would make the whole IAP→apiserver trust chain function is not actually configured.
- platform/access/oidc/dex-helmrelease.yaml:39,49,54-58 — Dex storage type is `memory` (non-persistent), a single hardcoded staticPassword (bcrypt hash for 'operator', explicitly commented 'demo only; never a real credential'), and a hardcoded clientSecret.
- platform/access/device/device-svid.yaml:23 and platform/eud/vms/*-device-svid.yaml:12/11 and platform/eud/tpm-devid-enroll.sh's default — every device SVID's `selectors: [tpm_devid:fingerprint:...]` is the literal placeholder string REPLACE_WITH_ATTESTED_TPM_FINGERPRINT; no real hardware or vTPM has ever completed attestation in this codebase, confirmed by up.sh's own comment ('fingerprints still placeholders until attested').
- platform/eud — the entire VM layer is 'offline prep only'; build-vm.sh never boots a VM, never installs an OS (README: 'never boots a VM or installs an OS ... GUI/ISO-gated and cannot run headless'); vms/*.json `iso` fields are literal placeholder strings REPLACE_WITH_WINDOWS11_ISO_PATH / REPLACE_WITH_LINUX_ISO_PATH.
- platform/eud — the emulated EK/DevID trust chain is explicitly a demo root, not a manufacturer root (windows-hello-for-business.md and both vms/*.json 'note' fields state this honestly); swtpm self-signs its own EK on first boot.
- platform/break-glass — the scenarios/*.json FAIR inputs (lef/lm triples) are hand-authored fixture files with narrative 'note' fields, not derived from any live telemetry, feed, or incident data; carried_gbp figures are simulation outputs of these fixtures, presented as if representative.
- platform/break-glass/README.md:107 — README itself states break-glass.py is meant to be 'the forward-auth / external-authz decision a Pomerium route calls' in a live estate, but no such integration (Pomerium external-authz plugin, webhook route, sidecar) exists anywhere in the six directories read; it is purely a standalone CLI/library.
- platform/currency-controller — the LIVE tail of verify-currency.sh (step 5) only triggers a manual Job run and reports whether the job was CREATED; it does not assert the pod was actually de-postured afterward (no follow-up check of the patched labels), so 'evidence the reconcile works live' is thinner than the offline proofs.
- platform/access/up.sh:37-44 — the tpm_devid attestor merge into ticket 14's spire HelmRelease is explicitly a manual, unautomated step ('Kept manual because it edits another ticket's release; do it once per venue') — up.sh only prints instructions, does not perform the merge.

### Risk and pricing

- platform/break-glass/break-glass.py:65-68 (carried_gbp) — calls fair.state()/fair.simulate()/fair.summarize() from ../fair/fair.py to compute a single-state FAIR triple's carried £ (TVaR + risk load); this is the only place in this cluster's six directories that computes a £ figure, and it is imported/reused, not reimplemented.
- platform/break-glass/break-glass.py:71-78 (required_tier) — maps carried £ to a 1-3 assurance tier via assurance-bands.json thresholds (step_up_at=10000, attest_at=100000, no_cage_at=1000000 GBP/yr), the mechanism by which £ directly sets human/device assurance requirements.
- platform/break-glass/assurance-bands.json — the calibration knob; README states bands are 'calibrated against the estate's appetite ordering (../risk/appetite.json, ludlow strictest)' — an external file (not in this cluster) that this cluster's bands are claimed to be consistent with but that was not independently checked here.
- platform/access/README.md:88 — explicitly names access.py's static OP_TIER table as the thing break-glass.py's £-crossover model is meant to eventually replace ('wire the tier to fair.py's £-crossover if the bar should move live with the risk number') — access.py itself has NO £/pricing touchpoint, only break-glass.py does.
- platform/currency-controller/README.md:52-53 — narrates that a de-postured pod loses reach and its OpenBao secret, 'priced into TCoR (user story 2)' — a narrative claim, not a computation; no TCoR/£ arithmetic exists in currency-controller's own code.

### Cages and enforcement

- platform/identity/istio/peerauthentication-strict.yaml:9-11 — mesh-wide STRICT mTLS is a hard enforcement gate (plaintext refused), applied via a real PeerAuthentication object at the root namespace.
- platform/identity/demo-mtls/authorizationpolicy.yaml — real Istio AuthorizationPolicy enforcing admission by SPIFFE principal (`acme.internal/ns/mesh-demo/sa/ping`), asserted live to actually deny/allow based on identity, not IP.
- platform/posture/policies/posture-trust-boundary.yaml — a ValidatingPolicy with `validationActions: [Deny]`, the graded-enforcement mechanism refusing forged/mismatched posture labels at admission.
- platform/posture/policies/stamp-posture.yaml — a MutatingPolicy providing the 'defence in depth' clobber-overwrite half of the trust boundary; README also cites RBAC absence-of-grant as a third layer (workload ServiceAccounts lack patch/update on pods) but this is asserted only as design intent in the README's prose, not independently checked by any verify script in this cluster.
- platform/currency-controller — the orphan-guard cross-reference in verify-currency.sh (step 3) is the closest thing to an 'orphan guard' touchpoint in this cluster: it checks that de-posturing removes the CLAIM_LABEL so the pod also falls out of the orphan-guard's and versioned require-* policies' scope. The orphan-guard's own implementation lives outside this cluster (distribution/) and is not read here.
- platform/access/access.py — the graded enforcement (DENY/STEP_UP/ALLOW) at the human/device layer; tier-3 ops (break-glass/cluster-admin/delete) require the cumulative device_svid factor, the strongest rung this module offers.
- platform/break-glass/break-glass.py — adds a fourth rung, CAGE (a scoped/read-only session for a stale device below the no_cage_at £ ceiling), the most granular enforcement gradient found across the six directories — genuinely graded, not binary, and asserted for monotonicity.
- platform/currency-controller's DEPOSTURE action is itself an enforcement/de-posture (not full deny) mechanism: it drops a stale pod to the un-postured base-mesh SVID rather than blocking it outright — a real, tested 'keep running but caged' pattern distinct from break-glass's CAGE rung (different layer: workload vs. human).

### Feeds, Wardley, war-gamer

- NONE FOUND in these six directories. No feeds ingestion, no Wardley map generation/consumption, no wargamer/proposer logic, and no code that opens a real GitHub PR exists anywhere in platform/identity, platform/posture, platform/currency-controller, platform/access, platform/break-glass, or platform/eud.
- The nearest adjacent mechanism is currency-controller's read of a live flux-operator ResourceSet (fluxcd.controlplane.io/v1 resourcesets/policy-versions) at platform/currency-controller/currency.py:154-157 (get_supported) — this is a real live cluster-state read, not a 'feed' in the market/vulnerability-intelligence sense, and it writes back only pod label patches/deletes via the k8s API, never a git commit or PR.
- No PR-opening, git, or GitHub Actions code appears in any file read across this entire cluster.

### Original-thesis mechanisms

- Multi-version coexistence — PRESENT, thinly, only in platform/posture: up.sh renders and applies per-version copies (stamp-posture-<v>, posture-trust-boundary-<v>) from distribution/versions.yaml via distribution/render-and-prove.py; verify-posture-projection.sh's live check loops over the version list to confirm each versioned object is installed. Not present at all in identity, currency-controller, access, break-glass, or eud — those tickets are unversioned singletons.
- ResourceSet matrix — PRESENT only as a READ dependency: currency-controller/currency.py:147-157 reads a live flux-operator ResourceSet (fluxcd.controlplane.io/v1 resourcesets/policy-versions) as its 'supported versions' source of truth, with a SUPPORTED_VERSIONS env override for when flux-operator isn't installed. No ResourceSet is authored, defined, or delivered anywhere in these six directories — the ResourceSet mechanism itself lives outside this cluster.
- Renovate bump PR — ABSENT. No Renovate config, no PR-opening code, anywhere in this cluster.
- Signed tags — ABSENT in this cluster directly, but access/oidc/dex-helmrelease.yaml's comment and access/README.md explicitly narrate that the human OIDC subject (operator@acme.internal, logging in via Dex) is 'the SAME subject narrated as the gitsign committer' — i.e. this cluster claims alignment with a gitsign/keyless-signing mechanism that lives elsewhere (not verified here) rather than implementing tag-signing itself.
- Orphan guard — PRESENT only by cross-reference: currency-controller/verify-currency.sh step 3 parses the posture policy source files to prove the de-posture patch takes a pod out of scope for 'the orphan-guard, AND the posture ClusterSPIFFEID podSelector'; the orphan-guard's actual implementation (render-orphan-guard.py) is referenced (used by posture/verify-posture-projection.sh to enumerate versions) but lives in distribution/, outside this cluster's six directories.
- OSCAL/C2P — ABSENT. No OSCAL, C2P, or compliance-artifact-generation code anywhere in this cluster.
- Shift-left — PRESENT conceptually in posture (Kyverno admission-time mutate+validate is inherently a shift-left admission control) and in identity's STRICT mTLS/AuthorizationPolicy (admission/connection-time enforcement) but the term/thesis label itself is not used; no CI/pre-commit shift-left tooling exists in this cluster.
- Handbook — ABSENT as a discrete artifact; READMEs across all six directories serve a handbook-like documentation role (mermaid diagrams, 'what's here' tables, calibration knobs sections) but there is no dedicated handbook.md or generator.
- Sunset — PRESENT as the core mechanism of currency-controller: a version 'retired' from distribution/versions.yaml is the trigger for de-posture/evict; this is effectively the sunset lifecycle stage acted upon, though the word 'sunset' itself doesn't appear — the mechanism (retire-from-array → lose currency → lose reach/secret) is the real implementation.
- Notifications — ABSENT. No alerting, Slack/webhook, or notification code in this cluster; the CronJob's failure mode is just JobHistoryLimits and logs.
- Dashboards — ABSENT. No dashboard, Grafana config, or metrics-exposition code in any of these six directories; verify-*.sh scripts print to stdout only.

### Runtime dependencies

- Flux helm-controller — real, drives every HelmRelease in identity, posture-via-render, and access; up.sh scripts call `flux reconcile helmrelease` with a timeout and treat a timeout as non-fatal ('safe to re-run').
- SPIRE (spiffe helm-charts-hardened, versions spire-crds 0.5.0, spire 0.24.0) — real, the workload/device/human-adjacent attestation CA across identity, posture, access, and eud.
- Istio (base+istiod, 1.24.0, oci://gcr.io/istio-release/charts) — real, consumes SPIRE identity via the documented (non-istio-csr) Workload API socket path.
- Kyverno (MutatingPolicy/ValidatingPolicy CRDs, policies.kyverno.io/v1alpha1) — real; posture's mutate/validate trust boundary depends on it, but Kyverno's own installation is out of scope for this cluster (README says it comes from platform/engine, ticket 11) — not read/verified here.
- OpenBao (0.16.0, openbao-helm) — real chart, but running in dev/ephemeral mode with a hardcoded root token — simulated production posture.
- Dex (0.19.1, charts.dexidp.io) — real, but with in-memory storage and one hardcoded static password — a demo, not a federated identity provider.
- Pomerium Core (52.3.0, helm.pomerium.io) — real chart with a real policy structure, but its signing key is an empty placeholder, so the JWT-assertion trust chain to the kube-apiserver is not actually functional as configured.
- flux-operator ResourceSet (fluxcd.controlplane.io/v1 resourcesets 'policy-versions') — currency-controller's get_supported() reads this live in-cluster; SUPPORTED_VERSIONS env var is an explicit override 'for demo paths where flux-operator isn't installed', implying the ResourceSet is not reliably present.
- distribution/render-and-prove.py and distribution/render-orphan-guard.py (referenced, not in this cluster's file set) — posture's up.sh and verify script depend on these external distribution/ scripts for versioned rendering and version enumeration; not independently verified in this scan.
- QEMU/UTM + swtpm — real, locally-installed CLI tools (qemu-img confirmed to have actually run, producing real qcow2 files); swtpm/utmctl presence is only probed, not required, by verify-eud.sh.
- TPM/vTPM hardware or emulation — simulated only: no real manufacturer TPM anywhere in this cluster; the Mac (the only live presenting hardware) explicitly has none (Secure Enclave substitutes); the two EUD VMs' swtpm is never actually booted in this codebase (placeholders throughout).

### Verify scripts

| Script | Needs cluster | Proves |
|---|---|---|
| `platform/identity/verify-identity.sh` | False | Offline (always runs): PyYAML structural asserts that SPIRE/Istio/OpenBao HelmRelease values are wired correctly (controller-manager+OIDC+CSI enabled, trust domain acme.internal, agent socket path, is |
| `platform/posture/verify-posture-projection.sh` | False | Offline (always runs, requires the `kyverno` CLI + python3/PyYAML): kyverno test proves stamp-posture stamps-from-claim and clobbers a forger's posture, and posture-trust-boundary denies a forged/mism |
| `platform/currency-controller/verify-currency.sh` | False | Offline (always runs): currency.py's own selfcheck asserts (select_stale correctness, retire/re-add transitions, the both-labels-removed de-posture patch); an offline `plan` invocation against a JSON  |
| `platform/access/verify-access.sh` | False | Offline (always runs): access.py selfcheck (the graded ALLOW/STEP_UP/DENY behaviour matrix, proportionality, monotonicity); a PyYAML structural check that Dex is the OIDC issuer, Pomerium consumes tha |
| `platform/break-glass/verify-break-glass.sh` | False | Fully offline, no live tail at all: break-glass.py selfcheck (the full DENY/CAGE/STEP_UP/ALLOW behaviour matrix across all four fixture scenarios, including the money-shot 'same stale device caged on  |
| `platform/eud/verify-eud.sh` | False | Offline (always runs): JSON schema checks on both VM specs (TPM 2.0/swtpm declared, narrated as virtual, sane sizing); that tpm-devid-enroll.sh renders a valid ClusterStaticEntry on the acme.internal  |

**Notes:** This cluster maps six platform/ tickets (14, 15, 16, 18, 19, 20) forming a chain: identity (14, the SPIRE/Istio/OpenBao attestation root) → posture (15, Kyverno-stamped posture riding in the SVID path) → currency-controller (16, closing the admission-vs-live gap) → access (18, projecting the same root onto humans/devices via Pomerium/Dex) → break-glass (19, pricing human/device assurance by FAIR £, reusing fair.py and access.py rather than reimplementing) → eud (20, virtual Windows/Linux TPM devices proving the device-SVID mechanism the Mac can't). All six are self-consistently documented, cross-reference each other accurately in comments, and each verify-*.sh script is genuinely offline-first with an honestly-labelled, non-blocking live tail — none of the six scripts fabricate a pass when the live substrate is absent; they report 'skipped' or 'not applied yet'. Three live-discovered bugs are documented and fixed with regression asserts (istiod ENABLE_CA_SERVER, double-prefixed SPIFFE principal, missing ClusterSPIFFEID className). The weakest points for a drift review: (1) platform/posture is the only one of the six with any multi-version/ResourceSet-style delivery, and even that is explicitly narrated as 'DEMO PATH, not delivery' via a separate render-and-prove offline twin, not the real flux-operator ResourceSet path; (2) Pomerium's signingKey is empty — the actual JWT-trust chain from IAP to the kube-apiserver as configured would not function; (3) every device SVID (Mac, Windows EUD, Linux EUD) is still a REPLACE_WITH_ATTESTED_TPM_FINGERPRINT placeholder — no device in this codebase has ever completed real attestation; (4) break-glass.py, despite its README claiming it should be 'the forward-auth / external-authz decision a Pomerium route calls', has zero actual Pomerium/webhook integration anywhere in the six directories — it is pure decision logic invoked only by CLI; (5) feeds/Wardley/wargamer/PR-opening mechanisms are entirely absent from this cluster — none of that thesis machinery lives here, it must live in a different cluster the drift review should check separately.

## estate — original-org (policy-as-versioned-flux single-org reference implementation): pavf-fleet, pavf-policy, pavf-governance-agent, pavf-handbook-g

### Real

- Multi-version Kyverno policy coexistence on a live KiND cluster via ResourceSet-generated per-version matchConditions (fixed from the broken objectSelector approach), proven by verify-coexistence.sh against real admission verdicts (pavf-fleet/verify-coexistence.sh)
- Orphan guard: deterministic Deny catch-all templated from the same ResourceSet array as installed versions, proven to deny unlabelled/unknown-version pods and to report-not-evict pre-existing orphans (pavf-fleet/verify-orphan-guard.sh; pavf-fleet/clusters/cluster1/policy-versions.yaml lines ~180-260)
- Real gitsign identity-pinned tag verification + tag-resolves-to-commit check + kyverno-test release gate in pavf-policy/.github/workflows/release.yml, running on real tag pushes
- Real Renovate customManager (git-refs datasource) proven against the real multi-element array via an actual `npx renovate --platform=local` dry run against local git fixtures (pavf-fleet/verify-renovate.sh)
- Real PolicyReport-to-Prometheus metrics via Policy Reporter + kube-prometheus-stack, proven live including a non-evicted failing Audit workload (pavf-fleet/verify-monitoring.sh)
- Real gotk_resource_info Flux-revision metrics via kube-state-metrics customResourceState, proven live per installed version (pavf-fleet/verify-flux-dashboard.sh)
- Real Crossplane v2 + AWS provider-family CRD install with a genuine dependsOn/healthCheck ordering gate, proven by the sample RDS Instance CR only being appliable after CRDs are Established (pavf-fleet/verify-crossplane.sh, infrastructure/crossplane-sample/rds-instance.yaml)
- Real Flux notification Provider/Alert broadcasting GitRepository revision changes to an in-cluster echo receiver, proven via kubectl logs of an actually-delivered event (pavf-fleet/verify-notifications.sh)
- Real C2P result2oscal CronJob running every 15 minutes against live PolicyReports, output served over nginx for Grafana's infinity datasource (pavf-fleet/infrastructure/c2p/cronjob.yaml, oscal-file-server.yaml)
- Real per-cluster narrowing/retirement: cluster2 installs only >=2.0.0, and live retirement of a version tightens the orphan guard in the same reconcile, proven across both live kind-cluster1/kind-cluster2 contexts (pavf-fleet/verify-retirement.sh)
- Real governance-agent demonstrator: live `gh api` call to GitHub Security Advisories for kyverno/kyverno, with real severity/recency filtering, real title-based dedup query, and real `gh issue create`/`gh label create` writes when not DRY_RUN (pavf-governance-agent/demonstrator.sh)
- Real sunset-escalator: reads fleet's live sunset: dates via `gh api`, and on/after the date does a real `git clone`+edit+`git push`+`gh pr create` against fleet (never merges) -- wired into a real daily GitHub Actions cron in pavf-fleet/.github/workflows/sunset-escalator.yml with a documented real git-identity/org-toggle fix
- Real handbook generation via `git show`/`git ls-tree` plumbing against any policy checkout+tag, structurally unable to drift (pavf-handbook-generator/generate.sh), verified against a real clone of the real policy repo
- Real hash-keyed cache-freshness gate (verify-fresh.sh) for handbook summaries, proven to fail loudly on stale/missing cache and pass on a hash match

### Thin or stubbed

- governance-agent enforcement boundary was previously documented as a hard GitHub-App-scoped 403 permission boundary; corrected 2026-07-18/07-20 to state honestly that no such scoped token was ever set up -- the real guarantee is only 'the code never calls the forbidden gh/git command', not an API-enforced permission (pavf-governance-agent/SPEC.md §5, README.md)
- governance-agent demonstrator.sh has no scheduling wired up in this repo at all (no cron/workflow file here) -- must be invoked manually, unlike sunset-escalator.sh which is scheduled from pavf-fleet
- handbook-generator's --with-summaries `claude -p` call path is explicitly untested by verify.sh, which only exercises the cache contract via a hand-placed fixture cache file, never actually invoking claude (pavf-handbook-generator/verify.sh, generate.sh summarize())
- handbook-generator --with-summaries has no CI wiring anywhere (no ANTHROPIC_API_KEY secret provisioned, no workflow file in the repo) -- named as a real residual gap in the README, not silently skipped
- Crossplane sample RDS Instance CR deliberately 'sits unreconciled' -- no ProviderConfig, no cloud credentials anywhere in this cluster, by design (pavf-fleet/infrastructure/crossplane-sample/rds-instance.yaml) -- proves ordering only, not real AWS reconciliation
- notifications receiver is an in-cluster http-echo pod standing in for a real Slack/Teams webhook, explicitly documented as a substitute since 'this repo has no real chat-webhook credential' (pavf-fleet/infrastructure/notifications/provider.yaml, receiver.yaml)
- monitoring dashboards' OSCAL and Renovate panels are unfiltered by policy_version (documented limitation: OSCAL findings are control-level not per-version, and PRs bump multiple array elements at once)
- cluster cross-querying (a real cluster1+cluster2 combined Grafana view) is not implemented -- cluster2 deliberately runs no monitoring stack, so there is no second Prometheus to federate/query (pavf-fleet README)
- pavf-apps (app1/app2/app3, three identical nginx pods) is fully archived/superseded and not live -- kept only as history
- governance-agent watched-dependencies.yaml covers exactly one dependency (kyverno/kyverno) and one signal source, explicitly out of scope for cloud/regulatory-change ingestion and Wardley climatic signals per SPEC.md §6 ('bounded demonstrator scope')

### Risk and pricing

- None found in this cluster. No £/FAIR/appetite-band/penalty/TCoR computation anywhere in pavf-fleet, pavf-policy, pavf-governance-agent, pavf-handbook-generator, pavf-apps, or pavf-cloud. The closest artifact is OSCAL-formatted compliance evidence (pavf-fleet/infrastructure/c2p/component-definition.json mapping require-s3-bucket-encryption/require-rds-multi-az to NIST sc-28/cp-10, and pavf-cloud's harvested NIST 800-53r5 catalogue/profiles) -- this is control-mapping/assessment-results data, not a monetary risk or pricing model.

### Cages and enforcement

- Kyverno ValidatingPolicy validationActions: Deny (gate) vs Audit (lane-keeper) is the entire enforcement-tier mechanism -- see pavf-policy/workloads/kyverno/*/policy.yaml and cloud/*/policy.yaml `spec.validationActions`
- Orphan guard: a single deterministic Deny catch-all ValidatingPolicy templated from the same ResourceSet input array as the installed versions, making it structurally unable to drift from what's installed (pavf-fleet/clusters/cluster1/policy-versions.yaml lines ~180-260, cluster2/policy-versions.yaml equivalent) -- this is the 'locked door' the README describes, proven live by pavf-fleet/verify-orphan-guard.sh and verify-live.sh
- governed-namespace exclusion list on the orphan guard's namespaceSelector (kube-system, kyverno, flux-system, crossplane-system, monitoring, etc.) so infrastructure pods aren't caught by the catch-all (pavf-fleet/clusters/cluster1/policy-versions.yaml)
- No 'cage tiers' / 'Audit vs Deny graded enforcement rollout' concept beyond the fixed per-policy validationActions field; no dynamic de-posture or currency-controller mechanism found in this cluster
- governance-agent's SPEC.md §5 'never-edits-enforcement invariant' is the closest analogue to a cage boundary for the agent layer itself: code-level (no git/gh-pr call exists), honestly stated as not an API-enforced permission boundary (pavf-governance-agent/SPEC.md §5, README.md)

### Feeds, Wardley, war-gamer

- Real feed: GitHub Security Advisories API for kyverno/kyverno, queried live via `gh api repos/kyverno/kyverno/security-advisories` in pavf-governance-agent/demonstrator.sh -- real, not simulated
- Real feed: fleet's own live sunset: dates in clusters/cluster1/policy-versions.yaml, read via `gh api` in pavf-governance-agent/sunset-escalator.sh -- real, not simulated
- Real PR opened: sunset-escalator.sh does a genuine `git clone`+edit+`git push`+`gh pr create` against the fleet repo on/after a sunset date (never merges) -- proven live per fleet ticket-09 comments and wired into a real daily cron (pavf-fleet/.github/workflows/sunset-escalator.yml)
- No Wardley mapping or wargamer/proposer component exists anywhere in this cluster's code. governance-agent/SPEC.md §1 names Wardley climatic movement as a signal class but explicitly marks it 'Not automatable' and modelled only as a manually-curated climatic-signals.yaml file that SPEC.md describes but does not exist in this repo -- not implemented, spec-only
- GitHub issues opened for CVE/decision-framing (demonstrator.sh, sunset-escalator.sh) are real `gh issue create` calls, not narrated/simulated output, when DRY_RUN is false

### Original-thesis mechanisms

- Multi-version coexistence: present and live-proven -- pavf-fleet/clusters/cluster1/policy-versions.yaml (3 versions) and cluster2 (narrowed >=2.0.0), verify-coexistence.sh
- ResourceSet matrix: present -- the {version,tag,commit,policies[]} input array ranged over by resourcesTemplate is the crux mechanism (pavf-fleet/clusters/cluster1/policy-versions.yaml and cluster2 equivalent)
- Renovate bump PR: present -- pavf-fleet/renovate.json's customManager, proven against the real array via a real dry run (verify-renovate.sh); never automerged (packageRules pin + automerge:false)
- Signed tags: present -- gitsign identity-pinned verify-tag in pavf-policy/.github/workflows/release.yml, tag-immutability GitHub ruleset documented in pavf-policy/README.md
- Orphan guard: present -- deterministic Deny catch-all templated from the same array, live-proven in pavf-fleet/verify-orphan-guard.sh and verify-retirement.sh
- OSCAL/C2P: present -- real component-definition.json + a real 15-minute CronJob (c2p-collector) turning live PolicyReports into OSCAL assessment-results, served over nginx for Grafana (pavf-fleet/infrastructure/c2p/); pavf-cloud holds the harvested NIST catalogue/profiles as static data
- shift-left: partially present as verify-determinism.sh (static CEL grep) and pr-gate.yml (a pinned pr-gate-action gating merges) but no dedicated 'shift-left' pipeline stage beyond these
- handbook: present -- pavf-handbook-generator, a generic tool reading any tag's tree via git plumbing, with an optional claude-generated plain-language summary layer that is cache-freshness-gated but has no CI wiring
- sunset: present -- ADR-0010-style sunset: dates in the ResourceSet array, escalated to a GitHub issue then a real (never-auto-merged) retirement PR by pavf-governance-agent/sunset-escalator.sh, scheduled daily via pavf-fleet's workflow
- notifications: present -- Flux Alert/Provider broadcasting policy-source revision changes to an in-cluster echo receiver standing in for a real chat webhook (pavf-fleet/infrastructure/notifications/)
- dashboards: present -- Policy Reporter's own pre-built Grafana dashboards plus two hand-authored ConfigMap dashboards (flux-policy-dashboard: 4-panel 'which version/is it passing/are controls satisfied/adoption velocity' CIO story; estate-staleness-dashboard) auto-discovered by the Grafana sidecar (pavf-fleet/infrastructure/monitoring/)

### Runtime dependencies

- Flux (Flux Operator via FluxInstance, pinned 2.9.2 upstream-alpine) -- real, drives the whole cluster1/cluster2 reconciliation (pavf-fleet/flux-instance.yaml)
- Kyverno (>=1.18, chart 3.8.2/app 1.18.2 pinned) -- real, the live admission-webhook engine enforcing all ValidatingPolicies (pavf-fleet/infrastructure/kyverno/helmrelease.yaml)
- SPIRE -- not present anywhere in this cluster's manifests or scripts; not used
- Istio -- not present anywhere in this cluster's manifests or scripts; not used
- OpenBao -- not present; no secrets manager in this cluster
- Pomerium -- not present; not used
- Crossplane v2 (2.3.3) + AWS provider-family (S3, RDS v2.6.0) -- real CRD/provider install on KiND, but deliberately has no ProviderConfig/credentials, so nothing actually reconciles against AWS (pavf-fleet/infrastructure/crossplane*)
- trivy (trivy-operator 0.34.0, ClientServer mode) -- real, scans real app images for CVEs, several real live-debugged issues documented (DB download timeout, OOMKill) (pavf-fleet/infrastructure/monitoring/trivy-operator-helmrelease.yaml)
- C2P (c2p-collector image, digest-pinned) -- real CronJob reading real live PolicyReports and writing real OSCAL output every 15 minutes (pavf-fleet/infrastructure/c2p/cronjob.yaml)
- Renovate -- real, both the fleet's renovate.json customManager (proven via an actual npx renovate dry run in verify-renovate.sh) and referenced in policy repo's release process
- gitsign -- real, identity-pinned tag signature verification in pavf-policy/.github/workflows/release.yml, pinned binary+SHA256, offline Rekor mode
- GitHub Actions -- real workflows: pavf-policy/release.yml (tag-triggered release gate), pavf-fleet/pr-gate.yml (pinned pr-gate-action), pavf-fleet/sunset-escalator.yml (daily cron calling governance-agent's script), pavf-fleet/weekly-governance-nag.yml, pavf-fleet/checkbox-followthrough.yml
- claude -p (Claude CLI) -- real integration point in pavf-handbook-generator/generate.sh's summarize(), but unwired in CI (no ANTHROPIC_API_KEY secret) and untested by verify.sh, which never actually invokes it

### Verify scripts

| Script | Needs cluster | Proves |
|---|---|---|
| `pavf-fleet/verify-live.sh` | True | compliant labelled pod admits; unrecognised-department gate refuses; missing-department lane-keeper admits+PolicyReport-fails; unlabelled pod refused by orphan guard |
| `pavf-fleet/verify-coexistence.sh` | True | exactly 9 ValidatingPolicies present, no name collisions; every generated Kustomization dependsOn kyverno and waits; identical pod shape gets different verdicts pinned to 1.0.0 (Audit) vs 2.0.0 (Deny) |
| `pavf-fleet/verify-orphan-guard.sh` | True | no-label pod denied; unknown-version pod denied; guard's CEL allow-list mentions every installed version; a pre-existing orphan (created while guard absent) is reported as a PolicyReport failure but n |
| `pavf-fleet/verify-renovate.sh` | False | the one Renovate customManager finds exactly 3 deps in the real multi-element array against a local git fixture upstream, correctly reports a newer tag available for each without automerging (dry run, |
| `pavf-fleet/verify-retirement.sh` | True | cluster1 has 1.0.0 policies, cluster2 correctly doesn't; cluster2 denies a 1.0.0-pinned pod while cluster1 admits the identical pod; retiring 2.0.0 from cluster2's array live-prunes it and immediately |
| `pavf-fleet/verify-monitoring.sh` | True | policy_report_result Prometheus metrics exist for every installed version; a deliberately non-compliant Audit-mode pod shows as failing in Prometheus without being evicted |
| `pavf-fleet/verify-notifications.sh` | True | notifications Kustomization is Ready and the revision-echo receiver already holds (in current or --previous logs) a real delivered Flux event for one of the currently-installed policy sources |
| `pavf-fleet/verify-flux-dashboard.sh` | True | gotk_resource_info exists for every installed policy-version's GitRepository; flux-policy-dashboard ConfigMap carries the grafana_dashboard sidecar label; each version resolves both a 'where installed |
| `pavf-fleet/verify-crossplane.sh` | True | crossplane/crossplane-providers/crossplane-sample Kustomizations all Ready in dependency order; provider-family CRDs reached Established; the sample RDS Instance CR exists but Synced!=True (no Provide |
| `pavf-policy/verify.sh` | False | kyverno test fixtures pass/fail/skip correctly for every policy in the tree; kustomize build's nameSuffix/version label/matchConditions all agree with each other; each policy's rationale.md cross-refe |
| `pavf-policy/verify-live.sh` | True | generically (by validationActions, not hardcoded policy name) that Deny policies refuse their own failing fixture and Audit policies admit-but-report it, applied/removed directly via kubectl bypassing |
| `pavf-policy/verify-determinism.sh` | False | static grep that spec.validations/spec.matchConditions never reference advisory-metadata field names or time functions, as defence-in-depth on top of a structural Kyverno CEL-context argument |
| `pavf-policy/demo-removal/run.sh` | False | in a throwaway git worktree, adding then removing a policy is a pure git-diff deletion (no archive/deprecated flag, no lingering reference anywhere in the tree) |
| `pavf-handbook-generator/verify.sh` | False | against a real clone of the real pavf-policy repo at tag v1.0.3: generate.sh produces the expected handbook header/sections without invoking claude when --with-summaries is omitted; verify-fresh.sh co |
| `pavf-handbook-generator/verify-fresh.sh` | False | for a given policy checkout+tag, every policy's current rationale.md hash has a matching cached summary file; used both standalone and as the subject of verify.sh's test |

**Notes:** Last commit dates (2026-08-27 today): pavf-fleet 2026-07-20, pavf-policy 2026-07-18, pavf-governance-agent 2026-07-20, pavf-handbook-generator 2026-07-18, pavf-apps 2026-07-16 (archived), pavf-cloud 2026-07-14. All six repos are roughly 5-6 weeks stale relative to today, clustered around a late-July 'real-estate epic' / audit-wave period, with no commits since.

Six-org estate reference check: grepped the OSERA/ and sandbox-probe/ directories at repo root (the closest candidates for a broader multi-org estate tree) for any mention of pavf-fleet/pavf-policy/pavf-governance-agent/pavf-handbook-generator/pavf-apps/pavf-cloud -- no matches. The only tree that references these six repos by name is policy-as-versioned-flux/ itself (this original org's own hub/tracker: docs/SHOW-AND-TELL.md, spikes/c2p-real-job/README.md, and .scratch/faithful-floor issue files), which is this cluster's own origin repo, not an external six-org estate. So: nothing outside this original-org's own hub references these repos; they appear to be self-contained and not consumed by any broader multi-org estate structure found in this filesystem.

Two other things worth flagging for a drift review: (1) pavf-policy's own README table still lists v2.2.0 as "(pending) not yet tagged" while pavf-fleet's ResourceSet already pins tag: "2.2.0" with a real commit SHA and treats it as a real content release shipping the cloud plane -- either the policy README is stale or the tag landed after the README's last edit; worth confirming directly against the policy repo's actual tag list. (2) governance-agent's demonstrator.sh has no scheduled trigger anywhere in this codebase (unlike sunset-escalator.sh, which pavf-fleet schedules daily) -- SPEC.md's contract describes it as proving one live signal path end-to-end, but nothing here runs it unattended.

## estate — nist + ico (regulators)

### Real

- nist catalog is the genuine, verbatim NIST SP 800-53 Rev 5.2.0 OSCAL content (usnistgov/oscal-content), sha256-checked against recorded provenance -- nist/catalog/CATALOG_VERSION.json, verified live by nist/scripts/verify_catalog.py
- LOW/MODERATE/HIGH baseline profiles are genuine NIST-shipped OSCAL profiles, resolved exact-string (bare ids, no case-fold, no prefix strip) against the catalogue -- nist/scripts/verify_baselines.py:34-47, ran live: LOW=149, MODERATE=287 (holds ac-6/cm-6/ac-6.10), HIGH=370, all in-catalogue
- ico penalty schema fines are real, cited public enforcement actions (BA 2020, Marriott 2020, TikTok 2023, Clearview AI 2022, Doorstep Dispensaree 2019 in v2) -- ico/schema/v1/penalty-schema.json:16-45, v2 diff
- ico schema is genuinely ed25519-signed and offline-verified, and a tamper test genuinely fails verification -- ico/schema/verify.sh:18-19, verify-penalty-feed.sh:22-35, ran live
- the v1->v2 schema bump genuinely changes fair.py's computed ALE with zero fair.py code changes -- ico/verify-penalty-feed.sh:40-51, ran live (£16,901,472 -> £9,039,791 for uk-gdpr/lower-tier warn)
- combining two regimes on one breach (ticket 18) genuinely raises ALE further via fair.py's correlated pricing -- ico/schema/to_fair_scenario.py:78-112, ico/verify-penalty-feed.sh:53-65, ran live (+£1,966,638)
- gitsign keyless signing/verification design (identity-pinned regexp, offline Rekor bundle) is a real, complete workflow spec in both repos' release.yml, matching driftwood's own convention
- EXPECTED_IDENTITY_REGEXP anchoring is genuinely correct and self-tested against foreign-org/foreign-repo/foreign-workflow/unanchored-suffix spoofing attempts in both repos, ran live
- bump-nist-pin.sh genuinely produces a real, reviewable sed diff of the Flux GitRepository pin file -- driftwood/scripts/bump-nist-pin.sh:16-22

### Thin or stubbed

- ico's ed25519 signing key is a repo-local demo keypair via openssl, not gitsign/cosign+Rekor -- explicitly flagged 'ponytail: repo-local demo key' in ico/schema/sign.sh:4-8 and ico/README.md:26, with a named upgrade path (swap for cosign sign-blob) that is not implemented
- bump-nist-pin.sh 'stops at the diff': it never pushes, never opens a PR, and says so explicitly -- driftwood/scripts/bump-nist-pin.sh:3-4,38-40 ('Never pushes or opens the PR itself... it stops at the diff')
- to_fair_scenario.py's loss-event-frequency (how often a breach happens) is NOT sourced from the schema at all -- it is a flat 'ponytail' editorial constant (DEFAULT_WARN_LEF=(1,2,4), DEFAULT_DENY_LEF=(0,0,1)) applied uniformly per regime regardless of institution -- ico/schema/to_fair_scenario.py:19-22,38-39
- which regulatory regimes actually apply to which workload is explicitly still open/undecided -- ico/README.md:41 and to_fair_scenario.py:29,85-86 both flag this as ticket 17, a named unresolved gap, not a stubbed-but-hidden one
- sign.sh cannot be exercised from this worktree: the private key ico-signing-key.pem is absent (only the .pub.pem is checked in) -- ico/schema/keys/ contains only ico-signing-key.pub.pem, confirmed by ls
- both repos' cut-release.yml/release.yml GitHub Actions workflows were inspected only, not executed in this session -- they require a live GitHub remote, a real OIDC token, and Fulcio/Rekor connectivity none of which are available offline here

### Risk and pricing

- ico/schema/to_fair_scenario.py:47-75 (lm_triple) -- converts a penalty-schema formula (pct_of_global_turnover, per_violation_tier, per_month_escalating) into a (min,mode,max) loss-magnitude triple grounded in real cited fines
- ico/schema/to_fair_scenario.py:78-112 (build_scenario) -- combines multiple regimes on one breach into a single fair.py scenario with a shared/correlated LEF (ticket 18)
- ico/verify-penalty-feed.sh:37-65 -- calls platform/fair/fair.py directly (python3 fair.py summary ...) to compute and print real ALE figures from the schema, demonstrating the schema-bump-moves-the-£ property live
- platform/compose/composition.py:2269-2404 -- consumes an ico penalty-schema bump (v1->v2) as a live input that moves 'uncaged exposure' pricing in composition's own price rendering (per grep; not read in full in this pass, flagged as a touchpoint)
- platform/graded/cage.py:22 -- names 'the nist OSCAL risk / ico penalty consumers' as what the cage-tier machinery reads (per grep; not read in full in this pass, flagged as a touchpoint)
- platform/feeds/to_fair_scenario.py + platform/feeds/README.md:5,59 -- platform's own feeds machinery documents itself as sharing the identical (min,mode,max) scenario shape with ico/schema/to_fair_scenario.py, i.e. ico's converter is the pattern platform's feed ingestion follows (per grep; not read in full in this pass, flagged as a touchpoint)

### Cages and enforcement

- No cage-tier, Audit/Deny, orphan-guard, governed-namespace, de-posture, or currency-controller logic exists inside nist/ or ico/ themselves -- these repos are pure regulator publishers (data + signing + release plumbing). The only touchpoint found is a one-line name-check in platform/graded/cage.py:22 identifying nist OSCAL risk and ico penalty data as inputs cage-tier consumers read; the cage/enforcement mechanism itself lives entirely in platform/, out of this cluster's scope.

### Feeds, Wardley, war-gamer

- Neither nist nor ico opens a real GitHub PR anywhere in this cluster: nist's driftwood/scripts/bump-nist-pin.sh explicitly stops at a local sed diff and states it never pushes or opens the PR itself (driftwood/scripts/bump-nist-pin.sh:3-4,38-40); no equivalent bump script for ico was found under ico/ itself
- Neither repo reads a real live external feed: nist's catalog and ico's penalty schema are both static, checked-in JSON snapshots with recorded provenance/fetch timestamps (fetchedAt fields), not live-polled sources -- nist/catalog/CATALOG_VERSION.json, ico/schema is versioned by hand-authored v1/v2 directories
- platform/wargamer/wargamer.py and platform/wargamer/tier_pr.py were found (by grep) to reference 'ico'/related terms but were not read in this pass -- they live outside this cluster's file scope (nist, ico) and were not inspected; flagged as an area a broader platform-cluster review should cover
- platform/feeds/to_fair_scenario.py explicitly mirrors ico's own to_fair_scenario.py shape (platform/feeds/README.md:5,59), suggesting platform's feed ingestion is designed to accept regulator-shaped inputs the same way ico's script does -- but whether platform/feeds actually ingests a live external feed was not verified in this pass (out of cluster scope)

### Original-thesis mechanisms

- Multi-version coexistence: nist ships v1.0.0 and v1.1.0 as immutable tags (nist/.git tags); ico ships v1.0.0 with v1/v2 schema dirs coexisting on disk (ico/schema/v1, v2) -- both versions readable and independently signed/verified simultaneously
- ResourceSet/baseline matrix: nist/catalog/BASELINE_VERSIONS.json + LOW/MODERATE/HIGH profiles is the concrete instance of this mechanism for NIST controls -- present in full
- Renovate/dependency-bump PR: driftwood/renovate.json, ludlow/renovate.json, tuppence/renovate.json all reference nist (per grep); driftwood/scripts/bump-nist-pin.sh demonstrates the reviewable-diff half of this mechanism for the nist pin specifically, but explicitly does not open the PR itself -- the bump-PR mechanism is present but stops short of actually opening a PR, from this cluster's side
- Signed tags: both nist and ico publish gitsign keyless-signed (Fulcio/Rekor) tags via cut-release.yml -- present as workflow spec in both repos, not exercised live in this session (needs real GH remote)
- Orphan guard: not present anywhere in nist/ or ico/ -- no references found; this mechanism, if it exists, lives entirely in platform/ or the enactment repos, out of this cluster
- OSCAL/C2P: nist/catalog/*.json IS the OSCAL artifact this mechanism consumes -- the catalog and baseline profiles are genuine OSCAL documents; the C2P (compliance-to-policy) plumbing itself lives in platform/oscal (referenced by platform/oscal/fixtures/component-definition-unknown-control.json per grep), out of this cluster's file scope
- Shift-left: driftwood/.github/workflows/shift-left.yml, ludlow/.github/workflows/shift-left.yml, tuppence/.github/workflows/shift-left.yml all reference nist (per grep) -- the shift-left gate mechanism lives in the institution repos, consuming nist as an input; not itself present inside nist/ or ico/
- Handbook: no reference found in nist/ or ico/
- Sunset: no reference found in nist/ or ico/
- Notifications: no reference found in nist/ or ico/
- Dashboards: no reference found in nist/ or ico/

### Runtime dependencies

- gitsign (keyless signing via Fulcio/Rekor) -- real tool, pinned version+sha256 in both repos' workflows, but only exercised inside GitHub Actions (not run in this offline session)
- openssl pkeyutl (ed25519 sign/verify) -- real, used directly by ico's sign.sh/verify.sh, exercised live in this session
- platform/fair/fair.py -- real, unmodified sibling dependency consumed via relative path by ico/verify-penalty-feed.sh and ico's release.yml (checked out as a second sibling path in CI); present in this estate clone and ran live successfully
- Flux GitRepository (source-controller) -- real Flux CRD spec in driftwood/ludlow/tuppence's gotk-sync-nist.yaml pinning nist by tag+commit; not reconciled live in this session (no cluster touched)
- GitHub Actions / gh CLI / Rekor -- required for cut-release.yml and release.yml to actually run; simulated/unexercised here, inspected as static YAML only
- python3 stdlib (json, hashlib, statistics, argparse) -- real, used throughout, no external deps beyond stdlib for the verify/scenario scripts

### Verify scripts

| Script | Needs cluster | Proves |
|---|---|---|
| `nist/scripts/verify-catalog.sh` | False | catalog is well-formed OSCAL with matching sha256; LOW/MODERATE/HIGH baselines resolve exact-string against the catalogue with the required control membership (ac-6/cm-6/ac-6.10 in MODERATE, ac-6 abse |
| `nist/scripts/verify_catalog.py` | False | catalog sha256 matches recorded metadata, is a genuine OSCAL document (uuid/metadata present, uuid matches recorded source), group/control counts match recorded metadata (1196 controls, 20 groups), an |
| `nist/scripts/verify_baselines.py` | False | each baseline's sha256 matches, imports the catalogue exactly once by href, resolves every listed id (bare, exact-string) into the catalogue with no missing ids, matches the recorded control count, an |
| `nist/scripts/verify-cert-identity-regexp.sh` | False | the EXPECTED_IDENTITY_REGEXP extracted live from release.yml matches this org/repo/workflow on main and release/x.y.x branches and rejects foreign org, foreign repo, foreign workflow path, wrong branc |
| `nist/verify-certificate-identity-regexp.sh (top-level, ticket cs-14)` | False | same regexp property as above, standalone top-level entry point. Not separately re-run (duplicate of the scripts/ version's assertions) but present and consistent. |
| `ico/schema/verify.sh` | False | for a given version dir, the schema file and its .sig both exist, schema_version field matches the directory name, and the ed25519 signature verifies against the checked-in public key. Ran live for v1 |
| `ico/verify-penalty-feed.sh` | False | v1 and v2 signatures verify; a tampered copy of v1 fails signature verification; platform/fair/fair.py (unmodified, sibling checkout) consumes schema-derived scenarios and computes real differing ALE  |
| `ico/verify-certificate-identity-regexp.sh` | False | same EXPECTED_IDENTITY_REGEXP property as nist's version, scoped to policy-as-versioned-ico/ico. Ran live: OK. |

**Notes:** Both repos are minimal, self-contained regulator publishers: no Kubernetes manifests, no CronJobs, no long-running services live inside nist/ or ico/ themselves -- everything here is either static signed/versioned data, an offline verify script, or a GitHub Actions release workflow (uses gh CLI, gitsign, Fulcio/Rekor -- none exercised live in this offline session, only inspected as YAML). Every offline verify script that could be run (7 of them) was actually run in this session and passed for real, with genuine computed numbers (control counts, sha256 matches, and real £ ALE deltas from fair.py), not narrated or hardcoded output.

Last commit dates: nist's most recent commit is 2026-08-25 (a merge of 'policy-composition/tickets-09-16-wip', following a 2026-08-22 cs-14 identity-regexp commit); ico's most recent is 2026-08-22 (the same cs-14 identity-regexp fix), with earlier history back to 2026-08-20. Both are current relative to today's date (2026-08-27), i.e. actively maintained within the last week, not stale.

Cross-references from the rest of the six-org estate: confirmed via grep. driftwood, ludlow, and tuppence (the three institution repos) each carry a renovate.json, a shift-left.yml, a cut-release.yml, and a Flux GitRepository pin (gotk-sync-nist.yaml, both in gitops/ and .work/seed/) that names nist explicitly -- i.e. nist is a real, referenced upstream dependency across all three institutions, not just a standalone unused repo. platform/ references ico in five real files (wargamer.py, tier_pr.py, party_artefact.py, composition.py, cage.py, feeds/to_fair_scenario.py, feeds/README.md) beyond the direct fair.py consumption already verified live -- these were located by grep but not individually read in full in this pass since they sit in platform/, outside this cluster's requested file scope (nist, ico); a platform-cluster review should read composition.py:2269-2404 and cage.py in full to confirm exactly how deeply the pricing/cage machinery depends on ico's schema shape. No unresolved contradiction found between README claims and actual file contents in either repo -- both READMEs' factual claims (control/baseline counts, script names, what's "real" vs "repackaged") checked out exactly against the live-run verify scripts.

## estate — estate adopters: driftwood, tuppence, ludlow (the three regulated institutions of the six-org estate, cloned under /Users/cns/httpdocs/contr

### Real

- Flux reconciliation from a tag+commit-pinned GitRepository on a local KinD cluster — driftwood/scripts/up.sh:62-102, proven by real drift samples carrying revision sha1:2fc21df8858b2ee98f07e3c89e32189a919557f4
- gitsign-signed annotated release tags cut by an ambient Actions identity — v1.0.0 and v1.1.0 with real signature blocks in all three repos (driftwood/.github/workflows/cut-release.yml:103-112)
- Offline, identity-pinned gitsign verify-tag on every tag push — driftwood/.github/workflows/release.yml:76-86
- Identity-regexp anchoring proved with the REAL gitsign binary against real tags — driftwood/scripts/verify-identity-regexp.sh:32-47, negative shapes via grep -E at :60-78
- Cross-org CI checking out platform/nist/ico at this repo's own pins, refusing on commit disagreement — driftwood/.github/workflows/shift-left.yml:89-99 and :311-331
- Adopter gate composing a bump from the publisher's signed evidence, never recomputing it — driftwood/.github/scripts/adopter-gate.py:284-330 (compose) and :232-270 (verify_evidence)
- Real cosign verify-blob refusals: missing bundle, garbage bundle, key-signed bundle under identity pinning — driftwood/.github/scripts/adopter-gate.py ~:712-780; ludlow/verify-adopter-gate.sh Parts C and E (offline, egress blocked via HTTPS_PROXY, committed trusted_root.json)
- compose-check: composed artefact regenerated on every PR and byte-diffed against the committed copy — driftwood/.github/workflows/shift-left.yml:332-357
- Pre-tag re-render: composition.py verify runs before any tag is created — driftwood/.github/workflows/cut-release.yml:85-93
- Forced-drift latency campaign really executed against a real cluster — driftwood/drift/forced-campaign.log (2026-08-15, four trials) plus 464 real samples
- Probe writes an unreachable sample rather than nothing, so silence reads as a coverage hole — driftwood/drift/probe.sh:39-43
- Posture gate logic parsed out of the real shipped Istio/OpenBao manifests and asserted offline — tuppence/reset/reach.py:32-122
- PR-body splice with marker replacement (first run appends, re-run replaces in place) — driftwood/.github/scripts/adopter-gate.py:107-118, proved in selfcheck

### Thin or stubbed

- The composed Kyverno policy set is never applied to any cluster by these repos — composed/policies/** is generated YAML in git; gitops/apps/kustomization.yaml (driftwood:1-6) reconciles only a namespace and two ConfigMaps
- gitops/platform/platform-pin.yaml (the ResourceSet multi-version fan-out) is explicitly opt-in and NOT in the Phase-0 reconcile — driftwood/gitops/platform/platform-pin.yaml:6-11; no evidence it was ever applied
- The 'live version' surface is a Phase-0 marker ConfigMap standing in for the real policy set — driftwood/gitops/apps/version-configmap.yaml:8-11 says so in the file
- driftwood/gitops/flux-system/gotk-sync.yaml:22-23 leaves the commit COMMENTED OUT, so the canonical committed form lacks the belt-and-braces pin its own README claims; only the up.sh-generated in-cluster object has one
- verify-reconcile.sh's nist assertion is stale in all three: catalogVersion 1.0.0 asserted (driftwood:38, tuppence:39, ludlow:39) against a committed ConfigMap saying 1.1.0 (nist-pin-configmap.yaml:20)
- The README risk-skin story (driftwood Audit-heavy vs ludlow 'Deny-heavy (strictest)') is not visible in the composed artefacts: the three composed policy trees are byte-identical apart from the composed-for label — require-nonroot is Audit and posture-trust-boundary is Deny in all three (composed/policies/v3.0.0/*.yaml:14-15)
- evidence.json cages[] is empty and prices[] changed:false in all three — the pricing/tiering path exists but has never moved anything
- scripts/bump-nist-pin.sh stops at a printed diff and never opens the PR it narrates — driftwood/scripts/bump-nist-pin.sh:16, :26
- Renovate is configured and dispatchable but no Renovate-authored bump PR is evidenced; the platform pin moved by hand-authored ticket-18 commits
- The cosign ACCEPT path (a valid Fulcio keyless bundle) is unprovable outside a live Actions run, disclosed in all three gates and both offline twins — driftwood adopter-gate.py ~:545-560; tuppence/scripts/verify-adopter-gate.sh:14-30; ludlow/verify-adopter-gate.sh:28-42
- ludlow's adopter_gate.py selfcheck mocks verify_evidence/_run/declared_bump — ludlow/.github/scripts/adopter_gate.py:641-666, :828-846, :906
- tuppence/reset live proof is conditional: verify-reach-secrets.sh:55-98 skips reach/secret checks when the substrate is absent and still prints PASS
- tuppence and ludlow have identity-regexp verification SCRIPTS but no workflow running them — only driftwood has .github/workflows/verify-identity-regexp.yml
- drift/README.md claims samples.jsonl and forced-campaign-samples.jsonl are untracked; both are in fact committed (git ls-files drift/)
- Organic drift coverage is ~3 samples against a declared 91-day hourly window — far under verdict.yaml's own 0.90 reading gate, so no branch may be read
- propose-tier.yml would find nothing to propose today (prices changed:false) and has no committed run evidence
- The committed .work/ trees (nist-seed OSCAL JSON, bare .git contexts) are up.sh build residue, not source

### Risk and pricing

- tuppence/gitops/apps/risk-appetite-configmap.yaml:16-18 — toleranceGBP 15000, skin 'toward-strict', reconciled as an audit-readable mirror of platform/risk/appetite.json
- ludlow/gitops/apps/risk-appetite-configmap.yaml:16-18 — toleranceGBP 5000, skin 'Deny-heavy (strictest)'
- driftwood has NO risk-appetite ConfigMap (gitops/apps/kustomization.yaml:1-6) despite platform/risk/appetite.json carrying a driftwood entry — an asymmetry the READMEs never mention
- tuppence/verify-reconcile.sh:41-46 and ludlow/verify-reconcile.sh:41-46 — the only place in this cluster where a £ figure is checked against its source of truth (platform/risk/appetite.json orgs.<org>.tolerance)
- composed/evidence.json prices[] — driftwood: ico pricing £16,901,471.55 tier deny (proposed_as issue), platform threat £19,558.55 tier baseline (proposed_as label); tuppence: same ico price, threat £222,574.31 tier deny; ludlow: same ico price, threat £318,229.78 tier deny. All changed:false; computed by platform/compose/composition.py and only consumed here
- composed/evidence.json cages[] empty in all three — no cage tier has been priced into an enforcement change
- .github/workflows/propose-tier.yml:60-72 — the £-derived tier proposal path: reads composed/evidence.json prices/tiers and asks platform/wargamer/tier_pr.py to open a PR (tier change) or an issue (proposed deny)
- driftwood/drift/verdict.yaml:34-46 — the risk basis stated in the £ engine's own terms (path_admission_threshold 2, evidence_ladder_version 2); the amendment at :116-129 sends any impact that loses its continuity evidence into the unpriced structural blast radius
- FAIR, appetite bands, penalties and TCoR are NOT computed anywhere in this cluster — the ico pricing parent (ico/schema/to_fair_scenario.py) sits outside it; these repos only mirror and consume

### Cages and enforcement

- composed/policies/v{2.0.0,2.0.1,3.0.0}/cage-tier.yaml — Kyverno MutatingPolicy with the three-tier dial (baseline/restricted/quarantine -> cpu/mem limits, priorityClass, harden flags, a coraza WAF sidecar for restricted+quarantine, capabilities drop ALL when hardened) — driftwood/composed/policies/v3.0.0/cage-tier.yaml:30-43
- composed/policies/v*/cage-netpol.yaml — GeneratingPolicy emitting a cage-egress-lockdown NetworkPolicy (egress to kube-system DNS only) for pods labelled posture.acme.io/caged=true — driftwood/composed/policies/v3.0.0/cage-netpol.yaml:33-34
- Graded enforcement: require-nonroot is Audit (driftwood/composed/policies/v3.0.0/require-nonroot.yaml:14-15) and posture-trust-boundary is Deny (same dir :14-15) — IDENTICAL in tuppence and ludlow, so the README's Audit-here/Deny-there proportionality claim is not realised in the composed artefacts
- Orphan guard: composed/orphan-guard.yaml:12-13 Deny, allow-list rendered as ['2.0.0','2.0.1','3.0.0'] at :30, annotated inherited-from platform@1.1.1, source distribution/versions.yaml — present in all three
- Governed namespace guard: composed/governed-namespace-guard.yaml:12-13 Audit, CREATE-only on pods in namespaces labelled policy-as-versioned.dev/governed=true, message 'Silence is not an exemption (ADR-0014)'
- The governed declaration itself: gitops/apps/namespace.yaml:14 (all three) sets policy-as-versioned.dev/governed: "true"; HEADER.yaml:24-25 mirrors it as advisory metadata
- Ungoverned record: tuppence/composed/HEADER.yaml:600-601 and evidence.json ungoverned[] name tuppence-reset (driftwood and ludlow: empty)
- De-posture / currency controller: NOT in this cluster — referenced from tuppence/reset/README.md:47-48 as ticket 16's controller living in platform; the consequence (drop to base SVID, lose both globs) is asserted offline at tuppence/reset/reach.py:112-113
- posture-trust-boundary (Deny) is the anti-forgery rule — a user-supplied or mismatched posture.acme.io/version label is refused: driftwood/composed/policies/v3.0.0/posture-trust-boundary.yaml:37-39
- Reach/secret enforcement (tuppence only): Istio ALLOW-only on acme.internal/posture/2.0.0/* (tuppence/reset/authorizationpolicy.yaml:35-41) and OpenBao bound_claims glob (tuppence/reset/openbao-role.yaml:45-54); the DestinationRule SAN override (destinationrule.yaml:30-36) is the calibration knob that must move with them
- Nothing in these repos APPLIES any composed Kyverno policy to a cluster — enforcement here is committed artefact plus CI gate, not a running admission controller

### Feeds, Wardley, war-gamer

- REAL PR-opening path: .github/workflows/propose-tier.yml (driftwood:60-72, and the tuppence/ludlow variants) runs platform/wargamer/tier_pr.py with contents:write / pull-requests:write / issues:write and really commits, pushes and opens a PR, or an issue for a proposed deny. Trigger is a MERGED pin-bump PR or workflow_dispatch — never scheduled (propose-tier.yml:18). No committed run evidence, and prices changed:false means it currently no-ops
- REAL PR-editing path: shift-left.yml's cs-29 step edits the pull request BODY via `gh pr edit --body-file`, splicing the gate's own marked span (driftwood:177-224; tuppence:202-225; ludlow:248-259), and posts a signed attestation comment (driftwood:245-270)
- NARRATION ONLY: driftwood/scripts/bump-nist-pin.sh:16-26 prints the diff and stops — 'next (human/CI, not this script): commit, gitsign, open PR'
- Wardley maps: ABSENT from this cluster — no map, no evolution axis, no reference in any of the three repos
- Wargamer: the engine is platform/wargamer/* (wargamer.py, tier_pr.py, proposer_bounds.py, scenarios/, fixtures/threat-register/); this cluster is only its caller and subject. The proposer's no-merge property is asserted in the workflow header (propose-tier.yml:8-10) and enforced by those platform modules' own selfchecks, not here
- Feeds: the only external data ingested are PINNED GIT DEPENDENCIES — nist 800-53 OSCAL catalog v1.1.0 (gotk-sync-nist.yaml:28-29) and platform v1.1.1 (platform-pin.yaml:24-25), plus ico at its default branch in CI (shift-left.yml:325-330, ico ships no tags). Renovate's git-refs datasource is the only live-polling mechanism and it is dispatch-only. No HTTP feed, no threat-intel feed, and no simulated feed generator exists here
- Committed .work/nist-seed/*.json are real NIST SP 800-53 rev5.2.0 catalog and LOW/MODERATE/HIGH baseline profiles — real regulator data, but an up.sh build artefact rather than a live feed

### Original-thesis mechanisms

- Multi-version coexistence — PRESENT as artefact only: composed/policies/{v2.0.0,v2.0.1,v3.0.0}/ in all three, each policy gated on 'only-this-policy-version'; never installed on a cluster from these repos
- ResourceSet matrix — NOT here, consumed by reference: gitops/platform/platform-pin.yaml:44-48 reconciles platform's ./distribution, opt-in and unapplied; the array's contents are mirrored into orphan-guard.yaml:30
- Renovate bump PR — MECHANISM PRESENT, PR UNEVIDENCED: renovate.json's two customManagers maintain the {tag, commit} pair; renovate-run.yml is workflow_dispatch-only; the actual pin bumps were hand-authored ticket-18 commits
- Signed tags — REAL: v1.0.0 and v1.1.0 in all three repos carry gitsign SIGNED MESSAGE blocks, cut by cut-release.yml, verified offline and identity-pinned by release.yml, with per-org anchoring scripts
- Orphan guard — PRESENT: composed/orphan-guard.yaml (Deny) in all three, allow-list rendered from platform's version array
- OSCAL / C2P — PARTIAL: real NIST OSCAL catalog pinned as a Flux GitRepository and mirrored in nist-pin-configmap.yaml (catalogVersion 1.1.0, nistRevision 5.2.0, oscalVersion 1.2.2, baselineName MODERATE, cross-checked against party.yaml by party_artefact.py). C2P is named only as future plumbing (nist-pin-configmap.yaml:12). 285 controls are recorded as holes in every composed artefact
- Shift-left — REAL: .github/workflows/shift-left.yml in all three runs platform/shift-left/ci-check.py against deploy/pod.yaml on every PR with no paths filter, plus the party-artefact check, the adopter gate and compose-check
- Handbook — ABSENT from this cluster
- Sunset / retirement — PRESENT AS RULE, not as an event: retirement forces a major in every adopter gate (driftwood/.github/scripts/adopter-gate.py:289-295; ludlow's docstring step 3; tuppence's docstring), prune:true on both Kustomizations, and the orphan guard stops allowing a removed version. No version has actually been retired here
- Notifications — ABSENT: no Slack, Alertmanager or notification-controller; the closest thing is the PR comment/PR body write from shift-left.yml
- Dashboards — ABSENT: no Grafana, no dashboards; Renovate's dependencyDashboard is explicitly disabled (renovate.json:7 in all three)

### Runtime dependencies

- Flux (source-controller + kustomize-controller) — REAL, installed by up.sh into KinD; drives the reconcile the drift probe samples
- KinD + Docker — REAL, one control-plane node per org (kind/<org>.yaml)
- Kyverno — REAL binary in CI (kyverno CLI 1.18.2, sha256-pinned, shift-left.yml:115-124) via platform/shift-left/ci-check.py; the Kyverno CRDs the composed policies target are never installed on a cluster by these repos
- flux-operator (ResourceSet) — DECLARED as a prerequisite for gitops/platform only; never installed or exercised here
- cosign 3.1.3 — REAL, sha256-pinned; signs the shift-left attestation keyless (CI only) and verifies platform's evidence; verify path proven offline in ludlow via committed trusted_root.json
- gitsign 0.17.1 — REAL, sha256-pinned; really signed v1.0.0/v1.1.0 and really verifies them (offline Rekor mode)
- Rekor / Fulcio (Sigstore) — REAL in CI via Actions OIDC; OFFLINE/pinned for verification (GITSIGN_REKOR_MODE=offline; ludlow's committed trusted_root.json)
- GitHub Actions — REAL, five to six workflows per repo with cross-org checkouts of policy-as-versioned-platform/nist/ico
- Renovate 44.37.1 — configured and dispatchable (self-hosted npx), but no evidenced bump PR in these repos
- kustomize 5.8.1 — REAL, sha256-pinned, used as the release gate (build only, no cluster)
- SPIRE — REAL manifests and live-discovered findings, but the substrate lives in platform/identity; tuppence/reset consumes it and degrades to offline-only when absent
- Istio (AuthorizationPolicy, DestinationRule) — same: real manifests, real live findings recorded, applied onto an externally provisioned substrate
- OpenBao — REAL Job manifest creating a posture-bound jwt role in dev mode (root token, openbao/openbao:latest unpinned and flagged in-file as a tunable knob); only reachable with the substrate up
- Pomerium — ABSENT from this cluster
- Crossplane — ABSENT
- trivy / vulnerability scanning — ABSENT
- C2P / OSCAL tooling — PARTIAL: real NIST OSCAL catalog pinned and mirrored (nist-pin-configmap.yaml), but C2P is named only as 'future plumbing' (nist-pin-configmap.yaml:12); no C2P code here
- platform/compose/composition.py, platform/party/party_artefact.py, platform/shift-left/ci-check.py, platform/wargamer/tier_pr.py — REAL cross-repo library dependencies, always invoked through the pinned platform checkout, never vendored

### Verify scripts

| Script | Needs cluster | Proves |
|---|---|---|
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/driftwood/verify-reconcile.sh` | True | GitRepository Ready + pinned tag/commit, Kustomization Ready, namespace + live-version ConfigMap reconciled, nist GitRepository Ready + pinned, nist-pin ConfigMap present. Its nist catalogVersion asse |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/tuppence/verify-reconcile.sh` | True | Same four steps for tuppence plus step 5: the risk-appetite ConfigMap tolerance is 15000 AND matches platform/risk/appetite.json orgs.tuppence.tolerance (a real cross-repo £ consistency check, needs a |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/ludlow/verify-reconcile.sh` | True | Same as tuppence's with tolerance 5000 / orgs.ludlow.tolerance. |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/driftwood/scripts/verify-identity-regexp.sh` | False | Layer 1 (load-bearing): real gitsign verify-tag of every v*.*.* tag against release.yml's real EXPECTED_IDENTITY_REGEXP and issuer. Layer 2: grep -E negative shapes (foreign org/repo/workflow path/ref |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/tuppence/scripts/verify-identity-regexp.sh` | False | Anchoring proof for BOTH tuppence's release.yml EXPECTED_IDENTITY_REGEXP and shift-left.yml's EVIDENCE_EXPECTED_IDENTITY_REGEXP, using bash [[ =~ ]] ERE rather than the real gitsign binary (declared a |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/ludlow/verify-certificate-identity-regexp.sh` | False | Pure bash-ERE match/reject table for ludlow's release.yml EXPECTED_IDENTITY_REGEXP including the literal-dot case (githubXcom rejected). No gitsign binary, no CI workflow runs it. |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/tuppence/scripts/verify-adopter-gate.sh` | False | Six scenarios against a real local platform clone: D — the real currently-tagged v1.0.0 honestly refuses on missing evidence; C — commit-pin mismatch refused; D2 — real cosign rejects a present-but-ma |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/ludlow/verify-adopter-gate.sh` | False | Part A identity regexp match/reject incl. workflow-rename-breaks-it and a cross-check it is not release.yml's own constant; Part B throwaway platform+ludlow git repos proving resolved-commit refusal,  |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/tuppence/reset/verify-reach-secrets.sh` | False | Offline core (unconditional): reach.py selfcheck — the Istio principal glob and the OpenBao bound_claims glob are the same current-posture prefix, admit a current SVID and refuse stale, de-postured an |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/driftwood/.github/scripts/adopter-gate.py --selfcheck` | False | read_pin against a real multi-document stream; verify_pinned_commit match and mismatch on a real git repo; read_policy_array_at/diff_arrays/fetch_tag against real tags and a real clone-of-a-clone; ver |

**Notes:** JSON written to /private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/417e2917-726b-46c9-9117-7b880114f08b/scratchpad/codemap/estate-adopters-driftwood-tuppence-ludlow.json. Scope note: the task's 'original-org cluster' clause does not apply here — these three are adopter orgs, each its own GitHub org (policy-as-versioned-driftwood/tuppence/ludlow) cloned side by side under .estate-clone. Last commits: driftwood eacae33 2026-08-25 18:06:24 +0100, tuppence 751522b 18:06:28, ludlow a800a58 18:06:32 — all three the same ticket-18 'release workflow re-renders and verifies before any tag is cut' change, minutes before the parent repo's aebbb9e. Commit counts 52 / 31 / 29; first commits 2026-07-31. Cross-references from the rest of the estate: platform references all three heavily (risk/appetite.json orgs.{driftwood,tuppence,ludlow}; compose/composition.py composes the REAL driftwood in its selfcheck at lines 1625-1812 and asserts governed-namespaces == ['driftwood']; wargamer/*, honesty/*, posture/*, identity/*, party/*); nist references them in README.md and scripts/publish.sh; ico in .github/workflows/release.yml and schema/to_fair_scenario.py. Divergence worth a drift review: all three were built from driftwood as the template and have since diverged in ways the READMEs do not describe — three mutually incompatible adopter-gate CLIs (subcommands / flags-only / underscore-named), only driftwood wires its identity-regexp check into CI, only driftwood has the drift instruments, only tuppence has the workload-identity flagship, only tuppence/ludlow carry a risk-appetite ConfigMap, and the composed enforcement artefacts are identical across all three despite the stated Audit-vs-Deny proportionality thesis.

## estate — platform: fair / risk / graded / tcor / oscal / honesty (the £ engine, the appetite band, the graded cage, the balance sheet, the OSCAL up-f

### Real

- Deterministic Monte-Carlo FAIR pricing with seeded reproducibility and a real tail-risk decomposition (ALE/VaR95/TVaR/economic capital/risk load) — fair.py:60-126, asserted fair.py:180-205.
- Multi-obligation-source pricing that is additive AND correlated through one shared frequency draw, with an assertion that it beats a naive independent sum in the tail — fair.py:81-88, fair.py:226-236.
- Appetite-band-driven Audit/Deny selection that is a pure function of £ with a machine-checked absence of any clock/date import — enforce.py:46-72, enforce.py:109-115.
- Per-org proportionality: the same control Audits in driftwood and Denies in ludlow, from one appetite store — enforce.py:106, verify-risk-tuned.sh:30-32.
- Deterministic tier->dial expansion with a real drift guard between the python table and the Kyverno CEL map, checked field by field — cage.py:65-93 vs cage-tier.yaml:74-78, verify-graded.sh:42-72.
- £-selected cage tier with monotone reduce/cost ordering and a Deny bottom rung — cage.py:117-126, asserted cage.py:262-275.
- A real Kyverno MutatingPolicy that cages by degree without ever denying, including a defaulting path so an unknown/missing tier label falls to baseline rather than a no-op skip — cage-tier.yaml:64-69, proven by the kyverno test matrix tests/cage-tier/kyverno-test.yaml:21-32.
- A real Kyverno GeneratingPolicy producing an egress-lockdown NetworkPolicy, proven against an expected generated resource — cage-netpol.yaml:36-49, tests/cage-netpol/generated.yaml.
- Four-move TCoR crossover computed rather than asserted, with the choice demonstrably flipping when a cost moves — tcor.py:121-131, asserted tcor.py:229-239.
- The living-£ levers moving the portfolio number in the predicted directions — tcor.py:161-182, asserted tcor.py:249-256.
- PolicyReport -> observation -> finding -> risk -> related-observation chain that resolves by shared-uuid construction rather than by eyeball — result2oscal.py:99 + cage.py:177-179, asserted result2oscal.py:188-203 and verify-upflow.sh:38-56.
- Two-direction OSCAL claim linting against real shipped policy trees and the real pinned NIST catalogue, with an unknown-control-id fixture proving hard failure — lint_claims.py:130-165, lint_claims.py:196-201.
- Bühlmann credibility recalibration with correct shrinkage/direction/k-behaviour properties asserted, and an incident log authored to actually produce a 'recalibrate' verdict — calibration.py:68-95, calibration.py:201-235.
- Proposer bounds with a structurally-guaranteed no-merge surface (module-level attribute check for merge/approve/dispose/auto_merge) — proposer_bounds.py:177-180, cross-checked from reflexive.py:144-148.
- Real cryptographic feed verification and tamper rejection in the honesty beat: feeds/verify.sh on a live committed feed plus an openssl pkeyutl check that a forged feed does NOT verify — verify-honesty.sh:24-42.
- The apparatus priced by the same engine and same appetite store it prices everyone else with, with a machine check that no forked scoring path is used — reflexive.py:52-64, reflexive.py:133.

### Thin or stubbed

- Every scenario in this cluster is a hand-authored fixture triple; no estimate here comes from an elicitation process or a real actuarial source — fair/scenarios/driftwood-cart-pii.json:5-12, risk/scenarios/driftwood-cart-pii-tightened.json:5-12, graded/scenarios/driftwood-behind-posture.json:5-8, tcor/scenarios/driftwood-portfolio.json:6-45, honesty/scenarios/platform-self.json:6-13.
- The cage tier table's reduce/cost values are explicitly labelled calibration knobs with no telemetry behind them — cage.py:63-64 ('tune to real WAF/eviction telemetry'), graded/README.md:118-126.
- The WAF sidecar image ghcr.io/acme/coraza-waf:cage is a named placeholder that does not exist — cage-tier.yaml:105, graded/README.md:125-126.
- The insurer load 0.40 and DEFAULT_LOAD/premium formula are a documented mid-range guess, not a quoted rate — tcor.py:57-61.
- risk/PR.md is a narrated PR: it shows a validationActions Audit->Deny diff that no code applies; the field is described as hand-edited to match the number — PR.md:39-49. Nothing in this cluster writes a policy body from enforce.py action output.
- platform/risk has no verify-* coverage of an actually-deployed policy: verify-risk-tuned.sh only re-runs the python decision, so the claim 'that verdict IS the Kyverno validationActions value' (enforce.py:10) is unproven against any shipped YAML.
- OSCAL up-flow input is fixture-only: result2oscal.py defaults to fixtures/policyreports.yaml (result2oscal.py:42, 172) and no code in this cluster reads PolicyReports from a live cluster.
- OSCAL schema validation is optional and skipped whenever trestle is absent — verify-upflow.sh:59-66; it skipped on this machine.
- honesty/incidents.json is a curated fixture standing in for a loss ledger, and the recalibration it computes opens no PR — honesty/README.md:134-139.
- honesty/rejections.json is a static ledger; nothing appends to it, so 'learn from rejections' learns only from a hand-edited file — rejections.json:4-18.
- reflexive.feed_integrity()'s 'signed' flag is a .sig file-existence check, not a signature verification — reflexive.py:100; the real verification lives in verify-honesty.sh:24-42 and is a separate step.
- proposer_bounds confidence for scenario-move drifts is a hardcoded STRUCTURAL_CONFIDENCE=0.5 with an explicit upgrade note — proposer_bounds.py:26-30, 50, 61.
- graded/up.sh is self-labelled 'DEMO PATH, not delivery' and takes Flux out of the loop, applying rendered versioned copies with kubectl — up.sh:1-14.
- oscal/verify-claims.sh's header still narrates an EXPECTED-RED state ('cm-6 claims require-policy-version and ac-6 claims may-run-root-if-attested') that no longer exists — verify-claims.sh:6-10 contradicts lint_claims.py:59-62 and the now-green run; stale prose.
- graded/verify-graded.sh's live tail is currently FAILING on this machine (real exit code 1): the kind-driftwood cluster carries cage-tier-1-0-0 and cage-tier-2-0-0, while distribution/versions.yaml declares 2.0.0/2.0.1/3.0.0, so 'FAIL: cage-tier-2-0-1 MutatingPolicy not installed live' (verify-graded.sh:101-107). The offline steps 1-5 all pass.
- The Deny rung is emitted as data only: cage.py:148-154 returns action Deny, and graded/README.md:133-135 says enforcement of it belongs to other policies. Nothing in this cluster turns a computed Deny into an applied Kyverno validationActions change.
- No time/date-driven behaviour anywhere by design (ADR-0006), which also means no sunset, no expiry, no scheduled re-pricing in this cluster.

### Risk and pricing

- fair.py:44-47 — the fixed engine constants: ITERATIONS 10_000, SEED 42, PERT_LAMBDA 4.0, COST_OF_CAPITAL 0.06.
- fair.py:104-126 summarize() — ALE, VaR95, TVaR, economic_capital = TVaR-ALE, risk_load = 0.06*economic_capital, carried = TVaR+risk_load.
- fair.py:129-143 control_value() — risk_bought, capital_released, effectiveness.
- risk/appetite.json:3-21 — the single tolerance store: driftwood 40000, tuppence 15000, ludlow 5000, platform 10000 (root_of_trust).
- risk/enforce.py:37-43 tolerance_for(); enforce.py:46-72 decide() computing risk_bought, verdict, headroom and the £ reason string.
- risk/PR.md:12-14 — the £ figures (£54,520 vs £40,000; £19,439) quoted as the escalation justification.
- graded/cage.py:65-84 TIERS reduce/cost; cage.py:96-114 caged_residual and tcor(); cage.py:117-126 select_tier(); cage.py:129-163 select() emitting uncaged_residual, tier, dials, tcor and a £ reason.
- graded/cage.py:216-228 — the OSCAL annualised-loss-expectancy facet in GBP with basis 'caged-residual' and a cost-of-controls prop.
- tcor/tcor.py:57-61 DEFAULT_LOAD 0.40; tcor.py:70-115 moves() pricing fix/cage/transfer/deny; tcor.py:118-131 ORDER + crossover(); tcor.py:135-154 balance_sheet() summing residual/cost_of_controls/transfer_premium.
- tcor/tcor.py:161-182 — accept_condition (LEF x1.6), tighten_control (LM x0.5), threat_or_eol (LM x2.5).
- tcor/scenarios/driftwood-portfolio.json:13-43 — the per-risk fix/deny costs and transfer load/deductible that decide each crossover.
- honesty/calibration.py:99-146 backtest_org() and _backtest_verdict() (under-prices / over-prices / defensible thresholds at 2x expected exceedances, 1.5x and 0.5x model ALE).
- honesty/calibration.py:68-95 buhlmann(); calibration.py:171-186 run_recalibrate() emitting recalibration_factor = credibility_premium / model_ale.
- honesty/reflexive.py:52-64 govern_self() — the apparatus's own risk_bought vs its £10k band, and residual_within_band.
- honesty/proposer_bounds.py:54-61 confidence() — materiality as (risk_bought_current - tolerance)/tolerance, the £-derived gate on whether a proposal reaches a human.

### Cages and enforcement

- Cage tiers: cage.py:65-86 TIERS + ORDER (baseline/restricted/quarantine); cage.py:89-93 dials().
- Graded enforcement selection: cage.py:117-126 select_tier() walking loosest-to-tightest, falling through to 'deny'.
- Deny as bottom rung: cage.py:148-154 (action Deny, reason 'even quarantine leaves £X > band'); cage.py:196-197 oscal_risk() refuses to build a risk for a Deny because nothing is retained.
- Audit vs Deny: enforce.py:54 verdict; enforce.py:61 validationActions:[verdict] — the value is emitted but never written into any policy YAML by code.
- The mutate that enforces the cage: cage-tier.yaml:79-130 (SSA ApplyConfiguration for label/priorityClass/limits/securityContext/WAF sidecar; JSONPatch for drop-ALL caps on hardened tiers only).
- The generate that cuts reach: cage-netpol.yaml:29-49 (matchCondition on posture.acme.io/caged, generator.Apply of the egress-lockdown NetworkPolicy).
- Eviction dial: priorityclasses.yaml:15,27,39 (-10/-100/-1000, preemptionPolicy Never).
- De-posture / no-uncaged-state: cage-tier.yaml:53-69 — the claims-a-policy-version matchCondition, and the rawTier->tier fallthrough where a missing OR unrecognized label both default to baseline rather than a skip (the exemption the project bans); tests/cage-tier/resources.yaml:65-77 proves an unclaimed system pod is genuinely out of scope.
- Drift guard between the python tier table and the enforced CEL map: verify-graded.sh:42-72.
- Orphan guard: referenced, not defined here — verify-graded.sh:108-118 imports distribution/render-orphan-guard.py's versions() to derive the live version list, and lint_claims.py:67-70 names policy-version-orphan-guard as a shipped platform-machinery policy.
- Governed namespace: oscal/component-definition.json:36 claims cm-6 via governed-namespace-requires-claim; lint_claims.py:67-70 recognises it as shipped platform machinery; the policy body itself lives outside this cluster.
- Currency controller: consumed, not implemented here — graded/README.md:130-132 states ticket 16's currency controller decides when a workload has fallen behind and stamps posture.acme.io/tier; this cluster only consumes that label. The controller itself is platform/currency-controller (a CronJob, manifests/cronjob.yaml).
- The gate as backstop: proposer_bounds.py:100-102 asserting merged/auto_merge False and required_gate present on every emitted proposal; proposer_bounds.py:177-180 and reflexive.py:144-148 asserting no merge/approve/dispose surface exists.

### Feeds, Wardley, war-gamer

- Nothing in these six directories opens a pull request, and nothing reads a live feed or network resource. All six are offline.
- Feeds (SIMULATED as live, REAL as signed artefacts): honesty/reflexive.py:68-113 globs ../feeds/*/v*/*.json and reports signed/sourced/bounded over 6 committed feed files; honesty/verify-honesty.sh:24-42 performs a REAL openssl signature verification of feeds/threat-register/v1/register.json and a REAL tamper-rejection. The feeds themselves are versioned committed fixtures — no fetch of endoflife.date, trivy or GHSA occurs (platform/feeds/README.md:1-30).
- Feed bounds: reflexive.py:104-112 runs to_fair_scenario.selfcheck() to assert every feed entry yields a valid lo<=mode<=hi triple.
- Wargamer (SIMULATED drift): honesty/proposer_bounds.py:45-46 imports ../wargamer/wargamer.py and proposer_bounds.py:99 calls wargamer.propose() to build a proposal object in memory. The drift rows come from committed scenarios (wargamer/scenarios/human-device.json). No git, no gh, no network in the honesty path.
- The real PR opener is OUTSIDE this cluster: platform/wargamer/tier_pr.py (subprocess git/gh wrappers, tier_pr.py:43,104-107), driven by the adopter workflows driftwood|ludlow|tuppence/.github/workflows/propose-tier.yml, which run `python3 platform/wargamer/tier_pr.py run` with GH_TOKEN to open a real PR editing posture.acme.io/tier (or an issue for a proposed deny). That workflow consumes this cluster's tier vocabulary but is not code in these six directories.
- Wardley: nothing here. platform/wardley/wardley.py and wardley/README.md:70 reference ../tcor/tcor.py's costs.cage_discount as the consumer of a commoditisation signal — the touchpoint is tcor.py:79-82,94,109 (an optional per-risk multiplier defaulting to 1.0), read from the risk JSON, never computed here.
- risk/PR.md is a narrated PR document, not an opened one (PR.md:1-56).

### Original-thesis mechanisms

- Multi-version coexistence — PRESENT, indirectly. The graded policies ship as cage-tier-<v>/cage-netpol-<v> under platform/distribution/policies/v2.0.0|v2.0.1|v3.0.0 (the distribution copies add a matchConditions self-scoping comment and an only-this-policy-version condition absent from the graded authoring copy). result2oscal.py:49,70 strips the -N-N-N suffix precisely so one component-definition maps every coexisting version. verify-graded.sh:101-118 checks each declared version's policies live.
- ResourceSet matrix — PRESENT by reference only. platform/distribution/versions.yaml is the flux-operator ResourceSet ranging the versions array; nothing in these six directories defines or renders it. graded/up.sh:1-14 explicitly says it is the offline twin and takes the ResourceSet out of the loop.
- Renovate bump PR — ABSENT from this cluster. Renovate workflows exist only in the adopter repos (driftwood|ludlow|tuppence/.github/workflows/renovate-run.yml).
- Signed tags — ABSENT from this cluster's code; present at the platform-repo level (platform/.github/workflows/release.yml gitsign verify-tag identity-pinned + cosign verify-blob of release-gate evidence). The only signing this cluster touches is the ed25519 feed signatures verified by verify-honesty.sh:24-42.
- Orphan guard — PRESENT by reference. verify-graded.sh:108-118 imports distribution/render-orphan-guard.py's versions(); lint_claims.py:67-70 treats policy-version-orphan-guard as a shipped claimable policy. The guard itself is not defined here.
- OSCAL / C2P — PRESENT and the strongest mechanism in this cluster: oscal/result2oscal.py (an offline hand-written twin of C2P result2oscal, not the real C2P tool), oscal/component-definition.json, oscal/lint_claims.py against the pinned NIST catalogue, and cage.py:166-239 emitting the OSCAL risk with a GBP facet. trestle validation is optional and skipped without the CLI.
- Shift-left — ABSENT here. platform/shift-left/verify-shift-left.sh is the release gate in platform/.github/workflows/release.yml; none of these six dirs is exercised in CI.
- Handbook — ABSENT. No handbook, runbook or narrative operator doc in this cluster beyond the four READMEs.
- Sunset — ABSENT by design. ADR-0006 no-time-conditional-verdicts is enforced: enforce.py:109-115 machine-checks that no datetime/time import exists, and cage.py:193-194 + cage.py:303 assert a cage carries no deadline and is never time-boxed.
- Notifications — ABSENT. No alerting, no Slack/email/webhook anywhere in this cluster.
- Dashboards — ABSENT. Output is JSON on stdout and coloured shell 'say' lines; no Grafana, no rendered board view, no served page.

### Runtime dependencies

- python3 stdlib — REAL and the only hard dependency of fair/risk/graded(cage.py)/tcor/honesty.
- PyYAML — REAL, required by result2oscal.py, lint_claims.py, and verify-graded.sh step 5.
- kyverno CLI — REAL, required by verify-graded.sh for the two offline `kyverno test` matrices; present on this machine.
- Kyverno admission controller (MutatingPolicy/GeneratingPolicy CRDs, policies.kyverno.io/v1alpha1) — REAL but only in the live tail; installed on the local kind-driftwood cluster with stale versions (cage-tier-1-0-0, cage-tier-2-0-0).
- kubectl + a KinD cluster (kind-driftwood) — REAL for graded/up.sh and verify-graded.sh step 6 only; every other component in this cluster is cluster-free.
- Flux / flux-operator ResourceSet — REAL but NOT in this cluster's own loop: the graded policies reach a cluster as versioned copies under platform/distribution/policies/v2.0.0|v2.0.1|v3.0.0 delivered by distribution/versions.yaml's ResourceSet. graded/up.sh deliberately bypasses Flux (up.sh:10-14).
- openssl — REAL, used by verify-honesty.sh:38 for the tamper-rejection check against the committed ed25519 public key.
- compliance-trestle (C2P OSCAL validator) — OPTIONAL/absent; verify-upflow.sh skips the schema-validation tail when the trestle CLI is missing, which it is here. The C2P conversion itself is a hand-written offline twin (result2oscal.py:8-9), not the real C2P tooling.
- NIST catalogue — REAL data, read from a sibling ../nist/catalog checkout pinned by CATALOG_VERSION.json (lint_claims.py:54, 125-127).
- platform/feeds — REAL committed signed JSON feeds (threat-register, cve, eol; 6 files), read offline by reflexive.py; SIMULATED as a live source — the feeds are versioned fixtures, no fetch of endoflife.date / trivy / GHSA happens (feeds/README.md:1-30).
- wargamer — REAL python module imported by proposer_bounds.py; its drift rows come from committed scenarios (wargamer/scenarios/human-device.json), so the drift being bounded is SIMULATED.
- SPIRE, Istio, OpenBao, Pomerium, Crossplane, trivy, Renovate, gitsign, GitHub Actions — NOT dependencies of this cluster. Crossplane appears only as a fixture resource kind (oscal/fixtures/policyreports.yaml:70); trivy only as a feed shape name; gitsign/GitHub Actions/Renovate live in platform/.github and other clusters and touch nothing here except via the versioned distribution trees the graded policies ship in.

### Verify scripts

| Script | Needs cluster | Proves |
|---|---|---|
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/risk/verify-risk-tuned.sh` | False | enforce.py selfcheck plus four assertions: loose cart-PII Audits in driftwood, the tightened triple Denies, the decision text carries a £ justification, and the same loose control Denies under ludlow' |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/tcor/verify-tcor.sh` | False | tcor.py selfcheck, that the demo book actually books all three of fix/cage/transfer with all three £ lines non-zero and summing exactly, and that a stricter band raises the caged row's control-spend ( |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/graded/verify-graded.sh` | False | Offline (needs kyverno CLI + python3): cage.py selfcheck; the cage-tier mutate matrix (behind-posture pods mutated not denied, in-currency pod caged to baseline, unclaimed pod skipped); the cage-netpo |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/oscal/verify-claims.sh` | False | lint_claims.py --selfcheck plus the real claim check against component-definition.json: every Check_Id resolves to a shipped policy identity and every control-id resolves in the pinned NIST catalogue. |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/oscal/verify-upflow.sh` | False | result2oscal builds assessment-results from the fixture, ac-6 is not-satisfied and cm-6 satisfied, result2oscal's own selfcheck, and the join: cage.py's risk related-observation uuid is present among  |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/honesty/verify-honesty.sh` | False | Four beats, offline, needs python3 + openssl: calibration selfcheck + a real backtest run; a REAL signature verification of feeds/threat-register/v1/register.json via feeds/verify.sh plus a forged-fee |

**Notes:** Provenance: .estate-clone is gitignored by the parent repo and each org is its own git checkout. platform's remote is https://github.com/policy-as-versioned-platform/platform, HEAD 58ef9c5 dated 2026-08-25 ('cs-27: signed release-gate evidence for policy/v3.0.0'). Last commit per directory: fair 2532ddc 2026-08-20 (multi-obligation pricing); risk 201beae 2026-08-20; graded 2667204 2026-08-22 (cs-17: gate live tails on versioned resource names); tcor 6d1078c 2026-08-20 (cage_discount); oscal 72c7083 2026-08-25 (repoint the up-flow fixture at real policy names); honesty c4463fa 2026-08-24 (mo-25: check the public signing key, not the private one).

Six-org estate references: driftwood, ludlow and tuppence each carry composed/policies/v2.0.0|v2.0.1|v3.0.0/cage-tier.yaml and cage-netpol.yaml plus composed/evidence.json, so the graded cage policies genuinely propagate into all three adopter repos. All three also have .github/workflows/propose-tier.yml, which checks out platform at the pinned tag and runs platform/wargamer/tier_pr.py to open a real PR editing posture.acme.io/tier — the adopter-side consumer of this cluster's tier vocabulary. ico/verify-penalty-feed.sh:8 and ico/schema/to_fair_scenario.py:6 point at platform/fair/fair.py; nist is referenced only as a catalogue source by lint_claims.py. No org repo references fair/risk/tcor/oscal/honesty python directly beyond those two ico hooks.

Execution results on this machine (2026-08-27): all nine python selfchecks pass; risk/verify-risk-tuned.sh, tcor/verify-tcor.sh, oscal/verify-claims.sh, oscal/verify-upflow.sh and honesty/verify-honesty.sh all PASS. graded/verify-graded.sh passes offline steps 1-5 but exits 1 on the live tail because kind-driftwood has cage-tier-1-0-0 and cage-tier-2-0-0 installed (4d20h old) while distribution/versions.yaml declares 2.0.0/2.0.1/3.0.0 — a real, current red.

Two prose-vs-code drifts worth a reviewer's eye: oscal/verify-claims.sh:6-10 still narrates an EXPECTED-RED state that lint_claims.py:59-62 and the green run have superseded; and graded/README.md:1-7 presents the cage as the delivered mechanism while up.sh:1-14 concedes the apply path is a demo twin with Flux out of the loop.

Shape of the cluster overall: a tight, single-source-of-truth £ stack (fair -> risk -> graded -> tcor, each importing the previous rather than reimplementing it, asserted at reflexive.py:133 and break-glass/verify-break-glass.sh:32), with real Kyverno policy artefacts and real offline proofs at the graded layer, and a candid honesty layer that names its own fixtures. What is not built anywhere in these six directories: any write-back — no policy YAML is edited from a computed verdict, no PR is opened, no feed is fetched, no PolicyReport is read from a cluster, and no number is displayed anywhere but stdout.

JSON written to /private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/417e2917-726b-46c9-9117-7b880114f08b/scratchpad/codemap/estate-platform-risk-fair-graded-tcor.json (30 components).

## estate — platform/feeds + platform/wardley + platform/wargamer (repo: policy-as-versioned-platform/platform, cloned at /Users/cns/httpdocs/controlpla

### Real

- Offline ed25519 detached-signature verification of every versioned feed file, with real tamper-rejection proofs: feeds/verify.sh:20, feeds/verify-feeds.sh:28-41, wargamer/verify-wargamer.sh:19-31, wardley/verify-wardley.sh:23-35.
- Feed-version-vs-directory consistency check: feeds/verify.sh:17.
- Feed -> FAIR scenario conversion consumed by an unmodified fair.py, with the money genuinely moving on a version bump (£222,574 -> £326,139 measured): feeds/to_fair_scenario.py:42-104, feeds/verify-feeds.sh:50-59.
- The EOL time-varying ramp: eol_ramp() is real arithmetic, monotone and capped at +4x, asserted at feeds/to_fair_scenario.py:143-151 and end-to-end at feeds/verify-feeds.sh:67-81.
- Wardley projection and MOVEMENT flagging (stage-crossing vs static position), with a deliberately non-vacuous negative control: wardley/wardley.py:149-176 and selfcheck 2b at wardley/wardley.py:316-332.
- The fail-closed enactment gate with three named failure modes and planted-violation proofs: wardley/wardley.py:111-138, wardley/verify-wardley.sh:82-116.
- Per-institution divergence is machine-checked, not asserted in prose: wardley/wardley.py:436-442 and wardley/verify-wardley.sh:70-75 require driftwood's and ludlow's drift sets to differ.
- The fix-is-a-fixed-point property, swept over bump factors rather than only today's K: wardley/wardley.py:498-503.
- Proportionality drift detection: enforce.decide baseline-vs-current per institution (wargamer/wargamer.py:98-126) and tcor.crossover chosen-vs-deployed (wargamer/wargamer.py:129-150).
- The `applicable` regression pin for hyperscaler concentration, asserting the exact ~£3,726 failure it prevents: wargamer/wargamer.py:281-300.
- Structural propose-never-dispose: no merge/dispose/approve symbol in wargamer.py (asserted l.319-320), proposer_bounds.py, or tier_pr.py (asserted l.380-384).
- Real git+gh mechanics in tier_pr.py: branch force-reset to origin/base, single fresh commit, force-push, PR create-or-edit dedupe by branch name, issue dedupe by HTML-comment marker - all exercised offline against a real local bare repo and a stateful gh stub (tier_pr.py:277-392).
- The deny-never-travels-as-a-label invariant (a merged `tier: deny` would be coerced to baseline by the cage-tier MutatingPolicy, inverting the proposal): tier_pr.py:214-245, wargamer.py:214-221.

### Thin or stubbed

- NO FEED IS EVER FETCHED. All six feed files, the v3 fixture and market-intel.json are hand-authored static JSON; there is no HTTP/urllib/requests/curl anywhere in the cluster (grep clean). CVE data is 'trivy/GHSA-style' shape only, two of three ids marked '(illustrative)' at feeds/cve/v1/cve-feed.json:18,33; EOL data is transcription; the threat register says outright 'not a live threat-intel subscription' (feeds/threat-register/v1/register.json:4).
- £ bands are editorial by declaration, not derived: THREAT_LM_GBP hardcoded per institution at feeds/to_fair_scenario.py:34-38; severity_lm_gbp declared 'not a real breach-cost dataset' at feeds/cve/v1/cve-feed.json:4; annual_events_if_exploited=(1,2,6) hardcoded as a default arg at feeds/to_fair_scenario.py:56.
- ATTACK_COST_COLLAPSE_K = 4.0 is a single editorial dial (wardley/wardley.py:84), with an unusually honest caveat that widening it is UNSAFE because cage TCoR is non-monotone in the threat.
- wardley/sign-map.sh CANNOT RUN: it needs ../feeds/keys/feeds-signing-key.pem (l.18) and only the .pub is committed. No path in this repo can re-sign a feed or a map. feeds/README.md:24-31 owns the equivalent admission for sign.sh.
- wardley/enactment.json is UNSIGNED (self-documented at l.3): tamper-evidence stops at file-exists-on-disk, and the evidence check is os.path.isfile only (wardley/wardley.py:131) - it never reads or validates evidence content.
- gitsign/Rekor is a STRING, not an operation: `"identity": "gitsign keyless (OIDC -> Fulcio) -> Rekor transparency log"` and `"signed": True` are literals at wargamer/wargamer.py:199-200 and :230-231. propose-policy-pr.sh:62-66 narrates gitsign presence/absence and stamps nothing.
- propose-policy-pr.sh renders the Audit->Deny diff with `sed` into a tmpdir (l.35) and never commits, pushes, opens or merges - self-declared at l.4-6 and wargamer/README.md:80-85.
- DEFECT (real, reproduced): verify-wargamer.sh exits 1 and propose-policy-pr.sh exits 1 wherever kyverno is installed (1.18.2 here). propose-policy-pr.sh:52-54 asserts ci-check.py FAILS on shift-left/fixtures/workload-flip.yaml; it now PASSES ('compliant across its supported window [2.0.0, 2.0.1]', pass:1 fail:0). The 'whole beat end to end' README claim (wargamer/README.md:70) holds only where kyverno is absent - i.e. the passing path is the one that skips the check.
- DOC/CODE DRIFT: wardley README and docstrings say 'all three institutions (driftwood, tuppence, ludlow)' (wardley/README.md:57-65,88-91; wardley/wardley.py:36-37,143,253,528) but institutions() reads risk/appetite.json which has four orgs; live output is '11 forward drift(s) across 4 institution(s)'. The extra org is `platform` scoring itself.
- wargamer/scenarios/human-device.json is hardcoded to org 'tuppence' (l.2) and is unsigned, unlike every feed the same code paths verify.
- wargame_cage_tier() is deliberately NOT wired into wargame() (wargamer/wargamer.py:166-169) - the real-PR path and the demo path are disjoint, and run() explicitly refuses to call the demo path (tier_pr.py:240-247) to stop the fixture leaking into an adopter run.
- tier_pr.py's edit is regex over flow-style `labels: { ... }` maps only (tier_pr.py:63, 80-82); a block-style adopter manifest is out of scope and would silently report 'nothing to land' (l.204-206).
- The only production caller of this cluster would land nothing today: all prices[] entries in driftwood/composed/evidence.json have changed:false.
- wardley/map/wardley-map.json is a committed render of a deterministic function - re-derivable, carrying no information the intel does not (confirmed byte-identical to a fresh render).
- Two map entries exist expressly to fire nothing: nb-refining-capacity (actor gate, market-intel.json:136) and pqc-transport-migration, labelled 'KNOWN-INERT (finding F2)' at market-intel.json:157 - a commoditising defence with no path to move any number.

### Risk and pricing

- feeds/to_fair_scenario.py:34-38 - THREAT_LM_GBP, the hardcoded per-institution loss-magnitude bands.
- feeds/to_fair_scenario.py:56-70 - CVE epss -> lef and severity -> lm £ band lookup.
- feeds/to_fair_scenario.py:74-104 - eol_ramp() and eol_scenario(): the time-varying £, +1x/yr capped at +4x.
- feeds/to_fair_scenario.py:29 - DENY_LEF = (0,0,1), the estate-wide deny convention.
- feeds/cve/v1|v2/cve-feed.json:5-10 - severity_lm_gbp £ tiers (critical 50k/150k/400k ... low 100/1k/5k).
- feeds/verify-feeds.sh:18 - `ale()` shells platform/fair/fair.py summary --mode warn and reads ['ale'] - the only place in this cluster that computes an actual ALE.
- wardley/wardley.py:84 - ATTACK_COST_COLLAPSE_K = 4.0, the frequency-multiplier dial.
- wardley/wardley.py:185-192 - _forward_risk(): warn/behind LEF x (1 + K*movement).
- wardley/wardley.py:203-210 - _forward_defence(): costs.fix x factor and costs.cage_discount = factor, the cost-of-controls side.
- wardley/wardley.py:351-357 - tcor.crossover on base vs forward control, asserting the board line (TCoR) falls.
- wardley/enactment.json:15 - the linked control's costs {fix 55000, deny 90000, transfer load 0.7 deductible 40000}.
- wardley/intel/market-intel.json:16-24, 35-44, 55-64, 97-106, 118-126, 137-145 - six embedded base_risk FAIR postures with warn/behind/deny lef+lm and costs incl. transfer load/deductible.
- wargamer/wargamer.py:105-107 - enforce.decide(threat_scenario(feed, org), org, enforce.tolerance_for(org)): the appetite-band verdict.
- wargamer/wargamer.py:116-118 - risk_bought_deployed / risk_bought_current / tolerance on every enforcement row (driftwood measured £41,095 vs a £40,000 band).
- wargamer/wargamer.py:137 - tcor.crossover(risk, tol)['chosen'], the four-move (fix/cage/transfer/deny) TCoR crossover.
- wargamer/wargamer.py:158-179 - wargame_cage_tier(): old_price/new_price carried as tolerance/risk_bought_current so materiality reuses one formula.
- wargamer/scenarios/human-device.json:13,24,35,46,57,68 - per-risk costs blocks incl. transfer load and deductible; l.64 `applicable: [transfer, deny]` guards against a £3,726 nonsense fix.
- honesty/proposer_bounds.py:53-63 (consumer) - confidence() = (risk_bought_current - tolerance)/tolerance, CONFIDENCE_MIN 0.05, RATE_LIMIT 3.

### Cages and enforcement

- Graded enforcement Audit/Deny: wargamer/wargamer.py:98-126 computes the £-implied verdict per institution; the drift becomes a proposal flipping validationActions [Audit] -> [Deny] on distribution/policies/v2.0.0/require-nonroot.yaml (wargamer/wargamer.py:74-78, propose-policy-pr.sh:16,35).
- Cage as a priced move: `cage` is one of the four TCoR moves and the deployed_move for stolen-laptop (wargamer/scenarios/human-device.json:19) and for the forward phishing/ransomware/worm postures (market-intel.json:38,58,120). Live wardley run shows cage -> fix drifts for 3 of 5 forward controls.
- Cage cost discount: wardley/wardley.py:206 introduces costs.cage_discount, an optional backward-compatible field tcor.py reads (documented wardley/wardley.py:31-32).
- Cage TIERS: wargamer/wargamer.py:214-245 and tier_pr.py:56-66 - TIER_LABEL 'posture.acme.io/tier', tiers baseline/restricted/quarantine, and the rule that a proposed `deny` must open an ISSUE because the `cage-tier` MutatingPolicy coerces an unrecognised label to baseline (ADR-0015). tier_pr.py:151-181 implements the issue path.
- Cage-tier drift rows: wargamer/wargamer.py:158-179, consumed only by tier_pr.py:261 (never by wargame()).
- The population gate: tier_pr.py:56 CLAIMS_LABEL 'policy-as-versioned.dev/policy-version' - the tier label is only written into a labels map that already claims a policy version, mirroring the cage-tier policy's own matchCondition.
- The hard backstop is the PR gate, not the agent: GATE string at wargamer/wargamer.py:80 ('shift-left version cross-check, target +/-1 window'), asserted present on every proposal (wargamer.py:313, wardley/verify-wardley.sh:66, proposer_bounds.py:104).
- Enforcement-adjacent CI gate execution: propose-policy-pr.sh:49-57 runs shift-left/ci-check.py (kyverno) against a fixture - currently the broken assertion.
- Orphan guard, governed namespace, de-posture, currency controller: NOT in this cluster. They exist as sibling directories (platform/currency-controller, platform/graded, platform/posture) and as composed artifacts in the adopter repos (driftwood/composed/orphan-guard.yaml, governed-namespace-guard.yaml). The only link is that tier_pr.py reads composed/evidence.json, which those mechanisms produce.

### Feeds, Wardley, war-gamer

- Feed -> risk: feeds/to_fair_scenario.py consumed by wargamer/wargamer.py:62 (loaded by path, unmodified), platform/compose/composition.py:606, platform/honesty/reflexive.py:46.
- Feed -> war-gamer: wargamer/wargamer.py:64 pins feeds/threat-register/v1 as baseline and :67 pins its own signed v3 fixture as current. Both are FIXTURE FILES on disk - no feed is read from any network source anywhere in this cluster (grep for requests/urllib/curl/http finds only two example.invalid strings in the gh stub, tier_pr.py:432,440). SIMULATED.
- Wardley -> war-gamer seam: wardley/wardley.py:258-276 forward_into_wargamer()/_all() imports wargamer and calls wargamer.wargame_scenarios() + wargamer.propose() unmodified; the org's band comes from wargamer.enforce.tolerance_for (l.266). REAL code path over simulated intel.
- Wardley map artifacts: wardley/map/wardley-map.json is rendered by wardley.py map (sign-map.sh:24) and signed with the feeds key (sign-map.sh:27) - a genuine evolution/velocity projection, but over hand-authored intel.
- REAL PR OPENING - exactly one path: wargamer/tier_pr.py:130-138 (`gh pr create` / `pr edit`) and :172-181 (`gh issue create` / `issue edit`), preceded by a real `git push --force` at :224. In production it is invoked only by the adopters' propose-tier.yml (driftwood l.68, ludlow l.116, tuppence l.106) on a merged pin-bump or manual dispatch.
- SIMULATED PR opening: wargamer/propose-policy-pr.sh renders a sed diff and stops (l.35-44, l.68-69); wargamer.propose() returns a dict describing a PR that is never created (wargamer.py:194-211). wardley's 'signed PR' output is this same dict shape.
- REAL FEED READING: none. Nothing in this cluster performs any network read.
- Evidence flow into the real path: tier_pr.py:256-261 reads the adopter's committed composed/evidence.json prices[] (produced by platform/compose), bounds it via honesty/proposer_bounds.bound (:262), and lands what survives.
- Bounding layer: platform/honesty/proposer_bounds.py:46 imports wargamer and wraps proposals with confidence/rate-limit/rejection-ledger bounds; platform/honesty/reflexive.py:104-110 runs to_fair_scenario.selfcheck() as the feed-boundedness check; platform/honesty/verify-honesty.sh:25-29 re-uses feeds/verify.sh and the v1 register.

### Original-thesis mechanisms

- multi-version coexistence - NOT in this cluster; only referenced as the target of a proposal (require-nonroot@2.0.0, wargamer/wargamer.py:74-78) and as the shift-left +/-1 window in the GATE string (wargamer.py:80).
- ResourceSet matrix - ABSENT here. Lives in platform/distribution (referenced from driftwood/gitops/platform/platform-pin.yaml).
- Renovate bump PR - ABSENT from this cluster's code, but it is the upstream TRIGGER: Renovate bumps the adopter's platform-pin.yaml tag+commit, and the merged pin-bump PR fires propose-tier.yml (driftwood/.github/workflows/propose-tier.yml:17-25).
- signed tags - PARTIAL/adjacent. This cluster signs DATA (detached ed25519 over feed/intel/map JSON, verified offline) but never a tag. Tag signing and gitsign verify-tag live in platform/.github/workflows/release.yml:89-129. The war-gamer's own 'signed' is a literal (wargamer/wargamer.py:200). Adopters do verify the pinned platform tag's commit before running tier_pr.py (propose-tier.yml:57-58).
- orphan guard - ABSENT here (platform/graded + adopters' composed/orphan-guard.yaml).
- OSCAL / C2P - ABSENT as code; nist OSCAL named only in prose (wargamer/wargamer.py:9, feeds/README.md:5) as a pinned upstream dep priced elsewhere.
- shift-left - PRESENT as a hard dependency: the version cross-check gate is the required_gate on every proposal (wargamer/wargamer.py:80, asserted at :313; wardley/verify-wardley.sh:66) and is actually executed by propose-policy-pr.sh:52 - which is where the cluster currently fails.
- handbook - ABSENT.
- sunset - PRESENT but deliberately REFRAMED: instead of a bespoke sunset mechanism, an unmaintained policy version is priced as ordinary EOL risk via the time-varying ramp (feeds/README.md:52-54, feeds/to_fair_scenario.py:17, feeds/eol/v1/eol-feed.json:4).
- notifications - ABSENT. No schedule, no alerting; the adopters' workflows state 'Nothing timed, ever -- no `schedule:` anywhere' (propose-tier.yml:18). The only human-facing output is a PR or issue body (tier_pr.py:141-148, 157-169).
- dashboards - ABSENT. No Grafana, no metrics; output is JSON on stdout and coloured shell narration.

### Runtime dependencies

- python3 - REAL (every module and script).
- openssl (pkeyutl ed25519 verify) - REAL, actually invoked; signing side unusable (private key absent).
- git - REAL, but only in wargamer/tier_pr.py (fetch/checkout -B/add/commit/push --force) and its offline selfcheck.
- gh CLI - REAL in production (tier_pr.py:115-121, 124-181); SIMULATED in selfcheck via a stateful python stub written to PATH (tier_pr.py:414-444).
- GitHub Actions - REAL: driftwood/ludlow/tuppence .github/workflows/propose-tier.yml is the only production runner; never scheduled, only merged-pin-bump or workflow_dispatch.
- gitsign / Fulcio / Rekor - SIMULATED in this cluster: identity strings and `signed: True` literals (wargamer.py:199-200) plus a `command -v gitsign` narration (propose-policy-pr.sh:62-66). Real gitsign verification lives elsewhere in the repo (platform/.github/workflows/release.yml:99).
- kyverno CLI - REAL when present, and its presence currently BREAKS the beat (propose-policy-pr.sh:49-57). No kyverno admission controller and no cluster is involved.
- Flux - ABSENT from this cluster. Nothing in feeds/, wardley/ or wargamer/ is Flux-reconciled; the adopter Kustomization points at platform's ./distribution path only (driftwood/gitops/platform/platform-pin.yaml).
- Kubernetes cluster / CronJob - ABSENT. Nothing here is a CronJob or any in-cluster resource.
- trivy - SIMULATED (the CVE feed is 'trivy/GHSA-style' shaped data; trivy is never invoked).
- endoflife.date - SIMULATED (shape and dates transcribed by hand).
- SPIRE / Istio - REAL as evidence artifacts only: wardley/enactment.json:20-23 names ../identity/spire/helmrelease.yaml and ../identity/istio/peerauthentication-strict.yaml, and corroborated_enactment() checks only that those files exist.
- Renovate - REAL but OUT of this cluster: it bumps the adopter's platform pin, and the merged pin-bump PR is the trigger that can fire propose-tier.yml (driftwood/.github/workflows/propose-tier.yml:17-25).
- OpenBao / Pomerium / Crossplane / C2P / OSCAL - not used here; OSCAL and Pomerium appear only as prose (wargamer/wargamer.py:9, wargamer/scenarios/human-device.json:10).
- platform siblings imported directly - REAL: fair/fair.py, risk/enforce.py, risk/appetite.json, tcor/tcor.py, shift-left/ci-check.py, honesty/proposer_bounds.py.

### Verify scripts

| Script | Needs cluster | Proves |
|---|---|---|
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/feeds/verify.sh` | False | One named feed file's feed_version matches its directory and its committed detached ed25519 signature verifies against the committed public key. Needs python3 + openssl only. |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/feeds/verify-feeds.sh` | False | All six feed files verify; a tampered CVE feed is rejected; an unmodified fair.py prices all three feeds; a v1->v2 bump raises the ALE by a measured amount; EOL ALE ramps monotonically across three -- |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/wardley/verify-wardley.sh` | False | Intel and map signatures verify; a forged commoditising flag fails verification; the map flags movement not position; the forward signal feeds the war-gamer per institution producing drift and gated u |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/wargamer/verify-wargamer.sh` | False | Intends: the v3 fixture verifies and a tamper is rejected; the feed->PR seam selfcheck passes; the drift report contains both an enforcement and a scenario drift; the propose-never-dispose beat runs.  |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/wargamer/propose-policy-pr.sh` | False | Not a verify-*.sh by name but the beat verify-wargamer.sh delegates to: renders the Audit->Deny policy diff without touching main, optionally runs the cross-check gate, narrates the gitsign identity,  |
| `in-module selfchecks: feeds/to_fair_scenario.py selfcheck, wardley/wardley.py selfcheck, wargamer/wargamer.py selfcheck, wargamer/tier_pr.py selfcheck` | False | All four run offline and pass. tier_pr.py's is the heaviest: a real local bare-repo remote plus a stub `gh` on PATH proving PR-vs-issue routing, branch-name dedupe, force-push freshness (1 commit not  |

**Notes:** JSON written to /private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/417e2917-726b-46c9-9117-7b880114f08b/scratchpad/codemap/estate-platform-feeds-wardley-wargamer.json (validated).

Last commit dates in this cluster (repo policy-as-versioned-platform/platform): feeds 2026-08-23 (1a8b871, cs-27 signing rework), wardley 2026-08-23 (f5c0461), wargamer 2026-08-25 (a64b52f, policy-composition tickets 10/17 fixes). All three trace back to 7a36bf7 "Estate build: 27 tickets implemented via dependency-wave workflow" 2026-07-31. These directories are NOT tracked by the outer policy-as-versioned-flux repo (.gitignore:7 excludes .estate-clone/); each org directory is its own git clone.

Cross-estate references: (1) driftwood, ludlow and tuppence each run platform/wargamer/tier_pr.py from .github/workflows/propose-tier.yml - the only production consumer of this cluster; ludlow and tuppence guard it with a file-exists SKIP because their pinned platform tag may predate tier_pr.py, driftwood does not (it pins v1.1.1, which does contain wargamer/tier_pr.py - verified with git ls-tree). (2) platform/honesty/proposer_bounds.py and reflexive.py import wargamer and to_fair_scenario; verify-honesty.sh calls feeds/verify.sh. (3) platform/compose/composition.py shells out to feeds/to_fair_scenario.py for the threat leg of its pricing. (4) driftwood/README.md:58 links to wargamer/README.md. (5) ico/schema/to_fair_scenario.py is a sibling of the same shape, not an importer. Nothing outside platform imports wardley.py at all - the Wardley layer's only consumer is its own verify script.

Two live defects worth a drift review: (a) verify-wargamer.sh and propose-policy-pr.sh both exit 1 wherever the kyverno CLI is installed, because the negative assertion at propose-policy-pr.sh:52-54 no longer holds (ci-check.py now reports workload-flip.yaml compliant across [2.0.0, 2.0.1], pass:1 fail:0) - the beat only "passes" on machines missing the tool it is meant to prove; (b) wardley docs and docstrings say three institutions while risk/appetite.json now carries four, so the live run scores `platform` against its own band and prints 4.

Overall shape: honest, well-asserted offline arithmetic over hand-authored data. Every signature check, ramp, projection, crossover and gate assertion is real code that really runs; every input is a fixture, every £ band is editorial by declaration, and the only thing that ever reaches the outside world is tier_pr.py's gh/git calls in an adopter Actions run - which, given all current prices[] entries carry changed:false, would land nothing today.

## estate — platform/compose + platform/computed-semver (inside .estate-clone/platform, a real GitHub org repo: origin https://github.com/policy-as-vers

### Real

- compose() runs against the real estate and produces committed artefacts with real resolved SHAs — composition.py:1066; driftwood/composed/HEADER.yaml lines 6-22 carry four real 40-char SHAs
- Parent SHA resolution reuses the SHA Renovate already wrote to spec.ref.commit rather than re-deriving it — composition.py:269-283
- Kind-aware render: spec.validationActions written only onto a ValidatingPolicy — composition.py:421-439, asserted at composition.py:1711-1719
- Render faithfulness: strip the three advisory keys and the doc equals the committed source — composition.py:442-465, asserted across every live member at composition.py:1700-1709
- Byte-for-byte verify() of the committed composed tree — composition.py:1328-1352; run in every adopter's cut-release.yml:93
- Baseline resolution against the real nist catalogue, walking nested controls so ac-6.10 is found — composition.py:537-556, 559-591
- OSCAL control-claim merge across every implementations parent plus the adopter's own component-definition.json — composition.py:794-810, 1133-1134, 1175-1176
- Hole / ungoverned-namespace new-recorded-closed diff against the last signed header, with a real bootstrap case — composition.py:880-905 and 516-548
- Restatement strictness ladder Audit<Deny; stricter accepted and rendered, weaker caged — composition.py:236, 712-717
- Weaker restatement priced through the estate's REAL cage engine (platform/graded/cage.py) against the REAL risk/appetite.json band — composition.py:584-597, 612-617, 745
- Pricing/threat re-pricing through the estate's own converters (ico/schema/to_fair_scenario.py, platform/feeds/to_fair_scenario.py) — composition.py:964-973, 602-610, 988-1018
- run_gate produces a complete evidence document on pass and on refusal — gate.py:215-418, asserted gate.py:432-470
- Version legality (5 semver rules, gaps legal, reset-on-bump) — gate.py:139-168
- Computed bump from real kyverno admission movement plus the cage-spec lattice — cage_engine.py:469-489, rederive_bumps.py:46-54
- The gate refuses a declared bump weaker than computed, naming the moved pods and the CEL expression, and passes-with-a-printed-discrepancy on a stronger one — gate.py:337-359, 386-415
- The four structural release-integrity refusals against a real git repo and real tags — release_integrity.py:90-238
- Pairwise corpus generation with a real checksum, real counts and no size ceiling — corpus_generator.py:428-544
- Coverage as counts and named holes with two binary build-failing gates — coverage.py:305-472, wired at gate.py:272-305
- Publisher gate wired into real CI before `git tag`, with cosign keyless evidence signing and no override at any scope — platform/.github/workflows/cut-release.yml:53-72, .github/scripts/cut-release-gate.py:43-52
- Adopter-side composition wired into real CI on every PR with drift detection — driftwood/.github/workflows/shift-left.yml:272-357 (and the tuppence/ludlow equivalents)

### Thin or stubbed

- The per-institution matrix is never populated in production: cut-release-gate.py builds ComparisonWindow WITHOUT institution_pins (.github/scripts/cut-release-gate.py:173-178), so all three committed evidence records carry matrix: {}. The feature is real code (comparison_window.py:108-118, gate.py:323) proved only in gate.py's own selfcheck (gate.py:832-843).
- Six real-infrastructure witnesses (spire, istio, openbao, pomerium, dex, git-server) do not exist — computed-semver/corpus/witnesses/real/ is not present on disk at all. witness_set.py:53-60 names the gap; witness-manifest.yaml records real-infrastructure-committed: 0, missing: 6; verify-witness-set.sh:48-65 prints it loudly but does NOT fail.
- coverage-exclusions.yaml is empty (declared_holes: []) and coverage-baseline.yaml is empty ({}). The declared-hole and baseline-diff machinery is real code exercised only by constructed fixtures in coverage.py's selfcheck; no live data flows through it.
- static_proof (proved exclusions) has zero live hits — coverage.py:56-63 says the real subject carries zero tautologies today.
- not_looked_at[] is empty in all three real evidence records.
- Two of the three limits[] entries are hardcoded 'open by decision' regardless of count — coverage.py:496-534; the third (cage-not-priced-residual) is open only because the six real witnesses are missing.
- The tier axis in the generated corpus is synthetic: no pod maps to a priced residual (coverage.py:527-534). Track 2's cage half is proved on synthetic input only.
- MANUAL_PROBES is a two-entry hardcoded dispatch table for expressions no generic regex shape matches — corpus_generator.py:375-380. probe_for raises rather than skipping on an unrecognised expression (corpus_generator.py:400-405), so the generator's reach is bounded by three regex families plus those two.
- The split-diamond and cross-party rule-conflict refusals fire only against fixtures — the real estate pins exactly one implementations publisher, reported honestly every run via limits[] two-publisher-conflict count 1 / status open (composition.py:1178-1184).
- No restatement fires in the real estate: driftwood/tuppence/ludlow evidence.json all carry restatements: [] and cages: []; the caging table is proved only by selfcheck fixtures (composition.py:1932-1964).
- No real appetite band anywhere in the estate straddles a tier boundary on either real price bump — the crossing case needs a FIXTURE ico penalty schema (composition.py:1551-1581); the real bumps move the £ but never the tier (composition.py:2269-2320).
- The pricing edge re-prices exactly one hardcoded regime/violation-type pair, uk-gdpr/lower-tier — composition.py:953-954; which regimes apply to which workload is an explicitly open gap.
- _resolve_unpinned_sha falls back to a content digest for a non-git party tree (a fixture) — composition.py:298-315; advisory only.
- The composed artefact carries no namespace list and nothing rendered ever reads either namespace set (composition.py:1301-1310) — the governed set is advisory metadata only.
- README.md in computed-semver documents cs-01 only; nine later tickets have no README coverage.
- generator_standing_check.py:33-39 still says no evidence record exists on disk; three do, committed the same day.
- GENERATOR_VERSION is hand-bumped (corpus_generator.py:64-66) — nothing enforces that a logic change bumps it except check_generator_pinning's manifest match.

### Risk and pricing

- composition.py:584-597 _appetite_tolerance — reads platform/risk/appetite.json directly, returns GBP/year tolerance; a missing band is a composition refusal (composition.py:733-740 no-appetite-band), never sys.exit
- composition.py:602-610 _threat_scenario — subprocess into platform/feeds/to_fair_scenario.py threat <register.json> <party>
- composition.py:612-617 _cage_engine — imports platform/graded/cage.py, the estate's real £ engine, explicitly rather than modelling a second one
- composition.py:745 cage.select(scenario, adopter_party, band, mode='warn') — the actual pricing call for a declared inability
- composition.py:747-753 cages[] entry: party, rule, band, residual (tcor.residual or uncaged_residual), tier, action, priced_from, changed
- composition.py:953-954 ICO_REGIME='uk-gdpr', ICO_VIOLATION_TYPE='lower-tier' — the one hardcoded regime/violation pair re-priced
- composition.py:964-973 _ico_scenario — subprocess into ico/schema/to_fair_scenario.py build
- composition.py:988-1018 price_parent — prices old and new versions through cage.select, emits old_price/new_price/old_tier/proposed_tier/changed/proposed_as
- composition.py:1017 proposed_as = 'issue' if tier == 'deny' else 'label' (ADR-0015: a merged tier: deny label would be silently coerced to baseline)
- composition.py:1021-1042 compute_prices — runs every run unconditionally; returns [] when the party has no appetite band
- composition.py:1260-1261 the compose() call site for pricing
- driftwood/composed/evidence.json — real committed £ figures: ico pricing old/new 16,901,471.55 (tier deny, proposed_as issue), platform threat old/new 19,558.55 (tier baseline, proposed_as label)
- DOWNSTREAM (outside this cluster): platform/wargamer/tier_pr.py:233-261 and wargamer/wargamer.py:158-230 read the adopter's committed composed/evidence.json prices[] and turn them into proposals — that is where a PR or issue would actually be opened
- computed-semver has NO £, NO FAIR, NO appetite band, NO TCoR anywhere. The only pricing-adjacent thing is coverage.py:527-534's 'cage-not-priced-residual' limit, whose whole point is to declare that nothing in the corpus maps a pod to a priced residual.

### Cages and enforcement

- composition.py:236 STRICTNESS = {'Audit': 0, 'Deny': 1} — the whole ladder, a ValidatingPolicy concept and nothing else (ADR-0016)
- composition.py:692-700 restatement-of-non-validating refusal (a MutatingPolicy/GeneratingPolicy has no ladder to compare on)
- composition.py:712-717 stricter restatement accepted and the rendered member carries it; weaker is never applied
- composition.py:718-762 weaker restatement = declared inability, priced and caged; the rendered member KEEPS the inherited action
- composition.py:1966-1990 selfcheck asserts no tier and no tier floor appears anywhere composition itself writes (exact-key check on its own three added metadata keys)
- composition.py:396-410 _load_guards — the ORPHAN GUARD (rendered from the real version array via render-orphan-guard.py) and the GOVERNED-NAMESPACE GUARD (render-governed-namespace-guard.py, ADR-0014's fifth gap), both composed under the platform tag with version: None
- composition.py:473-489 governed_namespaces / 491-514 ungoverned_namespaces — the governed-namespace lint: an institution-labelled Namespace without governed:"true" is ungoverned; no institution label means infrastructure and is ignored
- composition.py:516-548 compute_ungoverned — new refuses, recorded does not, closed prints; bootstrap records everything and refuses on none
- composition.py:1253-1255 the compose() call site; composition.py:1308 the header field ungoverned-namespaces
- composition.py:1179-1184 limits[] two-publisher-conflict, count 1 status open in the real estate
- cage_engine.py:29-56 Track 2: the cage-spec permissiveness lattice with UNCAGED at the top, so 'cage-tier added' = major and 'cage-tier removed' = patch need no special case
- cage_engine.py:156-167 _pc_value_table — reads real PriorityClass `value:` fields out of graded/policies/priorityclasses.yaml
- cage_engine.py:194-205 CageSpec / UNCAGED; 219-244 dial_table parses the real cage-tier.yaml `dial` CEL map with ast.literal_eval
- cage_engine.py:250-282 permissive_rank / at_least_as_permissive — a genuine partial order over cpu, mem, priorityClass, dropAll, readOnlyRootFs, waf; one field improving never excuses another regressing
- cage_engine.py:288-297 effective_tier — mirrors cage-tier.yaml's own CEL default-to-baseline, never a skip
- cage_engine.py:394-437 classify_cage_tier; cage_engine.py:146 RANK with 'removed' aggregating at patch's rank
- coverage.py:496-534 compute_limits — cage-ratchet-one-way and cage-removal-scores-patch both hardcoded status 'open' by decision; cage-not-priced-residual closes only when the six real witnesses land
- gate.py:337-359 / 386-415 — declared weaker than computed refuses and names the moved pods plus the CEL expression; stronger passes with a printed discrepancy
- NOT PRESENT in this cluster: de-posture, the currency controller, break-glass. No reference to any of them in either directory.

### Feeds, Wardley, war-gamer

- composition.py:602-610 _threat_scenario — REAL subprocess into platform/feeds/to_fair_scenario.py against feeds/threat-register/v{1,2}/register.json. Real converter, but the register is a hand-authored, committed, repo-locally-signed JSON fixture (feeds/README.md), not a live feed poll. SIMULATED as an ingestion path.
- composition.py:964-973 _ico_scenario — REAL subprocess into ico/schema/to_fair_scenario.py against a committed penalty schema. Real converter, fixture data, no live regulator fetch.
- composition.py:1017 proposed_as marks a deny as 'issue' and everything else as 'label' — explicitly THE MARK, NOT THE ACT (composition.py:175-181): composition itself opens nothing.
- NOTHING in platform/compose or platform/computed-semver opens a PR or an issue. The proposer that reads prices[] lives in platform/wargamer (tier_pr.py:233-261, propose-policy-pr.sh) — a different cluster.
- NOTHING in either directory reads a live feed, calls a network endpoint, or fetches a URL at runtime. The only network calls in the surrounding CI are pinned binary downloads (gitsign/cosign/kyverno by SHA256) and actions/checkout.
- NO Wardley map, value chain, evolution axis or gameplay reference anywhere in either directory. platform/wardley/ is a separate cluster.
- NO wargamer scenario, NPC or move generation in either directory.
- The only 'simulated adversary' shape present is the corpus generator's forged-posture probe (corpus_generator.py:290-306), which models the posture-trust-boundary policy's own documented threat as a pod fixture — a test input, not a wargame.

### Original-thesis mechanisms

- MULTI-VERSION COEXISTENCE — PRESENT and load-bearing. comparison_window.py is entirely about it (comparison_window.py:5-40); gate.py:312-362 wires it; the retirement rule forces major with no body diff (comparison_window.py:93-106). In compose it appears as load_implementations walking every live policy version (composition.py:328-345) and composing per-version trees (composition.py:1273).
- RESOURCESET MATRIX — PRESENT as a READ dependency only. distribution/versions.yaml is a flux-operator ResourceSet whose spec.inputs[0].versions array is read by composition.py:322-326, corpus_generator (via render-orphan-guard.versions()), release_integrity.py:203-213 and cut-release-gate.py. Neither directory writes or reconciles a ResourceSet; the selfcheck fixture writes a minimal one at composition.py:2414-2421.
- RENOVATE BUMP PR — PRESENT only as a consumed artefact. composition.py:269-283 reuses the SHA Renovate wrote to spec.ref.commit; composition.py:1457-1466 _bump_parent_version simulates 'the same edit a real Renovate PR would make to party.yaml'. Nothing here runs Renovate or opens a bump PR.
- SIGNED TAGS — PRESENT and real, at the CI boundary rather than inside these directories. gitsign-signed release commits/tags and cosign keyless sign-blob of the gate evidence (cut-release.yml:53-72; cut-release-gate.py:202), re-verified per policy tag at release.yml:103-125. Three real .bundle files in computed-semver/evidence/. The gate runs BEFORE `git tag` by design.
- ORPHAN GUARD — PRESENT in both halves. compose loads it through the parent's own offline twin and renders it under the platform tag with version None (composition.py:396-410, asserted composition.py:1721-1729). computed-semver uses the same twin for the version-pin axis (corpus_generator.py:88) and pairing.py:50-62 proves the emitted guard really carries the platform-machinery identity. Its sibling, the governed-namespace guard, loads the same way (composition.py:404-405).
- OSCAL / C2P — OSCAL PRESENT, C2P ABSENT. Real catalogue and profile reads (composition.py:537-591), real component-definition Check_Id claim parsing (composition.py:794-810), claim ownership per ADR-0017 (composition.py:829-877), 285 real holes recorded. No compliance-to-policy tooling, no assessment-results generation, no result2oscal call anywhere in this cluster.
- SHIFT-LEFT — PRESENT as the calling context, not as code here. Each adopter's shift-left.yml has a compose-check job running composition.py on every PR (driftwood/.github/workflows/shift-left.yml:272-357). rederive_bumps.py:19 explicitly reuses the same offline `kyverno apply` primitive platform/shift-left/verify-shift-left.sh runs.
- HANDBOOK — ABSENT. No handbook, operator guide or runbook in either directory. compose/README.md is a per-ticket engineering account; computed-semver/README.md covers ticket cs-01 only.
- SUNSET — PARTIAL. Retirement is modelled: a version leaving new_window forces major (comparison_window.py:23-30, 93-106) and gate.py case D proves it on a byte-identical body. But there is no EOL/sunset date, no --as-of, no clock: composition.py:2358-2373 asserts the module cannot even import datetime/time/sched/croniter, and an 'eol' parent kind does not exist in the party artefact schema.
- NOTIFICATIONS — ABSENT as delivery. Nearest thing is a GitHub job summary written by the adopter compose-check step (shift-left.yml:339-346) and gh pr comment in an adjacent job. No Slack, email, webhook or alerting anywhere in either directory.
- DASHBOARDS — ABSENT. No Grafana, Prometheus, metrics export or dashboard JSON. Evidence is JSON documents and printed selfcheck lines only.

### Runtime dependencies

- kyverno CLI — REAL. `kyverno apply` shelled out one policy file at a time, offline, no cluster (rederive_bumps.py:49-54, 178). Pinned by SHA256 in cut-release.yml (KYVERNO_VERSION 1.18.2). Present on this machine and exercised by 6 of the verify runs.
- cosign — REAL. Keyless sign-blob of gate evidence in cut-release-gate.py:202, verified with `cosign verify-blob --certificate-identity-regexp` in release.yml:109-113. Real sigstore certs in the committed .bundle files.
- gitsign — REAL. Pinned by SHA256 in cut-release.yml; signs release commits/tags.
- GitHub Actions — REAL. platform/.github/workflows/{cut-release,release}.yml; driftwood/tuppence/ludlow shift-left.yml and cut-release.yml, with cross-repo actions/checkout@v4 at the adopter's own pinned tags.
- git — REAL. `git show <tag>:<path>` for the frozen-tree rule (release_integrity.py:90), `git log -1 --format=%H` for unpinned parent SHAs (composition.py:301-306), `git tag -l policy/v*` for the legal version history (cut-release-gate.py:92-101).
- Flux — INDIRECT, not run by this cluster. composition.py READS the adopter's GitRepository spec.ref.commit off disk (composition.py:269-283) and reads distribution/versions.yaml, a flux-operator ResourceSet. Nothing here is Flux-reconciled; neither directory has a kustomization.yaml.
- Renovate — INDIRECT. Its written spec.ref.commit is what composition.py reuses; composition.py:1457-1466 simulates the edit a Renovate PR would make. Nothing here runs Renovate or opens a bump PR.
- PyYAML — REAL, the only third-party python dependency.
- platform/graded/cage.py — REAL, imported live by composition.py:612-617; its TIERS presets read for real (not modelled) by cage_engine.py:156-167 and 219-244.
- platform/risk/appetite.json — REAL, read directly at composition.py:584-597.
- platform/feeds/to_fair_scenario.py + feeds/threat-register/v{1,2}/register.json — REAL code path (subprocess, composition.py:602-610), but the feed itself is a hand-authored versioned JSON fixture with a repo-local demo signing key (feeds/README.md). SIMULATED as a data source.
- ico/schema/to_fair_scenario.py + ico/schema/v1/penalty-schema.json — REAL converter and real committed schema, invoked as a subprocess (composition.py:964-973). The band-crossing variant used in tests is a fixture (composition.py:1551-1581).
- platform/distribution/render-orphan-guard.py and render-governed-namespace-guard.py — REAL offline twins, dynamically imported (composition.py:396-410, corpus_generator.py:88-89).
- platform/distribution/render-version-tree.py — REAL, used by corpus_generator and by release_integrity's re-render and mandatory-member rules.
- nist catalogue + BASELINE_VERSIONS.json — REAL committed OSCAL data read by composition.py:537-591.
- SPIRE / Istio / OpenBao / Pomerium / Dex / git-server — NAMED ONLY, absent. Six real-infrastructure witnesses that do not exist on disk (witness_set.py:53-60).
- Kubernetes cluster, Crossplane, C2P, trivy — NOT USED anywhere in this cluster. No verify script in either directory needs a cluster.

### Verify scripts

| Script | Needs cluster | Proves |
|---|---|---|
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/compose/verify-composition.sh` | False | composition.py --selfcheck: the real driftwood composes against its real pinned parents with zero refusals; render faithfulness across every live member; verify() catches tampering; every ticket-13/14 |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/computed-semver/verify-rederive-bumps.sh` | False | the three known-good historical bumps rederive from observed kyverno admission movement. Needs the real kyverno CLI (offline); SKIPs exit 0 without it. RAN HERE: exit 0. |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/computed-semver/verify-gate.sh` | False | gate.py --selfcheck — the whole seam: document shape, version legality, computed vs declared bump, coverage gates, comparison window cases A-E, release-integrity through the seam. Gated on kyverno pre |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/computed-semver/verify-cage-engine.sh` | False | cage_engine --selfcheck: Track 1 admission (needs kyverno, SKIPs otherwise) and Track 2's permissiveness lattice (pure python). RAN HERE: exit 0. |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/computed-semver/verify-corpus-generator.sh` | False | 3 steps: generator selfcheck; regenerate the committed spine into a scratch dir and diff byte-for-byte (manifest minus wall_clock); kyverno-evaluate a sample generated pod against the real require-non |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/computed-semver/verify-witness-set.sh` | False | 5 steps: witness selfcheck; the missing-shape gate passes against the committed corpus; the witness manifest regenerates byte-identical; the six missing real-infra witnesses print loudly WITHOUT faili |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/computed-semver/verify-pairing.sh` | False | pairing.py --selfcheck: pairing on (identity, version-stripped name) proved by a filename swap; set comparison of rules; unversioned-member refusal; platform-machinery as a class not a name; two v1.0. |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/computed-semver/verify-coverage.sh` | False | coverage.py --selfcheck plus gate.py --selfcheck (the two coverage gates through the seam). No kyverno gate on the script, but gate.py's selfcheck does shell out to kyverno for the historical rederiva |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/computed-semver/verify-comparison-window.sh` | False | comparison_window.py --selfcheck: strictest-of-window, retirement forces major, backport narrowing, the per-institution matrix. Needs kyverno (SKIPs otherwise). RAN HERE: exit 0, but slow (10+ minutes |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/computed-semver/verify-release-integrity.sh` | False | release_integrity.py --selfcheck: builds a real git repo + tag and hand-edits to prove each of the four refusals fires (frozen tree, re-render, mandatory member, empty commit). No kyverno needed. RAN  |
| `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform/computed-semver/verify-generator-standing-check.sh` | False | the generator's one standing check: the three known-good bumps must still rederive (refuses if any stops), the committed manifest's generator_version must match the live generator, and the most recent |

**Notes:** JSON written to /private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/417e2917-726b-46c9-9117-7b880114f08b/scratchpad/codemap/estate-platform-compose-semver.json.

ORIGINAL-ORG CLUSTER NOTES. Both directories live inside .estate-clone/platform, which is its own git repo (remote https://github.com/policy-as-versioned-platform/platform) and is NOT tracked by the outer policy-as-versioned-flux repo — `git ls-files platform/compose` from the outer repo returns nothing, and .estate-clone is untracked. Last commits: platform/compose — 2b69a6a 2026-08-25 "policy-composition: fix ac-6/cm-6 dangling claims, build ADR-0014's guard" (only two commits ever touch it; the other is 963872b 2026-08-25 "WIP: uncommitted policy-composition tickets 09-16 work, safety commit"). platform/computed-semver — 58ef9c5 2026-08-25 "cs-27: signed release-gate evidence for policy/v3.0.0", which is also the repo HEAD; preceding 7cf0d55 and d64e0d5 (same day, evidence for 2.0.1 and 2.0.0), then 860e744 and 7a8df7b 2026-08-24 (cs-16 fixes). Everything in this cluster landed 2026-08-24/25.

CROSS-ESTATE REFERENCES (six-org estate). platform/compose is referenced by all three adopter repos: driftwood/.github/workflows/shift-left.yml:336 and cut-release.yml:93, tuppence/.github/workflows/shift-left.yml:336 and cut-release.yml:93, ludlow/.github/workflows/shift-left.yml:330 and cut-release.yml:93; also mentioned in each adopter's adopter-gate script and read-two-pins.py. All three carry committed composed/ trees (HEADER.yaml, evidence.json, orphan-guard.yaml, governed-namespace-guard.yaml, policies/). platform/computed-semver is referenced by platform/.github/workflows/{cut-release,release}.yml, platform/.github/scripts/{cut-release-gate.py,cut-release-commit-evidence.sh}, platform/verify-publisher-gate.sh, platform/distribution/render-orphan-guard.py, platform/feeds/README.md, and by the driftwood/tuppence/ludlow adopter-gate scripts. It in turn reads platform/graded, platform/risk, platform/feeds, platform/distribution and (via compose) the nist and ico org repos.

DRIFT-RELEVANT OBSERVATIONS, neutral: (1) the per-institution matrix is the clearest built-but-not-wired case — real code, real selfcheck, matrix: {} in every committed evidence record because cut-release-gate.py never passes institution_pins. (2) The six real-infrastructure witnesses were named in the spec and never landed; the directory does not exist; the gate prints the gap without failing, which is the disclosed design. (3) coverage-exclusions.yaml and coverage-baseline.yaml are both empty — the two-tier exclusion mechanism is real code with zero live data. (4) All three committed evidence documents record computed "no predecessor" or "none" against a declared major/patch — no real release in this line has yet had the gate compute a bump that constrained the publisher's number; every pass so far is "declared stronger than computed". (5) composition.py's real-estate outcome flipped from "refuses today" (README ticket-14 section) to "composes clean" (composition.py:1483) within the same commit that fixed ac-6/cm-6; the README paragraph reads as stale in isolation. (6) generator_standing_check.py's docstring claim that no evidence record exists on disk is stale. (7) Zero restatements and zero cages fire in the real estate; the caging and cage-tier proposal paths are fixture-proved only. (8) I RAN 9 of the 11 verify scripts to completion here (kyverno and cosign both present, no cluster, no network): verify-composition.sh, verify-pairing.sh, verify-release-integrity.sh, verify-coverage.sh, verify-comparison-window.sh, verify-corpus-generator.sh, verify-witness-set.sh, verify-cage-engine.sh, verify-rederive-bumps.sh — ALL exit 0, no SKIPs. verify-gate.sh and verify-generator-standing-check.sh were still running when I finished, but verify-coverage.sh already runs gate.py --selfcheck in full and passed.

## estate — platform publisher cluster — .estate-clone/platform: README.md, distribution/, policy/, engine/, shift-left/, party/, top-level verify-*.sh,

### Real

- Multi-version coexistence via matchConditions self-scoping, proved offline with the real kyverno CLI: distribution/tests/require-nonroot/kyverno-test.yaml:14-40 asserts pass/fail/skip for 2.0.0 and 3.0.0 against five pods; verify-coexistence.sh:19-21 runs it (step 1 passed on this machine).
- The orphan-guard allow-list is genuinely derived from the array, never hand-maintained: render-orphan-guard.py:47-49 and versions.yaml:87-88 both range the same field; verify-orphan-guard.sh RUN, exit 0 — 9.9.9 denied, the declared version admitted, unversioned skipped, exact verdict spread asserted at verify-orphan-guard.sh:55.
- Retirement-by-deletion proved offline: verify-retirement.sh:28-41 RUN, exit 0 — the same pod flips admit->deny when 2.0.0 is dropped from the array.
- Per-version tree rendering from single authoring copies, with the cage-tier PriorityClass rewrite: render-version-tree.py:114-144, --selfcheck passes, and verify-render-version-tree.sh:51-55 proves version isolation with a real `kyverno apply` mutation check (exit 0).
- The governed-namespace claim requirement, functionally: verify-governed-namespace-guard.sh:61-68 RUN, exit 0 — unclaimed pod denied, claimed pod admitted, exact spread asserted.
- Kyverno + flux-operator actually installed and running: engine/verify-engine.sh:55-68 live branch RUN and passed on kind-driftwood (4 CRD/pod assertions).
- The shift-left check's orphan-target refusal and unversioned pass-through: verify-shift-left.sh:17-18 and :29-34 both hold (only the flip case fails).
- The party artefact check, end to end against real Flux pin files: party_artefact.py:373-441 selfcheck; wired cross-org in driftwood/.github/workflows/shift-left.yml.
- Release cutting: multi-tag dispatch, all-tags-checked-before-any-created refusal, atomic push rollback, and cs-27's mis-shaped-tag refusal — all proved against a real git repo and a real local bare remote by verify-cut-release-tags.sh:34-108 (exit 0).
- Real keyless signing happened: computed-semver/evidence/*.json.bundle carry real base64 Fulcio certs and signatures; policy/v2.0.0, policy/v2.0.1, policy/v3.0.0 exist as real tags.
- Identity pinning: verify-certificate-identity-regexp.sh:19-40 (exit 0) proves release.yml:54's regexp rejects foreign orgs, foreign workflow paths and unanchored variants.
- Real downstream consumption: driftwood/ludlow/tuppence each carry composed/orphan-guard.yaml and composed/governed-namespace-guard.yaml rendered from this cluster's twins, annotated `inherited-from: platform@1.1.1`, with the allow-list literal ['2.0.0','2.0.1','3.0.0'] matching versions.yaml:31-33 exactly.

### Thin or stubbed

- THE FAN-OUT HAS NEVER RUN LIVE. `kubectl -n flux-system get resourceset` on kind-driftwood returns 'No resources found'; there are no policy-vN Kustomizations and no policy-vN GitRepositories. The cluster instead carries hand-applied require-nonroot-1-0-0 / require-nonroot-2-0-0 (ages 4d20h) — versions not in the current array. Every distribution claim is offline-only, as distribution/README.md:59-71 and :73-83 honestly say.
- verify-shift-left.sh FAILS TODAY (exit 1). fixtures/workload-flip.yaml:8-13 targets 2.0.0 and relies on 3.0.0 being the +1 neighbour; cs-16's insertion of 2.0.1 at versions.yaml:32 moved 3.0.0 out of the ±1 window (ci-check.py:68-78), so the Audit->Deny flip is no longer caught. release.yml:87 runs this as the release gate.
- verify-coexistence.sh FAILS TODAY (exit 1) — not offline, but because its 'optional live tail' is not optional-safe: verify-coexistence.sh:29-34 fires whenever ANY validatingpolicy exists at CTX and then hard-fails on require-nonroot-3-0-0 being absent. A reachable-but-unfanned-out cluster turns an offline-green beat red.
- verify-retirement.sh:55-56 prints 'live: policy-v2-0-0 Kustomization is gone at context kind-driftwood — retirement pruned it live'. FALSE POSITIVE: that Kustomization was never created, so 'gone' proves nothing. The script's own comment at :47-50 says the passive read must 'say so plainly'; the elif branch does the opposite.
- The offline twins DRIFT from the live ResourceSet render, and nothing checks it: render-orphan-guard.py:65 and render-governed-namespace-guard.py:57 both stamp `policy-as-versioned.dev/policy: platform-machinery` (cs-22's pairing-rule identity), while versions.yaml:70-71 and :109-110 render the same two policies with NO labels at all. The twins are documented as what flux-operator would render (render-orphan-guard.py:4-11); they are not.
- render-and-prove.py:22-30's honesty note is stale: it says distribution/policies/vN/kustomization.yaml does not name the graded/posture members and that the fold-in is simulated. v2.0.0/v2.0.1/v3.0.0 kustomization.yaml now name all six.
- cut-release-gate.py:218-222 claims release.yml refuses a CUT_RELEASE_TEST_MODE bundle by reading the flag. release-verify-evidence.py:25-30 reads only outcome and declared — no test_mode check.
- README.md:19's 'notification event spine' and README.md:17-19's dependsOn/health/drift-heal are not present anywhere in this cluster (no Alert/Provider/Receiver in the whole platform repo; no dependsOn/healthChecks in distribution/versions.yaml).
- verify-publisher-gate.sh is real but effectively unrunnable at demo speed: ~28 minutes on this machine without finishing Part A, against a documented 'several minutes' (verify-publisher-gate.sh:20-22).
- distribution/README.md:31's mermaid says the Kustomization path is './policies/vN'; versions.yaml:61 renders './distribution/policies/vN'. Cosmetic, but a reader following the README looks in the wrong place.
- shift-left/ci-workflow.example.yml is a reference shape only — 'Not run here' (lines 2-3). The real wiring lives in each adopter repo.
- distribution/policies/v1.0.0 is on disk but in no array element and covered by no test (the kyverno test matrix uses 2.0.0/3.0.0 only). Deliberate per render-orphan-guard.py:121-128, but it is dead weight a reader can mistake for a shipped version.

### Risk and pricing

- platform/policy/verify-conditional.sh:37-42 — step 3 shells out to ../fair/fair.py summary on policy/scenarios/driftwood-root-residual.json --mode warn and asserts the residual ALE is positive. Real computation: verified independently, ale = 21359.7, var95 = 36573.3, tvar = 40913.3, carried = 42086.5.
- platform/policy/scenarios/driftwood-root-residual.json:5-12 — the FAIR (min,mode,max) triples for the caged root residual, warn vs deny branches. Fixture data, real engine.
- platform/policy/README.md:53 — '£21,360/yr' claim, matches the live fair.py output exactly.
- platform/policy/README.md:62-66 — '£ picks the loosest tier whose caged residual fits the org's appetite band (baseline for driftwood, TCoR ≈ £23.7k/yr)' — narrative only in this cluster; computed in the sibling ../graded/cage.py and ../tcor/tcor.py.
- platform/policy/README.md:73-81 — the OSCAL risk object carries the £ ALE as a facet under https://pavf.dev/ns/risk/gbp; generator is ../graded/cage.py, not in this cluster.
- platform/README.md:20-21 and :31-33 — the FAIR engine and platform's own strict £10k appetite band (risk/appetite.json, root_of_trust: true) are described here, implemented in the sibling fair/ and risk/ areas.
- NOTHING in distribution/, engine/, shift-left/, party/ or .github/ computes or consumes £ at all. The publisher gate is a semver-movement gate, not a priced one: cut-release-gate.py and gate.run_gate() decide on declared-vs-computed bump, and computed-semver/evidence/3.0.0.json carries outcome/bump/movement/counts with no monetary term anywhere.

### Cages and enforcement

- Graded cage tiers, rendered per version: render-version-tree.py:74-80 pulls graded/policies/cage-tier.yaml, cage-netpol.yaml and priorityclasses.yaml (cage-baseline/-restricted/-quarantine, values -10/-100/-1000) into each distribution/policies/vN tree.
- render-version-tree.py:135-142 rewrites cage-tier's dial table so each version's cage names only its own versioned PriorityClasses — verified in the committed trees (distribution/policies/v3.0.0/cage-tier.yaml:36 names cage-baseline-3-0-0 etc.), and asserted at render-version-tree.py:199-206.
- Orphan guard, Deny: versions.yaml:73 validationActions:[Deny]; render-orphan-guard.py:67. Unlabelled pods are deliberately out of scope (matchConditions at versions.yaml:80-83) — absence is not the trigger.
- render-orphan-guard.py:59 refuses to render an orphan-guard with an empty allow-list — fail-closed against retiring the last version.
- Governed-namespace guard, Audit: versions.yaml:112 and render-governed-namespace-guard.py:60. ADR-0014's fifth named gap; starts Audit and promotes by editorial PR, never a timer (versions.yaml:104-106).
- De-posture / currency-controller: the governed-namespace guard is CREATE-only precisely so the currency-controller's de-posture UPDATE patch keeps working — render-governed-namespace-guard.py:7-9, :48-51, :86 and versions.yaml:103-104. The currency-controller itself is a sibling area; this cluster only carves the hole for it.
- Audit-only enforcement everywhere in the shipped policy trees: every require-nonroot version (v1.0.0:18, v2.0.1:29, v3.0.0:18) is validationActions:[Audit]. The only Deny in this cluster is the orphan guard. Audit->Deny promotion is stated as editorial (v3.0.0/require-nonroot.yaml:7-8, ADR-0006) and verify-publisher-gate.sh:128-145 uses that promotion as its one disclosed mutation to manufacture a real narrowing.
- Exemptions banned rather than dissolved: policy/README.md:1-15 and :56-66 — the git-ledger/PolicyException mechanism is deleted, and a one-off that cannot meet condition C gets ../graded/cage.py's priced tier or Deny, never a carve-out.
- Shift-left as pre-merge enforcement: shift-left/README.md:16-21 and ci-check.py:14-19 — `kyverno apply` reports the CEL verdict regardless of Audit/Deny, so the flip is catchable pre-merge. Currently not caught for the shipped fixture (see stubbed/thin).
- Publisher gate as release-time enforcement: cut-release.yml:142-147 runs the gate BEFORE `git tag` ('a gate after the tag can only burn the number'), with no override at any scope (cut-release-gate.py:43-52), and a refusal on any policy tag blocks the whole dispatch (cut-release-gate.py:279-284).
- Governed-namespace lint escalated one level up: compose/composition.py:133-150 (sibling area) turns an un-labelled institution namespace into a refusal, using the same GOVERNED_LABEL this cluster defines.

### Feeds, Wardley, war-gamer

- NOTHING in this cluster reads a feed, builds a Wardley map, or war-games. distribution/, policy/, engine/, shift-left/, party/ and .github/ contain no reference to feeds, wardley or the wargamer.
- The only mention is narrative: platform/README.md:25-26 — 'war-gamer + AI-Wardley — collect → war-game → signed policy PR (propose-never-dispose)'. The implementation is the sibling wargamer/, feeds/ and wardley/ areas.
- Inbound touchpoint from the sibling wargamer: wargamer/propose-policy-pr.sh:16-17 reads distribution/policies/v2.0.0/require-nonroot.yaml and calls shift-left/ci-check.py, and at :51-53 asserts ci-check.py must FAIL on shift-left/fixtures/workload-flip.yaml. That call is a second casualty of the ±1-window regression — the script exits 1 when the fixture now passes.
- DOES ANYTHING OPEN A REAL PR? Not in this cluster, and not in the wargamer either: wargamer/propose-policy-pr.sh:5-6 states plainly 'It NEVER commits, pushes, opens or merges the PR itself'; it renders a diff and stops. It also degrades to narration when kyverno/gitsign are absent (:12, :58-60).
- Real PR machinery that DOES exist, downstream of this cluster: each adopter's shift-left.yml edits the pull request BODY for real via `gh pr edit --body-file` and posts a signed cosign attestation comment via `gh pr comment` (driftwood/.github/workflows/shift-left.yml). Those PRs are opened by Renovate, not by anything in platform.
- DOES ANYTHING READ A REAL FEED? Not in this cluster. The threat and pricing parents are explicitly named as having NO Flux pin anywhere in this estate (party_artefact.py:26-35, :74, :203-208): ico ships no git tags at all, and the threat register is a versioned subdirectory read out of the already-pinned platform checkout, not a second pin.

### Original-thesis mechanisms

- MULTI-VERSION COEXISTENCE — PRESENT and the strongest thing here. distribution/README.md:40-48 (matchConditions, never objectSelector, with the shared-webhook rationale), every policy body's only-this-policy-version matchCondition, distribution/tests/require-nonroot/kyverno-test.yaml's full pass/fail/skip matrix, verify-coexistence.sh and verify-render-version-tree.sh. Proved offline with the real kyverno CLI; never observed live.
- RESOURCESET MATRIX — PRESENT as a declaration (distribution/versions.yaml:21-128: one array fanning out GitRepository + Kustomization per version plus two singleton guards) and modelled faithfully by the offline twins. NEVER RECONCILED: no ResourceSet exists in the reachable cluster. The twins also add a platform-machinery identity label the ResourceSet render does not.
- RENOVATE BUMP PR — NOT in this cluster; documented at README.md:58-60 and implemented in the adopters (driftwood/ludlow/tuppence renovate.json, two git-refs customManagers each, automerge:false, rangeStrategy pin). Real.
- SIGNED TAGS — PRESENT and REAL. cut-release.yml + .github/scripts/cut-release-create-tags.sh:21-24 (gitsign keyless via the run's ambient Actions identity), release.yml:89-101 (gitsign verify-tag identity-pinned, offline Rekor bundle), verify-certificate-identity-regexp.sh and verify-cut-release-tags.sh as offline twins. Three real policy/v* tags and five real v* tags on disk; real cosign bundles committed under computed-semver/evidence/.
- ORPHAN GUARD — PRESENT and real offline. versions.yaml:67-95 (live render), render-orphan-guard.py (twin), verify-orphan-guard.sh and verify-retirement.sh (both exit 0). Composed into all three adopters' composed/orphan-guard.yaml.
- OSCAL / C2P — ABSENT from this cluster as code. Referenced narratively only: policy/README.md:12-15 and :68-81 (cage.oscal_risk, the £ facet under https://pavf.dev/ns/risk/gbp, related-observations joining ../oscal/result2oscal.py) and party/README.md:50. No C2P anywhere in the repo.
- SHIFT-LEFT — PRESENT: shift-left/ci-check.py is real, reuses the one array, runs the real kyverno CLI, and is wired cross-org into all three adopters' shift-left.yml plus platform's own release.yml:87 gate. Currently REGRESSED — its own verify fails because the ±1 window no longer reaches the version the flip fixture violates.
- HANDBOOK — ABSENT. No handbook, runbook or narrative guide in this cluster; distribution/README.md:81-83 and policy/README.md:95-100 defer live bring-up to 'the parent runbook (ticket 26)', which is not here.
- SUNSET / RETIREMENT — PRESENT as retirement (delete the array element -> Flux prunes -> the re-rendered guard denies stragglers): distribution/README.md:36-38, versions.yaml:62-63 (prune: true), verify-retirement.sh. No time-based sunset anywhere, deliberately — ADR-0006's 'editorial, never a timer' is restated at v3.0.0/require-nonroot.yaml:7-8, ci-check.py:17-18 and versions.yaml:104-106.
- NOTIFICATIONS — ABSENT despite being claimed. README.md:19 promises 'the notification event spine'; there is no Alert, Provider or Receiver anywhere in the platform repo. The only notification-shaped behaviour in the estate is the adopters' PR body edits and comments, which are downstream and not Flux notifications.
- DASHBOARDS — ABSENT. No Grafana, no dashboards, no metrics in this cluster. The nearest thing is cut-release-gate.py:229-241's GITHUB_STEP_SUMMARY markdown table for the gate outcome.

### Runtime dependencies

- Flux (source/kustomize/helm controllers) — REAL and installed on kind-driftwood (a `driftwood` Kustomization is Ready), but no distribution object of this cluster is reconciled by it.
- flux-operator (ResourceSet CRD) — REAL: HelmRelease at engine/flux-operator/helmrelease.yaml pinned to OCI tag 0.58.1, pod present and CRD registered live. But zero ResourceSet objects exist, so its templating has never been exercised — the versions.yaml render is only ever produced by the python twins. SIMULATED in every proof.
- Kyverno — REAL, twice over: the admission controller is installed live (chart 3.8.2 / appVersion 1.18.2, both CRDs registered), and the pinned kyverno CLI 1.18.2 is genuinely invoked by verify-orphan-guard.sh, verify-retirement.sh, verify-render-version-tree.sh, verify-governed-namespace-guard.sh, verify-coexistence.sh, shift-left/ci-check.py:89-92 and the publisher gate.
- kubectl — REAL, used by engine/up.sh, engine/verify-engine.sh, the verify live tails, and by render-and-prove.py:98 as the independent `kubectl kustomize` builder.
- gitsign 0.17.1 — REAL in CI (pinned binary + sha256 at cut-release.yml:88-89 and release.yml:48-49; `gitsign verify-tag` identity-pinned with an offline Rekor bundle at release.yml:99-101). SIMULATED in the offline twin: CUT_RELEASE_TEST_MODE=1 swaps it for a plain annotated tag (cut-release-create-tags.sh:18-19). The boundary is stated openly.
- cosign 2.4.1 — REAL in CI (`cosign sign-blob` keyless at cut-release-gate.py:225; `cosign verify-blob` at release.yml:124-128) and the committed evidence bundles carry genuine Fulcio certificates. SIMULATED locally (cut-release-gate.py:213-224 writes a marked non-signature).
- GitHub Actions — REAL: cut-release.yml and release.yml have both demonstrably run (real signed tags, real evidence commits, HEAD is one such commit).
- Renovate — REAL but downstream, not in this cluster: driftwood/ludlow/tuppence renovate.json each define two git-refs customManagers maintaining the {tag, commit} pair for the nist and platform pins, automerge:false, rangeStrategy pin.
- jq — REAL, required by four .github/scripts and by verify-cut-release-tags.sh.
- PyYAML — REAL, required by every renderer, ci-check.py, party_artefact.py and cut-release-gate.py.
- SPIRE / Istio / OpenBao / Pomerium / Crossplane / trivy / C2P — NOT PRESENT in this cluster at all (they live in the sibling identity/, access/, oscal/, posture/, eud/ areas). This cluster references OSCAL narratively only (policy/README.md:68-81, party/README.md:50); no C2P anywhere.
- A KiND cluster (default CTX kind-driftwood) — REAL and reachable, which is exactly what exposes verify-coexistence.sh's live-tail failure and verify-retirement.sh's misleading live line.

### Verify scripts

| Script | Needs cluster | Proves |
|---|---|---|
| `platform/distribution/verify-coexistence.sh` | False | Offline core (kyverno test + render-orphan-guard --selfcheck) proves two versions self-scope and admit side by side with no shared-webhook collision. RUN → exit 1: steps 1 and 2 pass, but the live tai |
| `platform/distribution/verify-orphan-guard.sh` | False | A version not in the array is denied, a declared version admits, an unversioned pod is out of scope — via a real `kyverno apply` on the rendered guard, with the exact verdict spread asserted (:55). RU |
| `platform/distribution/verify-retirement.sh` | False | Deleting one array element flips the same pod from admitted to denied (the orphan-guard re-rendered from the shrunk array). RUN → exit 0. Its live tail (:51-59) is passive and currently emits a mislea |
| `platform/distribution/verify-render-version-tree.sh` | False | All 7 mandatory members render with versioned names/labels/matchConditions self-scope and never objectSelector; live path == offline twin; re-render refused; and with the real kyverno CLI, 8.8.8's cag |
| `platform/distribution/verify-governed-namespace-guard.sh` | False | Structurally: the guard is platform-machinery, Audit, CREATE-only, namespaceSelector governed=true. Functionally: the claim-requirement expression denies an unclaimed pod and admits a claimed one, wit |
| `platform/policy/verify-conditional.sh` | False | One conditional CEL rule ('nonroot // (attested && hardened)') admits everyone meeting C with no named team, fails those who don't, skips the unversioned pod, and its residual is priced by fair.py. No |
| `platform/engine/verify-engine.sh` | False | Offline: both HelmReleases parse, charts are pinned, flux-operator comes from an OCIRepository, and no FluxInstance exists (the ADR-0005 guardrail). Live (opt-in on ns kyverno existing, :55): Kyverno  |
| `platform/shift-left/verify-shift-left.sh` | False | Intends: a compliant workload passes its ±1 window; an unversioned one passes trivially; an Audit->Deny flip fails CI; an orphan target is refused. RUN → exit 1. Three of four hold; the flip case no l |
| `platform/party/verify-party-artefact.sh` | False | party_artefact.py --selfcheck: schema.json is the single enum source; every structural defect is caught; a real agreeing Flux pin passes and a real disagreement refuses; pricing/threat are named as un |
| `platform/verify-certificate-identity-regexp.sh` | False | release.yml's EXPECTED_IDENTITY_REGEXP, read straight out of the workflow file (:13), accepts this repo's main and release/<major>.<minor>.x and rejects six foreign-org/foreign-path/unanchored variant |
| `platform/verify-cut-release-tags.sh` | False | Against a real scratch git repo and a real local bare remote, running the SAME .github/scripts the workflow runs: the single-tag legacy form works; multi-tag lands every tag on one commit; the existin |
| `platform/verify-publisher-gate.sh` | False | Intends: a real gate refusal and a real pass computed by gate.run_gate() against the real committed v2.0.0/v3.0.0 trees plus one disclosed Audit->Deny mutation (Part A, :107-155); cut-release-gate.py' |

**Notes:** Scope note: the task's "original-org cluster" paragraph does not apply here — this is the platform publisher repo, not the original-org one. Commit dates reported anyway. Per-path last commits: README.md and shift-left/ 2026-08-23 (e34ae7f, cs-15 repair release); engine/ 2026-08-20 (66a7bf0); verify-certificate-identity-regexp.sh 2026-08-22 (379aade); verify-cut-release-tags.sh 2026-08-23 (f5c0461); policy/ 2026-08-24 (586db39, cs-16) and verify-publisher-gate.sh 2026-08-24 (860e744); distribution/ 2026-08-25 (2b69a6a, ADR-0014 guard); party/ 2026-08-25 (963872b, a commit self-described as "WIP: uncommitted policy-composition tickets 09-16 work, safety commit"); .github/ 2026-08-25 (76a5737, backfill mode). Repo HEAD 58ef9c5 2026-08-25.

Six-org estate references INTO this cluster are real and load-bearing, not decorative. driftwood, ludlow and tuppence each (a) pin platform by {tag, commit} in gitops/platform/platform-pin.yaml with a Renovate customManager maintaining the pair, (b) run platform/shift-left/ci-check.py cross-org in their own shift-left.yml with platform checked out AT THE PINNED TAG and the resolved commit verified against the pin, (c) run platform/party/party_artefact.py check against their own party.yaml, (d) verify platform's cs-27 signed evidence identity-pinned in their adopter gate, and (e) carry composed/orphan-guard.yaml and composed/governed-namespace-guard.yaml regenerated from this cluster's offline twins, with allow-lists matching versions.yaml exactly. ico and nist do not reference this cluster (nist is referenced BY it, as the controls parent).

Four findings a drift review should weigh, in severity order. (1) verify-shift-left.sh fails today and it is release.yml's release gate: cs-16 inserted 2.0.1 into the array, pushing 3.0.0 out of 2.0.0's ±1 window, so the Audit->Deny flip fixture is no longer caught; wargamer/propose-policy-pr.sh breaks on the same cause. (2) The ResourceSet fan-out — the central mechanism of the distribution area — has never been reconciled anywhere; the reachable cluster carries hand-applied policies for versions no longer in the array. (3) The offline twins and the live ResourceSet render disagree on the platform-machinery identity label, with nothing comparing them, despite the twins being documented as what flux-operator would render. (4) verify-coexistence.sh's "optional" live tail turns an offline-green beat red on any reachable cluster, and verify-retirement.sh's live branch prints a pruning claim it cannot support.

Honesty texture worth recording: this cluster is unusually candid where it is thin. render-and-prove.py:22-30, verify-governed-namespace-guard.sh:4-22, verify-publisher-gate.sh:26-43, party_artefact.py:26-35 and cut-release-create-tags.sh:7-11 each name exactly what is simulated and why, in prose, before the code does it. The gaps found above are mostly places where that discipline lapsed (a stale note, a mislabelled twin, a live branch that asserts rather than reports), not places where it was absent.

Not run to completion: verify-publisher-gate.sh (~28 min, killed) and verify-conditional.sh. Every other verify script in this cluster was executed on this machine and its exit code is recorded above. JSON written to /private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/417e2917-726b-46c9-9117-7b880114f08b/scratchpad/codemap/estate-platform-distribution-policy-engine.json

