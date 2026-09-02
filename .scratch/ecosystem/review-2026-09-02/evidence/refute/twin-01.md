# Refutation attempt — TWIN-01 (twin-validity, critical)

Verdict: **NOT REFUTED on its core claim; two of its supporting statements are wrong or
over-broad and must be corrected.** Confidence: high — every line below was re-derived from
primary sources, not from the auditor's quotes.

## 1. The core claim holds (re-derived)

`twin/verbs.py:948`, inside the only forecast-producing loop in `run()`:

```
            "probability": float(beliefs[proposition_id]),
```

`beliefs` is `world_model.get("beliefs", {})` (`twin/verbs.py:934`). There is no other expression
in that dict, no arithmetic, no reference to a signal, a fact, an edge or a component's position.

The authored constant, verbatim, `twin/fixtures.py:4232-4243`:

```
    "orgs/royal-mail/world_models/market-consensus-2013.yaml": """\
id: market-consensus-2013
...
beliefs:
  automation-shortfall-forces-a-remedial-investment-by-2019: 0.05
```

The fixture's own `note` says the number was chosen, not measured: "A low prior, deliberately …
The point of a low-notoriety key is that the twin **has to earn a higher belief from the signals
below, not start from one**." Nothing earns it.

Reproduced live, offline, in the scratchpad (writes only to a temp dir; no cluster, no network):

```
$ bash twin/beat-royal-mail.sh <scratch>/rm-beat
    market-consensus-2013        p=0.05   brier=0.9025   log-loss=2.9957   [as-consumed]  adjusted brier 0.8641
  as-consumed      5 fact(s) admitted
  model residual not computed: … A forecast here reads a world model's declared belief and
  nothing infers it from a signal, so the three probabilities are identical by construction …
```

The emitted bundle confirms the five signals never reach the forecast. They appear in exactly two
places in the whole artefact — the gate's `admitted.signals` list and the empty
`claims_withheld_with_their_signal` — and in no field of the forecast object itself:

```
$ python3 -c "... re.findall(r'[^\"]*signal[^\"]*', json.dumps(bundle))"
'signals'
'claims_withheld_with_their_signal'
```

The estate says the same thing about itself in three committed places:
- `twin/regimes.py:305-308` — "nothing in this system infers a probability from a fact yet — a
  forecast reads a world model's declared belief … the honest state until the sense→move loop closes"
- `twin/verbs.py:1000` — "nothing here infers a probability from a fact yet"
- `twin/README.md:2910-2911`

Corroborating structure: `twin/primitives.py:182-214` (`updated_beliefs`) walks causal ancestors
of an observation and returns each with `"directional_only": True` and, in its own docstring,
"carries **no magnitude** — the diagnostic direction needs a prior over the causes and this model
authors none". The one other module that could emit a scored forecast,
`twin/forecast_book.py:118` (`emit(..., probability: float, ...)`), also takes the number as a
caller parameter, and it is wired into no CLI verb and no script — `grep -rn forecast_book` outside
its own file returns only `tests/`, `twin/invariants/harness.py` and a `CLAIM_SCOPE` import in
`twin/benchmark.py`. `twin/pricing.py` contains the string "probability" zero times (`grep -c`).

## 2. Correction A — the title's first clause is over-broad

"Nothing in the twin infers a probability" is false as a statement about the package.
`twin/severity.py:127-137` computes `tail_probability` = `P(X > threshold)` and `survival(x)` from
a lognormal body spliced to a GPD tail; `twin/anchoring.py:42-66` (`fit_lognormal`) solves
`(mu, sigma)` in closed form from two **cited, dated, sourced** quantiles in
`twin/severity-anchors.yaml`. Those are computed probabilities, not transcriptions.

They do not rescue the finding: they are probabilities of a *loss magnitude*, not of a
proposition, and none of them is ever scored under a proper scoring rule. The defensible sentence
is the narrower one, which survives intact: **no probability of a proposition is inferred, and
every probability the twin scores is a verbatim read of an authored `beliefs:` entry.**

## 3. Correction B — the fit-impact sentence is refuted

"change 0.05 to 0.95 and the red result goes green with nothing else in the estate moving" is
**false**. `twin/invariants/harness.py:2795-2800`, inside harness guard
`a_scored_forecast_is_never_silently_dropped`:

```
    worst = max(body["scores"], key=lambda s: s["brier"])
    if worst["brier"] <= 0.25:
        raise Violated(
            f"the worst forecast on this key scores {worst['brier']}, better than a flat 0.5 — the "
            "beat's red result has been tuned away, …"
```

Its docstring (`:2687-2690`) names the exact attack: "**The red result is not tuned away** … asserted
on the *worst* score … quietly re-authoring the losing belief does not [pass]."

Ran it: `harness.run(only=['a_scored_forecast_is_never_silently_dropped'])` →
`Result(number=37, status='PASS', detail="… the worst is brier 0.9025 and is printed first …")`.
And `scoring.score(0.95, True)` → `{'brier': 0.0025, …}`, which is ≤ 0.25 and trips the guard.
The suite runs in `.github/workflows/twin.yml:24-36` on any push touching `twin/**`, which is where
`fixtures.py` lives. So a re-authored digit is caught by a real, running check.

Note the guard's limit, which is the honest replacement claim: it is a threshold on the *result*,
not a mechanism that makes the number earned. It pins the demo to staying red; it does not make
anything infer.

## 4. Correction C — "claimed ownership: none found" needs qualifying

Narrowly true for an *open closing ticket*: I found none. `grep -rn -i -e infer -e belief -e prior`
over `.scratch/ecosystem/issues/*.md` and `.scratch/ecosystem/map.md` returns nothing that owns
making a signal move a probability; ticket 46 ("the forecast book and the scorer party") is about
publisher-reliability scoring, not inference.

But the limitation is *owned as a disclosure and closed as accepted*:
`.scratch/twin/build/36-…md:35-37` and `.scratch/twin/build/72-…md:44-49` both state it and are
ticked `[x]`. So this is a disclosed, deliberately-accepted design state with no closing ticket —
not a concealed defect. Reporting it as if it were hidden would overstate it.

## 5. A supporting tension the auditor did not cite

The same run prints `sense-move  full  8/8 of decision ticket 11` on every artefact, while
`twin/regimes.py:308` calls the same loop open ("until the sense→move loop closes"). The
capability's eight ACs (`twin/capabilities/sense-move.yaml`) genuinely do not include "a signal
moves a forecast probability", so the grade is not lying about its own checklist — but "sense-move:
full" and "nothing consumes a signal" print in the same terminal output.

## 6. A sharper ambition hook than the one given

`NORTH-STAR.md:35` (principle 6) says "Forecasts are pre-registered and scored against reality
under proper scoring rules" — a pre-registered authored prior scored under Brier satisfies that in
letter, so it is the weakest available hook. Stronger, and unquoted by the auditor:

- `NORTH-STAR.md:34` (principle 5): "Feeds refresh, **the twin re-forecasts**, cages re-price".
  A feed refresh cannot move a number read out of a `beliefs:` map, so "the twin re-forecasts" is
  structurally unreachable today, not merely unbuilt.
- `NORTH-STAR.md:19` (the twin's row): consumes "Feeds, the adopter's own overlay, history". The
  overlay and history are consumed (gating, pins, admission); the feeds are not consumed by the
  forecast at all.
