# Standards review — 2026-10-03

Baseline: hub `4c3ed061f5837281ac9b07c3bb0a6de3c5620063`, including the requested new verification files and actual platform/feeds/adopter working diffs. Generated corpus, user-owned skills/workflows and pitch artifacts were excluded. Filesystem-only review; no network calls.

## Hard standards

One concrete finding was raised and closed: skipped, tolerated or filtered pull-request gates could derive zero proposal reach. The reviewed readers were `verify/pound-seam/pound_seam.py:760` / `:791` and `.estate-clone/platform/compose/composition.py:4175` / `:4208`. This violated NORTH-STAR's observed-true/false/could-not-look contract. Independent temporary fixtures confirmed that the corrected job/step `if: false` and `continue-on-error: true` cases now produce an unknown instead of a closed path, while preserving the unconditional baseline. A follow-up caught `paths: [docs/**]` and `types: [opened]` still being accepted. Root's final checkpoint confirms trigger filters are now closed too, with the focused selfcheck/regression evidence passing. That final filter closure is root-reported evidence; no additional shell recheck was performed after the request to stop commands.

## Smells — judgement calls

No additional actionable baseline smells. The independent composition and seam arithmetic/readers deliberately repeat derivations, and adopter-local instruments deliberately travel with each repository; the repository's independent proof and loose-coupling rules justify these copies. Existing large modules alone were not counted as new findings. No cosmetic or tool-enforced issues reported.

No remaining reported hard findings; no smell findings. Root's final focused checkpoint reports 154 passes and 8 skips; existing unavailable live instruments remain named skips rather than observed passes.
