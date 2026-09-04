---
name: classify-and-judge
description: Classify the unbound pool (the news and market-moves feeds) against one adopter's twin overlay and, where the human judges a move, record an evolution override — as one reviewed PR on that adopter's own repo
disable-model-invocation: true
---

# classify-and-judge

The twin's `signal-classify` and `evolution-judge`, packaged as **one skill a human runs**
(ecosystem tickets 23 and 50, ADR-0024). It reads the pool the `feeds` repo publishes, proposes a
binding and an evolution position for each entry, takes the human's judgement where he has one,
and writes **one claim file** that lands as a **pull request on the adopter's own overlay**.

**Nothing here ever runs on a GitHub clock.** `disable-model-invocation: true` in the frontmatter
above is not decoration: it is the mechanism. The daily publisher fetch
(`feeds/.github/workflows/fetch.yml`) gathers readings and computes a bump with a rule file; the
adopter's daily sweep reads a committed lookup table (`twin/signals.yaml`). Neither calls a model,
and neither may invoke this skill. Reasoning is a human at a keyboard, and its output is a claim
somebody merges.

**Amended 2026-09-03 (ticket 92; ticket 75 Q10, the owner, reasoned).** The sentence above used
to read "Nothing here ever runs on a clock." The owner permitted a model in the twin on one
condition: it runs inside Claude Code on his machine, from a schedule or shell script he runs,
because no tokens exist anywhere else. So there is now a third clock, `talk/local-clock.sh`, and
it invokes this skill headlessly as `claude -p "/classify-and-judge <adopter>"`. That is a *user*
invocation from the owner's own machine under the owner's own login -- the thing
`disable-model-invocation: true` still forbids is the model deciding to run this skill, and
Claude Code's own scheduled-task preload; both stay forbidden. What changes in a headless run,
and why it is still "a claim somebody merges": there is nobody at the keyboard, so the run writes
**no override** (an override is a human's judgement claimed by a role; the validator refuses one
from a run marked `headless`), leaves every "stop and ask" item unbound with its reason, and
still commits on a branch and stops. The PR body sentence in step 5 is now "no model ran on a
GitHub clock to produce this; it ran on the owner's local clock" for such a run.
`talk/local-clock.headless.md` is the note the clock appends to the system prompt and is the
authority on what a headless run may do.

**Two things this skill may never do:** merge its own PR, and invent an entry. If a statement is
not in the published pool with a URL, it does not become a signal here — it is a **scenario**, and
scenarios live in the adopter's `twin/orgs/<org>/scenarios/` library. The niobium supply shock is
the standing example: it is in driftwood's library, it is not in the news feed, and this skill does
not put it there.

## 0. Inputs

Ask for the adopter if it was not named. Then gather, and print, each of these before doing
anything else:

| input | where |
|---|---|
| the adopter's overlay | `<adopter>/twin/orgs/<org>/` — components, people, edges, scenarios |
| the pins | `<adopter>/party.yaml` `inherits[]` — the exact `{party, kind, name, version}` rows |
| the news pool | `feeds/news/v<MAJOR>/feed.json` at the **pinned** version |
| the market series | `feeds/market-moves/v<MAJOR>/feed.json` at the **pinned** version |
| the bound signals | `<adopter>/twin/signals.yaml` — what the clock already binds by lookup |
| the role register | `twin/roles.yaml` in the hub — an override is claimed by a **role** |

Read the version off each envelope, not off a directory name. An entry that is already bound in
`signals.yaml` is **not** in the unbound pool: the clock owns it, and a second binding here would
be a duplicate claim.

Done when: you can state the two feed versions, the adopter, and how many pool entries are unbound.

## 1. Derive the moves — never the levels

For market-moves, the series is what is published and a **move** is what a consumer derives:

```
python3 - <<'PY'
import json, sys; sys.path.insert(0, ".")   # the hub root, where the twin package lives
from twin.market_signals import PriceObservation, price_moves, move_statement
feed = json.load(open(".estate-clone/feeds/market-moves/v1/feed.json"))
obs = [PriceObservation(mid, m["venue"], p["date"], p["price_level"])
       for mid, m in feed["payload"]["markets"].items() for p in m["observations"]]
for move in price_moves(obs):
    print(move.to_date, f"{move.delta:+.2f}", move_statement(move))
PY
```

A price **level** is never a probability. `twin/market_signals.as_probability` refuses outright,
and so do you: the favourite-longshot bias makes a level a biased estimator of unknown scale,
worst in exactly the low-price tail this estate prices tail risk from (twin research 17 S3.1).
Consume the derivative, and say "moved from 0.44 to 0.52", never "a 52% chance".

Done when: you have a list of dated move statements and a list of dated news statements, each with
its source and its provenance URL.

## 2. Classify — one statement at a time, with the human reading each

For each unbound statement, propose:

- the **STEEP** tag (`social, technological, economic, environmental, political`), and
- the **component** in the adopter's overlay it binds to, from the overlay's own component ids.

`twin/signal_classify.py::classify` is the committed heuristic stand-in and it is fitted to four
historical fixtures. Use it to see the shape, then **do the classification yourself and show the
human both**, including where you disagree with it. Every binding you write is `evidence_grade: 5`
— the ladder's weakest rung, "a claim with no independent corroboration" — and it is contestable
downstream. It informs and ranks. **It does not price.**

Stop and ask when: no component is a good fit (say so and leave it unbound, with the reason), or
two components fit equally (the human picks).

Done when: every statement is either bound to one component with one STEEP tag, or explicitly left
unbound with a reason.

## 3. Judge the evolution position — and let the human overrule you

For each component a binding touched, infer its evolution position from the accumulated evidence
(`twin/evolution_judge.py::judge`, grade 5, kind `position`), state it to the human with your
reasoning, and ask whether he judges it differently.

If he does, write an `override`:

- `kind: override`, `evidence_grade: 4` ("calibrated expert judgement, named by role"),
- `claimed_by` a role id **in `twin/roles.yaml`** — never a person's name, never free text,
- an **absolute** `evolution_position`, not a delta,
- `answers` naming the `position` claim it overrules, so the twin's own estimate is retained
  beside it and the disagreement is on the record (`evolution_judge.pushback`),
- the **headline itself in `evidence`** — the dated statement and its URL.

**Only the override prices.** It is the one claim in this file a £ path may read, and it is priced
under the adopter's own perspective by composition, never here. The machine proposes; the role
disposes; the role is scored later against what happened.

Done when: every touched component has an inferred position, and every position the human
disagreed with has an override answering it.

## 4. Write the claim file

One file, in the adopter's repo:

```
<adopter>/twin/claims/<YYYY-MM-DD>-<slug>.claim.yaml
```

Its shape is `assets/example-claim.yaml` beside this file, and `assets/validate_claim.py` is what
the gate runs over it. The rules the validator enforces, so you write them right the first time:

- every claim's `kind` is one the twin already has (`binding`, `position`, `override`,
  `enactment`) — a skill never invents a claim kind;
- `derived_from` names **every pin** the claims were derived from, in `inherits[]` shape, and
  every pin a claim cites is in it — provenance reads the same way on both sides of the seam;
- a `binding` names its signal and carries no `evolution_position`; a `position` and an `override`
  carry one and name no signal (`twin/schema.py::_refine_claim`);
- `price_eligible: true` appears on overrides and nowhere else.

Validate before you open anything:

```
python3 .claude/skills/classify-and-judge/assets/validate_claim.py <the claim file> --twin .
```

Done when: the validator exits 0 and prints the claim count.

## 5. Open the PR — and stop

Branch in the **adopter's** repo, commit the claim file only, open a pull request, and stop. The
PR body carries: the two feed versions read, the count of statements classified, each override with
its role and its headline, and the sentence "no model ran on a clock to produce this" -- or, from
the local clock (amendment above), "no model ran on a GitHub clock to produce this; it ran on the
owner's local clock (ticket 92); no override is claimed".

**Never** merge it. **Never** tag. **Never** touch `signals.yaml`, `composed/`, `deploy/`,
`gitops/` or any other declaration in the same PR — a claim is a claim, and one of those is a
declaration a different review owns.

Done when: the PR is open and its URL is reported to the human.

## What this skill does not do

- It does not price. Composition prices, under the adopter's perspective, from the override.
- It does not bind what the clock already binds by lookup.
- It does not decide the twin is right. `pushback` keeps both claims; the score comes later.
- It does not add an entry to any feed. A statement with no URL is a scenario, and the scenario
  library is somewhere else.
