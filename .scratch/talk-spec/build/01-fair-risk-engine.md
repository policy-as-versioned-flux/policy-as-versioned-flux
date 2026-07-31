# 01 — FAIR risk engine (`fair.py` CLI)

**What to build:** A pure, deterministic CLI that turns versioned `(min,mode,max)` risk triples into `{ALE, VaR₉₅, TVaR}` with a risk load. This is the load-bearing seam for the whole risk thesis — the "£ moves when you tighten a control" beat is two invocations differing by one input. No cluster needed.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Reads versioned triples → beta-PERT → seeded Monte Carlo → aggregate annual-loss distribution
- [ ] Emits ALE (mean), VaR₉₅ (95th pct), TVaR (mean beyond VaR₉₅), and £ carried = TVaR + risk load
- [ ] Deterministic under a fixed seed; self-check asserts TVaR ≥ VaR₉₅ ≥ ALE and a Deny buys positive risk vs Warn (`ALE_warn − ALE_deny`)
- [ ] Runs fully offline
