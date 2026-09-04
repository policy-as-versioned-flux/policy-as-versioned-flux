# 44 — Eco-system misuse catalogue graded by the gate

Type: task (AFK)
Status: resolved
Blocked by: 19

## Question

Add `twin/ecosystem-misuse-catalogue.yaml` (schema `twin.misuse-catalogue/v1`) with the four rows and the mechanism strings from ticket 19, a harness check that loads all three catalogues and refuses a row without a mechanism, and `verify/verify-misuse.sh` so `verify-all.sh` grades it.

## Notes

Graduated 2026-08-28 from ticket 19's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Resolved 2026-09-03 (wave 1 of the everything-open build). Hub only; no unit was touched.

1. **The third catalogue.** `twin/ecosystem-misuse-catalogue.yaml`, `twin.misuse-catalogue/v1`, version 1, four rows with ticket 19's ids and its draft mechanism strings expanded to what each decision actually names: `publisher-games-own-feed-price` (widen to the publisher-shipped `widen_to` on a publisher-reliability score below appetite; ticket 18's degraded tier as a priced hole; the switching cost as the £ reason to switch), `regulator-data-mispriced-downstream` (`lm_triple`'s hi = max(cap, 1.2 × largest example, mode) and rate × turnover; a pin behind a newer version priced by the EOL ramp per D5; score disclosed in prices[]; un-pinning the sole price refuses per ADR-0020), `adopter-buys-intel-on-rival` (no purchase exists; a rival's reading is its own perspective's price under `twin/pricing.py`'s rule; the adopter prices the read as the standing scenario `rival-reads-my-holes-2026`), `twin-valuation-used-in-negotiation` (the twin values only under its own perspective; the number is the org's own, signed by role; `_sum_prices`/`fair.sum_prices` refuse a list that crosses perspectives, ADR-0021; no recommended-action field). It lives in the hub because a regulator mispricing an adopter is in nobody's `party.yaml` (ticket 19 default, kept).
2. **The loader.** `twin/misuse.py` gains `ECOSYSTEM_CATALOGUE_PATH`, `ALL_CATALOGUE_PATHS`, `ECOSYSTEM_ROW_IDS` and `load_all_catalogues()`, which runs the one `load_catalogue()` over the three files and adds the one rule a per-file loader cannot see: an id belongs to exactly one scope. No second loader.
3. **The harness check.** `misuse_catalogues_load_and_every_row_names_a_mechanism` in `twin/invariants/harness.py`, beside the three misuse checks: three distinct files load through the one loader, no id in two catalogues, ticket 19's four ids present, every eco-system row carries a path anchor or the ticket building its price, and a copy with one mechanism blanked is refused with the loader's own "no mechanism" reason (the refusal proven, not assumed). `twin verify --only misuse_catalogues_load_and_every_row_names_a_mechanism` reports it as check 11; every later check's plan number moves up by one (names unchanged; nothing in `verify/`, `talk/` or `.github/` calls `--only` by number).
4. **The check in the gate.** `verify/misuse/verify-misuse.sh`, discovered by `talk/verify-all.sh`'s glob (`find .estate-clone verify -name 'verify*.sh'` lists it tenth). Three legs, all offline: its own instrument on eight planted rows (a blanked mechanism refused, a missing anchor, a missing token, a resolved waited-on ticket, an unknown ticket and a bare row each FAIL; an open waited-on ticket is could-not-look by name; a resolving row passes), plus the script's own exit contract run end to end in a scratch hub whose `bin/twin` reports the check FAIL and which has no `.estate-clone`: the run must end FAIL with an exit that is neither 0 nor 3; the harness check exactly as `twin verify` reports it; and the four real rows graded against this checkout. `selfcheck` runs the first leg alone. First run: PASS, 2 of 4 rows resolve by path, 2 could-not-look by name.
5. **Grading a row.** Each eco-system row carries `anchors:` (paths, optionally `::token`, that must exist and contain the token; a path whose first segment is a unit name is `.estate-clone`-relative, any other is hub-relative and graded against the hub alone) and, where its cage price is decided but not built, `waits_on: [{ticket, for}]`. `misuse.grade_entry()` grades anchors first (a claimed, absent path fails whatever the row waits on), then the waits: could-not-look while the ticket is open, FAIL once it is resolved and the row still says it waits, FAIL if the ticket does not exist. A FAIL always wins over could-not-look: an estate anchor nobody can look at does not shield a resolved or unknown waited-on ticket. The escape hatch closes itself. Today `publisher-games-own-feed-price` waits on 45 (the switching price) and 46 (the reliability feed and scorer party); `regulator-data-mispriced-downstream` waits on 84 (D5 applied to a pricing pin) and 46 (the score on the prices[] entry). Both name their anchors that do exist (`PRICE_KINDS` reserving `switching` and `reliability`, `gate.py`'s degraded prerelease, `lm_triple`, `eol_ramp`, ADR-0020).
6. **Tests.** `tests/test_misuse.py`: 41 pass (20 new: the third catalogue loads, the four ids, three scopes do not conflate, a duplicate id across catalogues is refused, every row anchors or waits, the ten grading cases, the ticket-status reader, the real rows against this checkout, and the harness check itself). `mypy` clean on `twin/misuse.py` and `twin/invariants/harness.py`.
7. **Review fixes, 2026-09-04.** The 2026-09-03 review found leg 3's substrate `skip` masking a leg-2 FAIL as SKIP (exit 3) on a checkout with no clone; `skip` now consults `$fail` and reports FAIL (exit 1) once anything was observed false, and leg 1 proves it end to end (item 4). Hub-relative anchors are now graded against the hub alone, so a typo in a `twin/` or `docs/` anchor fails in CI too (item 5); a FAIL from `waits_on` wins over a could-not-look anchor. Three prose-word tokens became identifiers (`DEGRADED_TIER`, `NO_VALUATION`, ADR-0021's "Every price carries `perspective`"); catalogue version 2.

**For the integrator.** Ticket 45 is being built in this wave and row 1 waits on it; rows 1 and 2 also wait on 46 and 84. By design, the integration step that merges 45, 46 or 84 with `Status: resolved` must re-anchor the waiting row by path in the same step, or `verify/misuse/verify-misuse.sh` goes red in the gate ("still says it waits on ticket 45 (resolved)"). That red is the check working, not a defect; the fix is one row edit and a version bump.

Decisions, each delegated (ADR-0025):

- **Script location** `verify/misuse/verify-misuse.sh`, not the ticket's flat `verify/verify-misuse.sh`. Every hub script sits one level down and the glob finds either; the ticket's spelling was a name for the check, not a path decision. Delegated.
- **A mechanism may name a decision plus the nearest existing code, and must say what it waits on.** Ticket 19 wrote its mechanism strings before ticket 45, 46 or 84 built anything; rows 1 and 2 cite widening and disclosure that do not exist in `composition.py`. Refusing those rows would have emptied half the catalogue; letting prose stand in for code would have made "names a mechanism" mean "names a sentence". So the row keeps the decided mechanism in prose, anchors the parts that exist by path and token, and names the open ticket for the rest by number. The gate grades that row could-not-look by name (the wave lead's instruction for ticket 45, applied the same way to 46 and 84) and fails it the day the ticket resolves. Delegated.
- **The two twin-scoped catalogues are graded for mechanism presence only.** Their mechanisms name invariants `twin verify` already runs and modules the tests already import; a path grammar on them would be a second thing to maintain with nothing new to catch. The eco-system rows are anchored because their mechanisms are estate code the twin never imports. Delegated.
- **The verify script runs the single harness check, not the whole suite.** `verify/twin-evals/verify-twin-evals.sh` already runs the suite's evals; a focused `--only` keeps this capture readable and its FAIL attributable. Delegated.
- **All-could-not-look is a FAIL of the script, not a SKIP.** Inside the grader, a catalogue where no row can be looked at exits 3 (that is what the planted fixture proves); at the script level the real catalogue has two rows whose anchors resolve today, so a run where none resolve means something is broken, and the script says so rather than reading as "could not look". Delegated.
- **Version 1, and the file header distinguishes the three scopes** in the same words `behavioural-misuse-catalogue.yaml` uses for two; the conflation test now covers three files and checks that no twin-scoped id names a publisher, regulator, rival or negotiation. Delegated. (Version 2 since the 2026-09-04 review fixes: three anchor tokens changed.)
- **A FAIL always wins over a SKIP, in the script and in the grader.** Exit 3 means "nothing could be looked at" and is only honest when nothing was observed false; the moment a leg has seen a FAIL, a later leg's could-not-look is reported as FAIL with both reasons. Fixed in `skip()` rather than by reordering the legs, so no future leg can reintroduce it, and planted in leg 1 so the gate keeps proving it. Delegated.
- **An anchor's first path segment decides where it is looked for.** A unit name (`ESTATE_UNITS`: platform, ico, nist, driftwood, tuppence, ludlow, feeds, insurer) means `.estate-clone`; anything else means the hub, and a missing hub file FAILs on every checkout. The alternative, a hub-first fallback to the estate, let a typo in a hub anchor read as could-not-look wherever the clone was not assembled. Delegated.
- **Tokens are identifiers, not prose words.** A `::token` that is an ordinary word in a comment survives the mechanism being removed; a def, a constant or an id does not. Delegated.

Facts found while building, for their owners: tuppence and ludlow carry no `rival-reads-my-holes` scenario file (ticket 11 item 4 says each adopter carries six standing scenarios; only driftwood does), so row 3 anchors driftwood's; `widen_to` is shipped by no publisher yet (ticket 24 item 3); `tests/test_invariant_suite.py::test_the_suite_is_green` stays red on the one standing red, `flux_coverage_floor_is_still_reachable` (the unreachable drift floor, recorded 2026-08-16), which the plan numbered 44 on main and numbers 45 here because this check sits at 11.

Map line: 44 — third misuse catalogue (four eco-system rows, ticket 19's mechanisms, anchored by path or by the open ticket building the price) loaded by the one loader, harness check `misuse_catalogues_load_and_every_row_names_a_mechanism`, `verify/misuse/verify-misuse.sh` in the gate: PASS, 2 rows resolve, 2 could-not-look by name (45/46, 84/46); the affected-parties re-cut (open item above) can start.

## Waits on the owner

Nothing. Merging the hub PR is the integrator's, as `pavc-other-hand`.

## Comments

**2026-09-04, merge attribution (the assistant, recorded as an incident).** Hub PR #11 was merged
at 2026-09-04T00:09:26Z under the owner's login, not as `pavc-other-hand[bot]`. Cause: the merge
command minted the app token with a relative `.venv/bin/python` path while the shell's working
directory was `.estate-clone/`, the mint failed, `GH_TOKEN` was empty, and `gh` fell back to the
owner's keyring token. The guard admitted the command because its text had the other-hand shape.
The review itself was done (two lenses, one fix round, re-review approved as the app). Nothing can
re-attribute a merge; this note is the record. From this merge on, the mint uses the absolute
interpreter path from the hub root. Ticket 65's parser is not at fault: the shape was right, the
path was not.
