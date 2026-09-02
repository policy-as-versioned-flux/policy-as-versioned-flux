# Publisher repos: nist, ico, feeds, insurer

Scope: the four publisher units. Everything below was read from the fresh clones
under `scratchpad/units/{nist,ico,feeds,insurer}` unless marked otherwise, cross-checked
against GitHub via `gh` (each unit is its own GitHub org: `policy-as-versioned-<unit>`)
and against `gitsign verify-tag` run locally against the real Rekor transparency log
(network access was available). Driftwood/tuppence/ludlow clones were touched only to
verify claims insurer's `party.yaml` makes about them (out of this task's primary scope,
but load-bearing for insurer's honesty).

Not covered / not run: platform's own checkout (not in scope, referenced only where a
workflow checks it out as a dependency), `verify-feeds.sh` and `verify-market-and-news.sh`
end-to-end (they need a sibling `platform` checkout for the envelope schema — I did not
clone platform to run them; I read them and ran the parts that are self-contained:
`bump.py selfcheck`, `converters/fx.py selfcheck`), `verify-insurer-quote.sh` end-to-end
(same reason — needs sibling `nist`/adopter checkouts wired the way CI wires them; I did
the underlying cross-checks by hand instead, see Insurer section), `publish.sh` (nist —
not run, it seeds a git repo under `.work/`, avoided per the read-only/no-writes-under-units
rule), and `verify-insurer-party.sh` / `verify-catalog.sh` full runs where they need a
sibling `platform` checkout (both exit 3/SKIP without one; I ran their self-contained
sub-parts directly instead and report those).

---

## nist — `policy-as-versioned-nist/nist`

**party.yaml**: `roles: [publisher]`, `inherits: []`. Publishes one `kind: controls`
artefact, `name: sp-800-53`, `path: catalog`, `revoked: []`. No `payload_schema` (a
controls catalogue is OSCAL, not a feed envelope — party.yaml's own comment is explicit
about this distinction).

**Catalogue**: `catalog/NIST_SP-800-53_rev5.2.0_catalog.json`, 4,906,119 bytes, real
OSCAL content (verified: `catalog.metadata.title` = "Electronic (OSCAL) Version of NIST
SP 800-53 Rev 5.2.0 Controls and SP 800-53A Rev 5.2.0 Assessment Procedures", uuid
`ea7c7688-79c5-463b-a91b-0650f2d98623`). `CATALOG_VERSION.json` records
`sha256: d820835a...012024cb`; `shasum -a 256` on the file on disk **matches exactly**.
`scripts/verify_catalog.py` (pure read, run directly): `OK: 1196 controls across 20
groups, sha256 verified, NIST rev 5.2.0 (OSCAL 1.2.2)`. Source recorded:
`usnistgov/oscal-content`, upstream URL is the real NIST OSCAL GitHub raw URL,
`fetchedAt: 2026-07-31T00:00:00Z` — this is a one-time snapshot commit, not a live fetch
(see fetch.yml below).

**Baselines**: `BASELINE_VERSIONS.json` + three profile files (LOW/MODERATE/HIGH).
`scripts/verify_baselines.py` (run directly): `OK: LOW=149, MODERATE=287, HIGH=370, all
bare, all in the catalogue`; a fixture profile carrying an unknown id (`zz-999`)
correctly fails resolution.

**bump.yaml / rule.yaml**: `catalog/rule.yaml` — `changed_when: "a control id added
(minor), removed or renamed (major), or an existing control's text edited (patch)"`,
`entries: controls`, `numeric_tolerance: 0`. `catalog/bump.yaml` currently declares
`bump: none`. `.github/scripts/declared-bump-gate.py --selfcheck` (7 fixture cases) and
`--tree` (`OK: declared bump 'none' == computed bump 'none' (v1.1.0 -> v1.1.1)`) both
pass when run directly.

**fetch.yml**: cron `41 2 * * *`. This is **not** an upstream fetcher — its own header
comment says so plainly: *"nist's clock observes what is published rather than
comparing it against an upstream"* because "this repository ships no upstream fetcher
yet." Each run reads `party.yaml`'s own `publishes[]`, hashes the newest
`catalog/v<N>/feed.json` (there is none — nist's catalogue lives at `catalog/`, not
`catalog/v1/feed.json`), and appends a line to `observations/sp-800-53.jsonl` on the
`observations` branch, gitsign-signed. **No real external NIST source is ever fetched by
this repo's automation**; the catalogue is a one-time human-committed snapshot.
Confirmed live: `origin/observations:observations/sp-800-53.jsonl` carries exactly the
"no catalog/v<N>/feed.json in this repository yet" line, twice (2026-09-01, 2026-09-02).

**cut-release.yml / release.yml**: workflow_dispatch only; gitsign keyless (Actions OIDC
identity), tag immutability check, `release.yml` runs `scripts/verify-catalog.sh` as the
gate, verifies the tag with `gitsign verify-tag` pinned to
`^https://github\.com/policy-as-versioned-nist/nist/\.github/workflows/cut-release\.yml@refs/heads/(main|release/...)$`,
and publishes a GitHub Release.

**Tags**: `v1.0.0` (2026-08-21), `v1.1.0` (2026-08-25). Both **verify** with
`gitsign verify-tag` against the identity regexp above (`Validated Git signature: true`,
`Validated Rekor entry: true`, `Validated Certificate claims: true`).

**Finding — v1.1.0 was never released via `release.yml`.** `gh run list` shows
`cut-release` ran successfully for v1.1.0 (run 32867491295, 2026-08-25T15:42:45Z), but
the matching `release` workflow run does **not exist** — the only `release` run in the
repo's history is the one for v1.0.0 (32459930395, 2026-08-21). `gh release list` shows
only `v1.0.0`. So v1.1.0 is a real, gitsign-verified tag with **no GitHub Release and no
recorded run of the offline verify-catalog gate against it** — the tag exists but the
release pipeline was never dispatched for it (`release.yml` is `workflow_dispatch`-only
on the chained-tag path, and nobody ran it).

**Branches**: `main`, `observations` (2 commits, both `[skip observation]`-style
gitsign-signed "observe nist's published feeds"), plus stale WIP/renovate branches
(`ecosystem/thin-slice`, `policy-composition/tickets-09-16-wip`, `renovate/configure`)
not otherwise examined.

**Run history** (`gh run list`, 5 runs total, all `success`): 2× `fetch` (schedule,
2026-09-01/02), 2× `cut-release` (workflow_dispatch, 2026-08-21 and 2026-08-25), 1×
`release` (workflow_dispatch, 2026-08-21).

---

## ico — `policy-as-versioned-ico/ico`

**party.yaml**: `roles: [publisher]`. `inherits`: one entry, `{party: nist, kind:
controls, version: "1.1.0", since: 2026-08-28}` — pins nist's controls catalogue.
Publishes one `kind: feed`, `name: penalty-schema`, `path: penalty-schema`,
`payload_schema: penalty-schema/payload.schema.json`, `revoked: []`.

**Penalty schema — majors and real numbers.** Three payload majors on disk:
- **v1/v2** (`payload.schema.v2.json`, `required: [note, regimes]`): four regimes —
  `uk-gdpr` (ICO, UK GDPR/DPA 2018 s157, `pct_of_global_turnover` 4%/cap £17.5m
  higher-tier, 2%/cap £8.7m lower-tier — real cited fines: BA £20m/2020, Marriott
  £18.4m/2020, TikTok £12.7m/2023, Clearview £7.55m/2022, Doorstep Dispensaree
  £275k/2019, each with an ICO monetary-penalty-notice citation), `pci-dss`
  (card-scheme escalating monthly bands £5k–£100k/month), `hipaa` (US HHS OCR, Tier 4
  willful-neglect $68,928–$2,067,813, cites Anthem $16m/2018, Premera $6.85m/2020), `fca`
  (UK FCA five-step framework, DEPP 6.5, cites Standard Chartered £102.16m/2019, TSB
  £48.65m/2022).
- **v3** (current `payload.schema.json`, major 3): the v2 payload plus a
  `control_weights` block — per regime/violation-type, a list of `{source: nist, id,
  weight}` entries summing to 1.0, keying onto nist's pinned catalogue (e.g. uk-gdpr
  higher-tier: sc-28 0.30, ac-3 0.25, ac-6 0.20, au-2 0.15, ir-4 0.10).

**rule.yaml / bump.yaml**: `changed_when: "any formula rate or cap changes, any
real_example added, any weight changes"`, `entries: regimes`, `numeric_tolerance: 0`.
`penalty-schema/bump.yaml` currently declares `bump: major`, with a comment explaining
this was corrected 2026-08-29 (ticket 43) from a stale `none` that disagreed with what
was actually in the tree, and instructing: *"Set this back to `none` once v3.0.0 is
tagged and nothing further is queued."*

**Finding — bump.yaml is stale relative to its own instruction.** `v3.0.0` **is** now
tagged (2026-08-31), but `bump.yaml` still declares `major`. Running
`.github/scripts/declared-bump-gate.py --tree` today still reports `OK: declared bump
'major' == computed bump 'major' (v2 -> v3)` — the gate doesn't catch this because it
recomputes the bump between the two newest *published feed majors on disk* (v2, v3), not
against "is v3 already tagged." The declared value is technically self-consistent with
the gate's question but contradicts the file's own stated intent (the comment's cleanup
step was never done).

**Legacy `schema/` artefact shape** (separate from `penalty-schema/`, pre-dates the
ADR-0019 envelope): `schema/v1/penalty-schema.json`, `schema/v2/penalty-schema.json`,
each with a detached ed25519 signature (`sign.sh`/`verify.sh`, repo-local keypair,
explicitly labelled "ponytail: demo key" in the README). Ran `verify.sh v1` and `verify.sh
v2` directly: both report `Signature Verified Successfully` / `signature verified,
schema_version matches`. No `schema/v3` — the legacy shape was not updated for major 3.
`schema/to_fair_scenario.py` is the converter that turns a penalty-schema entry into a
`fair.py` scenario (FCA/HIPAA/PCI/GDPR handling all lives here as one publisher's
reading of four regimes — see feeds' `converters/README.md`, which documents this as a
known, named gap: none of FCA/HIPAA/PCI has its own converter yet because none of those
regimes has its own feed).

**fetch.yml**: identical pattern and code to nist's (cron `04:09` UTC instead of nist's
`02:41`) — confirmed by diff, only the cron, org name and commit identity differ. Same
"ponytail: this repository ships no upstream fetcher yet" comment. **No real external ICO
enforcement-notice source is fetched**; the fine figures are one-time human-authored
content (with cited sources in the payload itself), not live-pulled.

**cut-release.yml / release.yml**: same shape as nist's.

**Tags**: `v1.0.0` (2026-08-21), `v3.0.0` (2026-08-31) — **no `v2.0.0` tag was ever cut**
(the v2 payload exists on disk/in `git log` but was never released as a signed tag; only
v1 and v3 went through `cut-release.yml`). Both existing tags **verify**
(`gitsign verify-tag`, identity-pinned to
`.../ico/.github/workflows/cut-release.yml@refs/heads/main`): `Validated Git signature:
true`, `Validated Rekor entry: true`, `Validated Certificate claims: true`.

**Finding — same v1.1.0-class gap as nist: v3.0.0 has no GitHub Release.** `gh run list`
shows `cut-release` succeeded for v3.0.0 (run 33406040611, 2026-08-31T15:01:31Z); the only
`release` workflow run in the repo's history is for v1.0.0 (32459940693, 2026-08-21).
`gh release list` shows only `v1.0.0`. v3.0.0 is signed and verifiable but has never been
through the offline release gate or had a GitHub Release published.

**Run history** (`gh run list`, 5 runs, all `success`): 2× `fetch` (schedule, 09-01/09-02),
2× `cut-release` (2026-08-21, 2026-08-31), 1× `release` (2026-08-21 only).

---

## feeds — `policy-as-versioned-feeds/feeds`

**party.yaml**: `roles: [publisher]`, `inherits: []`. Publishes five feeds:
`threat-register`, `cve`, `eol`, `fx`, `market-moves`, `news` (six, not five — I
miscounted; all six listed with their own `path` and `payload_schema`, `revoked: []`
each).

**Envelope / bump machinery**: `bump.py` at repo root is the shared ladder every feed's
`rule.yaml` parametrises (`entries`, `numeric_tolerance`, optional `minor_when_changed`,
optional `series`/`series_value`/`move_threshold`). Ran `python3 bump.py selfcheck`
directly: **21/21 cases pass** (generic ladder, fx's `minor_when_changed: period`,
market-moves' series-threshold logic, news' list-keyed-by-id logic).

**Per-feed rule.yaml / bump.yaml** (all six currently declare `bump: none`):
- `threat-register`: `changed_when: "institution added/removed, or lef moves >10%"`,
  tolerance 0.10.
- `cve`: `"cve added/removed, or cvss/epss moves >5%"`, tolerance 0.05.
- `eol`: `"component added/removed, or base rate moves >10%"`, tolerance 0.10.
- `fx`: `"a new monthly period, a currency added/withdrawn, or a corrected rate"`,
  tolerance 0, `minor_when_changed: period`.
- `market-moves`: one mechanical selection rule over Polymarket-shaped data
  (`categories`, `min_liquidity: 50000`, `min/max_horizon_days: 7/365`, `max_markets:
  40`, `sample_seed: 20260829`, `rule_version: 1`), threshold `move_threshold: 0.05` (5
  price points), `minor_when_changed: selection_rule`.
- `news`: admission mechanics only (`requires_provenance_url: true`, `max_age_days:
  365`, `rule_version: 1`); "an admitted event not already published" = minor, a
  withdrawal = major, a restatement = patch.

**Real published numbers**:
- `fx/v1`: period `2026-08`, base GBP, 14 currencies (USD 1.284, EUR 1.1735, JPY
  191.42, etc.) — shaped like the real HMRC monthly customs/VAT rate table.
- `cve/v2` (4 CVEs): `CVE-2024-1234-envoy` (cvss 9.1, epss 0.42, istio/envoy),
  `CVE-2023-4567-curl` (7.5/0.18), `CVE-2023-9999-openssl` (5.3/0.06),
  `CVE-2024-8888-istiod` (9.8/0.55, added in the v1→v2 bump per its changelog).
- `eol/v2` (4 components): python-3.9 (eol 2025-10-31), ubuntu-20.04 (eol 2025-04-30),
  istio-1.18 (eol 2024-02-21), kyverno-1.10 (eol 2024-08-01, added in v2) — each with
  `base_lef`/`base_lm_gbp` triples and an `endoflife.date/...` source citation.
- `threat-register/v2` (3 institutions): driftwood (cart/checkout PII exfiltration,
  lef [2,4,9]), tuppence (payment-fraud/ATO, lef [4,9,20], raised from [3,6,14] in v2 per
  its own changelog "reflects the 2026 uptick in API-based account-takeover fraud...
  industry roundup, not a driftwood-specific incident"), ludlow (health-record
  exfiltration, lef [1,2,5]) — each keyed to a DBIR sector base rate, editorial midpoint.
- `market-moves/v1`: 7 Polymarket-shaped markets across regulatory/macro/geopolitics/
  technology/sports categories with price-level series.
- `news/v1`: 5 pool entries, 4 admitted with real provenance URLs, 1 deliberately
  refused for having none (see below).

**Definitive finding — no feed has ever ingested a real external datum.** Every
`fetch/<feed>.py` reads via `fetch/lib.py`'s `read_upstream()`, which is explicitly a
**committed fixture** under `fetch/source/<feed>.json`, never a network call. Each
script's own header names the real upstream it stands in for and calls itself
"ponytail" (a deliberate placeholder), e.g.:
  - `cve.py`: `UPSTREAM = "https://api.first.org/data/v1/epss + trivy image scan"` —
    upgrade path named, not implemented.
  - `eol.py`: `UPSTREAM = "https://endoflife.date/api/"` — not called.
  - `fx.py`: `UPSTREAM = "https://www.gov.uk/.../exchange-rates-for-customs-and-vat"` —
    not called.
  - `threat-register.py`: `UPSTREAM = "https://www.verizon.com/.../dbir/"` — not called.
  - `market-moves.py`: `UPSTREAM = "https://gamma-api.polymarket.com/markets"` — not
    called; its own fixture (`fetch/source/market-moves.json`) states in its own comment
    that the seven markets are **"ILLUSTRATIVE, in the venue's published shape and
    magnitude — this is not a fetch of Polymarket."**
  - `news.py`: `UPSTREAM = "publisher release records in the policy-as-versioned
    organisations"` — and indeed, the four admitted events' provenance URLs are GitHub
    Release pages of **this same estate's own sibling repos**
    (`.../policy-as-versioned-ico/ico/releases/tag/v1.0.0`,
    `.../policy-as-versioned-platform/platform/releases/tag/policy%2Fv3.0.0`,
    `.../policy-as-versioned-nist/nist/releases/tag/v1.1.0`,
    `.../policy-as-versioned-platform/platform/releases/tag/v1.1.1`) — these are real,
    verifiable GitHub Releases, but they are the estate's own self-referential events,
    not third-party news. The fifth entry (`an-unsourced-statement`, no provenance URL)
    is deliberately present to prove the admission rule refuses it, per `news/rule.yaml`.

**cut-release.yml**: unlike nist/ico, tags are per-feed: `<feed>/vX.Y.Z` (own comment
explains why: multi-feed repo). Checks out a pinned `platform` tag (`v2.0.1`) for the
envelope schema, gates on `./verify-feeds.sh` and `./verify-market-and-news.sh`. Also
carries a declared/computed bump agreement concept inside `verify-feeds.sh`
(`bump.py` selfcheck + rule-vs-payload cross-checks), but — unlike nist/ico — there is
**no `declared-bump-gate.py`-equivalent script that refuses a mismatched *declared* bump
before tagging a specific version**; the gate only proves the ladder is internally
consistent, not that this feed's own `bump.yaml` agrees with what's about to be tagged.

**Tags**: only `threat-register/v1.0.0` and `threat-register/v2.0.0` exist. **cve, eol,
fx, market-moves, and news have never had a single tag cut**, despite cve and eol having
published v2 payloads and fx/market-moves/news having published v1 payloads sitting in
the tree. Both threat-register tags verify (`gitsign verify-tag`,
`Validated Git signature/Rekor entry/Certificate claims: true` each). `gh release list`
confirms: only `threat-register/v1.0.0` and `threat-register/v2.0.0`.

**Live, currently-failing automation — two distinct, reproducible bugs, both active as
of today.**

1. **`gh run list` shows the scheduled `fetch` workflow failed outright on both of its
   only two runs** (2026-09-01T08:37Z, run 33488014777; 2026-09-02T07:54Z, run
   33605912295) — **every one of the 6 matrix jobs failed on both days** except
   `market-moves` on 09-01. Root causes, read directly from the run logs:
   - **09-01**: for cve/eol/fx/threat-register/news, `bump.py` computed a non-`none`
     verdict (e.g. cve: `patch`, version `2.0.1`) and the "propose PR" step tried to
     `gh pr create`, which failed with `GraphQL: GitHub Actions is not permitted to
     create or approve pull requests (createPullRequest)`. Because this step has no
     `continue-on-error`, the whole job aborted there — the observation-append step
     (which runs "unconditionally" per its own comment) **never executed** for those
     five feeds that day. `market-moves` alone computed `none` and succeeded straight
     to the observation branch (confirmed: `origin/observations:observations/
     market-moves.jsonl` has exactly one line, 2026-09-01T08:38:41Z; no
     `cve.jsonl`/`eol.jsonl`/`fx.jsonl`/`threat-register.jsonl`/`news.jsonl` exist on
     that branch at all).
   - **09-02**: the five feeds whose `fetch/<feed>-<version>` branch was already open
     from 09-01 correctly short-circuited ("`fetch/eol-2.0.1` already open — nothing to
     propose", exit 0) and fell through to the observation-append + cage steps — where
     **all six jobs, including market-moves this time, failed** on
     `"::error::the scheduled fetch left a change outside the observation lane"`,
     citing untracked `__pycache__/bump.cpython-312.pyc` and
     `fetch/__pycache__/lib.cpython-312.pyc`. Root cause: `.gitignore` (which lists
     `__pycache__/`) exists only on `main`; the cage step operates after `git checkout
     --orphan observations` / `git checkout observations`, and the `observations`
     branch (by design, per its own multi-paragraph comment about the 2026-08-28 bug)
     carries no `.gitignore` at all — so Python's own bytecode cache, generated by
     `python3 fetch/<feed>.py` importing `lib.py`/`bump.py` earlier in the same job,
     shows up as untracked on that branch and trips the "anything outside
     OBSERVATION_LANE fails the run" check. **This has broken the feeds repo's daily
     automated fetch for both days it has existed**, for every one of the six feeds at
     least once, and for all six simultaneously on the most recent run.
   Evidence: `gh run view 33605912295 -R policy-as-versioned-feeds/feeds --log-failed`
   and `gh run view 33488014777 -R policy-as-versioned-feeds/feeds --log-failed`
   (job-by-job).

**Observations branch** (`origin/observations`): only two files exist —
`observations/README.md` and `observations/market-moves.jsonl` (2 lines total, both
`bump: none`, carrying `price_levels` readings). No observation was ever successfully
recorded for cve, eol, fx, threat-register, or news, because of the bugs above.

**Run history** (`gh run list`, 7 runs): 2× `fetch` schedule (both **failure**), 2×
successful `cut-release`+`release` pairs (threat-register v1.0.0 and v2.0.0, both
2026-09-01), 1× `cut-release` **failure** (2026-09-01T07:11Z, not investigated in
detail — precedes the two successful cut-release runs the same day, likely an input
mistake later corrected).

---

## insurer — `policy-as-versioned-insurer/insurer`

**party.yaml**: `roles: [publisher, insurer]`, `reporting_currency: GBP`. `inherits`:
four entries — `{platform, kind: implementations, version: "1.1.1"}` and one
`{party: <adopter>, kind: feed, name: exposure, version: "v1.1.0"}` each for driftwood,
tuppence, ludlow. Publishes `quote-driftwood`, `quote-tuppence`, `quote-ludlow`
(`path: quote/<adopter>`, shared `payload_schema: quote/payload.schema.json`).

**Notable — party.yaml's own comment documents a prior real defect and its fix.** The
file's comment block states verbatim that these three exposure pins used to read
`"v1.2.0"` — a tag *no adopter had ever cut*, with no adopter's `publishes[]` even
carrying a feed called `exposure` at the time — so "the fabricated version was laundered
into driftwood's own signed evidence.json as the provenance of a six-figure cost line
(found 2026-08-29)." The comment says it is now pinned to `v1.1.0`, described as "the
highest tag each adopter has actually signed and the one whose tree carries the exposure
section."

**Finding — that claim is not correct, and the same class of defect is still live.**
I checked the three adopters' actual git history (via their fresh clones and via `gh api
repos/policy-as-versioned-<x>/<x>/tags`, which confirms `git tag -l` is complete: each of
driftwood, tuppence, and ludlow has **only** `v1.0.0` and `v1.1.0`, nothing higher):

- `git -C driftwood show v1.1.0:composed/HEADER.yaml` parses to a document with **no
  `exposure` key at all** (top-level keys at v1.1.0: `policy-as-versioned.dev/composed,
  parents, baseline, governed-namespaces, holes, selected-controls,
  ungoverned-namespaces`). The `exposure` key was added later, in commit `ceac84b`
  ("ecosystem ticket 36: pin the insurer's quote and sign the exposure section") —
  confirmed `git merge-base --is-ancestor v1.1.0 ceac84b` (true, so it postdates the
  tag) and `git tag --contains ceac84b` returns **nothing** (no tag, on any of the three
  adopters, has ever included this commit). The same is true for tuppence and ludlow
  (`exposure` present at HEAD, absent at `v1.1.0`, in both).
- This is exactly reproduced **live in CI, today**: the insurer's `fetch.yml` `requote`
  job checks out each adopter at `git ... ref: <the pinned tag>` (into
  `.adopters/<adopter>`) and runs `pricing/quote.py bump`. `gh run view 33615860064`
  (2026-09-02, `schedule`) shows **all three `requote (driftwood|tuppence|ludlow)` jobs
  failing** with the identical refusal:
  `REFUSED: missing instrument: .adopters/<adopter>/composed/HEADER.yaml carries no
  `exposure` section -- there is no signed exposure to attach a layer to`. The prior
  day's run (33496526156, 2026-09-01) shows the same. So **the insurer's own pricing
  clock has been unable to re-quote any of its three insured adopters for at least two
  consecutive days**, because the pin it trusts points at a tag whose tree genuinely does
  not carry what the pin claims it carries.
- Separately (comparing the *published* quote feeds against the adopters' *current main*
  HEAD, not the pinned tag, as a sanity check on drift): `quote/tuppence/v1/feed.json`
  and `quote/ludlow/v1/feed.json` each record an `exposure_sha256` that **matches
  exactly** a fresh hash of their current `composed/HEADER.yaml` `exposure` section
  (computed independently with the same canonical-JSON method `pricing/quote.py` uses).
  `quote/driftwood/v1/feed.json`'s recorded `exposure_sha256`
  (`397abe81d6cbdbd7b27a5d2516dd9c35417e9922f995b8b6af7d1fca34829820`) does **not** match
  driftwood's current HEAD exposure (`5822260bab861329b13b78e2a865b1801ebe83d1b2cb7e23e84871f4bad19241`)
  — driftwood's exposure has moved since the quote was rendered and driftwood has not
  been re-priced. So: two of three quotes are at least internally consistent with the
  adopter's *current unsigned* state (but not with the *tag* the pin names, which is the
  thing actually meant to be trustworthy); the driftwood quote isn't even consistent with
  that.

**pricing/quote.py**: formula `layer-rate-on-line` v1.0.0 — `excluded` (sum of excluded
regime/control amounts from the adopter's own signed exposure), `insured = total -
excluded`, `layer = clamp(insured - attachment, 0, limit)`, `premium = round(layer * rate
* (1+load), 2)`. `attachment` is explicitly **not** restated by the insurer — it is read
from the adopter's own signed appetite. Every `Refused` (missing-instrument) path is a
hard exception, never a guessed number (checked: currency mismatch across terms/exposure,
an exclusion naming an unpriced regime/control, a missing composed artefact). Ran
`python3 pricing/quote.py selfcheck` directly: **all 7 assertions pass** (formula
arithmetic, limit clamping, zero-layer-when-below-attachment, whole-regime exclusion,
every refusal path, digest stability, and the bump/tolerance rule).

**terms/{driftwood,ludlow,tuppence}.yaml**: real, distinct, signed rate cards — limits
£3m/£4m/£5m, rates 3.5%/4.5%/3%, loads 25%/35%/30%, each with its own named exclusions
(keyed to nist control ids pl-2/ra-3/ca-2, with rationale citing ico's published control
weights) and conditions (`ac-6` → void if least-privilege lapses; `cm-6` → a stated £
uplift if config-drift is found), each cross-referenced against nist's real catalogue ids.

**quote/rule.yaml (per adopter)**: `changed_when: "the premium moves by more than 2%, or
the attachment, the limit, any exclusion or condition, the validity dates or the pinned
exposure sha256 changes at all"`, tolerance 0.02. Each adopter's `quote/<adopter>/bump.yaml`
currently declares `bump: none`.

**Published quote v1/feed.json (driftwood, worked example)**: attachment £40,000, limit
£3,000,000, one exclusion (uk-gdpr pl-2+ra-3), premium **£113,403.30** to driftwood,
formula intermediates `excluded £1,072,306.25 / insured £2,632,075.49 / layer
£2,592,075.49`, `priced_against` names `platform 1.1.1` and `driftwood exposure v1.1.0`
(the now-fixed-in-appearance-but-still-inaccurate pin discussed above).

**cut-release.yml**: **notably thinner than nist/ico's** — it has the tag-immutability
check and the gitsign-tag/push steps, but **no declared-bump-gate step at all** (diffed
directly against ico's cut-release.yml: ico has two extra steps — "the tag must name a
real, released feed version" and "the declared bump must agree with the computed bump
(ticket 43, 18 Answer 5)" calling `.github/scripts/declared-bump-gate.py` — neither
exists in insurer's workflow, and insurer's `.github/scripts/` directory does not exist
at all). Ticket 43's bump-agreement gate, present in nist and ico, has not been ported to
insurer (nor to feeds, which also has no `declared-bump-gate.py`; feeds' `verify-feeds.sh`
only self-checks `bump.py`'s ladder, it does not check the actual declared value for the
version about to be tagged).

**release.yml gate**: `./verify-insurer-party.sh` (checked: needs a sibling `platform`
checkout for its schema-validation step, `exit 3`/SKIP without one; its self-contained
checks — party.yaml parses, roles include insurer+publisher, publishes[] paths exist,
payload_schema files parse — are straightforward and not independently re-run here
beyond reading the script).

**`.github/rulesets/observation-lane.json`**: identical restricted-path ruleset to
nist/ico/feeds. **Finding**: insurer's `.github/rulesets/README.md` carries an extra,
self-documented caveat not present in the other three repos' copies of this file — it
explicitly states the ruleset "is inert today (this repo is public, so the ruleset
cannot be applied at all)" and flags that the `requote/*` proposal branches
(`fetch.yml`'s `requote` job) would, in principle, collide with the same restricted-path
list feeds' `fetch/*` branches use, and that this needs "a carve-out" the owner hasn't
yet chosen among three named options. In other words: the branch-protection ruleset this
repo ships is known, in its own README, to not actually be enforced.

**gitops/platform/platform-pin.yaml**: a real Flux `GitRepository` document (no
`Kustomization` — insurer runs no cluster, by design, per an extensive comment
explaining why `party_artefact.py` needs this file to resolve the `platform/
implementations` edge even for a non-cluster-running consumer), pinned to
`policy-as-versioned-platform/platform` tag `v1.1.1`, commit `58ef9c57e5...2c60`.
`renovate.json` carries a matching `customManagers` regex (`git-refs` datasource) to keep
`tag` and `commit` bumped together — the same pattern driftwood/tuppence/ludlow use for
their own platform pins.

**Tags**: only `v1.0.0` (2026-08-21 per `gh release list`'s date, though the tag/PR
history shows the actual cut-release+release pair ran 2026-09-01T07:11-07:12Z — the repo
was evidently re-created/renamed around ticket 57's "register workflows" commits, see
`git log`: `632db22 register workflows, second attempt`, `8172962 register workflows...
push event so GitHub indexes .github/workflows/ after the rename to main`). Verified:
`gitsign verify-tag v1.0.0` against
`.../insurer/.github/workflows/cut-release.yml@refs/heads/main` — `Validated Git
signature/Rekor entry/Certificate claims: true`.

**Run history** (`gh run list`, 4 runs): 1× successful `cut-release`+`release` pair
(2026-09-01, v1.0.0), and **2× scheduled `fetch` runs, both `failure`**
(2026-09-01T10:16Z run 33496526156, 2026-09-02T09:45Z run 33615860064) — broken down
above into `fetch` (the plain observation job, which **succeeds**: it only observes
insurer's own already-published quote feeds) and `requote` (which **fails on all three
adopters both days**, per the exposure-pin defect above).

---

## Cross-cutting facts worth an auditor's attention

- **All four repos' `cut-release.yml`/`release.yml` use the same gitsign keyless-signing
  and identity-pinned-verification pattern**, and every tag I checked across all four
  repos (nist ×2, ico ×2, feeds ×2, insurer ×1 — 7 tags total) **verified successfully**
  against Rekor with `gitsign verify-tag`, identity-regexp-pinned to that repo's own
  `cut-release.yml@refs/heads/main`. I found no forged or unverifiable tag anywhere in
  this scope.
- **Two repos (nist, ico) have a tag that was cut but never carried through
  `release.yml`** (nist v1.1.0, ico v3.0.0) — signed and verifiable, but with no GitHub
  Release and no recorded run of the offline release gate against that specific tag.
- **feeds' scheduled `fetch.yml` is currently, actively broken** for two independent,
  reproducible reasons (GH-Actions PR-creation permission denial; untracked
  `__pycache__` tripping the observation-lane cage on a branch with no `.gitignore`),
  confirmed via live `gh run` logs from the two most recent scheduled runs (2026-09-01,
  2026-09-02) — every one of the six feeds has failed to log a successful daily
  observation at least once, and only `threat-register` has ever been formally released.
- **insurer's exposure pins name a tag (`v1.1.0`, all three adopters) whose tree
  genuinely does not carry the `exposure` section being priced from** — this is not a
  copy-paste residue of the previously-found-and-"fixed" fabricated-`v1.2.0` bug; it is
  the same underlying problem (a pin naming something that isn't really there)
  recurring under the corrected version number, and it is provably, currently breaking
  the insurer's own daily re-quote automation for all three adopters (`REFUSED: missing
  instrument`, both of its two runs to date).
- **No feed in the `feeds` repo, and no catalogue/schema in `nist`/`ico`, has ever
  ingested a real external datum through its automation.** Every number is real-world
  *grounded* (cited NIST/ICO/HHS/FCA/DBIR/endoflife.date/HMRC-shaped sources, named in
  the payloads themselves) but every payload was **authored by a human and committed
  directly**; the scheduled "fetch" clocks that exist read fixtures, not the network, and
  every script says so in its own header comment.
- **Coverage gap on the ticket-43 declared-bump gate**: present in nist and ico, absent
  from feeds and insurer (feeds has a self-check of the ladder but not a
  declared-vs-computed-for-this-tag refusal; insurer has neither).

## Files not covered / could not fully verify

- Did not run `nist/scripts/publish.sh` (writes a seed repo under `.work/`, avoided —
  script itself was read and is idempotent/local-only by design, no push).
- Did not run `feeds/verify-feeds.sh`, `feeds/verify-market-and-news.sh`,
  `feeds/verify-news-headline-skill.sh`, `insurer/verify-insurer-party.sh` (full),
  `insurer/verify-insurer-quote.sh`, or `nist/scripts/verify-catalog.sh` (full) to
  completion — each needs a sibling `platform` (and in the insurer verify-quote case,
  sibling adopter) checkout wired the way CI wires it, which I did not build; I read
  each script and ran the self-contained portions directly instead (`bump.py selfcheck`,
  `converters/fx.py selfcheck`, `declared-bump-gate.py --selfcheck`/`--tree`,
  `pricing/quote.py selfcheck`, `verify_catalog.py`, `verify_baselines.py`,
  `verify-cert-identity-regexp.sh`, `schema/verify.sh` v1/v2).
- Did not investigate the one `cut-release` **failure** run in feeds' history
  (33480935507, 2026-09-01T07:11:21Z) beyond noting it preceded two same-day successes —
  plausible operator error on a first attempt, not chased further given time.
- Did not examine driftwood/tuppence/ludlow beyond the narrow cross-checks needed to
  verify insurer's factual claims about them (their own full publisher/adopter shape is
  out of this task's scope).
- Did not examine the `policy-as-versioned-platform/platform` repo directly (out of
  scope; referenced only as a dependency several workflows check out).
