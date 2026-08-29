# 43 — The first gate-determined release (H9-04)

Type: task (AFK)
Status: resolved
Blocked by: 16, 21, 25

## Question

Cut one policy release whose number the gate determines before the tag: change one CEL predicate so admission movement is real, read the bump from the array element, produce evidence in the pre-tag run, sign with the gitsign tag, commit E then tag E then array A on main, wire tag-commit == array-commit into talk/verify-all.sh, and decide the 2.0.1 orphan (re-cut or record) on the day.

## Notes

Graduated 2026-08-28 from ticket 18's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. A degraded publish carries a prerelease suffix that sorts below the clean number, the declared bump lives on the array element or the one-key bump.yaml, and the gate refuses when computed and declared disagree. The adopter fills its own matrix row; the publisher matrix stays empty and says so. The release is proven end to end as a dry run; the verify script exits 3 naming the tag CI must cut, because a signature cannot be made locally.

Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it is the TRUTH line of 2026-08-29.
