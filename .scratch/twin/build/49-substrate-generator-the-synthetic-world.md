# 49 — `substrate-generator`: the synthetic world

**What to build:** Generate the world — org events, communications, HR records, telemetry — as the **medium** in which
instrumented test cases sit. Believability serves measurement rather than competing with it, and
where they conflict, **measurability wins**.

The second of the two hardest tickets, split from the recipe mechanics for that reason.

**Blocked by:** 48

**Status:** done (2026-08-12)

**Reading list:** Decision ticket 12 (synthetic substrate). Spec stories 54, 55.

- [x] Skill generates a coherent multi-modal substrate from a pinned recipe.
- [x] Generation is seeded and regenerable via ticket 48's mechanics.
- [x] Output is mundane by default — the substrate is mostly uninteresting, because real ones are.
- [x] Where believability and measurability conflict, the resolution is recorded, and measurability wins.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-12)

`twin/substrate_generator.py`, `tests/test_substrate_generator.py`, one `skill-thresholds.yaml`
entry (`substrate-generator`), one harness guard
(`substrate_generator_is_mundane_by_default_and_records_measurability_winning`).

- One pinned `SubstrateRecipe` (ticket 48, unmodified) in, a coherent multi-channel substrate out —
  events, communications, HR, telemetry — decision ticket 12's own four examples of the medium.
  Every batch shares one seed-derived "focus" entity across all four channels, so it reads as one
  coherent batch rather than four unrelated lists of sentences.
- **Seeded and regenerable via ticket 48's mechanics, literally**: each channel's lines are
  produced by calling `substrate.generate_deterministic` itself (a derived per-channel recipe,
  still pure `random.Random`), so two calls against the identical recipe reproduce byte-for-byte.
  This is the fifth of the six skills seam 3 evaluates, and — like the other four — a heuristic
  reference implementation, not a live model call.
- **Mundane by default, structurally**: at most one planted signal per channel
  (`SubstrateGeneratorError` refuses a recipe that schedules more than the four channels can each
  carry one of, rather than silently dropping the overflow), so even a batch at that ceiling stays
  above `MIN_MUNDANE_FRACTION` (0.7).
- **The believability/measurability conflict is recorded on the artefact, not only decided in
  prose**: a believable substrate would scatter a plant at a random position and vary how many
  land per channel; this generator always inserts a channel's plant at the fixed midpoint index,
  and every batch's own `resolution` field says why — checked against real output by
  `tests/test_substrate_generator.py::test_the_resolution_names_measurability_winning_over_believability`.
- Registered into the seam-3 eval harness exactly as `signal-classify` through `gameplay-lens`
  are: one `skill-thresholds.yaml` entry (0.8), a three-recipe labelled corpus (zero, sparse and
  one-per-channel plant schedules), and a harness guard carrying reproducibility, the
  mundane-fraction floor at the ceiling, the recorded resolution and the real corpus passing (with
  a silent generator failing it) into the permanent suite.
- Does **not** move the `synthetic-substrate` capability grade or its digest: AC 3 (the planting
  protocol) asks for the full strength/lead-time/burial/difficulty-distribution bundle, this ticket
  builds burial only, and `twin/capabilities/synthetic-substrate.yaml` is untouched — still 1/7,
  `partial`, re-asserted rather than left to drift
  (`tests/test_substrate_generator.py::test_the_synthetic_substrate_capability_grade_stays_partial`).
  No capability file changed, so no golden digest needed re-blessing.

Not built: spine anchoring against the public record (50), the fidelity eval suite that tunes
signal-to-noise, plant difficulty and reporting asymmetry against a target (51) — deliberately,
per this ticket's own scope.
