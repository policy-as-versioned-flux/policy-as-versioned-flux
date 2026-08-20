# 17 — An institution answers to many masters, and the estate models one

Type: grilling
Status: resolved
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

## Answer

Resolved by grilling, 2026-08-20. The owner's answer overrode the recommendation on conflict
handling, and the correction is recorded rather than smoothed over.

**1. Overlap and duplication are permanent and expected — not a defect to normalise away.** Owner:
*"there will always be duplications and overlap."* So obligation sources are **one kind** in the sense
that they share machinery (signed, versioned, pinned artefacts an institution consumes), but the
estate must not try to deduplicate the *obligations themselves*. Two regulators demanding overlapping
controls is the normal case, not a modelling error.

Evidence the shared kind is already wanted: `ico` runs a **parallel feed stack** —
`estate/ico/schema/{v1,v2,sign.sh,to_fair_scenario.py}` — a near-duplicate of
`estate/platform/feeds/`, with its own key and its own beat. Two near-identical loaders is the estate
telling you it has a general concept it has not named.

**2. Obligations scope per *workload*, not per institution.** Owner: *"they may not all apply to all
workloads."* Today the scope is institution-wide — `nist-pin-configmap.yaml` is
`namespace: driftwood`, and the pin covers everything in it. A workload handling card data is subject
to PCI; one that never touches it is not. **Gap: there is no per-workload obligation scoping.**

**3. A single breach can trigger several consequences, and the £ must take the worst case.** Owner:
*"the org may be subject to multiple fines or other consequences for a single breach, so you may need
to consider the worst case scenario."* **Gap, and a significant one:** `fair.py` models **one
loss-magnitude triple per risk** (`lm: [min, mode, max]`), and `simulate()` sums magnitude *per event
within one regime*. `ico/schema/to_fair_scenario.py` reads *regime → violation-type → fine
formula/cap* — one regime at a time. Nothing aggregates an ICO fine plus a PCI penalty plus SLA
credits plus litigation arising from the *same* incident. Raised as its own ticket.

**4. Conflict: overlap is normal; genuine deadlock gets a deferred reconciler.** The recommendation
here was *refuse to render*, and it was **not** taken. The owner's position is better: most "conflict"
is ordinary overlap that should simply be carried, and only genuine deadlock — two obligations
demanding incompatible things — needs handling. That handling is **explicitly deferred**: *"we may
later need to consider an overrides or reconciler stage where the org or other providers can manually
manage conflicts."*

Recorded as deferred rather than designed. Note the shape when it comes: an override is dangerously
close to an exemption, which is a banned concept — so a reconciler must resolve *between obligations*,
never waive one.

**5. Curated bundles exist as a convenience, never as the only path.** Platform may publish
meta-packages bundling upstreams and pinning versions, but an institution can always pin sources
directly. Mandatory bundles would re-introduce through the back door the intermediation that was
rejected for regulator pins — platform as a single point of failure for regulatory currency.
