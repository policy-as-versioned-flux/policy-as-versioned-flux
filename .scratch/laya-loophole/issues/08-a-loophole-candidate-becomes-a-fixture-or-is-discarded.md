# 08 — A loophole candidate becomes a fixture, or is discarded

Type: task
Status: resolved
Blocked by: 07

## Question

loophole's output is non-deterministic. Under "derive what you assert" it is a hypothesis, never a
finding. Resolve every candidate ticket 07 produced.

For each candidate, do one of two things:

1. Write a deterministic check that reproduces it. The check is the finding. The candidate was
   only the pointer.
2. Discard it, with a one-line reason.

A candidate that survives lands in the misuse catalogue through a reviewed pull request.

Record the survival rate.

**Added 2026-09-21, from ticket 06.** loophole carries no licence. Do not commit its source, its
prompts, or a paraphrase of its prompts into the estate. A surviving candidate enters the misuse
catalogue as **our own** fixture, written from the scenario it describes, not as copied text.

## Done

Every candidate resolved to a fixture or to a recorded discard. A stated survival rate.

## Notes

The survival rate is the honest verdict on the tool. A rate near zero says the tool generates
noise, and that result is as valuable as a rate near one. Do not tune the run to raise it.

**Added 2026-09-21, from ticket 07.** The six candidates are in
[`research/07-loophole-round/candidates.json`](../research/07-loophole-round/candidates.json), keyed
`loophole-1` to `loophole-3` and `overreach-4` to `overreach-6`. Each carries the scenario, the
explanation and the judge's verdict. Five read resolvable and `overreach-5` reads unresolvable.

Two things this ticket must not do. Do not treat the judge's "resolvable" as evidence that a
candidate is real; it is the same non-deterministic model. Do not copy a scenario's wording into a
fixture; write the fixture from what the scenario describes, because loophole carries no licence
and the model's output was produced under loophole's prompts.

Denominator for the survival rate: 6.

## Answer

**Two of six survived. The survival rate is 2/6, 33%.** Both survivors were reframed by the
measurement: neither reproduces the mechanism the model named, and both point at a real hole the
estate did not hold. Four were discarded, each for a stated reason, and three of those four are
false against the code rather than merely unproven.

The two survivors are `tests/test_cage_ladder_holes.py`, nine legs, and two rows in
`twin/ecosystem-misuse-catalogue.yaml` (version 3 to 4). Each row waits on a new eco-system
ticket. No loophole text reached the tree: both fixtures are written from what the scenario
describes, against the estate's own files.

### Survivor 1 — `loophole-2` → `adopter-runs-uncaged-in-the-platform-substrate`

The candidate said a contractor's workloads in an `infra` Namespace inherit "the loosest-
privileged, highest-trust rung". Measured under kyverno 1.18.2, the version `release.yml` pins,
the conclusion is right and every step of the reasoning is wrong.

1. **No served `cage-tier` body contains the word `infra`**, with comments stripped: not the hub's
   v4.0.0 or v5.0.0, not `graded/`, not any adopter's composed copy. There is no `infra` cage.
   The rung is absent from `variables.tier`'s membership test, so an `infra` Namespace falls to
   that test's else branch.
2. **A pod that claims a policy version in the platform's three `infra` Namespaces lands on
   `baseline`** under the body all three adopters serve. `platform/engine/namespaces.yaml`
   declares kube-system, flux-system and kyverno at `infra` and governs none of them by design,
   and v4.0.0's else branch is `nsGoverned ? 'isolated' : 'baseline'`. Measured: 500m/256Mi,
   `priorityClassName: cage-baseline-4-0-0`, priority -10, no hardening, no WAF sidecar. Under
   v5.0.0 the same pod gets `isolated`.
3. **Pulling the declaration changes nothing for CoreDNS.** An unclaimed pod is skipped by
   `cage-tier`'s own matchConditions with the label and without it, under both bodies. That is
   the configuration `distribution/verify-infra-declaration.sh` calls its proof-3 tripwire the
   guard for, in its own words "exactly what stops CoreDNS landing in isolated the moment the
   fail-closed default ships". No served body produces it. The tripwire guards a hazard that does
   not exist, and misses the one that does, which is fact 2.

Graduated as [eco-system ticket 113](../../ecosystem/issues/113-the-infra-declaration-is-read-by-no-served-policy.md).

### Survivor 2 — `loophole-3` → `adopter-silences-its-own-binding-observation`

The candidate said an adopter can freeze a stale loose tier by making its declaration ambiguous,
because a refusal to update is not a fail-closed re-render. Half of that is wrong: each adopter's
own `shift-left.yml` turns the check's exit 3 into a failed pull request by name, so the
ambiguity cannot arrive through a pull request that runs that job. The other half is real, and it
is at the hub rather than the adopter.

`platform/shift-left/tier_binding.py` returns 3, could-not-look, for two governed Namespace
declarations. That is right and ticket 78 built it on purpose. The hub's estate walk then drops
it: `verify/tier-binding/tier_binding_estate.py` prints the party's SKIP line, `continue`s, and
returns `1 if failed else 0`. A skipped party is neither looked at nor failed, so the script exits
0. `talk/verify-all.sh` grades a script by its exit code alone, so the gate reads PASS for an
estate in which one party's cage is unobserved.

Measured on a planted estate of two bound parties built around the real platform checkout: adding
a second governed Namespace document to one gives `SKIP: driftwood`, `PASS: ludlow`, exit 0. The
control, the same estate without the second document, gives two PASS lines and exit 0, so the
exit code is not the walk passing everything.

Graduated as [eco-system ticket 114](../../ecosystem/issues/114-an-unobserved-party-does-not-leave-the-walk-green.md).

### The four discards

- **`loophole-1`** (a team under-declares by never submitting a price line for its sensitive
  workload): **discarded — there is no per-workload price line to withhold.** `prices[]` carries
  one entry per declared feed edge, derived by composition from the party artefact; no workload
  ever appears in one, so the omission the scenario turns on cannot be made. The residual true
  sentence, that the tier is a function of declared edges and not of what runs in the Namespace,
  is ADR-0022's own stated design ("One Namespace carries one tier for every pod in it"), not a
  hole in it.
- **`overreach-4`** (an SRE cannot run network diagnostics in an `isolated` Namespace):
  **discarded — it restates a decision ADR-0022 records with the owner's own reason.** The
  factual half is true: `cage-netpol` gives `isolated` ingress `[]` and egress `[]`. But
  ADR-0022's note of 2026-09-02 states the reason in the owner's words, prices a lowered floor
  rather than refusing it, and says in writing that "Loosening is not implemented, and that is
  the decision, not an omission". `platform/break-glass/` exists and gates a human's session by
  £; it was never a pod's egress.
- **`overreach-5`** (an ungoverned Namespace evicts a benign wiki preview): **discarded — it does
  not reproduce on any served tree, and where it does reproduce it is a ratified decision.** All
  three adopters serve v4.0.0, whose ungoverned branch is `baseline` at priority -10, not
  `isolated` at -10000; measured above. The flip lives in platform v5.0.0, which no adopter has
  re-pinned to, and ADR-0022 decided it in writing: "silence buys nothing anywhere".
- **`overreach-6`** (a non-platform party's `infra` declaration silently renders `isolated` with
  no feedback): **discarded — the render is what ADR-0022 says must happen, and it is not
  silent.** Measured: a governed `infra` Namespace renders `isolated` under both v4.0.0 and
  v5.0.0, which is the entitlement rule working. The binding check names the declared tier in its
  output on every run: `ludlow: gitops/apps/namespace.yaml declares 'infra' ... bound`. The one
  real residual, that the check cannot tell an entitled `infra` from an unentitled one because
  `rank("infra")` is the maximum, is recorded as ticket 113 item 4 rather than as a survivor: no
  workload is under-caged by it today.

### What this says about the tool

One round, six candidates, two survivors that each needed their stated mechanism thrown away and
rebuilt from measurement. The tool did not find either hole. It pointed at two places — who runs
pods in an `infra` Namespace, and what an ambiguous declaration does to the checks — and the
measurement found something real in both. Three of the four discards are false against the code,
not merely unproven, and a reader who trusted the judge's "resolvable" would have carried all
five resolvable candidates forward.

Ticket 11 asks whether a second round finds the same holes. Nothing here answers that: 2/6 is one
draw.

### Side findings

1. **kyverno 1.19.1 cannot compile the served `cage-tier` body.** It rejects the mutation
   expression with `expected type 'string' but found 'dyn'`. The release workflows pin 1.18.2;
   `graded/verify-graded.sh` calls a bare `kyverno` and asserts no version, so the local gate
   cannot state which engine it measured with. It fails loudly rather than quietly, so this is a
   legibility gap, not a false green. `tests/test_cage_ladder_holes.py` asserts the pin and skips
   by name on any other engine.
2. **`.scratch/ecosystem/issues/` holds two tickets numbered 111**, and `twin/misuse.py`
   `ecosystem_ticket_status()` resolves a number with `sorted(glob(...))[0]`. A `waits_on: "111"`
   row therefore reads whichever file sorts first, silently. Tickets 113 and 114 avoid the
   collision; the collision itself is unfixed.
3. **A standing red pre-dates this ticket.** `regulator-data-mispriced-downstream` anchors
   `platform/compose/composition.py::price_supersede`, which that file does not carry, so
   `verify/misuse/verify-misuse.sh` and `tests/test_misuse.py::test_the_four_rows_grade_against_this_checkout`
   are red before and after this change. Confirmed by re-running both against the unmodified
   catalogue.
4. **The eco-system catalogue was closed to new rows by its tests, not by its schema.**
   `tests/test_misuse.py` asserted the entry count and the exact id set. `twin/misuse.py`
   `ECOSYSTEM_ROW_IDS` and `twin/invariants/harness.py` already treated ticket 19's four as a
   subset, so only the tests needed the change, and both added ids name a marketplace party so
   the scope assertion stands unweakened.
