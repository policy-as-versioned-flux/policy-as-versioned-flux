# 07 — `ico` penalty schema feed

**What to build:** `ico` publishes a small bespoke, signed, versioned penalty schema (regime → violation-type → fine formula/cap), sourced from real public fine magnitudes, feeding the FAIR loss-magnitude directly (not force-fit into OSCAL).

**Blocked by:** 01, 02

**Status:** done (2026-08-20) — `estate/ico/verify-penalty-feed.sh` PASSes offline

- [x] `ico` schema signed + versioned; grounded in real public fines — `bash estate/ico/verify-penalty-feed.sh` → `v1 signature verified`, `v2 signature verified`; `estate/ico/schema/v2/penalty-schema.json` cites named, dated real penalties (British Airways £20m/2020, Marriott £18.4m/2020, TikTok £12.7m/2023, Clearview AI £7.55m/2022, Standard Chartered £102m/2019, etc., each with a `source`)
- [x] `fair.py` consumes it as a loss-magnitude input — same run, step 3: `ale(v1 uk-gdpr/lower-tier warn) = £16901472`, computed by unmodified `fair.py` via `to_fair_scenario.py`
- [x] A schema bump changes the £ via a reviewable PR — same run, step 4: `£ moved by £-7,861,681 on a version-only schema diff (£16,901,472 -> £9,039,791)`, `ok  tampered schema correctly rejected` proves the signature actually gates it

## Comments

- 2026-08-20 (audit mo-02): `verify-penalty-feed.sh` PASSes offline, all 3 ACs directly evidenced. Status corrected from `ready-for-agent` to `done`.
