# 06 — Implement the scenario slate into the feeds and standing library

Type: task
Status: open
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
