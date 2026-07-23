# Wardley mapping as the strategic (anticipation) layer

Type: grilling
Status: resolved
Blocked by: 04

## Question

The feeds are *reactive* (a CVE landed, an EOL passed). Wardley mapping is *anticipatory* — it maps
the value chain **and** the evolution axis (genesis → custom → product → commodity), so
commoditisation is visible before it bites. Pin:

- **What it tracks:** the chains (what depends on what — this *is* the dependency graph: regulator →
  institution → team → workload → underlying tech, with an evolution overlay) and the climatic
  patterns ("everything evolves to commodity") driving shocks like *attack tooling commoditising*
  (mythos) and *RSA/ECC drifting toward broken-by-commodity-quantum*.
- **AI-enabled + market-intel-driven:** the map isn't only human-curated — it's fed by **market
  intelligence** (adoption curves, vendor signals, tech movements) and AI-assisted positioning; it
  is itself another feed into the war-gamer (13).
- **How it feeds risk:** an evolution movement (a component nearing "commodity") is a *forward*
  signal that ramps a future TEF / control obsolescence — feeding the FAIR model (04) ahead of the
  reactive feeds.
- **Honest boundary:** ADR-0007 already flagged Wardley climatic movement as "not fully automatable"
  — decide what's AI-inferred vs human-curated, and don't fake certainty about the future.

Output: the Wardley layer's data model + how it feeds the war-gamer and the risk timeline.

## Answer

Settled at the decision level. **AI-enabled Wardley mapping is the anticipation layer**, driven by
**market intelligence**: it tracks **commoditisation** (e.g. mythos-style scanning, attack-cost
collapse, post-quantum) and value-chain movement *ahead* of the reactive feeds, and hands the
war-gamer (13) a forward view so proportionality re-tunes before the threat lands, not after. Its
map updates are commits with attestable provenance like everything else. The mapping generator +
market-intel ingestion are build-work, not a remaining decision.
