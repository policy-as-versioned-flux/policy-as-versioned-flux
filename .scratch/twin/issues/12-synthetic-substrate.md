# 12 — The synthetic org substrate: generating a world to sense

Type: grilling
Status: RESOLVED (2026-08-05)
Blocked by: 07, 11 (both resolved)

## Question

The AI-generated operational + behavioural data the twin senses — email, chat, commits, HR events,
supply-chain, telemetry — with **realistic noise** and **planted weak signals of known ground truth**,
so detection and the what-if→materialises loop are validatable rather than asserted. Pin:

- **What is generated vs what is real.** The co-flagship spines (Netflix, Intel) are real public
  record; the behavioural substrate is invented. Where exactly is the seam, and how do they stay
  consistent with each other?
- **Fidelity target** — what must feel real (volume, noise, mundanity, org politics) vs what can be
  thin. What makes synthetic data fail to be a fair test?
- **Planting** — how ground-truth signals are planted: their strength, lead time, burial in noise, and
  how planting stays honest given the closed-loop critique (fable #1: signals graded by the mind that
  planted them).
- **Blind/adversarial separation** — who plants, who detects, and how they are kept apart.
- **Generation method** — LLM generation at volume, simulation, replay of real public corpora, or a mix.
  Reproducibility and versioning of a generated world.
- **Contamination** — the substrate must not leak the answer (a planted signal that is trivially
  findable proves nothing; parametric contamination from famous real events).
- **Ethics** — the substrate is why the demo is exempt; keep it genuinely synthetic and non-identifying.

## Acceptance criteria
- [ ] The real/synthetic seam defined, with a consistency rule between spine and substrate.
- [ ] A fidelity target + a stated list of what would make the substrate an unfair test.
- [ ] The planting protocol (strength, lead time, burial, distribution of difficulty).
- [ ] A blind/adversarial separation mechanism between planter and detector.
- [ ] Generation method + reproducibility/versioning decision.
- [ ] Anti-contamination measures.
- [ ] Ethics/non-identification check.

## Decided so far (grilling 2026-08-05)

**Q1 — purpose: (c) LAYERED — a believable world as the *medium*, planted ground truth as instrumented
*test cases* inside it. Measurability wins ties.**
- Success criterion is **"we can state a hit rate and a lead time with error bars"**, not "it reads
  convincingly."
- **Believability-first is a trap**: a rich, convincing org that we then ask "did the twin find the
  signals?" feels impressive and proves little — the fable critique in pure form. Realism is
  *instrumentally* required (a signal buried in unrealistic noise is not a fair test), and it is a
  **testable property** (volume, noise, mundanity) rather than an asserted vibe.
- **Volume argument:** the weather-forecast frame needs many scoreable events. Believability-first tends
  to produce a handful of rich dramatic storylines — the low-n problem that makes calibration meaningless.
  Measurement-first deliberately produces **many planted signals across a spread of difficulty, most of
  them boring.**

**Q2 — planting: (b) ENFORCED ADVERSARIAL SPLIT, with its limits stated plainly.**
A **planter** agent holds ground truth in a sealed artefact; a **detector** agent runs with no access to it
and no shared context; a **scorer** reads both. Mechanically enforceable with the existing workflow
machinery (separate subagents, isolated contexts, ground truth written where the detector cannot read) —
**real separation, not a promise**.
**What it does NOT fix (recorded, not papered over):** planter and detector are the **same model family
and share priors**. The detector may find a signal because it *thinks like the planter*, not because the
signal was findable. Varying the planting model helps at the margin and must not be oversold.
**Therefore the two falsification mechanisms do DIFFERENT JOBS and neither is sufficient alone:**
- **The synthetic substrate measures detection *mechanics*** — hit rate vs burial depth, lead time vs
  signal strength, the ticket-11 decay/rescue path. Measurable only because we know the answer.
- **The real backtest suite (Carillion, NMC, Wirecard, Kodak) validates against ground truth we did not
  author** — the external surprise no internal rigour can synthesise (fable's meta-point).
**Standing honesty rule:** a synthetic result is **never** evidence the twin anticipates *the world* —
only evidence that the detection machinery works. Claims must be stated at that scope.

**Q3 — consistency: (c) ANCHORED at real events, FREE-RUNNING mundane noise elsewhere.**
Rule: **the spine is authoritative and immutable; the substrate may never contradict a dated public fact,
but is free wherever the record is silent** — which is almost everywhere. Also keeps ethics clean:
invented material sits exactly where no real person's actual behaviour is documented.
**(a) generate-everything-from-the-spine is actively dangerous:** the noise floor would be wrong and
**planted signals become trivially findable by being the only thing not anchored to public record** — a
rigged test that looks rigorous. Realistic mundanity (lunch orders, sprint grumbling, expense chasing, a
long argument about a staging environment) is a **test-fairness requirement**, not decoration. (b)
generate-then-reconcile is the wrong order: expensive, and it leaves seams.

**Q3b — ACTIONABILITY HORIZON: detection is not the product; actionable lead time is** (human,
2026-08-05: *"by the time something is detectable it's often too late to course correct, positive or
negative"*).
Every planted signal carries a **point of no return** — a date after which detection stops helping. The
score is **detected before or after the actionability horizon**, not merely detected. A detection past the
horizon has near-zero **option value** and must be priced as such (ticket 09). An engine that reliably
reports what you can no longer act on is a **post-mortem generator wearing an anticipation engine's
clothes** — and without this measure we would not be able to tell the difference.
Implication for planting: the difficulty spread must include signals that are **only ever detectable too
late**, so the twin's honest ceiling is measured rather than assumed.

**Q3c — NEGATIVITY BIAS in the record (human, 2026-08-05: *"a slant towards negative being reported more
than positive"*) — and it has infected our own roster.**
Bad news generates post-mortems, inquiries, litigation and journalism; good decisions generate a quiet
year. So the public record **over-represents failure**, and a substrate mirroring it will train/tune the
twin toward threat-detection.
**Consequences:**
1. The substrate must **model the reporting asymmetry deliberately** (negative events better documented,
   positive ones sparse and late) rather than generating a falsely balanced world — otherwise the test is
   unrealistically easy in a way that flatters us.
2. **The twin will be better at fear than opportunity unless explicitly counterweighted** — directly
   undermining the committed "fear AND opportunity" / Wardley-gameplay half.
3. **ROSTER GAP (raised here, owned by the backtest workstream):** every backtest case chosen —
   **Carillion, Enron, Wirecard, NMC, Kodak** — is a **collapse**. We validate an engine that promises
   opportunity-seizing **exclusively on catastrophes**. Needed: **seized-opportunity cases** with dated,
   contemporaneous evidence that the opportunity was publicly visible before it was taken (and ideally
   **missed-opportunity** cases — where the option was visible and not taken). Netflix's DVD→streaming
   and ad-tier moves are candidates on the flagship itself, but the *suite* needs its own.

**Q4 — generation: (a) SEEDED LLM GENERATION WITH A VERSIONED RECIPE, plus an EVAL + TUNING LOOP**
(human addition: *"include evals to test the agency, which leans towards b — that tunes the signal:noise
and accuracy"*).
Rejected: **(c) transformed real corpus** (e.g. the Enron email set) — it fails twice on prior
commitments: real people's real emails (the ethics reason we chose synthetic), and it sits in every
model's training data (**parametric contamination**). **(b) agent-based simulation** — a large build for
questionable gain; we would be debugging an org simulator instead of a twin.

**Reproducibility rule:** the world must be **regenerable, not merely stored**. The **generator recipe** —
prompts, seeds, model version, planted-signal schedule — is **versioned in git**; the bulk output lives
outside it (ticket 07's exception) and is reproducible from the recipe. Without this, a backtest cannot be
re-run after any change and *"we improved the detector"* becomes unfalsifiable because the world moved
too. Same property as everywhere else: **the thing you must trust is small, versioned and inspectable;
the bulk is derived.**

**THE EVAL SUITE IS THE FIDELITY TARGET.** Realism is *encoded as evals and tuned*, not asserted in prose
— the concrete form of Q1's "measurability wins". The generator becomes a **calibrated component**, same
discipline as the twin itself (and this iterative tuning is where it borrows simulation's character
without becoming an org simulator). Evals measure at least:
- **signal-to-noise ratio** against a target, tuned rather than guessed;
- **planted-signal difficulty** — not trivially findable, not impossible; the intended spread achieved;
- **spine consistency** — no contradiction of a dated public fact;
- **reporting asymmetry** — the negative/positive documentation slant (Q3c) matches the real world;
- **volume and mundanity** — enough boring material for signals to genuinely hide in.

## RESOLVED (2026-08-05)

A **believable world as medium, instrumented test cases inside it, measurability winning ties**; built by
**seeded LLM generation from a versioned recipe** with an **eval suite that defines and tunes fidelity**;
**anchored to the immutable public spine, free-running where the record is silent**; ground truth planted
under an **enforced adversarial split** whose limits are stated (shared model priors — so synthetic
results evidence *detection mechanics only*, never anticipation of the world); every planted signal
carrying an **actionability horizon** so the measure is *actionable* lead time; and the **negativity bias
modelled deliberately** rather than smoothed away.

## Acceptance criteria — all met
- [x] Real/synthetic seam defined, with a consistency rule (spine authoritative + immutable; free where silent).
- [x] Fidelity target + what makes it an unfair test — **encoded as the eval suite**; unfair-test list:
      over-anchored noise, trivially-findable plants, falsely balanced positive/negative, wrong volume.
- [x] Planting protocol — difficulty spread, burial, **actionability horizon**, incl. deliberately
      too-late-to-act signals so the honest ceiling is measured.
- [x] Blind/adversarial separation (planter / detector / scorer), **with its limits recorded**.
- [x] Generation method + reproducibility (versioned recipe; regenerable, not merely stored).
- [x] Anti-contamination (no real corpora; the ticket-06 Enron-as-control discount remains the measure).
- [x] Ethics/non-identification (fully synthetic; invented material sits only where the record is silent).
