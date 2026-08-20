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
  sooner: re-record that one segment (~20s, one act), not the deck.
- Skills each session should consult: `/grilling`, `/domain-modeling`; the repo's
  `docs/agents/issue-tracker.md`.

## Decisions so far

<!-- index of closed tickets; one line each, linking the ticket that holds the detail -->

- [Research the full war-gaming scenario slate](issues/05-scenario-slate-research.md) — 4 components
  (2 fire, 2 deliberately inert); **feed carries the trajectory, library carries the posture**; K=4.0
  validated by measurement but its "widen K" comment is unsafe (cage TCoR is non-monotone). Surfaced
  three defects that outrank the slate: the forward layer is hardcoded to one institution, it is
  monotone-pessimistic, and `pq-cryptanalysis`'s declared `transfer` is never cheapest at any band.

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
- **Building out the `twin/` project itself.** Complete at 73/73; its own roadmap is a separate
  effort. Note this is *not* a blanket exclusion of the twin: its `market_signals.py` mechanism and
  the `price_levels_never_probabilities` invariant are live candidates for reuse here — see the
  prediction-market feed ticket. Reusing twin machinery is in scope; extending the twin is not.
