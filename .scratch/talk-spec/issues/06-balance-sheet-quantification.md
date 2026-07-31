# Balance-sheet quantification (residual → £ → insurance/valuation), built real

Type: grilling
Status: resolved
Blocked by: 04, 07, 09

## Question

Build — for real, comprehensively, no hand-waving — the chain that turns enforced controls and
priced exemptions into a **technological-risk number the business could put on its balance sheet**.
The human's instruction: go deep, prove it, *then* decide whether to cut it from the talk. Pin:

- **The number** — how residual risk (04) becomes a defensible £ figure: expected annual loss, or a
  distribution (VaR-style), grounded in the org brief (01) and FAIR (07). What exactly is "on the
  balance sheet" — a provision, a disclosed contingent liability, an insurance-premium input?
- **The up-flow that feeds it** — how OSCAL evidence + the exemptions ledger produce the inputs;
  whether OSCAL's own risk/POA&M objects (research 09) carry accepted-risk natively.
- **The three consumers** — frame each concretely: (a) **insurance** — how an underwriter would
  price a premium off this; (b) **valuation/diligence** — how an acquirer reads it; (c) **board** —
  a line, not a RAG. Which of these we actually demonstrate live.
- **Provable, not asserted** — the number must move when you'd expect: grant an exemption → it
  rises; tighten a control (version bump) → it falls; a new threat lands → it jumps. Demo that loop.

Output: the quantification method + a real, moving £ readout + the three framings — built even if
later cut from the deck.

> **Folded in 2026-07-23 — traditional insurance/actuarial practice** (see `../the-whole-model.md`
> + the map's Settled framing): proportionality = the four risk-financing moves **avoid · reduce ·
> transfer(insure) · retain** — *insurance is a control option*. Use **TVaR** (not just VaR₉₅) + a
> **risk load** on the £; calibrate with **credibility theory (Bühlmann)**; frame the balance-sheet
> number as **economic/risk-based capital** (Solvency II). Validations: warranties ↔ conditional
> policy, cat-modelling ↔ war-gamer, IBNR reserving ↔ the provision, correlation ↔ systemic risk.

## Answer

- **It's the narrated close, not a live beat** (spine decision). **Narration angle (2026-07-23):**
  **lead with insurance** (the external validator — underwriters price the *same* controls,
  ±20–40% premium; proves the model isn't invented, it's the industry's own maths), **land on the
  board** ("technological risk becomes a *line your board can read, defend, and act on*" — the
  leader takeaway); **valuation/diligence** = one line, not a section.
- **Still built real** (per the ticket): residual £ → **economic/risk-based capital** (Solvency-II
  framing), TVaR + risk-load, reserving/provisioning line. The **provable loop** is demonstrated
  even though the framing is narrated: accept a condition → £ rises; tighten a control → £ falls; a
  new threat/EOL lands → £ jumps.
- Method + the moving-£ readout are build-work; the *angle* is the decision, and it's locked.

## Update (2026-07-23) — the number is Total Cost of Risk, not just residual

Grilling ticket 16 (enforcement response gradient) upgrades what the balance-sheet number *is*:

> **TCoR = retained residual (ALE/TVaR) + cost of controls in force + risk transfer (premiums)**

The graded-enforcement **cages** are the *cost-of-controls* term, and they make it **dynamic**: a
workload/fleet drifting out of posture doesn't only raise the residual line — it raises the
control-spend line as cages kick in (a cage is a *priced partial-reduce on a retained risk*: residual
drops to R′>0 **and** costs C_cage/yr to run; **both** book to the sheet). "Compliant = cheap" becomes
a **computed** crossover (`C_cage + R′` forever vs `C_fix` once → baseline), and it's the fork the
war-gamer evaluates: **fix vs cage vs transfer vs deny**, chosen by TCoR. See [ticket 16](16-enforcement-response-gradient.md).
