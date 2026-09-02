# Assessment — the £ engine's economic validity

Auditor pass, 2026-09-02. Citable run: `TRUTH 2026-09-02T10:11Z run=21 ... pass=57 fail=7 skip=18 excluded=2 total=84`.

Unit paths below are the fresh default-branch clones at
`/private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/8c6523c6-66de-4c91-94ed-4ceff16a6a76/scratchpad/units/<unit>/…`,
abbreviated `units/<unit>/…`. Hub paths are relative to
`/Users/cns/httpdocs/controlplane/policy-as-versioned-flux`. Captures quoted from
`git -C <hub> show origin/main:talk/captures/<file>`.

---

## 0. What the estate is required to do with the £

The 2022 thesis makes **no £ claim at all**. `research/03-blogs-thesis.md` mentions
"risk" only as rationale metadata (`:80-83`, `:210`); grep for `£|cost|price|insur|actuar|FAIR`
returns four hits, none of them a pricing claim. The £ is entirely a NORTH-STAR addition.

`NORTH-STAR.md:32` (principle 3) is the whole contract:

> **One £ currency, proportionate to the org.** Every impact and every candidate response is
> priced in one currency so a pay rise, a hardening control, a cage tier, an insurance transfer
> and a strategic play are **comparable**. The price is **proportionate to the organisation**:
> its turnover, its customers, its regulators, its declared appetite. Regulator penalties enter
> as published schemas applied to the adopter's own size.

The operative words are **comparable** and **proportionate**. NORTH-STAR nowhere asks for a
defensible expected annual loss, a calibrated frequency, or an actuarially fair premium. This
matters for grading: several things a risk quant would call fatal are, against this ambition,
either out of scope or already owned as ponytails. I have graded them accordingly and said so.

`NORTH-STAR.md:22` also records that the insurer row "*Does not exist yet*" as of ratification —
so the insurer's arithmetic is new work built after the ambition was written, and is fair game.

---

## 1. Reproducing three published numbers by hand

All three reproduce exactly. This is the single strongest fact in this dimension.

### 1.1 driftwood's uk-gdpr exposure — £1,787,177.0751717847

Inputs, all signed:

* `units/ico/penalty-schema/v3/feed.json` → `regimes["uk-gdpr"].violation_types["lower-tier"]`:
  `formula = {type: pct_of_global_turnover, rate: 0.02, cap_gbp: 8700000}`,
  `real_examples_gbp = [Clearview 7,552,800; Doorstep Dispensaree 275,000]`.
* `units/driftwood/party.yaml` → `size.turnover = {amount: 86000000, currency: GBP}`, `as_of 2026-06-30`.
* `units/ico/schema/to_fair_scenario.py:47-72` (`lm_triple`) and `:38` (`DEFAULT_WARN_LEF = (1, 2, 4)`).
* `units/platform/fair/fair.py:96-148` (`pert`, `simulate`), `SEED=42`, `ITERATIONS=10_000`.

Hand arithmetic (I re-implemented `pert`/`simulate` from their docstrings rather than importing
them, so this is an independent re-derivation, not a tautology):

```
unsized triple  = (275,000, median[7,552,800; 275,000] = 3,913,900, max(8,700,000, 7,552,800×1.2, mode) = 9,063,360)
scale           = rate × turnover / cap = 0.02 × 86,000,000 / 8,700,000 = 0.19770114942528735
sized triple    = (54,367.816091954024, 773,782.5287356322, 1,791,836.6896551724)
ALE(lef=(1,2,4), seed 42, n=10,000) = 1787177.0751717845
published        composed/evidence.json prices[0].amount = 1787177.0751717847
```

Match to 2 ulp (float-order difference only). Frequency draw distribution over the 10,000
simulated years: `{1: 1188, 2: 6055, 3: 2674, 4: 83}` — mean 2.1652 events/yr, **no zero-loss
years at all**.

### 1.2 the insurer's driftwood premium — £113,403.30

Inputs: `units/driftwood/composed/HEADER.yaml` `exposure` (total 3,704,381.737952101;
attachment 40,000; controls pl-2 536,153.1225515354, ra-3 536,153.1225515354) and
`units/insurer/terms/driftwood.yaml` (`limit 3,000,000`, `rate 0.035`, `load 0.25`,
`exclusions: [{regime: uk-gdpr, control_ids: [pl-2, ra-3]}]`).

Formula `units/insurer/pricing/quote.py:186-193`:

```
excluded = 536,153.1225515354 × 2      = 1,072,306.2451030708
insured  = 3,704,381.737952101 − …     = 2,632,075.49284903
layer    = min(max(insured − 40,000,0), 3,000,000) = 2,592,075.49284903
premium  = round(2,592,075.49284903 × 0.035 × 1.25, 2) = 113,403.30
```

Matches `units/insurer/quote/driftwood/v1/feed.json` and `driftwood/composed/evidence.json`
prices[2].amount exactly.

### 1.3 the twin's loss magnitude — [192000.0, 384000.0, 800000.0]

`units/driftwood/twin/orgs/driftwood/perspectives/driftwood.yaml`:
`checkout-revenue.amount = 3,200,000` (= 86,000,000 × `share_of_turnover` 0.1488372093023256 ÷
`periods_per_year` 4 = one quarter's checkout revenue).
`units/driftwood/twin/orgs/driftwood/edges/cart-pii-loss-cuts-checkout-revenue.yaml:7`:
`elasticity: {min: 0.06, mode: 0.12, max: 0.25}`.
`emit-forward-intel.py` `lm = [base × elasticity[k] for k in (min, mode, max)]`
→ `[192000.0, 384000.0, 800000.0]` — byte-identical to
`units/driftwood/twin/forward-intel/v1/feed.json`.

Annualised in `composition.py:1745-1752` with the borrowed `threat-register` lef `[2,4,9]`
(mean 4.5/yr) → £1,897,646.11, matching prices[3].amount.

**Verdict on traceability: the arithmetic is real, deterministic and re-derivable from signed
artefacts by a third party. That is a genuine, unusual achievement and I want it on the record
before the criticism starts.**

---

## 2. Findings

### F1 (critical) — the insurer's premium is 1/22 of the expected loss on its own layer

Computed with the estate's own engine, on the estate's own signed numbers. I simulated
driftwood's three exposure lines at their published triples, summed them year by year (the
"fuller shape" `composition.py:1894-1901` names as its own upgrade path), applied the terms'
exclusion and layer, at n=200,000:

```
mean of summed annual loss     = 3,696,478   (signed total: 3,704,381.74 — the sum-of-means agrees)
mean insured (less pl-2/ra-3)  = 2,627,358   (signed: 2,632,075.49)
E[loss in the 3,000,000 xs 40,000 layer] = 2,470,722
premium charged                = 113,403.30
implied loss ratio             = 2,179 %
burn cost as share of limit    = 82.4 %
```

The carrier has written a layer that, on the insured's own signed numbers, burns 82% of its
aggregate limit **in expectation, every year**, and charged 3.8% rate-on-line for it. The same
shape holds for the other two: `talk/captures/.estate-clone_insurer_verify-insurer-quote.out`
records tuppence's layer clamping at the full £5,000,000 limit for a £195,000 premium, and
ludlow's at £4,000,000 for £128,862.17.

The code owns *half* of this (`quote.py:31-38`: "`layer * rate` is a rate-on-line … NOT the
expected loss between attachment and limit"). What it does not own, and what nothing in the
estate grades, is the **magnitude**: the ponytail reads as a refinement, and it is a factor of
22. Two signed artefacts in the same estate — driftwood's exposure and the insurer's quote —
cannot both be believed as £ quantities.

**Remedy (smallest honest one):** state on the quote payload the implied loss ratio against the
signed exposure, and let it be red. Either the rate is wrong or the exposure is wrong; the
estate should say which it thinks, rather than publishing both.

### F2 (critical) — the frequency that annualises every number has no empirical basis, and cannot produce a loss-free year

`units/ico/schema/to_fair_scenario.py:38`: `DEFAULT_WARN_LEF = (1, 2, 4)   # plausible regulatory-incident frequency, events/yr`.
The docstring at `:19-22` is honest ("ponytail: a flat editorial per-regime warn-LEF"), and
`composition.py:1587-1593` carries the note onto the entry.

But the number it produces is the headline. driftwood's published uk-gdpr exposure asserts
**2.17 ICO monetary penalty notices per year** against a single £86m-turnover retailer. The ICO
issues on the order of tens of monetary penalties per year across the whole UK against millions
of controllers; the estate's own schema can only cite five real UK examples across two tiers
since 2019. The modelled per-firm rate is wrong by something in the region of five orders of
magnitude. `NORTH-STAR.md:32` says regulator penalties enter "as published schemas applied to
the adopter's own size" — the schema publishes no frequency, and the number that supplies it is
a constant in the converter, not a published fact.

Second, structural: `fair.py:133` is
`freqs = [max(0, round(f)) for f in pert(*lef, n, rng)]`. Rounding a continuous beta-PERT on
`[1,4]` yields a minimum of 1, so `p_gt_0 = 1.0` — the model **cannot draw a year with no ICO
fine**. There is no counting distribution (Poisson/negative binomial) anywhere; frequency is a
rounded severity-shaped variate. That is not FAIR practice and it removes the entire
zero-inflation that dominates a low-frequency regulatory risk.

**Remedy:** either the publisher ships a frequency with a stated denominator and base-rate
citation, or the £ stops being called an annualised loss and is renamed to what it is (a
severity-scaled comparability index).

### F3 (major) — the exposure total sums lines annualised on inconsistent frequencies for the same event, and the twin's own declared scope overlaps the ico line

`units/driftwood/composed/HEADER.yaml` `exposure.total = 3,704,381.737952101` is
`_sum_prices` over the three `EXPOSURE_KINDS` entries (`composition.py:1879`, `:1928-1929`):

| line | event named | lef | annualised at |
|---|---|---|---|
| ico / uk-gdpr | (a breach drawing a lower-tier penalty) | (1,2,4) | 2.17 /yr |
| feeds / threat-register | "cart/checkout PII exfiltration" | (2,4,9) | 4.5 /yr |
| twin / forward-intel | "An exfiltration of the cart record store suppresses checkout conversion for a quarter" | (2,4,9) borrowed | 4.5 /yr |

`composition.py:1587-1593` names this defect verbatim — "two lines annualised at 2.167 and 4.5
events a year were summed into one total" — and the fix applied was to **carry the note**, not
to reconcile the frequencies. The three lines describe the same underlying event (a cart-PII
exfiltration) happening at two different rates in one total.

Worse, `units/driftwood/twin/forward-intel/v1/feed.json` payload declares
`claim_scope: {included: ["uk-gdpr"], excluded: ["pci-dss"]}` with the note "priced under the
one regime this party subscribes to a pricing feed for". If that declaration is true, the twin's
£1,897,646 sits **inside** the regime the ico line already prices at £1,787,177, and the total
double counts. If it is false (the twin's `lm` is a checkout-conversion loss, not a penalty),
then the signed scope declaration is wrong and the insurer's exclusion machinery — which keys
purely on regime names (`quote.py:158-176`) — cannot see the twin line as uk-gdpr at all, so
the pl-2/ra-3 carve-out silently applies to one uk-gdpr line and not the other.

`fair.py:106-131` gets this exactly right *within* one risk (one shared lef, additive within an
event, with a selfcheck proving the correlated tail beats the naive-independent one). The
portfolio level does the opposite of what that docstring argues for.

**Remedy:** decide whether the twin line is a further consequence of the same event (then it
belongs *inside* the ico line's `lm` list, sharing one lef, exactly as `fair.py`'s multi-source
path already supports) or a distinct event (then fix `claim_scope`).

### F4 (major) — `appetite.tolerance` is one signed number doing three incompatible jobs

driftwood signs `appetite: {tolerance: {amount: 40000, currency: GBP}}` once
(`units/driftwood/party.yaml`). It is then read as:

1. **A threshold on the *benefit* of a control.** `units/platform/risk/enforce.py:98-100`:
   `risk_bought = ALE_warn − ALE_deny`; `verdict = Deny if risk_bought > tolerance`.
2. **A threshold on retained expected annual loss.** `units/platform/graded/cage.py:171-181`
   (`select_tier`): the loosest tier whose `caged_residual` ≤ tolerance.
3. **An insurance attachment point (an aggregate deductible).**
   `composition.py:1921-1927`: "The attachment IS the appetite, seen from the other side".

These are three different economic quantities: a marginal benefit, a mean, and a per-year
aggregate retention against a *distribution*. "I will accept £40,000 of expected annual loss"
and "I will carry the first £40,000 of loss each year" are not the same statement and do not
have the same units of meaning. Nothing in the estate distinguishes them; the pound-seam gate
checks only that two *implementations* of use (2) agree.

### F5 (major) — no aggregation: every line is tiered against the *full* band, and the retained total exceeds it

Selection is per prices[] entry. From driftwood's signed evidence and `cage.TIERS`:

```
ico   isolated   1,787,177.075 × (1 − 0.98) = 35,743.54
feeds baseline      19,558.550 × (1 − 0.30) = 13,690.98
twin  isolated                                37,952.92   (recorded on the entry itself)
                                    total  =  87,387.44   vs a signed appetite of 40,000
```

Every line "fits the band"; the org carries 2.18× its own declared appetite. Add a fourth priced
parent and it carries more, with every line still green. An appetite is a budget; the estate
spends it once per line.

### F6 (major) — the sizing rule diverges from the decided rule and from the statute

`units/ico/schema/to_fair_scenario.py:68-71`:
`scale = (rate × turnover) / cap; lo, mode, hi = lo*scale, mode*scale, hi*scale`.

The decided rule (`.scratch/ecosystem/issues/07-org-size-obligations-and-currency.md:19`, ticket
07 §1) is `hi = min(rate × turnover, cap)`, examples scaling by `hi/cap`. **The code has no
`min`.** Run directly against the shipped v3 schema:

```
turnover unset       → (275,000, 3,913,900, 9,063,360)
turnover  86,000,000 → (54,368, 773,783, 1,791,837)
turnover 1,000,000,000 → (632,184, 8,997,471, 20,835,310)     cap_gbp = 8,700,000
```

At £1bn turnover the loss triple's max is 2.4× the statutory cap the ticket said binds. The
converter's own selfcheck (`:167-168`) asserts `big[2] > unsized[2]`, i.e. it **enforces** the
divergence.

Separately, UK GDPR Art 83(4) sets the maximum as the *higher* of £8.7m or 2% of turnover, not a
ratio. For driftwood (2% = £1.72m < £8.7m) driftwood's real statutory maximum is the **full
£8.7m**; the model scales the whole triple down to 19.8% of it. So a firm below the cap-equivalent
turnover is under-priced against statute and a firm above it is over-priced against the decision.
Both directions live in one line of code.

Ticket 24 (resolved) recorded this whole area as owner-decided; the divergence is between the
decision and the build, not an unowned surprise about size *existing*.

### F7 (major) — the threat line's loss magnitude is a platform-held fixture, the exact class ADR-0021 retired

`units/platform/feeds/to_fair_scenario.py:34-37`:

```python
THREAT_LM_GBP = {
    "driftwood": (1_000, 4_000, 9_000),
    "tuppence": (5_000, 25_000, 90_000),
    "ludlow": (20_000, 100_000, 400_000),
}
```

`units/feeds/threat-register/v2/feed.json` publishes **only** `lef` per institution. The
magnitude that turns it into money is a per-adopter constant hard-coded in the *platform* repo,
keyed by adopter name, not sized to anything, and not signed by the publisher whose feed it
prices. `ADR-0021` retired `platform/risk/appetite.json` for precisely this reason —
`enforce.py:170-171` asserts that file no longer exists — and `enforce.py:17-23` states the
principle: "a party's band is now declared by the party that carries it, next to its size, and
nobody else." `THREAT_LM_GBP` is the same fixture pattern, still load-bearing.

Related: ticket 24 item 4 (provisional) says "Each publisher ships its converter beside its
feed." The `feeds` repo ships no `to_fair_scenario.py` (find across the clone returns only
`platform/feeds/to_fair_scenario.py`); `composition.py:542-550` falls through to the platform
copy. The publisher does not price its own feed.

Note the scale mismatch this creates: the same named event costs **£4,000 mode** as a threat
line and **£384,000 mode** as a twin line, in one document.

### F8 (major) — "proportionate to the org" holds for one adopter of three

`grep -l '^size:'` across the three adopters returns driftwood only. Consequence, read off the
signed artefacts:

```
driftwood uk-gdpr exposure = 1,787,177.075…
tuppence  uk-gdpr exposure = 9,039,791.01976426
ludlow    uk-gdpr exposure = 9,039,791.01976426      (identical to the last decimal)
```

A fintech and a healthcare provider carry the *same* penny-identical uk-gdpr exposure, because
neither declares size, so both fall to the publisher's statutory-cap read
(`composition.py:1487-1506`, `_sized_turnover` returns None). Every `per_customer` field in both
is `null`. NORTH-STAR §4 step 2 — "The composition re-prices the adopter's exposure against its
own size" — is vacuous for two of the three example consumers. The *mechanism* is right (a
missing size widens, it never refuses); the *demonstration* is one third built.

### F9 (major) — the falsification instrument is real, runs, disagrees with the model, and is wired to nothing

`units/platform/honesty/calibration.py` back-tests the FAIR model against `incidents.json` and
recalibrates with Bühlmann credibility. I ran it offline just now:

```
driftwood: model_ale 19,558.55  observed_ale 35,000  var95 30,947.91  exceedance_rate 0.40
           verdict "under-prices (too many VaR95 breaches) — recalibrate up"
ludlow:    model_ale 1,025,511   observed_ale 130,000  ale_ratio 0.127
           verdict "over-prices (actuals run cold) — recalibrate down"
tuppence:  "defensible"
```

Three separate problems:

1. **Its verdicts are ignored.** `grep -rln calibration` across all eight units and the hub's
   `verify/` and `talk/` finds exactly one reader outside `honesty/` — none. The README claims
   "The recalibration factor prem_i / model_ale_i is the reviewable diff that re-tunes the £";
   no such diff is produced or applied anywhere.
2. **It grades a different number.** The scenarios it back-tests are fixtures
   (`fair/scenarios/driftwood-cart-pii.json`, `break-glass/scenarios/*.json`), not the composed
   exposure. driftwood's back-tested model ALE is £19,559 — the *threat* line — while the number
   the estate publishes and the insurer prices from is £3,704,382, 189× larger. The honesty log's
   own "real" driftwood losses (£20k–£55k/yr) are 100× below the published exposure.
3. **Its data is authored.** `incidents.json`'s own note: "Authored so the estate exercises BOTH
   recalibration directions". Fine as a mechanism demonstration; not a back-test.

A 40% VaR95 exceedance rate against a 5% target, printed every run and read by no one, is the
falsifiability claim failing on its own instrument.

### F10 (major) — the control weights carry no citation, and they drive both the hole prices and 60% of the insurance exclusion

`units/ico/penalty-schema/v3/feed.json` `control_weights["uk-gdpr"]["lower-tier"]` =
pl-2 0.3, ra-3 0.3, ca-2 0.2, ir-8 0.2. Every regime's weights are round tenths. Nothing in the
feed, the changelog, `payload.schema.json` or `verify-penalty-feed.sh` states where they come
from, unlike the fines beside them, which each carry an authority, a statute and a dated
monetary-penalty-notice reference.

Downstream: those four weights fix driftwood's hole prices at £536,153.12 / £536,153.12 /
£357,435.42 / £357,435.42 (`composition.py:1473-1474`), and `terms/driftwood.yaml` excludes
pl-2 + ra-3 — **60% of the largest exposure line** — on the strength of them.

The partition property is properly enforced (`composition.py:1467-1472` refuses weights that do
not sum to 1.0 within tolerance 1e-9), and `verify-penalty-feed.sh:170-206` re-checks it. I also
confirmed all 18 weight ids resolve in nist's real 1,196-control catalogue. The *shape* is
sound. The *values* are an uncited assertion sitting under a six-figure carve-out.

### F11 (major) — the daily re-pricing clock is dead, and one signed quote is already stale

`gh run view 33615860064 --repo policy-as-versioned-insurer/insurer --log`:

```
requote (driftwood) REFUSED: missing instrument: .adopters/driftwood/composed/HEADER.yaml carries no `exposure` section
requote (tuppence)  REFUSED: … no `exposure` section
requote (ludlow)    REFUSED: … no `exposure` section
```

Both of the insurer's scheduled runs to date failed identically (33496526156 on 2026-09-01,
33615860064 on 2026-09-02): CI checks the adopter out at the pinned tag `v1.1.0`, whose tree
predates the exposure section. Meanwhile run 21's own capture records the consequence:

> `SKIP: quote-driftwood: priced against exposure sha256:397abe81d6cb but
> ../driftwood/composed/HEADER.yaml now signs sha256:5822260bab86 -- the insured re-signed its
> exposure and a re-quote PR is due (the clock opens one; a human merges it)`

The clock cannot open one. NORTH-STAR principle 5 ("Intelligence re-prices on a clock") is not
holding for the priced-transfer line. The SKIP is honest; the mechanism behind it is not
running. (This is the residue of REVIEW-2026-08-31 M1, now half-fixed: the insurer *has* a tag
and registered workflows; the jobs still fail.)

### F12 (major) — `tcor.py`'s transfer move double counts the deductible and charges the full ALE

`units/platform/tcor/tcor.py:116-118`:

```python
premium = ale_warn * (1.0 + load)
out["transfer"] = line(deductible, 0.0, premium)
```

Two errors in two lines. The premium is charged on the **whole** expected loss including the
part below the deductible, and the deductible is then booked *again* as a residual — and booked
as its face amount (a limit) rather than as an expected retained loss (which, with ~2.17
events/yr, would be roughly 2.17× the per-event retention). Correct decomposition is
`premium = (1+load) × E[loss above deductible]`, `residual = E[loss below deductible]`.

The effect is a systematic bias **against** transfer in the four-move crossover — and the
crossover being *computed rather than asserted* is tcor.py's headline claim
(`tcor.py:10-11`). It is also a *third* transfer formula in one estate: `tcor.py` says
`1.4 × ALE`, `quote.py:192` says `layer × rate × (1+load)`, and nothing reconciles them.

### F13 (minor) — the twin's whole exposure line rests on one number with no stated basis

`units/driftwood/twin/orgs/driftwood/edges/cart-pii-loss-cuts-checkout-revenue.yaml` carries
`elasticity: {min: 0.06, mode: 0.12, max: 0.25}`, `evidence_grade: 2`, and a `note` that
restates the shock. It has **no `basis` field** — unlike the four `responses/*.yaml` beside it,
every one of which carries a written `basis` citing "this estate's own two prior incident
post-mortems". The valuation it multiplies (`checkout-revenue`) does carry a full derivation,
added after a reviewer misread it. The elasticity — the single number that turns £3.2m of
revenue into a £1.9m exposure line and 51% of driftwood's signed total — did not get the same
treatment.

### F14 (minor) — a hole's price does not depend on whether the hole is open

`composition.py:1457-1462` is explicit: "Every published weight becomes a hole, whether or not
this adopter has that control open: the list is the PARTITION of the exposure, not the adopter's
open holes." So closing pl-2 changes no number anywhere. The living-£ loop does not run on the
hole dimension at all. Owned: ticket 38, Status open, and its 2026-08-31 comment says the
remaining scope is exactly the refusal deletion and the ungoverned ramp.

For what it is worth the current data makes the gap invisible: driftwood's HEADER records 285
holes of 287 selected controls (only `ac-6` and `cm-6` are covered), and all four weighted
controls are open, so partition == open-hole price today by coincidence.

### F15 (minor) — three of the four published regimes are size-blind or absurd, and the decisions to fix them were made but not built

Run against the shipped v3 schema:

```
hipaa  unsized (68,928, 2,067,813, 2,067,813)   at turnover 1bn: identical
fca    unsized (48,650,000, 75,406,600, 122,595,840)   at turnover 1m: identical
pci    unsized (600,000, 900,000, 1,200,000)    at turnover 1m: identical
```

FCA's ceiling is 1.2× Standard Chartered's £102m fine **for any firm of any size**. Ticket 24
decided (provisionally) that HIPAA scales by `data_subjects × provisions` (item 1) and FCA by
`rate_lo/mode/hi × relevant_revenue` with a `widen_to` (item 3), and named ticket 21 as the
builder. Ticket 21 is **resolved**; the shipped v3 feed carries no `provisions`, no `rate_lo`,
no `widen_to`, and `composition.py:1374-1375` still hard-codes `ICO_REGIME = "uk-gdpr"` /
`ICO_VIOLATION_TYPE = "lower-tier"` — which ticket 24's consequences list said ticket 21 would
drop. Latent rather than live (no adopter declares `obligations`, and only uk-gdpr is priced),
but the code would emit these the day a second regime is wired, and its selfcheck only asserts
`lo <= mode <= hi`.

### F16 (minor) — the adopter's "own" selection policy has zero degrees of freedom

`verify/pound-seam/pound_seam.py:503-598` runs the adopter's package and `cage.select_tier` over
60 constructed cases (each rung's exact band boundary ±1e-6, every rung tried as a floor) and
**FAILs on any disagreement**. Run-21 capture: "driftwood: platform/graded/cage.py and
driftwood's own selection-policy package pick the same rung in all 60 cases".

That is a genuinely strong anti-gaming control (F16 is not a complaint about the check). It is a
complaint about the claim built on top of it: `selection_policy.py`'s docstring and ADR-0021 say
the rule "lives here, in the adopter's own repository, because whose money is at risk decides
how much of it to carry". A party that decided to select on VaR95 rather than the mean, or to
require two rungs of headroom, would be refused by the hub gate. Today the adopter's freedom is
the freedom to reimplement `cage.select_tier` exactly.

### F17 (minor) — the reduction table that prices the tier is unevidenced; the adopter's measured one is not used

`units/platform/graded/cage.py:71-80` says it plainly: "WHOSE NUMBERS THESE ARE. They are the
PLATFORM's, self-declared, evidenced by nothing but this comment." `TABLE_VERSION = "1.0.0"`,
reduce = 0.30/0.70/0.92/0.98. driftwood's own overlay publishes *measured* mode reductions of
0.05/0.30/0.65/0.90 (`twin/orgs/driftwood/responses/*.yaml`, each with an `evidence_grade: 2`
and a written basis). The residuals the tier is selected from are computed from the platform's
set (`composition.py:1758`), and the entry says so (`residual_basis: platform-cage-tiers@1.0.0`).

The estate grades the divergence — but grades the *wrong* question.
`pound_seam.py:431-500` compares which rung is **cheapest** on `net_cost_of_risk`. The number
that actually enforces is which rung the **selection** returns, which uses `reduce` only.
Run-21: "they differ by up to 171,600 on the rungs themselves". On today's data both routes land
on `isolated` (driftwood's own 0.90 reduction would leave £189,765 residual against a £40,000
band → fail-closed to isolated; the platform's 0.98 leaves £37,953 → fits). Same answer, opposite
reasons, and the check that exists would not notice if they diverged.

### F18 (minor) — tier selection is saturated, and no real £ has ever crossed a band

Across the three adopters' signed evidence: 8 of 9 priced tier selections sit on the bottom rung
(`isolated`); the ninth is `baseline`. Every entry has `changed: false` and `old_price ==
new_price`. `talk/captures/verify_e2e_verify-e2e-step3-price-crosses-band-pr-opens.out` grades
PASS on an explicitly **synthetic** residual: "a SYNTHETIC residual placed either side of
driftwood's own signed appetite band … (20,000.00 → 58,269.23 GBP, **not driftwood's real
priced position**)". Ticket 60's 2026-09-01 comment: "the proposer returned [] — no band crossed,
no proposal PR". Ticket 74 ("step 3 happens once, for real") is open.

The honesty is exemplary. The economics is: with every line 45–90× over the band, the ladder has
no resolving power on the real data, and the mechanism's only demonstration is a fixture.

### F19 (minor) — no counting distribution, no aggregate cap, no overlap correction

Beyond F2's rounding: per-event magnitudes are drawn i.i.d. within a year
(`fair.py:145-147`) with no aggregate annual cap. The twin's shock is defined as
"suppresses checkout conversion **for a quarter**" and is drawn up to 9 times in a modelled
year at `lef = [2,4,9]`. Nine quarters of suppressed conversion cannot occur in one year; the
shock windows overlap and the marginal effect of an overlapping event is not additive. Nothing
in the model caps a line at the exposed revenue (£12.8m/yr for driftwood's checkout) or corrects
for overlap. Similarly, `annual_cap_usd` is present in the HIPAA formula and read by nothing
(ticket 24's facts section already found this).

### F20 (minor) — the "mode" of the uk-gdpr triple is a two-point median

`lm_triple` sets `mode = statistics.median(ex)`. For uk-gdpr lower-tier `ex` has **two** members
(Clearview £7,552,800 and Doorstep Dispensaree £275,000), so the mode is their midpoint,
£3,913,900 — a value no regulator has ever imposed, sitting 14× above one datum and half the
other. The beta-PERT then puts weight λ=4 on it, so 67% of the distribution's mean comes from a
number with n=2 behind it. The higher tier has n=3. `lo` is also scaled by the turnover factor,
which means Doorstep Dispensaree's £275,000 fine (against a small pharmacy) is rescaled *down*
by driftwood's ratio to £54,368 — scaling a small firm's fine by a large firm's ratio.

---

## 3. Where the £ engine is genuinely strong

Each with evidence, because a review that only lists faults is useless.

1. **Three published numbers reproduce exactly by hand from signed inputs** (§1). I re-derived
   the PERT sampler independently and hit `1787177.0751717845` against a published
   `1787177.0751717847`.
2. **The perspective/currency partition is real and enforced, not documented.**
   `fair.py:67-93` (`sum_prices`) raises on any mix; `composition.py:1704-1711` refuses a
   forward-intel feed pricing another party's balance sheet; `quote.py:186-192` refuses a layer
   across two currencies; `price_quote` refuses a quote insuring another adopter or booking a
   premium on another sheet. Run-21 capture: "driftwood: every list of amounts in the document
   is one perspective in one currency" for all three adopters, and "the estate's own summing
   helper refuses to add this quote's layer to its premium".
3. **`premium` is correctly excluded from exposure.** `composition.py:1875-1879`: "folding it in
   would make the premium an input to the formula that computes it." That is the right call and
   it is enforced by the `EXPOSURE_KINDS` tuple, not by discipline.
4. **The hole breakdown is a strict partition, refused otherwise.** `composition.py:1467-1472`
   raises if published weights do not sum to 1.0 (abs_tol 1e-9); `verify-penalty-feed.sh:170-206`
   re-checks sum, duplicates, range and regime/violation-type existence. I independently
   confirmed all 18 weight ids resolve against nist's real 1,196-control OSCAL catalogue.
   Run-21: "driftwood regime entry (penalty-schema): 4 priced hole(s) sum to its total
   1,787,177.08 GBP". **No double counting exists within the priced regime.**
5. **The multi-source correlation model is actuarially correct and proved.** `fair.py:106-131`
   draws one frequency and sums magnitudes *within* the event; the selfcheck at `:300-310`
   proves the correlated tail sits above a naive independent sum. This is the one place in the
   estate that reasons like an actuary, and it is right.
6. **Two selection engines are cross-checked at the band boundary in 60 cases** and a
   disagreement is a hard FAIL (`pound_seam.py:576-596`). A rigged adopter policy cannot pass.
7. **Missing-instrument discipline is coherent and asymmetric in the right direction.** A missing
   *size* widens to the statutory cap and never refuses (`composition.py:1477-1506`); a missing
   *currency* or a missing FX rate for the date refuses and emits nothing
   (`composition.py:1548-1555`, `:1437-1446`). Run-21 verifies both directions live: "GBP->AUD
   on 2026-08-15 is 1.936, the rate the signed fx feed publishes" and "a date the fx feed does
   not publish (2025-08-15) refuses as a missing instrument, and prices nothing".
8. **Nothing in the £ path is red on the citable run.** From `gh run view 33616685427 --log`,
   run 21 grades: `fair/verify-fair-tail.sh PASS`, `tcor/verify-tcor.sh PASS`,
   `risk/verify-risk-tuned.sh PASS`, `compose/verify-composition.sh PASS`,
   `verify/pound-seam PASS`, `honesty/verify-honesty.sh PASS`, `wargamer PASS`,
   `ico/verify-penalty-feed.sh PASS`, `insurer/verify-insurer-party.sh PASS`,
   `verify/party PASS`. None of run 21's seven FAILs is in this dimension. The £ engine is the
   greenest surface in the estate.
9. **The ponytails are honest, dated and specific**, and several name their own upgrade path
   precisely (`quote.py:31-38` on rate-on-line vs E[layer loss]; `composition.py:1894-1901` on
   sum-of-means vs distribution; `cage.py:71-79` on whose numbers the table is). The estate
   consistently tells you where it is thin. My criticism is almost never "this was hidden"; it
   is "the magnitude of the named gap is not stated, and nothing grades it".
10. **The self-referential pricing cycle was found and cut.** `emit-forward-intel.py:230-239`
    records that the insurer's quote — priced off the exposure whose largest line derives from
    this feed — used to be named as an input, "and it made the premium and the forecast mutually
    self-supporting". Removed. That is the right instinct applied correctly.

---

## 4. Answers to the questions posed

**Are the formulas defensible?** The *mechanics* are: beta-PERT with λ=4 is standard FAIR;
TVaR ≥ VaR95 ≥ ALE is guaranteed by construction and asserted; the risk load
`COC × (TVaR − ALE)` at Solvency II's 6% is a real convention correctly applied; the
lognormal–GPD peaks-over-threshold splice in `severity.py` is textbook and validated. The
*inputs* are not: frequency is a constant (F2), one magnitude table is a platform fixture (F7),
control weights are uncited (F10), the twin's elasticity has no basis (F13), and the sizing rule
diverges from both the decision and the statute (F6).

**Are the published numbers real?** Yes — three traced exactly in §1, all from signed artefacts,
with no hand-entry anywhere in the chain.

**Is "price of a hole = control weight × regime exposure" a partition or double counting?**
A strict partition, enforced to 1e-9, within one regime and one violation type. It is *not* a
function of hole status (F14), and only one of four published regimes is priced, so the
cross-regime double-count risk (ac-3, sc-28, au-2, ir-4 and au-6 each appear under two regimes'
weights) is latent, not live.

**Does annualisation of a scenario have a stated frequency basis?** Stated, yes —
`lef_basis` is carried on every entry and `lef_from` names the borrowed feed. Grounded, no: the
ico basis is "warn/deny lef are editorial (schema doesn't carry frequency)" and the threat basis
is "DBIR retail-sector web-app-attack base rate, editorial midpoint" with no denominator.

**Is the tail model coherent between fair.py and the twin?** Structurally yes — the seam is a
JSON payload, not a shared module, and `severity.py:6-14` explains why. Practically it is unused:
driftwood's live feed emits a bounded triple (`tail: bounded-pert` on the entry) and the
lognormal-GPD path is exercised only by
`fair/scenarios/driftwood-twin-heavy-tail.json`, whose own note says the parameters "are
illustrative". So no published £ in this estate has a heavy tail today.

**Can the adopter game its own price?** Partially. It self-declares turnover (linear in the ico
price; understating halves it, and omitting it *raises* it to the cap, which is the right
incentive shape), appetite tolerance (unconstrained; a larger band buys a looser cage), and
`overlay.floor` (tighten-only, correctly clamped). It cannot game the selection rule
(F16's cross-check), cannot game the hole partition (weights must sum to 1), and cannot sum
across perspectives. Nothing cross-checks a declared size against any independent source, and
the 12-month staleness rule is the only guard.

**Is the tier selection empirically grounded or a threshold table?** A threshold table, self-
declared, evidenced by nothing but its own comment, which says so (F17).

**Do prices ever cross perspectives?** No. This is genuinely watertight and the best-defended
property in the dimension (strength 2).

**What is the smallest honest claim the estate can make about its £ today?**

> Every price in this estate is **traceable**: it reproduces exactly, by a third party, from
> signed and versioned publisher artefacts and the adopter's own signed declarations, with the
> engine, the seed, the frequency basis and the reduction set all named on the artefact. Prices
> are **comparable within one party's balance sheet and one currency**, and the estate refuses
> rather than sums across either. That makes the £ an **ordinal, auditable comparison
> instrument** — good enough to rank control options and to make a change in a pinned dependency
> visible as a number in a reviewed PR.
>
> It is **not** an expected annual loss. The frequency that annualises it is an editorial
> constant with no cited base rate; the magnitudes rest on n=2–3 published fines rescaled by a
> ratio that is not the statutory formula; and the estate's own back-test says the model
> over-prices one adopter by 8× and breaches its own VaR95 at 40% against a 5% target. Nobody
> should book it, cede it, or defend it to a regulator or a carrier.

The estate is one honest sentence away from being able to say this. Today the artefacts do not
say it: `HEADER.yaml` publishes `exposure.total` with no qualifier, and an insurer prices a real
layer off it.

---

## 5. Notes for the other reviewers

* The `truth-series` map lists `verify-pound-seam` among 21 scripts "in FAIL state consistently
  across all 12 mature runs (10–21)". Run 21's own gate output disagrees:
  `verify/pound-seam/verify-pound-seam.sh PASS` (`gh run view 33616685427 --log`). I did not
  check runs 10–20, so the map may be right about those; it is wrong about 21.
* `REVIEW-2026-08-31.md` raised no economic-validity findings — it graded the £ seam as "computes
  for real" (`:31`), which is true and is a different claim from the one I have tested. Nothing
  here re-raises or contradicts a refuted claim of that review. Its M1 (feeds/insurer
  mechanically unrunnable) is now half-fixed and half-live: tags and registered workflows exist,
  and the requote jobs still fail daily (F11). Its M9 (step 3 never real) still stands (F18).
