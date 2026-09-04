# 82 — Licence, attribution and disclaimers

Type: task (AFK build, HITL decision on named individuals)
Status: resolved
Blocked by: none

## Question

Nine public repositories, no legal realism assessed. The hub holds the thesis, 24 ADRs, NORTH-STAR, the truth surface and 56,000 lines of Python under no licence at all, while every unit is Apache-2.0. The nist repo redistributes the NIST SP 800-53 rev 5.2.0 catalogue, a US Government work, under a blanket Apache-2.0 licence with no NOTICE and no attribution. Ico's signed payload says `authority: ICO (Information Commissioner's Office)` and no README, party artefact or org description anywhere says the party is a demonstration and not the regulator. The twin's public corpus names eleven real firms and four living Intel chief executives beside scored fraud and failure probabilities, and publishes a probability about a listed issuer.

1. Add `LICENSE` (Apache-2.0, matching the units) at the hub root and one line in README.
2. Add a NOTICE to nist attributing the catalogue to NIST and stating its public-domain status.
3. Add a `DISCLAIMER.md` to ico and nist and one line in every README and party artefact: a demonstration party, not affiliated with the named authority. Add a gate check that every party artefact carries the line.
4. The owner decides whether the twin corpus keeps named living individuals, and whether the Intel scenario needs a "not investment research" line. Record the decision against NORTH-STAR §6's exclusion of real surveillance data.

Done = `gh api .../license` returns Apache-2.0 for the hub; the NOTICE and disclaimers exist and are checked; the named-individuals decision is recorded with a reason.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R11. Findings: operability/O5, completeness C5 and C10. Cheap, and a precondition for every purpose in ticket 75 Q1 except a private talk.

## Answer

**2026-09-03.** Built in one hub branch (`ticket-82-licence-attribution-and-disclaimers`) and eight
unit branches of the same name off `ecosystem/build-2026-09-03`, committed locally, never pushed.

1. **Hub licence.** `LICENSE` is the Apache License 2.0 verbatim, byte-identical to the file all
   eight units already carry (one md5 across the nine). README gains a licence paragraph that
   names it, says quoted third-party material stays under its authors' own terms, and points at
   the check. `gh api .../license` turns true only once this branch is merged and GitHub's
   detector runs; that is a live read the gate does not take, so the gate reads the file.
2. **nist NOTICE.** `NOTICE` attributes the SP 800-53 rev 5.2.0 catalogue and the LOW, MODERATE
   and HIGH profiles to NIST as a US Government work, public domain under 17 U.S.C. section 105,
   cites the upstream URL and every sha256 that `catalog/CATALOG_VERSION.json` and
   `catalog/BASELINE_VERSIONS.json` record, and says Apache-2.0 covers only the wrapper. It is
   rendered from the manifests by `verify/disclaimer/disclaimer.py notice`, and the check refuses
   a NOTICE whose values disagree with the manifests, so a catalogue bump that forgets the NOTICE
   is red, not silent.
3. **Disclaimers.** One sentence, the same bytes everywhere:
   `A demonstration party, not affiliated with, endorsed by or speaking for any real authority it names.`
   It sits on line 1 of all eight `party.yaml` files as a `#` comment, in a paragraph under the
   header of all eight READMEs (feeds gains the licence line the other seven already had), and in
   `ico/DISCLAIMER.md` and `nist/DISCLAIMER.md`, which also say what the `authority` field, the
   catalogue and the signatures do and do not mean.
4. **The check** is `verify/disclaimer/verify-disclaimer.sh`, discovered by `talk/verify-all.sh`
   through the hub `verify/` glob, driving `disclaimer.py selfcheck`: the real estate is clean,
   then six violations are planted in copies and each is refused (party.yaml without the comment,
   the sentence as a key instead of a comment, a bare README, a NOTICE sha256 drifted from the
   manifest, a missing DISCLAIMER.md, a hub without LICENSE), then each restored copy passes.
   `tests/test_disclaimer.py` covers the same functions over fixtures and reads the real clone
   when present. Every party.yaml still parses and still validates against
   `platform/party/schema.json` (ico's pre-existing pin-file refusal is unchanged by this ticket).

Decisions, each delegated (ADR-0025):

- **Comment line, not a schema key.** The artefact is signed under the unit's tag and
  `schema.json` is `additionalProperties: false`, so a key changes eight signed artefacts and
  needs a platform tag first; a comment changes nothing a parser reads. The check also refuses
  the sentence as a key so nobody drifts into the schema by accident. A later ticket that needs
  it machine-readable edits schema.json and `disclaimer.py` together.
- **A new `verify/disclaimer/`, not an extension of `verify/party/party.py`.** party.py is the
  roles guard and grades one fact; this grades a different fact, gets its own PASS line on the
  TRUTH surface, and the wave note says the hub `verify/` tree. It reuses `verify/_estate.py`
  and `verify/party/roles.json` for the party list, so a party declared but not cloned is a
  refusal, not a silent zero.
- **NOTICE wording.** 17 U.S.C. section 105, the upstream URL and every recorded sha256, and the
  explicit line that Apache-2.0 covers only the wrapper, rendered from the manifests rather than
  typed, for the reason in item 2.
- **ico's `authority` field stays as it is.** It is the provenance of a real magnitude: the body
  that levied the fine. Rewording it would launder the citation. `ico/DISCLAIMER.md` explains
  the field is a citation, not a claim of identity, and the README links it.
- **One LICENSE for the whole hub, with the README noting cited material keeps its own terms.**
  Splitting the hub into differently licensed trees would need a licence per directory and buys
  nothing: quoting a press release in a fixture is citation, not redistribution, and the README
  says so.
- **The named-individuals ruling is not made here** and NORTH-STAR §8 is not edited by this
  ticket: the ruling names real people, which ADR-0025 point 6 keeps with the owner. The draft
  is below with both options laid out; whichever the owner picks lands in §8 as an
  owner-reasoned line with the owner's words.

**2026-09-04, review fixes.** Two reviews, both request-changes on the same sentence, both fixed:

- **ico/DISCLAIMER.md asserted a data property the schema does not have** (blocking, both
  reviews). It said a fine reduced on appeal or never collected is recorded "as data" by the
  schema. Checked against `ico/schema/v1`, `v2`, `penalty-schema/v1..v3/feed.json` and both
  payload schemas: each real example records `org`, `year`, `fine_gbp`/`fine_usd` (a `note` for
  pci-dss), an optional `proposed_gbp` and `source`, and nothing else; no version carries a
  status, appeal, collection, litigation or final-as-of field. The text now says exactly what is
  recorded, that no version records a later reduction or non-collection, and that ticket 79
  (still open) *plans* to add `status` and `final_as_of` and correct the stale figures in a new
  major. The clause existed in that one file only; the other seven units and the hub never
  copied it. Unit commit ico a525889.
- **`notice_problems` passed a NOTICE whose baseline manifest could not be read** (minor). It
  refused only when the catalogue manifest yielded no facts, so a missing
  `BASELINE_VERSIONS.json` was a pass for the half of the attribution the NOTICE makes about the
  three baselines. It now refuses when no baseline sha256 can be cited, test first
  (`test_notice_is_refused_when_the_baseline_manifest_cannot_be_read`, red then green).
- **Where the verification was taken** (minor, both reviews). The hub worktree's
  `.estate-clone/` is not the brief's single symlink to the real clone: it is a directory of
  eight symlinks, one per unit, each into that unit's `.work/ticket-82` worktree, so the check
  and the eight parametrised real-estate tests read the ticket commits. The real
  `.estate-clone/<unit>` checkouts are on `ecosystem/build-2026-09-03` without them.
  **Integrator: merge the eight unit branches into `ecosystem/build-2026-09-03` and check them
  out before, or in the same step as, merging PR 8**; otherwise `verify-disclaimer.sh` and eight
  tests go red on main until the units catch up.
- **feeds does not gitignore `.work/`** (minor, pre-existing, not this ticket's edit): its
  `.gitignore` lists `__pycache__/` and `.fetch/` only, so `git status` in the feeds checkout
  shows `?? .work/` and a `git add -A` there would try to embed the ticket worktree. Left for
  the integrator; adding the line is a one-line feeds commit on the integration branch.

Verified (from the hub worktree root, re-run 2026-09-04 after the fixes):

- `bash verify/disclaimer/verify-disclaimer.sh` exits 0, last line `PASS: all eight parties say
  they are a demonstration ...`.
- `.venv/bin/python -m pytest tests/test_disclaimer.py -n0 -q`: 16 passed.
- `MYPYPATH=verify .venv/bin/python -m mypy verify/disclaimer/disclaimer.py
  tests/test_disclaimer.py`: no issues.
- `bash verify/party/verify-party.sh` still passes with the comment line in place (2026-09-03
  run; nothing it reads changed on 2026-09-04).

Map line: 82 built: hub LICENSE Apache-2.0, nist NOTICE from its manifests, one demonstration line on all 8 party.yaml (comment) and READMEs, DISCLAIMER.md on ico and nist, verify/disclaimer/ grades it; named-individuals ruling drafted, waits on the owner.

## Waits on the owner

1. **Push the eight unit branches** `ticket-82-licence-attribution-and-disclaimers` (via
   `ecosystem/build-2026-09-03` once the integrator merges them) to the enactment orgs; the
   guard refuses agent pushes there. Commits: platform 2b86446, driftwood 18c6416, tuppence
   b078731, ludlow b966eb9, feeds 113a2cb, insurer 8a308f1, ico d6ed440 and a525889 (the
   2026-09-04 disclaimer correction), nist ea84ef8 and 683784f.
2. **Cut new signed tags** for each unit through cut-release.yml, since party.yaml is signed
   under the unit's tag and its bytes changed. Nothing here fakes a signature; the comment line
   is unsigned until the owner tags.
3. **The named-individuals ruling.** The twin corpus (`twin/fixtures.py`) names four living
   people beside scored probabilities, all inside the Intel scenario: Brian Krzanich (2015 EUV
   statements, twice), Pat Gelsinger (retirement press release, twice), Lip-Bu Tan (appointment
   and an earnings-call statement, three times) and Michelle Johnston Holthaus (interim co-CEO,
   once). The Enron scenario names nobody in prose, though the signal id
   `skilling-resigns-2001-08-14` carries a surname. Every mention is a public statement by a
   named executive in their corporate role, cited by URL to the issuer's own press release or a
   newswire, and no score attaches to the person: the probabilities attach to propositions about
   the firm. NORTH-STAR §6 excludes real surveillance data and says substrates are synthetic with
   planted ground truth; this corpus is public-record, not surveillance, but §6 does not say
   whether public statements by named living people are in or out. Draft §8 entry, ruling blank:

   > 17. Named living individuals in the twin corpus: **[A / B]** (owner-reasoned, 2026-09-__;
   > ticket 82). **A, keep the names**: each is a public statement in a corporate role, cited to
   > its source, with no score on the person; the corpus is public record and stays inside §6's
   > exclusion of surveillance data. Consequence: nothing changes; a rule that a name appears only
   > with a URL to the statement is added to `twin/fixtures.py`'s header. **B, remove the
   > names**: replace each with the role ("the then chief executive") and keep the URL, so the
   > citation survives and the corpus names firms only, matching ticket 94's "do not name a
   > private individual". Consequence: seven edits in `twin/fixtures.py`, the signal id
   > `skilling-resigns-2001-08-14` renamed, and the hindsight tests re-run.
   >
   > 18. The Intel scenario publishes a probability about a listed issuer: **[carry / do not
   > carry]** a "not investment research" line (owner-reasoned, 2026-09-__; ticket 82). The
   > estate is a demonstration under a declared perspective, the £ is an ordinal comparison
   > instrument (§8 item 4), and no forecast is offered to anyone as advice. If carried, the line
   > goes on the forward-intel envelope and the README beside the Intel org, and
   > `verify/disclaimer/` grows a check for it.

   The assistant's recommendation, for the owner to accept or overrule: A and carry. A because
   the citation is the evidence ladder's own rule (a statement without its speaker is a weaker
   grade), and carry because it costs one line and closes the only reading of the corpus that
   could be mistaken for advice.
