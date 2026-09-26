# 147 — The adopter declares its engine where it installs it

Type: task
Status: open
Blocked by: 146 (the engine table)

## Question

Graduated 2026-09-25 from grilling ticket 71, decisions 2, 5 and 17 (delegated), and ADR-0033
point 2. Decision 17 replaced decision 11 on 2026-09-26.

The adopter owns its engine version, and its engine install file is its declaration. Today:

- No adopter reconciles a platform path. Each adopter serves its own composed set
  (`gitops/composed/`). `gitops/platform/platform-distribution.yaml` is opt-in, and the drift lane
  does not apply it. No adopter file names platform `./engine`.
- The named demo cluster `kind-driftwood` gets the platform's Kyverno from hub `talk/up.sh`, which
  runs platform `engine/up.sh`. tuppence's workload flagship also runs on that cluster.
- Each adopter's `drift-sample.yml` installs the raw `install.yaml` from its own `KYVERNO_VERSION`
  env, and each `shift-left.yml` pins its own CLI.
- No adopter declares its engine anywhere, and `party/schema.json` does not allow a field for it.

Build the following in driftwood, tuppence and ludlow, and in the hub:

1. **The declaration is one file: `gitops/engine/kyverno.yaml`.** The path is decided here
   (delegated), because ticket 161 reads it. The file:
   - states the Kyverno version, for example `1.18.2`;
   - names the raw `install.yaml` URL for that version and its sha256, in a form the lane can apply
     server-side (two Kyverno CRDs are larger than 256KB, so the lane applies them server-side);
   - puts every object it installs in the `kyverno` namespace, which the platform declares as
     substrate (`engine/namespaces.yaml`), so composition prices none of them.
2. **A recompose in the same adopter PR.** The comparison identity hashes every non-hidden source
   file outside `composed/` and the observation lanes (ticket 134). A new file makes
   `composed/HEADER.yaml` stale, so `compose-check` and the pre-tag check refuse until the adopter
   recomposes.
3. **Every cluster the adopter runs installs from that file.**
   - The drift lane: `drift-sample.yml` stops using its own `KYVERNO_VERSION` and checksum, and
     reads both from the file.
   - The named demo clusters: hub `talk/up.sh` installs each named cluster's Kyverno from the file
     of the adopter that owns the cluster, not from platform `engine/up.sh`. The platform's
     `engine/kyverno` stays as the platform's reference install only.
4. **One engine per shared cluster.** A hub check asserts that the adopters who use one cluster
   declare the same engine. Today that is driftwood and tuppence on `kind-driftwood`.
5. **A static check on the file.** A hub check asserts that each adopter's stated version, install
   URL and checksum agree with the platform engine table's row for that version (ticket 146). This
   replaces the drift fact of decision 11. That fact could only read true, because the lane
   installs from the same file that it would compare against.
6. **`shift-left.yml` uses the declared engine.** The adopter's offline CLI version equals its
   declared engine, read from the same file, with the CLI checksum from the engine table.
7. **Tell the session that owns ticket 161.** Its `verify-cage-probe.sh` compares the CLI version
   with the adopter's engine, and must read that version from `gitops/engine/kyverno.yaml`. This
   ticket does not edit `drift/five-facts.py` or `drift/window.yaml`.

Every adopter declares 1.18.2 here. Ticket 150 is the only ticket that moves an adopter to
another engine.

## Done

On each adopter's `origin/main`, `gitops/engine/kyverno.yaml` exists, the composed header is
current, and a scheduled drift sample installed Kyverno from that file. A dispatched run does not
count. `talk/up.sh` installs `kind-driftwood`'s engine from driftwood's file. The shared-cluster
check and the static check pass on the hub, and each fails on a planted disagreement.

## Notes

- Ticket 148 must not land before this ticket lands on all three adopters. If composition prices
  before an adopter declares its engine, that adopter gets the `undeclared-engine` price.
- The engine versions as read on 2026-09-25: `drift-sample.yml` driftwood `:56-57`, ludlow and
  tuppence `:59-60`; `shift-left.yml` driftwood `:117-118`, ludlow `:140-141`, tuppence
  `:138-139`. The lane applies Kyverno server-side at `drift-sample.yml:162-167`.
