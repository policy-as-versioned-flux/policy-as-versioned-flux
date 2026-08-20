# Map — the estate becomes genuinely multi-org, and genuinely green

Label: `wayfinder:map`. Charted 2026-08-19.

## Destination

The estate is **actually complete and actually multi-org**: `estate/talk/verify-all.sh --live`
reports **28/28 green with no vacuous checks**, and the six institutions are **six real GitHub
organisations** holding their own repos, consuming each other as signed, versioned, Renovate-bumpable
dependencies over the real internet. The demo's claim "six live organisations" becomes literally true.

Reaching it means: the live identity chain works (tickets 14→15→17 of `talk-spec` close for real),
every verify script fails when it cannot see, the split is done with history preserved, and the
war-gaming scenario library is substantially expanded.

## Notes

**Domain.** Governance-as-priced-judgement estate: `estate/` holds six units (`platform`,
`driftwood`, `tuppence`, `ludlow`, `nist`, `ico`) plus cross-cutting `verify/` and `talk/`.
Read `CONTEXT.md`, `estate/README.md`, `estate/talk/RUNBOOK.md`, and the `talk-spec` build tickets
(`.scratch/talk-spec/build/`) — 14 and 17 are the reopened ones.

**Vocabulary — fix this early (see ticket 03).** "Organisation" is currently unowned and means three
different things: a GitHub org, a modelled institution, and a directory. `CONTEXT.md` defines none of
them. Settle the glossary before the split hard-codes the ambiguity.

**Execution is in scope.** The owner chose destination (b) — the estate actually complete, not merely
a plan for it. So `task` tickets here *do* the work; this map is not planning-only.

**Standing preferences.**
- Assume internet always. The old "no venue-Wi-Fi dependency" guarantee in `RUNBOOK.md` is a
  **declared false constraint** and is being removed, not worked around.
- Split preserves history (`git filter-repo`), and the hub **loses** `estate/` — the six repos become
  the source of truth, not a mirror of a monorepo.
- Honesty over green. A check that passes because it could not look is worse than a red one; this
  effort has already found three.
- **`pitch-v5.mp4` is internal-only until the split lands.** It narrates "six live organisations",
  which is six directories and six empty orgs until then. Not a re-cut — just don't put it in front of
  a customer or a conference while that line is false. Cheapest honest fix if it is needed externally
  sooner: re-record that one segment (~20s, one act), not the deck. The entitled replacement sentence
  is settled — see the organisation-glossary ticket: "Six independent GitHub organisations — a shared
  platform that prices its own risk like everyone else, three regulated institutions, two regulators."
  
- Skills each session should consult: `/grilling`, `/domain-modeling`; the repo's
  `docs/agents/issue-tracker.md`.

## Decisions so far

<!-- index of closed tickets; one line each, linking the ticket that holds the detail -->

- [Do prediction markets belong in the £?](issues/13-prediction-market-feed.md) — **benchmark only,
  and therefore no estate work**: markets may grade forecasts, never price a control. The twin's own
  research measured the overlap at ~1 of 10 scenario families and 0% of the org overlay, so scoring
  the estate's projections against a venue trading none of them is arithmetic without an answer. The
  mechanism stays in the twin.
- [The forward layer can only ever raise the bill](issues/15-monotone-pessimism.md) — **yes, via
  cost-of-controls, gated on corroborated enactment.** A cheaper defence lowers what a control costs
  to run, not attack frequency. The estate has no corroboration mechanism today (`deployed_move` is a
  declared field, not evidence), so the gate must be built rather than borrowed.
- [An institution answers to many masters](issues/17-many-obligation-sources.md) — overlap and
  duplication are **permanent and expected**, not to be normalised away; obligations scope
  **per-workload**, not per-institution; one breach can draw **several consequences** and the £ takes
  the worst case; genuine deadlock gets a **deferred** reconciler (which must resolve between
  obligations, never waive one — exemptions are banned). Curated bundles are a convenience, never the
  only path. `ico`'s parallel feed stack is the evidence the shared kind is already wanted.
- [Split mechanics and cross-org verification](issues/07-split-mechanics-decision.md) — platform ships
  the verify harness as a pinned dependency, `verify/` and `talk/` become **separate repos in the hub
  org**, and tags are **dual-signed** (gitsign + OpenPGP) because Flux's `spec.verify` only speaks
  OpenPGP — a time-boxed bridge until Flux supports gitsign. Only 4 scripts carry a single-tree
  assumption. Regulator pins stay **direct**, and `README.md:19`'s `nist`/`ico` → `platform` →
  institutions chain is **false** and must be corrected.
- [Settle what "organisation" means](issues/03-organisation-glossary.md) — no collective noun for the
  six; name the kind, but all six are independent GitHub organisations. **Roles compose** —
  publisher / risk-bearer / adopter — and `platform` is already two of them, carrying its own £10k
  band. `org` stays overloaded but documented (renaming churns the artefact provenance surface).
  Terms written into `CONTEXT.md`.
- [Research the full war-gaming scenario slate](issues/05-scenario-slate-research.md) — 4 components
  (2 fire, 2 deliberately inert); **feed carries the trajectory, library carries the posture**; K=4.0
  validated by measurement but its "widen K" comment is unsafe (cage TCoR is non-monotone). Surfaced
  three defects that outrank the slate: the forward layer is hardcoded to one institution, it is
  monotone-pessimistic, and `pq-cryptanalysis`'s declared `transfer` is never cheapest at any band.
- [The forward layer spoke for one institution](issues/14-forward-layer-is-single-institution.md) —
  **fixed: it is per-institution now.** `forward_signal`/`forward_into_wargamer` take `org` as a
  required argument (no hardcoded `driftwood`, no default); the `_all()` variants read the three
  institutions from `../risk/appetite.json` so the set can't drift from the bands. Confirmed the
  ticket's own claim: at ludlow's band phishing does not drift and ransomware already drifts at the
  reactive base; proposal counts are driftwood=2, tuppence=1, ludlow=1 (4 total, not 3× driftwood).
  `selfcheck()`'s vacuous `credential-stuffing-aas` assertion is fixed in place, isolated with a
  synthetic clone carrying a real `base_risk`.
- [The researched scenario slate is landed, signed and machine-checked](issues/06-scenario-slate-implement.md) —
  4 new `market-intel.json` components (2 fire: `agentic-commit-access` absorbed at `fix`,
  `pkg-registry-worm` flips `cage->fix`; 2 loud-but-inert: `nb-refining-capacity` the ticket's
  required non-firing entry, `pqc-transport-migration` F2's known-inert twin of
  `spiffe-workload-identity`) plus `hyperscaler-region-concentration` in the standing library; the
  unsafe "widen K" doc comment is corrected, K=4.0 unchanged. `verify-wardley.sh` / `verify-wargamer.sh`
  / `verify-feeds.sh` all pass. F4 (`pq-cryptanalysis`'s never-cheapest `transfer`) stays open —
  named in the research, not in this ticket's text.
- [The exemption ledger is gone; the 28/28 denominator is confirmed, not moved](../govern-what-you-dont-control/issues/05-remove-the-exemption-ledger.md) —
  `verify-all.sh` drops `verify-exemption.sh` (offline count 26→**25**); the live beats are
  unchanged at 3, so the full `--live` total stays **28** (25 offline + 3 live). This map's
  destination already named 28 as the target, so removing the banned ledger lands on the same
  number rather than moving it. Offline-only (`estate/talk/verify-all.sh`, no cluster) is 25 beats,
  not 26.

## Not yet specified

<!-- in-scope fog: real, but not yet sharp enough to ticket -->

- **The demo re-cut.** `pitch-v5.mp4` says "six live organisations" and shows no real screenshots.
  Once the split lands, both the claim and the missing screenshots can be fixed together — but what
  the deck should show of a six-org estate isn't visible until the split exists. Explicitly
  deprioritised by the owner ("don't stress the video as scope").
- **The headline→coordinate classifier.** Nothing ingests a news headline and decides which Wardley
  component it moves, or by how much; today that is an analyst's judgement. Whether this becomes real
  machinery — and if so, whether it proposes a signed intel diff rather than auto-applying — waits on
  how far the scenario library expansion goes.
- **Per-org CI.** Six repos each need their own gate workflow; what runs where, and how the
  cross-org version cross-check works when the checkouts are separate, is not yet clear.

## Out of scope

<!-- ruled beyond the destination; never graduates -->

- **Archiving the old `policy-as-versioned-flux` estate** (`talk-spec` ticket 27 and the ~16 old repos
  in the hub org). A separate cleanup, not on the route to a working multi-org estate.
- **Policy-version inheritance, and computable semver bumps.** Policies are code, so a version could
  `extends` its predecessor rather than restate it — today `v2.0.0/require-nonroot.yaml` copies
  `v1.0.0`'s CEL expression byte-identically, hand-edits the version string in three places, and
  appends one rule. It would have to be *source-level* inheritance rendering down to today's flat,
  per-version `matchConditions` self-scoping, since the shared-webhook alternative is documented to
  break coexistence. The strong version of the idea: `CONTEXT.md` already defines semver by
  **verdict impact on currently-compliant workloads**, and `verify-shift-left.sh` already runs a
  workload against two versions offline — so the major/minor/patch bump could be *computed* rather
  than asserted. Genuinely good, genuinely uncaptured, and **not on the route to this destination**:
  the split concerns version transport, not version authoring. **Now charted as its own effort** —
  see [`.scratch/computed-semver/map.md`](../computed-semver/map.md), whose destination is a release
  gate that derives the bump and refuses a tag the evidence contradicts. Inheritance is fenced there
  to one question (does the delta need it?) rather than a refactor.

- **Building out the `twin/` project itself.** Complete at 73/73; its own roadmap is a separate
  effort. Note this is *not* a blanket exclusion of the twin: its `market_signals.py` mechanism and
  the `price_levels_never_probabilities` invariant are live candidates for reuse here — see the
  prediction-market feed ticket. Reusing twin machinery is in scope; extending the twin is not.
