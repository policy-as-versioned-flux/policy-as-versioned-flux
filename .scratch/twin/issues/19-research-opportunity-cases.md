# 19 — Research: opportunity cases for the backtest roster

Type: research
Status: RESOLVED (2026-08-05)
Blocked by: none

## Question

Ticket 12 exposed a roster gap: **every backtest case chosen (Carillion, Enron, Wirecard, NMC, Kodak)
is a collapse.** We validate an engine promising *fear AND opportunity* exclusively on catastrophes,
and ticket 13's push/pull decision makes opportunity a first-class engine capability. The suite needs
opportunity cases held to the same evidential bar as the collapse cases.

Find, with dated contemporaneous evidence:
- **Seized-opportunity cases** — the option was *publicly visible* before it was taken, and someone took
  it. Scoreable: would the twin have surfaced the play at the time?
- **Missed-opportunity cases** — arguably more valuable: the option was visible, documented, and *not*
  taken, with a knowable counterfactual outcome.

Same bar as the collapse roster: **contemporaneous, opposed-interest, timestamped** evidence beats
retrospective narrative; **low parametric contamination** (a famous story an LLM has memorised proves
nothing); real **temporal resolution**; and an **actionability horizon** — was there a window in which
acting was still possible?

## Acceptance criteria
- [ ] ≥10 candidates surveyed across both classes and multiple sectors.
- [ ] Each scored on evidence contemporaneity, contamination risk, temporal resolution, actionability window.
- [ ] A recommended set (seized + missed) to add to the backtest suite, with rationale.
- [ ] Honest note on whether opportunity cases can meet the collapse cases' evidential bar at all.

## Answer (2026-08-05) — resolved. The bar CANNOT be met, and that is a finding.

**Structural verdict: not one of 14 candidates meets the collapse cases' evidential bar — for structural
reasons, not research failure.** The collapse bar rests on instruments that exist **because a collapse
creates the loss that pays for them**: capital-backed dated short theses (Muddy Waters/NMC,
Zatarra/Wirecard), **statutory adverse-position disclosure** (the free dated FCA short register that makes
Carillion beat Enron), court-forced examiner reports and parliamentary post-mortems (Valukas, HC 769),
CDS/ratings curves. **None has an opportunity equivalent. There is no short side of an opportunity** —
anyone with dated capital-backed conviction that a firm should buy an asset buys it themselves; publishing
destroys the edge. Nobody convenes an inquiry into a success.
**So ticket 12's negativity bias is not merely a reporting artefact — it is baked into how evidence is
created.** This bounds what the engine's opportunity half can ever be validated against, and must be
stated in any claim about opportunity performance.

**Three ideas the survey produced that were not asked for:**
1. **Activist investors are the closest analogue to short-sellers on the opportunity side** — opposed-
   interest actors with capital at risk who publish on a date.
2. **MISSED opportunities are better evidenced than SEIZED ones** — because someone flagged them at the
   time and was ignored, and **the flagging is the record**.
3. **HINDSIGHT-RESISTANCE CONTROLS — a new case category.** Cases where the contemporaneous record
   *contradicts* the canonical retelling, so **confident agreement with the famous story is a
   memorisation detector**.

**Recommended additions:**
- **SEIZED — DSV/Panalpina (2019)** *(primary)*: Cevian's Oct 2018 public demand, Artisan Partners
  attacking mid-bid, DSV's own failed Ceva bid as a dated leading indicator; ~2.5 months of dated public
  bidding. Contamination only medium (headline memorised; load-bearing texture is specialist trade press).
- **SEIZED — Albemarle/Rockwood lithium (2014-15)**: reframed to the *demand-signal detection* thesis —
  dated Feb 2014 sell-side notes on Gigafactory lithium demand + the Dec 2013 Talison/Tianqi 8-K
  supply-concentration tell; tight ~5-month window; low contamination. (The nominated overpay thesis was
  killed by verification — the criticism postdates close by ~11 months.)
- **CONTROL (scored inversely) — AstraZeneca rejects Pfizer (2014)**: shares fell 11-13% on rejection and
  Schroders publicly criticised it; "AZ was right" is **entirely retrospective**. **A twin confidently
  flagging this as a clean seize is retrieving, not reasoning.** Also carries the pack's only statutory
  clock (UK Takeover Code PUSU, 26 May 2014). Pair with Sanofi as a second inverse trap.
- **PULL-SIDE CONTAMINATION DIAL — Ørsted (2012-17)**: weak standalone (company-sourced narrative; the
  real decision point is far less dated than the famous endpoints; partly state industrial policy). Its
  value is the **Enron-as-control pattern on the opportunity side**: run the identical rubric on Ørsted
  (saturated) vs Albemarle/Deere (thin) at matched evidence density; **the delta measures pull-side
  memorisation leakage** and discounts every opportunity score.
- **MISSED — Royal Mail parcels automation** *(primary; closest to the collapse bar)*: the counterfactual
  sits **inside the subject's own audited filings** (GLS — the profitable automated continental parcels
  arm — reported line-by-line in the same segmental accounts), so no outside-rival inference is needed.
  6+ dated checkpoints incl. the legally-liable 2013 IPO prospectus forecasting the very trend, Ofcom
  statutory monitoring, dated rival hub openings, the Oct 2018 profit-warning RNS.
- **MISSED — Morrisons online grocery (2007-13)**: dated named third-party flags (The Grocer, 6 Jun 2009;
  a TNS director calling it "the obvious elephant in the room") against the CEO's **dated on-record
  refusal**. Scope the backtest tightly to pre-2010 evidence.
- **MISSED — RWE through the Energiewende (2000-11)**: hardest possible start timestamp (the EEG statute,
  1 Apr 2000) and the only structure rhyming with the collapse pattern — **a dated opposed-interest
  warning met by a documented company rebuttal** (WWF/SAM "Carbonizing Valuation" Nov 2006, publicly
  contested by RWE). Pairs with Ørsted: same trade, opposite sides, overlapping windows, shared external
  instrumentation. Frame as *insufficient reallocation*, not ignorance.

Full: `research/opportunity-cases.md`.
