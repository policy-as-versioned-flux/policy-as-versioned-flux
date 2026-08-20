# 17 — An institution answers to many masters, and the estate models one

Type: grilling
Status: open
Blocked by: none

## Question

Surfaced resolving *Split mechanics and cross-org verification*. Owner: platform could publish
**meta/curated packages** that bundle upstreams and pin versions; a consuming org may be subject to
**more than one regulator** — ICO/GDPR *and* PCI, say; and **customer SLAs load in the same fashion**.

The estate models one regulator catalog (`nist`, pinned directly by each institution) plus one penalty
schema (`ico`, pinned by nobody, arriving by another route). A real institution carries several
obligations at once, from sources that are not all regulators.

**Decide:**

1. **Is an obligation source a first-class kind?** Regulators, customer contracts and internal
   standards all impose controls an institution must satisfy, and all could be signed, versioned,
   pinned artefacts. Is "obligation source" one concept with several instances, or are a regulator
   catalog and a customer SLA different enough to model separately?
2. **Do curated bundles exist, and who owns them?** A platform-published meta-package pinning a set of
   upstreams is a distro metapackage — convenient, and it re-introduces exactly the intermediation
   that was just rejected for direct regulator pins. If platform can bundle, it can also be a single
   point of failure for currency. Does a bundle *replace* direct pins, or sit alongside them as a
   convenience an institution may decline?
3. **What happens when obligations conflict?** Two regulators, or a regulator and a customer SLA, can
   demand incompatible things — a data-residency clause against a retention rule. Does the estate
   detect the conflict, pick by some precedence, or refuse to render? Note this is the first place the
   estate would need a notion of obligation *precedence*, and there is none today.
4. **How does a customer SLA differ from a regulator catalog in the £?** Breaching a regulator's rule
   risks a fine (the `ico` schema already prices these). Breaching a customer SLA risks credits,
   churn, or litigation — and it is the mirror of the vendor-recourse decision on the
   govern-what-you-don't-control map, where *you* are the customer holding the indemnity. Same
   machinery, opposite direction.

**Scope note:** this expands what the estate models, beyond making it multi-org. If it turns out
large, it is a candidate to spin out rather than to swell this map — but the split's Renovate wiring
needs at least the shape of the answer, so it is recorded here and the release/Renovate ticket is
made to wait on it.
