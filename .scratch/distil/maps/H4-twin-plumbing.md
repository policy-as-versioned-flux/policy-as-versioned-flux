# H4 - The hub twin's plumbing, substrate and command line

Area: `FRESH/hub/twin` (FRESH = `fresh`), 38 files, 19,947 lines (wc -l). Paths below are relative to `hub/twin/` unless prefixed.

## Summary

- 19,947 lines in 38 files; 35 of the 38 files were born in August 2026 (5-29 Aug), three in September (strict_yaml 09-09, corpus_size 09-22, synthetic 09-26). Per-file `git log -1` over all 38: 36 files have not changed since 2026-09-26 or earlier (fixtures 2026-08-29). Two were edited in October: `gameplay_lens.py` (2026-10-26, 41ac7b3f, +24/-1, "State the actual basis in all six skill evaluations") and `substrate_generator.py` (2026-10-30, a00ad91e, +49/-6, "Require actual distinct substrate plant witnesses"). Author is the owner on every commit; the unnumbered imperative subject style differs from the September "Ticket N:" style, which is consistent with Codex but does not prove it. The area is otherwise a frozen August-September build.
- Only Q has code here: `price`, `exposure`, `options`, `severity*`. T (tolerance), C (compare), R (ratchet) and E (enact) have no verb in this area. The word "appetite" here means an evidence-grade pricing threshold, not money (`schema.py:290`, `evidence.py:51-58`). `propose` only writes a proposal and carries no rung and no £ reduction (`enact.py:292-321`). Where those steps live, per `verify/pound-seam/pound_seam.py:30,39-40,46-49`: the adopter's appetite is a signed fact on its own party.yaml; `platform/graded/cage.py` and the adopter's selection-policy package pick the rung; the served total carries the aggregate of its selected-tier residuals "beside the one tolerance the appetite declares", the only compare found, and it is outside this area.
- The twin refuses the C step by design: no organisational total exists (`schema.py:125,558` refuses any authored `total`/`aggregate` key; `verbs.py:630-631` "A single organisational price is the collapse this system refuses"; `verbs.py:673` a scenario "has no single figure").
- 47 CLI verbs. CI runs `verify`, `fixture`, `run`, `score` directly (`.github/workflows/twin.yml:38,123-129`) and, through `demo.sh` and `beat-sequence.sh` (`twin.yml:87,93`), 30 distinct verbs in all (grep of `"$TWIN" <verb>` over the five scripts), every one against fixture repos built by `twin fixture`. The other 17 are untouched by CI. No workflow runs any verb against an adopter's model repo; `price`, `options`, `propose`, `sense` run only on fixtures.
- The only recorded live use of anything here is the three adopters' `twin/emit-forward-intel.py`, which imports `twin.repo`, `twin.schema.CAUSAL_EDGE`, `twin.fixtures.git` and `LIBRARY_WORLD_FILES`, never `cli` or `verbs`. Its daily "twin sweep" in driftwood logged 39 observations (2026-09-05 to 2026-10-22), all `moved: false`, none since.
- `fixtures.py` is 5,951 lines (30% of the area); production touches about 280 of them (the `git()` helper and the library world layer).
- Kernel for the loop in this area: none. The twin is an optional input to the platform's £ engine (`pound_seam.py:11`: a twin entry exists only when the adopter publishes a forward-intel feed).

## Components

Origin rule used throughout: git author is the owner on every commit and says nothing. `delegated` only for files born after ADR-0025 (2026-09-02, `docs/adr/0025-the-assistant-decides-architecture-and-records-it.md`). `owner_words` only with a dated quotation. Everything else `assistant`; ambiguity listed in the structured `could_not_determine`.

| # | name | paths | lines | born | what it does | loop role | necessity | origin | status | cite |
|---|------|-------|------:|------|--------------|-----------|-----------|--------|--------|------|
| 1 | fixture: flagship default + git helper | fixtures.py:1-1038 | 1038 | 2026-08-05 | Builds a deterministic git model repo (fixed dates, `git()`, `build()`, `advance_world()`), toy Netflix+Intel overlay, behavioural overlay | evidence | support | assistant | tested_offline (the `git()` helper observed_running in adopters) | fixtures.py:914-972; driftwood/twin/emit-forward-intel.py:143-146 |
| 2 | fixture: library world layer (vendored by adopters) | fixtures.py:3698-3939 | 242 | 2026-08-12 (blame of fixtures.py:3698; made public 2026-08-29, eco ticket 29) | Tenant-free world layer (scenario classes, components) that each adopter copies into its own repo | quantify | support | assistant | observed_running | fixtures.py:3698-3706; driftwood/twin/VENDORED.md:16 |
| 3 | fixture: pocket org + defect plants | fixtures.py:1039-1635 | 597 | 2026-08-11 (blame of fixtures.py:1039) | Tiny org whose numbers are hand-computed, plus helpers that plant a recalibration, unrecorded regrade, enforcement move or world violation so checks can be seen to fail | evidence | support | assistant | tested_offline | fixtures.py:1039,1426,1452-1635; worksheet.py:1-12 |
| 4 | fixture: backtest answer keys | fixtures.py:1636-2885, 2886-3279, 4204-4496, 5613-5951 | 2276 | 2026-08-05 | Regime test org plus nine real-firm collapses or decisions (Carillion, NMC, Wirecard, Enron, AstraZeneca, Sanofi, Royal Mail, Kodak, Maersk) as YAML inside Python strings, to score a forecaster against known outcomes | none | off_mission | assistant | tested_offline | fixtures.py:1849,2180,2393,2636,2886,3081,4204,5613,5785; .scratch/twin/issues/12-synthetic-substrate.md:63,101 |
| 5 | fixture: Netflix + Intel demo subjects | fixtures.py:4497-5612 | 1116 | 2026-08-05 | The two full "flagship" orgs: dated SEC-filing spine, causal edges, rival causal accounts, pricing, corroborated enactment | presentation | off_mission | assistant | tested_offline | fixtures.py:4497-4600,4779,5053,5170; twin/beat-netflix.sh |
| 6 | fixture: twin-self org + library overlay | fixtures.py:3280-3697, 3940-4203 | 682 | 2026-08-05 | An org that models the twin's own threats; an overlay that exists to be swept; `build_standing_library` | ceremony | off_mission | assistant | tested_offline | fixtures.py:3280-3330,4168-4180 |
| 7 | CLI: wiring, parser, refusal table | cli.py:1-80, 1663-2141 (imports, `_say/_emit/_open`, `build_parser`, `main`) | 559 | 2026-08-05 | Defines 47 verbs, shared flags, turns known exceptions into one-line refusals | none | support | assistant | tested_offline | cli.py:1663-2127; tests/test_seam1_cli.py (720 lines) |
| 8 | CLI: quantify, causal and rewind handlers | cli.py handlers sense, run, score, price, exposure, options, severity, severity-anchor, constraints, propose, blast, propagate, intervene, observe, rewind, backtest, graph, map, affected-parties | 479 | 2026-08-05 | Prints and emits artefacts for the verbs that price a shock, filter and cost responses, propagate a shock, bind a signal | quantify | support | assistant | tested_offline (CI exercises most of these verbs through the demo scripts, on fixtures only) | cli.py:132,535-580,693-775,895-927 |
| 9 | CLI: forecast, calibration, schedule and drift handlers | cli.py handlers unbound-pool, retrospective-sweep, scenario-diff, regimes, positions, credibility, causal-accounts, trade-off, sweep, gameplay-sweep, reliability, drift | 283 | 2026-08-05 | Verbs about forecasting quality, rival maps, scheduled sweeps and the Flux drift measurement | react | off_mission | assistant | tested_offline (the demo scripts call `sweep`; no adopter workflow does) | cli.py:89-131,159-264,375-422,581-644 |
| 10 | CLI: governance, publication, validation handlers | cli.py handlers does-not-do, demo-slice, ontology, enforcement, disparate-impact-*, challenge, resolve-challenge, worksheet, validate, index, substrate, fixture | 429 | 2026-08-05 | Publishes the twin's self-description, handles contestation of artefacts, validates a model repo, emits the substrate report | ceremony | ceremony | assistant | tested_offline | cli.py:776-860,928-1045,1072-1275 |
| 11 | CLI: verify, sign, reproduce, rehash, bless, grade | cli.py:1262-1660 region (cmd_verify, _attestation, cmd_sign, _reproduce, _rehash, _bless_goldens, cmd_grade, _split_manifest...) | 391 | 2026-08-05 | Runs the invariant suite, checks sidecars, signs authored artefacts, re-pins check hashes and golden digests | evidence | support | assistant | tested_offline (CI-wired, run record not read) | cli.py:1312-1660; .github/workflows/twin.yml:38,120,325 |
| 12 | verbs: price, exposure, options, severity | verbs.py:544-576, 577-662, 663-902, 1469-1548 | 439 | 2026-08-11 | Prices one shock under every perspective with response costs and mitigation credit; values a scenario per perspective; pre-filters then costs options; lognormal+GPD loss-exceedance curve | quantify | support | assistant (nearest owner quote asks for proportionality, which pound_seam checks, not verbs.py: NORTH-STAR.md:55) | tested_offline; not on the live path | verbs.py:577-646,663-700; NORTH-STAR.md:55 |
| 13 | verbs: run, score, positions, credibility, trade-off, reliability | verbs.py:903-1028, 1029-1111, 1112-1225, 1226-1468 | 566 | 2026-08-11 | Executes a scenario to forecasts; scores forecasts against outcomes (Brier/log loss); rival maps; blended priors; net cost per response across causal accounts | react | off_mission | assistant | tested_offline (CI runs `run` + `score` on the Netflix fixture only) | verbs.py:903,1226; .github/workflows/twin.yml:127-129 |
| 14 | verbs: sense, graph, blast, propagate, intervene, observe, rewind, header | verbs.py:1-178, 179-287, 288-348, 349-488, 489-543, 1549-1559 | 554 | 2026-08-11 | Binds a dated signal to a component; builds the typed graph; traverses downstream; do()/observe(); model state at a past time | quantify | support | assistant | tested_offline | verbs.py:179,288,349,373,472,489 |
| 15 | schema: closed typed schema | schema.py | 1149 | 2026-08-11 | Closed validators for every file in a model repo: valuation, PERT money triples, evidence grades, causal edges, mitigation, enforcement, GDPR Article 9 denylist, authored-roll-up refusal | quantify | support | assistant | observed_running (CAUSAL_EDGE imported by adopters; loaded on every Overlay.load) | schema.py:188-330,433-450,558-577,623-890; driftwood/twin/emit-forward-intel.py:101 |
| 16 | repo: pinned model repository | repo.py | 400 | 2026-08-05 | Opens a git repo at a ref and reads through the tree, refusing a dirty working tree | evidence | support | assistant | observed_running | repo.py:1-14; driftwood/twin/emit-forward-intel.py:100,342 |
| 17 | envelope, canonical JSON, strict YAML | artefact.py, canon.py, strict_yaml.py | 258 | 2026-08-05 (strict_yaml 2026-09-09) | Artefact envelope (pins, authored/derived mark), canonical serialisation, a YAML loader that refuses duplicate keys | evidence | support | assistant (strict_yaml.py alone is delegated: born 2026-09-09, after ADR-0025) | tested_offline (artefact and canon in the adopter closure) | artefact.py:1-8; canon.py:1-8; strict_yaml.py:1-12 |
| 18 | blob refs and derived index | blob.py, index.py | 149 | 2026-08-05 | Content-hash references for bulk synthetic substrate; a rebuildable per-unit index | none | off_mission | assistant | tested_offline (index imported by cli only) | blob.py:1-8; index.py:1-6 |
| 19 | reproduce: recompute an artefact from its pins | reproduce.py | 286 | 2026-08-06 | Re-derives an artefact and its chain and compares bytes | evidence | support | assistant | tested_offline | reproduce.py:1-30; cli.py:1460 |
| 20 | substrate: recipe, generator, spine, ingest | substrate.py, substrate_generator.py, spine.py, ingest.py, netflix-substrate-recipe.yaml | 830 | 2026-08-11 | Seeded generator of synthetic company email/chat/commit corpora with planted weak signals, anchored to a dated spine, plus automated STEEP-tag and bind at volume | none | off_mission | assistant (resolved in an owner grilling 2026-08-04, issue 01 "Answer"; no verbatim quote) | tested_offline; substrate_generator.py edited 2026-10-30 (a00ad91e, +49/-6) | .scratch/twin/issues/01-subject-and-purpose.md:30-40; substrate.py:1-20; ingest.py:1-20 |
| 21 | substrate: fidelity eval, report, planter | substrate_eval.py, substrate_report.py, planter.py | 831 | 2026-08-13 | Measures seven fidelity dimensions of the synthetic corpus, scores a detector against sealed plants, emits both in one artefact via `twin substrate` | none | off_mission | assistant | tested_offline | substrate_eval.py:1-20; planter.py:1-25; cli.py:1220 |
| 22 | synthetic: "a synthetic record never raises a grade" | synthetic.py | 197 | 2026-09-26 | Marks a record synthetic and lets `pricing`/`verbs` refuse to price anything resting on one | quantify | support | delegated (ADR-0032, eco ticket 141) | tested_offline | synthetic.py:1-30; docs/adr/0032-... |
| 23 | corpus_size: items a threshold needs | corpus_size.py | 98 | 2026-09-22 | Derives the minimum labelled-item count for a skill threshold; on the live path only through `skills.py` | ceremony | ceremony | delegated (ticket 112) | tested_offline | corpus_size.py:1-12; skills.py:31 |
| 24 | Wardley maths and gameplay lens | wardley.py, gameplay_lens.py | 565 | 2026-08-06 | Evolution-stage bands and D/K/R relations ported from arckit; scans the map for strategic play preconditions | none | off_mission | assistant | tested_offline; gameplay_lens.py edited 2026-10-26 (41ac7b3f, +24/-1) | wardley.py:1-30; gameplay_lens.py:1-20; tests/test_wardley.py, tests/test_gameplay_lens.py |
| 25 | self-description artefacts | ontology.py, demo_slice.py | 371 | 2026-08-18 | Publishes the ontology generated from schema.py and the demo slice's thesis/boundary/AC map | presentation | ceremony | assistant | tested_offline | ontology.py:1-20; demo_slice.py:1-20 |
| 26 | pocket-org worksheet check | worksheet.py, pocket-org-worksheet.md | 825 | 2026-08-06 | Hand-computed expected numbers for the pocket org, parsed and compared to emitted artefacts | evidence | support | assistant | tested_offline | worksheet.py:1-25 |
| 27 | schedule sweep and scenario diff | schedule.py, scenario_diff.py | 270 | 2026-08-10 | `sweep()` runs every scenario of every org unconditionally; `scenario-diff` renders two git refs of a scenario as a map-diff | react | off_mission | assistant | tested_offline (no adopter workflow calls `twin sweep`) | schedule.py:1-20; scenario_diff.py:1-15; driftwood/.github/workflows/twin-sweep.yml:67-70 |
| 28 | demo and beat scripts | demo.sh, beat-intel.sh, beat-netflix.sh, beat-royal-mail.sh, beat-sequence.sh, __main__.py | 809 | 2026-08-05 | Walks sense, run, score then four narrated "beats" for a demo, offline | presentation | off_mission | assistant | tested_offline (CI-wired) | demo.sh:1-12; .github/workflows/twin.yml:87,93 |
| 29 | README | README.md | 3210 | 2026-08-12 | Status ledger and per-capability prose ("What is honestly built" 2184-2598, "What is not built" 2846-3128) | ceremony | ceremony | assistant | unknown | README.md:1-25,2184,2846 |
| 30 | self-versioning | RELEASE.md, VERSION | 48 | 2026-08-29 | Releases the twin as `twin/v0.1.0` so adopters can pin it | ceremony | support | assistant (eco ticket 29) | observed_running (tag cut 2026-10-23; driftwood/twin/PIN.yaml `tag_cut: true`) | RELEASE.md:1-20; driftwood/twin/PIN.yaml |

Sum of component lines: 19,947 (computed by script from the table). `born` is the file's birth date (`git log --diff-filter=A`), except rows 2 and 3 where the slice's first line was blamed.

## CLI verbs (47, counted by `grep -c 'subs.add_parser(' cli.py`)

Mark: **HAND** = a person needs it to run the loop once by hand. Loop step in brackets; "-" means it does not serve a step of Q T C R E X.

| verb | one line | loop | HAND |
|------|----------|------|------|
| sense | bind a dated signal to a component through a committed claim | X (input only; does not re-price) | HAND |
| unbound-pool | signals that bind nowhere, kept with decay | - | |
| retrospective-sweep | rebind pooled signals after a model change, report lead time | X (weak) | |
| run | execute a scenario at a declared time under a named information regime; emits forecasts | - | |
| scenario-diff | two git refs of a scenario rendered as a map-diff | - | |
| regimes | one scenario under all three regimes, with the two gaps | - | |
| price | one shock priced in £ per declared perspective, with response costs and mitigation credit, no ranking | Q, part of R | HAND |
| drift | the Flux drift measurement so far, no verdict | - | |
| positions | believed map vs rival forecasts vs revealed truth, with deltas | - | |
| credibility | blend a world-layer prior with an org's own sparse data | Q (weak) | |
| causal-accounts | rival causal accounts, each propagated, with the spread | Q (weak) | |
| trade-off | net cost of risk per response across rival accounts, marked default | Q/R (weak) | |
| score | score a forecast bundle against a recorded outcome | - | |
| sweep | run every scenario of every org across repos, unconditionally | X (never invoked by a workflow) | |
| gameplay-sweep | scan every org for strategic play preconditions | - | |
| reliability | calibration diagram over a pool of score cards | - | |
| severity | loss-exceedance curve from declared lognormal+GPD parameters | Q | optional |
| severity-anchor | the same curve fitted from cited public quantiles | Q | optional |
| graph | emit the typed knowledge graph | Q (input) | |
| map | render the Wardley map from the graph | - | |
| blast | what is downstream of a component, which part may be priced | Q (input) | |
| exposure | a scenario valued per perspective from declared valuations, a spread not a total | Q | HAND (alternative to price) |
| propagate | compose a shock along causal edges with depth attenuation | Q (input) | |
| intervene | do(x): cut incoming edges, propagate downstream | - | |
| observe | observe(x): update belief about causes too | - | |
| rewind | model state at a past time | - | |
| backtest | rewind then run | - | |
| options | choice set after the constraint pre-filter, survivors costed | R (candidates only) | HAND |
| constraints | publish the legal/ethical floor, exclusions, pricing gate | cage (floor) | |
| does-not-do | register of unchecked capability criteria | - | |
| demo-slice | the demo slice's rendered artefact | - | |
| ontology | the schema's vocabulary as an artefact | - | |
| affected-parties | who bears a modelled consequence with no perspective | - | |
| enforcement | the enforcement rungs and move record | cage (rungs), no £ | |
| propose | write a proposal to enact a response via one of two channels; disposes of nothing | E (proposal text only) | HAND |
| disparate-impact-audit | raise a sealed disparate-impact finding | - | |
| disparate-impact-respond | close such a finding as the registered role | - | |
| challenge | dispute one claim in one artefact | - | |
| resolve-challenge | resolve a challenge | - | |
| validate | validate every object in a model repo against the closed schema | support | HAND |
| index | build the derived index | - | |
| substrate | fidelity bands and planted-signal scoring for a substrate recipe | - | |
| fixture | build a deterministic fixture model repository | support (to have something to run on) | HAND (unless you have a model repo) |
| worksheet | check the pocket org against its hand-computed worksheet | evidence | |
| sign | sign an authored artefact as a role | evidence | |
| grade | show computed depth grades | - | |
| verify | run the invariant suite, or recompute an artefact from its pins | evidence | HAND (to trust the result) |

By hand, once: `fixture` (or author a model repo) -> `validate` -> `sense` -> `price` (or `exposure`) -> `options` -> `propose` -> `verify <artefact>`. That is 7 of 47 verbs. Steps with no verb here: T (tolerance), C (compare exposure to tolerance), R (choosing a rung), E (changing a running system). The person must do T and C by eye, and R and E elsewhere (platform selection policy; the reviewed-PR route outside `twin`).

## What the loop would lose if this area vanished

- The adopters' forward-intel emitters would stop: they import `repo.py`, `schema.py` (CAUSAL_EDGE and the valuation/edge validators through `Overlay.load`), `artefact`/`canon`/`wardley` transitively, `fixtures.git` and `LIBRARY_WORLD_FILES` (import closure of `evidence, fixtures, model, repo, schema, valuation` restricted to this area: artefact, canon, corpus_size, fixtures, repo, schema, wardley).
- Beyond that, nothing the loop needs. The platform's £ engine and tier selection run without a twin entry (`pound_seam.py:11` says a twin entry exists only when a forward-intel feed is published). The tolerance, compare and rung logic are not in this area (`pound_seam.py:39-49`: cage.py and the selection policy pick the rung; the composer shows residuals beside the appetite's tolerance).
- Lost with it, but not by the loop: the 47-verb CLI, ten historical answer keys, the synthetic substrate chain, the beats and the README.

## The simplest thing that would do this area's loop job

The loop job of this area is Q: state the exposure from a perspective's declared valuations and the evidenced causal path to them, and say which responses reduce it. Concretely:

- One file `twin/price.py` (about 250 lines): load one YAML (perspective's cash-flow valuations as min/mode/max £ triples, causal edges with an elasticity triple and evidence grade, responses with a cost triple and a mitigation fraction); keep the two rules that earn their lines (a valuation below the evidence threshold is a register entry with no amount; a synthetic basis never prices); emit one JSON with the exposure as a PERT mean and a p90, the weakest grade it rests on, and each response's reduction.
- Keep `repo.py` (400 lines, reads through the git tree) or replace it with `git show <ref>:path` (about 30 lines).
- Keep the pocket org (413 lines) and its hand-computed worksheet as one 100-line test.
- A 40-line `twin/compare.py` that the area lacks: exposure vs appetite (read from the adopter's party.yaml) and print "within" or "over by £X".
- That is about 800 lines against 19,947 (4%). Delete: the other 40 verbs, the substrate chain, nine answer keys, the beats, the Wardley gameplay layer, the README ledger.

## Surprises

1. The area states the opposite of the owner's compare step. `schema.py:125,558-577` refuses any authored key named `total`, `aggregate` or `subtotal`; `verbs.py:630-631` says a single organisational price "is the collapse this system refuses: there is no such thing"; `verbs.py:673` says a scenario "has no single figure". A figure for an organisation to hold against a tolerance cannot be produced here.
2. "appetite" in the twin is `appetite.pricing_threshold: 2|3`, an evidence-grade gate (`evidence.py:51-58`, `schema.py:290`). Zero occurrences of a monetary tolerance in the 38 files (grep of `tolerance|appetite` over every `.py`, the README, the worksheet and the five shell scripts: the README's two hits are `appetite.pricing_threshold` and a "zero-tolerance band (0.0, 0.0)" on a fidelity metric). The only other hit, `enforcement.py:233`, is a prose phrase ("a residual over the appetite band") in a rule string for a ladder that carries no number.
3. The twin's recorded commission is breadth: `.scratch/twin/issues/01-subject-and-purpose.md:45-56` ranks purposes "personal magnum opus > shippable product > research > persuasion", "no external gate lowers the bar", and a success bar of every signal class modelled end to end. The same file asks for a "recommended cheapest proportionate response" (line 56); the code that was built emits `not_a_ranking` (`verbs.py:642`).
4. CI exercises 30 of 47 verbs, all on fixture repos built by `twin fixture`, and none against an adopter's model repo; the adopters' only live twin step is a Python emitter that never touches `cli.py`. `cli.py` reaches 63 of the twin's 106 modules, and nothing imports `cli` except `__main__`.
5. The "twin sweep" in driftwood is not `twin sweep`. Its own comment says so: "the sweep is the forward-intel re-render, the only twin output this repository has today" (`driftwood/.github/workflows/twin-sweep.yml:67-70`). 39 daily observations, 2026-09-05 to 2026-10-22, `moved` true 0 times. `verify-twin-sweep-moved.sh:11-13,168` treats the moved path as unproven until a line with `"moved": true` exists, so that half is a could-not-look. No twin-sweep observation after 2026-10-22 although driftwood committed on 2026-11-13 (20 drift-sample commits since 2026-10-23); the reason is not in the files read. `twin-sweep.yml` itself was edited 2026-10-23 (120a48c "Adopt signed twin and recovery shadow feed") and 2026-10-24 (5bc9718 "Resolve signed twin tag"), the two days after the last observation.
6. `fixtures.py` (5,951 lines) is imported by production only for `git()` (`emit-forward-intel.py:143-146`, also in tuppence and ludlow) and `LIBRARY_WORLD_FILES` (driftwood/twin/VENDORED.md:16). 2,276 lines are answer keys for firms that failed; 1,116 more are two demo subjects.
7. The substrate chain (1,661 lines, components 20-21) was extended on 2026-10-30, after the calibration programme began: `substrate_generator.py` in this area (a00ad91e) plus `substrate_candidate.py`, `substrate_generation.py`, `substrate_recipe_basis.py` outside it (b1f5e325, 1ed746fa). The programme builds on a chain this map classes off-mission. `gameplay_lens.py` also got an October edit (41ac7b3f).
8. `README.md` (3,210 lines) is nearly as long as `cli.py` and `verbs.py` combined (3,700); its banner counts build tickets ("88 of 92 build tickets closed", README.md:10) rather than anything about the loop.
