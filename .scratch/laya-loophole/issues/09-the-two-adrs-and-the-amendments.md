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

**Added 2026-09-21, from ticket 04. The Laya ADR's measured number has arrived.**

Laya loses five of six metrics to the heuristics, ties the sixth, and on five of six does not beat
a constant answer on the same corpus. `substrate-generator` is not measurable against it at all.
Six rows are recorded in `twin/skill-scores.jsonl` at `model_version: laya-1c5edc17`, on the same
six corpus digests `heuristic-0.1.0` was scored on. Five things the ADR must carry.

- **State the number and its bar together.** A score without the best constant answer its corpus
  admits is not a result. `signal-classify` grades at 0.80 on a corpus where "always economic"
  scores 0.913, and Laya's recorded row reads `"passed": true` at 0.870 while catching **neither**
  of the two items the corpus exists to discriminate. A corpus baseline is a condition of entry,
  not a caveat.
- **Give the incumbent's 1.000 no more weight than the candidate's number.** Ticket 03 measured
  five of six thresholds as unfalsifiable on their own corpora. Ticket 04 found two more reasons:
  `signal-classify`'s threshold sits under its own majority-class baseline, and
  `causal-claims`' elasticity constant is exactly the mean of its own four labels inside a
  tolerance that covers all four. Neither side of this bake-off has been shown to judge.
- **Refuse `act_probability` as a permission signal, and say why in the ADR.** It read exactly
  1.000000 on all 279 calls across three runs. Two more near-constant heads appeared in the same
  run. This is map call 14, now measured four times in one model.
- **State the pin as a condition, not a footnote** (map call 10), and state the split environment:
  the bake-off ran in ticket 02's own venv at `transformers==5.9.0`, because `laya` 0.3.4 permits
  a 4.x build that loads the checkpoint and silently gives different numbers.
- **Do not present the route disagreement as a win.** On `evolution-judge` the declared primary
  route scores 0.500 and the declared `noul` sensitivity route scores 4 of 4 with the rank order
  correct. Both were fixed in code before the run, and 4 items cannot tell them apart at 95%. The
  honest sentence is that the continuous head carries signal where the band classifier does not,
  and that nothing here measures it well enough to enter on.

6. **Fix or record the twin-evals baseline defect.** `verify/twin-evals/verify-twin-evals.sh`
   grades the incumbent's fresh score against `prior[-1]["score"]`, the last recorded row of **any**
   model version. Recording Laya moved the heuristic's baseline for the next run. It is harmless
   only while the incumbent scores 1.000 and a candidate can at best tie. Either scope the
   comparison to the incumbent's own `model_version`, or record the hazard with its reason. Found
   by ticket 04 and unfixed.

**Added 2026-09-21, from ticket 05. This ticket is now the frontier: every other ticket on the
map is resolved.**

The permission exists, it is on the truth surface, and **it grants nothing**. 0 of 14 (metric,
model version) pairs hold one. That changes what three of the five items above have to say.

- **Item 1, the Laya ADR.** Laya is now refused by the estate's own rule, not only by a bad
  score. It fails items 1, 2, 5, 8 and 9 across the seven metrics. State the refusal as the
  rule's output, and cite `verify/model-permission/verify-model-permission.sh`.
- **The ADR must also say the incumbent is refused**, on the tenth condition: `heuristic-0.1.0`
  is graded on the corpus it was fitted on. A rule that cleared the incumbent and refused the
  candidate would be a rule fitted to the answer. This is the strongest thing the ADR can say
  about its own fairness.
- **Item 3, the two prose amendments.** `.claude/skills/classify-and-judge/SKILL.md` already
  carries a dated amendment from ticket 05 that describes the mechanism and changes no rule: its
  "nothing here ever runs on a GitHub clock" still stands, because nothing holds a permission.
  ADR-0024 still needs its own. **`CONTEXT.md` is untouched on purpose** — the map forbids
  assuming the new wording before this ticket lands.
- **Item 4, the ticket 75 Q10 note.** The condition to record is the ten-condition rule in
  `twin/model_permission.py`, and the scope: the permission governs the **GitHub** clock alone,
  because that is the clock the owner's words named and the one ADR-0024 forbade. A human run
  and the local clock keep their own terms.
- **A new measured fact for whichever ADR carries the corpus argument.** Five of the seven
  thresholds sit at or below the best constant answer their own corpus admits. Ticket 04 found
  one; ticket 05 derived all seven. It is reported and not graded on the gate, and eco-system
  ticket 112 owns the sizing.
