# RESEARCH: OSCAL risk / POA&M / accepted-risk for the up-flow

Type: research
Status: resolved
Blocked by: —

## Question

The estate already emits OSCAL assessment-results (C2P). Does OSCAL natively carry the *risk* half
of the model, or must we bolt it on? Surface the facts the exemptions ledger (05) and balance-sheet
(06) wait on:

- **OSCAL model** — assessment-results, findings, observations, and especially **POA&M**
  (plan of action & milestones) and any **risk** objects: can OSCAL represent an *accepted risk* /
  a *deviation* / a *risk log* with an owner, deadline, and (crucially) a magnitude?
- **The up-flow** — how a policy result → control satisfaction → residual risk is expressed in
  OSCAL today, and where our current component-definition/assessment-results stop short.
- **Exemption ↔ OSCAL** — can a ledger exemption (05) map to an OSCAL risk/deviation object so the
  evidence chain natively shows "control not satisfied here, risk consciously accepted, priced"?
- **Quantification hooks** — does OSCAL carry any numeric risk fields, or do we attach the £ via
  props/links (and is that the honest way)?

Findings → write to `.scratch/talk-spec/research/09-oscal-risk.md`; link it back here.

## Answer

Full findings + JSON snippets: [`../research/09-oscal-risk.md`](../research/09-oscal-risk.md).

- **OSCAL carries the risk half natively.** `risk` is a first-class assessment-layer assembly, shared
  verbatim between `assessment-results` and `plan-of-action-and-milestones` (identical syntax → zero
  translation). Acceptance is a property *of the risk*, not a bolt-on.
- **Accepted risk is a real shipped shape.** NIST's own POA&M example carries a risk with
  `status:"deviation-approved"`, a remediation `props[] {name:"type", value:"accept"}`, and a
  `deadline` — i.e. a consciously-accepted, dated deviation, out of the box.
- **Owner + deadline + status are first-class fields**, no props needed: owner via
  `origins[].actors[]` (→ a metadata `party`), `deadline` is a native dateTime, `status` a token, plus
  a `risk-log` audit trail of status changes.
- **Exemption ↔ OSCAL is a clean 1:1.** A ledger (05) row → one `risk` with
  `status:deviation-approved` + remediation `type:accept` + `related-observations[].observation-uuid`
  pointing at the exact C2P not-satisfied observation. The chain *control-not-satisfied → evidence →
  risk-accepted → tracked* is native end-to-end (`poam-item` is a thin wrapper referencing the risk +
  observation).
- **"Magnitude" is qualitative by design.** OSCAL magnitude = `characterizations[].facets[]`
  `{name, system, value}`, names `likelihood|impact|severity|risk`. `value` is a **string** — CVSS
  scores ride here as strings too. There is **no native numeric or money datatype.**
- **The £ is attached the same idiomatic way CVSS is** — a `facet` (preferred; it's literally "a risk
  metric within a system") or a `prop`, under our own `system` URI e.g.
  `{name:"annualised-loss-expectancy", system:"https://pavf.dev/ns/risk/gbp", value:"12000"}`. Honest
  and standard (same extension mechanism FedRAMP/CVSS use), *not* a fork — but the number is an
  unchecked string, so summation/validation is our tooling's job (feeds 06).
- **Where our current output stops short:** C2P `result2oscal` emits only observations + findings
  (control satisfied/not-satisfied). It **never instantiates a `risk`.** The residual/accepted/priced
  half is absent by omission, not blocked by schema.
- **To close the up-flow:** make the exemptions ledger (05) a generator of `risk` objects (linked to
  C2P observations by uuid), placed either as a `risks` array inside the assessment-results or as a
  standalone POA&M — identical syntax makes it usable either way.
