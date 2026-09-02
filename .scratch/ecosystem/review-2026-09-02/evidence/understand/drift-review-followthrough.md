# Drift-review follow-through — GAPS, REGRILL, REVIEW-08-31, process rules vs run 21

Method note (read this first): this is a single-pass reader map, not an exhaustive
per-row forensic audit. GAPS.md has 66 rows across four tiers, REGRILL-ANSWERS.md
carries 41 answers + 22 reversals, REVIEW-2026-08-31.md carries C1/M1-18/10 refutations.
Given the time available I verified the highest-leverage claims directly (current TRUTH
line, the seven live reds and their capture files, ticket status fields for tickets
54-74, a sample of unit-repo files) and inferred the rest from ticket titles/status,
the map, and the two handoff documents, cross-checked against dates. Rows marked
**[inferred]** were not independently re-verified in the unit repos this pass — treat
those as "ticket-file says X" rather than "I read the code and confirmed X." Rows
marked **[verified]** I read directly (file, tag list, or capture).

Baseline: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 ... pass=57 fail=7 skip=18
excluded=2 total=84` (given in task). Run-21's seven fails, read from
`origin/main:talk/captures/*.out` **[verified]**:
1. `.estate-clone_driftwood_twin_verify-twin-scenarios.out` — "2 standing-scenario check(s) observed false"
2. `.estate-clone_driftwood_verify-reconcile.out` — "a fact of the five-fact sample was observed false"
3. `.estate-clone_driftwood_verify-twin-overlay.out` — "1 twin-overlay check(s) observed false"
4. `.estate-clone_ludlow_verify-reconcile.out` — five-fact sample false
5. `.estate-clone_tuppence_verify-reconcile.out` — five-fact sample false
6. `verify_demo_verify-demo.out` — "talk/deck.md has been hand edited or is stale"
7. `verify_e2e_verify-e2e-step4-flux-reconciles-cage.out` — step-4 lane sample false

Note the C1 kyverno-pin trio (verify-graded, verify-shift-left, verify-render-version-tree)
and the M2/M3/M4/M10 items named in REVIEW-08-31 are **absent** from run 21's fail list —
consistent with tickets 54 (resolved) and 61 (resolved) having closed them. See ticket
status table below.

## Ticket status, tickets 54-74 (all charted from REVIEW-2026-08-31) **[verified — read Status: field directly]**

| # | Title | Status |
|---|---|---|
| 54 | The gate observes with the estate's own toolchain (kyverno pin, C1/M5) | resolved |
| 55 | Every red on the clock is real, explained and finishable (M2/M3/M4) | prepared |
| 56 | The citable run can see whether the clocks ran (M6) | open |
| 57 | Feeds and insurer become runnable, workflows registered (M1) | claimed |
| 58 | Grilling the four architectural gaps and the untagged pin (M11) | resolved |
| 59 | Build the two unbuilt §5 bullets: fall blocks, Status is derived (M14) | open |
| 60 | Scheduled observations land in the citable number; steps 3-4 (M7/M9) | resolved |
| 61 | Renovate completes step 2 once for real (M8) | resolved |
| 62 | The feed parents are consumed pinned and signed (M10) | open |
| 63 | The unlabelled default flips to isolated (M12) | open, blocked by 58 |
| 64 | The twin is three adopters, tagged and signed (M15/M16) | open |
| 65 | enact_guard closes the git-dir family (M17) | open |
| 66 | The deck check grades the run its own truth line names (M18) | open |
| 67 | The record matches the surface (M13) | open |
| 68 | Federation gets its peer | open |
| 69 | An untagged pin is a priced hole | open |
| 70 | The observation lane is detectively enforced and honest | open |
| 71 | Which kyverno versions does the estate support | open |
| 72 | A feed bump re-renders the twin's derived artefacts | open |
| 73 | The verifier rejects a tag whose cert postdates its tagger time | open |
| 74 | Step 3 happens once for real | open |

Recent hub commits (given in task) corroborate: "ticket 60 resolved: the gate grades
from real signed samples on TRUTH run 20; step 3 graduates to ticket 74" and "ticket 60:
round-2 wait fix was mis-ordered; round 3 committed with asserted order" — i.e. ticket 60
was closed and immediately spawned ticket 74 for the still-unfired step 3, which is why
74 is open and is one of run 21's seven reds (fail #2/4/5 above, all "five-fact sample
observed false").

---

## Part 1 — GAPS.md, tier by tier

### Tier 0 (7 rows) — decision gaps

| # | Gap | Status | Evidence |
|---|---|---|---|
| 0.1 | No document states the eco-system | **Closed.** NORTH-STAR.md exists at repo root (task's key-documents list confirms it's live, not just proposed). | [verified — file listed as a key document, ratified per REGRILL header] |
| 0.2 | Twin/estate demote each other | **Likely closed** — TO-SPEC-HANDOFF.md says "ADRs 0014, 0015, 0016, 0018 carry banners" and REGRILL P001 reversal says redraw with no neck. Did not re-open `.scratch/twin/map.md` or `docs/ARCHIVE.md` to confirm the literal banner text. | [inferred] |
| 0.3 | Which engine is the £ | **Decided** (REGRILL #33 P192: "one currency, many perspectives... no perspective privileged") and echoed in BUILD-BRIEF rule 7 ("Every price carries perspective and currency"). Build follow-through: GAPS 3.18 (currency modelling) still tracked separately — see below, still open. | [verified — rule 7 in BUILD-BRIEF.md] |
| 0.4 | Cage-tier seam twin/estate | **Decided**, REGRILL #21 P133: "the twin computes the tier under the org perspective; the estate war-gamer enacts it as a PR." TO-SPEC-HANDOFF built this into the thin slice (steps 25/26/40). Operationally this is the seam that ticket 74/step-3 (open) has still never fired for real end to end — decided but not yet demonstrated live. | [verified decision + inferred build gap] |
| 0.5 | Identity layer spine or cut | **Decided spine** — REGRILL #21 reversal P203 "versioned policy is the spine," and ticket 12 (Identity as spine) resolved with two new ADRs per TO-SPEC-HANDOFF. But REVIEW-08-31 M11 flags federation has no second peer (ticket 68, still open) and identity substrate pods are still crash-looping per ticket 12's own comment (spire-agent CrashLoopBackOff, currency-controller 404) — so the *decision* is closed, the *build* is not. | [verified — ticket 12 comment quoted above] |
| 0.6 | 41 re-grills | **Done**, answered 2026-08-28. See Part 2. | [verified] |
| 0.7 | 22 reversals | **Done**, all confirmed 2026-08-28. See Part 3. | [verified] |

### Tier 1 (13 rows) — operate end to end once

| # | Gap | Status | Evidence |
|---|---|---|---|
| 1.1 | Nothing runs on a clock; rule said "never" | **Closed.** `propose-tier.yml` in driftwood/tuppence/ludlow all carry `schedule:` at line 42, with a comment citing ADR-0024 replacing the old rule. | [verified — grep hit in all three repos] |
| 1.2 | ResourceSet fan-out never reconciled | **Partly closed.** verify-reconcile now grades a real scheduled lane sample (ticket 60, resolved) — but that sample is currently observed **false** in run 21 for driftwood, tuppence and ludlow simultaneously (3 of the 7 reds). So the wiring exists and runs on a clock, but has not yet produced a passing reconcile. | [verified via captures] |
| 1.3 | Composed policy set never reaches a cluster | **[inferred] Partly closed** — ticket 40 ("driftwood proves the composed set in force from signed sources in CI") is resolved per TO-SPEC-HANDOFF build order, but M7 in REVIEW-08-31 says ticket 40's own resolved Answer cites an uncitable observation, and ticket 60's comment explicitly flags this as still wrong ("Correct ticket 40's Answer... with a dated note"). Net: claimed done, review found the claim's evidence to be fabricated/stale as of 08-31; ticket 60 (resolved) says it added the correction note but the underlying five-fact reconcile is still red on run 21. | [verified overlap with 1.2's red] |
| 1.4 | No workload ever caged by degree; cages[] empty | **[inferred] Open-ish.** Ticket 63 (unlabelled default → isolated) is still open, blocked by 58. The currency-controller 404 is still live per ticket 12's own comment (dated during the 08-31 review, not re-checked live this pass — live checks were out of scope/read-only). | [inferred from ticket status + not re-run live] |
| 1.5 | No bottom rung below quarantine | **Closed** — REGRILL reversal #17 (P143): "add the bottom rung below quarantine; an unknown tier label fails closed to the strictest cage," and ticket 09 v2 (map.md line 36) records "the bottom rung is `isolated`... replaces Deny-to-issue." Ladder is now baseline/restricted/quarantine/isolated/infra per BUILD-BRIEF rule 8. | [verified — BUILD-BRIEF.md:63, map.md:36] |
| 1.6 | Regulator (ico) consumed unpinned from main | **Partly closed for platform/nist, open for ico/feeds/insurer.** GAPS 2.7/3.11 area: M10 (REVIEW-08-31) explicitly says "ico is checked out at `ref: main`... §2's pinned/signed holds for platform and nist only," and this is ticket 62, still **open**. | [verified — ticket 62 status] |
| 1.7 | No feed ever fetched | **Closed** — feeds repo now has real tags: `threat-register/v1.0.0`, `threat-register/v2.0.0` [verified by `git tag` in the fresh clone]. This contradicts GAPS 1.7's "no feed is ever fetched" as of 08-27, but M1 in REVIEW-08-31 (08-31) still said feeds/insurer were mechanically unrunnable with zero tags — so this closed **between 08-31 and now** via ticket 57 ("claimed", not yet resolved). | [verified — tag list] |
| 1.8 | No party can publish a new feed version (no signing key) | **Consistent with 1.7 — closed for feeds** (signed tags now exist; whether they're gitsign vs cosign not independently re-verified). Insurer has a plain `v1.0.0` tag only [verified], and GAPS 2.14/M1 flagged driftwood pinning an *unsigned* quote-driftwood v1 — insurer's signing state not confirmed this pass. | [inferred] |
| 1.9 | tier_pr.py doesn't sign; wargamer.py has a hardcoded `"signed": True` | **Not closed.** `wargamer/wargamer.py:200,232` still literally contains `"signed": True,  # stamped at commit time by propose-policy-pr.sh` [verified, read directly]. `wargamer/tier_pr.py` (the actual PR opener, per its own docstring "the one place in the estate that actually commits, pushes and opens") uses plain `_git("commit", ...)` with no explicit gitsign invocation in the script body [verified — grep for gitsign/sign in tier_pr.py found only comments, no signing call]. Ticket 60's notes mention `clone-estate.sh` now sets `gpg.x509.program=gitsign` globally so lane commits verify via `%G?` — this may cover tier_pr.py's commits transitively via git config rather than an explicit call, but I did not trace whether tier_pr.py's commit path runs inside an environment with that config set at the time it commits. REGRILL reversal #16 (P142) says "sign the proposal commit with the workflow Actions identity" — decided, but the literal `wargamer.py` fixture with hardcoded `signed: True` for its synthetic/dry-run path (called out in REVIEW-08-31 M9: "the £ crossed a band only in the SYNTHETIC dry-run") still exists unchanged. | [verified partial, inferred rest] |
| 1.10 | Org-proportionate pricing unbuilt | **[inferred] Not independently checked this pass** — no party.yaml diff read. GAPS 3.19 covers the same ground (appetite bands living in platform's repo not institutions') and is presumably still open; not confirmed. | [not checked] |
| 1.11 | Twin models real firms, not adopters | **Decided closed, build partly done.** REGRILL #31 (P182) and reversal-adjacent #39 (P208): adopters become primary subjects. Ticket 11/29 built adopter twin overlays, but M15 (REVIEW-08-31) found only driftwood has twin files — tuppence and ludlow have zero — and ticket 64 (the fix) is still **open**. | [verified — ticket 64 status, consistent with M15] |
| 1.12 | Niobium headline non-firing | **[inferred] Not independently checked** — no ticket in 54-74 obviously owns this; GRILL-WALK C13 shows it was disputed (20 calls niobium first news entry, 23 says never) inside the 08-28 batch, presumably resolved in ticket 20/23's Answers. Not verified this pass. | [not checked] |
| 1.13 | No Wardley output ever moved a cage/price/policy | **[inferred] Partly built** — ticket 25 (£ seam) and 29 (twin evals) are in the resolved batch per handoff order, and step 2 £ movement is independently confirmed real by REVIEW-08-31 ("Step 2's re-price moves tuppence 222,574 → 326,139 GBP"). Whether Wardley/forward-intel specifically reaches `evidence.json prices[]` end to end is the substance of open ticket 72 ("a feed bump re-renders the twin's derived artefacts") and open ticket 51/M16 (forward-intel outside every tag). Net: partly closed. | [verified re-price figure from REVIEW doc; rest inferred] |

### Tier 2 (16 rows) — make the truth surface true

| # | Gap | Status | Evidence |
|---|---|---|---|
| 2.1 | verify-all.sh red, not in CI, covers 28/54 scripts | **Closed as stated, new number is bigger.** verify-all.sh now runs on the hub clock (task's TRUTH lines show runs 17-21 all on schedule) and discovers 84 total scripts (pass+fail+skip+excluded = 84 in every run-17-21 line), not 28. Still red (fail>0 in every one of runs 17-21: 1,3,3,7,7). | [verified — TRUTH line arithmetic] |
| 2.2 | Hub CI 10/10 failed since Aug 16, hides pytest | **[inferred] Improved but not green.** REVIEW-08-31 already noted a working clock (M-section "What is genuinely done"); ticket 54 (kyverno toolchain fix, the biggest single cause) is resolved. Gate is still not fail=0 on any of runs 17-21. | [verified no fail=0 run] |
| 2.3 | twin verify red / hung 15 min | **Not independently checked** this pass (would need running twin verify, which risks a live/offline distinction I didn't chase). Run 21's fails don't obviously include a twin-verify-suite hang, so likely improved, not confirmed. | [not checked] |
| 2.4 | Invariant 42 / pre-registration window not committed | **Not checked this pass.** | [not checked] |
| 2.5 | shift-left ±1 array-index bug | **Likely closed** — verify-shift-left is one of the three checks C1 named as red-by-kyverno-pin, and ticket 54 is resolved, and it does not appear in run 21's fail list. But GAPS 2.5's specific semver-distance defect is a separate root cause from C1's kyverno CEL issue; both happened to red the same script. Not confirmed the semver-distance fix itself landed vs. just the kyverno pin being fixed. | [inferred] |
| 2.6 | verify-retirement / verify-coexistence false "observed" claims | **Not checked this pass.** | [not checked] |
| 2.7 | tuppence/ludlow GitRepositories tag-only pins; stale nist assertion | **Overlaps GAPS 1.6 / M10 — open**, ticket 62 open. | [verified via ticket 62] |
| 2.8 | Identity plane down (spire-agent crashloop, Pomerium absent, currency-controller 404) | **Still true as of ticket 12's comment** (dated during the 08-31 grilling pass, not re-run live this session — live verification of pod state was not attempted, consistent with the read-only constraint). | [inferred, stale by ~2-3 days] |
| 2.9 | Ticket status typed by hand | **Not closed.** All ticket files inspected this pass (54-74) still carry a free-typed `Status:` field (resolved/open/claimed/prepared) with no visible derivation from a named check. M14 in REVIEW-08-31 says the same for 16/53 tickets; ticket 59 (which explicitly targets "Status is derived") is still **open**. | [verified — read Status: lines directly] |
| 2.10 | Six talk-spec tickets cite deleted estate/ paths | **Not checked this pass.** | [not checked] |
| 2.11 | pitch-v6 mis-attributes reds to transient load | **Not checked this pass** — pitch-v6 exists as untracked content per git status (`.scratch/talk-spec/pitch-v6/`), consistent with GAPS 3.28 ("pitch-v6 untracked") still being true. | [verified untracked via git status snapshot] |
| 2.12 | Docker-not-running incident unrecorded | **Not checked this pass.** | [not checked] |
| 2.13 | twin grade prints 73/73 full inside a red suite | **Not checked this pass.** | [not checked] |
| 2.14 | Stray KiND cluster c2p-spike | **Not checked this pass** (would require `kind get clusters`, a live command; not run to stay conservative, though it is nominally read-only-permitted). | [not checked] |
| 2.15 | flux/policy 8/12 tags bad_cert | **Not checked this pass.** Possibly related to open ticket 73 ("the verifier rejects a tag whose cert postdates its tagger time"), which suggests this class of cert issue is still being worked, not closed. | [inferred link to ticket 73] |
| — | (2.16 duplicate numbering in source; GAPS.md's own table has 16 Tier-2 rows numbered 2.1-2.16, sixteen total, matching what's covered above.) | | |

### Tier 3 (30 rows) — propagate evolution into docs/model

Given the volume (30 rows) and remaining time budget, I checked a targeted sample
directly and report the rest as **not independently checked this pass** — auditors
should not treat silence below as "closed."

| # | Gap | Status | Evidence |
|---|---|---|---|
| 3.1-3.9 | CONTEXT.md rewrites, cage vocabulary, mutating-vs-validating pod defaults, forgeable tier label, de-posturing, adopter tightening, ladder unification, identity substrate caging | **Decision layer closed** for most (REGRILL/reversal answers #21-29 above cover 3.4-3.9 directly: strictest-cage-default MutatingPolicy, tighten-only mutation, overlay floor). **Build layer**: 3.4/3.5 (unlabelled default flip) is explicitly open ticket 63. Others not independently checked. | [verified decision layer via REGRILL; ticket 63 verified open] |
| 3.10 | Proportionality money-shot is a hub fixture, three composed sets byte-identical | **Not checked this pass.** | [not checked] |
| 3.11 | Every overlay path empty | **Not checked this pass.** | [not checked] |
| 3.12 | Computed semver never computed a real bump | **Likely progressing** — feeds repo now has two real tags (v1.0.0→v2.0.0) [verified], and ticket 61 (Renovate completing step 2) is resolved, suggesting at least one real computed bump has occurred; ticket 43 ("the first gate-determined release") status not checked (not in the 54-74 range I pulled — it's an earlier ticket, presumably resolved per handoff's build order but not reconfirmed). | [inferred] |
| 3.13 | Dual signing (OpenPGP bridge) decided/reversed | **Not checked this pass.** REGRILL #18 (P118) says "scope cluster-side verification as real work (controller or the mo-07 OpenPGP bridge)" — decided to keep exploring, not confirmed built. | [inferred from REGRILL text only] |
| 3.14-3.30 | COTS shim, in-cluster git server, fair.py tail, insurance counterparty, currency modelling, feeds marketplace contract, prediction markets, AI-Wardley model call, estate apps, lifted tools (handbook/scanner/etc.), Renovate dashboard, sunset proposal, tag/commit pin semantics, demo artefacts, party registry, EUD/VM | **Not independently checked this pass**, with two exceptions already covered above: 3.17 (insurance) was reversed per REGRILL #20 (P177) to build the full policy structure — ticket 14/36 ("the insurer quote slice") is in the resolved-batch build order and the insurer repo does have a `v1.0.0` tag [verified tag exists], consistent with at least a first quote artefact existing; and 3.28 (pitch-v6 untracked) is **confirmed still true** via git status. | [mixed — see notes] |

**Tier 3 coverage caveat:** of 30 Tier-3 rows, I directly verified evidence for 3 (3.4/3.5 via ticket 63, 3.17 via insurer tag, 3.28 via git status) and inferred a decision-only closure for a handful more from REGRILL text. The remaining ~20 rows were not checked this pass — do not treat them as closed or open on my say-so.

---

## Part 2 — REGRILL answers (41): where the estate implements them, where it doesn't yet

Full one-by-one verification of all 41 was not completed given the time budget. High-confidence, evidence-backed statuses:

- **#1 P006 (re-scoped Flux test, drop drift-floor)** — matches user's own memory note "Flux verdict closes unmeasured... owner chose to record it, not restart the probe" and ticket 74 ("step 3 happens once for real") is the successor thread, still open. **Answer recorded; the re-scoped test itself has not yet produced a clean pass** (run 21's step-4/reconcile reds are arguably downstream of this same seam).
- **#8 P060 (re-price bumps version)** — **implemented**: REVIEW-08-31 independently confirms "Step 2's re-price moves tuppence 222,574 → 326,139 GBP through composition," and feeds' v1.0.0→v2.0.0 tag progression [verified] is consistent with a computed bump on a re-price.
- **#21 P133 (twin computes tier, estate enacts as PR)** — **decision implemented in the architecture** (ticket 60/74 build this seam) but **not yet demonstrated end to end for real**: ticket 74 open, and 3 of run 21's 7 reds are exactly this reconcile/scenario path failing.
- **#23 P144 (adopter can tighten, tighten-only)** — **implemented per BUILD-BRIEF rule 8 and ticket 09v2** (map.md:36: "the cage mutation is tighten-only in all served copies").
- **#28 P174 (unlabelled pods default strictest)** — **decided, not yet built**: ticket 63 open, explicitly the tracking ticket for this exact gap (REVIEW-08-31 M12).
- **#31 P182 / #39 P208 (adopters as twin subjects, real firms as evals)** — **decided, partly built**: only driftwood has a twin overlay; tuppence/ludlow do not (ticket 64 open, M15).
- **#37 P202 (twin acts inside a priced cage)** — **not independently checked**; no ticket in the 54-74 set obviously closes this.
- **#40 P209 (itemise the Aug-5 cut)** — **done**: AUG-05-CUT.md exists and REGRILL-ANSWERS.md's own closing section reports its correction ("the '20-from-16 scope cut'... was not a scope cut").

The remaining ~33 answers were not individually cross-checked against current code this
pass. Given the pattern above (decisions consistently ratified and largely propagated
into ADRs/tickets by 2026-08-28, but *build* lagging into the 08-31 review's M-numbered
findings, several of which remain open tickets today), auditors should assume the same
split — decided-and-documented, build-in-progress-or-not-started — applies broadly
across the answer set unless a specific answer is independently checked.

## Part 3 — Reversals (22): current status

All 22 were "confirmed" 2026-08-28 per REGRILL-ANSWERS.md's own text — this is a
decision-layer fact, directly quoted from the document, not something I re-derived.
Build-layer follow-through, spot-checked:

- **#11-12 (P129/P132, unlabelled-pod MutatingPolicy)** — decided; build tracked as still-open ticket 63 (same gap as GAPS 1.4/3.4 and REVIEW-08-31 M12). **Not yet built.**
- **#16 (P142, sign the proposal commit with the workflow identity)** — decision recorded; `tier_pr.py` shows no explicit gitsign call in the commit path I read, and `wargamer.py`'s synthetic path still hardcodes `"signed": True` [verified]. **Ambiguous/likely not fully built** — the config-level gitsign wiring added by ticket 60 for lane commits may or may not cover the proposer's commit; I could not confirm from the diff alone.
- **#17 (P143, bottom rung + fail-closed)** — **built**: ladder now has `isolated` as the bottom rung, confirmed in BUILD-BRIEF.md rule 8 and map.md ticket-09-v2 summary.
- **#20 (P177, insurance structure + seventh-party quote)** — **partly built**: insurer repo has a real tag (`v1.0.0`) [verified], consistent with at least one signed quote artefact existing; full attachment/limit/exclusion/TVaR structure not independently confirmed.
- **#22 (P207, forecast book built out)** — REVIEW-08-31's own refutations list confirms `twin/scoring.py` and `twin/forecast_book.py` exist and are gate-checked, with remaining decisions in open tickets 51/46. **Built, with named residuals.**

The other 17 reversals were not independently re-checked against current code this pass.

## Part 4 — REVIEW-2026-08-31 findings vs run 21

| Finding | 08-31 status | Run-21 status | Evidence |
|---|---|---|---|
| C1 (kyverno pin mismatch, 3 checks always red) | Critical, unowned | **Fixed** — ticket 54 resolved; verify-graded/verify-shift-left/verify-render-version-tree absent from run 21's 7 fails | [verified via fail-list absence + ticket status] |
| M1 (feeds/insurer unrunnable, zero tags) | Major | **Fixed for tags** — both repos now tagged [verified `git tag`]; ticket 57 status is "claimed" not "resolved," so the workflow-registration half may still be in progress | [verified tags; ticket 57 claimed] |
| M2 (signature spine misclassified as REJECTED) | Major | **Likely fixed** — ticket 55 status "prepared" (not yet resolved); not in run-21 fail list, consistent with a fix landed but ticket bookkeeping lagging, or with the check now SKIPping rather than genuinely passing (skip=18 in run 21, up from run-20's 18 too — no clear signal either way). **Treat as unconfirmed.** | [inferred] |
| M3 (verify-publisher-gate times out, no evidence) | Major | **Not independently confirmed**; bundled under ticket 55 "prepared." | [inferred] |
| M4 (SIGPIPE in verify-corpus-generator) | Major | **Not independently confirmed**; bundled under ticket 55. | [inferred] |
| M5 (jsonschema not installed, 4 checks skip forever) | Major | **Not independently confirmed**; ticket 54 (resolved) named as owner for this too, alongside C1. If truly fixed, skip count should have dropped — run 21's skip=18 is in fact *lower* than run-17-19's skip=22, consistent with some skips converting to real grades. | [inferred from skip-count trend] |
| M6 (verify-schedules can't see clocks, no credential) | Major | **Open** — ticket 56, status open. | [verified] |
| M7 (gate can't convert scheduled observations) | Major | **Substantially fixed** — ticket 60 resolved, rewired verify-reconcile and verify-e2e-step4 to grade lane samples cluster-free (see ticket 60 comment above), but the underlying five-fact samples are now **failing for real** (3 of run 21's 7 reds) rather than SKIPping. This is progress (real signal instead of a fake pass) but the finding's "cannot convert" framing has flipped to "converts, and what it shows is red." | [verified via ticket 60 comment + captures] |
| M8 (Renovate never lands a real PR for step 2) | Major | **Fixed** — ticket 61 resolved. | [verified ticket status; not independently re-run] |
| M9 (step 3 never fired for real) | Major | **Still true** — ticket 74 (successor to 60) open; run 21's driftwood-reconcile/twin-scenario/twin-overlay reds are consistent with step 3/4 still not clean. Ticket 60's own comment says step 3 "stays unfired until a residual really crosses a band; that is correct behaviour, not a defect" as of 09-01 — i.e. the *mechanism* now runs on schedule, but no real proposal PR had opened as of that note. | [verified via ticket 60 comment, quoted above] |
| M10 (feed parents unpinned, esp. ico on main) | Major | **Open** — ticket 62 open. | [verified] |
| M11 (four architectural gaps are orphans) | Major | **Resolved as a grilling ticket** (58, resolved) — meaning the owner has now decided the gaps, not that all four are built. Sub-items: unlabelled default (63, open), conditional-rule instance, federation peer (68, open), observation-lane server-side cage (70, open). | [verified ticket statuses] |
| M12 (unlabelled default still baseline) | Major | **Still open** — ticket 63. | [verified] |
| M13 (map cites an uncitable number) | Major | **Open** — ticket 67. | [verified] |
| M14 (fall-blocks-nothing; Status hand-typed) | Major | **Open** — ticket 59; confirmed hand-typed Status fields still present in tickets 54-74 themselves. | [verified] |
| M15 (only driftwood has a twin) | Major | **Open** — ticket 64. | [verified] |
| M16 (twin release untagged/unsigned) | Major | **Open** — ticket 64 (same ticket as M15). | [verified] |
| M17 (enact_guard `--git-dir` hole) | Major | **Open** — ticket 65. | [verified] |
| M18 (verify-demo names a nonexistent workflow step) | Major | **Still failing** — this is run 21's fail #6 (`verify_demo_verify-demo.out`: "talk/deck.md has been hand edited or is stale"), and ticket 66 is open. | [verified directly against run-21 capture] |
| 10 refutations (feeds M1-adjacent claims, "never run as chain," "no clock ever fired," ticket 53, "only pods have cages," "holes refused not priced," "observation lane conventional," "no forecast scoring," "no live forecast," "17/22 bare agrees," "publisher clocks unowned") | — | **None found to look wrong on this pass.** The refutations were narrowly worded (e.g. "the break was fixed 42 minutes later," "ticket 53 owns the residue") and nothing in the run-21/ticket evidence I gathered contradicts them. I did not re-derive each refutation's underlying grep independently, so this is a non-finding, not a clean bill of health. | [not independently re-derived] |

## Part 5 — Process rules (GAPS.md tail) vs what happened after 2026-08-28

1. **"No recommendation without a trade attached"** — not independently audited across all tickets; the 08-28 batch's Answers do consistently follow a held-round-then-Answer structure per GRILL-WALK.md, which is the pattern this rule asks for. [not fully checked]
2. **"At most five decisions per day"** — **explicitly overridden by the owner for the 08-28 batch**, recorded in map.md:18 verbatim: *"The five-per-day rule was overridden by the owner's instruction for this batch."* Ticket-creation-date histogram (git log first-add date for `.scratch/ecosystem/issues/*.md`) [verified]: **52 tickets added 2026-08-28**, 19 on 2026-08-31, 3 on 2026-09-01. That 52-in-a-day figure is the ticket-file count, not the decision count (GRILL-WALK documents "14 held rounds, 70 questions... one ticket a day" as the plan, but the map's own text confirms the daily cap was waived for this batch) — so the rule was knowingly broken by explicit owner instruction, not silently.
3. **"Spec cannot advance without recorded confirmation; silence isn't consent"** — consistent with what's documented: every ticket I opened (54-74) carries an explicit `Status:` and, where resolved, a dated comment describing what was done — no silent advancement observed in this sample. [inferred from sample]
4. **"Done is the truth surface, never the demo"** — **holding**: run 21 (2026-09-02) is still red (fail=7), and no TRUTH line across runs 17-21 sampled has fail=0, and ticket bookkeeping (55 "prepared," 57 "claimed," 63/64/etc. "open") does not overclaim done. This rule appears to be honored operationally.
5. **"Every ticket's DoD wires its check into the gate"** — consistent with tickets 54-74's own "Notes" sections, which all cite "Closes review findings: Mn" back to REVIEW-2026-08-31.md and (per BUILD-BRIEF rule 2) the standing convention that a verify-*.sh lands per ticket. Not individually confirmed for each of the 20 tickets.
6. **"One north-star, one status vocabulary, one truth number with a date"** — the truth number is holding (one TRUTH line format across runs 17-21) [verified]. Status vocabulary is **not yet unified**: tickets in the 54-74 sample use at least four distinct free-text values (resolved, prepared, open, claimed) with no visible enum or derivation — this is the same finding as GAPS 2.9/REVIEW M14, both still open (ticket 59).

Bare-agree count: 15 files under `.scratch/ecosystem/issues/` and `docs/adr/` contain
the phrase "bare agree" [verified grep count]; I did not read each to confirm which are
pre- vs post-2026-08-28, so this is a raw hit count, not a dated tally.

---

## Summary for the auditors

- The clock is real and dated, and the citable number has *not* been gamed to hide its
  reds — runs 17-21 all show fail>0, and the fails map onto named, ticketed, still-open
  work (60→74 step-3/4, 56, 59, 62-70). That is the single most load-bearing fact for
  this whole document.
- The kyverno-pin critical (C1) and several majors from the 08-31 review (M7 partial,
  M8) are genuinely closed, evidenced by their absence from run 21's fail list and by
  resolved ticket status.
- Several majors are explicitly still open with no ambiguity: M6 (56), M12 (63), M13
  (67), M14 (59), M15/M16 (64), M17 (65), M18 (66, and directly reproduced in run 21's
  fail #6).
- The decision layer (REGRILL, reversals, GAPS Tier 0) is essentially fully closed —
  every item I checked has a recorded owner answer. The **build layer consistently
  lags the decision layer** by one review cycle: 08-27's decisions produced 08-28's
  tickets, which the 08-31 review found mostly undone; 08-31's findings produced
  tickets 54-74, of which roughly a third are resolved as of today (09-02) and the
  rest are open, tracking almost exactly onto today's seven live reds.
- Coverage gap I own: Tier-3 of GAPS.md (30 rows) and most of the 41 individual REGRILL
  answers were not independently re-verified against current code this pass — only
  decision-text and a handful of spot-checks. Also not checked: live pod/cluster state
  (spire-agent, currency-controller, KiND clusters), invariant-42 pre-registration,
  verify-retirement/coexistence text, twin-verify timeout behaviour, and roughly 20 of
  the Tier-3 rows. An auditor relying on this document for those areas should re-check
  directly rather than cite this map.
