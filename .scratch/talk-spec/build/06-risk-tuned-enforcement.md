# 06 — Risk-tuned enforcement (£ → Audit/Deny)

**What to build:** The FAIR £ drives Audit-vs-Deny selection against a tolerance band; tighten a versioned triple → £ rises → the policy flips Audit→Deny in a reviewable PR. No date logic in policy bodies.

**Blocked by:** 01, 03, 04

**Status:** done (2026-08-20) — `estate/platform/risk/verify-risk-tuned.sh` PASSes offline

- [x] `ALE_warn − ALE_deny` vs a tolerance band selects Audit or Deny — `bash estate/platform/risk/verify-risk-tuned.sh` → `driftwood(£40000 tol): loose buys £19439 -> Audit | tightened buys £54520 -> Deny`
- [x] Tightening a triple raises the £ and flips the verdict via a PR — same run, steps 1-2; `estate/platform/risk/PR.md` is a real drafted PR body citing the exact before/after £ numbers
- [x] Enforcement escalation is justified by a number, not a timer — `enforce.py` (`estate/platform/risk/enforce.py:114-115`) asserts `"datetime" not in s and "time" not in s` on every policy body it touches; `PR.md` cites ADR-0006

## Comments

- 2026-08-20 (audit mo-02): `verify-risk-tuned.sh` PASSes offline; all 3 ACs directly evidenced by the run plus the drafted `PR.md`. Status corrected from `ready-for-agent` to `done`.
