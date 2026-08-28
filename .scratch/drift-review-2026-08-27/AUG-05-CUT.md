# The 2026-08-05 "cut", itemised

Sources: session digest `dc4083c1_2026-08-05.md` (span 18:04–18:30 UTC), `.scratch/twin/spec.md`
(93 user stories, committed `3f311ba` at 18:00 UTC), and commit `1da4655` *"Split the twin spec
into 77 build tickets with coherence guardrails"* (Aug 5 19:30 +0100 = **18:30 UTC** — the
republish itself).

---

## 0. Correction to the premise, before anything else

**There was no 20-ticket-from-16 scope cut. The record does not contain one.**

The phrase in the transcript is:

> "I'd apply everything above, including my `20 ← 16` cut, unless you want to argue any of it."

`20 ← 16` is **a blocking edge**, written in the breakdown's own dependency notation (`X ← Y` = "X is
blocked by Y", used throughout the same message: `33 ← 32` delete, `23 ← 22` delete, `61 ← 28`
delete). The assistant deleted the edge making the **£ chain** (then-tickets 20–28, published 23–33)
wait on the **Monte-Carlo propagation chain** (then-16, published 20). Its stated reason:

> "Pricing takes a distribution as input; it does not care whether that distribution came from
> Monte-Carlo propagation or from a committed fixture. If both meet at the pocket-org fixture,
> `20 ← 16` breaks and the £ chain (20→28) runs genuinely parallel to the causal chain."

The separate "20" the owner may be thinking of is the **critical path length** recorded in
`00-constitution.md`: *"Computed from the blocking graph, it is 20 tickets long."* Two different
20s, neither of them a scope cut.

**What the republish actually did to scope: nothing was dropped.** Verified mechanically — of the
93 spec user stories, the published 77 tickets cite 92 by number. The single uncited story is
**story 2** (*"git-versioned text is the source of truth and every store a derived index"*), which is
covered by the constitution invariant `store_rebuildable_from_git` and by ticket 01's model-repo
layout, just never cited by its number. The current 92-ticket tree has exactly the same coverage
profile. So the honest headline is: **six merges, five splits, six additions, six edge changes — and
zero removals.**

---

## 1. Before and after

### Before — the 72-ticket breakdown (digest 18:09:23 UTC, never committed)

This was the state Fable reviewed. It was itself a re-split of an earlier **30-ticket** proposal
(digest 18:04:41), made after the owner said *"err on the side of splitting things up and introduce
guardrails and defensive integration tests."* Titles below are as written in the transcript
(shorthand, since they were one-line list entries, not files).

| # | Title as written | # | Title as written |
|---|---|---|---|
| 01 | Model repository layout + `twin` CLI shell | 37 | NMC Health + Wirecard |
| 02 | **The invariant suite** | 38 | Enron control + memorisation-leakage discount |
| 03 | Depth grades + authored/derived marking enforced at load | 39 | Hindsight-resistance cases + inverted scoring |
| 04 | World/overlay split + the directional reference rule | 40 | The skill-eval harness (seam 3) + score-over-time per model version |
| 05 | `twin sense` — dated signal binds to a component | 41 | `signal-classify` |
| 06 | `twin run` — execution emits a forecast **list** with pins | 42 | `evolution-judge`, inferred-first |
| 07 | `twin score` — score against a known outcome, skeleton closes | 43 | Human override with pushback, itself a scored claim |
| 08 | Pin capture + `twin verify` | 44 | `causal-claims` + grade-accuracy scoring |
| 09 | Signing: human accountability vs agent origin; derived-anomaly detection | 45 | `gameplay-lens` |
| 10 | Schema, validation, derived roll-ups, no special-category slot | 46 | The scheduled opportunity sweep |
| 11 | The Wardley spine, D/K/R inherited from arckit | 47 | `ethics-gate` — purpose → necessity → proportionality + DPIA triage |
| 12 | Believed / rival-forecast / revealed-truth separation, no privileged actual map | 48 | Ingest + STEEP + automated binding at throughput |
| 13 | Edges: sign, lag, PERT elasticity | 49 | The decaying unbound pool |
| 14 | The evidence ladder 1–5 | 50 | Retrospective sweep + lead-time-to-recognition |
| 15 | Use-gating + the unpriced blast-radius | 51 | **Coherence: skills → sensing → forecast → score** |
| 16 | Monte-Carlo propagation + depth attenuation | 52 | `substrate-generator` + versioned recipe + seeded regeneration |
| 17 | Shared-ancestry / common-cause handling | 53 | Spine anchoring + free-running where the record is silent |
| 18 | `do()` downstream-only vs observation bidirectional | 54 | The eval suite: fidelity metrics and tuning |
| 19 | Rival causal accounts as ensemble spread | 55 | Planter/detector/scorer split + actionability horizons + negativity bias |
| 20 | PERT sampling + calibrated triples | 56 | Question selection rule + ingestion quarantine |
| 21 | Heavy-tailed severity: lognormal body + GPD tail | 57 | Blind pinned emission + resolution scoring + narrow claim scope |
| 22 | TVaR + loss-exceedance curve | 58 | Constraint set + published scope exclusions |
| 23 | The perspective object: who pays, red lines, universal floor | 59 | Affected-parties register + role-not-person signatures |
| 24 | Constraint pre-filter before pricing + published set | 60 | Misuse catalogue + constraint-removal logging with attractiveness |
| 25 | Causally-gated admission to the £ | 61 | Contestability workflow + disparate-impact audit channel |
| 26 | Response pricing + evidence-graded mitigation credit | 62 | Twin-inside-twin depth-1 + adoption as a risk about itself |
| 27 | Rival world models as repo units | 63 | **The Flux falsification test** |
| 28 | Trade-off curve with a marked default | 64 | Propose-only PR channel |
| 29 | **Coherence: graph → causal → £** | 65 | Policy as a signed pinned dependency |
| 30 | The rewind primitive (abduction) | 66 | Graded enforcement + posture-as-identity, narrowed |
| 31 | Three information regimes + gate-by-construction | 67 | Multi-channel enactment sensing, corroboration sets the grade |
| 32 | `twin backtest` = rewind + projection, no separate harness | 68 | **Full-system coherence before the beats** |
| 33 | Proper scoring rules + the score card | 69 | Royal Mail beat |
| 34 | Reliability diagrams over volume | 70 | Netflix beat |
| 35 | Scheduled emission as the production line | 71 | Intel beat |
| 36 | Carillion, the primary key | 72 | Depth grades surfaced + does-not-do register + thesis sequencing |

### After — the 77 published tickets (`1da4655`), titles verbatim from each file's H1

```
00 — The constitution
01 — Model repository layout and the `twin` CLI shell
02 — The invariant suite: harness, refusal tests, pending manifest, hash protection
03 — Depth grades as computed checklists, and authored/derived marking
04 — The world layer, org overlays, and the directional reference rule
05 — `twin sense` — a dated signal binds to a component
06 — `twin run` — an execution emits a forecast list with pins
07 — `twin score` — a forecast is scored against a known outcome
08 — Proper scoring rules and the score card
09 — Reliability diagrams over volume, and scheduled emission
10 — Pin capture and `twin verify`
11 — Signing: accountability, origin, and the derived-artefact anomaly
12 — The graph schema and validation
13 — Derived roll-ups
14 — The Wardley spine: evolution positions and D/K/R
15 — The pocket-org golden fixture
16 — Believed map, rival forecasts, revealed truth — and the deltas between them
17 — Causal edges: sign, lag, and PERT elasticity
18 — The evidence ladder, grades 1 to 5
19 — Use-gating and the unpriced structural blast-radius
20 — Monte-Carlo propagation, depth attenuation, and the seam-2 harness
21 — Shared ancestry and common-cause handling
22 — Intervention versus observation: `do()` downstream-only
23 — PERT sampling and calibrated-range triples
24 — Heavy-tailed severity, TVaR, and the loss-exceedance curve
25 — Empirical severity anchoring
26 — The perspective object: who pays, red lines, and the universal floor
27 — The constraint set and published scope exclusions
28 — The constraint pre-filter, running before pricing
29 — Causally-gated admission to the £
30 — Response pricing and evidence-graded mitigation credit
31 — The credibility prior: blending world layer and sparse overlay
32 — Plurality: rival world models and rival causal accounts
33 — The trade-off curve across the ensemble
34 — Coherence audit: graph → causal → £
35 — The rewind primitive
36 — The three information regimes, gated by construction
37 — `twin backtest`, and all four verbs from two primitives
38 — Carillion: the primary answer key
39 — NMC Health and Wirecard
40 — Enron as contamination control, and the memorisation-leakage discount
41 — Hindsight-resistance cases and inverted scoring
42 — The skill-eval harness (seam 3)
43 — `signal-classify`
44 — `evolution-judge`, and human override with pushback
45 — `causal-claims`, scored on grade accuracy
46 — `gameplay-lens` and the scheduled opportunity sweep
47 — `ethics-gate`: admission ladder, DPIA triage, gameability, and fast improvement
48 — Substrate recipe format, seeded regeneration, and the authored-or-derived spike
49 — `substrate-generator`: the synthetic world
50 — Spine anchoring and free-running
51 — The substrate eval suite: fidelity measured, not asserted
52 — The planter/detector/scorer split and actionability horizons
53 — Ingest, STEEP tagging, and automated binding at throughput
54 — The decaying unbound signal pool
55 — Retrospective sweep and lead-time-to-recognition
56 — Coherence audit: skills → sensing → forecast → score
57 — Benchmark question selection and ingestion quarantine
58 — Blind pinned emission, resolution scoring, and the narrow claim
59 — Prediction-market price moves as world-layer signals
60 — Contestability as a primary workflow
61 — The affected-parties register and the disparate-impact channel
62 — The misuse catalogue and constraint-removal logging
63 — The twin inside the twin, and adoption as a risk about itself
64 — Flux drift measurement: instrument and wait
65 — The Flux falsification verdict
66 — Propose-only enactment: PRs and policy as a signed pinned dependency
67 — Graded enforcement and posture-as-identity, narrowed
68 — Multi-channel enactment sensing, with corroboration setting the grade
69 — The standing scenario library
70 — Full-system coherence: confirmatory
71 — Royal Mail: the answer key
72 — Royal Mail: run and score the falsifiability beat
73 — Netflix: the spine and the substrate
74 — Netflix: run the whole engine
75 — Intel: the live, unresolved, pinned forecast
76 — Kodak and Maersk: the portfolio at declared depth
77 — Honesty made structural: depth grades, the does-not-do register, thesis sequencing
```

### The exact diff

Arithmetic: **72 − 6 merged + 5 split + 6 added = 77.** ✔ (The assistant's own in-transcript
estimate was "~72 → ~66 after merges, back up to ~71" — it undercounted its own additions by one
and the merges by one; the published number is 77 and the mapping below is exhaustive.)

**MERGED — six pairs became six tickets (−6)**

| Before | Became | Anything lost? |
|---|---|---|
| `34` Reliability diagrams over volume **+** `35` Scheduled emission as the production line | **09 — Reliability diagrams over volume, and scheduled emission** | No. Both halves are ACs; the merge also picked up the arckit `build --refresh` single-repo caveat as ticket work rather than a footnote. |
| `21` Heavy-tailed severity: lognormal body + GPD tail **+** `22` TVaR + loss-exceedance curve | **24 — Heavy-tailed severity, TVaR, and the loss-exceedance curve** | No. Offset by the *new* ticket 25 (empirical severity anchoring), so the tail-maths area went 2 → 2, re-cut along a different line. |
| `19` Rival causal accounts as ensemble spread **+** `27` Rival world models as repo units | **32 — Plurality: rival world models and rival causal accounts** | No. Four ACs cover both, plus "no mechanism exists to adjudicate by authorship or recency". |
| `42` `evolution-judge`, inferred-first **+** `43` Human override with pushback | **44 — `evolution-judge`, and human override with pushback** | No. Five ACs cover both. Note this contradicts the 18:09 message's own line *"Six tickets are now small enough to question — 12, 19, 35, 43, 46, 59. … I'd keep them"* — five of those six (19, 35, 43, 46, 59) were merged away 20 minutes later without that reversal being called out. |
| `45` `gameplay-lens` **+** `46` The scheduled opportunity sweep | **46 — `gameplay-lens` and the scheduled opportunity sweep** | No. Negativity-bias counterweight survives as an AC ("opportunity output volume is reported alongside threat output volume"). |
| `64` Propose-only PR channel **+** `65` Policy as a signed pinned dependency | **66 — Propose-only enactment: PRs and policy as a signed pinned dependency** | **Yes — see §2.** This one has a real cost. |

**SPLIT — five tickets became ten (+5)**

| Before | Became |
|---|---|
| `10` Schema, validation, derived roll-ups, no special-category slot | **12 — The graph schema and validation** + **13 — Derived roll-ups** |
| `52` `substrate-generator` + versioned recipe + seeded regeneration | **48 — Substrate recipe format, seeded regeneration, and the authored-or-derived spike** + **49 — `substrate-generator`: the synthetic world** |
| `63` The Flux falsification test | **64 — Flux drift measurement: instrument and wait** + **65 — The Flux falsification verdict** |
| `69` Royal Mail beat | **71 — Royal Mail: the answer key** + **72 — Royal Mail: run and score the falsifiability beat** |
| `70` Netflix beat | **73 — Netflix: the spine and the substrate** + **74 — Netflix: run the whole engine** |

**ADDED — six new tickets (+6)**

| New ticket | Origin |
|---|---|
| **15 — The pocket-org golden fixture** | Fable's one genuinely new mechanism. Load-bearing: it is what makes the `20 ← 16` edge cut safe. |
| **25 — Empirical severity anchoring** | Cyentia IRIS / DBIR anchoring, previously implicit in `21`. |
| **31 — The credibility prior: blending world layer and sparse overlay** | Fable found spec **story 5** (Bühlmann–Straub) had no owner. |
| **59 — Prediction-market price moves as world-layer signals** | Fable found spec **story 53** had only its emission half built; adds invariant `price_levels_never_probabilities`. |
| **69 — The standing scenario library** | Fable reversed the assistant's own call. See §2 — this was the one near-drop. |
| **76 — Kodak and Maersk: the portfolio at declared depth** | Fable: "Kodak and Maersk have zero tickets." |

**RENAMED / WIDENED, not narrowed**

- `47` `ethics-gate — purpose → necessity → proportionality + DPIA triage` → **47 — `ethics-gate`:
  admission ladder, DPIA triage, gameability, and fast improvement** (absorbs spec stories 67 and 68,
  which Fable found ownerless).
- `59` "role-not-person signatures" moved out of the affected-parties ticket into **11 — Signing**
  (AC: *"Signatures bind to roles, not named individuals, and the role register is versioned"*).
  Relocated, not lost.

**EDGE CHANGES — six (the actual "cuts")**

| Edge | Change | Effect in the published graph |
|---|---|---|
| `33 ← 32` | **deleted** (Fable: "the single highest-leverage correction") | Scoring moved from position 33 to **08**, immediately after the skeleton closes at 07. |
| `23 ← 22` | **deleted** | Perspective object no longer queues behind tail maths: **26 ← 12**. |
| `58 ← 24` | **reversed** (was backwards) | Constraint set authored (**27**) before the pre-filter enforcing it (**28 ← 27, 23**). |
| `61 ← 28` | **deleted** | Contestability pulled from position 61 to **60 ← 11, 12**. |
| `10 ← 07` added | Fable's fix for two tickets both defining the graph schema | **12 ← 07** — skeleton's minimal schema first, 12 formalises it. |
| **`20 ← 16`** | **deleted — the assistant's own cut** | £ chain re-rooted on the pocket-org fixture: **23 ← 15**, not `23 ← 20`. |

---

## 2. Per-item: what it covered, who picked it up, does the north star need it

The north star: *a loosely coupled eco-system of publishers, regulators, a feeds marketplace, a
platform, adopter orgs as example consumers, the twin as intelligence, cages as enforcement, one £
currency, provenance.*

### 2.1 The `20 ← 16` cut (the item the owner asked about)

- **Spec stories affected:** none removed. The cut re-parents the £ chain (stories 21, 22, 23, 24,
  25, 26, 28, 29, 30, 31) onto the pocket-org fixture instead of onto propagation.
- **Picked up later?** N/A — nothing was dropped to pick up. The published ticket 23 states the
  rationale in its own body: *"Blocked on the pocket-org fixture rather than on propagation —
  pricing takes a distribution as input and does not care where it came from."*
- **North star:** **the cut helps.** "One £ currency" is a north-star pillar and this is the edge
  that lets the £ engine be built and evidenced without the whole Monte-Carlo causal stack landing
  first. The risk it carries — a £ chain validated only against a hand-computed fixture, never
  against real propagation output — is contained by coherence ticket **34 — Coherence audit: graph →
  causal → £**, which is exactly where those two chains are forced back together.
- **Verdict: sound. Leave it cut.**

### 2.2 `64` + `65` → published `66` (the one merge with a real cost)

- **Spec stories:** **80** (twin proposes only, never merges), **81** (policy as versioned, signed,
  pinned dependency — the verification substrate), **82** (the narrowed claim: policy-as-code is *an*
  arm, not *the* definition of governance).
- **What it cost:** merging them re-coupled story 80 to the Flux verdict. Published `66 ← 65 ← 64,
  29, 11`, and `67 ← 66`, `68 ← 67`. The propose-only PR channel does not need the Flux verdict; only
  the policy-pinning half does. The assistant recorded this against itself in `00-constitution.md`
  in the same commit: *"The next largest is relaxing `66 ← 65`: the propose-only PR channel does not
  need the Flux verdict, only the policy-pinning half does. Split it if the calendar matters."*
- **This lands on the critical path.** The published critical path is
  `01→02→03→04→05→06→07→12→26→27→28→29→65→66→67→68→70→73→74→77` — 20 tickets, and `65→66→67→68`
  is four consecutive links of it.
- **Picked up later?** **No.** As of today `66` still reads `**Blocked by:** 65`, `67 ← 66`,
  `68 ← 67`, and the constitution still carries the un-relaxed path verbatim. Commit `ff4907f`
  ("Build ticket 66: propose-only enactment in two layers") built both layers inside the merged
  ticket rather than splitting it.
- **North star:** **needs it split.** "Cages as enforcement" and "the platform" both sit downstream
  of the propose-only PR channel, and in the current eco-system framing the PR channel is what
  adopter orgs actually consume. Keeping it behind a Flux falsification verdict — a verdict the
  project has since recorded as *unmeasured* (`project_flux_verdict_unmeasured`, drift floor
  unreachable from 2026-08-16) — means an enforcement arm gated on a question that was closed
  without an answer.

### 2.3 The near-drop that Fable caught: the standing scenario library

- Not part of the 18:09 → 18:30 change; it was proposed for dropping at the **30-ticket** stage
  (18:04): *"Nothing here builds the scenario library contents (story 43). … That's authoring work
  spread across the tickets that need each entry, not a build slice."*
- **Spec story 43** plus the whole committed scenario class list: quantum/HNDL, bus-factor,
  insider/coercion, supply shock, sanctions, M&A, memory cost, AI-model access, climate.
- Fable reversed it: *"only the entries the beats need get authored … that's the scope drop your
  standing guard names."* It became **69 — The standing scenario library**, with a new invariant
  `standing_library_covers_committed_classes`.
- **North star:** essential. The scenario classes are the sensing surface a feeds marketplace would
  publish into. **Correctly restored — no action.**

### 2.4 The five "small enough to question" tickets

The 18:09 message named `12, 19, 35, 43, 46, 59` as small-but-load-bearing and said *"I'd keep
them."* Twenty minutes later five of the six were merged away (`19`→32, `35`→09, `43`→44, `46`→46,
`59`→11+61) with no note that the earlier judgement had been reversed. **Substance survives in every
case** (checked AC by AC above), so this is a record-keeping fault rather than a scope fault — but it
is the shape of thing the standing guard exists to catch, and it is worth knowing that the reversal
was silent.

### 2.5 Spec story 2 — the only uncited story

*"As a twin operator, I want git-versioned text to be the source of truth and every store to be a
derived index."* Cited by no ticket, in either the 77 or the current 92. Held only by the
constitution invariant `store_rebuildable_from_git` and implicitly by ticket 01. **North star:**
provenance is a named pillar and this is its foundation. Low risk (the invariant is live) but it is
the one story with no owning ticket.

### 2.6 What the north star needs that this breakdown never had

Not a cut — a gap that predates and postdates 2026-08-05, recorded here because the question was
asked. Grepping `spec.md` and all 92 build tickets:

| North-star element | Coverage |
|---|---|
| the twin as intelligence | full — tickets 05–58 |
| cages as enforcement | tickets 66–68 (and 86) |
| one £ currency | tickets 23–33 |
| provenance | tickets 10, 11, 89 |
| regulators | mentioned only as a *modelled actor* (26, 39), never as an eco-system participant |
| **publishers** | **zero occurrences** |
| **feeds marketplace** | **zero occurrences** |
| **adopter orgs as example consumers** | **zero occurrences** ("adopter" appears nowhere) |
| **the platform** as a distinct role | only incidental ("platform owner" in story 81) |

The nearest seed is **04 — The world layer, org overlays, and the directional reference rule** plus
**26 — The perspective object**: shared world layer + private per-org overlay + perspectival £ is
structurally the publisher/consumer split, unnamed. If the eco-system framing is the destination,
that is new spec work, not a restoration.

---

## 3. Recommended put-backs

Short list, in priority order. Three items, only one of which is a genuine restoration.

1. **Split published `66` back into its two halves and relax `66 ← 65`.** This is the assistant's own
   recorded next-best cut, written into `00-constitution.md` on 2026-08-05 and never taken. It frees
   the propose-only PR channel (story 80) from a Flux verdict it does not need, and removes up to
   four links from a 20-ticket critical path. It matters more now than it did then, because the Flux
   verdict was subsequently closed **unmeasured** — so the current graph gates the enforcement arm on
   a question with no answer.
2. **Give spec story 2 an owning ticket** (cite it in `01`'s reading list, or add it to ticket 10, "Pin
   capture and twin verify"). One line of editing; makes the git-is-truth guarantee traceable
   rather than invariant-only, which is what "provenance" as a north-star pillar needs.
3. **Do not restore anything else.** The six merges each kept both halves as acceptance criteria; the
   one genuine near-drop (scenario library) was caught by Fable and restored as ticket 69; nothing
   else left the plan. If the eco-system north star is now binding, the missing pieces —
   publishers, the feeds marketplace, adopter orgs as consumers — are **new spec stories against
   `04`/`26`'s world-layer/overlay seam**, not items to put back.

**One process note worth recording**: the 18:17 review message put ~30 individual changes to the
owner as a single "unless you want to argue any of it", and the answer was one word. Five of those
changes reversed a judgement the assistant had made 8 minutes earlier and recommended keeping. The
substance survived; the audit trail did not. A merge/split list of this size is worth putting as a
table rather than as prose, so a one-word "yes" is a decision rather than a delegation.
