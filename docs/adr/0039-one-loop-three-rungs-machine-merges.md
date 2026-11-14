---
status: accepted
---

# One loop, three rungs, machine merges

Recorded 2026-11-14. The owner's ten answers of that day, in the owner's words, are in
`.scratch/distil/DECISIONS.md`, and are not restated here. Answer 3 is a question back, so the
tolerance stays a fixture. The design built on them is `.scratch/distil/CONTRACT.md`, which gives
the reason for each decision below. `LOOP.md` describes the loop and its state. `CONTEXT.md`
defines the terms.

## Decision

Each decision carries the contract's label. *Owner-instructed* restates an answer in
`DECISIONS.md`. *Delegated* is the assistant's, under ADR-0025.

| # | Decision | Label |
|---|---|---|
| K1 | The compared figure is exposure plus the current rung's running cost a year | owner-instructed |
| K2 | The loop moves one notch towards a goal rung. It tightens at once and releases after the dwell, by the same machine path | owner-instructed |
| K3 | Three rungs: `baseline`, `quarantine`, `isolated`. The old `restricted` is merged into `quarantine` | delegated |
| K4 | Two capabilities only: `egress` and `inbound` | delegated |
| K5 | The cluster is built by `kubectl apply -k` from pinned checkouts. Flux is not installed | delegated |
| K6 | Pins are followed by `loop.py bump-pins` with plain git. Renovate is not run | delegated |
| K7 | No reusable workflow. Driftwood's workflow checks platform out at the pinned commit and runs its scripts | delegated |
| K8 | No exploited-flaw list, image inventory, scanner or fetch. They are parked, not dropped | delegated |
| K9 | Ico and feeds have no scheduled job and no landing job. Their one unattended act is to cut a tag when a merge changes the feed's version | delegated, applying decision 2 |
| K10 | Network tests run from the probe pod, not inside every workload container | delegated |
| K11 | A loss the cage cannot touch is a priced row with no `needs`, on the publisher's editorial band | delegated, applying decision 5 |
| K12 | No veto on a refused release | owner-instructed |
| K13 | `pins.sh` verifies a tag's signature when a pin names a tag | delegated |
| K14 | Driftwood's workloads stay bare Pods, with no rollout stamp | delegated |
| K15 | The party file and the ladder file are JSON, not YAML | delegated |
| K16 | A notch is judged by the goal it leads to, not by its own gain | delegated reading of decision 6 |

Two things are derived from the owner's sentence, and the owner has commented on neither
(`.scratch/distil/DISTILLATION.md` section 7): the pound is a real figure, not a ranking, because
a ranking cannot be within a tolerance; and the exposure compared is the whole organisation's,
because the tolerance is the organisation's.

## Alternatives and consequences

**Reversed.**

- The ordinal pound. Ticket 75 recorded the pound as "an ordinal, auditable comparison
  instrument", delegated on a "yes" (`.scratch/ecosystem/issues/75-grilling-what-is-this-for-the-twelve-questions.md:111`).
  The figure is now pounds a year, on the same scale as the tolerance.
- ADR-0022's floor (lines 53-54), and its note of 2026-09-04 that the tier written is "never
  looser than what the Namespace declares today" (line 125). Driftwood's floor is removed by
  decision 8, and the loop releases (K2). ADR-0022's rule that the cage "never writes a security field looser
  than the workload declared" (line 47) stands: the version 8 cage keeps it.
- A human on the merge path. ADR-0002 adopts versions "via a Renovate PR that a human reviews and
  merges" (line 9). ADR-0023 says a scheduled run "may never commit a declaration: a tier, a pin"
  (lines 85-87). ADR-0024 says "A human still merges a reviewed tier PR" (line 47), "A release
  stays a human act" (line 59) and "A scheduled job still never merges" (line 449). Under
  decision 2, the app now merges a notch or a pin change in the same run that proposed it, after a
  job that checks the diff.

**Superseded in full.** ADR-0021. There is no twin scenario and no selection policy package. The
loop's goal chooses the rung.

**Sided with.** ADR-0015 rejected "a tighten-only proposer" because "It ratchets the estate toward
deny and never recovers" (lines 68-69), and let proposals go both ways (point 7). This loop also
moves both ways. Unlike ADR-0015, no human merges either direction.

**Not the ratchet ADR-0026 rejected.** That ratchet made the selected set "the union with the last
signed selected set", which "composes against a set the party artefact does not declare" and
"makes a hole that can never close, a count that never falls" (lines 187-191). Here the rung is the
one declared line in git, with no second copy, and `release` loosens it when the figure allows. The
figure falls when a measured, declared closure removes a row, when a publisher's change lands, or
when a rung's cost leaves it.

The records above are left unedited, with no banners. This record names what each of them loses.
