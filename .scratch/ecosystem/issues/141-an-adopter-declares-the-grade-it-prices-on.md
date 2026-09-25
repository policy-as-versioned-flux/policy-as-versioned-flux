# 141 — An adopter declares the grade it prices on

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-25 from grilling ticket 30, decision 6 (delegated), and ADR-0032.

The estate default pricing threshold is grade 2 (`twin/evidence-ladder.yaml` `pricing_threshold`
and `path_admission_threshold`). An adopter may declare, on its own signed `party.yaml`, that it
prices on grade 3: "published work, not observed here". Build that declaration end to end:

1. **The platform party schema** gains the declaration. The schema is closed
   (`party/schema.json`, `party/party_artefact.py`), so this is a platform release. The only
   admitted values are 2 and 3. A value looser than 3 is refused by the schema: grade 4 is an
   expert's say-so and grade 5 a model's, and neither may price.
2. **The twin reads the declaration** where it applies the two thresholds, and the valuation
   schema admits an amount at grade 3 only for a perspective whose party declares 3.
3. **Every price shows the weakest grade it rests on**, the one operation ADR-0024 point 6 admits
   on grades (an order statistic). The forward-intel payload, the `prices[]` line and the handbook
   carry it.
4. **A synthetic record never raises a grade** (twin ticket 12). The check refuses an edge or a
   valuation whose grade rests on a record marked synthetic, planted or injected.

The hub default stays 2 for every overlay that does not declare, including the real-firm backtest
corpus.

5. **`data_subjects` becomes optional in the size block** (decided 2026-09-25, delegated; see
   ticket 144's Comments). Neither comparable filing discloses it, and nothing in the estate reads
   it today. A converter that needs it refuses by name when it is absent (ADR-0020).

## Notes

Ticket 144 needs this before tuppence, ludlow and driftwood can price on their comparable-firm
anchors. The release cut and the adopter tags wait for the owner's authorisation.
