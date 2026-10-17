---
status: accepted
---

# An adopter explicitly retires a measured policy window

Delegated decision, 2026-10-17, under ADR-0025 and eco-system ticket 150.

The compiler normally inherits every policy line its implementation parent serves. That remains
the default. The September 10 compiler split deliberately avoided filtering inherited policies
(adopter README, “Compiler tools and accepted implementations”). Ticket 132 likewise left
retirement unconditionally refused because accepting it “would need a new format, and nothing
asks for one”. Ticket 150 now asks for exactly that operation: after a genuine scheduled engine
baseline, one adopter retires the incompatible lines, delivers its signed composition, and only
then changes its engine. The old major-acceptance record accepts a carried version and cannot
express a removal.

## Decision

A **consumer retirement** is the adopter's reviewed decision to remove exact versions from its
own composed window, bound to an exact signed implementation parent, a retained window and a
measured engine transition. It removes those versions for every workload of that adopter. It is
not selected implicitly by engine incompatibility and is not an exception for a named adopter.

The new record is an explicit input under `implementation-retirements/`. No record means the
whole parent window. A valid record must name the adopter and publisher, the exact parent
version/tag/commit and complete before-window, disjoint retired and retained sets whose union is
that window, the current and planned engines, and the delegated decision's author and basis.
Every retained line and the machinery must declare support for both engines under
`every-served-body-v1`. Every versioned workload the adopter serves must claim a retained line.

Before a record can alter composition, its scheduled baseline must be independently reproducible:
the official GitHub run attempt identifies the source, event and default branch; the unchanged
original gitsign commit verifies that workflow's exact identity, source and event; the original is
an ancestor of the actual public default branch and the tree under composition; and all original
JSONL appends, including the OSCAL/PolicyReport capture, remain byte-for-byte present exactly
once. The source's own engine declaration must equal the baseline engine. An asserted receipt is
not a substitute for any of these checks. Failed or unavailable checks refuse with a named
missing instrument; they never create a green measurement.

The compiler renders only the retained policy bodies and renders every version-dependent
machinery allow-list against the same retained set. Retired claims still reach the orphan cage
and report, including its UPDATE hold. It does not edit a frozen publisher tree or the publisher's
array. The publisher continues to serve three lines, and other adopters continue to inherit them.

The adopter gate still computes **major** for each retirement. A separately validated exact
consumer-retirement record supplies the review decision beside that bump; it never changes the
bump. Existing added-major acceptance and signature checks remain. An unrelated removal, a new
parent, an unaccepted major, a mismatched engine or a changed baseline cannot borrow the record.
The record and resulting composition become authoritative only through ordinary reviewed source
delivery and the adopter's normal signed release. There is no bypass merge or signing identity.

For ticket 150 the order remains: publish the genuine scheduled 1.18.2 PolicyReport baseline;
retire 5/6 while still declaring 1.18.2; cut and verify the signed composition and move its delivery
pointer; move only Ludlow's declaration to 1.19.1 and recompose; then compare the next genuine
scheduled sample. Rehearsals and dispatched samples do not close that ticket.

## Alternatives and consequences

Removing 5/6 from the publisher's default array would reduce its declared coexistence window to
one and affect future consumers. A separate publisher release branch would still introduce a
one-line publisher window and duplicate lifecycle administration. Editing the frozen bodies or
claiming unmeasured support is false. Silently filtering by the declared engine hides a retirement
and moves policy before review. An explicit adopter decision preserves these distinctions at the
cost of a new record and its reproducible validation.

This amends ticket 132's unconditional-retirement admission decision and the September 10
no-filter implementation choice only for this explicit contract. It does not weaken ADR-0011's
computed bump, the publisher's coexistence checks, or ordinary unsigned/unsupported-pairing
pricing. A compiler release is selected under delegated software-interface SemVer; the existing
policy bump oracle explicitly excludes bare compiler tags and must not be described as computing
that software release number.
