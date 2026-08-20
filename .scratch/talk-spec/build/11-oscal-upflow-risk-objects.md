# 11 — OSCAL up-flow + risk objects

**What to build:** c2p emits observations/findings from CEL policy reports; the ledger extends it to emit OSCAL `risk`/POA&M objects (`deviation-approved`, £ as a `facet`).

**Blocked by:** 04, 05

**Status:** done (2026-08-20) — `estate/platform/oscal/verify-upflow.sh` PASSes offline

- [x] c2p emits observations + findings from CEL reports — `bash estate/platform/oscal/verify-upflow.sh` → `3 observations, 2 findings; AC-6 not-satisfied, CM-6 satisfied` (`result2oscal.py`)
- [x] The ledger generates OSCAL `risk`/POA&M objects (related-observations → the not-satisfied observation) — step 3: `risk 0248b558 (£21360) -> observation db875252 RESOLVES`; `render-exemption.py`'s `oscal_risk()` sets `status: "deviation-approved"` (`estate/platform/policy/render-exemption.py:144`)
- [x] £ attached as a `facet` under a custom `system` URI — `render-exemption.py:37,124-129`: `GBP_SYS = "https://pavf.dev/ns/risk/gbp"`, facet carries `{"name": "currency", "value": "GBP"}` under that system URI; asserted by `render-exemption.py`'s own selfcheck (line 177-184)

## Comments

- 2026-08-20 (audit mo-02): `verify-upflow.sh` PASSes offline, all 3 ACs directly evidenced; schema-validation against the real OSCAL spec is skipped (compliance-trestle CLI not installed) but that's not one of this ticket's ACs. Status corrected from `ready-for-agent` to `done`.
