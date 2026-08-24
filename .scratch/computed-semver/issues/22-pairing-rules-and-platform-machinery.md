# 22 — Pairing rules and the `platform-machinery` class

Type: task
Status: done (2026-08-24)
Blocked by: 21

Source: [`spec.md`](../spec.md), *Pairing and structural rules*, and *The subject*.

## What to build

The gate pairs an old policy with its new counterpart correctly, and refuses when it cannot. A wrong
pairing produces a confident wrong bump.

**Parse the YAML.** In the named historical pair, 19 of the 30 changed lines are comments. A text diff
would classify a comment change.

**The identity label is a family name, not a unique key.** `graded-enforcement` and `posture` each
group different unversioned policies. Pair on the tuple of identity and the policy name with its
version stripped.

**Fail on an unversioned member.** Movement traced to an unversioned policy fails the gate and names
the file. This is the finding that made
[ticket 15](15-the-repair-release.md) exist, and it stays a gate rule afterwards.

**Compare rules as a set.** Order is not meaning.

**Treat a version-literal difference as unproven.** The gate does not guess.

**`platform-machinery` is a class, not a by-name exclusion.** The orphan guard carries no identity
label and is legitimately unversioned, because the platform tag numbers it. Give it that identity and
teach the pairing rule that this family is numbered by the platform tag. A by-name exclusion lets the
next machinery object slip through.

**Two versioned trees declaring the same version with different content fails the gate.**

**The subject is every Kyverno policy that can reach a pod, plus the version array.** The array decides
which bodies run. The dial map inside the tier policy is a policy body. Tightening a `baseline` limit
downward is major, because a pod that cannot schedule under the new limit is refused.

## Acceptance criteria

- [x] The engine parses the YAML and never diffs text.
- [x] A comment-only change classifies as no movement.
- [x] Pairing uses the tuple of identity family and the name with its version stripped.
- [x] An unversioned member fails, and the document names the file.
- [x] Rules compare as a set.
- [x] A version-literal difference is reported as unproven.
- [x] The orphan guard carries the `platform-machinery` identity.
- [x] The pairing rule treats `platform-machinery` as a class numbered by the platform tag.
- [x] A new machinery object with no identity still fails, so the class is not a by-name escape.
- [x] Two versioned trees declaring the same version with different content fails.
- [x] The version array is part of the subject.
- [x] A tightened `baseline` dial classifies as major.

## Comments

Shipped in `platform` at `c29869f` + `86ea2ec` (cs-22).
