# 42 — The skill-eval harness (seam 3)

**What to build:** The six skills are **non-deterministic by construction**, so they cannot be asserted at seam 1 or
seam 2 at all. This harness runs each against a fixture corpus and scores its output against expected
classifications with a **pass threshold, not exact match**.

It also records **score-over-time per skill per model version**, so a model upgrade that degrades
judgement shows up as a regression rather than being discovered inside an artefact months later.
Without this seam, skill regression is the failure most likely to go entirely silent.

**Blocked by:** 03

**Status:** ready-for-agent

**Reading list:** Decision ticket 20 (the determinism split). Spec: Testing Decisions, seam 3.

- [ ] Harness runs a skill against a fixture corpus and produces a threshold-based pass/fail plus a score.
- [ ] Score-over-time recorded per skill per model version, and a degradation is surfaced as a regression.
- [ ] Thresholds are versioned; lowering one is a visible, cited change.
- [ ] The harness is skill-agnostic — adding a skill requires a corpus, not harness changes.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
