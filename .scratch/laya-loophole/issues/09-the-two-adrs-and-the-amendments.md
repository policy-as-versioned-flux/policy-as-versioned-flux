# 09 — The two ADRs and the amendments

Type: task
Status: open
Blocked by: 04, 05, 08, 11

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

**Added 2026-09-21, from ticket 07.** Three things the loophole ADR must state, each measured.

- **One round costs 8 model calls the way this estate runs it, 185.8 s, and 0.4150 USD at list
  price**, which the subscription absorbs. The published loop costs 14, and the 6 extra calls are
  the Legislator rewriting the norm document. This estate does not let a model rewrite its own ADR,
  so the Legislator never runs and every case is judged against one fixed text.
- **`--bare` must never appear in the invocation.** It never reads OAuth, so with no
  `ANTHROPIC_API_KEY` the call fails with exit code 0, `subtype: "success"` and
  `result: "Not logged in · Please run /login"`. The obvious adapter hands that sentence to the
  parser, which returns zero candidates, and loophole then prints that the legal code appears
  robust. A broken login reads as a clean bill of health. The ADR states the guard, not the flag.
- **A clean run needs two counters at zero, not one.** Ticket 07's negative control shows that the
  `<scenario>` tag counter catches a malformed tag but misses a total format collapse. The
  under-production counter catches that case. The ADR names both.
