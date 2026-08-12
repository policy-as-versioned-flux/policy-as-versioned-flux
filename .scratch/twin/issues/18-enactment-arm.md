# 18 — The enactment arm: from recommendation to change in the world

Type: grilling
Status: RESOLVED (2026-08-05)
Blocked by: 09, 10, 13, 14 (all resolved)

## Question

How a priced, contested recommendation becomes an actual change — and whether the **prior thesis
survives contact with the risk basis**. The old estate *assumed* policy-as-versioned-dependency,
graded enforcement and posture-as-identity were right. They are hypotheses; this ticket tests them.

**Already determined:**
- Responses are **first-class objects priced against a scenario** by the FAIR factor they modify (09).
- Output is a **trade-off curve, advisory, contestable** (09, 10).
- git-native, **signed, reconstructable provenance**; authored vs derived cryptographically distinct (14).
- **Multi-org reality**: real separate repos with real signed dependency pins, never a monorepo
  (settled framing).

**Genuinely open:**
- **Does the twin act, or only propose?** ("Propose, never dispose" was the prior thesis — inherit or
  re-derive?)
- **Non-IT levers.** A pay rise, a process change, a strategic play are not code. How are they enacted,
  tracked, and closed the loop on — or is the twin blind to whether its advice was taken?
- **Does policy-as-versioned-dependency survive?** Is versioned, pinned, signed policy actually the
  right enactment mechanism for the IT/security slice *given the risk basis* — or was it a solution
  looking for a problem?
- **Graded enforcement / posture-as-identity** — same test.
- **The loop back**: ticket 08 requires knowing whether a recommendation was acted upon. What closes it?

## Acceptance criteria
- [ ] Act-vs-propose decided, with the boundary stated.
- [ ] A mechanism for non-IT enactment + tracking, or an explicit admission of blindness.
- [ ] A verdict on policy-as-versioned-dependency: survives / survives-narrowed / rejected, on the risk basis.
- [ ] A verdict on graded enforcement and posture-as-identity on the same basis.
- [ ] The action-state feedback path that closes ticket 08's conditional-forecast loop.

## Decided so far (grilling 2026-08-05)

**Q1 — (a) PROPOSE ONLY. The twin never changes the world without a human; it changes its own model
constantly.**
Notably this is now **derived, not inherited** — the prior estate *asserted* "propose, never dispose";
three independent decisions now force it:
1. **Advisory-only under Art. 22** (research 05) — no solely-automated significant decision. Law, not
   preference.
2. **The output is a trade-off curve, not a verdict** (09) — there is nothing to auto-execute; *choosing a
   point on the curve is inherently the human's act*, and that is deliberate.
3. **Agent signatures assert reproducible origin, never endorsement** (14) — an agent-initiated change has
   nobody accountable behind it.
**Why (b) graduated autonomy was rejected** despite its appeal ("auto-apply the cheap reversible stuff"):
cheapness is computed by **the twin's own £ model**, which is model-relative and explicitly never
authoritative — so autonomy would be gated by exactly the number we agreed not to trust. **The twin would
be deciding its own leash length.**
**Carve-out (not an exception):** the twin **acts freely on itself** — scheduled executions, signal
ingestion, updating inferred positions, opening its own contests. All *derived* artefacts under ticket 14:
machine-signed, reproducible, no human hands.

**Q2 — policy-as-versioned-dependency: (b) SURVIVES, NARROWED.** The prior estate's central thesis was
*asserted*; tested against the risk basis it holds only in a smaller form.
**What survives, and is now JUSTIFIED rather than assumed:** a control that modifies a named FAIR factor
must be **provably in force**, and a signed, pinned, versioned dependency makes *"this control is actually
running"* **verifiable rather than asserted**. Without it the £ number claims a control is in effect with
nothing behind the claim. That is a real requirement the risk work generates.
**What does NOT survive: the claim that versioned policy is *how governance works*.** Ticket 09 breaks
it — responses are priced by **the FAIR factor they modify**, and **most levers are not code** (a pay
rise, a JIT access change, a supplier switch, a strategic play). If versioned policy were the shape of
governance, **the cross-domain comparison that is the entire point of the £ engine could not exist.**
**So it narrows to two roles:**
1. **The enactment channel for the subset of controls that are machine-enforceable.**
2. **The verification substrate for controls that are not** — a pay rise can carry a **versioned, signed
   record that it was enacted** without being *enforced* by policy. This is the salvage that matters: it
   is what closes **ticket 08's action-state loop** and makes conditional forecasts scoreable.

**Q3 — enactment records: (c) SENSED — where "sensors" INCLUDE declarations and evidence, and
corroboration across channels increases the weight of the intel** (human, 2026-08-05).
Declarations and evidence are **not alternatives to sensing — they are sensor channels.** So an enactment
is **just another observation** in ticket 11's existing machinery (binding to the **Response** object
rather than to a Component), and its **evidence grade emerges from CORROBORATION** rather than from which
category a single source fell into:
- a bare declaration alone → low weight;
- a payroll change / merged PR / signed contract / newly-pinned policy version → higher;
- **several channels agreeing → higher than any of them alone.**
**No parallel record type is invented, and the incentive lands correctly** — if you want calibration credit
for acting, corroborate. This connects directly to ticket 08's rule that **mitigation credit is
evidence-graded and grades 4–5 earn no calibration credit**: an uncorroborated self-declaration marks the
scenario branch but earns no credit; a corroborated enactment does.
**Guard (unchanged):** this does **not** licence sensing people to verify enactment — that still must pass
ticket 15's purpose→necessity→proportionality ladder. In practice the multi-channel approach **reduces**
surveillance pressure: if a declaration and a payroll record corroborate, nobody needs watching.

**Q4 (derived, not separately grilled) — the remaining prior-estate hypotheses, on the same test:**
- **Graded enforcement — SURVIVES.** It needs no special status: it is simply a control that modifies a
  FAIR factor **by degree rather than binary**, and the £ engine already prices partial mitigation.
- **Posture-as-identity — SURVIVES NARROWED.** Valid as an *implementation* of "provably in force" for
  machine-enforceable controls (Q2 role 1); **not** as a governance philosophy.

## RESOLVED (2026-08-05)

**The twin proposes; it never changes the world without a human — but changes its own model constantly**
(derived from Art. 22 + the trade-off curve having nothing to auto-execute + agent signatures asserting
origin, not endorsement). **Policy-as-versioned-dependency survives narrowed** — the enactment channel for
machine-enforceable controls, and the **verification substrate** for those that are not, since the £
engine's cross-domain comparison requires that most levers are *not* code. **Enactment is sensed through
multiple channels** — declarations and evidence are sensor inputs, and corroboration sets the weight —
which closes ticket 08's action-state loop with no new machinery and reduces rather than increases
surveillance pressure. **Graded enforcement survives; posture-as-identity survives narrowed.**

## Acceptance criteria — all met
- [x] Act-vs-propose decided, with the boundary stated (world vs own model).
- [x] Mechanism for non-IT enactment + tracking (multi-channel sensing with corroboration-weighted grade).
- [x] Verdict on policy-as-versioned-dependency: **survives narrowed**, on the risk basis.
- [x] Verdict on graded enforcement (survives) and posture-as-identity (survives narrowed).
- [x] The action-state feedback path closing ticket 08's conditional-forecast loop.
