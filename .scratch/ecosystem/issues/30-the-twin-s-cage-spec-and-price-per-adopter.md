# 30 — The twin's cage, spec and price per adopter

Type: grilling (HITL)
Status: open
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
