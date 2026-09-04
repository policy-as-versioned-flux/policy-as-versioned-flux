---
status: accepted
---

# The cage ladder: tier per Namespace, tighten-only cage, an `isolated` rung, one floor, `infra` by role

The cage was the only enforcement in vocabulary but not in code (findings H2-01, H2-03, H2-12,
H2-13, H8-03). The tier label was forgeable, an unknown tier fell to the loosest cage, the bottom
rung was a GitHub issue, and the baseline cage wrote `readOnlyRootFilesystem: false` over pods that
set `true`. Decided 2026-08-28 in `.scratch/ecosystem/issues/09`. Provisional: the owner agreed
without a reason.

## The decision

- A tier attaches to a governed **Namespace**. It is declared on the Namespace manifest next to
  `governed: "true"` (ADR-0018), rendered from the signed composed artefact. `cage-tier` reads it
  through `namespaceObject` and writes it onto every pod. The pod label is an output only. A
  governed Namespace with no tier fails closed to `isolated`.
- The cage is **tighten-only**. It never writes a security field looser than the workload declared.
  This lands in every served copy of `cage-tier`, and the computed-semver engine treats "writes
  false over true" as a loosening.
- The ladder is `baseline, restricted, quarantine, isolated, infra`. **`isolated`** is the bottom
  rung: quarantine dials, no ingress, no egress, first eviction. Everything still runs. The £
  selects `isolated` where it selected `deny`. `cage-netpol` generates per-tier reach.
- An adopter may declare one tighten-only **floor** on its party artefact. Selection clamps to the
  floor. Lowering the floor is priced, never refused.
- Only a party with the `platform` role may declare a Namespace at **`infra`**. A declaration
  from any other party renders to `isolated`. The platform's `infra` declaration lands, and the
  truth surface asserts it, before the default for an unlabelled Namespace flips to `isolated`.
- **Added 2026-08-28 (review):** a Namespace that is not governed at all still renders **`baseline`**
  for a pod that claims a policy version. That is the other half of the ordering rule above, and it
  had been a fall-through with no decision behind it: the cage stamped posture labels, a negative
  eviction class and a resource ceiling on workloads in Namespaces nobody governs. It is now
  written down and carries a fixture (`graded/tests/cage-tier`, pod `ungoverned-ns`). It flips to
  `isolated` in the same one-line edit as the rest of the ordering rule.
- **Added 2026-08-28 (review):** a pod created in a governed Namespace with NO
  `policy-as-versioned.dev/policy-version` claim is REFUSED by
  `governed-namespace-requires-claim`, promoted that day from `Audit` to `Deny`. Live, `Audit` let
  such a pod run completely uncaged -- no tier, no class, no limits, no hardening, no reach cage --
  inside a Namespace whose declared tier was `isolated`, so the Namespace fell closed and the pod
  fell open. This is the one refusal the doctrine allows and it is a missing INSTRUMENT (ADR-0020),
  not a posture judgement: the claim is what selects which served version cages the pod, so without
  it there is no cage to put the workload in. A pod that claims is caged and priced, never refused.

## Alternatives

- Tier per workload, on the pod manifest, as `tier_pr.py` does. Rejected: the pod label is the
  forgeable object reversal 13 moved away from.
- Tier baked into the adopter's rendered policy copy. Rejected: it breaks `render_is_faithful` and
  ADR-0018's "no namespace list in the artefact".
- A `replicas: 0` bottom rung. Rejected: that is a refusal under another name.
- A hub-signed allowlist of infra namespaces. Rejected: a second declaration path.

## Consequences

Supersedes ADR-0014's CREATE deny, ADR-0015's "a proposed Deny opens an issue", ADR-0016 §3 (the
artefact carries no tier and no floor) and ADR-0018 §4. The offline test needs a `Values` file
carrying the Namespace; `kyverno apply` 1.18.2 evaluates `namespaceObject` from it (proven
2026-08-28). H8-03 closes when the pod label is an output.

## Note, 2026-09-02 (ticket 75 Q5, the owner's reason)

The isolated rung replacing Deny was recorded on 2026-08-28 as the assistant's reading of the
owner's words. On 2026-09-02 the owner gave the reason in their own words: proportionality is
managed and run with a better cage and better protections and mitigations; a workload can find
itself unable to run only because it does not fit the cage, never because it is deliberately denied;
in Kubernetes terms the estate is a mutating admission controller more than a validating one. The
assistant's narrower alternative, a surviving locked door for access control, data protection and
key management, was put and overruled. Consequence: no Deny-shaped rule ships that is not a cage
constraint (ticket 89).

## Note, 2026-09-04 (ticket 78, delegated): the proposer only tightens, and the selection is over the party

The cage was recorded as tighten-only above. The **proposer** was not. `tier_pr.py` ran
`wargame_cage_tier()` once per `prices[]` line and `apply_tier_declaration()` wrote that line's
`proposed_tier` onto the governed Namespace unconditionally, so driftwood's only reachable band
crossing today -- the threat-register line moving `baseline` to `restricted`, beside two lines
that already select `isolated` -- would have stamped `restricted` over a Namespace declared
`isolated`. Tighten-only was a property of the mutating webhook and of nothing that wrote the
declaration the webhook reads.

Three things now hold, and each carries a check:

- **The selection is over the party, not the price line.** One Namespace carries one tier for
  every pod in it, so the declaration cannot be looser than the party's worst-priced regime. The
  tier written is the **strictest `proposed_tier` across `prices[]`**, clamped up to the declared
  `overlay.floor`, and never looser than what the Namespace declares today. A line whose fold does
  not tighten the declaration is **held**: no branch, no commit, no pull request.
  (`wargamer.select_party_tier`, and driftwood's own `selection-policy` v1.1.0 `select_party`.)
- **The declaration is bound to the price, on every pull request.** A proposer that only tightens
  does not stop a hand edit or a merge that races a re-price, so
  `platform/shift-left/tier_binding.py` reads `proposed_tier` off the composed evidence and
  `posture.acme.io/tier` off the governed Namespace and refuses the looser label. It runs in each
  adopter's `shift-left.yml` and, across the estate, in the hub's `verify/tier-binding/`.
- **The proposal commit is signed and its identity is checked.** `propose-tier.yml` installs
  gitsign by checksum, signs the commit with the workflow's own keyless Actions identity, and
  verifies it against a second constant, `EXPECTED_PROPOSAL_IDENTITY_REGEXP`, anchored to
  `propose-tier.yml@refs/heads/main`. It is deliberately not an alternation widened into
  `release.yml`'s `EXPECTED_IDENTITY_REGEXP`: proposing a tighter cage and publishing a signed
  release are different powers, and each adopter's identity-regexp check now proves the two do not
  overlap in either direction.

**Strictest line, not summed residual, is the rule this note records** -- the interim the ticket
states, pending PE-05 / ticket 75 Q4. A summed rule would slot into exactly one place,
`select_party_tier()`'s fold of `lines` to `strictest`, mirrored in the adopter package. The
version bump is what makes that swap reviewable: driftwood's selection-policy is now 1.1.0.

**Loosening is not implemented, and that is the decision, not an omission.** ADR-0022 prices a
lowered floor rather than refusing it, so a party's aggregate residual should one day be able to
argue a looser declaration. Doing that needs a residual the proposer does not yet compute and a
pull-request body that carries the argument, so this ticket writes nothing looser at all and the
looser path stays a later ticket. Until then a loosening is a human edit to the Namespace, in the
open, under the binding check -- which is where an unargued loosening belongs.
