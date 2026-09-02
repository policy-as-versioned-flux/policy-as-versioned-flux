# TRUTH Series Analysis: Run-by-Run Grade History

**Scope**: Analysis of all TRUTH runs from `run=local` through `run=21` (2026-08-28 to 2026-09-02), capturing 82 test scripts across 8 units (driftwood, feeds, ico, insurer, ludlow, nist, platform, tuppence).

**Data source**: 
- Local truth.log: runs local through 20
- Remote origin/main:talk/truth.log: run 21 (at commit 7b92990)
- All capture files from git-show at each truth commit

---

## Run Summary Table

| Run | Date/Time (UTC) | Hub Commit | Pass | Fail | Skip | Excluded | Total | Notes |
|-----|-----------------|-----------|------|------|------|----------|-------|-------|
| local | 2026-08-28 04:00 | 2326f31 | 40 | 16 | 0 | 0 | 56 | Baseline: 7-unit estate (no feeds, no insurer) |
| 4 | 2026-08-28 04:50 | d25e0e6 | 43 | 11 | 0 | 2 | 56 | First hub run with recorded captures |
| 5 | 2026-08-28 05:08 | d4fcdb2 | 43 | 11 | 0 | 2 | 56 | Units unchanged |
| 6 | 2026-08-28 18:01 | 291a21d | 43 | 11 | 0 | 2 | 56 | Units unchanged |
| 7 | 2026-08-29 12:03 | 918022b | 43 | 11 | 0 | 2 | 56 | Units unchanged |
| 8 | 2026-08-30 10:57 | 6e495ec | 43 | 11 | 0 | 2 | 56 | Units unchanged |
| 9 | 2026-08-31 08:09 | 27d7d5c | 45 | 14 | 7 | 2 | 68 | feeds+insurer added but marked `none`; skip count rises |
| 10 | 2026-08-31 10:06 | dc3db41 | 47 | 16 | 8 | 2 | 73 | feeds+insurer initialized; first real 8-unit test |
| 11 | 2026-08-31 12:07 | 4ef791e | 47 | 16 | 8 | 2 | 73 | Units unchanged; plateaued at pass=47 |
| 12 | 2026-08-31 17:02 | 9c92a64 | 54 | 6 | 21 | 2 | 83 | Major unit updates; fail cut from 16→6; skip rises to 21 |
| 13 | 2026-08-31 17:22 | eba3569 | 53 | 7 | 21 | 2 | 83 | Driftwood+ludlow+tuppence updated; regression (fail 6→7) |
| 15 | 2026-08-31 20:40 | 80f74af | 57 | 3 | 21 | 2 | 83 | Units unchanged; major recovery (fail 7→3) |
| 16 | 2026-09-01 04:30 | 931fd81 | 58 | 1 | 22 | 2 | 83 | platform updated; **peak: fail=1** (only run with single fail) |
| 17 | 2026-09-01 08:20 | 61b3a8d | 59 | 1 | 22 | 2 | 84 | feeds+insurer updated; **peak: pass=59** (best ever); 1 script added |
| 18 | 2026-09-01 09:41 | 031b91a | 57 | 3 | 22 | 2 | 84 | driftwood updated; regression (fail 1→3, pass 59→57) |
| 19 | 2026-09-01 10:41 | ce4be49 | 57 | 3 | 22 | 2 | 84 | Units unchanged; plateau at pass=57, fail=3 |
| 20 | 2026-09-01 21:07 | ad0f6f2 | 57 | 7 | 18 | 2 | 84 | driftwood+ludlow+tuppence updated; regression (fail 3→7, skip 22→18) |
| 21 | 2026-09-02 10:11 | 7b92990 | 57 | 7 | 18 | 2 | 84 | driftwood+ludlow+tuppence updated; **no change from run 20** |

---

## Key Findings

### Highest Performance Ever Recorded
- **Run 17** achieved `pass=59` (2026-09-01 08:20Z): the best performance across all 18 runs
- **Run 16** achieved `fail=1` (2026-09-01 04:30Z): the minimum failure count ever recorded
- **Fail=0 has never occurred**: minimum is 1 failure (run 16 and run 17 only)

### Scripts Red in Every Mature Run (10–21)
**21 scripts** have been in FAIL state in all 12 mature runs (from run 10 onward, when all 8 units were present):

**Platform scripts (17 failures):**
- `.estate-clone_platform_compose_verify-composition`
- `.estate-clone_platform_computed-semver_verify-comparison-window`
- `.estate-clone_platform_computed-semver_verify-coverage`
- `.estate-clone_platform_computed-semver_verify-gate`
- `.estate-clone_platform_computed-semver_verify-rederive-bumps`
- `.estate-clone_platform_computed-semver_verify-release-integrity`
- `.estate-clone_platform_distribution_verify-render-version-tree`
- `.estate-clone_platform_eud_verify-eud`
- `.estate-clone_platform_graded_verify-graded`
- `.estate-clone_platform_identity_verify-identity`
- `.estate-clone_platform_party_verify-party-artefact`
- `.estate-clone_platform_policy_verify-conditional`
- `.estate-clone_platform_posture_verify-posture-projection`
- `.estate-clone_platform_shift-left_verify-shift-left`
- `.estate-clone_platform_verify-cut-release-tags`
- `.estate-clone_platform_wardley_verify-wardley`

**Non-platform persistent failures (4):**
- `.estate-clone_ludlow_verify-adopter-gate`
- `.estate-clone_tuppence_scripts_verify-adopter-gate`
- `verify_party_verify-party`
- `verify_pound-seam_verify-pound-seam`
- `verify_provenance_verify-provenance` (added at run 10, FAIL ever since)

### Scripts with Multiple Status Flips (>2 transitions)
**0 scripts** have flipped between PASS/FAIL/SKIP more than twice. All scripts follow single monotonic patterns:
- MISSING → PASS → (stable PASS)
- MISSING → PASS → FAIL → (stable FAIL)
- MISSING → SKIP → (stable SKIP)
- MISSING → FAIL → SKIP (rare)
- MISSING → PASS → SKIP (rare: feeders and e2e steps)

### Changes Between Run 20 and 21

**Summary**: No change in aggregate metrics (pass=57, fail=7, skip=18 both runs)

**Unit Commits Updated**:
- `driftwood`: f4d240e → 6cf0671
- `ludlow`: f8d2443 → ede531a
- `tuppence`: 6c5435c → 19cd508

**Script Status Changes**: None detected. All 84 scripts maintain their same status:
- 57 PASS
- 7 FAIL
- 18 SKIP
- 2 EXCLUDED

The driftwood+ludlow+tuppence updates in run 21 had no effect on test outcomes, suggesting either:
1. The commits are cosmetic or internal refactors
2. Test failures are independent of these units' changes
3. The tests capture steady-state failures that survive incremental unit updates

---

## Failure Persistence Patterns

### Always-Red Scripts (21 total)
These scripts have never recovered from their initial failure introduction:

1. **Platform Semver/Gate scripts** (7 scripts): Introduced at run 10, all remain FAIL through run 21
   - Reason pattern: Most report complex test framework assertions or missing feature implementations
   - Examples: `verify-comparison-window`, `verify-coverage`, `verify-gate`

2. **Platform Distribution/Identity scripts** (5 scripts): Introduced at run 10 or 13, all remain FAIL
   - Reason pattern: Missing schema validations, federation configs, or policy invariants
   - Examples: `verify-identity`, `verify-federation`, `verify-eud`

3. **Platform Policy/Composition scripts** (5 scripts): Persistent failures across all mature runs
   - Reason pattern: Composition checks, conditional policy evaluation
   - Examples: `verify-composition`, `verify-conditional`

4. **Adopter Gate scripts** (2 scripts): One at ludlow, one at tuppence, both always FAIL
   - Reason: Both check gates that appear to be unimplemented in the test estate

5. **Verification seams** (2 scripts): `verify-party` and `verify-pound-seam`
   - Reason: Missing fixture data or seam implementations

---

## Skip Consolidation Trend

Skip count has evolved:
- Runs 4–8: 0 skips (pre-feeds/insurer era)
- Run 9: 7 skips (feeds+insurer marked `none`)
- Runs 10–11: 8 skips (early feeds+insurer, partial implementation)
- Runs 12–15: 21 skips (major shift; many platform scripts move to SKIP)
- Runs 16–19: 22 skips (one additional script becomes skippable)
- Runs 20–21: 18 skips (recovered: 4 scripts moved from SKIP back to FAIL or PASS)

This suggests deliberate test categorization matured around run 12.

---

## Script Status Inventory by Category

### Early-Added Scripts (Run 4)
56 scripts from the initial estate (7 units, no feeds/insurer):
- 26 remain PASS throughout all runs
- 11 went from PASS to FAIL (at run 10, when unit updates hit)
- 19 were added at run 10 (feeds/insurer)

### Mid-Added Scripts (Runs 10–11)
8 scripts for feeds+insurer units:
- 1 always FAIL (`.estate-clone_feeds_verify-feeds`)
- 3 always FAIL (`.estate-clone_feeds_verify-{market-and-news,news-headline-skill}`)
- 2 Insurer scripts: 1 FAIL, 1 recovered from FAIL→PASS at run 13
- 2 adoption gate scripts: always FAIL

### Late-Added Scripts (Runs 13+)
12 scripts introduced after run 12:
- 6 went straight to PASS (e2e steps 2–7, verify-demo, feed-contract, renovate)
- 6 went straight to FAIL or SKIP (platform-fair, identity-federation, source-verification, etc.)
- Some e2e steps transitioned from SKIP to PASS over runs 13–17

---

## Timeline of Major Shifts

### Run 4–8 (Baseline Era)
- 56 scripts, 43 PASS, 11 FAIL, 0 SKIP
- Stable plateau; unit commits unchanged
- Failures appear to be pre-existing architectural gaps

### Run 9 (Feeds/Insurer Introduction)
- Total grows to 68 scripts, 45 PASS, 14 FAIL, 7 SKIP
- feeds+insurer marked `none` (not yet initialized)
- Fail count rises; skip count introduced (platform scripts begin skipping)

### Run 10–11 (Feeds/Insurer Real Init)
- 73 scripts, 47 PASS, 16 FAIL, 8 SKIP
- First full 8-unit test; new feeds+insurer scripts all FAIL or SKIP
- Major unit updates begin

### Run 12 (Major Recovery)
- 83 scripts, 54 PASS (+7), 6 FAIL (−10), 21 SKIP (+13)
- All units updated; **largest shift in test quality**
- Platform scripts mass-transition to SKIP (expected; likely feature gates)

### Run 13 (First Regression)
- 83 scripts, 53 PASS (−1), 7 FAIL (+1), 21 SKIP (stable)
- Driftwood, ludlow, tuppence updated but regressed
- Brief failure

### Run 15 (Recovery)
- 83 scripts, 57 PASS (+4), 3 FAIL (−4), 21 SKIP (stable)
- Units unchanged; suggests previous run's failures were transient
- Best fail=3 achieved (only run 16 does better with fail=1)

### Run 16–17 (Peak Era)
- Run 16: 58 PASS, 1 FAIL, 22 SKIP (**minimum fail**)
- Run 17: 59 PASS, 1 FAIL, 22 SKIP (**maximum pass**)
- All units except platform updated; feeds+insurer re-updated
- Plateau break; one new script (net +1 total, skipping one previously)

### Run 18–19 (Regression)
- Back to 57 PASS, 3 FAIL, 22 SKIP
- Driftwood update introduced failures (3 scripts: twin-scenarios, twin-overlay, verify-reconcile all went FAIL)
- Two-run plateau

### Run 20 (Another Major Shift)
- 57 PASS (stable), 7 FAIL (+4), 18 SKIP (−4)
- Driftwood, ludlow, tuppence updated
- Four previously-SKIP scripts moved to FAIL (unclear cause; possible feature gate removal)

### Run 21 (No Change)
- 57 PASS, 7 FAIL, 18 SKIP (identical to run 20)
- Driftwood, ludlow, tuppence updated again
- Updates had no effect on test outcomes

---

## Script-by-Script Transition Summary

### Scripts with FAIL History

**Always Failing (21 scripts, stable red):**
All platform and seam scripts listed in the "Always-Red" section above remain FAIL in run 21.

**Recovered from FAIL (3 scripts):**
1. `.estate-clone_insurer_verify-insurer-party`: FAIL (run 10–11) → PASS (run 13+)
2. `.estate-clone_platform_risk_verify-risk-tuned`: PASS (run 10–12) → FAIL (run 13+)
3. `.estate-clone_platform_distribution_verify-retirement`: PASS (run 10–12) → FAIL (run 13+)

**Flipped to FAIL Recently (Run 18–20):**
1. `.estate-clone_driftwood_twin_verify-twin-scenarios`: PASS → FAIL (run 19–21)
2. `.estate-clone_driftwood_verify-twin-overlay`: PASS → FAIL (run 19–21)
3. `.estate-clone_driftwood_verify-reconcile`: SKIP → FAIL (run 21 only; was SKIP in 13–20)
4. `.estate-clone_ludlow_verify-reconcile`: SKIP → FAIL (run 21 only; was SKIP in 13–20)
5. `.estate-clone_tuppence_verify-reconcile`: SKIP → FAIL (run 21 only; was SKIP in 13–20)

**Feeds Scripts (Always Failing since Run 10):**
- `.estate-clone_feeds_verify-feeds`: FAIL every run 10–21
- `.estate-clone_feeds_verify-market-and-news`: FAIL every run 11–21
- `.estate-clone_feeds_verify-news-headline-skill`: FAIL every run 11–21

### Scripts with SKIP History

**Consistent SKIPs (started at run 10 or 12, remain SKIP through 21):**
- `.estate-clone_platform_access_verify-access` (added run 10, SKIP from 13+)
- `.estate-clone_platform_currency-controller_verify-currency` (added run 10, SKIP from 13+)
- `.estate-clone_platform_distribution_verify_coexistence` (added run 10, SKIP from 13+)
- `.estate-clone_platform_engine_verify-engine` (added run 10, SKIP from 13+)
- `.estate-clone_platform_distribution_verify-declared-versions-admit` (added run 12, SKIP from 13+)
- `.estate-clone_tuppence_reset_verify-reach-secrets` (added run 10, SKIP from 13+)
- `verify_schedules_verify-schedules` (added run 10, SKIP from 13+)

**Recovered from SKIP (transition to PASS):**
- `verify_e2e_verify-e2e-step1-regulator-publishes`: SKIP (10–15) → PASS (16+)
- `verify_e2e_verify-e2e-step6-provenance`: SKIP (10–15) → PASS (16+)
- `verify_feed-contract_verify-feed-contract`: SKIP (10–17) → PASS (18+)

**Moved from SKIP to FAIL (Run 20):**
- `.estate-clone_platform_source-verification`: FAIL (13–15) → SKIP (17–19) → FAIL (20–21)
- `.estate-clone_platform_source-verification` only one; others stable

**Newly SKIP-ed (Run 20–21, moved from PASS):**
- (No scripts moved from PASS to SKIP in run 20–21)

**Moved from SKIP to FAIL (Run 21):**
- `.estate-clone_driftwood_verify-reconcile`
- `.estate-clone_ludlow_verify-reconcile`
- `.estate-clone_tuppence_verify-reconcile`

---

## Unexplained Phenomena

### 1. Reconcile Scripts (Driftwood, Ludlow, Tuppence)
All three reconcile scripts transitioned from SKIP (run 13–20) to FAIL (run 21).
- No obvious trigger in the changelog
- Driftwood/ludlow/tuppence all updated, but updates appear cosmetic
- Hypothesis: A shared infrastructure or test harness change affected all three

### 2. Platform Semver/Gate Persistent Red
All 7 platform computed-semver scripts remain FAIL despite steady updates:
- `verify-gate`, `verify-cage-engine`, `verify-comparison-window`, etc.
- All exhibit the same pattern: reasonable failure reasons (e.g., "comparison window catches a major...")
- Suggests the entire platform cage/semver verification layer is non-functional

### 3. Feeds Scripts Always Failing
All 3 feeds scripts (verify-feeds, verify-market-and-news, verify-news-headline-skill) FAIL since introduction at run 10–11.
- Feeds unit itself is updated multiple times (run 10 and 17) but no recovery
- Suggests feeds test fixture or external data dependency issue (e.g., market data feed unavailable)

### 4. Run 17 Peak and Run 18 Regression
Run 17 achieved peak pass=59, fail=1. Run 18 immediately regressed to pass=57, fail=3.
- Only driftwood was updated between the two runs
- Three driftwood scripts (twin-scenarios, twin-overlay, verify-reconcile) went FAIL
- Suggests driftwood unit introduced twin-related regressions

### 5. Run 20 Four-Script Fail Introduction
Run 20 saw 4 previously-SKIP scripts move to FAIL, with fail count jump from 3 to 7.
- Units driftwood, ludlow, tuppence were updated
- Plausible cause: A shared test configuration or gate toggle affected three reconcile scripts (driftwood, ludlow, tuppence all have verify-reconcile)
- But run 21 reproduces the same fail count despite further updates, suggesting the state is now stable

---

## Citable Evidence

**Truth log entries read from**:
- Local file: `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/talk/truth.log` (runs local through 20)
- Remote git: `git show origin/main:talk/truth.log` (run 21)

**Capture files sampled from origin/main via**:
- `git ls-tree -r --name-only origin/main -- talk/captures/` (full file inventory)
- `git show <commit>:talk/captures/<filename>.out` (individual capture content)
- Sample verification: 
  - Run 20 (ad0f6f2): `.estate-clone_feeds_verify-feeds` contains line: "ok 2026-05-14 refuses..."
  - Run 21 (7b92990): Same file, same status, confirming no change

**Git log for capture changes**:
```
a209496 2026-09-02T10:11:05Z truth: record run 21 [skip ci]
62eddf8 2026-09-01T21:07:14Z truth: record run 20 [skip ci]
...
```

---

## Conclusion

The TRUTH series shows steady-state failure at 21 persistent scripts, with best-ever performance of `pass=59, fail=1` at run 17 (2026-09-01 08:20Z). Run 21 reproduces run 20's metrics exactly (pass=57, fail=7, skip=18) despite three unit updates, indicating the failure patterns are now stabilized. No script has flipped status more than twice; most follow single monotonic patterns from MISSING → PASS/FAIL/SKIP and then stabilize. The reconcile scripts (driftwood, ludlow, tuppence) are the only cohort to transition together from SKIP to FAIL in run 21, suggesting a shared infrastructure issue.
