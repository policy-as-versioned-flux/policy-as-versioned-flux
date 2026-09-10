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

Historical map summary, superseded 2026-09-10 during integration review: the cage is graded on
the adopters' lane and proven offline in the hub, and both sentences are now in the record.

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
  what the truth runner sees:** at most one change per adopter, and it is the intended one.
  `verify-reconcile.sh` goes **3 → 1** wherever that adopter's newest lane sample carries a fact
  observed FALSE. Every other script is unchanged, including tuppence's pre-existing
  `scripts/verify-adopter-gate.sh` red (rc 1 before and after, not this ticket's).
- **Re-measured 2026-09-10 against each adopter's own `main` as it stands**, after driftwood's
  11:23Z scheduled sample landed: tuppence **3 → 1**, ludlow **3 → 1**, driftwood **3 → 3**, because
  driftwood's newest sample now carries no FALSE at all — ticket 107's round-4 wait order working.
  An earlier measurement, against the samples of 2026-09-09, gave 3 → 1 on all three. Both are
  recorded because the difference between them is the point: this change makes the grader tell the
  truth about whatever the lane observed, and what the lane observes moves.

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
therefore, and never citable. `talk/truth.log` records no such line and this quotation is **not citable**:

```
TRUTH 2026-09-10T05:30Z run=230 hub=5050b08 enact=development units=[driftwood=a181725@main
feeds=ca40396@main ico=9653fd9@main insurer=61fba9d@main ludlow=2c2d740@main nist=f83126f@main
platform=8da250d@main tuppence=bd15aae@main] pass=78 [observed=24 self=41 simulated=4 meta=9]
fail=8 skip=30 [never=9 waits=21] excluded=8 total=124 ceiling=105
```

Figure for figure the same as run 225 on `main`, which is the expected answer: the units are still at
their own mains, so the hub half of this ticket moves the record and not the number. The run's
conclusion is `failure`, as `main`'s own runs 34425782322 and 34422085511 are, on the estate's
standing eight reds.

## The battery, and what it says

**On the branch and on a throwaway merge onto `origin/main`.** The merge is a fast-forward and the
trees are identical — `git diff --stat <branch> <merge>` is empty — so anything measured on one is
measured on the other, and both were run anyway.

| check | branch | throwaway merge onto `origin/main` (6fd9cc1) |
|---|---|---|
| `talk/verify-all.sh --selfcheck` | PASS, exit 0, 7s | PASS, exit 0, 7s |
| a full local gate run (`talk/verify-all.sh`, no flag) | ran to completion, exit 1 | ran to completion, exit 1 |
| `verify/cited-truth/verify-cited-truth.sh` | PASS | PASS |
| `verify/every-green/verify-every-green.sh` | PASS | PASS |
| `verify/truth-line/verify-truth-line.sh` | PASS | PASS |
| `talk/verify-demo.sh` | PASS | PASS |
| `talk/truth_manifest.py check` | rc 0 | rc 0 |
| `mypy twin tests conftest.py` | Success, 189 files | Success, 189 files |
| `pytest -q` | 7 failed, 2525 passed | 7 failed, 2525 passed |

**The selfcheck row was mislabelled and is corrected here (review F-13).** `talk/verify-all.sh`
matches only the double-dashed `--selfcheck`; a bare `selfcheck` matches no case, is silently
ignored, and the script runs the full local gate. That is what the first version of this table timed
at thirty-five minutes and reported as a selfcheck exiting 1, and it is why the row needed a
paragraph of caveat under it. With the real flag it is seven seconds and exits 0 on both trees. A
battery row that names one thing and runs another is the shape this ticket exists to fix, one level
up. Both rows are kept: the full local gate run is worth having, under its own name.

**The local full-gate numbers are not the runner's and are not quoted as such.** This machine
has docker and the three named KinD clusters, so the live tails the manifest classes `never:` do
run here and several fail; the manifest's own header names that substrate difference. On the serial
merge run the line reads `pass=70 fail=30 skip=17 excluded=8 total=125 ceiling=106`, and three of
those thirty are the adopters' `verify-reconcile.sh` taking their LIVE path and printing
`GitRepository ... points at the in-cluster git server` — a reason that exists only on a machine
with those clusters. The comparison that means anything is the gate run below and the clean-clone
adopter runs above.

**The seven pytest failures are `origin/main`'s, not this branch's.** One is the standing red,
`flux_coverage_floor_is_still_reachable` (build ticket 70's finding 1). The other six are
`tests/test_map_surface.py` (four) and `tests/test_can_record.py` (two); running exactly those two
files gives `6 failed, 68 passed` on a clean `origin/main` worktree at 6fd9cc1, and the same six at
88fe6fc. The whole suite on a clean `origin/main` worktree gives `23 failed, 2499 passed` — worse,
because that worktree has no estate clone — so the outcome there turns on the checkout's estate
clone and not on anything here. `.github/workflows/twin.yml` is `failure` on `main`'s own last three
runs.

### The gate run of the final head

Run **232**, `gh run view 34441742700`, hub `269bcc5`, conclusion `failure` — as `main`'s own runs
are, on the estate's standing eight reds. **A branch run records nothing** (ticket 100), so this
line is quoted from the run log and is not citable. `talk/truth.log` records no such line and this quotation is **not citable**:

```
TRUTH 2026-09-10T06:18Z run=232 hub=269bcc5 enact=development units=[driftwood=a181725@main
feeds=ca40396@main ico=9653fd9@main insurer=61fba9d@main ludlow=2c2d740@main nist=f83126f@main
platform=8da250d@main tuppence=bd15aae@main] pass=78 [observed=24 self=41 simulated=4 meta=9]
fail=8 skip=31 [never=9 waits=22] excluded=8 total=125 ceiling=106
```

Against run 225 on `main` (`pass=78 ... fail=8 skip=30 [never=9 waits=21] excluded=8 total=124
ceiling=105`) the hub half of this ticket moves `pass` and `fail` not at all; `total`, `skip`,
`waits` and `ceiling` are each one higher because ticket 31's sensor-admission check landed on
`main` between the two runs. That is the expected answer: the units are still at their own mains,
so until the three adopter branches merge, the hub half moves the record and not the number.

Run **233**, `gh run view 34446814409`, was then dispatched on hub `df413c1` -- the head that
carries the whole build, record included -- and reads the same line, figure for figure. `talk/truth.log` records no such line and this quotation is **not citable**:

```
TRUTH 2026-09-10T07:13Z run=233 hub=df413c1 ... pass=78 [observed=24 self=41 simulated=4
meta=9] fail=8 skip=31 [never=9 waits=22] excluded=8 total=125 ceiling=106
```

**A record commit cannot name its own run**, and this paragraph is the proof: naming run 233 moves
the head past the commit run 233 measured. The regress terminates here rather than being hidden --
everything after `df413c1` is these three sentences, and a run of the head that carries them would
find the same 125 scripts.

**Final heads.** Hub `df413c1` plus this note; driftwood `cecd1e4`, tuppence `c069cf2`, ludlow
`a9f2f7c`, each `verify-reconcile.sh` rc 1 and `drift/five-facts.py selfcheck` rc 0 in a clean
clone with gitsign configured. Nothing is merged.

## The fall this merge will record, and the order to merge in (review F-06)

**Predicted by MECHANISM, not by a number, because the number moves daily.** Under this estate's
contract a rise in `fail` on the run that records it is a blocking event and owes an entry in
`talk/verify-falls.txt`, in that file's own grammar (`run=N | reason`), keyed to the run that
records it.

**The rule that decides how many rows move**, which is what should be written down rather than a
count that will be stale by the time it is read: after the merge, one row moves SKIP -> FAIL for
**each adopter whose newest lane sample, on the day, carries a fact observed FALSE**, plus
`verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh` when the adopter IT grades (driftwood) is one
of them. Nothing else in the four moves, and no other check is touched.

**The first version of this paragraph said four rows, and it was already out of date when I wrote
it.** It was measured against run 225's grade table, where all three adopters carried
`FALSE fact_5_every_rendered_object_is_in_the_flux_inventory`. Ticket 107's round-4 wait order has
since done its work: re-measured 2026-09-10 against each adopter's own `main` after driftwood's
11:23Z scheduled sample (run 34470909429),

| adopter | FALSE facts in its newest lane sample | `verify-reconcile.sh` before | after |
|---|---|---|---|
| driftwood | 0 | SKIP (3) | SKIP (3) — no change |
| tuppence | 3 | SKIP (3) | FAIL (1) |
| ludlow | 3 | SKIP (3) | FAIL (1) |

so a merge on 2026-09-10 records `fail` **+2**, not +4: driftwood's sample is clean, so its row does
not move and neither does step 4's, which grades driftwood. A merge on a day when driftwood's
sample is red again records +3 or +4. **Write the entry from the two grade tables on the day.** The
prediction here is the mechanism and the direction; the count is whatever the lane observed.

**The cause is not a regression.** All four grade the adopters' lane sample through
`drift/five-facts.py grade`, and that grader accumulated its verdict with `max(verdict, 1)`: once
any earlier fact had been recorded as a could-not-look the verdict was 3, and `max(3, 1)` is 3, so
every fact observed FALSE after it was reported as a fact that could not be looked at. On run 225's
own grade table all four rows read
`SKIP: ... a fact could not be looked at, and a fact not looked at is never a pass`, while the
sample they graded carried three `FALSE fact_5_every_rendered_object_is_in_the_flux_inventory`
lines. Nothing about the estate gets worse at that run; four already-true reds stop being laundered.
The reds themselves are ticket 107's and ticket 81's to clear, not this ticket's.

**A draft of the entry, to be dated and given its real run number on the day** — the integrator
writes it, and it should not have to be reconstructed:

    run=N | 2026-09-DD, ticket 86's merge across the three adopters. `fail` rose F -> F+K and
    `skip` fell S -> S-K between run <before> (hub <sha>) and run N (hub <sha>). The K rows are
    <named from the two grade tables>, each SKIP -> FAIL, one per adopter whose newest lane sample
    carried a fact observed FALSE, plus verify-e2e-step4 if driftwood was among them; measured by
    diffing the grade tables the two recording commits carry, not inferred from the counts.
    NO CHECK OF THE ESTATE LOST A GREEN. All of them
    grade the adopters' lane sample, and ticket 86 fixed a grader that could not fail:
    `max(verdict, 1)` softened every fact observed FALSE that followed a could-not-look, so those
    four SKIPs were already FAILs that the instrument was reporting as could-not-looks -- on run
    225 all four printed "a fact could not be looked at" over a sample carrying three
    `FALSE fact_5_...` lines. The underlying red is fact 5, owned by tickets 81 and 107. Ticket 86
    owns the instrument, and the instrument is now telling the truth.

**Merge order, which I will hold to:**

1. **The hub branch first.** It moves the record and not the number — proved three times, runs 230,
   232 and 233 all read `pass=78 fail=8` against `main`'s own run 225 — so ADR-0028, the manifest
   annotations and this ticket are on `main` and findable *before* any run records the rise they
   explain.
2. **Then the three adopters, all three before the next 06:20 UTC lane cron**, so all three register
   their pre-registration on the same day and the first scheduled sample that can carry facts 6 and
   7 carries them for the whole estate rather than for one adopter. Order among the three does not
   matter; being inside one cron window does.
3. **Then the falls entry, on the day, keyed to the run that records it**, from the two grade tables
   rather than from this prediction. If the four rows are not exactly the four named above, the
   entry says what actually moved and this paragraph was wrong.

## Adversarial review, 2026-09-10 — five findings taken, one renamed

Three blocking, two major, one minor. All six are addressed; the code fixes carry their own red and
green above and in the adopter commits.

| # | finding | where |
|---|---|---|
| F-01 | the record cited run 233, which `talk/truth.log` does not carry, so `verify/cited-truth` exited 1 | hub `89fd9c9` |
| F-02 | fact 7 could go green when the cage was not the reason | adopters `a0ad108` / `40f05bb` / `a4cb73b` |
| F-03 | fact 6 went green for a pod the cage never touched | same |
| F-04 | the pre-registration section was unbounded at end of file | same |
| F-06 | no falls entry and no merge order for a predicted `fail` +4 | the section above |
| F-13 | a battery row named `selfcheck` that ran the full local gate | the table above |

**F-01.** Only a FENCED block inherits the paragraph above it as the scope a `not citable` marker
may live in. My run quotations were indented blocks, so the marker did not bind. All three are now
fenced with the disclaimer in the preamble. Runs 230 and 232 were not flagged and are fixed anyway:
they escaped only because their `run=` and `pass=` tokens happened to land on different wrapped
lines, and an exemption that rests on where a line wrapped is not an exemption.

**F-02, F-03, F-04** are in the adopter commit above, each with the measurement that found it.
F-03's red was reproduced live on a throwaway cluster; F-02's over the real function with sleeps
counted; F-04's on a throwaway clone with the served ref advanced commit by commit.

**F-13** is the reporting version of this ticket's own defect, and it is named as such in the
battery section: `talk/verify-all.sh` matches only `--selfcheck`, so a bare `selfcheck` ran the
whole local gate for thirty-five minutes under the wrong name. Both rows are now in the table, each
under the name of what it actually runs.

### Charted rather than built

The reviewer's remaining findings are non-blocking and I have not built them. Two are worth naming
because they are real:

- **`_cage_networkpolicies` matches on the two labels the cage stamps**, so a NetworkPolicy
  selecting the bottom-rung pod on some other label is not counted, and fact 7 becomes a
  could-not-look on a cage that is really holding. A false red, never a false green, and it is on
  the function's own docstring. Fixing it properly means implementing label-selector semantics
  including `matchExpressions`, which is a second implementation of something the API server owns.
- **The two connects are two ports on two addresses.** "Reaches nothing" is grounded in exactly
  those, and the fact says so on its ceiling. Widening it is a measurement design question, not a
  defect.

### The battery and the gate run, after the review round

Branch and a throwaway merge onto `origin/main` at `21b4514`: real merge, **zero conflicts**, and
the two trees identical (`git diff --stat` between them is empty).

| check | branch | throwaway merge |
|---|---|---|
| `talk/verify-all.sh --selfcheck` | PASS, exit 0 | PASS, exit 0 |
| `verify/cited-truth/verify-cited-truth.sh` | PASS | PASS |
| `verify/truth-line/verify-truth-line.sh` | PASS | PASS |
| `verify/every-green/verify-every-green.sh` | PASS | PASS |
| `talk/verify-demo.sh` | PASS | PASS |
| `talk/truth_manifest.py check` | rc 0 | rc 0 |
| `mypy twin tests conftest.py` | Success, 189 files | Success, 189 files |
| `pytest -q` | — | 7 failed, 2525 passed |

`truth-line` and `every-green` first returned 3 in the merge worktree, on
`SKIP: no .estate-clone (run clone-estate.sh)`; the branch worktree had a clone and the merge
worktree did not. Given the same substrate — the branch's clone COPIED across rather than
re-fetched, because `--refresh` near a shared clone deletes other builders' worktrees — both PASS.
The seven pytest failures are the same seven as before and are `main`'s: one standing coverage-floor
red and six that reproduce file-for-file on a clean `origin/main` worktree.

The gate run of the final head is run **238**, `gh run view 34474968513`, hub `40dde19`, conclusion
`failure` as `main`'s own runs are. `talk/truth.log` records no such line and this quotation is
**not citable**:

```
TRUTH 2026-09-10T12:34Z run=238 hub=40dde19 enact=development units=[driftwood=b0eb73a@main
feeds=c3c654a@main ico=abcb3a8@main insurer=61fba9d@main ludlow=2c2d740@main nist=f83126f@main
platform=5b88f1d@policy/v5.0.0 tuppence=bd15aae@main] pass=80 [observed=25 self=42 simulated=4
meta=9] fail=8 skip=29 [never=10 waits=19] excluded=8 total=125 ceiling=106
```

`fail=8`, unmoved, for the fourth time across runs 230, 232, 233 and 238: the hub half of this
ticket moves the record and not the number. `pass` is 80 rather than 78 and `platform` is read at
`policy/v5.0.0` because three signed tags were cut this morning on the owner's authorisation; that
is the estate's own step and none of it is this ticket's.

Run **239**, `gh run view 34478290894`, was then dispatched on hub `a21e99c` — the head carrying
the whole build and the whole review round. `talk/truth.log` records no such line and this
quotation is **not citable**:

```
TRUTH 2026-09-10T13:09Z run=239 hub=a21e99c enact=development units=[driftwood=aa8ca08@main
feeds=c3c654a@main ico=abcb3a8@main insurer=61fba9d@main ludlow=2c2d740@main nist=f83126f@main
platform=5b88f1d@policy/v5.0.0 tuppence=bd15aae@main] pass=80 [observed=25 self=42 simulated=4
meta=9] fail=8 skip=29 [never=10 waits=19] excluded=8 total=125 ceiling=106
```

Identical to run 238. Every one of the five branch runs this ticket has taken — 230, 232, 233, 238,
239 — is a branch run whose figures are **not citable**, and across all five the `fail` count did
not move. The regress named earlier applies again and terminates the same way: everything on this
branch after `a21e99c` is this paragraph.

**Final heads.** Hub `a21e99c` plus this note; driftwood `35e46ee`, tuppence `40f05bb`, ludlow
`a4cb73b`. Each adopter's `drift/five-facts.py selfcheck` exits 0 in a clean clone. Nothing is
merged, and all four `main` branches are untouched.

## Integration preparation, 2026-09-10

The existing hub branch at `f0f8ea7` was combined without conflicts with PR 77's reviewed
head `1abb816` in an isolated worktree. No merge commit or push was made. The newer ticket-109
generator and map-transcription checks remain byte-identical to that base; its manifest census
cleanup survives. The deck was regenerated with that generator from recorded run 235's committed
captures, rather than copying the older generated deck.

Focused deck, map-surface and cited-truth tests: 159 passed. The citation checker and the deck's
public check pass; the map's figure, reference, link and exact-transcription checks report no
findings (eight exact copies, 38 disclosed historical summaries before the canonical ticket-86 copy below was added). Manifest syntax/exclusions
validation passes, with the expected notes that this isolated hub worktree contains no adopter
clones. These are local integration checks, not a citable run of the merged changes.

Both independent reviews remain due before completion. The three existing adopter branches were
not edited or merged. Scheduled facts 6/7 and the signed composed-pin migration remain pending;
no rehearsal or dispatched sample was substituted for those observations.

## Integration spec-review corrections, 2026-09-10

The reviewer found two live summaries that still predicted a fixed rise after the ticket had
already corrected that prediction. The map and ADR-0028 now derive any fall from the newest
samples and the two recorded grade tables on the day, with no fixed next-run count. Run 225's
four-row measurement remains dated history. The map also follows ADR decision 4: registration
is the newest first-parent change to the registration section, not the commit that introduced
the fact ids. Changes outside the section do not re-register it.

The earlier prose map summary remains labelled historical. The current exact transcription
below is graded by ticket 109's comparison so future divergence cannot pass silently.

Map line: `- [86 — The cage enters the citable number](issues/86-the-cage-enters-the-citable-number.md) — open, built and pushed 2026-09-10 on all three adopters and in the hub, not merged. Ticket 75 Q8 took the lane branch, so the estate's most distinctive claim -- nothing is denied, and the bottom rung runs and reaches nothing -- is now graded where a cluster exists: two more facts in the same record, on the same scheduled run, as the five. The RUNG IS DERIVED and never named: the sampler creates a governed namespace with no tier and lets the cage's own fall-closed rule decide, and a non-governed one for the control, so the word `isolated` appears nowhere in the probe. The CONTROL is what stops a false green -- a pod that reaches nothing because the cluster is broken must not read the same as a pod that reaches nothing because the cage holds -- so a control that reached nothing either is UNMEASURED against a declared falsifier, and so is a cage that puts both pods on the same rung. Pre-registration is MEASURED: `grade` walks first-parent history on the served ref and reads the newest commit that changed the `cage_behaviour_sample` registration section in `drift/window.yaml`, refusing to score a sample taken before that change (ticket 93's rule, one level down); editing the question, falsifiers or ceilings re-registers it, while edits outside that section do not; a branch commit registers nothing. Two defects found by building it, both fixed here because without them the ticket delivers nothing: a wait that read `ContainerCreating` as a verdict (round 3 of ticket 107 one level down, measured grading a healthy caged pod FALSE 1.9s after creating it), and a grader that could not fail -- `max(verdict, 1)` softened every fact observed FALSE after an earlier could-not-look, measured returning 3 on `origin/main` over a sample carrying three FALSE lines, which is what run 225's four lane-grading SKIPs actually were. The resulting grade change depends on the newest samples when the merge is measured: each adopter whose sample carries an observed FALSE may move from SKIP to FAIL, and step 4 moves with driftwood when it has such a FALSE. Derive the actual changed rows from the two recorded grade tables on the day, and acknowledge only the observed fall with its real run number; no fixed count predicts the next run. ADR-0028 records what is proven and how, and the ROAD NOT TAKEN with its cost: item 2, an ephemeral KinD on the hub clock, was refused because the adopters' lane already builds that cluster, an adopter's own clock observing its own composed set is an estate observation where platform grading platform on a cluster platform built is a self-proof, and eleven `never:` rows becoming passable moves the one number NORTH-STAR publishes; the cost is that the other ten platform live tails stay could-not-looks. The deck says the same in the presenter's voice. **Done is half open**: the ADR-and-deck branch is closed, the PASS branch needs a scheduled run of the lane AND a reviewed pull request that adds 4.0.0 to each adopter's ResourceSet array and moves the composed pin to a tag whose tree carries it -- until then fact 6 reads FALSE on the version in force, with the API server's own words, because the composed set ships `cage-tier` and not the `priorityclasses.yaml` platform ships beside it.`
