# Map: `twin/` — the org digital-twin package

Scope covered: `twin/*.py` (76 files, excl. `__pycache__`), `twin/invariants/`, `twin/capabilities/*.yaml`
(13 files), `twin/*.yaml` (15 root fixtures/tables), `tests/*.py` (81 files), `bin/twin`,
`.github/workflows/twin.yml`, and driftwood's `twin/` overlay
(`…/scratchpad/units/driftwood/twin/`). Read `twin/README.md` in full (3,167 lines — it is the
package's own running honesty ledger) plus `RELEASE.md`, `VERSION`, `ENACT_MODE`, and the relevant
`.scratch/twin/build/*.md` tickets. **Not read in full**: `twin/fixtures.py` (5,951 lines — sampled
by function/grep, not line-by-line), `twin/cli.py` (2,133 lines — sampled), `twin/verbs.py` (1,520
lines — docstring + grep only), `twin/model.py` and `twin/schema.py` (795/1,101 lines — sampled).
Every quantitative claim below (LOC, test counts, capability grades) was independently recomputed
from the tree, not copied from README prose, per the note in "Counts" below.

## Counts

```
twin/*.py (excl. __pycache__, incl. invariants/):  33,872 lines  [wc -l twin/*.py twin/invariants/*.py]
  twin/*.py alone:                                 27,572 lines
  twin/invariants/*.py alone:                       6,300 lines
  twin/fixtures.py alone:                           5,951 lines  (largest module by far)
  twin/cli.py:                                      2,133 lines
  twin/verbs.py:                                     1,520 lines
tests/*.py:                                         18,623 lines across 81 files
  test functions (grep '^def test_'):                1,326
twin/capabilities/*.yaml:                              13 files
twin/*.yaml (root, non-capability tables/fixtures):    15 files
invariant checks:
  twin/invariants/checks.py — 16 hash-pinned "constitutional" checks (manifest.yaml)
  twin/invariants/harness.py — 58 @harness_check-decorated build-ticket guards
  → ~74 distinct invariant checks `bin/twin verify` can run (README's last self-reported run: "70 pass, 2 fail,
    2 skipped" — see "Known red" below; the 74 figure is my own count of decorated/registered functions today,
    not reconciled against that older narrative number)
```

I ran `PYTHONPATH=. python3 -P -m twin grade` locally (read-only, no network, no cluster —
permitted) rather than trust README prose:

```
==> aggregate: 73 of 73 across 13 capabilities, 13 at `full`
```

All 13 capability files are `full` (every acceptance criterion of their owning decision ticket
checked), **and this is a live-validated number, not typed**: `twin/grades.py`'s `_load_one` refuses
to load a capability file that types a `grade:` key by hand, and `_validate_against_ticket` refuses
to load one whose checklist text or count has drifted from the actual `## Acceptance criteria`
section of its owning ticket under `.scratch/twin/issues/` (`twin/grades.py:150-188`). A tick also
requires non-empty `evidence` and `ticked_by` fields or the loader refuses it
(`twin/grades.py:159-164`) — "a tick with no witness is a self-declared grade." This is a genuinely
enforced anti-gaming mechanism, not a policy statement.

README's own last full audit (`twin/README.md:2637-2645`) states `bin/twin verify` — 70 pass, 2
fail, 2 skipped, 0 pending; `pytest -q` — 1,536 tests, 1,535 pass. The two failing invariants are
named and explained as **expected, not defects**: `drift_window_is_actually_being_sampled` (a
live-cluster probe-staleness check, red between samples) and `flux_coverage_floor_is_still_reachable`
(red since 2026-08-16 and staying red until the 91-day window closes on 2026-11-06 — see "Flux
verdict" below). I did not re-run `bin/twin verify` myself (it needs `clone-estate.sh`, a network
fetch, out of scope for read-only review) so I cannot independently confirm today's pass/fail count;
I can only confirm the two named failures are structurally expected given what `drift.py`/`verdict.py`
implement (see below).

---

## 1. Model / ontology (`model.py`, `ontology.py`, `schema.py`, `repo.py`, `primitives.py`, `canon.py`, `index.py`)

**What it is.** `repo.py` (400 lines) opens a model repository strictly through a **git tree
object**, never the working tree — `ModelRepo.open()` refuses a dirty tree, which is what makes
`rewind` (below) and `identical_pins_identical_bytes` possible at all. `model.py` (795 lines) is the
typed graph: a **world layer** (components, propositions, world models) that may never reference an
org's **overlay** (signals, claims, scenarios, outcomes) — enforced by the live invariant
`world_never_references_overlay` (`twin/invariants/checks.py:673`). `schema.py` (1,101 lines) is the
closed typed schema for every object kind (components, edges, claims, signals, scenarios, outcomes,
perspectives, responses…) — closed meaning an unrecognised field is a load-time refusal, which is
the mechanism `no_special_category_slot` and `no_recommended_action_field` ride on (there is no slot
to smuggle a forbidden field into). `ontology.py` (177 lines) generates the named core ontology
**from `schema.py`'s own vocabulary** (`twin ontology --out F`) rather than a hand-maintained second
document. `primitives.py` (267 lines) gives `do()`/`observe()`/`rewind()` distinct types so a swap
between intervention and observation is a `mypy` error. `canon.py`/`index.py`/`blob.py` are plumbing
(canonical JSON serialisation for hashing, a derived non-authoritative index, content-hash blob
refs).

**Real computation vs lookup.** This layer is genuine graph/schema machinery, not a lookup table —
it is the substrate everything else sits on. `index.py`'s own docstring is explicit that it is "a
store, and therefore never authoritative" (i.e., always rebuildable, never a second source of
truth).

**Tests.** `tests/test_seam2_model.py`, `test_seam2_propagation.py`, `test_ontology.py`,
`test_schema.py`, `test_repo_and_envelope.py`, `test_primitives.py` (the last also proves
`sense()`'s upstream/downstream distinction against real fixture data —
`test_sense_reaches_an_ancestor_the_same_component_intervention_would_not`,
`twin/README.md:2712-2714`-adjacent per capability file `sense-move.yaml`).

## 2. Pricing / severity / tail (`pricing.py`, `severity.py`, `severity-anchors.yaml`, `anchoring.py`, `pert.py`, `admission.py`, `options.py`, `constraints.py`/`.yaml`, `evidence.py`/`evidence-ladder.yaml`)

**What a price is, mechanically:** `price at C = perspective's declared valuation of C × propagated
influence at C` (`twin/pricing.py:9`). Deliberately **no separate authored severity slot** on a
component — the docstring names the reason: two authored magnitudes under one eye let an author
launder a price through whichever is watched less.

**Real computation.** `severity.py` (215 lines) is genuine closed-form statistics: a lognormal body
spliced continuously to a Generalised Pareto Distribution tail at an authored peaks-over-threshold
cut, with TVaR in closed form (McNeil & Frey 2000) and an explicit refusal when `xi ≥ 1` (tail mean
does not exist) or when the requested confidence lands inside the lognormal body rather than the
declared tail (`twin/severity.py:159-175`). This is real, checkable maths, not a table.

**Lookup / honestly-marked-unfit-for-purpose parameters.** `twin/severity-anchors.yaml` anchors
**2 of 4** GPD parameters from real cited sources (Cyentia Institute IRIS 2025, two quantiles,
fit by closed-form two-point calibration — `twin/severity-anchors.yaml:39-54`) and explicitly marks
the other two (`xi`, `beta` — the tail shape and scale) `anchored: false` with an `illustrative_value`
and a stated reason ("no public source in this file's reading list reports a fitted GPD shape
parameter for cyber-loss severity" — `twin/severity-anchors.yaml:55-80`). This is disclosed, not
hidden — the invariant `unanchored_severity_parameters_are_marked` exists specifically to keep it
disclosed (`twin/invariants/harness.py:3000`).

**Standalone, not wired to any price.** README states directly: "nothing in `twin price` or the
pocket org calls it… its own TVaR is tail-only" (`twin/README.md:2836-2843`). Severity is a real,
tested capability that produces no number anyone's price actually uses yet.

**The pre-filter (`options.py`, 310 lines).** Removes candidate responses that cross a constraint
**before** any pricing happens — the ordering is structural: the pre-filtered product **re-derives
the filter from the constraint set it carries and refuses if the answer disagrees**
(`twin/README.md:184-193`), because a construction sentinel alone survived `dataclasses.replace`
unmodified once and that was the exact "innocent refactor" that would have defeated the lock.
Invariant: `prefilter_precedes_pricing` (`twin/invariants/harness.py:1182`).

**Admission (`admission.py`, 121 lines).** An impact enters the £ only via a causal path to a
**declared cash flow**, graded inside a published threshold — two exceptions named honestly: (1) a
component named *as* the cash flow itself is admitted with zero evidence (the one route by which a
figure enters with nothing behind it, and it is subtotalled **separately** from derived figures so
the two are never summed silently — `twin/admission.py:16-27`); (2) mitigation credit additionally
requires **corroborated enactment**, not just a graded claim (`twin/pricing.py:41-46` — closing a
classic "the incident didn't happen because of our control" unfalsifiability loophole).

**Tests.** `test_severity.py` (incl. `test_a_var_shaped_summary_hides_what_tvar_surfaces`),
`test_pricing.py`, `test_admission.py` (via `test_pert.py`/pricing chain), `test_use_gating.py`,
`test_scenario_selection_tiers.py`.

## 3. Forecasting / scoring / forecast_book (`scoring.py`, `forecast_book.py`, `verbs.py::run/score`, `regimes.py`, `benchmark.py`, `market_signals.py`)

**Scoring rules are real, proper scoring rules.** `scoring.py` (167 lines): Brier and log-loss, both
losses (lower is better), each refusing a probability not strictly in (0,1) because "a claim of
certainty carries an infinite log-score penalty" (`twin/scoring.py:41-46`). Rounded to 12
significant digits specifically because `math.log` is not correctly-rounded cross-platform and
would otherwise break `identical_pins_identical_bytes` (`twin/scoring.py:22-31`).

**Three information regimes (`regimes.py`, 350 lines), and `twin run` has no default regime** —
an omitted flag would be a silent claim to have run under the honest gate (`twin/README.md:270-273`).
`as-consumed` (only what was ingested by T) vs `as-knowable` (dated ≤T regardless of ingestion) vs
`with-hindsight` (unrestricted). The gap between the first two localises to **sensing**; between the
second two, to **interpretation**; a residual that stays zero under all three localises to the
**model** and is reported as **not computed** rather than a misleadingly reassuring zero
(`twin/README.md:293-299`).

**`forecast_book.py` (209 lines) is the pre-registered, blind, external-baseline half** (decision
ticket 21): `emit()` refuses to emit at or after its own question's resolution window opens
(temporal blindness enforced structurally, not by review), and exposes exactly 3 functions with no
function anywhere in it that can place a stake/side/order — checked as a public-surface allow-list
by harness guard `forecast_book_is_blind_by_construction_and_observe_only`
(`twin/invariants/harness.py:2227`). `benchmark.py` (435 lines) is the companion mechanical
question-selection + ingestion quarantine.

**Has a forecast ever been scored against a realised outcome? YES — this is the most important
single fact in this group.** `tests/test_royal_mail_beat.py` runs the real CLI end to end
(`twin backtest` → `twin score`) against Royal Mail's own **real, dated, cited** 2013 flotation
prospectus market-consensus forecast and its **real, cited** 2019 outcome (the GBP1.8bn remedial
investment concession), and the result is genuinely red: **Brier 0.9025, worse than a coin flip**
(`tests/test_royal_mail_beat.py:118-127`, docstring lines 7-10). The same test also runs Carillion's
and Enron's own backtests as legs feeding a memorisation-leakage discount
(`tests/test_royal_mail_beat.py:44-71`). The test file's own words: "these tests assert the red
result **survives to the surface** rather than asserting it is small" — and
`test_the_poor_score_is_printed_first_rather_than_buried` proves the CLI surfaces the worst score
first, not last. This is real, working, honestly-red backtesting, not a demo that only shows green.

By contrast: Netflix (`test_netflix_beat.py`) and Intel (`test_intel_beat.py`) are **deliberately
unscoreable** and say so structurally — Netflix because the story is too famous to distinguish
anticipation from recitation, Intel because its proposition has not resolved yet (2026/2027
resolution window). `twin score` **refuses** on both, and the refusal is itself asserted
(`test_this_subject_carries_no_answer_key_and_the_engine_says_so`,
`test_no_outcome_is_authored_and_score_refuses_and_names_the_absence`). Kodak/Maersk carry no
outcome at all by design (`tests/test_kodak_maersk.py:82-85`, "no outcome is authored").

**Tests.** `test_scoring.py`, `test_forecast_book.py`, `test_benchmark.py`, `test_regimes.py`,
`test_rollups.py`, `test_hindsight_resistance.py`, `test_market_signals.py`,
`test_intervention_aware_scoring.py`, `test_royal_mail_beat.py`, `test_netflix_beat.py`,
`test_intel_beat.py`, `test_four_verbs.py`.

## 4. Signals / feeds / market (`feed_signal.py`, `signal_classify.py`, `market_signals.py`, `unbound_pool.py`, `retrospective_sweep.py`, `ingest.py`, driftwood's `signals.yaml`)

**`feed_signal.py` (251 lines) is a deliberate lookup table, not a classifier, and says so.** "A
pinned feed version becomes one dated signal, by lookup, with no judgement" — because a clock
consumes only committed, reviewed claim files and "reasoning is a skill a human runs"
(`twin/feed_signal.py:1-16`). A feed name with no row raises rather than guesses. **This is exactly
the mechanism driftwood's own `twin/signals.yaml` implements**: five hand-authored `pin → signal →
scenario` rows plus two scenarios explicitly declared `unbound_scenarios` with a stated reason each
(one needs an internal HR event with no feed to bind to; one needs a human-run classify-and-judge
skill) — "a lookup that priced anything would be judgement wearing a table's clothes"
(driftwood `twin/signals.yaml` header comment).

**`signal_classify.py` (202 lines) is a keyword/word-overlap heuristic, openly labelled as such**
("the point being proven is the harness and the contract, not classifier quality" —
`twin/evolution_judge.py:20-21`, same admission repeated across all six "skill" modules). It is
graded against a labelled corpus **pooled from the same four real backtest orgs**
(Carillion/NMC/Wirecard/Enron) it was fitted to, and it scores 1.0 on that corpus by construction —
the threshold (0.8, `twin/skill-thresholds.yaml`) is then set *below* the achieved 1.0 "rather than
padded up to the achieved number." **This is a real circularity worth flagging explicitly**: the
same person/commit authored both the heuristic and the labelled corpus from the same four events,
so "passing the eval" tells you the author's own examples still parse the way the author wrote them
— it demonstrates the harness/threshold *mechanism* works, not that the classifier generalises.
This pattern repeats identically for all six "skills" (`signal-classify`, `evolution-judge`,
`causal-claims`, `gameplay-lens`, `substrate-generator`, `ethics-gate`) — see
`twin/skill-thresholds.yaml`, every entry reads "the heuristic scores 1.0 on its own
N-item corpus… set below that." Each module's docstring discloses this ("swap the body for a model
call; nothing else… changes"), so it is honestly labelled, but the labelling does not remove the
circularity — it only documents it.

**`unbound_pool.py` (223 lines) / `retrospective_sweep.py` (157 lines)**: weak signals are never
dropped, only decayed against `twin/decay.yaml`, and can be rescued later if a model change makes
them interpretable — each rescue records a computed `lead_time_to_recognition_days`.

**`market_signals.py` (257 lines)**: consumes prediction-market **price moves**, never price
**levels**, as probabilities — cites Bürgi/Deng/Whelan 2026 on Kalshi finding Mincer-Zarnowitz
unbiasedness rejected in every subsample, worst in the low-price tail. `as_probability()` exists
solely to refuse, always, so nobody is tempted to wire a price level into a belief later
(`twin/market_signals.py:22-25`). Also explicitly excludes any benchmark-quarantined question id
**before** classification runs, not just in an after-the-fact audit.

**Tests.** `test_signal_classify.py`, `test_market_signals.py`, `test_unbound_pool.py`,
`test_retrospective_sweep.py`, `test_ingest.py`, `test_prefilter.py`.

## 5. Wardley / evolution / gameplay (`wardley.py`, `evolution_judge.py`, `gameplay_lens.py`)

**`wardley.py` (210 lines) is inherited, not authored** — bands and D/K/R relations ported verbatim
from the `arckit` plugin (`~/.claude/plugins/cache/arc-kit/arckit/6.7.5/`), with the *action band*
each relation ships with deliberately stripped (an action band is a recommended action under
another name, refused by `no_recommended_action_field`). Pure IEEE-754 multiplication, no
quantisation — the module explicitly notes arckit's own worked example prints a rounded display
value (0.64) rather than the true product (0.6375), and this module carries full precision.

**`evolution_judge.py` (263 lines) — the same disclosed-heuristic/circularity pattern as §4.** A
hand-fitted keyword-to-position lookup (`_MATURITY_KEYWORDS`, `twin/evolution_judge.py:65-79`)
grounded in "ordinary Wardley judgement" but fitted to the same four backtest orgs' component names,
scoring 1.0 on its own four-item corpus (`tests/test_evolution_judge.py:200-227`), threshold set at
0.75 (one item allowed to miss) — this is the tuned-to-corpus-then-graded-on-corpus shape again.
**Not itself circular in a worse sense**: `judge()` infers first (grade 5), and a human `override()`
requires the inferred claim as its own first parameter and is structurally impossible to call
without it, returning grade 4 attributable to a registered role; `pushback()` never returns silently
on agreement.

**`gameplay_lens.py` (332 lines)** — covers exactly 2 of Wardley's ~100+ named gameplay patterns
(`land-grab`, `exploit-commoditisation`), chosen because both have preconditions **actually
checkable** from the graph (evolution position, `needs`-edge structure, `maintains`/`knows`/`owns`
ownership edges). Explicitly does **not** check incumbency ("no incumbent holds position") because
the map carries no rival-occupancy data — every such reason names the gap rather than dropping it
silently. `sweep()` scans the map on every scheduled run (opportunities must be "pulled"; threats
"push"). Exercised for real on Netflix (land-grab) and Intel (a real cited EUV-readiness opportunity
edge, added at build ticket 88 specifically to replace a toy `example.invalid` fixture that had
been standing in for it — `.scratch/twin/issues/*` per `bin/twin grade` output, criterion 7 of
`scenario-engine`).

**Tests.** `test_wardley.py`, `test_evolution_judge.py`, `test_gameplay_lens.py`.

## 6. Enactment / enact_guard / admission (`enact.py`, `enact_guard.py`, `enforcement.py`,
`corroboration.py`, `enactment-channels.yaml`, `enforcement-grades.yaml`)

**Two layers, deliberately redundant, deliberately asymmetric in how they fail (`twin/enact_guard.py:1-24`).**

*Layer 1 (`enact.py`, 328 lines):* the twin's public surface simply contains no merge-shaped
function — an **absence**, asserted by an invariant reading the module's own allow-listed surface.
Its own docstring names the weakness: "Python has no private constructor" — an absence has no call
site to forget, but it also does not survive the twin later gaining a shell tool, an MCP GitHub
server, or a subagent with `gh`, **with no diff to `twin/` at all**.

*Layer 2 (`enact_guard.py`, 334 lines):* a `PreToolUse` hook (`python3 enact_guard.py`, registered
in `.claude/settings.json:35`, confirmed present) that inspects every tool call before it runs and
denies: `gh pr merge`, `gh api …/merge`, `gh pr … --auto`, any tool name matching
`merge|squash|rebase_and_|dispose|land_|ship_` (a keyword screen over MCP tool names), and any
`git push` whose *resolved* remote URL matches `policy-as-versioned-[a-z0-9-]+` — **except this
repository's own origin**, a deliberate, named, owner-authorised weakening
("This is still a weakening… before this, the twin could not write to any remote… now it can
publish its own model unattended" — `twin/enact_guard.py:228-238`).

**Known holes, named in the source itself, not discovered by me:**
- The command-pattern net is explicitly "not a proof" — a differently-named wrapper script or a
  hand-rolled `curl` REST call with a token is not matched (`twin/enact_guard.py:29-33`).
- The MCP tool-name screen is a keyword match, not an enumerable allow-list, because an MCP
  server's tool-name space is "somebody else's namespace… mostly not ours" — a server calling its
  merge tool `apply_changes` is not caught (`twin/enact_guard.py:121-129`).
- **Two real bugs, found and fixed in-repo, both about `_push_target` resolving the wrong `cwd`**:
  on 2026-08-31 the guard resolved a push's remote against the *caller's* cwd rather than the
  directory `git -C <dir>` or a leading `cd <dir> &&` actually pointed at, which matched the
  self-push carve-out and **silently admitted a push to all six enactment repositories**
  (`twin/enact_guard.py:151-166, 217-238` — the docstring records this as a real incident, not a
  hypothetical).
- **Mode is a durable file, not a hard rule**: `twin/ENACT_MODE` (currently checked in as
  `operations`, confirmed by reading the file) or `TWIN_ENACT_MODE` env can flip the guard to
  `development`, where `decide()` returns `None` for everything (`twin/enact_guard.py:266-272`).
  The docstring records that the *default* used to fail open silently in `development` mode until
  2026-08-29, when the fallback was flipped to `operations` specifically because "thirteen tests
  that assert what the guard DOES had been red since commit 9282301" while an autouse test fixture
  quietly forced `operations` for the *test process only* — i.e. the test suite had been passing
  while asserting behaviour the shipped default did not exhibit. This is a real, admitted, dated
  regression-then-fix, not a live hole.
- Harness guard `enactment_is_propose_only_at_both_layers` explicitly does **not** assert that a
  given agent runtime routes subagent tool calls through this hook — that is "the runner's
  business," and the invariant "deliberately does not pretend to."

**`enforcement.py` (488 lines)**: enforcement rungs and posture-as-identity are computed from two
declared facts, never typed by a human, backed by `enforcement-grades.yaml` (a versioned rung ladder
that the module docstring in `README.md:3129-3130` notes carries "no number anywhere on it" — i.e.
enforcement strength and £ price are kept structurally separate). `corroboration.py` (425 lines):
enactment sensing across multiple channels (`enactment-channels.yaml`, a closed table), grade set by
corroboration across channels — no single channel prices alone, and a subject cannot corroborate
itself.

**Tests.** `test_enact.py`, `test_enforcement.py`, `test_corroboration.py` (via
`test_admission.py`/pricing chain), `test_use_gating.py`.

## 7. Misuse / ethics / disparate impact (`misuse.py`, `ethics_gate.py`, `disparate_impact.py`,
`misuse-catalogue.yaml`, `behavioural-misuse-catalogue.yaml`, `affected_parties.py`, `does_not_do.py`)

**`misuse.py` (205 lines)**: the catalogue names mechanisms, not risks — every entry must carry a
non-empty `mechanism` field or the loader refuses it (`twin/misuse.py:70-74`). Constraint-removal
"attractiveness" logging is **computed, never stated**: `log_removal()` accepts no float parameter;
the only way to produce a number is to re-run the real pre-filter with one constraint stripped
(`twin/misuse.py:86-127`) — a genuinely non-fakeable design (no code path lets a caller type a
number directly into the log).

**`ethics_gate.py` (513 lines)**: a three-rung admission ladder (purpose → necessity →
proportionality), walked in strict order and stopping structurally at the first failed rung. DPIA
triage names the ICO's 2023 monitoring-guidance mandatory cases. `classify_gameability()` is again a
small, disclosed keyword match fitted to one worked example (bus-factor scoring) — same pattern as
§4/§5. `honest_build.py` explicitly reclassifies `ethics-gate`'s admission machinery as `code` not
`skill` for the harness-inventory purposes, on the grounds that a correctly-implemented boolean
ladder has exactly one right answer and nothing interpretive left in what the eval harness actually
scores (`twin/honest_build.py:27-40`) — a genuinely careful distinction, not a rationalisation glossed
over.

**`disparate_impact.py` (110 lines)**: a **sealed** channel — the twin structurally cannot represent
a protected characteristic anywhere (`no-special-category-representation`, the universal floor), so
a disparate-impact finding must be made *externally* and reported in without ever naming the
protected ground (`raise_audit()` runs the same `refuse_special_category` refusal the model
repository itself runs). `respond()` requires the exact role `disparate-impact-respondent`.

**`affected_parties.py` (79 lines)**: names non-contracting third parties who bear a modelled
consequence with no perspective of their own, and refuses to price their harm — closing decision
ticket 09's "ethical harms" acceptance criterion honestly (the harm is disclosed, not converted into
a number).

**`does_not_do.py` (90 lines)**: **generated, never authored** — a pure function of
`grades.Capabilities` listing every unchecked acceptance criterion across every capability. There is
no YAML file behind it and "no field through which an entry could be typed," so the demo's honesty
register cannot drift from the checklists it reads (`twin/does_not_do.py:9-13`). Given today's live
`73/73, 13 at full` result, this register is currently **empty** — every capability is full, so
there is nothing left to disclose through this particular mechanism (open question: is an empty
does-not-do register itself tested/asserted anywhere as a real, changing state, or would it read
identically empty whether or not a criterion existed at all? I did not verify this — flagged below).

**Tests.** `test_misuse.py`, `test_ethics_gate.py`, `test_disparate_impact.py`,
`test_affected_parties.py`, `test_does_not_do.py`.

## 8. Substrate / planter / sensors (`substrate.py`, `substrate_generator.py`, `substrate_eval.py`,
`substrate_report.py`, `planter.py`, `detector.py`, `scorer.py`, `spine.py`, `sensors.yaml`,
`plant-horizons.yaml`, `netflix-substrate-recipe.yaml`)

**A genuinely enforced adversarial split, structurally verified on real source, not asserted in
prose.** `planter.py` (202 lines) is the *only* module that ever reads
`substrate_generator.generate()`'s `plants` field; `detector.py` (85 lines) **imports nothing naming
`planter`**, checked by an **AST scan of the real source**
(`tests/test_detector.py::test_detector_module_imports_nothing_naming_planter`), and `detect()` is
proven behaviourally blind by showing it returns byte-identical output whether or not a decoy
`plants` key is spliced into its input. `scorer.py` (106 lines) takes ground truth and detections as
two independent explicit arguments, never a merged object. Every `ScoreResult` carries
`SHARED_PRIOR_LIMITATION` verbatim — the named, un-fixed limit that planter and detector share the
same model family and priors, so "a synthetic result is never evidence the twin anticipates the
world" (`twin/scorer.py:19-21`).

**Scoring is real arithmetic on declared thresholds**: a plant detected on/before its declared
`actionability_horizon` scores `TIMELY_SCORE=1.0`; after it, `LATE_SCORE=0.05` (near-zero, not
zero — "a late detection is a post-mortem, not nothing"); never detected, `MISSED_SCORE=0.0`
(`twin/scorer.py:27-29`).

**`spine.py` (170 lines)**: the spine is an org's own **real, dated `signal` documents** — no second
authored format — and `reconcile()` structurally refuses if the free-running substrate does not
verbatim carry every spine fact knowable by a checkpoint.

**`substrate_eval.py` (469 lines)** computes six real, declared fidelity dimensions from a batch's
own content (signal-to-noise, plant difficulty + spread, spine consistency, reporting asymmetry,
mundanity, **contamination**) rather than an eyeball. Contamination scanning uses a small
known-real-entity blocklist (the 11 real backtest/flagship subjects plus 3 real named people) and
**hard-refuses** (`ContaminationError`) rather than merely reporting, on a demonstrated real hit
(planting "Markus Braun," Wirecard's real former CEO, into synthetic content —
`tests/test_substrate_eval.py::test_refuse_if_contaminated_fires_on_a_planted_real_name_collision`).

**Reproducibility**: a versioned recipe + seed regenerates a toy substrate byte-for-byte, but
regenerated substrate is deliberately typed **authored, not derived** — a live generator cannot
promise `identical_pins_identical_bytes` (demonstrated with a stand-in generator that genuinely does
not reproduce — `twin/invariants/harness.py:4114`, `_substrate_regeneration_is_not_deterministic_so_it_is_authored`).

**Tests.** `test_substrate.py`, `test_substrate_generator.py`, `test_substrate_eval.py`,
`test_planter.py`, `test_spine.py`, `test_netflix.py` (the real committed Netflix substrate scores
contamination 0.0 and every fidelity dimension inside its target band).

## 9. Demo / beats (`demo.sh`, `beat-sequence.sh`, `beat-royal-mail.sh`, `beat-intel.sh`,
`beat-netflix.sh`, `demo_slice.py`)

**The order is asserted as the argument, in code, not just prose.** `beat-sequence.sh` runs
**b → b → c → a**: Royal Mail (falsifiability, retrospective, red result), then Intel
(falsifiability, live/forward, unscoreable and says so), then Netflix last (versioned governance,
concluding in the one-currency £ comparison) — "£ appears nowhere before this, the third and final
beat" (`twin/beat-sequence.sh:12-14`). Harness guard
`the_demo_sequence_earns_credibility_before_it_spends_it` reads this **shell script's own literal
text** to hold CI to that order, because "no bash parser exists" to check it structurally
(`twin/invariants/harness.py:4422`). A named CI incident is recorded as the reason this exists: an
earlier 3-separate-CI-steps version once silently priced Netflix's beat before Intel's own step ran
(`.github/workflows/twin.yml` comment, "royal-mail, netflix, intel priced its beat before the third
one ran").

**`demo_slice.py` (194 lines)** emits the demo's own rendered artefact: thesis, subjects, boundary,
and an acceptance-criteria map — the structured, checkable content decision ticket 22 asked for,
distinct from this README's prose.

**Tests.** `test_demo_slice.py`, `test_beat_sequence.py`, `test_royal_mail_beat.py`,
`test_netflix_beat.py`, `test_intel_beat.py`.

## 10. Verification / grades / honest_build (`grades.py`, `honest_build.py`,
`twin/invariants/{checks,harness}.py`, `reproduce.py`, `attest.py`, `sign.py`, `challenges.py`)

**Grades**: covered in "Counts" above — computed checklists, refuses hand-typed grades, refuses
drift from the owning decision ticket's live acceptance-criteria text, requires evidence+witness per
tick.

**Two signature kinds, refused as a type error before values are even checked** (`sign.py`, 186
lines): a **human** signature binds to a **role** from `roles.yaml`, never a named individual; an
**agent** signature asserts reproducible origin (runtime + tool version) and explicitly states what
it does *not* assert — correctness, accountability, human review. A derived artefact may carry only
the second, never the first — invariant `derived_never_human_signed`
(`twin/invariants/checks.py:826`). Mechanism today is HMAC-SHA256 keyed from `TWIN_SIGNING_KEY`
(README's own words: "a shared key proves possession, not identity" — this is a named, current
ceiling, not a hidden one; the stated upgrade path is sigstore/gitsign + in-toto, which is exactly
what driftwood's *own* CI workflows (`cut-release.yml`, `twin-sweep.yml`) already use for their
git-level signing — the twin package's own artefact-level signing has not yet moved to that
stronger mechanism).

**`attest.py` (168 lines)**: attestation sidecars carry machine-varying facts (wall clock, host,
interpreter) *outside* the artefact body, which is what makes `identical_pins_identical_bytes`
possible across architectures — verified for real by the CI `determinism` job's 3-way OS/arch matrix
plus a `reproduce-elsewhere` job that recomputes an x86_64-Linux-emitted artefact on a macOS ARM
runner from nothing but its pins (`.github/workflows/twin.yml`, `determinism`/`reproduce-elsewhere`
jobs).

**`reproduce.py` (286 lines)**: recomputes an artefact from its own recorded pins/command; `VERBS`
now includes `backtest`, reusing `run()`'s own replay branch rather than a second implementation.

**`challenges.py` (163 lines)**: contestability is a primary workflow — `twin challenge` disputes
one claim path in one artefact; `twin verify --attestation`/`--challenge` surfaces open/resolved
challenges beside the reproduced artefact.

**Invariant harness discipline worth flagging**: several checks explicitly read the wall clock
because the property under test is inherently about *now* (`drift_window_is_actually_being_sampled`,
`flux_verdict_is_pre_registered_and_derived`, `flux_coverage_floor_is_still_reachable`) — README
notes "a pinned clock would make all three green forever at the moment they were written, which is
how the gap the third one guards went unseen" (`twin/README.md:2653-2657`) — i.e. the package's own
authors record having previously shipped a clock-blind version of this exact check and having caught
the gap only via a dedicated audit (build ticket 70).

---

## The eleven real-firm subjects (`twin/fixtures.py`)

All eleven `build_<x>_org()` functions carry real `https://` citations to real, dated, publicly
documented sources (verified by direct grep, not by trusting docstrings):

| Subject | `build_` function | Real URLs (module-local count) | Has a scored outcome? |
|---|---|---|---|
| Carillion | `build_carillion_org` | 9 (incl. FCA decision notices, HC 769 parliamentary inquiry PDF) | Yes — leg in Royal Mail beat |
| NMC Health | `build_nmc_health_org` | 6 (Muddy Waters, Gulf News, FCA-adjacent) | Outcome authored, contamination `low` |
| Wirecard | `build_wirecard_org` | 7 (BaFin, KPMG report, Bundestag inquiry) | Outcome authored, contamination `high` (the one deliberately-failed low-notoriety control) |
| Enron | `build_enron_org` | 4 (CNN, SEC EDGAR) | Yes — leg in Royal Mail beat, contamination `control` |
| AstraZeneca | `build_astrazeneca_org` | 6 | Not checked in detail (out of scope sample) |
| Sanofi | `build_sanofi_org` | 4 | Not checked in detail |
| Royal Mail | `build_royal_mail_org` | 8 (own 2013 IPO prospectus, rival hub openings, own FY17-18 results, own profit warning) | **Yes — the primary scored backtest, Brier 0.9025** |
| Netflix | `build_netflix_org` / `build_and_corroborate_netflix_org` | 17 combined (SEC EX-99.1 shareholder letters + press) | **Deliberately no outcome — too famous to score honestly** |
| Intel | `build_intel_org` | 15 (SEC EDGAR, IR press releases, trade press through 2026) | **Deliberately no outcome — hasn't resolved yet (2026H2/2027H1)** |
| Kodak | `build_kodak_org` | 2 (Forbes, CNN) | No outcome authored by design |
| Maersk | `build_maersk_org` | 2 (Maersk investor relations, CNBC NotPetya) | No outcome authored by design |

Citations for Royal Mail/Netflix/Kodak/Maersk/Intel live in module-level `_SUBJECT_*` dict
constants defined just above each `build_` function rather than inline in the function body, which
is why a naive line-range grep undercounts them — I re-verified by locating those constants
(`twin/fixtures.py:4206-4394` for Royal Mail, `:5174-5615` for Intel, `:5615-5787` for Kodak,
`:5787-5951` for Maersk) and grepping those ranges specifically.

Four more fixtures are **not** real firms and should not be counted as a twelfth/thirteenth: `pocket_org`
and `regime_org` are synthetic hand-computable fixtures (`example.invalid` URLs, by design — see
`twin/pocket-org-worksheet.md`); `twin_self_org` is the twin's reflexive self-model (no URLs, not a
firm); `library_org`/`build_standing_library` is the generic, tenant-free standing scenario library
driftwood vendors (see below).

## Twin → driftwood forward-intel → `prices[]`

Confirmed by reading `emit-forward-intel.py` and `composed/evidence.json` directly, not inferred:

1. Driftwood vendors the hub's **standing-library world layer** (`twin.fixtures.LIBRARY_WORLD_FILES`
   — 30 files: `world/meta.yaml`, 15 components, 13 propositions, 1 world model) verbatim into
   `driftwood/twin/world/`, pinned by `twin/PIN.yaml` (`twin_version: 0.1.0`, `tag_cut: false`) and
   cross-checked against a re-staged git mirror commit hash in `VENDORED.md`.
2. `driftwood/twin/emit-forward-intel.py` builds a **deterministic two-commit throwaway git mirror**
   of `world/` + `orgs/`, opens it through `twin.repo.ModelRepo`, loads the `driftwood` `Overlay`,
   finds the **one** graded causal edge reaching the perspective's declared cash flow (refuses if
   there isn't exactly one — `cash_flow_edge()`), and computes `lm = [base*elasticity[k] for k in
   min/mode/max]` — a real read of the overlay's own numbers, not a stub.
3. That `lm` triple (plus a `curve` computed per selection-policy ladder rung: `impact*(1-reduction)+cost`)
   is written into `forward-intel/v1/feed.json` under the ADR-0019 envelope
   (`kind: feed, name: forward-intel`).
4. `forward-intel/payload.schema.json`'s own description states the consuming contract explicitly:
   "The estate consumes it as one more pricing parent edge — `source: twin` in `prices[]` — and
   `platform/fair/fair.py` annualises it."
5. I confirmed the far end lands: `driftwood/composed/evidence.json:1400-1401` carries
   `"source": "twin", "kind": "twin"` — i.e. the composed pricing evidence chain genuinely names the
   twin as a pricing parent, not merely a schema comment promising it would.
6. **A self-referential cycle was found and removed, not merely avoided** — `emit-forward-intel.py`'s
   own comment records that an earlier version of `derived_from` named the insurer's quote pin,
   which is itself priced off driftwood's composed exposure whose largest line is derived from
   *this very feed* — "a feed naming as its input a document containing its own output is a cycle...
   it made the premium and the forecast mutually self-supporting" (`emit-forward-intel.py:172-179`).
   `derived_from` now names only the overlay's own ref and the one subscribed frequency-donor feed.

The forward-intel scenario itself has **no frequency** (`lef: null`) — frequency is deliberately
borrowed from one, and only one, named subscribed feed (`FREQUENCY_FROM = "threat-register"`); the
curve **never selects a tier** — "the curve never picks" (payload schema description) — the estate's
own versioned `selection-policy` package does that, downstream.

## The twin sweep clock (`driftwood/.github/workflows/twin-sweep.yml`)

Cron `5 7 * * *` (07:05 UTC). Each firing does **exactly one of two things, structurally enforced**:

- **Render unchanged** (per `forward-intel/rule.yaml`'s tolerance: shock/perspective/currency/
  register changed, or any curve/`lm` number moved >10%) → append one JSON line to
  `observations/twin-sweep.jsonl` on `main`, gitsign-signed, `[skip ci]`.
- **Render moved** → open a pull request carrying the re-rendered feed on a dated branch; **never
  commits the declaration directly** — "a published feed is a DECLARATION, and a clock never
  commits one" (ADR-0024 D1).

**The observation cage.** A dedicated step (`if: always()`) resets the git index and stages *only*
paths in the declared `OBSERVATION_LANE` env var, then fails the run if anything else is staged or
left dirty. The workflow's own comments record **two real, dated incidents this cage was built to
stop**, both from the 2026-08-28 review: (1) `if: always()` running on the moved==true branch meant
HEAD was the proposal branch (feed declaration and all), and only `git diff --cached --quiet`
happening to be true kept it off `main`; (2) an earlier guard filtered `git status --porcelain`
with `grep -v '^[AMD] '`, which stripped exactly the staged-and-clean entries, so a declaration
already staged by an earlier step was committed and pushed while the guard printed "this clock
declared nothing."

**First scheduled firing (2026-09-01), per user memory `project_clock_first_firings.md`,
independently consistent with what the workflow file itself implies about untested cron paths**: GitHub
cron fired ~5-5.5h late across the estate; a real bug in the sweep's re-render branch was
unreachable under GitHub's default `bash -e` (recorded as ticket 72); a `curl -o kind` collision bug
in the unrelated `drift-sample.yml` clock was also found the same day. I did not independently
re-verify these firing timestamps (would require a GitHub Actions run-log fetch, out of scope for
this file-based review) — reported here as memory-sourced, not directly observed.

## Version / tag status

`twin/VERSION` = `0.1.0` (confirmed by reading the file). `twin/RELEASE.md` states the tag the owner
must cut is `twin/v0.1.0` (prefixed, because the hub repo is not only the twin) and **"It is not cut
yet. Nothing in this build can cut it: a signed tag is cut in Actions, never locally."** Driftwood's
`twin/PIN.yaml` and `VENDORED.md` both independently confirm `tag_cut: false` and record that
`world_ref` (a raw commit SHA) is "the only pin with bytes behind it" in the meantime. This is
self-consistent across both repos — no discrepancy found between the hub's claim and the adopter's
recorded pin state.

## enact_guard.py — summary (see §6 for full detail)

A `PreToolUse` hook, registered and confirmed present in `.claude/settings.json:35`, mode currently
`operations` (confirmed by reading `twin/ENACT_MODE`). Refuses merges (command-pattern net, not a
proof), refuses MCP tool calls matching a merge-shaped keyword screen, refuses pushes to any
`policy-as-versioned-*` repo except this one (a named, dated, owner-authorised carve-out). Two real
bugs in `_push_target`'s `cwd` resolution were found and fixed in-repo (2026-08-31 incident) — both
documented as bugs that **silently admitted** exactly the pushes the guard exists to refuse, until
caught. The permissive-by-default failure mode was also found and fixed (2026-08-29) after
discovering the test suite had been passing against a forced `operations` override that did not
match the shipped default.

## Notable circularities (flagging for the auditors, not adjudicating)

1. **The six "skill" heuristics are each graded against a corpus the same author hand-built from the
   same handful of subjects the heuristic was tuned on**, then a pass threshold is set just below the
   1.0 score each achieves on its own corpus (`signal-classify`, `evolution-judge`, `causal-claims`,
   `causal-claims-grade-accuracy`, `gameplay-lens`, `substrate-generator`, `ethics-gate` — all seven
   entries in `twin/skill-thresholds.yaml` read this way). Every module's docstring discloses this
   candidly ("the point being proven is the harness and the contract, not classifier quality") and
   names a stated upgrade path (swap the heuristic body for a model call). The disclosure is
   consistent and repeated, not hidden — but the corpora do not constitute independent evidence of
   classification quality, only evidence that the eval-harness *mechanism* (threshold, grading,
   refusal-on-drop) works.
2. **The capability grade system is not self-referentially circular** in the same way — it is
   validated against acceptance-criteria text read live from `.scratch/twin/issues/`, not against
   anything `twin/` itself produced, and typing a grade by hand is a hard refusal. This is a
   materially different (stronger) design than the skill-corpus pattern above and should not be
   conflated with it.
3. **`does_not_do.py`'s register is currently empty** (all 13 capabilities full) — I did not find a
   test asserting the register is non-trivial when a criterion is genuinely unchecked vs. simply
   always-empty-by-construction; flagged as an open question below rather than asserted as a defect.

## What I did not verify / could not look at

- Did not run `bin/twin verify` (needs `clone-estate.sh`, a network fetch — out of scope for
  read-only review) or `pytest -q` (would need the pinned venv; I confirmed `pyyaml` import works
  with system python3 but did not install the pinned pytest/mypy versions to actually execute the
  suite). All test-count and pass/fail figures above are either grep'd test-function counts (which I
  did run) or quoted from README's own last self-reported audit — the latter are dated, not
  re-verified live.
- Did not read `twin/fixtures.py`, `twin/cli.py`, `twin/verbs.py`, `twin/model.py`, or `twin/schema.py`
  line-by-line — these four alone are ~11,500 of the package's 27,572 non-invariant lines. Everything
  said about them above is from docstrings, targeted greps, and cross-references from other modules
  and from README, not full reads.
- Did not examine AstraZeneca's or Sanofi's fixtures beyond confirming citation counts — no claim
  above about their content, outcome status, or contamination class.
- Did not trace driftwood's `selection-policy` package or `compose/`/`scripts/render_composed.py`
  beyond confirming the one `source: twin` line in `composed/evidence.json` — the full annualisation
  and tier-selection arithmetic downstream of the twin's `lm`/`curve` numbers is unverified by me.
- Did not independently verify the 2026-09-01 first-clock-firing timing/bug claims against actual
  GitHub Actions run logs; reported as consistent with prior session memory, not directly observed
  in this review.
- Did not read `twin/verbs.py` (1,520 lines, the sense/run/score implementation) in full — everything
  about `sense`/`run`/`score` mechanics above is inferred from `regimes.py`, `scoring.py`,
  `forecast_book.py`, capability-file evidence text, and test names, not from `verbs.py`'s own body.
- Capabilities/tests for `twin/skills.py`, `twin/record_skill_scores.py`, `twin/scenario_diff.py`,
  `twin/schedule.py`, `twin/causal_accounts.py`, `twin/tradeoff.py`, `twin/positions.py`,
  `twin/credibility.py`, `twin/worksheet.py` were identified and one-line-summarised via docstring
  grep only (see the batch table mid-session) — not individually read or cross-checked against their
  tests.
