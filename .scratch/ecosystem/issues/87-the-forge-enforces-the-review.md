# 87 — The forge enforces the review

Type: task (HITL)
Status: open
Blocked by: 75

## Question

Principles 4 and 5 say policy is bumped only by reviewed PR and a human merges. Nothing on GitHub enforces either. Zero rulesets, zero branch protection, zero tag protection on all nine repositories, verified live. Every merged PR in the estate has author equal to merger. Every identity pin accepts a tag signed from `release/<M>.<m>.x`, platform has such a branch, and nothing guards it. Anyone with push access can rewrite `cut-release.yml`, push it unreviewed, dispatch it, and produce a tag every consumer accepts. The 2022 org still has tag protection; the successor has none.

Under ticket 75 Q6:

1. If it binds: apply a ruleset on `main` and `release/*.x` in all nine repos requiring a pull request and one approving review from an identity other than the author, plus tag protection matching each repo's release pattern. Name the second identity. Add an assertion to the identity-regexp verify family that every branch the accepted pattern admits is protected, so the pin and the protection cannot drift apart.
2. If it does not bind for this build: record the single-operator state in NORTH-STAR §6, and stop presenting principle 5 as enforced.
3. Either way: `twin/ENACT_MODE` is a file the agent writes. Replace it with a declaration in a repo the agent cannot push to, with a price attached, or record why not.

Done = `gh api repos/<org>/<repo>/rulesets` is non-empty on nine repos and the verify family asserts it, or §6 carries the dated decision.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R9. Findings: security/SS-04, SS-05, scope/F8, engineering/EQ-08. Ticket 65 (the `--git-dir` hole) is the guard's own half. Ticket 74's definition of done cannot be written until Q6 is answered.
