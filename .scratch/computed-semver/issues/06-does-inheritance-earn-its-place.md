# 06 — Does the rule-set delta need inheritance to be readable?

Type: prototype
Status: open
Blocked by: 01

## Question

The narrow question, deliberately fenced: **does computing the bump require policies to `extends`
their predecessor, or is a rendered-artefact diff enough?**

The duplication is real. `estate/platform/distribution/policies/v2.0.0/require-nonroot.yaml` copies
`v1.0.0`'s CEL expression byte-identically, hand-edits the version string in three places, and appends
one rule. With `extends`, the delta *is* the source; without it, the delta must be recovered by
diffing two full bodies that differ in cosmetic ways (names, labels, `matchConditions`, message text)
as well as substantive ones.

**Prototype it both ways** on the rederivation ticket's own material, and judge:

1. Can a diff of rendered policy bodies isolate the *substantive* rule change from the version-string
   noise reliably enough to compute a bump? If yes, inheritance is a separate DRY improvement and
   leaves this map.
2. If not, what is the minimum inheritance shape that fixes it — and note the hard constraint: it must
   render down to today's flat, per-version `matchConditions` self-scoping. The policy files' own
   comments record that `objectSelector` gets flattened into one shared webhook and "silently breaks
   multi-version coexistence", so runtime inheritance is ruled out. Source-level only.

**Do not use this ticket as a doorway to refactoring every policy file.** If inheritance wins, it wins
a follow-on effort; what this ticket owes the map is the answer to whether the gate needs it.
