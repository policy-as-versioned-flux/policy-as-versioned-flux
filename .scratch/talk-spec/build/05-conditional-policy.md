# 05 — Conditional policy (exemptions dissolved)

**What to build:** "You may X *if* conditions C" as uniform versioned Kyverno CEL — not carve-outs. A git ledger entry renders a `PolicyException` (Flux prune + `cleanup.kyverno.io/ttl`) and is the generator of its OSCAL risk object.

**Blocked by:** 03

**Status:** done (2026-08-20) — `verify-conditional.sh` + `verify-exemption.sh` both PASS offline

- [x] A conditional branch admits for anyone meeting C, uniformly, in CEL; residual feeds the £ — `bash estate/platform/policy/verify-conditional.sh` → `root-attested-hardened ADMITS (met C); root-bare + attested-unhardened FAIL`; residual priced via `fair.py`: `£21360/yr`
- [x] A ledger entry renders a `PolicyException`; removing it prunes (+ ttl backstop) — `bash estate/platform/policy/verify-exemption.sh` → entry renders a `PolicyException` (TTL backstop `2026-10-01`, `cleanup.kyverno.io/ttl` in `render-exemption.py:73`); removing the row → re-render is empty → pod denied again
- [x] No ledger entry ⇒ no exception (verified) — same run, step 1: `NO ledger entry -> no exception -> the pod is DENIED`

## Comments

- 2026-08-20 (audit mo-02): behaviour is correct and both verify scripts pass offline. Flagging, not fixing: `CONTEXT.md`'s Exemption entry itself notes "the estate currently ships an exemptions ledger that contradicts [the ban]; its removal is tracked in `.scratch/govern-what-you-dont-control/`" — `estate/platform/policy/ledger/exemptions.yaml` and `verify-exemption.sh`/`render-exemption.py` still carry the banned "exemption" name even though the mechanism is a conditional `PolicyException`, not a carve-out. Out of scope for this audit ticket; already tracked separately. Status corrected from `ready-for-agent` to `done`.
