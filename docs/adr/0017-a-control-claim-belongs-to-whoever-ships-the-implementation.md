---
status: accepted
---

> **Superseded in part, 2026-09-04.** "Refuse, same as any new hole (chosen)", the self-created hole refusal, and "Removing a self-added control: never" are superseded by [ADR-0026](0026-a-hole-is-priced-never-refused-the-claim-keys-on-source-and-id.md): an adopter's own addition is a priced new hole and its removal a priced delta, keyed (source, id) across every controls parent. The rest stands: a claim belongs to whoever ships the implementation, it lives in that party's component-definition, and nobody claims against an inherited policy. The self-created hole half was built 2026-09-03 by ticket 38; the removal half waits on a platform build.

# A control claim belongs to whoever ships the implementation, and an adopter's own addition is an ordinary hole

[ADR-0013](0013-regulator-publishes-baselines-adopter-selects.md) lets an adopter **add** a control
to its selected baseline. It did not say what may fill one. The estate's adopters ship no
implementations: `driftwood` "authors no policy today" and pins `platform` and `nist`. In the
`cs-06b` prototype the adopter can add a **policy** (`overlay.add`), but coverage reads only the
publisher's OSCAL component-definition (`compose.py`, step 5), so nothing an adopter does can fill
a control it adds. The addition is a hole the moment it lands, with no route out.

**A control is filled by a signed OSCAL control claim, made by whoever ships the implementation.**
The composition does not care which party made the claim. An inherited publisher fills an added
control when its component-definition already evidences it. The adopter fills one by shipping its
own member, with its own claim, in its own component-definition next to the party artefact it
signs. A third implementations publisher fills one by being pinned as a parent.

**An adopter-added hole is an ordinary new hole.** The composition compares against the last signed
composed artefact, finds the hole new, and refuses. The adopter clears it in the same reviewed PR:
it supplies the implementation, or it accepts the hole onto the recorded list. There is no
"I added it on purpose" flag.

**The adopter may never claim a control against a policy another party ships**, and **may never
remove a control it added**.

**Shipping a member adds no obligation the adopter does not already carry.** The member is an
overlay member of the composed artefact that ADR-0012 already makes the adopter gitsign-sign. It
is versioned with that artefact and has no separate semver axis and no separate pin. The adopter
becomes an **implementations** publisher only when another party pins its composed artefact as a
parent, which is a fact about the pinner and not a role the adopter declares.

## Considered options

**What fills an adopter-added control**

- **Any signed control claim, from whoever ships the implementation (chosen).** One rule, and the
  rule the composition already applies to parents. Only the read side changes: the adopter's own
  claim is read beside the parents' claims.
- **Only an inherited publisher's implementation.** Rejected: an adopter that needs a control no
  parent evidences has no route except asking upstream, which makes the addition useless.
- **A separate "adopter implementation" mechanism.** Rejected: a second claim format is a second
  place for the id form to drift, which ADR-0013 just removed.

**Whether a self-created hole refuses**

- **Refuse, same as any new hole (chosen).** ADR-0013's widening edge at size one. The refusal is
  the signal, and it clears in a reviewed PR.
- **Skip the refusal when the hole and the addition land in one commit.** Rejected: an override
  branch. The map's standing preference says there is never an exemption.

**Where the adopter's claim lives**

- **The adopter's own OSCAL component-definition, next to its party artefact (chosen).** Bare id,
  `source` href naming `nist` plus a path, exactly as ADR-0013 requires of `platform`.
- **A `claims:` list on the party artefact itself.** Rejected: a second format for the same fact.

**Claiming against an inherited policy**

- **Forbidden (chosen).** The claim is unsigned by the party that owns the policy, and it breaks in
  silence when that party changes the policy. The adopter asks upstream, or ships its own member.
- **Allowed, as an adopter-side annotation.** Rejected for the reason above.

**Removing a self-added control**

- **Never (chosen).** Adding was a claim. Withdrawing it is an exemption by another name. The
  control stays, the hole is recorded, and the cage prices it.
- **Allowed, because the adopter created it.** Rejected: origin does not change what removal does
  to the £.

## Consequences

- **The composition reads one more component-definition.** The adopter's, from its own repo. The
  `cs-06b` prototype's `pubs["mapping"]` becomes a merge over every party that ships a member,
  including the composing party.
- **An adopter's own member is subject to ADR-0016.** It is a new member, not a restatement. A
  mutate it ships is its own, and it still cannot restate an inherited one.
- **A second implementations publisher becomes possible.** Ticket `01` recorded that two parents
  whose rules disagree is refused and untested. Pinning a third publisher makes that path live.
- **Terms.** `CONTEXT.md` gains **Control claim**, distinct from the pod's **claim** label, and the
  **Baseline** entry gains the addition rules.
