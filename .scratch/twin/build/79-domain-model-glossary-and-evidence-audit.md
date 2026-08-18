# 79 — Domain-model: the named ontology, and an evidence audit of the other six ACs

**What to build:** Decision ticket 07 is resolved at the design level but `domain-model` is graded
`partial` at 1/7 in `twin/capabilities/domain-model.yaml`. A prior research pass across the current
code found that five of the six unchecked ACs look already satisfied by code built since ticket 07
was resolved — the checklist is stale, not the implementation. Verify each claim below live before
ticking anything; do not tick on the strength of this ticket's own say-so.

**Blocked by:** none

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 07 (`.scratch/twin/issues/07-twin-domain-data-model.md`).
`twin/capabilities/domain-model.yaml` for the exact AC text and current `checked` state.

- [x] AC 1 — "A named core ontology (entity types + relationship types + the backbone) in ubiquitous
      language." No single named artefact collects this today; `twin/schema.py`'s `EDGE_TYPES` and
      entity `Schema`s exist but are not assembled into one named, checked ontology. This is real
      new work — build it as a derived artefact generated from `schema.py`'s own definitions (not a
      hand-typed doc that can drift out from under the code), the same shape `does_not_do.py` takes
      against `grades.py`.
      **Closed.** `twin/ontology.py` — `entity_types()`, `relationship_types()`, `backbone()`, all
      read straight out of `schema.SCHEMAS`/`EDGE_TYPES`/`COMPONENT_KINDS`/`EVOLUTION`, published as
      a `domain-model-ontology` DERIVED artefact via `twin ontology`. `tests/test_ontology.py::
      test_every_schema_kind_is_a_named_entity_type` and `test_every_edge_type_is_classified_into_
      exactly_one_family` assert this stays a live read rather than a snapshot.
- [x] AC 2 — "The layering decision (one graph vs coupled) with the seam(s) defined." Candidate
      evidence: `twin/model.py`'s `World`/`Overlay` split and `DirectionError` enforcement, citing
      decision ticket 07 Q1b in its own docstring, built by build ticket 04. Confirm this actually
      answers the AC as worded before ticking; cite the exact test that exercises the seam.
      **Confirmed, already satisfied.** `enforce_direction`/`check_direction` refuse any repository
      where the world layer references an overlay, live-exercised by
      `tests/test_seam2_model.py::test_the_world_layer_may_never_reference_an_overlay` (plants a
      violation, asserts it is caught). The stale checklist, not the implementation.
- [x] AC 4 — "The temporal/versioning model + how scenarios are represented." Candidate evidence:
      `twin/repo.py`'s `UnitRef`/`Pin` (git-commit-pinned) and `twin/schema.py`'s `"scenario"`
      schema requiring a regime per execution. Confirm and cite the exercising test.
      **Confirmed, already satisfied.** `UnitRef`/`Pin` git-commit-pin the world layer and each
      overlay as independently versioned units, exercised by `tests/test_seam2_model.py::
      test_an_overlay_stays_pinned_while_the_world_moves`. A scenario deliberately carries no
      regime field; every execution must name one with no default (`twin/regimes.py::require`),
      exercised by `tests/test_regimes.py::test_a_scenario_cannot_declare_its_own_regime` and
      `test_an_execution_with_no_regime_is_refused_rather_than_defaulted`. (The draft's phrasing —
      "the scenario schema requiring a regime" — had it backwards: the schema refuses one, the
      execution requires one. The AC's substance, temporal versioning + how scenarios are
      represented, holds either way.)
- [x] AC 5 — "The representation/format decision (reuse vs custom) with what's authored vs derived."
      Candidate evidence: `twin/artefact.py`'s `AUTHORED`/`DERIVED` constants and their enforcement.
      Confirm and cite.
      **Confirmed, already satisfied.** `attest.py` refuses a human signature on a `DERIVED`
      artefact and requires one on an `AUTHORED` one, exercised by
      `tests/test_repo_and_envelope.py::test_a_derived_artefact_refuses_a_human_signature` and
      `test_an_authored_artefact_carries_the_signature_that_gives_it_accountability`.
- [x] AC 6 — "Where the £/risk, people, assets and signals attach to the graph." No single written
      mapping exists; `model.py`'s `OVERLAY_COLLECTIONS` (people, signals, claims, scenarios,
      causal_accounts, enforcement_moves, ...) and `schema.py`'s collection kinds are the candidate
      evidence, but they need a short authored mapping tying each named thing (£/risk, people,
      assets, signals) to its attachment point — likely folds into AC 1's ontology artefact rather
      than a second one.
      **Closed, folded into AC 1's artefact as drafted.** `twin/ontology.py`'s `ATTACHMENT` table
      names all four things and their schema kinds; `_check_attachment_vocabulary()` refuses to
      publish if a named kind is not real, so the mapping cannot silently drift the way a doc
      would. `tests/test_ontology.py::test_ac6_names_exactly_the_four_things_the_ticket_names` and
      `test_ac6_attachment_vocabulary_catches_a_renamed_schema_kind` (the guard actually bites).
- [x] AC 7 — "Exercised against Netflix + Intel (does the model actually hold each subject?)."
      Candidate evidence: `twin/fixtures.py`'s `build_netflix_org` and `build_intel_org`, exercised
      by build tickets 73 and 75. Confirm both fixtures actually exercise the model's ontology (not
      just its £ engine) before ticking, and cite the tests that load and validate each.
      **Confirmed, already satisfied.** Both fixtures build full value chains of typed components
      (kinds `capability`/`activity`/`practice`/`data`), structural `needs` edges and causal
      `influences` edges positioned on the evolution axis. `Overlay.load`'s own
      `_check_references()` validates the whole ontology — not only the £ path — against both on
      every load, and `tests/test_netflix_beat.py::test_the_dated_state_carries_no_layer_that_
      postdates_it` asserts the causal layer in `.graph().edges` genuinely appears/disappears
      across a rewind, which only happens if the ontology (not just pricing) is real.

If any of the five "candidate evidence" ACs turns out NOT to be genuinely satisfied on inspection,
say so plainly in this ticket and scope the real gap — do not force a tick to make the number look
better. Depth-grade honesty is the whole point of this project; a false tick here is worse than a
stub label.

## What was actually true on inspection

The ticket's own draft was right about the shape of the gap: one real gap (AC 1, folding in AC 6),
five stale ticks. All five candidate-evidence ACs (2, 4, 5, 7) were genuinely satisfied by code
already in the tree — confirmed by reading each cited module and running the exercising test
before ticking, not assumed from the draft's prose. `domain-model` moves from 1/7 (`partial`) to
7/7 (`full`) — the first capability in this project to reach `full`.

## Also found and fixed

- **Standards axis.** `ontology.artefact()` initially always recomputed `published()` itself, so
  `cmd_ontology` in `twin/cli.py` paid for the walk over `schema.SCHEMAS` twice (once to print,
  once inside `artefact()`) — the same waste `does_not_do.artefact` was built to avoid by taking an
  optional `body` parameter. Fixed: `ontology.artefact()` now takes the same `body` parameter and
  `cmd_ontology` passes its already-computed body through, matching the shape this ticket was asked
  to copy.
- **Standards axis.** `tests/test_ontology.py`'s people-attachment test asserted
  `model.OVERLAY_COLLECTIONS` is truthy as filler "sanity", which is not a claim about anything —
  its own docstring promised to confirm `model.py`'s graph-building code treats the same
  `PERSON_EDGES` this artefact cites, and did not check that. Fixed: the test now inspects
  `model.Graph.bus_factor`'s own source for the `PERSON_EDGES` name it must read, so a future
  hand-typed parallel list in `model.py` that disagreed with `schema.PERSON_EDGES` would fail it.
- **Spec axis / repo-wide consistency.** Ticking `domain-model` to `full` is a real, structural
  change: two existing tests (`tests/test_grades.py::test_the_shipped_capabilities_are_all_
  partial_or_stub` and `test_the_shipped_capabilities_never_reach_full`) asserted no shipped
  capability would ever reach `full` — true when written, and now false by design, not by drift.
  Fixed in place rather than deleted: both now assert `domain-model` is the one exception and every
  other shipped capability still is not, preserving the guard's real intent (no capability may
  claim `full` on say-so) without pretending honest, fully-cited progress cannot happen. A
  docstring nearby in the same file ("the shipped capabilities all happen to sit at the same grade
  today") was stale for the same reason and corrected.
- **Spec axis / downstream consequence.** Raising `domain-model`'s depth block changes the bytes of
  every artefact whose `depth` cites it, which moved every committed artefact digest away from
  `twin/invariants/golden-digests.json`'s recorded values (`identical_pins_identical_bytes` went
  red). This is the documented, expected consequence of a real capability-grade change — build
  ticket 72 hit the identical situation adding the `demo-slice` checklist and re-blessed for the
  same reason. Re-blessed via `twin verify --bless-goldens --authorise "decision ticket 07 — ..."`
  (see Evidence below); no scoring rule, serialisation or engine output changed.
- **Judgement call, not fixed.** `twin/README.md`'s "Run it" quick reference did not list
  `does-not-do` before this ticket either (an existing, pre-79 gap, not one this ticket's diff
  introduced) — noted rather than silently fixed under a different ticket's scope; `ontology` was
  added beside `constraints` since this ticket added that command.

## What still isn't true

Nothing. All seven ACs are genuinely closed with live citations; `domain-model` is `full`. What
remains true and unrelated: `Asset`/`DataAsset` still has no dedicated schema kind (a `component`
of kind `data` realises it, which is what decision ticket 07's own Q1 resolution — "not separate
models" — already says should happen; `twin/README.md`'s "What is not built" section is corrected
to say so rather than imply a missing schema blocks anything).

## Evidence

```
$ .venv/bin/python -c "
from twin.grades import Capabilities
caps = Capabilities.load()
g = caps.require('domain-model')
print(g.grade, sum(1 for c in g.criteria if c.checked), '/', len(g.criteria))
"
full 7 / 7

$ .venv/bin/python -m twin ontology --out /tmp/ontology-artefact.json
==> ontology: 20 entity types, 5 relationship types, 4 attachment points named
  ... (20 entity rows, 5 relationship rows, 4 attachment rows) ...
domain-model-ontology -> /tmp/ontology-artefact.json
  attestation  ontology-artefact.json.att.json (unsigned — no signing key present)
  sha256       5c4b0ee67e84ac6751126ac22ccdb31578b531f2a71e26508cf9921d9b349de9
  depth        full
    domain-model       full     7/7 of decision ticket 07  unchecked: -

$ .venv/bin/python -m pytest -q tests/test_ontology.py
12 passed in 0.83s

$ .venv/bin/python -m pytest -q tests/test_grades.py tests/test_ontology.py
29 passed in 0.84s

$ .venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
Success: no issues found in 150 source files

$ .venv/bin/python -m pytest -q
1455 passed, 1 failed in 302.32s (0:05:02)
FAILED tests/test_invariant_suite.py::test_the_suite_is_green
  — the single pytest-level failure aggregates two pre-existing, known, unrelated invariant reds
  (drift_window_is_actually_being_sampled, flux_coverage_floor_is_still_reachable — both red since
  2026-08-16 per the owner's own recorded decision not to restart the probe; confirmed present with
  this ticket's changes fully reverted via `git stash`, run in isolation before any of this
  ticket's code existed). Same failure identity, same count, as before this ticket; nothing this
  ticket touched moved it.

$ .venv/bin/python -m twin verify --bless-goldens --authorise "decision ticket 07 — build ticket 79
  closes domain-model's remaining acceptance criteria (1, 2, 4, 5, 6, 7), so every artefact's
  capabilities_digest and depth block move; no scoring rule, serialisation or engine output changed"
golden digests -> golden-digests.json (12 artefacts)
  ... (12 digest lines) ...

$ .venv/bin/python -m twin verify
RESULT: 68 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: ... (known, pre-existing)
  FAIL flux_coverage_floor_is_still_reachable: ... (known, pre-existing, see project memory
  flux_verdict_unmeasured — the owner's own recorded decision, 2026-08-16)
```
