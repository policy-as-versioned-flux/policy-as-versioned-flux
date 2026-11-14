# K3: the loop cannot converge at the tightest rung (refuter's working)

Date: 2026-11-14. Read-only. Paths are relative to the scratchpad: `fresh/<repo>/...`. I read hub history from the local working copy at `<hub working copy>` with `GIT_NO_LAZY_FETCH=1`. `fresh/hub` is a partial clone, and `git log -S` there tried to fetch from the network and was refused.

## The claim under test

> At the tightest rung two of three adopters remain far above tolerance (tuppence about 2.06M GBP against 15,000; ludlow about 61.7M GBP against 5,000), and driftwood is inside (about 36,150 against 40,000) only because of the unsourced 0.98 reduction. The tolerance figures date from an automated build commit of 2026-07-31 and were never set by the owner as considered amounts. One ICO fine line, a fixed 2.0781 percent of turnover at an editorial frequency, dominates every adopter's exposure.

## Verdict: partly refuted

- **Sentence 1 (numbers) holds**, with two corrections. Ludlow's figure and driftwood's figure are partial sums, so the composer gives no verdict on either. Driftwood's "inside" also depends on which lines are left out of the sum, not only on the 0.98.
- **Sentence 2 (tolerance origin) holds**, with one qualification. On 2026-10-23 the owner adopted assurance cutoffs whose middle value equals each tolerance. The record says the tolerances themselves were "retained", not chosen. The owner's exact words for that adoption could not be found.
- **Sentence 3 (ICO dominates every adopter) is false for tuppence.** At tuppence the ICO line is 17.4% of exposure. A twin forward-intel line is 81.8%. The 2.0781% figure is right, but only for the pinned ICO v3. That version carries two fines the estate itself recorded as stale. The publisher's current v4 corrects them, and on v4 the share would be about 0.70%.

## 1. Every priced line, per adopter

Terms used below:
- **Uncaged amount**: the line's annual loss figure before any cage.
- **Residual**: what is left after the cage tier's reduction: amount x (1 - reduce).
- **Reduction table**: baseline 0.30, restricted 0.70, quarantine 0.92, isolated 0.98. Source: `fresh/platform/graded/cage.py:84-110`. The table calls itself "self-declared, evidenced by nothing but this comment" (`cage.py:71-72`).
- **The aggregate**: the composer sums only lines of kind `feed` and `twin` (`fresh/platform/compose/composition.py:5086`, `:5202`). It recomputes each residual with `cage.caged_residual` (`:5213-5215`). If any of those lines has no tier, the verdict is `None` (`:5247-5252`).

### driftwood (turnover 86,000,000 GBP; tolerance 40,000)

Sources: `fresh/driftwood/composed/evidence.json` (`prices`, `floor_change`); `fresh/driftwood/composed/HEADER.yaml:1361-1431`.

| line (kind) | uncaged GBP | tier | residual GBP | in aggregate? | source |
|---|---:|---|---:|---|---|
| ico penalty-schema v3 (feed) | 1,787,177.08 | isolated | 35,743.54 | yes | lm from two ICO fines scaled to turnover; lef (1,2,4) editorial |
| feeds threat-register v4 (feed) | 19,558.55 | isolated | 391.17 | yes | editorial DBIR-based bands, "COULD NOT LOOK" |
| feeds cve v3 (feed) | null (absence only) | none | null | named as not tiered | "No scanned CVE is in the pinned KEV feed; 418 ... named absences" |
| twin forward-intel 2.0.0 (twin) | 758.33 | isolated | 15.17 | yes | grade 3 anchor (DSG/Currys) |
| ico supersede | 200,751.40 | none | n/a | no, by design | surcharge for staying on v3 behind v4 |
| insurer quote-driftwood (premium) | 113,403.30 | none | n/a | no, it is a cost | signed quote |
| platform twin-agent (agent-cage) | 0.00017 | isolated | 0.00 | no | |
| switching x4 | 1,787,177.08 / null / null / 0.00 | none | n/a | no | |

- **Recomputed sum**: 35,743.54 + 391.17 + 15.17 = 36,149.88. This matches `HEADER.yaml:1376`.
- **Verdict**: `breaches_band: null` (`:1380`), because the cve line is untiered (`:1381`, `:1392-1393`).
- **ICO share**: 98.88% of the priced subtotal (1,807,493.96, `:1368`). The same 98.88% holds for the residual.

### tuppence (turnover 861,741,000 GBP; tolerance 15,000)

Sources: `fresh/tuppence/composed/evidence.json`; `fresh/tuppence/composed/HEADER.yaml:1329-1400`.

| line | uncaged GBP | tier | residual GBP | source |
|---|---:|---|---:|---|
| ico penalty-schema v3 | 17,907,950.70 (`:1369`) | isolated | 358,159.01 (`:1352`) | as driftwood, turnover 861.7M |
| threat-register v4 | 326,139.13 (`:1387`) | isolated | 6,522.78 | editorial, lef (4,9,20) |
| cve v3 | 437,107.34 (`:1393`) | isolated | 8,742.15 | Log4j KEV headline entry |
| twin forward-intel 1.0.0 | 84,198,283.09 (`:1399`) | isolated | 1,683,965.66 (`:1361`) | FCA Starling final notice as 6.4/7.0/9.9% of revenue; lef (4,9,20) editorial; grade 3 |
| supersede / agent-cage / switching | 1,128,446.21 / 18.70 / ... | | | not in aggregate |

- **Recomputed sum**: 2,057,389.61. This matches `:1343`. `breaches_band: true` (`:1347`).
- **Shares**: ICO is 17.41% of the uncaged subtotal (102,869,480.25, `:1336`) and 17.41% of the residual. Forward-intel is 81.85% of both.
- **Floor**: every line already chose isolated before the floor was applied (`floor_change.lines`, before_tier = isolated). Forward-intel's own `policy_basis` reads "no priced tier is under the tolerance (15000.00 GBP), so the selection fails closed".

### ludlow (turnover 197,584,000,000 USD, priced as 147,814,767,711.53 GBP; tolerance 5,000)

Sources: `fresh/ludlow/composed/evidence.json`; `fresh/ludlow/composed/HEADER.yaml:1389-1468`; `fresh/ludlow/composed/feeds/ico/penalty-schema/v3/PROVENANCE.json:10-16`.

| line | uncaged GBP | tier | residual GBP |
|---|---:|---|---:|
| ico penalty-schema v3 | 3,071,757,723.56 (`:1431`) | isolated | 61,435,154.47 (`:1413`) |
| threat-register v4 | 318,229.78 | isolated | 6,364.60 |
| cve v3 | null (112 absences) | none | null |
| eol v2 | 787,227.83 | isolated | 15,744.56 |
| twin forward-intel 1.0.0 | 13,435,900.93 | isolated | 268,718.02 |

- **Recomputed sum**: 61,725,981.64. This matches `:1404`.
- **Verdict**: `breaches_band: null` (`:1408`), because cve is untiered.
- **ICO share**: 99.53% of both.
- **"Far above" is still safe without a verdict.** The partial sum is 12,345 times tolerance, and the missing line can only add to it.

## 2. Attacks on sentence 1

1. **"Far above": holds.**
   - Tuppence without its ICO line still leaves 1,699,231. Ludlow without its ICO line still leaves 290,827. Neither result depends on the ICO line.
   - The largest reduction is 0.98, so any line whose uncaged amount is more than 50 times tolerance cannot fit any rung.
   - The ratios: tuppence ICO is 1,194 times tolerance; tuppence forward-intel is 5,613 times; ludlow ICO is 614,352 times.
2. **"Driftwood is inside": overstated.** The composer refuses to say so (`breaches_band: null`).
   - The one untiered line is cve. Its own evidence says no scanned CVE is in the KEV feed, so treating it as zero is defensible. The code does not do that.
   - Driftwood sits 3,850.12 below tolerance only because three things are left out of the sum:
     - **The supersede line.** 200,751.40 x 0.02 = 4,015.03, which is more than the margin. It is excluded by design: the basis text says it is "never summed into the exposure the line itself is already in" (evidence.json supersede `basis`; `composition.py:504-510`).
     - **The cage's own run cost.** Isolated costs 15,000 a year (`cage.py:107`). Residual plus cost is 51,149.88 (`cage.py:318-330`, `tcor`).
     - **The insurer premium.** 113,403.30. That is a cost, not exposure, but it alone is more than tolerance.
3. **"Only because of the 0.98": holds, and holds under every alternative I tried.**
   - At quarantine (0.92) the ICO line alone leaves 142,974.17.
   - The break-even reduction for the ICO line is 0.97785. Below that, driftwood is over.
   - Driftwood's own twin publishes a mode reduction of 0.90 for isolated (`fresh/driftwood/twin/orgs/driftwood/responses/run-the-checkout-at-isolated.yaml:10-14`, evidence grade 5, "grants no pound credit"). On that curve the total is 180,749.40.
   - Even on the publisher's corrected ICO v4 (section 4), quarantine leaves about 49,900. So isolated, and therefore 0.98, is still needed.

## 3. Attacks on sentence 2 (where the tolerance figures came from)

1. **First appearance in text: the 2026-07-31 build commit.**
   - Platform `7a36bf7` (2026-07-31 16:22:39 +0100) adds `risk/appetite.json` with 40000/15000/5000. The hub carries the same file in `26770f85` (`estate/platform/risk/appetite.json`).
   - The commit message reads "Fresh-context agents built the six-org estate ... Claude-Session: ...". It is authored under the owner's name, but the agents built it.
   - The only earlier `-S'40k'` hit is hub `6ab21fb8` (12:48 the same day). That hit is in binary pitch media only (`frame250.png`, `pitch.mp4`, `seg08.mp4`), not text.
   - The talk-spec written that morning delegated the figures. In `6ab21fb8`: "Exact £, bands, and per-institution threat registers *derive* during build from FAIR + feeds + org briefs". Also `.scratch/talk-spec/issues/04-risk-proportionality-model.md:48`.
2. **The numbers have never changed.**
   - Platform `201beae` (2026-08-20) changed only the note and added a platform entry. `4e809f8` (2026-08-28) deleted the file.
   - The numbers moved unchanged into each `party.yaml` on 2026-08-28. `git blame`:
     - driftwood `party.yaml:60` comes from `710595cb`
     - tuppence `:34` comes from `01258be6`, with the comment "Copied from platform/risk/appetite.json orgs.tuppence.tolerance" (`:18`)
     - ludlow `:35` comes from `7c37d2e3`
3. **The meaning changed while the number stayed.**
   - In July the figure was a per-control threshold on "residual risk-bought (ALE_warn - ALE_deny)" that flipped Audit to Deny (`7a36bf7` appetite.json note).
   - On 2026-09-02 the assistant redefined it as "one quantity, an annual aggregate", on the owner's bare "yes" to Q4 (`fresh/hub/.scratch/ecosystem/issues/75-...md:111`).
4. **The owner chose "plausible firms", and the tolerances were not recalibrated.**
   - Ticket 75 Q7 put this to the owner: "a retailer with a £40,000 appetite against £86m turnover is not plausible" (`75-...md:41`). The owner answered: "They should be plausible firms" (`:81`).
   - Sizes were then reset to real filings on 2026-10-04 (tuppence `party.yaml:21-25` from `c70edb11`; ludlow `:22-26` from `4f81da7e`). The tolerances were left as they were.
   - The result: ludlow's 5,000 GBP is 0.0000034% of its turnover.
5. **Qualification: the 2026-10-23 adoption.**
   - The owner "accepted all three recommendations" (`fresh/hub/.scratch/ecosystem/issues/27-the-cage-ladder-round-2.md:184-188`; `backup/.scratch/ecosystem/research/adopt-three-owner-policies-20261023/ADOPTION.md:1-3`).
   - That set `assurance_bands` at 0.1x / 1x / 10x tolerance. For example, driftwood `attest_at: 40000` (`party.yaml:57`, commit `d2c6f83`).
   - The record says "Existing party tolerances and strict comparison semantics remain" (ADOPTION.md:3; ticket 27:187).
   - The owner had answered "delegate" to the item that asked for the proposals (`backup/.../resume-user-decisions-20261022/OWNER-INSTRUCTION.md:7-12`).
   - The brief put to the owner asked him to "use or revise the proposed GBP/year cutoffs". It did not ask about the tolerance (`backup/.../resume-active-20261022T2203/NEXT-OWNER-DECISIONS.md:3`).
   - The exact reply is said to be in `OWNER-DECISION.json`. That file is not in the backup disk, the local working tree, or git history I could read. The three adoption commit bodies carry only a title.
   - So: what the owner wrote on 2026-10-23 **could not be determined**. On the record, he accepted cutoffs anchored to the tolerance figures. He was not asked to set the tolerance.

## 4. Attacks on sentence 3 (the ICO line)

1. **"Dominates every adopter": false for tuppence.** The ICO line is 17.4% there, and forward-intel is 81.8% (section 1). True for driftwood (98.9%) and ludlow (99.5%).
   - Tuppence's dominant line is also a regulator fine taken as a share of revenue at an editorial frequency: the FCA Starling notice, lef (4,9,20). So a broader sentence does hold for all three: "a regulator-fine-as-share-of-turnover line at an editorial frequency dominates each adopter".
2. **Formula, as it ran**: the vendored v3 converter `fresh/driftwood/composed/feeds/ico/penalty-schema/v3/penalty-schema/to_fair_scenario.py`.
   - **lm** (loss magnitude, the size of one fine) = (min, median, max) of the example fines. Here that is 275,000 / 3,913,900 / 9,063,360 (`:56-61`), scaled by 0.02 x turnover / 8,700,000 (`:68-71`).
   - **lef** (loss-event frequency, events per year) = `DEFAULT_WARN_LEF = (1, 2, 4)`, labelled "plausible regulatory-incident frequency" (`:38`). The line itself says "warn/deny lef are editorial (schema doesn't carry frequency)".
   - Feed values: rate 0.02, cap 8,700,000, examples Clearview 7,552,800 and Doorstep 275,000 (`.../v3/feed.json`; identical to `fresh/ico/penalty-schema/v3/feed.json`).
3. **The "fixed 2.0781%": confirmed, as a ratio that comes out of the arithmetic, not as a written constant.**
   - amount / turnover = 0.0207811 at all three adopters.
   - The simulation is deterministic (`fair.py:54-55`: 10,000 iterations, seed 42) and linear in the lm scale, so the ratio is the same for every adopter.
   - The closed-form mean is 2.0748%. The 0.16% gap comes from `simulate()` rounding each year's event count to an integer (`fair.py:159-160`).
4. **The figure rests on stale inputs.**
   - Ticket 75 recorded on 2026-09-02 that Doorstep is £92,000, not £275,000, and that Clearview "has never been collected". Correcting them "moves driftwood's largest line by minus 63 percent" (`75-...md:29`). The decision said "The two stale fines are corrected" (`:111`).
   - ICO v4 (published 2026-09-09, signed tag v4.0.1 on 2026-10-23) does correct them. Clearview is `not-collected` and does not price. Doorstep is 92,000 `final`. The frequency becomes (0,2,4), still "editorial" (`fresh/ico/penalty-schema/v4/feed.json`, lower-tier `frequency`).
   - All three adopters still pin v3 (`party.yaml` inherits; evidence.json `superseded.state: behind`).
   - **v4 counterfactual (hand-computed, closed form, using the v4 converter `fresh/ico/schema/to_fair_scenario.py:206-249`)**: about 0.702% of turnover, a cut of about 66%.
     - driftwood ICO about 603,600, isolated residual about 12,100, total about 12,500. Quarantine would still be about 49,900, which is over.
     - tuppence ICO about 6.05M, total about 1.82M. Still breached.
     - ludlow ICO about 1.04bn, total about 21.0M. Still breached, and ICO is still about 98.6% of it.
   - These are estimates, not composer output.
5. **The v3 converter has no statutory-maximum clamp.** The v4 converter added one (`fresh/ico/schema/to_fair_scenario.py:234-249`), because "the old rule ... priced a fine the statute does not permit". Under v3, the per-event maximum for tuppence and ludlow is above the UK GDPR statutory maximum.
6. **Whether UK GDPR applies to ludlow (a US health firm) could not be determined.** The converter says which regimes apply to which workload "stays an open, separate gap (ticket 17)" (v3 converter `:27-29`).

## Restated claim

At the tightest rung (isolated, reduction 0.98), tuppence leaves £2,057,390 against £15,000, and the composer flags it as a breach. Ludlow leaves at least £61,725,982 against £5,000; that is a partial sum with no verdict, but it can only grow. Driftwood's partial sum is £36,150 against £40,000. That is no verdict, and it is under tolerance only because three things hold: the self-declared 0.98 (below 0.978 it is over), the supersede line and the cage's £15,000 run cost being left out of the sum, and the unpriced cve line. The tolerances (40,000 / 15,000 / 5,000) first appear in text in the agent-built estate commit of 2026-07-31, have never changed since, and were kept when sizes were reset to real firms. The owner's 2026-10-23 adoption accepted assurance cutoffs set at 0.1x / 1x / 10x those tolerances, while the record says the tolerances were "retained"; the owner's own words that day were not found. The ICO v3 line, 2.0781% of turnover (seed-42 simulation, editorial frequency 1/2/4, two fines the estate itself recorded as stale), dominates driftwood (98.9%) and ludlow (99.5%) but not tuppence (17.4%), where a grade-3 FCA-anchored twin line is 81.8%. On the publisher's corrected v4 the ICO share of turnover falls to about 0.70%, and none of the three verdicts changes.
