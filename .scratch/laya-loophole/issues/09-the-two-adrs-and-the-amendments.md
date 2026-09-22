# 09 — The two ADRs and the amendments

Type: task
Status: resolved
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

## Answer

Resolved 2026-09-22. The destination is reached: two ADRs, three amendments, one defect fixed,
three tickets graduated, and the eco-system map updated.

### 1. The two ADRs

**[ADR-0029 — A candidate model enters on a measured permission, and Laya does not hold one](../../../docs/adr/0029-a-candidate-model-enters-on-a-measured-permission-and-laya-does-not-hold-one.md).**
**Laya is refused.** Not by a bad score alone, but by the estate's own rule:
`verify/model-permission/verify-model-permission.sh` reports **0 of 14 (metric, model version)
pairs hold a permission**, and the ADR tabulates which of the ten conditions refuses each pair.
Laya is refused on items 1, 2, 5, 8 and 9 across the seven metrics; **the incumbent heuristic is
refused too**, on item 10, because it is graded on the corpus it was fitted on. That second
refusal is the strongest thing the ADR says about its own fairness: a rule that cleared the
incumbent and refused the candidate would be a rule fitted to the answer.

Eleven points. Every score carries the best constant answer its own corpus admits beside it, in
one table. `substrate-generator` is recorded as **not measurable** and not as 0.000. The pin
outside the vendor's package and the pinned `transformers==5.9.0` build are both conditions of
entry, not footnotes. `act_probability` is refused as a permission signal, and the near-constant
head is named as the same defect loophole's judge carries. The `noul` route disagreement is
reported and **not** presented as a win. The four things no measurement changes — no LICENSE file
at the pin, unpublished provenance, no independent evaluation, a days-old repository with a
fast-moving `main` — are weighed rather than listed: they set the terms and raise the bar, and
the measurement did not clear a lower one. Point 10 states the six terms a candidate may
re-enter on, so the ADR refuses Laya and not the class.

**[ADR-0030 — loophole runs as an external tool, in rounds, and the estate keeps the pointer and throws the sentence away](../../../docs/adr/0030-loophole-runs-as-an-external-tool-in-rounds-and-the-estate-keeps-the-pointer.md).**
**loophole enters**, in the only shape its licence permits: an external tool a human runs from a
clone that stays outside the project tree, never vendored, forked or reimplemented. Nine points.
The unit of adoption is **three rounds against one document**, with the honest caveat that three
is not enough to fix the number. The budget is stated twice: 24 calls, about 9 minutes and about
1.24 USD at list price for the model, and **roughly three times ticket 08 for the checking**,
which is the half anyone would forget. The Legislator never runs. The judge's verdict is not a
filter, so every candidate goes to a deterministic check. `--bare` never appears and the guard is
on the failure shape rather than the flag. A clean run needs two counters at zero. Output is
kept and input never, proved by a reusable check. It never becomes a gate check.

### 2. The three amendments

- **`CONTEXT.md`, the Twin entry.** The sentence now reads: anything needing judgement is a skill
  a human runs, **unless a model holds a measured permission for that skill**. It names the
  owner's amendment with its date, cites `twin/model_permission.py` and ADR-0029, and states that
  0 of 14 pairs hold one, so **today the sentence reads exactly as it did before** and the
  difference is that a check observes it. This file was untouched on purpose until this ticket
  landed, as the map required.
- **ADR-0024 point 6** gains a dated note in its Consequences, in the estate's own shape: the
  point's own text is not rewritten. It carries the owner's amendment, the scope (the GitHub
  clock alone), the ten conditions, the derived clock and the assertion that no workflow may set
  or clear a marker, the seam inside the claim validator, the two validators the clock's steps
  table names, and what does not change: nothing about the lane, D1 or D2.
- **`.claude/skills/classify-and-judge/SKILL.md`** already carried ticket 05's amendment, which
  described the mechanism and changed no rule. It now cites the two ADRs and repeats that nothing
  in its opening sentence or its ordinary path changes.

### 3. The ticket 75 Q10 note

`.scratch/ecosystem/issues/75-...md` gains a new section, **Amendments to the answers above,
dated, with the original left as it stands**. Item 10 is not rewritten: it recorded the owner's
2026-09-03 constraint and that was true when written. The note records the 2026-09-21 answer, the
condition as built (ten conditions, not a threshold, because five of seven thresholds sit at or
below their own corpus's best constant answer), the scope (the GitHub clock alone; ticket 92's
local clock untouched), and that it grants nothing today.

### 4. Item 6: the twin-evals baseline defect is fixed, not recorded

`verify/twin-evals/verify-twin-evals.sh` graded the incumbent's fresh score against
`history_for(skill)[-1]`, the last row of **any** model version. Recording six Laya rows had made
Laya the incumbent's bar: before the fix the run printed `last=0.870`, `0.500`, `0.000`, `0.333`
and `0.200` for five of the seven metrics, so **the incumbent could have fallen from 1.000 to
0.600 and still read `pass`**. Five of the seven regression comparisons were dead.

Fixed by scoping the comparison to the row's own `model_version`, in a named `last_for()` with a
docstring saying why it is still not `detect_regression()`. It carries a **negative control in
both directions** on synthetic rows: a candidate's row is invisible to the incumbent's bar, the
incumbent's own last row is still read, a version never recorded returns `None`, and the exact
case that was dead now derives `fell` while the old read derives `pass`. After the fix all seven
metrics read `last=1.000` and the check exits 0. The script header and the
`talk/verify-manifest.txt` row both say what changed and why.

### 5. Graduated, and ruled out of scope

Three tickets on the eco-system map:

- [115 — A loophole round is a procedure this estate can re-run](../../ecosystem/issues/115-a-loophole-round-is-a-procedure-this-estate-can-re-run.md).
  The adoption work ADR-0030 creates. The harness is a wayfinder asset in `.scratch/`, the two
  guards are remembered rather than asserted, and the prompt-leak check is run by hand.
- [116 — The twelve unchecked loophole candidates](../../ecosystem/issues/116-the-twelve-unchecked-loophole-candidates.md).
  Fog until ADR-0030 fixed the unit of adoption at three rounds, which turns 12 unread candidates
  into a gap. At the measured survival rate the eight new ones hold about two or three real
  defects, and nobody has looked.
- [117 — Two tickets share the number 111](../../ecosystem/issues/117-two-tickets-share-the-number-111.md).
  Found by ticket 08 and unfixed. `ecosystem_ticket_status()` takes `sorted(glob(...))[0]`, so a
  `waits_on` row reads whichever sorts first. Both tickets are open today, so it is harmless; the
  first one to close makes it wrong and silent.

Four lines in the eco-system map's **Out of scope**, each with its reason and a link: Laya and
any adoption of it, a corpus bought or built for a specialised fit, vendoring or reimplementing
loophole, and either tool as a gate check. Two lines stay as fog there: whether a model on a
GitHub clock ever presents itself honestly in a real Actions run, which nothing can measure until
a model holds a permission; and the kyverno 1.19.1 compile failure, which belongs with ticket
71's engine-version matrix and fails loudly rather than quietly.

### What this ticket refused to do

- **It did not soften either refusal into a "monitor and revisit".** Laya is refused by a named
  condition and re-enters on six stated terms. A hedge would have left the estate with a model
  that never enters and never leaves.
- **It did not delete the six Laya rows** from `twin/skill-scores.jsonl`. They are the first
  independent measurement of this model on anything, and deleting an unflattering measurement is
  the defect this estate exists to refuse. Item 6 fixed the check instead.
- **It did not rewrite ADR-0024 point 6 or ticket 75 item 10.** Both were true when written. The
  estate amends by dated note, as ADR-0015 was amended.
- **It did not claim the loophole survival rate is a property of the tool.** "About a third"
  rests on six checked candidates from one round, and the ADR says so in its own Consequences.

### Checks named by this answer

- `verify/twin-evals/verify-twin-evals.sh` — the fix in item 6. PASS, exit 0, all seven metrics
  reading `last=1.000` against the incumbent's own row.
- `verify/model-permission/verify-model-permission.sh` — the rule ADR-0029 rests on. PASS,
  0 granted of 14 pairs.
- `verify/map-surface/verify-map-surface.sh` — the eco-system map edits. PASS.
- `verify/cited-truth/verify-cited-truth.sh` and `verify/derived-status/verify-derived-status.sh`
  — the ticket 75 note and the three new tickets. Both PASS.

All four were run locally on 2026-09-22 on a moved estate clone, so no TRUTH line is quoted here
and no count from this run compares to a citable run. What is named is the exit code of each
script, which is what this ticket changed.
