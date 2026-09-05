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

*A second seam bug found while building, red before green:* `posture-trust-boundary` **Denies** any
pod carrying the identity posture label without a matching claim. A patch that removed the claim
and left that label behind would have been **refused at admission**. All four label writes go in
one merge patch.

**What `verify-currency.sh` observes offline, always.** The controller's logic against **planted**
state, and the seam between that logic and the policy bodies this repo ships — every fact
**derived** from the shipped file, never restated: `cage.py`'s own `ORDER` (so the mirror in
`currency.py` cannot drift), `cage-tier.yaml`'s own matchConditions and `UPDATE` operation,
`render-orphan-guard.py`'s own label and identity, `posture-trust-boundary.yaml`'s own validation,
`cage-netpol.yaml`'s own rung list, reach table and generated podSelector key/value pairs (parsed
out and used to *compute* which reach policy selects the pod before and after the patch), and
`rbac.yaml`'s own verbs. 57 `ok` lines.

**What it cannot observe offline, and never claims.** No pod exists there. Nothing offline observes
that the CronJob fired, that the API server accepted the patch, that admission did not clobber it,
or that the NetworkPolicy actually cut the pod's reach. Those are facts about a running cluster.
`lib.sh pass_line` makes an unobserved live tail exit 3, so **this script has no PASS that does not
rest on an observed pod**, and its live half asserts the pod is still `Running` — a re-cage that
removed the workload would FAIL, not pass.

- **The live half is a named could-not-look, not a simulation** — *decision, delegated.* Reason:
  the scheduled runner has no cluster, and the alternative — planting a fake pod list and printing
  a PASS — would be a sentence claiming more than the run observed. The tail names each precondition
  separately instead of one aggregate: a `kind` cluster `driftwood`, the `currency-controller`
  CronJob, a readable `currency-controller-src` ConfigMap, **this checkout's** copy of `currency.py`
  inside it (compared by sha256 — grading a pass taken by a different copy would be a claim about
  code the run never read), a readable `policy-versions` ResourceSet, and a running pod whose claim
  the array has retired. All twelve reasons are declared in `talk/verify-manifest.txt`; a
  thirteenth would go red as an undeclared skip, which was checked with `truth_manifest.judge`.
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

- **A cluster carrying both the instrument and the subject, so the live half can be observed.**
  Concretely: `graded/up.sh` then `currency-controller/up.sh` on `kind-driftwood` after this
  platform branch merges, with a readable `policy-versions` ResourceSet, and
  `tuppence-reset/teller-stale` left in place. The check then either PASSes on a real re-caged pod
  or FAILs — no third outcome. This build did not do it because installing unmerged code and
  re-caging a live pod on the shared cluster changes state other checks read.
- **Merging the platform pull request.** Until it merges, `truth.yml` clones platform's default
  branch and grades the pre-ticket-91 script. The manifest row is written to be true on both sides.

Map line: `- [91 — The currency controller is un-retired and owned](issues/91-the-currency-controller-is-un-retired-and-owned.md) — ticket 13's retirement is withdrawn on the sources (fx is money, "it 404s" was ticket 32's unbuilt substrate repair); the controller becomes a platform-owned `implementations` member numbered by the platform's own tag, with one action and no `delete` verb, and its patch now writes the `isolated` rung it never wrote before — removing the claim alone froze a stale pod at its admitted rung forever. `CONTEXT.md` gains a **Currency controller** term and `verify-currency.sh` grades its sentence: the offline half derives the seam from cage.py, cage-tier, cage-netpol, posture-trust-boundary and the RBAC verbs; the live half is a named could-not-look with six preconditions, and there is no PASS that does not rest on an observed pod. Ticket 80 item 6 closes on *own*. Delegated under ADR-0025.`
