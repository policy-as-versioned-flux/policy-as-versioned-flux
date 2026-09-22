# 10 — What the trdrbot prior art teaches

Type: research (AFK)
Status: resolved
Blocked by: none

## Question

`https://github.com/emson/trdrbot_hackathon` is a live options-trading agent, MIT licensed, 296
commits. It is a working implementation of three things this estate claims but has not built.
Read it and report what transfers.

### What is already established, 2026-09-21, before this ticket

Confirmed by reading the repository:

- It scores forecasts under a proper scoring rule. Brier 0.237 across 76 scoreable forecasts, 95
  resolved.
- It states a sample-size bar: "every threshold that matters wants ~50 resolved forecasts".
- It sizes positions by measured track record. "Size is earned, not chosen." A SCALE tier is
  earned, not granted, and there is no manual approval gate.
- It runs an attribution matrix over thesis-held against outcome-profitable. A lucky win, which
  is a failed thesis with a profitable outcome, **blocks** promotion up the size ladder.
- It refuses instruments it cannot price, rather than approximating them. "A confident wrong
  payoff is worse than a refusal."
- `specs/issues.md` logs a defect at discovery, and only the fixing commit may remove it.

Confirmed by reading this estate:

- The twin already scores with Brier and log loss, `twin/scoring.py`, and already compares against
  an external adversarial baseline, `contemporaneous-consensus`, `twin/forecast_book.py:71`. It
  already names the coin-flip comparison, `twin/README.md:998`. The estate is **ahead** here.
- The twin has **no** luck-versus-skill separation. A grep for luck, spurious, and "right for the
  wrong reason" across `twin/*.py` and `twin/README.md` returns nothing. A forecast that scored
  well for the wrong reason is indistinguishable from one that scored well for the right reason.
- `twin/skill-thresholds.yaml` states **no** minimum corpus size. `twin/skills.py` refuses only an
  empty corpus. A one-item corpus passes today.

### What this ticket must answer

1. Read `agent/` and report the code that computes the attribution matrix, by file. Report how it
   decides that a thesis held, separately from whether the trade paid.
2. Report the confidence tier mechanism precisely. What tiers exist, what measured quantity
   promotes and demotes, over what sample size, and what each tier permits.
3. Where does the "~50 resolved forecasts" bar come from? Is it derived or chosen? Report which.
4. Read `specs/issues.md` and `specs/decisions.md`. Report how the defect ledger is enforced, if
   it is enforced by anything other than discipline.
5. Report what the repository does **not** do. It has no backtesting and it runs on live paper
   data only. Name every other limit its own documentation states.

   **Premise corrected 2026-09-21.** This item originally read "no backtesting and no Monte
   Carlo". The Monte Carlo half was wrong. The repository has a block bootstrap from each name's
   own demeaned returns, `agent/src/trdrbot/experiments.py:213`. The error came from a fetched
   page summary rather than the source, which is the mistake this estate's own rule names.
6. State plainly which of the five ideas above this estate should take, and which it should not,
   with a reason for each.

## Done

A research note under `.scratch/laya-loophole/research/`. Each of the six answers carries a file
reference into the trdrbot repository. The note ends with a take-or-leave verdict per idea.

Where an idea should be taken, the note graduates it as a ticket on the eco-system map. It does
not build it here.

## Notes

**Licence and attribution.** MIT, and the copyright line names a real person. Lifting code, or
crediting the idea in public, is a named-individual question. It goes to eco-system ticket 82 and
is not decided here.

**Why this blocks ticket 05.** Ticket 05 designs an earned permission for a model on a clock. This
repository has a working earned-permission ladder with an anti-superstition rule. Designing ours
without reading theirs first wastes the read.

**Do not flatter the source.** Brier 0.237 over 76 forecasts beats a constant 0.5 predictor, which
scores exactly 0.25, by 0.013. The repository is 8 days into paper trading and says its own
calibration is young. Report the ideas, not the numbers.

## Answer (2026-09-21)

Full note: [`research/10-trdrbot-prior-art.md`](../research/10-trdrbot-prior-art.md). Read at HEAD
`ae922ac`, 2026-09-04. deepwiki has no index of this repository; every claim is from the source.

**1. The attribution matrix** is `agent/src/trdrbot/experiments.py:315`, `attribute(held,
profited)` — a pure function of two booleans returning one of five verdicts (`:308-312`).
`agent/src/trdrbot/attribution.py` computes the two inputs independently: *held* from
`Thesis.holds_at` → `optmath.band_holds` (`:145`), an inclusive test against a band written at
entry, `None` when unfalsifiable; *paid* from `pos.last_pnl_pct > 0` (`attribution.py:173`),
measured, never inferred from the close label. It runs **at the thesis horizon, not at close** —
a stop on day 2 of a 10-day thesis says nothing yet. A lucky win carries signal `None`, so the
memory update is *skipped*, not neutralised (`experiments.py:366`).

**2. The ladder** is `competence.py:124`. EXPLORE/ESTABLISH/SCALE/MATURE at 10/15/20/25% book cap.
**The promoting quantity is the count of resolved theses** (0/5/15/40), plus an attributable rate
≥0.6 at SCALE and ≥0.7 at MATURE, plus Murphy reliability <0.04 at MATURE only. Lucky wins and
unscoreables are excluded from the attributable numerator (`:303`), so luck blocks promotion.
Demotion is asymmetric: 5% drawdown drops a tier, 10% drops to EXPLORE. No human gate exists.
Below 5 verdicts the rate is `None` — unmeasured, never 0 — and blocks only at MATURE.

**3. The ~50 bar is chosen, not derived.** Every mention traces to one imported research sweep,
`docs/sources/trading_techniques_review.md:83,241`. Its sibling 152 is a real power calculation;
the ~50 carries no formula, no simulation, no citation. The ladder does not use it.

**4. Nothing enforces the defect ledger.** CI runs pytest and ruff only. No hook, no script; the
one test that reads `issues.md` counts entries and never fails. Enforcement is prose plus
publication to the public site. Its own principles doc rates prose at 25-40% compliance.

**5. Correction:** it has no backtesting (out of charter), but it **does** have Monte Carlo — a
block bootstrap (`experiments.py:193`, `discovery.py:52`). Other stated limits: calendars and
diagonals refused not approximated, one vol not a smile, no guardrail layer by choice, indicative
playbook pricing, the first position permanently unattributable, IEX feed only.

**6. Verdict.**

- **TAKE — luck/skill attribution.** The estate has none. → eco-system ticket **100**.
- **TAKE — a minimum corpus size, derived, never ~50.** ~50 would fail all six skills at once. →
  ticket **101**.
- **TAKE — automatic pre-registration** (`ledger.py:24`), not in the five. Fold into 100.
- **LEAVE — the size ladder.** Take its failure instead: I-68 says the sizer ran in 2 of 89
  cycles. Ticket 05's permission must bind at a seam the actor cannot skip.
- **LEAVE — the scoring rule.** The estate is ahead.
- **LEAVE — refuse-what-you-cannot-price.** Already held, by allow-list, in `forecast_book.py`.
- **LEAVE — the defect ledger.** Prose where the estate already has CI gates.

Map edits for 100/101 are specified in the note and deferred: a sibling agent holds that file.
