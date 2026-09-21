# Ticket 11 — rounds two and three against ADR-0022

Measured 2026-09-21. Three rounds now exist against one document at one pin.

## What ran

Ticket 11 asked for a second round. This note records a second **and a third**.
Two rounds give one overlap number with no way to tell a stable overlap from a
lucky one. Three rounds give three pairwise numbers, so the overlap can be read
with its own spread. The extra round cost 8 more calls, which the subscription
absorbs. The choice is the assistant's under ADR-0025.

Everything about the run is held fixed. The harness is byte-identical, the
inputs are the same files, and the clone is at the same commit.

| | round one (ticket 07) | round two | round three |
|---|---|---|---|
| harness sha256 | `ceb6ca92ff98fd4f` | same | same |
| `adr-0022.md` sha256 | `728129b37152e434` | same | same |
| `principles.md` sha256 | `8d7d9c5798ee1162` | same | same |
| loophole commit | `129f7c0e` | same | same |
| model served | `claude-sonnet-5` | same | same |
| model calls | 8 | 8 | 8 |
| model time | 185.8 s | 173.5 s | 179.7 s |
| list price | 0.4150 USD | 0.4069 USD | 0.4197 USD |
| output tokens | 14,368 | 13,398 | 14,564 |
| candidates | 3 + 3 | 3 + 3 | 3 + 3 |
| finder parse failures | 0 | 0 | 0 |
| finder under-production | 0 | 0 | 0 |
| judge parse failures | 0 | 0 | 0 |

The three rounds cost 1.2416 USD at list price in total. The price of a round is
stable to within 3%. A reader can therefore budget a round, which matters for
ticket 09.

Run wall time was 173 s and 180 s, against ticket 07's 185.8 s of model time.

**The harness writes `"ticket": "07"` into both new summary files.** That string
is a constant in `loophole_round.py`. The harness was not edited, because ticket
11 demands the same harness, and the digest above is the proof. Read the field as
"written by the ticket 07 harness", not as the round's own number.

## The match test

Ticket 11 states the test: two candidates match when they attack the same clause
for the same reason, never when the words match.

**No two of the 18 candidates share a single run of 8 consecutive words.** That
holds across all 153 pairs. The words never match, so a word test would report an overlap of
zero and stop there.

To make the test reviewable, `11-targets.json` records two fields for each of
the 18 candidates: the clause it attacks and the reason it gives. Every number
below is computed from those two fields. A reader who disagrees can change one
row rather than argue with a verdict.

### Overlap by reason, which is the ticket's own test

| pair | shared reasons | of 6 |
|---|---|---|
| one vs two | no break-glass path; innocent omission punished | 2 |
| one vs three | innocent omission punished | 1 |
| two vs three | ratchet reset by recreate; no fast lawful loosening; innocent omission punished | 3 |

**All three rounds share exactly one reason of six: an innocent omission draws
the same bottom rung as deliberate evasion.** The mean pairwise overlap is 2 of
6, which is 33%.

### Overlap by clause, which is a looser test

| pair | shared clauses | of 6 |
|---|---|---|
| one vs two | principle 12 / `infra` declaration; principle 7 / silence | 2 |
| one vs three | principle 12 / `infra` declaration; principle 7 / silence | 2 |
| two vs three | those two, plus principle 8 / the tighten-only ratchet | 3 |

**Two clauses are attacked in every round.** They are the `infra` declaration and
the fail-closed default for silence. The mean pairwise overlap is 2.33 of 6,
which is 39%.

### The `infra` clause is the clearest single result

Four of the 18 candidates attack the `infra` declaration. Every round produces at
least one. No two give the same reason:

| round | candidate | the reason it gives |
|---|---|---|
| one | `loophole-2` | nothing restricts who may run pods inside an `infra` Namespace |
| one | `overreach-6` | a non-platform declaration renders `isolated` with no legible error |
| two | `loophole-1` | nothing says who grants the `platform` role |
| three | `loophole-2` | nothing restricts which Namespaces a platform party may declare `infra` |

The place repeats every round. The mechanism never repeats. That is map call 12
measured rather than asserted.

## What one round is worth

Three rounds of six produced 13 distinct reasons and 12 distinct clauses. Nine
reasons appeared exactly once, three appeared twice, and one appeared three
times.

Chao1 on those frequencies estimates the tool's reason population at **26.5**.
By that estimate one round of six candidates captures about **23%** of what the
tool has to say about this document.

State the caveats with the number:

1. Chao1 on three samples of six is a lower bound with a wide interval. The
   number is an order of magnitude, not a measurement.
2. The population is the tool's output, not the document's real defect set.
   Ticket 08 measured that 4 of 6 candidates were false against the code.
3. The estimate assumes each round is an independent draw from a fixed
   population. Three rounds cannot test that assumption.

Ticket 08 measured a survival rate of 2 of 6. If that rate held across the
population, which is unmeasured, an estimated 9 real defects sit behind the
tool, and one round finds about 2 of them.

## The overlap number is itself a draw

The match test is a judgement. To measure how soft that judgement is,
`match_rounds.py` asks an independent reader the same question three times. The
candidates are anonymised and shuffled from a fixed seed, so neither the label
nor the list position can carry the answer. The reader is the same
non-deterministic instrument the round used.

| pair | matches per repeat | unanimous across 3 repeats |
|---|---|---|
| one vs two | 2, 2, 1 | **0** |
| one vs three | 2, 4, 3 | 2 |
| two vs three | 3, 3, 3 | 1 |

**Asked three times about rounds one and two, the reader named no pair in all
three repeats.** Two pairs appeared twice and one appeared once. Its mean
unanimous overlap across the three round pairs is 1 of 6, which is 17%, against
the assistant's 2 of 6.

The reader independently reproduced the `infra` finding. It reported
`loophole-2 ~ loophole-1` and `overreach-6 ~ loophole-1` as same-clause,
different-reason pairs, which is the table above reached by another route.

It disagreed with the assistant in two places, and both are real boundary calls:

- It matched round one's `loophole-3` to rounds two and three's `loophole-3` in 5
  of 6 repeats. The assistant did not. Round one says an ambiguous declaration
  freezes a stale tier; rounds two and three say delete-and-recreate resets the
  ratchet. Both defeat the binding comparison. The reader grouped them, the
  assistant split them.
- It called round two's `loophole-2` and round three's `loophole-1` the same
  clause 3 times of 3. The assistant filed them under different clauses. Both
  attack ungoverned Namespaces.

The overlap number therefore depends on the resolution the reader chooses, and
the tool does not supply the resolution. The honest statement is a range: **the
overlap between two rounds is 1 to 3 of 6.**

The matcher cost 0.4689 USD at list price for 9 calls.

## The judge's verdict carries no signal

Across the three rounds the judge called **17 of 18 candidates resolvable**. The
single exception is round one's `overreach-5`.

Set that against ticket 08. Of round one's five resolvable candidates, two
survived a deterministic check and three were false against the code. Of the one
unresolvable candidate, zero survived. At n = 6 that separates nothing.

The verdict is near-constant, so it is not a filter. Anyone who treats
`resolvable` as a quality signal is reading a head that says the same thing every
time. This is the same defect shape ticket 02 measured in Laya, where
`act_probability` read 1.000000 on all 16 calls.

## Round three states a fact the estate already holds, and states it wrongly

Round three's `loophole-1` attacks the ADR line added 2026-08-28: an ungoverned
Namespace still renders `baseline` for a pod that claims a policy version. It
argues that opting out of governance beats opting in, because governed with no
tier renders `isolated`.

**As written against the current document the candidate is false.** The same
document records the 2026-09-04 flip at line 173, and the 2026-08-28 bullet
itself says it flips. The judge caught this and called the text superseded.

**The place it points at is real.** Ticket 08 measured that the served v4.0.0
body reads `nsGoverned ? 'isolated' : 'baseline'`, so an ungoverned Namespace with
a claiming pod does land on `baseline` under the body all three adopters serve.
That fact is already held as eco-system ticket 113. Nothing new graduates.

This is map call 12 a second time. The sentence is wrong and the pointer is
right, and only a deterministic check can tell the two apart.

## Twelve candidates are recorded and unchecked

Ticket 11 asks whether the tool repeats itself. It does not ask whether the new
candidates are real, and this note does not answer that. The 12 candidates from
rounds two and three sit in `candidates.json` with no deterministic check against
the code. Four of them restate a reason round one already gave. Eight are new.

Whether any of the eight earns a ticket-08 style check is a scoping call for
ticket 09, and it is recorded as fog on the map.

## Licence

The committed artefacts hold the model responses and a sha256 plus a length for
each prompt. `check_no_prompt_leak.py` takes every run of 8 or more consecutive
words from `loophole/prompts.py`, normalises whitespace and case, and searches
the committed files for each one. It finds 1,287 distinct runs, fires on all
1,287 against the source itself as a negative control, and finds **0** in all six
committed files across the three rounds. The output is `11-prompt-leak-check.txt`.

The unredacted logs stay in the session scratchpad, outside the project tree.

## Files

- `11-loophole-round-two/` and `11-loophole-round-three/` — `summary.json`,
  `candidates.json`, `calls.jsonl` for each round.
- `11-targets.json` — the clause and reason for all 18 candidates, and the
  overlap arithmetic computed from them.
- `11-blind-match/` — the blind reader's three repeats per round pair, with the
  anonymous-label maps that let any repeat be replayed.
- `11-prompt-leak-check.txt` — the licence check output.
- `../bench/match_rounds.py` and `../bench/check_no_prompt_leak.py` — the two new
  instruments. Neither holds loophole source or loophole prompt text.
