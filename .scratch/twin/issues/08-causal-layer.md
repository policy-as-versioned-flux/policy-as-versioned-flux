# 08 — The causal layer: making fast-forward/rewind/play interventional

Type: grilling
Status: open
Blocked by: 07 (resolved)

## Question

Ticket 07 decided causal edges exist as a typed layer with evidence + confidence. This ticket decides
**how they actually work** — fable's #2 finding: a knowledge graph gives Pearl rung 1, but *play* is
rung 2 (intervention) and *rewind* is rung 3 (counterfactual).

- **Claim model** — what exactly does a causal edge assert (direction, sign, lag, functional form,
  strength)? Point estimate or distribution?
- **Evidence grades** — what backs a causal claim (documented mechanism, historical co-movement,
  expert judgement, literature)? How is confidence expressed, and when is an edge too weak to use?
- **Intervention semantics** — how `do(x)` propagates: which edges carry it, how effects compose along
  paths, what happens where only structural edges exist.
- **Counterfactual/rewind semantics** — what "would it have happened if we'd patched?" computes over.
- **Intervention-aware scoring** — the forecast record must know a prediction was *acted upon*, else a
  mitigated non-event scores as a bad forecast and poisons calibration. How is action recorded and
  netted out?
- **Confounding discipline** — how much identification rigour without stalling on causal purism.

## Acceptance criteria
- [ ] A causal-edge schema (assertion + evidence grade + confidence) in ubiquitous language.
- [ ] Defined intervention + counterfactual semantics, incl. behaviour on structural-only paths.
- [ ] The intervention-aware scoring rule, with a worked example of a mitigated non-event.
- [ ] A stated identification/confounding discipline + its honest limits.
- [ ] Exercised on a real claim from each co-flagship (Qwikster→churn; EUV delay→node slip).
