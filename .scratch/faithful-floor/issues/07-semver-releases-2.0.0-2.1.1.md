# 07 — Cut 2.0.0 + 2.1.1 releases exercising semver meaning

**What to build:** Make semver carry its defined meaning (CONTEXT "Policy version"): a **major** `2.0.0` whose change can fail a previously-compliant workload at the gate (e.g. free-text department label → enum), and a **patch/minor** `2.1.1` line whose passing set only grows or adds an Audit policy. Both released through the signed pipeline. This gives the estate ≥3 real versions for coexistence, and release notes that make version changes **communicable**.

**Blocked by:** 04 — Signed release pipeline.

**Status:** done

- [x] `2.0.0` contains a verdict-tightening change; a fixture compliant under `1.0.0` fails under `2.0.0`
- [x] `2.1.x` contains an addition/widening that cannot fail an existing compliant workload, with fixtures proving it
- [x] Every tag in the real release line gitsign-signed and CI-verified like `v1.0.0`
- [x] Release notes state what changed and why, per the semver-by-verdict-impact rule

## Comments

Done 2026-07-14, except the last box. `require-department-label` promoted Audit → Deny (major,
CONTEXT's own "Audit→Deny promotion" example) — live-proved: a pod missing `department`, pinned
to 2.0.0, was refused at admission (would have been admitted-but-reported under 1.0.x). New
`require-owner-annotation` (Audit, minor) + `require-known-department-label`'s known set widened
`+legal` (patch) at 2.1.1 — live-proved: a pod with `department: legal`, pinned to 2.1.1, was
admitted (refused under 2.0.1's narrower enum). `verify.sh` extended to also assert every policy
in the tree agrees on one version (a policy version covers the whole body).

Same signing-mistake-then-patch pattern as v1.0.0→v1.0.1 happened twice more, each caught by the
release pipeline's own CI gate rather than silently shipping:
- `v2.0.0` was accidentally SSH-signed (a global git-config default; the local override from
  issue 04 was lost when the repo clone was recreated after an earlier incident) →
  `gitsign verify-tag` failed in CI as designed → `v2.0.1` is the working major-2 release.
- `v2.1.1` shipped correctly, but then I found "release notes state what changed and why" wasn't
  actually true: `gh release create --generate-notes` alone only produces a commit-list changelog,
  not the semver-by-verdict-impact narrative written into the annotated tag message. Fixed
  `release.yml` to prepend `git tag -l --format='%(contents)'` to the release body — but proving
  it needs a new tag push, and cutting one (`v2.1.2`, prepared) hit an expired gitsign OAuth
  credential (the credential cache from issue 04 only holds a token for a limited window) mid-tag,
  right as the user had to step away and asked me to pause rather than retry blind. Left as the
  one open item; not silently skipped.

Root cause worth carrying forward (issue 11/12 territory): `gpg.format`/`gpg.x509.program` are
not scoped per git-object-type, so setting them locally to route *tag* signing through gitsign
also silently rerouted ordinary *commit* signing through gitsign's OIDC flow (the user's global
default is SSH commit signing, which needs no auth at all) -- caused a real 2-minute hang on a
plain `git commit`. Fixed by using inline `git -c gpg.format=x509 -c gpg.x509.program=gitsign
tag -s ...` for tag operations only, instead of persistent local config.

**2026-07-15, last box resolved without a new tag:** re-examined the actual gap instead of
assuming it required `v2.1.2`. The *tag* message for `v1.0.1`/`v2.0.1`/`v2.1.1` already carried
the correct semver-by-verdict-impact narrative (gitsign signs the tag object, narrative included
-- that part was never broken). What was actually wrong was narrower: the *GitHub Release* object
for each -- a separate, unsigned piece of metadata -- only had `gh release create`'s
auto-generated commit-list body, missing the narrative. That's editable directly
(`gh release edit --notes-file`) without touching the tag, the commit, or any signature. Rebuilt
each release's notes as tag-narrative + the existing verified-signature line (the exact shape
`release.yml`'s fix now produces for future tags) and pushed it live for all three real releases.
Verified by re-fetching each release body afterward: all three now state what changed and why.
No gitsign OAuth needed -- the fix didn't actually require one, only the earlier assumption that
"prove it" meant "cut a new tag" did.
