# 02 — The invariant suite: harness, refusal tests, pending manifest, hash protection

**What to build:** The guardrail that makes a seventy-way split safe. Most of the spec's non-negotiables are
**absences**, and an absence never shows up in a diff — a new feature does, a removed refusal does
not. This ticket builds the suite that asserts them at seam 1 (the artefact CLI).

Most invariants have no subject yet at this point, so the suite ships as a **harness plus a manifest
of pending invariants**, each naming the ticket that must activate it. An invariant still pending
after its activating ticket has closed is itself a failure — otherwise "pending" becomes a silent
weakening the guardrail cannot see.

Carry forward the `estate/` verify-script *shape* — a numbered check per claim, each independently
runnable, reporting pass/fail — because it produced an honest 27-of-28 rather than a rounded-up
result. Nothing else from that effort transfers.

**Blocked by:** 01

**Status:** ready-for-agent

**Reading list:** Decision tickets 20 (skill inventory, the standing guards), 22 (the honest boundary). Spec: Testing Decisions, seam 1. Constitution.

- [ ] The manifest names all thirteen invariants with an activating ticket for each: `no_collapse_mechanism`, `no_recommended_action_field`, `no_special_category_slot`, `world_never_references_overlay`, `as_consumed_admits_no_post_T_fact`, `grade_5_only_path_never_prices`, `ruin_class_absent_not_priced`, `prefilter_precedes_pricing`, `derived_never_human_signed`, `every_artefact_marked`, `every_capability_depth_graded`, `identical_pins_identical_bytes`, `only_as_consumed_scores`.
- [ ] Invariants whose subject exists at ticket 01 are live and green; the rest are explicitly pending.
- [ ] CI fails if an invariant is still pending after its activating ticket is closed.
- [ ] Each invariant's test body is hashed into a committed manifest; CI fails on a hash change whose commit does not cite an authorising decision ticket.
- [ ] `identical_pins_identical_bytes` runs on **two different machines/architectures** in CI, not one — seeded floating-point identity across platform maths libraries is the landmine, and it is cheap now and architectural later.
- [ ] Each check is independently runnable and self-describing, verify-script style.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
