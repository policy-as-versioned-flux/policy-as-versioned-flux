# 89 — Deny is not a rung: the mutating controller

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Ticket 75 Q5 was answered by the owner with a reason: proportionality is managed with a better cage and better mitigations; a workload can find itself unable to run only because it does not fit the cage, never because it is deliberately denied; the estate is a mutating admission controller more than a validating one. The assistant's narrower call, a surviving locked door for access control, data protection and key management, is overruled.

Make the estate say and do that:

1. Inventory every shipped `validationFailureAction: Enforce` or Deny-shaped rule in the served policy copies (the review counted two Deny policies). For each, either re-express it as a cage constraint (a mutation that renders the workload into a rung it cannot run from, or a tighten-only mutation the workload must fit) or retire it with the engine's computed bump. Record the choice per rule.
2. `verify/proportionality` derives Audit versus Deny from each party's signed band and has no shipped subject. Retire the Audit-versus-Deny derivation, or re-point it at tier selection, and update or delete the verify script so the gate does not grade a mechanism that no longer exists.
3. Reconcile the three documents that disagree about whether a Deny may ship (the review names them under principles/P2) to one sentence: nothing is denied; a workload that does not fit its cage does not run.
4. Amend CONTEXT.md's Cage entry (done by ticket 75 for the definition) and check ADR-0014, ADR-0018 and ADR-0022 carry dated notes that say the same.

Done = no served policy copy contains a Deny-shaped rule that is not a cage constraint, `verify-all.sh` grades no Audit-versus-Deny subject, and the three documents agree.

## Notes

Charted by ticket 75 (Q5). Findings: REVIEW-2026-09-02.md principles/P2, the two shipped Denys. ADR-0022 carries the owner's reason as a dated note.

## Answer

Built 2026-09-05. The estate's Deny-shaped rules were three, not two: the review's own condensed
evidence (P2-4) names the third. All three now carry a recorded choice, the two the platform
renders no longer refuse anything, `verify/proportionality` grades tier selection instead of
Audit-versus-Deny, and four documents carry one sentence between them.

**Nothing is denied; a workload that does not fit its cage does not run.**

### The check that grades it

`verify/deny-is-not-a-rung/verify-deny-is-not-a-rung.sh`, discovered by `talk/verify-all.sh`
(106 discovered on this branch, measured by `verify-truth-line.sh` and never typed into a
check), row in `talk/verify-manifest.txt` as `estate-observation | waits:`
with both could-not-look reasons declared. It scans the hub and all eight units for Deny-shaped
rules — `spec.validationActions` carrying `Deny`, and the 2022 `validationFailureAction: enforce`
— and joins them to `verify/deny-is-not-a-rung/register.yaml`, which records the choice and the
reason per rule.

The inventory is taken on every run, not written down once, because a written inventory starts
rotting the next day: this ticket exists partly because `CONTEXT.md` called a shipped Deny "the
July record, superseded" for eight days while the gate graded its denial as correct. The join is
graded in both directions, so the register cannot lie either way: an unrecorded Deny FAILS, a row
that says converted while a copy survives FAILS, a row that says a copy survives when none does
FAILS, and a row still marked `waiting` whose declared source no longer emits the Deny FAILS with
"move the row to converted-at-source". An outstanding copy is exit 3 naming the tag it waits for,
never a pass.

The scan is line-based, and that is load-bearing: three of the estate's Denys live inside a
`ResourceSet`'s `resourcesTemplate` STRING (one per adopter, `gitops/composed/composed-set.yaml`),
where a `yaml.safe_load_all` walk sees a ResourceSet and no policy at all. A document scan would
have reported the estate three refusals cleaner than it is. Measured 2026-09-05 after the scan was
widened: 36 Deny-shaped rules across the hub and the eight units, 15 of them inside the four trees
the register excludes with a reason, 21 on the register -- and all 21 still outstanding. Run
`--inventory` for the figure on the day you read this rather than trusting these; the register is
the record of choices, and the scan is what keeps it honest.

### Item 1 — the inventory, and the choice per rule

| rule | copies | choice | state |
|---|---|---|---|
| `governed-namespace-requires-claim` | 4 | re-expressed as a cage constraint | source converted on the platform branch |
| `policy-version-orphan-guard` | 7 | re-expressed as a cage constraint | source converted on the platform branch |
| `posture-trust-boundary` | 10 | retired at the next declared line | waiting |
| `encrypt-at-rest` (hub, `verify/proportionality`) | 0, was 1 | retired | converted, gone |

**`governed-namespace-requires-claim` — a MutatingPolicy that puts the pod on the bottom rung.**
ADR-0022's 2026-08-28 addendum promoted this to `Deny` and called it "the one refusal the doctrine
allows", for a reason that was real and observed live: under `Audit` a claim-less pod ran
COMPLETELY UNCAGED inside a Namespace whose declared tier was `isolated`, so the Namespace fell
closed and the pod fell open. The shape was wrong, not the reason. It is a `MutatingPolicy` now
and the pod is admitted carrying `isolated`, its dials, `cage-isolated` with its integer priority
and `preemptionPolicy`, host namespaces shut, all capabilities dropped and a WAF sidecar — so the
pod falls closed with the Namespace. Silence is not an exemption and it is not a refusal either:
silence is the bottom rung. The mutation body is `graded/policies/cage-tier.yaml`'s own, read out
of that file by the renderer with `tier` pinned to the literal `'isolated'` and the now-unread
`nsTier` variable dropped, so there is no third copy of the dial table to drift.

**`policy-version-orphan-guard` — `Audit`, and `cage-tier` is the cage.** The rule matches a pod
that CLAIMS a version, and every claiming pod is already caged by `cage-tier`, which renders its
Namespace's declared tier and falls closed to `isolated` — since ticket 63 for an ungoverned
Namespace too. So the demotion admits nothing uncaged. The versioned rules an orphan claim escapes
are a priced hole (ADR-0026), and the report is the observation that price rests on.

**`posture-trust-boundary` — retired, at the next declared line, not in this build.** It is
already unreachable: `posture/policies/stamp-posture.yaml` overwrites `posture.acme.io/version`
from the validated claim on CREATE and UPDATE, and Kyverno's mutating webhook runs before its
validating one, so for the population this rule matches the label IS the claim by the time it
evaluates. It refuses nothing today; it is a tripwire in the shape the owner ruled out, and there
is nothing to re-express because the mutation already IS the boundary. It is not deleted here
because it ships in four CUT, SIGNED version lines (2.0.0, 2.0.1, 3.0.0, 4.0.0), history is not
rewritten, all three adopters pin 4.0.0, and platform's own composition selfcheck uses it as the
Deny-inheriting fixture — so retiring it is one change with the next declared line, which ticket
84 owns.

### Item 2 — `verify/proportionality` re-pointed at tier selection

The Audit-versus-Deny derivation is retired and the beat grades the mechanism that ships. Same
workload, same FAIR scenario, same uncaged residual of £21,360 (GBP, the adopter's perspective):
driftwood's signed £40,000 band selects `baseline`, ludlow's signed £5,000 band selects
`quarantine`, because a baseline cage leaves £14,952 and only a quarantine cage gets ludlow under
its band. `render.py` stamps the rung onto a governed Namespace manifest — which is where ADR-0022
put the declaration — instead of stamping an action onto a policy body. Step 4 then runs the
estate's REAL shared cage (`graded/policies/cage-tier.yaml`) over one pod in each Namespace in a
single `kyverno apply` and asserts each comes out with its own rung's tier, PriorityClass, cpu
dial and WAF presence, with `fail: 0`. That is a stronger subject than the bespoke demo policy it
replaces. `policies/`, `control/encrypt-at-rest.tmpl.yaml` and `tests/encrypt-at-rest/` are
deleted, and the beat itself asserts they stay deleted. The hub ships no Deny of its own.

### Items 3 and 4 — the documents

One sentence, dated 2026-09-05, in all four places that disagreed:

* `CONTEXT.md` **Cage** — carries the sentence and points at the register as the state of the code.
* `CONTEXT.md` **Orphan guard** — corrected. It claimed the guard "cages to `isolated`"; it did
  not, and the entry now says what the pair actually does and what is not yet done.
* `CONTEXT.md` **Governed namespace** — "there is no `CREATE` deny any more" is dated true from
  2026-09-05 and marked false for the eight days it was written and wrong.
* ADR-0014 — banner corrected: it said the CREATE deny was superseded on the same day ADR-0022's
  addendum promoted it. Two consequences are voided by name.
* ADR-0018 §4 — dated note.
* ADR-0022 — the "one refusal the doctrine allows" sentence is struck, the addendum rewritten to
  keep its reason and drop its shape.
* NORTH-STAR principle 2 — its forward reference to this ticket is replaced by what was built.

### Decisions

**D1 (delegated). Every Deny gets a recorded choice in a register a check grades, not a
one-off sweep.** The ticket asks for an inventory; an inventory is a document, and this repository
has just spent eight days with a document that said a Deny was gone while the code shipped it. A
register the gate joins to the trees on every run cannot drift, and it goes red when the excuse
expires rather than when someone next reads it.

**D2 (delegated). `governed-namespace-requires-claim` is re-expressed, not retired, and the rung
is the BOTTOM one rather than the Namespace's declared tier.** A pod that claims nothing is
reached by no served policy version, so the ladder cannot place it; what the ladder cannot place
goes to the bottom, which is the same fail-closed rule that gives an untiered Namespace
`isolated`. Retiring the rule instead would restore exactly the hole ADR-0022 promoted it to close.

**D3 (delegated). ADR-0020's missing-instrument refusal does not reach admission.** ADR-0022 used
it to justify the Deny: "the claim is what selects which served version cages the pod, so without
it there is no cage to put the workload in". A missing instrument refuses to emit a PRICE; it has
never refused a workload. The bottom rung needs no version claim to select it, so there was a cage
all along. ADR-0020 is unchanged in its own domain.

**D4 (delegated). The governed-namespace cage stays `CREATE` only, on a new reason.** ADR-0014's
reason — an `UPDATE` deny would refuse the currency controller's de-posture patch — is void,
because a mutation refuses nothing. The new reason: on that `UPDATE` this mutation would begin
matching a pod `cage-tier` had been caging and would inject a `waf-sidecar` into an immutable
container list, and the API server would reject the patch. That is the cage becoming a refusal by
another name, the exact failure ticket 26 observed live on 2026-08-28. A de-postured pod is caged
when its controller recreates it, which CONTEXT.md's **De-postured** entry already says.

**D5 — WITHDRAWN 2026-09-05, it was wrong, and the review caught it.** It read: "the orphan guard
is demoted to `Audit` rather than paired with a second mutating policy", on a measurement showing
two mutating policies producing a pod labelled `isolated` carrying `cage-baseline`'s PriorityClass.
The measurement was taken against `graded/policies/cage-tier.yaml`, which matches ANY claim and
which `graded/up.sh` says in its own header it never applies — "applies ONLY the rendered,
versioned copies". It measured a configuration that exists nowhere. Every SERVED `cage-tier`
carries `only-this-policy-version`, so it never sees an orphan pod and the contention cannot
arise. The consequence of the error was not academic: demoted alone, an orphan claim ran with no
tier, no caged marker, no PriorityClass, no limits, no hardening and no NetworkPolicy — the
"Namespace fell closed, pod fell open" hole ADR-0022 promoted the other guard to `Deny` to close,
re-opened through this one, and selectable by any pod that claimed a bogus version, which is a
self-service exemption principle 1 bans.

**D5b (delegated, replaces D5). The demotion ships WITH a cage that reaches an orphan claim.**
`policy-version-orphan-cage`, a MutatingPolicy ranged from the same array, matching claims NOT in
it. The same version scoping that made D5 wrong makes the pair safe: the served cage takes claims
in the array, this one takes claims not in it, disjoint by construction, so the two mutations
never contend for a field. `verify-orphan-guard.sh` proves the disjointness by running both bodies
over the same three pods and asserting each pod's label agrees with its dials. Folding the
bottom-rung selection into `cage-tier`'s own `tier` expression is still tidier and is still ticket
84's, because that is a versioned policy body.

**D6 (delegated). The `Audit` report stays, and for the governed-namespace rule it had to be
BUILT.** "Never count" bans the exemption ledger, not measurement; `require-nonroot` has shipped
`Audit` in every version line throughout, which settles that the shape is sanctioned. The report
is the observation an orphan claim's priced hole rests on. The first cut claimed the same of the
governed-namespace rule — "the guard drops to `Audit` so silence is still observed" — and that was
never true of the code: the ValidatingPolicy was REPLACED by the mutation, so nothing observed an
unclaimed pod at all. `governed-namespace-unclaimed-report` is rendered beside the cage now. A
mutation and a report do not contend for a field, which is why this pair is safe where two
mutations would not be.

**D7 (delegated). The adopters' composed copies are NOT hand-edited.** They are composed against
platform's pinned, signed tag `v2.0.1`. Editing them by hand would forge a composition against a
tag that does not carry it — the same class of thing as faking a signature. They change when the
owner merges the platform branch, `cut-release.yml` cuts the next tag and each adopter's pin bump
re-composes. The check names that and exits 3.

**D8 (delegated). `verify/proportionality` is re-pointed, not deleted.** The ticket allowed
either. The comparison is the talk's load-bearing beat, and the same two signed bands select two
different rungs through `cage.py select_tier`, which is a real shipped mechanism with a real
subject — so the beat keeps its meaning and gains a stronger proof.

**D9 (delegated). Each renderer's `--selfcheck` now asserts that `versions.yaml` renders the same
document it does.** Found while doing the work: both offline twins carried the
`policy-as-versioned.dev/policy: platform-machinery` identity label and neither copy in the live
ResourceSet template did, with nothing comparing them. That silence is how the 2026-08-28
`Audit -> Deny` promotion came to be made by hand in two places. `distribution/resourceset.py`
reads the template; the drift is fixed and cannot come back unobserved.

### What the run observed, and what it did not

* The platform beats ran green on this machine with kyverno 1.18.2: the unclaimed pod is admitted
  and fully caged, the orphan is reported and not reported-on-the-declared-version, and the same
  orphan pod comes out of `cage-tier` with its Namespace's tier.
* `verify-orphan-guard.sh` names its own ceiling rather than claiming past it. The pinned CLI
  evaluates a CEL `ValidatingPolicy` identically under `Audit` and `Deny` — same verdict spread,
  same exit code, `--audit-warn` included — so the action is proved structurally and whether the
  API server ADMITS the orphan pod is left to `verify-graded.sh`'s cluster tail. The old beat read
  the denial off the exit code, and the exit code never carried it.
* `verify-proportionality.sh` passed with both live tails, because `kind-driftwood` and
  `kind-ludlow` exist on this machine. On the scheduled runner it exits 3 with all three reasons
  declared in the manifest.
* Platform's `compose/composition.py --selfcheck` fails identically on untouched `origin/main`
  (`assert document["party_artefact_errors"] == []`, line 3427), so it neither validates nor
  invalidates this change. Not this ticket's red. `_load_guards` and `render_member` were driven
  directly instead: the kind change flows through, and the composed governed-namespace member
  carries no `validationActions` and no `Deny`.

Map line: `- [89 — Deny is not a rung: the mutating controller](issues/89-deny-is-not-a-rung-the-mutating-controller.md) — three Deny-shaped rules, not two, each with a recorded choice in verify/deny-is-not-a-rung/register.yaml that the gate joins to the trees on every run and refuses to let drift; the two machinery guards become six documents that refuse nothing (orphan guard Audit + orphan cage, governed-namespace cage + unclaimed report, bottom-rung netpol, and the unsuffixed cage-isolated PriorityClass without which the Priority plugin would refuse every pod they cage); posture-trust-boundary retires at ticket 84's next declared line because stamp-posture already is the boundary; verify/proportionality grades tier selection (£21,360 uncaged: baseline in driftwood, quarantine in ludlow) and ships no policy body; CONTEXT.md, ADR-0014, ADR-0018 §4, ADR-0022 and NORTH-STAR carry one dated sentence and ADR-0022's "one refusal the doctrine allows" is struck. Three rounds, each fixing a defect of the same shape found only by running the thing: round 1 shipped a real regression — the demotion alone left an orphan claim uncaged, because every served cage-tier is version-scoped — and the review caught it; round 2's UPDATE arm was itself a third refusal by another name that would have broken ticket 91's recage patch (split into labels-only hold policies, measured against the real patched object), and round 2's allow-list allowed an UNCUT version no cage serves (now cut elements only); round 3's register prose still described round 2 and repeated the claim round 3 disproved, and the UPDATE hold asserted labels on pods it had never caged (both fixed; the hold gates on oldObject now, so it re-asserts); adding a claim to a running bottom-rung pod is refused by the API server and that is DECIDED as correct, with recreate as the remediation, recorded in CONTEXT.md and as ticket 98's one live instance. All four defects reason from a PROXY for the served thing -- an unapplied artefact, a label whose name implies a provenance it lacks, a file's existence for a cage's service, prose for code -- and the rule is that every safety claim names the SERVED artefact and the OPERATION that reaches it and is measured against both, which the estate can only half do today. The fixes and the findings are in the ticket -- the sharpest being that every served PriorityClass is version-suffixed, so the machinery's own cage named a class no cluster has and would have made every pod it caged inadmissible: a refusal by another name, inside the ticket about refusals by another name, invisible to every static check here and now named in deny_register.BLIND_SPOTS as wanting a ticket of its own. Disjointness is proved from the array. Three clock observations were lost, and the cause is the clock: truth.yml rebases a branch onto main and then pushes to the branch, which can never fast-forward once the branch has diverged -- run 98 was rejected with the tip unmoved and nobody pushing. So a TRUTH line produced on a ticket branch normally never lands, and the brief now says rebase onto main rather than merge it, which is the opposite of what this build first wrote. All three lines are quoted in the ticket from the Actions logs and none is written into truth.log. The 21 served copies wait on the platform branch, a signed tag and three pin bumps, named by the check.`

### Round 2, 2026-09-05 — the review found five blocking findings and the central one was real

The first cut of this ticket shipped a safety regression. It is recorded here rather than quietly
fixed, because the register's whole purpose is that the record cannot drift from the code.

**F1 (central).** The orphan-guard demotion rested on "every claiming pod is already caged by
`cage-tier`". False of the served estate: every served copy carries `only-this-policy-version`,
and an orphan claim is by definition a version no served line carries. Fixed by D5b above: the
demotion now ships with `policy-version-orphan-cage`. Every document that said an orphan claim is
caged by `cage-tier` — the register row, the renderer docstring, CONTEXT.md's Orphan guard entry
and ADR-0022's amendment — says what is true instead.

**F2.** `verify-orphan-guard.sh` step 3 proved the cage with `graded/policies/cage-tier.yaml`, an
unserved authoring artefact that matches any claim, so the beat passed while proving nothing about
what runs. It reads the SERVED body now, and the step it proves is inverted: the served cage does
NOT reach the orphan pod, which is the fact the new cage exists for.

**F3.** Two of three live register rows misstated the code on the day they were written. Both are
rewritten to describe what was built, and the governed-namespace row's missing observation is now
a real object.

**F4, F9.** CONTEXT.md's Orphan guard entry replaced one untrue sentence with another; it now
states what the served policies do, and records both errors. The Governed namespace entry
distinguishes source from served, as the four ADRs already did.

**F5.** `verify-retirement.sh`, untouched by round 1, still made a denial its subject and its pass
line, and went green anyway because the pinned CLI reports a rule failure identically for `Audit`
and `Deny`. Its subject is now "retiring a version moves a straggler out of every served policy
version onto the bottom rung", and it proves the cage. `verify-declared-versions-admit.sh`'s
header carried the same stale premise and is corrected.

**F6.** `CREATE`-only left a caged pod permanently relabelable out of `cage-reach-isolated`. Both
cages match `UPDATE` now, gated on the pod already carrying `posture.acme.io/caged: "true"`, which
keeps the de-posture patch legal at the same time.

**F7.** `cage-tier` maps `object.spec.containers` only, so a privileged `runAsUser: 0`
initContainer rode in with the newly admitted pod. `cage_body.py` extends the same tighten-only
hardening to `initContainers`; `runAsUser: 0` survives beside `runAsNonRoot: true`, so the kubelet
refuses to start that container and the pod is admitted, caged and does not run — the doctrine's
own permitted outcome, named in the module rather than left to be found. The hostPath escape is
NOT closed and is named: ADR-0022's own ponytail already carries it for `cage-tier`'s population,
and it needs a price or a volume-level mutation, neither of which is this ticket's.

**F8.** `cage-netpol` is version-scoped in every served copy, so neither population got a
NetworkPolicy and "a running cage with no ingress and no egress" was untrue of exactly the pods
this ticket creates. `render-bottom-rung-netpol.py` renders `cage-netpol-bottom-rung` from
`cage-netpol`'s own body with the version scoping replaced by "claims no served version".

**F10, F11, F12.** `origin/main` merged in (the branch was six commits behind and
`verify-truth-line.sh` was red on ticket 64's four new manifest rows); the script count is read
from the run, not typed; the dead `want_absent()` is gone.

**The scan's blind spots** are now a declared constant, `deny_register.BLIND_SPOTS`, printed on
every run and held non-empty by a test. Four of the reviewer's plants are fixed with tests that
were red first — a `.json` policy, a one-line flow mapping, a multi-line flow sequence, and
`validationFailureActionOverrides` — and the exploitable one is closed: name attribution was
positional and unbounded, so a document whose `metadata:` follows its `spec:` inherited the
previous document's name, and a second Deny appended to a file a row's globs already covered read
as accounted for. Attribution is bounded to its own document now, backwards then forwards. What
stays unseeable is stated: a YAML anchor, a template engine's conditional arm, an action computed
at admission, and a refusal by another name.

**A sixth defect the review did not name, found by RUNNING the policy rather than reading it —
and it is the strongest evidence this build produced.** `distribution/policies/v4.0.0/
priorityclasses.yaml` ships `cage-baseline-4-0-0`, `cage-restricted-4-0-0`,
`cage-quarantine-4-0-0` and `cage-isolated-4-0-0`: every one version-suffixed, because the
version tree is the only thing applied. These machinery cages belong to no version and have no
suffix to borrow, so the plain `cage-isolated` they named exists on no cluster — and the Priority
admission plugin rejects a pod naming a PriorityClass that does not exist.

**This ticket's own cage would have made every pod it caged inadmissible. That is a refusal by
another name, inside the ticket whose whole subject is refusals by another name.** It would have
passed every check here: `verify-deny-is-not-a-rung.sh` sees no Deny-shaped text in a
MutatingPolicy, because there is none; the selfchecks compared the body to `cage-tier`'s and it
matched, because the authoring copy is exactly where the unsuffixed name comes from. Nothing in
the estate's static surface could have caught it. It surfaced only because the beat ran the two
bodies together and asserted the served pod's PriorityClass, which came out `cage-quarantine-4-0-0`
where the assertion expected `cage-quarantine`.

The fix: the machinery renders the unsuffixed class as a sixth document and a composed member,
and `cage_body.assert_priorityclass_is_rendered()` ties the pinned tier's `pc` and `prio` to it in
both renderers' selfchecks, so unpinning the tier or renaming the class fails offline instead of
on a cluster.

**This needs to become someone's ticket.** `deny_register.BLIND_SPOTS` now says a refusal by
another name is graded by nothing, and names the two instances the estate has produced: ticket 26
on 2026-08-28 (a `waf-sidecar` appended twice, so every `UPDATE` to a caged pod was rejected) and
this one on 2026-09-05. Both were found by running a policy; neither was findable by reading one.
A check that grades it would have to admit a pod through a real API server and observe that it was
admitted — which is `verify-graded.sh`'s live tail, and that has never had a cluster on a citable
run (review finding P2-6). Naming the two together is what makes the case; the ticket is not
written here because charting is not this ticket's, but nothing else in the record puts the two
instances side by side.

### Round 3, 2026-09-05 — the UPDATE arm was a third refusal by another name

Round 2's fix introduced its own defect, of exactly the class this ticket is about, and the
review caught it before it merged.

**R1 (central). The `UPDATE` gate was not what I thought it was.** I matched `UPDATE` on
`posture.acme.io/caged == "true"`, reading that marker as "caged by this policy". It is not:
`cage-tier` writes it for its whole population at every rung. So the bottom-rung cage matched a
pod `cage-tier` had caged at `baseline`, and applying the full body to a RUNNING pod appends a
`waf-sidecar` to an immutable container list and rewrites `priorityClassName` and `priority`.
The API server refuses that. **A refusal by another name, in the ticket about refusals by
another name, and the third instance in this estate.**

It was not theoretical. Ticket 91's `recage_patch()` is an `UPDATE` that strips the claim and
writes `tier: isolated` + `caged: "true"` in one merge patch — the estate's only mechanism for
moving a running pod off a retired version — and its patched object matches both my gates
exactly. Ticket 91 merged to platform `main` while this branch sat behind it, and its own words
in the file I was editing say `UPDATE is excluded on purpose, so the currency-controller's
re-cage patch keeps working`. I had never read them, because the branch had not merged them, and
the conflict lands in precisely those lines. The collision was invisible from inside either
branch.

**The fix, and why the obvious narrowing does not work.** Gating on
`tier == 'isolated' && caged == 'true'` fails too: that is exactly what `recage_patch()` writes.
`UPDATE` needed the LABELS re-asserted, not the cage re-applied — which is all `UPDATE` was ever
wanted for (stopping a post-creation relabel escaping the reach cage). So the two jobs are split:
the cages keep `CREATE` and the full body, and two labels-only `MutatingPolicy`s
(`governed-namespace-cage-holds`, `policy-version-orphan-cage-holds`) take `UPDATE` and write
`tier` and `caged` and nothing else. They append no container, rewrite no immutable field, are
byte-identical for an already-correct pod, and are admissible on top of `recage_patch()`, which
writes the same two values.

**Measured, and now graded.** `verify-governed-namespace-guard.sh` step 5 builds the object
`currency.recage_patch()` actually produces, on a pod admitted at `baseline`, and runs it through
the `UPDATE`-scoped policies: container list unchanged, `priorityClassName` still
`cage-baseline-4-0-0`, `priority` still `-10`, both labels held. The step names its own ceiling:
`kyverno apply` has no `UPDATE` mode, so operation scoping is proved structurally and the
mutation content functionally — feeding it the `CREATE`-scoped cages would measure a
configuration the API server never produces, which is the round-1 mistake in a new place.

**R2. The name-attribution fix closed one route and opened an easier one.** Widening the name
regex from a `match` to a `search` made a `- name:` inside `matchConditions`, `variables` or
`validations` readable as the document's own name. The reviewer planted a Deny called
`block-all-images-from-anywhere` whose only camouflage was
`matchConditions: [{name: posture-trust-boundary}]` sitting between the real metadata name and
the `validationActions` line, appended to a path the register's globs already declare: the
inventory called it an accounted-for copy of `posture-trust-boundary` and the check returned its
normal SKIP. Attribution now prefers the parsed `metadata.name`, and only where the parsed
document ITSELF carries the shape — a ResourceSet parses cleanly and would otherwise lend its own
name, `composed`, to the three Denys inside its template string. Where nothing parses, the
shallowest non-list `name:` in the region wins, and the region is bounded to the enclosing block
scalar and its nearest `---`, indented separators included. Five tests, red first, including both
plants end to end.

**R3. The completeness leg tested that a FILE exists, not that a cage is SERVED.** `5.0.0` is
declared with no `commit`, so it sat in the allow-list — the orphan cage skipped it, the report
did not report it — while no `cage-tier-5-0-0` is installed anywhere. A pod claiming it ran
caged by nothing, selectable by anyone who read `versions.yaml`: **round 1's defect in a new
place, and I had written the completeness leg that was supposed to catch it.** The allow-list
ranges over CUT elements only now, reusing `verify-declared-versions-admit.sh`'s own
`partition()`, and the selfcheck asserts every uncut declared version is in the orphan
population. One honest consequence, not hidden: with a single cut version, `verify-retirement.sh`
is back to the offline refusal ticket 63's second declared version had retired, and the manifest
row says so and says it lifts when a second TAG is cut, not when a second version is declared.

**R5.** `cage-netpol-bottom-rung` wrote the served generator's downstream names. Two owners for
one downstream name is what `DeleteDownstreams` wiped across namespaces on 2026-08-28. It has its
own names now (`cage-reach-bottom-rung-*`) with the same podSelector, so the reach is identical
and neither generator can delete the other's objects.

**R6, R7.** The withdrawn round-1 premise is gone from `render-orphan-guard.py`'s `ACTION`
comment. The report stays `CREATE`-only and says why: its subject is ARRIVAL, and an
`UPDATE`-scoped report would fire on every relabel and loudest of all on `recage_patch()` — the
estate working correctly — while PolicyReports are what the priced hole is computed from, so
repeating one event would double-count it. `BLIND_SPOTS` gains Gatekeeper's
`enforcementAction: deny`, the 2022 `rules[].validate.deny{}` block, and a webhook's
`failurePolicy: Fail`.

**R4.** Both branches are REBASED onto their mains, not merged — this ticket's own new brief rule.
ADR-0014's conflict is resolved on the merits: ticket 91's amendment is kept whole and ticket 89's
is added dated beside it, agreeing with it, and saying in terms why the `UPDATE` arm was wrong.

**Three defects of mine, three rounds, all the same shape.** Round 1 reasoned from an artefact
that is never applied. Round 2 reasoned from a label that does not mean what its name suggests,
and tested a file's existence instead of a cage's service. Each was invisible to every static
check here and each was found by running the thing. That is the case for
`deny_register.BLIND_SPOTS`'s first entry becoming somebody's ticket, and it is now three
instances, not two.

### Round 4, 2026-09-05 — the record was the fourth proxy

**S1 (blocking). The register still described the round-2 design, and repeated as its
justification the exact claim round 3 disproved.** The governed-namespace row said "`CREATE` plus
`UPDATE`, the `UPDATE` arm gated on the pod already carrying `posture.acme.io/caged: \"true\"` ...
without the gate the mutation would inject a sidecar into the de-posture patch's immutable
container list and the API server would refuse it". The gate was removed *because it did not
prevent that injection* — it caused it. Neither hold policy appeared anywhere in the file, and
both rows cited a commit the rebase had already replaced. `CONTEXT.md` carried the same stale
sentence. ADR-0014 was correct, which is what makes this an oversight and not a decision.

Both rows and the `CONTEXT.md` sentence now describe what was built: a `CREATE`-only full-body
cage, a separate `UPDATE`-only labels-only hold over the same population gated on `oldObject`,
and why the split exists. Both drafts of the governed row that were wrong are named in it, with
what each got wrong, because this ticket's Done clause is that the documents agree and the
register's whole purpose is that it cannot drift from the code.

**S2 (major). The hold asserted where it should have re-asserted.** Its predicate matched the
cage's; its extension did not. On `UPDATE` it matched any unclaimed pod whether or not the cage
had ever caged it — so a pod `cage-tier` caged at `baseline` whose claim was later removed came
out labelled `tier: isolated` over a baseline spec, and a pod nothing had ever caged gained both
labels with no dials at all. Reach only tightens, so it was not a safety regression; but it
inverts the invariant `cage-tier`'s own header states ("the pod label is an OUTPUT only"), and it
is the same label-and-dials incoherence D5 gives as the reason a second mutating writer was
rejected. Writing a label that promises dials the pod does not carry is the thing the estate
refuses to do.

Both holds now gate on `oldObject` already carrying the bottom rung. F6 is delivered in full,
because the relabel case starts from a pod the cage put at `isolated` and `oldObject` is what
sees through the forged incoming label. The populations it deliberately stops touching are all
`CREATE`-time or recreate problems and each is reachable: a Namespace that gains
`governed: "true"` after its pods exist, a pod created while the webhook was down, a claim
stripped by anything other than the currency controller.

That gate is invisible to `kyverno apply`, which has no `UPDATE` and cannot populate `oldObject`
— so step 5 would have passed because *nothing applied*. It strips the gate on a throwaway copy
before measuring what the mutation writes, exactly as it already strips `namespaceSelector`, and
says so; the gate's shape is asserted structurally instead.

**S3 (major, decided rather than fixed). Adding a claim to a running pod is not a remediation.**
A pod the cage put on the bottom rung can be labelled with a served version, at which point
`cage-tier` takes it over: measured, `tier: isolated -> baseline`, `priorityClassName:
cage-isolated -> cage-baseline-4-0-0`, `priority: -10000 -> -10`, and both spec fields are
immutable on a running pod, so the API server refuses the edit.

**Decision (delegated). The refusal is the correct outcome and is not worked around.** The
alternative — letting the edit through — is a workload moving itself off the bottom rung by
asserting a label, which is the self-service exemption principle 1 bans. A pod's cage is written
at admission from what it declared then, so the way into governance is to declare the claim and
let the controller recreate the pod, which is the route `CONTEXT.md`'s **De-postured** entry
already describes. It is in `CONTEXT.md` in those terms, and because the API server refuses while
no policy denies, it is recorded as a LIVE instance of a refusal by another name — in
`BLIND_SPOTS` and on ticket 98, which owns grading that class. It is the one instance of the four
that is in the estate right now rather than replayable only as a fixture, and a check that went
red on it would have caught the other three.

**S4, S5.** Step 1's `say` line announced "CREATE plus UPDATE-when-already-caged" while the
selfcheck below it asserted `["CREATE"]`. `verify-retirement.sh`'s own skip said "declares one
version" where the array declares two of which one is cut; it says that now, and says it lifts
when a second TAG is cut. The bottom-rung generator emitted all three restricting rungs, two of
them byte-identical duplicates of the served generator's objects; its population is pinned to
`isolated`, so it ranges the bottom rung only.

### What all four defects have in common

In the reviewer's words: each reasons from a **proxy** for the served thing instead of the served
thing — an authoring artefact that is never applied; a label whose name implies a provenance it
does not carry; a file's existence standing in for a cage's service; and the register's prose
standing in for the code. Each proxy is cheap to read and each is checkable by something already
in the repository, so the reasoning never has to leave the repository.

The rule that would have caught all four: **every safety claim must name the SERVED artefact and
the OPERATION that reaches it, and be measured against both.**

And the honest limit on that rule, which is the estate's and not this ticket's: it cannot
currently do the second half. `kyverno apply` has no `UPDATE` mode, and no cluster has run these
policies on a citable run (review finding P2-6). So three of the four were catchable only by
READING, and the fourth only by RUNNING — and the one that is live today (S3) is catchable by
neither, until ticket 98 builds the check.

In my own words: I kept proving things about the estate I could reach from a text editor, and
every time the thing that was actually served differed from it. The proxy was never wrong by
much. It was wrong in the one direction that mattered each time.

### Three observations were lost, and the clock is why, not the pushes

Three `truth` runs on this branch produced a TRUTH line and none of the three reached
`talk/truth.log`. I got the reason wrong twice on the way to it, and both wrong answers are left
here because the second one nearly shipped as advice to the next builder.

First I wrote that no observation was lost. Then, re-reading the logs, that one was lost to
`origin/main` moving and a second to my own push — I had pushed while runs were in flight, reading
the top rows of `gh run list` instead of the `status` column, which is a real rule violation and
mine. Then run 98 settled it: **it was rejected with the remote tip unmoved and nobody pushing at
all.** That is the controlled case, and it says the cause is structural.

**`truth.yml` cannot land an observation on a branch that has diverged from main.** After writing
its line it commits and runs `git pull --rebase --autostash origin main`, then pushes to the
BRANCH. On `main` the rebase is a no-op and the push fast-forwards. On a ticket branch it rewrites
every commit, so the result is not a descendant of the branch's own remote ref and the push is
refused non-fast-forward. My push made run 95's tip move as well, but run 98 shows the rejection
arrives without it.

All three lines are quoted below from the Actions logs. None is written into `talk/truth.log`: a
builder does not author a clock's observation, and a line hand-copied there would be
indistinguishable from one the clock landed.

**The first: `origin/main` moved.** Run 92, on hub commit `c28541e`
([Actions run 33936905680](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/actions/runs/33936905680)),
produced this line at 2026-09-05T02:03:57Z and it never reached `talk/truth.log`:

```
TRUTH 2026-09-05T02:03Z run=92 hub=c28541e units=[driftwood=a1a2a78@main feeds=b6eaa0a@main ico=6217c3a@main insurer=9e90e1b@main ludlow=d092400@main nist=b9f5fff@main platform=bbda376@main tuppence=fca6a58@main] pass=65 [observed=15 self=40 simulated=6 meta=4] fail=13 skip=19 [never=10 waits=9] excluded=8 total=105 ceiling=86
```

**Why it did not land.** The workflow committed it as `5c75197` and then ran
`git pull --rebase --autostash origin main`. It rebases onto **origin/main**, not onto the branch
it is running on. `origin/main` had moved while the run was in flight — ticket 64's merge, the
`--refresh` fix, and run 94's own `talk/truth.log` entry — so replaying eight branch commits onto
it conflicted in `talk/truth.log` and in three `talk/captures/*.out` files, and the rebase stopped
at `error: could not apply 5c75197... truth: record run 92 [skip ci]`.

**That one was not my push.** The rebase failed at 02:04:28Z; my next push to the branch
(`d961091`, the merge of `origin/main`) is 41 minutes later. Two other runs my pushes DID cancel
— on `26eb5ac` and `602cda3` — were cancelled before reaching a TRUTH line, so neither produced
an observation to lose; their logs carry no `TRUTH` line at all. Checked, not assumed. The remedy
is in this branch by accident: merging `origin/main` in (F10) is what stops a branch's rebase
conflicting with main's `truth.log`, and a branch that sits behind main will keep losing
observations this way. That is a property of `truth.yml`, not of this ticket.

**The second: rejected, and I had also pushed.** Run 95, on hub commit `f91c0f6`
([Actions run 33941571076](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/actions/runs/33941571076)),
produced this line at 2026-09-05T03:44:07Z:

```
TRUTH 2026-09-05T03:44Z run=95 hub=f91c0f6 units=[driftwood=a1a2a78@main feeds=b6eaa0a@main ico=6217c3a@main insurer=9e90e1b@main ludlow=d092400@main nist=b9f5fff@main platform=bbda376@main tuppence=fca6a58@main] pass=68 [observed=16 self=40 simulated=6 meta=6] fail=6 skip=24 [never=10 waits=14] excluded=8 total=106 ceiling=87
```

It committed as `10a495c` and the push came back
`! [rejected] HEAD -> ticket-89-deny-is-not-a-rung (non-fast-forward)`. The tip HAD moved to
`91bd500`, which I pushed at 03:21Z about a minute after that run started at 03:20:18Z — the
failure the build brief warns about, in the shape it warns about it, with the warning in front of
me. I recorded it as my fault, and the rule violation was mine. Run 98 then showed the rejection
happens with no push at all, so the push was not what cost this line. The observation is gone
either way: the next run measures a different tree.

It is worth saying what was lost, because it was the best number this branch has produced:
`pass=68 fail=6 skip=24 of 106, ceiling 87`. It is quoted here so the work is not invisible, and
it is NOT a citable line — no run recorded it in `talk/truth.log`, so nothing may cite it.

**The third, and the controlled case: nobody pushed.** Run 98, on hub commit `11f156f`
([Actions run 33942739871](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/actions/runs/33942739871)),
produced `TRUTH 2026-09-05T04:29Z run=98 hub=11f156f ...`, committed it as `3c6a442`, logged
`Rebasing (12/12)` and `Successfully rebased and updated refs/heads/ticket-89-deny-is-not-a-rung`,
and was then refused: `! [rejected] HEAD -> ticket-89-deny-is-not-a-rung (non-fast-forward)`. The
remote tip was `11f156f` throughout and I pushed nothing after it. Twelve commits rebased onto
`origin/main` cannot fast-forward a ref that still points at the un-rebased twelfth.

**Confirmed by the fix working.** Run 100 LANDED on this branch — the first observation it has
ever recorded — and it landed because the branch had been REBASED onto `origin/main` (round 3,
R4) rather than carrying a merge commit, so the workflow's `git pull --rebase origin main` was a
no-op and its push fast-forwarded. That is the rule the brief now carries, verified by an
observation arriving rather than by argument:

```
TRUTH 2026-09-05T13:51Z run=100 hub=e40852c units=[driftwood=96f4d0d@main feeds=b6eaa0a@main ico=6217c3a@main insurer=9e90e1b@main ludlow=d40b3fb@main nist=b9f5fff@main platform=ea9b2ee@main tuppence=c0e37e0@main] pass=68 [observed=16 self=40 simulated=6 meta=6] fail=6 skip=24 [never=10 waits=14] excluded=8 total=106 ceiling=87
```

**So the finding is about the clock, and one piece of my own advice was backwards.** I had written
into the build brief that merging `origin/main` into a ticket branch removes the loss. It does the
opposite: the merge commit (`d961091`) is what guarantees the rebase rewrites history, and so
guarantees the rejection. The brief now says **rebase onto `origin/main`, do not merge it** — a
branch whose commits already sit linearly on current main rebases to a no-op and its runs can
land. Not pushing during an `in_progress` run stays a rule, as a separate way to lose the same
thing.

The consequence worth someone's attention: **a TRUTH line produced on a ticket branch normally
never lands, so branch runs are not a record of anything.** Only `main` accumulates observations.
Nothing in the estate says so, and three lines were lost here before it was visible. Both halves
are in `.scratch/ecosystem/BUILD-BRIEF-2026-09-03.md` under the rules that do not bend, which is
where the next builder looks.

**Composition** carries the three new policy members and the PriorityClass, read defensively so an
adopter pinned to a parent tag from before this ticket composes exactly what it composed then.

## Waits on the owner

1. **Merge platform branch `ticket-89-deny-is-not-a-rung`** (commits `af7d87d` and `bd9e919`;
   eleven files under `distribution/` and `compose/`). Nothing in this ticket reaches a cluster
   until it is on platform `main`.
2. **Dispatch `cut-release.yml`** to cut the next signed platform tag. Only the owner dispatches
   it, and no agent fakes a tag. Until that tag exists the three adopters keep composing the old
   Deny from `v2.0.1`, and `verify-deny-is-not-a-rung.sh` exits 3 naming it.
3. **Let each adopter's Renovate pin bump land** (driftwood, tuppence, ludlow), which re-composes
   `composed/orphan-guard.yaml`, `composed/governed-namespace-guard.yaml` and
   `gitops/composed/composed-set.yaml`, and writes four NEW files per adopter
   (`orphan-cage.yaml`, `governed-namespace-report.yaml`, `bottom-rung-netpol.yaml`,
   `bottom-rung-priorityclass.yaml`). That is 11 of the 21 outstanding copies.
4. **Each adopter's `scripts/render_composed.py` needs the new machinery files added to its
   object list.** It hardcodes `paths = ["composed/orphan-guard.yaml"]` and does not list the
   governed-namespace guard either, so fact 4 of the five-fact sample would compare a set that
   omits them. That is an adopter-repo edit, and adopter repos are the owner's to push.

The remaining 10 are `posture-trust-boundary` and wait on ticket 84's next declared line, not on
the owner.

## Not done

* `posture-trust-boundary` is recorded, not removed. See D2 and the item-1 table above, and ticket 84.
* An orphan claim gets the bottom rung from a policy BESIDE `cage-tier` rather than from
  `cage-tier`'s own `tier` expression. D5b says why and names ticket 84 as the owner of the
  tidier form.
* The hostPath escape (F7) is not closed: an isolated pod can still mount the node filesystem,
  bounded only by the forced `runAsNonRoot`. ADR-0022's own ponytail already carries this for
  `cage-tier`'s population; it needs a price or a volume-level mutation.
* A refusal by another name is graded by nothing, and this ticket produced the second instance
  itself. `deny_register.BLIND_SPOTS` says so on every run and names both. **This wants a ticket
  of its own**, and it is not written here because charting is not this ticket's: the check would
  have to admit a pod through a real API server and observe that it was admitted, which is
  `verify-graded.sh`'s live tail, and that has never had a cluster on a citable run (P2-6).
* No cluster ran the converted policies. `verify-graded.sh`'s live tail is where that is observed,
  and it has never had a cluster on a citable run (review finding P2-6, still open). One thing WAS
  observed on a real API server: `kubectl --context kind-driftwood apply --dry-run=server` accepts
  a pod carrying `initContainers: null`, which is what the initContainer mutation writes on a pod
  that declares none.
* `verify-graded.sh` itself is not extended to the two new populations. It grades `cage-tier`'s
  claiming population on a cluster; nothing yet drives an unclaimed or orphan pod through a real
  API server, which is the only place the PriorityClass and NetworkPolicy facts above become
  observations rather than renders.
