# 79 — The £ inputs are published, sourced and current

Type: task (AFK)
Status: resolved
Blocked by: 75 (resolved)

## Question

The £ engine reproduces its numbers to the last digit and publishes them with no qualifier, from inputs that are editorial, platform-held or legally stale. Under whichever answer ticket 75 Q4 and Q7 give, the following must be true before any £ is shown to an audience:

1. The ICO penalty schema carries a `status` and `final_as_of` per real example. Doorstep Dispensaree is £92,000, confirmed by the Court of Appeal 2024-12-09. Clearview AI's £7,552,800 is under appeal and never collected. The publisher decides the rule ("a penalty under appeal is not a published fine" or "the final figure, not the notice figure"), records it in `rule.yaml`, cuts ico v4.0.0, and the bump propagates by Renovate. The other regimes' examples are audited the same way.
2. Tuppence and ludlow declare `size` and `obligations`. A party with no size is graded amber by the gate, not silently priced at the statutory cap.
3. Every frequency carries a basis: the ICO converter's `DEFAULT_WARN_LEF` becomes a publisher-shipped field with a cited base rate and a stated denominator, or the artefact stops calling the output annualised. Frequency becomes a counting distribution so a loss-free year is possible.
4. The threat register's loss magnitudes move from `platform/feeds/to_fair_scenario.py`'s adopter-keyed table into the feeds publisher's own payload, and the converter into the feeds repo, as ticket 24 decided.
5. Every control weight carries a `basis`, and `verify-penalty-feed.sh` refuses a weight without one.
6. `verify-insurer-quote.sh` prints the implied loss ratio, expected layer loss over premium, on every run and reds above a declared band.
7. The ICO converter applies the decided cap rule, `hi = min(rate × turnover, cap)`, or the statute's rule if the owner prefers it, and its selfcheck asserts the chosen one.
8. `tcor.py` prices a transfer as `(1 + load) × E[loss above deductible]` with the retained part below the deductible as residual.
9. The exposure section records the sum of selected-tier residuals beside the band, so a breach of the aggregate is visible.
10. The artefact states what the number is. If Q4 is (a), `exposure.total` carries "an ordinal, auditable comparison under one perspective; not an expected annual loss", and the deck says the same.

Done = driftwood's, tuppence's and ludlow's `composed/evidence.json` re-render from sourced inputs, the gate names every unsourced input amber, and the FCA and HIPAA converters ticket 24 decided exist or the decision is recorded lapsed.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R1. Findings: pound-engine/PE-01, PE-02, PE-05, PE-06, PE-07, PE-08, PE-10, PE-12, principles/P3-1, scope/F2, completeness C1. The completeness critic's re-run of the production path with corrected fines is at [review-2026-09-02/evidence/completeness/](../review-2026-09-02/evidence/completeness/).

## Comments

**2026-09-02, ticket 75 resolved.** Q4 is (a), delegated: the £ is an ordinal, auditable comparison instrument under one perspective, and every artefact that shows a total says so (item 10 applies). `appetite.tolerance` is one annual-aggregate quantity. The insurer is an illustrative counterparty, and its quote says so. Add a litigation-status field beside `status` and `final_as_of` in item 1. Q7: the adopters are plausible firms, based on studied existing firms where needed; ticket 94 (research) supplies the candidates and item 2 picks under that record. Unblocked.

## Answer

Built 2026-09-09 on `ticket-79-the-pound-inputs` in ico, feeds, platform, insurer and the hub.
Every decision below is **delegated** (ADR-0025) unless it says otherwise; nothing here is a date,
an identity, an authorisation or a real person, and the two figures that ARE money are under
*Waits on the owner*, unsigned.

**Read this first: three of this ticket's own statements were stale, and the measurement is beside
each.** They are corrected in place below rather than argued with.

1. **"`tcor.py` prices a transfer as `premium + deductible`"** — item 8 named `tcor/tcor.py:19`,
   which is a DOCSTRING line. The code was `tcor.py:117-118`:
   `premium = ale_warn * (1.0 + load)` then `out["transfer"] = line(deductible, 0.0, premium)`.
   The defect was worse than the docstring said: the premium was `(1 + load) x E[TOTAL loss]`, so
   the loss below the deductible was charged into the premium AND booked again as the residual.
   Measured on the planted case: `E[loss] GBP 152,526.05 = E[below] GBP 49,776.61 + E[above]
   GBP 102,749.44`; old premium GBP 213,536.46, TCoR GBP 263,536.46; and raising the deductible
   from GBP 1,000 to GBP 80,000 left the premium at GBP 213,536.46 both times.
2. **"the ICO converter applies `hi = min(rate x turnover, cap)`"** — item 7's premise. The code
   was `to_fair_scenario.py:61` `hi = max(cap, 1.2*max(ex), mode)` and `:68-71` scaled the whole
   triple by `rate*turnover/cap`. Neither a min nor a cap: the scale factor runs past 1 for any
   firm bigger than `cap/rate`, so at a turnover of GBP 5,000,000,000 the triple topped out at
   **GBP 104,176,551.72 against a statutory maximum of GBP 100,000,000.00** — a fine the statute
   does not permit. The `min` the ticket proposed is refused with its reason under item 7.
3. **"the FCA and HIPAA converters ticket 24 decided exist"** — ticket 24 decided no such thing.
   Its Q1 to Q4 decide how HIPAA, PCI and FCA read the SIZE facts, all four inside ico's one
   converter, and its own Notes say "`ico/schema/to_fair_scenario.py:47-75` is the only parser of
   the penalty schema" and "One publisher, `ico`, publishes FCA and HHS penalties". The
   separate-publisher question is listed under **"Later, blocked on the above: … whether `ico`
   keeps publishing `fca`, `hipaa` and `pci-dss` or each regulator becomes its own publisher
   party (ticket 21's move, Q3's schema major forces the question)"**. **The lapse is recorded,
   not built** (delegated): building an FCA and a HIPAA publisher today would create two parties
   whose payloads nobody has sourced, when the estate's one penalty publisher already carries both
   regimes, prices both through one converter, and now grades both for finality. What a real split
   needs is the deferred decision, not code. Ticket 24's "Later" list is where it stays.

A fourth, smaller correction: item 1 said v3's fines carry "NO `status` field". True, and so did
majors 1 and 2, and so did every control weight and every frequency — the defect is the whole
payload's, not the two examples'.

### Item by item

**1. Penalty status, `final_as_of` and litigation. Built; the cut waits on the owner.**
`penalty-schema/payload.schema.v4.json` requires `status`, `final_as_of` and `litigation` on every
real example; `penalty-schema/v4/feed.json` carries them; `penalty-schema/rule.yaml` records the
publisher's rule in full and `penalty-schema/bump.yaml` declares `major`.

*The rule, delegated:* **a published fine is the FINAL COLLECTED FIGURE, not the notice figure.**
The reason is this schema's own data: Doorstep Dispensaree's notice was GBP 275,000 and the figure
that stands is GBP 92,000 (Court of Appeal, 2024-12-09) — the notice overstated by 3x; Clearview
AI's GBP 7,552,800 has never been collected; and the DSG penalty ticket 94 studied went
GBP 500,000 -> GBP 250,000 -> set aside -> remitted, with no final figure six years on. Notice
figures are not noisy around the truth, they are biased upward every time.

*Three statuses price or do not, and the third one is the interesting decision.* `final` prices.
`imposed-appeal-unchecked` prices AND says so on every scenario it reaches: the regulator imposed
the figure (a penalty notice, not a notice of intent), no adverse litigation is known to this
repository, and **no tribunal or court register was read**. Everything else — `under-appeal`,
`set-aside`, `not-collected`, `notice-of-intent`, `not-a-penalty`, `unknown` — does not price.
The third value exists because both alternatives were wrong: marking every unverified figure
`final` is the defect this ticket exists to close, and marking them all `unknown` would have left
uk-gdpr higher-tier with no priceable example at all AND would have claimed "we checked and it is
not final", which is equally untrue. `imposed-appeal-unchecked` says the one thing that is true.

*What moved in v4.* Doorstep Dispensaree GBP 275,000 -> **GBP 92,000**, `final`, `final_as_of
2024-12-09`, with the notice figure kept as `notice_gbp`. Clearview AI GBP 7,552,800 ->
`not-collected`, stops pricing. TikTok, Premera, Standard Chartered and TSB -> `unknown`, each
naming what was not looked at, all stop pricing. British Airways and Marriott ->
`imposed-appeal-unchecked`. Starling Bank's FCA final notice of 2024-09-27, GBP 28,959,426, is
ADDED as the one example whose finality a run of this estate actually established (ticket 94).
uk-gdpr/lower-tier consequently prices `lm (92,000.00, 92,000.00, 8,700,000.00)` where v3 priced
`(275,000.00, 3,913,900.00, 9,063,360.00)`.

*Backwards compatibility, derived from the bytes and not from a version string:* a payload in
which NO example carries a `status` predates the field, prices exactly as it always did, and the
scenario says so by name. One where SOME carry it and some do not is refused, naming the example —
a dataset half-checked for finality is worse than one not checked at all, because the checked half
makes the rest look checked too.

**2. Signed sizes for tuppence and ludlow. Not built: it is money. See *Waits on the owner*.**
Verified: neither `party.yaml` carries `size:` or `obligations:`, and both carry only
`appetite.tolerance`. Verified too that the amber the ticket asks for **already exists and already
fires** — `verify/portability/` prints, today, `ludlow publishes no signed size:, so the feed
prices its own served entries say were 'priced at the statutory cap' … are the publisher's
ceiling, not a figure about this institution (ticket 64)`, and proves it rather than asserting it
by printing that ludlow and tuppence price penalty-schema at **exactly GBP 9,039,791.02 each**, the
same number to the penny for two different institutions, which is what a statutory cap looks like.
So item 2 needs no new check; it needs two signed numbers.

**3. A basis for every frequency and every control weight. Built.** `DEFAULT_WARN_LEF = (1, 2, 4)`
stops being a bare default. From payload major 4 the PUBLISHER ships `frequency` per violation
type: a `lef` triple and a `basis` carrying `kind` (`counted | published | editorial`), a
`statement`, a dated `as_of`, a `denominator` and a `could_not_look`. The converter refuses a
frequency with no basis, naming the violation type and where the basis goes. Every control weight
carries the same `basis` shape and `verify-penalty-feed.sh` refuses one without it.

*What the basis actually says, delegated:* `editorial`, with a named could-not-look, not a counted
rate. No run of this repository has counted a regulator's own published enforcement register, and
**neither regulator publishes the denominator** (organisations in scope of that violation type), so
a rate cannot be derived from anything this estate holds. Writing a counted-looking number would be
the exact defect the ticket is about. What would close it is printed on the feed: a fetch that
counts actions per year from the register, plus a stated population in scope, both dated.

*The floor moves to 0* (delegated): v4 publishes `[0, 2, 4]` where the converter defaulted to
`(1, 2, 4)`. A loss-free year must be possible and `(1, 2, 4)` made one impossible — a regulator
does not fine every controller every year. Open limit, printed: `fair.py`'s PERT is a continuous
distribution, so "a counting distribution" is expressed here as a zero floor; a true Poisson or
negative-binomial frequency is a change to `fair.py` and is not in this ticket.

**4. Threat magnitudes into the publisher, and the converter with them. Built; the cut waits on
the owner.** `platform/feeds/to_fair_scenario.py`'s `THREAT_LM_GBP` was an ADOPTER-KEYED table in
the SUBSCRIBER's repository: the platform held a signed-looking number about each institution that
no publisher had published, that no subscriber could re-derive, and that a fourth adopter could not
have obtained at all. From `threat-register` payload major 3 the number is
`institutions.<name>.lm_gbp` with an `lm_basis` (and `lef_basis` beside it), and the converter that
reads it is `feeds/threat-register/to_fair_scenario.py` — the publisher's own repository, and the
FIRST place `composition.py`'s `_converter()` looks.

*The numbers do not move* (delegated): major 3's magnitudes are byte-for-byte platform's own table.
Re-homing a number and re-pricing it in one release makes it impossible to say which moved the GBP.
The feeds selfcheck asserts it against major 2 directly.

*Platform keeps a fallback and says what it is.* A composition against a feeds checkout pinned
before the move finds no converter in the publisher's tree and falls back to platform's; that copy
now reads `lm_gbp` too, its table is renamed `FROZEN_LM_GBP` and documented as frozen, and
**platform's own selfcheck runs both modules over every published payload and asserts they agree
byte-for-byte on all 9 (version, institution) scenarios** — so the fallback cannot drift from what
the publisher ships. A pre-major-3 payload prices at the frozen magnitude and every scenario says
`MAGNITUDE UNSOURCED: … a named could-not-look … never a bare number`.

*Ticket 45 stays green, and it is measured, not hoped.* `composition.py`'s selfcheck used to assert
`converter_from == "platform"` as a constant; it now DERIVES it — a feeds tree that ships the
converter must record `feeds`, one from before the move must record `platform` — so the record and
the disk agree either way. And the hub's `verify/portability/` gained a leg that replays the REAL
moved converter (not a fixture shaped like one): see *Red first (c)*.

**5 and 7 are one item, and this Answer treats them as one.** The build brief numbered the ticket's
list differently from the ticket: brief item 5 is the ticket's item 7 (the cap rule), and the
ticket's item 5 (a basis on every control weight) is inside brief item 3. Brief item 7 folds into
brief item 5, as it invited.

**7. The cap rule. Built.** *Decision, delegated:* **the sized triple is clamped at the statutory
maximum, `max(cap, rate x turnover)` — the statute's own "whichever is higher" — and the ratio
scaling shapes the published evidence only INSIDE that ceiling.** UK GDPR Art 83(4)/(5) and DPA
2018 s157 set the maximum at the greater of the fixed sum and the percentage of turnover. The
`min` the ticket proposed takes the LESSER, which contradicts the statute in the other direction:
it would price a GBP 5bn-turnover firm at the GBP 8.7m cap where the statute allows GBP 100m. The
clamp is the smallest change that makes the converter unable to print a fine the regulator could
not impose, and it moves no adopter's price today (driftwood's sized `hi` under the v3 payload is
GBP 1,791,836.69 against a statutory maximum of GBP 8,700,000 — the first cut of this Answer
wrote GBP 1,791,873, two digits transposed, review F10; the claim it supports is unchanged).

**6. The implied loss ratio. Built.** `insurer/pricing/quote.py` gains `implied_loss_ratio()` and
`verify-insurer-quote.sh` prints it on EVERY run, before the staleness check that used to `continue`
past it, and reds outside a band each `terms/<adopter>.yaml` declares. Today: driftwood 22.8571,
tuppence 25.6410, ludlow 16.4609, band 5.00–50.00.

*What the number is, said every time it prints* — because a check that borrows the name "loss
ratio" without the thing would be this estate's own defect class. A true loss ratio wants
`E[loss in the layer]`; the insured signs a POINT TOTAL and no aggregate loss distribution exists,
so the numerator is the LAYER: the insured's ordinal, auditable exposure between attachment and
limit. And it is an **identity** — `layer / premium == 1 / (rate x (1 + load))` exactly — so the
ratio carries no information about the insured at all. That is what makes it worth banding: it is a
statement about the carrier's own two knobs. Above the band the premium is a token sum against the
layer it stands behind; below it the premium approaches the whole ordinal exposure, which is
prepayment and not cover. *Band `5.0–50.0`, delegated*, declared per adopter beside `rate` and
`load`, which are already this carrier's stated calibration knobs; the owner may overrule it. It
becomes an actuarial ratio at formula 2.0.0, when the exposure carries a distribution.

**8. tcor's transfer formula. Built.** *Decision, delegated:* the deductible **partitions one loss
distribution**. `premium = (1 + load) x E[max(L - D, 0)]`, `residual = E[min(L, D)]`, and the two
sum to `E[L]` by construction, so no pound is counted twice and none falls between them. The
deductible is a CONTRACT TERM; the residual is what that term costs. On the planted case TCoR goes
GBP 263,536.46 -> GBP 193,625.82, and a deductible raised from GBP 1,000 to GBP 80,000 now takes
TCoR from GBP 213,136.46 to GBP 182,251.09 instead of leaving the premium unmoved. A deductible
that cannot make cover cheaper is not a deductible, and the four-move crossover this module exists
to compute was rigged against transfer.

**9. The aggregate beside the band. Built.** `appetite.tolerance` is ONE annual-aggregate quantity
(ticket 75 Q4, folded), but the ladder picks a tier per LINE against that one number. Measured on
driftwood the day this was written: three priced lines, a band of GBP 40,000, and the residuals
their selected tiers leave summing to **GBP 87,387.45** — a 2.2x breach of the declared aggregate
that no signed artefact stated anywhere. `aggregate_section()` now renders it beside the
attachment: the per-line residuals with their tiers, the tolerance, a plain `breaches_band`, and
any line carrying no selected tier NAMED rather than silently dropped. **It is not a refusal**:
there is no gate (ADR-0020, ticket 75 Q5), a breach is priced and shown.

**10. The ordinal statement on every total. Built, in the COMPOSER.** `ORDINAL_STATEMENT` is ticket
75 Q4's own words — *"an ordinal, auditable comparison under one perspective; not an expected
annual loss"* — written onto every exposure section `composition.py` renders, with an
`ordinal_basis` saying what AUDITABLE means here (reproducible from the signed inputs named beside
it) and what it does not mean (several of the frequencies and magnitudes under it are editorial
bands carrying a named could-not-look, so the total compares versions and pins and is not a number
to reserve against). `compose/handbook.py` renders both, and the aggregate, and records a NAMED
ABSENCE where an artefact states a total and carries no statement — it renders what the artefact
says and never a sentence of its own authority. **No adopter's `composed/` tree was regenerated**:
the brief forbids composing from an untagged branch, so every adopter gains both sentences from the
first composition under the owner's next signed platform tag, and `verify/pound-seam/` says exactly
that per adopter, naming the pin.

### Red first, at each seam

Each red was committed before the logic that greens it (ico `7a34cf1`, platform `6cc7b1d` and
`0a615fa`).

- **(a) a fine with no `status`.** RED: `FAIL (a) an example with no 'status' beside one that has
  it is refused by name: an example with no 'status' beside one that has it priced anyway:
  lm_triple returned (275000.0, 3913900.0, 9063360.0)`. GREEN: `ok  (a) an example with no
  'status' beside one that has it is refused by name`, and in the feed check
  `FAIL: uk-gdpr/higher-tier British Airways carries no 'status', so a penalty under appeal prices
  as if it were final -- the defect eco-system ticket 79 item 1 exists to close` when the field is
  removed.
- **(b) a frequency or a weight with no basis.** RED: `FAIL (b) a published frequency with no
  'basis' is refused, naming where the basis goes: a published 'frequency' of [0, 2, 4] events/yr
  with NO 'basis' was used to annualise the loss; its basis belongs on
  regimes.uk-gdpr.violation_types.lower-tier.frequency.basis in the ico penalty-schema payload`.
  GREEN: `ok  (b) a published frequency with no 'basis' is refused, naming where the basis goes`.
  On a weight, with the basis removed: `FAIL: uk-gdpr/lower-tier nist/pl-2 publishes a weight of
  0.3 with no 'basis' -- a bare number. Its basis belongs beside it in the payload (eco-system
  ticket 79 item 3)`.
- **(c) the moved converter, replayed.** GREEN: `OK (c) the MOVED converter
  (feeds/threat-register/to_fair_scenario.py) replays its recorded invocation
  'to_fair_scenario.py threat <payload> driftwood' in a directory holding nothing but itself and
  the vendored payload -- no publisher clone, no platform, no hub -- and returns the very scenario
  it was priced from (sha256 6046699614c5), pricing lm [1000.0, 4000.0, 9000.0] at lef
  [2.0, 4.0, 9.0]`. That digest is the one `composition.py` itself records in `PROVENANCE.json`
  (`"scenario_sha256": "6046699614c5d4ebc35e0bb00b3c521d1c4e5ab07930527cdc595c745d2a008c"`).
  WRONG INVOCATION, named: `FAIL: ado's vendored converter for threat-register@v2 replayed
  'to_fair_scenario.py threat <payload> tuppence' standalone and returned a scenario digesting to
  7e41008d87c4, and the record it was vendored with says 6046699614c5 — the same command over the
  same payload gave a different answer, so what this copy re-derives is not what was priced`.
- **(d) the cap rule and the tcor formula, both numbers printed.** Cap rule RED: `FAIL (d) the
  sized triple never tops the statutory maximum max(cap, rate x turnover): the sized loss magnitude
  tops out at 104176551.72 GBP, above the statutory maximum of 100000000.00 GBP (UK GDPR Art 83:
  the GREATER of the fixed sum 8700000.00 and 0.02 x turnover 5000000000.00) -- the converter
  prices a fine the statute does not permit`; GREEN at GBP 100,000,000.00. tcor RED: `FAIL (d) a
  transfer premium is (1 + load) x E[loss above the deductible]: the transfer premium is GBP
  213536.46, which is (1 + 0.40) x E[TOTAL loss] GBP 152526.05. The ticket's rule is (1 + load) x
  E[loss ABOVE the deductible] = GBP 143849.21, so the GBP 49776.61 of loss below the deductible is
  charged into the premium AND booked again as the residual`; and `FAIL (d) a higher deductible
  buys a cheaper premium: raising the deductible from GBP 1,000 to GBP 80,000 left the premium at
  GBP 213536.46 and GBP 213536.46 -- it did not fall`. GREEN: both `ok (d)`, TCoR GBP 193,625.82.
- **(e) a total with no ordinal statement.** RED: `FAIL (e) exposure.total of 3704381.74 GBP
  carries no 'ordinal' statement: nothing on the artefact says the number is an ordinal, auditable
  comparison under one perspective and not an expected annual loss (eco-system ticket 79 item 10,
  ticket 75 Q4)` and `FAIL (e) the exposure section records no 'aggregate': driftwood's 3 priced
  lines each picked a tier against a band of 40000.00 GBP, and the sum of the residuals those tiers
  leave is 87387.45 GBP -- a breach of the one annual aggregate the appetite declares is not
  visible anywhere on the artefact (eco-system ticket 79 item 9)`. GREEN: `OK (e) driftwood's
  exposure section carries the ordinal statement on its total and the aggregate of its
  selected-tier residuals beside the band`.

### Which check grades what

| item | check |
| --- | --- |
| 1, 3, 7 | ico `verify-penalty-feed.sh` sections 9, 10, 11; `schema/to_fair_scenario.py selfcheck` |
| 1 (the cut) | ico `.github/scripts/declared-bump-gate.py --tree`: `OK: declared bump 'major' == computed bump 'major' (v3.0.0 -> v4.0.0)` |
| 4 | feeds `verify-feeds.sh` (new section) and `threat-register/to_fair_scenario.py selfcheck`; platform `feeds/to_fair_scenario.py selfcheck` (agreement leg); hub `verify/portability/` `_t79_moved_converter` |
| 6 | insurer `verify-insurer-quote.sh` (new 4b) and `pricing/quote.py selfcheck` |
| 8 | platform `tcor/verify-tcor.sh` and `tcor/tcor.py selfcheck` |
| 9, 10 | platform `compose/composition.py --selfcheck` (hard refusal); hub `verify/pound-seam/` leg 11 (the served half, a named could-not-look until the owner's tag) |
| 2 | hub `verify/portability/` — already fires; it waits on two signed numbers, not on code |

### Waits on the owner

1. **Cut ico `v4.0.0`.** Dispatch `.github/workflows/cut-release.yml`. `bump.yaml` declares `major`
   and the ticket-103 gate computes `v3.0.0 -> v4.0.0` against it. Nothing was tagged here.
2. **Cut feeds `threat-register/v3.0.0`.** Same shape; `bump.yaml` declares `major`. Nothing
   re-prices when it lands, because major 3's magnitudes ARE the numbers platform's table held.
3. **A signed platform tag**, and each adopter's pin moving to it. Until then no adopter's
   `composed/` tree carries the ordinal statement, the aggregate, or the corrected ico v4 inputs;
   `verify/pound-seam/` names the pin each adopter is on and says so. **No `composed/` tree was
   regenerated by this ticket.** When that recomposition happens, the exposure section gains keys,
   so `pricing/quote.py`'s `exposure_sha256` moves and a **re-quote PR is due** for all three
   quotes — the same mechanism that already reports driftwood's exposure as re-signed today.
4. **`size:` and `obligations:` for tuppence and ludlow — MONEY, so unsigned here.** Ticket 94's
   record supplies the candidates and their sources; these are the figures it recommends, and the
   owner signs or replaces them:
   * **tuppence -> Starling Bank Limited** (ticket 94's cleanest candidate: an FCA Final Notice of
     GBP 28,959,426, 2024-09-27, final, collected, no appeal). Turnover GBP 414.8m–452.8m (two
     primary sources differ), ~3.6m customers, 2,762 employees, a Board-approved risk-appetite
     framework. `obligations: [uk-gdpr, fca, pci-dss]`.
   * **ludlow -> Anthem, Inc.** Revenue USD 84,194m (SEC 10-K FY2016), 39.9m members, ~53,000
     employees; HHS OCR USD 16,000,000, 2018-10-15, final and collected.
     `obligations: [hipaa, uk-gdpr]`.
   The figures are not written into either `party.yaml` here, and neither adopter repository was
   touched. What signing them unblocks: ticket 74's likeliest real mover — with a signed turnover
   the penalty-schema line stops pricing at the publisher's statutory cap, the two identical
   GBP 9,039,791.02 figures separate, and `verify/portability/`'s two standing could-not-looks
   close. Note the currencies differ (Anthem's record is USD) and the FX bridge is signed and
   working, so a USD size is priceable.
5. **Confirm or replace the implied-loss-ratio band `5.0–50.0`** in `insurer/terms/*.yaml`. It is a
   ratio, not money, and it is decided here; it is listed because it is a carrier's commercial
   judgement.

### Not done, and why

* No tag, no dispatch of `cut-release`, no `uses:` step and no job added to any workflow.
* No adopter's `composed/` tree regenerated (the brief forbids composing from an untagged branch),
  and no adopter repository touched at all.
* FCA and HIPAA converters: the lapse is recorded above against ticket 24's own "Later, blocked"
  list, not built.
* A true counting distribution for frequency waits on `fair.py`; the zero floor is what is
  reachable here, and the limit is printed on the feed.
* `tests/test_misuse.py::test_the_four_rows_grade_against_this_checkout` is red in this working
  copy and it is not this ticket's: the shared `.estate-clone/platform` checkout is at `bbda376`,
  behind `origin/main` `b6d5045`, so it carries no `price_supersede` — the row grades a stale
  clone. `grep -c price_supersede` is 3 against origin/main and 0 against the shared checkout.


## Review fixes, 2026-09-09

A Fable review returned CHANGES REQUESTED: three blocking, six minors, six lows and notes. Every
one is answered below, changed or recorded, with the measurement beside it. The paragraphs above
are corrected in place where they were wrong; this section says what moved and why.

### The materiality the review asked to be stated plainly

**Composition prices exactly one regime and one violation type: `uk-gdpr/lower-tier`**
(`composition.py:2200-2201`, `ICO_REGIME` / `ICO_VIOLATION_TYPE`). So of the eleven fines this
payload now grades, **nine never reach an adopter**, and `imposed-appeal-unchecked` — the status
this ticket invented — was invented for figures in tiers composition never reads. The one graded
fine that reaches money is Doorstep Dispensaree's, and it moves driftwood's regime line, derived
here with the estate's own `fair.py` over the two payloads at driftwood's signed turnover of
GBP 86,000,000:

| payload | lef | lm | ale |
| --- | --- | --- | --- |
| v3 | (1, 2, 4) | (54,367.82, 773,782.53, 1,791,836.69) | **1,787,177.08** |
| v4 | (0, 2, 4) | (18,188.51, 18,188.51, 1,720,000.00) | **607,314.15** |

A fall of **GBP 1,179,862.93/yr**, once ico v4.0.0 is cut and driftwood's pin moves. Both the
finality correction and the zero frequency floor are in that move.

### F1 (blocking) — a priced fine needed no source. Fixed.

The review was right and the reproduction is exact. Appending
`{org: 'Invented Ltd', fine_gbp: 5000000, status: 'final', final_as_of: '2025-01-01'}` with no
`source` printed `ok  uk-gdpr/lower-tier Invented Ltd final 2025-01-01`, moved the priced mode from
GBP 92,000.00 to **GBP 2,546,000.00** — 27x — and the run exited PASS. The whole of item 1 graded
FINALITY and nothing graded SOURCING, so the map line's "every figure the £ engine prints now says
what it rests on" was not derived. Fixed three ways: `source` is in
`payload.schema.v4.json`'s `required` list with `minLength 1`; the converter refuses a PRICED
example with no source, by name; and `verify-penalty-feed.sh` section 9 prints each example's
source beside its status and refuses a priced one without it. Every scenario now also prints
`Priced from, with what each rests on: …` per figure.

RED, on the fixed check, with both of the review's plants:
`FAIL: uk-gdpr/lower-tier Invented Ltd carries a figure and a status of 'final' but NO `source`,
so it prices from a number nobody can trace back to a regulator's own instrument (eco-system
ticket 79 review F1)` and the same line for `fca/systems-and-controls-failure Starling Bank
Limited` with its `source` deleted. In the converter:
`FAIL (f1) an example with a status and no source is refused by name: an example with a `status`
and NO `source` priced: lm_triple returned (92000.0, 2546000.0, 8700000.0)`.

### F2 (blocking) — the one figure that moves money cited the ticket, not a source. Fixed.

Also right, and worse than "uncited": the served artefact attributed the reduction to the **Court
of Appeal**, and the estate's own sourced record says otherwise. `REVIEW-2026-09-02.md`, citing
Hunton and DataGuidance, records that the **First-tier Tribunal** cut it to GBP 92,000 in **2021**
and the Court of Appeal in **2024** dismissed the further appeal. No source this estate holds
carries a day, so `final_as_of: '2024-12-09'` was a claim about a court record nobody here has
read — inside a payload whose own `imposed-appeal-unchecked` definition declared that no register
is read. Fixed:

* `final_as_of` accepts `YYYY`, `YYYY-MM` or `YYYY-MM-DD`, and Doorstep's is **`2024`** — the
  precision the source supports. Precision is part of the claim, and a rounder date is the honest
  one here, not a sloppier one.
* `source` names the First-tier Tribunal, the year, the Court of Appeal's dismissal, the year, and
  cites `REVIEW-2026-09-02.md` **with the Hunton and DataGuidance URLs** — the way Starling and
  Anthem cite ticket 94.
* `litigation` says "`fine_gbp` is the figure that stands" (it said "is what was imposed and
  stands"; GBP 275,000 is what was imposed) and names the BASIS: published legal reporting
  recorded in this estate, not a register queried here.
* The `imposed-appeal-unchecked` definition now says no register was read **for that example**, so
  it is a statement about that figure and not a blanket one the payload then contradicts.
* Clearview's entry gains the estate's own fuller sourced record too: set aside 2023, reinstated on
  jurisdiction by the Upper Tribunal in October 2025, remitted, never collected.

### F3 (blocking) — `breaches_band` compared two currencies. Fixed.

Reproduced: a tolerance of `{amount: 40000, currency: 'USD'}` against a GBP total returned
`breaches_band: true`, and the handbook rendered "70,000.00 GBP against a tolerance of 40,000.00
USD -- BREACHES". Its own neighbour does the opposite and says why. And it is reachable on this
ticket's own next step: the ludlow candidate under *Waits on the owner* has a USD record.

Fixed by converting through the signed FX feed — `_converted()`, the same helper every other
crossing amount in this module uses — with `tolerance_in_reporting_currency` printed beside the
raw tolerance, and by refusing to give a verdict at all where no rate can be read:
`breaches_band: None` plus a named `could_not_look`. `handbook.py` prints `NO VERDICT — <reason>`
instead of a comparison. Measured, both ways:

```
OK (F3) an appetite declared in USD against a GBP exposure is CONVERTED through the signed FX feed
(40,000.00 USD = 31152.65 GBP at 2026-08-15, breaches_band=True), and with no rate for the date
there is no verdict at all: breaches_band=None and a named could-not-look, never a comparison of
two currencies. (F8) a book whose every line is untiered still returns a section, naming all 3.
```

### Minors

* **F4, changed.** The finality rule was non-uniform and the non-uniformity tracked the pricing
  outcome: ICO notices priced, FCA final notices did not, and the two litigation notes described
  the same posture. Now ONE rule, written into `rule.yaml`: a regulator's own **concluding
  instrument** — an ICO monetary penalty notice, an FCA Final Notice, an HHS OCR resolution
  agreement — with no adverse litigation known here and no register read for it is
  `imposed-appeal-unchecked`, whichever regulator issued it. Standard Chartered, TSB, TikTok and
  Premera move to it; `unknown` now applies to nothing in this payload, because every example
  names the instrument it came from. Nine of eleven figures price; `uk-gdpr/lower-tier`, the only
  tier composition reads, is unchanged by this.
* **F5, changed.** A `notice_gbp` below its own `fine_gbp` is refused in section 9, naming both:
  `FAIL: … carries a notice figure of 50,000 below the figure that stands, 92,000. …rule.yaml's
  rule rests on notice figures being biased one way, UPWARD; a notice below its own final figure
  is either a transposition or a case that rule does not describe`.
* **F6, changed.** `implied_loss_ratio()` returns `band_source` and the line prints it. With
  `loss_ratio_band` deleted from `terms/tuppence.yaml` it now says
  `(band 5.00-50.00, from pricing/quote.py DEFAULT_LOSS_RATIO_BAND -- this carrier's own terms
  file declares no 'loss_ratio_band')` where it used to claim the terms file regardless.
* **F7, changed as far as this ticket may.** The raw `assert mine == theirs` tuple dump is now a
  named refusal listing the fields that differ; proved by mutating the publisher's own
  `FROZEN_LM_GBP` 9,000 → 9,999, which reds with
  `…institutions.driftwood: this FALLBACK copy and the publisher's own threat-register converter
  no longer agree… Fields that differ -- deny: this copy says {…9000.0}, the publisher's says
  {…9999.0}`. **A CI job was NOT added**: the build brief forbids adding a `uses:` step or a job
  to any workflow. So the line now says what the guarantee rests on instead — "No workflow in this
  repository runs it and no CI job clones feeds beside platform, so nothing automated asserts the
  agreement today" — and the absent-checkout branch says plainly that nothing checked it on that
  run. A platform CI job that checks out feeds at the pinned tag is the right fix and is left for
  a ticket that may touch workflows.
* **F8, changed.** `aggregate_section` returned `None` when every line was untiered, throwing away
  the names in the one case where they matter most. It now returns the section with a `0.0` total
  and `not_tiered` populated.
* **F9, changed, both halves.** `pound_seam.py` no longer substring-matches the composer's source
  and then claims behaviour — a comment would have satisfied it. It IMPORTS the composer and RUNS
  `exposure_section` over a synthetic two-line book, then reads the keys off what comes back:
  `PASS: the composer was RUN, not read: exposure_section over a synthetic two-line book (100.00 +
  200.00 GBP, both at tier 'baseline', against a 1.00 GBP band) came back carrying the ordinal
  statement and an aggregate of 210.00 GBP with breaches_band=True`. And composition's `OK (e)`
  now prints the aggregate, the tolerance and `breaches_band`, which only its red text used to.

### Lows and notes

* **F10, corrected.** GBP 1,791,873 does not reproduce; the derivation gives **1,791,836.69**, two
  digits transposed. Corrected above. The claim it supports — that the clamp moves no adopter's
  price today — is unchanged.
* **F11, changed.** Three docstring summary lines carried the names their bodies disclaim, which is
  the class this ticket corrected three of in other people's code. `quote.py`'s "Expected layer loss
  over premium" is now "The ORDINAL exposure inside the layer over the premium", saying that it is
  what item 6 asked for and is deliberately not called that; `verify-insurer-quote.sh`'s header 4b
  likewise; and `to_fair_scenario.py`'s "Only a penalty whose status is `final` enters the loss
  magnitude" now says TWO statuses price and what the second one admits.
* **F12, changed.** The replay computed its own digest, wrote it into the record it replayed
  against, and printed it — a circle proving the converter is a function, not that it re-derives
  the signed price. The digest is now held to the CONSTANT
  `6046699614c5d4ebc35e0bb00b3c521d1c4e5ab07930527cdc595c745d2a008c`, copied from platform's own
  `PROVENANCE.json` and named as such; a converter change that moves the price now SKIPs with both
  digests rather than quietly re-baselining.
* **F13, changed.** A REWORDED ordinal sentence used to SKIP saying "carrying no `ordinal`", which
  is the same class of wrong sentence the leg exists to catch. Absent and different are now
  distinguished: absent is the could-not-look, different is a FAIL naming both strings.
* **F14, recorded, against item 2's signing.** The clamp turns `uk-gdpr/higher-tier` into a POINT
  estimate above a turnover of `cap/rate` = GBP 17,500,000 / 0.04 = **GBP 437,500,000**, where mode
  and hi collapse. Measured: T = GBP 400,000,000 gives (11,611,428.57, 16,822,857.14,
  17,500,000.00); T = 437,500,000 gives (12,700,000.00, 17,500,000.00, 17,500,000.00); T =
  452,800,000 (the tuppence candidate's upper turnover) gives (13,144,137.14, 18,112,000.00,
  18,112,000.00). Both candidate sizes under *Waits on the owner* land above that line. It is not
  wrong — the statutory maximum IS a ceiling and a firm that large sits on it — but the owner
  should know that signing either size makes that tier's mode and hi one number. Composition does
  not read higher-tier, so nothing prices differently today.
* **F15, recorded, not changed.** `portability.py` treats any unrecognised `argv[1]` as `check`,
  and ico's converter raises a bare `KeyError` when handed a whole envelope instead of a payload.
  Neither is reachable from the gate as it runs (the wrapper passes `check` or `selfcheck`;
  composition always unwraps the envelope before calling a converter), and both are argument
  handling in code this ticket did not otherwise open. Named here so the next reader does not have
  to rediscover them.

Map line: **[79 — The £ inputs are published, sourced and current](issues/79-the-pound-inputs-are-published-sourced-and-current.md)** — every figure the £ engine prints now says what it rests on or names what could not be looked at. ico payload major 4 grades every published fine for finality (`status`, `final_as_of`, `litigation`): the publisher's rule is the FINAL COLLECTED FIGURE, so Doorstep Dispensaree becomes the GBP 92,000 the Court of Appeal confirmed on 2024-12-09 and Clearview AI's uncollected GBP 7,552,800 stops pricing, taking uk-gdpr/lower-tier from `(275,000.00, 3,913,900.00, 9,063,360.00)` to `(92,000.00, 92,000.00, 8,700,000.00)`; `DEFAULT_WARN_LEF = (1, 2, 4)` becomes a publisher-shipped `frequency` with a dated basis, a stated denominator gap and a zero floor, and a frequency or a control weight with no basis refuses by name. The threat register's loss magnitudes leave the SUBSCRIBER's adopter-keyed table for the publisher's own payload (major 3) and the converter goes with them, unchanged, so the move re-homes the numbers without re-pricing them; the hub replays that moved converter standalone to the digest composition recorded (sha256 6046699614c5) and names a wrong invocation by both digests. The cap rule is the statute's — the sized triple is clamped at `max(cap, rate x turnover)`, where the old arithmetic printed GBP 104,176,551.72 against a statutory maximum of GBP 100,000,000.00 — and `tcor`'s transfer partitions one loss distribution at the deductible instead of charging the retained part twice (GBP 263,536.46 -> GBP 193,625.82). The composed exposure section states what its number IS, in ticket 75 Q4's own words, and carries the aggregate of its selected-tier residuals beside the band, which showed driftwood breaching its GBP 40,000 tolerance at GBP 87,387.45 with nothing on any signed artefact saying so. Three cuts and two signed sizes wait on the owner; no `composed/` tree was regenerated.
