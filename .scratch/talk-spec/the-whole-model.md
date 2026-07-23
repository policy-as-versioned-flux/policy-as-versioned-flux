# The whole model — one page

Consolidation of the charting grilling (2026-07-23). The map's tickets hold the detail; this is the
picture they add up to, plus the build order and the talk's spine.

## Thesis (one line)

> Governance is a **proportionate, informed, continuously re-tuned response to quantified risk** —
> and versioning the whole chain from risk-appetite to evidence, with **every actor attestable**, is
> how proportionality stays honest and current as the world moves.

Policy is a **versioned dependency** (a lint/rule pack): pinned, signed, adopted per-team by PR.
That's the *mechanism*. Risk is the *ground*. The hourglass is the *structure*. The living loop is
what keeps it *alive*.

## The integrated picture

```
   ANTICIPATE                RISK APPETITE (£ per institution) ── the ground & the scoreboard
   AI-Wardley ──┐            ┌──────────────┴───────────────────────────────▲─────────────┐
   (commodit-   │  sets proportionality                                     │ residual £  │
    isation,    ▼            ▼                                              │  → BALANCE   │
    market-  ┌──────────────────────────────────────────────┐             │    SHEET     │
    intel)   │  PRINCIPLES → CONTROLS → ENFORCEMENT          │  the        │  (insurance, │
   OBSERVE   │  Kyverno CEL · CONDITIONAL policy (no         │  hourglass  │   valuation, │
   feeds:    │  exemptions) · ±1 shift-left checked in CI    │             │   board)     │
   threat ·  │  Flux distributes: signed GitRepository,      │   EVIDENCE ─┘              │
   CVE ·     │  ResourceSet fan-out, prune-on-retire, heal   │   (OSCAL risk objects)     │
   EOL ·     └───────────────────────┬──────────────────────┘   flows UP ────────────────┘
   penalties │                       ▼
     ──────► │                  WAR-GAMER  ── stress-tests controls ──► proportionality drift?
             │                  (governance-agent evolved)                     │
             └──────────────────────────────────────────────────────► on drift: opens a POLICY PR
                                                                              │  PROPOSES, never disposes
                                        human review + PR-gate + gitsign ◄────┘
                                                    │ signed release → estate re-tunes → £ moves
              ── every actor & action attestable (gitsign keyless → Rekor): verify, don't trust ──
```

## The six-org dependency & provenance graph

```
  policy-as-versioned-nist ──(OSCAL controls, real)──┐
  policy-as-versioned-ico  ──(penalties@v, £)────────┤ upstream, versioned, signed
                                                      ▼
  policy-as-versioned-platform ──(the discipline: Flux templates, FAIR engine, war-gamer,
       │  Wardley layer, ledger→PolicyException render, shift-left harness, OSCAL plumbing)
       │  inherited as a pinned, signed dependency by each institution ↓
       ├──► policy-as-versioned-driftwood  (e-comm · PCI+GDPR · teaching default · FULLY LIVE)
       ├──► policy-as-versioned-tuppence   (fintech · FCA+PCI+GDPR · scary £  · FULLY LIVE)
       └──► policy-as-versioned-caldera    (US health · HIPAA · long-life data · FULLY LIVE)
  (existing policy-as-versioned-flux → ARCHIVE as the last migration step)
```

## What's built (nothing is a "nice-to-have")

- **Distribution** — Flux: `ResourceSet` version fan-out, signed `GitRepository`, prune-on-retire,
  drift-heal, `dependsOn`/health, notification spine.
- **Enforcement** — Kyverno CEL `ValidatingPolicy`; **conditional policy** (exemptions dissolved —
  "you may X if C", uniform, versioned); orphan-guard locked door.
- **Risk engine (actuarially grounded — FAIR *is* frequency×severity)** — `(min,mode,max)` leaves →
  beta-PERT → Monte-Carlo → aggregate loss distribution → **ALE + VaR₉₅ + TVaR** (Expected
  Shortfall — the tail measure Solvency II mandates, not just the percentile). The £ carries a
  **risk load** for volatility, not just the mean.
- **Proportionality = the four risk-financing moves** — for each risk: **avoid · reduce** (a
  control) **· transfer** (insure it — premium £ vs control £; moves the risk off residual onto a
  carrier) **· retain** (conditional policy + priced residual). The war-gamer weighs them and
  proposes whichever is proportionate; *insurance is a control option*. Net £ = risk-removed −
  cost-of-the-chosen-move, judged against tolerance bands.
- **Calibration via credibility theory (Bühlmann)** — the proven actuarial method for blending the
  model estimate with emerging actual losses; how the £ stays falsifiable and audit/insurer-defensible.
- **Feeds (all signed, versioned upstreams)** — institution threat register · CVE (`trivy`/GHSA) ·
  EOL (`endoflife.date`) · regulator penalties (`nist`+`ico`) · market-intel via **AI-Wardley**.
- **Living loop** — **war-gaming agent** (evolved `governance-agent`): collect → war-game → on
  drift open a **policy PR**; propose-never-dispose; the PR-gate + human + versioning are the rails.
- **Provenance** — every actor & action gitsign-signed → Rekor; verifiable feed→scenario→PR→merge.
- **Shift-left** — ±1 version-skew off the `ResourceSet` array; `kyverno apply` runs the target
  version's real action offline (Audit→Deny caught in CI; a deploy-time fail is unheard-of).
- **Evidence up-flow** — `c2p`/OSCAL; exemptions/accepted-risk as OSCAL `risk`/POA&M objects.
- **Balance sheet = economic / risk-based capital** — residual £ (post reduce/transfer/retain),
  framed as Solvency-II-style economic capital held against quantified risk over a horizon → the
  reserving/provisioning line, the insurance-premium input, the diligence number, the board line.
  Validated against real practice: **underwriting warranties ↔ conditional policy**, **cat-modelling
  ↔ the war-gamer**, **IBNR reserving ↔ the provision**, **correlation/diversification ↔ shared-
  platform systemic risk**.
- **Anticipation** — Wardley (AI + market-intel): commoditisation + chains, ahead of the feeds.
- **NEW, folded in 2026-07-23:**
  - **Calibration / back-testing** — log real incidents/near-misses, compare to prediction,
    recalibrate; the number's falsifiability + its audit/insurer defensibility.
  - **Securing the security system** — feed integrity (signed/sourced/bounded) + AI-proposer bounds
    (confidence, rate-limit, learn-from-rejections), gate as hard backstop.
  - **Reflexive self-governance** — the apparatus prices itself (is it proportionate?), and governs
    its own supply chain (platform/Kyverno/Flux under the same risk model). It passes its own test.

## Build order (dependency-driven)

0. **Platform skeleton** — Flux + Kyverno + `ResourceSet`; `driftwood` minimal, one version live.
1. **Risk engine + conditional policy + the £** — FAIR against `driftwood`; `nist` controls feed.
2. **The other two institutions + `ico` penalties + the proportionality *comparison*** (same
   control, Audit in retail / Deny in health, different £) — the thesis's money shot.
3. **Up-flow + balance sheet + shift-left** — OSCAL risk objects; residual → £; CI ±1 check.
4. **The living loop** — feeds + war-gamer + AI-Wardley + provenance-for-every-actor.
5. **Calibration + feed-integrity + reflexive** — the honesty/robustness layer.

## The talk's spine (through-line), and demonstrable-core vs narrated-vision

**Locked (2026-07-23):** a **~35–40 min conference talk that tours** — principal-engineers +
leaders. Three beats demoed **live**: *proportionality* (retail-vs-health), the *living loop*
(war-gamer → signed PR → human+gate → £ moves), and *provenance* (verify in Rekor). *Breach-cost*
is the cold open and *balance-sheet* the close — both **narrated**, not demoed. Touring ⇒ two
build requirements: **(a) reproducible on a laptop at a venue** (idempotent bring-up, offline-safe,
resettable between runs); **(b) audience-modular** — re-foreground the institution that matches the
room (`tuppence`/fintech, `caldera`/health, `driftwood`/general) with zero rebuild.

**Spine:** open on **what a breach costs** (risk, not GitOps) → policy is a **versioned dependency**
(the lint-pack you already trust) → **proportionality** (same control, different verdict per
institution, because the £ differs) → the **living loop** (the estate war-games itself, opens a
*signed* PR, a human + the gate dispose, the £ moves) → **provenance** (verify, don't trust the AI)
→ close on **risk on the balance sheet**.

- **Demonstrable-core — built and shown LIVE:** the six-org estate; coexisting signed versions;
  admission enforcement + conditional policy; the FAIR £ moving when you tighten a control or accept
  a condition; the war-gamer opening a **real signed PR** off a feed change; that PR's provenance in
  Rekor; the **cross-institution comparison** (retail vs health, same control, different £).
- **Narrated-vision — real, grounded, but gestured not fully productionised:** regulator-publishes-
  penalties-as-code as an *industry* norm; the full insurance-underwriting / board-balance-sheet
  consumption; post-quantum + the commodity-attack-cost-collapse as *worked scenarios* the war-gamer
  runs (we did one by hand — ransomware/PQ — live-runnable, not a slide).
