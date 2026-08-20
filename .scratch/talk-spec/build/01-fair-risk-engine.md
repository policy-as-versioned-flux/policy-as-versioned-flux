# 01 — FAIR risk engine (`fair.py` CLI)

**What to build:** A pure, deterministic CLI that turns versioned `(min,mode,max)` risk triples into `{ALE, VaR₉₅, TVaR}` with a risk load. This is the load-bearing seam for the whole risk thesis — the "£ moves when you tighten a control" beat is two invocations differing by one input. No cluster needed.

**Blocked by:** None — can start immediately.

**Status:** done (2026-08-20) — `python3 estate/platform/fair/fair.py selfcheck` exits 0

- [x] Reads versioned triples → beta-PERT → seeded Monte Carlo → aggregate annual-loss distribution — `pert()`/`simulate()` in `estate/platform/fair/fair.py:42-64`; scenario shape confirmed by `scenarios/driftwood-cart-pii.json`
- [x] Emits ALE (mean), VaR₉₅ (95th pct), TVaR (mean beyond VaR₉₅), and £ carried = TVaR + risk load — `summarize()` (`fair.py:80-103`); `selfcheck` output: `ALE=19559 VaR95=30948 TVaR=34087 carried=34958`
- [x] Deterministic under a fixed seed; self-check asserts TVaR ≥ VaR₉₅ ≥ ALE and a Deny buys positive risk vs Warn (`ALE_warn − ALE_deny`) — `cmd_selfcheck` asserts (`fair.py:159-178`) all pass; `selfcheck` output: `Deny buys 19439 (99% effective)`
- [x] Runs fully offline — stdlib only (`argparse`,`json`,`random`); no network/cluster call in `fair.py`

## Comments

- 2026-08-20 (audit mo-02): re-ran `fair.py selfcheck` clean, exit 0. All 4 ACs directly proven by the script's own asserts. No cluster or verify-*.sh needed for this ticket — `fair.py` is the load-bearing unit itself. Status corrected from `ready-for-agent` to `done`.
