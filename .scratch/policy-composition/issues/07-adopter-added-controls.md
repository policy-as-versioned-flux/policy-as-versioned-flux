# 07 — What fills a control the adopter adds itself

Type: grilling
Status: resolved
Blocked by: none

Surfaced by ticket [`03`](03-baseline-and-catalogue-ids.md). That ticket settled that an adopter may
**add** a control to its selected baseline and may never remove one. It did not settle what happens
next. The estate's adopters ship no implementations: `driftwood` "authors no policy today" and pins
`platform` and `nist`. So an adopter-added control is a hole the moment it is added, with no
publisher able to fill it.

## Question

When an adopter adds a control to its own baseline, what may fill it? Does an adopter-added hole
behave differently from an inherited one under ticket `03`'s new-hole rule, given that the adopter
created it deliberately in the same commit? And if an adopter can also ship an implementation, does
it become an implementations **publisher**, with the versioning and signing obligations that role
carries?

## Answer

**A control is filled by a signed OSCAL control claim, from whoever ships the implementation. An
adopter-added hole is an ordinary new hole.** Recorded as
[ADR-0017](../../docs/adr/0017-a-control-claim-belongs-to-whoever-ships-the-implementation.md),
with a new **Control claim** term and an amended **Baseline** entry in `CONTEXT.md`.

### Facts the decision rests on

| Fact | Evidence |
|---|---|
| The prototype lets an adopter add a **policy** but not claim a **control** | `spikes/cs-06b-cross-party-composition/compose.py` step 4 reads `overlay.add`; step 5 reads only `pubs["mapping"]` |
| The adopter already signs a composed artefact with the publisher's own mechanism | ADR-0012, `CONTEXT.md` *Role: adopter* |
| A widening of the baseline already refuses with no override | Ticket `03`, edge 2 |

### The six decisions

1. **What fills it.** Any signed control claim: an inherited publisher that already evidences the
   control, the adopter's own member, or a third publisher pinned as a parent. One rule, the one
   the composition already applies to parents. Only the read side changes.
2. **Self-created hole.** No special case. It is new against the last signed composed artefact, so
   it refuses. It clears in the same reviewed PR, by supplying the implementation or accepting the
   hole onto the recorded list. No "I added it on purpose" flag.
3. **Where the claim lives.** The adopter's own OSCAL component-definition, next to the party
   artefact it signs. Bare id, `source` href naming `nist` plus a path, as ADR-0013 requires.
4. **Publisher obligations.** None new. The member is an overlay member of the composed artefact,
   versioned and signed with it, with no separate axis and no separate pin. The adopter becomes an
   **implementations** publisher only when another party pins it. Roles compose.
5. **Claiming against an inherited policy.** Forbidden. The claim would be unsigned by the owner
   and would break in silence when the owner changes the policy.
6. **Removing a self-added control.** Never. Same rule as ADR-0013. Withdrawal is an exemption by
   another name.

### What this ticket did not do

It changed no repo but the hub. The prototype's `pubs["mapping"]` merge and the adopter-side
component-definition are edits to the `cs-06b` spike and the adopter repos, and the map rules
repairs out of scope. A second implementations publisher is now possible, and ticket `01`'s
untested two-parent disagreement path stays untested.
