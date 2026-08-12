# 50 — Spine anchoring and free-running

**What to build:** Anchor the substrate to the **immutable public spine** — the real dated record — but let it
free-run where the record is silent.

Both halves matter: anchoring makes the ground truth real, and free-running is what stops plants
being trivially findable by diffing the substrate against the public spine.

**Blocked by:** 49

**Status:** done (2026-08-12)

**Reading list:** Decision tickets 06 (flagship OSINT scoping), 12. Spec story 57.

- [x] Substrate reconciles with the public spine at every dated checkpoint.
- [x] Where the record is silent the substrate free-runs, and a diff against the spine does not reveal plant locations.
- [x] A test attempting the diff attack and failing to locate plants.
- [x] Spine facts carry knowability dates so regime gating works over the substrate.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-12)

`twin/spine.py`, `tests/test_spine.py`, one harness guard
(`substrate_reconciles_with_the_spine_and_the_diff_attack_finds_no_plants`). No new invariant
manifest entry — a harness guard, the same shape build tickets 16, 31, 33, 60-62 and 46/49 left
behind, not a seventeenth invariant.

- **The spine is not a new authored format.** `Spine.from_overlay()` reads an org's own real,
  dated `signal` documents directly (the Carillion/NMC/Wirecard/Enron answer keys already carry
  them) — `DATED_FACTS["signals"] == "date"` (`twin/schema.py`) is already the field
  `twin/regimes.py` gates `as-consumed`/`as-knowable` on, so a spine fact's knowability date is
  the identical field the regime gate already understands, not a look-alike. `Spine.at()` calls
  `regimes.cutoff()` itself for the same reason: a malformed checkpoint fails with
  `regimes.RegimeError`, proving reuse rather than a parallel parser that happens to agree today.
- **Reconciliation is checked, not assumed.** `anchor()` inserts every fact knowable by a
  checkpoint, verbatim, into a generated substrate batch (`twin/substrate_generator.py`'s own
  output shape); `reconcile()` refuses, naming what is missing, if the batch does not carry one;
  `reconcile_at_every_checkpoint()` runs that check once per distinct spine date — the "at every
  dated checkpoint" AC, not only the last one.
- **The diff attack, demonstrated both ways.** `diff_against_spine()` splits every substrate line
  into `anchored` (matches a spine fact verbatim) and `free_running` (everything else). On the
  real Carillion fixture, a batch carrying one planted signal leaves the plant beside dozens of
  non-plant mundane decoys in `free_running` — the diff alone does not single it out. The negative
  control proves the guard measures something real: a batch built the forbidden way
  (generate-everything-from-the-spine, decision ticket 12 Q3's own "actively dangerous" case) does
  expose the plant as the diff's sole residual.
- **Depth grade.** `twin/capabilities/synthetic-substrate.yaml` AC 1 ("the real/synthetic seam
  defined, with a consistency rule between spine and substrate") ticks — `synthetic-substrate`
  moves from 1/7 to 2/7, still `partial`. AC 3 (planting protocol's lead time/difficulty
  distribution) and the rest are unaffected — this ticket did not touch them.
