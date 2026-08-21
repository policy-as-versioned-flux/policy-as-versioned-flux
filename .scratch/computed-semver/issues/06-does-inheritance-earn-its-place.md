# 06 — Does the rule-set delta need inheritance to be readable?

Type: prototype
Status: resolved
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

## Correction

**This ticket's body wrote down the wrong question.** It asked whether a policy version needs to
extend **its own predecessor** — intra-policy DRY, `require-nonroot` 2.0.0 extending 1.0.0. The intent
was always **cross-party**: a party's policy set inherits from **other parties**, and mashes them up
the way a class inherits. Policy as a dependency you extend, not only pin. The map's own standing
preference says "policies-that-`extends`-policies", which is the cross-party reading.

The Answer below is correct **for the narrow question as written**, and it stands. It does not settle
the real one. The real question got its own map:
[`policy-composition`](../../policy-composition/issues/01-does-composition-hold-up.md). Its answer is
yes, composition is a real and missing layer. This map takes exactly one fact from it: **the bump is a
property of a composition, so the gate computes it after composition.**

Two of the four findings below survive and matter more under composition. The render-down constraint
is now load-bearing rather than incidental. The pairing key is worse across parties, because two
publishers can ship the same family name. The claim "inheritance leaves this map" is withdrawn.

## Answer

**No. A rendered-artefact diff is enough. Inheritance leaves this map.** Prototype:
`spikes/cs-06-inheritance-vs-diff/` — `./run.sh`, exit 0, self-checking.

Both paths were built and run over the same real material: the `require-nonroot` pair this ticket
names, and cs-01's own corpus (`department-label` 1.0.0→2.0.0, `known-department-label`
2.0.1→2.1.1, `owner-annotation` added). They return the **same delta** on the named pair.

The answer to question 1 is yes, but the reason is not that the diff is clean. It is that **the gate
never classifies from the delta**:

- **major** and **patch** come from verdict movement on the corpus (cs-01), plus `validationActions`.
- **minor** comes from *presence* plus `validationActions` — cs-01 proved verdict movement cannot see
  it. That is a set difference over identities, not a delta.
- The corpus generator (cs-03, per CEL expression) wants the **list** of expressions on each side. A
  list, not a delta.
- The delta is evidence prose for the reviewing human (ADR-0002). Imprecision there costs a noisy
  evidence line, never a wrong bump.

Four findings the gate has to carry, each demonstrated by the prototype rather than asserted:

1. **Parse the YAML; never text-diff.** The raw text diff of the named pair changes 30 lines, 19 of
   them comment prose. Parsing removes all of it for free.
2. **The identity label is a family name, not a unique key.** Reading the live estate,
   `graded-enforcement` and `posture` each group several *different* policies carrying no version
   label. The pairing key must be `(identity, name-with-version-stripped)`, and an unversioned member
   must **fail** the gate rather than pair by accident. This sharpens cs-03's "five live policies
   carry no version": they *do* carry the identity label, which is what makes naive pairing silently
   wrong.
3. **Compare rules as a set.** Swapping two rules and changing nothing else makes a positional
   compare report 2 added and 2 removed.
4. **A version-literal difference is UNPROVEN, not a change.** A policy whose approved image tag
   happens to equal `1.0.0` at both policy versions becomes a false positive under version-string
   normalisation. Path A cannot tell "the version" from "a value equal to the version".

Question 2 is answered anyway, for the follow-on effort: **the minimum inheritance shape is three
ops** — `actions`, `addValidations`, `replaceValidations` — which covers the estate's entire real
release line. `render()` in the prototype flattens it to the committed per-version files
(parsed-equal), so the hard constraint holds: `matchConditions` self-scoping, no runtime inheritance,
`objectSelector` still avoided. Inheritance is also immune to findings 3 and 4 by construction. That
is an argument *for* inheritance as a DRY effort. It is not an argument that the gate needs it.
