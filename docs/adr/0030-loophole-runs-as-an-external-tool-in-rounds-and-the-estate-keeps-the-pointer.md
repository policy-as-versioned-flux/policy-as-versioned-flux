---
status: accepted
---

# loophole runs as an external tool, in rounds, and the estate keeps the pointer and throws the sentence away

Decided 2026-09-22 by the assistant under
[ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md), labelled delegated.
Wayfinder ticket 09, on the map
[Laya, loophole and the trdrbot prior art, measured then decided](../../.scratch/laya-loophole/map.md).
Supersedes nothing.

## Context

loophole is an adversarial agent loop. It attacks a norm stated in prose, and it looks for
scenarios that are legal but immoral and scenarios that are illegal but moral. This estate's norm
documents are its ADRs, so the question was whether attacking one finds real holes.

**The range of outcomes was narrowed before any measurement, and by a fact rather than by a
score.** loophole carries **no licence at all**, verified four ways by ticket 06, and it was last
pushed on 2026-06-03. All rights are reserved. So it can never be vendored, forked into the
estate, or reimplemented from its prompts. The only adoption available is **an external tool a
human runs from a clone that stays outside the project tree**. Running a clone on the owner's
machine is not distribution; committing its source, its prompts, or a close reimplementation is.
The residual risk is stated rather than hidden: GitHub's terms grant viewing and forking within
GitHub, and a local clone sits outside that grant. The call is to evaluate and never distribute,
because evaluation is the whole purpose.

### What was measured

Three rounds ran against
[ADR-0022](0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md), the cage
ladder, at the same pin, with the same harness by sha256 and the same inputs.

- **A round costs 8 model calls, about 180 s, and about 0.41 USD at list price**, which the
  subscription absorbs. Ticket 07 measured 0.4150, ticket 11 rounds two and three 0.4069 and
  0.4197: stable to 3%. Three rounds cost 1.2416 USD. The published loop costs 14 calls; the 6
  extra are the Legislator, which this estate does not run.
- **Each round produced 6 candidates, 3 loophole and 3 overreach, with 0 parse failures and 0
  under-production.**
- **2 of round one's 6 candidates survived a deterministic check against the code: a survival
  rate of 33%.** Both survivors lost the mechanism the model named and kept only the place it
  pointed at. Three of the four discards are false against the code, not merely unproven.
- **The overlap between any two rounds is 1 to 3 candidates of 6.** By reason the pairwise
  overlap is 2, 1 and 3; by clause 2, 2 and 3. All three rounds share exactly one reason and two
  clauses. No two of the 18 candidates share a run of 8 consecutive words, across all 153 pairs.
- **The tool repeats its target and never its mechanism.** The `infra` declaration is attacked in
  every round, by four candidates, and no two give the same reason.
- **One round reads about 23% of what the tool has to say about a document.** Three rounds gave
  13 distinct reasons from 18 candidates, and Chao1 on the frequencies estimates the population
  at 26.5. That is a lower bound from three samples of six, with a wide interval, and the
  population is the tool's output rather than the document's real defect set.
- **The overlap number is itself a draw.** An independent reader, asked the same question three
  times with the candidates anonymised and shuffled, named no pair in all three repeats for
  rounds one and two. Its mean unanimous overlap is 1 of 6 against the assistant's 2 of 6.

The two survivors are real defects in this estate, and both are now held by
`tests/test_cage_ladder_holes.py` across nine legs, measured under the pinned kyverno 1.18.2.
They entered `twin/ecosystem-misuse-catalogue.yaml` at version 4 and graduated as eco-system
tickets [113](../../.scratch/ecosystem/issues/113-the-infra-declaration-is-read-by-no-served-policy.md)
and [114](../../.scratch/ecosystem/issues/114-an-unobserved-party-does-not-leave-the-walk-green.md).

## Decision

### 1. loophole enters as an external tool a human runs, and is never vendored

No licence permits any other shape. The clone lives in the scratchpad, outside the project tree.
The estate commits **its own harness** and **the tool's output**, never the tool.

### 2. The unit of adoption is three rounds against one document, not one run

One round is one draw and reads about 23% of the tool's population. Three rounds read roughly
half of it, by the same Chao1 estimate, and three is **not enough to fix that number** — the
interval is wide and the estimate rests on three samples of six. Three is chosen because it is
the point at which the measurement showed the tool repeating a *place* while never repeating a
*mechanism*, which is the property a reader needs. A later run may re-measure it, and a run that
does states its own number.

Budget for one document: **24 model calls, about 9 minutes and about 1.24 USD at list price**,
absorbed by the subscription. That is not the real cost. The real cost is the deterministic
check: ticket 08 checked six candidates and that was a whole ticket's work. **Three rounds
produce about 18 candidates and about 6 real defects at the measured survival rate, and checking
18 candidates costs roughly three times ticket 08.** Anyone who budgets the model calls and not
the checking has budgeted the cheap half.

### 3. The human keeps the pointer and throws the sentence away

Both survivors kept the place the candidate pointed at and lost the mechanism it named. Neither
would have graded as real if the question asked had been "is this scenario true as written", and
neither would have been found if the pointer had been discarded for being wrong. So the rule is:
**test the place, never the sentence**, and count the survival rate on the candidates **as
stated**, so the tool is not flattered by the checking's own work.

Round three's `loophole-1` is the clean illustration from the other direction: it is false as
written against the supplied document, and the place it points at is real and is already
eco-system ticket 113.

### 4. The Legislator never runs, so no model rewrites a norm document

loophole's published loop drafts the legal code and revises it after every resolved case, so
cases 2 to 6 are judged against text a model wrote. This estate supplies its real ADR and holds
it fixed for the whole round. Two reasons: the target stays the estate's own document, and the
six verdicts stay comparable. It also costs 6 fewer calls. This is the shape of adoption, not a
tuning choice.

### 5. The judge's verdict is not a filter and may never be presented as one

loophole's judge called **17 of 18 candidates resolvable** across three rounds, and ticket 08
then found 3 of round one's 5 resolvable candidates false against the code, and the single
unresolvable one false too. A near-constant verdict separates nothing. **Every candidate goes to
the deterministic check whatever the judge said.** This is the same defect
[ADR-0029](0029-a-candidate-model-enters-on-a-measured-permission-and-laya-does-not-hold-one.md)
point 5 refuses in Laya's `act_probability`: two unrelated tools, one defect.

The judge carries the same silent failure in a second place: `agents/judge.py:62-63` reads a
missing `<verdict>` tag as the literal verdict "unresolvable".

### 6. `--bare` never appears in the invocation, and a clean run needs two counters at zero

- **The guard, not the flag.** `claude -p --bare` never reads OAuth, so with no
  `ANTHROPIC_API_KEY` the call fails with **exit code 0**, `subtype: "success"`, `is_error: true`
  and `result: "Not logged in · Please run /login"`. The obvious adapter hands that sentence to
  the parser, which returns zero candidates, and loophole then prints that the legal code appears
  robust. **A broken login reads as a clean bill of health.** The harness asserts on the failure
  shape rather than trusting the flag, because the next flag with this property will have a
  different name.
- **Two counters, not one.** The `<scenario>` tag counter catches a malformed tag and **misses a
  total format collapse**: a model that abandons the format opens no tag, so the parse-failure
  count reads 0 and the candidate count reads 0. The under-production counter catches that case.
  A clean run needs **both** at zero, and a negative control fires each of them.

This is the estate's own defect class, eco-system ticket 98, found in somebody else's code: **a
tool that cannot report its own failure is not measured, it is trusted.**

### 7. The estate keeps loophole's output and never its input

Every system prompt and user message in a run is loophole's own prompt text verbatim, and
loophole carries no licence. The committed log holds the **responses** and a **sha256 of each
prompt**. The unredacted copy stays in the scratchpad.

`.scratch/laya-loophole/bench/check_no_prompt_leak.py` proves it and is reusable: it takes every
run of 8 or more consecutive words from `loophole/prompts.py`, normalises case and whitespace,
and searches the committed files. It finds **1,287 distinct runs**, fires on all 1,287 against
the source itself as a negative control, and finds **0** in all six committed files across the
three rounds. **Any later round runs this check before its files are committed.**

### 8. loophole never becomes a gate check

Its output is non-deterministic, and a non-deterministic instrument cannot grade the truth
surface. It is a generator. What reaches the gate is the **deterministic check a survivor earns**
— `tests/test_cage_ladder_holes.py` for the two survivors — behind a reviewed pull request.

### 9. What a round writes down

A committed round carries: the target document and its commit, the harness sha256, the model
served, the call count, the wall time, the list price, both counters, every candidate with its
verdict, and the prompt digests. Ticket 07's and ticket 11's three summaries are the shape.
One flaw is recorded rather than patched: all three `summary.json` files carry `"ticket": "07"`,
because the harness is a constant and ticket 11 demanded the same harness by sha256. Read that
field as "written by the ticket 07 harness".

## Options considered

**Does loophole enter?**

- **Yes, as an external tool run in rounds (chosen).** It found two real defects in this estate's
  cage ladder for about 1.24 USD and three minutes of model time, and both are now regression
  tests. A 33% survival rate on a document that four separate reviews had already passed is a
  return nothing else on this map produced.
- **No, on the licence.** Rejected. The licence forbids distribution, and nothing here
  distributes it. Refusing a tool the estate may lawfully run locally, after it found two real
  defects, would cost the estate the defects and save it nothing.
- **Yes, and vendor the harness and prompts so a clock can run it.** Refused, and it is not a
  close call. No licence permits vendoring, forking, or reimplementing the prompts, and a clock
  that runs it would make a non-deterministic instrument into a gate.
- **Yes, on one round per document.** Rejected. One round reads about 23% of the tool's output,
  and the three rounds overlapped by as little as 1 of 6. A single round is a draw presented as a
  survey.

**What is the target?**

- **A norm document this estate wrote, held fixed (chosen).** Point 4.
- **Kyverno CEL.** Ruled out of scope on the map. loophole attacks prose. A CEL expression is
  checked by compose-check and the adopter gate, which are deterministic and already exist.

**What runs the model?**

- **`claude -p` through loophole's own `create_provider()` seam at `loophole/llm.py:119`
  (chosen).** Per-role provider substitution is already wired, so no fork is needed, and the
  owner ruled on 2026-09-21 that there is no paid Anthropic API spend. The cost is real and
  recorded: the adapter **drops the deliberate temperature split between the finder and the
  judge**, so the two roles that the tool's author meant to run at different temperatures run at
  one. What that costs the output is unmeasured.
- **Ollama, or any locally served small model.** Rejected by ticket 06 before any round ran. A
  model too weak to hold the XML format makes `_parse_scenarios` return an empty list, and the
  caller then prints that the code appears robust. That is a false green, which is point 6's
  whole subject.

## Consequences

- **A norm document can now be attacked for about 1.24 USD and nine minutes of model time**, and
  the estate has a measured survival rate to price the reading against: about 1 real defect in 3
  candidates, at a checking cost of roughly half a ticket per candidate.
- **Two defects are already in the record.** Eco-system tickets 113 and 114, reproduced by
  `tests/test_cage_ladder_holes.py`, and two rows in `twin/ecosystem-misuse-catalogue.yaml`.
- **12 candidates from rounds two and three are unchecked**, and this ADR's point 2 makes that a
  gap rather than a curiosity. Four restate a reason round one already gave; eight are new.
  Graduated to the eco-system map.
- **The harness lives in `.scratch/` and is not an estate artefact.** Point 1 says the estate
  commits its own harness, and today that harness is a wayfinder asset. Making it a durable
  procedure anyone can re-run is adoption work, and it is graduated to the eco-system map rather
  than done here.
- **Nothing about this is on a clock**, and nothing about it grades the truth surface. Point 8.
- **kyverno 1.19.1 cannot compile the served `cage-tier` body** (`expected type 'string' but
  found 'dyn'`), found while checking a survivor. The release workflows pin 1.18.2;
  `graded/verify-graded.sh` calls a bare `kyverno` and asserts no version. It fails loudly rather
  than quietly, which is why it is a consequence here and not a survivor.
- **What this ADR does not claim.** It does not say loophole finds a document's real defect set.
  It says the tool is a **pointer generator**, that its pointers repeat while its reasons do not,
  that about a third of them survive a deterministic check, and that the measurement of "about a
  third" rests on six checked candidates from one round.

### Evidence

- `.scratch/laya-loophole/bench/loophole_round.py` — the harness. It holds no loophole source and
  no loophole prompt, and imports the scratchpad clone through `LOOPHOLE_SRC`.
- `.scratch/laya-loophole/bench/parse_failure_control.py`,
  `.scratch/laya-loophole/bench/check_no_prompt_leak.py`,
  `.scratch/laya-loophole/bench/match_rounds.py` — the negative controls and the overlap.
- `.scratch/laya-loophole/research/07-loophole-round/`,
  `.scratch/laya-loophole/research/11-loophole-round-two/`,
  `.scratch/laya-loophole/research/11-loophole-round-three/`,
  `.scratch/laya-loophole/research/11-blind-match/` — the three rounds and the blind reader.
- `tests/test_cage_ladder_holes.py` — the two survivors, nine legs.
