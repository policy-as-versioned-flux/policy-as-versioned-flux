# Spec — the eco-system runs end to end once, on a clock, and one command says so

Status: ready-for-agent
Source: `.scratch/ecosystem/map.md` (`wayfinder:map`, charted 2026-08-28) and its 22 resolved
tickets; `TO-SPEC-HANDOFF.md`; ADR-0019 to ADR-0023. Written 2026-08-28.
Scope: **the thin slice of NORTH-STAR §4**: one regulator, one adopter (driftwood), one feed,
one cage move, one twin forecast, all real, plus tuppence and ludlow consuming, graded by the
truth surface. Ratification: every decision below is provisional unless marked **decided**
(D1 to D5, ADR-0023). A provisional decision reopens with a reason, never with a bare letter.

---

## Problem Statement

Chris runs an org of repos that claims to be an eco-system: regulators publish, adopters
compose, the price picks a cage, Flux reconciles it, a twin forecasts, and one command reports
the truth. Today none of NORTH-STAR §4 steps 1 to 5 runs end to end. The tier label is
forgeable and falls open. The bottom rung is a GitHub issue. The twin and the estate have no seam.
The clocks that should gather do not exist. The truth surface reports 40 of 56 and cannot look
at the cluster. A reader of the demo cannot tell what is real, and the owner cannot say "done"
without watching a video.

## Solution

Build the seven joints of §4 as the thinnest real slice, each joint owned by one ticket whose
definition of done is a check inside `talk/verify-all.sh`. A regulator feed publishes, Renovate
pins it, the composition re-prices the adopter against its own size, the price crosses a band,
the cage tier moves by a reviewed PR, Flux reconciles the new cage onto a cluster the truth run
can see, the twin plays a signal forward and publishes forward intelligence the estate consumes,
every step is provenance-checked, and the daily TRUTH line reports each as pass, fail or
could-not-look. One end-to-end harness drives the seven steps on an ephemeral cluster inside the
scheduled truth run. Nothing is refused; everything is caged and priced.

## User Stories

### The owner, reading the truth
1. As the owner, I want one dated TRUTH line per day, so that I quote one number and nothing else.
2. As the owner, I want each §4 step to report pass, fail or could-not-look by name, so that I know which joint is real.
3. As the owner, I want a step the run cannot see to say could-not-look and never pass, so that the number is honest.
4. As the owner, I want the end-to-end harness to run inside the scheduled truth run, so that there is one clock and no presenter-run number.
5. As the owner, I want a scheduled run to append observations to main and never a declaration, so that a clock cannot change what is enforced. **Decided (D1).**
6. As the owner, I want the observation lane caged by a repo ruleset and signed bot commits, so that the lane is a cage, not a policy statement. **Decided (D1).**
7. As the owner, I want every decision in this spec traceable to a ticket Answer, so that I can reopen one with a reason.

### The regulator (ico, nist), publishing
8. As a regulator, I want to publish a feed in one signed envelope, so that every consumer parses it the same way.
9. As a regulator, I want a scheduled fetch to open a PR only when the computed bump is not none, so that I review change, not noise. **Decided (D2).**
10. As a regulator, I want to define what "changed" means for my feed in a versioned rule file, so that a market tick and a monthly rate are each a change on their own terms. **Decided (D2).**
11. As a regulator, I want sub-threshold observations to land on an observation branch, so that a series survives for scoring.
12. As a regulator, I want to publish per-violation control weights keyed by catalogue and control id, so that a hole partitions my regime's exposure and never adds to it.
13. As a regulator, I want to pin another regulator's catalogue as a parent, so that my weights key on the same control ids.
14. As a regulator, I want a withdrawn version priced now and a superseded version priced by the EOL ramp, so that two states have two prices. **Decided (D5).**
15. As a regulator, I want the gitsign tag to be the only signature I need, so that I run one release path.

### The adopter (driftwood first, then tuppence and ludlow), composing and being caged
16. As an adopter, I want Renovate to raise my pin when a parent publishes, so that adoption is a reviewed PR.
17. As an adopter, I want the composition to price my exposure against my own signed size, obligations and currency, so that the number is mine.
18. As an adopter, I want every hole priced and none refused, so that a control I cannot meet moves my tier instead of blocking my build.
19. As an adopter, I want the tier declared on my governed Namespace manifest and rendered onto every pod, so that a pod cannot pick its own cage.
20. As an adopter, I want an unknown or missing tier to fail closed to the strictest running cage, so that silence is never an exemption.
21. As an adopter, I want the cage to be tighten-only, so that a stricter setting I declared is never loosened by the cage.
22. As an adopter, I want the bottom rung to be a running, unreachable cage rather than a refusal, so that nothing is ever denied.
23. As an adopter, I want to declare one tighten-only floor, so that I can hold myself stricter than the price requires.
24. As an adopter, I want lowering my floor priced as a delta and never refused, so that the balance sheet carries my choice.
25. As an adopter, I want the proposer to open a PR that edits the tier declaration when the price crosses a band, so that a human merges the move.
26. As an adopter, I want the proposer to re-compose at today's date before proposing and commit nothing, so that a date-driven crossing is a trigger and not a silent change.
27. As an adopter, I want rejected proposals suppressed with a half-life derived from closed PRs, so that I am not asked the same question daily.
28. As an adopter, I want my appetite as a signed fact on my party artefact, so that the tier selection reads my tolerance and no fixture.
29. As an adopter, I want the selection policy as my own versioned package, so that the rule that picks my tier is pinned and reviewed.
30. As an adopter, I want every price to carry perspective and currency and never sum across perspectives, so that no number is a lie by addition.
31. As an adopter, I want a per-customer restatement of each price, so that the figure is proportionate to my org.
32. As an adopter, I want the second and third adopters to consume the same slice, so that the eco-system is not one org's demo.

### The platform, holding the substrate
33. As the platform, I want my own party artefact with roles, size, appetite and what I publish, so that I am a party like any other.
34. As the platform, I want to declare my own Namespaces at the infra tier by role, so that kube-system, flux-system and kyverno are caged explicitly and no allowlist exists.
35. As the platform, I want my infra declaration to land before the unlabelled default flips to isolated, so that CoreDNS does not stop.
36. As the platform, I want a degraded publish to carry a prerelease suffix and a priced hole at the adopter, so that a weak release is priced, never a floor.
37. As the platform, I want the first gate-determined release, so that the computed bump and the declared bump agree on the wire.

### The cluster, reconciling
38. As a cluster, I want Flux to reconcile the composed set from the adopter's signed tag, so that the cage on the cluster is the cage in git.
39. As a cluster, I want an identity-pinned gitsign-verifying controller at the source boundary, so that one signature is verified and no key re-signs a ref. **Decided (D3).**
40. As a cluster, I want a five-fact sample proving the composed set is in force from signed sources, so that "reconciled" is an observation, not a claim.
41. As a cluster, I want three falsifiers declared before the first sample, so that the sample cannot pass by accident.
42. As a cluster, I want per-tier reach generated from the tier, so that isolated reaches nothing and baseline reaches normally.

### The twin, forecasting
43. As the twin, I want my overlay in the adopter's own repo with the world layer vendored, so that the adopter owns its own model.
44. As the twin, I want my own semver tag, so that an overlay pins me like any other parent.
45. As the twin, I want a subscribed feed version to map to one dated signal by lookup, so that the clock binds without judgement.
46. As the twin, I want to emit a forward-intel feed with a scenario under a perspective and no recommended action, so that the estate selects and I do not.
47. As the twin, I want six standing scenarios per adopter, including a rival reading my holes and a publisher withdrawing, so that the library lives in one place.
48. As the twin, I want the estate to annualise my scenario as a source-twin price entry, so that my forecast reaches the balance sheet.
49. As the twin, I want my evals in the gate with truth.log as the record, so that my scores are graded like everything else.
50. As the twin, I want the niobium headline in my scenario library and never in the news feed, so that a scenario is not a fact.
51. As the twin, I want classification and the headline judgement packaged as a skill a human runs, so that no heuristic runs on the clock.

### The insurer, quoting
52. As the insurer, I want to pin the platform and the adopter's signed exposure as parents, so that I price from signed facts.
53. As the insurer, I want exclusions keyed on regime names and control ids and attachment equal to appetite, so that the quote reads the same artefact the adopter signed.
54. As the insurer, I want to publish one quote feed per adopter with priced-against and conditions, so that the premium is a contract cost under the adopter's perspective.

### The reader of the demo
55. As a reader, I want the deck generated from gate captures, so that every slide is a read of the truth surface.
56. As a reader, I want step 4 to say could-not-look until the CI cluster run lands, so that I am not shown a rehearsal. **Decided (D4).**
57. As a reader, I want the seven steps on the deck from day one, red where red, so that progress is visible without a video.
58. As a reader, I want provenance for every step verifiable in Rekor and in the artefact sidecars, so that I can check without trusting.

### An adversary
59. As a bad publisher, I want my reliability priced as a feed that widens subscriber triples, so that my unreliability costs my subscribers and not the estate's honesty.
60. As a forging pod, I want my tier label clobbered from the Namespace, so that my forgery is an output overwritten at admission.
61. As a departing adopter, I want feed payloads and converter code vendored, so that I can re-derive my prices offline.
62. As a switching adopter, I want the switching cost computed by re-composition and priced, so that lock-in is a number.

## Implementation Decisions

### The truth surface and the harness
- `talk/verify-all.sh` stays the one gate. It discovers every verify script by glob and grades by exit code: 0 pass, 3 could-not-look, else fail. The TRUTH line is the only citable number.
- One **end-to-end harness** (owner's choice, seam question 2026-08-28) drives the seven §4 steps in order on an ephemeral KinD cluster. It is one verify script under the gate, run by the scheduled truth workflow. It never runs as a presenter-run number. Its steps report individually so that one red step does not hide six greens. The harness owns no state: it reads the same signed artefacts Flux reads.
- The scheduled truth run is an **observation** lane (**decided, D1**). It appends `truth.log`, drift samples and gate captures to main. A repo ruleset on each unit limits the scheduled identity to those paths. Bot commits are signed. `verify-schedules.sh` asserts that no scheduled run changed a signed artefact and that every clock ran within its period.
- Every build ticket's definition of done wires one verify script into the gate. No ticket closes on a demo.

### The feed contract (ticket 21, ADR-0019)
- One envelope: kind, name, version, published_by, published_at, payload_schema, payload. Signed by the gitsign tag and nothing else. Parent kinds closed to controls, implementations, feed. Subscription is `inherits[]` plus `since`. Discovery is `publishes[]` on the publisher's party artefact. Revocation is a new version plus `revoked[]`, priced now.
- Any party may carry `inherits[]`. ico pins nist. The insurer pins the platform and the adopter's exposure.
- A publisher fetch on a clock opens a PR only when the computed bump is not none (**decided, D2**). Each feed defines "changed" in its own versioned rule file beside the feed. Sub-threshold observations append to the feed's observation branch.
- A pin behind a newer published version is priced by the existing EOL ramp from the newer version's publish date. `revoked[]` stays withdrawal (**decided, D5**). Revisit trigger: an explicit supersedes field with an EOL date if the ramp misprices.

### The £ seam (ticket 25, ADR-0020, ADR-0021)
- The adopter signs size (turnover, customers, data subjects, headcount, as-of) and obligations on its party artefact. Percent-of-turnover formulas scale the published examples by the adopter's cap. Stale size widens to the cap. A missing regime price or FX rate is an instrument fault and refuses. A missing behaviour is priced.
- Appetite is a signed fact on the party artefact. The platform's appetite fixture is retired.
- The twin emits a forward-intel feed from the adopter's repo. `prices[]` gains a `source: twin` entry. A versioned selection-policy package picks the tier. The curve never picks.
- One `prices[]` schema pass, in this ticket, adds together: per-hole breakdown under the regime entry, the premium as a contract cost line, reliability fields and a switching entry, and a per-customer restatement. One forward-intel payload amendment adds register, claim scope and derived-from together as one major.
- Every price carries perspective and currency. No sum crosses perspectives. Reporting currency defaults to USD; the adopters declare GBP. FX is a signed feed, HMRC monthly as the source.
- FCA reads relevant revenue with published rate bands and a publisher-shipped widening target. HIPAA reads data subjects against the annual cap times provisions. PCI stays size-blind until a publisher ships a per-card line. Each publisher ships its converter beside its feed; composition calls it with the adopter's size.

### The cage ladder (ticket 26, ADR-0022)
- The ladder is baseline, restricted, quarantine, isolated, infra. Isolated is quarantine dials plus no ingress, no egress, first eviction. The selection returns isolated where it returned deny.
- A tier attaches to a governed Namespace, declared on the Namespace manifest next to the governed label, rendered from the composed artefact. The cage policy reads the Namespace and writes the tier onto every pod. The pod label is an output only. A governed Namespace with no tier fails closed to isolated.
- The cage is tighten-only in every served copy. The computed-semver engine treats "writes false over true" as a loosening.
- Per-tier reach is generated from the tier with per-tier names and ingress added. The synchronize gap on a tier move is named in the verify script.
- One tighten-only floor on the adopter's overlay. Selection clamps to the floor. Lowering is priced.
- Only a platform-role party declares infra. Its declaration lands, and the gate asserts it, before the unlabelled default flips to isolated.
- Offline proof: the policy test supplies the Namespace through the CLI values file. Proven on 2026-08-28.

### Schedules and skills (ticket 28, supersedes ADR-0015 point 5)
- One daily schedule floor on every unit: publisher fetch, Renovate, propose-tier, twin sweep. Each org picks its time. No cross-org ordering is promised.
- A clock consumes only committed, reviewed claim files. Reasoning is a skill a human runs. A heuristic stand-in never runs on the clock.
- The adopter's clock re-composes at today's date, proposes, commits nothing.
- The rejection ledger is derived from closed unmerged PRs on the dedupe branch with a half-life, keyed org, kind, slug. A changed curve hash resets it. The fixture fallback is deleted.

### Identity (ticket 32)
- One trust domain per party that runs a cluster, federated pairwise, all declared on the party artefact. The workload identity path carries the cage tier from the same rendered label. A serving org declares its cross-org demand in its composed artefact; a caller that fails it loses reach, priced as a source-twin entry, never gated.
- Two issuers: GitHub OAuth for humans, Actions OIDC for tags, proposer and twin agent. SPIRE for workloads and devices. Dex retired. The substrate ships as a platform implementations package with control claims.

### Flux (tickets 40 to 42, ADR-0023)
- The gitsign tag is the only signature (**decided, D3**). An identity-pinned gitsign-verifying controller at the source boundary verifies it, time-boxed until Flux #1068. Precondition: test Flux mode Tag with a pinned commit first.
- Driftwood proves the composed set in force with a five-fact sample per source: ready at tag and commit on the real remote, verified, last applied revision equals the commit, rendered objects byte-equal live, objects in the inventory. Three falsifiers are declared before sample one.
- The adopter's ResourceSet ranges its composed directory at its own tag. Platform and nist stay verified sources checked against header SHAs.
- Tuppence and ludlow widen after driftwood is green.

### The twin (tickets 29, 49, 50)
- The overlay lives in the adopter's repo. The world layer is vendored at a pinned ref. The twin cuts its own semver tag first. The authored floor is workload, policy line, data, roles, one graded edge to a cash flow, one employer perspective with a currency checked against the reporting currency.
- A pinned feed version maps by lookup to one dated signal. Four scenarios per adopter become six. Penalty-published prices the post-fine value-chain shock, never the fine.
- The market-moves feed uses one mechanical rule over one source and publishes a series; the twin classifies by a human-run skill; a PR opens on the feed's own threshold as its definition of change.
- The news feed carries a minimal payload. The classify-and-judge skill writes binding and override; only override prices. Claim scope rides on forward-intel. Niobium lives in the scenario library, never in the feed.
- One twin-evals verify script in the gate. truth.log is the record.

### The publisher release (ticket 43)
- A degraded publish carries a prerelease suffix on the declared number. A degraded tier at the adopter is a signed fact priced into the adopter's prices. The institution matrix is filled by adopters with the published computed-semver package. The bump lives on the versions array element for the platform and a one-key file for ico and nist.

### The insurer (ticket 36)
- Exclusions keyed on regime names and control ids. Attachment equals appetite. The adopter's composed artefact gains a signed exposure section. The insurer pins the platform and the exposure, runs the pricing under its own perspective on a clock, and publishes one quote feed per adopter. A human merges.

### The demo (ticket 47)
- The deck is generated from gate captures. The live run id is the scheduled one. Seven steps from day one. A verify-demo script in the gate. The mp4 is a release asset, never the deliverable.

## Testing Decisions

- A good test observes an external fact and exits 0, 3 or non-zero. It never asserts on implementation shape. It says on its last line why it could not look. It runs offline where the fact is offline and exits 3 where the fact is live and unreachable.
- The seam is the end-to-end harness inside `talk/verify-all.sh`. The harness drives the seven §4 steps on an ephemeral KinD cluster in the scheduled truth run. Each step is one graded sub-result. The harness is the highest seam; every other verify script is a sub-seam under the same gate.
- Under the harness: the composition self-checks and the computed-semver classifier tests (existing python selfchecks), the offline policy tests with a values file for the Namespace (existing cage-tier test shape, extended), the five-fact Flux sample, the twin evals, the schedules verifier, the demo verifier.
- Prior art: `talk/verify-all.sh` and its 51 unit verify scripts; the cage-tier offline test; the composition selfcheck that asserts render fidelity; the truth workflow that appends `truth.log`.
- Modules tested: feed envelope and bump computation; composition and pricing; cage policy and per-tier reach; selection policy and proposer; Flux source verification and the five-fact sample; twin overlay, signal lookup and forward-intel; insurer quote; schedules; the deck.
- The three Flux falsifiers are written and committed before the first sample is taken. A sample that passes with a falsifier undeclared is a fail.

## Out of Scope

- The video as the deliverable or the clock.
- A power layer beyond portability as a priced cage.
- Covert sensing and real surveillance data.
- Rewriting history in place. Superseded documents get banners.
- Reopening the 114 re-ratified decisions.
- The eight graduated grilling tickets (27, 30, 31, 35, 37, 46, 48, 51). None blocks the slice.
- Per-workload de-posture inside a Namespace tier. Ticket 27 decides it.
- Lifting the original apps, the handbook render, priced holes beyond the slice, switching cost, the misuse catalogue grade (tickets 33, 34, 38, 44, 45). They follow the slice.
- A move from Kyverno v1alpha1 to v1beta1.

## Further Notes

- Build order: 21, then 25, then 26, 28 and 32 in parallel, then 40, 41, 42, then 29, 49, 50, then 43 and 47. The harness grows one step at a time in the same order and reports could-not-look for steps not yet built.
- Known residuals: step 4 reads could-not-look until ticket 40 lands; the isolated default must not flip before the platform's infra declaration lands; the per-tier reach synchronize gap; the EOL-ramp price may misprice.
- Ratification: tickets 04, 07, 08 and the 2026-08-28 batch are provisional. D1 to D5 are decided with the owner's reason. The owner overrode the five-decisions-per-day rule for the batch.
- Vocabulary: CONTEXT.md as merged 2026-08-28. There is no gate. Everything is caged. Price and cage; never count, refuse or file. Never an exemption.
