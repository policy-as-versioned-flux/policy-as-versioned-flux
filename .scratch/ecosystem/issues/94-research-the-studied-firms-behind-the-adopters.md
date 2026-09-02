# 94 — Research: the studied firms behind the adopters

Type: research (AFK)
Status: resolved
Blocked by: none

## Question

Ticket 75 Q7: driftwood, tuppence and ludlow are plausible firms. Where the estate cannot make a fictitious firm plausible, the firm becomes a nickname for a well-known, studied, existing firm, and its size, obligations and appetite are based on that firm's public numbers.

Find, from primary sources (annual reports, regulator decisions, court records, company filings), one candidate existing firm per adopter whose public record supplies:

- turnover, customer count, data-subject count and headcount, with the filing year;
- the regimes it is subject to (UK GDPR, PCI DSS, FCA, HIPAA, NIS2 as applicable);
- at least one published regulator action or breach with the final, collected figure and its litigation status;
- an appetite the record supports (a disclosed risk tolerance, an insurance programme, or a stated materiality threshold).

Match each candidate to the adopter's declared sector as recorded in its `party.yaml` and CONTEXT.md. Where the current signed numbers make no rung reachable (a £40,000 appetite against £86m turnover), show what the candidate's numbers would make reachable on the current ladder. Prefer UK firms with ICO or FCA records, because the ICO and FCA penalty schemas are the ones the estate publishes.

Record the findings as a Markdown file under `.scratch/ecosystem/research/94-studied-firms.md` with every number sourced by URL and date. Do not name a private individual. Do not choose; ticket 79 chooses under this record.

## Notes

Charted by ticket 75 (Q7). Feeds ticket 79 items 2 and 10. The ICO fine corrections (Doorstep Dispensaree £92,000 after the Court of Appeal 2024-12-09; Clearview AI never collected) are already in ticket 79.

## Answer

**2026-09-02.** Findings recorded at
[`.scratch/ecosystem/research/94-studied-firms.md`](../research/94-studied-firms.md), with every
number sourced by URL and date; no private individual named. One candidate per adopter:

- **driftwood → DSG Retail Limited** (Currys PC World / Dixons Travel, part of Currys plc). ICO
  Monetary Penalty Notice £500,000 (2020-01-09) for a PCI DSS/DPA 1998 breach affecting ≥14m
  people; still litigating six years on (FTT £250,000 in 2022, set aside by the Upper Tribunal in
  2024, point of law settled for the ICO by the Court of Appeal 2026-02-19, case remitted to the
  FTT) — **no final, collected figure exists today**, the same "final_as_of" problem ticket 79
  item 1 already names for Doorstep Dispensaree and Clearview. Currys plc's own Annual Report &
  Accounts 2024/25: turnover £8,706m, 24,706 employees, no published risk-appetite figure.
- **tuppence → Starling Bank Limited.** FCA Final Notice, £28,959,426 (2024-09-27, ref 730166),
  final and collected, no appeal — the cleanest of the three. Its own record (FCA notice +
  Starling's 2023 Annual Report): ~3.6m customers, £414.8m–£452.8m turnover (two primary sources
  differ slightly), 2,762 employees, an explicit Board-approved risk-appetite framework.
- **ludlow → Anthem, Inc.** HHS OCR Resolution Agreement $16,000,000 (2018-10-15), plus a
  $115,000,000 federal class-action settlement (final 2018-08-15) and a $48,200,000 multistate AG
  settlement (2020-09-30) on the same 2015 breach of 78.8m individuals — three independent final,
  collected figures. SEC 10-K FY2016: $84,194m revenue, 39.9m members, ~53,000 employees.

For each candidate the file shows the residual arithmetic: none of the three makes an existing
priced rung reachable by a bare swap of turnover, because the estate's own residual pricing scales
with the same size facts. Restated as a share of the candidate's own turnover, the driftwood
candidate's regulator record implies ~0.006%, tuppence's ~6–7%, ludlow's ~0.02–0.2% — three
different orders of magnitude, which bears directly on the "appetite as a share of turnover"
question open in ticket 79. Could not fetch: hhs.gov's Anthem page (403 to WebFetch and curl, its
Wayback snapshot unreachable from this environment) — corroborated instead via four independent
secondary sources; the ICO's original 2020 DSG press release no longer resolves at any URL tried,
so the FTT's own reproduction of the notice is cited instead. Ticket 79 item 2 picks under this
record; this ticket does not choose.
