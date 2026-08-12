# 14 — Provenance & attestation: signal → inference → decision → action

Type: grilling
Status: RESOLVED (2026-08-05)
Blocked by: 07, 08, 10, 11 (all resolved)

## Question

Every signal, inference, decision and action attestable and auditable end to end — including
**provenance of inferences, not just of data** (fable's missing-workstream point).

**Already determined by prior tickets (not re-litigated here):**
- Git-native source of truth (07) → **commits are the provenance substrate**; every change has an
  author, a timestamp and a diff for free.
- Evidence grades carry **who claimed it, from what evidence, at what confidence** (08).
- An **override is a provenanced claim** that is itself scored (11).
- **Contests and their outcomes are recorded** (10).
- **Full transparency** of method and content (10).
- Every scenario execution pins **{graph-version, world-model(s), time, information-regime}** (13).

**Genuinely open:**
- **What is attested** — the artefact, or the reasoning chain that produced it?
- **Actor identity** — do agents as well as humans sign? What identity does a non-human actor carry,
  and what does its signature mean?
- **Depth of the chain** — how far back must a recommendation be traceable, and is the chain
  reconstructable or materialised?
- **What attestation is FOR here** — audit after the fact, tamper-evidence, or reproducibility?

## Acceptance criteria
- [ ] Decided: artefact attestation vs reasoning-chain attestation (or both, with the seam).
- [ ] An actor-identity model covering humans and agents, and what a signature asserts.
- [ ] The chain-depth rule for a recommendation, and materialised-vs-reconstructable.
- [ ] A stated purpose for attestation, consistent with the transparency decision.

## Decided so far (grilling 2026-08-05)

**Q1 — (c) SIGNED ARTEFACTS + RECONSTRUCTABLE DERIVATION.** Sign the outputs; pin the inputs; recompute
the "why" on demand rather than storing it a million times.
- **(a) artefacts alone fails contestability** — ticket 10 rests on being able to ask *"which claim
  produces this number?"*; without a mechanical answer, contestability degrades into an argument about
  memory.
- **(b) materialised chains** is what we want epistemically but is enormous: one recommendation touches
  thousands of nodes, and storing full derivations for every scheduled execution across the ensemble
  would dwarf the model.
- **(c) works *because of* ticket 07:** with git-versioned text as source of truth and everything else
  derived and rebuildable, **pinning the inputs is equivalent to storing the derivation**. Ticket 13
  already pins {graph-version, world-model(s), time, information-regime} on every execution — exactly the
  pin required. The chain is **reconstructable by re-running**.
**Non-trivial condition that makes this honest: derivation must be DETERMINISTIC GIVEN THE PINS.** LLM
binding and inference are not naturally deterministic, so **seeds, model versions and prompts are pinned
too** — the same rule ticket 12 set for the substrate generator. **If we cannot reproduce the derivation,
the attestation is a claim rather than a proof.**

**Q2 — (c) BOTH, WITH DELEGATION — and the two signatures assert DIFFERENT THINGS.**
- **Human signature = accountability for a judgement.** "I looked at this, I stand behind it."
- **Agent signature = attestation of origin and reproducibility.** "This artefact was produced by this
  agent, at this model version, with these inputs and this seed." An agent has no accountability to give;
  claiming otherwise would let agent output silently inherit human endorsement — **the oracle problem
  ticket 10 designed against**. A signed agent artefact must read as *"mechanically produced and
  reproducible"*, never *"someone competent agreed with this."*
- **Delegation chain** carries the accountability the agent lacks: a human authorised this agent to operate
  in this scope, and answers for it. Gives the carried-forward misuse catalogue (ticket 10) something
  concrete to attach to.
- The agent signature is effectively **the pin, signed** — it makes Q1's "you can recompute this"
  verifiable rather than asserted.

**Q2b — SIGNATURES CARRY RUNTIME ATTESTATIONS, AND ATTEST THE *ABSENCE* OF HUMAN INVOLVEMENT** (human,
2026-08-05: *"like a CI build artifact being signed by CI"*).
Signatures carry **runtime, model versions, configuration** — and attest **human involvement, preferably
its lack**.
**The inversion that matters: for a DERIVED artefact, human involvement is a defect, not a warrant.** A
hand-touched derived output can no longer be recomputed, so *"no human hands; produced hermetically by
this pipeline, at this model version, from these pinned inputs"* is exactly what makes Q1's
reconstructable-derivation claim hold.
**Consequence — ticket 07's authored/derived split becomes CRYPTOGRAPHICALLY ENFORCEABLE:**
- **Authored** (overrides, causal claims, constraints, world-models) → **human-signed, carries
  accountability**.
- **Derived** (inferred positions, forecasts, roll-ups, blast-radius, D/K/R metrics) → **machine-signed,
  attesting absence of human involvement**.
- **A derived artefact bearing human fingerprints is a detectable anomaly** — someone manually adjusted a
  number that was supposed to be computed. Previously an undetectable failure mode; now caught by
  construction.
**Prior art to build on (not to reinvent):** **SLSA build provenance / in-toto attestations** assert
precisely this shape (builder identity, hermetic build, no manual steps, pinned inputs); **sigstore /
gitsign** for the signing itself.

**Q3 (derived, not separately grilled) — chain depth + purpose.**
- **Depth:** unbounded but **recomputable** — a recommendation traces to its forecasts, to the execution's
  pins, to the graph version, to the signals, because each layer pins its inputs. Nothing is materialised;
  everything is re-derivable.
- **Purpose:** **reproducibility first**, which subsumes the rest — signing gives tamper-evidence, git
  history gives audit. Under ticket 10's full transparency this is not about secrecy but about being able
  to **prove what was computed and re-derive it**.

## RESOLVED (2026-08-05)

**Sign the artefact, pin the inputs, recompute the why.** Human signatures assert accountability for
judgements; agent signatures assert reproducible origin, carrying runtime/model/config attestations and
**attesting the absence of human involvement**, CI-style — which makes ticket 07's authored/derived split
enforceable and manual tampering with derived values detectable. Derivation must be deterministic given
the pins (seeds, model versions, prompts pinned) or the attestation is a claim, not a proof.

## Acceptance criteria — all met
- [x] Artefact vs reasoning-chain attestation decided (signed artefacts + reconstructable derivation).
- [x] Actor-identity model for humans and agents, and what each signature asserts (accountability vs
      reproducibility, plus delegation).
- [x] Chain-depth rule and materialised-vs-reconstructable (reconstructable via pins).
- [x] Stated purpose, consistent with the transparency decision (reproducibility first).
