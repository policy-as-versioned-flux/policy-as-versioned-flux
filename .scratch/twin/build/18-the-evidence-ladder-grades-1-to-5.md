# 18 — The evidence ladder, grades 1 to 5

**What to build:** A typed ladder from **1 (dated natural experiment)** to **5 (model assertion)**, with the grade
travelling with the claim rather than living in a side table. The strength of a claim has to be
inseparable from the claim, because the whole use-gating mechanism depends on it.

**Blocked by:** 17

**Status:** done (2026-08-06)

**Reading list:** Decision ticket 08. Spec story 22.

- [x] Five typed grades with written admission criteria per grade, versioned.
- [x] The grade is a required field on every causal claim; an ungraded claim does not load.
- [x] Grade is immutable without a provenanced regrade event recording who and why.
- [x] A regrade upward is distinguishable from a regrade downward in the record — the former is the one to be suspicious of.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-06)

`twin/evidence-ladder.yaml`, `twin/evidence.py`, the `regrade` schema and collection, and the
grade-history gate in `twin validate`.

- **The ladder is data, not code.** Five typed rungs, each with a written admission criterion and
  a worked example, in a versioned YAML file a reader who does not write Python can diff. It is
  validated on read: a ladder that has lost a rung, or whose `may_price` flags disagree with its
  threshold, is refused rather than allowed to gate on nothing while still looking published.
- **The grade travels with the claim.** `evidence_grade` on a claim was `whole` — any
  non-negative integer. It is now the ladder's rung, so an off-ladder grade does not load, and
  every emitted causal edge carries `evidence_grade_name` and `may_price` beside the number. A
  reader should not have to hold a five-rung ladder in their head to know what admitted a claim.
- **A grade is immutable without a provenanced regrade event**, guarded at two depths. At load,
  the recorded chain must be contiguous and must end at the grade the file declares. At `twin
  validate`, the file's **git history** is read and every observed change must be covered by a
  regrade event — which is the one that bites on the first unrecorded edit, when there is no
  chain yet to be inconsistent with. `fixtures.plant_unrecorded_regrade` plants exactly that and
  the check catches it.
- **Direction is derived and named, never authored.** `up` is ambiguous on a ladder whose
  strongest rung is numbered 1, so a regrade is `strengthened` (to a lower number) or `weakened`.
  Strengthening is the direction to be suspicious of — it is how a model assertion becomes a
  measurement — and the record makes the two distinguishable at a glance. The schema is closed,
  so `direction` cannot be typed into a regrade file.
- **A regrade names a role, not a person**, and an unregistered role is refused: a role nobody
  holds records nobody.
- The pocket-org worksheet gained lines 30-31, and the fixture carries one regrade in each
  direction.

Not built: the history check does **not follow renames**, so moving a file and changing its grade
in one commit reads as a new file at its original grade. The limit is named in `twin/evidence.py`
rather than implied. Decision ticket 08's acceptance criteria are untouched by this ticket — the
ladder is one clause of AC 1, which build ticket 17 already ticked, so `causal-layer` gains no
tick here and stands at 1/5.
