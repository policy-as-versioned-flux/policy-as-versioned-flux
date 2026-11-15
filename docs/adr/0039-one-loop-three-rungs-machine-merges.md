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
| K6 | The publishers' pins are followed by `loop.py bump-pins` with plain git. The platform pin is not followed (K17). Renovate is not run | delegated |
| K7 | No reusable workflow. Driftwood's workflow checks platform out at its pin and runs its scripts | delegated |
| K8 | No exploited-flaw list, image inventory, scanner or fetch. They are parked, not dropped | delegated |
| K9 | Ico and feeds have no scheduled job and no landing job. Their one unattended act is to cut a tag when a merge changes the feed's version | delegated, applying decision 2 |
| K10 | Network tests run from the probe pod, not inside every workload container | delegated |
| K11 | A loss the cage cannot touch is a priced row with no `needs`, on the publisher's editorial band | delegated, applying decision 5 |
| K12 | No veto on a refused release | delegated, applying decisions 1 and 2 |
| K13 | `pins.sh` verifies a tag's signature when a pin names a tag | delegated |
| K14 | Driftwood's workloads stay bare Pods, with no rollout stamp | delegated |
| K15 | The party file and the ladder file are JSON, not YAML | delegated |
| K16 | A notch is judged by the goal it leads to, not by its own gain. This departs from a consequence written in the option the owner chose: option (c) of `.scratch/distil/DISTILLATION.md` section 7 item 6 reads "cost is added to exposure, so a notch that costs more than it saves is not taken", and the owner answered "Always". The loop instead never starts a climb unless some tighter rung predicts a lower figure, cost included, and one notch on the way may cost more than it saves. Judged one notch at a time, the first notch closes nothing today's rows need, so the loop would stay at `baseline` for ever, which is not what the owner was told to expect under decision 5. Option (c) as written leaves the loop at `baseline`, red, with the shop serving. The owner can reverse it (`LOOP.md`, what waits for the owner) | delegated |
| K17 | The loop never moves the platform pin. `bump-pins` follows ico and feeds only, and a platform change reaches the adopter by a pull request that changes the platform pin line. The pinned platform holds `check-diff` and `bump-pins`, which gate what lands, so a loop that pinned a new platform tag itself would be following its own code. The pull request is pushed from an agent session, so its own cycle runs the new platform on a cluster before the app merges it. Decided 2026-11-15, after the second look (`.scratch/distil/CONTRACT.md` section 11) | delegated |
| K18 | A row whose counted door is found closed stays in the register at the rate its own method gives, 0, with the reading dated. It is not removed and not left at the old rate. Feeds' second row is the case: its N, read again, is 0, so leaving the old rate would knowingly overstate it, and removing the row would lose the reading and its history. Decided 2026-11-15, after the owner's "Do everything" (`.scratch/distil/CONTRACT.md` section 11) | delegated, applying "Do everything" |

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
- The half-life on a refused release. The owner's rule was "Flood guard with a half life. Point in
  time rejection does not mean never." (`.scratch/drift-review-2026-08-27/REGRILL-ANSWERS.md:28`).
  With no person merging, no release is refused, so the rule has no occasion (K12).

**Superseded in full.** ADR-0021. There is no twin scenario while the twin is parked. There is no selection policy package. The
loop's goal chooses the rung.

**Sided with.** ADR-0015 rejected "a tighten-only proposer" because "It ratchets the estate toward
deny and never recovers" (lines 68-69), and let proposals go both ways (point 7). This loop also
moves both ways. Unlike ADR-0015, no human merges either direction.

**Not the ratchet ADR-0026 rejected.** That ratchet made the selected set "the union with the last
signed selected set", which "composes against a set the party artefact does not declare" and
"makes a hole that can never close, a count that never falls" (lines 187-191). Here the rung is the
one declared line in git, with no second copy, and `release` loosens it when the figure allows. The
figure falls when a measured, declared closure removes a row; when a publisher's change lands,
which the loop follows by itself; or when the loop leaves a rung and that rung's cost leaves the
figure. The adopter's turnover in `party.json` and platform's rung costs can lower it too, each
only by a pull request the loop cannot write. The tolerance, the margin and the dwell change the
verdict, not the figure, and move only by such a pull request.

The records above are left unedited, with no banners. This record names what each of them loses.
