# 86 — The cage enters the citable number

Type: task (AFK)
Status: open
Blocked by: 75 (resolved)

## Question

The estate's most distinctive claim, that the bottom rung is a running cage that reaches nothing, has never been graded PASS on any of 21 truth runs. `verify-graded.sh` proves it by a real TCP connection from an isolated pod, and it has never exited 0 because the hub clock creates no cluster. Twelve of run 21's eighteen skips name a persistent kind cluster called `driftwood` that the runner never has. Every identity-plane script skips the same way. NORTH-STAR §5 forbids any document from citing the presenter-run evidence that is the only evidence there is.

Under ticket 75 Q8 and Q12:

1. If the lane: add two facts to `drift/five-facts.py` and `drift/window.yaml` on every adopter, pre-registered before the first sample: "a pod at the isolated rung is admitted and Running", and "it reaches neither the API server nor the internet, while a baseline pod does". Grade them in the same sample and the same citable run.
2. If the clock: give `truth.yml` an ephemeral KinD of the shape `drift-sample.yml` already proves, checksum-pinned, deleted on exit, and let the eleven platform live tails run against it under a name they can find.
3. Either way: the identity plane's six scripts either grade on a lane, or move to `talk/verify-exclusions.txt` with a reason and NORTH-STAR §1 reads "every artefact is attestable".
4. Correct the SKIP reason lines so they state the absence rather than restating the claim.

Done = "the bottom rung runs and reaches nothing" is a PASS on a citable TRUTH line, or the record says in ADR form that cage behaviour is proven offline only and the deck says the same.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R5. Findings: thesis/TF-05, principles/P2-6, security/SS-02, engineering/EQ-06, truth-surface/TS-C2 (ceiling). The adopters' lane already samples an ephemeral cluster per run with pinned tools.

## Comments

**2026-09-02, ticket 75 resolved.** Q8 is (b), delegated: the lane branch (item 1), with the ceiling published on the TRUTH line by ticket 83. Item 2 (an ephemeral cluster on the hub clock) is not taken; record it as the road not taken in the ADR-form note item 5 asks for. Q12 is (b): item 3 now belongs to ticket 90 (the six scripts move to the exclusions file with a reason). Unblocked.

**2026-09-04, ticket 90 built.** Item 3 is done, in its exclusions form: the six identity-plane
scripts (`platform/identity/verify-identity.sh`, `.../verify-federation.sh`,
`platform/access/verify-access.sh`, `platform/eud/verify-eud.sh`,
`platform/posture/verify-posture-projection.sh`, `tuppence/reset/verify-reach-secrets.sh`) are in
`talk/verify-exclusions.txt`, each with what it waits for, and NORTH-STAR §1 now reads "every
artefact is attestable" with principle 6 keeping the actor half as shelved design. Item 4 (sharpen
the SKIP reason lines in the estate repos) is NOT done for those six and no longer needs to be:
they are not run, so they print no reason. It stands for whatever the lane of item 1 brings back.
Items 1, 2 and 5 remain this ticket's.

## Answer

**2026-09-10: items 1, 2-as-a-record, 4 and 5 are built and pushed on all three adopters and in
the hub. One half of Done is outstanding and it needs a scheduled run, so the wait is left open.**

Map line: the cage is graded on the adopters' lane and proven offline in the hub, and both
sentences are now in the record.

### What was built

1. **Two facts, in the same sample, on the same run, as the five** (item 1), on
   `policy-as-versioned-driftwood/driftwood`, `-tuppence/tuppence` and `-ludlow/ludlow`, branch
   `ticket-86-the-cage-enters-the-citable-number`:
   - `fact_6_the_bottom_rung_is_admitted_and_runs` — the workload the cage puts on its own bottom
     rung is admitted by the API server and reaches Running and Ready.
   - `fact_7_the_bottom_rung_reaches_nothing_while_the_control_reaches` — that workload completes
     neither a TCP connection to the API server's ClusterIP nor one to an address outside the
     cluster, while a control workload the cage left loose completes both.
   Both are in `ALL_FACT_IDS`, so `_verdict` and `grade` score them exactly as they score the five.
2. **The pre-registration**, `drift/window.yaml` section `cage_behaviour_sample`: the question, what
   is measured and what is not, the experiment in full, the two facts, four falsifiers, the
   operation, and the road not taken. Committed before any sample can score it, and the instrument
   proves that rather than asserting it (below).
3. **The lane builds the cage's own stand-in sidecar**: `.github/workflows/drift-sample.yml` builds
   `graded/waf-placeholder` out of platform's tree at the tag this repository already pins, under
   the name the cage injects, and loads it into the ephemeral node. Round 4 of the wait order
   (ticket 107) is untouched, and `verify/sampler-wait-order/verify-sampler-wait-order.sh` grades
   the three patched files PASS.
4. **ADR-0028** (item 5), `docs/adr/0028-cage-behaviour-is-graded-on-the-adopters-lane-and-proven-offline-in-the-hub.md`:
   what is proven and how, the six decisions, the road not taken with its reasons and its cost, and
   the consequences.
5. **The deck says the same** (item 5): the step-4 narration in `talk/narration.json` now says, in
   the presenter's own voice, that on every citable run the cage claim is proven offline only, that
   the live instrument has recorded could-not-look every time, that the presenter has seen it hold
   on a laptop and may not quote that, and that the adopters' lane now takes two more facts whose
   verdict is not yet in. `talk/deck.md` is regenerated; `talk/verify-demo.sh` PASSes.
6. **A grader that could not fail** (found here, fixed here): `grade` accumulated its verdict with
   `max(verdict, 1)`, so a fact observed FALSE after any earlier could-not-look was reported as a
   could-not-look. Measured on `origin/main`, unmodified: `five-facts.py grade` returned 3 over
   each adopter's own committed `drift/samples.jsonl` while its own output carried three `FALSE`
   lines. Fixed to a named `_worse()` with a selfcheck. Without it fact 6's FALSE would have been
   laundered into a skip and this ticket would have delivered nothing.

Item 4 (the SKIP reason lines state the absence) is satisfied by construction rather than by
correction: every could-not-look these facts can print names what was absent — the control reached
nothing either, the cage put both pods on the same rung, no cage is installed, the connect could not
be run, nothing in the cage selects the pod — and none restates the claim.

### Decisions, all delegated under ADR-0025, with reasons

1. **The wording, and what each fact is about.** Fact 6 is ADMISSION AND LIFE; fact 7 is REACH.
   They are two facts and not one because they fail for different reasons and one must never hide
   inside the other: a pod that was refused, or that never started, also reaches nothing, so a
   single fact would grade a cage that is a gate exactly as it grades a cage that holds.
2. **One window entry, two fact ids.** They share one experiment, one setup, one control and one
   set of falsifiers, so they are one pre-registration; they are scored independently because they
   fail independently.
3. **The pods are created by the lane, not assumed to exist.** A pre-existing pod would carry
   somebody's earlier decision about its rung, and the question is what the cage does to a workload
   that declares nothing. Both namespaces are deleted at the end of the sample whatever happened.
4. **The rung is derived and never named.** The instrument creates a `governed` namespace with NO
   tier and lets the cage's own fall-closed rule decide, and a non-governed namespace for the
   control so the cage picks its loosest rung. The word `isolated` appears nowhere in the probe. An
   adopter whose composed array declares a different ladder gets its own answer with no edit.
5. **A cluster that is there and a pod that never becomes Ready is FALSE, not could-not-look** —
   with one exception. A pod stuck on the sidecar the cage injected, or on the hardening the cage
   wrote, did not run *because of the cage*, and NORTH-STAR §4 step 4 says the workload keeps
   running. The exception is the pod the cluster never SCHEDULED (`PodScheduled=False`), which is
   the runner's capacity and not the cage's doing, and reads could-not-look. A pod still in
   `ContainerCreating` when the bounded wait ran out says so in its own sentence.
6. **The probe image is the cage's own placeholder, built from platform's tree at the pin.** The
   cage injects `ghcr.io/acme/coraza-waf:cage`, which exists in no registry; without a stand-in
   every hardened pod sits in ErrImagePull and the fact measures a registry. Platform already
   carries the stand-in and the lane already checks platform out at the pin, so nothing is invented
   or vendored here. Recorded on the fact, with the ceiling: a sleeping busybox is not a WAF.
7. **No new hub gate script.** The pre-registration is graded by the instrument that scores the
   facts — `grade` FAILs outright while `window.yaml` does not declare both fact ids and all four
   falsifiers — and that grade already runs under the gate through each adopter's
   `verify-reconcile.sh` and through `verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh`. A hub
   copy would be a second ruler for one rule, which is how one of them goes on passing after the
   other is fixed.

### The registration commit, and how I know it precedes any score

The registration is not a date typed in a file. `cage_registration()` runs
`git log --first-parent --reverse -S <fact 6's id> refs/remotes/origin/main -- drift/window.yaml`
and takes the first commit: the commit that introduced the fact's id into the pre-registration on
the SERVED ref. `grade` scores the two facts only against samples whose `ts` is at or after it, and
says on its own output line which of the two it did.

- On the branch as pushed, the registering commit is driftwood `1d0fdfb`, tuppence `7146412`,
  ludlow `0b508bd` (each `ticket 86: the cage enters the citable number ...`), and it is not on
  `origin/main` yet. Measured: `cage_registration('HEAD')` → `registered by 1d0fdfb6dc25 at
  2026-09-10T04:46:13+01:00`; `cage_registration()` on `refs/remotes/origin/main` → `None`, "no
  commit on refs/remotes/origin/main introduces fact_6... so the cage facts have not been
  registered on the served ref". A branch commit registers nothing, because a branch run records
  nothing (ticket 100).
- **It precedes any score by construction, and the instrument enforces it rather than trusting it.**
  The newest committed sample in each adopter is older than the registering commit, so `grade`
  prints `the cage facts (6, 7) are NOT SCORED on this sample: it was taken 2026-09-09T11:27:02Z,
  before they were registered by 1d0fdfb6dc25 ...` and scores five facts. The first sample that can
  carry facts 6 and 7 at all is the first scheduled run after the merge, which is necessarily
  later. Nothing was backdated and no sample was edited.
- Rewriting either fact's wording after it lands re-registers it on the day of the rewrite and
  every score taken against the old wording stops counting. That is ticket 93's rule for a
  forecast, applied to a fact; it is why the section is written once.

### Red first, and the pairs

Every pair below was measured on a throwaway KinD cluster on 2026-09-10, with its own kubeconfig,
never touching the three named clusters, and deleted after. They are REHEARSALS (ADR-0023 D4):
they are the reasoning behind the instrument, and none of them is cited as gate evidence.

**1. Fact 6 and fact 7 against the cage as the estate declares it today (composed 4.0.0).**

RED — the cage as the lane's cluster actually reconciles it (composed 2.0.0/2.0.1/3.0.0 at the
pinned tag `v1.1.0`), with the PriorityClasses absent exactly as the lane's cluster has them:

    FACT6 False | the cage REFUSED the workload: Error from server (Forbidden): error when
      creating "STDIN": pods "cage-probe" is forbidden: no PriorityClass with name
      cage-baseline-3-0-0 was found
    FACT7 None  | no workload was running on the bottom rung, so there was nothing to measure
      reach from; a pod that never ran reaches nothing for a reason that is not the cage

GREEN — the same instrument, same cluster, against composed 4.0.0 applied in its place:

    FACT6 True | the workload the cage put on its bottom rung (isolated) was ADMITTED and is
      Running, on priority class cage-isolated-4-0-0 (priority -10000), carrying 2 container(s)
      including waf-sidecar injected by the cage
    FACT7 True | the workload the cage put on its bottom rung (isolated) reached NEITHER the API
      server nor 1.1.1.1, while the control workload on baseline reached both from the same
      cluster with the same image -- a connection refused by the cage, not a YAML read

**2. The block is the cage, not the pod.** With `cage-reach-isolated` deleted and nothing else
changed, the same pod reached both:

    isolated pod with the reach cage DELETED -> apiserver: REACHED
    isolated pod with the reach cage DELETED -> 1.1.1.1:80 : REACHED

**3. A wait that answered before the answer could exist — in my own code, caught by running it.**
The first version treated any container waiting reason as settled, so `ContainerCreating` ended the
wait:

    RED:   FACT6 False | the workload was admitted onto the bottom rung (isolated) and never ran:
             app: ContainerCreating (no message); waf-sidecar: ContainerCreating (no message)
           (1.9 seconds after the pods were created)
    GREEN: FACT6 True  | ... was ADMITTED and is Running ...   (11.8 seconds)

That is round 3 of the sampler wait order (ticket 107) one level down, and it is now a named
constant, `CAGE_TRANSIENT_WAITS`, with the measurement in its comment.

**4. The grader could not fail.** RED, `origin/main` unmodified, over driftwood's own committed
`drift/samples.jsonl`:

    ON MAIN: rc = 3
    last line: SKIP: a fact could not be looked at, and a fact not looked at is never a pass
    false facts: 3

GREEN, on this branch: `rc = 1`. Selfcheck: `_worse(3, False) == 1`.

**5. Six branches of fact 7, in the selfcheck, with no cluster** (a fixture that answers only what
the fact asks): the green; the pod that reached (FALSE, falsifier 2); the control that reached
nothing either (null, falsifier 3, "UNMEASURED"); both pods on the same rung (null, falsifier 4);
no NetworkPolicy selecting the pod (null, "nothing in the cage SELECTS IT"); an exec that never ran
the connect (null, "could not be RUN"); and a workload that never ran (null). All three adopters'
`five-facts.py selfcheck` exit 0.

**6. The registration cannot be faked into existence.**
`cage_registration('refs/remotes/origin/no-such-ref-for-a-selfcheck')` returns `None` with a reason
naming the ref, asserted in the selfcheck: an unreadable served ref leaves the facts unscored, never
quietly passed.

### Per adopter, before and after, in clean clones

Every `verify-*.sh` in each adopter, run from a fresh clone of `main` (before) and of the pushed
branch (after).

- **Plain clone, as `git clone` leaves it:** identical exits on all three adopters — driftwood 3,0,3,3,3,3;
  tuppence 0,1,0,3,3,3; ludlow 3,3,0,3,3.
- **With `gpg.x509.program gitsign` configured, which is what `clone-estate.sh` leaves and therefore
  what the truth runner sees:** exactly one change per adopter, and it is the intended one.
  `verify-reconcile.sh` goes **3 → 1** on driftwood, tuppence and ludlow. Every other script is
  unchanged, including tuppence's pre-existing `scripts/verify-adopter-gate.sh` red (rc 1 before and
  after, not this ticket's).

### What the citable number will do, and why

On run 225 the four scripts that grade the lane sample recorded SKIP with the tail `a fact could not
be looked at`, while the sample they graded carried three `FALSE fact_5_...` lines: that is decision
6's defect. With it fixed, `.estate-clone/{driftwood,ludlow,tuppence}/verify-reconcile.sh` and
`verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh` exit 1 where they exited 3, so four scripts
move from the skip column to the fail column. Run 225's line, for the reader who wants the before:
`pass=78 [observed=24 self=41 simulated=4 meta=9] fail=8 skip=30 [never=9 waits=21] excluded=8
total=124 ceiling=105`. Nothing about the estate got worse; the instrument stopped softening what it
saw. The manifest rows for those four are annotated to say so, and their `waits:` patterns are kept
and expected to stop matching; `talk/truth_manifest.py judge` says `declared waits` for each of the
four real SKIP tails and `undeclared` for an invented reason.

### The half of Done that is outstanding, and exactly what closes it

Done reads: *"the bottom rung runs and reaches nothing" is a PASS on a citable TRUTH line, OR the
record says in ADR form that cage behaviour is proven offline only and the deck says the same.*

- **The second branch is closed.** ADR-0028 says it, and the deck says it in the presenter's voice.
- **The first branch is open, and needs two things that are not this ticket's to do.**
  1. **A scheduled run of the adopters' lane.** Only `.github/workflows/drift-sample.yml` on its
     06:20 UTC cron produces a citable sample. A run triggered by hand is a measurement and not the
     scheduled observation the Done line names, and a hand-taken sample is a rehearsal that is never
     appended or cited (ADR-0023 D4). This wait is left open, as ticket 107 left its own.
  2. **The composed pin must carry the cage release.** Every adopter's ResourceSet array declares
     2.0.0, 2.0.1 and 3.0.0 and the pin is tag `v1.1.0`, whose tree stops at 3.0.0. The `isolated`
     rung, the fall-closed rule and the per-rung reach projection are all in
     `composed/policies/v4.0.0`, which the array does not declare. Until a reviewed pull request
     adds the element and moves the pin to a tag whose tree carries it — the move
     `gitops/composed/composed-set.yaml` has named in its own comment since 2026-08-28 — fact 6 will
     read FALSE and fact 7 will read could-not-look on every scheduled run, and honestly so.
- **So the first citable score will be a red.** It will be the API server's own words about the cage
  the estate actually delivers, which is the most useful thing this instrument can say on the day it
  starts saying anything.

### Not this ticket's to fix, found while measuring

1. **The composed set omits `priorityclasses.yaml`.** Platform ships one in every
   `distribution/policies/v*/`; every adopter's `composed/policies/v*/` has five files and not six.
   `cage-tier` therefore names PriorityClasses that the set delivering it does not deliver, and the
   API server refuses every pod it touches: measured, `no PriorityClass with name
   cage-baseline-3-0-0 was found`. This is a composition defect, and it is the direct cause of the
   red above.
2. **The served cage carries ticket 98's instance 1.** With the classes supplied by hand, composed
   3.0.0 still refuses: `the integer value of priority (0) must not be provided in pod spec;
   priority admission controller computed -10 from the given PriorityClass name`. 3.0.0's
   `cage-tier` writes `priorityClassName` without the priority trio — the exact defect
   `verify/refusal-by-another-name/` exists to catch, live on all three adopters' served version.
3. **Ticket 98's scan grades no adopter cage at all.** It reads the working tree; the adopters'
   SERVED versions exist only in the tree at tag `v1.1.0`, and the version on disk (4.0.0) is not
   declared by the array, so `refusal_scan.py --inventory` classes all three `unserved-on-disk` and
   excludes them: *"v4.0.0 is on disk and driftwood's version array does not declare it, so Flux has
   pruned it: history, not service"*. That reason is also the wrong way round — 4.0.0 is not history
   but a composed version not yet pinned — and the population it excludes is the only cage any
   adopter actually serves.
4. **Nothing else grades the lane's own instrument.** `five-facts.py selfcheck` is not run by any
   hub check; the adopters' `verify-reconcile.sh` calls `grade` and never `selfcheck`. Its asserts
   caught two real defects while this was built and no gate would notice if they stopped running.

## Self-review rounds, 2026-09-10 — three findings, all in my own code, all fixed on the branch

None of these was reported by anything. Each was found by running the instrument or by re-reading
the rule it claims to obey, and each is the same failure one level down: a question answered before
its answer could exist, or a rule half built.

**R1 — the same-rung question was asked last, after four connects** (adopter commits `ecb7dc6`,
`08484cd`, `dff7d13`). Fact 7 measured reach and only then noticed that the cage had put both
workloads on the same rung. On the composed version every lane actually reconciles today that is the
live case, and that cage locks down every caged pod alike, so the control would come back silent and
the fact would have said *"the control reached nothing either"* — true, and less than *"this cage has
no bottom rung distinct from its loosest one"*. The question needs no network and no exec, so it is
asked first now, and the connects run only where there is a rung below the loosest one.

**R2 — my own bound read as the cage failing** (`42d304e`, `8fb231c`, `91946ce`). Fact 6 graded
FALSE whenever the bounded wait ran out with the pod still in `ContainerCreating`. An instrument
that runs out of patience must not assert that the cage prevented a workload from running. The
verdict is now `_cage_admission_verdict(state, applied_ok)` with seven asserts. Three states are
could-not-looks because they are not verdicts the cage reached: a pod the cluster never SCHEDULED
(the runner's capacity), a pod still coming up at the bound (this instrument's bound), and an apply
that reported success with no pod behind it. Everything else that leaves a caged workload not
running is the cage's doing, because the only difference between it and an ordinary pod is what the
cage wrote onto it.

**R3 — I had built the cheap half of ticket 93's rule and not the half that costs something**
(`1ae6742`, `02d9deb`, `e6d8430`). The rule is that a question rewritten after it landed
re-registers, so every score taken against the old wording stops counting. My first cut keyed on the
FIRST commit that introduced a fact id — so the question could have been reworded, a claim narrowed,
a falsifier softened or a ceiling deleted while the facts were being scored, and nothing would have
moved. `cage_registration` now walks the first-parent history of `drift/window.yaml` on the served
ref, reads the `cage_behaviour_sample` block out of each blob, and returns the NEWEST commit at
which that block changed.

Measured on a throwaway clone of the pushed branch, four commits deep:

    BEFORE a rewrite:                   registered by 1d0fdfb6dc25 at 2026-09-10T04:46:13+01:00
    AFTER  a rewrite of the question:   registered by 067b1a017878 at 2026-09-10T06:32:35+01:00
    AFTER  a comment-only change:       registered by 39d25145941f at 2026-09-10T06:32:35+01:00
    AFTER  an edit outside the section: registered by 39d25145941f  (unmoved)

The unit is the SECTION and not the file, and the difference from ticket 93 is in the docstring
rather than left to be found: this window carries three instruments and an addendum to one of the
others is not a rewrite of this question. Within the section it is raw text, comments included,
because a comment here carries the reasoning a reader trusts and a rule that re-registers on a
changed claim but not on a rewritten reason would let the reason be weakened under a fact already
being scored.

**The registering commit is unchanged by all three rounds**: driftwood `1d0fdfb`, tuppence `7146412`,
ludlow `0b508bd`. R1, R2 and R3 touch `drift/five-facts.py` only; `drift/window.yaml` has not been
edited since it landed, which is exactly the property R3's rule now measures.

### The gate run of the final hub head before these rounds

Run **230**, `gh run view 34439399424`, on hub `5050b08`, a push to
`ticket-86-the-cage-enters-the-citable-number`. **A branch run records nothing** (ticket 100) and the
run says so in its own log: *"the line above is NOT being written to talk/truth.log: this run is on
ticket-86-..., not main, and only main's talk/truth.log is citable"*. Quoted from the run log,
therefore, and never citable:

    TRUTH 2026-09-10T05:30Z run=230 hub=5050b08 enact=development units=[driftwood=a181725@main
    feeds=ca40396@main ico=9653fd9@main insurer=61fba9d@main ludlow=2c2d740@main nist=f83126f@main
    platform=8da250d@main tuppence=bd15aae@main] pass=78 [observed=24 self=41 simulated=4 meta=9]
    fail=8 skip=30 [never=9 waits=21] excluded=8 total=124 ceiling=105

Figure for figure the same as run 225 on `main`, which is the expected answer: the units are still at
their own mains, so the hub half of this ticket moves the record and not the number. The run's
conclusion is `failure`, as `main`'s own runs 34425782322 and 34422085511 are, on the estate's
standing eight reds.
