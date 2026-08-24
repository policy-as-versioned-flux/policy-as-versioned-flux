# 26 — The four extra gate rules

Type: task
Status: done (2026-08-24)
Blocked by: 12, 22, 24

Source: [`spec.md`](../spec.md), *The four extra gate rules*. Replaces the rules half of
[ticket 11](11-gate-rules-from-cs-07.md).

## What to build

Four structural rules that close four ways the gate could be fooled. Each is a refusal, not a bump
class, so the number stays honest.

**1. Read prior versions from their tags, never from HEAD.** The delivered `1.0.0` comes from tag
`policy/v1.0.0`, but the gate would naturally read `distribution/policies/v1.0.0/` at HEAD. A hand edit
there would fool the gate about what `1.0.0` means. A **frozen-tree check** fails when a HEAD copy of a
released tree differs from its tag. This makes "the window as it stood before this release" mechanical
rather than aspirational.

**2. Re-render only the tree being cut.** Same shape as the corpus check. Regenerate, diff, fail.
Re-rendering every tree and failing on any diff would freeze the dial table for ever. A renderer defect
therefore appears as a refusal in the evidence document, which is why the renderer gets no second seam.

**3. Refuse a release that removes an enforcement surface from a version.**
[Ticket 12](12-render-mandatory-members-into-a-version-tree.md)'s mandatory-member list **is** the
enforcement-surface list, so the rule is a set comparison against it.

**4. Refuse an array element with an empty `commit`.** Both elements carry `commit: ""` today.
[Ticket 15](15-the-repair-release.md) fills them. Without this rule the field silently empties again on
the next hand-edited element.

## Acceptance criteria

- [x] The gate reads every prior version from its tag.
- [x] A hand-edited HEAD copy of a released tree refuses under the frozen-tree check.
- [x] The gate re-renders the tree being cut, diffs it and refuses on a difference.
- [x] The gate never re-renders a released tree.
- [x] A renderer defect surfaces as a refusal in the evidence document.
- [x] A release that removes a mandatory member from a version refuses.
- [x] The enforcement-surface rule is a set comparison against the mandatory-member list.
- [x] An array element with an empty `commit` refuses.
- [x] Every refusal names what it refused and why.

## Comments

Shipped in `platform` at `8715610` (cs-26).
