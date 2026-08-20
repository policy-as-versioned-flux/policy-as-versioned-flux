# 05 — Research the full war-gaming scenario slate

Type: research
Status: resolved
Blocked by: none

## Question

The owner's instruction is "all — go big war gaming". What is the defensible slate of forward
scenarios the estate should carry, and what are each one's real coordinates and numbers?

One worked example already exists to the required standard:
`.scratch/talk-spec/pitch-v4/research/quantum-niobium-analysis.md` — a quantum-CRQC entry with a
Wardley value chain, per-link causal strength ratings, sourced facts, and an explicit
fact/inference/judgement boundary. Its headline finding is a *negative* one (niobium supply does not
move the risk; a published algorithmic result does), which is exactly the standard to hold: a
scenario that concludes "this changes nothing" is as valuable as one that fires.

**Produce, for each proposed scenario:** the component and its `evolution`/`velocity`/`visibility`,
the linked risk with FAIR triples, the causal chain with honest per-link strength, sources, and the
fact/inference/judgement split. Anything that cannot meet that bar does not go in.

**Candidate directions** (not a closed list — propose better ones):
quantum-CRQC (already researched, port it in); strategic-mineral / supply-concentration; an
AI-agent-with-commit-access insider path; an EOL-cliff cascade; a regulator fine-regime shift;
post-quantum migration cost as its own control; cloud-provider concentration.

Also answer: do these belong in `market-intel.json` (the forward Wardley feed), the standing scenario
library (`estate/platform/wargamer/scenarios/`), or both — and what distinguishes the two.

Deliver as a research document; implementation is ticket 06.

## Answer

Full research: [`research/scenario-slate.md`](../research/scenario-slate.md) (1,188 lines). Every
number in it is engine output, not assertion; `wardley.selfcheck()` passes unchanged against the
proposed v2 intel, and both firing entries hold their conclusion across four alternative coordinate
choices each.

**The slate — 4 components, 2 fire, 2 inert.**

| id | actor | evo/vel | fires | drift |
|---|---|---|---|---|
| `agentic-commit-access` | attacker | 0.40 / 0.09 | yes ×2.08 | **no** |
| `pkg-registry-worm` | attacker | 0.45 / 0.09 | yes ×2.08 | yes → `cage→fix` |
| `nb-refining-capacity` | supply-constraint | 0.62 / 0.05 | **no** | — |
| `pqc-transport-migration` | defensive | 0.62 / 0.10 | **no** | — |

**The deliberate non-firing entry is `nb-refining-capacity`** — it flags `commoditising: true` (the
loudest new flag on the map) and still emits nothing, and it carries a **full `base_risk`** so the
assertion cannot pass vacuously. Flipping one string (`actor`) makes it fire *and* drift, proven.
A second, richer shape also exists: `agentic-commit-compromise` fires, is re-priced ×2.08, and the
war-gamer still proposes nothing, because `fix` is a provable fixed point — fix/deny read the
untouched `deny` state, so the bump only ever raises cage/transfer. Verified over movement 0→1.0 and
K∈{1..8}.

**Feed vs library — five axes, four filesystem-verifiable.** The feed is **signed** (`.sig` +
tamper-test) and **versioned**; the library is neither. Feed = machine-derived, forward, published by
`platform`. Library = human-curated (`author` asserted), standing posture, owned by the war-gamer.
Rule: **the feed carries the trajectory, the library carries the posture.** Cloud concentration is
library-only — the evolution axis has no concentration dimension — and is the only estate risk that
exercises `applicable`; without it the engine recommends "fix a hyperscaler outage for £3,726".

**Calibration: `ATTACK_COST_COLLAPSE_K = 4.0` needs no change, and that is measured** — it sits in a
stable plateau across 3.0–5.0. But the source comment inviting a reader to "widen K if a real
trajectory should flip a move sooner" is **unsafe**: `cage.select_tier()` picks the loosest fitting
tier and the tier cost curves cross at ALE £3,750, so cage TCoR is non-monotone in K. At K=6 the
flagship `phishing-kits-aas` *stops* drifting. The comment must be corrected wherever K is documented.

**Rejected, with reasons recorded:** regulatory regime shift (a calendar, not a diffusion curve — and
the data contradicted the researcher's own first argument, which is recorded rather than quietly
dropped), EOL, physical/geopolitical, and n-day weaponisation (double-counts EPSS).

**Three findings that outrank the slate** — all independently verified before recording:

- **F1 — the forward layer is single-institution.** `wardley.py:137` hardcodes `"org": "driftwood"`.
  At ludlow's band phishing does not drift, and ransomware drifts at base. Every forward claim the
  estate makes is one institution's, in an estate whose whole point is six. Now its own ticket.
- **F2 — the layer is monotone-pessimistic.** No commoditising *defence* can lower any cost.
  Concretely: npm shipped default-off lifecycle scripts (Jul 2026) and revoked classic tokens
  (Dec 2025) — real, free risk reduction, structurally invisible to this model. Now its own ticket.
- **F4 — `pq-cryptanalysis`'s declared `transfer` is never cheapest at any band** (4.8×–25.5× off).
  Verified across £5k–£500k: the engine picks `fix` or `cage`, never `transfer`. This closes the open
  question in the map's fog — it is a misconfiguration, not editorial choice.

**Also surfaced, folded into the vacuous-gate sweep:** `credential-stuffing-aas` has
`base_risk: null`, so `selfcheck`'s assertion that it "must not signal (no movement)" would pass even
if it *did* move — `forward_signal()` skips any component without a `base_risk` first. The assertion
cannot fail for the reason it claims to test.
