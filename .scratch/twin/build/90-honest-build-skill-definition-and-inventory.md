# 90 — Honest build: the skill definition and capability inventory, as data instead of prose

**What to build:** `honest-build` is 1/4 — only the build-order AC (3) is checked, even though
decision ticket 20 itself is fully resolved in prose. The pattern is consistent with every other
capability in this batch: the checklist tracks code that realises the decision, not the decision's
existence in prose. This ticket makes the other three ACs queryable and asserted rather than
narrated in a docstring.

Run this ticket after every other ticket in this ninety-through batch (79–89) so its capability
inventory (AC 2) reflects the system's real, final state rather than a snapshot that goes stale the
moment the next ticket lands.

Note an open tension found during research, worth resolving honestly rather than papering over:
`twin/ethics_gate.py` — one of the six named "skills" — reads as deterministic, rule-based code
(a fixed ladder walk and gameability classification), not an LLM judgement call at evidence grade 5.
If the capability inventory (AC 2) finds it doesn't actually meet decision ticket 20's own
determinism-split test, say so in this ticket rather than forcing it onto the skill side to match
the six-skill count map.md already states. A corrected classification is a better outcome than a
consistent-looking but wrong one.

**Blocked by:** 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 20 (`.scratch/twin/issues/20-skill-inventory.md`).
`twin/capabilities/honest-build.yaml` for exact AC text. `twin/skills.py`.

- [x] AC 1 — "A definition of 'skill' for this project, and the unit of packaging." The determinism-
      split test currently lives only as a module docstring in `twin/skills.py`. Make it a
      queryable constant or function other code (AC 2's inventory) can assert against, not prose a
      human has to keep in sync by hand.
      **Closed.** `twin/skills.py` `SKILL_DEFINITION` (a real string) and `classify_by_determinism()`
      — decision ticket 20 Q1's own test, as one function. `twin/honest_build.py`'s
      `validate_inventory()` calls it against every inventory entry's own `reproducible_from_pins`
      flag, so it is genuinely load-bearing, not decorative —
      `tests/test_honest_build.py::test_a_kind_that_contradicts_its_own_determinism_flag_is_refused`
      proves a hand-edited `kind` that disagrees with its own determinism flag is refused.
- [x] AC 2 — "The inventory: which capabilities are skills, which are code, which are inherited from
      arckit." A `CAPABILITY_INVENTORY` table classifying every named capability, checked against
      actual files (every "code" entry has a corresponding non-empty module; every "skill" entry has
      a threshold entry in `skill-thresholds.yaml`). Resolve the ethics-gate classification question
      above as part of building this, not before.
      **Closed.** `twin/honest_build.py` `CAPABILITY_INVENTORY`: 18 entries covering every
      capability decision ticket 20 Q3 named (10 code, 3 inherited from arckit, 5 skill), checked
      against real files by `validate_inventory()`, wired into the standing suite as harness check
      `honest_build_inventory_matches_files_and_owning_tickets`
      (`tests/test_honest_build.py::test_the_real_inventory_validates_clean`).
      **The ethics-gate tension, resolved rather than papered over — the finding turned out to be
      real.** `ethics_gate.scorer()` — the function `skill-thresholds.yaml`'s `ethics-gate` entry
      actually scores — compares only `admitted` and `stopped_at`, i.e. `admit()`'s ladder-walk
      plus DPIA triage. Given a payload of already-quantified facts (booleans, floats, an enum),
      that computation has exactly one correct answer: it is reproducible from pins. Contrast the
      other five skills, each of which documents its own "swap the body for a model call" upgrade
      path (`signal_classify.py`, `evolution_judge.py`, `causal_claims.py`, `gameplay_lens.py`,
      `substrate_generator.py` all say this in their own module docstrings) because each stands in
      for a genuinely ambiguous reading of unstructured evidence. `ethics_gate.py`'s admission
      machinery documents no such path, because no model call would change a correctly-implemented
      ladder's answer. `classify_gameability()` — the one piece of the module that *is* irreducibly
      interpretive (reading free-text `metric_description`) — is not part of what the threshold
      entry scores at all, so it does not rescue the module's classification.
      `ethics-gate` is classified `code` in `CAPABILITY_INVENTORY` here
      (`tests/test_honest_build.py::test_ethics_gate_is_classified_code_not_skill`,
      `::test_ethics_gates_own_scorer_only_reads_the_deterministic_ladder_surface`). The existing
      eval harness (`skill-thresholds.yaml`, `twin/skills.py`, and every "sixth and last of the six
      skills" docstring across the codebase) is **left as-is** — rewriting that prose across seven
      files and `tests/test_record_skill_scores.py`'s `_EXPECTED_SKILLS` would be a large,
      unrequested rewrite chasing a label rather than a correction of behaviour, and none of it is
      wrong about what the harness *does*, only about what to call it. See this ticket's "Also found
      and fixed" and "What still isn't true" sections below.
- [x] AC 4 — "Each skill's owned decision-record (which resolved ticket defines its contract)."
      A `SKILL_OWNING_TICKET` mapping validated against `.scratch/twin/issues/` existing, the same
      way `twin/grades.py`'s `acceptance_criteria()` validates ticket existence elsewhere.
      **Closed.** `twin/honest_build.py` `SKILL_OWNING_TICKET`: five entries (signal-classify -> 11,
      causal-claims -> 08, evolution-judge -> 11, substrate-generator -> 12, gameplay-lens -> 13) —
      not six, because AC 2's correction excludes `ethics-gate` — each validated against a real file
      under `.scratch/twin/issues/` by `validate_owning_tickets()`
      (`tests/test_honest_build.py::test_owning_tickets_are_exactly_the_skill_classified_capabilities`,
      `::test_an_owning_ticket_that_names_no_real_file_is_refused`).
- [x] AC 3 — "A build order with the bootstrap sequence made explicit." Already closed by build
      ticket 07 (the walking skeleton, `twin/demo.sh`), before this ticket existed; untouched here.

## Also found and fixed

- **`honest-build` reaching `full` changed `Capabilities.digest`, which every emitted artefact's
  `tool.capabilities_digest` field carries — the same mechanism build ticket 89 hit when
  `provenance` reached `full`.** The twelve committed golden digests in
  `twin/invariants/golden-digests.json` went stale the moment AC 1, AC 2 and AC 4 ticked. Re-blessed
  via `twin verify --bless-goldens --authorise "decision ticket 20 — honest-build reaches full, AC
  1/2/4 closed and ethics-gate reclassified code (build ticket 90)"`.
- **`tests/test_grades.py`'s two capability-set guards hardcode the shipped-`full` set by name** —
  the same maintenance every prior ticket that reached `full` for the first time (79–89) already did
  to this exact pair. `honest-build` reaching `full` changed both:
  `test_only_..._and_provenance_have_earned_full` and
  `test_..._and_provenance_are_the_shipped_capabilities_at_full`, renamed to name `honest-build` too
  and their bodies updated to add it to the expected `full` set (`caps.aggregate()` moved from
  `(66, 73)` to `(69, 73)` in the same step).
- **`twin/README.md`'s "What is honestly built" table and aggregate paragraph were about to go
  stale in the same commit that fixed them.** The `honest-build` row moved from `partial 1/4` to
  `full 4/4`, the aggregate from **66 of 73** to **69 of 73**, "eleven of them full" to "twelve",
  and a new paragraph added matching the existing per-capability "moved from X/Y to full, at build
  ticket N" convention (`provenance`, `enactment`, `twin-inside-twin` each already had one).
  `tests/test_grades.py::test_the_published_aggregate_matches_the_computed_one` reads the figure
  back out of the file, so this was caught mechanically, not by re-reading.
- **`./bin/twin verify`'s own published pass count in `twin/README.md`'s "The invariants" section
  needed the same live re-derivation** once the new harness check
  (`honest_build_inventory_matches_files_and_owning_tickets`) added a 70th passing check on top of
  the prior 69 — see the Evidence section below for the live numbers this was corrected to.

**Judgement calls made, not revisited:**
- **The existing "six real skills" prose is left untouched everywhere except this ticket's own new
  code and documentation.** `twin/ethics_gate.py`'s own docstring, `twin/skills.py`'s module
  docstring, five other skill modules' "Nth of the six skills" openers,
  `tests/test_record_skill_scores.py`'s `_EXPECTED_SKILLS`, and `.scratch/twin/map.md`'s
  decision-ticket-20 summary all still say six. Decision ticket 20's own resolution (AC 2 and AC 4)
  is what this ticket's checklist tracks — the six-skill eval harness's own behaviour (which
  `skill-thresholds.yaml` entries exist, what `evaluate()` runs against) is unaffected by a
  classification correction in a table those modules never read. Rewriting seven files' worth of
  "sixth of six" prose to keep a label consistent, when nothing about what any of that code *does*
  is wrong, would be scope creep chasing cosmetics rather than closing a real gap — the
  `CAPABILITY_INVENTORY` entry's own `note` field states the discrepancy in full instead, at the
  one place a reader checking "is this actually a skill by ticket 20's own test" would look.
- **`CAPABILITY_INVENTORY`'s twelve "code"/"inherited" entries each cite one primary module**, even
  where a capability's own implementation spans several files (e.g. `fair-pricing-engine` cites
  `pricing.py` but names `pert.py`/`severity.py`/`tradeoff.py` in its `note`). Decision ticket 20 Q3
  named these as twelve capabilities, not as a file-by-file manifest, and `validate_inventory()`'s
  own check ("a corresponding non-empty module") only needs one real anchor per entry to be
  meaningful — a table that instead tried to enumerate every contributing file per capability would
  be a second, competing module map growing out of sync with the first.

## What is honestly true now, and what still isn't

**True now:** all four of decision ticket 20's acceptance criteria are closed by real, queryable
code rather than by the decision ticket's own prose, `honest-build` reaches `full` (4/4), and the
ethics-gate classification tension this ticket was asked to investigate turned out to be a genuine
finding, not a false alarm — recorded honestly in `CAPABILITY_INVENTORY` rather than smoothed over.

**What still isn't true:** the "six real skills" identity persists, unreconciled, across
`skill-thresholds.yaml`, `twin/skills.py`, five skill modules' own docstrings and one test file —
this ticket names the discrepancy rather than closing it (see "Judgement calls" above). Nobody has
gone back to check whether the same determinism-split test, applied as rigorously as it was applied
to `ethics-gate` here, would also unsettle any of the other five skills' classifications — this
ticket only investigated the one tension it was asked to investigate, not a fresh audit of all six.
`CAPABILITY_INVENTORY`'s "code" entries name one primary module each rather than every file that
contributes to a capability, so a reader wanting the full file-level footprint of, say, the FAIR
pricing engine still has to read `pricing.py`'s own docstring, not just this table.

## Evidence

Baseline, before this ticket's edits (`.venv/bin/python -m pytest -q`):
```
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionErro...
1 failed, 1518 passed in 339.25s (0:05:39)
```
The one pre-existing failure is `test_the_suite_is_green`, itself failing on two known,
unrelated invariants (memory: "Flux verdict closes unmeasured, 2026-08-16" — the owner recorded it
rather than restarting the probe): `drift_window_is_actually_being_sampled` and
`flux_coverage_floor_is_still_reachable`.

New capability module and its own tests, in isolation (`.venv/bin/python -m pytest -q
tests/test_honest_build.py`):
```
bringing up nodes...
bringing up nodes...

.................                                                        [100%]
17 passed in 0.83s
```

`.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores`:
```
Success: no issues found in 156 source files
```

The new inventory validated live against the real `twin/` tree
(`.venv/bin/python -c "from twin import honest_build; honest_build.validate_inventory();
honest_build.validate_owning_tickets(); print('OK', honest_build.inventory_summary())"`):
```
OK {'code': ['causal-propagation', 'ethics-gate', 'fair-pricing-engine', 'graph-schema-validation',
'intervention-time-primitives', 'provenance', 'scenario-execution-forecast-objects',
'scoring-harness', 'substrate-eval-suite', 'unbound-signal-pool'], 'skill': ['causal-claims',
'evolution-judge', 'gameplay-lens', 'signal-classify', 'substrate-generator'], 'inherited':
['blast-radius', 'scheduled-execution', 'wardley-maths']}
```

`honest-build` reaches `full` (`.venv/bin/python -c "from twin.grades import Capabilities; caps =
Capabilities.load(); print(caps.require('honest-build').grade, caps.require('honest-build').summary());
print('aggregate', caps.aggregate())"`):
```
full {'grade': 'full', 'owning_ticket': '20', 'checked': 4, 'total': 4, 'unchecked': []}
aggregate (69, 73)
```

Golden digests re-blessed once `honest-build` reaching `full` moved `Capabilities.digest` (the
same mechanism build ticket 89 hit):
```
$ .venv/bin/python -m twin verify --bless-goldens --authorise "decision ticket 20 — honest-build
  reaches full, AC 1/2/4 closed and ethics-gate reclassified code (build ticket 90)"
golden digests -> golden-digests.json (12 artefacts)
  blast-radius       07b18ef7ab9382638788e8072514f6b250b0124fc26e19d0e3fb43d34262887f
  ... (12 artefacts total)
```

Final `./bin/twin verify` (full suite, `.venv/bin/python -m twin verify`), including the new
harness check:
```
 14  PASS  honest_build_inventory_matches_files_and_owning_tickets  18 capabilities classified
      (10 code, 3 inherited, 5 skill); 5 skill(s) each resolve to a real decision ticket under
      .scratch/twin/issues/
...
RESULT: 70 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: ...
  FAIL flux_coverage_floor_is_still_reachable: ...
```
Both failures are the same two pre-existing, unrelated ones named above — no new failure, no
change in identity or count.

Final `.venv/bin/python -m pytest -q` (full suite, after the golden-digest re-bless):
```
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionErro...
1 failed, 1535 passed in 351.89s (0:05:51)
```
1535 = 1518 baseline + 17 new (`tests/test_honest_build.py`), exactly. The one failure is the same
pre-existing `test_the_suite_is_green`, for the same two named reasons — zero new failing tests,
zero changed in identity.
