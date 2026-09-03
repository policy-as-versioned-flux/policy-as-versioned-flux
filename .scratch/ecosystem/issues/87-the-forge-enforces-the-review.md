# 87 — The forge enforces the review

Type: task (HITL)
Status: open
Blocked by: 88

## Question

Principles 4 and 5 say policy is bumped only by reviewed PR and a human merges. Nothing on GitHub enforces either. Zero rulesets, zero branch protection, zero tag protection on all nine repositories, verified live. Every merged PR in the estate has author equal to merger. Every identity pin accepts a tag signed from `release/<M>.<m>.x`, platform has such a branch, and nothing guards it. Anyone with push access can rewrite `cut-release.yml`, push it unreviewed, dispatch it, and produce a tag every consumer accepts. The 2022 org still has tag protection; the successor has none.

Under ticket 75 Q6:

1. If it binds: apply a ruleset on `main` and `release/*.x` in all nine repos requiring a pull request and one approving review from an identity other than the author, plus tag protection matching each repo's release pattern. Name the second identity. Add an assertion to the identity-regexp verify family that every branch the accepted pattern admits is protected, so the pin and the protection cannot drift apart.
2. If it does not bind for this build: record the single-operator state in NORTH-STAR §6, and stop presenting principle 5 as enforced.
3. Either way: `twin/ENACT_MODE` is a file the agent writes. Replace it with a declaration in a repo the agent cannot push to, with a price attached, or record why not.

Done = `gh api repos/<org>/<repo>/rulesets` is non-empty on nine repos and the verify family asserts it, or §6 carries the dated decision.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R9. Findings: security/SS-04, SS-05, scope/F8, engineering/EQ-08. Ticket 65 (the `--git-dir` hole) is the guard's own half. Ticket 74's definition of done cannot be written until Q6 is answered.

## Comments

**2026-09-02, ticket 75 resolved.** Q6 is (a), owner-reasoned: principle 5 binds for the demonstration. Item 1 applies. The second identity is the machine identity ticket 88 creates for the assistant, which reviews and merges during the development window while the owner authors and pushes (the owner's word: theatre). Item 3: `twin/ENACT_MODE` flips to `development` only after ticket 88 lands, with a dated docstring line; the declaration the agent cannot write is the ruleset itself, which requires the second identity's review. Blocked by 88 now, not 75.

**2026-09-03, ticket 88 resolved.** The second identity is the GitHub App `pavc-other-hand` (App ID 4819564), installed on all nine orgs. Item 1's ruleset requires one approving review from an identity other than the author; the app's review counts as that identity. Item 3: `twin/ENACT_MODE` reads `other-hand`, and the admitted merge shape is one that mints the app's token inline; the declaration the agent cannot write is the ruleset itself. Unblocked.
