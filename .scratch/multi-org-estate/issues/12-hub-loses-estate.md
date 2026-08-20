# 12 — Delete estate/ from the hub and rewrite the docs it invalidates

Type: task
Status: open
Blocked by: 09, 11

## Question

Complete the split: the hub stops holding the estate, so the six orgs are unambiguously the source of
truth rather than a mirror of a monorepo.

Includes: removing `estate/` from the hub; whatever `clone-estate.sh` / cross-org verify arrangement
ticket 07 settled; and rewriting the docs this makes false —

- `estate/talk/RUNBOOK.md`'s **"There is no venue-Wi-Fi dependency in any [LIVE] beat"** guarantee and
  its offline-safety section (the constraint is now explicitly abandoned, so this must be deleted and
  said plainly, not quietly dropped);
- `estate/README.md`'s "monorepo-style working tree ... becomes its own GitHub repo at split" framing,
  which describes a state that no longer exists;
- `estate/ARCHIVE.md`, whose checklist assumes the old shape;
- any `$ROOT/estate/...` path assumption left in the bring-up and verify scripts.

Run `verify-all.sh --live` from the new arrangement and confirm the count is unchanged from ticket 11.
