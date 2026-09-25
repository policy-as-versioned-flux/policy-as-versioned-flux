---
status: accepted
---

# The twin agent is caged by its own dial table on the one ladder; the platform prices it, and the adopter selects the rung

Decided 2026-09-25 by the assistant under
[ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md), labelled **delegated**: the
owner answered "agree" to four grilling rounds with no reason. Eco-system ticket 30, decisions 1
to 18 ([issues/30](../../.scratch/ecosystem/issues/30-the-twin-s-cage-spec-and-price-per-adopter.md)).
Extends [ADR-0022](0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md) to a
subject that is not a pod. Supersedes nothing.

## Context

CONTEXT.md says a workload, a human, a device, a model action and the twin itself each run inside
a cage, and re-grill 37 says the twin acts inside a priced cage with propose-only outermost. No
cage for the twin existed in code. The ladder's dials (`graded/cage.py` `TIERS`) fit only pods.

Measured on 2026-09-25, before any decision:

- Each adopter's twin runs in two places with nobody at the keyboard: `twin-sweep.yml` on a
  GitHub-hosted runner, and the model steps of `talk/local-clock.sh` on the owner's machine.
- The sweep token holds `contents: write`. With it, the job can merge a PR by REST, push `main`,
  and create a tag and a release. Each adopter's `main` carries only `deletion` and
  `non_fast_forward`. The observation-lane ruleset is applied nowhere. So the only limit was the
  workflow's own text.
- Each sweep checked out the hub at `main`. Whatever landed on hub `main` ran in every adopter's
  next sweep, with that adopter's write token. The twin package has never been tagged.
- Under `operations`, the local-clock guard refused a plain adopter push and admitted the same
  push made inside `python3 -c 'subprocess.run(...)'`.
- Composition selects a tier from the platform table's residuals and only hashes the twin's curve.
  The tier fold folds every `prices[]` line that carries a proposed tier into a Namespace.

## Decision

1. **The caged subject is the twin agent**: every act of an adopter's twin with nobody at the
   keyboard, on any host. A skill a human runs is the human's act.
2. **Propose-only is the loosest rung that exists today.** A rung where the twin acts may come
   later, inside the priced cage. For a significant decision about a person, no rung is looser
   than propose-only (UK GDPR Article 22). `no-automatic-enactment` in `twin/constraints.yaml`
   stays as written until a ticket adds an act rung.
3. **One ladder, a dial table per actor class.** The rung names are shared. The twin agent's dials
   are what it may write, what its credential can do, whether a model step runs, and its network
   reach:

   | Rung | Writes | Model step | Local clock |
   |---|---|---|---|
   | baseline | the writer job appends an observation line, pushes a proposal branch and opens a PR | local clock at grade 5, no override; GitHub only where a measured permission holds | runs |
   | restricted | as baseline | none | does not run |
   | quarantine | an observation line only | none | does not run |
   | isolated | nothing; the twin job writes only to its job log | none | does not run |

4. **The spec at every rung.** The twin code is pinned by the hub commit in the adopter's
   `twin/PIN.yaml`, and by the signed `twin/v0.1.0` tag once it is cut. The sweep splits into a
   **twin job** with `contents: read` and a **writer job** with no hub checkout, no twin code and
   inline shell only. Every download is pinned by hash. The local-clock child holds no push
   capability: no credential, strict MCP configuration, Bash limited to named scripts.
5. **The platform prices the cage; the adopter selects the rung.** Platform publishes the
   twin-agent dial table. Each rung's reduction is the share of the scenario's loss carried by
   the misuse paths that rung closes. The scenario's loss magnitude is the gap between the
   adopter's residual at the loosest rung and at the selected rung, over the window until the gate
   detects the act; its frequency is a threat-register row. The adopter's selection policy selects
   the rung, the proposer proposes it, and a human merges. **The twin never prices or selects its
   own cage.**
6. **A new `prices[]` kind** carries the line, and the tier fold keys on the subject, so the line
   never folds into a Namespace tier.

## Options considered

- **Run the twin as a pod** in a governed Namespace, so the pod dials apply. Rejected: it moves the
  daily clock onto KiND clusters that run only on the owner's machine, and a pod still needs the
  push credential that matters.
- **A separate ladder for the twin.** Rejected: it breaks "one ladder".
- **A dedicated GitHub App for the twin agent.** Not needed for the twin code once it holds no
  write token. Ticket 87's App, if the owner creates it, serves writer jobs only.
- **The twin prices its own cage** with a curve over its own rungs. Rejected: twin decision 10
  cuts self-reference at depth one, and the evidence would be grade 3 at best, so selection would
  fail closed to `isolated` and stop the twin.
- **The adopter declares the rung with no price.** Rejected: it breaks "the £ selects the spec".
- **Copy the pod reductions.** Rejected: `cage.py` calls them "evidenced by nothing but this
  comment".

## Consequences

- Eco-system tickets 142, 143 and 145 build this. Ticket 142's check grades the served
  `origin/main` of each adopter and FAILs by name until 143 and 145 land.
- With the reductions derived from the misuse paths, `restricted` carries the same residual as
  `baseline`, because model claims never price today. The £ therefore never selects
  `restricted` for its own sake. That is correct, not a gap.
- The writer job still holds a token that can merge. The remaining limit is reviewed adopter text
  and the fixed schedule checker, until a review rule on `main` exists (ticket 87).
- Revisit when: an act rung is proposed; a model holds a measured permission on a GitHub clock;
  the repositories go private, so a push ruleset can restrict paths; or the twin package is tagged.
