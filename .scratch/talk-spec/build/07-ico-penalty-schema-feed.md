# 07 — `ico` penalty schema feed

**What to build:** `ico` publishes a small bespoke, signed, versioned penalty schema (regime → violation-type → fine formula/cap), sourced from real public fine magnitudes, feeding the FAIR loss-magnitude directly (not force-fit into OSCAL).

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [ ] `ico` schema signed + versioned; grounded in real public fines
- [ ] `fair.py` consumes it as a loss-magnitude input
- [ ] A schema bump changes the £ via a reviewable PR
