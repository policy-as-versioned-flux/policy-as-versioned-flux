# 23 — AI-Wardley forward layer

**What to build:** AI + market-intel Wardley mapping anticipates commoditisation / attack-cost-collapse / PQ *ahead* of the reactive feeds and hands the war-gamer a forward view so proportionality re-tunes before a threat lands.

**Blocked by:** 22

**Status:** done (2026-08-20) — `estate/platform/wardley/verify-wardley.sh` PASSes offline

- [x] Produces a Wardley map from market intel; flags commoditisation movement — `bash estate/platform/wardley/verify-wardley.sh`: `phishing-kits-aas ... product -> commodity (+0.36)`, `ransomware-aas ... product -> commodity (+0.24)`, `spiffe-workload-identity ... product -> commodity (+0.3)`; `commoditisation is read as MOVEMENT across the horizon, not static position`
- [x] Feeds a forward signal into the war-gamer — step 4: `2 forward drift(s) -> 2 signed PR(s), 0 merged, all gated`; step 5: `forward signal: 2 attacker-capability(ies) re-priced (phishing collapse x2.44); fed through the war-gamer -> 2 forward drift(s) -> 2 PR(s) proposed`
- [x] Map updates are attestable commits — step 1: `signed + verified: intel/market-intel.json`, `signed + verified: map/wardley-map.json`; step 2: `tampered map correctly rejected`; `estate/platform/wardley/sign-map.sh` gitsign-signs the landing commit (keyless, OIDC→Fulcio→Rekor) in addition to the detached openssl signature on the JSON

## Comments

- 2026-08-20 (audit mo-02): `verify-wardley.sh` PASSes offline, all 3 ACs directly evidenced, including a genuine tamper-rejection test. Status corrected from `ready-for-agent` to `done`.
