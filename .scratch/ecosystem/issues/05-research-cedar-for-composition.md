# 05 — Research cedar for composition

Type: research (AFK)
Status: resolved
Blocked by: none

## Question

Does Cedar's sound-and-complete permissiveness analysis (more-permissive / less-permissive between two policy sets) fit cross-party composition? Specifically: can a composed set (nist -> platform -> driftwood, with a restatement and a cage tier floor) be lowered to Cedar so that 'is the adopter's composed set strictly stricter than its publisher's' is a decidable check, and can a cage spec (CPU, memory, netpol, WAF) be expressed on the same lattice? What does the lowering lose? Compare with `platform/computed-semver/cage_engine.py` Track 2, which already compares cage specs on a partial order.

## Notes

Re-grill 41. The twin's ticket 27 note is the prior art. Output: a research note with a go/no-go recommendation and a minimal lowering example.

## Answer

**No-go now; a conditional go later, and the condition belongs to ticket 09.** Full note:
[research/05-cedar-for-composition.md](../research/05-cedar-for-composition.md). Built
`cedar-policy-cli` 4.12.0 with `--features analyze` plus cvc5 1.3.4 and ran every claim below.

- **The analysis is real and it does decide the question.** `cedar symcc implies`, run both ways,
  decides "strictly stricter" soundly and completely, in 19ms, with a concrete counterexample.
  Ran the lowered nist -> platform -> driftwood set with one restatement (require-nonroot@3.0.0
  Audit -> Deny) and a `restricted` tier floor: driftwood ⟹ platform VERIFIED, platform ⟹
  driftwood REFUTED. A floor loosened to cpu 1000m is refuted naming `cpuMilli: 1000`.
  `cedar-lean-cli analyze compare` gives the ticket's exact four-way
  equivalent/more/less/**incomparable** verdict, but only there, and only as a reference
  implementation.
- **A cage spec does sit on the lattice — and that is the easy, worthless part.** Encode each dial
  as an independent `forbid` and Cedar's allow-set inclusion *is* Track 2's componentwise order.
  Same verdict as `cage_engine.py` `at_least_as_permissive`, for a Rust toolchain, an
  out-of-process solver, a pre-1.0 non-default feature, a hand-written schema and a hand-written
  lowering. netpol is not a dial at all (a boolean generate off the `caged` label, not on
  `CageSpec`'s six fields); priorityClass ranks on a value in another YAML file that Cedar would
  have to inline, reintroducing the bug Track 2 has a named regression guard for.
- **The lowering loses two thirds of the artefact, not the edges.** Of the six composed members
  ADR-0016 tabulates, only 2 have any image: two Deny `ValidatingPolicy`s. Two mutates and a
  generate carry no action; `require-nonroot` is Audit, which is invisible on a deny plane — ran
  it, and Cedar calls the real 2.0.0 -> 3.0.0 tightening "equivalent". (Mitigable: lower an audit
  plane and a deny plane and order the pair.) CEL's `.all()` has no image and never will — RFC
  0021 was rejected *because* quantifiers break the analysis — so it must be hoisted into an
  opaque boolean, which is structurally the same failure ticket 27 used to reject Dogwood. The
  nist, ico and threat edges lower to nothing: coverage, holes and the £ are properties of the
  artefact, not of a request.
- **The one genuine win is unreachable today.** Track 2 has no condition axis. An adopter that
  tightens cpu to 250m in `payments` and loosens to 750m elsewhere reads as a tightening to Track
  2; Cedar refutes it naming `cpuMilli: 750`. That is the whole case for Cedar in this system,
  and ticket 09's tier floor is one value per party, so nothing can hide there.

**Decision handed to ticket 09:** if the tighten-only tier floor may ever be *scoped* — per
namespace, workload or label — componentwise comparison is provably blind and Cedar becomes the
right instrument. If the floor stays one value per party, reuse Track 2 and drop Cedar.
Second trigger: a second `implementations` publisher with overlapping match sets, when per-rule
restatement stops being sound.

**Free steal, no Cedar required:** make `at_least_as_permissive` return the offending *value*
beside the field name. One line, and most of the readable half of what Cedar offers.

**Correction to ticket 27:** its "sound and complete" citation holds — now Lean-proved, not just
on paper — but the guarantee covers Cedar's deliberately small fragment, the estate does not write
in that fragment, and the lowering that bridges the gap spends the completeness the citation was
reaching for.
