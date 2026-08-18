# 91 — Demo slice: the rendered artefact decision ticket 22 actually asked for

**What to build:** `demo-slice` is graded `stub`, 0/4 — the biggest single gap in this batch, and the
one build ticket 77 named explicitly in its own "what still isn't true" section. Ticket 77 built the
honesty *machinery* (depth grades travel automatically, the does-not-do register, thesis sequencing
in `beat-sequence.sh`) but deliberately did not build the demo-slice artefact itself.

Today the demo scripts (`twin/demo.sh`, `twin/beat-sequence.sh`, and the three beat scripts) run the
real mechanics and narrate to stdout, but produce no single artefact carrying the four things these
ACs ask for as first-class, checkable content — the thesis, the subject rationale, the boundary, and
the AC-to-ticket mapping all currently live scattered across comments, READMEs, and ticket prose.

Run this last, after every capability-closing ticket in this batch, so its boundary block (AC 3) and
AC-to-ticket mapping (AC 4) reflect the system's real final depth grades rather than a snapshot from
partway through this batch.

**Blocked by:** 90

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 22 (`.scratch/twin/issues/22-demo-slice.md`) in full. Build ticket
77 in full, especially its "what still isn't true" section. `twin/capabilities/demo-slice.yaml` for
exact AC text. `twin/does_not_do.py`, `twin/grades.py`, `twin/beat-sequence.sh`, the three beat
scripts.

- [x] AC 1 — "A single demonstrable thesis, stated in one sentence." One sentence, in one place, in
      a structured artefact — not distributed across comments and echo statements.
      `twin/demo_slice.py`'s `THESIS` constant — decision ticket 22's own resolved Q1 answer,
      verbatim, in one place. `summary()` composes it into the artefact `twin demo-slice` emits;
      `tests/test_demo_slice.py::test_summary_composes_all_four_pieces` asserts the body carries it
      unchanged.
- [x] AC 2 — "Subject + scenario selection, with rationale." Collect the Royal Mail / Netflix / Intel
      rationale already written across decision ticket 22 and build tickets 71/73/75 into the
      artefact's own data, not by reference only.
      `twin/demo_slice.py`'s `SUBJECTS` — each subject's `org`, `beat`, `carries`, `role` and
      `rationale`, collected as data rather than left in scattered prose.
      `tests/test_demo_slice.py::test_summary_composes_all_four_pieces` asserts all three subjects
      (royal-mail, netflix, intel) carry a non-empty rationale.
- [x] AC 3 — "An explicit shown/stubbed/absent boundary and how it is surfaced." Wire
      `does_not_do.published()` and `Capabilities.load()`, filtered to the capabilities the demo
      sequence actually touches, into a boundary block scoped to this specific sequence — the
      mechanism already exists (build ticket 77); this ticket assembles it for the demo, not the
      whole system.
      `twin/demo_slice.boundary()` computes `shown` (`TOUCHED_CAPABILITIES`, read from the same
      `CAPS_*` constants the three beat scripts' own verbs already carry, never retyped), `stubbed`
      (the does-not-do register's own entries, scoped to those capabilities) and `absent` (every
      other loaded capability). Printed by `twin demo-slice` and asserted by
      `tests/test_demo_slice.py::test_boundary_shown_and_absent_partition_the_loaded_capabilities`
      and `::test_boundary_stubbed_entries_are_scoped_to_touched_capabilities_only`.
- [x] AC 4 — "Acceptance criteria for the slice, tied back to the owning tickets' criteria." A table
      mapping this decision ticket's own four ACs to the build tickets that realise them (71, 73, 75,
      77, and this ticket itself).
      `twin/demo_slice.py`'s `ACCEPTANCE_CRITERIA` — asserted by
      `tests/test_demo_slice.py::test_summary_composes_all_four_pieces` (all four indices present,
      each naming at least one build ticket).

Built `twin/demo_slice.py` in the shape `does_not_do.py` already established: a pure `summary()`
function composing the four pieces above, exposed as a derived `Artefact` via a new CLI verb
(`twin demo-slice`), wired into `beat-sequence.sh` as a final step that emits and prints this
summary rather than only echoing prose. `twin/capabilities/demo-slice.yaml` closes at 4/4, `full`
— the thirteenth and last shipped capability to reach it, moving the aggregate to **73 of 73**.

## Also found and fixed

Same discipline build tickets 77 and 78 name for themselves: findings recorded and fixed, not
glossed over.

- **Real consequence, not a bug: closing the last checklist moves every artefact's bytes.**
  `demo-slice` reaching `full` changes `Capabilities.load().digest`, which travels in every
  artefact's `pins.tool.capabilities_digest` — so `identical_pins_identical_bytes` failed against
  the twelve committed golden digests the moment the checklist closed, exactly as it did the last
  time a checklist closure moved the digest (build ticket 90). Fixed the only way this invariant
  allows: re-blessed via `twin verify --bless-goldens --authorise "decision ticket 22 — demo-slice
  closes its own checklist (build ticket 91)..."`, the same gate build ticket 90 used.
- **Spec axis, real gap.** Two tests in `tests/test_grades.py` hardcode the exact set of
  capabilities graded `full`, by design (the walking skeleton must not claim `full` on say-so) —
  but that means every ticket that closes a capability must extend them or the suite would stay
  green on a false claim about which capabilities are complete. Both renamed and extended to add
  `demo-slice` as the thirteenth and last: `test_..._provenance_honest_build_and_demo_slice_have_
  earned_full` (was `..._and_honest_build_have_earned_full`) and its companion
  `..._are_the_shipped_capabilities_at_full`. The first test's own closing assertion strengthened
  from `assert "full" not in grades.values()` to `assert not grades` — every capability the test
  named is now popped, and an empty dict is a stronger check than one that would silently pass
  even by dropping a name.
- **Spec axis, real gap.** `tests/test_royal_mail_beat.py::test_the_demo_slice_grade_is_computed_
  from_decision_ticket_22` asserted `STUB` and its own docstring stated "it opens at stub" — true
  when build ticket 72 wrote it, false once this ticket ran. Fixed to assert `FULL` and narrate the
  ticket that closed it, rather than leave a passing test asserting last month's grade.
- **Spec axis, real gap.** `twin/beat-royal-mail.sh` step 5's own narration ("it opens at stub
  because three of four beats do not exist") and closing echo ("none of them is full") were
  hand-typed claims about a computed grade — precisely the failure mode decision ticket 22 Q3
  exists to rule out, now stale rather than caught by anything, since nothing checks prose against
  the number it echoes. Fixed to state what is true today; the underlying grade itself was never
  wrong, only the sentence describing it.
- **Standards axis, real gap, fixed — but pre-existing, not this ticket's own regression.**
  `twin/README.md`'s capability-table paragraph claimed "most artefacts stay `partial`" even where
  the named capabilities are `full`; on inspection this was already inaccurate *before* this
  ticket touched it — twelve of thirteen capabilities were already `full`, and no artefact's own
  `CAPS_*` list ever cites `demo-slice`, so no ordinary artefact was ever kept at `partial` by it.
  Fixed while recomputing the paragraph for the new 73/73 count (see README's "What is honestly
  built") rather than left to compound — touching the sentence without fixing a claim already
  false in front of it would have been the same drift the review discipline exists to catch.
- **Judgement call, not changed.** `demo_slice.artefact()`'s own `depth` block is scoped to
  `TOUCHED_CAPABILITIES` (the capabilities the three beat scripts actually exercise) rather than
  every loaded capability, even though `boundary()`'s own `absent` list names the rest. This
  matches AC 3's own instruction ("scoped to this specific sequence") and `does_not_do.py`'s
  precedent (its own `depth_block` covers exactly what its register surveyed); an artefact whose
  envelope claimed to be "produced by" a capability nothing in the sequence actually touches would
  be the wrong direction of overclaim for a demo built on this thesis.
- **Judgement call, not changed.** No new harness guard was added. Ticket 77's own precedent
  (`does_not_do_register_is_generated_never_typed`, `the_demo_sequence_earns_credibility_before_
  it_spends_it`) exists because those properties needed checking against live source text with no
  other enforcement. `demo_slice.py`'s own four pieces are already covered by
  `Capabilities.load()`'s existing drift guard (`_validate_against_ticket`, which refuses a
  checklist whose text has drifted from decision ticket 22) plus `tests/test_demo_slice.py`'s seven
  tests; a guard duplicating what those already check would be the "third copy"
  `beat-royal-mail.sh` and ticket 77's own review both decline to write.

## What still isn't true

`does_not_do_register_is_generated_never_typed` (build ticket 77) now **skips** rather than
passes: its own live-read proof needs at least one unchecked criterion to flip, and with all
thirteen capabilities `full` there is none left in the shipped tree. `twin verify` reports this as
"skipped and not faked", the same honest-skip discipline the manifest already requires — not a new
gap this ticket leaves, just a fact worth naming so a future reader does not mistake the skip for
a broken guard. The two pre-existing failures named below (`drift_window_is_actually_being_
sampled`, `flux_coverage_floor_is_still_reachable`) are unrelated to this ticket and unchanged by
it — see build ticket 78 and the Flux verdict memory for their own history.

One flaky, pre-existing, order-dependent test was observed during this ticket's own full-suite
runs and investigated: `tests/test_seam1_cli.py::test_an_attestation_sidecar_accompanies_every_
artefact` failed once under full-suite `pytest-xdist` parallel execution but passes standalone and
as its whole file every time it was run in isolation (below). Nothing in this ticket's diff touches
signing, environment variables or attestation status text — `demo_slice.py` reads only
`Capabilities` and `does_not_do`, neither of which this test's own path exercises — so this is an
existing order/worker-pollution flake in the suite's xdist configuration, not a regression this
ticket introduced. Left unfixed as out of this ticket's scope; worth a future ticket if it recurs.

## Evidence

```
.venv/bin/python -m pytest -q tests/test_demo_slice.py -v
  7 passed in 1.01s
  test_touched_capabilities_is_a_real_subset_naming_demo_slice PASSED
  test_boundary_shown_and_absent_partition_the_loaded_capabilities PASSED
  test_boundary_stubbed_entries_are_scoped_to_touched_capabilities_only PASSED
  test_demo_slice_itself_closes_its_own_unchecked_entries PASSED
  test_summary_composes_all_four_pieces PASSED
  test_the_artefact_is_derived_and_depth_scoped_to_touched_capabilities PASSED
  test_artefact_accepts_a_precomputed_body_without_recomputing PASSED

.venv/bin/python -m pytest -q tests/test_demo_slice.py tests/test_does_not_do.py \
  tests/test_beat_sequence.py tests/test_grades.py tests/test_royal_mail_beat.py
  42 passed in 12.84s

.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
  Success: no issues found in 158 source files

.venv/bin/python -m pytest -q          # full suite, clean baseline BEFORE this ticket's changes
                                         # (working tree stashed to twin/beat-sequence.sh, twin/cli.py,
                                         # tests/test_demo_slice.py, twin/demo_slice.py during this run)
  1 failed, 1535 passed in 341.87s (0:05:41)
  FAILED tests/test_invariant_suite.py::test_the_suite_is_green  — known, pre-existing (drift/coverage)

.venv/bin/python -m pytest -q          # full suite AFTER this ticket's changes, capability closed,
                                         # golden digests re-blessed, dependent tests updated
  2 failed, 1541 passed in 412.05s (0:06:52)
  FAILED tests/test_seam1_cli.py::test_an_attestation_sidecar_accompanies_every_artefact
    — investigated: passes standalone and as its whole file every time (see below); an
      order/worker-pollution flake under full-suite pytest-xdist, unrelated to this ticket's diff
  FAILED tests/test_invariant_suite.py::test_the_suite_is_green — same known pre-existing failure

.venv/bin/python -m pytest -q tests/test_seam1_cli.py::test_an_attestation_sidecar_accompanies_every_artefact
  1 passed in 2.96s
.venv/bin/python -m pytest -q tests/test_seam1_cli.py
  44 passed in 23.46s

.venv/bin/python -m twin verify --bless-goldens --authorise "decision ticket 22 — demo-slice \
  closes its own checklist (build ticket 91), changing the capabilities digest every artefact's \
  pins carry"
  golden digests -> golden-digests.json (12 artefacts)

.venv/bin/python -m twin verify
  RESULT: 69 passed, 2 failed, 3 skipped (0 pending invariants, 3 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: known, pre-existing (build ticket 78 / Flux verdict)
  FAIL flux_coverage_floor_is_still_reachable: known, pre-existing (build ticket 70's finding 1)
  SKIP does_not_do_register_is_generated_never_typed: "every loaded capability is already `full`;
    there is nothing left to check off" — honest skip, not a fake pass (see "What still isn't true")
  PASS the_demo_sequence_earns_credibility_before_it_spends_it

bash twin/beat-sequence.sh
  ... (all three beats PASS as before; final step:)
  ===> SLICE — the rendered artefact decision ticket 22 asks for: thesis, subjects, boundary, ACs.
  ==> demo slice: we can model an organisation's landscape, anticipate its movements, prove when
      we're wrong, and price the response wherever it lives
    subject  royal-mail   falsifiability (b), retrospective — proves the twin can be checked
    subject  netflix      versioned governance (c), concluding in the one-currency comparison (a)
             — shows the whole engine
    subject  intel        falsifiability (b), live and forward — shows the twin will be checked next
    shown    9 capabilities: causal-layer, currency-regimes, demo-slice, domain-model, enactment,
             provenance, scenario-engine, sense-move, synthetic-substrate
    stubbed  0 unchecked criteria within them
    absent   4 capabilities never touched: ethics-gate, forecast-book, honest-build, twin-inside-twin
    AC 1  A single demonstrable thesis, stated in one sentence.  -> build ticket(s) 77, 91
    AC 2  Subject + scenario selection, with rationale.  -> build ticket(s) 71, 73, 75, 91
    AC 3  An explicit shown/stubbed/absent boundary and how it is surfaced.  -> build ticket(s) 77, 91
    AC 4  Acceptance criteria for the slice, tied back to the owning tickets' criteria.  ->
          build ticket(s) 91
  demo-slice-summary -> .../demo-slice.json
    depth        full
      (all nine touched capabilities: full)
  PASS: the demo sequence ran b -> b -> c -> a. ...

grep -l '**Status:** done' .scratch/twin/build/*.md | wc -l
  88   (of 92 — matches twin/README.md's recomputed banner)
```
