# 76 — Every green rests on an observation

Type: task (AFK)
Status: open
Blocked by: none

## Question

Fourteen findings in the 2026-09-02 review share one root cause: a check reaches exit 0 from a path where the property was never observed. Close every one, and add a selfcheck to each so the class cannot return. The list:

1. Seven scripts under `platform/computed-semver/` print `SKIP:` and exit 0 when kyverno is absent: `verify-cage-engine.sh`, `verify-comparison-window.sh`, `verify-gate.sh`, `verify-rederive-bumps.sh`, `verify-generator-standing-check.sh`, and step 3 of `verify-corpus-generator.sh` and step 5 of `verify-witness-set.sh`. Exit 3.
2. `verify/provenance/verify-provenance.sh` and `verify/proportionality/verify-proportionality.sh` have no exit-3 path for their live tails and assert PASS after printing a note. Add one.
3. `verify/e2e/verify-e2e-step6-provenance.sh:88` selects tags with `git tag -l 'v*.*.*'`, which cannot match feeds' `threat-register/v2.0.0`, and prints "no signed tag yet" about a Rekor-validated publisher. Resolve each unit's tag shape from its own `publishes[]`, verify the newest tag per published line, and never print an absence that was inferred from a failed lookup.
4. `verify/e2e/verify-e2e-step5-twin-forecasts.sh` grades path existence and passes in the same run in which driftwood's twin-overlay and twin-scenarios checks fail on the same file. Step 5 must consume those verdicts, or run `emit-forward-intel.py --check` itself, and exit 3 naming ticket 72 until a dated sweep observation exists.
5. `driftwood/drift/five-facts.py:522-528` records `fired: false` for a falsifier that was never run. Carry `None` through so the grader's could-not-look branch fires.
6. `platform/wargamer/wargamer.py:200,232` hardcode `"signed": True` and `:324` asserts the literal. Derive the field from the commit or delete it. The signing itself is ticket 78.
7. `verify/twin-evals/verify-twin-evals.sh` scores seven heuristics at 1.000 against a baseline recorded once, and the evolution-judge eval scores a lookup table against its own values. Hold out a corpus the heuristics were not fitted on, or relabel the seven on the surface as harness-mechanism checks.
8. The five-fact sample prints fact 3 for the two publishers as three independent proofs when it is one chain. Say so in the capture text.

Done = each of the eight has a failing-before test or selfcheck, the TRUTH line moves by the honest amount, and no capture on the next citable run prints a green sentence about something the script did not observe.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R3. Findings: truth-surface/TS-C1, engineering/EQ-02, principles/P6-1, P6-2, P7-1, P5-3 (literal half), demo-steps/DS-F1, DS-F4, operability/O3, scope/F5, truth-surface/TS-M8, twin/TWIN-06, TWIN-07, security/SS-08 (literal half). The correct pattern already exists in `distribution/verify-render-version-tree.sh`. Items 1 and 2 were ticket 55's class and escaped it.
