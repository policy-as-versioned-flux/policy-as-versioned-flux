# War-gaming & AI policy-PR agent (the loop-closer)

Type: prototype
Status: resolved
Blocked by: 04, 14

## Question

Design the agent that keeps proportionality current — your `governance-agent` (ADR-0007, today
CVE→issue) evolved into a war-gaming policy-PR proposer. Pin:

- **Collect** the feed threads (threat-landscape, CVE, EOL, regulator penalties, market-intel via
  AI-Wardley — 14).
- **War-game** scenarios against the *current* controls (the ransomware/PQ/attack-cost-collapse
  class we traced by hand): does proportionality still hold, or has risk crossed tolerance / a
  control gone over-priced?
- **Propose, never dispose** — output is a **pull request** on the policy with re-tuned controls,
  which hits the same wall as any change: human review + the PR-gate version cross-check + gitsign +
  versioned distribution. The scary capability is safe *because* it rides the existing rails.
- **Attestable provenance** — every commit/PR the agent (and every actor) makes carries its **own
  attestable identity** (gitsign keyless → Rekor), so the chain feed → scenario → proposed PR →
  review → merge → signed release is verifiable end to end: *which* actor (AI or human) proposed
  *what*, *when*, *from which evidence*. For an AI-enabled org this is how you trust the machine.
- **Scenario library** — how are war-game scenarios authored/generated (AI-generated + human seed),
  and how do results feed back as evidence.

Output: the agent design + the signed-PR provenance model + a rough war-game→PR prototype.

> **Folded in 2026-07-23 — traditional insurance/actuarial practice** (see `../the-whole-model.md`
> + the map's Settled framing): proportionality = the four risk-financing moves **avoid · reduce ·
> transfer(insure) · retain** — *insurance is a control option*. Use **TVaR** (not just VaR₉₅) + a
> **risk load** on the £; calibrate with **credibility theory (Bühlmann)**; frame the balance-sheet
> number as **economic/risk-based capital** (Solvency II). Validations: warranties ↔ conditional
> policy, cat-modelling ↔ war-gamer, IBNR reserving ↔ the provision, correlation ↔ systemic risk.

## Answer

Settled at the decision level (ticket body + the model + the by-hand ransomware/PQ scenario). The
`governance-agent` evolves into a **war-gaming policy-PR proposer**: collect the five feeds →
war-game scenarios against current controls → on proportionality drift (risk over tolerance, or a
control gone over-priced) **open a policy PR** with re-tuned controls. **Proposes, never disposes** —
the PR rides the existing rails (human review + PR-gate version cross-check + gitsign → Rekor +
versioned distribution). Every actor/action carries its **own attestable identity** so
feed→scenario→PR→review→merge→signed-release is verifiable end to end. Scenarios: AI-generated +
human seed, results logged back as evidence (calibration). Agent code + scenario library are build.
