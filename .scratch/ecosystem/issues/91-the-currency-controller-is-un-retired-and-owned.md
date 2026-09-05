# 91 — The currency controller is un-retired and owned

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Ticket 13 item 2 retired the currency controller because "ticket 07's fx feed replaces it". The controller re-cages a running pod after its admitted version is retired; the fx feed is money. Ticket 75 Q13 withdrew the retirement: the controller is the estate's only post-admission re-caging mechanism.

1. Amend ticket 13's Answer item 2 with a dated comment that withdraws the retirement of the currency controller and cites ticket 75 Q13. The rest of item 2 stands.
2. Give the controller an owner: it becomes a versioned member of the platform's published `implementations` package, numbered by the platform's tag, with a `party.yaml` line naming platform as its publisher. Its CronJob keeps its schedule under ADR-0024's clock rules and may only re-cage, never loosen, consistent with tighten-only.
3. Define what it does in one sentence in CONTEXT.md (rewrite line 246's aside into a term), and make `verify-currency.sh` or its successor grade that sentence: a pod admitted under a version that is later retired is re-caged to `isolated` on the next controller pass.
4. Ticket 80 item 6 changes direction: execute the un-retirement, not the retirement.

Done = the controller is a graded, owned, versioned member and a retired version's running pod is observed re-caged on a lane sample or an offline harness run named in the gate.

## Notes

Charted by ticket 75 (Q13). Record: REVIEW-2026-09-02.md R10, legacy/L5. The owner's answer was a bare "a"; the reason recorded is the assistant's, under Q11.

## Answer

Built 2026-09-05. All four items. Every decision below is **delegated** under ADR-0025 unless it
says otherwise; none of them is money, a date, an identity, an authorisation or a real person.

### 1. Ticket 13 item 2 is amended, dated, with the reason each clause fails

`issues/13-lift-or-retire-the-original-mechanisms.md` gains a dated comment that strikes the two
retirement clauses and leaves the rest of item 2 standing. Both clauses fail on the primary sources:
"ticket 07's fx feed replaces it" is a homonym (that currency is money, this one is version
currency; the owner's GAPS register keeps them as separate rows 2.8 and 3.18), and "it 404s" is the
substrate absence ticket 12 itself classified as "Substrate repair, not a decision" and ticket 32
scoped and never built. Two further findings are recorded there: the item's headline reason ("two
live implementations", H9-11) cannot reach a module no legacy repo contains, and item 2's own staged
rule — archive only after the truth surface grades the replacement green — was never satisfied,
because `verify-currency.sh` has SKIPped on every citable run it has ever appeared in.

### 2. The controller has an owner, a number and a schedule it may not exceed

- **`platform/party.yaml` declares it.** A third `implementations` line, `name:
  currency-controller`, `path: currency-controller`, `revoked: []`. It passes
  `party_artefact.py check` (`OK: party.yaml is a valid party artefact`).
- **Numbered by the platform's own `v*` tag** — *decision, delegated.* It gets **no** version axis
  of its own, unlike `identity-substrate`. Reason: it is platform machinery, exactly like the
  orphan guard, whose emitted body already carries `policy-as-versioned.dev/policy:
  platform-machinery` for this reason. A `currency-controller/vX.Y.Z` line would claim the module
  can be pinned independently of the cage ladder it writes into, and it cannot — the rung it writes
  is `graded/cage.py`'s own bottom rung and the two must ship together. Every object in
  `manifests/` now carries that identity label, and the check asserts the value by reading it off
  `render-orphan-guard.py` rather than restating it.
- **The schedule stays one minute** — *decision, delegated.* Reason: ADR-0024's clocks are
  *repository* clocks, daily because feeds and pins move at most daily, each org at its own UTC
  hour. This is a cluster reconciler and its period **is** the estate's exposure window — how long
  a pod may keep running at its pre-retirement rung. What ADR-0024 binds and this obeys is
  recorded in `manifests/cronjob.yaml`: it acts on the cluster and commits nothing to any
  repository, opens no pull request and cuts no tag (its grant holds no credential that could); it
  may only tighten; and a missing instrument refuses the pass rather than acting on a guess.
- **Tighten-only, three ways, one of them not code** — *decision, delegated.* `recage_patch()`
  takes the retired claim and nothing else, so it cannot read and therefore cannot echo back a
  looser rung; `is_tighten()` holds every pod before it is patched and *holds* one it would not
  tighten, printing why; and `manifests/rbac.yaml` loses `delete` on pods. Reason for the third:
  a property that depends only on the code being right is one edit from being false, and RBAC is
  the half that survives a bad edit.
- **`--action evict` is deleted** — *decision, delegated.* Reason: eviction is a refusal wearing a
  cage's clothes. The old module's own README said the recreated pod "hits the retired-version
  orphan-guard → DENIED", i.e. the workload stops. Ticket 75 Q5 is the owner's own reason that the
  estate is a mutating controller and a workload never fails because it was deliberately denied.
  There is now one action.
- **A missing instrument re-cages nothing** (ADR-0020) — *decision, delegated, and the build of
  ticket 32's unbuilt item.* An array the controller cannot read is **not** an empty array: an
  empty `supported` set makes every claiming pod in the estate stale and would re-cage the lot. A
  404, an unreadable array, an empty array and an empty `SUPPORTED_VERSIONS` each raise
  `MissingInstrument`; the pass exits 2 with the reason named and touches no pod. The old
  `_default_supported()` fallback literal `1.0.0,2.0.0` is deleted with it — it named two versions
  the estate has retired (review finding EQ-11), and a stale default here re-cages the estate.

### 3. The term, and what the check can and cannot observe

`CONTEXT.md` gains a **Currency controller** term carrying the sentence verbatim; the old
**De-postured** entry is kept, marked superseded, and corrected — the word never covered the
**rung**, which is the whole defect. `ADR-0014` gains a dated amendment for the same reason.

**The controller's action changed, and this is the ticket's real finding.** Its patch removed the
version claim and the identity posture label. Under ADR-0022's ladder that cages *nothing*:
removing the claim takes the pod permanently out of `cage-tier`'s scope, so a patch that names no
tier **freezes** the pod at whatever rung admitted it, for the rest of its life. A retired-version
pod sat on at `restricted` and the retirement changed nothing. The patch now writes
`posture.acme.io/tier: isolated` and asserts `posture.acme.io/caged: "true"` in the same update, so
`cage-netpol`'s already-generated `cage-reach-isolated` — empty ingress and empty egress under both
policyTypes — selects it. The claim it removes survives as the annotation
`policy-as-versioned.dev/retired-claim`, so no record is destroyed.

*A second seam bug found while building, red before green:* the **unversioned**
`posture-trust-boundary` — the copy installed on the demo cluster — **Denies** any pod carrying the
identity posture label without a matching claim, and is not gated on a version. A patch that
removed the claim and left that label behind would have been **refused at admission** there. Every
*served* copy adds `only-this-policy-version`, so for an adopter running only the composed set a
claimless pod is out of its scope and there is no Deny; the reason the posture label is removed is
the unversioned copy, not those. Removing it is required against the first and harmless against the
second, so all four label writes go in one merge patch unconditionally.

**What `verify-currency.sh` observes offline, always.** The controller's logic against **planted**
state, and the seam between that logic and the policy bodies the estate actually **serves** — every
fact **derived** from a shipped file, never restated: `cage.py`'s own `ORDER` (so the mirror in
`currency.py` cannot drift), the served `cage-tier`'s matchConditions and `UPDATE` operation,
`render-orphan-guard.py`'s own label and identity, `render-governed-namespace-guard.py`'s own
`operations`, `posture-trust-boundary.yaml`'s validation, the served `cage-netpol`'s rung list,
reach table and generated podSelector key/value pairs (parsed out and used to *compute* which reach
policy selects the pod before and after the patch), and `rbac.yaml`'s own verbs. 59 `ok` lines.

The set of bodies is itself derived: the version array in `distribution/versions.yaml` — the same
array the orphan guard allow-lists and the controller reads — decides which trees are served, so
the retired 2.x/3.x shapes and the `vselfcheck` fixture are named and excluded rather than silently
included or silently skipped.

**What it cannot observe offline, and never claims.** No pod exists there. Nothing offline observes
that the CronJob fired, that the API server accepted the patch, that admission did not clobber it,
or that the NetworkPolicy actually cut the pod's reach. Those are facts about a running cluster.
`lib.sh pass_line` makes an unobserved live tail exit 3, so **this script has no PASS that does not
rest on an observed pod**, and its live half asserts the pod is still `Running` — a re-cage that
removed the workload would FAIL, not pass.

- **The live half is a named could-not-look, not a simulation** — *decision, delegated.* Reason:
  the scheduled runner has no cluster, and the alternative — planting a fake pod list and printing
  a PASS — would be a sentence claiming more than the run observed. The tail names each precondition
  separately instead of one aggregate. **Eight** of them: `kubectl` on `PATH`; the substrate
  (`docker`, the `kind` cluster `driftwood`, Flux Ready); the `currency-controller` CronJob; a
  readable `currency-controller-src` ConfigMap; **this checkout's** copy of `currency.py` inside it,
  compared by sha256 with both sides normalised the same way (grading a pass taken by a different
  copy would be a claim about code the run never read); a readable `policy-versions` ResourceSet; a
  running pod whose claim the array has retired; and a `cage-reach-isolated` NetworkPolicy already
  in that pod's namespace. Those preconditions produce **fifteen** distinct could-not-look
  sentences — five inherited from `lib.sh`'s `substrate_ok`, ten the script's own — and all fifteen
  are declared in `talk/verify-manifest.txt`; a sixteenth goes red as an undeclared skip, which was
  checked reason by reason with `truth_manifest.judge`.
- **Class stays `estate-observation | never:`** — *decision, delegated.* Reason: the manifest's own
  rule classes a script by what its PASS would rest on, and this one's PASS rests on a live pod.
  The first declared alternative also matches the pre-ticket-91 script, so the row is true on both
  sides of the platform merge.

**The old script's PASS claimed more than it observed, and that is fixed too.** Its live branch
created a Job from the CronJob and printed `ok reconcile job created`, then fell through to
`pass_line`. It never waited for the Job, never re-read the pod and never checked anything had
changed — so an exit 0 said "stale posture is re-evaluated post-admission" on the strength of one
`kubectl create job` succeeding. That PASS is recorded, on a machine with clusters, in
`REPAIR-2026-09-04.md:425`. The rewritten tail waits for the Job to complete, re-reads the pod, and
asserts four things on it: `tier=isolated`, the claim gone, the retired claim recorded in the
annotation, and `phase=Running` — a re-cage that removed the workload FAILs rather than passes.

**What the estate looked like while this was built, and it is not comfortable.** `kind-driftwood`
today carries `tuppence-reset/teller-stale`, a pod claiming `1.0.0` while the array declares
`4.0.0`, with **no tier and no caged label at all** — admitted before `cage-tier-4-0-0` was
installed and never re-evaluated since. That is the subject of this sentence, sitting uncaged on a
real cluster, and it is the best evidence that the mechanism was needed. It was **not** used to
produce a green: the cluster has no readable `policy-versions` ResourceSet and its CronJob mounts
the pre-ticket-91 code, so the tail reported exactly that and exited 3.

### 4. Ticket 80 item 6 changes direction

`issues/80` item 6 is struck through and closed: "delete or own" is no longer a live disjunction,
Q13 settled it on **own**, and this ticket executed it. `map.md`'s two retirement sentences (the
ticket-13 line and "The currency controller is retired (ticket 13)" under *Not yet specified*) are
corrected in the same change. Nothing is left for ticket 80 there.

### Pull requests

- hub: https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/pull/32
- platform: https://github.com/policy-as-versioned-platform/platform/pull/12

### Round 2, 2026-09-05: what review found, and what changed

The build was reviewed and **not** merged. Four blocking findings, two of them decisive, plus one
major and six minor. All are fixed; each is a real defect and none was a matter of taste.

- **F1, and it killed the live half outright.** The ConfigMap arrives through a command
  substitution, which strips trailing newlines, while the file was hashed straight off disk. So the
  two sides could **never** compare equal — not even against a byte-identical file — and
  `verify-currency.sh` had **no path to a PASS on any cluster**. The ticket's Done clause was
  unreachable and this ticket's own "either PASSes on a real re-caged pod or FAILs, no third
  outcome" was false as shipped. Both sides now go through the same normalisation. Measured on the
  module's own file: `0c9fd0e5ce96` with the trailing newline, `af313b20590d` without.
- **F2, its mirror image, and it defeated the thing its comment claimed to prevent.** `fail`'s
  `exit 1` runs inside the `$( )` subshell of the `[` test, and `set -e` does not propagate out of
  a command substitution used in a comparison. On a runner with neither `sha256sum` nor `shasum`
  both sides evaluated to the empty string, **compared equal**, and the script fell through into
  the live pass having read nothing. The hashes go into variables, the status is checked, and a
  missing tool is a `live_tail_skip` with a declared reason — a missing instrument is a
  could-not-look here, the same rule the controller itself follows (ADR-0020).
- **F3.** Step 4 derived the ticket's central claim from `graded/policies/`, which **no gitops
  Kustomization serves** and which is installed on no cluster. Every served and composed body
  carries an `only-this-policy-version` matchCondition the authoring copy lacks, and it **reverses**
  the answer for `cage-netpol`: with the claim removed the policy does not fire. The ok line
  "cage-netpol's own matchConditions still fire on the labels the patch leaves ... so it fires" was
  **false against every body the estate serves**. The check now reads the served bodies, derived
  from the declared version array, and keeps `graded/` only as a named cross-check that prints the
  difference.
- **F4, the consequence, and it is the honest limit of this mechanism.** Because the served reach
  generator is claim-gated, the re-caged pod **cannot generate its own reach cage**. It can only be
  *selected* by a `cage-reach-isolated` the namespace **already carries**. On the demo cluster
  `cage-reach-*` exist only in namespace `driftwood`; `kubectl get networkpolicy -n tuppence-reset`
  returns nothing — and `tuppence-reset/teller-stale` is the estate's one stale pod. Re-caging it
  today would write `isolated` as a **label**, not isolation. That precondition is now named in
  `CONTEXT.md`, `README.md`, the module docstring and this answer, and the live tail checks the
  NetworkPolicy **before** the reconcile pass, because the pass strips a live pod's claim and there
  is no undo: a precondition discovered afterwards would be a red left behind as damage.
- **F5, major.** The `posture-trust-boundary` Deny holds for the **unversioned** copy installed on
  the demo cluster, not for the served ones, which are claim-gated too. Removing the posture label
  is still right; the reason is recorded with its scope in all four places.
- **F7** `governed-namespace-requires-claim` is now asserted `operations == ['CREATE']` off its own
  renderer — it is the one Deny whose whole subject is a claimless pod, and this patch makes one, so
  a promotion to `UPDATE` should break this check rather than every re-cage in the estate.
  **F8** the `caged` label enters the trimmed pod shape: every reach policy selects on caged **and**
  tier, so a pod at the bottom rung with the caged label absent was held forever and selected by
  nothing — it is re-caged now, and the patch asserts the label. **F9** the live PASS compares the
  NetworkPolicy's own `podSelector` against the pod's labels instead of merely observing the object
  exists. **F10** the `party.yaml` contrast is the `policy` tag line, not `identity-substrate`.
  **F11** an unrecognised argument is now a fault rather than a silent no-op.
- **Review finding on defect (c), accepted and sharper than reported.** The old live branch selected
  **any** postured pod, not a stale one, and then printed a PASS on the strength of one `kubectl
  create job`.

**Two residual softenings, recorded rather than hidden** (they are not counter-examples to
tighten-only; they are what the patch costs, and neither was written down before this round):

1. `infra` is a platform **role declaration** on a Namespace (ADR-0022), not a rung on this ladder.
   A pod somehow carrying `tier=infra` reads as unknown and is **overwritten** with the bottom rung
   — fail-closed, but an overwrite of a declaration rather than a move along the ladder.
2. After the patch the pod is outside the scope of the cage mutation, the orphan guard **and** every
   served reach generator, so its rung is held by a label **no admission will ever re-assert**. A
   claiming pod's rung is re-clobbered from its Namespace on every update; a re-caged pod's is not.
   What still holds it is RBAC: a workload cannot patch its own pod.

Both are now in `CONTEXT.md`'s term and in the ADR-0014 amendment.

### Files changed

- **platform** (`ticket-91-the-currency-controller-is-owned`, one commit): `currency-controller/currency.py`,
  `currency-controller/verify-currency.sh`, `currency-controller/README.md`,
  `currency-controller/up.sh`, `currency-controller/manifests/rbac.yaml`,
  `currency-controller/manifests/cronjob.yaml`, `party.yaml`,
  `distribution/render-governed-namespace-guard.py`.
- **hub** (`ticket-91-the-currency-controller-is-owned`): `CONTEXT.md`,
  `docs/adr/0014-unclaimed-is-caged-governed-namespace-requires-claim.md`,
  `talk/verify-manifest.txt`, `talk/up.sh`, `.scratch/ecosystem/issues/13`, `/80`, `/91`,
  `.scratch/ecosystem/map.md`.

### Not done

- **No live observation of the sentence.** Deliberate. See item 3.
- **`up.sh` ordering in `talk/up.sh` is corrected but unproven.** The controller is now installed
  after `graded/up.sh` rather than before it, because there is no ladder to re-cage into until the
  cage policies are on the cluster. Nothing in the gate runs `talk/up.sh`, so that ordering is
  argued, not observed.
- **The orphan guard still ships `Deny`.** It is the admission-time half of the same retirement
  rule and it refuses rather than caging. That is ticket 89's, not this one's, and this build
  deliberately did not touch a released policy body.

## Waits on the owner

- **A cluster carrying the instrument, the subject AND a reach cage in the subject's namespace, so
  the live half can be observed.** Concretely, after this platform branch merges: `graded/up.sh`
  then `currency-controller/up.sh` on `kind-driftwood`, a readable `policy-versions` ResourceSet,
  `tuppence-reset/teller-stale` left in place — **and** a `cage-reach-isolated` NetworkPolicy in
  `tuppence-reset`, which that namespace does not have today because its only non-stale pods sit at
  `baseline` and the reach generator skips `baseline`. Without it the tail reports a could-not-look
  and runs no pass, by design. This build did not install anything or re-cage a live pod: that
  changes state other checks read.
- **Whether a namespace at `baseline` should carry the bottom rung's reach cage at all.** It is the
  gap F4 exposes and this module does not own it: either the governed tier already puts a claiming
  pod above `baseline`, or the reach cages are rendered per governed Namespace from the composed
  artefact instead of generated from a pod — the upgrade path `cage-netpol.yaml`'s own header
  already names. It belongs with the cage ladder, not with the controller.
- **Merging the platform pull request.** Until it merges, `truth.yml` clones platform's default
  branch and grades the pre-ticket-91 script. The manifest row is written to be true on both sides.

Map line: `- [91 — The currency controller is un-retired and owned](issues/91-the-currency-controller-is-un-retired-and-owned.md) — ticket 13's retirement is withdrawn on the sources (fx is money, "it 404s" was ticket 32's unbuilt substrate repair); the controller becomes a platform-owned `implementations` member numbered by the platform's own tag, with one action and no `delete` verb, and its patch now writes the `isolated` rung it never wrote before — removing the claim alone froze a stale pod at its admitted rung forever. `CONTEXT.md` gains a **Currency controller** term and `verify-currency.sh` grades its sentence: the offline half derives the seam from cage.py and the bodies the estate SERVES, never the authoring copies under graded/; the live half is a named could-not-look with eight preconditions, and there is no PASS that does not rest on an observed pod. Its precondition is part of the term: every served reach generator is claim-gated, so a re-caged pod cannot generate its own reach cage and can only be selected by one its namespace already carries. Ticket 80 item 6 closes on *own*. Delegated under ADR-0025.`
