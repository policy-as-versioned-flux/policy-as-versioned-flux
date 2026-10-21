# 37 — insurance round 2

Type: grilling (HITL)
Status: resolved
Blocked by: 14

## Question

Aggregate versus per-obligation sub-limits; which adopter carries the first quote and whether all three need one before NORTH-STAR §4 step 4; the insurer's own size and whether it is priced as a risk-bearer; whether a priced hole and an excluded item are one retained line or two on the sheet.

## Notes

Graduated 2026-08-28 from ticket 14's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Comments

- 2026-08-31 (ambition review): Note a new blocker: the first insurer quote tag cannot be cut until the insurer repo's workflows register with Actions (zero registered today) — new ticket 57 owns that. Add the ticket-58 question (may an adopter pin an untagged feed) as an input to this ticket's first-quote decision.


## Answer — decisions recorded, 2026-10-21

These four architectural decisions are delegated under [ADR-0025](../../../docs/adr/0025-the-assistant-decides-architecture-and-records-it.md), with their reasons recorded here. They retain [ticket 75 Answer 4](75-grilling-what-is-this-for-the-twelve-questions.md)'s ordinal comparison instrument and illustrative counterparty, and [ticket 79](79-the-pound-inputs-are-published-sourced-and-current.md)'s accepted formula 1. A portfolio distribution and actuarial formula 2 remain deferred; no amount, calibration, quote term or financial authority is created by this decision record.

1. **One annual aggregate, using the existing terms.** Attachment and limit remain annual aggregate, as ticket 14 Answer 1 chose. Attachment is the adopter's signed appetite seen from the other side. No per-obligation sublimit or optional amount is added: there is no declared need or sourced term for one. A later genuine requirement for sublimits can reopen that bounded question through its own versioned terms.
2. **Driftwood first; the demonstration advances per adopter.** Driftwood remains the first thin slice built by ticket 36. NORTH-STAR section 4 is the assistant's incremental build order, as ticket 75 Answer 2 records; step 4 describes one adopter's reconciled cage and residual. It has no all-three-insurance-before-any-step-4 prerequisite. All three historical quote 1 feeds already exist in the insurer's signed `v1.0.0` carrier, annotated object `d45005c2f4d6ec5832c33f43161f401d5501c885` targeting `632db22c92003b048795cea1f5d5bf6e08dcf386`. That publication does not assert three current subscriptions, valid fulfilled cover or real transfer. Insurer PR18's later merged Ludlow proposal is not a new signed quote release or an adoption.
3. **Keep the declared publishing/insurer role; add no own risk book.** The actual insurer party declares `roles: [publisher, insurer]`, not `risk-bearer`. Those roles remain unchanged. The illustrative quote publisher needs no fabricated own size, appetite or priced portfolio to perform this role. A future genuine role/input declaration may open self-pricing; no such declaration or institution signature is inferred here.
4. **One retained economic book, with distinct typed reasons.** A priced source/control hole and a contractual quote exclusion remain different explanations within one book. Existing source-hole evidence and quote exclusions retain their types and perspectives; they are not two calculated losses to add for the same underlying exposure. This chooses the existing structured representation, with no invented allocation, retained-loss value or new dedicated human bucket columns. An unknown aggregate stays unknown.

## Evidence and limits — 2026-10-21

The existing insurer party and quote checks are registered in `talk/verify-manifest.txt` and discovered by `talk/verify-all.sh`. Authentic recorded TRUTH 438 gives `.estate-clone/insurer/verify-insurer-party.sh` PASS and `.estate-clone/insurer/verify-insurer-quote.sh` **SKIP: 5 of 19 checks could not be looked at**. The quote capture retains all three stale quoted exposure bases and Driftwood/Ludlow's absent current priced totals. This decision record claims that wiring and those actual outcomes, not a new all-green result.

The published modeled-condition contract preserves met, breached and unobserved technical states, exact quote/exposure/source binding, and signed re-quote/adoption timing. Missing or incomplete evidence remains unknown; a counted claim grants no fulfillment or transfer credit. Booked premium does not change merely because a technical observation or modeled conditional view exists. No legal payability, actual cover, transferred-loss amount, current basis match or new financial input is supplied here.

The earlier helper README's “ticket37 remains open” describes what counted-claim evidence alone did not implement. The later technical contract likewise says native proof alone cannot close this ticket. The four decisions above now supply the missing decision record; none waives the remaining evidence or financial limits. Existing distribution/formula-2 work is not silently activated.

**Separate follow-up, 2026-10-21 — disclosure remains MISSING.** Ticket 75 Answer 4 requires the illustrative-counterparty statement on the quote itself. The three historical signed-v1 and current quote JSONs lack that statement; the party/README demonstration qualifier is outside the quote. [Task 162](162-the-insurer-quote-states-its-illustrative-scope.md) owns the concrete emitter/schema/publication/adoption repair. It is claimed, not delivered. This later disclosure defect is recorded explicitly rather than described as already shipped or added as a new question in original ticket 37.
