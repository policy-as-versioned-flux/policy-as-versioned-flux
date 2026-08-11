# 45 — `causal-claims`, scored on grade accuracy

**What to build:** Propose causal edges with sign, lag and elasticity, flag confounders, and offer alternative
explanations.

**Scored on grade accuracy as hard as on the claim itself.** Over-grading is the dangerous failure:
a skill that confidently stamps a grade-5 assertion as grade-2 defeats use-gating entirely, and that
failure is invisible at seams 1 and 2 — the artefact just looks priced.

**Blocked by:** 42, 18

**Status:** ready-for-agent

**Reading list:** Decision ticket 08. Spec stories 21, 22, 23.

- [ ] Skill proposes edges with sign, lag, elasticity, evidence grade, confounders and alternatives.
- [ ] Evaluated against edges with **known** grades; grade accuracy is a separate reported metric from claim accuracy.
- [ ] Over-grading is penalised asymmetrically relative to under-grading, and the asymmetry is documented.
- [ ] A systematic over-grading drift is detectable in the score-over-time record.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
