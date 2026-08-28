# Orchestrator notes — drift review (2026-08-27)

## Owner steer (AskUserQuestion, 2026-08-27)
- North star: "one loosely coupled 'system' but its a broader whole eco-system, with the orgs as an example consumers to demonstrate the whole eco-system operating."
- Bare agree / letter replies: treat ALL as provisional; report re-presents each with then-recommendation, now-recommendation, verdict.
- Live verification: yes, full, read-only. Start Docker/KiND if needed. No pushes, merges, deletes.
- Output: exhaustive report + re-baselined north-star doc + ranked gap/reversal list. No code changes.
- Owner's own evolution: binary admission -> cage/constraint shape; how risk assessment was done and what was modelled.

## My reading of the arc (from all 68 sessions, user side read in full)
Phase 0 (Jun 6 - Jul 14): PRD/ADRs/research. Faithful-to-intent re-implementation of Policy as [Versioned] Code on Flux.
Phase 1 (Jul 14-20): faithful-floor (26) + real-estate (16) epics; adversarial waves; show+tell -> "slideware", "not real", "cardboard cutout".
Phase 2 (Jul 23-Aug 4): talk-spec wayfinder. Owner ambition expands: risk-proportionate governance, FAIR £, hourglass (appetite->principles->controls->enforcement->evidence->balance sheet), regulators as upstream feeds (nist, ico), war-gaming AI opening signed PRs, Wardley, insurance/actuarial, "all of this is 'the policy'" (no exemptions), graded enforcement / cages / degraded states, posture-as-identity (SPIFFE/SPIRE), EUD/human identity, six orgs, "build everything", "nothing is a nice to have", "no cuts". 27 build tickets; estate monorepo; 3 KinD clusters; pitch v1-v3; demo-deck rejected then accepted.
Phase 3 (Aug 4-Aug 19): twin reset. "trash almost all... no actual risk modelling, wardley mapping... develop skills first... start from basics". Digital twin: sense any signal, Wardley spine, fast-forward/rewind/play, one £ currency across HR/security/strategy, falsifiability/backtests, weather forecast, contamination controls, Netflix/Intel/Carillion. 22 decision tickets (letter answers), 93-story spec, 92 build tickets, twin/ Python (33k lines). Governance demoted to "one enactment arm"; estate called "prior to test". Flux "integral unless proven otherwise" -> drift instrument, verdict pending. Owner Aug 19: v5 pitch "fucking shit... nothing about Monte Carlo and continuous refreshing"; wants niobium/quantum Wardley scenario; regulators publishing machine-readable fines; "reference arch + platform + economic platform for risk feeds (Gartner/Bloomberg-style)".
Phase 4 (Aug 19-25): back to estate. multi-org-estate (split everything; filter-repo; real orgs; dual sign; Renovate), govern-what-you-dont-control (COTS wrap/shim; "you're always caged even if permissive"; "never an exemption ledger EVER"), computed-semver (semver computed from verdict impact; OO-style inheritance "from others, not itself"; "no real gate anymore, just cages"), policy-composition (cross-party composition; what gets signed; feeds re-price never apply; baselines; control claims; governed namespace). Docker-not-running incident Aug 25 ("how on earth are you saying its working"). enact_guard disposition made configurable. Pitch v6 built Aug 25 (20 min, estate + twin).

## Drift hypotheses to test (not conclusions)
H1. Two centres of gravity (estate vs twin) were each declared the whole at different times; owner's north star is an eco-system containing both, loosely coupled. Neither spec states the eco-system.
H2. The twin's "propose only", "one enactment arm", and "prior to test" framings were letter/bare answers during a marathon grill (Aug 4-5) and may not reflect owner intent; owner's Aug 19-25 words treat governance as central.
H3. Risk assessment: the estate has fair.py + scenarios (talk-spec); the twin has PERT/Monte-Carlo/TVaR/credibility (twin/). Two risk engines exist despite "no second risk engine" (policy-composition standing preference). Owner's Aug 19: risk should be proportionate to the org (per-customer, % global revenue), regulator-published. Check which engine the cages use.
H4. Cages/graded enforcement: owner's evolution to "always caged, spec of the cage changes"; check whether the built cage-tier/graded layer matches (tiers, priced verdicts, proposer turns the knob).
H5. Feeds marketplace / regulators publishing machine-readable penalties: ico schema exists; is there a "feeds" party? Org policy-as-versioned-feeds does not exist. Check platform/feeds.
H6. Wardley engine wired to feeds/wargamer: talk-spec had platform/wardley; twin has map render. Owner's niobium scenario: was it built?
H7. Honesty: many tickets "done" with offline-only proofs; live beats partial; 28/56 scripts covered by honesty gate; reds on Aug 25 unfixed; Docker incident. Check what "done" means per effort.
H8. Original thesis items (multi-version coexistence, Renovate bump PR, orphan guard, OSCAL/C2P, shift-left, handbook, sunset) — did they survive the trash-and-rebuild into the six-org estate, or are they only in the original org?
H9. Identity/EUD/SPIRE/Istio/OpenBao/Pomerium/vTPM: large build in talk-spec; partial; does the north star need it?
H10. Demo/talk drove build ordering repeatedly (pitch v1-v6); owner said talk is a byproduct (twin phase) and later "this is a demo of it all".

## Workflows launched
- wf_546bde91 grilling-reconstruction -> scratchpad/grill_out/*.json (42 sessions, sonnet)
- wf_38442ed7 spec-inventory -> scratchpad/inventory/*.json (22 groups)
- wf_4ae89e53 live-verification -> scratchpad/live/*.json (8 probes)
- wf_efb51ef2 ambition-timeline -> scratchpad/ambition/*.json (4 chunks, opus)
- (next) twin code map -> scratchpad/codemap/
- (after clone) estate code map -> scratchpad/codemap/

## Report plan
1. Executive summary (drift verdict against eco-system north star).
2. The ambition, in the owner's words, as a timeline (from ambition/*).
3. What was decided: per effort, with provisional-decision audit (from grill_out/* + inventory/*): then-recommendation, now-recommendation, verdict.
4. What was built and what actually runs (from live/* + codemap/*), per capability, with honesty grade.
5. Drift analysis per theme (H1..H10), each with evidence.
6. Contradictions and duplications across efforts.
7. Re-baselined north star (eco-system: publishers, regulators, feeds marketplace, platform, adopters, twin as intelligence, cages as enforcement, £ as currency, provenance).
8. Ranked gap and reversal list.
Appendices: decision ledger, ticket ledger, verification captures index.

## Decision ledger stats (grill_out, 2026-08-27)
- 482 decisions, 42 sessions. reply kinds: bare_agree 233, bare_letter 73, elaborated 50, deferred 48, pushback 40, engaged 28, correction 10.
- Architectural (254): bare_agree 121 + bare_letter 36 = 157 (62%) bare. Scope (53): 28 bare.
- Accepted-recommendation among bare replies: 282/306. => the assistant's recommendation shaped ~60% of architecture.
- Ledger: scratchpad/DECISION_LEDGER.json (all sessions, all decisions). Bare-architectural list saved in tool-results b87xozmde.txt.
- Next: provisional-decision audit workflow (opus/fable): for each bare architectural/scope decision, then-rec vs now-rec against eco-system north star + owner's stated evolution (cages, risk modelling). Needs inventory + live + ambition first.

## Inventory takeaways (INVENTORY.json, 22 groups) — cross-document contradictions to carry into the report
- Hub repo: docs/ARCHIVE.md declares the hub "superseded, research-only, no further feature work" (mo-12), yet PRD/README/north-star read as live with no banner; archive checklist NOT DONE. twin/ and verify/ and talk/ live in the "archived" hub.
- talk/deck.md + talk/verify-all.sh = estate-only, 24 offline + 3 live beats; pitch-v6 = 81 segments, estate + twin, 28-of-56 honesty gate. Relationship unstated.
- multi-org-estate destination "28/28 live green" never reached: mo-01 25+3skip, mo-11 25 pass/3 fail, mo-12 22 pass/6 fail; map still says 28.
- policy-composition: ticket 18 file says ready-for-agent/unchecked while map says "built and landed, signed v1.1.0 on all three adopters"; tickets 09-12 "not landed" vs ticket 17 "committed on wip branch" vs 18 "real tags".
- computed-semver: spec/tickets say platform 1.0.0 + policy 1.0.2 + 2.0.1; shipped tags v1.0.0, policy/v2.0.0, policy/v3.0.0, policy/v2.0.1 (release/2.0.x). Boxes ticked with old numbers.
- twin: Flux drift instrument's hourly crontab never installed; 90% floor permanently unreachable from 2026-08-16; verdict pending forever. ENACT_MODE=development (permissive). Propose-only refusal built, PR channel NOT wired (ticket 66 unclosed). Six "skills" are keyword heuristics. No feeds/markets/Flux/K8s/GitHub I/O anywhere in twin/. Substrate generator is toy. HMAC signing (shared key), not gitsign.
- twin map/spec framing: "prior to test", "one enactment arm", "talk is a byproduct", "bin estate/ and the KinD clusters" — all reversed in practice by Aug 19-25 estate work, never reconciled in twin/map.md or spec.md.
- talk-spec build: all 27 tickets re-statused 2026-08-20 (board was wrong both directions); identity plane (SPIRE/Istio/OpenBao) partial with contradictory comments; proportionality "load-bearing live beat" is actually offline; EUD "no VM ever built".
- Exemptions ledger was SHIPPED in talk-spec build (05) then BANNED and deleted (govern-what-you-dont-control 05). CONTEXT.md: "banned concept".
- ADR-0007 governance agent: two in-text corrections; demonstrator opens issues not PRs; scoped token never existed. wargamer.py docstring overclaimed gitsign stamping (ADR-0015 corrected).
- Two risk engines exist: platform/fair/fair.py (talk-spec seam 1) and twin/ risk engine (pert/severity/pricing). policy-composition standing preference: "no second risk engine, no second appetite store".
- Regulator pins: institutions pin nist directly; nobody pins ico as GitRepository (penalty schema by separate feed route). No policy-as-versioned-feeds org exists.
- Honesty pattern: every effort has post-hoc correction waves; tickets marked done with unchecked ACs (twin 06), stale banners, counts drifting. HISTORY.md self-corrects 4 times.
- Research/22 D1.2 pin-vs-range "sharpest cross-doc disagreement" left as open register, never resolved by grilling per file's own statement.

## Live verification takeaways (LIVE_RESULTS.json, 2026-08-27, read-only)
- talk/verify-all.sh offline: 17 PASS / 8 FAIL / 3 SKIP-live, exit 1. --live (after one talk/up.sh driftwood): 17 pass / 11 fail / 0 skip, exit 1. "SOME BEATS WOULD FAIL ON STAGE".
- All three live reconcile beats FAIL: tuppence+ludlow GitRepository has tag only, no commit pin (contradicts ADR-0001 "pinned on tag AND commit"); driftwood verify-reconcile asserts nist 1.0.0 while tree pins 1.1.0 (verifier behind content).
- ResourceSet fan-out NEVER reconciled on kind-driftwood (no resourceset objects); cluster carries hand-applied 1-0-0/2-0-0 only; require-nonroot-3-0-0, cage-tier-2-0-1, stamp-posture-2-0-1 absent; up.sh reports posture+cages "degraded".
- Two purely offline gate defects: shift-left ci-check.py passes a workload that should fail (±1 window broke when 2.0.1 inserted); wargamer gate same root cause. Both are listed as passing OFFLINE beats in verify-all.
- Identity substrate broken: spire-agent CrashLoopBackOff 398 restarts (6d22h); no sidecar injection; mTLS beat and tuppence reach/secrets flagship fail. Pomerium pod absent though up.sh says ok. currency-controller CronJobs erroring HTTP 404 continuously.
- verify-all covers 28 of 54 scripts on disk (memory said 56). Of 54: 38 pass, 14 fail, 2 timeout. Real defects outside the gate: verify-governed-namespace-guard.sh (render-governed-namespace-guard.py missing on disk), verify-coverage.sh AssertionError (2.0.1/patch), tuppence adopter-gate cosign identity mismatch.
- twin: all 5 beats PASS; grade 73/73 full; drift red-by-design (floor unreachable); `twin verify` bare: VerbError no perspective 'the-operator' in overlay 'netflix', and a second invocation hung 15 min -> timeout. ENACT_MODE=development.
- spikes: cs-06b self-check FAILS against moved-on estate; c2p-validatingpolicy-oscal hung and left a stray KiND cluster 'c2p-spike' running (tell owner; not deleted).
- GitHub: 7th org policy-as-versioned-feeds does not exist. flux/policy: 8 of 12 tags verified=false reason=bad_cert (anomaly). Satellite bot tags verified=false/no_user (keyless). Open unmerged "Configure Renovate" PRs on ico, nist, platform since 2026-08-21. Original org fleet/policy live and still referencing each other; apps archived.
- pytest: first probe aborted at 23% with visible F markers; rerun in progress (task btu273izm) -> live/pytest-rerun/.
- pytest rerun (29 min): 1530 passed, 13 failed. 12 = tests/test_enact.py layer-2 refusal tests (guard permissive under ENACT_MODE=development). 1 = test_invariant_suite: invariant 42 drift_window_was_declared_before_it_was_measured FAILS: probe samples exist but drift window/forced-campaign.yaml never committed, so pre-registration cannot be shown. mypy: clean, 158 files.
