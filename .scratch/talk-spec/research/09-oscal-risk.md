# Research: does OSCAL natively carry the RISK half? (accepted / residual / priced)

Ticket: `../issues/09-research-oscal-risk.md`. Feeds exemptions-ledger (05) and balance-sheet (06).

**Bottom line:** OSCAL carries the risk half natively — the `risk` assembly (accepted risk,
deviation, owner, deadline, status, remediation-with-acceptance, evidence link) is a first-class
OSCAL object, and a real NIST example ships an accepted risk verbatim. The **one** thing it does not
carry natively is a *numeric £ magnitude*: OSCAL risk "magnitude" is a qualitative
likelihood/impact/severity facet by design, and a monetary figure is attached the same idiomatic way
CVSS scores are — a `facet` (or `prop`) under a custom `system` URI. That is the honest, standard
extension path, not a hack. What our current C2P output is missing is not schema support — it is that
`result2oscal` emits findings/observations only and stops short of ever instantiating a `risk`.

---

## 1. Where risk lives in the OSCAL model

OSCAL is three layers ([NIST layers/models](https://pages.nist.gov/OSCAL/documentation/schema/)):

- **Control layer** — `catalog`, `profile` (the NIST 800-53r5 catalog we already `source`).
- **Implementation layer** — `component-definition` (what we hand-author in `c2p/`), `ssp`.
- **Assessment layer** — `assessment-plan`, **`assessment-results`**, **`plan-of-action-and-milestones` (POA&M)**.

Risk is an **assessment-layer** concept. Two facts matter for us:

1. The **`risk` assembly is shared** between `assessment-results` and `poam-item`/POA&M. NIST states
   the POA&M model was *"designed to use identical syntax to the assessment results model, for
   overlapping assemblies (results: observations and risks), which allows easy transfer of identified
   risks from an assessment report to a POA&M"*
   ([POA&M concept](https://pages.nist.gov/OSCAL/learn/concepts/layer/assessment/poam/)). So the same
   risk object can be emitted alongside our C2P results **or** carried in a standalone POA&M — no
   translation.
2. *"Risk deviations, such as false positive identification, risk adjustments and risk acceptance
   (operational requirement) are also identified as part of the risk itself"* (ibid). **Acceptance is
   a property of the risk, not a bolt-on.**

## 2. The `risk` assembly — full field list (verified against a real NIST example)

From NIST's own POA&M example
([`usnistgov/oscal-content` → `examples/poam/json/ifa_plan-of-action-and-milestones.json`](https://github.com/usnistgov/oscal-content/blob/main/examples/poam/json/ifa_plan-of-action-and-milestones.json)),
a `risk` object carries exactly these fields (confirmed present in the file):

| Field | Type | Carries |
|---|---|---|
| `uuid` | uuid | stable id, referenced by `poam-item.related-risks[].risk-uuid` |
| `title` / `description` / `statement` | markup | what the risk is, and its impact narrative |
| `status` | token | lifecycle — the example uses **`deviation-approved`** and **`open`** |
| `origins[].actors[]` | ref | **owner** — `type:"party"` + `actor-uuid` → a `party` in metadata |
| `threat-ids[]` | ref | optional threat catalogue linkage |
| `characterizations[].facets[]` | name/system/value | **the "magnitude"** — likelihood/impact/severity/risk |
| `mitigating-factors[]` | markup | compensating controls |
| `deadline` | **dateTime** | native remediate-by date (example: `2024-01-01T05:00:00-04:00`) |
| `remediations[]` (a.k.a. response) | lifecycle+tasks | plan, incl. **acceptance** (see §3) |
| `risk-log[].entries[]` | start/end/logged-by/status-change | audit trail of status changes over time |
| `related-observations[].observation-uuid` | ref | **evidence link** back to the failing check |

`status` is an open token, not a closed enum — NIST's example uses `deviation-approved`; FedRAMP
layers its own vocabulary on top via props (§4). `deadline` being a native dateTime and `origins`
giving an owner-party means **owner + deadline + status are all first-class, no props needed.**

## 3. Accepted risk is native — the priced-exemption shape

The NIST example *is* an accepted risk. Trimmed to the load-bearing parts:

```json
{
  "uuid": "8b8bae66-b28c-4fa5-9a20-b79e7322fc00",
  "title": "PAO staff have over-privileged access to SYSTEM1234",
  "statement": "An account without least-privilege ... significant financial and reputational risk.",
  "status": "deviation-approved",
  "characterizations": [
    { "origin": { "actors": [ { "type": "party", "actor-uuid": "e7730080-..." } ] },
      "facets": [
        { "name": "likelihood", "system": "https://ifa.gov/division/ociso/sca", "value": "low" },
        { "name": "impact",     "system": "https://ifa.gov/division/ociso/sca", "value": "high" }
      ] } ],
  "deadline": "2024-01-01T05:00:00-04:00",
  "remediations": [
    { "uuid": "d28873f7-...", "lifecycle": "planned",
      "title": "Product-team response",
      "description": "... the owner of the SYSTEM1234 system has decided to accept this risk until end of December 2023 ...",
      "props": [ { "name": "type", "value": "accept" } ],
      "tasks": [ { "type": "milestone", "title": "EOY remediation report",
        "timing": { "within-date-range": { "start": "2023-09-29T09:00:00-04:00", "end": "2024-01-01T05:00:00-04:00" } } } ] } ],
  "related-observations": [ { "observation-uuid": "0c4de4fc-9bde-46af-b6fe-3b5e78194dcf" } ]
}
```

Note `remediations[].props[] name:"type" value:"accept"` — **"accept" is the recognised remediation
type** for a consciously-accepted risk (vs. `mitigate`/`transfer`/`avoid`). Combined with
`status:"deviation-approved"` and the `related-observations` pointer back to the evidence, this single
object already expresses *"control not satisfied here (observation X), risk consciously accepted,
owned by party Y, review by deadline Z."* That is the whole exemptions-ledger row (05), minus the £.

## 4. Owner / deadline / status — and the FedRAMP deviation vocabulary

FedRAMP's OSCAL profile shows the production idiom for the *type* of acceptance. Rather than a bespoke
status, you keep `status:"open"` and add a prop naming the deviation
([FedRAMP SAR→OSCAL mapping](https://automate.fedramp.gov/documentation/sar/4-sar-template-to-oscal-mapping/)):

- **Operational requirement** (accepted-because-needed): `prop name:"operational-requirement"
  ns:"http://fedramp.gov/ns/oscal" value:"pending"`, status stays `open`.
- **Risk adjustment** / **false positive**: analogous props (`risk-adjustment`, `false-positive`).

Two idioms, both native: NIST's example bakes acceptance into `status`+remediation `type:accept`;
FedRAMP encodes the *reason* as a prop and leaves status `open`. Either maps our exemption cleanly —
for the talk, the NIST `deviation-approved` + `type:accept` shape is the clearer story.

## 5. The magnitude / £ question — the one genuinely non-native bit

**OSCAL has no numeric risk field and no money type.** "Magnitude" in OSCAL = a `characterization`
containing `facet`s, each `{name, system, value}`
([assessment-results definitions](https://pages.nist.gov/OSCAL-Reference/models/v1.1.2/assessment-results/json-definitions/)):

- `name` ∈ recommended `likelihood | impact | severity | risk` (extensible).
- `system` = a URI naming the scoring scheme — NIST recommends its own ns, and supports CVSS v2/v3
  systems; **the example above uses a fully custom `https://ifa.gov/...` system URI.**
- `value` = a **string/token** — there is no numeric datatype on `value`. CVSS base scores (e.g.
  `"9.8"`) ride in a facet `value` as a string too. So a qualitative `low`/`high` and a numeric score
  are represented identically: string value under a declared system.

Therefore a **£ figure is attached exactly the way CVSS is** — as a facet under your own `system`:

```json
"characterizations": [
  { "facets": [
    { "name": "likelihood", "system": "https://pavf.dev/ns/risk", "value": "likely" },
    { "name": "impact",     "system": "https://pavf.dev/ns/risk", "value": "high" },
    { "name": "annualised-loss-expectancy",
      "system": "https://pavf.dev/ns/risk/gbp", "value": "12000",
      "props": [ { "name": "currency", "value": "GBP" }, { "name": "basis", "value": "priced-deviation" } ] }
  ] } ]
```

`facet` is the *semantically correct* home (it is literally defined as "a risk metric within the
specified system"), and declaring your own `system` URI is the mechanism NIST intends for extension —
the same one FedRAMP and CVSS use, and the pattern in NIST's
[props/links extension tutorial](https://pages.nist.gov/OSCAL/learn/tutorials/general/extension/).
A top-level `prop` on the risk would also validate, but a `facet` is the honest choice because £ is a
risk *metric*, not arbitrary metadata. **This is standard OSCAL, not a fork.** The only caveat: the
number is a string the schema won't range-check, so any arithmetic/validation lives in our tooling —
same as everyone doing quantitative risk in OSCAL today.

## 6. The up-flow, and where our current output stops short

Intended chain: **policy result → observation (evidence) → finding (control satisfied?) → risk
(residual/accepted) → poam-item (tracking)**, stitched by uuid refs (`related-observations`,
`related-risks`).

What we emit **today** via C2P `result2oscal` (per ADR-0009 + `c2p/component-definition.json`): an
`assessment-results` doc with **observations** (PolicyReport evidence) and **findings** mapping each
NIST control to satisfied / not-satisfied. **It never instantiates a `risk`.** C2P's job is
control-satisfaction, so the up-flow stops at *"cp-10 not-satisfied on this RDS instance."* The
residual/accepted/priced half is simply absent — not blocked by schema, just not produced.

To close it, the exemptions ledger (05) becomes a generator of **`risk` objects** (§3 shape) whose
`related-observations[].observation-uuid` points at the exact C2P observation for the failing check.
Two placements, both valid:

- **Enrich the assessment-results** with a `risks` array beside the existing `findings` (same doc), or
- **A standalone POA&M** that `import-ssp`s / references the C2P results and carries the risks +
  `poam-items`. Because the `risk` syntax is identical (§1), the ledger emits one object usable either
  way.

`poam-item` itself is thin — `{uuid, title, description, related-observations, related-risks}` (verified
in the example) — a tracking wrapper that points at the real evidence (observation) and the real risk.
So the balance-sheet (06) sums `facet.value` (the £ ALE) across `status:deviation-approved` risks; the
ledger (05) is the list of those risks with owner (`origins.actors`), deadline, and evidence link.

## 7. Answer to the ticket's four questions

1. **Accepted risk / deviation / risk log with owner+deadline+magnitude?** Yes, natively, except the
   magnitude is qualitative-by-design. `risk.status`, `origins.actors` (owner), `deadline` (dateTime),
   `remediations[type:accept]`, and `risk-log` are all first-class.
2. **Up-flow in OSCAL today?** observation → finding → (risk) → poam-item by uuid ref. Our C2P output
   stops at findings; it emits no `risk`.
3. **Exemption ↔ OSCAL?** Clean 1:1. Ledger row → one `risk` with `status:deviation-approved` +
   `remediation type:accept` + `related-observations` → the C2P not-satisfied observation. The
   evidence chain is native end-to-end.
4. **Numeric hooks / £?** No native numeric or money field. Attach £ as a `facet` (preferred) or
   `prop` under your own `system` URI — identical to how CVSS scores are carried. Honest and standard;
   validation/summation is our tooling's job.

## Sources

- [OSCAL layers & models](https://pages.nist.gov/OSCAL/documentation/schema/)
- [POA&M concept (risk = accepted/deviation; shared syntax with AR)](https://pages.nist.gov/OSCAL/learn/concepts/layer/assessment/poam/)
- [Assessment-results JSON definitions (characterization/facet name·system·value)](https://pages.nist.gov/OSCAL-Reference/models/v1.1.2/assessment-results/json-definitions/)
- [NIST POA&M example — real accepted risk](https://github.com/usnistgov/oscal-content/blob/main/examples/poam/json/ifa_plan-of-action-and-milestones.json)
- [FedRAMP SAR→OSCAL mapping (operational-requirement / risk-adjustment / false-positive deviation props)](https://automate.fedramp.gov/documentation/sar/4-sar-template-to-oscal-mapping/)
- [NIST extension tutorial (props/links / custom `system` URIs)](https://pages.nist.gov/OSCAL/learn/tutorials/general/extension/)
- Local: `docs/adr/0009-oscal-attestation-via-c2p.md`, `pavf-fleet/infrastructure/c2p/component-definition.json`
