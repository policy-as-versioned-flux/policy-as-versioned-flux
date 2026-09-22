# 118 — A green that rests on luck may not promote

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-21 from [the Laya and loophole map](../../laya-loophole/map.md), ticket 10.

Renumbered from 111 to 118 on 2026-09-22 by
[ticket 117](117-two-tickets-share-the-number-111.md). It took 111 after
[111 — The cage names priority classes its own delivery does not deliver](111-the-cage-names-priority-classes-its-own-delivery-does-not-deliver.md)
had already landed on main, so it is the later of the two.

The skill-eval harness records two states. `twin/skills.py:103` declares
`ItemResult(item_id, passed: bool)`, and `EvalResult.score` is the fraction that passed. A skill
that reached the right answer for the wrong reason is therefore indistinguishable from one that
reasoned correctly. Both raise the score, and the score is what a threshold grades.

The trdrbot prior art solves this with a twelve-line pure function of two booleans,
`attribute(thesis_held, profited)`. It yields five verdicts, and the lucky-win case carries a
learning signal of `None` so the memory update is **skipped** rather than applied at 0.5. That was
measured, not guessed: a 0.5 "learn nothing" signal was dragging every block toward 0.5.

1. Add a third state to `ItemResult`. A right answer whose stated basis is wrong is neither a pass
   nor a fail. Decide the name, record it with the reason, and do not reuse `passed`.
2. Exclude that state from the numerator, not from the denominator. Luck must lower the attributable
   rate, not raise the score.
3. Where a skill's corpus item carries no checkable basis, mark it unscoreable rather than passed.
   `twin/scoring.py:16` already has `ScoreError`, "not scoreable, a refusal", so the estate holds
   the concept and the harness does not.
4. Wire a gate check. A threshold graded on a score that counts luck grades nothing.

## Done

Three states in the harness, the attributable rate recorded beside the score in
`twin/skill-scores.jsonl`, and a gate check that grades it.

## Notes

The estate is **ahead** of the prior art on scoring rules and baselines. `twin/forecast_book.py`
has blindness by construction, co-registration and an external adversarial baseline. Take the
attribution idea only. Do not import the rest.

Licence and attribution: the source is MIT and its copyright line names a real person. Crediting
the idea in public is a named-individual question for ticket 82.
