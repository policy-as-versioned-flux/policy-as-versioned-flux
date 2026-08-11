# 48 — Substrate recipe format, seeded regeneration, and the authored-or-derived spike

**What to build:** The substrate is **regenerable, not merely stored**: a versioned recipe plus a seed reproduces it.

This ticket also runs a **cheap spike on a structural tension that would otherwise surface at ticket
52 or the final coherence audit**. `substrate-generator` is a skill — grade-5, non-deterministic —
yet regeneration demands determinism-given-pins for anything derived, and regenerated substrate is
not byte-reproducible across model versions. So: is regenerated substrate **authored** (content-
hashed, outside attestation) or **derived** (attested)? Answer it here with a toy substrate and a
`twin verify` attempt, for pennies, rather than architecturally later.

**Blocked by:** 42, 10

**Status:** done (2026-08-11)

**Reading list:** Decision tickets 12, 14. Spec stories 3, 55, 64.

- [x] Recipe format is versioned; recipe + seed regenerates a toy substrate.
- [x] **Spike answered and recorded**: regenerated substrate is classified authored or derived, with the reasoning and its consequences for pin capture and anomaly detection written down.
- [x] The content-hash exception from ticket 01 is exercised for real.
- [x] If the answer is 'authored', the boundary is explicit and `derived_never_human_signed` is checked against it.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-11)

`twin/substrate.py`, `twin/capabilities/synthetic-substrate.yaml`, `tests/test_substrate.py`, one
harness guard (`substrate_regeneration_is_not_deterministic_so_it_is_authored`).

- A versioned recipe format (`twin.substrate-recipe/v1`: prompts/templates, seed, model version,
  planted-signal schedule — decision ticket 12's "generator recipe") plus a seed regenerates a toy
  substrate byte-for-byte, on any machine, forever (`generate_deterministic`).
- **The spike, answered:** regenerated substrate is classified **authored, not derived**. A
  stand-in for the real generator (`generate_non_reproducible`, drawing on `os.urandom` — entropy
  no recipe can pin, the one honest thing a live model call over an API actually is) does not
  reproduce from an identical recipe on two calls in a row, which is why decision ticket 14's
  determinism-given-the-pins requirement cannot be asserted for real substrate generation. The
  reasoning and its consequences are written into `twin/substrate.py`'s module docstring and
  `twin/README.md`'s "The substrate recipe format" section.
- The content-hash reference form (`twin/blob.py`, build ticket 01) is exercised for real for the
  first time: a real, non-empty generated blob's reference is carried through the exact `twin
  sense` pipeline ticket 01 built the hook for, and resolves against the real bytes.
- **The "twin verify attempt":** a `sense` artefact referencing real substrate reproduces cleanly
  from its pins via `reproduce.reproduce()` — without the substrate bytes ever being written
  anywhere `twin` can read them, because `reproduce.py`'s `sense` branch only re-reads the
  committed reference string. The reference participates in derivation; the bytes behind it never
  do — the concrete finding that makes "authored" the honest answer rather than an assertion.
- The boundary is checked, not merely stated: an artefact carrying substrate content itself, marked
  `authored`, accepts a human signature; an artefact that only references the substrate by content
  hash stays `derived` and `derived_never_human_signed` still refuses one, unchanged from ticket 01.
- `twin/capabilities/synthetic-substrate.yaml` (owning ticket 12) ticks AC 5 ("generation method +
  reproducibility/versioning decision"), computed at 1/7 — `partial`, never asserted as more.
  Adding it moved `Capabilities.load().digest`, embedded in every artefact's `pins.tool` — golden
  digests re-blessed (`twin verify --bless-goldens --authorise "decision ticket 12 — ..."`), the
  same re-blessing build tickets 43 and 44 needed for the identical reason.

Not built: the real seeded-LLM generator (49), spine anchoring against the public record (50), the
fidelity eval suite (51) — deliberately, per this ticket's own brief ("a cheap spike... for
pennies, rather than architecturally later").
