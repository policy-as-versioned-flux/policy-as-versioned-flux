# governance-agent

Agent governance layer (ADR-0007, issue 23): spec + thin demonstrator.

[`SPEC.md`](SPEC.md) — signal ingestion, noise reduction, decision framing, PR/issue surfacing,
and the never-edits-enforcement invariant with its enforcement mechanism. **Correction (2026-07-18,
wave-1 audit)**: earlier drafts of this line and SPEC.md described the mechanism as a scoped
GitHub App token (`issues:write`/`contents:read`, 403-enforced) — no such App or scoped token was
ever actually set up anywhere in this estate; every write here runs on the same full-access
personal `gh` auth as everything else in the org. The real, verified guarantee is code-level: the
demonstrator's only writes are `gh issue create` and `gh label create` (repo metadata, not
enforcement content; grep-verified, no `git`/`gh pr` calls exist in the script at all — earlier
drafts said "only `gh issue create`", overlooking the label create, corrected 2026-07-20), the
same never-calls-the-forbidden-thing pattern
`sunset-escalator.sh`'s own header already states honestly. A token that also carried write
access *could* still call those endpoints directly — that residual is real, same as
`sunset-escalator.sh`'s own admission below.

The demonstrator (issue 24) is a separate, deliberately narrow implementation of one signal path
through this spec — see SPEC.md §6 for its exact scope.

## Sunset escalator (ticket 09, real-estate epic)

`sunset-escalator.sh` extends the same contract with sunset proximity as a second signal source
(ADR-0007's "external signals" alongside CVEs), watching `fleet`'s own `sunset:` dates (ADR-0010)
instead of `policy`'s rationale. Within `ESCALATION_WINDOW_DAYS` (default 30) of a version's
sunset date: an escalation issue against `fleet`, checkbox-framed like the demonstrator's. On or
after the date: a machine-opened retirement PR removing that array element — never merged by this
script (see the script's own header for the honest enforcement discussion: unlike the
demonstrator's code-level, single-write-path shape, opening a PR genuinely needs
`contents:write`+`pull-requests:write`, so what actually holds "never automerged" is the code
never calling `gh pr merge`, plus `fleet`'s org-wide `allow_auto_merge:false`, ADR-0010).

`DRY_RUN=true` prints without writing. `SUNSET_TODAY_OVERRIDE=YYYY-MM-DD` simulates a different
"today" — used to prove the retirement-PR path fires correctly without waiting for a real date to
arrive (see ticket 09's comments in the hub for the live proof: a real retirement PR opened
against a simulated post-sunset date, confirmed the cluster stayed untouched while it sat
unmerged, then closed once observed since the real date hadn't actually arrived).
