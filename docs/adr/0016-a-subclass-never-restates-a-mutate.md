---
status: accepted
---

# A subclass never restates a mutate: the tier is the only knob, and only the proposer turns it

Composition lets a subclass tighten an inherited rule. It compares the inherited action against the
restated one on the `Audit < Deny` ladder, and accepts the restatement only when it is stricter. That
ladder is a `ValidatingPolicy` concept. Half the live admission set is not a `ValidatingPolicy`.

## What was already there

`cs-12`'s `render-version-tree.py` emits four claim-wide policies into every version tree. Composing
the whole live set for one version gives six members:

| member | family | kind |
|---|---|---|
| `require-nonroot` | `require-nonroot` | ValidatingPolicy |
| `posture-trust-boundary` | `posture` | ValidatingPolicy |
| `stamp-posture` | `posture` | MutatingPolicy |
| `cage-tier` | `graded-enforcement` | MutatingPolicy |
| `cage-netpol` | `graded-enforcement` | GeneratingPolicy |
| `policy-version-orphan-guard` | `platform-machinery` | ValidatingPolicy |

Three of the six carry no `spec.validationActions` at all. A `MutatingPolicy` and a
`GeneratingPolicy` have no action, so they have no place on the strictness ladder.

## The decision

1. **A restatement applies to a `ValidatingPolicy` and to nothing else.** A composition that restates
   a mutate or a generate is refused. There is no ladder to compare on, so an accept would be a
   guess.
2. **The cage tier is the only knob an adopter has on the graded members.** `cage-tier` reads
   `posture.acme.io/tier` from the workload. The tier is a priced verdict that `cage.py` selects.
3. **Only the proposer turns it.** ADR-0015 already settled that the adopter runs the war-gamer and
   that it opens a PR editing `posture.acme.io/tier` on a workload manifest. That is the whole path.
   The composed artefact carries no tier and no tier floor.
4. **The resolver keys on the identity family plus the name with its version stripped.** The
   `policy-as-versioned.dev/policy` label is a family name, not a unique key: `graded-enforcement`
   covers five objects and `posture` covers two. `cs-22` settled this key for the release gate. The
   resolver takes the same one.
5. **The orphan guard composes under a second numbering axis.** It is the aggregate over the version
   array, so it cannot self-scope to one claim. It carries the `platform-machinery` identity and the
   platform tag numbers it. A composition carries that axis; it never forces the guard onto the
   policy-version axis.

## Considered options

- **Restrict restatement to `ValidatingPolicy`, tier via the proposer (chosen).** It keeps the £ as
  the only thing that moves a verdict, which is the map's standing preference. It adds no mechanism:
  ADR-0015's rail already exists and already edits the right label.
- **Let the overlay declare a per-party tier floor that `cage-tier` reads.** Rejected. A tier is a
  priced verdict, and `cs-02` settled that the cage spec *is* the verdict. A floor in the overlay is
  a verdict set by a declaration rather than by the £. That is the override this model does not have.
- **Refuse any composition that touches a non-`ValidatingPolicy` member.** Rejected. It leaves an
  adopter with no route at all, and the members compose and render down cleanly. The restriction
  belongs on restatement, not on composition.
- **Invent an action for a mutate, so the ladder covers every kind.** Rejected. The Kyverno schema
  has no such field. Writing one produces a manifest the cluster refuses.

## Consequences

- **The spike had this defect and it is fixed.** `spikes/cs-06b-cross-party-composition/compose.py`'s
  `render()` wrote `spec.validationActions` onto every member unconditionally. On a mutate or a
  generate that invents a field the schema does not have. It is now guarded by kind.
- **The old resolver key overwrites in silence.** `load_publications` keys on
  `(identity label, version)`. Two members of one family at one version collide, and the second wins
  with no error. It has not fired only because exactly one `ValidatingPolicy` per family per version
  exists today. That is luck, not design. **A named gap in the spike, closed in the new loader.**
- **Mutation ordering is inherited, not declared.** `stamp-posture` writes the label
  `posture-trust-boundary` validates. `cage-tier` writes the label `cage-netpol` generates from. A
  flat per-version render does not state either dependency. Kyverno runs the mutating webhook before
  the validating webhook, which is what makes it work. **This is `platform` machinery and it is out
  of scope for composition.** A second implementations publisher is what would expose it, and the
  estate has one.
- **The whole live set renders back down faithfully**, every kind, including the guard. Five members
  compare against a committed file. The guard has no committed rendered form, so it compares against
  the estate's own `render-orphan-guard.py`. That proves composition carries it unchanged. It does
  not prove the twin matches what flux-operator renders in-cluster.
- **No new refusal reaches an adopter today.** No party manifest in the estate restates a
  non-`ValidatingPolicy` member, because the inheritance edges do not exist yet. The rule is written
  before the first case, not after it.
