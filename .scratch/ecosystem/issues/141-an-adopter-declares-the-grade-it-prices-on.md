# 141 — An adopter declares the grade it prices on

Type: task
Status: claimed
Blocked by: none

## Question

Graduated 2026-09-25 from grilling ticket 30, decision 6 (delegated), and ADR-0032.

The estate default pricing threshold is grade 2 (`twin/evidence-ladder.yaml` `pricing_threshold`
and `path_admission_threshold`). An adopter may declare, on its own signed `party.yaml`, that it
prices on grade 3: "published work, not observed here". Build that declaration end to end:

1. **The platform party schema** gains the declaration. The schema is closed
   (`party/schema.json`, `party/party_artefact.py`), so this is a platform release. The only
   admitted values are 2 and 3. A value looser than 3 is refused by the schema: grade 4 is an
   expert's say-so and grade 5 a model's, and neither may price.
2. **The twin reads the declaration** where it applies the two thresholds, and the valuation
   schema admits an amount at grade 3 only for a perspective whose party declares 3.
3. **Every price shows the weakest grade it rests on**, the one operation ADR-0024 point 6 admits
   on grades (an order statistic). The forward-intel payload, the `prices[]` line and the handbook
   carry it.
4. **A synthetic record never raises a grade** (twin ticket 12). The check refuses an edge or a
   valuation whose grade rests on a record marked synthetic, planted or injected.

The hub default stays 2 for every overlay that does not declare, including the real-firm backtest
corpus.

5. **`data_subjects` becomes optional in the size block** (decided 2026-09-25, delegated; see
   ticket 144's Comments). Neither comparable filing discloses it, and nothing in the estate reads
   it today. A converter that needs it refuses by name when it is absent (ADR-0020).

## Notes

Ticket 144 needs this before tuppence, ludlow and driftwood can price on their comparable-firm
anchors. The release cut and the adopter tags wait for the owner's authorisation.

## Comments

**2026-09-25, claimed and built.** Owner-instructed: the owner wrote on 2026-09-25, "i'm afk you
have all the approvals you need to deliver". That authorises feature branches and pull requests
in the hub and the estate repos; it does not authorise a merge, a push to any main, a tag, a
release or a workflow dispatch, which the integrator does. Two pull requests build this ticket:
platform `ticket-141-party-declares-pricing-threshold` (the party schema,
policy-as-versioned-platform/platform PR #45) and hub `ticket-141-declared-pricing-threshold`
(the twin, policy-as-versioned-flux PR #141). The platform PR merges first. A platform tools
release (`cut-release.yml`) and the three adopters' pin moves are needed before ticket 144 can
put the declaration on a signed `party.yaml`.

**What the platform PR builds.** `party/schema.json` and `party/party_artefact.py`:
`appetite.pricing_threshold`, an optional integer whose enum is `[2, 3]`, read from schema.json by
the validator (one source of truth); 1, 4, 5, any other integer, a string, a float, a bool, null
and a container are each refused with the reason named (4 and 5 never price for anybody; 1 needs
no declaration). `size.data_subjects` becomes optional; `turnover`, `customers`, `headcount` and
`as_of` stay required and a present `data_subjects` is still checked. The selfcheck gains planted
good and bad cases for both. `party/README.md` documents the field. Every other place in platform
that enumerates party or size fields was searched (`data_subjects`, `headcount`, `tolerance`,
`schema.json`): none enumerates them (`compose/composition.py` reads `size.turnover`,
`size.as_of` and `size.customers` by name; `risk/enforce.py` reads `appetite.tolerance`), so
nothing else changed. `compose/composition.py` `price_twin` carries `rests_on_grade` on the
`source: twin` `prices[]` line, read off the served forward-intel payload and null where the
payload predates the field; `compose/handbook.py` prints the grade beside the twin line or names
its absence. No release is cut here.

**What the hub PR builds.** *(Superseded in part on 2026-09-26, see the two review-round
comments below: `tests/test_pricing_threshold.py` holds 49 tests, the golden citation reads
"eco-system ticket 141 (ADR-0032, decided by eco-system grilling ticket 30 decision 6) ...", and
the synthetic-record rule reads the admitting path and runs in `twin exposure` too.)*
`twin/evidence.py`: `DECLARABLE_THRESHOLDS = (2, 3)`,
`declared_threshold(party)` (reads `appetite.pricing_threshold` off a parsed `party.yaml`, absent
means the ladder's 2, anything else refused by name), `check_threshold`, `may_price(grade,
threshold=...)`, `applied(...)` and `published(pricing=..., admission=...)` (the thresholds in
force and their basis beside the ladder's pin), and `weakest(*grades)`, the order statistic.
`twin/model.py`: `Overlay.load(repo, org, pricing_threshold=None)` validates every valuation
against the threshold it is handed and records it as `Overlay.pricing_threshold`.
`twin/schema.py`: `valuation()` keeps the shape and the one refusal true for every party (an
amount at grade 4 or 5 never loads); `valuation_tie()` enforces the grade-amount tie per party
through `validate(..., pricing_threshold=...)`. `twin/admission.py` `admit(...,
threshold=...)`. `twin/pricing.py`: `impacts(graph, perspective, origin, overlay)` and `price`
gate on `overlay.pricing_threshold`, re-check the valuation's grade themselves, carry
`rests_on_grade` on every impact and every credit, and refuse `RESTS_ON_SYNTHETIC`.
`twin/synthetic.py` (new): what a synthetic record is and whether an edge, valuation or claim
rests on one. `twin/verbs.py` `exposure` threads the same threshold and carries `rests_on_grade`
on admitted entries. `tests/test_pricing_threshold.py` (42 tests). The golden digests for
`priced-impact` and `scenario-exposure` are re-blessed under the citation "eco-system decision
ticket 30, decision 6 (ADR-0032), built by eco-system ticket 141". The API ticket 144's emitters
call: `threshold = evidence.declared_threshold(party)`; `Overlay.load(repo, ORG,
pricing_threshold=threshold)`; `evidence.may_price(edge.grade, threshold=threshold)`; and the
payload's new top-level field is `rests_on_grade`.

**Decisions, each delegated (ADR-0025).**

1. *Placement* (as briefed): `appetite.pricing_threshold`, optional integer, 2 or 3, absent
   means 2; it governs both twin thresholds for that party only.
2. *Where the grade-amount tie is enforced*: at the source, parametrised by the declaration, and
   again at the gate. `Overlay.load` hands the party's threshold to the schema, so a grade-3
   amount does not load for a party that declared nothing (exactly as today) and loads for one
   that declared 3; `pricing.impacts` and `verbs.exposure` then re-check each valuation's grade
   against `overlay.pricing_threshold` rather than trusting the loader. An amount at grade 4 or
   5 is refused by the schema unconditionally, since no party may declare those. Reason: the
   gate at the source is what stops a grade-3 amount reaching an emitter that reads
   `values[...]["amount"]` directly (driftwood's does), and a second check at the gate costs one
   comparison. Nothing is less safe: no file that loaded before loads differently, and the only
   new admission is a signed declaration.
3. *The declaration never enters the model repository*: no overlay file, scenario or CLI flag
   sets a threshold. It is read off the signed party artefact by the emitter and handed to the
   loader. Reason: an overlay that could set its own threshold would be an author marking its
   valuations priceable, the move decision ticket 09 refused.
4. *The corroboration gate does not read the declaration.* A mitigation claim's own grade is
   gated on the party's threshold; the enactment half stays at the ladder's default. Reason: a
   declaration widens what a party may price about the world (published work), not what counts
   as the party having acted; every channel alone holds grade 3 or 4, so reading the declaration
   there would let one uncorroborated machine channel price on its own, which the corroboration
   table exists to refuse (decision ticket 18 Q3).
5. *The weakest grade* (amended 2026-09-26 after review, see the fixer's comment below):
   `rests_on_grade` on each priced impact is the weakest of the propagation path's worst hop, the
   valuation and the admitting path's worst hop; on a credit, the weakest of the impact, the
   claim and the corroborated enactment; on an exposure entry, the weaker of the valuation and
   the admitting path. The `gating` block carries `applied` (both thresholds and their basis)
   only in the bodies that price and expose; blast and propagation bodies are byte-identical to
   before.
6. *Forward-intel payload and the prices[] line*: the payload schema is closed and lives in each
   adopter repo, so the field is a payload MAJOR that ticket 144 cuts (top-level
   `rests_on_grade`, an integer 1-5, equal to the hub's priced impact). Platform reads it off the
   served payload onto the twin `prices[]` line and the handbook names its absence until then;
   nothing is derived on the platform side, because the seam holds no grade of its own.
7. *A synthetic record*: a signal whose `substrate` is a non-empty blob reference, or whose
   `provenance` carries `synthetic`, `planted` or `injected` set true. A grade rests on one when
   a claim binds such a signal, when a strengthening regrade of the subject names one by id or
   says its evidence is synthetic, planted or injected, or when the subject's own prose (an edge
   note, a valuation basis, a claim's evidence) does. The prose legs are a net, not a proof, and
   `twin/synthetic.py` says so; the served overlays of all three adopters and the hub fixtures
   carry no marker word in any graded collection (measured with `git grep` on `origin/main`).
   The net caught two test plants in `tests/test_pricing.py` whose mitigation basis literally
   read "planted"; they now say "authored".
8. *`twin/VERSION` and `TOOL_VERSION` stay at 0.1.0* although emitted price and exposure bytes
   change. Reason: all three adopters' `twin/PIN.yaml` pin 0.1.0, their sweeps check out hub
   `main`, and `emit-forward-intel.py` refuses when the versions disagree, so a bump would refuse
   every sweep between this merge and ticket 144's pin moves with no tag to move to. The goldens
   are re-blessed instead, with the citation recorded in `golden-digests.json`; the version moves
   when ticket 143 pins the twin by hub commit or the owner cuts `twin/v0.1.0`.
9. *No invariant body changed*: the existing `grade_5_only_path_never_prices` already asserts the
   default admits `[1, 2]` and never 5; the declaration is covered by the new test file.
   Editing `twin/invariants/checks.py` would move the pinned module hash and need a manifest
   re-pin for no new assertion.

**What was measured.** On the hub branch merged onto `origin/main` at `501858bb`:
`tests/test_pricing_threshold.py` 42 passed; `tests/test_pricing.py test_evidence_ladder.py
test_perspective.py test_admission.py test_use_gating.py test_corroboration.py` 139 passed
(139 before the change); `tests/test_schema.py test_seam2_model.py test_causal_edges.py
test_twin_inside_twin.py test_refusals.py test_registration.py test_seam2_propagation.py
test_signal_classify.py test_local_clock.py` 292 passed; `twin verify --only
grade_5_only_path_never_prices --only prefilter_precedes_pricing --only
identical_pins_identical_bytes --only ruin_class_absent_not_priced` 4 passed after the goldens
were re-blessed (only `priced-impact` and `scenario-exposure` moved; the other ten digests are
unchanged), and `TWIN_CI_ARCH_MATRIX=1 twin verify --only cross_architecture_determinism` 12
artefacts byte-identical on arm64. The ladder's digest is unchanged by its new comment
(`97f8399a0a5f`). On the platform branch at `557c153`: `party/party_artefact.py --selfcheck` 34
OK lines; the platform's own `party.yaml` checks out; the served `party.yaml` of driftwood,
tuppence and ludlow at their `origin/main` validate under the new schema unchanged;
`compose/handbook.py --selfcheck` 47 checks PASS; `compose/composition.py --selfcheck` against
the local estate clones (`PAVC_ESTATE_CLONE`) selfcheck ok, with driftwood's real twin line
carrying `rests_on_grade: null` because its served payload (schema 2.0.0) does not state it.
`verify/twin-evals/verify-twin-evals.sh` on the hub branch: exit 0, every line PASS or NOT
MEASURABLE as before, `cross_architecture_determinism` 12 artefacts byte-identical on arm64.

**2026-09-26, review findings addressed.** Owner-instructed: the owner wrote on 2026-09-25,
"i'm afk you have all the approvals you need to deliver". That authorises this push to the same
two feature branches and nothing more. The reviewer returned two blocking and three minor
findings on hub PR #141 and none on platform PR #45. The platform branch is unchanged. One hub
commit (`6528c680`) builds the following, and the earlier measurement paragraph is superseded by
the one after this.

*Blocking 1, the invariant suite main runs.* Invariant 59
`mitigation_credit_is_gated_on_corroborated_enactment_not_just_claimed_evidence` (a harness
guard in `twin/invariants/harness.py`, not hash-pinned in the manifest) planted a claim whose
basis read "planted for the harness guard", and the synthetic-record net refused both of its
options with `RESTS_ON_SYNTHETIC`. Decision (delegated, ADR-0025): the plant is reworded to
"authored for the harness guard", as the builder had already reworded `tests/test_pricing.py`,
rather than narrowing leg 3 so a claim's basis stops counting. Reason: leg 3 is the rule's answer
to the honest case (a claim whose basis says it rests on the synthetic drill), and narrowing it
would make the gate less safe to spare one test string a rewording. The marker-word net stays
uniform across an edge note, a valuation basis and a claim basis. The first record's `--only`
line measured four invariants and was read as the suite; the full suite is what main runs and is
what is measured below.

*Blocking 2, the typecheck main runs.* `tests/test_pricing_threshold.py` binds the result of
`is_synthetic_record` before the `in`. The check re-run is main's own command, `python -m mypy
twin tests conftest.py --ignore-missing-imports --warn-unused-ignores`, not the six-module proxy
the first record cited.

*Minor 1, accepted: a price rests on its admitting path.* `pricing.impacts` folds
`verdict["worst_evidence_grade"]` (the admitting path's worst hop, `None` when the perspective
named the component as its own cash flow) into `rests_on_grade`, the same three legs
`verbs.exposure` already folded. Decision 5 above is amended. Reason: admission is the third
gate and a precondition of the price, so the price rests on it, and the fold can only weaken a
stated grade, never strengthen it. Measured: no golden digest moved (all twelve unchanged), so
no fixture had an admitting path weaker than its propagation path and valuation.

*Minor 2, accepted: the citation names its namespace.* `twin/cli.py` `_cites` admits
`eco-system ticket NNN` (up to three digits) beside `decision ticket NN` (two digits, the twin's
own `.scratch/twin/issues`), and a three-digit number is never read as a twin decision ticket.
The golden-digests citation now reads "eco-system ticket 141 (ADR-0032, decided by eco-system
grilling ticket 30 decision 6) ...", and only `authorised_by` changed. The refusal messages and
the `--authorise` help name both forms. A test in `tests/test_pricing_threshold.py` covers both
namespaces. `_cites` checks the form of a citation, not that the ticket exists, and its
docstring says so.

*Minor 3, accepted: a quoted stamp marks a record.* `twin/synthetic.py` reads a provenance stamp
the way YAML 1.1 reads a boolean (`TRUTHY`: true, yes, on, y and 1 in any case, quoted or not,
and the integer 1), and the module docstring states the limit: any other value marks nothing. A
planted test stamps `synthetic: 'yes'` on the pocket org's drill and the price goes red through
the record leg alone (the regrade names the signal by id and carries no marker word); the
control stamps `synthetic: 'no'` and prices.

*Nothing is less safe.* Each change removes a price (minor 3), lowers a stated grade (minor 1),
or changes a test string, a citation form or a test. No gate is loosened.

**What was measured, 2026-09-26.** On a throwaway merge of the hub branch at `6528c680` onto
`origin/main` at `0c1249d0`: `./bin/twin verify` in full, the check main's `invariants` job
runs: 71 passed, 2 failed, 2 skipped. The two are 44 `drift_window_is_actually_being_sampled`
and 45 `flux_coverage_floor_is_still_reachable`, which fail identically on pristine
`origin/main` at `0c1249d0` today (measured with `--only` on an unmerged worktree; they are the
probe reds, and main's own CI run of 2026-09-25 showed 45 alone because the newest drift sample
was then under a day old). Invariant 59 passes. `tests/test_invariant_suite.py::
test_the_suite_is_green` fails on the same two and nothing else. Main's typecheck command over
`twin tests conftest.py`: no issues in 202 files. `tests/test_pricing_threshold.py` (44 tests)
with the six pricing-side files (`test_pricing.py test_evidence_ladder.py test_perspective.py
test_admission.py test_use_gating.py test_corroboration.py`): 183 passed. The nine schema-side
files: 292 passed. `tests/test_seam1_cli.py`: 44 passed. `verify/twin-evals/
verify-twin-evals.sh`: exit 0, every line PASS or NOT MEASURABLE. `TWIN_CI_ARCH_MATRIX=1 twin
verify --only cross_architecture_determinism`: 12 artefacts byte-identical on arm64.
`identical_pins_identical_bytes` passes with the twelve goldens unchanged. Not run, per the
brief: the full pytest suite and `talk/verify-all.sh`.

**2026-09-26, second review round addressed.** Owner-instructed: the owner wrote on 2026-09-25,
"i'm afk you have all the approvals you need to deliver". That authorises this push to the same
two feature branches and nothing more. The reviewer returned one blocking and four minor
findings; all five are addressed, with one hub code commit (`3c96ca77`), the hub record commit
after it, and one platform commit (`e291139`) on PR #45's branch. The measurement paragraph
after this supersedes the one above.

*Blocking, the admitting path.* `pricing._synthetic_reason` read the propagation path and the
valuation and never `verdict["path"]`, the path `admission.admit` returns as the one that admits
the figure to the declared cash flow. Decision 5 (amended) says the price rests on that path and
folds its worst hop into `rests_on_grade`, so a grade raised on it by a synthetic record was a
grade the price rested on, and the reviewer's plant priced through it (`reporting-service` at
9000.0, admitted over an edge strengthened 3 to 2 on a signal stamped `synthetic: true`).
`twin/synthetic.py` gains `path_rests_on(overlay, hops, label)`, which reads a whole path of
hops the way `rests_on` reads one edge, and `twin/pricing.py` reads both paths through it, the
admitting one labelled "admitting-path hop" in the refusal. The reviewer's plant and its control
are in `tests/test_pricing_threshold.py`: the plant is refused `RESTS_ON_SYNTHETIC` naming the
admitting hop and the drill under the default and under 3, the control (the same regrade citing
dated incident records) prices 9000.0 resting on grade 2. `twin/pricing.py`'s docstring and
`twin/README.md` now say "propagation path, admitting path or valuation" where they said "path
or valuation".

*Minor 1, accepted: `twin exposure` applies the same net.* Decision (delegated, ADR-0025):
`verbs.exposure` reads each valued component's basis and its admitting path through the same
two functions, first and by name, and a hit is a register entry whose reason starts with
`RESTS_ON_SYNTHETIC` and carries no figure. Reason: an exposure figure carries `rests_on_grade`
folded from exactly those two subjects, so the subjects a figure shows its grade from and the
subjects it can be refused on are one set; the alternative, stating that point 4 stops at
`price`, would leave `twin exposure` admitting 400000 on the valuation `twin price` refuses,
which is the inconsistency the reviewer planted. Two plants with controls: the portal's basis
rewritten onto the drill (register entry, `order-service` still admitted, `declared_exposure`
250000.0) and the reporting service admitted over the drill-strengthened edge (register entry
naming the admitting hop; the control admits 30000.0 resting on grade 2). The `scenario-exposure`
golden digest is unchanged, so no fixture figure rested on a marked record. `twin/synthetic.py`'s
docstring gains a section naming which subjects each kind of figure rests on.

*Minor 2, accepted: a precondition for ticket 144 the record had not named.* Under
`Overlay.load(..., pricing_threshold=3)` the tie's gap rule refuses a grade-3 valuation with no
amount ("admits a figure and none is declared"). At `origin/main` tuppence's
`values.payment-fee-income` (`twin/orgs/tuppence/perspectives/tuppence.yaml`, 5deffe6) and
ludlow's `values.plan-administration-fees` (b8e14f7) are grade 3 with no amount, so both served
overlays refuse to load under a declaration of 3 until ticket 144 puts amounts on them from the
comparable filings (driftwood's `checkout-revenue` is grade 2 with an amount and `brand-trust`
grade 5 with none, so it loads under either). That is the pre-existing tie rule and not a defect
here, and no figure is invented for it (ADR-0020); it is a hard precondition for 144 beside the
platform release and the pin moves, and the merge order below names it.

*Minor 3, accepted: the handbook selfcheck measures the twin branch.* `compose/handbook.py
--selfcheck` had no `prices[]` entry of kind `twin`, so its 47 PASS lines never reached the
branch PR #45 added. Seven planted checks now render one at `prices[4]`: `rests_on_grade: 3`
prints "rests on evidence grade 3" and names no absence; null, a boolean, a string, a float and a
missing field each name `prices[4].rests_on_grade` absent and print no sentence; a feed line
carrying the field prints nothing, because only the twin's price rests on a graded chain. 54
checks PASS. The check bites: with the branch skipped the stated-grade check fails, and with the
bool guard dropped the boolean check fails (both broken on purpose in the worktree and restored).
The sentence now names the three subjects the hub folds: the propagation path, the valuation and
the path that admits the figure to the cash flow.

*Minor 4, accepted: the record matches the artefact.* A supersession note now heads the first
"What the hub PR builds" paragraph (49 tests, the re-cited golden, the admitting path).

*Nothing is less safe.* Each change removes a figure (a price or an exposure figure that rested
on a marked record), adds a check to a selfcheck, or changes a record. No gate is loosened and
no golden moved. The synthetic-record prose legs remain a net, not a proof, as the module says.

**What was measured, 2026-09-26, second round.** On a throwaway merge of hub `3c96ca77` onto
`origin/main` at `0c1249d0` (worktree `build/141/fix2-merge`, merge `a1e49b92`): `./bin/twin
verify` in full: 71 passed, 2 failed, 2 skipped, the two being 44
`drift_window_is_actually_being_sampled` and 45 `flux_coverage_floor_is_still_reachable`, which
fail with the same messages on a pristine `origin/main` worktree at `0c1249d0` today (measured
with `--only`, worktree removed after). Main's typecheck command (`python -m mypy twin tests
conftest.py --ignore-missing-imports --warn-unused-ignores`): no issues in 202 files.
`tests/test_pricing_threshold.py` (49 tests) with `test_pricing.py test_evidence_ladder.py
test_perspective.py test_admission.py test_use_gating.py test_corroboration.py
test_seam1_cli.py`: 232 passed. With `twin/pricing.py`, `twin/synthetic.py` and `twin/verbs.py`
stashed back to the previous head, the three plants fail and the two controls pass (3 failed, 2
passed), so the refusals are attributable to the fix. `twin verify --only
identical_pins_identical_bytes --only grade_5_only_path_never_prices --only
mitigation_credit_is_gated_on_corroborated_enactment_not_just_claimed_evidence --only
prefilter_precedes_pricing --only ruin_class_absent_not_priced`: 5 passed, 12 artefacts
identical to the committed goldens. `verify/twin-evals/verify-twin-evals.sh`: exit 0, every
line PASS or NOT MEASURABLE, `cross_architecture_determinism` 12 artefacts byte-identical on
arm64. `tests/test_invariant_suite.py::test_the_suite_is_green`: fails naming the same two probe
reds and nothing else. On the platform branch at `e291139` over `origin/main` 557c153 (a
fast-forward): `compose/handbook.py --selfcheck` 54 checks PASS; `party/party_artefact.py
--selfcheck` selfcheck ok; `PAVC_ESTATE_CLONE=... compose/composition.py --selfcheck` selfcheck
ok. Not run, per the brief: the full pytest suite and `talk/verify-all.sh`.
