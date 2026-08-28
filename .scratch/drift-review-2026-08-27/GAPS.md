# Ranked gaps and reversals

Ranked by what each unblocks for the eco-system demonstration in NORTH-STAR.md §4. Each gap names the smallest honest fix. Sizes: S = under a day, M = days, L = a ticket effort. Evidence ids point to Appendix G (H-ids) and Appendix C (P-ids). Nothing here is done; nothing here was changed by the review.

## Tier 0 — decide before building

| # | Gap | Fix | Size | Evidence |
|---|---|---|---|---|
| 0.1 | No document states the eco-system | NORTH-STAR.md RATIFIED 2026-08-27; still to be committed at repo root | S | H1-01, H10-04 |
| 0.2 | Twin and estate demote each other in writing | Dated superseded banners on .scratch/twin/map.md, .scratch/twin/spec.md, docs/ARCHIVE.md | S | H1-04, H1-06 |
| 0.3 | Which engine is the eco-system's £ | Decide: twin prices a shock under a perspective (intelligence); estate prices annualised residual against appetite (enactment); one converts into the other | S decision, M build | H3-01, H1-13, P133 |
| 0.4 | The cage tier seam between twin and estate | Decide: the twin's Monte Carlo produces the tier number; the estate enacts it | S decision | H1-10, P133, P202 |
| 0.5 | Is the identity layer spine or cut | Decide explicitly | S decision | H8-11 |
| 0.6 | The 41 re-grills | ANSWERED 2026-08-28, see REGRILL-ANSWERS.md | done | Appendix C |
| 0.7 | The 22 reversals | ALL CONFIRMED 2026-08-28, see REGRILL-ANSWERS.md | done | REPORT.md §3.2 |

## Tier 1 — make the eco-system operate once, end to end

| # | Gap | Fix | Size | Evidence |
|---|---|---|---|---|
| 1.1 | Nothing runs on a clock in any of the six orgs; "nothing timed, ever" is written as a rule | Add `schedule:` to the three `propose-tier.yml`; delete the rule from three repos and CONTEXT.md; keep ADR-0010's "timed proposal, never timed application" | S | H4-02, H6-03, P086, P135, P140 |
| 1.2 | The ResourceSet fan-out has never reconciled on an estate cluster | Wire `gitops/platform` into each adopter's Phase-0 reconcile; health-gate behind Kyverno and flux-operator; re-cut the live beats | M | H6-01, H9-01 |
| 1.3 | The composed policy set never reaches a cluster | Make `composed/` the thing the fan-out installs in at least one institution | M | H9-01 |
| 1.4 | No workload has ever been caged by degree; `cages[]` empty everywhere | Drive one pod baseline → restricted → quarantine on driftwood with the £ moving it; fix the currency-controller 404; install cage-tier at the released version | M | H2-01, H2-03 |
| 1.5 | The ladder has no bottom rung; deny resolves to "open an issue" nothing opens | Add a fourth tier below quarantine ("too expensive to run or not functional") so the proposer always has a tier to write | S | H2-03, P143 |
| 1.6 | The regulator is consumed unpinned from `main` | Cut ico tags; `gotk-sync-ico.yaml` with tag and commit in each adopter; Renovate customManager on it; compose at the pinned tag | S | H4-08, H9-05 |
| 1.7 | No feed is ever fetched | One real adapter behind the fixture interface: endoflife.date into the EOL feed on a scheduled workflow that commits a signed version | M | H4-01, H3-08 |
| 1.8 | No party can publish a new feed version (no private key anywhere) | cosign sign-blob keyless in each publisher's release workflow, as cs-27 already did for evidence | S | H4-05, H5-11 |
| 1.9 | The only real PR opener does not sign; the one that claims `signed: True` never commits | gitsign in `tier_pr.py`; delete the literal `"signed": True` | S | H4-10, P142 |
| 1.10 | Org-proportionate pricing is unspecified and unbuilt; all three orgs price ICO identically | Add size (turnover, customers, data subjects) and `obligations:` to each party.yaml; honour the schema's `rate` and `cap_gbp`; pass obligations to the converter | M | H3-02, H9-06, H9-07 |
| 1.11 | The twin models eleven real firms and none of the adopters | Make driftwood, tuppence, ludlow the twin's primary subjects; keep the real firms as the backtest corpus | L | H1-02, P182 |
| 1.12 | The niobium headline is a non-firing map row, absent from the deck | Commit it as a signed intel variant; make the supply-constraint actor a first-class path; raise the headline classifier as a ticket and put it to the owner | M | H5-02, H4-12, H5-05 |
| 1.13 | No Wardley output has ever moved a cage, price or policy | Twin publishes a signed forward-intel artefact; platform consumes it into `evidence.json` `prices[]` that `tier_pr.py` already reads | M | H5-01, H5-06 |

## Tier 2 — make the truth surface true

| # | Gap | Fix | Size | Evidence |
|---|---|---|---|---|
| 2.1 | `talk/verify-all.sh` is red (17/8/3 offline, 17/11 live), runs in no CI, and covers 28 of 54 scripts | Put it on a schedule in the hub; discover scripts by glob with a committed exclusions file; make its output the only citable number | S | H7-03, H7-04, H10-03 |
| 2.2 | Hub CI has failed 10 of 10 runs since Aug 16 and hides pytest behind `twin verify` | Split into independent jobs; triage the 13 test failures | S | H7-02 |
| 2.3 | `twin verify` red: `no perspective 'the-operator' in overlay 'netflix'`; a bare run hung 15 minutes | Fix the fixture or the verb; add a timeout | S | Appendix E |
| 2.4 | Invariant 42 fails: drift window never committed, so pre-registration cannot be shown | Commit `window.yaml` and `forced-campaign.yaml` in the driftwood repo, or read the pre-registration date from a signed sidecar | S | Appendix E, H7-07 |
| 2.5 | shift-left ±1 is array-index adjacency; inserting 2.0.1 dropped 3.0.0 and the beat has been red since; war-gamer beat red for the same cause | Define the window by semver distance; re-cut the flip fixture | S | H6-05, H4-17, Appendix E |
| 2.6 | `verify-retirement.sh` prints "retirement pruned it live" for a Kustomization that never existed; `verify-coexistence.sh` fails offline when any policy is reachable | One rule for live tails: observed-true, observed-false, could-not-look | S | H7-11 |
| 2.7 | tuppence and ludlow GitRepositories pin tag only, no commit | Add the commit; fix `verify-reconcile.sh`'s stale nist 1.0.0 assertion in all three | S | Appendix E |
| 2.8 | The identity plane is down: spire-agent CrashLoopBackOff 398 restarts; Pomerium absent though `up.sh` says ok; currency-controller 404 every run | Fix the two pods; make `up.sh` report a layer ok only when its pods are Ready; make the controller fail loudly on a missing ResourceSet | M | H8-10, H2-01 |
| 2.9 | Ticket status is typed by hand; six policy-composition tickets `resolved` with 0 ACs; ticket 18 `ready-for-agent` while "landed" | Derive `Status:` from a named check, as `twin grade` does | M | H7-01, H7-05 |
| 2.10 | Six talk-spec tickets `done` cite scripts at deleted `estate/` paths | Rewrite citations to `.estate-clone/` paths; let the scheduled gate flip statuses | S | H7-16 |
| 2.11 | pitch-v6 attributes six reproducible reds to transient load | Re-attribute in plan.md | S | H7-13 |
| 2.12 | The Docker-not-running incident has no record and no guard | A post-mortem note in HISTORY.md; every live-claiming script asserts its substrate first | S | H7-15 |
| 2.13 | `twin grade` prints 73/73 `full` inside a red suite; `enactment: full` while `ENACT_MODE=development` | Stamp the aggregate SUITE RED when `twin verify` fails; print the live mode beside enactment | S | H7-08, H7-14 |
| 2.14 | The "real incidents" back-test is an authored fixture written to produce the narrated verdict; narration omits driftwood's 40% exceedance | Three string changes (note, source, banner) and narrate both verdicts | S | H3-03, H3-04 |
| 2.15 | Stray KiND cluster `c2p-spike` left running by the spike probe | Owner to delete (`kind delete cluster --name c2p-spike`) | S | Appendix E |
| 2.16 | `flux/policy` 8 of 12 tags `bad_cert` | Investigate; not fixed by the review | S | Appendix E |

## Tier 3 — propagate the owner's evolution into the documents and the model

| # | Gap | Fix | Size | Evidence |
|---|---|---|---|---|
| 3.1 | CONTEXT.md teaches the gate as a co-equal primitive; "Compliant means admitted"; semver by "fail at the gate" | Rewrite the Lane-keeping-vs-gate and Policy version entries in cage-spec terms | S | H2-08 |
| 3.2 | the-whole-model.md draws the neck and the exemptions ledger | Redraw as the eco-system diagram inside NORTH-STAR.md; no neck, no ledger | S | H2-09, H1-12, P001 |
| 3.3 | `appetite.json` and `risk/PR.md` say enforcement is binary | Rewrite in cage vocabulary: the band selects a tier | S | H3-17 |
| 3.4 | The unclaimed-pod hole was closed with a ValidatingPolicy that ships as Audit | Replace with a MutatingPolicy that defaults the strictest cage at CREATE | S | H2-11, P129, P132 |
| 3.5 | The cage tier label is forgeable; only the version label has a trust boundary | ValidatingPolicy denying an unentitled tier; mutating clobber from the priced decision; absent defaults strictest | S | H8-03, H2-16, P134 |
| 3.6 | De-posturing strips the label that puts a pod in a cage and books no £ | Make de-posture a tier move that keeps the claim and prices the residual | S | H2-12 |
| 3.7 | An adopter that widens its baseline is refused; an adopter cannot tighten its own cage | Price the widening; let the overlay carry a tier floor the adopter sets | S | H2-13, P128, P144 |
| 3.8 | Four enforcement ladders disagree on whether a rung has a price | One cage-spec ladder, priced, projected onto workloads, humans, devices and model actions; delete `access.py` OP_TIER | M | H2-06, H8-12 |
| 3.9 | The identity substrate itself runs uncaged | Label the four identity namespaces governed; wrap the five charts with a platform-machinery claim | M | H8-02 |
| 3.10 | The proportionality money shot is a hub fixture; the three composed sets are byte-identical | Distribute a £-derived control so composition renders `validationActions` from each adopter's band | M | H2-05, H9-02 |
| 3.11 | Every overlay path is empty | ludlow restates an inherited Audit as Deny; tuppence declares an inability so the cage prices; one adopter ships a component-definition | M | H9-03, H9-13 |
| 3.12 | Computed semver has never computed a bump on a real release | Cut one release whose number the gate determines; pass `institution_pins` so the matrix fills | S | H9-04 |
| 3.13 | Dual signing decided and silently reversed | Implement the OpenPGP bridge with `spec.verify`, or record the reversal with a link to the upstream Flux gitsign issue | M | H9-09 |
| 3.14 | The COTS shim decided four times, built zero times | Wrap one real third-party chart (istiod is named) with a stamped version claim in one institution | M | H9-08 |
| 3.15 | Clusters reconcile from an in-cluster git server seeded from the local tree | Repoint one institution at its real GitHub remote at a tag with the resolved commit | S | H9-10 |
| 3.16 | `fair.py` has a bounded light tail; the twin has the GPD tail | Splice `twin/severity.py` in as an optional LM model, or state the bound plainly | S | H3-10 |
| 3.17 | Insurance is a 40% guess with no counterparty | Attachment, limit, exclusions on the appetite object; price transfer off TVaR; a seventh party publishing a quote | M | H3-14, P177 |
| 3.18 | Currency is not modelled; USD and GBP triples are summed | A currency on every amount; refuse to combine without a signed FX feed | S | H3-15 |
| 3.19 | Appetite bands and threat pricing live in the platform's repo, not the institutions' | Move each tolerance into its own party.yaml, signed under its own tag | S | H3-11 |
| 3.20 | The feeds marketplace has no contract, no publisher party, no subscription record | One feed envelope with JSON Schema; a `feeds` publisher org; a subscription record in each adopter's party artefact | M | H4-03, H4-04, H4-16 |
| 3.21 | Prediction markets closed as "no estate work"; forecast book built as "a floor" | Ship market moves as a sixth feed; build the forecast book out as the marketplace's credibility instrument | M | P031, P207, H4-13 |
| 3.22 | "AI-Wardley" has no model call; evolution-judge scores 1.0 against its own lookup; gameplay ships 2 of ~100 plays and no doctrine or climate | Rename or build the model step; disclose the circularity in the skill card; reopen doctrine and climate | M | H5-04, H5-08, H5-09 |
| 3.23 | The estate has no applications; the five real apps live only in the original org | One app repo per adopter with a real vulnerable dependency, so feeds re-price something real | M | H6-04 |
| 3.24 | Handbook generator, notification spine, dashboards, readiness collector, Crossplane, vulnerability scanner did not survive "everything built, no cuts" | One explicit decision each: lift from the original org, or record the cut | S decisions, M builds | H6-06 to H6-11 |
| 3.25 | Renovate's dependency dashboard is off in every adopter | Turn it on | S | H6-07 |
| 3.26 | Sunset lost its proposal half in the estate | A scheduled publisher-side job that turns an EOL date into a retirement PR | S | H6-13 |
| 3.27 | The {tag, commit} pin names an ancestor of the signed tag by design | Make the tag the last commit, or state the meaning in ADR-0001 | S | H6-12, H9-14 |
| 3.28 | Two demo artefacts, neither deliverable: `talk/deck.md` three epics stale; pitch-v6 untracked | Rebuild the deck from pitch-v6's captures around the eco-system spine; commit pitch-v6 | M | H10-02, H10-01 |
| 3.29 | The party registry is one hub-owned file with a string-match guard | Roles in each party's own artefact; the hub file a derived index | S | H9-12 |
| 3.30 | The EUD half never booted a VM | Boot one Linux VM with swtpm and land one real attested device SVID, or record the cut | M | H8-07 |

## Process changes (from H10)

1. No recommendation attached to an architectural question. State the trade, or make the call and record it as the assistant's.
2. At most five decisions put to the owner per day. None inside an implementation run.
3. A spec cannot advance to tickets without a recorded owner confirmation. Silence is not consent.
4. Done is defined by the truth surface, never by the demo.
5. Every ticket's definition of done includes wiring its check into the gate.
6. One north-star document; one status vocabulary; one truth number with a date.
