# Local drift lane verification, 2026-10-03

- All three `drift/five-facts.py selfcheck` commands pass, including stale cage-registration and three-null source/cage grading cases.
- New `served_apps.py selfcheck` and `oscal_lane.py selfcheck` pass in all three adopters. Their behavior slices were red before implementation.
- All three public `verify-cage-probe.sh` scripts pass using the checksum-verified Kyverno1.18.2 binary at `/private/tmp/pavf-kyverno-engines/1.18.2/kyverno`, both at signed v3.0.0 and at HEAD. These are served-document proofs, not cluster behavior evidence.
- `tests/test_cage_ladder_holes.py`: 34 passed with the verified1.18.2 binary on PATH. Initial run on the Homebrew1.19.1 CLI had24 passes/10skips; the correct-engine rerun removes those skips.
- Mypy with `--ignore-missing-imports --follow-imports=skip --check-untyped-defs` reports no issues in both new lane modules.
- Named hub workload/OSCAL checks exercise their public selfchecks and correctly return3 with no scheduled new-instrument observations. The manifest declares that concrete rollout wait. No lane sample was invented.
- Patches pass git whitespace checking and include new adopter files, bundled-source deletion, manifest/pin/manager changes, and the recovered161work.

Full suite, independent review, external rollout and post-change scheduled proof remain integrator work.
