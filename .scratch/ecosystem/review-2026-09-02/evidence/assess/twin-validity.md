# Assessment — The twin's epistemic validity

Dimension: is the twin intelligence or theatre, for the purpose NORTH-STAR gives it?
Auditor pass, 2026-09-02. Read-only. Newest citable line: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990
… pass=57 fail=7 skip=18 excluded=2 total=84`.

The standard I am grading against is NORTH-STAR.md:19 — the twin's row in the participants table:

> **The twin** | Priced forecasts and forward intelligence under a declared perspective, signed by an
> agent identity, scored against reality | Feeds, the adopter's own overlay, history | `twin/`
> (subjects are eleven real firms today, not the adopters)

and NORTH-STAR.md:35 principle 6 ("Forecasts are pre-registered and scored against reality under proper
scoring rules"), NORTH-STAR.md:31 principle 2 (the £ selects the cage spec), and NORTH-STAR.md:46 §4
step 5 (the twin, on its schedule, plays a dated external signal forward — the niobium headline —
emits a scored forecast, and publishes forward intelligence the platform consumes).

---

## 1. The one-paragraph verdict

The twin is not theatre and it is not yet intelligence. It is a very large, unusually honest
**instrument for holding a forecast to account** — real proper scoring rules, a real rewind that
reads a git tree at T, real information regimes, a real adversarial planter/detector split, a real
invariant harness that runs daily on a live CI runner and is currently red for a pre-registered
reason — wrapped around a **forecast that is a hand-typed constant**. `twin.verbs.run()` emits
`"probability": float(beliefs[proposition_id])` — a verbatim read of a YAML number. Nothing in the
package infers a probability from a signal, and the package says so itself, in the artefact, at run
time. Everything downstream of that number is honest and well-built; the number itself has no
provenance requirement in the schema and, in 19 of the 20 world models in the fixture corpus, no
citation at all. On the estate side, the seam is wired but not load-bearing: the twin's £1,897,646
line is driftwood's largest price and it reaches a real enacted Namespace cage tier — but by a
hand-transcribed comment that no check verifies, on a feed that sits outside every signed tag
driftwood has ever cut, produced by a clock that has fired twice and failed twice and has never
written a single observation line.

## 2. What is genuinely done and proven

Each item verified directly, not taken from a map.

**S1. A forecast really has been scored against a real, dated, cited outcome, and the answer is
red.** I ran it: `python3 -P -m twin backtest --repo … --org royal-mail --scenario
would-the-twin-have-flagged-it --regime as-consumed --at 2018-06-01` then `twin score … --outcome
royal-mail-concedes-the-automation-shortfall-2019` printed
`market-consensus-2013 p=0.05 brier=0.9025 log-loss=2.9957 [as-consumed]`. The outcome document
(`twin/fixtures.py:4395-4416`) cites Royal Mail's real 2019-05-23 announcement of a c.£1.8bn
five-year UK investment programme with a URL. The rewind is real: the bundle's
`regime.gate.ingestion_history.committed` is `2018-05-17T09:00:00Z`, before the declared T, so the
October 2018 profit warning and the answer key are absent from the tree, not filtered afterwards.
The red result is surfaced first, not buried — invariant 37 in today's CI run asserts exactly that
("the worst is brier 0.9025 and is printed first, worse than a coin flip and still the headline").

**S2. The subjects' *facts* are real.** `grep -o "https://[^ \"']*" twin/fixtures.py | sort -u | wc -l`
→ **81** distinct real citations (SEC EDGAR, FCA, `commonslibrary.parliament.uk`, the Royal Mail
prospectus on `data.parliament.uk`, BaFin, trade press), plus 18 `example.invalid` URLs confined to
the two deliberately-synthetic hand-computable fixtures. GAPS 2.14's critique ("the 'real incidents'
back-test is a hand-authored fixture written to produce the narrated verdict") is aimed at
`platform/honesty/incidents.json`, **not** at the twin's eleven firms, and does not transfer: the
twin's signals and outcomes are real, dated and sourced.

**S3. The engine refuses to score what it cannot score.** Netflix ("too famous to distinguish
anticipation from recitation") and Intel (unresolved until 2026H2/2027H1) carry no answer key and
`twin score` structurally refuses; Kodak and Maersk carry no outcome by design. This is the opposite
of a demo that only shows green.

**S4. The invariant harness is real, runs daily on a live runner, and is honestly red.** Hub
`twin.yml` run 33615039125 (2026-09-02T09:36Z): `RESULT: 70 passed, 1 failed, 3 skipped (0 pending
invariants, 3 skipped and not faked)`; `1 failed, 1550 passed in 115.13s`. The single failure is
`flux_coverage_floor_is_still_reachable`, a pre-registered falsifier that the guard itself labels
"**This guard staying red is the finding, not a defect in it**". Three determinism jobs
(x86_64-linux, aarch64-linux, arm64-darwin) plus `reproduce-elsewhere` all pass.

**S5. The capability grades are not self-declared.** `PYTHONPATH=. python3 -P -m twin grade` →
`aggregate: 73 of 73 across 13 capabilities, 13 at full`, reproduced locally.
`twin/grades.py:150-188` refuses a hand-typed `grade:` key and refuses a capability file whose
checklist text or count has drifted from the owning ticket's live `## Acceptance criteria` section.
This is materially stronger than the skill-eval mechanism below and should not be conflated with it.

**S6. Several anti-gaming mechanisms are structural, not prose.** `twin/detector.py` imports nothing
naming `planter` (AST-checked on real source) and `detect()` returns byte-identical output with a
decoy `plants` key spliced in; `misuse.log_removal()` accepts no float parameter so a
constraint-removal "attractiveness" number can only be produced by re-running the real pre-filter;
`grade_5_only_path_never_prices` is enforced (`evolution_judge.judge()` hard-codes `evidence_grade:
5`, and `evidence-ladder.yaml` sets `pricing_threshold: 2`, so no skill output can ever price);
`no_recommended_action_field` passes with "7 map positions carry numbers and no inherited action
band". `enact_guard.py` records two real, dated, self-caught bugs (2026-08-29 permissive default,
2026-08-31 `_push_target` cwd resolution) rather than presenting itself as sound.

**S7. The self-disclosure is specific and, in the sharpest case, is exactly the finding an auditor
would write.** `twin regimes` printed, live:

> model residual **not computed**: … A forecast here reads a world model's declared belief and
> nothing infers it from a signal, so the three probabilities are identical by construction and a
> computed residual of zero would read as 'the model is fine' rather than as 'nothing consumes a
> signal'.

That is the twin naming its own central limitation in its own output. It is a real strength, and it
is also why F1 below is a shortfall against the north star rather than an accusation of dishonesty.

## 3. Findings

### F1 (critical) — Nothing in the twin infers a probability; every scored "forecast" is a transcription

`twin/verbs.py:932-956`: `run()`'s only probability expression is
`"probability": float(beliefs[proposition_id])`, a direct read of the world model's YAML. There is no
other producer of a forecast probability anywhere in the package (`grep` for `probability` in
`twin/pricing.py` returns nothing; `scoring.py` only consumes). Reproduced live: the Brier 0.9025 is
`p=0.05` and `0.05` is literally the value on line 8 of
`orgs/royal-mail/world_models/market-consensus-2013.yaml` in `twin/fixtures.py`.

Consequences that a skeptic can re-derive:
- The Royal Mail beat scores the fixture author's authored prior against a real outcome. Change one
  YAML digit to `0.95` and the flagship "we can prove when we're wrong" result goes green. Nothing
  else in the estate would move.
- The five real, cited, dated Royal Mail signals in the same fixture are loaded and admitted (my
  `twin regimes` run: `as-consumed 5 fact(s) admitted`) and consumed by nothing.
- The three-regime localisation diagnostic can only ever localise to *sensing* or *interpretation*;
  the *model* residual is structurally uncomputable and is reported as such.

NORTH-STAR principle 6 says forecasts are "scored against reality under proper scoring rules". The
scoring rules are real and the reality is real. The forecast is not a forecast in the sense the
sentence implies — it is a recorded belief. **No open ticket owns this.** The remedy is a decision,
not a patch: either build a signal→probability path (which reopens everything twin 11 Q1 decided
about ordinal arithmetic and grade-5 judgement), or amend the north-star row to say the twin scores
*recorded* beliefs, which is a different and smaller claim.

### F2 (major) — The schema demands provenance on everything except the number that scores

`twin/schema.py:615-624`: a `signal` **requires** `id, date, steep, source, statement, provenance`.
`twin/schema.py:611-614`: a `world-model` requires only `id, name, beliefs` — no source, no
provenance, no evidence grade, no calibration. A `valuation` requires `basis` prose
(`schema.py:232`); a causal edge requires `sign, lag_days, elasticity, evidence_grade` but
`calibration` is optional (`schema.py:790-806`) and `evidence_grade` is validated only as an integer
1-5 (`schema.py:177-185`) with nothing checking that grade 2 ("repeated historical co-movement — the
same relationship observed moving together across several instances") is backed by any observation.

Measured: of 20 `world_models/*.yaml` documents in `twin/fixtures.py`, **exactly one** contains any
URL, and that one (`twin-self/…prediction-market-pattern.yaml`) cites Cowgill & Zitzewitz in support
of the narrative, not of the `credence: 0.6` or the belief numbers. Driftwood's own
`world/world_models/reference-map.yaml` carries 13 beliefs (0.45, 0.5, 0.25, 0.1, 0.15, 0.35, 0.08,
0.2, 0.12, 0.3, 0.4, 0.1, 0.18) with a note that says nothing about where they came from. No
invariant covers this (`grep world_model twin/invariants/*.py` finds only forecast-shape checks).

The system that refuses a hand-typed capability grade, refuses a hand-typed constraint-removal
number, and refuses a claim that names its own grade, accepts a hand-typed probability with no
witness at all. **No open ticket owns this.**

### F3 (major) — Everything the twin publishes sits outside every signed tag

`git -C units/driftwood ls-tree -r --name-only v1.1.0 | grep -c '^twin/'` → **0**. v1.1.0 is dated
2026-08-25; `twin/forward-intel/v1/feed.json` was added 2026-08-28 (commit 055e340, "ecosystem ticket
25"). v1.1.0's `composed/evidence.json` carries prices from `['ico', 'platform']` only — no twin
line. Driftwood's signed `party.yaml:62-66` states in its own words:

> The twin renders `twin/forward-intel/v1/feed.json` … Signed by the same gitsign tag as everything
> else here (ADR-0012), so **an untagged feed.json on a branch is never a signature**.

The feed is untagged, so by the party artefact's own rule it carries no signature. `feed.json`
contains no envelope signature of its own either, and the twin package's artefact signing
(`sign.py`) is HMAC from `TWIN_SIGNING_KEY`, which the package's README itself calls "a shared key
[that] proves possession, not identity". `twin/forward-intel/bump.yaml` reads `bump: none` — nothing
is queued. `twin/VERSION` is `0.1.0` and `twin/v0.1.0` is not cut (`PIN.yaml`, `VENDORED.md`:
`tag_cut: false`).

The north-star row says "signed by an agent identity". Today that is unmet at both levels.
**Owned by ticket 64 (open)**, which names M15/M16; the tag-tree evidence above is new.

### F4 (major) — The twin's clock has never once succeeded

`gh run list --repo policy-as-versioned-driftwood/driftwood --workflow twin-sweep.yml` returns
exactly two runs, both `schedule`, both `failure`: 33508119299 (2026-09-01T12:31Z) and 33627910027
(2026-09-02T12:04Z, i.e. after run 21's TRUTH line). `--log-failed` on today's run shows the step
declared `shell: /usr/bin/bash -e {0}` while the script body opens `set -uo pipefail`; `python3
twin/emit-forward-intel.py --check` exits 1 (`FAIL: twin/forward-intel/v1/feed.json is not what the
overlay renders`) and the job aborts before `rc=$?`, so the `moved=true` branch — the entire purpose
of the sweep — is unreachable. `set -uo pipefail` does not clear the `-e` on the shell invocation;
the fix needs `set +e` or `|| rc=$?`.

Consequence, checked directly: `units/driftwood/observations/` does not exist. The sweep has never
appended a single line. The workflow's own comment (`twin-sweep.yml:30-33`) also admits the sweep is
"the forward-intel re-render, the only twin output this repository has today… Ticket 29 lands the
scenario library and the scored sweep; when it does, this job runs `twin sweep`" — ticket 29 is
marked **resolved**, and `twin sweep` is not run by anything.

**Owned by ticket 72 (open)**, which names the `bash -e` cause precisely. The "never wrote an
observation" fact and the stale `twin sweep` ponytail are new here.

### F5 (major) — NORTH-STAR §4 step 5 has never happened, and the twin's own design excludes it from the clock

Step 5 names the niobium headline as the stimulus the twin plays forward *on its schedule*.
Driftwood's `twin/signals.yaml` declares `niobium-supply-shock-2026` under `unbound_scenarios`:

> A tier-one supplier failing to deliver arrives as a dated headline a human classifies with the
> classify-and-judge skill (ticket 50). Binding it to a pin here would be the twin deciding on the
> clock, which is the one thing this table exists to prevent.

That is a deliberate, well-argued reversal of step 5's mechanism — but step 5 was never restated.
The replacement mechanism has never run: feeds' `verify-news-headline-skill.sh` capture on run 21
says `ok  no adopter repo carries a claim file yet -- the skill has not been run for real`. The
scenario also has no outcome document anywhere in driftwood's overlay (`find … -name '*outcome*'`
returns nothing), so no driftwood forecast is scoreable even in principle.

**Owned by ticket 51 (open, frontier)**, "The supply-constraint actor path and the scored headline
forecast". Step 5's own north-star wording is not owned by anything and is now inaccurate.

### F6 (major) — The step-5 gate check grades file presence, and passed green in the same run in which the same artefact failed twice

`verify/e2e/verify-e2e-step5-twin-forecasts.sh` quotes step 5's sentence in its header and then says,
honestly, "This script does not pretend to look at a forecast". Its run-21 capture is seven `ok
<path>` lines plus the evals. In the *same* TRUTH run 21:

- `verify_e2e_verify-e2e-step5-twin-forecasts.out` → `PASS: … driftwood/twin/forward-intel/v1/feed.json
  (the feed the estate consumes) … ok`
- `.estate-clone_driftwood_verify-twin-overlay.out` → `FAIL: twin/forward-intel/v1/feed.json is not
  what the overlay renders`
- `.estate-clone_driftwood_twin_verify-twin-scenarios.out` → `TOTAL: 14 pass, 2 fail`, both fails on
  that same feed and the signal-lookup rows behind it

Two of run 21's seven fails are the twin's stale derived artefacts; the beat that narrates the twin
is green. The deck's beat title is "The twin plays a dated signal forward and is scored"
(`talk/narration.json`), which neither the script nor the estate proves.

**Owned by ticket 64** (REVIEW-2026-08-31's "minor step-5-presence-only") and **ticket 72** (the
reds). The green-beside-red-in-one-run pairing is new evidence that the presence check is
load-bearing on the deck.

### F7 (major) — The skill evals are saturated, tautological in at least one case, and their regression guard has never had two data points

`verify/twin-evals` run-21 capture: all seven metrics `score=1.000 … last=1.000`. Corpus sizes from
`twin/skill-scores.jsonl` (7 lines, one commit `f91a41c`, all `recorded_at 2026-08-13T00:00:00Z`):
23, 4, 4, 4, 3, 3, 5 — **46 labelled items in total**, all hand-built by the same author from the
same four backtest orgs the heuristics were fitted to, all scoring 1.0, never once moved.
`twin/skill-thresholds.yaml` states this candidly for every entry ("the heuristic scores 1.0 on its
own N-item corpus… set below that"), so it is disclosed, not hidden.

The sharpest case is not merely circular, it is tautological.
`twin/evolution_judge.py:71-85`'s `_MATURITY_KEYWORDS` is 14 phrases; the diagnostic ones are
`payment-acquiring / merchant acquiring` (Wirecard), `construction / support-services` (Carillion),
`hospital operations / healthcare` (NMC), `mark-to-market / energy trading` (Enron) — one phrase
uniquely identifying each of the four corpus orgs, mapping to the corpus label. The eval asks whether
a lookup table returns the value in the lookup table. Ticket 23's own facts section already recorded
this ("three of four corpus labels are literal keyword-table values", H5-08, GAPS 3.22).

Today's CI: invariant 15 `skill_score_log_is_append_only` **SKIP** — "the score-over-time log has
fewer than two committed versions; nothing to compare yet". So ticket 29's promise that "a fall in
any score against the last recorded value is a fail" has never been exercised.

GAPS 3.22 asked for disclosure and disclosure exists. **The circularity itself is owned by no
ticket.** Severity is major because `verify-twin-evals.sh` is the *only* twin quality signal on the
truth surface, and it is structurally incapable of moving.

### F8 (major) — The twin's price is the one pricing parent with no pin, no version resolution, no signature check, and a silent absence

`platform/compose/composition.py:1617-1631`, `_forward_intel()`: reads
`<adopter_dir>/twin/forward-intel/v*/feed.json` from the working tree, takes the highest major
directory, and its docstring says "**No feed at all is simply no twin entry -- never a refusal**".
Every other parent is pinned in `party.yaml`'s `inherits[]` with a version and a `since`, resolved
through `parent_trees`, and a missing instrument **refuses** under ADR-0020 (the same file raises
`Refused(f"missing instrument: …")` for a mismatched perspective and for an unnameable frequency
donor, three lines away).

The twin is therefore the only price line in driftwood's £ that can be deleted with no refusal, no
amber and no gate row. It is also the **largest** line: `composed/evidence.json` prices[] →
`{"source": "twin", "amount": 1897646.11, "per_customer": 7.91}` versus ico 1,787,177.08, insurer
113,403.30, feeds 19,558.55.

**No ticket found owning this.**

### F9 (major) — The £ → cage last mile is a hand-transcribed comment that nothing checks

`units/driftwood/gitops/apps/namespace.yaml` carries `posture.acme.io/tier: "isolated"` with a
comment explaining that this is "the strictest `proposed_tier` across today's composed/evidence.json
prices[] for this party". `grep -rln "proposed_tier"` across driftwood returns **nothing** —
no script, workflow or gate check in the adopter reads the composed `proposed_tier` and compares it
to the Namespace label. On the hub side only `verify/e2e/step2_reprice.py` and `step3_band.py` read
the field, and both operate on a `tempfile.TemporaryDirectory()` copy. `platform/compose/
composition.py` mentions `posture.acme.io/tier` only to assert it is *absent* from a pod section
(line 3179).

So the north-star seam "the £ selects the cage spec, the estate enacts it" is completed by a human
typing a word into a YAML file. The enactment beyond that point is real (driftwood's five-fact
sample for run 33624104359 reports 16/16 rendered objects present, byte-equal and in a Flux
inventory), but the binding between the priced tier and the enacted tier is unverified.

**No ticket found owning this specific binding.** Ticket 09's resolution says the check "is then a
Namespace-level check at compose time"; the check does not exist.

### F10 (minor) — The twin's contribution to driftwood's enacted tier is currently redundant, and the ladder cannot select anything but its bottom rung

Driftwood's own Namespace comment records that the ico penalty-schema line **and** the twin line both
land `isolated`, so deleting the twin's line changes no enacted tier today. Separately,
`party.yaml:43-44` declares `appetite.tolerance: {amount: 40000, currency: GBP}` against residuals
`{baseline: 1328352.28, restricted: 569293.83, quarantine: 151811.69, isolated: 37952.92}` — only the
tightest rung is under tolerance, by 5%. NORTH-STAR principle 2 says the £ *selects* the spec; on the
only adopter with a twin, the £ has exactly one admissible answer. Related to **ticket 74** (open,
"step 3 happens once for real"), whose ticket-60 comment already records "the proposer returned [] —
no band crossed".

### F11 (minor) — Only driftwood has a twin; ticket 29 is resolved claiming three

`ls units/tuppence/twin` and `ls units/ludlow/twin` → no such directory;
`grep -c twin units/{tuppence,ludlow}/composed/evidence.json` → 0 for both. Ticket 29's Answer states
"the six standing scenarios exist per adopter". **Owned by ticket 64 (open)**, which also requires a
dated correction to ticket 29 — the correction has not been written into ticket 29.

### F12 (minor) — The honesty register cannot currently be shown to work

Today's CI: invariant 56 `does_not_do_register_is_generated_never_typed` → **SKIP**, "every loaded
capability is already `full`; there is nothing left to check off". With 73/73 at `full`,
`does_not_do.py`'s register is empty and indistinguishable from a register that would be empty
whatever the state. This is the twin map's own open question, confirmed.

### F13 (minor) — The only real statistics in the package price nothing

`twin/severity.py` (lognormal body spliced to a GPD tail, closed-form TVaR, refusal when `xi >= 1`)
is genuine, tested, and honest about its parameters (invariant 40 today: "3 anchored (mu, sigma,
threshold), 2 unanchored (beta, xi)"). It is reachable only through the `lm` lognormal-GPD payload
shape that `forward-intel/payload.schema.json:54-62` describes — and driftwood's feed emits the
bounded triple instead (`"tail": "bounded-pert"` in `evidence.json`). `emit-forward-intel.py:236-240`
says why: "this overlay carries no own-data observations and no world-layer prior to fit one from".
So the twin's tail model contributes no number to any price in the estate.

### F14 (minor) — `twin grade` still prints a green aggregate with no reference to the suite state

GAPS 2.13 asked for two changes: stamp the aggregate `SUITE RED` when `twin verify` fails, and print
the live enact mode beside `enactment`. The second is effectively done (`twin/ENACT_MODE` now reads
`operations`). The first is not: `grep -rn "SUITE RED" twin/*.py` finds only a prose mention inside
`enact_guard.py`, and `twin grade` printed `aggregate: 73 of 73 across 13 capabilities, 13 at full`
for me with no suite line, while the suite is red in CI.

### F15 (minor) — The deck's honesty slide names the wrong standing red

`talk/narration.json`, "Honesty over green": "it does not run the twin's python test suite, which
carries one standing red of its own — **the drift window is open and its newest sample is weeks
old**". Today's CI: invariant 43 `drift_window_is_actually_being_sampled` → **PASS**, "9 sample(s) in
an open window, newest 2026-09-01, 64 day(s) left". The actual standing red is
`flux_coverage_floor_is_still_reachable`. The disclosure is stale in a slide whose whole subject is
disclosure accuracy.

### F16 (minor) — `author: "ai-generated"` is still stamped by arithmetic with no model call, after ticket 23 decided it retires

`platform/wardley/wardley.py:202` and `:219` set `r["author"] = "ai-generated"` on records produced by
`factor = 1.0 + ATTACK_COST_COLLAPSE_K * movement` and its reciprocal. No model call exists anywhere
in the eight unit repos or in `twin/` (checked by grep for anthropic/openai/LLM; every hit in `twin/`
is a docstring naming a future "swap the body for a model call" upgrade path).
`wargamer/wargamer.py:270` *asserts* that both `human-seed` and `ai-generated` authors are present,
so the label is enforced rather than merely tolerated. Ticket 23's Consequences say "`author:
ai-generated` retires when the skill lands"; ticket 23 is **resolved**, ticket 50 (build the skill)
is **resolved**, and the skill has never been run for real (F5), so the retirement is stranded
between three closed tickets.

### F17 (minor) — A truth-surface PASS line reads as a Polymarket observation of an illustrative fixture

`verify-news-headline-skill.sh`'s run-21 capture: "the largest is +0.03: polymarket price for
'0x9ad402' moved from 0.58 to 0.61 (up) between 2026-08-27 and 2026-08-28". The underlying corpus
(`feeds/fetch/source/market-moves.json:2`) states "The seven markets below are ILLUSTRATIVE… this is
not a fetch of Polymarket", and the published envelope repeats it in its `payload.note` — but the
envelope's top-level `venue: polymarket` and `source: https://gamma-api.polymarket.com/markets`
fields, and the gate's PASS line, do not. To the credit of the same script, the line immediately
below it proves the level-is-not-a-probability refusal fires for real.

### F18 (minor) — GAPS 2.14's remedy is half-applied in the estate's only £ back-test

`platform/honesty/incidents.json` now discloses in its top note "Authored so the estate exercises
BOTH recalibration directions". The per-org `source` fields were not changed and still read as real
registers for fictional companies: "driftwood SecOps incident register + WAF blocked-skimmer counts",
"tuppence fraud-ops loss ledger + FCA reportable near-misses", "ludlow HIPAA breach log + break-glass
audit". GAPS 2.14 named "three string changes (note, source, banner)"; one landed. Adjacent to this
dimension because it is the estate's only £-calibration back-test and it is the mechanism the twin's
real scoring machinery is *not* connected to.

### F19 (minor) — Stale self-descriptions in the sweep's own observation record

`twin-sweep.yml:145` writes `"twin_ref": "policy-as-versioned-flux@main -- the twin package does not
self-version yet (ticket 29)"`. The twin does self-version: `twin/VERSION` is `0.1.0` and
`verify-twin-evals.sh` asserts it ("twin self-versions: twin/VERSION=0.1.0,
twin.TOOL_VERSION=0.1.0"). Harmless today only because the line has never been written (F4).

## 4. Instrument faults vs estate faults

- **Instrument fault:** F6 (step 5 grades presence, not the property it quotes), F7 (the only twin
  quality metric on the surface cannot move), F14 (`twin grade` reports green regardless of the
  suite).
- **Estate fault:** F3, F4, F5, F8, F9, F10, F11, F16, F17, F18.
- **Design shortfall against the ambition, neither a bug nor an instrument fault:** F1, F2, F13.
- **Correctly-reported red:** the two driftwood twin fails in run 21 are real, named, ticket-owned
  estate defects, exactly as ticket 55's rule requires. The truth surface is telling the truth about
  them.

## 5. Built-and-proven-on-a-citable-run vs built-and-proven-locally vs asserted

| Claim | Status |
|---|---|
| Brier 0.9025 on a real cited outcome | proven on run 21 (`verify-twin-evals` PASS, "three real-firm beats") **and** reproduced by me locally |
| 73/73 capabilities at `full` | proven locally by me; on the citable run only via the evals wrapper |
| 70/1/3 invariants, 1550 tests | proven on hub `twin.yml` run 33615039125, today, on a live runner (workflow conclusion is failure, by design) |
| cross-architecture determinism | proven on the citable run (`verify-twin-evals`) and on the 3-way CI matrix today |
| "the twin plays a dated signal forward on its schedule" | **asserted**; never observed (F4, F5) |
| "signed by an agent identity" | **asserted**; falsified for the published feed (F3) |
| "the twin computes a cage tier the estate enacts" | half-proven: the price and `proposed_tier` are computed and the tier is enacted, but the binding between them is a comment (F9) and the twin's number is not decisive (F10) |
| the six skills' scores | proven on the citable run, but the metric is saturated and tautological (F7) |

## 6. Test count vs code size

`twin/*.py` + `twin/invariants/*.py` = 33,872 lines; `tests/*.py` = 18,623 lines across 82 files with
1,326 `def test_` functions and 1,550 collected tests. Roughly one test per 22 lines of source — a
genuinely high ratio, and the tests are behavioural (they run the CLI end to end, AST-scan real
source, and construct negative controls that must fail).

Set against that: the twin's total contribution to the estate is one 41-line JSON feed for one
adopter, containing three `lm` numbers and four `curve` rows, derived from two authored constants
(£3,200,000 × {0.06, 0.12, 0.25}), currently stale, currently red on two gate checks, outside every
signed tag, and produced by a clock that has never succeeded. The eval corpus behind the twin's only
published quality metric is 46 hand-authored items.

## 7. The smallest honest claim about the twin today

> The twin is a working, well-tested, self-auditing **apparatus for scoring beliefs**: it rewinds a
> model repository to a declared time, withholds facts by construction rather than by review, refuses
> to score what it cannot honestly score, applies real proper scoring rules, and reports a red result
> first. Applied to Royal Mail's real 2013 prospectus and its real 2019 concession, an authored prior
> of 0.05 scores Brier 0.9025 — worse than a coin flip — and the apparatus says so. It does not yet
> forecast: no code path turns a signal into a probability, and no adopter's scenario has an outcome
> to score. Its one connection to the estate is a single unsigned, currently stale, untagged JSON
> feed whose two authored numbers become driftwood's largest price line and are transcribed by hand
> into an enacted cage tier that would be the same without them.

Everything in that paragraph is checkable in one sitting. Anything larger than it — "the twin
forecasts", "the twin is scored against reality", "the twin plays the niobium headline forward on a
clock", "the twin computes the cage the estate enacts" — overstates what run 21 and today's CI show.

## 8. Fitness for purpose

**Not fit yet, for a specific and fixable reason, plus one that is a decision rather than a fix.**
The instrument half of the north-star's twin row (proper scoring rules, agent attestation shape,
regimes, contestability, adversarial substrate, non-fakeable grading) is built to a standard well
above the rest of the estate. The evidential half — a probability that is derived, a published
artefact that is signed, a clock that runs, a seam whose last mile is checked — is not. Four of my
nine major findings (F3, F4, F5, F6) are already owned by open tickets 51, 64 and 72 and are
finishable this week. Three (F2, F8, F9) are unowned and small: a required `evidence_grade`+`basis`
on a world model, a `Refused` when a declared `publishes[]` feed is absent, and one check comparing
`proposed_tier` to `posture.acme.io/tier`. F1 and F7 are not patches — they are the two questions
only the owner can answer.
