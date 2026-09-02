# Skeptic pass on TWIN-07 — verdict: NOT REFUTED, but the claim needs three corrections

Re-derived 2026-09-02 from primary sources. Core holds; three subsidiary assertions are wrong or
mislabelled, one of them in a way that inverts what the code actually does.

## What I confirmed

**Saturation (holds, exactly as stated).**
`git -C <hub> show origin/main:talk/captures/verify_twin-evals_verify-twin-evals.out` — seven
metric lines, every one `score=1.000 … last=1.000`:
signal-classify 0.800, evolution-judge 0.750, causal-claims 0.800, causal-claims-grade-accuracy
0.800, gameplay-lens 0.650, substrate-generator 0.800, ethics-gate 0.800.

`twin/skill-scores.jsonl` — exactly 7 lines, all `"recorded_at": "2026-08-13T00:00:00Z"`, all
`"model_version": "heuristic-0.1.0"`, all `"score": 1.0`. Totals 23, 4, 4, 4, 3, 3, 5.
`git rev-list --count origin/main -- twin/skill-scores.jsonl` → `1`
`git log --oneline origin/main -- twin/skill-scores.jsonl` → `f91a41c Build ticket 56: coherence
audit — skills, sensing, forecast, score`. One commit, as claimed.

**The evolution-judge circularity (holds, and is *stronger* than the finding's own supporting
citation).** I ran the real corpus builder and the real lookup:

```
python3 -c "import tempfile,pathlib; from twin import evolution_judge as ej; ..."
carillion | comp.name= "Carillion's UK construction and support-services business" | expected= 0.62 | fired= ('support-services', 0.62)
enron     | comp.name= "The subject's energy-trading and mark-to-market business"   | expected= 0.45 | fired= ('mark-to-market', 0.45)
nmc       | comp.name= "The subject's UK-listed hospital operations"                | expected= 0.55 | fired= ('hospital operations', 0.55)
wirecard  | comp.name= "The subject's third-party payment-acquiring business"       | expected= 0.8  | fired= ('payment-acquiring', 0.8)
```

FOUR of four, not the "three of four" that ticket 23:29 records. In each case the phrase that
fires sits in the component's own **name** (`twin/evolution_judge.py:257-262`, `_ORGS`), so the 4-8
accumulated evidence statements are not needed at all, and the keyword's value is *bit-identical*
to the expected label — not merely inside the ±0.15 `_TOLERANCE` at `twin/evolution_judge.py:213`.
Table at `twin/evolution_judge.py:71-85`. `_infer_position` returns on first substring hit,
longest-first (`:92-97`).

**Partial disclosure.** `twin/skill-thresholds.yaml:16-83` does say every heuristic "scores 1.0 on
its own N-item corpus" and that thresholds are "set below that … never padded up". The
`evolution_judge.py:20-24` `ponytail:` note discloses the lookup is "fitted to the four real
backtest orgs' own component descriptions". Neither states the sharper fact I measured: that four
of four expected labels are literal values in that table and the component name alone decides.

**No ticket owns the fix.** GAPS.md:81 row 3.22 asks only to "disclose the circularity in the skill
card". Grepping `.scratch/ecosystem/issues/` for "circular"/"evolution-judge" returns tickets 10,
23 and 50; 23:29 records it as a fact, 10:47 references H5-08, 50 packages the skill for a human to
run. None charts removing it. The finding's ownership line is right.

**Only twin quality metric on the truth surface.** The gate discovers `verify*.sh` under
`.estate-clone` and `verify/` (`talk/verify-all.sh:45`); `talk/verify-exclusions.txt` excludes two
unrelated scripts. Of the 84 run-21 captures, four are twin-related: `verify_twin-evals_*` (the
scores), `verify_e2e_verify-e2e-step5-twin-forecasts.out` (a presence check that ends by quoting
verify-twin-evals' own PASS line), `.estate-clone_driftwood_twin_verify-twin-scenarios.out` and
`.estate-clone_driftwood_verify-twin-overlay.out` (both structural/render checks, both currently
FAILing on feed re-render). Nothing else scores twin judgement quality. Qualifier holds.

## Correction 1 — "46 hand-authored items drawn from the same four subjects" is false

Two errors. (a) 46 is the sum of *metric*-item pairs; `causal-claims` and
`causal-claims-grade-accuracy` share corpus digest `6c8f7f4a…` in skill-scores.jsonl and are the
same 4 items scored by two scorers (`twin/record_skill_scores.py:56-59`). Distinct items = **42**.
(b) Only 27 of the 46 come from Carillion/NMC/Wirecard/Enron. I enumerated every corpus:

| metric | n | subjects |
|---|---|---|
| signal-classify | 23 | carillion(8) nmc(5) wirecard(6) enron(4) — the four |
| evolution-judge | 4 | the four |
| causal-claims | 4 | `netflix:streaming-displaces-dvd`, `netflix:cdn-capacity-lifts-streaming`, `netflix:price-separation-erodes-goodwill`, `intel:euv-delay-slips-the-node` |
| causal-claims-grade-accuracy | 4 | same 4 items, `grade_scorer` |
| gameplay-lens | 3 | `intel`, `netflix`, `pocket` |
| substrate-generator | 3 | `quiet-week`, `sparse-plants`, `dense-plants` — synthetic schedules, no org |
| ethics-gate | 5 | `bus-factor-structural-aggregate`, `mood-sensor-no-scenario`, `individual-email-content-when-aggregate-suffices`, `expensive-surveillance-low-value`, `keystroke-monitoring-no-dpia` — sensor-admission cases, no org |

The fitting-circularity argument is carried by evolution-judge, and to a lesser extent
signal-classify (whose own docstring, `twin/signal_classify.py:14-22`, concedes it "has only ever
been proven against `political` and `economic` signals"). It does not generalise to the other 19
metric-item pairs, and the finding should not spend that credit.

## Correction 2 — "its regression guard has never had two data points" conflates two mechanisms

There are two distinct guards and the finding merges them.

- The **regression guard** is `verify/twin-evals/verify-twin-evals.sh:107-119`: `prior =
  history_for(skill); last = prior[-1]["score"]`, then `verdict(score, threshold, last)` returns
  `"fell"` if `score < last`. It **has** a data point — the 2026-08-13 value — and it compares
  against it on every gate run (that is where the `last=1.000` column in the capture comes from).
  The script's comment at `:110-112` explicitly rejects `detect_regression()` precisely *because*
  that one "says nothing at all while only one has ever been recorded".
- The "fewer than two committed versions" SKIP belongs to `skill_score_log_is_append_only`
  (`twin/invariants/harness.py:735-776`), which is an **append-only** guard against a previously
  committed entry being edited or removed — not a regression guard at all.

Two further mislabels in the same sentence. That check is a `@harness_check`, not one of the 16
entries in `twin/invariants/manifest.yaml` (I grepped: it is absent), so "invariant 15" is a
positional count of decorators, not an invariant number. And it does not run in the gate: the
harness is reached only via `bin/twin` and `.github/workflows/twin.yml`, which
`verify-twin-evals.sh:5-7` itself notes "is never cited by any document". So "Today's CI" here is
not the truth surface. (The SKIP itself is real: one commit touches the log, so `len(history) < 2`
at `harness.py:766` is unavoidable. `twin.yml` last ran 2026-09-02T09:36Z, run 33615039125,
conclusion failure — I did not open its log.)

## Correction 3 — "structurally incapable of moving" and "never once exercised" both overstate

`verify-twin-evals.sh:83-84` evaluates the skills live every run against fixture repositories built
fresh in a `TemporaryDirectory`, recording nowhere. A heuristic that regressed would score below
1.000 and the gate would print `-- FELL` and fail. The metric can move **down**; it cannot move
**up**, and its baseline has not been re-recorded since 2026-08-13.

And the `fell` branch is exercised on every gate run, deliberately —
`verify/twin-evals/verify-twin-evals.sh:70-73`:

```
assert verdict(0.7, 0.8, None) == "below", verdict(0.7, 0.8, None)
assert verdict(0.9, 0.8, 1.0) == "fell",  verdict(0.9, 0.8, 1.0)
assert verdict(1.0, 0.8, 1.0) == "pass",  verdict(1.0, 0.8, 1.0)
```

with the comment at `:64-67`: "Named and asserted below, because a comparison that is only ever
exercised by scores that all pass cannot tell 'correct' from 'always says pass'." The author
anticipated this exact objection and answered it in code. What has never happened is a *real* fall
in a *real* score — which is a statement about the estate's stability, not about an untested guard.

## What I could not look at

The `twin.yml` run log for 2026-09-02 (I derived the SKIP from the code path and the one-commit
history instead). Whether a real model swap would move any score — no such swap exists to observe.
