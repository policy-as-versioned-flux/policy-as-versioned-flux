# Engine implementation prepared 2026-10-03

Platform base: `cb680f22eb46b0fab5e56844758242a2ab200975`.

`platform-engine.patch` contains the engine lane. The twin lane's platform patch must supply
its complete composer (recovered148 plus145). No signed tags or remote writes were made.

Ticket158 and159(a) declare the uncut6.0.0 candidate. The security fixture first failed
pod-nonroot-baseline and ungoverned-baseline (16 passed/2 failed), then passed18/0 on1.18.2.
The pod runAsNonRoot default now falls back to its pod securityContext. The tier is read only
from a Namespace carrying governed=true; all other claiming Namespaces fall to isolated.
The existing5.0.0 tree is unchanged.

Ticket149 declares the following uncut6.0.1 candidate: v1 policies, string-typed tier output,
a generated-document fixture including an uncaged restricted trigger, and retirement of
posture-trust-boundary from that candidate's tree. Historical5.0.0 and security6.0.0 retain their
own Deny and bytes. Generator tests first produced four false passes (each removed gate on
each engine); after the grader included document comparison, all four mutations correctly
failed their grade. The real fixture remains green on both engines.

Measured:

- Engine matrix: six supported cells passed, including both machinery engines and both6.0.1 engines.
- Three-declared-version require-nonroot fixture:45 assertions passed.
- Grader unit tests:23 passed; engine pairing unit tests:13 passed.
- The generation gate integration proof passed on1.18.2 and1.19.1.
- Renderer and every machinery twin selfcheck passed; kubectl kustomize built all declared trees.
- cage_engine and corpus_generator selfchecks passed. The current pairwise corpus has180 entries.
- Full generated pairwise comparisons:5.0.0 ->6.0.0 computesmajor;6.0.0 ->6.0.1 computespatch.
- Shift-left verification passed on1.18.2. It now observes whether the historical flip fixture
  actually changes validation verdicts, and explicitly uses its planted4/5 window when the
  current served window is all-pass for that fixture. An unavailable instrument or target
  failure stays on the served path and remains red.
- Hub mypy passed during development; engine-pairing's own mypy passed.
- Currency controller offline proofs passed; its live tail skipped because Docker was not reachable
  at that point. This is not a live admission or rollout result.

`engine-cells.json` records a temporary local unsigned candidate snapshot, with the real tagged
5.0.0 bytes and candidate6.0.0/6.0.1 bytes. `computed-bumps-generated.json` records complete
pairwise-spine comparisons, not signed release evidence or the complete release gate.

Release order: cut6.0.0, then6.0.1. The first is a major and each institution requires its owner's
written acceptance before adoption. Against current cut5.0.0, a direct6.0.1 comparison is major;
the patch classification assumes6.0.0 became the base first. Tools release, adopter recomposes,
composed tag moves and citable scheduled/live observations remain owner/deployment steps.
Tickets148,149,150,158 and159 are not resolved by this preparation.

Update, 2026-10-03: the owner delegated the institution decisions to this implementing assistant
with "you tell me, you control them all, you don't need me to answer". Exact 6.0.0 and 6.0.1
acceptance records are prepared for all three adopters. These decisions no longer wait on an
owner answer. Publication and pin moves remain unperformed; network permission was revoked.
The 1.19.1 upgrade rehearsal's retained-policy fail-open measurement is recorded separately
under research/resume-2026-10-03/engine-150-admission/upgrade/measurement.json.
