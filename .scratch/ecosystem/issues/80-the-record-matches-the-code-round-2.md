# 80 — The record matches the code, round 2

Type: task (AFK)
Status: open
Blocked by: none

## Question

Ticket 67 makes the map match the surface. This ticket makes the ADRs, the tickets and the glossary match the code. Ten cheap corrections:

1. Fifteen resolved build tickets (21, 25, 26, 28, 29, 32, 36, 40, 41, 42, 43, 47, 49, 50, 52) cite "the TRUTH line of 2026-08-29" as proof their check is in the gate. That line is run 7, graded before the build, and its tree contains none of the checks. Append the dated correction ticket 40 already carries to the other fourteen, and widen ticket 67(d)'s check so any TRUTH figure quoted in `issues/*.md` must resolve to a real line whose tree contains the named check.
2. ADR-0010's consumer-side `sunset:` was decided away by ticket 13 D5. ADR-0008's dashboards were rejected on 2026-07-20. Neither carries a banner. Add dated superseded-in-part banners to both.
3. ADR-0019, 0020, 0021 and 0023 say `accepted` and nowhere say the decision rests on a bare agree. Copy ADR-0022's one-sentence provisionality line into each, with the originating ticket path.
4. CONTEXT.md's Governed-namespace entry says there is no CREATE deny. ADR-0022's 2026-08-28 addendum promoted `governed-namespace-requires-claim` to Deny inside an implementation run with no round. Correct CONTEXT.md to match the shipped code, and list the promotion in ticket 75 as an assistant-made call.
5. Restore GAPS rule 1 to `map.md`'s process rules, or delete it from GAPS.md with a dated reason. It was dropped in the copy.
6. ~~The currency controller: correct `map.md:113` with whatever ticket 75 Q13 decides, and delete or own the module in one commit.~~ **Direction settled and item DONE, 2026-09-05 (ticket 91 item 4).** Ticket 75 Q13 decided (a): the retirement is withdrawn. So the disjunction closes on **own**, not delete — "delete or own" is no longer an open choice and no build should read it as one. Ticket 91 executed the un-retirement: the module is a versioned member of platform's published `implementations` package numbered by the platform's own tag, its CronJob may only tighten, `CONTEXT.md` carries a **Currency controller** term, and `verify-currency.sh` grades that term's sentence. The two map sentences this item named — the ticket-13 line's "currency-controller retired" and "The currency controller is retired (ticket 13)" under *Not yet specified* — are corrected in the same change. Ticket 13's Answer carries the dated withdrawal with the reason each retirement clause failed on. **Nothing is left for ticket 80 here.**
7. The three ADR notes ticket 13 assigned itself (0004, 0007, 0010) are unwritten. Write them.
8. `talk/RUNBOOK.md` section 1 says driftwood's bring-up reconciles the real signed GitHub remote. `scripts/up.sh` reconciles an unsigned tag from a git server built on the laptop. Correct the runbook, or give `up.sh` a `--remote` mode.
9. The fourteen legacy repos and the `policy-as-versioned-flux` org carry no signpost to the eco-system. Add a dated "superseded reference implementation" banner to each README and an org description naming both implementations.
10. `platform/README.md` calls the adopter apparatus a shared config base. Three independent gates of 1087, 661 and 1213 lines share 260 lines. Say which it is, per ticket 75 Q7.

Done = a script under `verify/` greps each of the ten facts and passes; no ADR says `accepted` for a decision the tracker records as provisional; no ticket cites a number no TRUTH line records.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R10 and R12. Findings: process/P1, P4, P5, P7, P8, principles/P2-4, legacy/L4, L5, scope/F10, operability/O4, O7, truth-surface/TS-M4 (record half). Sibling of ticket 67.
