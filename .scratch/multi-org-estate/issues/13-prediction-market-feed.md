# 13 — Should the estate gain a prediction-market signal feed?

Type: grilling
Status: claimed (this session)
Blocked by: 05

## Question

The estate's £ engine has never seen a market price. Its five signed feeds are threat-register, CVE,
EOL, ICO penalties, and market-intel (the AI-Wardley forward layer). Should there be a sixth, sourced
from prediction-market price moves?

**The mechanism already exists — in the other codebase.** `twin/market_signals.py` (+ `twin/benchmark.py`,
`twin/benchmark-selection-rule.yaml`) was built for `twin` decision ticket 21 / build tickets 57–59,
with research at `.scratch/twin/research/prediction-markets.md`. Three properties carry over and must
not be lost if it is reused here:

- **Venue-agnostic, no adapter.** It reads a caller-supplied fixture price series; `market_signals.py:18`
  — "Swapping in a real Polymarket/Kalshi adapter changes nothing here." There is no live integration
  anywhere, by design.
- **`price_levels_never_probabilities`.** Consume price *moves* as world-layer signals, never price
  *levels* as probabilities — favourite–longshot bias is worst in the deep tail this engine cares about.
  `as_probability()` exists only to refuse, every time, rather than warn.
- **A narrow claim scope that travels with every result** — non-overconfidence in general
  world-forecasting only; explicitly *not* £ pricing or the org overlay.

**Decide:**

1. **Does it belong at all?** A market price move is a *signal source*, not a scenario — unlike
   everything ticket 05 is researching. Does it earn a feed, or is it a benchmark-only device that has
   no business touching a priced control decision? Note the twin's own claim scope says it evidences
   nothing about £ pricing — so wiring it into the £ path may contradict a boundary already drawn.
2. **Live adapter or authored fixtures?** Internet is now assumed (Q5), so a live Polymarket/Kalshi
   adapter is newly possible. Weigh demo fragility, rate limits and the signing/provenance story — every
   other feed here is signed and tamper-checked, and a live third-party API is not.
3. **Cross-project reuse.** Copy, extract a shared library, or reimplement? The twin and the estate are
   separate codebases about to become separate GitHub orgs. Whichever way, the invariant must come with
   it — a copy that drops `price_levels_never_probabilities` is worse than not doing this at all.

Blocked by the scenario slate research, whose "what does the current feed miss" and "feed vs library"
answers bear directly on whether this is a feed, a benchmark, or neither.
