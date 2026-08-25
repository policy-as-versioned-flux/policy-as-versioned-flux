# 18 — Wire composition into adopter CI, sign the first composed artefacts, hand the bump to ADR-0011

Type: task
Status: ready-for-agent
Blocked by: 14, 15, 16

Source: [`spec.md`](../spec.md), *Where it runs*, *The composed artefact*, *Further Notes*.
Decisions: [ADR-0011](../../../docs/adr/0011-release-gate-computes-the-bump.md),
[ADR-0012](../../../docs/adr/0012-composed-artefact-self-signed-pinned-sha.md).

## What to build

An institution engineer merges a Renovate bump, and what runs is the sum of what was pinned, signed.

Each adopter's shift-left check recomposes on every pull request. It regenerates the composed
artefact and the evidence document, and fails on any diff against the committed copies. It fails on
refusal and prints the document as the job summary. The composed artefact and the document are
committed files in the adopter's repo. The adopter's ordinary release tag then covers them. No second
signing mechanism.

The adopter gate from ADR-0011 reads the composed artefact as its subject, so the composed bump is
computed after composition. A workload pinning a retired version classifies as major there, with no
policy diff. The verify mode from ticket `12` runs in the release workflow, re-rendering from the
recorded SHAs and comparing byte-for-byte.

Cut the first tag on each adopter. It records 285 holes and one ungoverned namespace per adopter if
ticket `11`'s label is not yet merged, and refuses on none. That tag is the comparison point for every
run after it.

Warning. Do not hand-edit the first tag's hole list. A hole removed by hand prints as closed on the
next run and cannot be told from a filled one.

Retire the prototype's README claims that say nothing is signed and there is no proposer. Point it at
the real engine.

## Acceptance criteria

- [ ] Each adopter's shift-left check recomposes on every pull request and fails on a diff or a refusal.
- [ ] The evidence document is the job summary on every run, refusal included.
- [ ] The composed artefact and the document are committed and covered by the adopter's release tag.
- [ ] The release workflow re-renders from the recorded SHAs and fails on a byte difference.
- [ ] The adopter gate computes the composed bump from the composed artefact.
- [ ] A retired pin classifies as major in the adopter gate with no policy diff. A fixture proves it.
- [ ] Each adopter has one signed composed artefact tag, and its hole list is the comparison point for the next run.
- [ ] The prototype README points at the real engine and no longer claims nothing is signed.
