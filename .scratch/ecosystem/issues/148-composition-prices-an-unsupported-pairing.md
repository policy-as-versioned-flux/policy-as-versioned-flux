# 148 — Composition prices an unsupported pairing

Type: task
Status: resolved
Blocked by: 146, 147, and the owner's authorisation for a platform tools tag and the adopter tags

## Question

Graduated 2026-09-25 from grilling ticket 71, decisions 6, 16 and 18 (delegated), and ADR-0033
points 3 and 7.

An unsupported pairing is an adopter whose declared engine is not a supported engine of a line, or
of the machinery, that the adopter composes. Composition prices it and never refuses it. Build the
following in the platform tools:

1. **Composition reads three facts.**
   - The adopter's declared engine, from its `gitops/engine/kyverno.yaml` (ticket 147).
   - Each composed line's `tested_engines`, from the platform's `distribution/versions.yaml` at the
     adopter's pinned platform tag.
   - The machinery's `tested_engines`, from the same platform tag (ticket 146 item 4).
2. **An unsupported pairing makes every claimed control a hole.** On an engine that a line does
   not support, the line's control claims do not count. Each control that the line claims is then
   a hole, priced as ADR-0026 prices a hole. The evidence document shows an `unsupported-engine`
   delta that names the line and the engine. The machinery's claim, cm-6, is priced the same way.
   A line or a machinery release with no `tested_engines` supports no engine.
3. **No declaration is priced the same way,** under an `undeclared-engine` delta. Under ADR-0020
   this is a missing behaviour, not a missing instrument: the gate can read the claims and their
   hole prices, and only the engine is unknown.
4. **The composed header records the declared engine.**
5. **The shift-left check runs each line only on engines that the line supports** (decision 18).
   `shift-left/ci-check.py` runs every line in the ±1-major window with the adopter's declared
   engine. A line in the window that does not support that engine is reported by name as an
   unsupported pairing. It is not a compile error and not a pass.
6. **The machinery supports 1.19.1 and moves to `policies.kyverno.io/v1`** in the same tools
   release. Fix each machinery body that ticket 146 item 4 grades red on 1.19.1, as ticket 149
   fixes cage-tier. Then the machinery's `tested_engines` is `[1.18.2, 1.19.1]`. If this ticket
   lands before ticket 149, it adds the 1.19.1 row to the engine table. The bodies are `v1alpha1` today,
   and both engines mark `v1alpha1` deprecated. Ticket 149 moves the policy line's bodies.
7. **A hub check grades the price.** A planted declaration of an engine that a composed line does
   not list gives the `unsupported-engine` delta. Its amount equals the sum of the hole prices of
   the controls that the line claims.

Then the rollout. Each step after the first is an owner step:

- a signed platform tools tag;
- a pin move on each adopter;
- a recompose on each adopter;
- each adopter's signed composed tag, and its composed-set move to that tag (ticket 130's route).
  The machinery reaches a cluster only through that move.

## Done

Each adopter's composed evidence records its declared engine, 1.18.2, and shows no engine delta.
The hub check passes on its planted cases. The truth run after the recomposes records no fall.

## Notes

- The order is a safety rule. This ticket lands only after ticket 147 has landed on all three
  adopters. Otherwise all three get the `undeclared-engine` price, all their claimed controls
  become holes, and the gate records a fall.
- The price assumes the worst case: the body does not load. Whether a body that does not compile
  fails open or refuses at admission is not measured. Ticket 150 measures it. If admission refuses,
  ADR-0033 point 3 reopens.
- The composer reads the substrate from the platform's `engine/namespaces.yaml`, never from the
  adopter (ticket 119). The engine version is the adopter's own fact, so it is read from the
  adopter.

## Resume implementation, 2026-10-03

Composition prices unsupported and undeclared engine pairings as named holes, with the exact engine declaration in the composed header. Engine-pairing tests pass (13 assertions). The hub priced-hole vocabulary carries both new kinds. Publication and adopter recomposition remain pending.

The owner delegated the implementing decisions on 2026-10-03: "you tell me, you control them all, you don't need me to answer". This is recorded as delegated, not as an invented institution signature.

## Answer

**2026-10-18, delivered pricing and original rollout reconciled.** The initial all-1.18.2 milestone is historical, not a requirement to undo ticket 150's authorized successor. Each adopter's signed v4.0.1 artefact records 1.18.2 without an engine delta; its final composed-set pointer precedes the source sampled by [TRUTH 379](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/261d130a9376417be52465bfee66fae7e00b8b02/talk/truth.log). Those sources are Driftwood `1194561829ff60f89cd3889ab8cf06a45d5e9dd0`, Tuppence `011942de87ba827b5bc2949da0057d862b6b69f6` and Ludlow `e7243d917c323364c0fb74d312f921d0d1ec1356`. The signed tools, pin moves, recomposes, own composed tags and composed-set moves are delivered.

[Original run 37217452830/1](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/actions/runs/37217452830/attempts/1), source `002f2a3c2e3849af6453d4e484a6efa3e4953fc7`, recorded original `261d130a9376417be52465bfee66fae7e00b8b02`. Its [engine-pairing capture](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/261d130a9376417be52465bfee66fae7e00b8b02/talk/captures/verify_engine-pairing_verify-engine-pairing.out) passes all three served and forward compositions and all five planted controls, including the independently weighted hole. The tracked 377→379 transition has no fall under the classwise contract: observed 28→38, self 50→54, simulated 3→4, meta 7→9; fail 25→5; ceiling 124 and total 143 unchanged. The in-gate fall capture deferred that run's not-yet-written line; it is not a claimed post-record workflow verdict. Genuine historical signature verification now accepts the exact original, production-default identity/claims and Rekor proof. This is standalone historical authentication, not a current-schema full-delivery receipt or an engine-only causal experiment.

Current [recorded TRUTH 435](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/79f5d3f95042463695471822fb20c3ffc7c1e2e8/talk/captures/_grades.tsv), original `2c3a651a9c4353401c26491b05d4236ba3d69b1f` delivered through PR216, gives `verify/engine-pairing/verify-engine-pairing.sh` PASS. Its full capture binds compiler `a27c83b` to accepted implementation `703eff6`, with no engine delta on Driftwood/Tuppence 1.18.2 or Ludlow 1.19.1. The declared-engine header, independently read support/claims, missing-declaration hole price, shift-left handling and v1 machinery support are delivered. The earlier recorded 432 reader failure remains historical; local repair proof is not substituted for 435.

The wrapper's touching Git subjects yield no ticket owner. This named PASS is corroboration, not an invented owned PASS; the tracker consults ownership for red rows. Original 379 supplies the post-rollout no-fall condition, not an assertion about 435's transition. Producer 435 still concludes FAILURE with four other failing rows; no estate-wide green, new financial credit or changed historical observation is claimed. Tickets 146/147 and the owner delivery steps are complete. Ludlow's later move belongs to ticket 150.
