# 09 — The two ADRs and the amendments

Type: task
Status: open
Blocked by: 04, 05, 08

## Question

Reach the destination.

1. Write one ADR for Laya and one for loophole. Each cites the number this map measured. An ADR
   that cites a vendor number fails this ticket.
2. Amend the `CONTEXT.md` twin entry. It says today that anything needing judgement is a skill a
   human runs. The owner amended that on 2026-09-21.
3. Amend `.claude/skills/classify-and-judge/SKILL.md` and
   [ADR-0024](../../../docs/adr/0024-the-daily-clock-the-caged-observation-lane-and-the-derived-ledger.md).
   Both say today that nothing runs on a GitHub clock.
4. Record the owner's amendment to eco-system ticket 75 Q10 with its date and its condition. Do
   not rewrite the original. Add a dated note, as this estate does.
5. Graduate any adoption work as tickets on the eco-system map. Work that this map rules out goes
   to that map's Out of scope with one line and a link.

## Done

Two ADRs, the three amendments, and the eco-system map updated.

## Notes

A rejection is a valid outcome for either tool, and needs the same ADR. The measured number
decides, not the effort already spent.

**Added 2026-09-21, from ticket 01.** Laya's ADR must weigh four things that no measurement will
change: the weights repository ships no LICENSE file, training data provenance is unpublished, no
independent evaluation exists, and the repository is days old with a fast-moving `main`. An estate
that pins everything and prices every hole has to say what an unprovenanced model weighs.

**Added 2026-09-21, from ticket 06.** loophole's ADR has a narrower range of outcomes than Laya's,
and the narrowing happened before any measurement. loophole carries no licence, so it can never be
vendored, forked into the estate, or reimplemented. The only adoption available is an external tool
a human runs from a scratch clone. The ADR must say that, and must say that the `claude -p` adapter
drops the deliberate temperature split between the finder and the judge.
