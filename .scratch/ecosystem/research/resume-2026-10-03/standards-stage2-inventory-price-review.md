# Independent stage2 source review — 2026-10-03

## Inventory provenance

No hard finding. Each `.estate-clone/{driftwood,tuppence,ludlow}/inventory/PROVENANCE.json` matches its own repository origin, actual annotated v3.0.1 tag object, peeled commit, preparatory apps-source declaration and complete tagged image graph. Inventory byte SHA256 values match. All five primary report SHA256 values, reported artifacts and observed image digests match; the real inventory normalizer reproduces every existing row, canonical row hash and vulnerability-row count (0/212/395/9/228).

The exact tag objects and commits also match the prior complete genuine Git/Rekor/Actions identity verification evidence. A new local offline cryptographic rerun could not open the user TUF-cache lock outside the workspace; no successful new rerun is claimed. The recorded scanner executable hash matches, cached database update is explicitly skipped, and the provenance denies release or cluster activation. No live observation, policy/compiler upgrade or inventory adoption follows from this local preparation.

## CVE price transitions

No hard finding in `compose/composition.py` price_parent around 3597–3675 or new `compose/test_feed_price_transitions.py`. Seven public pricing tests pass independently. Actual scenarios alone reach the money/tier selector. An absent old intersection keeps old_price/old_tier null with an old absence reason; an absent new intersection retains known old money and leaves new money/tier null. Measured comparisons between two priced sides remain intact. Missing inventory, missing required FX and malformed scenarios still refuse. The price-entry consumer preserves absent per-customer money, and no tier movement is asserted without two measured tiers.

## Relocation fix

The original public three-adopter relocation replay was red before the fix: Driftwood and Tuppence failed only composed/HANDBOOK.md byte comparison; Ludlow passed. `_portable_reason` around 5059 stripped resolved paths while real exceptions named lexical symlink aliases.

The narrow helper fix now normalizes both absolute lexical and resolved spellings of each declared source, preserving longest-prefix precedence. No handbook context, frequency, monetary value or tier rule changed. Three regressions pass independently, including the real compute_switching→compute_prices→price_twin refusal path with null amount/over_pin_life, a named reason and preserved known unpriceable money. No hard source finding remains. Cloud's original full public compose/relocated-byte replay now passes for all three adopters (53/50/54 rendered files), confirmed from its proof. No shared composed files were written and no foundation adoption is claimed. The exact pre/post compiler typecheck retains 131 existing diagnostics and introduces none; it is not a clean typecheck.

This review changed no source or external state.

Evidence and release-preparation patches:

- [Inventory joins](inventory-provenance-independent-review.json), [original relocation red](standards-stage2-alias-original-red.json), and [final all-three replay](adopter-stage2-compose-replay.json).
- [CVE transition patch](../../patches/resume-2026-10-03/feed-price-transition-fix.patch) and [report](feed-price-transition-fix.md).
- [Alias patch](../../patches/resume-2026-10-03/portable-reason-alias-fix.patch), [report](portable-reason-alias-fix.md), and [unchanged typecheck delta](portable-reason-typecheck-delta.json).
- [Previously validated handbook null-amount patch](../../patches/resume-2026-10-03/platform-handbook-unpriced-only.patch).
