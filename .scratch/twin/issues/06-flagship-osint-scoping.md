# 06 — Flagship OSINT-scoping: source the deep org from the evidence

Type: research
Status: RESOLVED (2026-08-04) — Netflix + Intel co-flagships; contamination-controlled backtest suite
Blocked by: 01 (resolved)

## Question

Exhaustively survey candidate **real organisations** to source the **flagship fictitious archetype**
from — and 2–3 contrasting **portfolio** candidates. The selection criterion the human set: **maximum
sourceable OSINT depth**, but with a deliberate bias toward **smaller, more *comprehensible*
organisations** — some of which may have *richer* public history than the mega-caps. **Disney and the
giants are explicitly de-prioritised** (Disney was only a source exemplar). "Comprehensible" = one
person can hold the whole value chain, cast of key people, and history in their head.

Rank each candidate on:
- **OSINT depth & quality** — volume and richness of *narrated strategic history*: Acquired-grade
  transcripts, biographies/memoirs, founder & employee interviews, long-form journalism, oral
  histories, filings, court records, post-mortems.
- **Comprehensibility** — small/legible enough to model at *maximum depth* without drowning.
- **Risk-surface breadth vs the scenario library** — how many of {geopolitical, sanctions, supply-
  chain, IP, cyber/data, insider/key-person, HR/comp/morale, climate/physical, M&A, tech-evolution}
  the org's real history genuinely exercises.
- **Idiosyncratic entropy** — how much *specific, non-generic* texture the sources reveal (the thing
  that stops it being a sector-average cardboard cutout).
- **Documented history of *movement and shocks* (NEW — the decisive axis).** Because the flagship's
  real history is now the **backtest ground truth** (rewind→fast-forward scored against what actually
  happened), the org must have a **long, well-documented history of components *moving* on the map**
  — evolution, strategic pivots, acquisitions, crises weathered, technologies commoditised. A richly-
  described but *static* org is worth less than a smaller org with a well-narrated arc of *change*.

## Acceptance criteria

- [ ] ≥ 15–20 candidate orgs surveyed **across all sectors**, each with a short sourcing dossier
      (what public material exists, its volume/quality, and the gaps).
- [ ] Explicit, evidenced bias toward smaller/comprehensible orgs; a giant only shortlisted if
      *uniquely* sourceable **and** still comprehensible.
- [ ] Every candidate scored on the four axes above, with the evidence cited.
- [ ] Every candidate assessed for a **documented arc of change over time** (the backtest corpus), not just static richness.
- [ ] A recommended **flagship** + **2–3 contrasting portfolio** orgs (different sectors), with rationale.
- [ ] Fold in any selection criteria surfaced by the fable blind-spots pass before firing.
- [ ] NOT fired until the human gives the go.

## Wave 1 (2026-08-04) — done; surfaced a criteria flaw

24 orgs surveyed (model-tiered workflow). Opus recommended **LEGO** (portfolio ARM/Maersk/Nokia);
the **fable contrarian dismantled it** on a load-bearing point: LEGO's "ground truth" is a sanctioned
survivor memoir (*Brick by Brick*, hindsight baked in), a private company gives **no temporal
resolution** (can't score *when* the twin should have flagged), and the **collapsed-firm-with-answer-
key class was never in the candidate set**. Full survey + contrarian: `research/flagship-osint-scoping.md`.
Human decision: **run a second wave** before committing. The OSINT axis rewarded story depth over
contemporaneity/adversariality — corrected in the settled framing.

## Wave 2 (firing 2026-08-04) — sample the missing class + re-score on the new axis

- **Class A — collapsed firms with an official post-mortem + market-priced answer key:** Carillion,
  Marconi/GEC, Northern Rock, Enron, Wirecard, Lehman Brothers, Nortel, Silicon Valley Bank, Kodak.
- **Class B — re-score the top living orgs on temporal resolution + adversariality:** LEGO, Ferrari,
  ARM, Nintendo, Netflix.
- **Corrected weighting:** flagship = best *living, whole-org* model (fear AND opportunity + behavioural
  substrate) with decent temporal resolution; **dedicated backtest org** = best collapsed-firm
  answer-key case; plus breadth portfolio. Output: `research/flagship-osint-scoping-wave2.md`.

## RESOLVED (2026-08-04) — the subject roster

Two adversarial waves (24 + 14 orgs). Wave 1's LEGO pick was overturned in wave 2 (LEGO → composite 4,
fails the temporal-resolution test). Human decision: **two co-flagships + a contamination-controlled
backtest suite.**

### Co-flagships (both at maximum depth — the twin proves itself BOTH directions)
- **Netflix — retrospective / whole-engine flagship.** Living, comprehensible; exercises fear (Qwikster
  2011, 2022 crash) AND seize (verticalisation, ad tier, live sports) on dated evidence; unusually deep
  behavioural substrate (culture deck, keeper test, no-bonus comp, Hastings→Sarandos); real quarterly
  temporal resolution. Carries the rewind/backtest + the full sense→map→price→respond loop.
  *Caveats:* fear is museum-grade (a mid-2026 consensus winner); substrate is named living individuals
  + a live lawsuit (Baillie) → allegations tagged as allegations, no Netflix marks/impersonation.
- **Intel — live / forward flagship.** A genuinely UNRESOLVED 2026 existential situation (foundry gamble,
  AI miss, share collapse, US-gov stake). Carries fast-forward + the **pre-registered forecast gate** —
  the twin makes falsifiable FORWARD predictions scored against what actually materialises. Accepts the
  mega-cap/comprehensibility cost for thesis-purity: anticipation in flight, not just in retrospect.

### Backtest / falsification suite (resolved answer keys)
- **Carillion — PRIMARY.** Low-contamination; *free, dated, public* answer key (most-shorted LSE stock
  ~2yr pre-collapse via statutory FCA disclosures) + four forced post-mortems (select committee, FRC/
  KPMG fine, director disqualification). No live brand/family to impersonate.
- **NMC Health — second low-contamination key** (Muddy Waters dated PDF Dec 2019 → administration Apr
  2020 → ADGM judgment vs EY 2024). *Needs a verification pass before anchoring scores.*
- **Enron — CONTAMINATION CONTROL, not proof.** Run the identical rubric on Enron and on an obscure key;
  the Enron-over-obscure delta = a **measured memorisation-leakage discount applied to all backtest
  scores** (the calibration dial). Turns Enron's fatal fame into instrumentation.
- **Wirecard — captured-regulator / signal-suppression exemplar** (BaFin short-ban + journalist
  prosecution): tests whether the twin mistakes regulatory legitimacy for reassurance.

### Breadth portfolio
- **Kodak** — slow-drift / capability-rigidity tempo (graduated market key 2003→2012 + the 1979/81
  Barabba internal-foresight study). **Maersk** — cyber / operational resilience (NotPetya 2017).

### Methodological pillar banked
**Parametric contamination is first-class** for the backtest workstream: an LLM twin "flagging" a famous
collapse can't be distinguished from memorisation. Prefer low-notoriety keys; measure + discount
leakage via the Enron control; gate all information at time-T.

### Open verification items (before locking backtest SCORES — Claude-in-Chrome deep-pull)
- Carillion FCA short-position disclosure history (dates); the HC 769 select-committee report.
- NMC Health: the Muddy Waters PDF (17 Dec 2019) + the ADGM judgment vs EY (2024).
- **Jonathan Weil, WSJ, 20 Sep 2000** — the earliest opposed-interest Enron signal (predates Chanos);
  both waves missed it. Confirm date + content.
- Intel's live 2026 posture (for the forward-forecast baseline).

Full surveys: `research/flagship-osint-scoping.md` (wave 1) + `research/flagship-osint-scoping-wave2.md`
(wave 2, incl. both contrarian challenges).
