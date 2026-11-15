# The penalty rate: a choice for the owner

Written 15 November 2026. Research only. Nothing lands in ico's feed. The owner chooses.

## The choice, in short

The loop stands at `isolated`. The shop serves 0 of 3. Every cycle is red, at a figure of GBP 1,643,518.63 against a tolerance of GBP 40,000.

That figure rests on one number nobody had counted: the penalty rate, the chance that one personal data breach draws an ICO monetary penalty. ico publishes it as `penalty_rate` in `penalty-schema/feed.json`. It is `null` today, and the loop reads `null` as 1.

Three researchers have now counted it, each a different way. A checker tried to break each count. The counts differ by a factor of about 18 at their point values, and about 200 from the lowest low to the highest high.

Two money choices are open, and they are coupled: the rate and the tolerance. The GBP 40,000 in driftwood's `party.json` is labelled "fixture 2026-07-31, not owner-declared". The assistant suggested 0.5% of turnover, GBP 430,000, on 14 November (`../DECISIONS.md`, "Tolerance: what the industry does"). The owner has chosen neither. From where the loop stands today:

| What the loop does | Tolerance GBP 40,000 | Tolerance GBP 430,000 |
|---|---|---|
| Waits 7 days, releases two notches, rests at `baseline`, green. The shop serves | a rate up to 0.0005618 (1 in 1,780) | a rate up to 0.01800 (1 in 56) |
| Turns green at `isolated` and never releases. The shop stays closed | above that, up to 0.01417 (1 in 71) | above that, up to 0.2539 (about 1 in 4) |
| Stays red at `isolated`, at a smaller figure. The shop stays closed | above 0.01417 | above 0.2539 |
| No rate (`null`, read as 1): red, closed, GBP 1,643,518.63 | GBP 1,603,518.63 over | GBP 1,213,518.63 over |

Where the three counts land, at their low, point and high:

| Count | Low, point, high | At GBP 40,000 | At GBP 430,000 |
|---|---|---|---|
| All reports | 0.000128, 0.0002095, 0.0004 | reopens, reopens, reopens | reopens, reopens, reopens |
| Cyber only | 0.000237, 0.000529, 0.001407 | reopens, reopens, green and closed | reopens, reopens, reopens |
| Serious breaches | 0.0010, 0.0038, 0.026 | green and closed, green and closed, red and closed | reopens, reopens, green and closed |

- At GBP 40,000 the method, and the end of its interval, decide whether the shop reopens.
- At GBP 430,000 every counted value reopens the shop except the top of the third count. No counted value leaves the loop red. Only `null` does.

## How the rate enters the figure

- A row's amount is `mean(events a year) x (mean(loss an event) + penalty rate x mean(penalty at the adopter's turnover))`.
- The figure is the sum of the open rows plus the cost of the current rung. One rate serves every row.
- There are three rows: a checkout data exfiltration (closed by `isolated`), a misused write credential, and an insider or lost-device disclosure. The last two are open at every rung. At `isolated` nearly all of the exposure, the sum of the open rows, is the insider row, which is not a cyber event. With no rate that is nearly all of the figure. At the counted rates the rung's cost of GBP 15,000 is a large part of it, and most of it below a rate of about 0.008.
- A release needs the loop to be release-ready on every cycle for `dwell_days`, which is 7. Release-ready means a looser rung is predicted at or below `(1 - margin) x tolerance`: GBP 32,000 at GBP 40,000, and GBP 344,000 at GBP 430,000.

## Table 1. The three counts, after their checks

| Count and files | What was counted | Rate | Interval | For | Against |
|---|---|---|---|---|---|
| **All reports** (`all-reports.md`, `all-reports-check.md`) | 20 security penalties over 95,466 breach reports of every kind, ICO years 2018/19 to 2025/26 | 0.0002095 (1 in 4,770) | 0.000128 to 0.000400 | Both sides are the ICO's own published records. The penalties match the annual reports' totals where a total is given; 2019/20 gives none, and the 2022/23 match is weaker evidence. It is the only count that covers every kind of breach | A rate over every report. In the ICO's incident file for 2019 to 2025, 89% of reports closed with no or informal action. Its researcher calls it a floor, too low for a serious breach by an amount the method cannot state |
| **Cyber only** (`cyber-only.md`, `cyber-only-check.md`) | 10 penalties that followed an outside attack over 18,897 reports the ICO classes as cyber, 2019 to 2025 | 0.000529 (1 in 1,890) | 0.000237 to 0.001407 | It counts the kind of event the largest row prices. The checker read every notice again | Ten events, clumped by year. Most cyber reports are small. For reports of 10,000 people or more its side figure is about 0.0067 (8 of 1,203), which the count and the check both call weak and biased high |
| **Serious breaches** (`serious-breaches.md`, `serious-breaches-check.md`; its researcher calls it the "own method") | 3 penalties over about 800 reports by commercial firms, cyber, 10,000 people or more, reported 2019 to 2022 | 0.0038 (1 in 270) | 0.0010 to 0.026 | The only count aimed at the case being priced. It matches each penalty to the year the breach was reported | Three events. The 800 is an estimate (650 to 960): the published counts bracket it at 394 and 2,957. The class was chosen after the numbers were seen. The top is a judgement |

What the checks changed:

- **All reports.** The rate and the interval hold. One sensitivity row was wrong: with the 1998-Act penalties added over the financial years, the count is 36 to 37, not 31, and the rate is 0.000377 to 0.000388, not 0.000325. So the top edge is soft: the sampling limits of other variants reach about 0.00053. The ICO's own "penalty pursued" shares, 0.05% and 0.03% of closed cases, are the same order of size.
- **Cyber only.** Nothing in the rate. The errors are dates and wording on left-out cases, and a reconciliation weaker than claimed. The low end is soft: if the year-to-year clumping is allowed for, it could fall to about 0.00014. The top does not move. The ICO's own sector tag files two of the ten, Ticketmaster and Interserve, under "Retail and manufacture".
- **Serious breaches.** The headline changed. The researcher counted 4 penalties and gave 0.005, with an interval of 0.0014 to 0.026. The checker removed Advanced, a processor that did not report the breach and had no duty to. That leaves 3 penalties: point 0.0038, low 0.0010. The checker kept the high at 0.026 as a judgement. Computed on 3 penalties it is 0.022. A sensitivity that adds the breaches reported in 2018 reaches about 0.029. The checker also corrected the range of the 800 from "650 to 930" to 650 to 960, and added that the count is per report, not per breach, so the rate per breach is higher.
- **Advanced** is counted in the first two counts and not in the third. Without it the cyber-only rate is 0.00048, inside its interval.

## Table 2. What the loop does at each rate

Every row was run, not reasoned. The rows are in order of rate. The two figures do not depend on the tolerance. "Figure at `isolated`" is the first cycle after the rate arrives. "Figure at `baseline`" is what the loop prints at `baseline` at that rate. Where the loop rests, its figure is the one for that rung. Green is the verdict `within`. Red is `saturated`.

| Rate | Where it comes from | Figure at `isolated` | Figure at `baseline` | Rests, at GBP 40,000 | Rests, at GBP 430,000 |
|---|---|---|---|---|---|
| 0.000128 | All reports, low | GBP 17,158.72 | GBP 24,240.18 | `baseline`, green, serving | `baseline`, green, serving |
| 0.0002095 | All reports, point | GBP 17,291.29 | GBP 25,698.05 | `baseline`, green, serving | `baseline`, green, serving |
| 0.000237 | Cyber only, low | GBP 17,336.01 | GBP 26,189.96 | `baseline`, green, serving | `baseline`, green, serving |
| 0.0004 | All reports, high | GBP 17,601.14 | GBP 29,105.69 | `baseline`, green, serving | `baseline`, green, serving |
| 0.000529 | Cyber only, point | GBP 17,810.97 | GBP 31,413.24 | `baseline`, green, serving | `baseline`, green, serving |
| **0.0005618** | **At GBP 40,000, the highest rate that still releases to `baseline`** | GBP 17,864.32 | GBP 31,999.96 | `baseline`, green, serving | `baseline`, green, serving |
| 0.0005619 | The next rate up | GBP 17,864.49 | GBP 32,001.75 | `isolated`, green, closed | `baseline`, green, serving |
| 0.0010 | Serious breaches, low | GBP 18,577.09 | GBP 39,838.46 | `isolated`, green, closed | `baseline`, green, serving |
| 0.001407 | Cyber only, high | GBP 19,239.09 | GBP 47,118.84 | `isolated`, green, closed | `baseline`, green, serving |
| 0.0038 | Serious breaches, point | GBP 23,131.47 | GBP 89,924.68 | `isolated`, green, closed | `baseline`, green, serving |
| **0.01417** | **At GBP 40,000, the highest rate at which `isolated` is within tolerance** | GBP 39,998.98 | GBP 275,422.61 | `isolated`, green, closed | `baseline`, green, serving |
| 0.01418 | The next rate up | GBP 40,015.25 | GBP 275,601.50 | `isolated`, red, closed | `baseline`, green, serving |
| **0.01800** | **At GBP 430,000, the highest rate that still releases to `baseline`** | GBP 46,228.74 | GBP 343,933.43 | `isolated`, red, closed | `baseline`, green, serving |
| 0.01801 | The next rate up | GBP 46,245.01 | GBP 344,112.31 | `isolated`, red, closed | `isolated`, green, closed |
| 0.026 | Serious breaches, high | GBP 59,241.29 | GBP 487,036.95 | `isolated`, red, closed | `isolated`, green, closed |
| **0.2539** | **At GBP 430,000, the highest rate at which `isolated` is within tolerance** | GBP 429,936.16 | GBP 4,563,698.37 | `isolated`, red, closed | `isolated`, green, closed |
| 0.2540 | The next rate up | GBP 430,098.81 | GBP 4,565,487.15 | `isolated`, red, closed | `isolated`, red, closed |
| 1 | Today: `null`, read as 1 | GBP 1,643,518.63 | GBP 17,909,890.06 | `isolated`, red, closed | `isolated`, red, closed |

Notes on the table:

- **The thresholds, to nine places.** Found by halving. At GBP 40,000 the loop releases at 0.000561802 and not at 0.000561803, and `isolated` is within tolerance at 0.014170628 and not at 0.014170629. At GBP 430,000 the loop releases at 0.018003721 and not at 0.018003722, and `isolated` is within tolerance at 0.253939249 and not at 0.253939250.
- **A release is two notches after one wait.** The dwell is served once at `isolated`. The next cycle, at `quarantine`, releases again.
- **Where the loop rests depends on where it stands.** A loop already at `baseline` would stay there, green, up to 0.001009031 at GBP 40,000 and up to 0.022811430 at GBP 430,000. A loop at `isolated` stays at `isolated` above the release threshold, because it is not release-ready. The margin makes that gap. In that gap the line prints `goal` `baseline` and `release_ready` false, and the loop does not move.
- **The soft edges change nothing at GBP 430,000 and little at GBP 40,000.** The soft top of all reports (0.00053) and the soft low of cyber only (0.00014) release at both tolerances. The other tops of the third count (0.022 and 0.029) do what 0.026 does: red at GBP 40,000, green and closed at GBP 430,000.
- **The room at GBP 40,000 is thin.** The cyber-only point releases with GBP 586.76 to spare, and the soft top of all reports with GBP 568.87. At GBP 430,000 the highest counted value that still releases is the third count's point, GBP 254,075.32 under the line. That threshold, 0.01800, falls inside the third count's interval, between its point and its high. So for that count the end still decides.
- **The cyber-only side figure for large breaches** (0.0067, interval 0.003 to 0.013) is green and closed at GBP 40,000 and releases at GBP 430,000, across its interval.
- **A counted rate does not make any row sourced.** At every rate the rows stay `upper` and the sourced share stays 0, because no row cites a tier and the row bases are editorial. The weakest basis moves from "not-counted: uk-gdpr penalty_rate" to "unsourced: cost of" the current rung.

## How long a release takes

Run, with back-dated ledger lines standing in for the waiting days, at both tolerances:

- With the first release-ready line 6 days 23 hours 59 minutes old, the verdict is `within`. The loop waits.
- With it 7 days 1 minute old, the verdict is `release`, `isolated` to `quarantine`. The next cycle releases to `baseline`. There the verdict is `within`, and still `within` after 39 more daily lines.

Read from the records, not run: the cycle runs once a day and on a merge that changes the rung line, and `LOOP.md` says a dwell is usually met a day late. So the shop would serve again 7 to 8 days after the first cycle that reads the new rate. Before that the rate has to reach driftwood: ico merges and its workflow cuts a tag, a driftwood cycle proposes the pin, the check passes it and the app merges it.

## The options

Each option names a count. The owner also chooses an end of its interval, and a tolerance.

- **Leave `null`.** *For:* it needs no judgement about the class of breach, and nothing has to be defended. *Against:* 1 is not a count either, and the highest value any count defends is 0.026, or 0.029 on one sensitivity. *The loop:* red and closed at both tolerances.
- **All reports.** *For:* the most events, 20, and the ICO's own totals on both sides. It is the only one that covers the insider row, which is nearly all of the exposure at `isolated`. *Against:* its researcher says it is too low for a serious breach, and its checker calls that reading sound. *The loop:* the shop reopens at any end and at both tolerances.
- **Cyber only.** *For:* it counts the kind of event the largest row prices, on ten events. *Against:* it leaves out breaches that are not cyber, and its researcher puts the rate for a large breach about ten times higher. *The loop:* at GBP 40,000 the low and the point reopen the shop, and the high leaves it green and closed. At GBP 430,000 all three reopen it.
- **Serious breaches.** *For:* it is aimed at a serious breach at a commercial firm. Among the reports of 2019 to 2022, no penalty went to a commercial firm for a breach that was not cyber: 0 of 11,326 (17,769 commercial reports less 6,443 cyber ones; the subtraction is this file's). So, as far as that cohort shows, a cyber rate does not run low for the insider row. Doorstep Dispensaree, a pharmacy fined for paper records, is outside that class: the ICO files it under Health, and by the third count's account, which its check did not verify, it did not start from a breach report. *Against:* three events, an estimated denominator, a class chosen after the numbers were seen, and the breaches reported in 2018 left out. *The loop:* the shop stays closed at GBP 40,000, green at the low and the point and red at the high. At GBP 430,000 the low and the point reopen it, and the high leaves it green and closed.
- **Which end.** *For the high end:* the number replaces 1, so it lowers the figure, and the high end puts the doubt in the count on the side of the larger figure. *Against:* `LOOP.md` step 10 lets a publisher's change lower the figure, so a point value breaks no rule. The feed's only kind for a number is `counted`. A point value is a count. The top of an interval is not, and its basis text would have to say so. The top of the third count is a judgement.
- **Which class.** The three counts answer three questions: any report, any cyber report, a serious cyber breach at a commercial firm. Which one fits depends on how large one "event" in the threat rows is. The rows say 2 to 9 events a year at GBP 1,000 to GBP 9,000 each, which reads like an ordinary report. The publisher marks those bands editorial: "Nobody has counted it".
- **The tolerance.** `../DECISIONS.md` gives the basis of each candidate. Here only GBP 40,000 and GBP 430,000 were run.

**One view, which the owner may ignore:** the earlier draft of this file preferred the third count at its high end, 0.026, so that the doubt about the class and about the end both raise the figure.

## What publishing would take

Not done here.

- Two values change in ico's `penalty-schema/feed.json`: `penalty_rate` and `penalty_rate_basis`. The feed's `version` changes in the same pull request.
- ico's test wants a number above 0 and at most 1, with the basis kind `counted`. A copy of the feed at 0.026 passes ico's four tests. Run here.
- The loop accepts that copy. With no probe, as the pin check runs it, it ends `could-not-look` with exit 3, which is what that check needs. Run here.
- The tolerance is in driftwood's `party.json`. It changes only by a pull request the loop cannot write.

## What was run, and what was not

- **Run.** The loop program, the rungs and the two feeds are the commits driftwood pinned on 14 November (platform `1c92754`, ico `93d1fc8`, feeds `2ea67d1`). The party file and the namespace file are driftwood's own, at `420d7e2`. All were read from each repository's history and not from a working copy. The ledger is a copy of driftwood's six lines. Each run is one `cycle` of that program:
  `python3 -B loop.py cycle --party <party copy> --namespace-file <namespace copy at the rung> --penalties <ico feed copy with the rate> --threats <feeds feed> --rungs <rungs.json> --probe <probe file for the rung> [--ledger <ledger copy>] --cause check --cluster none --run 0 --commit 0 --rung-set-by=check --out <temp file>`
- The probe files are in the shape of the ledger lines, one for each rung, for a cage that works at that rung. Rebuilt from each line's own fields, they give the five ledger lines that carry a verdict again: the same figure, exposure, cost and verdict.
- The feed copy carries the rate and the basis kind `counted`. The party copy changes only the tolerance amount, to 430000. Written as `share_of_turnover` 0.005, the loop prints the same tolerance.
- Each rate was run from `isolated`, cycle after cycle, until the loop made no move. Each threshold was found by halving between 0.000000001 and 1, in steps of 0.000000001. Several hundred runs in all.
- A second driver, written apart from the first, ran the same landed files again. It got the same three rung figures. It confirmed each of the six thresholds at its two boundary rates. At each count's low, point and high, at both tolerances, it got the resting rung and colour the tables state.
- **Not run.** No cluster, no workflow, no pin move, no merge and no network. The probe files stand in for a working cage. The web sources were not fetched again: the counts and their checks are the six reports'. The loop as changed on 15 November (platform `policy/v8.0.1`) was run at `isolated` for `null`, 0.0004 and 0.026 only. It gives the same three figures. The other tolerances in `../DECISIONS.md` (GBP 86,000, GBP 860,000, GBP 1,720,000) were not run.

## What is still unknown

- **How large one "event" in the threat rows is.** This picks the class, and so the count. feeds counting or sourcing its own rows would settle it.
- **How many reported breaches were really large.** The ICO records size as first reported, and often as "Unknown". This is the gap between 394 and 2,957 in the third count. An ICO count by final size, sector and year would settle it.
- **The rate for a breach that is not cyber, at a commercial firm.** One rate serves the insider row too. No count exists for large non-cyber breaches alone.
- **Late penalties.** In the commercial cyber cases a penalty comes 1.5 to 3.8 years after the report. Two public-sector and charity cases took 1.1 and 1.4 years. Reports of 2021 to 2023 may yet draw one.
- **The breaches reported from 25 May to 31 December 2018.** British Airways, Marriott and Ticketmaster were all fined. No report count by size exists for those months.
- **Retail alone.** The count of penalties on retailers is 0 or 1, depending on whose sector label is used.
- **Whether each penalty stood.** Appeals and payment were checked for a few only.
- **The rung costs,** GBP 500, GBP 6,000 and GBP 15,000. They are unsourced, and every threshold here depends on them.
- **What the live loop does with a counted rate.** Every run here used stand-in probe files. The first real cycle after a rate is published settles it.
