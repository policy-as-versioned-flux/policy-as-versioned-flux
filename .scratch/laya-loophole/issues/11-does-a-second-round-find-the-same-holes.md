# 11 — Does a second round find the same holes?

Type: task
Status: resolved
Blocked by: 08

## Question

Ticket 07 ran one round and it is one sample. loophole's output is not deterministic, and ticket 07
measured the two things that make that concrete: no temperature flag reaches the finder, and the
served model is newer than the published one. So the six candidates are one draw, not the tool's
answer about ADR-0022.

Run a second round against the same document, at the same pin, with the same inputs, by the same
harness. Then answer one question: **how much of the tool's output is the document, and how much is
the draw?**

1. Run `.scratch/laya-loophole/bench/loophole_round.py` a second time against
   `research/07-loophole-round/inputs/`. Same code sha256, same principles sha256.
2. Record the parse-failure and under-production counters, as ticket 07 did. Both at zero, or the
   run failed.
3. Compare the second round's candidates to the first. Name the overlap. A candidate matches when
   it attacks the same clause for the same reason, not when the words match.
4. State the cost of the second round beside ticket 07's 8 calls, 185.8 s and 0.4150 USD.

## Done

A stated overlap between two rounds. The raw output of round two stored beside round one.

## Notes

This is not a repeat of ticket 08. Ticket 08 asks whether a candidate is real. This ticket asks
whether the tool says the same thing twice. A tool that finds six different holes each time is a
generator, and ticket 09's ADR must say how many rounds a human has to run before the output means
anything.

**Close this out of scope if ticket 08 records a zero survival rate.** A tool that produced nothing
real once does not need its repeatability measured. The map's Out of scope section takes the line.

## Answer

**Two rounds ran, not one, and the overlap between any two rounds is 1 to 3 of 6.
The tool repeats its target and never its mechanism.** Ticket 08 recorded a 2/6
survival rate, so the close-out-of-scope clause did not fire.

Full working: [`research/11-loophole-rounds-two-and-three.md`](../research/11-loophole-rounds-two-and-three.md).

### Item 1 — the runs

Rounds two and three both ran against `research/07-loophole-round/inputs/`. The
harness, the ADR, the principles and the clone are identical to round one by
sha256 and by commit, and all three rounds were served `claude-sonnet-5`.

A third round is beyond this ticket's literal ask. Two rounds give one overlap
number with no way to tell a stable overlap from a lucky one. Three rounds give
three pairwise numbers, and they differ by a factor of three, which is the
finding. The extra round cost 8 calls the subscription absorbs. The call is the
assistant's under ADR-0025.

### Item 2 — the counters

| round | finder parse failures | finder under-production | judge parse failures |
|---|---|---|---|
| two | 0 | 0 | 0 |
| three | 0 | 0 | 0 |

Both counters read zero for both finders in both rounds, so neither run failed
silently. Each round produced 3 loophole and 3 overreach candidates.

### Item 3 — the overlap

No two of the 18 candidates share a run of 8 consecutive words, across all 153
pairs. A word test reports zero. The clause and reason for each candidate are
recorded in `research/11-targets.json`, and every number below is computed from
those two fields.

| pair | same reason | same clause |
|---|---|---|
| one vs two | 2 of 6 | 2 of 6 |
| one vs three | 1 of 6 | 2 of 6 |
| two vs three | 3 of 6 | 3 of 6 |

**All three rounds share exactly one reason: an innocent omission draws the same
bottom rung as deliberate evasion.** All three share two clauses: the `infra`
declaration and the fail-closed default for silence.

**The `infra` declaration is attacked in every round, by four candidates, and no
two give the same reason.** Round one says nothing restricts who runs pods
inside such a Namespace; round one's other candidate says the non-platform
render is silent; round two says nothing says who grants the `platform` role;
round three says nothing restricts which Namespaces a platform party may so
label. The place repeats. The mechanism never does. That is map call 12
measured rather than asserted.

### Item 4 — the cost

| | round one | round two | round three |
|---|---|---|---|
| model calls | 8 | 8 | 8 |
| model time | 185.8 s | 173.5 s | 179.7 s |
| list price | 0.4150 USD | 0.4069 USD | 0.4197 USD |

Three rounds cost 1.2416 USD at list price, absorbed by the subscription. The
price of a round is stable to within 3%, so ticket 09 can budget a round.

### What one round is worth

Three rounds produced 13 distinct reasons from 18 candidates. Chao1 on the
frequencies estimates the tool's reason population at **26.5**, so one round
captures about **23%** of what the tool has to say about this document. That is
a lower bound from three samples of six, with a wide interval, and the
population is the tool's output rather than the document's real defect set.

Combined with ticket 08's 2/6 survival rate, and assuming that rate holds across
the population, which is unmeasured: about 9 real defects sit behind the tool
and one round finds about 2.

### The overlap number is itself a draw

`bench/match_rounds.py` puts the same question to an independent reader three
times, with the candidates anonymised and shuffled from a fixed seed.

| pair | matches per repeat | unanimous across 3 repeats |
|---|---|---|
| one vs two | 2, 2, 1 | **0** |
| one vs three | 2, 4, 3 | 2 |
| two vs three | 3, 3, 3 | 1 |

Asked three times about rounds one and two, the reader named no pair in all
three repeats. It independently reproduced the `infra` clause finding, and it
disagreed with the assistant on two boundary pairs, both of which are genuine
judgement calls recorded in the research note.

So the overlap depends on the resolution the reader chooses, and the tool does
not supply the resolution. The honest statement is the range, not a point.

### Side finding 1 — the judge's verdict carries no signal

Across the three rounds the judge called **17 of 18 candidates resolvable**. The
one exception is round one's `overreach-5`. Ticket 08 then found that 3 of round
one's 5 resolvable candidates were false against the code, and that the single
unresolvable one was also false. The verdict is near-constant, so it is not a
filter, and nobody may use it as one.

This is the same shape ticket 02 measured in Laya, where `act_probability` read
1.000000 on all 16 calls. Two unrelated tools, one defect: a head that says the
same thing every time still reads as a signal.

### Side finding 2 — round three points at a real place with a false sentence

Round three's `loophole-1` says an ungoverned Namespace renders `baseline` for a
claiming pod, so opting out of governance beats opting in. **As written against
the supplied document it is false**: the same document records the 2026-09-04
flip at line 173, and the judge caught it. **The place is real**: ticket 08
measured the served v4.0.0 body as `nsGoverned ? 'isolated' : 'baseline'`, which
all three adopters serve. That fact is already eco-system ticket 113, so nothing
new graduates. Map call 12 again, from the other direction.

### Side finding 3 — the harness writes `"ticket": "07"`

Both new `summary.json` files carry `"ticket": "07"`. That string is a constant
in `loophole_round.py`. The harness was not edited, because this ticket demands
the same harness, and its sha256 `ceb6ca92ff98fd4f` is the proof. Read the field
as "written by the ticket 07 harness".

### Licence

`bench/check_no_prompt_leak.py` is new and reusable. It takes every run of 8 or
more consecutive words from `loophole/prompts.py`, normalises case and
whitespace, and searches the committed files. It finds 1,287 distinct runs,
fires on all 1,287 against the source itself as a negative control, and finds
**0** in all six committed files across the three rounds. Output:
`research/11-prompt-leak-check.txt`. The unredacted logs stay in the scratchpad.

### What this hands ticket 09

1. One round is one draw and reads about a quarter of the tool. An ADR that
   describes adoption must say how many rounds, and three is not enough to fix
   the number.
2. What recurs is the place, never the mechanism. The ADR must say that a human
   reads the pointer and throws the sentence away.
3. The judge's verdict is not a filter and must not be presented as one.
4. A round costs 8 calls and about 0.41 USD at list price, stable to 3%.

### Left undone

The 12 candidates from rounds two and three carry no deterministic check against
the code. This ticket asks whether the tool repeats itself, not whether the new
candidates are real. Four restate a reason round one already gave; eight are
new. Whether any of the eight earns a ticket-08 style check is recorded as fog
on the map.
