# 95 — The record states the purpose

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

The 2026-09-02 review found that no document says what the estate is for, who receives it, or by when. Ticket 75 answered that. Write it down where every session orients:

1. NORTH-STAR gains a section before §1, "0. What this is for", in the owner's chain: (a) a touring talk that proves the corrected thesis as running code, leading to (b) a reference implementation ControlPlane lifts into client work, which makes (c) adoption by a fourth organisation available because the estate is open source, all underwritten by (d) the argument as a written, checkable artefact. No date: "when we've got something good, we'll tour it" (owner, 2026-09-02). Audience: the circuit the last talk toured, listed in ticket 75.
2. §4's heading and preamble say it is the assistant's build order, with a dated line, and that the definition of done is fitness for (a) as the truth surface defines green under ticket 75 Q8 (b), with the ceiling published.
3. §6 records three things with dates: the talk is a byproduct and a marketing tool (owner, 2026-09-02, superseding the 2026-07-23 instruction and re-attributing the existing byproduct line to the owner); the development-window theatre, in which the assistant reviews and merges as a second identity while the narrative says a human merges, with AI disposal as the end state; and the identity substrate as designed and shelved (ticket 90).
4. §3 principle 2 replaces "That a refusal is therefore the bottom rung... is my reading, not your words" with the owner's 2026-09-02 words from ticket 75 Q5.
5. §8 gains the pointer ticket 75 already added, expanded to the sixteen decisions by number.
6. CONTEXT.md's Cage and Multi-version coexistence entries are already amended by ticket 75; check they agree with the new §0 to §6 text.

Done = a reader of NORTH-STAR alone can answer "what is this for, who receives it, by when, and what is done", and every sentence that rests on the owner carries a date.

## Notes

Charted by ticket 75 (Q1, Q2, Q5, Q6, Q9, Q15, Q16). First in the order of attack: every other ticket's definition of done reads against §0.

## Answer

Resolved 2026-09-03. A reader of NORTH-STAR alone can now answer the four questions.

1. **§0 "What this is for"** is new. It carries the owner's chain (a) to (d) with the 2026-09-02 quote from Q1; who receives each purpose, with the circuit of about twenty venues (2022-06-01 to 2023-09-21) named as the audience of (a) and the "principal engineers and leaders" reading marked as the assistant's; "by when" as the owner's "when we've got something good, we'll tour it" (Q15); "what is done" pointing at §4's preamble; and the two consequences recorded with Q1 (the licence work in ticket 82 is on the route, the truth surface is the instrument of (d)).
2. **§4** is re-headed "The build order: what the demonstration must show". Its preamble says it is the assistant's build order (owner, "not mine", 2026-09-02, Q2) and defines done as fitness for (a) as the truth surface defines green under Q8 (b), the ceiling published (ticket 83), the cage graded through two more lane facts (ticket 86), with (d) true on every citable run. The "none of steps 1 to 5" line is dated 2026-08-27 and a dated standing line for 2026-09-02 follows, including the step-2 fold (fired once for real, the price not moving is a £-inputs defect owned by tickets 77 and 79).
3. **§6** records three things, each dated: the talk is a byproduct and a marketing tool (owner, 2026-09-02, Q9 and Q16), superseding the 2026-07-23 instruction, with the byproduct line re-attributed from the twin map to the owner; the development-window theatre with the Q6 quote, the second identity `pavc-other-hand` created 2026-09-03 (ticket 88), ticket 87 as the protection, and AI disposal as the recorded end state; the identity substrate designed and shelved (Q12, delegated; ticket 90), with the 24-of-24 Rekor count dated.
4. **§3 principle 2** no longer says "is my reading, not your words". It quotes the owner's Q5 answer in full, spelling as sent, and draws the one consequence: a workload that does not fit its cage does not run (ticket 89). The Q6 quote in §6 is also the full answer.
5. **§8** gains a dated update listing the sixteen decisions by number, each with its status label (owner-reasoned, owner-instructed, delegated), its date, and the tickets or ADR that carry it. The ticket text says ticket 75 "already added" a pointer; at HEAD (bb7fd8f) NORTH-STAR.md contained no reference to ticket 75, so the pointer is new, not expanded.
6. **CONTEXT.md** Cage and Multi-version coexistence entries were checked against the new §0 to §6 text. Both already carry the ticket 75 amendments (the owner's mutating-controller words; the 2022-03-11 reason and three declared lines). They agree. No edit was needed.
7. **The check in the gate.** The ticket asks for text edits; the map's process rule says every ticket's definition of done includes wiring its check into the gate, so `verify/record/verify-record-states-the-purpose.sh` exists and `talk/verify-all.sh` discovers it. It greps every fact above, requires a date on every line that attributes something to the owner (line grain, coarser than the sentence grain the Done line asks for), and checks the two CONTEXT.md entries. Its self-check strips §0 from a copy and reverts principle 2 to the assistant's reading, requires both to FAIL, and runs first on the plain path, as step 7 does. It grades the record, not the estate. The TRUTH line's `total` moves from 84 to 85 on the next run; ticket 83's ceiling is derived from its manifest and is unaffected.

Applied from the two-axis review before the commit: the AI-disposal end state now carries its real date (re-grill 29, 2026-08-28) instead of "before ticket 75"; the Q16 decision, the venue list and the no-onboarding fold are attributed to the assistant as delegated, not to the owner; the Q5 and Q6 quotes are complete; §4 defines a lane fact inline so "done" reads from the file alone.

Not changed: the file's title line still reads "proposed re-baseline, for the owner's ratification". That is history and the Status line below it records the ratification. §1's "every actor is attestable" and principle 6 are ticket 90's to edit; §6 says so.
