# 30 — The twin's cage, spec and price per adopter

Type: grilling (HITL)
Status: resolved
Blocked by: 09, 12

## Question

What cage the per-adopter twin runs inside, its spec on the ticket 09 ladder, and its price, reusing the `twin-self` shape; propose-only outermost, Article 22 floor.

## Notes

Graduated 2026-08-28 from ticket 11's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.


## Pricing prerequisites exposed by the clocks, 2026-09-10

Ticket 64 completed the authored-but-unpriced Tuppence and Ludlow overlays. Their existing
emitters refuse with named missing signed size valuations and a grade-3 causal edge beyond the
admitted threshold. The new observation clocks (Tuppence PR33, Ludlow PR30) record that actual
refusal before preserving a non-green outcome. These unresolved pricing prerequisites belong
here, rather than making resolved ticket 64 imply that a valuation fix awaits observation.

The clock-owner map therefore points both twin sweeps to this open ticket. The handoff does not
supply a monetary value, admit an unsupported causal edge, price a GitHub runner as a Kubernetes
Namespace, or claim that the twin's runtime containment and price have been resolved. Propose-only
and the Article 22 floor remain binding. Actual scheduled observations remain outstanding.

## Facts found, 2026-09-25, before round 1

- Each adopter's twin runs in two places with nobody at the keyboard: `twin-sweep.yml` on a
  GitHub-hosted runner, daily, and the model steps of `talk/local-clock.sh` on the owner's machine.
  No twin part runs in a Kubernetes pod.
- The sweep job holds `contents: write`, `pull-requests: write` and `id-token: write`
  (`driftwood/.github/workflows/twin-sweep.yml`). Propose-only on GitHub rests on the workflow text
  and `verify/schedules/verify-schedules.sh`. The server ruleset is prepared and not in force
  (ADR-0024 point 3).
- The sweep checks out the hub at `main`. The twin package has no tag (`git tag` in the hub: 0).
  A hub push changes what runs inside every adopter's twin.
- The ladder's dials exist only for pods (`platform/graded/cage.py` `TIERS`; `cage-tier` matches
  `pods`).
- `twin-self` is a test fixture only (`tests/test_twin_inside_twin.py`). No adopter and no gate
  loads it. driftwood prices its checkout at each rung as four twin responses
  (`twin/orgs/driftwood/responses/run-the-checkout-at-*.yaml`), the nearest shape to reuse.
- Only driftwood's twin emits a price: `source: twin`, GBP 1,897,646.11
  (`driftwood/composed/evidence.json`). tuppence and ludlow refuse by name: no signed `size:`, and
  a causal edge at grade 3 beyond the path admission threshold of 2.
- driftwood's price-eligible edge `cart-pii-loss-cuts-checkout-revenue` declares grade 2 with a
  one-line note and no observations. The 2026-09-02 review found it; it is unchanged.
- `twin/constraints.yaml` carries `no-automatic-enactment` in the universal floor. Re-grill 37
  says "The twin acts inside a priced cage; propose-only is the outermost setting; Article 22 floor
  for significant decisions about people."

## Grilling round 1, 2026-09-25

Five questions, put in chat. The owner answered "agree" to all five on 2026-09-25, with no reason.
Under ADR-0025 each item is **delegated**.

1. **The caged subject is the twin agent** (Q1(a), delegated). The twin's cage covers every act of
   an adopter's twin with nobody at the keyboard: the GitHub sweep job and the headless steps of
   the local clock. A skill a human runs is the human's act, so the human's cage applies. A cage
   belongs to an actor, not to a host: the runner and the owner's machine are two hosts of one
   actor (ticket 12 item 4). The local clock has no identity of its own (ticket 90), so on that
   host the guard mode binds the cage, not a credential.
2. **"Propose-only is the outermost setting" means the loosest rung that exists today** (Q2(a),
   delegated; the owner's own phrase from re-grill 37). A looser rung, where the twin acts, may
   come later inside the priced cage; re-grill 29 names that end state. The Article 22 floor
   means that no rung is looser than propose-only for a significant decision about a person.
   This ticket builds no act rung. `no-automatic-enactment` stays as written until a ticket adds
   an act rung; that ticket narrows it to the scope of Article 22.
3. **One ladder, a dial table per actor class** (Q3(a), delegated). The rung names stay. The twin
   agent's dials are what it may write, what its credential can do, whether a model step runs, and
   its network reach. The pod dials do not change. Running the twin as a pod was rejected: it moves
   the daily clock onto KiND clusters that run only on the owner's machine, and a pod still needs
   the push credential that matters. A separate ladder was rejected: it breaks "one ladder".
4. **The assistant picks the size figures for tuppence and ludlow** (Q4(b), delegated). The
   recommendation read "(a) or (b)" and the owner gave no figure, so the answer is read as (b):
   the assistant picks a turnover, currency and `as_of` for each from
   `.scratch/ecosystem/research/94-studied-firms.md` and records the pick as delegated. This is
   money under ADR-0025, delegated by the owner's answer. The owner may correct it.
5. **A marked synthetic incident record counts as grade 2 for a fictional adopter** (Q5(a),
   delegated). The adopters are fictional firms by design (ticket 75). An incident record in the
   adopter's own repository, marked synthetic, may support a causal edge at grade 2, like the
   substrates with planted ground truth (NORTH-STAR §6). All three adopters' pricing edges cite
   one, driftwood's included: its grade 2 has no record today.

## Facts found, 2026-09-25, before round 2

Four read-only finders, each checked by a separate adversarial checker: 147 facts, 140 confirmed,
6 corrected, 1 refuted. Adopters read at `origin/main` (driftwood 155db9e, tuppence 5deffe6,
ludlow b8e14f7, platform 557c153); the local clones lag.

**Round 1 item 5 rests on a wrong citation.**
- `NORTH-STAR.md:98` ("Substrates are synthetic with planted ground truth") is under `## 6. What
  is explicitly out` (`:91`). It is about surveillance data, not pricing evidence.
- Twin ticket 12's standing rule (`.scratch/twin/issues/12-synthetic-substrate.md:65-66`),
  `twin/planter.py:57-62` and driftwood's `drift/forced-campaign.yaml:14-19` all limit a
  synthetic result to evidence about detection machinery, never about the world.
- Grade 2 is "repeated historical co-movement ... the repetition is the evidence"
  (`twin/evidence-ladder.yaml:52-59`). A record that earns grade 2 must show repeated history.
- Ticket 75 Q7 (owner-instructed) makes the adopters plausible firms modelled on studied real
  firms, not "fictional by design".
- The code never ties a grade to a record: `evidence_grade` is an integer 1-5 and `may_price` is
  `grade <= 2` (`twin/schema.py:177-185`, `twin/evidence.py:130-132`).
- driftwood's rung responses cite "two prior incident post-mortems" and "the platform's own
  break-glass drill" at grade 2. No such file exists on driftwood `origin/main`.

**The twin agent's write reach on GitHub.**
- Every adopter's sweep token holds `contents: write`. Under that permission it can merge a PR by
  REST, fast-forward push `main`, and create a tag and a release. Only driftwood's also holds
  `pull-requests: write`.
- Live rules on each adopter's `main` are `deletion` and `non_fast_forward` only. Rulesets carry no
  bypass actor. `observation-lane.json` is applied nowhere: push rulesets need private repos.
- So the only write limit is the workflow's own cage step, plus after-the-fact checks.
- `verify/schedules/schedules.py` `_SIGNED_ARTEFACT` misses `gh api ... pulls/N/merge`,
  `gh api ... releases`, `gh api ... git/refs`, `curl -X PUT .../merge`, `git update-ref` and
  `git push origin <tag>` (probed).
- `lane.py` would grade a REST merge made with the sweep token as a NOTE, not a FAIL (inferred from
  `lane.py:198-204`; not observed).
- Every twin-sweep grades PASS with "nothing it runs is opaque to this checker"
  (`schedules.py:976-979`). The check flags only `uses:` actions. All three sweeps run hub Python
  that imports `twin` from the hub checkout. The PASS sentence claims more than the check reads.
- A token with `pull_requests: write` and no `contents: write` cannot push a branch or append an
  observation (`POST git/refs` needs Contents). The upgrade `enact_guard.py:29-33` names cannot
  carry the sweep's current writes alone.
- Ticket 87 says `pavc-other-hand` has no `workflows` permission. Live, it has `workflows: write`
  on eight of the nine orgs; nist is the exception.

**The pin.**
- All three sweeps check out the hub at `ref: main`. The hub has no tags. `twin/v0.1.0` is not cut
  (`PIN.yaml` `tag_cut: false` in all three; `twin/RELEASE.md:15-24`). No open ticket owns it.
- Whatever lands on hub `main` runs in every adopter's next sweep with that adopter's write token.
  Hub `main` carries `deletion` and `non_fast_forward` only.

**The local clock.**
- Not installed in launchd and never run on a schedule here (`.local-clock/` absent).
- Under `operations`, the guard refuses a plain adopter push but ADMITS the same push made inside
  `python3 -c 'subprocess.run([...push...])'` (probed). `Bash(python3 *)` is in the child's
  allowed tools (`talk/local-clock.sh:138`).
- The child starts without `--strict-mcp-config` or `--restricted`, so user-scope MCP servers
  and settings may load. Not measured, because no run exists.
- `twin/ENACT_MODE` reads `development`. Ticket 97's "the env may only tighten" is not in code.

**Network and model.**
- No Actions job in the estate has an egress control. The sweeps reach GitHub, sigstore and the
  pip index; `pip install pyyaml` is not pinned by hash.
- 0 of 14 (metric, model version) pairs hold a permission. No workflow calls a model. A permission
  would unlock nothing that runs: its seam has no runner on the GitHub clock.

**Selection and price.**
- Composition selects the tier from platform `cage.py` residuals, `ale * (1 - reduce)`. The
  twin's curve is only hashed (`composition.py:3570-3582`). The twin prices the ALE; it does not
  select the tier. CONTEXT.md said "the twin computes it"; corrected on this branch to ADR-0021.
- The tier fold folds every `prices[]` line that carries a `proposed_tier` into the Namespace,
  whatever its kind (`wargamer.py:249-258`). `pound_seam.py` allows exactly one `source: twin`
  line and only known sources (`:79`, `:159-161`, `:199-227`).
- No rule forbids a party pricing or selecting its own cage. The risk-bearer selects its own
  workloads' cage by design; platform prices itself against its own GBP 10,000 band
  (`honesty/reflexive.py`). Nearest code rules against self-grading:
  `twin/corroboration.py:403-408`, `twin/derived_forecast.py:19-22`.
- twin-self is loaded by the pytest suite and the harness, never by `talk/verify-all.sh`.

**What tuppence and ludlow still lack, after a size and a grade.**
- A cash-flow valuation needs a share-of-turnover figure (driftwood: 0.1488, per quarter). The
  research gives none, and check 9 fails an amount with no `derived_from_party_fact`.
- A `selection-policy/` package (driftwood has one; they have none).
- The publishing contract: `feed.json`, `rule.yaml`, `bump.yaml` and a `publishes[]` record.
- The comparables' filing dates are 32 to 116 months old. A size `as_of` older than 12 months
  prices at the cap.
- A replacement edge must replace the grade-3 edge, not sit beside it: exactly one causal edge
  may reach the cash flow.

Stale records found: `verify/schedules/clock-owners.yaml` still maps driftwood's green sweep to
ticket 72; ticket 64 `:230` says tuppence and ludlow have no twin-sweep; tuppence's and ludlow's
`twin-sweep.py` records a loader `ModelError` (exit 1) as a moved render.

## Grilling round 2, 2026-09-25

Five questions (Q6 to Q10), put in chat after the facts above. The owner answered "agree" on
2026-09-25, with no reason. Each item is **delegated** (ADR-0025).

6. **Round 1 item 5 is reversed: an adopter may declare that it prices on grade 3** (Q6(c)). The
   estate default pricing threshold stays 2. An adopter may declare grade 3, "published work, not
   observed here", on its own signed `party.yaml`. Every price shows the weakest grade it rests
   on. A synthetic record never raises a grade (twin ticket 12). tuppence's and ludlow's
   comparable-firm anchors then price at grade 3. driftwood's edge drops to grade 3 and gets a
   comparable-firm anchor; its rung responses drop to grade 3 or cite a real source. The cost is a
   platform party-schema release. Reason: nothing is invented, and the adopter signs the trade as
   it signs its appetite. Keeping round 1 broke twin ticket 12's rule; grade 2 only removed the one
   working twin price.
7. **The twin package is pinned by hub commit** (Q7(a)). Each adopter's `twin/PIN.yaml` names a
   hub commit; the sweep checks out that commit; the adopter moves it by a reviewed PR. The signed
   `twin/v0.1.0` tag replaces the commit when it is cut. Reason: today another party's `main` runs
   with each adopter's write token (NORTH-STAR §2).
8. **The sweep splits into a read-only twin job and a writer job with no twin code** (Q8(b)). The
   twin job holds `contents: read` and hands its observation line and proposal to the writer as an
   artifact. The writer job has no hub checkout and only inline shell. The checker's blind spots
   are fixed as well (REST merge, release and ref forms, `git update-ref`, tag pushes, and the
   "nothing it runs is opaque" PASS line). Ticket 87's App, when the owner creates it, serves writer
   jobs only, never twin code. Reason: the twin code never holds a write token, with no new
   identity.
9. **The network dial is declared, and every download is pinned by hash** (Q9(a)). No egress tool.
   Reason: a marketplace egress action is third-party code the checker cannot read; a self-hosted
   runner is a host nobody runs; after item 8 the twin job holds no write token.
10. **The platform prices the twin agent's cage; the adopter's selection policy selects the rung**
    (Q10(c)). Platform publishes a dial table for the twin-agent class, with a reduction and a cost
    per rung, and a scenario for a scheduled agent that misuses its credential. The proposer
    proposes; a human merges. The twin never prices its own cage. A new `prices[]` kind carries the
    line, because the tier fold would otherwise fold it into a Namespace. Reason: a self-priced
    cage rests on grade 3 at best and fails closed to `isolated`; a declared rung with no price
    breaks "the £ selects the spec".

CONTEXT.md: the **Synthetic incident record** entry from round 1 is replaced by **Pricing
threshold**.

## Grilling round 3, 2026-09-25

Four questions (Q11 to Q14). The owner answered "agree" on 2026-09-25, with no reason. Each item
is **delegated** (ADR-0025).

11. **The twin agent's dial table has four rungs** (Q11(a)). Every rung keeps the code pinned by
    hub commit (item 7) and every download pinned by hash (item 9).

    | Rung | Writes | Model step | Local clock |
    |---|---|---|---|
    | baseline (propose-only, the loosest today) | the writer job appends an observation line, pushes a proposal branch and opens a PR | local clock at grade 5, no override; GitHub only where a measured permission holds (none today) | runs |
    | restricted | as baseline | none: lookup and deterministic render only | does not run |
    | quarantine | an observation line only; no proposal | none | does not run |
    | isolated | nothing; the twin job runs and writes only to its job log; the writer job does not run | none | does not run |

    Reason: the £ tightens one step at a time, first the model, then proposals, then writes. A
    two-rung table stops proposals and the scoring series together. At `isolated` the twin still
    runs, as a pod does.
12. **The twin agent's scenario takes its loss magnitude from the adopter's own prices and its
    frequency from the threat register** (Q12(a)). The worst act the writer job can do without a
    review is to push a looser declaration. The loss magnitude is the gap between the residual at
    the loosest rung and at the selected rung, over the window until the gate detects it. The
    frequency is a row feeds publishes in the threat register, the same class as the pod frequency
    today. Reason: the harm is derived from figures the adopter already signs. The detection window
    is only as short as the item-8 checker fixes make it: today the gate does not detect a REST
    merge.
13. **Sizes copy the comparable firm's published figures and their real date** (Q13(a), under the
    Q4 delegation). tuppence copies Starling's, ludlow copies Anthem's; the share-of-turnover figure
    comes from the same filing. A stale `as_of` widens the price to the cap, as designed. Reason:
    nothing is invented and no date is false. **This rule is fixed before its effect is computed**,
    because a size change is one of ticket 74's three movers and must not be tuned to cause a
    crossing.
14. **The local-clock child holds no push capability** (Q14(b)). No credential helper, no
    `GH_TOKEN`, `--strict-mcp-config`, a clock-only settings file, and Bash limited to named
    scripts instead of `python3 *`. Reason: the guard's patterns are "a net, not a proof"
    (`twin/enact_guard.py:29-33`); the script already makes the real push under the owner's `gh`
    after the read-back.

## Grilling round 4, 2026-09-25

Four questions (Q15 to Q18). The owner answered "agree" on 2026-09-25, with no reason. Each item
is **delegated** (ADR-0025).

15. **Each rung's reduction is derived from the misuse paths it closes** (Q15(a)). After items 7
    and 8 the pin and the split hold at every rung. Four paths remain: the writer job pushes a
    looser declaration (closed at `isolated` only, because the writer keeps the same token at
    every rung it runs); the writer merges or tags through REST (`isolated`); a misleading proposal
    PR is merged by a human (`quarantine`); a model step writes a wrong binding or forecast
    (`restricted`, about £0 on price, because model claims are grade 5 and not price-eligible). A
    rung's reduction is the share of the scenario's loss its closed paths carry. Every run cost is
    £0 in cash and stays out of selection. Reason: it prices only what each rung removes. The
    pod reductions are "evidenced by nothing but this comment"; an empty table refuses as a missing
    instrument.
16. **One new check grades the twin agent's cage on each adopter's served `origin/main`**
    (Q16(a)): the selected rung is on the ladder, the sweep's jobs match that rung's dial row, and
    the local-clock child holds no push capability. The schedule checker's blind spots are fixed
    with it. Reason: the observation cage and the twin agent's cage are two subjects with two dial
    tables; grading only that a price line exists grades a stand-in for the workflow that runs.
17. **Five tickets graduate, and ticket 30 resolves** (Q17). Ticket 30's definition of done, a
    check wired into the truth surface, moves to ticket 142: a resolved grilling ticket must not
    name a check that does not exist yet. Stale records are corrected on this branch: ticket 87
    (the app's `workflows` permission) and ticket 64 (twin sweeps for tuppence and ludlow). The
    clock-owner rows for tuppence's and ludlow's sweeps move from 30 to 144.
18. **Two ADRs are written**: ADR-0031, the twin agent's cage, and ADR-0032, the pricing threshold
    (Q18). Each is hard to reverse, surprising without context, and the result of a real trade.

## Answer

Resolved 2026-09-25 in four grilling rounds, all answered "agree" by the owner with no reason, so
every decision is **delegated** under ADR-0025. Decisions 1 to 18 are recorded above, round by
round. The architecture is ADR-0031; the evidence rule is ADR-0032.

- **The caged subject** is the twin agent: every act of an adopter's twin with nobody at the
  keyboard, on the GitHub sweep and on the local clock. A skill a human runs is the human's act.
- **Propose-only is the loosest rung that exists today.** An act rung may come later; for a
  significant decision about a person, no rung is looser than propose-only (Article 22).
- **One ladder, a dial table per actor class.** The twin agent's four rows take away, in order,
  the model step, the proposals and the writes. At `isolated` the twin still runs.
- **The spec.** The twin code is pinned by hub commit in the adopter's `twin/PIN.yaml`. The sweep
  splits into a read-only twin job and a writer job with no twin code. Every download is pinned
  by hash. The local-clock child holds no push capability.
- **The price.** The platform prices the twin agent's cage from a dial table whose reductions are
  derived from the misuse paths each rung closes, and a scenario whose loss magnitude comes from
  the adopter's own prices. The adopter's selection policy selects the rung. The twin never prices
  or selects its own cage.
- **The pricing prerequisites.** An adopter may declare that it prices on grade 3, published work
  not observed here; a synthetic record never raises a grade. tuppence's and ludlow's sizes copy
  their comparable firms' published figures and real dates.

Round 1 item 5 was reversed in round 2 on evidence: it rested on a citation that did not support
it.

Graduated: 141 (an adopter declares the grade it prices on), 142 (the twin cage check and the
schedule checker's blind spots, carrying this ticket's definition of done), 143 (the sweep split),
144 (the twins price on published comparable evidence), 145 (the platform prices the twin agent's
cage).
