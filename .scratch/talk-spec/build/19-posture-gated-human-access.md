# 19 — Posture-gated human access (break-glass)

**What to build:** A risky operation (break-glass / `ludlow` patient data) demands current device posture + higher identity assurance; a stale/unattested device is caged (read-only/scoped/step-up) or denied — proportionally to the op's £.

**Blocked by:** 06, 18

**Status:** done (2026-08-20) — `estate/platform/break-glass/verify-break-glass.sh` PASSes offline

- [x] A risky op requires an attested device + step-up WebAuthn, proportionate to its £ — `bash estate/platform/break-glass/verify-break-glass.sh`: `read £1,868 T1 | write £53,469 T2 | export £534,694 T3-cage | patient £2,409,490 T3-deny`; `AC1: risky op ALLOWED with fresh attested device + step-up passkey`; `AC1: same op, no passkey -> STEP_UP (proportionate)`; tiers reuse `../fair/fair.py` for the £ and `access.py`'s decision vocabulary (no second risk engine)
- [x] A stale/unattested device is denied or dropped to a read-only/scoped session — same run: `AC2: stale device on a tier-3 op -> dropped to read-only/scoped (CAGE)`; `AC2: stale device on patient data -> DENY (proportional to the higher £)`; `AC2: unattested/unmanaged laptop -> DENY`
- [x] Verified access check — `break-glass selfcheck: all asserts passed`; final line `-- all offline invariants hold --`

## Comments

- 2026-08-20 (audit mo-02): `verify-break-glass.sh` PASSes offline, all 3 ACs directly evidenced by a real (non-mocked) decision-engine run covering both AC1 (allow/step-up) and AC2 (cage/deny) cases explicitly. Status corrected from `ready-for-agent` to `done`.
