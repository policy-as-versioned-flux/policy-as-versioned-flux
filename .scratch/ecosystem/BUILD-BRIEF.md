# Build brief — the thin slice, 2026-08-28

Read this first. Then read `spec.md` in this directory. Then the `## Answer` section of the
ticket you build (`issues/NN-*.md`). Then the ADRs it names (`docs/adr/0019` to `0023` at the hub
root). Vocabulary is `CONTEXT.md` at the hub root. The one sentence is `NORTH-STAR.md` §1.

## Where things are

Hub repo (this repo): `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux`.
- `talk/verify-all.sh` is the gate. It globs every `verify*.sh` under `.estate-clone/` and
  `verify/`, runs each, grades by exit code: 0 pass, 3 could-not-look (SKIP), else fail.
- `verify/<name>/verify-<name>.sh` are the hub's cross-party checks. Prior art:
  `verify/party/verify-party.sh`, `verify/provenance/`, `verify/proportionality/`.
- `clone-estate.sh` assembles `.estate-clone/`. Its `UNITS` list must gain `feeds insurer`.
- `twin/` is the twin (python package, entry `bin/twin`). `.venv/bin/python` has pyyaml and
  jsonschema. Estate scripts call plain `python3` (3.14, has pyyaml, NO jsonschema; prefer stdlib).

Unit repos, each a real GitHub repo, cloned under `.estate-clone/<unit>/`, each checked out on a
local branch **`ecosystem/thin-slice`**:
- `platform` (publisher, implementations). Key files: `compose/composition.py` (2440 lines,
  renders adopters' `composed/`), `graded/cage.py` (tier table, selection), `fair/fair.py` (£),
  `computed-semver/cage_engine.py` (classifies policy changes into bumps), `party/schema.json`
  and `party/party_artefact.py`, `distribution/policies/v3.0.0/{cage-tier,cage-netpol}.yaml`
  and `graded/policies/` (the served copies of the cage), `feeds/` (threat-register, cve, eol),
  `wardley/intel/market-intel.json`, `risk/appetite.json`, `wargamer/tier_pr.py` (proposer),
  `honesty/rejections.json`, `distribution/versions.yaml`.
- `driftwood`, `tuppence`, `ludlow` (adopters). `party.yaml`, `composed/` (rendered, includes
  `HEADER.yaml`, `evidence.json`), `gitops/` (Flux), `deploy/pod.yaml`, `.github/workflows/`
  (`propose-tier.yml`, `cut-release.yml`, `release.yml`, `renovate-run.yml`, `shift-left.yml`),
  `.github/scripts/adopter-gate.py`, `scripts/lib.sh` (`need_substrate`, `skip`), `drift/`.
- `nist` (regulator, controls: OSCAL catalogue + baselines), `ico` (regulator, penalty schema
  under `schema/v1`, `schema/v2`, with `.sig` files and a `to_fair_scenario.py`).
- `feeds` and `insurer`: **empty repos**, no commits. Author them from scratch on the branch.

Local branches only. Five upstream PRs are already folded into the branches (platform #3, #4;
driftwood #11; tuppence #8; ludlow #7).

## Hard rules

1. **Never push. Never merge a PR. Never create a tag.** Commit on `ecosystem/thin-slice` in each
   unit you touch, one commit per logical change, message in plain English, first line under 72
   chars. The hub repo: commit on `main` locally, do not push. The owner pushes and merges.
2. **Definition of done is a verify script in the gate.** Every ticket lands one `verify-*.sh`
   that `talk/verify-all.sh` discovers by glob. Contract: exit 0 = observed true; exit 3 = could
   not look, with the reason on the last line as `SKIP: <reason>`; any other exit = observed
   false, with `FAIL: <reason>` on the last line. A live check asserts its substrate first
   (`docker info`, `kind get clusters`, Flux Ready) and exits 3 if absent. Offline checks run
   offline. Never turn absence into pass.
3. **Signed tags cannot be cut locally.** Tags are cut by each repo's `cut-release.yml` in Actions
   with gitsign. A check that needs a signed tag on the real remote exits 3 with a reason naming
   the tag it waits for, until the owner merges and the workflow runs. Do not fake a signature.
4. **Price and cage. Never count, refuse or file. No gate. No exemption.** If code needs a
   refusal, the only allowed refusal is a missing instrument (ADR-0020: no price for a declared
   regime, no FX rate for the date). Every other missing thing is priced.
5. **A clock appends observations, never declarations (D1).** Scheduled workflows may append
   `truth.log`, `drift/samples.jsonl`, captures. They never commit a tier, pin, floor, overlay,
   or evidence file. Proposals are PRs a human merges.
6. **One signature, the gitsign tag (D3).** No cosign bundles, no SSH keys, no `.sig` files for
   new artefacts. Existing `.sig` files stay until their feed migrates.
7. **Every price carries `perspective` and `currency`. No sum crosses perspectives.**
8. **One render of Namespace tier to pod label: `cage-tier` via `namespaceObject`.** Pod label is
   an output. Unknown or missing tier fails closed to `isolated`. Ladder:
   `baseline, restricted, quarantine, isolated, infra`. `infra` only from a `platform`-role party.
9. **Do not edit `CONTEXT.md` casually.** Add a term only if the build introduces one. Do not
   rewrite ADRs; add a dated banner if you supersede one.
10. **Report honestly.** Your final report lists: files changed per repo, commits made (hash and
    message), the exact command you ran to verify and its last five lines, and what you did not
    do. A claim without a command output is a fail.
11. `ponytail`: smallest diff that works. Reuse what exists (fair.py, cage.py, party_artefact.py,
    adopter-gate.py, lib.sh). No new frameworks. No new dependencies beyond pyyaml/jsonschema in
    the hub venv. Mark deliberate ceilings with a `ponytail:` comment naming the upgrade path.
12. Do not touch `.work/`, `__pycache__`, `.venv`, `estate/` (stale), `.scratch/talk-spec/`.

## How to run things

- One verify script: `bash .estate-clone/<unit>/<path>/verify-x.sh` from the hub root, or
  `bash verify/<name>/verify-<name>.sh`.
- The gate (slow, minutes): `bash talk/verify-all.sh` from the hub root. Only the integration
  agent runs it. The TRUTH line is the last line.
- Composition: `python3 .estate-clone/platform/compose/composition.py --help` and its `selfcheck`.
- Kyverno offline: `kyverno test <dir>` and `kyverno apply --values <file>`. Kyverno CLI 1.18.2.
  `namespaceObject` in a MutatingPolicy is evaluated offline through a Values file `namespaces:`
  list (proven 2026-08-28; see `.scratch/ecosystem/research/kyverno-1.18-cage-facts.md`).
- KinD: clusters `driftwood`, `tuppence`, `ludlow` exist locally. Do not delete them. An
  ephemeral cluster for the harness must use a fresh name and delete itself.
- Python: `.venv/bin/python` (hub), `python3` (estate scripts).

## Build order and ownership

21 feed contract → 25 £ seam → 26 cage, 28 clocks, 32 identity (parallel) → 40, 41, 42 Flux →
29, 49, 50 twin → 43 release, 47 deck. Ticket 52 (the harness) starts with step skeletons that
exit 3 and grows one step per phase. Each phase runs as one workflow; each agent owns whole
repos, never a file another agent is editing at the same time.
