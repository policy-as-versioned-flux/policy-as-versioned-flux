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
