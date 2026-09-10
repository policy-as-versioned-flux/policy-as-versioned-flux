---
status: accepted
---

# Cage behaviour is graded on the adopters' lane; in the hub it is proven offline only, and the record says so

Decided 2026-09-10 by the assistant under ADR-0025, labelled delegated. Ticket 86, under ticket 75
Q8 (the owner answered "yes" to option (b); a bare letter is a delegation, so the reasons below are
the assistant's).

## Context

The estate's most distinctive claim is the one the 2022 mea culpa turns on: **there is no gate**. A
workload that does not fit its cage is not denied, it runs on a tighter rung, and the bottom rung
runs and reaches nothing. NORTH-STAR §4 step 4 says the workload keeps running. The owner's own
words for ticket 75 Q5, 2026-09-02: something can find itself unable to run "only because it
doesn't fit the cage, not because we deliberately deny it".

**That claim had never been graded PASS on a citable run.** Twenty-one truth runs, then more:
`platform/graded/verify-graded.sh` — the only instrument that observes the cage as behaviour rather
than as a document — has exited 3, could-not-look, on every run since run 15, because its live tail
needs a persistent KinD cluster called `driftwood` and no version of `.github/workflows/truth.yml`
has ever created one. The runs that *do* observe the cage holding are presenter runs on a laptop,
and NORTH-STAR §5 forbids any document from citing them. So the estate's central claim rested on an
offline render plus evidence nobody was allowed to quote.

What **is** observed on every citable run, and is real: the cage's DECISION LOGIC, offline, with
the estate's own pinned Kyverno. `cage.py selfcheck` over the whole ladder; the `cage-tier` mutate
tests (a governed namespace with no tier renders the bottom rung, a forged pod label is clobbered,
a declared hardening survives); the `cage-netpol` generate tests (the bottom rung's projection is
an ingress-and-egress deny-all); the drift guard tying the Kyverno tier map to `cage.py`'s table;
tighten-only at every rung. That is a proof about a decision, not about a cluster. No pod is
created, admitted by a real API server, or blocked by a CNI on any citable run.

Three facts measured first-hand on 2026-09-10, on a throwaway cluster, as rehearsals (ADR-0023 D4:
never cited, and they are not cited here as gate evidence — they are the reasoning behind this
decision):

1. At composed policy version **4.0.0** the claim is true and observable: a pod in a governed
   namespace with no tier is admitted, runs on `cage-isolated-4-0-0` with the injected sidecar,
   cannot connect to the API server's ClusterIP or to an address outside the cluster, while a
   control pod the cage left loose connects to both. Deleting the generated NetworkPolicy lets the
   same pod reach both — so the block is the cage.
2. At composed policy version **3.0.0**, which is what every adopter's lane cluster actually
   reconciles today, the cage is **a refusal**. The API server declines every pod it touches:
   `no PriorityClass with name cage-baseline-3-0-0 was found`, because the adopter's composed set
   ships `cage-tier` and not the `priorityclasses.yaml` platform ships beside it in every version;
   and with those classes supplied by hand, `the integer value of priority (0) must not be provided
   in pod spec` — 3.0.0's `cage-tier` writes `priorityClassName` without the priority trio, which
   is instance 1 of exactly what ticket 98's scan exists to catch.
3. Ticket 98's scan does not see it. The adopters' served cage lives only in the tree at tag
   `v1.1.0`; on disk they carry `composed/policies/v4.0.0`, which their ResourceSet array does not
   declare, so the scan classes it `unserved-on-disk` and excludes it. The cage in force on every
   adopter is graded by nothing.

## Decision

1. **Cage behaviour is graded LIVE on the adopters' observation lane.** `drift/five-facts.py` on
   driftwood, tuppence and ludlow gains two facts, taken in the same record, on the same scheduled
   run, on the same ephemeral cluster as the five: *the workload the cage puts on its own bottom
   rung is admitted and Running*, and *it reaches neither the API server nor an address outside the
   cluster, while a control workload the cage left loose reaches both*. Pre-registered in each
   adopter's `drift/window.yaml` under `cage_behaviour_sample`.

2. **The rung is derived, never asserted.** The instrument creates two namespaces and names no
   tier in either: one is `governed` with no tier, so the cage's own fall-closed rule decides where
   its pod lands, and one is not governed, so the cage puts its pod on its loosest rung. The word
   `isolated` appears nowhere in the probe. An adopter whose composed array declares a different
   ladder gets its own answer with no edit to the instrument.

3. **The negative is only a fact beside its control.** A pod that reaches nothing because the
   cluster is broken must not read the same as a pod that reaches nothing because the cage holds.
   So a run whose control reached nothing either is recorded UNMEASURED against a declared
   falsifier — not a null result, not a pass, and it may not be quoted as either. The same applies
   when the cage puts both pods on the same rung (there is then no bottom rung to look at), when a
   connect could not be run at all, and when nothing in the cage selects the bottom-rung pod, so
   nothing observed explains its silence.

4. **Pre-registration is measured, not asserted.** `grade` walks the first-parent history of
   `drift/window.yaml` on the served ref, reads the `cage_behaviour_sample` block out of the blob
   at each commit, and takes the NEWEST commit at which that block changed. It refuses to score
   either fact against a sample taken before that commit. A branch commit registers nothing,
   because a branch run records nothing (ticket 100). Reword the question, narrow a claim, soften a
   falsifier or delete a ceiling after the facts have landed and the registration moves to that
   day, so every score taken against the old wording stops counting. That is ticket 93's rule for a
   forecast, applied one level down to a fact — **including the half that costs something**, which
   the first cut of this build did not have: it keyed on the first commit that introduced a fact
   id, so a later rewrite would have been free. Corrected 2026-09-10 on the same branch, before
   anything was merged or scored.

   Where this is deliberately narrower than ticket 93: the unit is the SECTION, not the file,
   because this window carries three instruments and an addendum to one of the others is not a
   rewrite of this question. Within the section it is raw text, comments included, because a
   comment here carries the reasoning a reader trusts.

5. **In the hub, cage behaviour is proven OFFLINE ONLY, and every document says so** until a
   citable run scores the two facts. The decision logic is proven live-with-the-real-engine and
   offline; enforcement — admission by a real API server, a connection refused by a real CNI — is
   not proven by anything the estate may cite. The deck, the runbook and NORTH-STAR may claim the
   first and must not claim the second.

6. **A fail is the strongest verdict a fact can produce.** `grade` accumulated its verdict with
   `max(verdict, 1)`, so any fact observed FALSE after an earlier could-not-look was reported as a
   could-not-look. Measured on `origin/main` on 2026-09-10: rc 3 on a sample whose own output
   carried three `FALSE` lines. A fact that cannot fail is not graded, so this is part of the same
   decision and not a tidy-up beside it.

## The road not taken

**Ticket 86 item 2: give the hub's own clock an ephemeral KinD of the shape `drift-sample.yml`
already proves, checksum-pinned, deleted on exit, and let the eleven platform live tails run
against it under a name they can find.** Ticket 75 Q8 did not take it. The reasons, recorded here
because a road not taken that is written nowhere is a road not considered:

- **It would grade the same behaviour a second way.** The adopters' lane already brings up exactly
  that cluster, with exactly those pinned tools, reconciling from the real remotes. A second
  ephemeral cluster in the hub does not add an observation; it adds a second thing that can break,
  in the workflow whose output is the citable number.
- **The claim is weaker there.** A hub clock that builds a cluster for platform's own tails has
  platform grading platform on a cluster platform's own gate created. The adopters' lane is an
  adopter's own clock, observing its own composed set, arriving through a real org boundary — an
  estate observation rather than a self-proof, in the manifest's own vocabulary.
- **It moves the ceiling for a reason nobody chose.** Eleven `never:` rows would become passable,
  which changes the one number NORTH-STAR publishes, and the manifest's substrate note is explicit
  that a change of substrate is its own decision and not a side effect of a build.

**The cost of not taking it, named rather than assumed away.** The other ten platform live tails
stay could-not-looks on every citable run: the cage is the only one of the eleven this decision
reaches, and it is reached through the adopters rather than through platform's own instrument. So
`verify-graded.sh` keeps its `never:` row and stays outside the ceiling, and the estate observes
the cage's behaviour on three clusters it does not observe platform's other live claims on. If a
later ticket wants those ten, item 2 is the road, and this ADR is what it supersedes.

## Consequences

- **Done is half open, and the open half is named.** The two facts are built, pre-registered and
  pushed. Neither has been scored on a citable run, because only a scheduled run of the adopters'
  lane produces one and a run triggered by hand is a measurement, not the scheduled observation.
- **The first citable score will be a red, and it should be.** On the composed version in force
  today fact 6 is observed FALSE with the API server's own words. That is the estate's defect
  arriving where it belongs, not the instrument's: the composed set delivers a cage that the API
  server refuses. What closes it is a reviewed pull request that adds `4.0.0` to each adopter's
  ResourceSet array and moves the composed pin to a tag whose tree carries
  `composed/policies/v4.0.0` — named in `gitops/composed/composed-set.yaml`'s own comment since
  2026-08-28, and not ticket 86's to cut.
- **The adopters' `verify-reconcile.sh` moves from SKIP to FAIL on the citable run**, and so does
  `verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh`, for point 6. The TRUTH line will change
  shape: three or four scripts leave the skip column for the fail column. Nothing about the estate
  got worse; the instrument stopped softening what it saw.
- **The composed set omits `priorityclasses.yaml`.** Platform ships it in every version directory;
  every adopter's composition drops it. That is a composition defect, it is the direct cause of the
  first refusal above, and it is not this ticket's to fix.
- **Ticket 98's scan grades no adopter cage.** The served versions exist only at a tag; the version
  on disk is not served. Also not this ticket's to fix, and named so it is not rediscovered.
