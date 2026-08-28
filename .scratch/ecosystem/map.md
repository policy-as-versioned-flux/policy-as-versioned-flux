# Map — the eco-system, operating

Label: `wayfinder:map`. Charted 2026-08-28. Supersedes the nine earlier efforts under `.scratch/` as the single map for what comes next. Their maps and tickets stay as the record.

## Destination

Every joint in [NORTH-STAR.md](../drift-review-2026-08-27/NORTH-STAR.md) §4 (regulator publishes; Renovate pins; the £ crosses a band and a proposal PR opens; Flux reconciles the cage; the twin plays a signal forward; provenance; honesty) has an owning ticket the truth surface can grade, and the eco-system has run end to end once, on a clock, with driftwood, tuppence and ludlow consuming. Then hand off to `/to-spec`. This map carries execution: tickets build, not only decide.

## Notes

- The north star is ratified. The owner's answers to 41 re-grills and 22 reversals are binding: [REGRILL-ANSWERS.md](../drift-review-2026-08-27/REGRILL-ANSWERS.md). The ranked gaps are [GAPS.md](../drift-review-2026-08-27/GAPS.md).
- Build order: the seven steps in NORTH-STAR §4, thinnest slice end to end first (one regulator, one adopter, one feed, one cage move, one twin forecast, all real), before widening. The truth surface is built in parallel because it grades the slice.
- Vocabulary: there is no gate. Everything is caged; the spec of the cage is the only variable; the £ picks the spec; the bottom rung is "too expensive to run or not functional". Never an exemption, never an exemption ledger. Price and cage; never count, refuse or file.
- Versioning follows ESLint shareable configs: every package its own semver; a composed set is a new package; republish and inner-source are normal.
- Schedules run the LLM-free data gathering. Reasoning is packaged as Claude Code skills a human runs over the gathered results. The reviewed PR is the unit of adoption.
- Process rules (from the drift review): at most five decisions put to the owner per day, none inside an implementation run; a bare "agree" or letter does not ratify architecture, so a decision is recorded with the owner's reason or it stays open; a spec does not advance to tickets without a recorded owner confirmation; done is defined by the truth surface, never by the demo; every ticket's definition of done includes wiring its check into the gate.
- Skills to consult: `/mattpocock-skills:grilling` and `domain-modeling` for every grilling ticket; `/mattpocock-skills:research` for research tickets; `/arckit:wardley` and `/arckit:impact` for the twin; CONTEXT.md and docs/adr/ before any work.
- Identity is spine, not cut (charting Q2). The feeds and insurer parties are real orgs the owner creates (charting Q4).

## Decisions so far

<!-- one line per closed ticket -->
- [04 — The feed contract](issues/04-the-feed-contract.md) — one envelope (`kind`, `name`, `version`, `published_by`, `published_at`, `payload_schema`, `payload`), signed by the gitsign tag and nothing else; parent kind closed to `controls | implementations | feed` with a free `name`; subscription is `inherits[]` plus `since`; discovery is `publishes[]` on the publisher's `party.yaml`, no central catalogue; revocation is a new version plus `revoked[]`, a revoked pin is a priced hole. Owner agreed twice without a reason; recorded as such. ADR-0019.
- [03 — The truth surface](issues/03-the-truth-surface.md) — `talk/verify-all.sh` discovers all 56 scripts by glob, grades PASS/FAIL/SKIP by exit code, ends with one dated TRUTH line that `truth.yml` writes daily to `talk/truth.log`; first number 40/16/0 of 56; `twin.yml` split and scheduled; invariants 42 and 45 green, 43 and 44 red by decision; five unit-repo PRs (platform 3 and 4, driftwood 11, tuppence 8, ludlow 7) carry three-outcome live tails, substrate-first, the semver-distance window and pin-reading verifiers, unmerged; post-mortem in HISTORY.md; pitch-v6 reds re-attributed; tuppence scenario E, the six live-object reds and the 12 enact tests stay red and named.
- [02 — Supersede and rebaseline the documents](issues/02-supersede-and-rebaseline-the-documents.md) — NORTH-STAR.md is at the root and is the one referent; twin map, twin spec and ARCHIVE.md carry dated banners; the transport doc is renamed; CONTEXT.md's Cage, Policy version, Orphan guard and Proposer entries speak cage and schedule, and a Twin entry exists; the-whole-model.md is redrawn with no neck, no ledger, pins as crossing edges, tuppence and driftwood exploded. ADRs 0006, 0010, 0014, 0015 are not rewritten; tickets 09 and 10 own the superseding ADRs.
- [01 — Create feeds and insurer orgs](issues/01-create-feeds-and-insurer-orgs.md) — both orgs and both empty repos exist; Renovate installed on all repos in both (verified); Mend non-silent settings set by the owner, unverified.
- [05 — Research: Cedar for composition](issues/05-research-cedar-for-composition.md) — No-go: `symcc implies` really does decide strictly-stricter, but over 2 of the composed set's 6 members, and on the cage spec it only reproduces `cage_engine.py` Track 2. Its one real edge — catching a *conditional* widening Track 2 is blind to — is unreachable unless ticket 09 lets the tier floor be scoped; that is the trigger to revisit.
- [06 — Research: ESLint versioning semantics](issues/06-research-eslint-versioning-semantics.md) — copy ESLint's packaging model (every pack self-versions, a mashup is a new package, a severity-only override never touches the rule body, republish and inner-source are ordinary) but not its bump table, because ESLint's minor may break your build and answers that with `~` while ADR-0002 already pins everywhere; supersede, inner source and publisher-declared compatibility have no estate form at all, a regulator's baseline addition is a major nobody classifies, and the tier floor is the one thing ESLint never had to build.

- [07 — Org size obligations and currency](issues/07-org-size-obligations-and-currency.md) — the adopter signs `size` (turnover, customers, data subjects, headcount, `as_of`) and `obligations` (regime names) in its party artefact; `pct_of_global_turnover` gives `hi = min(rate × turnover, cap)` with the examples scaled by `hi / cap`; stale size widens to the cap, never refuses; every amount carries a currency, `reporting_currency` defaults to USD and the adopters declare GBP; FX is a signed `fx` feed; a missing regime price or FX rate is an instrument fault and refuses. Owner agreed; reason given only for the currency default. ADR-0020.

## Not yet specified

- The thin-slice build tickets themselves: one per NORTH-STAR §4 step, derived once the feed contract, the £ seam and the cage ladder tickets close.
- One test seam per eco-system joint (re-grill 30): composition, publisher release, adopter gate, cage tier move, feed fetch, twin-to-estate handoff. Shape follows the joints above.
- The Wardley publisher/consumer split: the twin publishes forward intel; the platform consumes it (H5-06). Waits on the £ seam.
- The forecast book as the marketplace's credibility instrument (reversal 22): continuous scoring, reliability diagrams per publisher, claim scope. Waits on the feed contract.
- Which mechanisms lifted from the original org land where (ticket 13 decides lift-or-retire; placement is fog).
- The eco-system re-cut of the misuse catalogue's affected-parties register and DPIA (waits on ticket 19).

## Out of scope

- The video as the deliverable or the clock. The demo is a read of the truth surface (NORTH-STAR §6).
- A power layer beyond portability-as-a-priced-cage.
- Covert sensing; real surveillance data (permanently excluded).
- Rewriting history in place. Superseded documents get banners.
- Reopening the 114 re-ratified decisions.
