# 106 — The composition selfcheck is red on main at the ungoverned-namespace leg

Type: bug
Status: open
Blocked by: none

## Question

`platform/compose/composition.py --selfcheck` is red on platform `origin/main` whenever the
estate's platform tree is also `origin/main`, and green only against the stale local clone. Fix
the leg without masking it, so `verify-composition.sh` (which runs the selfcheck) can go green on
the gate at the next refresh, and so the three price legs behind it execute again.

## Notes

Found by the 2026-09-08 review of ticket 34 (F-04) and measured by its builder the same day.

**Measured.** Platform `origin/main` = `30d104f`; every unit of the estate at its `origin/main`
(throwaway detached worktrees, so no local `main` was read):

    cd <platform@30d104f>/compose
    PAVC_ESTATE_CLONE=<estate@origin/main> python composition.py --selfcheck
    ...58 OK legs...
    File "compose/composition.py", line 5066, in selfcheck
        assert "acme" not in text, path
    AssertionError: composed/governed-namespace-guard.yaml
    exit=1

The reviewer measured the same assertion at `a270fce` (~line 4582) and, once that one is
skipped, the next on `composed/governed-namespace-holds.yaml` (~4588). Against the stale local
clone (`.estate-clone/platform` at local `main` = `bbda376`) the same selfcheck is green, which
is how it was cited green.

**Cause.** The ticket-15 leg plants an ungoverned namespace NAMED `acme`
(`_write_namespace(base, "acme", institution=True, governed=False)`, composition.py ~4988) and
then asserts that no file the engine reads carries the substring `"acme"` — the leg's claim is
that composition's own ungoverned-namespace bookkeeping never leaks into an applied object.
Since ticket 89 ("neither guard refuses; the unclaimed pod is caged", `553137f`, and ticket 91
`727ba39`, both under `git log bbda376..a270fce -- distribution graded`), the served
governed-namespace guard MUTATES: its expression stamps the labels
`posture.acme.io/caged: "true"` and `posture.acme.io/tier`. So the composed guard body carries
`acme` as the label PREFIX, and the substring assertion cannot tell the namespace name from the
label domain. It is a string collision in the fixture, not a leak.

**What it is not.** It is not evidence that the ungoverned set leaks into the guard: the
namespace name appears nowhere in the guard, only the `posture.acme.io/` prefix that every
served cage body has carried since ticket 26. Do not "fix" it by dropping the assertion or by
excluding the guard file from it: the leg exists to catch exactly a namespace name reaching an
applied object.

**Fix.** Rename the fixture namespace to something no label prefix in the estate contains
(`fixture-outside-the-cage`, say), and assert the NAME as a whole token rather than a substring
(`re.search(r"(?<![\w.-])acme(?![\w.-])", text)` or the renamed equivalent), so the leg stays a
leak detector and stops reading a label domain as a leak. Check the `holds` file the reviewer
named goes green for the same reason and not another. Red first: the current fixture against
the current guard is the red.

**Consequence until it lands.** `platform/compose/verify-composition.sh` line 23 runs
`composition.py --selfcheck`, so its manifest row (`estate-observation | waits: not on the real
remote until cut-release.yml cuts`) will FAIL, not SKIP, the first gate run after
`clone-estate.sh --refresh` moves the platform checkout onto current `origin/main` — regardless
of platform PR 18. Ticket 34's Answer no longer cites that script's SKIP as measured on main.
Three of the four paired handbook legs ticket 34 added (the three price legs, ~5398 onward) sit
behind this assertion and do not execute on current main; the untagged-pin and holes legs run
before it and do.

**Measured again 2026-09-08 (round-2 review of ticket 34, R2-04): the red is a cascade, not one
assertion, and the leg names one cause where the served bodies carry two.** Platform
`origin/main` = `b8598dd`; every unit at its `origin/main` in throwaway detached worktrees
(driftwood `25f1e6a`, tuppence `91ed30c`, ludlow `ba23b55`, feeds `8cb7ae8`, ico `c65b6b2`,
insurer `c991160`, nist `9dd7c31`; no local `main` read). Unmasked, from a throwaway copy of the
platform tree:

    PAVC_ESTATE_CLONE=<estate@origin/main> python composition.py --selfcheck
    ...58 OK legs...
    File "compose/composition.py", line 5126, in selfcheck
        assert "acme" not in text, path
    AssertionError: composed/governed-namespace-guard.yaml
    exit=1

Then, in that throwaway copy only (nothing committed, no mask in any tree), the loop's three
assertions (`"ungoverned" not in text`, `"acme" not in text`, `GOVERNED_LABEL not in text`) were
replaced by a recorder that prints every hit and continues. That run went **81 OK, exit 0**: every
leg behind the collision, ticket 34's three price legs included, executes and passes on current
main once it is out of the way. What the recorder saw, in the loop's iteration order:

1. `composed/governed-namespace-guard.yaml` — `"acme"`, **3 hits, two causes**: the label prefix
   `posture.acme.io/caged` and `posture.acme.io/tier` (as this ticket says), AND
   `image: "ghcr.io/acme/coraza-waf:cage"`, the WAF sidecar image's registry path. Renaming the
   label domain alone would not clear the file.
2. `composed/orphan-cage.yaml` — `"acme"`, 3 hits, the same three strings.
3. `composed/orphan-cage-holds.yaml` — `"acme"`, 3 hits: `oldObject.?metadata.?labels['posture.acme.io/tier']`
   and the two mutation labels.
4. `composed/governed-namespace-holds.yaml` — `"acme"`, 3 hits (as 3), **and** `GOVERNED_LABEL`,
   1 hit, in its own `namespaceSelector.matchLabels` (the structurally-correct use the comment at
   ~5127 exempts the guard for, and only the guard).
5. `composed/governed-namespace-report.yaml` — `GOVERNED_LABEL`, 2 hits: its `namespaceSelector`
   and its message text (`this namespace is governed (policy-as-versioned.dev/governed: "true")`).

`"ungoverned"` hits nothing in any file. So masking the `acme` assertion wholesale, as the reviewer
did, gives three steps — guard (`acme`, 5126), holds (`GOVERNED_LABEL`, 5132), report
(`GOVERNED_LABEL`) — and masking per (file, assertion) gives six. The exact assertions, by line on
`b8598dd`: `assert "acme" not in text, path` (5126) for files 1–4; `assert GOVERNED_LABEL not in
text, path` (5132) for files 4–5.

**Fix, amended.** Two changes, both needed, neither a mask:

- (a) rename the fixture namespace to a token no served body contains and assert it as a whole
  token (as above). That clears all four `acme` files at once, because none of them carries the
  namespace NAME — only the label domain and the image registry path. Keep the substring form
  of the check for the *renamed* token so a leak of the name inside a longer string is still seen.
- (b) review the `GOVERNED_LABEL` exclusion list. The comment says only the guard legitimately
  carries the label in its `namespaceSelector` (ADR-0014); since tickets 89 and 91 the holds and
  report bodies carry the same structurally-correct selector, and the report its message, and
  none is a leak of the ungoverned bookkeeping. Either name those two files beside the guard
  with the reason, or — better, so the leg stays a leak detector — assert the label appears
  nowhere OUTSIDE a `namespaceSelector` block or a quoted message. Say which in the comment.

Not fixed here: ticket 34's follow-up (2026-09-08) measured and recorded this only.

## Answer

(open)
