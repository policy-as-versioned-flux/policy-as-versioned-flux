# require-known-department-label

**Risk mitigated:** a free-text `department` value can be misspelled or
invented. That silently breaks cost attribution (charged to no real cost
centre) and, worse, evades any downstream automation that routes by
department (e.g. a regulated department's extra controls never fire because
its workloads are labelled with a value that automation doesn't recognise).
Unlike a missing label (caught by [require-department-label](../require-department-label/rationale.md)),
an unrecognised value looks legitimate at a glance.

**Intent:** this is the gate ("locked door") tier paired with the lane-keeper
above -- both label the same field, but this one is `validationActions:
Deny`. It is also this project's worked example of the semver-major case in
[CONTEXT.md](../../../CONTEXT.md#core-thesis-terms): "free-text label →
enum" is exactly a version bump that can turn a previously-passing workload
(any string) into a failing one.

**Why Deny, not Audit:** by the mea-culpa's own bar (CONTEXT: gate is
reserved for the "catastrophic minority" -- access control, data
classification, key management), a department label is a stretch, and this
is candidly the demonstrator that proves the Audit/Deny mechanism split
end-to-end (kustomize + CEL + version self-selector), not a claim that
department labelling is catastrophic. A production estate should reserve
`Deny` for the categories CONTEXT actually names.

**Scope:** only denies a *present but unrecognised* value -- it does not
require the label to exist (that is the lane-keeper's job, deliberately left
in `Audit` so the majority of the estate can adopt it gradually).

**Disagreement:** raise a pull request against this policy (e.g. to add a
department, or to demote back to `Audit`) -- not an out-of-band exemption
request.

Dated: 2026-07-14. Reviewed: 2026-07-14.
