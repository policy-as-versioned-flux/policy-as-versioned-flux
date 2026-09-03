Round 3 of the sampler's wait order (eco-system ticket 60, landed by ticket 81).

**What.** `.github/workflows/drift-sample.yml` waits for the kyverno admission controller and
flux-operator BEFORE it applies `gitops/composed/`, and waits for the Kustomizations and
ResourceSets AFTER. One file, 4 lines moved.

**Why.** The round-2 fix (merged 2026-09-01) mis-ordered itself: its second string replace hit the
first occurrence of the kyverno wait line, the one it had just inserted, so the executed order kept
the kyverno wait below the composed apply and ran an empty ResourceSet wait above it. The composed
apply raced the webhooks; tuppence and ludlow kept recording 16 of 16 rendered objects absent
(runs 33558854558, 33558858820). Driftwood passed only because an unrelated 3-minute wait gave
flux-operator time to retry.

**How verified.** The hub gate now grades the order in every adopter's checkout
(`verify/sampler-wait-order/verify-sampler-wait-order.sh`, with a selfcheck that fails round 2's
order, a duplicated wait and a missing wait). Against this branch it reads
`kyverno wait -> flux-operator wait -> composed apply -> Kustomization waits -> ResourceSet waits -> five-fact sample`.
The proof that matters is the next **scheduled** drift-sample run after merge, not a dispatch:
its `drift/samples.jsonl` line should record facts 4 and 5 true for the composed source.

**Cage.** The commit touches no observation path and mints nothing; it is a workflow edit
reviewed and merged by the other hand.
