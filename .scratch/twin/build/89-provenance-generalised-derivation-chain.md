# 89 — Provenance: generalise the derivation chain beyond its one hardcoded hop

**What to build:** Decision ticket 14's design (both artefact attestation and reasoning-chain
attestation, chain depth "unbounded but recomputable — a recommendation traces to its forecasts, to
the execution's pins, to the graph version, to the signals") is only partly built. `twin/reproduce.py`
has a real, recursive `Report.chain: list[Report]` mechanism (`.reproduces` checking, `reproduce.py`
~line 53) — but it is hardcoded to exactly one hop: score-card → forecast-bundle
(`reproduce.py` ~line 164). It never walks further (bundle → graph version → signals), and other
artefact kinds — a recommendation or response artefact — have no chain-walking at all. `twin verify
<artefact>` (`cli.py` ~line 1947, `_reproduce` ~line 1359) is the single-artefact-plus-one-hop entry
point today.

**Blocked by:** 86 (the response/recommendation artefact this ticket generalises chain-walking onto
now carries build ticket 86's enactment-state field; building the generalised walk after 86 avoids
re-deriving it against a shape that's about to change)

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 14 (`.scratch/twin/issues/14-provenance-attestation.md`), Q1 and Q3
specifically. `twin/capabilities/provenance.yaml` for exact AC text. `twin/reproduce.py`, `twin/cli.py`.

- [x] AC 1 — "Decided: artefact attestation vs reasoning-chain attestation (or both, with the seam)."
      The design already answers both, with a seam; this AC ticks once the seam is demonstrated
      generically rather than only for the score-card special case AC 3 fixes.
      Closed: `twin/reproduce.py` gains `_replay_subject`, the one place a subject reference
      (`{kind, sha256, produced_by, pins}`, plus whatever body content that kind's own replay
      needs) is walked, and it is no longer reachable only through the fallthrough `score` used to
      rely on. `replay()`'s `score` and `reliability` branches both call it explicitly — two
      different artefact kinds routed through the identical mechanism is what "demonstrated
      generically" means in code, not prose. `twin/capabilities/provenance.yaml` index 1.
- [x] AC 3 — "The chain-depth rule for a recommendation, and materialised-vs-reconstructable."
      Generalise `reproduce()`'s chain construction to walk any artefact's declared pins
      recursively — bundle → its execution's graph-version → signals — rather than the single
      hardcoded score-card→bundle hop. Extend to a recommendation/response artefact specifically,
      since that is the concrete case the AC names. Add a test that walks a chain at least three
      hops deep and one that proves an artefact kind with no chain-walking support fails loudly
      rather than silently returning an empty chain.
      Closed, with the scope corrected against what the domain actually has (see "what the draft
      guessed wrong" below): this codebase has no artefact kind literally named "recommendation"
      or "response" — `recommendation`/`recommended`/`recommended_action` are FORBIDDEN field names
      (`twin/artefact.py`'s `FORBIDDEN_KEYS`), and `verbs.price()`'s own body says so directly
      ("nothing recommends one"). The two places one artefact names another by digest are
      score-card → forecast-bundle (`body["subject"]`, pre-existing) and reliability-diagram →
      score-cards (`pins["score_cards"]`, plural — the decision-facing artefact this AC's "chain
      depth for a recommendation" concretely maps onto: a reliability diagram is what a reader
      reads to judge whether the twin's forecasts are trustworthy at all). `verbs.reliability()`'s
      `sources` entries now carry `kind`, `produced_by` and `body: {"subject": <the card's own
      bundle reference>}` alongside the digest and pins they already carried — enough to *walk*,
      not only to check. Reproducing a reliability diagram now walks reliability → score-card →
      forecast-bundle, three artefacts deep, each hop re-opening its own pinned model tree (AC 3's
      "unbounded but recomputable"; decision ticket 14 Q3). `twin/cli.py`'s `_reproduce` chain
      print is now recursive too (`_print_chain`), so a reader actually sees the second hop rather
      than the flat, one-level list that was the whole of what a chain could be before this ticket.
      Tests: `tests/test_reproduce.py::test_reproducing_a_reliability_diagram_walks_a_three_artefact_chain`
      (the three-hop walk, `report.reproduces` true end to end) and
      `tests/test_reproduce.py::test_a_chain_reference_missing_produced_by_fails_loudly_not_silently`
      (a reference carrying only `sha256`/`pins` — the pre-89 shape — raises `ReproduceError`
      naming exactly what is missing, never a bare `KeyError` and never a silently empty chain).
      `twin/capabilities/provenance.yaml` index 3.

## What the draft guessed wrong

The draft's own phrasing — "bundle → its execution's graph-version → signals" and "a
recommendation/response artefact specifically" — read as if three more *artefact kinds* needed
digest-level chain links added under a forecast bundle, and as if a "recommendation" artefact
already existed to extend. Neither is true. A forecast bundle's "graph-version" and "signals" are
already covered by the pin it carries (`_open_at` re-opens the exact pinned commit on every
recursive replay, which is the whole of what makes the model's state at that pin recomputable —
there is nothing further to "walk" there because nothing beyond the pin was ever materialised, by
Q1's own design). And no artefact called a recommendation exists to extend — the domain
deliberately refuses that shape. The real, buildable gap was structural rather than domain-shaped:
the chain-walking *mechanism* itself only worked for one hardcoded case and one field name
(`body["subject"]`), and the second real digest-reference this codebase already has
(`reliability`'s pooled score cards) had never been wired to it at all — confirmed by grep, zero
hits before this ticket, and by the fact `replay()` refused `twin reliability ...` outright as "not
a replayable command." Generalising the mechanism and wiring the one other real case is what
"three hops deep" turned out to mean once the domain was actually read rather than assumed from the
ticket's own draft language.

## Also found and fixed

- **A subject reference one level up only carried enough to check its own digest, not enough to
  walk it — a `KeyError: 'subject'` the first real test run caught.** `_replay_subject`'s synthetic
  doc for a nested reference started with `body: {}` unconditionally, which is correct for a
  forecast bundle (its own `replay()` branch never reads `doc["body"]`) but wrong the moment the
  *referenced* kind is itself a score card, whose `score` branch reads `doc["body"]["subject"]` to
  find its own bundle. Fixed by letting a subject reference carry an optional `body` — whatever
  body content that kind's own replay needs, nothing more — so `reliability`'s `score_cards`
  entries now include `"body": {"subject": card["body"]["subject"]}` and `_replay_subject` passes
  it through. `_SUBJECT_FIELDS` gained `pins` alongside `kind`/`sha256`/`produced_by` at the same
  time: without it, a nested `run`-verb reference missing `pins` would have hit
  `envelope["pins"]["model_repo"]` and raised a bare `KeyError`, the exact failure mode AC 3's
  loud-refusal test exists to close.
- **Two stale prose claims that this ticket's own change falsified, both citing `reproduce.py`'s
  discount refusal as proof reliability shared its limit.** `tests/test_enron.py`'s
  `test_a_discounted_score_card_honestly_refuses_to_replay_from_pins` and `twin/README.md`'s own
  discount paragraph both said a discount-carrying score card "honestly refuses to replay from its
  pins alone, the identical limit `twin reliability`'s own pooled inputs already carry" — true
  before this ticket, false after it (reliability now walks; a discount's own sources carry no
  `produced_by` pin at all, so there is nothing there to walk even in principle, which is a
  different reason than reliability's old one). Both updated to state the current, no-longer-
  shared reasons rather than leave a comparison the code no longer supports.
- **`tests/test_grades.py`'s two capability-set guards hardcode the shipped-`full` set by name** —
  the same maintenance every prior ticket that reached `full` for the first time (79, 80, 81, 82,
  83, 84, 85, 86, 87, 88) already did to this exact pair. `provenance` reaching `full` changed
  both: `test_only_..._and_scenario_engine_have_earned_full` and
  `test_..._and_scenario_engine_are_the_shipped_capabilities_at_full`, renamed to name `provenance`
  too (the function names enumerate the exact set — leaving a stale name while the assertion
  changed would be the same kind of drift this ticket's own docstring section above complains
  about) and their bodies updated to add `provenance` to the expected `full` set.
- **Golden digests needed re-blessing**, the same mechanism build tickets 85 and 86 used:
  `provenance` reaching `full` changes `Capabilities.digest`, which every emitted artefact's
  `depth` block carries, so the twelve committed golden digests in
  `twin/invariants/golden-digests.json` went stale the moment AC 1 and AC 3 ticked. Re-blessed via
  `twin verify --bless-goldens --authorise "decision ticket 14 — provenance reaches full, AC 1 and
  AC 3 closed (build ticket 89)"`.
- **`twin verify`'s own chain print was flat, and this ticket's own change made that a real gap
  rather than a cosmetic one.** Before this ticket, `report.chain` was never more than one entry
  deep, so `cli.py`'s `_reproduce` printing it as a single flat loop lost nothing. Once a
  reliability diagram's chain nests a score card's own chain inside it, a flat print would silently
  drop the second hop from what a reader sees while `report.reproduces` kept accounting for it
  correctly underneath — a real display gap, not just an omission. Fixed with a small recursive
  `_print_chain(links, depth)`, indenting each level.

**A judgement call, made and not revisited:** `_replay_subject`'s error message on a thin reference
lists every field the reference is missing (`sorted(missing)` against `_SUBJECT_FIELDS`) rather than
naming only the first. A reader debugging a real thin reference wants the whole shortfall in one
message, not one field at a time across repeated runs — the same instinct `_need()`'s existing
messages already follow (name the missing flag and the whole recorded command, not just "a flag is
missing").

## Evidence

Baseline, clean tree, before this ticket's edits (`.venv/bin/python -m pytest -q`, stashed working
tree, `git stash pop` restored after):
```
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionErro...
1 failed, 1516 passed in 402.58s (0:06:42)
```
The one pre-existing failure is `drift_window_is_actually_being_sampled` (memory:
"Flux verdict closes unmeasured, 2026-08-16" — the owner recorded it rather than restarting the
probe), unrelated to this ticket.

Live, single-command demonstration of the three-hop walk (`./bin/twin verify`, built fresh from
`run` -> `score` -> `reliability`):
```
==> reproducing /tmp/t89demo/reliability.json from its pins
  ok   score-card         52ae0a1fefbca01d (recorded 52ae0a1fefbca01d)
    ok   forecast-bundle    686c1204af755fbd (recorded 686c1204af755fbd)
  ok   reliability-diagram 57be68676a7ae270 (recorded 57be68676a7ae270)
  tolerance: none — byte identity. Scores carry a declared 12-significant-digit quantisation in the format.

REPRODUCES: the pins are sufficient to recompute this artefact exactly.
```

`.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores`:
```
Success: no issues found in 154 source files
```

`.venv/bin/python -m pytest -q` (final, after all fixes, including the golden-digest re-bless):
```
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionErro...
1 failed, 1518 passed in 381.76s (0:06:21)
```
Same single pre-existing failure as the baseline; the two extra passes are this ticket's own new
tests (`test_reproducing_a_reliability_diagram_walks_a_three_artefact_chain`,
`test_a_chain_reference_missing_produced_by_fails_loudly_not_silently`).

`.venv/bin/python -m twin verify`:
```
RESULT: 69 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: ...
  FAIL flux_coverage_floor_is_still_reachable: ...
```
Both failures are the pre-existing, named, owned findings (`.scratch/twin/build/70-*.md`); neither
is new and neither changed identity.

Golden digests re-blessed (`provenance` reaching `full` changes `Capabilities.digest`, carried in
every artefact's `depth` block):
```
./bin/twin verify --bless-goldens --authorise "decision ticket 14 — provenance reaches full, AC 1 and AC 3 closed (build ticket 89)"
golden digests -> golden-digests.json (12 artefacts)
```

Provenance depth block, live, after this ticket's checklist edit
(`.venv/bin/python -c "from twin.grades import Capabilities; print(Capabilities.load().depth_block(['provenance']))"`):
```
{'grade': 'full', 'capabilities': {'provenance': {'grade': 'full', 'owning_ticket': '14', 'checked': 4, 'total': 4, 'unchecked': []}}}
```
(`checked: 2/4` before — `twin/capabilities/provenance.yaml`'s own `git diff` shows exactly indices
1 and 3 flipping from `false` to `true`, matching this ticket's own two closed AC checkboxes above.)
