# Skeptic re-derivation: P1 (process-and-record)

Verdict: NOT REFUTED. One number corrected (85 -> 70) and two scope corrections.

## Re-derived, holds
- GAPS.md:93 "1. No recommendation attached to an architectural question. State the trade, or make the call and record it as the assistant's." (block at GAPS.md:91-98, six rules).
- map.md:16 "Process rules (from the drift review): ..." lists five: GAPS 2, a NEW rule ("a bare agree or letter does not ratify architecture..."), GAPS 3, GAPS 4, GAPS 5. GAPS 1 and GAPS 6 are absent.
- grep -rn "recommendation attached" .scratch/ecosystem/ -> no hits (exit 1). Substance greps ("state the trade", "no recommendation", "make the call and record it as the assistant") -> no hits anywhere in .scratch/ecosystem/; repo-wide only .scratch/drift-review-2026-08-27/ files match.
- REPORT.md:26 and REPORT.md:249 quoted verbatim correctly.
- appendices/G-drift-findings.md:1434 sharpens it: "do not do both and then cite his one word as agreement. Retire bulk confirmation outright: no single reply may close more than one decision."
- 13-lift-or-retire-the-original-mechanisms.md:60 is exactly the quoted line.
- git log: 8a14528 2026-08-28 03:31:06 +0100 (map charted); 20568bc 2026-08-28 12:32:35 +0100 (14 grilling tickets resolved).
- Pattern recurred: 80 "➡️" recommendations in the 14 batch tickets (70 in held rounds; 10 in two superseded first drafts, tickets 09 and 24). All 14 tickets carry the single owner line "ive already read the recommendations and I can't find fault with a single one".
- Still recurring after the batch: 58-grilling-...md "Five questions were put with recommendations" (round dated 2026-08-31).

## Corrections
1. Count. GRILL-WALK.md:5: "Fourteen held rounds, five questions each: 70 questions, one ticket a day." 70, not ~85. Separately: D1-D5 (5) closed on a second owner line with a reason; C1-C20 were assistant-applied amendments, not owner-accepted items; tickets 04 (5), 07, 08 (7) closed earlier on their own separate bare-agree lines.
2. Ratification. REGRILL-ANSWERS.md:3 records "North star: ratified"; the 41 answers and 22 reversals follow. The six process changes are nowhere in the owner's answers - they are the review's own recommendation. The map nonetheless self-binds ("Process rules (from the drift review)"), so the discrepancy is real, but the ambition ref should not be described as owner-ratified.
3. Two rules dropped, not one. GAPS 6 (one north-star doc, one status vocabulary, one truth number) is also absent from map.md:16, but it has an owning ticket (02, NORTH-STAR.md as the one referent) and is met. GAPS 1 has no owning ticket anywhere in .scratch/ecosystem/issues/.
4. Partial substitute exists. GRILL-WALK.md:5 "Recommendations stay the assistant's until the owner gives a reason" is a partial adoption of rule 1's second branch, but the rounds do both (state the trade AND recommend) and the batch then cites one owner line - the exact shape G-drift-findings.md:1434 forbids.
