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
platform `ticket-141-party-declares-pricing-threshold` (the party schema) and hub
`ticket-141-declared-pricing-threshold` (the twin). The platform PR merges first. A platform tools
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

**What the hub PR builds.** `twin/evidence.py`: `DECLARABLE_THRESHOLDS = (2, 3)`,
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
5. *The weakest grade*: `rests_on_grade` on each priced impact is the weaker of the path's worst
   hop and the valuation; on a credit, the weakest of the impact, the claim and the corroborated
   enactment; on an exposure entry, the weaker of the valuation and the admitting path. The
   `gating` block carries `applied` (both thresholds and their basis) only in the bodies that
   price and expose; blast and propagation bodies are byte-identical to before.
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
