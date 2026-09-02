# 77 — Every pin is checked for content, and the estate consumes itself the way it tells adopters to

Type: task (AFK build, HITL tag dispatch)
Status: open
Blocked by: none

## Question

NORTH-STAR §2's "consumed only through a pinned, signed dependency" is applied to the policy artefact and to almost nothing else, and where a pin exists the check is that the tag resolves, never that its tree contains what the consumer prices or enforces from it. Close the family:

1. One assertion, shared: a pinned tree must contain the section the pin is used for. Add it to composition (a parent pin whose tree lacks the declared feed path refuses as a missing instrument), to `insurer/pricing/quote.py` (never emit `priced_against` naming a tag whose tree lacks `exposure`), and to `verify/feed-contract`.
2. The insurer's quotes assert `<adopter> exposure v1.1.0`; no adopter's v1.1.0 tree has an exposure section. The owner dispatches one adopter release per adopter whose tree carries `exposure` and `composed/policies/v4.0.0`, then the insurer re-quotes from it. HITL for the dispatch.
3. The adopters' clusters reconcile composed 2.0.0, 2.0.1 and 3.0.0 from tag v1.1.0, the three retired lines. The same release in item 2 adds the `{ version: "4.0.0" }` element and bumps the composed pin, as the file's own comment prescribes.
4. Ico, insurer and feeds `release.yml` check platform out with no `ref:`. Pin each to the tag its own party artefact or platform pin names.
5. Driftwood consumes ico, feeds and insurer at `ref: main` in nine places, with no Flux source. Move them to the tag and commit `party.yaml` declares, and add an ico `GitRepository` in the nist pattern. Tuppence's and ludlow's twelve deleted-branch refs are ticket 62; land them together.
6. `.github/workflows/truth.yml:91` installs Flux with `curl -s https://fluxcd.io/install.sh | sudo bash` under a comment that says every tool is pinned. Copy `drift-sample.yml`'s pinned tarball form. Add `--fail` to every curl in the file.
7. `clone-estate.sh` clones default branches against its own comment that promises to pin once a signed tag lands. Whether the truth surface grades tags or branches is Q8 in ticket 75; until answered, record the tag beside each SHA in the TRUTH line so a reader can tell.

Done = a gate check resolves every declared pin in every party artefact against the tag it names and refuses a tree that lacks the named section; no workflow in the eight units checks another organisation out at a branch; the insurer's clock succeeds for real on the next scheduled run.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R4. Findings: participants/P1, P3, P4, P5, pound-engine/PE-11, principles/P4-2, security/SS-06, SS-03 (federation literals, ticket 68). Ticket 62 owns the tuppence and ludlow refs. Ticket 64 owns the twin tag. The insurer already recorded one fabricated version on 2026-08-29; this is the third artefact of that class.
