# 45 — `causal-claims`, scored on grade accuracy

**What to build:** Propose causal edges with sign, lag and elasticity, flag confounders, and offer alternative
explanations.

**Scored on grade accuracy as hard as on the claim itself.** Over-grading is the dangerous failure:
a skill that confidently stamps a grade-5 assertion as grade-2 defeats use-gating entirely, and that
failure is invisible at seams 1 and 2 — the artefact just looks priced.

**Blocked by:** 42, 18

**Status:** done (2026-08-11)

**Reading list:** Decision ticket 08. Spec stories 21, 22, 23.

- [x] Skill proposes edges with sign, lag, elasticity, evidence grade, confounders and alternatives.
- [x] Evaluated against edges with **known** grades; grade accuracy is a separate reported metric from claim accuracy.
- [x] Over-grading is penalised asymmetrically relative to under-grading, and the asymmetry is documented.
- [x] A systematic over-grading drift is detectable in the score-over-time record.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

**What shipped:** `twin/causal_claims.py` — `propose()` proposes a causal edge (sign, lag, a
calibrated-range elasticity, an evidence grade that genuinely varies with the evidence text, unlike
`signal-classify`'s and `evolution-judge`'s fixed grades) plus a graph-based confounder detector
(`shared_ancestors()`, decision ticket 08 Q5's "free structural check" that build ticket 21 found
still-to-build) and a mandatory, never-empty alternative-explanation field. Registered as **two**
metrics in `twin/skill-thresholds.yaml` on the one skill — `causal-claims` (claim accuracy) and
`causal-claims-grade-accuracy` — via the unmodified `twin/skills.py` harness, so a systematic
over-grading drift is detectable through the existing `record_score()`/`detect_regression()`
machinery rather than a bespoke mechanism. `grade_scorer()`'s asymmetric rule gives zero tolerance
to over-grading and one rung to under-grading, documented at the point it is enforced. Exercised on
both real co-flagship edges (`streaming-displaces-dvd`, `euv-delay-slips-the-node`) plus two more
graded edges from the same fixture. Ticks `causal-layer` (decision ticket 08) checklist item 4 —
the stated confounding discipline — bringing it to 2/5, still `partial`; items 2, 3 and 5 are out
of this ticket's scope and stay unchecked.
