---
status: accepted
---

# Release gate: compute the bump, refuse a weaker declaration, no override

> **Superseding note, 2026-08-29 (ticket 43, ticket 18 Answer 1).** Two sentences below are
> narrowed, nothing else changes.
> 1. "Neither ever rewrites the declared number" becomes **never rewrites the declared BASE
>    number**. A publish whose declared bump is weaker than the computed one is published
>    DEGRADED: the base number is untouched and a prerelease suffix is appended
>    (`policy/v4.0.1-quarantine.1`), which sorts below the clean number. The version string is
>    the one thing every consumer reads, so it says what happened.
> 2. "Both gates refuse a declared bump weaker than the computed one" becomes **publish it
>    degraded**. Weaker-than-computed is a read-and-priced behaviour, not an instrument fault
>    (ADR-0020): the gate read everything it needed. The array element carries
>    `tier: quarantine` as a signed fact and the ADOPTER prices it under its own perspective;
>    the publisher sets no floor in anyone else's repository (NORTH-STAR §2). Nothing is
>    refused, everything is caged.
>
> Unchanged: the declared bump is now DECLARED, in the reviewed `versions.yaml` array element
> (`bump:`) or ico/nist's `bump.yaml`, not derived from the tag arithmetic — and a declaration
> that disagrees with the step the number takes still refuses, because the gate then has two
> declarations of one fact and no rule for choosing between them.

Two gates evaluate every policy bump against a corpus of workloads and derive **major / minor /
patch** from observed verdict movement, rather than trusting the number a human typed into the
release workflow. The **publisher gate** runs inside `cut-release.yml`, before `git tag`: it
evaluates the candidate policy set and every supported lower version against a generated corpus,
observes how the cage spec each pod receives moves between versions, and derives the bump from that
movement. The **adopter gate** runs inside each institution's `shift-left.yml`, on the Renovate bump
pull request: it does not recompute the publisher's answer — a second answer to the same question has
no tie-breaker — but verifies the publisher's signed evidence against an identity the institution
holds itself, then computes that institution's own composed bump across every party it consumes. Both
gates **refuse a declared bump weaker than the computed one and permit a stronger one**; neither ever
rewrites the declared number. We chose this over trusting the declared bump, even though a human
typed it in good faith, because `CONTEXT.md`'s major/minor/patch definitions already describe verdict
movement on currently-compliant workloads, and nothing before this gate ever tested that the declared
number matched what actually moved — the faithful-floor release line shipped two version-mechanics
mistakes found by review, twice, not by CI.

## Considered options

- **Compute the bump from observed movement and refuse a weaker declaration (chosen).** The gate
  evaluates the candidate against a generated corpus, observes how the cage spec each pod receives
  moves between versions, and derives the bump `CONTEXT.md` already defines. A declared bump weaker
  than computed refuses the release; a stronger one is permitted and the discrepancy is printed. The
  gate always emits and signs its evidence, including when it refuses.
- **Trust the declared bump, test it after the fact (rejected — status quo).** A human types the
  number, then authors a fixture that agrees with it. That is post-hoc justification, not derivation,
  and it already missed version-mechanics gaps that only review caught, not CI.
- **Compute the bump and rewrite the declared number (rejected).** Would remove the human's editorial
  judgement entirely, and let a corpus with an unstated coverage hole silently set the wrong number
  with no review point to catch it. The gate refuses; it never rewrites.
- **Allow an override at some scope (rejected).** See "No override", below.

## No override

There is no override, at any scope, for anyone. `CONTEXT.md` already bans exemptions — a carve-out
for a named workload — at any scope, under any name. An override on this gate is the same shape
wearing a different label: evidence, a signature and an expiry attached to a decision to admit
something the rule would otherwise refuse. That is the exemptions ledger this estate already deleted
(`.scratch/govern-what-you-dont-control/issues/05-remove-the-exemption-ledger.md`). The only relief
valve is over-declaring — a publisher may always ship a stronger bump than the gate computed — and any
disagreement with the computed bump is resolved by a reviewed pull request to the generator or the
policy, exactly as `CONTEXT.md` already requires for changing what gets enforced.

## Consequences

- **[ADR-0002](0002-adoption-pinned-plus-renovate-pr.md) gains evidence, not a new gate.** ADR-0002
  already makes the reviewed pull request the only way a new version lands; before this gate, the
  reviewer approved a version string and a diff with no way to see which workloads changed verdict.
  This gate's signed evidence — verified by the adopter gate against its own held identity — is what
  the reviewer now reads alongside the diff. Neither gate weakens or bypasses the reviewed-PR
  requirement; the review is still where a disagreement with the computed bump gets resolved.
- **A refusal is signed too.** The gate emits and signs its evidence on refusal as well as on success —
  a refusal is the most valuable output it produces, not a silent dead end.
- **The publisher gate runs before `git tag`.** The release workflow refuses to move a tag once cut, so
  a late refusal would burn a version number; this gate has to run, and refuse, before that point.
- **The adopter gate does not recompute the publisher's answer.** It verifies the publisher's signed
  evidence against an identity the institution holds itself, then computes its own composed bump
  across every party it consumes — a second, independent recomputation of the same question would have
  no tie-breaker against the publisher's.
- **A coverage hole is grounds for a reviewed PR, never for an override.** The gate states what it
  didn't reach; it does not let an unreached case become a reason to bypass the rule.

## Note, 2026-09-05 (eco-system ticket 99: the adopter gate grades the change, not the window)

"Computes that institution's own composed bump" was read two ways by three adopters, and only one
can be the estate's. **The fold's subject is the DELTA the pull request makes to the institution's
composed window — the versions it adds and the versions it retires — never the whole window it
leaves standing** (delegated, ADR-0025). driftwood and ludlow already read it that way; tuppence
folded its whole supported window and was changed to match.

Four reasons, in order of weight. This gate runs "on the Renovate bump pull request" and computes
that institution's own *bump*, and a bump is a movement — tuppence reported `major` for a pull
request whose declared bump was `none`, because its pin did not move, so it was answering a question
about the window rather than about the change in front of it. The refusal it raised named a remedy
the gate has no input for: no flag records a review and no other path exists past the composed-major
line, and a refusal that cannot be satisfied is not strict, it is non-terminating. A check that
fails on every pull request has stopped discriminating — tuppence's last green `shift-left` was
2026-08-28 and it then failed twelve consecutive times. And two of three adopters were green on the
same platform tag and the same signed evidence.

**This is not the override "No override" bans.** Nothing is exempted and no refusal is weakened for
any subject: a composed major still refuses, a retirement is still a forced major, and an added
version's own signed evidence is still verified against the institution's own held identity and
re-read rather than recomputed. The gate is pointed at the question this ADR asks it.

**What the reading gives up, named.** A version standing at both ends of a pull request is not
folded, so on that pull request nothing re-verifies its signature. Measured, not argued: with
platform's `4.0.0.json.bundle` corrupted at a fresh tag and both folds run over identical inputs,
the window fold refuses on a real cosign failure and the delta fold adopts. driftwood and ludlow
have always had this property; tuppence now shares it. The class is not dropped, it is moved off the
pull request and onto the clock: `verify/unreviewed-major/verify-unreviewed-major-in-window.sh`
verifies every version in every adopter's composed window, with real cosign, at the tag that adopter
pins, on every truth-surface run, and reports one that does not verify as observed false. A window
verified only when somebody opens a pull request is verified less often than one verified daily.

The property the window fold was protecting — an institution should not quietly carry a major
nobody reviewed — is real, and survives as a report rather than a refusal, because the fact does not
depend on anyone opening a pull request. `verify/unreviewed-major/verify-unreviewed-major-in-window.sh`
names every major standing in an adopter's composed window on every truth-surface run, read from
that adopter's own composed artefact and from platform's signed evidence at the tag that adopter
pins. It records no review and invents none: disposing of a carried major is an owner authorisation
under ADR-0025. That the three adopters answer this ADR alike is itself graded, on planted
movements, by `verify/fold-agreement/verify-fold-agreement.sh`.

## Note, 2026-09-03 (ticket 53: the signed evidence reaches the branch, or nothing lands)

The consequence above says the publisher gate runs before `git tag`. It also commits its signed
evidence (`computed-semver/evidence/N.json` and the cosign `N.json.bundle`) onto the checked-out
branch before the tag is cut. On 2026-08-31 the push carried the tags alone, so those commits were
reachable only from the tag; `main` kept `4.0.0.json` without its bundle, platform `v2.0.0` was cut
from that `main` minutes later, and every adopter pinned to it refused, correctly.

Decided and enacted by the owner on 2026-08-31 (platform `b83eba1`, owner-instructed): the branch
is pushed in the same `--atomic` push as the tags, `HEAD:refs/heads/<branch>` beside `"${tags[@]}"`,
so either the evidence and every tag land or none of them do. The alternative, landing the evidence
by a reviewed pull request while the release pushes tags only, was not taken: the evidence is the
gate's own output for a tag that already exists, there is nothing for a reviewer to dispose of, and
a window in which a tag exists whose evidence `main` lacks is exactly the defect. A detached HEAD is
refused before anything is pushed.

Recovery of the orphaned commits (`64635df`, `1d8cec2`, signed on the `policy/v4.0.0` tag) was not
by cherry-pick, which would have put a second signature under a different identity on the same
content. The release bot re-committed the evidence onto `main` (`533dccb`, 2026-08-31T16:18Z), and
the `policy/v4.0.0` tag commit remains unreachable from `main` by design. That is the accepted state
and is not a hole to repair (delegated, ADR-0025). `v2.0.0` is immutable and keeps its hole; `v2.0.1`
is the first tag cut from a `main` that carries every bundle, and it is what the adopters pin.

Graded by platform `verify-cut-release-tags.sh` case 8 (the mechanism: branch and tags land together
or not at all, against a scratch remote) and by the hub's
`verify/provenance/verify-release-evidence-reaches-main.sh` (the outcome: every evidence document on
platform `origin/main` and on each adopter's pinned tag has its bundle, and the push line is the
atomic one).
