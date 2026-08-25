# 15 — The governed namespace lint

Type: task
Status: resolved
Blocked by: 12

Source: [`spec.md`](../spec.md), *Governed namespaces*. Decisions:
[ADR-0014](../../../docs/adr/0014-unclaimed-is-caged-governed-namespace-requires-claim.md),
[ADR-0018](../../../docs/adr/0018-the-namespace-manifest-is-the-governed-declaration.md).

## What to build

A namespace cannot exempt every workload in it by omission.

The composition reads every `Namespace` manifest in the adopter's repo. One that carries the
`institution` label and not `governed: "true"` is ungoverned. The rule is the hole rule. A new one
refuses. A recorded one records. A labelled one prints as closed. The comparison set is the list in
the last signed composed artefact.

The header gains the recorded ungoverned namespaces. The document gains `ungoverned[]`. The composed
artefact still carries no namespace list as a declaration. The governed set is advisory only.

## Acceptance criteria

- [ ] A new ungoverned adopter namespace refuses and names it.
- [ ] A recorded ungoverned namespace records and does not refuse.
- [ ] A namespace that gains the label prints as closed.
- [ ] A namespace without the `institution` label is ignored.
- [ ] The header carries the recorded ungoverned namespaces, and stripping it leaves the files unchanged.
- [ ] Nothing in the rendered files reads the governed set. Only the header carries it.

## Answer

Built, inside the same `compose()`, mirroring `compute_holes` exactly (new/recorded/closed shape,
same bootstrap rule).

`ungoverned_namespaces(adopter_dir)` (`.estate-clone/platform/compose/composition.py`) walks every
`Namespace` manifest in the adopter's repo and returns the names that carry
`policy-as-versioned.dev/institution` and not `policy-as-versioned.dev/governed: "true"`. A
namespace with no `institution` label at all never enters the set. `compute_ungoverned(current,
prev_ids)` compares that set against the last signed composed artefact's own recorded set (read
off `HEADER.yaml`'s new `ungoverned-namespaces` key by the existing `_previous_header`): a name not
in `prev_ids` is `new` and produces a `new-ungoverned-namespace` refusal
(`needs_composition: true`); a name already recorded stays `recorded`, no refusal; a name that was
recorded but has dropped out of the current set (it gained the label) prints `closed`. `prev_ids is
None` — no committed header at all — is the same bootstrap case `compute_holes` uses: every
currently-ungoverned namespace records and none refuses, matching spec.md's "the first composition
records ... three ungoverned namespaces and refuses on none".

The header gains `ungoverned-namespaces` (the still-open recorded set, next to `holes`); the
document gains `ungoverned[]` (every entry, with its status). The composed artefact still carries
no namespace list as a declaration — `governed_namespaces()` (unchanged, ticket 12) stays the only
list, and it is advisory metadata, not a rule input. Neither namespace set is ever read by
`render_member`/`strip_provenance` or written into any per-member file; `HEADER.yaml` is the only
place either appears, so stripping it leaves every other rendered file byte-for-byte unchanged
(asserted directly in `--selfcheck`, the same "strip the header, nothing else changes" check
ticket 14 already runs for `holes`).

Against the real estate: `driftwood`'s own `Namespace` manifest already carries both labels (ticket
11 landed it labelled from the start, ADR-0018), so the real composition today records zero
ungoverned namespaces — `document["ungoverned"] == []`. Every acceptance criterion above is instead
proved with a small fixture chain (`--selfcheck`, "TICKET 15" section): a namespace with no
institution label is ignored; a first composition (nothing committed yet) records a pre-existing
ungoverned namespace and refuses on none; an unchanged second run still records it, still no
refusal; the same namespace, once it gains `governed: "true"`, prints `closed`; and a namespace
absent from the last signed artefact's recorded set refuses as `new`, naming it.

`--selfcheck` and `./verify-composition.sh` both pass. No new ADR — ADR-0014 and ADR-0018 already
record every decision this ticket implements.
