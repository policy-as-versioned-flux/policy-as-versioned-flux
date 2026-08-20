# 03 — Settle what "organisation" means before the split hard-codes the ambiguity

Type: grilling
Status: open
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
