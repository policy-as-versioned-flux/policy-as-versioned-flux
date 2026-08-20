# 06 — Implement the scenario slate into the feeds and standing library

Type: task
Status: done
Blocked by: 05, 14

## Question

Land the researched slate as real, signed, versioned feed entries and scenario-library members, so
the war-gamer actually consumes them rather than the demo merely narrating them.

Includes: the quantum-CRQC entry (research already done — port it from
`.scratch/talk-spec/pitch-v4/research/quantum-niobium-analysis.md`), each new component's
`base_risk` FAIR triples, re-signing the feeds, and extending
`estate/platform/wardley/wardley.py`'s selfcheck to cover the new members.

**Guard against the obvious failure:** the slate must not be tuned so every scenario fires. At least
one entry should be a component that legitimately does **not** cross its stage boundary, and the
suite should assert that — the estate's credibility rests on the forward layer being able to say
"this loud thing changes nothing above it".

**Correct the K documentation while here.** The source comment inviting a reader to "widen K if a
real trajectory should flip a move sooner" is unsafe: `cage.select_tier()` picks the loosest fitting
tier and the tier cost curves cross at ALE £3,750, so cage TCoR is non-monotone in K — at K=6 the
flagship `phishing-kits-aas` stops drifting entirely. K=4.0 itself is validated (stable plateau
3.0–5.0) and needs no change.

Re-run `verify-wardley.sh`, `verify-wargamer.sh`, `verify-feeds.sh` and record the real new counts.

## Comments

Done 2026-08-20. Landed the whole researched slate, not just the named niobium entry.

1. **`market-intel.json` v1 -> v2** (re-rendered + re-signed via `sign-map.sh`), 4 new components,
   5 -> 9 total, 3/5 -> 7/9 flagged commoditising:
   - `agentic-commit-access` (attacker-capability) -- fires (x2.08+), re-priced, but the war-gamer
     proposes nothing: `agentic-commit-compromise` is deployed at `fix` already, and `fix` is a
     provable fixed point of the forward bump (proved in `selfcheck()` by sweeping the bump factor
     1..20x, not just today's K=4.0).
   - `pkg-registry-worm` (attacker-capability) -- fires and flips `dependency-worm-exfil` `cage -> fix`
     at driftwood, so the slate isn't tuned to be silent either.
   - `nb-refining-capacity` (supply-constraint) -- the ticket's required non-firing entry, ported from
     the niobium research's component table (qubit/SRF-grade Nb, vis 0.05/evo 0.62). The **loudest**
     new flag on the map (crosses product->commodity) and carries the **same real `base_risk`** as
     `pq-cryptanalysis` so the non-fire is not vacuous, proven non-vacuous by asserting `base_risk is
     not None` directly. Emits nothing: the actor gate, not a missing base_risk, is what stops it.
   - `pqc-transport-migration` (defensive-capability) -- known-inert twin of `spiffe-workload-identity`
     (finding F2: a commoditising *defence* has no path to lower a cost in this engine); carried with
     a `note` saying so rather than buried.
2. **`wargamer/scenarios/human-device.json`**: added `hyperscaler-region-concentration` (5 -> 6 risks),
   the only estate risk besides `driftwood-portfolio.json` that exercises `tcor.py`'s `applicable`
   field -- without it the engine "recommends" fixing a hyperscaler outage for £3,726.
3. **`wardley.py`'s `selfcheck()`** extended to cover all 4 new members (loud-and-silent x2,
   fires-and-absorbed, fires-and-flips) plus the free fix-fixed-point theorem `S1` names but nothing
   asserted before now.
4. **The unsafe "widen K" doc comment is fixed** in `wardley.py` and `wardley/README.md`: K=4.0 is
   measured to sit in a stable plateau (3.0-5.0) and is **unchanged**; widening it is not safe advice
   because `cage.py`'s loosest-fitting tier selection makes cage TCoR non-monotone in the threat
   (`phishing-kits-aas` stops drifting between K=5 and K=6).

Real new counts (all three verify scripts pass):
- `verify-wardley.sh`: 9 components, 7 commoditising, 4 attacker-capabilities re-priced (was 2),
  9 forward drifts -> 9 signed PRs across the 4 appetite-file institutions, 0 merged.
- `verify-wargamer.sh`: 6-scenario library, 3 scenario-path drifts + 1 enforcement drift -> 4 signed
  PRs, 0 merged; `hyperscaler-region-concentration` correctly does **not** drift (`transfer ->
  transfer`), proving `applicable` is doing real work, not decoration.
- `verify-feeds.sh`: unaffected (20 feed entries valid), included per the ticket's instruction.

Left out of scope, deliberately: the research's own S8 "must do" list also asks for a `note` on the
**existing** `pq-cryptanalysis` entry resolving finding F4 (its declared `transfer` is never cheapest
at any band). Ticket 06's own text does not name this, only the niobium port + the 4-component slate +
the K fix, so it is left for a follow-up rather than smuggled in here. Also noted but unchanged: the
war-gamer already runs against 4 "institutions" (`driftwood`/`tuppence`/`ludlow`/`platform`) because
`wardley.institutions()` reads every key of `appetite.json`'s `orgs`, including `platform`'s
root-of-trust band -- pre-existing (ticket 14), not introduced or touched here.

Evidence: `bash estate/platform/wardley/verify-wardley.sh`, `bash
estate/platform/wargamer/verify-wargamer.sh`, `bash estate/platform/feeds/verify-feeds.sh` all pass.
