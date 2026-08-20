# 03 — What represents "currently-compliant workloads"?

Type: grilling
Status: open
Blocked by: 01

## Question

The rule is defined against *currently-compliant workloads*, and nothing in the estate represents
that population. `estate/platform/shift-left/fixtures/` holds exactly two pods
(`workload-flip.yaml`, `workload-unversioned.yaml`), authored to demonstrate a flip — not to be
evaluated against.

A computed bump is only as good as the corpus it is computed over, and this is the ticket where that
is either taken seriously or quietly fudged.

**Decide:**

1. **What the corpus is.** Options: the estate's own deployed workloads harvested from the clusters;
   a hand-authored matrix of pod shapes chosen to span the policy surface; generated permutations
   over the fields the policies actually read; the institutions' real fixtures; or some combination.
2. **Who owns it.** One shared corpus in `platform`, or one per institution? An institution's real
   workloads are the honest population for *its* upgrade decision, but `platform` cuts the release —
   and after the six-org split they are different repos in different organisations.
3. **How it stays honest.** A corpus curated by the same people who choose the bump can be curated
   *toward* the bump they want. What stops that? Generation from the policy surface rather than
   hand-selection is one answer; signing and versioning the corpus is another.
4. **Whether it must be exhaustive.** It cannot be. That is fine only if the incompleteness is
   *stated* — see the coverage ticket, which this blocks in spirit.

Blocked by the rederivation ticket, whose "cannot distinguish X without Y" findings name the
properties the corpus must actually have — rather than guessing them now.
