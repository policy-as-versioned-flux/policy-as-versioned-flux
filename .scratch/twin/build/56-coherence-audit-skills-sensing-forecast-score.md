# 56 — Coherence audit: skills → sensing → forecast → score

**What to build:** Confirmatory audit across the non-deterministic half of the system, where the pocket-org worksheet
cannot reach. Same rule as ticket 34: if problems are found rather than confirmed absent, record
which ticket should have caught it and amend that ticket's ACs.

**Blocked by:** 55, 09, 52

**Status:** done (2026-08-13)

**Reading list:** The invariant manifest; the seam-3 score-over-time record. Constitution.

- [x] A full run from raw substrate signals through skills, sensing, execution and scoring.
      Each stage already had its own reproducible evidence in isolation — `twin/ingest.py`
      (build ticket 53) proves substrate → skill at volume, `twin/demo.sh` (run in CI) proves
      sense → run → score — but nothing had ever chained all four in one place. Fixed:
      `tests/test_ingest.py::test_the_full_loop_runs_from_raw_substrate_through_skills_sensing_execution_and_scoring`
      runs `ingest.ingest_run()` (raw substrate through the real `signal-classify` skill, grade 5
      by construction) then the real CLI (`twin sense` on the fixture's own
      `price-separation-announced` signal, `twin run --regime as-consumed`, `twin score`) end to
      end against the netflix fixture, asserting on each real artefact rather than trusting the
      command exited zero. This is a real, reproducible run pytest re-runs on every change, not a
      one-off manual command. It deliberately does **not** wire stage 1's classified output into
      stage 2's binding — `twin sense` reads a committed grade-5 claim, not a skill's live
      output, and the test's own docstring names why: "sensing is a dead end" (nothing yet
      consumes a bound signal to move a forecast) is an already-disclosed, honest limit this
      ticket re-confirms rather than quietly wires around. That limit belongs to decision ticket
      11, not this audit.
- [x] Score-over-time records exist and are populated for all six skills.
      Checked before assuming: `twin/skill-scores.jsonl` did not exist. Every real call site
      (`tests/test_skills.py`, `tests/test_causal_claims.py`, the per-skill harness guards in
      `twin/invariants/harness.py`) evaluated a real skill against its real corpus but recorded
      the result into a throwaway `tmp_path` log or did not record at all — the seam-3 harness
      had been built (42) and exercised against every real skill's corpus on every CI run since
      each skill was built (43-49), but `record_score()` had never actually been called against
      the committed log for any of them. This is exactly the shape of finding this ticket exists
      to catch: a mechanism built and unit-tested against a fixture, never actually run for the
      real subjects it exists to monitor.
      Fixed: `twin/record_skill_scores.py` (`run()`) evaluates each of the six real skills —
      `signal-classify`, `evolution-judge`, `causal-claims`, `gameplay-lens`,
      `substrate-generator`, `ethics-gate` — plus `causal-claims`'s separately-registered
      `causal-claims-grade-accuracy` metric, each against its own real labelled corpus, honestly
      (the skill's real function, never the degraded stand-in the harness guards use to prove a
      threshold gates something), and calls `record_score()` for real. Run once for real
      (`python3 -m twin.record_skill_scores --at 2026-08-13T00:00:00Z`), tagged
      `model_version: heuristic-0.1.0` — a real, honest tag naming what actually produced the
      score (a heuristic stand-in pinned to the tool version, not a live model call, per every
      skill module's own docstring), not the toy-classifier fixture skill and not a fabricated
      model name. All seven entries pass their own threshold at score 1.0 (`twin/skill-scores.jsonl`,
      committed). Reproducible, not a one-off: `tests/test_record_skill_scores.py` exercises
      `run()` against a tmp log, and re-running the module for real — after a genuine model swap
      — appends a fresh entry `detect_regression()` can compare against this baseline.
      A second, smaller gap surfaced by making the log non-empty for the first time:
      `twin/skills.py`'s own `record_score()` docstring claims a harness guard
      (`skill_score_log_is_append_only`) already asserts the log's append-only discipline against
      git history, the same way `hash_changes_are_authorised` protects the invariant manifest —
      and no such guard existed anywhere in `twin/invariants/harness.py`. Invisible while the log
      was empty (nothing to protect); live risk the moment this ticket gave it real content.
      Fixed: `skill_score_log_is_append_only` added to `twin/invariants/harness.py`, same
      two-branch git-history shape as `hash_changes_are_authorised`. `./bin/twin verify` shows it
      `SKIP`s honestly right now ("fewer than two committed versions; nothing to compare yet") —
      correct, since this commit is the log's first — and will assert for real from the next
      commit that touches the log onward.
- [x] Skill output grades are spot-audited for over-grading drift.
      Read fresh, not trusted from the existing harness guards' own docstrings.
      `inspect.signature()` against `signal_classify.classify`, `evolution_judge.judge`/`override`,
      `gameplay_lens.propose`, `causal_claims.propose`, `substrate_generator.generate`/
      `generate_from_recipe_yaml` and `ethics_gate.admit` confirms none accepts a grade-shaped
      parameter. Reading each function's own body confirms `"evidence_grade": 5` is a **literal**
      in `signal_classify.classify`, `gameplay_lens.propose` and `ethics_gate.admit`;
      `evolution_judge.judge`/`override` assign fixed module constants (`_INFERRED_GRADE=5`,
      `_OVERRIDE_GRADE=4`), never a parameter. `causal_claims.propose` is the one skill whose
      grade genuinely varies — `grade = _grade(haystack)`, computed from the evidence text itself,
      never read from a caller-supplied field — and the asymmetric grade-accuracy metric
      (`causal-claims-grade-accuracy`) exists precisely to penalise a proposer that over-grades in
      the dangerous direction, verified live above. No gameable grade-shaped parameter found
      anywhere across the six. Confirmed absent, not discovered — the same "the plan's own
      early-detection brief held" outcome ticket 34's audit reports for its own slice.
- [x] No invariant pending past its activating ticket.
      `twin/invariants/manifest.yaml`: all sixteen entries read `state: live`, zero `pending`.
      `./bin/twin verify`: `RESULT: 57 passed, 1 failed, 2 skipped (0 pending invariants, 2 skipped
      and not faked)` — explicit in the runner's own summary line. The one failure
      (`drift_window_is_actually_being_sampled`) is a live-cluster probe-staleness check from
      build ticket 64, unrelated to this ticket's own slice and expected to be red between
      samples by its own design (see `twin/README.md`'s own note on why the guard exists — added
      after a probe went silent for three days and nothing noticed). The two skips are the
      CI-only `cross_architecture_determinism` leg and this ticket's own newly-added
      `skill_score_log_is_append_only`, correctly declining on its first commit.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      No constitutional invariant changed — the sixteen named in the manifest are untouched, and
      `hash_changes_are_authorised` passed clean against them. One **harness** guard was added,
      `skill_score_log_is_append_only` (`twin/invariants/harness.py`) — the same class of addition
      ticket 34's own precedent explicitly allows ("extend the invariant suite only if you find a
      genuine gap the suite itself should close"), for the real gap named above: a claimed
      protection (`twin/skills.py`'s own docstring) that did not exist, now live risk with real
      content in the log for the first time. No existing check's body, hash or assertion was
      weakened.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      This ticket adds no derivation code and ticks no capability criterion — `./bin/twin grade`'s
      arithmetic is unchanged before and after this ticket (35/64; every row re-verified against
      the live command output, see the README finding below). An audit ticket that confirms
      coherence, and fixes the real gaps it found, has no owning decision ticket to grade against
      — the same conclusion ticket 34 reached for its own slice — so this ticket's own evidence
      **is** the six-fold run above (the full-loop test, the populated score log, the spot audit,
      the manifest/verify check, the harness addition, the README correction below), computed
      rather than typed, in the same spirit the checklist asks of every other ticket.

## Also found and fixed: `twin/README.md` drift

Not one of the six checklist items above, but the same shape of finding ticket 34's own audit
made against the capability table — checked here because the ticket asked to look for it, and it
was real. This session's merge activity had left `twin/README.md`'s invariants section and several
"What is not built" bullets stale, all now corrected against `./bin/twin verify`/`./bin/twin
grade`'s live output rather than the previous round's hand-carried numbers:

- **"## The invariants" summary and table** claimed "52 pass, 1 pending" and listed
  `price_levels_never_probabilities` (59) and `standing_library_covers_committed_classes` (69) as
  still pending — both had gone live rounds ago (ticket 59's own narration elsewhere in this same
  file already says so: "the sixteenth and last invariant... zero pending entries"), but the
  summary table itself was never updated to match. Corrected to the live count (57 pass, 1 known
  failure, 2 skipped, 0 pending) and a single "live" column.
- **The `<!-- NOTE: totals ... provisional ... final verification recomputes -->` comment** named
  in this ticket's own brief: searched for and found in git history (`git show 6d57b75 --
  twin/README.md`), but it was already introduced *and removed* within build ticket 52's own
  commit — not present in the current committed file. Confirmed already fixed, not a live
  finding.
- **The capability table itself (35/64) and the opening banner (64 of 77 build tickets closed)**:
  recomputed independently against a live `./bin/twin grade` run and a live scan of every ticket
  file's own `Status:` line. Both matched exactly — confirmed clean, not corrected.
- **Three "What is not built" bullets had gone stale** as later tickets closed the gaps they
  named: one claimed `ethics-gate` "still does not exist" (built at ticket 47, months of narrated
  sections above it in the same file say so); one claimed the misuse catalogue, affected-parties
  register and disparate-impact channel "are not built" (all three built, 61-62, and separately
  already described accurately elsewhere in this same file); one claimed the forecast book "has
  no market connection at all" and the standing scenario set is "unfiltered, because there is no
  library yet" (tickets 58, 59 and 69 closed exactly those, respectively). All four corrected in
  place to state the current, `./bin/twin grade`-verified position and what genuinely remains
  open (no live venue connection; no selection/prioritisation rule; ticket 52's planter/detector
  split, which the substrate-generator bullet also failed to mention, added).

## Also checked: no ticket 1-63/69/71 is silently un-bookkept

The specific gap ticket 34 found once (`Status: ready-for-agent` with real, committed code) does
not recur: every ticket file 01-63, 69 and 71 reads `Status: done`, and ticket 64 correctly
carries its own honest non-`done` status ("instrumented, NOT MEASURING") rather than being folded
into the closed count — matching the banner check above. Not re-verified in depth per ticket, per
this ticket's own brief ("a quick scan is enough").

One smaller, non-actionable pattern noted rather than acted on: a handful of already-`done`
tickets (02, 06, 10, 11, 20, 23, 25, 27, 32, 38-42, 60-62, 71) carry one or two individually
unchecked acceptance-criteria boxes inside an otherwise-closed file. Spot-checked three: all are
honest, explained partial-completion notes (the cross-architecture CI leg still unproven;
adjudication-by-calibration not yet closed and said so in the ticket's own words) rather than
silent gaps — the same "honestly `partial`" discipline the whole capability-grading system runs
on, not a bookkeeping defect. Ticket 06's own unchecked box looks like a minor early-era (2026-08-05)
oversight against its own "Built" section immediately below it, but moves no capability arithmetic
and gates nothing — left as found rather than hand-edited for cosmetics.

## Evidence

```
.venv/bin/python -m pytest -q
  1222 passed, 1 failed in 1021.26s (0:17:01)
  FAILED tests/test_invariant_suite.py::test_the_suite_is_green — the pytest-level surfacing of
  the identical, known, pre-existing drift-probe staleness `./bin/twin verify` also reports below.
  Confirmed by re-running the invariant suite directly, both before this ticket's own changes and
  after, and finding the identical single failure each time — unrelated to and unmoved by
  anything this ticket touched.

.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
  Success: no issues found in 130 source files

./bin/twin verify
  RESULT: 57 passed, 1 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: known, pre-existing, unrelated (build ticket 64's
  live-cluster probe staleness)
```
