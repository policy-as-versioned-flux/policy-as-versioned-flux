# Skeptic verdict on F4 (scope-and-coherence) — REFUTED as stated

Claim under test: "truth.yml never creates a cluster, so 11 of the 84 checks — precisely the ones
that would observe principle 2 and §4 step 4 — SKIP on every citable run, while the estate's own
rule forbids citing the local runs that can observe them."

## 1. The quoted grep evidence does not exist

    $ cd /Users/cns/httpdocs/controlplane/policy-as-versioned-flux
    $ grep -n "kind\|cluster" .github/workflows/truth.yml
    (no output)
    $ git show origin/main:.github/workflows/truth.yml | grep -n -i "kind\|cluster"
    (no output; exit 1)

The auditor reports this grep "returns only the CLI-install lines (78-91)". It returns nothing.
truth.yml:78-91 installs kyverno, cosign and flux and contains neither word. The underlying fact
(truth.yml creates no cluster) is true; the quoted evidence for it is fabricated.

## 2. The count of 11 holds; one reason string is misquoted

Run-21 captures, read from origin/main (a209496, "truth: record run 21"):

    git archive origin/main talk/captures | tar -x -C <scratch>

82 capture files = pass 57 + fail 7 + skip 18 (total 84 counts the 2 exclusions). Exactly 18
captures end in a SKIP line (verify-all.sh:63-70 grades by exit code and prints `tail -1`).
Eleven of those 18 skip for want of a cluster:

    platform/access, platform/currency-controller,
    platform/distribution/verify-declared-versions-admit, platform/engine, platform/eud,
    platform/graded, platform/identity/verify-federation, platform/identity/verify-identity,
    platform/posture/verify-posture-projection, platform/verify-source-verification,
    tuppence/reset/verify-reach-secrets

The auditor's list is correct. The reason string is not uniform: ten read "... kind cluster
'driftwood' is not listed by kind get clusters"; `.estate-clone_tuppence_reset_verify-reach-secrets.out`
reads "SKIP: kind cluster 'driftwood' does not exist".

## 3. §4 step 4 is NOT among them — it is observed on the citable run, and graded FAIL

`talk/captures/verify_e2e_verify-e2e-step4-flux-reconciles-cage.out` on run 21:

    five-fact sample 2026-09-01T21:07:22Z on cluster dsample-33558850420 (run 33558850420), 3 sources
    ... 15 facts, 14 true, fact_2 FALSE for driftwood-composed (cert not yet valid) ...
    FAIL: the scheduled lane sample observes a step-4 fact false

Step 4 is observed-false on a real cluster, not could-not-look. So is the composed-set-in-force
claim in driftwood/ludlow/tuppence `verify-reconcile` (three of run 21's seven FAILs).

The cluster is real and it is in CI. `units/driftwood/.github/workflows/drift-sample.yml:118-127`
brings up an ephemeral KinD cluster with a fresh name against the *real* remotes, installs Flux,
the gitsign verifier and the composed Kyverno set, takes the sample, signs it and commits it on
the observation lane. `units/driftwood/verify-reconcile.sh:10-33` then grades that sample
cluster-free, first, so the citable hub run consumes it.

This was a deliberate design decision, not an oversight:
- `.scratch/ecosystem/issues/16-...md:66` (C12): "Q3(a) makes the §4 step-4 live tail observable
  inside a CI run (ephemeral KinD in Actions)... If Q3(a) lands, 20 Q2(a) is the honest option and
  NORTH-STAR §5 ... is kept."
- Ticket 60 (`Status: resolved`) is exactly this rewire; the commit log records "ticket 60
  resolved: the gate grades from real signed samples on TRUTH run 20".

The auditor's own ownership paragraph concedes the sample lane covers step 4 — which contradicts
the claim sentence it is attached to.

## 4. The rule the finding invokes does not say what it is used to say

- NORTH-STAR.md:57 (§5): "Every live tail has exactly three outcomes: observed-true,
  observed-false, could-not-look. Could-not-look prints as SKIP with the reason." A SKIP is the
  *designed* honest outcome, not a breach of §5. Principle 6 (NORTH-STAR.md:34): "A green that
  could not look is a red."
- map.md:78 says "A hand-taken sample is a rehearsal and is never cited. The five-fact grader
  refuses any sample whose run id, committing identity or signature does not come from the
  observation lane." That forbids *hand-taken* samples, and in the same sentence names the lane
  that makes a machine-taken cluster observation citable. It is not a bar on citing runtime
  observation.

Therefore "the only permitted instrument cannot look and the rule forbids citing what can" is
false, and "permanent as truth.yml is written" is false twice over: the mechanism that closes it
deliberately does not live in truth.yml, and it is already shipped and firing in one adopter.

## 5. What actually survives

A narrower, principle-2-only claim, which I confirm:

The eleven cluster-dependent live tails above are could-not-look on every citable run, and the
observation lane does not yet stand in for them. The lane's five facts are reconciliation facts
(Ready at pin, tag signature at the source boundary, applied revision, byte-equal render, Flux
inventory) — `drift-sample.yml` installs the Kyverno admission controller and the composed
policies but records no admission-refusal fact. So no citable check today observes a cage
refusing or tightening a workload, a human or a device *in force on a running cluster*; that
claim rests on offline proofs plus local rehearsals. I found no ticket owning the widening
(tickets 03, 16, 20, 40, 52, 60 all `Status: resolved`; 74 is step 3, not this; map.md's "Not yet
specified" and the 54-67 order of attack do not name it). GAPS 2.6 (GAPS.md:44) is the
three-outcome rule, as the auditor says.

Severity of that residual: I would put it below "major" — it is a named, honest could-not-look
under a rule that provides for exactly that, on a lane the estate has already proved it can widen.
