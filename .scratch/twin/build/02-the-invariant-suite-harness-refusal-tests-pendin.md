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

**Status:** done (2026-08-05)

**Reading list:** Decision tickets 20 (skill inventory, the standing guards), 22 (the honest boundary). Spec: Testing Decisions, seam 1. Constitution.

- [x] The manifest names all thirteen invariants with an activating ticket for each: `no_collapse_mechanism`, `no_recommended_action_field`, `no_special_category_slot`, `world_never_references_overlay`, `as_consumed_admits_no_post_T_fact`, `grade_5_only_path_never_prices`, `ruin_class_absent_not_priced`, `prefilter_precedes_pricing`, `derived_never_human_signed`, `every_artefact_marked`, `every_capability_depth_graded`, `identical_pins_identical_bytes`, `only_as_consumed_scores`.
- [x] Invariants whose subject exists at ticket 01 are live and green; the rest are explicitly pending.
- [x] CI fails if an invariant is still pending after its activating ticket is closed.
- [x] Each invariant's test body is hashed into a committed manifest; CI fails on a hash change whose commit does not cite an authorising decision ticket.
- [ ] `identical_pins_identical_bytes` runs on **two different machines/architectures** in CI, not one — seeded floating-point identity across platform maths libraries is the landmine, and it is cheap now and architectural later.
- [x] Each check is independently runnable and self-describing, verify-script style.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-05)

`twin/invariants/` — `manifest.yaml`, `harness.py`, `checks.py`; run with `twin verify`.

Result today: **12 passed, 0 failed, 8 pending, 2 skipped and not faked.**

- The manifest names **sixteen** invariants, not the thirteen this ticket lists: the constitution's list
  grew by `store_rebuildable_from_git`, `price_levels_never_probabilities` and
  `standing_library_covers_committed_classes` after this ticket was written. Extending, never weakening;
  a harness check reads the constitution and fails if the two lists disagree, so the drift cannot recur.
- Eight are live and green. `derived_never_human_signed` is **activated ahead of its ticket** at
  structural depth — build ticket 11 deepens it to cryptographic signing.
- Body hashes: each live check's source is hashed into the manifest, plus a whole-module hash so a
  weakened *helper* cannot make a check pass unnoticed. Re-pinning needs
  `twin verify --rehash --authorise "decision ticket NN — reason"`, which writes the citation into the
  entry; a hash that moved against the committed manifest with no citation fails.
  Deviation: the citation lives in the manifest entry rather than the commit message — same guard,
  and it survives a rebase.
- A **live invariant that skips counts as a failure**. `pending` is the only honest way to not assert
  something, and it has to be declared where it can be seen.

Two things this guard cannot yet claim, both stated rather than hidden: `hash_changes_are_authorised`
needs two committed versions of the manifest and so skips until the second lands, and the
two-architecture leg below.

**Left unchecked, deliberately: the two-architecture leg has never run.** `.github/workflows/twin.yml`
declares the matrix (x86_64 / aarch64 / arm64-darwin) and `cross_architecture_determinism` skips rather
than fakes outside it; `twin/invariants/golden-digests.json` is committed for the runners to compare
against. The mechanism is wired and unproven. It ticks when CI has actually run green on more than one
architecture, not before.
