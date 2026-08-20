# 25 — Honesty layer (calibration + feed-integrity + reflexive)

**What to build:** Calibration/back-testing of the £ (credibility theory / Bühlmann); feed integrity (signed/sourced/bounded) + AI-proposer bounds (confidence, rate-limit, learn-from-rejections) with the gate as the hard backstop; reflexive self-governance (platform/Kyverno/Flux under the same risk model).

**Blocked by:** 13, 22

**Status:** REOPENED — NOT DONE. 2 of 3 ACs hold; the third (reflexive self-test) fails on a real bug, not an environment gap — `bash estate/platform/honesty/verify-honesty.sh` exits 1: `FAIL: reflexive selfcheck failed`

- [x] Real incidents/near-misses logged, compared to prediction, £ recalibrated — same run, step 1: `Bühlmann Z=0.78 k=1 mu=£63333 | back-test ludlow: model £1025511 vs actual £130000 (0/5 VaR95 breaches) -> over-prices (actuals run cold) — recalibrate down`; `estate/platform/honesty/incidents.json` holds the logged incidents
- [x] Feeds signed/sourced/bounded; proposer bounded; the gate is the hard backstop — step 2: `live feed signature verifies; a forged feed is rejected`; step 3: `bounded 4 drift(s): 1 suppressed(learned), 1 held(low-conf), 2 proposed(gated,unmerged) | rate-limit opens exactly 3/5 | no merge() by construction`
- [ ] The apparatus prices + governs itself under the same model (passes its own test) — **FAILS**: `python3 estate/platform/honesty/reflexive.py selfcheck` → `AssertionError: {'signing_key_present': False, ...}` in `cmd_selfcheck` (`reflexive.py:128`). Root cause: `feed_integrity()` (`reflexive.py:73-74`) checks for the existence of the **private** key `feeds/keys/feeds-signing-key.pem` — which `estate/.gitignore:2` deliberately keeps out of git (correctly: a private key shouldn't be committed) — instead of the **public** key `feeds-signing-key.pub.pem`, which is the one actually present and the one `feeds/verify.sh` uses to verify signatures. Isolating the two other checks: `reflexive.py govern-self` alone returns `"passes_own_test": true` (`risk_bought £1,018,853 > tolerance £10,000 -> Deny`) — the actual self-governance verdict is correct; only the `signing_key_present` flag inside `feed_integrity()` is wrong

## Comments

- 2026-08-20 (audit mo-02): this is a real, reproducible bug in `reflexive.py`, not a missing-cluster gap — it fails the same way on a fresh checkout with no Docker/network involved. It also means `estate/talk/verify-all.sh`'s offline pass count is currently 24/25, not 25/25, which contradicts the "25/25" figure `estate/ARCHIVE.md` cites for a different (much earlier) commit — see ticket 27's comments. Fix is a one-line change in `feed_integrity()` (check `feeds-signing-key.pub.pem` instead of the private key), but that's a code fix outside this audit ticket's scope (mo-02 is audit-only) — filing it here as the specific unmet AC rather than fixing it inline. Status corrected from `ready-for-agent` to `REOPENED — NOT DONE`, following the same honest-partial convention as tickets 14/17.
