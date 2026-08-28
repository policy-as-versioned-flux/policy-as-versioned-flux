# 09 — The cage ladder v2

Type: grilling (HITL)
Status: claimed
Blocked by: 08

## Question

The cage as the only enforcement, in full. The ladder gains a bottom rung below quarantine ('too expensive to run or not functional'). A MutatingPolicy defaults the strictest cage at CREATE to any pod that claims nothing; infrastructure claims an infra cage explicitly; the governed-namespace deny is replaced. The tier is declared in the adopter's signed composed artefact and rendered down to `posture.acme.io/tier`; it has a trust boundary (validating deny of an unentitled tier, mutating clobber from the priced decision, unknown label fails closed to strictest). De-posture is a tier move that keeps the claim and prices the residual. An adopter may set a tighten-only tier floor in its overlay. Loosening short of removal is priced; removal-to-nothing refuses. Warn rung: realise or drop. Access.py retired; break-glass scales by org appetite.

## Notes

Re-grills 15, 16, 23, 28; reversals 5, 11, 12, 13, 17; findings H2-01..H2-16, H8-03, H8-09, H8-12. Blocked by the £ seam because the tier's source is decided there.

## Comments

- 2026-08-28, from ticket 03: platform v3.0.0 `require-nonroot` refuses every baseline-tier pod, because `cage-tier` mutates `readOnlyRootFilesystem=false` before validation. A tightened rule and the default cage contradict. The ladder must say which wins, or price it.

## Facts found (2026-08-28, AFK, before any question to the owner)

Source of truth is `.estate-clone/`. Paths below are relative to it.

- The ladder today is `baseline, restricted, quarantine` (`platform/graded/cage.py:86`). `deny` is a fourth value `select_tier` returns but is never a label. It becomes a GitHub issue (`platform/wargamer/wargamer.py:216-222`).
- `platform/graded/policies/cage-tier.yaml:61-69`: the MutatingPolicy matches only pods that claim a `policy-version`. A missing or unknown `posture.acme.io/tier` falls to `baseline`, the loosest tier. The file's own comment says the opposite (H8-03). Nothing in the policy denies.
- The mutation writes `readOnlyRootFilesystem` and `runAsNonRoot` to `harden == 'true'` on every container (`cage-tier.yaml:99-100`). At `baseline` that writes `false` over a pod that set `true`. All three adopter pods set `readOnlyRootFilesystem: true` in `deploy/pod.yaml`. `require-nonroot` 3.0.0 (`platform/distribution/policies/v3.0.0/require-nonroot.yaml:29-35`, `Audit`) then fails both checks. That is the ticket 03 contradiction.
- Governed-namespace deny: `governed-namespace-requires-claim`, `Audit`, `CREATE` only, in `platform/distribution/versions.yaml` and `render-governed-namespace-guard.py:46-77`, copied into each adopter's `composed/`. ADR-0014. Reversals 11 and 12 replace it.
- `cage_engine.py` Track 2 compares dial tables per tier under a partial order over six fields. `UNCAGED` is the top of the lattice. No floor concept exists there.
- `graded/cage.py` selects the first tier whose caged residual is under `tolerance`. Ticket 08 moved tolerance onto `party.yaml` as `appetite` and made selection a versioned `selection-policy` package. `reduce` and `cost` per tier are calibration knobs (0.30/0.70/0.92 and £500/£2000/£6000).
- The tier is written nowhere automatically. `tier_pr.py` edits the pod label in the adopter's manifest by regex. `compose/composition.py:1966-1990` asserts that composition writes no tier and no floor. Reversal 13 reverses that assertion.
- `party.yaml` on all three adopters: `overlay: {add: [], restate: []}`. No `tier`, no floor key, anywhere. No pod in the estate carries a tier label.
- `access/access.py` is a static `OP_TIER` table over `oidc, webauthn, device_svid`. `break-glass/break-glass.py` replaces it with one global `assurance-bands.json` and a `CAGE` rung for a stale device. Three encodings, none authoritative (H8-12), none per org (H8-09).
- Quarantine is `100m/64Mi`, drop ALL, read-only root, heavy WAF, `cage-quarantine` priority class ("first to be evicted, the hardest cage short of Deny").
- Live cluster carries `cage-tier-1-0-0` and `cage-tier-2-0-0` only. `cage-tier-2-0-1` and `require-nonroot-3-0-0` are absent. The "caged by degree" beat FAILs (`evidence/LIVE_RESULTS.json`).
- ADR-0018 makes the Namespace manifest the governed declaration. That is the natural place to render the tier down to.

Already decided, not re-asked: refuse total removal, price loosening short of removal (re-grill 16); attach the £ of every computed move to the evidence (re-grill 15); the overlay carries a tighten-only floor (re-grill 23); strictest cage at CREATE for a pod that claims nothing, infra claims an infra cage (re-grill 28, reversals 11 and 12); the composed artefact declares the tier and the proposer edits the declaration (reversal 13); a bottom rung below quarantine and unknown tier fails closed to strictest (reversal 17).

## Grilling round 1 — drafted 2026-08-28, HELD

Tickets 04, 07 and 08 spent today's five-decision budget. This round goes to the owner on the next day the owner opens the map. Five questions. Nothing below has been put to the owner.

❓ **Q1** - **Which wins, the tightened rule or the cage default**: `require-nonroot` 3.0.0 wants `readOnlyRootFilesystem` and `runAsNonRoot` true. The baseline cage writes them false over a pod that set them true. Options: (a) the cage mutation is tighten-only, it never writes a security field looser than the pod already declared; (b) the cage wins and the rule is priced as a hole at baseline; (c) the rule wins and baseline gains `harden: true`.

➡️ (a). A cage is a floor on the workload, not a ceiling. `harden` at baseline becomes "leave the pod's own value". The engine's partial order already treats the pod's own stricter value as inside the cage. No price, no contradiction, one CEL change. (c) collapses baseline into restricted and makes the ladder two rungs.

❓ **Q2** - **The bottom rung, concretely**: reversal 17 adds a rung below quarantine, "too expensive to run or not functional". What does a pod in it look like on the cluster? Options: (a) quarantine dials plus a default-deny NetworkPolicy on ingress and egress and the lowest priority class, so it runs but reaches nothing and is evicted first; (b) `replicas: 0` written by the proposer, so it does not run; (c) the same as (a) with no eviction.

➡️ (a), named `isolated`. It keeps "everything runs, everything is caged" true on the cluster, it is a Flux-reconciled spec like every other rung, and "not functional" is literally true. (b) is a refusal with a different name. The label value space becomes `baseline, restricted, quarantine, isolated, infra`. `select_tier` returns `isolated` where it returned `deny`.

❓ **Q3** - **Where the declared tier lives on the cluster**: reversal 13 says the composed artefact declares the tier and it renders down to the label. The cluster must read the declaration to clobber a forged label. Options: (a) render the tier onto the governed Namespace as `posture.acme.io/tier` (ADR-0018 already makes the Namespace the governed declaration), and the MutatingPolicy copies it onto every pod, overwriting whatever the pod carries; (b) a per-adopter ConfigMap the policy reads via a parameter resource; (c) keep the pod label as the source and add a ValidatingPolicy that denies a looser value than the last proposal PR.

➡️ (a). One declaration, one rendering, already signed and already reconciled by Flux. The pod label becomes an output only, so H8-03 closes with no new object. A pod in a governed namespace with no Namespace tier fails closed to `isolated`. The validating deny of an unentitled tier is then a Namespace-level check at compose time, not an admission check.

❓ **Q4** - **The floor's shape**: re-grill 23 says the overlay carries a tighten-only floor. Options: (a) `overlay.floor: <tier>` on `party.yaml`, per adopter, one value; (b) per-namespace floors; (c) a floor per control family.

➡️ (a) for the thin slice. The selection policy clamps to `max(selected, floor)` in ladder order. Compose refuses a floor looser than the adopter's previous floor unless the PR carries a priced delta (re-grill 16 applied to the floor). Per-namespace floors are fog until an adopter needs two.

❓ **Q5** - **Who may claim the infra cage**: re-grill 28 says infrastructure claims an infra cage explicitly. Options: (a) a hub-signed allowlist of infra namespaces rendered from `versions.yaml`; any pod outside it that claims `infra` is clobbered to `isolated`; (b) any pod may claim `infra` and the claim is priced; (c) infra is a `party.yaml` role and the platform party's own composed artefact declares its namespaces.

➡️ (c). Infra is just another adopter whose composed artefact declares its namespaces at tier `infra`. The same Q3 rendering covers it, so there is one mechanism and no allowlist file. (a) is a second declaration path. (b) makes infra forgeable.

Later rounds, blocked on the above: the warn rung (realise as `Audit` findings that move nothing, or drop the word); de-posture as a tier move that keeps the claim (H2-12); `access.py` retirement and break-glass bands per org appetite (H8-09, H8-12); how a tier move prices against the ticket 08 `prices[]` entry.

## Facts found, second pass (2026-08-28, AFK, owner asked for AFK work)

- The cluster runs Kyverno v1.18.2 (read live, `kubectl get deploy -n kyverno`).
- `platform/graded/policies/cage-netpol.yaml` is a GeneratingPolicy that already exists. It fires on `posture.acme.io/caged: "true"` and generates one NetworkPolicy per namespace that limits every caged pod to egress DNS only. The cage-tier mutation stamps `caged: "true"` at every tier, so a baseline pod loses reach today the same as a quarantine pod. Reach is not tier-aware. This changes Q2: the bottom rung does not need a new NetworkPolicy mechanism, it needs `cage-netpol` to read the tier and generate per-tier reach (baseline: normal egress; quarantine: DNS only; isolated: none).
- `platform/distribution/render-governed-namespace-guard.py:20-29`: Kyverno's CEL `namespaceObject` and `matchConstraints.namespaceSelector` work at runtime but do not evaluate in the pinned offline CLI (kyverno/kyverno#9975, #13605, confirmed on 1.18.2). The truth surface grades offline first. So Q3 option (a), "the mutation reads the Namespace label", is not provable by `verify-all.sh` today. New option (d) for Q3: the composition renders the declared tier into the adopter's own copy of `cage-tier` as a CEL map `namespace → tier` baked at compose time. That copy is signed with the composed artefact, reconciled by Flux, and fully testable offline with `kyverno test`. The pod label stays an output. The cost is that a tier move re-renders a policy file, which is already how every other composed policy moves.
- Offline coverage today: `platform/graded/tests/cage-tier/kyverno-test.yaml` asserts mutation into each tier and that a claiming pod with no tier lands in baseline. The Q1 fix and the Q3 option (d) map both fit this test shape.

Recommendation change: Q3 recommended answer becomes (d). Q2 recommended answer names `cage-netpol` as the reach half of `isolated`. Docs research on the remaining Kyverno facts is in `research/kyverno-1.18-cage-facts.md` when it lands.

## Facts found, third pass: Kyverno docs research (2026-08-28, AFK)

Full findings with citations: [research/kyverno-1.18-cage-facts.md](../research/kyverno-1.18-cage-facts.md).

- The estate's note that `namespaceObject` cannot evaluate offline is stale. kyverno/kyverno#9975 closed in 1.12.1 and #13605 closed in 1.15.0. In the 1.18 CLI, `kyverno test` resolves `namespaceObject` and `namespaceSelector` from the values file (`namespaces:` full objects, or `namespaceSelector:` name plus labels). A `kind: Namespace` in `--resource` does not work. So Q3 option (a) is offline-provable after all, at the cost of one values file per test.
- `namespaceObject` in MutatingPolicy landed in 1.18.0. It is nil for cluster-scoped requests, so expressions need a null guard.
- Tighten-only mutation is expressible. ApplyConfiguration that only ever writes `true` is tighten-only by construction. A JSONPatch idiom is filter with `?.`/`orValue(false)` then patch. Q1 option (a) is real. The snippets in the research file are unexecuted.
- Kubernetes runs every mutating webhook before every validating webhook. So `require-nonroot` always sees the caged pod. Q1 cannot be solved by ordering. Order among MutatingPolicies is not guaranteed.
- A GeneratingPolicy can branch on a label value in CEL. With `synchronize`, a trigger UPDATE deletes the downstream then regenerates, with a brief gap. Per-tier reach from one `cage-netpol` is possible. The gap is a fact to name in the Q2 answer.
- No `paramKind`/`params` on MutatingPolicy or ValidatingPolicy in 1.18. Q3 option (b), a ConfigMap parameter, is out. `variables` plus `--context-file` is the substitute.
- The live cluster serves `policies.kyverno.io/v1`, `v1alpha1` and `v1beta1` (read live 2026-08-28). The estate's 85 `v1alpha1` policies still load. A move to `v1beta1` is a separate housekeeping item, not this ticket.

Round 1 stands with these amendments: Q1 recommendation (a) confirmed expressible. Q2 names `cage-netpol` as the reach half and names the synchronize gap. Q3 options are now (a) Namespace label read via `namespaceObject`, provable offline via the values file, or (d) tier baked into the adopter's rendered policy at compose time; (b) is removed. Recommendation stays (d): it needs no values-file plumbing in 56 verify scripts, and a tier move is already a rendered-policy change. (a) is the fallback if the owner wants one policy file across adopters.
