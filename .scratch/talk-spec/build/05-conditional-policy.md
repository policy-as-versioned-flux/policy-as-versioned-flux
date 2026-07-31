# 05 — Conditional policy (exemptions dissolved)

**What to build:** "You may X *if* conditions C" as uniform versioned Kyverno CEL — not carve-outs. A git ledger entry renders a `PolicyException` (Flux prune + `cleanup.kyverno.io/ttl`) and is the generator of its OSCAL risk object.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] A conditional branch admits for anyone meeting C, uniformly, in CEL; residual feeds the £
- [ ] A ledger entry renders a `PolicyException`; removing it prunes (+ ttl backstop)
- [ ] No ledger entry ⇒ no exception (verified)
