# The subject & purpose — who is this for, and which organisation gets twinned?

Type: grilling
Status: RESOLVED (2026-08-04)
Blocked by: none

## Question

The keystone. Everything — the twin's data model, the £ currency, every scenario, the demo slice,
each workstream's acceptance criteria — hangs on this. Pin, one at a time:

- **Subject** — *which* organisation does the twin model? A **real** org (ControlPlane itself? a
  named client?), a **richly-modelled fictitious archetype** (and which sector — the old
  driftwood/tuppence/ludlow, or something real enough to threat-model?), or an **org-agnostic
  framework** instantiated per-org? Real risk modelling needs a subject with real (or realistically
  detailed) value chains, supply chain, data assets, people, and threat surface — cardboard won't do. *Strong hypothesis (2026-08-04): a **richly-modelled fictitious
  org** whose operational + behavioural substrate (email, chat, commits, HR events, supply-chain,
  telemetry) is **AI-synthesised with realistic noise + planted weak signals with known ground truth**
  — resolves cardboard + real-surveillance ethics + gives validatable ground truth. Confirm/refine here.*
- **Purpose / audience** — is the destination a **product** orgs run, a **consultancy/advisory
  instrument**, a **research reference implementation**, a **conference showcase**, a **personal
  magnum opus**, or several? This fixes what "comprehensive and right" is measured against.
- **Success definition** — the top-level acceptance bar for the *whole*: what must be true for this
  to be "done, right, comprehensive"? (Each workstream's ACs derive from this.)

Output: a named subject + purpose + top-level success definition. Everything in **Not yet specified**
graduates from here.

## Answer (2026-08-04) — RESOLVED

**Subject = (b) a fictitious org with an AI-synthesised, noisy operational + behavioural substrate**
(email/chat/commits/HR/supply-chain/telemetry) carrying **planted weak signals with known ground
truth**. Realism is grounded in **deep OSINT study of real orgs across *all* sectors** — Acquired
transcripts, biographies, founder interviews, blogs, filings, consumed knowledge — capturing both the
**common structure** every org shares and the **idiosyncratic entropy** that makes a *specific* company
feel real. Structure: **ONE flagship modelled at maximum depth + a PORTFOLIO of shallower-but-still-
convincing orgs**, each depth-upgradable on its **own independent track**. Data model carries **N orgs
+ a per-org depth/completeness grade**; the depth ladder (convincing-but-shallow → flagship-deep) *is*
the acceptance-criteria scaffold for each org's workstream. Cross-org / cross-sector comparison is
first-class. **Flagship identity is NOT decided** — Disney was only a *source exemplar*, explicitly not
a nominee; the flagship will be a **smaller, more comprehensible org** (some may have *richer* public
history than the giants), chosen by an **exhaustive, unhurried OSINT-depth survey** (ticket 06). Do
nothing fast.

**Purpose priority (highest first): (d) personal magnum opus > (c) shippable product > (a) research
reference implementation > (b) advisory persuasion.** Magnum-opus primary = the yardstick is the
builder's own comprehensiveness/craft standard, **no external gate lowers the bar** — this is the
"ambition = everything" mandate as the literal success criterion. But it must genuinely **run** (c)
and be **honest/falsifiable** (a); persuasion/the talk is a pure **byproduct** (b). (The magnum-opus
"no external gate" is itself a risk — see fable blind-spots — so a voluntarily-adopted external gate
is likely warranted.)

**Top-level success definition (accepted):**
1. **Coverage (d):** every class of signal that can move the org's landscape — external *and* internal
   — has a modelled path end-to-end: sense → Wardley/dependency impact → £ price → candidate responses
   priced in the *same* currency → recommended cheapest proportionate response *wherever it lives*. No
   category hand-waved; the scenario library exercises each.
2. **Runnable (c):** a real system on a really-populated flagship — the engine computes on it, not on
   slideware — and the architecture could onboard a real org.
3. **Honest (a):** the £ is calibrated and back-testable; what-if projections are checked against what
   actually materialises; the ethics gate (DPIA / advisory-only / no special-category) demonstrably
   works on the synthetic substrate.
4. **Legible (b):** a decision-maker can read an output and act — last, not the driver.
Plus the standing structural bar: **every workstream carries its own explicit acceptance criteria, and
a worked-backwards minimal demo slice exists.**

## Refinement (2026-08-04) — the flagship is a real-history/synthetic-substrate hybrid

Forced by the **history-as-backtest** decision (see map settled framing). The flagship is **not fully
fictitious** — it splits into two layers:
- **Strategic/structural spine — REAL.** A *single real org's* public, documented history: value chain,
  tech evolution (genesis→commodity), acquisitions, market position, key-person moves, the external
  shocks it weathered. Kept real (or only lightly renamed) — public record, not surveillance, so no
  ethics problem. **This layer is the backtest ground truth.**
- **Operational/behavioural substrate — SYNTHETIC.** Email/chat/commits/HR/comp/morale, AI-synthesised
  (we can't get real internal comms; and it's the ethically-loaded layer), **anchored to** the real
  spine, with planted signals whose "materialisation" is checked against the real events on the spine.
Portfolio orgs stay lighter (composite fictions or real-tracked) and don't carry the backtest burden.
