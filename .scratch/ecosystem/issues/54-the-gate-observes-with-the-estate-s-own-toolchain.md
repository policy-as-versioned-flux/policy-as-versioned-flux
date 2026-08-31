# 54 — The gate observes with the estate's own toolchain

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

truth.yml pins kyverno 1.19.0 by accident (db47f88 was a URL fix) while the estate is authored against 1.18.2, so cage-tier 4.0.0 fails CEL compilation and reds verify-graded, verify-shift-left and verify-render-version-tree in every citable run. Either fix the expression (e.g. string(variables.tier)) so the policy loads on >=1.19 — cut through the release machinery if the engine computes a bump — or pin 1.18.2 with a written reason in the workflow; if the choice needs the owner, raise it inside ticket 58's round rather than assuming. Also: add jsonschema to the pip line (or build the .venv the scripts probe for) so e2e-step1, e2e-step6, feed-contract and twin-overlay can look; pin cosign by version and sha256 like gitsign. Done = the three CEL reds and four jsonschema SKIPs convert on a scheduled TRUTH run, and the toolchain pins each carry a reason.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: C1 (kyverno skew, 4 confirmed findings), M5 (jsonschema, 2 confirmed findings), minor cosign-unpinned.
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Answer (2026-08-31)

Decided by test, not judgement: **pin the gate to kyverno 1.18.2**, the version the estate is
authored and specified against (`.scratch/ecosystem/research/kyverno-1.18-cage-facts.md`).

The A/B proof, with both real binaries and the same estate:

| check | kyverno 1.18.2 | kyverno 1.19.0 |
|---|---|---|
| `verify-graded.sh` | rc=0 | rc=1, `cage-tier mutate matrix failed` |
| `verify-render-version-tree.sh` | rc=0 | rc=1 |

The 1.19 failure is `expected type 'string' but found 'dyn'` at
`"posture.acme.io/tier": variables.tier`. Wrapping it as `string(variables.tier)` compiles under
both, and it was tested: it fixes cage-tier, and then a SECOND and different 1.19 incompatibility
appears in `cage-netpol` (a behavioural difference in the generated NetworkPolicy, not a compile
error). So 1.19 support is not a one-line change. It is a supported-window question about which
engine version adopters' clusters run: real work with its own ticket (71), not an instrument fix.
The probe edit was reverted and no served policy body was touched.

Landed on the hub (`5edb962`, with `80f74af` fixing a SIGPIPE that commit introduced):

- kyverno pinned to 1.18.2 by version AND sha256; cosign pinned to 3.1.3 the same way. Both now
  match gitsign's existing pin style. An unpinned tool makes the number unreproducible.
- `jsonschema==4.23.0` added to the pip line. Verified locally: `verify-e2e-step1` and
  `verify-e2e-step6` both PASS once it is present, and `verify-feed-contract` becomes an honest
  SKIP naming the tag it waits for (ticket 57).
- `VERIFY_TIMEOUT: 900`. `verify-publisher-gate` takes about 120s of real kyverno CPU locally and
  was being killed at the 300s default.

**One honest correction.** My first commit added `kyverno version | head -1`, which is the exact
SIGPIPE class ticket 55 fixes elsewhere: under `set -o pipefail` head closes the pipe, and the
step exited 141 before the gate ran. Run 14 failed on it. Fixed in `80f74af`. Run 14's log proves
the pins themselves worked: `Version: 1.18.2` and jsonschema both installed.
