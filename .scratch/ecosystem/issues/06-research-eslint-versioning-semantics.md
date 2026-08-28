# 06 — Research eslint versioning semantics

Type: research (AFK)
Status: resolved
Blocked by: none

## Question

The owner's instruction for versioning is: 'copy the behaviour of how eslint linting packs are versioned, and how you can supersede, mashup, join them, republish, inner source'. Document precisely how ESLint shareable configs and plugin packs behave: each package's own semver; `extends` and flat-config composition order; overrides and rule severity precedence; peer dependencies and version ranges versus pins; republishing a composed config as a new package; scoped (inner-source) registries. Then map each behaviour onto policy packages: publisher policy, regulator baseline, composed adopter set, tier floor, restatement. Produce the rule set the computed-semver gate and composition must follow, and name every place the current estate disagrees.

## Notes

Re-grill 2. Output: a research note plus a table of current-vs-required behaviour.

## Answer

Research note: [`research/06-eslint-versioning-semantics.md`](../research/06-eslint-versioning-semantics.md).
Primary sources only — eslint.org, the ESLint repo README and `lib/config/flat-config-schema.js`,
node-semver's README, docs.npmjs.com, GitHub Packages, Verdaccio. Every claim there carries its link.

**The packaging model transfers wholesale. The bump table does not.**

What ESLint actually does, and what it maps to:

- **Every pack versions itself.** A shareable config is *"simply npm packages that export a
  configuration object or array"*; a plugin's `meta.version` *"should match the npm package version"*.
  → a party's own gitsign tag. Already true; re-grill 2 ratifies it.
- **Composition is an ordered array, last-wins, purely positional** — *"later objects overriding
  previous objects when there is a conflict"*. → the adopter's party artefact. **The estate departs
  deliberately: it refuses a conflict rather than resolving it by order.** Keep the departure.
- **A severity-only override keeps the inherited options** — *"the second configuration object only
  overrides the severity, so the final configuration for `semi` is `["warn", "never"]"`*. → a
  restatement names an action and never a rule body. `apply_restatements` already does exactly this.
- **There is no floor.** Nothing in any ESLint source lets a shareable config stop a consumer setting
  a rule to `"off"`. → the tier floor re-grill 23 wants **has to be invented**; ESLint gives nothing.
- **Shipping a capability and requiring it are separately versioned.** A new rule is a **minor**;
  adding that rule to `eslint:recommended` is a **major**. → a publisher shipping a policy nobody
  selects is minor; **a regulator adding a control to a published baseline is a major on the
  regulator's own version.** The estate classifies this nowhere today.
- **Deprecation is a minor; `npm deprecate` warns and removes nothing.** → **supersede**, the owner's
  own verb, and the estate has no publisher-side form of it (ADR-0010's `sunset:` is consumer-side and
  opt-in per fleet).
- **A prerelease is published, signed and resolvable but excluded from ordinary range matching.**
  Verdaccio's documented temporary-fork mode is `0.1.3-my-temp-fix`. → both re-grill 11's quarantined
  publish **and** the inner-source temporary carry are the same mechanism.
- **peerDependencies declare compatibility with a host you do not own.** → nobody in the estate
  declares which engine or which catalogue version they compose against; the split diamond is
  discovered at the adopter instead of at the publisher.
- **Scopes bound to private registries; Verdaccio's permanent fork vs temporary carry.** → **inner
  source**, the owner's other verb. The word appears nowhere in the estate.

**The one thing to refuse to copy.** ESLint's semver README states that a **minor** *"might break your
lint build"* and that *"any minor update may report more linting errors than the previous release... we
recommend using the tilde (`~`)... to guarantee the results of your builds."* `CONTEXT.md`'s minor is
stronger: it cannot fail a currently-compliant workload. ADR-0002 already forces the tilde on every
consumer by pinning exactly, so the estate has already paid for the stronger promise. **Copying
ESLint's bump table literally would weaken the contract for nothing.** Read the owner's instruction as
"copy the packaging model", and record the divergence in `CONTEXT.md`.

The note carries the full mapping table, a twelve-rule set for the computed-semver gate and the
composition, and a seventeen-row current-vs-required table. Seven rows are unowned:

- **re-price as a release** (re-grill 8) — sits between tickets 08, 09 and 18.
- **the meaning of minor** — one paragraph in `CONTEXT.md`, recording the ESLint divergence.
- **a regulator's baseline addition as a major on the regulator** — needs an owning ticket.
- **publisher-declared parent compatibility** (the peerDependency shape) — needs an owning ticket.
- **supersede** — no publisher-side form exists.
- **inner source** — no form exists; the word is absent from the whole estate.
- **one live republish edge** — a composed artefact pinned as another party's `implementations`
  parent, so the cross-party conflict path is proved rather than declared.

Plus one contradiction named but not resolved: the composition refuses on six conditions, and the map's
own vocabulary says *"Price and cage; never count, refuse or file."* Six refusals is six gates.

**Ticket 18 unblocks** — rows 1 to 4 of the current-vs-required table are its scope and are now
specified. **ADR-0016 §3** (*"The composed artefact carries no tier and no tier floor"*) is contradicted
by re-grill 23 and reversal 13 and must be **superseded by ticket 09, not quietly edited**.
