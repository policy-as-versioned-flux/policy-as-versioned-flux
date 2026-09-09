# 51 — The supply-constraint actor path and the scored headline forecast

Type: grilling (HITL)
Status: resolved
Blocked by: 11, 23 (both resolved; re-read 2026-09-09)

## Question

Decide whether `nb-refining-capacity -> pq-cryptanalysis` is a twin `needs` edge whose propagation moves the linked capability, given the twin has no velocity or horizon and twin 11 Q1 forbids arithmetic on the ordinal axis. Decide the forecast-book resolution question and pre-registration date for a scenario-library entry and for an override, under reversal 22.

## Notes

Graduated 2026-08-28 from ticket 23's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer (2026-09-09, hub branch `ticket-51-the-supply-constraint-actor-path`, driftwood branch of the same name)

**Blockers re-read first, as ticket 93's own correction requires.** `Blocked by: 11, 23`: ticket 11
is `Status: resolved` and ticket 23 is `Status: resolved`. Neither line had rotted; both were
checked rather than assumed, and this ticket was graduated out of 23's own Answer.

Both decisions are **delegated** under ADR-0025. Ticket 75 Q10 (the twin derives) and ticket 23's
own owner-recorded items are untouched.

### Decision 1 (delegated) — `nb-refining-capacity -> pq-cryptanalysis` is NOT a twin `needs` edge, and no `needs` edge moves a linked capability

The question has two halves and both are answered by measurement, not by argument.

**There is no such edge, in either model.** Measured 2026-09-09 against the estate's served
artefacts: neither `nb-refining-capacity` nor `pq-cryptanalysis` is a component of any twin
overlay or of the world layer under one -- 0 of 3 adopters (driftwood, ludlow, tuppence) -- so
neither can be an end of a twin edge of any type. Both are rows of
`platform/wardley/intel/market-intel.json`, and **both name the SAME `links_risk`**,
`pq-harvest-now-decrypt-later`, which is a FAIR risk id and not a component. Two rows pointing at
one risk is not one row pointing at the other, so what ticket 23 recorded as "the `links_risk`
edge to the capability it constrains" is not in the data. Both rows are printed off platform's own
served ref on every run of the check below, so the finding stays a measurement rather than becoming
a sentence.

**And the ruling would refuse the propagation even where the edge exists**, which is why the check
PLANTS the pair as two components with a `needs` edge between them and exercises the ruling on it.
A `needs` edge is `twin/schema.py`'s `STRUCTURAL_EDGE`: `_refine_edge` refuses `sign`, `lag_days`
and `elasticity` on one, so it asserts no direction of effect and no magnitude. The twin carries no
`velocity` field anywhere and no `horizon` outside a scenario, so there is nothing to move a
coordinate BY and no time to move it OVER -- ticket 23's own named cost, confirmed. What a `needs`
edge moves is REACHABILITY: `twin/blast.py` already follows one backwards to an unpriced set graded
`no-claimed-mechanism`, and `twin/propagate.py` already walks `influences` edges and nothing else.

**What ticket 51 adds, and it is the part neither module covered: a CAUSAL edge moves no coordinate
either.** The evolution axis is an interpretive ordinal judgement about ubiquity and certainty
(twin ticket 11 Q1), not a quantity, and the one operation ecosystem ticket 93 reopened the ordinal
ruling to admit is an ORDER STATISTIC OVER EVIDENCE GRADES -- the weakest grade among a
derivation's own signals. A coordinate move is neither that operation nor on that axis. So a
coordinate moves only by an attributable `position` or `override` claim, which carries provenance
and a role; never by a propagation. `twin/registration.py`'s `admits()` is the callable form
(`priced-causal`, `unpriced-structural`, `no-relation-in-this-model`, `not-in-this-model`) and
`refuse_move()` names each refusal; `MOVES` is a closed set, so a move nobody named is refused
rather than admitted by omission.

**What a propagation asserts, and what it does not.** A `needs` hop asserts: *this component is
downstream of that one and would break without it; nobody has claimed a mechanism.* It does not
assert a magnitude, a price, a probability, an evidence grade or a position -- and it does not
assert that the niobium constraint is irrelevant to post-quantum cryptanalysis. It asserts only
that the twin has no admissible operation for turning a structural dependency into a coordinate,
and that platform's Wardley intel is a different model with different objects. The honest path from
the headline to the twin is the one ticket 23 item 1 already chose and ticket 11 already built:
the headline is a standing SCENARIO in the adopter's own overlay, and what moves is a probability
against that scenario's proposition (ticket 93's apparatus) or an attributable override --
observation as belief update (twin 11 Q4), not `do()` and not an edge traversal.

### Decision 2 (delegated) — the resolution question, and what registers when

**A scenario-library entry's resolution question is its own `proposition` at its own `horizon`,**
answered by an `outcome` record in the same overlay that reaches `origin/main` on or after that
date and is immutable once there (ticket 93 review F2), scored by `twin/scoring.py`. The entry
itself carries no probability, **so the entry pre-registers nothing by existing**: what registers
is a forecast that names it.

**An override does not resolve on its coordinate.** Twin ticket 11 Q1 says an override "can be
scored later like any other forecast"; taken literally that scores `|asserted - revealed|` on the
evolution axis -- arithmetic on an ordinal scale, against an answer key nobody publishes, and the
thing Q1's own guard refuses two paragraphs later. So the sentence is sharpened, not dropped: **an
override is scoreable only THROUGH a falsifiable proposition** -- the proposition of a scenario in
the same overlay that names the component it moves -- and an override no such scenario reaches is
`unscoreable` WITH A REASON (twin 08's own first-class result), never a zero. Q1's purpose survives
where it matters: the human is calibrated against evidence on exactly the same proposition the
twin's own derived probability is scored on.

**And ticket 93's measurement is extended to the leg it did not have. The QUESTION is as rewritable
as the answer.** Ticket 93 made the forecast (F1) and the answer key (F2) immune to a silent
rewrite. Nothing measured the scenario entry, which carries the proposition, the horizon and the
words the question is asked in: edit any of the three after a forecast is registered against it and
every score already taken moves, with nothing on the record saying so. So a scenario entry and an
`override` now register the same way as a forecast -- the LAST first-parent write onto
`origin/main`, `twin/derived_forecast.py::first_reached` **imported and never re-implemented** --
and an entry whose `horizon` is not strictly after its own `at` is refused outright, because
nothing could ever be pre-registered against it.

**What Decision 2 does NOT assert.** It does not assert that a merge date is a wall clock: the
registering date is a committer date, GitHub's when merged there and a laptop's on a fast-forward
push, and the check cannot tell those apart offline. That limit is ticket 93's F10 and it stands
here unchanged. It does not assert that any probability has been scored: none has. And it does not
assert that the driftwood override is right -- only that it is attributable, dated, refusable and
scoreable through a named question.

### Which date it registers on, and why — measured

- **Every scenario-library entry in the estate registered on the day its file last reached its
  adopter's `origin/main`, and every one is in time.** Measured on this branch: driftwood's six on
  **2026-08-31** (`bd19e8c`), ludlow's six on **2026-09-05** (`d092400`), tuppence's six on
  **2026-09-05** (`fca6a58`); 18 of 18 resolvable, 0 rewritten since they arrived, horizons
  2027-08-28 and 2027-09-04.
- **The driftwood override in this ticket's PR registers on nothing yet, and that is the correct
  answer.** It is not on driftwood's `origin/main`; `registered_on()` returns `on_ref: false` with
  "nothing is registered until it is merged there". **When a human merges the driftwood PR it will
  register on the UTC date of that merge commit** -- not on the `2026-09-09` in its own id, and not
  on the date this branch was authored. If its `evolution_position` is edited after it lands, it
  re-registers on the day of that edit. Both dates are printed on every run.
- **The niobium entry's own note was amended in this PR, which re-registers the entry** on the day
  the driftwood PR merges. That is the rule working on its author, not an exception to it: it is
  far inside the 2027-08-28 horizon, and the run prints it as a rewrite.

### What was built

**In driftwood** (branch `ticket-51-the-supply-constraint-actor-path`):

- `twin/orgs/driftwood/claims/supply-constraint-position-2026-09-09.yaml` -- the first `override`
  claim in the estate. `component: tier-one-supplier-relationship`, `evolution_position: 0.55`
  against the 0.625 the `product` band derives, `claimed_by: model-steward` (the role register's,
  which the schema enforces), `evidence_grade: 4` (calibrated judgement recorded AS judgement). Its
  `evidence` says on its face what it asserts, what it does not, that at rung 4 it prices nothing
  on its own, and that its registration date is git's and not the one in its name.
- `twin/orgs/driftwood/scenarios/niobium-supply-shock-2026.yaml` -- `note` gains the resolution
  question and the registration rule, inside the signed artefact rather than in a README beside it.
- `twin/forward-intel/v1/feed.json` re-rendered. **The only thing that moved is the overlay's
  content pin** (`derived_from[].ref`): the priced payload is byte-identical, which is grade 4
  use-gating working -- an override at a rung that cannot price did not price.

**In the hub** (branch of the same name):

- `twin/registration.py` -- `admits`/`refuse_move`, `resolution_question`, `override_resolution`,
  `registered_on`, `read_model`, and the `check` the gate runs. Its own module for the reason
  `blast.py` is not part of `model.py`: this is a ruling over the graph and over git history, not
  part of loading a model. The git reads are `derived_forecast`'s, imported.
- `verify/twin-evals/verify-scenario-registration.sh` and `verify/twin-evals/registration_fixture.py`
  -- discovered by `talk/verify-all.sh`, manifest row `estate-observation` with TWO declared waits
  and FIVE undeclared could-not-looks (no unit carrying a twin overlay; and the wrapper's four
  interpreter and environment SKIPs), all five red, which is `verify-derived-forecast.sh`'s
  precedent.
- `tests/test_registration.py` -- 21 tests.

**One defect found by re-reading this branch as an adversary, before it was pushed.**
`read_model` keyed its path table by `id` ALONE. Ids are unique inside a collection and nothing
makes them unique across collections, so a claim and a scenario sharing an id would have made
`repo_relative` hand git the wrong file -- and a registration date read off the wrong file is
exactly the class of defect this module exists to close. The table is keyed by `(collection, id)`
now, and `test_a_claim_and_a_scenario_sharing_an_id_do_not_share_a_path` holds it.
- The record: ADR-0024 point 6, twin tickets 08 and 11 (the same three ticket 93 amended), ticket
  23's four corrected claims, this file, the map line.

### Which check grades it

`verify/twin-evals/verify-scenario-registration.sh`. Today: offline half PASS over the planted
fixture (and every line of it says fixture), then on the real estate `SKIP: 18 of 18
scenario-library entries on refs/remotes/origin/main carry a resolution question and a registration
date, and 0 override claim has reached refs/remotes/origin/main of any adopter (driftwood, ludlow,
tuppence): the headline skill's override PR (ecosystem ticket 23) has not been merged`, exit 3 --
the declared wait, which the driftwood PR closes when a human merges it.

### Red first, exact

| seam | red, measured against `origin/main` `0c1cb54` | green |
| --- | --- | --- |
| (a) the `needs` edge propagating what the ruling does not admit | `python -m twin.registration admits ... nb-refining-capacity pq-cryptanalysis` -> `No module named twin.registration`; `grep -c evolution_position twin/blast.py twin/propagate.py` -> `0` and `0`; and the whole planted overlay validates: `RED ACCEPTED component pq-cryptanalysis.yaml` (carrying `needs: [nb-refining-capacity]`) and `RED ACCEPTED claim planted-supply-position.yaml` (an override moving that component's coordinate). Nothing in the estate had an answer to what a `needs` edge moves. | `unpriced-structural -- moves reachability`, with `evolution_position`, `evidence_grade`, `weight`, `probability`, `magnitude` and `price` each refused by name, a priced causal edge refused a coordinate too, and `everything` refused as `is not one of the things a relation could move` |
| (b) an entry whose pre-registration would be later than its own outcome date | `RED ACCEPTED scenario planted-same-day-2026.yaml` -- `twin/schema.py` validates `at: 2026-01-01` with `horizon: 2026-01-01` cleanly, so it merges | `FAIL: driftwood: scenario 'planted-same-day-2026': horizon 2026-01-01 is not after its own at 2026-01-01. Pre-registration is strictly before the outcome date (ecosystem ticket 93), and this entry was authored on or after its own, so nothing could ever be registered against it` |
| (c) an override whose number changes after the entry landed | on `origin/main`, `first_reached` is called for `twin/forecasts/*.forecast.yaml` and `outcomes/` and for nothing else (`grep -rn first_reached twin/ verify/ tests/`), so no override and no scenario was ever measured for registration at all | `FAIL: driftwood: override 'planted-supply-position' registered on 2026-07-20, not before 2026-06-30: reached refs/remotes/origin/main 2026-02-01T00:00:00Z in d5de4af, last written there 2026-07-20T00:00:00Z in c9d28fa (rewritten after it landed)` -- and the same for a QUESTION rewritten after its horizon |

The RED for (b) is re-run inside the check itself (`schema.validate('scenario', ...)` on the
same-day entry), so the refusal cannot quietly stop being a refusal of something real.

### Placement, verified by planting

Ticket 93's decision -- a forecast lives at the ADOPTER's `twin/forecasts/`, never under
`twin/orgs/<org>/` -- was verified rather than repeated. A forecast planted at
`twin/orgs/driftwood/forecasts/2026-09-09-planted.forecast.yaml` in driftwood's worktree turned
driftwood's own twin gate red: `twin.model.ModelError: orgs/driftwood: nothing loads forecasts, so
nothing validates it. This unit reads components, world_models, signals, claims, scenarios,
outcomes, people, edges, perspectives, regrades, responses, own_data, causal_accounts,
enforcement_moves, behavioural and refuses to ignore anything else`, and `verify-twin-overlay.sh`
went `FAIL: 1 twin-overlay check(s) observed false`. The plant was removed. The override this
ticket writes lands in `twin/orgs/driftwood/claims/`, which IS a loaded collection, and the overlay
re-renders clean.

### Waits on the owner

- **A human merging the driftwood pull request.** Until then no `override` claim is on any
  adopter's `origin/main`, `verify-scenario-registration.sh` says SKIP by name, and the override's
  pre-registration date does not exist. That merge is the operation the check grades; nothing here
  performs it.
- **No forecast was written, and that is deliberate.** Ticket 93's own wait stands: a real derive
  run spends the owner's tokens under the owner's login. A forecast file whose `run` block says the
  local clock produced it, written by hand because the clock has not run, would be a faked
  observation, and this ticket does not lift that wait to make its own numbers look better.
- **The first score still waits on the calendar**: the earliest horizon in the estate is
  2027-08-28, and no outcome can be honestly recorded before then.

### Not done

- Nothing is scored. The apparatus for scoring an override exists and names the proposition it
  would be scored through; no proposition in this estate has resolved.
- The reopened comparison stays as narrow as ticket 93 left it. This ticket makes no new operation
  on grades admissible; it rules out one that was never admissible and had never been refused.
- The check reads a scenario's registration but cannot compare it to the registration of a forecast
  that names it, because no forecast exists on any adopter's main. The rule that a forecast must
  register AFTER the question it names is stated in the record and is not yet a leg of the check;
  it becomes measurable on the day the first forecast merges.
- `twin/schema.py` is unchanged: a scenario's `horizon` is still optional and a same-day horizon
  still validates where it is authored. The refusal lives in the gate, over `origin/main`, which is
  the served surface. Tightening the schema would refuse it earlier and is a separate change with
  its own blast radius across every committed scenario.
- The clock-provenance limit (ticket 93 F10) is inherited unchanged: a registering committer date
  merged through GitHub is GitHub's and a fast-forward push carries the laptop's, and this check
  cannot tell them apart offline either.
