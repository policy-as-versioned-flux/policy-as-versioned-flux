# 46 — `gameplay-lens` and the scheduled opportunity sweep

**What to build:** Wardley plays whose **preconditions actually hold**, plus doctrine and climate suggestions — the
suggestion-shaped part of Wardley that is a skill rather than inherited maths.

Run on a **schedule**, because threats push themselves forward and opportunities never do. The sweep
is the structural counterweight to the evidence record's negativity bias, and without it the twin is
merely a better fear machine.

**Blocked by:** 42, 14, 09

**Status:** done (2026-08-11)

**Reading list:** Decision ticket 13; research 03, 04. Spec stories 41, 42.

- [x] Skill proposes plays with their preconditions stated and checked against the current map.
      `twin/gameplay_lens.py::propose()` — a two-play catalogue (`land-grab`,
      `exploit-commoditisation`) checked against evolution position/stage, `needs`-edge dependency
      structure and ownership (`maintains`/`knows`/`owns` edges), reused from the same graph
      `verbs.graph()` already emits. Every proposed opportunity carries its checked
      `preconditions` and a `reason` naming them, plus the honest gap: decision ticket 13's own
      worked example also names incumbency ("no incumbent holds position"), which this map has no
      data for, so that leg is named unchecked rather than silently dropped.
- [x] Scheduled sweep runs without human initiation and emits opportunity candidates.
      `twin/gameplay_lens.py::sweep()` — no scenario or component is named at the call site
      (asserted directly in `tests/test_gameplay_lens.py::test_sweep_runs_without_a_named_scenario_or_component`);
      it walks every org overlay of every named repository unconditionally, the same
      "list of repositories, no staleness skip" shape `schedule.sweep()` (build ticket 09) uses.
      Wired to `twin gameplay-sweep --repo R [...]` (`twin/cli.py`) so a scheduler can call it the
      same way `twin sweep` already is.
- [x] Evaluated against plays whose preconditions are known to hold or not.
      `twin/gameplay_lens.py::labelled_corpus()` — three org maps built fresh from
      `twin/fixtures.py`: netflix (`land-grab` fires on `streaming-experience`), intel (nothing
      fires — custom-built, no ownership edges at all), pocket (`exploit-commoditisation` fires on
      `shared-database`). Registered in `twin/skill-thresholds.yaml` at 0.65 and run through the
      seam-3 harness (`twin/skills.py::evaluate`) in both `tests/test_gameplay_lens.py` and the
      new harness guard below.
- [x] Opportunity output volume is reported alongside threat output volume, so the counterweight is measurable.
      `sweep()`'s own artefact body carries `counts.opportunities` beside `counts.signals` (each
      org's bound-signal count, the push-side proxy decision ticket 13 Q3 names — "a threat
      announces itself, a signal lands, binds"), plus a per-org `by_org` breakdown of both. Asserted
      in `tests/test_gameplay_lens.py::test_sweep_reports_opportunity_volume_beside_signal_volume`
      and in the harness guard below.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`gameplay_lens_is_grade_5_and_reports_no_recommendation`,
      `twin/invariants/harness.py`) — grade-5-by-construction plus the labelled corpus, and
      re-asserts `no_recommended_action_field`'s own banned-word scan against the sweep artefact,
      the third artefact to carry that re-assertion after the Wardley map and the trade-off curve.
      Zero invariants weakened. The committed `twin/invariants/golden-digests.json` was re-blessed
      (`twin verify --bless-goldens --authorise "decision ticket 13 — ..."`) because every
      artefact's `capabilities_digest` pin moves when any capability checklist changes — the
      derivation itself is untouched, only the depth-grade total.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `twin/capabilities/scenario-engine.yaml` AC4 ("How opportunity/gameplay moves are proposed,
      with the negativity counterweight addressed.") ticked, evidence citing this module.
      `scenario-engine` moves from 2/7 to 3/7 checked — still `partial`, not `full`; four ACs
      remain (where scenarios live/are versioned, library admissibility, the selection rule, and
      exercise on the co-flagships — build tickets 69/71-77).
