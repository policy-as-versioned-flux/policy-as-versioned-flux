# Recovered estate implementation snapshots

`complete/manifest.json` is the canonical final source export. Each of its nine patches names an exact base commit, byte count, SHA-256 and changed paths. `export_estate.py` rebuilds these snapshots using temporary indices, leaving the source repositories' actual indices unchanged. These are source implementation snapshots, not signed release receipts or live observations.

Stored patches and raw command captures preserve their exact bytes, including standard diff context markers and output formatting. The dated directories' attributes mark these formats as captures for whitespace checks. Actual source diffs are checked independently; patch hashes and applicability are verified separately.

Other patches and measurements preserve earlier review checkpoints. In particular, `platform-full-final7-working-tree.patch` records the platform source used to reconstruct the original security6 PR49 head `9ddd6a2`; subsequent narrowly tested composition fixes appear in separate patches and the canonical final export. The historical 6.0.1 corpus and dry runs are retained as measured: the actual complete publisher window superseded that release proposal with **7.0.0**.

`platform-release-order.md` describes the measured security6 intermediate, followed by compatibility7 and tools5. The transition must preserve the genuine policy6 metadata supplied by the existing Actions cut. Unsigned local rehearsals are explicitly labelled and cannot substitute for a release.

Real delivery records distinguish the four merged independent-app maintenance PRs and three published, verified adopter app-only v3.0.1 releases from foundation publication and stage2 rollout. The exact primary scanner proof and rollout prerequisites are in the sibling `../../research/resume-2026-10-03/` directory. The automatic merge-review stops for platform PR49 and feeds PR10 are preserved; no merge, release cut or indirect workaround follows from those rejected actions.
