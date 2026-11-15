# The penalty rate: a choice for the owner

Written 15 November 2026. Run again the same day on the loop of `policy/v8.0.1` and feeds 5.1.0. Research, written before the owner chose.

**Chosen on 15 November 2026.** The owner chose the count over all reports, at its point value, 0.0002095, and a tolerance of 0.5% of turnover, GBP 430,000 (`../DECISIONS.md`, "15 November: the four answers"). The assistant had recommended the cyber-only count. Ico published the rate as `v5.1.0`, and the loop followed it the same day: ledger line 11 reads GBP 17,290.68, `within`, release-ready, at a tolerance of GBP 430,000. The rest of this file is the research as it was put to the owner: where it says the owner chooses, or has not chosen, read it as of that moment.

## The choice, in short

The loop stands at `isolated`. The shop serves 0 of 3. Every cycle is red. On feeds 5.1.0 the figure is GBP 1,643,087.14 against a tolerance of GBP 40,000. The live loop has not yet followed that tag: driftwood still pins feeds 5.0.1, and its last ledger line reads GBP 1,643,518.63. Every loop figure below is the one on `policy/v8.0.1` and feeds 5.1.0.

The figure rests on one number nobody had counted: the penalty rate, the chance that one personal data breach draws an ICO monetary penalty. ico publishes it as `penalty_rate` in `penalty-schema/feed.json`. It is `null` today, and the loop reads `null` as 1.

Three researchers have now counted it, each a different way. A checker tried to break each count. The counts differ by a factor of about 18 at their point values, and about 200 from the lowest low to the highest high.

Two money choices are open, and they are coupled: the rate and the tolerance. The GBP 40,000 in driftwood's `party.json` is labelled "fixture 2026-07-31, not owner-declared". The assistant suggested 0.5% of turnover, GBP 430,000, on 14 November (`../DECISIONS.md`, "Tolerance: what the industry does"). When this was written the owner had chosen neither. From where the loop stood then:

| What the loop does | Tolerance GBP 40,000 | Tolerance GBP 430,000 |
|---|---|---|
| Waits 7 days, releases two notches, rests at `baseline`, green. The shop serves | a rate up to 0.0005618 (1 in 1,780) | a rate up to 0.01800 (1 in 56) |
| Turns green at `isolated` and never releases. The shop stays closed | above that, up to 0.01417 (1 in 71) | above that, up to 0.2540 (about 1 in 4) |
| Stays red at `isolated`, at a smaller figure. The shop stays closed | above 0.01417 | above 0.2540 |
| No rate (`null`, read as 1): red, closed, GBP 1,643,087.14 | GBP 1,603,087.14 over | GBP 1,213,087.14 over |

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
- There are three rows: a checkout data exfiltration (closed by `isolated`), a misused write credential, and an insider or lost-device disclosure. The last two are open at every rung. Since feeds 5.1.0 the misused write credential prices at GBP 0.00. So at `isolated` all of the exposure, the sum of the open rows, is the insider row alone, at every rate. The insider row is not a cyber event. With no rate the exposure is nearly all of the figure. At the counted rates the rung's cost of GBP 15,000 is a large part of it, and most of it below a rate of about 0.008.
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

Every row was run, not reasoned, on the loop of `policy/v8.0.1` and feeds 5.1.0. The rows are in order of rate. The two figures do not depend on the tolerance. "Figure at `isolated`" is the first cycle after the rate arrives. "Figure at `baseline`" is what the loop prints at `baseline` at that rate. Where the loop rests, its figure is the one for that rung. Green is the verdict `within`. Red is `saturated`.

| Rate | Where it comes from | Figure at `isolated` | Figure at `baseline` | Rests, at GBP 40,000 | Rests, at GBP 430,000 |
|---|---|---|---|---|---|
| 0.000128 | All reports, low | GBP 17,158.15 | GBP 24,239.61 | `baseline`, green, serving | `baseline`, green, serving |
| 0.0002095 | All reports, point | GBP 17,290.68 | GBP 25,697.44 | `baseline`, green, serving | `baseline`, green, serving |
| 0.000237 | Cyber only, low | GBP 17,335.39 | GBP 26,189.34 | `baseline`, green, serving | `baseline`, green, serving |
| 0.0004 | All reports, high | GBP 17,600.45 | GBP 29,105.00 | `baseline`, green, serving | `baseline`, green, serving |
| 0.000529 | Cyber only, point | GBP 17,810.23 | GBP 31,412.50 | `baseline`, green, serving | `baseline`, green, serving |
| **0.0005618** | **At GBP 40,000, the highest rate that still releases to `baseline`** | GBP 17,863.56 | GBP 31,999.20 | `baseline`, green, serving | `baseline`, green, serving |
| 0.0005619 | The next rate up | GBP 17,863.73 | GBP 32,000.99 | `isolated`, green, closed | `baseline`, green, serving |
| 0.0010 | Serious breaches, low | GBP 18,576.14 | GBP 39,837.51 | `isolated`, green, closed | `baseline`, green, serving |
| 0.001407 | Cyber only, high | GBP 19,237.97 | GBP 47,117.72 | `isolated`, green, closed | `baseline`, green, serving |
| 0.0038 | Serious breaches, point | GBP 23,129.32 | GBP 89,922.53 | `isolated`, green, closed | `baseline`, green, serving |
| **0.01417** | **At GBP 40,000, the highest rate at which `isolated` is within tolerance** | GBP 39,992.36 | GBP 275,415.99 | `isolated`, green, closed | `baseline`, green, serving |
| 0.01418 | The next rate up | GBP 40,008.62 | GBP 275,594.87 | `isolated`, red, closed | `baseline`, green, serving |
| **0.01800** | **At GBP 430,000, the highest rate that still releases to `baseline`** | GBP 46,220.47 | GBP 343,925.16 | `isolated`, red, closed | `baseline`, green, serving |
| 0.01801 | The next rate up | GBP 46,236.73 | GBP 344,104.03 | `isolated`, red, closed | `isolated`, green, closed |
| 0.026 | Serious breaches, high | GBP 59,229.57 | GBP 487,025.23 | `isolated`, red, closed | `isolated`, green, closed |
| **0.2540** | **At GBP 430,000, the highest rate at which `isolated` is within tolerance** | GBP 429,988.83 | GBP 4,565,377.17 | `isolated`, red, closed | `isolated`, green, closed |
| 0.2541 | The next rate up | GBP 430,151.45 | GBP 4,567,165.93 | `isolated`, red, closed | `isolated`, red, closed |
| 1 | Today: `null`, read as 1 | GBP 1,643,087.14 | GBP 17,909,458.57 | `isolated`, red, closed | `isolated`, red, closed |

Notes on the table:

- **What the re-run changed.** Feeds 5.1.0 prices the misused write credential at GBP 0.00. None of the 18 outcomes in the table of where the three counts land changes. Every figure in Table 2 falls, by GBP 0.57 to GBP 431.49. One threshold moves at four figures: at GBP 430,000 the highest rate at which `isolated` is within tolerance is now 0.2540, not 0.2539. So at GBP 430,000 a rate of 0.2540 now leaves `isolated` green, not red.
- **The thresholds, to nine places.** Found by halving. At GBP 40,000 the loop releases at 0.000561844 and not at 0.000561845, and `isolated` is within tolerance at 0.014174699 and not at 0.014174700. At GBP 430,000 the loop releases at 0.018004184 and not at 0.018004185, and `isolated` is within tolerance at 0.254006869 and not at 0.254006870.
- **A release is two notches after one wait.** The dwell is served once at `isolated`. The next cycle, at `quarantine`, releases again.
- **Where the loop rests depends on where it stands.** A loop already at `baseline` would stay there, green, up to 0.001009084 at GBP 40,000 and up to 0.022812008 at GBP 430,000. A loop at `isolated` stays at `isolated` above the release threshold, because it is not release-ready. The margin makes that gap. In that gap the line prints `goal` `baseline` and `release_ready` false, and the loop does not move.
- **The soft edges change nothing at GBP 430,000 and little at GBP 40,000.** The soft top of all reports (0.00053) and the soft low of cyber only (0.00014) release at both tolerances. The other tops of the third count (0.022 and 0.029) do what 0.026 does: red at GBP 40,000, green and closed at GBP 430,000.
- **The room at GBP 40,000 is thin.** The cyber-only point releases with GBP 587.50 to spare, and the soft top of all reports with GBP 569.62. At GBP 430,000 the highest counted value that still releases is the third count's point, GBP 254,077.47 under the line. That threshold, 0.01800, falls inside the third count's interval, between its point and its high. So for that count the end still decides.
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
- **All reports.** *For:* the most events, 20, and the ICO's own totals on both sides. It is the only one that covers the insider row, which is all of the exposure at `isolated`. *Against:* its researcher says it is too low for a serious breach, and its checker calls that reading sound. *The loop:* the shop reopens at any end and at both tolerances.
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

The tables were run twice. Every loop figure, threshold and outcome in this file now comes from the second run.

- **The first run, 14 November's pins.** The loop program, the rungs and the two feeds were the commits driftwood pinned on 14 November (platform `1c92754`, ico `93d1fc8`, feeds `2ea67d1`). The party file and the namespace file were driftwood's own, at `420d7e2`. All were read from each repository's history and not from a working copy. The ledger was a copy of driftwood's six lines. Each run was one `cycle` of that program:
  `python3 -B loop.py cycle --party <party copy> --namespace-file <namespace copy at the rung> --penalties <ico feed copy with the rate> --threats <feeds feed> --rungs <rungs.json> --probe <probe file for the rung> [--ledger <ledger copy>] --cause check --cluster none --run 0 --commit 0 --rung-set-by=check --out <temp file>`
  Rebuilt from each line's own fields, the probe files gave the five ledger lines that then carried a verdict again: the same figure, exposure, cost and verdict. Several hundred runs in all. A second driver, written apart from the first, ran the same landed files again. It got the same three rung figures, confirmed each of the six thresholds at its two boundary rates, and got the resting rung and colour at each count's low, point and high, at both tolerances.
- **The re-run, 15 November.** The loop program and the rungs are platform `e91e5db`, which driftwood pins as `policy/v8.0.1`. ico's feed is `penalty-schema/feed.json` as at `8f4b1c6`, the same file as at `93d1fc8`. The threat feed is feeds 5.1.0, tagged at `489e2fe`. The re-run used the candidate, which differs from the tag only in the words of one basis text; every number is the same. The party file and the namespace file are driftwood's own, at `08ba2d0`: the party file's pin lines changed, the namespace file did not. The ledger is a copy of driftwood's nine lines, fresh for each run. The real ledger was not written.
- One driver ran the re-run. It calls the loop's own `cycle` with a clock it sets, starting at 06:47 UTC on 15 November and one day a cycle, and moves the rung line as the loop does. It was proved three ways. On the old feed, 5.0.1, it gives every number the first run gave, to the penny and to the ninth place. On the old feed it rebuilds all eight ledger lines that now carry a verdict: the same `figure`, `exposure`, `cost`, `verdict`, `rung_to`, `goal`, `unreachable`, `release_ready`, `rows`, `sourced_share`, `weakest_basis`, `serving` and `capabilities`. And 24 single cycles were also run through the same `cycle` command, with the labels `--cluster stand-in` and `--rung-set-by rerun`, every field equal to the driver's line. No second, separate driver was written for the new feed. 3,496 cycles in all.
- The probe files are in the shape of the ledger lines, one for each rung, for a cage that works at that rung. In the re-run each is rebuilt from the last real line that looked at its rung.
- The feed copy carries the rate and the basis kind `counted`. The party copy changes only the tolerance amount, to 430000. Written as `share_of_turnover` 0.005, the loop prints the same tolerance.
- Each rate was run from `isolated`, cycle after cycle, until a cycle made no move and was not release-ready. Three more cycles then checked that none moved. Each threshold was found by halving between 0.000000001 and 1, in steps of 0.000000001.
- **Not run.** No cluster, no workflow, no pin move, no merge and no network. The probe files stand in for a working cage. The web sources were not fetched again: the counts and their checks are the six reports'. ico's four tests were run in the first run only; ico's feed did not change. The other tolerances in `../DECISIONS.md` (GBP 86,000, GBP 860,000, GBP 1,720,000) were not run.

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
