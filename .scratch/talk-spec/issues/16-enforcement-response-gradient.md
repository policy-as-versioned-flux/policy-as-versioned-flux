# Enforcement response gradient — proportionate graded outcomes, not binary admit/deny

Type: grilling
Status: resolved
Blocked by: None (extends resolved 02, 04, 05, 06)

## Question

Today the policy answer is Boolean (admit / deny; at most Audit vs Deny). The human wants
enforcement to carry **colour** — a proportionate *gradient* of running conditions — while still
being driven by the risk £. Two directions surfaced:

- **Earn capability (upward):** privileges denied by default unlock **on proof** — "you may run
  privileged / as root / mount hostPath / hold this capability *if* signed + attested + clean SBOM."
  The conditional-policy pattern ("you may X if C"), but C gates *capabilities*, not just admission,
  and the proof is cryptographic (gitsign/attestation, which we already have).
- **Absorb friction (downward):** less trust ≠ eviction — it's a **constrained envelope.** Behind on
  patching / weak provenance / live CVE → still runs, but policy **mutates it into a proportionate
  cage:** throttled CPU/mem/IOPS/network, tighter NetworkPolicy + egress-deny, read-only-fs / seccomp
  / dropped caps, an injected heavier-WAF sidecar, lower eviction priority, no secret mounts.

**The unifying frame:** trust buys you *up* a curve (more capability, fewer runtime controls,
cheaper to run); its absence pushes you *down* (caged, more controls, more expensive) — and **deny is
just the bottom rung.** Each rung down **costs more to run AND carries more residual £** → the
degraded state is a priced *retain-with-mitigation* move, the compliant path becomes the *cheap*
path (economically, not just culturally), and every rung's cost + residual rolls up to the balance
sheet. Pod Security Standards (`privileged`/`baseline`/`restricted`) is the real-world anchor — but
static; we make it **risk-£-driven and attestation-gated.**

**Architectural consequence:** Kyverno stops being validation-only — the graded response is
**mutation + generation** (reshape the workload into its envelope: inject limits, generate the
NetworkPolicy, set securityContext, annotate for the WAF). Flux still distributes; the £ engine now
selects a *tier/envelope*, not just an action.

**To decide:** the gradient's abstraction (tiers vs dials vs both); how deep it goes
(demonstrable-core vs narrated); which rungs/dials are real on stage; how it plugs into the FAIR £
and the balance sheet; the Kyverno mutate/generate architecture. May spawn a research sub-ticket
(real-world graded-enforcement practice; Kyverno mutate/generate patterns) and/or a prototype.

> Reopens the map (was decision-complete). Pauses publishing the Phase 0–5 build tickets until the
> enforcement model settles, since it materially expands the enforcement + £ build.

## Evolving (grilling in progress, 2026-07-23)

**Correction (human):** encourage least-privilege / zero-trust — trust must never *earn you loose*.
The "upward = more privilege / looser netpol" framing is wrong. Least-privilege is the **floor for
everyone**; posture never buys you out of it. So the gradient is really **two mechanisms**:

- **(A) self-envelope** — posture cages *your own* runtime further (throttle CPU/mem/IOPS/net, heavier
  WAF, dropped caps, read-only-fs). Falling behind tightens *you*; it never loosens you.
- **(B) posture-as-identity (the richer, zero-trust-native axis)** — the policy version + attestation
  a workload was admitted under becomes a **claim on its attestable runtime identity**, and *other*
  services gate on it. A sensitive service (e.g. `customer-accounts-reset`) demands a higher posture
  bar for callers than a general runtime cluster does. Lose policy-currency → lose *reach* (and/or
  run caged) — never gain privilege. (tiers-vs-dials from the opening question drops to a sub-detail
  of how posture is expressed.)

**Stack for (B): a SPIFFE/SPIRE + Istio + OpenBao shape.** Kyverno records posture at admission →
projected into the workload's SPIFFE SVID → consumed by Istio `AuthorizationPolicy` (service-to-
service) + OpenBao (secret issuance gated on posture) → Flux distributes it all, versioned.
**Thesis payoff:** makes "provenance for every actor" *continuous* — gitsign→Rekor attests the
supply chain; SPIFFE→SPIRE attests the running workload; one unbroken verify-don't-trust chain from
commit → build → admission → runtime identity → every service call.

**Least-standard integration to de-risk:** Kyverno → SPIRE posture projection (admission posture →
SVID selector). Istio-consumes-SPIRE and OpenBao-consumes-SPIFFE are trodden; that hand-off is the
prototype/research candidate.

**Open (being grilled):** identity carrier (SPIRE vs projected-token vs Istio-mTLS-only); how much of
(B) is demonstrable-core vs narrated (mesh+SPIRE+OpenBao is a big build); which sensitive service +
institution carries the live beat.

**Q2 resolved — identity carrier = SPIFFE/SPIRE** (2026-07-23). Attestation-native, vendor-neutral,
consumed by both Istio and OpenBao; the runtime twin of gitsign — makes runtime identity attestable
in the same sense the supply chain is. Rejected: projected SA-token (re-introduces "trust the issuer"
at the verify hop) and Istio-mTLS-without-SPIRE (leans on the mesh CA, not a workload attestor).

**Balance-sheet economics of (A) resolved → TCoR** (see ticket 06 update).

## Answer (2026-07-23) — resolved

Enforcement is a **proportionate graded response**, not binary. Least-privilege is the floor for
everyone; trust never earns loose. Two mechanisms:

- **(A) self-envelope** — posture cages your *own* runtime by degree (throttle CPU/mem/IOPS/net,
  heavier WAF sidecar, dropped caps, read-only-fs, eviction priority). **Kyverno mutate + generate**
  reshapes the workload into its envelope. Deny is just the bottom rung.
- **(B) posture-as-identity** — the policy version + attestation a workload was admitted under is a
  **claim on its SPIFFE/SPIRE SVID**; **Istio AuthorizationPolicy** (service-to-service) and
  **OpenBao** (secret issuance) gate on it. Sensitive services demand a higher posture bar for
  callers; losing currency loses *reach* + secrets, never gains privilege.

**Economics = Total Cost of Risk.** A cage is a priced partial-reduce on a retained risk (residual
R′>0 **and** run-cost C_cage, both booked). Balance-sheet number = **TCoR = residual + cost-of-
controls (incl. dynamic cages) + transfer (premiums)**. "Compliant = cheap" is a computed crossover;
the war-gamer picks **fix vs cage vs transfer vs deny** by TCoR (ticket 06 updated).

**Provenance continuity (thesis payoff):** gitsign→Rekor attests the supply chain; SPIFFE→SPIRE
attests the running workload — one unbroken verify-don't-trust chain commit→build→admission→
runtime-identity→every-call. (A) deepens the proportionality beat, (B) the provenance beat; the
3-beat spine holds — no 4th beat.

**Decisions:** carrier = **SPIFFE/SPIRE** (Q2); Kyverno role = validate + mutate + generate +
posture-projection; Flux distributes the AuthorizationPolicies / SPIRE registrations / OpenBao
policies, versioned. **Abstraction = tiers over dials** (recommended default, build-detail, flexible):
independent dials (capability · resource envelope · runtime-controls · WAF weight · reach) are the
mechanism; a few named **tiers** (PSS-style) are the £/TCoR-selected, priceable presets that expand
via mutate/generate into dial settings.

**Scope = build everything, estate-wide** (human). Mechanism universal + deployed on all three
clusters + posture-gating across all institutions; **gating density follows proportionality**
(ludlow broad → driftwood narrow), so breadth-of-gating is itself a proportionality signal — *not*
every-call-uniform (which would violate the thesis). **Flagship live beat:** `customer-accounts-reset`
(tuppence) — Istio authz requires current-policy callers; OpenBao issues its credential only to
current-posture identities; a caller drifting out of currency loses reach + secret, live.
Audience-modular to `ludlow` patient-record-access.

**Spawned** [ticket 17 — research: Kyverno→SPIRE posture projection](17-posture-identity-research.md)
to de-risk the one non-trodden hand-off (research subagent fired). **Downstream (build fog):**
`the-whole-model.md`, `spec.md`, and the unpublished Phase 0–5 build tickets must fold in the
graded-response + posture-identity layer before publishing.

**Research (ticket 17) folded in (2026-07-23):** posture-as-identity is feasible natively — posture
carried in the **SVID path** (Kyverno mutate label → `ClusterSPIFFEID` template → SVID URI; Istio
principals prefix-match, OpenBao JWT `bound_claims` glob). Adds two required components to the build:
a **currency controller** (re-evaluate posture post-admission → makes runtime re-tuning real, not an
admission snapshot) and a **posture-label trust-boundary** (Kyverno-only-settable, else forgeable).
Base to extend: ControlPlane `getting-started-spire-openbao`.
