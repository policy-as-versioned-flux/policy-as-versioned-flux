# 98 — A refusal by another name is graded by nothing

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

The estate has a doctrine: nothing is denied, and a workload that does not fit its cage runs on a
tighter rung. Ticket 89 built a register that grades every Deny-shaped rule. Nothing grades the
other way a workload can be stopped: a MUTATION that makes a pod inadmissible. It has happened
twice, both times found by RUNNING a policy rather than reading one, and no static check in this
repository can see it.

Build a check that catches a mutation whose product the API server would reject. Done = the check
is in the gate, it goes red on each of the two instances below replayed as fixtures, and its
manifest row declares what it cannot see.

## Notes

Charted 2026-09-05 from ticket 89's round-2 build. Ticket 89 records the shape in
`deny_register.BLIND_SPOTS`; this ticket is the one that grades it.

**The two instances, both real.**

1. **2026-08-28, ticket 26.** The priority trio and the duplicate sidecar. A cage mutation produced
   a pod the API server would not accept.
2. **2026-09-05, ticket 89 round 2.** The new orphan cage named the PriorityClass `cage-isolated`.
   Every PriorityClass the estate ships is version-suffixed — `distribution/policies/v4.0.0/
   priorityclasses.yaml` declares `cage-baseline-4-0-0`, `cage-restricted-4-0-0`,
   `cage-quarantine-4-0-0` and `cage-isolated-4-0-0`. The plain name exists on no cluster, and the
   Priority admission plugin rejects a pod naming a PriorityClass that does not exist. So the cage
   built to REPLACE a refusal would have made every pod it caged inadmissible. The builder found it
   by running the beat, not by reading the body, and fixed it before the branch was reviewed.

**Why a static check is hard, and what to aim at anyway.** Whether the API server accepts a mutated
object depends on the cluster: which PriorityClasses exist, which admission plugins are on, whether
a field is immutable on UPDATE. A check that decided that offline would be guessing. Three things
are checkable without a cluster and would have caught both instances:

* **Every name a mutation writes into a reference field must be a name the same release ships.**
  `priorityClassName` is the one that bit. A mutation naming `cage-isolated` while the release
  declares `cage-isolated-4-0-0` is a defect the renderer can refuse at render time.
* **A mutation on UPDATE must be byte-identical on a already-mutated object.** `cage-tier`'s own
  header already argues this for its sidecar; nothing asserts it. An UPDATE mutation that adds a
  container to an immutable list is the second instance's shape.
* **A field a mutation writes must be one the resource allows to change on that operation.**

The live half belongs where a cluster is: `graded/verify-graded.sh`'s cluster tail, which has never
had a cluster on a citable run (review finding P2-6). State that rather than simulating it.

**Do not simulate an API server.** A check that plants a fake rejection and prints a PASS would be
the exact defect this estate keeps finding. What cannot be looked at offline is named and exits 3.

## Comments

**2026-09-05.** Both instances share a property worth stating: the mutation was correct as a
document and wrong as an effect. Reading it proved nothing. Every check in this estate that has
caught one did so by executing the policy against a resource, which is why `verify-orphan-guard.sh`
and `verify-graded.sh` are the places this belongs rather than a new scanner.

## Appended 2026-09-05 (ticket 89 rounds 3 and 4) — two more instances, and one that is LIVE

3. **2026-09-05, ticket 89 round 2.** The `UPDATE` arm on the bottom-rung cages, gated on
   `posture.acme.io/caged: "true"` in the belief that the marker meant "caged by this policy".
   `cage-tier` writes it for its whole population at every rung, so the cage matched a pod caged
   at `baseline` and applied the full body to a RUNNING pod: a `waf-sidecar` appended to an
   immutable container list, `priorityClassName` and `priority` rewritten. It would have refused
   the currency controller's `recage_patch()` — the only mechanism a pod on a retired version
   has. Fixed by splitting a labels-only hold onto `UPDATE`.

4. **LIVE, decided not fixed.** A pod the bottom-rung cage admitted can be labelled with a served
   policy version, at which point `cage-tier` takes it over and writes its Namespace's tier.
   Measured: `tier: isolated -> baseline`, `priorityClassName: cage-isolated ->
   cage-baseline-4-0-0`, `priority: -10000 -> -10`. Both spec fields are immutable on a running
   pod, so the API server refuses the edit. Ticket 89 decided this is the correct outcome —
   letting it through would be a workload moving itself off the bottom rung by asserting a label,
   the self-service exemption principle 1 bans — and recorded in `CONTEXT.md` that the
   remediation is a **recreate**, not a label edit.

   **This is the one to build the check against.** The first three are gone from the code and
   have to be replayed as fixtures; this one is in the estate right now, reachable with two
   `kubectl label` calls, and no check in the repository can see it. A check that goes red on it
   would have caught all three of the others.

**What the four have in common** (ticket 89's round-4 answer, in the reviewer's words): each
reasons from a PROXY for the served thing instead of the served thing — an authoring artefact
that is never applied; a label whose name implies a provenance it does not carry; a file's
existence standing in for a cage's service; and the register's prose standing in for the code.
Each proxy is cheap to read and each is checkable by something already in the repository, so the
reasoning never has to leave the repository. The rule that would have caught all four: **every
safety claim must name the SERVED artefact and the OPERATION that reaches it, and be measured
against both.** The estate cannot currently do the second half — `kyverno apply` has no `UPDATE`
mode, and no cluster has run these policies on a citable run — so three of the four were only
catchable by reading, and the fourth only by running.

## Answer

Built 2026-09-06. A refusal by another name is graded by
`verify/refusal-by-another-name/verify-refusal-by-another-name.sh`, discovered by
`talk/verify-all.sh` (110 scripts on this branch, measured by `verify-truth-line.sh` and never
typed into a check), with a row in `talk/verify-manifest.txt` as `estate-observation | waits:`
declaring both of its could-not-looks. The live half is `graded/verify-graded.sh` step 8b on the
platform branch, and it has now observed the refusal on a real API server.

**Four legs, one per way the estate has actually produced this failure.** Each is red-first
against the estate's OWN bodies, replayed on every run by `replays.py` — a grader that has never
gone red is a grader nobody has tested:

| leg | what it grades | the instance it catches |
|---|---|---|
| A | every name a mutation writes into a reference field is one the SAME RELEASE ships | 2 — `cage-isolated` where every served class is `cage-isolated-4-0-0` |
| B | an UPDATE-scoped mutation is identical applied to its own output — EXECUTED, on every rung | 1b — the `waf-sidecar` appended twice |
| C | a field written on UPDATE is one a running pod allows to change, joined to `register.yaml` | 3 and 4 |
| D | a mutation writing `priorityClassName` writes the whole priority trio | 1a — the trio that refused every pod on every released line |

**The live one is reported, not called a defect.** `register.yaml` records the decision ticket 89
made (S3): `cage-tier` writes thirteen fields a running pod forbids, and when a pod's rung changes
under it the API server refuses the edit — correctly, because the alternative is a workload moving
itself off the bottom rung by asserting a label. The row carries the reason, the remediation
(recreate) and the leg that bounds it, and the join is graded in BOTH directions: an unrecorded
write fails, a row narrower or wider than the code fails, a row matching no served mutation fails.
Narrowing the row to one field is asserted to go red on every run, so the acceptance can never
become a blanket permission.

### What the run observed

* `verify-refusal-by-another-name.sh` PASSES in 28s on this machine: 4 mutating policies on the
  served surface of the estate clone as it stands (`platform:v4.0.0`, `platform:v5.0.0`), 15
  authoring or pruned copies named and not graded, all four replays red, leg B executing four
  UPDATE-scoped mutations against their own output on all five rungs.
* Against a clone carrying platform's current `origin/main` (ticket 89 merged), the same check
  passes with 8 served mutations, including the four machinery policies inside the ResourceSet
  template. That was measured through a throwaway root of symlinks, not by refreshing the shared
  clone, which another builder was using.
* **The refusal itself, observed live on kind-driftwood, 2026-09-06** (`graded/verify-graded.sh`
  step 8b, whole script PASS). A pod admitted and caged at `quarantine`
  (`cage-quarantine-4-0-0` / `-1000`), the Namespace's declared tier moved to `baseline`, then one
  `kubectl label` on the running pod:

  ```
  The Pod "t98-probe" is invalid: spec: Forbidden: pod updates may not change fields other than
  `spec.containers[*].image`,`spec.initContainers[*].image`,`spec.activeDeadlineSeconds`,
  `spec.tolerations` (only additions to existing tolerations),`spec.terminationGracePeriodSeconds`
  ...
  - "PriorityClassName": "cage-quarantine-4-0-0",   + "PriorityClassName": "cage-baseline-4-0-0",
  - "Priority": -1000,                              + "Priority": -10,
  ```

  No policy denied anything. Not citable: a local run, not a gate run.

### The suite, and what was actually observed of it

The full test suite ran to completion **on CI, on this branch's first commit** — the `twin`
workflow, [run 34019956456](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/actions/runs/34019956456):
`1 failed, 1908 passed in 115.37s`, the 37 new tests among them. The one failure is
`test_the_suite_is_green`, from invariant 45 `flux_coverage_floor_is_still_reachable` — the
standing red the build brief names, whose staying red is the finding. The `invariants` job on the
same branch reports `RESULT: 71 passed, 1 failed, 3 skipped`, the same one. Invariant 44
`drift_window_is_actually_being_sampled` PASSED there. Neither is this ticket's.

**The local `-n0` run did not complete inside this session and its result is therefore not
recorded.** It was started twice: the first reached 45% and was killed with its parent shell; the
second was still at 3% under machine load (a second full suite from another build was running on
the same machine). Rather than write a number nobody watched arrive, the observation cited above
is CI's. Everything else in this section is a local run I watched finish.

### Decisions

**D1 (delegated). The check grades the SERVED surface and names everything it excludes, and that
partition is the ticket.** Graded: platform's version directories for versions the array DECLARES
and has CUT (`commit` present — `verify-declared-versions-admit.sh`'s own partition), the machinery
documents inside `versions.yaml`'s ResourceSet template, an adopter's composed version tree its own
array declares, and a declared-but-uncut tail (on no cluster, but what the next tag serves).
Excluded, each named with its reason on every run: `graded/policies/` (no Kustomization applies it
— ticket 89 round 1's mistake), `vselfcheck/`, and a version directory on disk the array no longer
declares (Flux pruned it: history, not service). Fifteen copies fall in that last set today,
including all three adopters' `composed/policies/v4.0.0`, whose own arrays declare 2.0.0/2.0.1/3.0.0.

**D2 (delegated). Leg C flags a hazard and the register holds the decision; it does not decide
alone.** Whether writing an immutable field on UPDATE actually refuses depends on whether the VALUE
changes, which depends on the object at that moment and is not decidable offline. So the structural
fact — this field, this operation — is what is graded, and the estate records what it means. That is
ticket 89's register shape, and for the same reason: a decision that stops being visible stops
being a decision.

**D3 (delegated). Leg B probes UPDATE-scoped mutations only.** A CREATE-only mutation never meets
its own output, because the object it writes does not exist until it has written it.

**D4 (delegated). A missing kyverno CLI is a FAIL, not a could-not-look.** Leg B is the only leg
that has ever caught one of these, and every other beat that needs the CLI declares no skip for it
either. A runner that has lost its instrument goes red rather than shrugging.

**D5 (delegated). The machinery is its own release group, so it may not borrow a version tree's
PriorityClass.** The ResourceSet installs the machinery beside every version tree, and a version can
be retired from the array and pruned at any time. A machinery cage naming `cage-isolated-4-0-0`
would refuse every pod it caged the day 4.0.0 retired. That is why leg A groups by delivery unit
rather than by cluster, and why ticket 89's unsuffixed `cage-isolated` is correct rather than sloppy.

**D6 (delegated). A dial table indexed by a PINNED tier resolves to that rung only.** The machinery
cages share `cage-tier`'s dial table and index it with `tier` pinned to `'isolated'`. Reading all
four rungs' classes out of it would demand the machinery ship three PriorityClasses no policy of its
can ever name — a red that is WRONG, which is worse than no check. Where the index is computed
(`cage-tier`'s own ternary) every rung is read. Test first, red first.

**D7 (delegated). The live half went into `graded/verify-graded.sh`'s tail, as the ticket says, and
reaches the refusal by moving the NAMESPACE's declaration rather than adding a claim.** Ticket 89's
exact route needs its machinery on a cluster and no cluster carries it yet. The Namespace is where
the tier is declared (ADR-0022), so moving it produces the identical rung change on the identical
two immutable fields. The claim route is printed as a NOT LOOKED AT line naming what is missing,
rather than the tail going dark while the machinery is in flight.

**D8 (delegated). The API server grades the offline table.** Kubernetes' refusal message enumerates
the fields a pod update MAY change. Step 8b asserts that list is exactly the five
`refusal_scan.MUTABLE_ON_UPDATE` carries, so the central constant of the offline check is measured
against the real API server rather than believed. The day Kubernetes widens it, that step goes red
and names the field.

### The hard part: `kyverno apply` has no UPDATE mode, and it is worse than "matches nothing"

Ticket 89 recorded that the CLI matches nothing against an UPDATE-scoped policy. Measured here on
2026-09-06, it is more dangerous than that. It prints **"Mutation has been applied successfully"**,
writes `<name>-mutated.yaml`, and the file it writes is the UNMUTATED resource; the counts line
reads `pass: 0`. A beat that greps that sentence, or reads the file's existence, measures nothing
and calls it a pass — which is the defect this ticket exists to catch, sitting inside the
instrument the ticket has to use.

What the build does about it, and it is four things, not one:

1. **The limit is measured, not disclosed.** `assert_no_update_mode()` runs on every invocation:
   an UPDATE-only policy, a resource it would match, and the requirement that the CLI apply
   nothing. If a future CLI grows an UPDATE mode, that probe FAILS with "the disclosed limit has
   LIFTED — rewrite this file". A disclosed limit is an assertion and goes stale like any other;
   this one cannot.
2. **Operation scoping is asserted STRUCTURALLY**, from `matchConstraints.resourceRules[].operations`
   in the served manifest (leg C), never from a run.
3. **The body is measured on a throwaway copy** whose operations are rewritten to CREATE, with
   `namespaceSelector` (kyverno/kyverno#13605), the `oldObject` gate and any template-ranged
   matchCondition removed — each difference from the served body printed beside the result.
4. **Nothing may pass because nothing applied.** `applied` is the PASS COUNT, never a file's
   existence; a policy no candidate pod reaches on any rung is a FAIL naming it; and the selfcheck
   plants a policy that matches nothing and requires the leg to refuse it.

One more thing the run found, and it changed the check: probing without a values file lands every
pod on whatever the body's fail-closed else-branch happens to be. The v4.0.0 body lands on
`baseline`, which carries no WAF sidecar — and the 2026-08-28 duplicate-sidecar defect replayed
GREEN. A leg that cannot reach the rung the defect lived on is not a leg. Leg B now supplies the
Namespace through a CLI values file and walks all four rungs plus the unlabelled case, and the
replay comes back with the engine's own sentence:
`.spec.containers: duplicate entries for key [name="waf-sidecar"]`.

### Red first, exact output

| what | red | green |
|---|---|---|
| the seam's 37 tests | `FileNotFoundError: .../refusal_scan.py` (collection error, before the module existed) | `37 passed in 0.06s` |
| the pinned-tier dial lookup | `assert frozenset({'cage-baseline-4-0-0','cage-isolated-4-0-0'}) == frozenset({'cage-isolated-4-0-0'})` | passes; the machinery no longer needs three classes it cannot name |
| replay 1b, the sidecar | `NOT CAUGHT -- leg B grades nothing` (probing without the values file, on `baseline`) | `error: failed to evaluate policy: ... .spec.containers: duplicate entries for key [name="waf-sidecar"]` |
| replay 3, the full body on UPDATE | — | `13 unrecorded writes on a running pod` |
| the register, narrowed to one field | — | `register row cage-tier* declares field set [...] and the code writes [...] -- the row no longer describes the code` |

### What this cannot see

`refusal_scan.BLIND_SPOTS`, six entries, every one DATED and printed on every run, and held
non-empty and dated by a test. The first is the one that matters: whether the API SERVER accepts
the mutated object is a cluster fact, and the live half has never had a cluster on a citable run
(P2-6). The others: a mutation whose written VALUE differs from what the object already carries;
the 2022 ClusterPolicy `rules[].mutate` and any other engine's mutation (none ships today);
resources other than the pod, which are counted and named as untabulated rather than graded; a
JSONPatch path computed from something other than concatenated literals; and the one worth a
reviewer's attention — every tree is read at the clone's HEAD, while an ADOPTER serves the tree at
the tag its own composed GitRepository pins, so where those differ the bytes graded are not the
bytes served. That is this ticket's own subject one level out. It bites nothing today (no adopter
array declares a version whose directory exists at HEAD, and every such directory is named in the
excluded list on every run) and closing it means reading each path out of `git show <tag>:<path>`.

Map line: `- [98 — A refusal by another name is graded by nothing](issues/98-a-refusal-by-another-name-is-graded-by-nothing.md) — the other way a workload is stopped is now graded: verify/refusal-by-another-name/ reads every mutation the estate SERVES and grades four things offline — a name written into a reference field is one the SAME RELEASE ships (the unsuffixed cage-isolated), the priority trio is whole (the trio that refused every pod on every released line), every write on UPDATE that a running pod forbids is on register.yaml with a reason, a remediation and the leg that bounds it, and every UPDATE-scoped mutation is EXECUTED against its own output on every rung and must come back identical (the waf-sidecar appended twice). All four instances the estate produced are replayed against its OWN bodies on every run and every one goes red; the fourth is LIVE and decided correct, so it is reported with its remediation (recreate) rather than called a defect, and the row is graded in both directions so it cannot outlive the code — narrowing it by one field is asserted to go red. The served partition is the ticket's own rule: graded are the declared-and-cut version trees, the machinery inside the ResourceSet template and the uncut tail; excluded and NAMED are graded/policies/ (no Kustomization applies it), vselfcheck/ and the fifteen version directories on disk that no array declares. kyverno apply has no UPDATE mode and is worse than that — it prints "Mutation has been applied successfully", writes an UNMUTATED file and counts pass:0 — so the limit is MEASURED on every run rather than disclosed (it goes red the day the CLI grows one), scoping is asserted structurally, the body runs on a throwaway copy whose every difference is printed, and applied means the pass count, so no step can pass because nothing applied. Probing without a values file was that same bug in this build: it landed every pod on baseline, where no sidecar exists, and replayed the 2026-08-28 defect GREEN. The live half is graded/verify-graded.sh step 8b, which OBSERVED the refusal on kind-driftwood on 2026-09-06 — a quarantine-caged pod, its Namespace moved to baseline, and one kubectl label refused with PriorityClassName cage-quarantine-4-0-0 -> cage-baseline-4-0-0 and Priority -1000 -> -10 — and which asserts the API server's own list of mutable-on-update fields is exactly the five the offline table carries, so the check's central constant is graded by the API server rather than believed. deny_register.BLIND_SPOTS now points at all of it.`

## Waits on the owner

Nothing. Both branches are pushed and both pull requests are open; the integrator merges.

## Not done

* **The claim route of instance 4 is not observed live.** Step 8b observes the same rung change by
  moving the Namespace's declaration; ticket 89's exact route (label a bottom-rung pod with a served
  version) needs `governed-namespace-cage` on a cluster, and kind-driftwood still carries the
  pre-ticket-89 ValidatingPolicy. The step prints that as a NOT LOOKED AT line naming what is
  missing rather than skipping.
* **`graded/verify-graded.sh`'s live tail still asserts the two guards REFUSE**, as
  ValidatingPolicies, which ticket 89 replaced with mutations. It passes today only because
  kind-driftwood carries the old objects; the day platform's machinery reaches a cluster that tail
  goes red for a reason that is ticket 89's, not this ticket's. Found while adding step 8b, not
  fixed here: it is a rewrite of somebody else's beat, and doing it blind — with no cluster carrying
  the new machinery to measure against — is exactly the reasoning-from-a-proxy this ticket is about.
* **Only the pod's mutability is tabulated.** A mutation on any other resource is counted and named
  as untabulated. None ships today.
* **The adopters' composed trees are graded but empty of served content**: all three declare
  2.0.0/2.0.1/3.0.0 in their composed-set arrays and carry only `composed/policies/v4.0.0` on disk,
  so every adopter copy lands in the excluded set. That mismatch is real and is not this ticket's;
  the check names it on every run rather than passing over it.
* No `kyverno` CLI in the estate can evaluate an UPDATE, so nothing offline proves that an
  UPDATE-scoped policy MATCHES what its manifest says it matches. That is asserted structurally and
  said so, in the script, in the manifest row and here.
