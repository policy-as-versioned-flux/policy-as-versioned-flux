---
name: derive-probability
description: Derive a probability for each of one adopter's standing scenarios from the served pool's dated observations and the world model's recorded belief, state its basis, grade and signals, and write one forecast file that lands as a reviewed PR on the adopter's own repo
disable-model-invocation: true
---

# derive-probability

The twin's forecast, packaged as **one skill the local clock runs** (ecosystem ticket 93; ticket
75 Q10, the owner, reasoned: the twin may derive a probability with a model call, and the model
runs inside Claude Code on the owner's machine because no tokens exist anywhere else). Until this
skill every probability the twin scored was a number read from YAML -- a world model's `beliefs`
-- and the package said so at run time. This skill reads the adopter's scenarios, the world
model's recorded belief for each, and the dated observations the pool serves, and writes **one
forecast file** that says, for every scenario, what the probability is, whether it was
**derived** from named observations or is the **recorded** belief unchanged, which perspective
and currency it is a forecast for, and the evidence grade the schema allows.

**How it runs.** `talk/local-clock.sh --step derive --adopter <adopter>` invokes it as
`claude -p "/derive-probability <adopter>"` on a branch cut from the adopter's `origin/main`, with
`talk/local-clock.headless.md` appended to the system prompt; that note is the authority on what a
headless run may do. `disable-model-invocation: true` forbids the model choosing to run this skill
and Claude Code's own scheduled-task preload; a user invocation, by hand or from the owner's
schedule, is what runs it. A human can also run it at the keyboard, and the same validator grades
the file either way.

**Two things this skill may never do:** price anything, and choose the outcome date. A derived
probability is a model assertion, grade 5, outside the ladder's `pricing_threshold`; the
scenario's `horizon` is the outcome date, and the artefact copies it so the validator can check it.
And two more, inherited: never merge its own PR, and never invent an observation. If a statement
is not in a served envelope, it is a **scenario**, and scenarios live in the adopter's
`twin/orgs/<org>/scenarios/` library.

## 0. Inputs -- read the listing, not the feeds

Ask for the adopter if it was not named. Then, from the hub root:

```
python3 -m twin.derived_forecast inputs --adopter <adopter checkout> --org <org> --feeds .estate-clone/feeds
```

(In a headless run the adopter checkout is the clock's worktree, named in the note; the feeds are
under the estate the note names.) The listing is deterministic and it is the whole of what a
derivation may rest on:

| field | what it is |
|---|---|
| `scenarios[]` | every standing scenario: `id`, `proposition`, `at`, `horizon`, `components`, `world_models`, and `recorded_beliefs` -- the number each named world model carries for the proposition |
| `pool.market-moves.moves[]` | every consecutive dated **move** in the served `market-moves` envelope, as `twin/market_signals.py` derives it: `market`, `venue`, `from_date`, `to_date`, `from_level`, `to_level`, `statement` (the move's own sentence), `from` (the envelope in `inherits[]` shape) |
| `pool.news.events[]` | every dated event in the served `news` envelope: `event`, `date`, `source`, `statement`, `url`, `from` |
| `perspectives` | each perspective in the overlay and the currency it prices in (`twin/currency.yaml`) |
| `subscribed` | whether the adopter's `party.yaml` pins each pool feed. On 2026-09-06 no adopter pinned either and the publisher had cut no signed tag for either: the pool is served unpinned and untagged, which is why nothing derived from it is price-eligible (ticket 23) |

Print the listing's counts before doing anything else: how many scenarios, how many moves, how
many events, and which pool feeds are subscribed.

Done when: you can state the served version of each pool feed, the adopter, and how many
scenarios carry a recorded belief.

## 1. For each scenario, decide the basis -- one scenario at a time

Read the scenario's `question`, its `components` and its `recorded_beliefs`. Then read every move
and every event in the listing and decide which, if any, **bears on this scenario's components**.
That is a judgement; make it one observation at a time and say why.

- **Nothing bears on it:** the basis is `recorded`. The probability is the world model's number,
  **unchanged**, named in `recorded_belief`, with no `signals`. It carries `evidence_grade: null`
  and `grade_absent_because` (the world-model schema carries neither a source nor a grade for a
  belief, and the ladder has no rung for an unsourced authored number -- a finding the artefact
  records; see `assets/example-forecast.yaml`). Say in `reasoning` that nothing bore on it.
- **Something bears on it:** the basis is `derived`. Start from the recorded belief, state in
  `reasoning` how each named observation moves it and to where, and give the probability as
  **your judgement**, strictly between 0 and 1. Keep the world model's number beside it in
  `recorded_belief`, the way an override keeps the position it answers, so the disagreement is
  on the record and both are scored.

Three rules, each of which the validator enforces because each is a way to lie with a number:

1. **A market level is never a probability.** `twin/market_signals.as_probability` refuses
   outright, and so do you: the favourite-longshot bias makes a level a biased estimator of
   unknown scale, worst in the low-price tail this estate prices tail risk from (twin research
   17 S3.1). Consume the **move** -- "moved from 0.40 to 0.45" -- and never write "a 45% chance".
   A signal carrying `probability` or `implied_probability` is refused.
2. **No arithmetic on ordinal grades.** Every observation you rest on is grade 5 (a feed
   observation read with nobody at the keyboard, the same rung `twin/feed_signal.py` gives a
   lookup). Your derivation is **no stronger than the weakest thing it rests on** -- a
   comparison, which the ladder admits -- and it is a model assertion, so it is grade 5. Grades
   are compared, never summed, averaged or weighted: a signal carrying `weight` or `score` is
   refused, and a derived probability whose grade is lower than its weakest signal's is refused.
3. **The outcome date is the scenario's.** `resolves_on` is the scenario's `horizon`, copied.
   You do not pick it, and a forecast merged on or after it is not scored (section 4).

Stop and ask when: two world models the scenario lists disagree and you cannot say which the
recorded belief is (name both in `reasoning` and use the first listed); or an observation
plainly bears on a component the overlay does not carry (say so and leave the scenario
recorded). In a headless run, do not ask: do what the parenthesis says and record the reason.

Done when: every scenario has a basis, a probability, and a reasoning that names each
observation it rested on by the fields the listing gave you.

## 2. Write the forecast file

One file, in the adopter's repo, **beside** `twin/claims/` and never under `twin/orgs/<org>/`
(the overlay loader refuses a directory it does not read, so a `forecasts/` collection there
would fail the adopter's twin gate):

```
<adopter>/twin/forecasts/<YYYY-MM-DD>-<slug>.forecast.yaml
```

Its shape is `assets/example-forecast.yaml` beside this file. The rules the validator enforces,
so you write them right the first time:

- `schema: twin.derived-forecast/v1`, `org`, and a `run` block naming `skill: derive-probability`
  and an `operator_role` from `twin/roles.yaml` (`model-steward` on the clock);
- `derived_from` names **every served envelope** a signal came from, in `inherits[]` shape, by the
  envelope's own `name` and `version`; every envelope named is cited by a signal and every signal's
  envelope is named;
- every forecast carries `scenario`, `proposition`, `resolves_on` (the scenario's horizon),
  `perspective` (in the overlay's `perspectives/`), `currency` (what that perspective prices in),
  `probability` strictly in (0,1), `basis`, `price_eligible: false`, `prices_through`,
  `recorded_belief` and `reasoning`;
- a `derived` forecast has `evidence_grade: 5` and at least one signal; each signal is a
  `market-move` (`market`, `venue`, `from_date`, `to_date`, `from_level`, `to_level`, the move's
  own `statement`) or a `news-event` (`event`, `date`, `url`, the event's own `statement`), with
  `evidence_grade: 5` and `from`; the validator confirms **the served envelope carries that
  observation**, and one it does not carry fails the file;
- a `recorded` forecast has `evidence_grade: null`, `grade_absent_because`, no signals, and a
  probability equal to `recorded_belief.probability`, which must be what the named world model
  carries for the proposition.

Validate before you commit:

```
python3 .claude/skills/derive-probability/assets/validate_forecast.py <the forecast file> --twin . --headless
```

(`--headless` on the clock; at the keyboard, without it.) Exit 0 prints the count of derived and
recorded probabilities and the envelopes cited; exit 2 means the validator could not read the
served feeds, and a file nobody could check is not proposed.

Done when: the validator exits 0.

## 3. Open the PR -- and stop

Branch in the **adopter's** repo, commit the forecast file only, and stop. On the clock the branch
is already made and the PR title and body go to the files the headless note names; at the
keyboard, open the pull request yourself. The body carries: the served version of each pool feed,
the count of scenarios, for each derived probability the recorded belief it moved from, the
probability it reached and the observations it rested on, the count of recorded beliefs, and the
sentence "A model ran on the owner's local clock (ticket 92), not on a GitHub clock; no override
is claimed; nothing prices; the clock never merges." (or, at the keyboard, "no model ran on a
clock to produce this").

**Never** merge it. **Never** tag. **Never** touch `twin/orgs/`, `signals.yaml`, `composed/`,
`deploy/`, `gitops/` or any other declaration in the same PR.

Done when: the PR is open, or its title and body are written for the owner to push.

## 4. What happens after -- pre-registration and the score

Neither is this skill's to write, and both are read off things the twin does not control:

- **Pre-registration is git history.** The forecast is pre-registered on the date the merge
  brings the file onto the adopter's `main` -- the first-parent commit on `origin/main`, dated by
  whoever merged it -- and only when that date is strictly before the outcome date. A field the
  twin writes (`run_at`, `derived_at`) is never what decides it. Propose early.
- **The outcome is a human's observation**, recorded in the overlay's own `outcomes/`
  collection (`twin/schema.py` `outcome`: `proposition`, `observed`, `resolved_on`, `source`,
  `contamination`, `source_dated`) and merged by a human on or after the date it resolved.
- **The score is computed by the gate**, `verify/twin-evals/verify-derived-forecast.sh`, with
  `twin/scoring.py`'s proper rules (Brier and log loss), from the pre-registered forecast and the
  outcome, and never read from a file. A probability that was not pre-registered is not scored.

## What this skill does not do

- It does not price. `price_eligible` is false on every forecast; the £ path is composition
  under the perspective, through a causal path graded inside `path_admission_threshold`.
- It does not write an outcome, and it does not score itself.
- It does not touch the world model's `beliefs`. A recorded belief is read, never rewritten.
- It does not add an entry to any feed, and it does not turn a scenario into a signal.
- It does not choose the outcome date.
