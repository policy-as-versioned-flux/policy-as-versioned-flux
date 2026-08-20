# 18 — One breach, several bills: the £ engine prices one regime at a time

Type: task
Status: done
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

## Comments

Done 2026-08-20.

1. **Additive, not worst-single-dominates.** Two obligation sources firing on the same breach both
   land — an ICO fine does not excuse a PCI penalty. Ticket 17's own words ("you may need to consider
   the worst case scenario") mean the worst case is the *fully-stacked* outcome, not the single largest
   regime cherry-picked; FAIR treats distinct secondary-loss channels (regulatory, contractual, legal)
   as additive within one loss event, and real breaches confirm it — Equifax's 2017 incident drew an
   FTC/CFPB settlement, several state-AG fines, and a class-action settlement concurrently, not the
   largest of the three alone.

2. **Correlated, not independently sampled — a structural change to `simulate()`, not a bigger
   triple.** `fair.py`'s `lm` may now be a list of `(min,mode,max)` triples, one per obligation source,
   alongside the existing single-triple shape (unchanged). All sources share the risk's one `lef`: one
   frequency draw decides how many breach *events* happen in a simulated year, and each event sums a
   magnitude drawn independently per source. Summing two *separately*-simulated regimes (each rolling
   its own frequency) would let a bad year for one land in a quiet year for the other, diversifying the
   tail away — measured directly: `fair.py selfcheck` asserts the correlated combination's TVaR sits
   above that naive independent sum's, on the same marginal distributions.

3. **Which regimes apply to which workload stays open** — the parent ticket's gap, not resolved here.
   `to_fair_scenario.py build ... --also REGIME:VIOLATION_TYPE` (repeatable) lets a caller name
   whichever sources apply to a given risk; nothing here decides that binding for
   driftwood/tuppence/ludlow.

4. **The tail gets fatter, not thinner, proven with real numbers.** Combining `uk-gdpr/lower-tier` +
   `pci-dss/non-compliance-escalating` on the ico v2 schema moves warn ALE from £9,039,791 (uk-gdpr
   alone) to £11,006,429 (combined) — `estate/ico/verify-penalty-feed.sh` step 5. No existing demo
   scenario (`driftwood-cart-pii.json`, `encrypt-at-rest.json`) was retrofitted to carry multiple
   sources — doing so means deciding which regimes bind to which institution, the open gap in point 3
   — so no £ figure already quoted in `deck.md`/`RUNBOOK.md`/the platform READMEs needs to move: they
   are computed from unmodified single-triple scenarios, and the single-triple code path is unchanged
   (same PERT/rng call sequence). Confirmed, not assumed: `fair.py selfcheck` still reproduces the
   exact £19,559 / £30,948 / £34,087 / £34,958 already in `deck.md`, and
   `verify-proportionality.sh`'s risk_bought is still exactly £21,107.

Evidence: `python3 estate/platform/fair/fair.py selfcheck`, `python3
estate/ico/schema/to_fair_scenario.py selfcheck`, `python3 estate/platform/feeds/to_fair_scenario.py
selfcheck`, and `bash estate/ico/verify-penalty-feed.sh` all PASS. Every other offline `verify-*.sh`
that consumes `fair.py` re-run individually and unaffected: `verify-conditional.sh`,
`verify-proportionality.sh` (steps 0-3, the only ones touching `fair.py`/`enforce.py`; step 4 —
`kyverno test`, unrelated to this change — did not complete in this sandbox and is not evidence of a
regression), `verify-risk-tuned.sh`, `verify-graded.sh`, `verify-tcor.sh`, `verify-feeds.sh`,
`verify-upflow.sh`, `verify-break-glass.sh`, `verify-wargamer.sh` all PASS unchanged.
`verify-honesty.sh` fails on `reflexive.py`'s `signing_key_present` assertion — pre-existing per
ticket 16's own resolution ("the private feeds-signing key was never committed... confirmed
pre-existing"), not touched by this ticket. No live cluster in this environment; `--live` beats out of
scope per this batch's instructions.
