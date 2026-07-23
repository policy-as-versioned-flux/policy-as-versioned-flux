# Risk → proportionality model (appetite in £ → control strength → residual)

Type: grilling
Status: resolved
Blocked by: 01, 07

## Question

Define the model that makes every control a *proportionate, informed* response to quantified risk
— the philosophical core, made concrete and computable. Pin:

- **How risk appetite is expressed** — grounded in the org brief (01) and a quantification method
  (FAIR or similar, research 07): threat × impact × likelihood → an expected-loss £ per risk, and
  an appetite band the business accepts.
- **How risk *sets* control strength** — the mapping from a risk's magnitude to the control's
  proportionate form: Audit vs Deny, the CVE tolerance threshold, the sunset pace. Make Audit→Deny
  a *proportionality escalation* someone can justify with a number, not "best practice".
- **How residual risk computes** — controls-enforced coverage against the register, minus accepted
  exemptions (05), yields residual £. The maths must be real and demo-able, not a hand-wave.
- **Where it lives** — is the risk register + appetite itself a versioned artifact (so "the
  regulator raised fines" or "Log4Shell dropped" = a version bump that re-tunes the estate)? How
  does a change to it flow down through the same Flux distribution?

Output: the risk→proportionality→residual model + data shapes, feeding exemptions (05) and
balance-sheet (06).

> **Folded in 2026-07-23 — traditional insurance/actuarial practice** (see `../the-whole-model.md`
> + the map's Settled framing): proportionality = the four risk-financing moves **avoid · reduce ·
> transfer(insure) · retain** — *insurance is a control option*. Use **TVaR** (not just VaR₉₅) + a
> **risk load** on the £; calibrate with **credibility theory (Bühlmann)**; frame the balance-sheet
> number as **economic/risk-based capital** (Solvency II). Validations: warranties ↔ conditional
> policy, cat-modelling ↔ war-gamer, IBNR reserving ↔ the provision, correlation ↔ systemic risk.

## Answer

Model decided — full picture in [`../the-whole-model.md`](../the-whole-model.md) + the map's Settled
framing. In short: FAIR (frequency×severity) → **ALE + VaR₉₅ + TVaR** with a **risk load** on the £;
proportionality = the **four risk-financing moves** (avoid · reduce · transfer/insure · retain);
five versioned **feed threads** (threat register · CVE · EOL · penalties · market-intel/Wardley);
calibration via **credibility theory (Bühlmann)**; the £ framed as **economic/risk-based capital**.

**Appetite framing locked (2026-07-23):** `caldera` **strictest** (Deny-heavy — HIPAA + decades-
confidential records → HNDL/PQ real); `driftwood` **loosest** (Audit-heavy — short-life cart data,
HNDL≈0); `tuppence` **between, toward strict** (FCA/PCI fines, but an availability/fraud/op-resilience
flavour). **Money-shot:** the *same* control (encrypt-at-rest / no-EOL-log4j) is **Audit in
`driftwood`, Deny in `caldera`** — same rule, opposite verdict, because the £ says so.

Exact £, appetite bands, and the per-institution threat registers **derive** from FAIR + the feeds +
the org briefs during the build; the *relative shape* is locked. Formalisation (formulas, data
schemas) is build-work, not a remaining decision.
