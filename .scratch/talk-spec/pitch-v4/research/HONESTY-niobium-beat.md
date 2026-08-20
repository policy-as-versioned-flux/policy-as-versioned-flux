# The niobium beat — what is machine-computed and what is not

Written so the demo's own boundary is on the record, in the same spirit as the estate's
does-not-do register. Full technical analysis: `quantum-niobium-analysis.md`.

## Machine-computed, real, reproducible

Everything from a `velocity`/`evolution` figure onward is the unmodified engine
(`estate/platform/wardley/wardley.py`, `tcor.py`, `wargamer.py`, `fair.py`). Verified live
2026-08-19:

| step | mechanism | verified output |
|---|---|---|
| projection | `projected = evolution + velocity × horizon(3)` | 0.30+0.06×3 = **0.48**; 0.34+0.06×3 = **0.52** |
| stage crossing | `_stage_idx(proj) > _stage_idx(ev)` | 0.48 → still `custom`; 0.52 → `product` |
| commoditising flag | `build_map()` | `false` at 0.48, `true` at 0.52 |
| emission | `forward_signal()` only emits commoditising attacker-capabilities | PQ absent at 0.48, present at 0.52 |
| attack-cost collapse | `factor = 1 + 4.0 × movement` | movement 0.18 → **×1.72** |
| LEF bump | applied to `warn`/`behind` triples | `[0,1,3]` → `[0,1.72,5.16]` |
| re-price | `tcor.crossover()` over four moves, Monte-Carlo ALE | transfer £1,017,450 → **£1,701,257**; cage → **INF** (`select_tier` returns "deny — no tier fits the band"); fix **£212,338 unchanged**; deny £312,338 |
| drift + PR | `wargame_scenarios()` → `propose()` | `transfer -> fix`, `signed: true`, `merged: false`, `auto_merge: false`, carries the cross-check gate |

Reproduce:

```sh
python3 estate/platform/wardley/wardley.py wargame --intel /tmp/intel-B-niobium-plus-gidney.json
```

## NOT machine-computed — the analyst step

**Nothing in this system ingests a news headline and decides which component it affects, or by
how much.** The `velocity` and `evolution` figures in `market-intel.json` are hand-authored
editorial — the file says so itself ("editorial velocity", "not a live subscription").

So the link *headline → revised coordinate* is a human/analyst judgement. In the demo this is
stated aloud ("an analyst nudges quantum's velocity"), not glossed as automation.

**The gap, named:** a headline→intel-diff classifier. If built, it should *propose* a coordinate
change as a reviewable signed diff rather than auto-apply it — the same propose-never-dispose
doctrine the rest of the estate already enforces.

## Attribution of the two numbers

The demo states this explicitly rather than letting the narrative imply a causal link the physics
does not support:

- **velocity 0.05 → 0.06** — the niobium headline. Small, because the causal chain is weak
  (see below). On its own this does **not** cross the boundary. That is the honest finding, and
  the demo shows it *not* crossing.
- **evolution 0.30 → 0.34** — a published algorithmic result (~20× reduction in the qubit
  requirement vs the same author's earlier estimate). Already true, arguably mis-priced in the
  current intel. This is what causes the crossing.

## Why the niobium chain is weak

The binding constraints on a cryptographically-relevant quantum computer are error-corrected
logical qubits (evolution ≈0.22) and superconducting surface/interface chemistry (≈0.20) — both
far *left* of niobium (0.62 refined / 0.88 ore). Specifically:

- Qubit-grade niobium is made by electron-beam refining capacity, not by mining tonnage. A
  deposit does not build a furnace.
- The documented coherence limiter is native Nb₂O₅ two-level-system loss, and that oxide forms
  **after deposition, on air exposure**, from the film's own surface. A purer ingot does not
  prevent it. The known mitigation is capping/encapsulation (Ta/Al/TiN), which the headline does
  not touch.
- Trapped-ion, neutral-atom and photonic platforms use no niobium at all. If the winning modality
  is not superconducting, the chain's strength is zero.

What the headline *does* legitimately change: supply concentration (Brazil ≈93% of mine output)
and the loss of export-control leverage — a left-tail effect on *who* gets there, not a shift in
the median date.

## Known engine observation, not hidden

`pq-cryptanalysis`'s reactive base posture **already drifts** independently of any forward signal:
`deployed_move` is `transfer` but `tcor.crossover` on the unmodified base returns `cage`
(£39,933 vs £1,017,450). Unlike `phishing-kits-aas`, whose selfcheck asserts the reactive base
does not drift, nothing asserts this for PQ.

The demo therefore does **not** claim "no drift before, drift after". It claims the precisely
true thing: at 0.48 the component is never emitted into the forward signal at all, so the
war-gamer never sees this risk on that path. Worth resolving in the intel file (either declare
the base deliberate in its `note`, or correct it) before this is toured.

## The mocked headline

`wardley/headline.png` is a composed illustration, not a real news report, and says so in its own
footer. No real outlet, byline or wire service is imitated.
