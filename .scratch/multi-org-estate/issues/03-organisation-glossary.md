# 03 — Settle what "organisation" means before the split hard-codes the ambiguity

Type: grilling
Status: resolved
Blocked by: none

## Question

"Organisation" currently means three different things and `CONTEXT.md` defines none of them:

- a **GitHub organisation** (six exist: `policy-as-versioned-{platform,driftwood,tuppence,ludlow,nist,ico}`, all empty since 2026-07-23);
- a **modelled institution** in the risk engine (driftwood/ludlow/tuppence have appetite bands, scenarios, £);
- a **directory** in `estate/`.

`estate/README.md` calls itself "the six-org talk demo" but its own table header says "Repo". The
demo narration says "six live organisations". After the split these stop being interchangeable —
a regulator (`nist`, `ico`) is an org that publishes but holds no risk appetite; `platform` is an org
that is a dependency, not an institution.

**Settle:** the canonical term for each concept, which of the six are institutions vs publishers,
and what the demo is entitled to call them. Write the resolved terms into `CONTEXT.md` (glossary
only — no implementation detail).

Blocks nothing mechanically, but every ticket downstream writes this vocabulary into READMEs, script
output and narration, so resolve it early.

## Answer

Resolved by grilling, 2026-08-20. Terms written into [`CONTEXT.md`](../../../CONTEXT.md)'s
*Core thesis terms* — glossary only, no implementation detail.

**The framing was wrong at the start.** "Organisation" appears nowhere in the estate's code, scripts
or READMEs — the codebase says `org` consistently. The word was introduced by the *demo narration*.
So this was never drift in the estate; it was a word the demo invented and then overloaded.

**1. No collective noun for the six.** Name the kind instead — "the platform, two regulators and
three institutions". A collective noun flattens exactly the distinction the thesis rests on: these
are *different kinds of party* exchanging signed dependencies across trust boundaries. What is true
of all six and worth saying: each is represented by its own **independent GitHub organisation**.

**2. Roles compose — they are not a partition.** The owner's call, and the estate already proves it:
`platform` is both a **publisher** and a **risk-bearer**, carrying its own strict £10k appetite band
in `estate/platform/honesty/scenarios/platform-appetite.json`. That file's own note says it was kept
local "rather than editing the shared appetite store" because sibling tickets owned that file — which
is precisely why the composability was invisible. Three roles defined: **publisher**, **risk-bearer**,
**adopter**; a party may hold several.

**3. `org` stays overloaded, but documented.** In code it means *risk-bearer* (`tolerance_for(org)`
hard-exits on a party with no band); in infrastructure it means *GitHub organisation*, which all six
have. Renaming it was rejected: `org` is a field name in emitted artefacts and golden digests, so a
rename churns the provenance surface for a vocabulary win. An undocumented overload is the bug; a
documented one is a decision.

**4. "Institution" kept** for `driftwood`/`tuppence`/`ludlow` over "consumer" or "adopter" — it
carries the regulatory weight the proportionality argument depends on, even though "consumer" better
describes the dependency direction.

**5. The demo's entitled sentence**, replacing "Six live organisations — one shared platform, three
regulated institutions, two regulators publishing controls and fines as code":

> Six independent GitHub organisations — a shared platform that prices its own risk like everyone
> else, three regulated institutions, two regulators.

This is only sayable once the split lands. It also recovers the reflexive beat the old wording threw
away: the apparatus refusing to exempt itself is the strongest claim on that slide.

**Surfaced:** the party model is prose-only and nothing validates it, and `platform`'s appetite is
split across two stores. Both folded into a new ticket rather than done here — this estate has just
been bitten three times by assertions that could not fail, so a `roles:` field nothing checks would
be a fourth.
