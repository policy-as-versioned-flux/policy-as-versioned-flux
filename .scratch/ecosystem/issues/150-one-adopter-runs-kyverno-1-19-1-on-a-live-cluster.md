# 150 — One adopter runs Kyverno 1.19.1 on a live cluster

Type: task
Status: resolved
Blocked by: 147, 148, 149, and owner steps: the adopter-gate retirement, the adopter's signed composed tag and composed-set move, and a platform tools tag that carries the 149 line

## Question

Graduated 2026-09-25 from grilling ticket 71, decision 13 (delegated). This is the first engine
bump to go through the route that ADR-0033 point 5 decides. Every earlier ticket grades policy
behaviour offline. This ticket grades it on a cluster that an adopter runs.

**The condition, from grilling ticket 152 (delegated, 2026-09-25), widened by ticket 71's
review.** No adopter moves to Kyverno 1.19.1 while a body that is served in its window does not
compile on 1.19.1. The 5.0.0 cage-tier body does not compile there. So the adopter that moves
composes only the ticket 149 line: its workloads claim that line, and 5.0.0 leaves its composed
set. Ticket 152 decided that on the drift lane an unstamped fall-closed pod keeps reading `null`
for fact 6. How facts 4, 5 and 7 read when the engine holds a body that it cannot compile is not
measured.

**Owner steps.** To drop 5.0.0 from an adopter's composed set is a retirement. The adopter's own
gate refuses a pull request that retires a version (ticket 132). The 4.0.0 retirement passed only
because the integrator merged over the refusal on the owner's authorisation (ticket 113). This
ticket needs the same authorisation. It also needs the adopter's signed composed tag and its
composed-set move (ticket 130), and a platform tools tag whose array carries the 149 line. If the
149 line is a major, the adopter's acceptance record comes first (ticket 149).

Build the following:

1. **Choose one adopter** and record the choice with its reason. Prefer an adopter none of whose
   workloads run on a cluster that another adopter uses, because a shared cluster runs one engine
   (ADR-0033 point 2). Today that is ludlow: tuppence's workload flagship runs on
   `kind-driftwood`.
2. **The adopter moves to the ticket 149 line.** Its composed set and its workloads' claims move to
   the new line only.
3. **The adopter declares 1.19.1** in `gitops/engine/kyverno.yaml` (ticket 147), and recomposes.
   Its evidence shows no engine delta, because the new line and the machinery both support 1.19.1.
4. **The hub runs the adopter's probe on the adopter's engine.** Ticket 161's
   `verify-cage-probe.sh` compares the CLI version with the adopter's declared engine. The hub runs
   it with the truth CLI, 1.18.2. Before the declaration moves, the hub gives that check the
   adopter's declared CLI from the engine table (ticket 146). Otherwise its row falls on every
   truth run.
5. **Measure the unsafe case on a throwaway KinD, never on the adopter's lane.** Install 1.19.1 and
   the 5.0.0 cage-tier body, which does not compile. Record what admission does with a pod: does it
   admit the pod without the mutation, or does it refuse the pod? If admission lets the pod in
   without the mutation, the cage fails open. That is the worst case that ADR-0033 point 3 prices.
   If admission refuses the pod, point 3 reopens. A throwaway-KinD capture is a rehearsal, not Done
   evidence (ADR-0028, lines 35-36, citing ADR-0023). Record it in this ticket as reasoning.
6. **Measure the PolicyReport effect on the lane.** `platform/oscal/result2oscal.py` drops a result
   whose policy maps to no control, so cage-netpol's report entries cannot change the OSCAL output.
   The entries that matter are `require-nonroot`'s, which map to ac-6. Drift samples record no
   PolicyReport today. So the lane first captures PolicyReports, and at least one scheduled 1.18.2
   sample carries that capture before the engine moves. Then compare it with the first 1.19.1
   sample.

## Done

A scheduled drift sample on the chosen adopter runs Kyverno 1.19.1 installed from its declared file.
It records the facts with the same values as the adopter's last 1.18.2 sample, or the ticket names
the reason for each difference. A dispatched run does not count. The admission question from item
5 has a recorded answer, and ADR-0033 point 3 is confirmed or reopened.

## Notes

- The other adopters stay on 1.18.2. Each adopter moves through its own declaration.
- If the chosen adopter's price changes, the evidence must name the reason.

## Resume implementation, 2026-10-03

Ludlow is selected because it does not share the cluster that serves tuppence. The isolated upgrade rehearsal retained the frozen 5.0.0 policy UID and spec: admission caged the pod on 1.18.2, then admitted it uncaged after upgrading to 1.19.1. Candidate 6.0.1 admitted and caged it while preserving pod runAsNonRoot. The raw measurement and cleanup records are in research/resume-2026-10-03/engine-150-admission/upgrade/. Both isolated clusters were deleted. This is rehearsal evidence. A scheduled 1.18.2 PolicyReport capture must precede Ludlow’s actual engine move, followed by the scheduled 1.19.1 comparison; neither is fabricated.

The owner delegated the implementing decisions on 2026-10-03: "you tell me, you control them all, you don't need me to answer". This is recorded as delegated, not as an invented institution signature.

## Comments

### 2026-10-18: genuine scheduled comparison and bounded ADR confirmation

The scheduled baseline is [run 38911688433, attempt 1](https://github.com/policy-as-versioned-ludlow/ludlow/actions/runs/38911688433),
source `9f76b2af169e76030538f0816db54e30f817b220`, original signed observation
[`f7449340dee254cba43ad5a829ab01403df9a97d`](https://github.com/policy-as-versioned-ludlow/ludlow/commit/f7449340dee254cba43ad5a829ab01403df9a97d),
on declared Kyverno 1.18.2. Its protected-main write failed after measurement; the original was
subsequently recovered unchanged. The first scheduled 1.19.1 comparison is
[run 39034542013, attempt 1](https://github.com/policy-as-versioned-ludlow/ludlow/actions/runs/39034542013),
source `34f077499b129005703aa0ed3d46ad9471a59868`, original signed observation
[`ea3e831de6531b10c9f519fa5a34286db17e4f87`](https://github.com/policy-as-versioned-ludlow/ludlow/commit/ea3e831de6531b10c9f519fa5a34286db17e4f87),
delivered through ordinary PR76. Official installation logs bind each exact declared engine and
checksum. Production signature/ancestry readers accept both originals; their three observation
files conserve the exact source prefixes and appended bytes on current Ludlow main.

All seven boolean facts remain true for all three source rows: 21 true values per run from one
cluster, not three independent cluster experiments. Reports remains Running on policy 7.0.0
with the same image and apps inputs; the reference also remains Running. Ludlow's explicit
retirement of 5/6 was delivered on 1.18.2 before its engine move. The retained eight version 7
bodies are byte-identical; 18 version 5/6 bodies are removed. Both samples read 42 PolicyReports
and map nine policies. All 12 non-SKIP outcomes (10 pass, two fail) and all eleven core price/tier
projections are equal. No unsupported-engine delta is present. Driftwood and Tuppence retain
their own 1.18.2 declarations.

Normalized OSCAL observations change from 468 to 136. Of the 332 removed SKIPs, 252 belong to the
retired 5/6 lines. The other 80 are 40 each from retained require-nonroot 7 and orphan-guard;
their cause remains **unmeasured**, because raw PolicyReport result bodies were not retained.
The same two missing risk joins remain: `42ca452a-8b23-50d0-8b67-3fa61c65e221` and
`6a834573-26b8-51b6-83a9-1c40cda91ab9`. Neither is replaced with a fabricated risk or zero price.
Fresh cluster resource identities and an 8 Ki runner memory difference are also retained; the
memory difference has no measured cause. Separate CVE absence-set churn and genuine EOL feed
publication change price provenance metadata without changing the eleven core monetary/tier
projections. Retirement, machinery, compiler, instrument and source changes accompany the
engine upgrade, so this is a chronological comparison, not an engine-only causal experiment.

[ADR-0033 point 3](../../../docs/adr/0033-a-policy-line-supports-exactly-the-engines-it-passed-on-and-any-other-engine-is-priced.md)
is now confirmed for the bounded fail-open possibility measured in the unchanged October 3
isolated server-dry-run rehearsal. That rehearsal is reasoning evidence, not scheduled Done
evidence, and its historical 6.0.1 candidate is not substituted for the final retained 7.0.0 line.
The genuine hub TRUTH 430 original `e5c83d9694650e591777f2a746f28a4a31c37c2e` separately records
the declared 1.19.1 CLI document probe passing for Ludlow's selected v5.1.1 composition and HEAD;
scheduled facts 6/7 supply the separate running-cluster evidence. No new cluster or probe was
started for this record. This amendment preserves the claimed status; completion will be assessed against the original
Done conditions, dependencies and current recorded grades. The unresolved differences remain
explicit limits. Historical observations, grades, prices and dates are unchanged.

## Answer

**2026-10-18, scheduled migration and admission answer reconciled.** Ludlow was chosen because it does not share the cluster serving Tuppence. The authorized retirement of 5/6 on 1.18.2, signed composed delivery and pointer preceded the engine move; the selected workload and composed set retain only final compatible line 7.0.0. Ticket 148's original stage is now reconciled above; tickets 147/149 and the recorded owner steps are delivered. This resolves the tracker dependency now, without rewriting earlier claimed statuses or migration history.

The genuine scheduled comparison is [38911688433/1](https://github.com/policy-as-versioned-ludlow/ludlow/actions/runs/38911688433/attempts/1), source `9f76b2af169e76030538f0816db54e30f817b220`, original `f7449340dee254cba43ad5a829ab01403df9a97d`, on declared 1.18.2, followed by the first scheduled [39034542013/1](https://github.com/policy-as-versioned-ludlow/ludlow/actions/runs/39034542013/attempts/1), source `34f077499b129005703aa0ed3d46ad9471a59868`, original `ea3e831de6531b10c9f519fa5a34286db17e4f87`, on declared 1.19.1. Official install logs bind the exact declaration/checksums. These are schedules, not dispatched substitutes. All seven facts on all three source rows remain true, and all eleven core price/tier projections are equal, without an engine delta.

The October 18 comparison above records item 6's PolicyReports and the bounded admission answer: the unchanged October 3 isolated 5.0.0/1.19.1 server-dry-run admitted an uncaged pod, confirming ADR-0033 point 3's fail-open possibility for that exact pairing. The deleted throwaway-cluster rehearsal is reasoning, not scheduled Done evidence; historical 6.0.1 is not substituted for released 7.0.0. The eight retained version-7 bodies stay exact. Both schedules carry 42 PolicyReports and equal twelve non-SKIP outcomes. The 80 retained-policy SKIPs that cease to appear, 8 Ki runner memory difference and two missing risk joins remain explicitly unresolved. The comparison does not isolate engine causality. Driftwood and Tuppence remain on their own 1.18.2 declarations.

Recorded 435 gives `.estate-clone/ludlow/verify-cage-probe.sh` and `verify/engine-pairing/verify-engine-pairing.sh` PASS, corroborating the declared 1.19.1 CLI and supported composed inputs. Neither wrapper's touching Git subjects establishes ticket ownership, so neither is claimed as an owned PASS for this ticket. Scheduled facts 6/7 provide the separate running-cluster evidence. The original Done requires matching seven-fact values or explanations for changed facts, the PolicyReport comparison and the recorded admission/ADR answer; it does not require a new engine-only cause for every ancillary raw difference. Producer 435's four other failures and all unmeasured financial/cohort limits remain. No new cluster, probe, observation, price, engine or policy release was created by this record reconciliation.
