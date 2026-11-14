# distil: the mission as one loop

Status: nine of ten decisions answered on 2026-11-14 (`DECISIONS.md`); the tolerance figure is open

A read-only review of the whole estate, made on 2026-11-14 against one sentence from the owner:

> "quantified risk and a reactive ratcheting process cage to mitigate the quantified risk until the risk is within financial tolerance of the organisation"

The review itself built, ran, moved and removed nothing. The clean-up that followed it, on the owner's instruction, is recorded in `ARCHIVE.md`.

## Read in this order

| File | What it is |
|---|---|
| `DISTILLATION.md` | The report. Start with "The short version" at the top. |
| `DECISIONS.md` | The owner's answers to the ten decisions, quoted, and what each changes. Where it differs from the report, it wins. |
| `ARCHIVE.md` | What the clean-up of 2026-11-14 archived, and how to bring any of it back. |
| `LEDGER.md` | Every area of the nine repositories in 26 rows: what was proposed, what a second reader found, and the call. |
| `TARGET.md` | The distilled design in full. Superseded wherever `DISTILLATION.md` sections 5.6 and 7 or `LEDGER.md` differ; its section 16 lists where. |

## The working behind it

| Folder | What it holds |
|---|---|
| `maps/` | 26 maps, one per area, each with file and line citations. A1 to A5 cover the mission, H1 to H15 the hub, P1 to P3 the platform, D1 and D2 the adopters, F1 the publishers. |
| `FACTS.md` | The digest of the maps given to the designers. Its top block lists what the keystone checks later corrected. |
| `designs/` | Four independent designs of the smallest working loop. Three judges scored them: owner-words 130, first-principles 123, the-room 115, subtractive 102. |
| `keystones/` | Four attempts to refute the main findings. One finding was confirmed and three were corrected in part. |
| `verdicts/` | One second reading per ledger row, L01 to L26. Eight disagreed with the proposal. |
| `evidence/` | The commit of every repository before and after the review (identical), and the names of the 40 local branches that are in no remote history. |

## How it was made

Two passes of agents, all read-only:

1. **Map.** 26 readers mapped every area against the six steps of the loop.
2. **Design and check.** Four designers, four refuters, three judges, one integrator, 26 second readers, then a writer, a critic and a reviser.

## Paths in the citations

- `hub/…`, `platform/…`, `driftwood/…` and the like are paths in clones of the nine remote default branches taken on 2026-11-14. The commits are in `evidence/sha-snapshot-before.txt` under `fresh/`. The clones were temporary and are not kept here.
- `troy/.scratch/…` is planning text read from the owner's backup disk.

## Known gaps

`DISTILLATION.md` section 9 lists what the review did not establish. The main ones: nothing was run; nothing that needs the forge was checked, including open pull requests; and about 116 hub test files were counted but not read one by one.
