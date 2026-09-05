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
(101 scripts now, was 100), row in `talk/verify-manifest.txt` as `estate-observation | waits:`
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
have reported the estate three refusals cleaner than it is. Measured on the day: 29 Deny-shaped rules
across the hub and the eight units, 8 of them in the two trees the register excludes with a
reason, 21 on the register -- and all 21 still outstanding.

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

**D5 (delegated). The orphan guard is demoted to `Audit` rather than paired with a second mutating
policy.** Measured, not assumed: with `cage-tier` and a second MutatingPolicy writing
`posture.acme.io/tier: isolated` both matching one pod, `kyverno apply` 1.18.2 produced a pod
labelled `isolated` carrying `cage-baseline`'s PriorityClass — the label-and-dials incoherence
H8-03 exists to prevent, arrived at from the other direction. One writer per field, or none.
Selecting the bottom rung for an undeclared claim therefore belongs inside `cage-tier`'s own
`tier` expression with the allow-list ranged in from the version array, which is a versioned
policy body and so a new declared line with the engine's computed bump — ticket 84's. Until then
an orphan claim is caged at its Namespace's tier, which for a `baseline` Namespace is looser than
the Deny was. That is named here rather than left to be discovered.

**D6 (delegated). The `Audit` report stays.** "Never count" bans the exemption ledger, not
measurement; `require-nonroot` has shipped `Audit` in every version line throughout. The report is
the observation an orphan claim's priced hole rests on, and `require-nonroot`'s precedent settles
that the shape is sanctioned.

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

Map line: `- [89 — Deny is not a rung: the mutating controller](issues/89-deny-is-not-a-rung-the-mutating-controller.md) — three Deny-shaped rules, not two, each with a recorded choice in verify/deny-is-not-a-rung/register.yaml that the gate joins to the trees on every run and refuses to let drift; governed-namespace-requires-claim is a MutatingPolicy putting an unclaimed pod on the bottom rung with cage-tier's own body, policy-version-orphan-guard is Audit with cage-tier as the cage and the escaped rules as a priced hole, posture-trust-boundary retires at ticket 84's next declared line because stamp-posture already is the boundary; verify/proportionality grades tier selection (£21,360 uncaged: baseline in driftwood, quarantine in ludlow) and ships no policy body; CONTEXT.md, ADR-0014, ADR-0018 §4, ADR-0022 and NORTH-STAR carry one dated sentence and ADR-0022's "one refusal the doctrine allows" is struck; a second mutating writer was measured incoherent (kyverno 1.18.2) so the orphan's bottom rung waits on 84; the 21 served copies wait on the platform branch, a signed tag and three pin bumps, named by the check.`

## Waits on the owner

1. **Merge platform branch `ticket-89-deny-is-not-a-rung`** (commit `af7d87d`, six files under
   `distribution/`). Nothing in this ticket reaches a cluster until it is on platform `main`.
2. **Dispatch `cut-release.yml`** to cut the next signed platform tag. Only the owner dispatches
   it, and no agent fakes a tag. Until that tag exists the three adopters keep composing the old
   Deny from `v2.0.1`, and `verify-deny-is-not-a-rung.sh` exits 3 naming it.
3. **Let each adopter's Renovate pin bump land** (driftwood, tuppence, ludlow), which re-composes
   `composed/orphan-guard.yaml`, `composed/governed-namespace-guard.yaml` and
   `gitops/composed/composed-set.yaml`. That is 11 of the 21 outstanding copies.

The remaining 10 are `posture-trust-boundary` and wait on ticket 84's next declared line, not on
the owner.

## Not done

* `posture-trust-boundary` is recorded, not removed. See D2 and the item-1 table above, and ticket 84.
* An orphan claim does not select the bottom rung specifically; it takes its Namespace's tier.
  D5 says why and names ticket 84 as the owner of the fix.
* No cluster ran the converted policies. `verify-graded.sh`'s live tail is where that is observed,
  and it has never had a cluster on a citable run (review finding P2-6, still open).
