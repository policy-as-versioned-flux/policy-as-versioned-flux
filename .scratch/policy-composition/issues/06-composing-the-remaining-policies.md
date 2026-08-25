# 06 — Composing the five unversioned live policies

Type: prototype
Status: resolved
Blocked by: none

Graduated from the map's Not yet specified: "Composing the five unversioned live policies." The
`cs-06b-cross-party-composition` prototype composes 3 of the 8 policies that `cs-03` found live and
unversioned.

## Question

Does composition still hold up, and render back down cleanly, across the remaining five policies
`cs-03` found that the prototype does not yet reach? Extend the spike to cover them and record what
changes, if anything, about the earlier findings.

## Answer

Resolved by prototype, 2026-08-25. Section 11 of
[`spikes/cs-06b-cross-party-composition/`](../../../spikes/cs-06b-cross-party-composition/) composes
the whole live set. `./run.sh` self-checks and exits 0. Recorded as
[ADR-0016](../../../docs/adr/0016-a-subclass-never-restates-a-mutate.md).

**Yes, it holds up, and every member renders back down faithfully.** No refusal, no lost body, no
leaked `objectSelector`.

### The premise was true when it was written, and the estate has since overtaken it

`cs-03` counted eight live policies, five carrying no version. **Four of the five are now versioned.**
`cs-12`'s `render-version-tree.py` emits `cage-tier`, `cage-netpol`, `stamp-posture` and
`posture-trust-boundary` into every version tree, self-scoped on the claim. They compose exactly as
`require-nonroot` does.

**The fifth cannot be versioned, and that is correct.** The orphan guard is the aggregate over the
version array, so it cannot self-scope to one claim. `cs-22` gave it the `platform-machinery`
identity: the platform tag numbers it. Composition carries a second numbering axis rather than
forcing the guard onto the first. Section 11 renders it from the array through the estate's own
`render-orphan-guard.py`, so the simulated list-membership check the first pass admitted to is gone.

| member | family | kind | declares |
|---|---|---|---|
| `require-nonroot` | `require-nonroot` | ValidatingPolicy | `3.0.0` |
| `posture-trust-boundary` | `posture` | ValidatingPolicy | `3.0.0` |
| `stamp-posture` | `posture` | MutatingPolicy | `3.0.0` |
| `cage-tier` | `graded-enforcement` | MutatingPolicy | `3.0.0` |
| `cage-netpol` | `graded-enforcement` | GeneratingPolicy | `3.0.0` |
| `policy-version-orphan-guard` | `platform-machinery` | ValidatingPolicy | — (platform tag) |

### Three findings, and the first two are defects in the spike

1. **An action is a `ValidatingPolicy` concept.** `render()` wrote `spec.validationActions` onto every
   member, which invents a field the schema does not have on a mutate and a generate. Fixed. The
   consequence is larger than the fix: the `Audit < Deny` ladder that `overlay.restate` compares on
   has no meaning for **three of the six** members. **A subclass cannot tighten a mutate.** The tier
   is the only knob, and ADR-0015's proposer is the only thing that turns it. ADR-0016 decides this.
2. **The identity label is a family, not a key.** `graded-enforcement` covers five objects and
   `posture` covers two. `load_publications` keys on `(label, version)`, so a second member of one
   family overwrites the first in silence. It has not fired only because one `ValidatingPolicy` per
   family per version exists today. That is luck. `cs-22` already settled the cure for the release
   gate; the resolver takes the same key.
3. **Two members mutate, so ordering is observable.** `stamp-posture` writes the label
   `posture-trust-boundary` validates. `cage-tier` writes the label `cage-netpol` generates from. A
   flat per-version render states neither. Kyverno's webhook ordering is what makes it work.
   **Ruled `platform` machinery and out of scope** for this map. A second implementations publisher
   is what would expose it, and the estate has one.

### Two facts about the estate, not about composition

- **Gap 2 changed shape.** `cs-16` deleted `policy/policies/` and folded `may-run-root-if-attested`'s
  widening into `require-nonroot@2.0.1`. `ac-6` still claims `may-run-root-if-attested`, which now
  exists nowhere. The gap moved from OVERCLAIMED-because-uninstalled to the same shape as gap 1: a
  dangling reference a plain lint finds. **The named gap does not shrink; it renames.**
- **The same-version-two-trees question is closed.** The first pass raised it as the map's own open
  question. The collision is gone because the tree is gone. `cs-22` kept the gate rule that refuses
  it, so a reappearance still fails.

### Honest limits

- The spike would not run at all before this ticket. `safe_load` crashed on the multi-document
  `priorityclasses.yaml`, and `policy/policies/` no longer exists. **The spike had rotted against the
  estate it reads**, and nothing was watching.
- Five members compare against a committed file. The guard has no committed rendered form, so its row
  compares against the estate's own twin. That proves composition carries it unchanged. It does not
  prove the twin matches what flux-operator renders in-cluster. `verify-orphan-guard.sh` covers that,
  and this spike runs no cluster.
- Sections 1 to 10 still describe the estate at `v1.0.0`/`v2.0.0`. They were re-run and their
  assertions hold, except the two this ticket corrected. **They were not rewritten to the current
  version array**, so read them as the first pass's record.

