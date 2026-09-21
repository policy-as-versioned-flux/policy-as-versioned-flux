# 05 — "Within thresholds" becomes a checkable permission

Type: task
Status: open
Blocked by: none

## Question

On 2026-09-21 the owner permitted a model to judge on a GitHub clock, within thresholds. Turn that
condition into something a check can grade.

Today the estate forbids it in two places. `CONTEXT.md` says anything needing judgement is a skill
a human runs. `.claude/skills/classify-and-judge/SKILL.md` sets `disable-model-invocation: true`
and says nothing there ever runs on a GitHub clock.

Design and build the permission:

1. A model may judge on a clock for one skill only when the newest recorded score for that skill
   and that `model_version` clears the versioned threshold in `twin/skill-thresholds.yaml`.
2. The corpus digest of that scoring run must match the corpus in the tree. A stale digest revokes
   the permission.
3. The clock records which `model_version` judged each claim. A claim with no recorded model is
   not a permitted claim.
4. The permission covers judging only. It never covers merging. A judged claim still lands as a
   pull request that a human merges.
5. A skill with no recorded score has no permission. Absence is not consent.

6. **The permission binds at a seam the actor cannot route around.** Added 2026-09-21 from ticket
   10, and it is the most valuable thing that ticket found. The trdrbot prior art has a complete,
   working permission ladder that its own open defect I-68 records as consulted **twice in 89
   decide cycles**, a rate of 2.2%. Its own words: "The refusals that matter are therefore not the
   sizer's; they happen upstream in prose." A permission the caller may decline to consult is not
   a permission. Name the seam, and prove by a check that no path reaches a judged claim without
   crossing it.
7. **Count the refusals.** trdrbot's sibling defect I-16 records that declines are never scored, so
   the blind spot has two halves. A skill that declines to judge must leave a counted row, or the
   permission's real exercise rate is unknowable.

Write a gate check that grades all seven, and wire it into the truth surface.

## Done

The permission rule in code, a gate check, and the check recorded on a citable run.

## Notes

Build this whether or not Laya passes ticket 04. The rule is estate doctrine about any model on a
clock. Laya is only the first candidate to meet it.

The threshold is the weak link, not the mechanism. `twin/skill-thresholds.yaml` already refuses a
lowered threshold with no `authorised_by`. A threshold measured on 4 items is still a threshold
measured on 4 items. Ticket 03 owns that problem. Say so in the check's own output.

**Ticket 10 resolved 2026-09-21, and this ticket is unblocked.** Its verdict on the size ladder was
**leave the mechanism, take its failure**. Items 6 and 7 above carry that failure across. Do not
copy the ladder's shape. The tier counts 0, 5, 15 and 40 are chosen, not derived, and only the 40
has a measured basis.
