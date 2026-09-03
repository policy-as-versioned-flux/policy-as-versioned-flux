# verify/priced-holes — a hole is priced, not counted (eco-system ticket 38)

`verify-priced-holes.sh` grades, on committed files only, that `platform/compose/composition.py`
no longer refuses on a new hole, a widened baseline or a new ungoverned namespace, and that each
adopter's `composed/evidence.json` carries what replaced those refusals:

- `deltas[]` — one entry per new/closed hole, per baseline widening, per new/closed ungoverned
  namespace, each under the adopter's own perspective and currency, priced where a pinned
  instrument names a price and a named absence (`amount: null`) where none does;
- `holes[]` keyed `(source, control_id)` across every controls parent, with `perspective`,
  `currency`, `amount` and `priced_by`;
- a `price` on every open `ungoverned[]` entry: workload share (re-counted from the adopter's own
  manifests), the EOL feed's ramp from `since` (re-derived), `min(base, base × share × ramp)` with
  `base` the header's signed exposure total, and `since` the date of the first *signed* tag whose
  header names the namespace (re-read from the adopter clone's tags) or null with a limit;
- the regime entry's weighted `holes[]` each carrying the adopter's status;
- the party schema admitting `overlay.controls` as bare ids and `party:id`.

Exit codes follow the gate contract: 0 true, 3 could not look (`SKIP:` — no estate, no evidence,
evidence composed under the refusal shape, a clone with no signed tag), 1 false (`FAIL:`).
`priced_holes.py selfcheck` plants each defect and proves the check bites; the hub's
`tests/test_priced_holes.py` covers the pure arithmetic and since-preservation.

The three adopters' evidence is re-composed and pushed by the owner (enactment pushes); until
then this check reads `SKIP` for each adopter and `PASS`/`FAIL` for the platform source and schema.
