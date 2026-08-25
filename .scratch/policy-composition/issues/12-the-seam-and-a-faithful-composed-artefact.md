# 12 — The seam, and a composed artefact that renders back down faithfully

Type: task
Status: resolved
Blocked by: 11

Source: [`spec.md`](../spec.md), *Resolution*, *The composed artefact*, *The evidence document*,
*Testing Decisions*. Decisions:
[ADR-0012](../../../docs/adr/0012-composed-artefact-self-signed-pinned-sha.md),
[ADR-0016](../../../docs/adr/0016-a-subclass-never-restates-a-mutate.md).

## What to build

One entry point composes an adopter from its parents and gives back two things. The evidence document
as a dictionary. The rendered composed artefact as a mapping of path to content. A thin command-line
wrapper writes the files, prints the document and exits non-zero on refusal. Every later ticket adds a
field or a refusal through this seam and nothing else.

The engine lives in `platform`. It reads the party artefact from ticket `11`, resolves each parent
tag to its commit SHA, and loads every member of every kind from the `implementations` parent at that
SHA. The resolver keys on the identity family plus the policy name with its version stripped. The
`platform-machinery` members load under the platform tag as a second axis.

The render emits the flat per-version files exactly as the version-tree renderer does, plus one
advisory header at the top. The header carries a composed marker, each parent's SHA once, the
selected baseline name, and the governed namespace names read from the adopter's `Namespace`
manifests. Hole and ungoverned lists join in later tickets. Per-rule `composed-for`,
`inherited-from` and `source-path` annotations stay. Strip the header and every file is byte-identical
to the parent's committed file. The orphan guard compares against the estate's own offline twin.

The evidence document starts with `outcome`, `parents[]`, `members[]` and `limits[]`. Every later
field is added here, never elsewhere.

Fixtures are party trees on disk. The real estate clone is the validation set. It SKIPs with exit 0
when absent. Start from the prototype's flow and its `render_is_faithful`. Rewrite the loader, which
keys wrongly, and the render, which wrote an action onto every kind.

## Acceptance criteria

- [ ] One entry point takes an adopter repo state plus parent trees and returns the document and the rendered files.
- [ ] The CLI wrapper writes the files, prints the document, and exits non-zero on refusal.
- [ ] Every member of every kind in the real estate composes and renders back byte-identical after the header is stripped.
- [ ] The orphan guard composes under the platform tag and renders back to the offline twin's output.
- [ ] Two members of one family at one version both survive resolution. A fixture proves it.
- [ ] No `validationActions` field is written onto a mutate or a generate.
- [ ] The header records each parent's resolved SHA once, the composed marker, the baseline name and the governed namespace names.
- [ ] A verify mode re-renders from the recorded SHAs and compares byte-for-byte against committed files.
- [ ] The document carries `outcome`, `parents[]`, `members[]` and `limits[]`.
- [ ] The engine has a self-check of runnable asserts, and SKIPs with exit 0 when the estate clone is absent.

## Answer

Built. `platform/compose/composition.py` (new), one entry point: `compose(adopter_dir,
parent_trees) -> (document, rendered_files)`. `parent_trees` is `{party name: its directory}` —
the seam takes trees, not a fixed clone layout, so a test fixture never needs the real
`.estate-clone` shape.

**The flow.** Loads `party.yaml` and runs ticket 11's `party_artefact.check()` first — a party
artefact that doesn't check out refuses before anything else runs, nothing safe to compose from
it. Resolves every declared parent to a commit SHA: `controls`/`implementations` read
`spec.ref.commit` already sitting in the adopter's own Flux pin (never re-derived, per
ADR-0012); `pricing`/`threat` have no Flux pin anywhere in this estate, so they resolve by
reading the party directly — `git log` on `ico`'s `schema/v1/` and `platform`'s
`feeds/threat-register/v1/`, falling back to a content digest for a non-git fixture tree. Loads
every `ValidatingPolicy`/`MutatingPolicy`/`GeneratingPolicy` member of every live policy version
from each `implementations` parent, keyed on **(identity family, name with its version suffix
stripped)** — the prototype's actual bug was keying on `(family, version)` alone, which drops a
second member of one family in silence (`graded-enforcement` covers `cage-tier` *and*
`cage-netpol`). The orphan guard loads through the parent's own offline twin
(`render-orphan-guard.py`) under the platform tag, never forced onto the policy-version axis.
Renders every member back down unchanged plus a `composed-for` label and
`inherited-from`/`source-path` annotations; `spec.validationActions` is written **only** onto a
`ValidatingPolicy` — the prototype's other defect was writing it onto every kind, inventing a
field the Kyverno CRD schema refuses on a mutate or a generate. Writes one advisory header
(`composed/HEADER.yaml`, separate from the per-rule annotations): the composed marker, each
parent's SHA once, the selected baseline, the governed namespace names (read off the adopter's
own `Namespace` manifests).

**Scope held at the ticket boundary.** No diamond check, no cross-party conflict, no
restatement/caging, no baseline/hole resolution, no governed-namespace refusal, no pricing —
those are tickets 13-16's. The only refusal source in this ticket is an invalid party artefact
(reusing ticket 11's `check()`); `outcome` is `"composed"` or `"refused"` with
`party_artefact_errors` (a plain list, deliberately *not* named `refusals[]` — ticket 13 owns
that field's shape, with `needs_composition` on every entry, and shouldn't inherit a
differently-shaped field to migrate). `limits: []` for the same reason: ticket 13 is the one that
knows how to count pinned implementations publishers.

**Verify mode.** `verify(adopter_dir, parent_trees)` re-runs `compose()` against the same parent
trees and diffs byte-for-byte against whatever `composed/` already holds on disk — catches both a
tampered committed file and a stale one a fresh render no longer produces.

**Verified against the real estate.** `--selfcheck` (14 asserts) composes the real `driftwood`
against its real pinned `platform`/`nist`/`ico`: all 4 parent kinds resolve to a non-empty SHA;
all 15 live members (5 per version × 3 live versions: `2.0.0`, `2.0.1`, `3.0.0`) plus the orphan
guard render back byte-identical after the header is stripped; `cage-tier`/`cage-netpol` (one
family, `graded-enforcement`, one version) both survive resolution, proven against the real
estate and against a dedicated synthetic fixture; no `validationActions` leaks onto the Mutating
or Generating members; the header carries all 4 parent SHAs, the composed marker, `baseline:
MODERATE`, `governed-namespaces: [driftwood]`; verify() round-trips clean and catches a tampered
file; the CLI (`compose`/`verify` subcommands) writes files, prints the document, and exits 1 on
a refused party artefact without writing anything. SKIPs with exit 0 when `driftwood`/`nist`/
`ico` are absent from `.estate-clone` (platform itself always exists, since this module ships
inside it). Re-ran ticket 11's own `verify-party-artefact.sh` — still clean, no regression.

Manually exercised `compose`/`verify` CLI against the real `tuppence` clone end-to-end (rendered
files written, then verified byte-for-byte, then removed — a throwaway run, not a deliverable).
No repo committed; same uncommitted-working-tree pattern as tickets 09-11. Review gate: PASS.
