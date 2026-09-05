# verify/deny-is-not-a-rung — every refusal the estate still ships, and what was decided about it

> *Nothing is denied; a workload that does not fit its cage does not run.*

Eco-system [ticket 89](../../.scratch/ecosystem/issues/89-deny-is-not-a-rung-the-mutating-controller.md).
The owner, 2026-09-02 (ticket 75 Q5): "something could find itself unable to run, but that's only
because it doesn't fit the cage, not because we deliberately deny it. So, in Kubernetes Parlance,
we've built a Mutating admission controller more than a Approving admission and control."

NORTH-STAR principle 2 and `CONTEXT.md`'s **Cage** entry have said that since 2026-08-28. The
served policy did not, and nothing was measuring the gap: the 2026-09-02 review found three
Deny-shaped rules shipping in platform's `ResourceSet`, in every served version directory and in
all three adopters' composed artefacts, while `CONTEXT.md` called one of them "the July record,
superseded" and the gate graded its denial as correct.

## What's here

| file | role |
|------|------|
| `deny_register.py` | the scanner and the grader. `--inventory` prints the inventory the ticket asked for, taken from the trees on the day it runs |
| `register.yaml` | the recorded CHOICE and REASON per rule: re-expressed as a cage constraint, or retired with the engine's computed bump |
| `verify-deny-is-not-a-rung.sh` | the beat in the gate |

## Why it is a check and not a document

An inventory taken once starts rotting the next day. This one is taken on every run and joined to
the register, and the join is graded in both directions:

* a Deny-shaped rule **no register row claims** is a FAIL — an undeclared refusal is shipping;
* a row that says **converted** while a copy survives is a FAIL;
* a row that says a copy survives when **none does** is a FAIL — the record is behind the code;
* a row still marked `waiting` whose **source no longer emits** the Deny is a FAIL — move it on;
* a row with **no reason**, no `awaits`, or a choice that is not one of the ticket's two is a FAIL;
* a row naming a `source_clean` path that **cannot be read** is a FAIL in either state — a
  register that names a file nobody can open is a register nothing can check;
* an outstanding copy is a **could-not-look (exit 3) that names the tag it waits for**, never a
  pass. It goes green when the estate does, and not before.

Two shapes count as Deny-shaped: the CEL `ValidatingPolicy`'s `spec.validationActions` carrying
`Deny` (ADR-0003) and the 2022 `ClusterPolicy`'s `validationFailureAction: enforce`.

Measured 2026-09-05, after the scan was widened to JSON and to the flow and override forms:
36 Deny-shaped rules across the hub and the eight units, 15 of them inside the four trees
`register.yaml` excludes with a reason, 21 on the register — and all 21 still outstanding, across
three rules. Run `--inventory` for today's figure rather than trusting this one.

## The scan is line-based, and that is load-bearing

Three of the estate's Denys live inside a `ResourceSet`'s `resourcesTemplate` **string** — one per
adopter, in `gitops/composed/composed-set.yaml`. A `yaml.safe_load_all` walk over those files sees
one `ResourceSet` and no policy at all, and would report the estate as three refusals cleaner than
it is. So the scan reads lines and recovers each rule's name from the nearest `name:` above it,
which is true inside a template string as well as inside a document.

## Escaping the register

## What this scan CANNOT see

`deny_register.BLIND_SPOTS`, printed on every run and held non-empty by a test: a YAML anchor or
alias; a template engine's conditional arm; an action computed at admission; Gatekeeper's
`enforcementAction: deny`; the 2022 `rules[].validate.deny{}` block; a webhook's own
`failurePolicy: Fail`; and the one that matters most, **a refusal by another name** — a mutation
that makes a pod inadmissible refuses the workload with no Deny-shaped text anywhere in it.

The estate has produced that failure three times, every one found by RUNNING the policy and never
by reading it: ticket 26 on 2026-08-28 (a sidecar appended twice, so every update to a caged pod
was rejected); this ticket's first cut on 2026-09-05 (the machinery cage named a PriorityClass no
cluster has, because every served one is version-suffixed); and its second, the same day (an
`UPDATE` arm that applied the full cage body to a running pod, which would have refused the
currency controller's re-cage patch — ticket 91's, and the only way a pod on a retired version
reaches the bottom rung). Two of the three were this ticket's own. Read the register for what was
decided; read the beats for what runs.

Four other blind spots a reviewer planted on 2026-09-05 are now closed, each with a test that was
red first: a `.json` policy, a one-line flow mapping, a multi-line flow sequence, and
`validationFailureActionOverrides`. The exploitable one is closed too — name attribution was
positional and unbounded, so a document whose `metadata:` follows its `spec:` inherited the
previous document's name and a second Deny appended to an already-covered file read as accounted
for. Attribution is bounded to its own document now.

Only `register.yaml`'s `excluded:` list, and every entry carries the reason it is not a served
policy copy. There are two today: the hub's `spikes/` material, and platform's `computed-semver`
corpus — whose Denys are the ENGINE'S INPUT, the pairs it computes an `Audit -> Deny` bump across.
Deleting those would delete the estate's ability to compute the bump that retires anything.

## Run it

```sh
./verify-deny-is-not-a-rung.sh              # selfcheck, then grade the hub and the estate
./verify-deny-is-not-a-rung.sh --selfcheck  # the grader's own asserts, plus a planted Deny
./verify-deny-is-not-a-rung.sh --inventory  # one row per finding: path, kind, name, shape, rule
```

## Where the rest of the ticket landed

* `verify/proportionality/` no longer derives `Audit` versus `Deny` from a party's band. It grades
  **tier selection** — the same mechanism the estate ships — and stopped rendering a Deny of its
  own (item 2).
* The platform's two machinery guards changed in `distribution/render-orphan-guard.py` and
  `distribution/render-governed-namespace-guard.py`, on platform branch
  `ticket-89-deny-is-not-a-rung` (item 1).
* `CONTEXT.md`, ADR-0014, ADR-0018 §4 and ADR-0022 carry one dated sentence between them
  (items 3 and 4).
