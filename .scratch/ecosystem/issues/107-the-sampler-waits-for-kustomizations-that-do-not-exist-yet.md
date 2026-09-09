# 107 — The sampler waits for Kustomizations that do not exist yet

Type: task
Status: open
Blocked by: none

## Question

Round 3 of the sampler wait order (ticket 81) is on all three adopters' `main` and graded green by
`verify/sampler-wait-order/verify-sampler-wait-order.sh`, and tuppence's and ludlow's composed source
still records fact 5 false on every scheduled five-fact sample since the merge: "15 of 16 rendered
objects are in no Flux inventory". The reason is measured in ticket 81's *Recorded 2026-09-08*
section and is not the one the fact's sentence suggests. `kubectl apply -k gitops/composed/` applies
two objects, the GitRepository and the ResourceSet; the fifteen policies are applied by the three
Kustomizations `composed-v2-0-0`, `composed-v2-0-1`, `composed-v3-0-0` that the ResourceSet
generates. Round 3's order runs the Kustomization wait loop BEFORE the ResourceSet wait loop, so the
loop enumerates `get kustomizations -o name` while the composed Kustomizations do not exist yet,
finds only the adopter's own (already Ready) Kustomization, and returns at once. The sample is then
taken the second the composed Kustomizations are created (`composed-v*` aged `0s`, the GitRepository
still `building artifact`), `drift/five-facts.py` reads the inventories once at the top of
`composed_set_facts` and the objects afterwards, and the policies land in between: live and byte-equal
for fact 4, in no inventory for fact 5.

Driftwood is the control. Its facts 4 and 5 read True on the scheduled samples of 09-05, 09-06 and
09-07 under the same workflow, because on each of those three runs its own `kustomizations/driftwood`
does not reach Ready on the ephemeral cluster and the loop's `--timeout=180s` on it stalls the job for
~3 minutes, long enough for `composed-v*` to apply: run 33961154234 timed out at
2026-09-05T10:41:33.58Z, run 34028943241 at 2026-09-06T11:04:14.49Z, run 34122734820 at
2026-09-07T12:40:10.14Z. On 09-08 the stall was not enough and driftwood read fact 3 false,
fifteen absent, inventory 4. A green that rests on a timeout is the accident ticket 81's Decisions
warned about, and it says fact 5 is reachable as defined: the fact is right, the moment of sampling
is wrong.

Fix the moment of sampling so the composed Kustomizations are waited for, on all three adopters, and
make the hub check grade the new order and refuse the old one.

Done = tuppence's and ludlow's newest scheduled `drift/samples.jsonl` line records facts 4 and 5 true
for the composed source, on a run whose Actions log shows `composed-v2-0-0`, `composed-v2-0-1` and
`composed-v3-0-0` `condition met` before the five-fact sample step; driftwood's fact 5 true no longer
depends on `kustomizations/driftwood` timing out; and `verify-sampler-wait-order.sh` grades the new
order on a recorded hub run, with a selfcheck in which round 3's order fails.

## Notes

Charted 2026-09-08 by ticket 81's record. Evidence, all on `origin/main` of the repository named,
measured 2026-09-08:

- tuppence drift-sample run 34228832561 (`ts` 2026-09-08T12:56:30Z): ResourceSet created 12:56:29.36;
  `kustomization/tuppence condition met` 12:56:29.65 (the Kustomization loop, `drift-sample.yml`
  line 183, returns); `resourceset/composed-set condition met` 12:56:30.28 (line 186); the `-o wide`
  listing at 12:56:30.41 shows `composed-v*` at `0s` with no status; sample `ts` 12:56:30Z. Fact 4
  false (one absent, `GeneratingPolicy/cage-netpol-2-0-0`), fact 5 false (15 of 16, inventory 8).
- ludlow drift-sample run 34232921856 (`ts` 2026-09-08T13:36:58Z): the same shape one hour later;
  fact 4 true (all sixteen live and equal), fact 5 false (15 of 16, inventory 8).
- driftwood, all three post-merge green runs: `error: timed out waiting for the condition on
  kustomizations/driftwood` ~3m after that run created the ResourceSet — run 33961154234 at
  2026-09-05T10:41:33.58Z (created 10:38:33.24Z), run 34028943241 at 2026-09-06T11:04:14.49Z (created
  11:01:14.26Z), run 34122734820 at 2026-09-07T12:40:10.14Z (created 12:37:09.78Z) — each with
  `composed-v*` at `2m59s`/`3m` carrying `Applied revision`, facts 4 and 5 true, inventory 19. Run
  34220235347 (09-08): the same timeout, `composed-v*` at `3m` with no status, fact 3 false.
- the same run measures the race inside itself: `take_sample` re-reads the Kustomization list after
  `composed_set_facts` returns (five-facts.py line 330) and fact 3 derives from that later read, so
  tuppence run 34228832561 records `inventory_entries` 8 and, from a strictly later instant, all three
  `composed-v*` having applied `751522b3bca9`.
- The hub check's `NAMES` array (`verify-sampler-wait-order.sh` line 40) requires `Kustomization
  waits` strictly before `ResourceSet waits`. The fix below flips that, so the check goes red on the
  fix unless it changes in the same wave: the eighth instance in the derive-what-you-assert note
  (two green branches, red together on main) is exactly this shape. Its selfcheck fixtures (lines
  75-88) encode the same order and move with it.
- The wait loops are bounded and best-effort by design (`|| true`, "whatever has or has not
  converged when this returns is the state the sample records"). The fix is not to make the sample
  wait for green; it is to make the sample wait for the objects the sampler itself created to have
  been looked at once.

Fix candidates, each with what it costs. No decision is made here.

1. **Round 4 of the order: ResourceSet waits first, then enumerate and wait for Kustomizations.** One
   swap of the two loops in each adopter's `drift-sample.yml`, so the enumeration happens after the
   ResourceSet has generated its children; `wait --for=condition=Ready` on a Kustomization with
   `wait: true` covers apply and health, so the inventory is populated by the time it returns.
   Costs: three adopter pull requests (development mode, pushed and merged as the other hand); the
   hub check's `NAMES` order and its round-3/round-4 fixtures change in the same wave, and the
   integrator runs the check on a throwaway merge onto current `origin/main` before merging either
   side; a fourth round of a fix whose first three shipped mis-ordered, so the selfcheck must make
   round 3's order FAIL, not merely round 2's. Residual: a ResourceSet Ready before its children are
   created is not something the flux-operator API promises in words; it is what both logs show.
2. **Wait by name for the Kustomizations the ResourceSet declares.** Read the versions array out of
   `gitops/composed/composed-set.yaml` (python stdlib plus pyyaml, the estate's rule) and
   `kubectl wait --for=create` then `--for=condition=Ready` each `kustomization/composed-v<slug>`,
   after the ResourceSet wait. Costs: a new marker for the hub check (a seventh line, with its own
   selfcheck cases) instead of a swap; the slugify rule (`2.0.0` to `2-0-0`) reimplemented in the
   workflow, which is a second copy of a rule the ResourceSet template owns; smaller blast radius
   than option 1 because the existing loops keep their order. Residual: the same hub-check coupling
   as option 1.
3. **Move the wait into `drift/five-facts.py`.** Before `composed_set_facts` reads the inventories,
   read the ResourceSet's own inventory, wait a bounded time for each Kustomization it lists to carry
   `lastAppliedRevision`, then sample. Costs: the sampler grows a wait it was designed not to have;
   the workflow's order stops being the thing that decides when the sample is taken, so the hub
   check would be grading something that no longer matters; and a wait inside the instrument is
   harder to see in a log than a `condition met` line. Residual: none of the three adopters' hub
   checks need change, which is the argument for it and the argument against it.

Redefining fact 5 ("the object Flux would render matches what is applied") is not a candidate on this
evidence: driftwood records fact 5 true under the same code when the reconcile has had time, so the
fact is reachable as defined, and the redefinition would have graded a hand-applied object green,
which is the case fact 5 exists to catch (`gitops/composed/composed-set.yaml`, header comment).

Two observations to read before charting anything from them, not part of this ticket's Done:
`kustomizations/driftwood` not reaching Ready on the ephemeral cluster (all four driftwood runs read),
and tuppence's moving fact-4 absence (five objects on 09-06 and 09-07, one on 09-08, none on 09-05),
which is the same race seen from the object side and should close with it.

## Answer

**2026-09-09: round 4 is built and pushed on all three adopters, the hub check grades it and
refuses round 3, and one line of Done is outstanding because it needs a scheduled run.**

### The decision (delegated, ADR-0025)

**Not candidate 1, not candidate 2, not candidate 3: a fourth shape that takes candidate 1's swap
and candidate 2's by-name wait, with the names DERIVED instead of re-spelled.**

Candidate 1 alone was rejected on the ticket's own rule. Swapping the two loops makes the
enumeration run later, but it leaves an enumeration deciding when the sample is taken, and an
enumeration that finds nothing still returns at once and still reads as a wait that succeeded. The
failure mode being removed is *asked a question before the answer could exist and took the silence
for a yes*; a later question with the same shape is the same bug with better odds. Candidate 1's
own residual says as much: "a ResourceSet Ready before its children are created is not something
the flux-operator API promises in words".

Candidate 2's by-name wait cannot go green on an empty enumeration, because a name is not a set:
`kubectl wait kustomization/composed-v2-0-0` either meets the condition or does not, and there is
no third answer where the question was never asked. That is the property this ticket needs. Its
cost was where the names come from — reimplementing `2.0.0` → `2-0-0` in the workflow is a second
copy of a rule the ResourceSet template owns, and two copies of a rule drift.

So the names are not re-spelled. They are read off the live ResourceSet's own `status.inventory`,
whose entries carry Flux's `<ns>_<name>_<group>_<Kind>` ids. The workflow therefore waits for the
objects the ResourceSet says it applied, named by the ResourceSet, and the slugify rule stays in
one place. Deriving what you assert rather than restating it is the estate's standing rule and it
applies here without amendment.

**What those ids are and are not** (corrected 2026-09-10, review F3; the first version of this
paragraph said "the same ids `drift/five-facts.py` reads for fact 5", which is wrong in both
directions). `inventory_ids` reads the union of the **Kustomization AND ResourceSet** inventories
(five-facts.py lines 214-225), and the ids that decide fact 5 are the **fifteen policy ids** that
live in the composed Kustomizations' OWN inventories — which this step never reads. What the step
reads is the ResourceSet's inventory filtered to Kind `Kustomization`: the four objects whose
reconcile populates those fifteen. It is a sound **proxy** for what fact 5 counts, and it is a
different set. The workflow comment now says so.

Candidate 3 (move the wait into `five-facts.py`) was rejected for the reason the ticket already
gives against it: the workflow's order would stop being the thing that decides when the sample is
taken, so the hub check would grade something that no longer matters, and a wait inside the
instrument is invisible in the Actions log. The Done line asks for `condition met` lines in the
log; candidate 3 cannot produce them.

**Why the new order cannot go green on an empty enumeration**, in the order's own words. The
comment block in each adopter's `drift-sample.yml` says it: "AN ENUMERATION THAT FINDS NOTHING IS
NOT A WAIT." Three things enforce it:

1. The derivation is retried, not sampled once: `for _ in $(seq 1 30)` with `sleep 2`, breaking on
   the first non-empty list. An inventory that names nothing yet is a reason to ask again, not an
   answer.
2. An inventory that names nothing after 60s prints a line saying so —
   `wait-order: 60s after the ResourceSets went Ready no ResourceSet inventory names a
   Kustomization; nothing composed was waited for and the sample below records what that leaves`.
   Silence is the one thing round 3 produced and this order will not produce.
3. Each name is then waited for individually, so the log carries one `condition met` line per
   composed Kustomization, which is the evidence Done asks for and which no enumeration can fake.

**Why driftwood's accident is removed** (corrected 2026-09-10, review F2). The first version of
this paragraph said sorting was what removed it — that `composed-v*` sorts above the adopter's own
name, so the composed waits finish before the adopter's own Kustomization stalls the loop. **That
argument is not load-bearing and the claim was wrong.** `drift-sample.yml` sets no
`timeout-minutes` (measured: zero occurrences in all three files), so the job default is 360
minutes and **every member of the union is waited for regardless of order**; the worst case is
about 12 minutes. Sorting changes wall-clock time and nothing else — `sort -u` is there to dedupe
the derived names against the enumeration. The ordering claim was not even generally true: it
holds only for adopter names that sort after the literal `composed-`, and `acme` or `bramble`
would invert it (`composed-v10-0-0` would not).

What actually removes the dependence is that **`composed-v*` is in the wait list at all**. The
wrong sentence also reached `map.md` and all three adopters' first pushed commit messages
(driftwood `872ae63`, tuppence `ff8d5af`, ludlow `5d0993b`); `map.md` is corrected in the same
commit as this paragraph, and the adopter commits were amended to `53b0a48`, `3b49a5a` and
`129d550`, which state the corrected reason. The superseded shas are named here so the correction
is checkable rather than laundered.

**What stayed the same, deliberately.** Every wait is still bounded and best-effort (`|| true`, no
`set -e`). This order does not make the sample wait for green; it makes the sample wait for the
objects the sampler itself created to have been looked at once. A hole is still reported as a fact
observed false, never as a failed job and never as a green.

### The order, before and after

| # | round 3 (on all three adopters' `main` since 2026-09-04) | round 4 (this build) |
|---|---|---|
| 1 | kyverno rollout wait | kyverno rollout wait |
| 2 | flux-operator rollout wait | flux-operator rollout wait |
| 3 | `kubectl apply -k gitops/composed/` | `kubectl apply -k gitops/composed/` |
| 4 | **Kustomization waits** (bare enumeration) | **ResourceSet waits** |
| 5 | **ResourceSet waits** | **composed Kustomizations named** off the ResourceSet's own `status.inventory`, retried, said out loud when empty |
| 6 | — | **Kustomization waits**, over the union of the named ones and the enumeration, sorted |
| 7 | the five-fact sample | the five-fact sample |

### Red first, and the pairs

**1. The workflow, measured against a fake `kubectl` that reproduces exactly what the Actions logs
show** — the apply creates two objects; the composed Kustomizations do not exist until the
ResourceSet has been waited for; the ResourceSet's inventory names them the moment it is Ready;
the unit's own Kustomization is already Ready and answers instantly.

RED, round 3's block as it stands on `main`, whole transcript:

    gitrepository.source.toolkit.fluxcd.io/unit-composed created
    resourceset.fluxcd.controlplane.io/composed-set created
    kustomization.kustomize.toolkit.fluxcd.io/unit condition met
    resourceset.fluxcd.controlplane.io/composed-set condition met
    (get -o wide listing)

No line names a `composed-v*`. That is the bug: the sample is taken next.

GREEN, round 4's block, whole transcript:

    gitrepository.source.toolkit.fluxcd.io/unit-composed created
    resourceset.fluxcd.controlplane.io/composed-set created
    resourceset.fluxcd.controlplane.io/composed-set condition met
    wait-order: the ResourceSet names these Kustomizations; each is waited for by name: kustomization.kustomize.toolkit.fluxcd.io/composed-v2-0-0 kustomization.kustomize.toolkit.fluxcd.io/composed-v2-0-1 kustomization.kustomize.toolkit.fluxcd.io/composed-v3-0-0
    kustomization.kustomize.toolkit.fluxcd.io/composed-v2-0-0 condition met
    kustomization.kustomize.toolkit.fluxcd.io/composed-v2-0-1 condition met
    kustomization.kustomize.toolkit.fluxcd.io/composed-v3-0-0 condition met
    kustomization.kustomize.toolkit.fluxcd.io/unit condition met
    (get -o wide listing)

Three `composed-v* condition met` lines, all above the unit's own, all above the sample step. This
is a harness and not a cluster: it proves the SHAPE of the order, and only a scheduled run proves
the estate. It is recorded as a harness for that reason.

**2. The same block against a ResourceSet whose inventory never names a Kustomization** — the
"empty enumeration" case, which is the one that must not be a quiet pass:

    resourceset.fluxcd.controlplane.io/composed-set condition met
    wait-order: 60s after the ResourceSets went Ready no ResourceSet inventory names a Kustomization; nothing composed was waited for and the sample below records what that leaves
    ...
    elapsed 62s

It retried for 60 seconds and then said so. Round 3 would have printed nothing and moved on in
0.3s.

**3. The hub check.** RED — the NEW `verify-sampler-wait-order.sh` against the three adopters'
`main` as it stands (round 3):

      FAIL driftwood: no composed names derived line (get resourcesets\.fluxcd\.controlplane\.io -o json)
      FAIL driftwood: Kustomization waits (line 180) sits above the ResourceSet waits (line 183)
      FAIL tuppence: no composed names derived line (get resourcesets\.fluxcd\.controlplane\.io -o json)
      FAIL tuppence: Kustomization waits (line 183) sits above the ResourceSet waits (line 186)
      FAIL ludlow: no composed names derived line (get resourcesets\.fluxcd\.controlplane\.io -o json)
      FAIL ludlow: Kustomization waits (line 183) sits above the ResourceSet waits (line 186)
    FAIL: 6 wait-order fact(s) false in a checked-out drift-sample.yml (tickets 81, 107): the sampler would ask before the answer could exist and read the silence as a yes

GREEN — the same check against the three patched checkouts:

      ok   driftwood: kyverno wait@174 flux-operator wait@175 composed apply@176 ResourceSet waits@196 composed names derived@216 Kustomization waits@234 five-fact sample@239
      ok   tuppence: kyverno wait@177 flux-operator wait@178 composed apply@179 ResourceSet waits@199 composed names derived@219 Kustomization waits@237 five-fact sample@242
      ok   ludlow: kyverno wait@177 flux-operator wait@178 composed apply@179 ResourceSet waits@199 composed names derived@219 Kustomization waits@237 five-fact sample@242
    PASS: driftwood, tuppence and ludlow each wait for the webhooks before applying the composed set, then wait for the ResourceSet and for the Kustomizations it names before enumerating anything (round 4 order)

**4. The selfcheck, with round 3 planted verbatim.** The fixture lines `K`, `F`, `A`, `Z` and `S`
are copied from round 3 as it shipped, and `write "$t/round3" "$C" "$K" "$F" "$A" "$Z" "$R" "$S"`
is the order that has been on all three adopters' `main` since 2026-09-04. The selfcheck requires
it to FAIL:

    PASS: selfcheck: round 4's order passes; round 3's order, round 2's order, a derivation below the bare enumeration, a duplicated wait and a missing wait fail; an absent clone skips

The `late` fixture is the near-miss this check exists to catch as much as round 3 is: the
derivation added but placed BELOW the bare enumeration, which would let the enumeration keep
deciding the moment of sampling. It fails.

**5. The coupling, measured rather than predicted.** The ticket's Notes said the two sides go red
together. They do. The OLD check against the NEW workflows:

      FAIL driftwood: ResourceSet waits appears 2 times (lines 196 216); round 2's bug was a duplicate
      FAIL tuppence: ResourceSet waits appears 2 times (lines 199 219); round 2's bug was a duplicate
      FAIL ludlow: ResourceSet waits appears 2 times (lines 199 219); round 2's bug was a duplicate

(the old check's `ResourceSet waits` pattern is not anchored to `-o name`, so it also matches the
new `-o json` derivation and reads it as round 2's duplicate bug).

**Corrected 2026-09-10 (review F5). "There is no merge order that avoids a red window" is false
about the RECORDED red, and the correction changes the instruction.** The logical state does have
a window — between the two merges one side grades the other's old shape — but nothing records it
unless a hub `truth` run fires inside that window, and `truth.yml`'s `on:` block decides that:

    push:
      paths: ['talk/verify-all.sh', 'talk/verify-exclusions.txt', 'talk/verify-manifest.txt',
              'talk/truth_manifest.py', 'talk/fall_check.py', 'talk/verify-falls.txt',
              'clone-estate.sh', 'verify/**', '.github/workflows/truth.yml']

An adopter merge is a push to an ADOPTER repository. It fires no hub run at all. So:

- **Adopters first, then the hub, before the next scheduled hub run (05:47 UTC): zero recorded
  reds.** The only hub run that fires is the one the hub merge itself triggers via `verify/**`,
  and by then both sides are round 4 and the row is green.
- **Hub first is strictly worse than the original claim.** The hub merge fires a run immediately;
  that run grades round-4 markers against round-3 adopters and goes red, and because
  `verify/a-fall-blocks` makes a fall a blocking event, the run's own conclusion fails AND the
  fall owes a `run=N | reason` line in `talk/verify-falls.txt` — which is itself on the push-path
  list above, so committing the reason fires another run. A permanent accepted-fall entry in the
  citable record, for a ten-minute ordering choice.

**So: merge driftwood, tuppence and ludlow first, then the hub, in the same window and ahead of
05:47 UTC**, and run `verify-sampler-wait-order.sh` on a throwaway merge before either side lands.
This is the eighth instance of the derive-what-you-assert shape and it is recorded as such.

**6. The step must not be able to fail the job, and nearly could.** The default shell for a
GitHub Actions `run:` step is `bash -e {0}`, and the step's own `set -uo pipefail` does not undo
`-e` — so the header's "Deliberately NOT `set -e`" is a description of intent, not of the shell
the step runs in. Under `-e` an assignment from a failing pipeline aborts the step:

    $ cat t2.sh
    set -uo pipefail
    c="$(false | cat 2>/dev/null)"
    echo "survived assignment, c='${c}'"
    $ bash -e t2.sh; echo "exit=$?"
    exit=1

    $ cat t3.sh
    set -uo pipefail
    c="$(false | cat 2>/dev/null)" || c=""
    echo "survived with guard, c='${c}'"
    $ bash -e t3.sh; echo "exit=$?"
    survived with guard, c=''
    exit=0

So the inventory read carries `|| composed=""`. Measured against a fake `kubectl` whose
`-o json` call fails on every one of the thirty attempts, under `bash -e`:

    resourceset.fluxcd.controlplane.io/composed-set condition met
    wait-order: 60s after the ResourceSets went Ready no ResourceSet inventory names a Kustomization; nothing composed was waited for and the sample below records what that leaves
    kustomization.kustomize.toolkit.fluxcd.io/composed-v2-0-0 condition met
    ...

The step survives, says what it could not do, and the enumeration below still catches the
composed Kustomizations. A kubectl that cannot answer for a moment leaves a fact observed false,
never a failed job. The existing lines in this step survive `-e` only because every one of them
ends in `|| true`; that is luck rather than design, and it is recorded below as something this
ticket found and did not fix.

### What is pushed, and where

| repo | branch | commit | PR |
|------|--------|--------|----|
| policy-as-versioned-driftwood/driftwood | `ticket-107-the-sampler-waits-for-what-exists` | `53b0a48` | [#35](https://github.com/policy-as-versioned-driftwood/driftwood/pull/35) |
| policy-as-versioned-tuppence/tuppence | `ticket-107-the-sampler-waits-for-what-exists` | `3b49a5a` | [#29](https://github.com/policy-as-versioned-tuppence/tuppence/pull/29) |
| policy-as-versioned-ludlow/ludlow | `ticket-107-the-sampler-waits-for-what-exists` | `129d550` | [#26](https://github.com/policy-as-versioned-ludlow/ludlow/pull/26) |

One file each, `.github/workflows/drift-sample.yml`, 77 insertions and 5 deletions, identical
diff on all three (56/5 before the review round below). All three pull requests are green on the adopters' own CI (`compose-check`
and `shift-left` pass on each). Nothing is merged.

The hub side is branch `ticket-107-the-sampler-waits-for-what-exists`, **rebased onto
`origin/main` and never merged into it**, pull request
[#73](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/pull/73). No sha is
quoted for it, deliberately: the branch head is whatever the newest commit in this file makes it,
and a sha written here is stale the moment it is written (see *The self-reference, stated rather
than chased*, below). Because the branch is rebased and not merged, the throwaway merge onto
`origin/main` is a fast-forward and its tree is the branch's tree — so any battery run on the
branch IS the battery run on the merge, at whatever head it was taken.

### The line of Done that is outstanding, and what closes it

Done has three clauses. Two are met and one is not:

- **met** — `verify-sampler-wait-order.sh` grades the new order, with a selfcheck in which round
  3's order fails. (The "on a recorded hub run" half of that clause needs the hub PR merged and a
  recorded clock run; a branch run records nothing and its TRUTH line is quotable from the Actions
  log only, never citable — ticket 100.)
- **met, pending the merge** — driftwood's fact 5 no longer depends on `kustomizations/driftwood`
  timing out: the composed waits are by name and sort above driftwood's own. This is a property of
  the order, provable by reading it and by the harness above; the estate proves it when the run
  happens.
- **NOT MET, and it cannot be met today** — "tuppence's and ludlow's newest scheduled
  `drift/samples.jsonl` line records facts 4 and 5 true for the composed source, on a run whose
  Actions log shows the three composed Kustomizations `condition met` before the five-fact sample
  step". Nothing on the adopters' `main` has changed yet; the branches are pushed and the PRs are
  open and unmerged. What closes it: the three PRs merge, and then the NEXT SCHEDULED
  `drift-sample` run on tuppence (08:22Z) and ludlow (09:16Z) appends a line. An agent then reads
  the run's log for the three `condition met` lines and the appended sample for facts 4 and 5, and
  records both here.

**On a dispatched run.** `drift-sample.yml` carries `workflow_dispatch: {}`, so a dispatch is
possible and would be a measurement, not a fabrication. It is NOT offered as the proof, for two
reasons that are this estate's own and not a preference. First, ticket 81's *Waits on the owner*
item 4 states the rule for this exact fix in this exact file: "The proof is the next **scheduled**
`drift-sample` run on each adopter ... not a `workflow_dispatch`." Second, a dispatched run's
sample would be an observation of a workflow that is not on `main`, on a branch, which is not the
served record: the served record is each adopter's `drift/samples.jsonl` at its `origin/main`,
appended by the adopter's own scheduled lane, and the observation cage would in any case refuse a
lane commit from a branch. A dispatch after the merge would sample the right code but would still
not be the scheduled observation the Done line names, and citing it as one would be the
substitution this ticket exists to refuse. **So the wait is left open.** No sample line was
written, edited or invented by this build.

### Decisions (ADR-0025), all delegated

- **The names are derived from the ResourceSet's own status inventory, not re-spelled from the
  version array** — delegated. Two copies of the slugify rule drift; one copy, read off the object
  that applied them, cannot. It also makes the wait assert the same thing fact 5 asserts, from the
  same ids.
- **The general enumeration stays, and moves below the derivation** — delegated. It is what waits
  for the adopter's own Kustomization, which fact 3 and the sample's `revision` read. Deleting it
  would trade one hole for another; moving it below means no enumeration in this file runs before
  its answers can exist.
- **`-o json` into `python3`, not `-o jsonpath`** — delegated. A ResourceSet with no status yet has
  no `.status.inventory` at all, and what `jsonpath` does with a missing key is a kubectl flag's
  default (`--allow-missing-template-keys`) rather than something this file states. The estate's
  rule is python stdlib plus pyyaml; this is stdlib `json` and the same `python3 -c` shape four
  other workflows in the estate already use.
- **The hub check gains a seventh marker rather than only swapping two** — delegated. Grading the
  swap alone would grade "the enumeration happens later", which is a better bet and not a
  different question. The seventh marker grades that the workflow derives the names. The `late`
  selfcheck fixture makes that distinction load-bearing.
- **And an eighth rule: the enumeration line must carry `${composed}`** — delegated, added
  2026-09-10 (review F1). A seventh marker alone grades that the names are *computed*, not that
  they are *waited for*. Measured: deleting `${composed}` from the union loop's word list on all
  three adopters left the check green while the workflow still printed that it was waiting for
  three Kustomizations and waited for none — round 3 restored with a log line asserting the
  opposite. Rule B closes it. The cost is that the check now grades a shell variable NAME, which
  is a coupling; it is the same kind of coupling as grading specific `kubectl` invocations, which
  this check already does, and it buys the one plant that produced a false green.
- **The check's `ResourceSet waits` pattern is narrowed to `-o name`** — delegated. Without it the
  derivation line matches the same marker and reads as round 2's duplicate bug, which is what the
  old check does against the new workflows (measured above). Narrowing is the smallest change that
  keeps "a duplicate is a FAIL" honest. **It has a price, named** (review F8): duplicate detection
  now only covers the two output formats the markers name. A third ResourceSet read planted as
  `-o yaml` beside them **passes the new check and fails the old one** (measured 2026-09-10). The
  old check would have caught a stray third read; this one will not.
- **One commit, three repositories, identical diff, pushed but not merged** — delegated. The task
  brief forbids merging; the three PRs carry the same body and name the merge order the coupling
  requires.

### Not this ticket's, found while measuring

- **WITHDRAWN 2026-09-10 (review F6), and the opposite is the interesting fact.**
  `kustomizations/driftwood` DID reach Ready on driftwood's newest scheduled run: 34345475988,
  2026-09-09T11:27Z, `kustomization.kustomize.toolkit.fluxcd.io/driftwood condition met` at
  11:27:01.51, **0.34s** after the apply created the ResourceSet, and that run's log contains no
  `timed out waiting` line at all. The stall is gone — and with it the accident. That run's
  driftwood sample records fact 3 True, fact 4 True (all 16 live and equal) and **fact 5 FALSE**,
  the same fifteen policies, `inventory_entries` 7, verdict FAIL. **All three adopters now record
  fact 5 false on the schedule**, which this ticket's evidence, stopping at 2026-09-08, did not
  show. Round 4 is more urgent than the ticket said, not less.
- `verify-adopter-gate.sh` disagrees with itself across adopters when no platform clone is present,
  and the shape is **three scripts at two paths** (corrected 2026-09-10, review F7; the first
  version said ludlow carried no copy, which was wrong — I globbed `scripts/*.sh` only).
  driftwood `scripts/verify-adopter-gate.sh` exits 3, `SKIP: no clone of platform at ...`; ludlow
  `verify-adopter-gate.sh`, at the repository ROOT, exits 3 with the same SKIP sentence; tuppence
  `scripts/verify-adopter-gate.sh` exits 1, `FAIL: no platform clone at ...`. Two agree, tuppence
  is the sole outlier, and the same question is asked from two different paths. Unchanged by this
  build (measured identical before and after) and not charted here.
- **A LIVE COVERAGE HOLE, not a footnote** (corrected 2026-09-10, review F9; the first version of
  this entry said every line in the step ends in `|| true` and called it luck — that is false).
  The `install the engine` step declares no `shell:`, so it runs under the default `bash -e {0}`,
  and its own `set -uo pipefail` does not clear `-e`. **Six commands in that step carry no
  `|| true` at all**: the two `kubectl apply --server-side` installs of kyverno and flux-operator,
  `flux install`, `kubectl apply -f gitops/flux-system/`, `kubectl apply -f
  gitops/platform/platform-pin.yaml`, and `kubectl apply -k gitops/composed/`. Under `-e` any one
  of them failing kills the job and **writes no sample at all** — which is the exact outcome the
  step's own header says it exists to prevent ("a job that failed instead would leave a coverage
  hole and report nothing"). Round 4's one new assignment is guarded explicitly and measured; the
  other six are a hole in the observation lane on all three adopters and want a ticket of their
  own, not a line in this one.
- In a bare clone with no `.work/` and no twin package above it, all three adopters'
  `verify-reconcile.sh` exit 3 on `git could not verify the signature on that lane commit
  (%G? = 'N')`. That is the clone's shape, not the estate's, but it means an adopter's own lane
  check cannot be run to a verdict outside the hub's estate clone.

### The battery, and what moved

Local, on this laptop, `talk/verify-all.sh` on the branch at tree `f3fa319` — `eba17ee`'s tree,
which is also the throwaway merge's tree at that head, since the branch is rebased onto
`origin/main` `c60dee5` — and on a pristine `origin/main` checkout, run back to back against the
same estate clone. The review round below changes
`verify/sampler-wait-order/verify-sampler-wait-order.sh`, so these figures describe the tree named
and not the head a reader has:

    branch  TRUTH ... hub=c50207b ... pass=69 [observed=20 self=38 simulated=2 meta=9] fail=32 skip=15 [never=4 waits=11] excluded=8 total=124 ceiling=105
    main    TRUTH ... hub=c60dee5 ... pass=70 [observed=21 self=38 simulated=2 meta=9] fail=31 skip=15 [never=4 waits=11] excluded=8 total=124 ceiling=105

Five rows differ. One is this change and is intended:

    verify/sampler-wait-order/verify-sampler-wait-order.sh   PASS (main)  ->  FAIL (branch)

The other four are the laptop, not the diff, and each was re-measured back to back on both trees
afterwards to say so:

- `.estate-clone/platform/distribution/verify-declared-versions-admit.sh` and
  `.estate-clone/platform/graded/verify-graded.sh`: exit 0 on both trees on re-measurement. The
  battery rows were taken forty minutes apart against a live kind cluster.
- `.estate-clone/platform/compose/verify-composition.sh`: the difference is this build's own test
  rig. `composition.py --selfcheck` asserts on the estate-clone path and the baseline worktree's
  `.estate-clone` was a SYMLINK to the branch worktree's, which the assert rejects
  (`AssertionError: .../wt-107-main/.estate-clone`). With a real directory it reads SKIP on both
  trees, on the pinned-parent leg ticket 106 owns.
- `verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh`: exit 3 then exit 1 across two runs
  minutes apart on the same tree; it reconciles against the shared `kind-driftwood` cluster,
  which the run before it had just mutated.

`talk/verify-all.sh --selfcheck` PASSES on the branch. `verify/cited-truth`, `verify/every-green`
and `verify/truth-line` each PASS on the branch and on the throwaway merge. `python -m mypy twin
tests conftest.py --ignore-missing-imports --warn-unused-ignores` (the command twin.yml runs):
`Success: no issues found in 186 source files`. `pytest -q` on the branch and on `origin/main`
produce the IDENTICAL failure set — 8 failed, 2313 passed, 10 errors, the same named tests on both
— so nothing here moved a test.

The manifest needs no change: this check's skip column is `-`, and `truth_manifest.py judge`
refuses both its real could-not-look line and an invented one:

    $ .venv/bin/python talk/truth_manifest.py judge talk/verify-manifest.txt verify/sampler-wait-order/verify-sampler-wait-order.sh "SKIP: /x/.estate-clone/driftwood is not here (run clone-estate.sh)"
    undeclared: talk/verify-manifest.txt declares no skip for verify/sampler-wait-order/verify-sampler-wait-order.sh (skip column is `-`) ...
    $ .venv/bin/python talk/truth_manifest.py judge talk/verify-manifest.txt verify/sampler-wait-order/verify-sampler-wait-order.sh "SKIP: the moon was in the wrong phase"
    undeclared: ... (skip column is `-`) ...

`truth_manifest.py check talk/verify-manifest.txt` exits 0.

### The selfcheck bites a grader that regresses

A mutant of this check with round 3's `NAMES` array and no derivation marker — the check exactly
as it stood on `origin/main` — run against the NEW selfcheck:

    selfcheck: the round-4 order failed
    selfcheck: round 3's order passed
    FAIL: selfcheck: the grader does not grade

So a future edit that quietly puts the old order back cannot pass its own selfcheck.

### The gate run of the final head

Actions runs **34406905104** (push) and **34406929631** (dispatch), branch
`ticket-107-the-sampler-waits-for-what-exists`, head `b63ee92`, finished 2026-09-09T21:47Z and
21:52Z, both conclusion failure, `run=218` and `run=219`, identical figures and byte-identical
failing sets. An earlier run, 34403542737 at head `464dab5`, measured the same thing; `464dab5` is
an unreachable head and is named only because the paragraph below was first written under it.

**The self-reference, stated rather than chased** (review F4). No section of this file can name a
gate run of the commit that carries it: writing the sentence makes a new head, and the run for that
head does not exist until after the sentence is written. Naming one anyway is how the citation
above came to sit at `464dab5`, a head no longer reachable. So this paragraph does not promise a
run id; it states the limit, and what a reader can check instead.

What is checkable is whether the GRADED ARTEFACT moved between the head a run measured and the head
a reader has. `verify/sampler-wait-order/verify-sampler-wait-order.sh` was byte-identical at
`eba17ee`, `464dab5` and `b63ee92`, so runs 218 and 219 measured the check as those three heads
carry it. The review round below CHANGES that file, so those runs do not speak for any head after
it, and a reader wanting a gate verdict on the check as it now stands should read the newest
`truth` run on this branch in the Actions log rather than a sha quoted here. The local battery
figures quoted further down were measured on tree `f3fa319`, which is `eba17ee`'s tree, not the
merge tree of any later head.

**These lines are not citable and are not in `talk/truth.log`**: a branch run records nothing (ticket 100), and the job says so itself —
"the line above is NOT being written to talk/truth.log: this run is on
ticket-107-the-sampler-waits-for-what-exists, not main, and only main's talk/truth.log is
citable". It is quoted here from the Actions log only.

What it measured, against the newest recorded run of `main` (hub `c50207b`, 2026-09-09T19:20Z),
which is the honest comparison because both graded the same eight unit checkouts:

- the recorded main run: 78 passing, 8 failing, 30 could-not-look, 8 excluded of 124.
- this branch run: 77 passing, 9 failing, 30 could-not-look, 8 excluded of 124.

The two failing sets differ by exactly one row, and it is this ticket's:

    + verify/sampler-wait-order/verify-sampler-wait-order.sh   FAIL (exit 1)

with the same eight fails on both — `.estate-clone/driftwood/twin/verify-twin-sweep-moved.sh`,
`.estate-clone/platform/distribution/verify-retirement.sh`, `verify/branch-refs`,
`verify/deny-is-not-a-rung`, `verify/derived-status`, `verify/handbook`, `verify/schedules` and
`verify/unreviewed-major`. So the gate says what this build claims it says: one new red, it is the
one the coupling predicts, and it turns green when the three adopter pull requests merge.

## Review round, 2026-09-10 — nine findings, all verified first-hand before being written down

An adversarial review request-changed **on the record, not the code**: it would merge the adopter
workflow diff unchanged, and confirmed by object identity that no sample line was written, edited
or invented (the `drift/samples.jsonl` blob sha is identical between `main` and the branch on all
three adopters, and the hub's `talk/truth.log`, `talk/verify-falls.txt` and grade table are
byte-identical too). Every finding below was re-measured here before it was believed; two of the
nine came back sharper than the review stated them, and both are recorded as measured.

**Corrections written into the sections above**, each dated and each naming what it replaces, so
the record does not end up saying both things at once:

| # | what was wrong | where it is corrected |
|---|----------------|------------------------|
| F5 | "There is no merge order that avoids a red window" — false about the RECORDED red | *The coupling, measured* |
| F2 | sorting removes driftwood's dependence on a timeout — not load-bearing, and not generally true | *Why driftwood's accident is removed* |
| F3 | "the same ids `drift/five-facts.py` reads for fact 5" — wrong in both directions | *The decision*, and the workflow comment |
| F4 | a run citation at an unreachable head, and a merge tree three heads stale | *The gate run of the final head* |
| F6 | "`kustomizations/driftwood` still does not reach Ready" — it does, and fact 5 went false anyway | *Not this ticket's* |
| F7 | "ludlow carries no copy of the script at all" — it does, at the repository root | *Not this ticket's* |
| F8 | narrowing marker 4 to `-o name` was recorded without its price | *Decisions* |
| F9 | "every existing line happens to end in `|| true`" — six do not | *Not this ticket's* |

**F1 got code, and it is the one that produced a false green.** The check could be satisfied by a
workflow that computes the derived names and never waits for them. Measured on all three adopters
by deleting `${composed}` from the union loop's word list and leaving the derivation in place:

    RED  (before rule B)   exit=0, PASS — while the workflow still printed
                           "the ResourceSet names these Kustomizations; each is waited for by
                           name: composed-v2-0-0 composed-v2-0-1 composed-v3-0-0" and waited for
                           none of them. Round 3 restored, with a log line asserting the opposite.

    GREEN (with rule B)    FAIL driftwood: the Kustomization waits (line 234) do not include
                           ${composed}: the names are derived and then never waited for, which is
                           round 3 with a log line that says otherwise
                           (and the same for tuppence and ludlow)

Rule B is six lines: the line matching marker 6 must also carry `${composed}`. Its selfcheck
fixture `unused` is round 4's exact ORDER with the round-3 enumeration line, so it fails on rule B
alone and on nothing else. Three further plants were measured and are **not** closed, and the
check's header now names them instead of claiming more than a grep can do: `seq 1 30` cut to
`seq 1 1`; `--timeout=180s` set to `--timeout=0s`; and a marker surviving inside a TRAILING
comment on a code line, because the comment filter is anchored at line start. So are two the
review named that this check structurally cannot see: a derivation hoisted into a function invoked
below the enumeration, and `if: false` on the step. The header's old sentence — that marker 5
"requires the workflow to derive the names … so found-nothing is a list it can see is empty" — was
stronger than the grep behind it, and has been replaced by an explicit *what this grades / what it
does not* pair.

**F3 got code too, because the defect is this ticket's own class.** The derivation dropped the
namespace while the wait hardcodes `-n flux-system`. Measured against a fake ResourceSet naming
`tenant-a/composed-v3-0-0`:

    RED    wait-order: the ResourceSet names these Kustomizations; each is waited for by name:
             ... composed-v2-0-0 ... composed-v2-0-1 ... composed-v3-0-0
           kustomization.../composed-v2-0-0 condition met
           kustomization.../composed-v2-0-1 condition met
           error: no matching resources found          <- swallowed by `|| true`, in milliseconds

    GREEN  wait-order: REFUSING tenant-a/composed-v3-0-0 -- a ResourceSet names a Kustomization
             outside flux-system and the wait below is -n flux-system, so it cannot be waited for here
           wait-order: about to wait, by name, for the Kustomizations the ResourceSet names in
             flux-system; each wait below prints its own verdict: ... composed-v2-0-0 ... composed-v2-0-1
           kustomization.../composed-v2-0-0 condition met
           kustomization.../composed-v2-0-1 condition met

A claimed wait that never happened, in the log this ticket's Done line reads its evidence from, is
the same failure this ticket exists to end — one level down. The announcement is now a statement of
intent and each `kubectl wait` prints its own verdict. Unreachable while everything is in
`flux-system`; refused anyway.

**What did not change.** The `-e` guard measurement re-ran identically after both code changes: 62
seconds and exit 0 with the guard, against a fake whose `-o json` call fails on all thirty
attempts. The healthy path is unchanged: three `composed-v* condition met` lines, all above the
adopter's own, all above the sample step.
