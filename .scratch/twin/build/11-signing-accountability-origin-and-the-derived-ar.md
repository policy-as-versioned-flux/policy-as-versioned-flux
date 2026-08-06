# 11 — Signing: accountability, origin, and the derived-artefact anomaly

**What to build:** **Human signatures assert accountability for a judgement. Agent signatures assert reproducible
origin only** — runtime, model version, config — so agent output never inherits human authority.

The consequence is the interesting part: signatures attest the *absence* of human involvement,
CI-style, which makes the authored/derived split cryptographically enforceable. A derived artefact
carrying human fingerprints becomes a **detectable anomaly** rather than a convention breach.

Role-not-person signatures land here: accountability attaches without creating a personal target.

**Blocked by:** 10

**Status:** done (2026-08-06)

**Reading list:** Decision tickets 14, 15. Spec stories 62, 63, 73.

- [x] Human and agent signature types are distinct and non-interchangeable.
- [x] `derived_never_human_signed` goes live; a planted human-signed derived artefact fails the check.
- [ ] An agent signature carries runtime, model version and config, and asserts nothing about correctness.
- [x] Signatures bind to roles, not named individuals, and the role register is versioned.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-06)

`twin/sign.py`, `twin/roles.yaml`, a rewritten `twin/attest.py`, and `twin sign` /
`twin verify <artefact> --attestation`.

- **Two signature types that never substitute.** A human signature asserts accountability for a
  judgement; an agent signature asserts reproducible origin and names, in the artefact, what it does
  **not** assert: correctness, accountability, human review. `sign.verify` refuses a type mismatch
  *before* it looks at the value, so an agent signature cannot be passed off as accountability by
  moving one field, even though its own value verifies perfectly.
- **The anomaly is detected, not trusted.** Emission already refused a human signature on a derived
  artefact. The remaining way to plant one was to edit the sidecar afterwards, so sidecars are now
  **read back**: `attest.check` recomputes the subject digest, verifies every signature, and reports
  a derived artefact carrying human involvement as a problem. The invariant plants exactly that.
- **Roles, never people.** A human signature names a role from `twin/roles.yaml` and carries the
  register's version and digest, so a role later renamed or withdrawn cannot silently change what an
  old signature meant. Seven personal field names (`email`, `identity`, `person`, …) are refused both
  when a sidecar is built and when it is read.
- **Untyped counts as human.** `is_human` returns true for anything that does not positively identify
  itself as an agent, so deleting or misspelling the type field is not a way past the refusal.
- The signature lives in the sidecar and never in the artefact: a keyed value in the envelope would
  break `identical_pins_identical_bytes` on the first machine holding a different key.

**`ponytail:` HMAC-SHA256 with a key from `TWIN_SIGNING_KEY`, and the ceiling is named.** A shared key
proves possession, not identity — anybody holding it can produce any role's signature. The upgrade is
sigstore/gitsign with in-toto subject digests, which decision ticket 14 already names; the shape here
(subject digest, role binding, register pin, typed assertion) is what that upgrade keeps. With no key
present nothing is signed and the sidecar says which variable is missing, rather than carrying a
placeholder that reads as signed.

Not built: an agent signature carries runtime and tool version but **no model version and no config
digest**, because nothing in this system is produced by a model yet — skills land at build ticket 42.
Two of that criterion's three clauses hold, so it stays unticked rather than being ticked on the two.
