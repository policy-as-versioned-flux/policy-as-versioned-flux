# 18 — One breach, several bills: the £ engine prices one regime at a time

Type: task
Status: open
Blocked by: 17

## Question

Surfaced resolving *An institution answers to many masters*. A single incident can trigger
consequences under several obligation regimes at once — an ICO fine **and** a PCI penalty **and**
customer SLA credits **and** litigation — and the estate prices one at a time.

**The gap, precisely:** `fair.py` carries **one loss-magnitude triple per risk**
(`lm: [min, mode, max]`); `simulate()` samples a frequency then sums a magnitude *per event*, all
within a single regime. `estate/ico/schema/to_fair_scenario.py` converts *regime → violation-type →
fine formula/cap* into exactly one `lm` triple. There is no notion of the same breach drawing from
several regimes.

**The job:** let a risk carry consequences from multiple obligation sources and price the **worst
case** across them, per the owner's instruction.

Questions the implementation must answer, and they are not trivial:

1. **Do consequences add, or does the worst dominate?** Two regulators fining the same breach is
   plausibly additive; a fine and a litigation award for the same loss may not be. Additive-by-default
   is the conservative reading and probably right, but say which and why.
2. **Are they correlated?** They are triggered by *the same* event, so they cannot be sampled
   independently — one breach draws every applicable consequence in the same simulated year. This is
   a structural change to `simulate()`, not a bigger triple.
3. **Which regimes apply to which workload?** Depends on the per-workload obligation scoping the
   parent ticket also identified as missing; the two are entangled.
4. **Does the tail change shape?** TVaR and the risk-load exist to price the bad year. Several
   correlated consequences on one event make the tail fatter, which is exactly the region the board
   line is most sensitive to.

Note this makes the £ **larger**, not smaller — worst-case aggregation raises every number the demo
quotes. That is the honest direction, and any recomputed figures in narration and README must move
with it.
