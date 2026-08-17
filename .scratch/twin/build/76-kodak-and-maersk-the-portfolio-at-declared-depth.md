# 76 — Kodak and Maersk: the portfolio at declared depth

**What to build:** The portfolio subjects, each carrying a depth grade and upgradable on its own independent track.

They are a ticket rather than an assumption because an earlier draft had them in the spec's Subjects
section and in no ticket at all — which is how a subject silently vanishes. If they are not built,
they go in the does-not-do register **by decision**, not by omission.

**Blocked by:** 70

**Status:** done (2026-08-17). Both subjects built at declared `stub` depth, each on its own
independent track; no outcome/backtest for either, by decision (see checklist AC 3).

**Reading list:** Decision tickets 01, 06. Spec: Implementation Decisions, Subjects.

- [x] Both subjects present at a declared, computed depth grade — `stub` is an acceptable outcome, silence is not.
      `twin/fixtures.py`'s `build_kodak_org` and `build_maersk_org`, registered in `BUILDERS` as
      `"kodak"` and `"maersk"`. Each is a real, schema-valid, isolated model repository: one
      component, one pre-signal world model, one `would-the-twin-have-flagged-it` scenario with
      its required `affected_parties`, and two real, dated, cited signals bound to the component
      by grade-1 claims. Both load (`Overlay.load`), validate (`twin validate`), sweep
      (`build_standing_library` → `schedule.sweep`, zero failures, both orgs present in
      `orgs_run`) and run (`twin run --org kodak|maersk --scenario
      would-the-twin-have-flagged-it`, exit 0, a reproducible forecast bundle each — verified by
      hand and by `tests/test_kodak_maersk.py::test_a_run_succeeds_and_reproduces_from_its_own_pins`).
      No outcome is authored for either — named explicitly in both docstrings and enforced
      structurally by `test_no_outcome_is_authored`, not left to prose. That is `stub`: present
      and computable, not silent, and honestly short of `full`.
      **Naming the word carefully**, since `twin/grades.py` also defines a formal `STUB` —
      that machinery grades *capabilities* against an *owning decision ticket*'s acceptance
      criteria (AC 5 below establishes neither subject has one), so it does not compute a value
      for these orgs at all. "`stub`" here is the ticket's own plain-English vocabulary (this
      ticket's own opening line: "`stub` is an acceptable outcome, silence is not"), not a
      `twin/grades.py`-derived grade — there is no such grade to derive for an org. The
      `depth` block `twin run` prints for each (see "What is honestly true now") is a different,
      unrelated figure: the *engine's own* capability maturity, identical for every org it runs
      against, not a measure of how much of Kodak or Maersk is modelled.
- [x] Each is on an independent upgrade track, not gated on the flagships.
      Two separate isolated git repositories built by two separate functions, sharing nothing
      with Netflix/Intel/Royal Mail beyond the `_write`/`git` helpers every fixture in this file
      already shares. Structurally proven, not just run by hand: each org's fixture is built into
      its own empty temp directory in `tests/test_kodak_maersk.py`'s `repo_dir` fixture, and
      `orgs(repo)` on that isolated repository returns exactly one name — verified directly
      (`orgs: ['kodak']`, `orgs: ['maersk']`) — so building or running either requires nothing
      else, no flagship and no sibling portfolio org, to exist. Manual runs corroborate the same
      thing end to end (`twin fixture --name kodak`, `twin fixture --name maersk`, `twin run`
      against each, independently, both exit 0).
- [x] Anything not built is entered in the does-not-do register with its reason.
      Named in-file (the module comment above `build_kodak_org`/`build_maersk_org` and each
      docstring) rather than silently absent: no outcome/answer-key (decision ticket 01 — a
      portfolio org does not carry the backtest burden the flagships and the dedicated backtest
      suite do); no behavioural substrate, causal edges, rival world models, perspectives,
      responses or people (stub depth, decision ticket 01's "lighter" portfolio tier); no
      `twin/capabilities/*.yaml` depth-grade file (no owning decision ticket exists to grade
      against — see AC 5). Build ticket 77 generates the published register **from** each
      capability's depth-grade checklist rather than by hand; this ticket's own checklist,
      naming each gap and its reason, is exactly that input. Nothing is written to a register
      file here because that file does not exist until ticket 77 builds it.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      No invariant or harness guard changed; none was needed. `tests/test_scenario_library.py`'s
      pre-existing, unmodified `test_the_standing_library_sweeps_with_no_separate_harness` already
      asserts `answer_keys <= orgs_run` for every name in `BUILDERS` outside `{default, library,
      pocket}` — adding `kodak` and `maersk` to `BUILDERS` made that assertion cover two more
      names automatically, and both satisfy it structurally (each org's one scenario sweeps
      clean) rather than needing an exemption or a new guard. `./bin/twin verify` run clean
      against it (see Evidence): 66 passed, the same 2 pre-existing, unrelated failures
      (`drift_window_is_actually_being_sampled`, `flux_coverage_floor_is_still_reachable` — the
      recorded-not-restarted probe gap, unmoved by anything this ticket touches).
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      No owning decision ticket — the same position build tickets 34, 56 and 78 found for a
      ticket of this shape. Decision ticket 01 has no `## Acceptance criteria` section for
      `twin/grades.py` to read; decision ticket 06's acceptance criteria describe the OSINT
      *survey* that picked Kodak and Maersk (already resolved 2026-08-04), not what a modelled
      portfolio org must contain — neither is a yardstick this ticket's capability could be
      validated against. This checklist itself, computed against real evidence — fixtures that
      build, validate, sweep and run; a dedicated 16-test file; a clean full-suite and `twin
      verify` run — is the evidence, in the same spirit the checklist asks of every other ticket.

## What is honestly true now, and what still isn't

Both portfolio subjects exist in the model, are schema-valid, sweep with the standing library and
run end to end, each on its own real, dated, cited evidence — not placeholders. Neither carries a
backtest answer key, a behavioural substrate, causal edges, or any depth beyond what its own
`would-the-twin-have-flagged-it` scenario exercises. `twin run`'s printed `depth` block
(`domain-model partial 1/7`, `provenance partial 2/4`, `scenario-engine partial 4/7`) is a
**different axis entirely** — it is the *engine's own* capability maturity from `twin/grades.py`,
identical for Kodak, Maersk or any other org, unmoved by this ticket because this ticket ticks no
capability criterion. It says nothing about how much of Kodak or Maersk itself is modelled; that
is the org-level `stub` named on AC 1, a separate, ticket-local judgement with no `grades.py`
machinery to compute it against (AC 5). Deepening either org — an outcome, a behavioural layer,
more signals — is that org's own independent upgrade track from here, exactly as decision ticket
01 specifies, and gated on nothing this ticket built.

## Evidence

```
.venv/bin/python -m pytest tests/test_kodak_maersk.py tests/test_scenario_library.py -q
  23 passed

.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
  Success: no issues found in 145 source files

.venv/bin/python -m pytest -q
  1417 passed, 1 failed in 385.11s (0:06:25)
  FAILED tests/test_invariant_suite.py::test_the_suite_is_green — the same single, pre-existing,
  unrelated failure every prior ticket's evidence names (the recorded-not-restarted drift/Flux
  probe gap); unmoved by anything this ticket touches.

.venv/bin/python -m twin verify
  RESULT: 66 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  Same two known failures (drift_window_is_actually_being_sampled,
  flux_coverage_floor_is_still_reachable). every_capability_depth_graded still reads
  "6 capabilities graded by computed checklist" — unmoved, because this ticket adds orgs, not a
  capability.

twin fixture --name kodak --out <tmp>/kodak-test  →  deterministic, exit 0
twin fixture --name maersk --out <tmp>/maersk-test  →  deterministic, exit 0
twin run --repo <tmp>/kodak-test --org kodak --scenario would-the-twin-have-flagged-it \
  --regime as-consumed --out <tmp>/kodak-bundle.json  →  exit 0, forecast-bundle emitted
twin run --repo <tmp>/maersk-test --org maersk --scenario would-the-twin-have-flagged-it \
  --regime as-consumed --out <tmp>/maersk-bundle.json  →  exit 0, forecast-bundle emitted
```
