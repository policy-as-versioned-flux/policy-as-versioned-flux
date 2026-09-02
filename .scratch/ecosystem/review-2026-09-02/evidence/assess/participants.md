# NORTH-STAR §2 PARTICIPANTS — assessment, 2026-09-02

Auditor pass. Every fact below was re-derived from a primary source in this session
unless it is explicitly marked "(map only)". Reader maps used as pointers:
`understand/publishers.md`, `understand/adopters.md`, `understand/github-live.md`,
`understand/twin.md`, `understand/verify-scripts-units.md`.

Citable truth line for this pass:
`TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 units=[driftwood=6cf0671 feeds=69c89b0
ico=9d09222 insurer=632db22 ludlow=ede531a nist=96154b8 platform=46cd775
tuppence=19cd508] pass=57 fail=7 skip=18 excluded=2 total=84`.

The clause under test is NORTH-STAR.md §2's closing paragraph:

> **Loosely coupled means:** each participant lives in its own GitHub organisation,
> ships on its own cadence, signs its own artefacts, and is consumed only through a
> pinned, signed dependency. No participant reaches into another. The only shared
> things are the artefact contracts and the £.

---

## 1. The row-by-row table

| §2 row | Own org? | Signed semver tags? | Consumed only pinned+signed? | Own clock? | Reaches into another? |
|---|---|---|---|---|---|
| Regulator `nist` | yes | yes, 2/2 verify | **no** — no Flux pin exists in any adopter for nist? *(it does: tag+commit, correct)* — yes for nist | runs daily, **observes null** | no |
| Regulator `ico` | yes | yes, 2/2 verify | **no** — consumed at `ref: main` in 9 adopter checkouts, no Flux pin anywhere | daily, success | no |
| Intelligence publisher `feeds` | yes | partial — only `threat-register` of 6 feeds is tagged | **no** — `ref: main` (driftwood) / a deleted branch (tuppence, ludlow) | **failed both runs it has ever had** | no |
| The twin | **no org** | **no tag, no signature** | **no** — vendored verbatim into driftwood; hub checked out at `ref: main` | **failed both scheduled sweeps**; hub twin.yml failing continuously | **yes** — driftwood runs inside `hub/.estate-clone/driftwood` |
| Platform | yes | yes, 11/11 verify | **yes** (tag+commit, both lines correct) for adopters; **no** for the three publisher release gates | daily, success | **yes, mildly** — still ships copies of `feeds`' cve/eol/threat-register |
| Adopter `driftwood` | yes | yes, 2/2 verify | n/a (publishes exposure + forward-intel) | 4 clocks, 3 green, twin-sweep red | consumes hub at `main` |
| Adopter `tuppence` | yes | yes, 2/2 verify | n/a | propose-tier **red every run** | no |
| Adopter `ludlow` | yes | yes, 2/2 verify | n/a | propose-tier **red every run** | no |
| Insurer | yes | yes, 1/1 verifies | its own consumption of adopters **names tags that do not carry the section it prices** | **requote red on both runs; has never produced a quote** | no |

Corrections to the header row above: nist and platform *are* consumed by a correct
tag+commit Flux pin; ico, feeds and insurer are not consumed by any pin.

### Evidence for the "own org" column

```
$ for o in twin platform nist ico driftwood tuppence ludlow feeds insurer; do
    gh api orgs/policy-as-versioned-$o --jq '.login+" repos="+(.public_repos|tostring)'; done
{"message":"Not Found", ... "status":"404"}   # policy-as-versioned-twin
policy-as-versioned-platform repos=1
policy-as-versioned-nist repos=1
policy-as-versioned-ico repos=1
policy-as-versioned-driftwood repos=1
policy-as-versioned-tuppence repos=1
policy-as-versioned-ludlow repos=1
policy-as-versioned-feeds repos=1
policy-as-versioned-insurer repos=1
```

Eight of the nine rows are their own single-repo organisation. The twin is not: it
lives in `twin/` inside the hub, which sits in `policy-as-versioned-flux` alongside
15 legacy repos.

### Evidence for the "signed tags" column

I ran gitsign against Rekor over every tag in all eight fresh clones (24 tags):

```
$ git -C <unit> -c gpg.format=x509 -c gpg.x509.program=gitsign tag -v <tag>
```

Every one returned `Good signature from
[https://github.com/policy-as-versioned-<org>/<repo>/.github/workflows/cut-release.yml@refs/heads/main]`
(platform's `policy/v2.0.1` from `refs/heads/release/2.0.x`) and
`Validated Rekor entry: true`. **No unsigned tag, no bad signature, anywhere.**
This is a real, re-derivable strength and it is the strongest thing in this dimension.

The hub has zero tags (`git tag -l` in the hub returns nothing), so the twin row has
no signed artefact at all.

---

## 2. Findings

### P1 (critical) — The insurer has never priced a quote from a signed exposure, and its signed tag asserts a provenance that cannot exist

`insurer/party.yaml:51-53` pins, for all three adopters:

```yaml
  - { party: driftwood, kind: feed, name: exposure, version: "v1.1.0", since: '2026-08-28' }
  - { party: tuppence,  kind: feed, name: exposure, version: "v1.1.0", since: '2026-08-28' }
  - { party: ludlow,    kind: feed, name: exposure, version: "v1.1.0", since: '2026-08-28' }
```

But `git -C <adopter> show v1.1.0:composed/HEADER.yaml` has these top-level keys and
no more, in all three: `policy-as-versioned.dev/composed, parents, baseline,
governed-namespaces, holes, selected-controls, ungoverned-namespaces`. **There is no
`exposure` section at v1.1.0 in any adopter.** Each adopter has exactly two tags
(`v1.0.0`, `v1.1.0`), so no tag anywhere carries the section.

The published quote nevertheless asserts it did. Read from *inside the insurer's
gitsign-verified tag*:

```
$ git -C insurer show v1.0.0:quote/driftwood/v1/feed.json | ... priced_against
[{"party":"platform","kind":"implementations","version":"1.1.1"},
 {"party":"driftwood","kind":"feed","name":"exposure","version":"v1.1.0",
  "exposure_sha256":"sha256:397abe81d6cbdbd7b27a5d2516dd9c35417e9922f995b8b6af7d1fca34829820"}]
```

Recomputing that digest with the insurer's own canonicalisation
(`insurer/pricing/quote.py:104-109`, `json.dumps(exposure, sort_keys=True,
separators=(",",":"))`) over each adopter's *current, untagged, unsigned* `main` HEAD:

| adopter | recorded | recomputed at HEAD | |
|---|---|---|---|
| driftwood | `sha256:397abe81d6cbdbd7…` | `sha256:5822260bab861329…` | **MISMATCH** |
| tuppence | `sha256:25418091ed892212…` | `sha256:25418091ed892212…` | match |
| ludlow | `sha256:b0808d7448a35bae…` | `sha256:b0808d7448a35bae…` | match |

So two of three quotes were priced from an *unsigned working tree*, and the third was
priced from a tree that has since moved and was never re-priced. In every case the
artefact names a tag as its source, and that tag does not contain the source.

It is breaking live, on the clock, right now. Both of the insurer's only two scheduled
runs have failed on all three requote legs:

```
$ gh run view 33615860064 --repo policy-as-versioned-insurer/insurer --json jobs
requote (tuppence)  failure
requote (ludlow)    failure
fetch               success
requote (driftwood) failure

$ gh run view 33615860064 ... --log-failed
REFUSED: missing instrument: .adopters/driftwood/composed/HEADER.yaml carries no
`exposure` section -- there is no signed exposure to attach a layer to
```

Same on run `33496526156` (2026-09-01). The refusal itself is honest and correct
behaviour — the engine refuses rather than guessing — which is why this is a
provenance defect, not a pricing defect.

This is the **second** occurrence of this exact class in this file. `insurer/party.yaml`'s
own comment records the first: the pins used to read a fabricated `v1.2.0` no adopter
had ever tagged, and "the fabricated version was laundered into driftwood's own signed
evidence.json as the provenance of a six-figure cost line (found 2026-08-29)". The
fix substituted a real tag number without checking the tag's tree, so the same
laundering is live under a correct-looking version string, and driftwood's
`composed/evidence.json` still carries the £113,403.30 premium line derived from it.

Ownership: ticket 69 ("an untagged pin is a priced hole") covers *driftwood's* pin on
the quote. Ticket 62 covers unpinned adopter CI. **Neither covers the insurer's own
pin naming a tag that lacks the section**, and ticket 36's resolved Answer — "The
insurer pins the platform and the adopter signed exposure, prices on its clock under
its own perspective, and publishes one quote feed per adopter" — is now false with no
dated correction on the ticket. Orphan.

### P2 (major, fully owned) — Twelve cross-participant checkouts name a branch that no longer exists

`ref: ecosystem/thin-slice` appears in tuppence and ludlow × {`propose-tier.yml`,
`cut-release.yml`, `shift-left.yml`} × {feeds, insurer} = **12 checkout sites** (my
own grep count; matches ticket 62's comment exactly). The branch does not exist on
either target:

```
$ gh api repos/policy-as-versioned-feeds/feeds/branches --jq '.[].name'
fetch/cve-2.0.1  fetch/eol-2.0.1  fetch/fx-1.1.0  fetch/threat-register-2.0.1  main  observations
$ gh api repos/policy-as-versioned-insurer/insurer/branches --jq '.[].name'
main  observations
```

Still red today: tuppence `propose-tier` run `33633036907` (2026-09-02T12:59:26Z)
`##[error]A branch or tag with the name 'ecosystem/thin-slice' could not be found`;
ludlow run `33518603510` (2026-09-01T14:18:00Z) identical. So two of the three adopter
rows cannot compose, propose a tier, run shift-left, or cut a release on any clock.

The source comment beside the ref is itself wrong about what it does:
`tuppence/.github/workflows/shift-left.yml:353` says "`main` matches the ico line
above: neither repo cuts a tag this adopter pins yet" — but the code says
`ecosystem/thin-slice`, not `main`, and feeds *has* since cut `threat-register/v1.0.0`
and `v2.0.0` and insurer `v1.0.0`.

Owned by ticket 62 (open, blocked by 57 which is `claimed`), whose 2026-09-01 comment
diagnoses it precisely and notes the feeds half is now unblocked. I record it here as
confirmed and still live, not as a new finding.

### P3 (major, owned) — Three of five parents are consumed with no pin of any kind

Flux `GitRepository` objects across the three adopters cover only: self, `platform`,
`nist`. There is **no Flux source object for ico, feeds or insurer anywhere** in
driftwood, tuppence or ludlow (`grep -rn "kind: GitRepository" */gitops`). Their
`party.yaml` records only a bare version string (`version: "v3"`, `version: "v2"`) —
not a tag, not a commit.

In CI, driftwood consumes all three at a moving default branch — nine sites:
`propose-tier.yml:129,144,151`; `cut-release.yml:83,97,104`;
`shift-left.yml:343,363,370`, each `ref: main`, two with the comment "ticket 57 renamed
the default branch; ticket 62 owns the real pin". ico has a signed `v3.0.0` that
driftwood's `party.yaml` names as `"v3"` and that no checkout ever uses.

driftwood's `propose-tier` succeeded today (run at 2026-09-02T11:43Z), which means
driftwood's daily re-price *did* read three participants' unsigned, moving branches.

Owned by ticket 62 (open).

### P4 (major, orphan) — Three publisher release gates load the platform from its moving default branch

`ico/.github/workflows/release.yml:60-62`, `insurer/release.yml:61-63` and
`feeds/release.yml:50-53` each check out `policy-as-versioned-platform/platform` with
**no `ref:` at all** — GitHub resolves that to platform's default branch.

Those checkouts are not decoration; they are the gate's instruments:

- `ico/verify-penalty-feed.sh:21` — `fair="$here/../platform/fair/fair.py"`
- `feeds/verify-feeds.sh:25-29` — resolves `platform/feeds/schema.json` (the ADR-0019
  envelope schema every feed is validated against)
- `insurer/verify-insurer-party.sh:83` — `checker="${PLATFORM_DIR:-../platform}/party/party_artefact.py"`

So what a publisher's release is permitted to assert depends on unpinned platform
`main`. feeds is internally inconsistent about this: its `cut-release.yml:59-61` *does*
pin (`ref: v2.0.1`) while its `release.yml` does not.

Ticket 62's scope sentence is "Every adopter's CI checks out ico at ref: main…" —
publishers are not named. Orphan.

### P5 (major, orphan) — The truth surface itself consumes every participant at its default branch

`/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/clone-estate.sh:37-39`:

> `# No signed tag exists yet (ticket 09/12: known, accepted partial state) so`
> `# this clones the default branch. Once a signed v1.0.0 lands, pin it here`
> `# (--branch v1.0.0) so the offline harness matches what Flux actually runs.`

and line 57: `git clone --quiet "https://github.com/$org/$u" "$dir"`.

The stated precondition has fired: all eight units now carry signed `v1.0.0`-class
tags, and I verified all 24 against Rekor above. The pin was never applied. The TRUTH
line's `units=[…]` SHAs are therefore default-branch HEADs of unsigned working state
— `driftwood=6cf0671` in run 21 is a `drift sample: five facts on an ephemeral cluster
[skip ci]` commit, not a tag.

Consequence for this dimension: the one instrument NORTH-STAR §5 permits any document
to cite grades content that nobody signed. A green on the truth surface is not, today,
evidence about the signed line. A grep of `.scratch/ecosystem/issues/` for
`clone-estate` hits tickets 10, 20, 40, 55, 57 and 60; none charts pinning it. Orphan.

### P6 (major, owned) — The twin is the one row with no org, no tag and no signature, and is consumed by copy

- `gh api orgs/policy-as-versioned-twin` → `404 Not Found`.
- The hub has zero tags.
- `driftwood/twin/PIN.yaml`: `twin_version: 0.1.0`, `twin_tag: twin/v0.1.0`,
  `tag_cut: false`.
- `driftwood/twin/VENDORED.md`: 30 files, "Copied | byte-for-byte, verbatim, no edits",
  staged to `world_ref: c2d07330a778ed547b60cfbb87217bcf9813181f`.
- `driftwood/.github/workflows/twin-sweep.yml:64-71`: `working-directory:
  hub/.estate-clone/driftwood`, checking out the hub at `ref: main` and then checking
  driftwood out *inside the hub's clone layout* "because twin/emit-forward-intel.py
  finds the `twin` package by walking UPWARDS from the overlay (the package does not
  self-version yet, so there is no tag to pin)".

This is the clearest breach of "No participant reaches into another" and of "consumed
only through a pinned, signed dependency" — driftwood is literally a tenant of the
hub's directory layout for the duration of that job.

To be fair to the build: the vendoring is documented, deliberate, justified by a real
loader constraint (`Overlay.load` resolves `world_ref` on the same `ModelRepo`), and
content-pinned two ways (`twin_version` must equal the hub's `twin/VERSION` or the
emitter refuses; `world_ref` must equal the staged bytes' commit). That is a good
substitute for a tag — it is just not a tag. Owned by ticket 64 (open, HITL).

### P7 (major, half-orphan) — driftwood's twin sweep can never propose: the "moved" branch is unreachable dead code

`twin-sweep.yml`'s sweep step body opens `set -uo pipefail` — note, **no `-e`** — and
then:

```bash
python3 twin/emit-forward-intel.py --check
rc=$?
if   [ "${rc}" -eq 0 ]; then echo "moved=false" >> "$GITHUB_OUTPUT"
elif [ "${rc}" -eq 1 ]; then echo "moved=true"  >> "$GITHUB_OUTPUT"
else echo "::error::the sweep could not render the overlay at all (exit ${rc})"; exit "${rc}"; fi
```

But the run log records the shell GitHub actually used:
`shell: /usr/bin/bash -e {0}`. `set -uo pipefail` does not clear an inherited `-e`, so
a non-zero exit from the python line aborts the step *before* `rc=$?` is evaluated.
The `moved=true` branch, and the "propose the moved scenario as a pull request" step
gated on it, can never execute.

Proof from the live log of run `33627910027` (2026-09-02T12:04:27Z) — its last two
lines are:

```
FAIL: twin/forward-intel/v1/feed.json is not what the overlay renders
##[error]Process completed with exit code 1.
```

The workflow's own `::error::the sweep could not render the overlay at all` line is
**absent**, which is the direct evidence that the shell died at the python line rather
than reaching either the `elif` or the `else`. Both scheduled runs ever
(`33627910027`, `33508119299`) failed this way.

Consequence: NORTH-STAR §4 step 5 — "the twin, on its schedule, plays a dated external
signal forward … emits a scored forecast, and publishes forward intelligence the
platform consumes" — is structurally unreachable on the clock. Even after ticket 72
fixes the staleness that makes `--check` return 1 today, the *next* genuine move will
also exit 1 and also abort the job.

Ticket 72 (open) owns the render-mismatch cause. No ticket names the unreachable
branch. Half-orphan.

### P8 (major, orphan) — The intelligence publisher has ingested no external datum, and three of four provenance URLs in the one feed whose rule demands provenance are dead

**Nothing fetches.** `feeds/fetch/lib.py:44-51`:

```python
def read_upstream(feed):
    """ponytail: a committed fixture stands in for the upstream GET."""
    source = os.environ.get("FEEDS_SOURCE_DIR") or os.path.join(ROOT, "fetch", "source")
    with open(os.path.join(source, f"{feed}.json")) as fh:
        return json.load(fh)
```

Every `fetch/<feed>.py` names a real UPSTREAM in a constant and never calls it. The
module docstring says so plainly. `market-moves`' own fixture states its seven markets
are "ILLUSTRATIVE, in the venue's published shape and magnitude — this is not a fetch
of Polymarket". This is disclosed everywhere it appears; I flag it as a fact about the
row, not as a concealment.

Per-feed status of the "real external datum" question:

| feed | real external datum? | basis |
|---|---|---|
| `nist` catalogue | **yes** | verbatim NIST SP 800-53 rev 5.2.0 OSCAL, `scripts/verify_catalog.py` → 1196 controls, sha256 matches `CATALOG_VERSION.json`; one-time human snapshot, no fetcher |
| `ico` penalty-schema | grounded, authored | real cited ICO/FCA/HHS penalty notices (BA £20m, TikTok £12.7m, TSB £48.65m…) hand-committed |
| `threat-register` | authored | "DBIR sector base rate, editorial midpoint"; DBIR never fetched |
| `cve` | authored | four entries with invented ids of the form `CVE-2024-1234-envoy` |
| `eol` | authored | real endoflife.date facts, hand-committed |
| `fx` | authored | HMRC-shaped monthly table, hand-committed |
| `market-moves` | authored, self-declared illustrative | fixture comment above |
| `news` | **self-referential, and 3 of 4 citations are dead** | below |

**The news defect.** `feeds/news/rule.yaml` states its own admission rule as:

> `requires_provenance_url  an event with no resolvable provenance URL is not admitted.`

The code, `feeds/fetch/news.py:39-41`, only checks the string:

```python
if rule.get("requires_provenance_url") and not str(
        event["provenance"].get("url", "")).startswith(("http://", "https://")):
    return "requires_provenance_url"
```

Of the four admitted events in `feeds/news/v1/feed.json`, all four cite a GitHub
Release page of this estate's own sibling repos. Three of those pages do not exist:

```
$ gh release view v1.0.0        --repo policy-as-versioned-ico/ico       → https://github.com/…/releases/tag/v1.0.0
$ gh release view v1.1.0        --repo policy-as-versioned-nist/nist     → release not found
$ gh release view 'policy/v3.0.0' --repo policy-as-versioned-platform/platform → release not found
$ gh release view v1.1.1        --repo policy-as-versioned-platform/platform   → release not found
$ gh release list --repo policy-as-versioned-platform/platform
v0.1.1  Latest  v0.1.1  2026-08-21
v0.1.0          v0.1.0  2026-08-21
```

The underlying *events* are true — I verified `nist v1.1.0`, `platform policy/v3.0.0`
and `platform v1.1.1` are real, gitsign-verified tags — but the cited evidence 404s
because `cut-release.yml` was dispatched and `release.yml` never was. The published
feed therefore violates its own stated admission rule for three of its four entries,
and the check that is supposed to catch it tests only the URL scheme. Orphan.

### P9 (major, partly owned) — Two participants' clocks have failed every scheduled run they have ever had; a third's regulator clock observes nothing

- **feeds**: `fetch` schedule failure on 2026-09-01T08:37Z (`33488014777`) and
  2026-09-02T07:54Z (`33605912295`) — the only two runs. The `observations` branch
  carries `observations/README.md` and `observations/market-moves.jsonl` only; five of
  the six feeds have never recorded an observation.
- **insurer**: `fetch` schedule failure on both runs; jobs break down as `fetch:
  success`, all three `requote: failure` (P1).
- **nist**: succeeds, and observes null:
  ```
  $ git -C nist show origin/observations:observations/sp-800-53.jsonl
  {"declared_bump":"none","feed":"sp-800-53","kind":"controls",
   "note":"no catalog/v<N>/feed.json in this repository yet -- this clock records that it
   looked and found none, which is a fact with a date on it, not a silence",
   "observed_at":"2026-09-01T07:59:06+00:00","payload_sha256":null,
   "published_version":null,"publisher":"nist","revoked":[]}
  ```
  Two lines, both null. REVIEW-2026-08-31 already refuted "the publisher clocks observe
  themselves" as a recorded scope decision (ADR-0024, ticket 10 D2), and I am not
  re-raising that. The *distinct* fact is narrower: nist's clock cannot observe even
  its own artefact, because the catalogue lives at `catalog/`, not at the
  `catalog/v<N>/feed.json` path its own reader looks for. The regulator row's clock is
  green on the surface and blind in substance.
- **hub**: `truth` and `twin` both failed their latest scheduled runs
  (2026-09-02T09:54Z and 09:36Z).

The feeds `__pycache__`/observation-lane cause is plausibly ticket 70's scope; the
insurer cause is P1; nist's null observation is not in any ticket I found.

### P10 (minor, orphan) — tuppence and ludlow ship a Flux-reconciled ConfigMap naming a deleted platform file as "the single source of truth"

`tuppence/gitops/apps/risk-appetite-configmap.yaml:9,13` (ludlow's is the same):

> `# Human/audit-readable mirror of ../../platform/risk/appetite.json's tolerance`
> `# … platform/risk/appetite.json remains the single source of truth,`

But `ls platform/risk/appetite.json` → *No such file or directory*, and
`platform/risk/enforce.py:171` asserts `"risk/appetite.json is retired -- appetite is a
signed fact on party.yaml"` (ADR-0021). `tuppence/party.yaml:17` and
`ludlow/party.yaml:17` both still read "Copied from platform/risk/appetite.json". This
is exactly the platform-held-fixture pattern ADR-0021 retired, migrated on driftwood
(which has no such ConfigMap) and left in place on the other two — a live
cross-participant dependency on an artefact that no longer exists.

### P11 (minor, owned) — The platform still ships copies of the intelligence publisher's feeds, and one live consumer reads the copy

`platform/feeds/{threat-register,cve,eol}/{v1,v2}` exist alongside the `feeds` org
repo's own copies. Composition is clean — `platform/compose/composition.py:198`
resolves `{party: feeds, kind: feed, name: threat-register, version: v1}` to
`<estate>/feeds/threat-register/v1/feed.json`, i.e. the publisher's own tree — but
`platform/honesty/verify-honesty.sh:29` still reads
`src="$platform/feeds/threat-register/v1/register.json"`, the platform's own copy.
Listed in REVIEW-2026-08-31's minors and folded into ticket 57's Notes ("minor stale
feeds tree on platform (once first tag exists)"); the first tag now exists, so the
stated precondition has fired.

Note that `platform/feeds/schema.json` — the envelope contract — is exactly the kind of
shared thing §2 permits ("the only shared things are the artefact contracts and the
£"). Only the duplicated *payloads* are the finding.

### P12 (minor, owned) — driftwood's published forward-intel derives from a feed version driftwood no longer pins

`driftwood/twin/forward-intel/v1/feed.json` → `derived_from[0] = {party: feeds, kind:
feed, name: threat-register, version: "1"}`, while `driftwood/party.yaml` pins
`{party: feeds, kind: feed, name: threat-register, version: "v2"}`. Ticket 72 (open)
owns this exactly, naming both symptoms.

### P13 (minor) — every repo's two Flux objects for itself disagree about which of its own tags is current

In all three adopters, `gitops/flux-system/gotk-sync.yaml` self-pins `tag: v1.0.0` while
`gitops/composed/composed-set.yaml` pins that same repo's `tag: v1.1.0` (commits
`eacae33…`, `751522b…`, `a800a58…` respectively, each matching the real v1.1.0). Both
commits are correct for their tag — the disagreement is which tag. Separately,
driftwood's `gotk-sync.yaml:40` still says `path: ./apps` where tuppence's and
ludlow's say `path: ./gitops/apps` with a comment explaining that `./apps` "resolves to
nothing there and the Kustomization never becomes Ready" against the real GitHub
remote — the fix found on driftwood was never back-ported to driftwood.

### P14 (minor) — NORTH-STAR §2's own table is now stale in the estate's favour

The table still reads "*Does not exist yet.* Today the platform publishes four of five
feeds to itself" for the intelligence publisher row and "*Does not exist yet.*" for the
insurer row. Both orgs now exist, both carry gitsign-verified tags. Ticket 67 ("the
record matches the surface", open) is the plausible owner. Recording it so the ambition
document is not read as under-describing what was built.

### P15 (minor) — organisational separation is nominal, not enforced

All nine repos return `[]` from `repos/O/R/rulesets` and 404 from
`branches/main/protection` (I re-checked driftwood directly: `gh api
repos/policy-as-versioned-driftwood/driftwood/rulesets` → `[]`). Every merged
non-Renovate PR I sampled was authored and merged by the same identity — driftwood
#22, #21, #20, #19, #18, #16 and ludlow #12, #11, #10, #8, all `chrisns` / `chrisns`
(the fuller 46-PR sweep is `understand/github-live.md`, which I did not re-derive in
full). Nine organisations is a real topology and a real separation of *artefacts*; it
is not yet a separation of *authority* — no participant can technically refuse
another's change, and NORTH-STAR §2's "No participant reaches into another" rests on
convention plus `enact_guard.py`, not on GitHub.

---

## 3. Strengths, with evidence

1. **Signing is genuinely done, everywhere, and I verified it myself.** 24 of 24 tags
   across eight units return `Good signature … Validated Rekor entry: true` under
   `gitsign`, each identity-pinned to that repo's own `cut-release.yml` OIDC subject.
   Not one exception. This is the single most load-bearing §2 property and it holds.
2. **Eight of nine participants really are separate organisations with one repo each**,
   confirmed against the live API, with real remotes in the clones.
3. **The two pins that exist are exact.** I resolved every one against the real tag:
   platform `v2.0.1` → `533dccb0a823001b396fd60ab08014bf75065a37` (matches all three
   adopters' `platform-pin.yaml`); nist `v1.1.0` →
   `33a05df1f5241bca6ffbc1c69a70075cdb7a5819` (matches all three
   `gotk-sync-nist.yaml`); insurer's platform pin `v1.1.1` →
   `58ef9c57e53543997e5ddbe829a7b7c9a2282c60`. Tag *and* commit, both right, in every
   case. The pattern §2 asks for is built and correct where it is applied.
4. **One row has a real external datum.** nist's catalogue is the genuine NIST SP
   800-53 rev 5.2.0 OSCAL file; `scripts/verify_catalog.py` re-derives 1196 controls
   across 20 groups and the sha256 on disk matches `CATALOG_VERSION.json` exactly.
5. **Refusal beats guessing, in code, under live load.** The insurer's requote job dies
   with `REFUSED: missing instrument … there is no signed exposure to attach a layer
   to` rather than emitting a number; nist's clock writes "it looked and found none,
   which is a fact with a date on it, not a silence" rather than nothing. Both are the
   §5 three-outcome discipline showing up in participants' own code, not just the gate.
6. **The estate names its own defects in-tree, with dates.** `insurer/party.yaml`
   records the fabricated-`v1.2.0` laundering of 2026-08-29; tuppence's and ludlow's
   `gotk-sync.yaml` record why `./apps` never becomes Ready; driftwood's
   `gitops/apps/pod.yaml` records the `runAsNonRoot`-on-nginx kubelet defect and its
   `runAsUser: 101` fix. This is why an auditor can find things quickly here.
7. **The worst §2 breach is already owned, accurately.** Ticket 62's 2026-09-01 comment
   independently names the same twelve `ecosystem/thin-slice` checkouts I counted, and
   correctly notes the feeds half is now unblocked by feeds' real tags.

---

## 4. What I could not look at, and why

- I could not verify any tag's signature *from inside a workflow's own trust chain* —
  only from this machine, with network access to Rekor. REVIEW-2026-08-31's M2 (the CI
  trust-chain failure) is outside this dimension and I did not re-test it.
- I did not re-derive the full 46-PR merge-authorship sweep (P15); I sampled ten and
  cite `understand/github-live.md` for the rest.
- I did not resolve *what tree* `exposure_sha256: 397abe81…` was actually computed
  over for driftwood — only that it is neither v1.1.0 (no section) nor current HEAD.
- I did not run any adopter's `verify-*.sh` end to end (they need sibling checkouts
  wired as CI wires them, and several need a cluster).
- Org-level Actions permissions (`orgs/<org>/actions/permissions`) return 403 without
  `admin:org`; unchecked for all nine orgs.
