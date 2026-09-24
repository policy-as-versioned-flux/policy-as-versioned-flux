# 137 — A second feed of one publisher cannot verify offline

Type: task
Status: resolved
Blocked by: none

## Question

Charted 2026-09-24 by the integrator from ticket 136's named residual.

`compose()` keeps one parent tree per party. When a publisher's clone is absent, as in the
offline re-verify that tickets 45 and 110 promise, a second feed of the same publisher reads the
first feed's vendored tree and refuses: "observation does not belong to this feed pin and parent
SHA". Ticket 136's builder measured it on platform 38089a6 with a fixture of cve@v1 and eol@v2.

tuppence pins two feeds of the feeds publisher, threat-register@v1 and cve@v2, so its offline
verify is exposed. The refusal names itself and never prices from the wrong bytes, but it breaks
the portability promise: an adopter can no longer re-verify its own signed tree with the
publisher absent.

What this ticket owes:

1. `compose()` resolves a parent tree per feed edge, not per party, so each feed reads its own
   vendored tree when the publisher is absent.
2. A red-first test at the `compose()` seam: two feeds of one publisher at different majors
   verify byte-identically with the publisher present and absent.
3. Run `verify` for the real tuppence with the feeds clone absent, before and after.

## Done

An adopter that pins two feeds of one publisher re-verifies its signed tree byte-identically with
that publisher's clone absent.

## Build, 2026-09-22

Built 2026-09-24. Platform PR: https://github.com/policy-as-versioned-platform/platform/pull/41
(branch `ticket-137-parent-tree-per-feed-edge`, commit 6b812cf, based on platform main 82d5377).

### The fix

- `ParentTrees` is a `dict[str, Path]` that also carries `feeds`, a tree per feed edge keyed
  (party, name, version).
- With a publisher's clone absent, `compose()` now validates each feed edge's own vendored copy
  and records it under that edge. The party key keeps the first copy for party-level reads, as
  before.
- `edge_tree(edge, parent_trees)` serves every edge-level read: SHA resolution, pin content,
  price, supersede, the threat scenario, `as_of`, restatements and vendoring.
- `_portable_reason` strips the per-edge paths too, so a refusal reads the same on any machine.
- Every feed of an absent publisher is now digest-checked. Before, the loop skipped the second
  feed because the party key was already set, so only the first copy was checked.

### Tests (all run in this task)

- Red first at the `compose()` seam: new `TwoFeedsOfOnePublisherAtTwoMajors` in platform
  `compose/test_portable_observations.py`. One fixture publisher carries cve@v1 and eol@v2. The
  first test composes with the publisher present, then composes and verifies with it present and
  absent. The second test tampers the eol copy and expects a refusal by that feed's name. On
  82d5377 both failed. The error was "fixture-publisher/eol@v2 has no valid recorded publisher
  observation (observation does not belong to this feed pin and parent SHA)". Both pass on
  6b812cf.
- `python3 -m unittest <module>` in platform `compose/`: test_portable_observations 11 OK (the
  nine ticket 110 and 136 tests among them), test_comparison_history 29 OK, test_floor_change 9
  OK, test_machinery_delivery 5 OK, test_priority_classes 16 OK.
- `PAVC_ESTATE_CLONE=<estate> python3 composition.py --selfcheck`: rc=0, 102 OK lines. The estate
  was detached worktrees of every unit at origin/main: driftwood f0e9279, tuppence d18018d,
  ludlow 3f8c526, nist f83126f, ico abcb3a8, feeds ff3ac9a, insurer d1c1844, and platform on
  this branch. The selfcheck includes the ticket 110 portability leg.
- `bash compose/verify-composition.sh` on the same estate: rc=0, "PASS: the composition seam
  holds".
- mypy on `compose/composition.py` with the hub venv: 95 errors on 82d5377 and 95 on 6b812cf.
  Diffing the sorted lines finds no error added or removed. This is not a clean typecheck, and
  the hub typecheck is untouched because no hub code changed.

### The real tuppence, feeds clone absent

How I measured it: tuppence was a detached worktree at origin/main d18018d. Its parents were
fresh GitHub clones at the pins `read-pins.py` reads from its gitops files: platform v3.3.0
(38089a6), nist v1.1.0 (33a05df), ico v3.0.0 (9d09222), feeds threat-register/v1.0.0 (69c89b0).
Each HEAD matched its pinned commit. The feeds pin carries `cve/v2`. I removed the old-layout
`composed/feeds/` and composed with every parent present. Then I ran `composition.py verify`
three times: with all parents, with feeds absent, and with feeds and ico absent. I did this once
with platform main as the composer (before) and once with this branch (after).

| composer | verify, all parents | verify, feeds absent | verify, feeds and ico absent |
|---|---|---|---|
| main 82d5377 | rc=0 OK | rc=1, refused | rc=1, refused |
| branch 6b812cf | rc=0 OK | rc=0 OK | rc=0 OK |

On main the refusal was "feeds/feed@v2: missing instrument: feeds/feed/cve@v2: the pinned tree has
no cve/v2/feed.json". The cve edge read the threat-register copy. In tuppence the two feeds
resolve to different publisher SHAs (threat-register 50a0b330, cve ddace466). So even with the
path check passed, the observation check would still have refused.

With every parent present, main and the branch compose byte-identical tuppence trees (`diff -r`,
no output). With feeds absent, the branch composes the same 42 rendered files byte for byte.
Only `composed/evidence.json` differs, and it is not a rendered file. The difference is the
vendored-substitution limit: open with count 1 ("feeds") instead of closed.

This meets Done on the branch. tuppence pins two feeds of one publisher and re-verifies its
composed tree byte-identically with the feeds clone absent. What it does not yet cover is
tuppence's own committed tree, which v3.3.0 composed in the old layout. That waits on the
release and the recompose below.

### Decisions

- **D1 (delegated): carry the per-edge tree on a `dict` subclass, not a new argument.** About
  fifteen functions take `parent_trees`. Party-level reads (party.yaml, the FX converter search,
  the feed-publisher survey) still want one tree per party. Edge-level reads now go through one
  helper. The live path does not change: tuppence composed byte-identically under main and the
  branch with every parent present.
- **D2 (delegated): the party key keeps the first vendored copy.** This matches the old
  behaviour for party-level reads. In tuppence both copies carry the same `party.yaml` digest
  (204f41b1). Named limit: if two feeds pinned different publisher commits whose party.yaml
  differ, party-level reads take the first edge's copy. No adopter shows that today.
- **D3 (delegated): check every copy's digests, not just the first.** The old loop skipped the
  second feed once the party key was set, so a tampered second copy only refused later and under
  another name. The new tamper test holds it to its own digest.
- **D4 (delegated): no new selfcheck leg on the real tuppence.** tuppence's committed tree is in
  the pre-136 layout until the next recompose. The fixture test runs inside
  `verify-composition.sh`, which the gate runs. The real measurement is recorded here.

### What remains

- Merge platform PR 41 (integrator).
- A platform tools release carrying PR 40 and PR 41: waiting on the owner, who cuts releases
  and signed tags. I did not dispatch or tag.
- Each adopter then takes the release by Renovate and recomposes. That recompose must delete the
  old `composed/feeds/<party>/<version>/` directories. I measured what happens if it does not:
  with them left in place, `verify` failed on both composers with three lines "committed but no
  longer produced by a re-render", one per stale `party.yaml` (ico/v3, feeds/v1, feeds/v2).
- After that recompose, tuppence's own signed tree re-verifies with feeds absent. The truth run
  can grade it then.

## Answer

Resolved 2026-09-24 by platform PR 41, shipped in tools v3.4.0, and tuppence's recompose under
v3.4.x (PRs 39 and 40).

1. `compose()` keeps a parent tree per feed edge, so each feed of an absent publisher reads its
   own vendored tree and is checked against its own digests.
2. **Measured on tuppence at f1c2619** (tools v3.4.1), which pins feeds/threat-register@v1 and
   feeds/cve@v2: verify exits 0 byte for byte with every parent present, with the feeds clone
   absent, and with the feeds and ico clones absent.
3. That head is tuppence's served main, not a signed tag. Its next tag carries the same tree, and
   its cut-release pre-tag verify runs the same check.
