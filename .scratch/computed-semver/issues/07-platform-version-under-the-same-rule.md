# 07 — What in `platform` carries a version, and what numbers it?

Type: grilling
Status: resolved
Blocked by: 05

## Question

Charting settled the premise, so do not re-argue it: **the same rule binds the platform**. Exempting
the distribution layer from the versioning rule the distribution layer enforces is the self-exemption
`honesty/reflexive.py` exists to refuse. The apparatus prices its own risk against its own £10k band
and passes its own test. This is the same argument.

What is not settled is the shape. Two questions sit under the premise, and neither has one obvious
answer. **Most of the platform's policy carries no version at all**, so "bind the platform's version"
begs the question of what a version would attach to. And where a version does exist, `platform` now
holds three of them: two `v1.0.0` directory trees that disagree, and the tag an institution pins.

Tickets 03, 04 and 05 have loaded a forcing function. The gate fails and names the file when observed
movement traces to a policy carrying no version. Five of the eight live policies carry none. So the
gate is red from day one until this ticket lands, and 05 refused a grace mode on purpose.

**Decide:**

1. **Each of the five unversioned policies: version it, or prove it cannot move a verdict.** The five
   are the rendered orphan guard, `graded/policies/cage-tier.yaml`, `graded/policies/cage-netpol.yaml`,
   `posture/policies/posture-trust-boundary.yaml` and `posture/policies/stamp-posture.yaml`. One answer
   for all five is almost certainly wrong. Two of them mutate every claiming pod, and ticket 02 settled
   that the cage *spec* is the verdict, so "cannot move a verdict" looks unavailable to them.
   `cage-tier.yaml` holds its dials inline as a CEL map, where `baseline` stamps `cpu: 500m` and
   `quarantine` `100m`. Editing one number re-specs every caged pod in the estate. Under `CONTEXT.md`
   that edit is major. Decide the route per file, and decide what a version line looks like for a
   MutatingPolicy. The three versioned policies use a `vN.M.P/` directory per version. Copying that
   shape to a mutating policy multiplies the mutations rather than replacing one.
2. **How the platform's own version line is numbered.** Ticket 05 handed this over and settled only
   that an array-only release is gated and that a retirement is major. An institution already pins two
   numbers: a platform tag in `gitops/platform/platform-pin.yaml`, and an element of the version array.
   Decide which number an adopter's break is expressed in, whether the platform tag is computed by the
   same gate against the same corpus, and what the platform tag means when a single policy inside it
   goes major.
3. **Whether the platform's version covers the orphan guard's own CEL.** `distribution/versions.yaml`
   is two things at once. It is the version *array*, which is data the guard ranges over. It is also an
   unversioned *policy*, which is the guard's own allow-list logic. Ticket 03 treats it as both, which
   is honest and leaves the decision here. Editing the array is settled by 05. Editing the guard's CEL
   is not. This is the ADR-0002 tension, and it belongs in this ticket, not in the corpus.
4. **Whether `distribution/policies/` and `policy/policies/` are one version line or two.** They are
   separate trees in the same repo. Each declares its own `v1.0.0` with different content, and
   `versions.yaml` reconciles only the first. Ticket 03 makes the gate refuse a
   same-version-different-content collision, so the gate cannot go green while both stand. Both answers
   are defensible. Two lines need a namespace in the pin. One line makes the second `v1.0.0` a mislabel
   to renumber, which is itself a release that the gate must classify.

**Settled elsewhere. Do not re-open:** the retirement edge is ticket 05's, and 05 answered it. A
retired array element classifies as major with no policy diff, because the comparison window is the one
that stood before the release, and the pinned consumer loses its pin. An array-only release is gated by
the same rule. This ticket keeps only the numbering.

**Hands on to implementation:** ADR-0011 records the gate and cross-references ADR-0002. `CONTEXT.md`
gains one sentence on reset on bump. Both come from 05 and are listed here so they are not lost.

## Answer

Resolved by grilling, 2026-08-22, over seven rounds and twenty-one decisions. Two reframes drove the
shape, and both came from outside the four decisions the ticket listed. One of my own recommendations
was wrong and the owner's answer corrected it. All three are recorded below, not smoothed over.

### The first reframe: unversioned is a symptom of unpinned delivery

All three institutions pin `path: ./distribution` and nothing else. **No Flux Kustomization anywhere
targets `./graded` or `./posture`.** Those four policies reach a cluster only through
`graded/up.sh` and `posture/up.sh` running `kubectl apply -f`, not even `-k`, so their
`kustomization.yaml` files are dead. `policy/policies/v1.0.0/` is absent from the version array, so
nothing renders a Kustomization for it either.

So four of the five, plus the second `v1.0.0` tree, share a deeper trait than carrying no version.
They are delivered outside the pinned path. A version number on a file that no `GitRepository` pins is
decoration, because ADR-0002's unit of adoption is the reviewed pin bump. **This ticket owns delivery
and numbering as one fix.**

This reaches back into cs-03 and cs-05. Both assume the installed set comes from the version array.
For four of the eight policies it does not, so the gate cannot see them in order to fail on them.
Raised as a comment on cs-05.

### The second reframe, from the owner: there is no gate, only cages

Two `Deny` policies remain, and both are structural. The orphan guard refuses an unknown claim.
`posture-trust-boundary` refuses a forged posture. **Every policy that carries content is `Audit`.**
So enforcement now happens by cage severity, and the cage ratchets in one direction. The owner's words:
it "may ultimately degrade to something that is too expensive to run or not functional". Versioning
makes that visible. It does not stop it. Sections 5 and 9 carry the consequences.

### 1. The five, under one mechanism

**One version mechanism, not two classes.** Each claim-wide policy becomes a per-version copy,
self-scoped on the claim value, exactly as `require-nonroot` already is. A pod pinned to `1.0.0` then
keeps `1.0.0`'s cage dials for ever, which is the estate's own thesis applied consistently.

I first recommended splitting the five, on the grounds that `stamp-posture` and
`posture-trust-boundary` are the anti-forgery pair that makes the claim mean anything, so an invariant
guarding the version mechanism cannot be a member of it. **The owner chose one mechanism.** The hole
that creates is closed by rendering rather than by exception, in the next paragraph.

I also argued at first that per-version copies would race, because two `MutatingPolicy` objects would
stamp the same `cpu` field. **That was wrong.** Self-scoped copies match on disjoint claim values, so
two copies never see the same pod. The real cost of one mechanism is duplication, not a race.

- **Mandatory members are generated into every version tree**, so a human cannot omit one. This removes
  the failure instead of detecting it, and the estate already owns the pattern in
  `render-orphan-guard.py`, which carries an offline twin and a self-check.
- **One authoring copy stays under `graded/` and `posture/`. The rendered copies are committed.** Git
  and the gate both read real files, which cs-06 requires, because it parses the YAML. Rendering at
  reconcile time would hide every claim-wide policy from the gate.
- **The PriorityClasses go in too, with versioned names.** `graded/policies/priorityclasses.yaml` is
  not a side file once severity is the enforcement. Its `value: -10` decides which pod the kubelet
  reclaims first, and `cage-tier` selects one of the three by name. So `cage-baseline` becomes
  `cage-baseline-1-0-0`, at three cluster-scoped objects per installed version, which is nine per
  cluster at the coexistence floor of three.
- **The orphan guard is the one member that cannot join**, because it is the aggregate over the array
  and cannot self-scope to one claim. It carries no identity label at all today, so cs-06's rule would
  fail the gate on the one policy that is correct. It takes the identity **`platform-machinery`**, and
  cs-06 learns that this family is numbered by the platform tag. The family name states the rule.
  A by-name exclusion would silently miss the next machinery object, and the PriorityClasses raise the
  same question, so the exception has to be a class.
- **`up.sh` becomes an offline twin, not a delivery path.** It renders the version trees exactly as the
  ResourceSet would and applies that, so the demo runs without Flux and there is still one truth.
  Stripping it entirely breaks the offline demo. Leaving it applying policy keeps the second delivery
  path alive, which is the defect this ticket exists to close.

**A version is four coordinated edits, not a directory.** The three versioned policies carry it in the
directory, in `metadata.name` (`require-nonroot-1-0-0`), in a `policy-version` label, and in a
`matchConditions` self-scope. The self-scope sits in `matchConditions` on purpose: a comment in
`v1.0.0/require-nonroot.yaml` records that Kyverno flattens `objectSelector` into one shared webhook
configuration, last-reconciled-wins, which silently breaks multi-version coexistence. The renderer must
emit all four.

### 2. The platform's own number

**One rule, one gate, one corpus.** The platform tag is major when a platform change can move any
workload's cage spec or admission. cs-05 already gated the array-only case, which is a platform-tag
release by definition.

The repo already carries two tag namespaces. HEAD is tagged `v0.1.1`, driftwood pins `tag: v0.1.0`
with its resolved commit, and the array's elements name `policy/v1.0.0` and `policy/v2.0.0`. Keep both.
Collapsing them breaks multi-version coexistence, because several policy tags must be installed at once
against one platform tag, and a version must be retirable without a machinery release.

**Cut platform `1.0.0` in the repair release.** cs-05 settled that version legality follows semver
2.0.0 and adds nothing. Semver 2.0.0 gives `0.x` no compatibility guarantee, so while the platform sits
at `v0.1.1` a change the gate computes as major can be declared `0.2.0` and the gate has nothing to
refuse. The rule would be decorative for exactly the period when these repairs land. Applying the
`>=1.0.0` rules at `0.x` by local rule was rejected: cs-05 refused to invent a dialect of semver.

### 3. The orphan guard and the ADR-0002 tension

**The platform number covers the guard's template as well as the array.** `versions.yaml` is both the
version array and a policy, and the platform tag numbers both. That is the whole tension, settled in
one sentence. Treating the template as machinery exempt from measurement is the self-exemption
`honesty/reflexive.py` refuses, because the template is where a `Deny` is written.

### 4. The two `v1.0.0` trees

**Not a collision of two installed lines.** Nothing installs `policy/policies/v1.0.0/`. It declares
`1.0.0` in all four places and its content contradicts the distribution tree's `1.0.0`:
`require-nonroot-1-0-0` wants `runAsNonRoot == true`, and `may-run-root-if-attested-1-0-0` permits root
when the pod is attested and hardened. A workload carries one claim string, so both would match the
same pod and report opposite results.

**It folds into the distribution line at `1.0.1`.** Its rule is `nonroot || (attested && hardened)`,
which is strictly wider than `1.0.0`, and `CONTEXT.md` calls a widening a patch. The line reads `1.0.0`,
then `1.0.1` widens, then `2.0.0` tightens by adding the read-only root filesystem. Because `2.0.0`
already exists this is a backport, and cs-05 specified the maintenance-branch shape and the
`--certificate-identity-regexp` it needs. A second policy family with its own claim was rejected: it
needs a second label, and the one-string pin that doubles as the workload selector is the original's
signature elegance.

### 5. What "major" means when the cage is the only enforcement

**Any change where the new cage spec is not at least as permissive as the old one.** Ticket 02 already
moved the comparison from verdict enums to cage specs, so the rule speaks the same language.

The rule is stated at spec level, not at dial level, because `cage-tier` changes more than dials. It
appends a `waf-sidecar` container at restricted and quarantine, sets `priorityClassName`, flips
`readOnlyRootFilesystem` and `runAsNonRoot`, and applies a second JSONPatch dropping `ALL` capabilities
when the tier hardens. An enumerated list of surfaces rots the first time someone adds a mutation.

**The gate never estimates viability.** A viability rule needs a threshold, and cs-04 banned thresholds
for exactly this reason: a threshold invites tuning the corpus until the release passes. The honest
limit it prints instead is one sentence. The ceiling moved down, and the gate does not know whose
workload dies at the new number.

### 6. The repair release

**Hand-classified, and recorded as the last unmeasured bump.** cs-05 settled the order: version the
five first, then ship the gate hard, with no grace mode. So the repair is cut while the gate does not
yet exist. Holding it until the gate exists is a deadlock dressed as rigour. Claiming it is
verdict-neutral by construction would be the post-hoc justification this map exists to delete. Write
the classification and the reasoning into the release commit, and let cs-05's honesty check re-run it
later. That check already prints when a past release would classify differently, and it does not fail.

**It re-cuts both supported versions.** Today one shared `cage-tier` cages every claiming pod, whatever
version it claims. After section 1 the cage lives inside each version tree, but `policy/v1.0.0` and
`policy/v2.0.0` are cut tags and cannot gain files. So on the day the shared copies are deleted, every
pod pinned to either version loses its cage, its network policy and its posture check. The release
therefore publishes `1.0.2` and `2.0.1` with the full set and swaps the array elements in the same
release, so no cluster ever runs a version without a cage. Running both copies side by side through a
transition window was rejected: a shared `cage-tier` and a per-version `cage-tier` both match the same
pod and both stamp `cpu`, which is the collision that section 1 shows does not otherwise exist.

**One commit, three tags, one evidence file.** Platform `1.0.0`, policy `1.0.2` and policy `2.0.1` are
one change to one repository, and splitting them invents an intermediate state where the machinery
expects trees that do not exist yet. One evidence file is also the honest record, because the
classification was computed once against one corpus. `cut-release.yml` takes a single `version` input,
so this needs a named change to that workflow rather than a silent one.

### 7. Four rules the gate gains

1. **Read prior versions from their tags, never from HEAD.** The delivered `1.0.0` comes from tag
   `policy/v1.0.0`, but the gate would naturally read `distribution/policies/v1.0.0/` at HEAD, and a
   hand-edit there would fool it about what `1.0.0` means. A **frozen-tree check** fails when a HEAD
   copy of a released tree differs from its tag. This also makes cs-05's phrase "the window as it stood
   before this release" mechanical rather than aspirational.
2. **Re-render only the tree being cut.** Re-rendering every tree and failing on any diff would freeze
   the dial table for ever, which is the opposite of what versioning is for.
3. **Refuse a release that removes an enforcement surface from a version.** A refusal, not a bump class,
   so the number stays honest. It costs almost nothing, because the mandatory-member list from
   section 1 **is** the enforcement-surface list, and the refusal is a set comparison against it. Two
   precedents in this map: cs-04 replaced its threshold with three binary refusals, and the composition
   work found a refusal on coverage with zero verdict movement.
4. **Refuse an array element with an empty `commit`.** Without it the field silently empties again on
   the next hand-edited element.

### 8. Three findings

1. **cs-03 and cs-05 assume the installed set comes from the version array.** For four of the eight
   policies it does not. Raised as a comment on cs-05.
2. **Both array elements carry `commit: ""`.** The template emits a `commit:` field only when the value
   is non-empty, so every per-version `GitRepository` is pinned by tag alone. ADR-0001 wants the
   resolved SHA as belt and braces and ADR-0002 says Renovate's `customManager` maintains the pair. The
   platform pin at driftwood does carry its commit, so the gap is inside the array only. Fill both in
   the repair release, and add rule 7.4 so it cannot recur.
3. **The array's `action: "Audit"` field is read by nothing.** It appears only in `versions.yaml`. The
   template never references it, `render-orphan-guard.py` never reads it, and cs-01's own
   `rederive_bumps.py` takes the action from `validationActions` inside the policy file. Two
   declarations of one fact with nothing reconciling them is the drift this estate writes verify
   scripts to catch. **Delete it.** Making it live instead was considered and rejected: `require-nonroot`
   is hand-authored rather than rendered, so the field's truth would split by whether a policy is
   rendered or written. Deleting it changes no rendered output, so it is a patch on the platform tag.

### 9. Two named limits

1. **The cage ratchets tighter and nothing pushes back.** Each tightening is correctly labelled major,
   and many correct majors still end at a platform too expensive to run. Versioning makes the movement
   visible and does not oppose it. `verify/proportionality/render.py` is the only apparatus in the
   estate that prices a control against a risk band, so it is the only candidate counter-pressure. It
   exists, confirmed. Wiring it in is not this ticket's job, and the limit stands until something does.
2. **The rule sees only the workload's side of the cage.** `CONTEXT.md` measures a bump by impact on
   the workload, so removing enforcement scores as a patch, because the passing set only grows. That is
   the rule working as written and giving an answer nobody wants. Rule 7.3 covers the case the gate can
   see. Redefining major to include enforcement removal was rejected, because it breaks the
   workload-side definition that is the hard half the estate already got right.

### What this ticket hands on

Three implementation tickets, per the owner's decision to keep this one a grilling:

- **[Ticket 09](09-repair-release-and-pinned-delivery.md)** cuts the repair release.
- **[Ticket 10](10-render-mandatory-members.md)** builds the renderer and its offline twin.
- **[Ticket 11](11-gate-rules-from-cs-07.md)** carries the four gate rules and the two `CONTEXT.md`
  edits.

Also inherited from cs-05 and still owed: **ADR-0011** records the gate and cross-references ADR-0002,
and **`CONTEXT.md`** gains one sentence on reset on bump.

### What this ticket did not decide

- **Whether `verify/proportionality/render.py` becomes the cage's counter-pressure.** Named as the only
  candidate and left as limit 9.1.
- **A viability model for a caged workload.** Refused on purpose. It needs a threshold, and cs-04
  banned thresholds.
- **Anything about `nist` and `ico`.** `nist` holds an OSCAL catalog and `ico` a penalty-feed schema.
  Neither pins platform and neither runs pods, so they are feeds, not consumers.
- **Cross-party composition.** Still the [`policy-composition`](../policy-composition/map.md) map's.

## Comments

Finding raised 2026-08-21 from [ticket 03](03-what-is-the-corpus.md). **This ticket is bigger than its
title.** It is written as "bind the platform's own *version*", but the real gap is that most of the
platform's policy carries no version at all.

`platform` holds eight live Kyverno policies. **Three carry a version:**

- `distribution/policies/v1.0.0/require-nonroot.yaml`
- `distribution/policies/v2.0.0/require-nonroot.yaml`
- `policy/policies/v1.0.0/may-run-root-if-attested.yaml`

**Five do not:**

- the orphan guard rendered from `distribution/versions.yaml`
- `graded/policies/cage-tier.yaml` (MutatingPolicy)
- `graded/policies/cage-netpol.yaml`
- `posture/policies/posture-trust-boundary.yaml`
- `posture/policies/stamp-posture.yaml` (MutatingPolicy)

Two of the five mutate **every** claiming pod. `cage-tier.yaml`'s dials live in it as a CEL map:
`baseline` stamps `cpu: 500m`, `restricted` `250m`, `quarantine` `100m`. Editing one of those numbers
changes the spec of every caged pod in the estate, and no version number says so. Under `CONTEXT.md`'s
own rule that edit is **major**, because a pod that cannot schedule under a tightened limit is
refused.

Ticket 03 settled the gate's behaviour here: the subject is **every** Kyverno policy that can reach a
pod, and when observed movement traces to a policy carrying no version the gate **fails and names the
file**. There is no version number that can describe that change. So this ticket now has a forcing
function — the gate will not go green until the unversioned five are either brought under a version
line or shown to be incapable of moving a verdict.

Note the ADR-0002 tension to settle here, not in the corpus: `versions.yaml` is simultaneously the
version *array* (data the orphan guard ranges) and an unversioned *policy* (the guard itself). Ticket
03 treats it as both, which is honest but leaves this ticket to decide whether the platform's version
covers the guard's own CEL.

Also unresolved and inherited: `distribution/policies/v1.0.0/` and `policy/policies/v1.0.0/` are
separate trees in the same repo, each declaring its own `v1.0.0`, and `versions.yaml` reconciles only
the first. Ticket 03 makes the gate refuse a same-version-different-content collision, which surfaces
the question. Deciding whether they are one version line or two belongs here.

---

Re-typed `task` to `grilling` on 2026-08-22, and re-titled. The comment above was right that the
ticket was bigger than its title, so the title now names the question instead of the job. The body
carries four decisions that the comment and ticket 05 had left implicit. Nothing was dropped. The
retirement edge moved out of the body and into a "settled elsewhere" line, because ticket 05 answered
it while this ticket was blocked.
