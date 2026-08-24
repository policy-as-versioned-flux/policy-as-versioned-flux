# 23 — Coverage stated as counts and holes

Type: task
Status: done (2026-08-24)
Blocked by: 19, 21

Source: [`spec.md`](../spec.md), *Coverage and evidence*.

## What to build

A reviewer reads what the gate did not test. **No coverage percentage exists anywhere.** A percentage
invites a threshold. A threshold invites tuning the corpus until it passes.

Coverage is defined over **predicate expressions only**, which means `matchConditions` and
`validations`. Several live expressions are variables returning strings or objects, and "satisfied" is
meaningless for them. A variable counts as covered when an enumerated axis spans its value space. Add
no new axis. Name the rest in the not-looked-at list.

**Two measurements, two jobs.** **Cells** are each predicate expression against satisfied, violated and
absent. **Pairs** are the axis combinations actually built.

**The pairwise gap is one sentence and two counts.** The sentence states that axes were combined
pairwise, so no three-way interaction was built. Never print a whole-space ratio. The space is over
four million and the built set is tens.

**Three binary gates replace the threshold.** An unreached predicate fails. A missing witness shape
fails, from [ticket 20](20-witness-set-and-missing-shape-gate.md). Movement on an unversioned policy
fails, from [ticket 22](22-pairing-rules-and-platform-machinery.md). The pairwise gap never blocks a
release.

**Unreachable expressions get a declared exclusion in two tiers.** A **proved exclusion** is one the
gate can prove nothing reaches. A **declared hole** is one it cannot prove, and it prints for ever. A
human may declare a hole. A human may not promote one to proved.

**A hole carries a stable id**, derived from a hash of the normalised expression text. Scope the id by
the identity family and by the policy name with its version stripped. Normalising removes the version
literal. An unchanged rule therefore keeps its id across versions.

**The limits are derived, not written.** Each limit is emitted by the check that would remove it, with
its current count. A limit never vanishes. At zero it prints as closed with the count that closed it.

Two limits stay open by decision. The cage ratchets one way and has no counter-pressure. The rule sees
only the workload's side, so removing enforcement scores as a patch. A third limit already has a
count: nothing maps a pod to a priced residual, so the cage half is proved on synthetic input.

## Acceptance criteria

- [x] No percentage appears anywhere in the document or the output.
- [x] Coverage counts cells and pairs as two separate numbers.
- [x] The pairwise gap prints as one sentence and two counts.
- [x] No whole-space ratio is printed.
- [x] Coverage covers predicate expressions only.
- [x] A variable counts as covered only when an enumerated axis spans its values.
- [x] An unreached predicate fails the build, and the document names the expression.
- [x] `not_looked_at[]` lists holes and proved exclusions, each with a stable id.
- [x] Each entry is marked new, carried over, or closed.
- [x] An unchanged rule keeps its hole id across two versions. A changed rule gets a new one.
- [x] The exclusion file lets a human declare a hole and refuses to let a human promote one to proved.
- [x] Each limit is emitted by the check that would remove it, with its count.
- [x] A limit at zero prints as closed rather than vanishing.
- [x] The three named open limits print with their counts.

## Comments

Shipped in `platform` at `ba273d9` (cs-23).
