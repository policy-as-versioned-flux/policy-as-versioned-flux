# 19 — Posture-gated human access (break-glass)

**What to build:** A risky operation (break-glass / `ludlow` patient data) demands current device posture + higher identity assurance; a stale/unattested device is caged (read-only/scoped/step-up) or denied — proportionally to the op's £.

**Blocked by:** 06, 18

**Status:** ready-for-agent

- [ ] A risky op requires an attested device + step-up WebAuthn, proportionate to its £
- [ ] A stale/unattested device is denied or dropped to a read-only/scoped session
- [ ] Verified access check
