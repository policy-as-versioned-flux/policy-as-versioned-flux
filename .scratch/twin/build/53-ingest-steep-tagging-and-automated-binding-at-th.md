# 53 — Ingest, STEEP tagging, and automated binding at throughput

**What to build:** Binding **fully automated at volume**, trusted downstream rather than gated at entry — because
gating at entry cannot reach the throughput the twin needs. Use-gating, contestability and
calibration are what make that safe.

Blocked on the substrate recipe as well as the skill, because "at throughput" needs volume to be at
throughput *against*, and until substrate exists there is nothing to run at volume.

**Blocked by:** 43, 48

**Status:** done (2026-08-11)

**Reading list:** Decision ticket 11. Spec stories 12, 15.

- [x] Ingest pipeline runs unattended at a declared throughput against substrate volume.
- [x] Every ingested item is provenanced — which is what later makes the benchmark quarantine auditable.
- [x] No human gate at entry; the safety argument rests on downstream gating and is documented as such.
- [x] Throughput is measured and reported, not assumed.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-11)

`twin/ingest.py`, `tests/test_ingest.py`, one harness guard
(`ingest_runs_unattended_with_provenance_and_measured_throughput`).

- `ingest.ingest_run(repo, caps, org, recipe, count, command)` runs `signal_classify.classify`
  (build ticket 43) unattended, in a loop, over `count` items generated from a
  `twin.substrate-recipe/v1` recipe (build ticket 48's `generate_deterministic` — the toy,
  seeded generator; build ticket 49's real one is not a blocker, because this ticket needs
  *volume*, not fidelity) against the real component candidates of a named org overlay
  (`candidates_of`, merging world and overlay components the way `Overlay.graph()` already
  does). Emits a `ingest-run` artefact, marked `derived`, carrying the identical capability set
  `twin sense` does (`sense-move`, `domain-model`, `provenance`) via the existing
  `caps.depth_block()` — so the artefact honestly reports `sense-move`'s computed grade
  (`partial`) rather than a new capability asserting anything.
- **No human gate, structurally:** `ingest_run` calls `classify()` directly with no confirmation,
  review or approval step anywhere in its call graph — checked both by signature (no
  `review`/`approve`/`confirm`/`human`-shaped parameter exists) and by source text (no
  `input(`, `sign.human`, `approve` or `confirm` anywhere in the function). The safety argument
  this rests on — grade-5-by-construction, `grade_5_only_path_never_prices`, contestability
  (build ticket 60), calibration over the skill-eval harness's own threshold — is documented in
  `twin/ingest.py`'s module docstring, per decision ticket 11 Q2.
- **Every item is provenanced:** each classified item (and each classification failure) carries
  `{substrate, recipe, model_version, index}` — the substrate blob's own content-hash reference
  (`twin/blob.py`, exercised for real at build ticket 48), the recipe id and model version, and
  the item's own index in the batch.
- **Throughput measured, not assumed:** `throughput_report()` times the loop's own wall-clock and
  computes `items_per_second` from what actually happened; a zero-elapsed call reports `None`
  rather than a fabricated rate or a `ZeroDivisionError`.
- Extends the invariant suite (one harness guard, no manifest or golden-digest change: the new
  guard is a "property of a module's contract" guard, the same shape
  `signal_classify_is_grade_5_by_construction` is, not one of the constitution's fixed sixteen;
  it touches no `twin/capabilities/*.yaml`, so `Capabilities.digest` — and every artefact's pins
  — are unchanged).
- Declares its depth grade by flowing through the existing `caps.depth_block(["domain-model",
  "provenance", "sense-move"])` — `sense-move` (owning decision ticket 11) stays honestly
  `partial` (4/8, unchanged by this ticket: it reinforces AC2, "the binding mechanism decided,
  incl. what is automated vs judged vs reviewed" — already checked by build ticket 43 — at the
  volume decision ticket 11 Q2's own resolution text names, rather than newly satisfying a
  different, unchecked criterion).
- `ponytail:` no `twin` CLI verb. Every other "runs unattended" pipeline in this codebase
  (`twin sweep`, `twin gameplay-sweep`) is wired to `twin/cli.py`, but a recipe has no on-disk
  home in a model repository yet (build tickets 49/52's territory) — wiring a CLI flag set now
  would invent that format ahead of the ticket that owns it. `ingest_run` is a typed function,
  exercised at seam 2, the same shape `schedule.sweep()` was before build ticket 09 wired its own
  verb. Add `twin ingest` once a recipe has somewhere to live in git.

**A pre-existing, unrelated gap found while verifying, not introduced here:** `pytest -q` on the
full suite reports `1 failed, 1014 passed`. The one failure is `drift_window_was_declared_before_it_was_measured`
(build ticket 64), and it is a worktree-sync artefact, not a defect in this ticket's own work —
this worktree's branch was cut from a stale base missing all twin/ history (the same gap named in
this branch's own `Sync worktree to main tip` commits), and restoring `estate/driftwood/drift/`
into a fresh branch necessarily commits it *now*, after the probe samples it carries were
originally recorded on main. Commit `2ff6be7` (this branch's own history, build ticket 61's
worktree) hit the identical gap syncing the same directory and left it open ("confirmed by a full
pytest run (882 passed, 2 failed, both this)"). Re-running the full suite before and after this
ticket's own change confirms the count of failures is unchanged (one, the same one) — this
ticket's own tests (`tests/test_ingest.py`, 11/11) and every other previously-green test still
pass. `mypy twin tests conftest.py` passes with no issues. Fixing the drift-window gap needs the
worktree's `estate/driftwood/drift/` commit to carry an honest historical date, which needs the
kind of history-editing this session's safety tooling correctly declines to perform blind — it is
exactly the pattern `drift_window_was_declared_before_it_was_measured` exists to catch, and the
right fix belongs to whoever integrates the branches with visibility across all of them, not to a
single ticket's worktree.
