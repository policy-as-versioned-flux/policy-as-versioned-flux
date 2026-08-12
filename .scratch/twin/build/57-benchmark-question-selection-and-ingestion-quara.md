# 57 — Benchmark question selection and ingestion quarantine

**What to build:** Questions selected by a **versioned, pre-registered mechanical rule** spanning the full confidence
range — so a change to the selection rule is as visible as a change to the constraint set, and
cherry-picking easy questions is structurally prevented.

The benchmark set is **quarantined from ingestion at any lag**, and the quarantine is **auditable
because ingestion is provenanced**. That is what makes *"we forecast before we looked"* provable
rather than asserted.

**Blocked by:** 08, 53

**Status:** done (2026-08-11)

**Reading list:** Decision ticket 21 (forecast book). Spec stories 49, 50.

- [x] Selection rule is mechanical, versioned and pre-registered; running it is reproducible.
- [x] Selected questions span the full confidence range, demonstrated by their distribution.
- [x] Quarantine holds at any lag and is auditable against the ingestion provenance record.
- [x] A planted quarantine breach is detected by audit.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-11)

`twin/benchmark.py`, `twin/benchmark-selection-rule.yaml`, `twin/capabilities/forecast-book.yaml`,
one harness guard (`benchmark_selection_is_mechanical_and_quarantine_catches_a_planted_breach`),
`tests/test_benchmark.py`.

- **The selection rule is mechanical, versioned, pre-registered and reproducible.**
  `twin/benchmark-selection-rule.yaml` states eligibility in resolvable terms only (liquidity
  threshold, resolution-horizon window, category list), the same discipline
  `twin/evidence-ladder.yaml`'s thresholds carry — a change to it is a dated diff in this file's
  own committed git history. `select_questions()` sorts candidates by id before anything else
  touches the pool (so arrival order cannot bias a volume cap) and is a pure function of
  `(rule, pool)`: the identical rule against the identical pool draws the identical set, twice,
  asserted directly rather than trusted. The one place chance enters is decision ticket 21 Q2's
  own named exception — "(c) random sampling as a volume valve if the rule selects too many" —
  drawn from the rule's own committed `sample_seed`, so the cut-down is deterministic and
  demonstrably a real sample rather than a truncation
  (`tests/test_benchmark.py::test_the_volume_valve_is_a_deterministic_seeded_sample_not_an_ad_hoc_cut`).
- **The full confidence range is demonstrated, not claimed.** `confidence_distribution()` bins the
  selected set against the rule's own declared bins, including empty ones, and
  `BenchmarkSet.spans_full_confidence_range()` is true only when every bin holds at least one
  question — checked against a real 18-question pool spanning all six committed bins in the
  harness guard, not asserted in prose.
- **The quarantine is a scan across ingestion provenance, not a single named field.**
  `audit_quarantine()` serialises each `(label, record)` pair whole and checks it for a substring
  match against every quarantined question id, so a breach nested in a recipe id or a free-text
  note is caught, not only a field a caller happened to check. Nothing here reads a timestamp,
  which is what makes the quarantine hold "at any lag" — an old record and one audited long
  afterward are scanned identically, exercised directly in both the test suite and the harness
  guard.
- **A planted quarantine breach is detected by audit, in both suites.** `tests/test_benchmark.py`
  plants a quarantined id nested inside an unrelated `recipe` field and confirms
  `audit_quarantine` reports it, alongside the negative leg (unrelated records report clean); the
  harness guard repeats the same shape against the real committed rule, planting the breach at
  two differently-labelled records to demonstrate "any lag" rather than only "the most recent
  record".
- **Both artefacts (`benchmark-set`, `quarantine-audit`) are `derived`** — nothing here could
  carry a human's accountability — and declare `twin/capabilities/forecast-book.yaml` (owning
  decision ticket 21) via `caps.depth_block`. Only decision ticket 21's first acceptance criterion
  (the selection rule) is checked by this ticket's code; the other five (venue/observe-only,
  blind emission, claim scope, the temporal-separation half of circularity, proportionality) are
  build tickets 58 and 59's, so the capability grades `partial` (1/6) honestly rather than `full`.
- Extends the invariant suite with one harness guard — no manifest or golden-digest change to the
  constitution's fixed sixteen, the same shape `ingest_runs_unattended_with_provenance_and_measured_throughput`
  (build ticket 53) is: a property of this module's own contract, not one of the sixteen fixed
  names. Adding `twin/capabilities/forecast-book.yaml` does move `Capabilities.digest`, and every
  artefact's pins with it, so `twin/invariants/golden-digests.json` was re-blessed via
  `bin/twin verify --bless-goldens --authorise "decision ticket 21 — build ticket 57 adds the
  forecast-book capability"` in the same change.
- `ponytail:` no `twin` CLI verb, the identical call `twin/ingest.py` (build ticket 53) made and
  named: `select_questions`/`audit_quarantine` are typed functions exercised at seam 2, and a real
  venue adapter (58/59) is what would give a CLI invocation something live to point at. Add
  `twin benchmark-select`/`twin benchmark-audit` once one exists.
- `ponytail:` no schema-validated, model-repository-resident question type. A candidate pool is a
  caller-supplied `list[dict]`, the same shape `twin/ingest.py`'s substrate templates are — this
  ticket owns the rule and the quarantine, not the venue integration, so inventing an on-disk
  format for a real market question ahead of build tickets 58/59 would be exactly the kind of
  speculative flexibility the constitution's sunk-cost-architecture guard refuses.

**A pre-existing, unrelated gap found while verifying, not introduced here:** the same
worktree-sync artefact build ticket 53's own notes name —
`drift_window_was_declared_before_it_was_measured` fails because this worktree's
`estate/driftwood/drift/` had to be committed fresh, after the probe samples it carries were
originally recorded on main — is still the only pre-existing failure. Confirmed unchanged before
and after this ticket's own change; this ticket's own tests
(`tests/test_benchmark.py`, 19/19, plus the new harness guard) and every other previously-green
check still pass. `mypy twin tests conftest.py` passes with no issues.
