# 11 — Four gate rules and two `CONTEXT.md` edits from cs-07

Type: task
Status: split
Blocked by: 10

**Split on 2026-08-22 into implementation tickets.** This ticket holds the reasoning. The four rules
live in [26](26-four-extra-gate-rules.md). The `platform-machinery` class and the spec-level restatement
of major live in [22](22-pairing-rules-and-platform-machinery.md) and
[21](21-cage-spec-comparison-and-computed-bump.md). ADR-0011 and the `CONTEXT.md` edits live in
[30](30-adr-0011-and-context-edits.md).

## Question

Spun out of [ticket 07](07-platform-version-under-the-same-rule.md), which settled the design. These
rules join the gate cs-05 specified. Rule 3 needs the mandatory-member list that
[ticket 10](10-render-mandatory-members.md) produces.

**The four rules:**

1. **Read prior versions from their tags, never from HEAD.** The delivered `1.0.0` comes from tag
   `policy/v1.0.0`, but the gate would naturally read `distribution/policies/v1.0.0/` at HEAD. A
   hand-edit there would fool the gate about what `1.0.0` means. Add a **frozen-tree check** that fails
   when a HEAD copy of a released tree differs from its tag. This makes cs-05's phrase "the window as it
   stood before this release" mechanical rather than aspirational.
2. **Re-render only the tree being cut.** Same shape as cs-03's corpus check: regenerate, diff, fail.
3. **Refuse a release that removes an enforcement surface from a version.** A refusal, not a bump class,
   so the number stays honest. Ticket 10's mandatory-member list **is** the enforcement-surface list, so
   the rule is a set comparison against it.
4. **Refuse an array element with an empty `commit`.** Both elements carry `commit: ""` today, so every
   per-version `GitRepository` is pinned by tag alone. Ticket 09 fills them. Without this rule the field
   silently empties again on the next hand-edited element.

**Two changes to rules cs-03 and cs-06 already hold:**

- **cs-06's family pairing needs the `platform-machinery` class.** It pairs on
  `(identity, name-with-version-stripped)` and fails on an unversioned member. The orphan guard carries
  no identity label at all, and cs-07 made it legitimately unversioned, because the platform tag numbers
  it. Give it the identity `platform-machinery` and teach cs-06 that this family is numbered by the
  platform tag, not by a claim. Make it a class, not a by-name exclusion. The next machinery object must
  not slip through.
- **Restate "major" at spec level, not dial level.** The rule is: any change where the new cage spec is
  not at least as permissive as the old one. `cage-tier` changes more than dials. It appends a
  `waf-sidecar` container at restricted and quarantine, sets `priorityClassName`, flips
  `readOnlyRootFilesystem` and `runAsNonRoot`, and applies a second JSONPatch dropping `ALL`
  capabilities when the tier hardens. An enumerated list of surfaces rots on the next mutation added.

**Two `CONTEXT.md` edits:**

- One sentence on reset on bump. Inherited from cs-05.
- The `platform-machinery` class, named, so a reader knows which policies are numbered by the platform
  tag rather than by a claim.

**The gate never estimates viability.** Print the limit instead, in one sentence: the ceiling moved
down, and the gate does not know whose workload dies at the new number. A viability rule needs a
threshold, and cs-04 banned thresholds because a threshold invites tuning the corpus until the release
passes.

Also still owed from cs-05: **ADR-0011** records the gate and cross-references ADR-0002.

## Comments

Raised 2026-08-22 from ticket 07's grilling. See that ticket's sections 5 and 7 for the reasoning, and
section 9 for the two limits that these rules deliberately do not close.
