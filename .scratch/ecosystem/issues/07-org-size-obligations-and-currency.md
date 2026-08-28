# 07 — Org size obligations and currency

Type: grilling (HITL)
Status: resolved
Blocked by: none

## Question

What each party artefact declares so the £ is proportionate to the org: annual turnover, customer count, regulated-data-subject count, headcount; an `obligations:` list (driftwood: uk-gdpr + pci-dss; tuppence: uk-gdpr + pci-dss + fca; ludlow: hipaa + uk-gdpr); how `pct_of_global_turnover` with `rate` and `cap_gbp` is applied per org; a currency on every amount with a signed FX feed before any sum; who signs the size facts and how often they refresh.

## Notes

Findings H3-02, H3-15, H9-06, H9-07. GAPS 1.10.

## Answer

Resolved 2026-08-28. Facts found first: no `party.yaml` declares size; the party schema is `additionalProperties: false`; `ico/schema/to_fair_scenario.py` ignores `rate` and turnover and builds the triple from the real examples and the cap, which is why all three orgs price ICO at £16,901,471.55; currency lives on the regime only and HIPAA is USD; `fair.py` sums triples with no conversion.

1. **Size facts.** The adopter's signed party artefact gains `size: {turnover: {amount, currency}, customers, data_subjects, headcount, as_of}`. The adopter signs it under its own gitsign tag; there is no second signer. `pct_of_global_turnover` becomes `hi = min(rate × turnover, cap)`; the real examples keep their shape and scale by `hi / cap`. An `as_of` older than 12 months does not refuse: the triple widens back to the cap. Stale size is a priced consequence, not a count. Owner agreed without a reason; recorded as such.
2. **Obligations.** `obligations:` is a list of regime names on the party artefact (driftwood: uk-gdpr, pci-dss; tuppence: uk-gdpr, pci-dss, fca; ludlow: hipaa, uk-gdpr). The converter reads the list from the signed artefact and drops `--also`. An obligation whose regime no subscribed pricing feed carries is an instrument fault: the composition refuses. "Never refuse" governs behaviour; a missing instrument is the gate failing to read, not a behaviour. Owner agreed without a reason; recorded as such.
3. **Currency.** Every amount is `{amount, currency}`. Each party declares a `reporting_currency`. The default is **USD** (owner: "USD is probably the default but we'll mostly use GBP"); the three adopters declare GBP explicitly. The FX rate is a signed feed, `kind: feed`, `name: fx`, from the feeds org, dated. A sum with no rate for the date is an instrument fault and refuses. No new mechanism beyond ADR-0019.

Graduated: ticket 24 (size beyond turnover). ADR-0020 records the refuse-versus-price line. CONTEXT.md gains Size facts, Obligation, Reporting currency, Instrument fault.
