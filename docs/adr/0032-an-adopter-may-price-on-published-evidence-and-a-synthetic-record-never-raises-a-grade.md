---
status: accepted
---

# An adopter may declare that it prices on published evidence; a synthetic record never raises a grade

Decided 2026-09-25 by the assistant under
[ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md), labelled **delegated**.
Eco-system ticket 30, decision 6, which reversed that ticket's round 1 item 5 on evidence
([issues/30](../../.scratch/ecosystem/issues/30-the-twin-s-cage-spec-and-price-per-adopter.md)).
Supersedes nothing.

## Context

The twin prices an impact only when its causal path and its valuation are graded 2 or better
(`twin/evidence-ladder.yaml` `pricing_threshold: 2`, `path_admission_threshold: 2`). Grade 2 is
"repeated historical co-movement ... the repetition is the evidence". Grade 3 is published work,
not observed here.

The three adopters are demonstration parties modelled on studied real firms (ticket 75 Q7). None
has a history of its own. tuppence's and ludlow's pricing edges carry honest grade-3 anchors from
their comparable firms' published regulatory records, so both twins refuse to price. driftwood's
pricing edge claims grade 2 with a one-line note and no record, and its rung responses cite
post-mortems and a drill that exist nowhere. The code never ties a grade to a record: a grade is
an integer, and `may_price` compares it with the threshold.

Round 1 of ticket 30 decided that a marked synthetic incident record may support grade 2. That
decision cited NORTH-STAR §6, whose line is under "What is explicitly out" and does not cover
pricing. Twin ticket 12, `twin/planter.py` and driftwood's drift fixtures all limit a synthetic
result to evidence about detection machinery, never about the world. A record that earns grade 2
would have to invent repeated history.

## Decision

1. **The estate default stays grade 2.**
2. **An adopter may declare, on its own signed party artefact, that it prices on grade 3.** Only 2
   and 3 are admitted: grade 4 is an expert's say-so and grade 5 a model's, and neither prices.
   The declaration is the risk-bearer's signed choice, like its appetite.
3. **Every price shows the weakest grade it rests on**, the one operation on grades ADR-0024
   point 6 admits.
4. **A synthetic record never raises a grade.** It evidences machinery, never the world.
5. **driftwood's unrecorded grade 2 drops to grade 3** and gets a comparable-firm anchor, as
   tuppence's and ludlow's have.

## Options considered

- **A marked synthetic record counts as grade 2** (ticket 30 round 1). Reversed: it breaks twin
  ticket 12's rule and needs invented repeated history.
- **Only grade 2 or better ever prices.** Honest, but it removes the one working twin price and
  leaves no route for a party with no history of its own, which is where every real adopter of a
  reference implementation starts.
- **Lower the hub threshold to 3 for everyone.** Rejected: it would move the real-firm backtest
  corpus and every other overlay without any party choosing it.

## Consequences

- Ticket 141 builds the declaration (a platform party-schema release). Ticket 144 moves the three
  adopters' evidence onto it and gives tuppence and ludlow their sizes.
- A price on grade 3 says so wherever it appears. A reader can see which prices rest on published
  comparables and which on the adopter's own observations.
- Revisit when an adopter holds a dated record of its own: it may then regrade to 2 through the
  regrade record `twin/evidence.py` already requires.
