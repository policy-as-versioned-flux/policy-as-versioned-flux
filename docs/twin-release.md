# Initial signed twin package

Tickets 29 and 64 require `twin/v0.1.0`. The repository is the package
(`bin/twin`); `twin/VERSION` supplies `0.1.0`. This initial publication has no
released predecessor and makes no computed patch/minor movement claim. Later
versions need their own reviewed bump contract; this route refuses them.

The artifact is one keyless gitsign-signed annotated Git tag. Its JSON annotation
binds the exact source commit, `twin/` Git tree, executable `bin/twin` blob,
version, release message and claim scope. There is no second signature, registry
package or detached manifest to authenticate. The signature covers the whole
repository, including its rationale and contracts (ADR-0001, ADR-0023).

## Cut and publication

After ordinary review and merge, the release operator dispatches `cut-release.yml`
on `main`, naming its full reviewed commit, version `0.1.0` and message. The
workflow's production CLI is `python3 talk/twin_release.py cut`. It requires the
canonical repository/workflow identity, clean source, matching local/remote main,
the executable entry point and no existing local or remote twin tag. A refused
preflight never invokes the signer. A failed signer or verifier never pushes.
Main is checked again immediately before the atomic tag push. Source, evidence
and branch history are not changed by the cut.

The workflow uses the estate's pinned gitsign0.17.1, embeds the offline Rekor
proof, and verifies the exact certificate subject
`https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/.github/workflows/cut-release.yml@refs/heads/main`
and issuer `https://token.actions.githubusercontent.com` before pushing.

The default Actions token does not trigger a second workflow from its tag push.
The cutter therefore explicitly dispatches `release.yml` with the same tag and
source commit. A direct matching tag push reaches that same route. Publication
refreshes only its local tag-object copy (checkout can flatten an annotated
tag), verifies identity/issuer and package metadata independently, and rechecks
the current remote tag object and peeled commit before `gh release create
--verify-tag --target <source>`. It creates a release; it never edits one.

Every job is bounded to15minutes and each CLI process to180seconds. There is no
force push, signature fallback, test-mode switch, tag rewrite or automatic retry.
If verification/publication fails after a tag landed, preserve that tag and the
failure. A separately authorized publication dispatch can verify the existing
tag; repeating the cut refuses. Advancing main requires a fresh reviewed expected
commit, not silently substituting a new source.

## What the gate proves

The initial artifact gate runs the package's actual workflow/CLI callsite tests,
then enforces source/object binding and real signature verification. Fixtures
use unsigned disposable Git repositories/local bare remotes and explicitly
substitute signer/verifier/GitHub responses. They do not establish a real hosted
signature, release, actor resistance or production outcome. Python3.12 Linux
proof dependencies and every downloaded action/binary are pinned by hash.

The whole `twin.yml` CI and invariant suite retain their existing behavior.
The historical `flux_coverage_floor_is_still_reachable` failure remains red;
missed measurement hours cannot be manufactured. Publishing versioned source
does not assert that whole CI or the running estate is green, or provide actor,
forecast, calibration, money or workload credit. Release notes and tag metadata
state that boundary. No existing gate is filtered or changed by this workflow.

## Adoption follows the real tag

All three adopter pins remain at their reviewed commits until a genuine tag
exists (ticket143; ADR-0031). After authenticating it against the publisher
identity above, each adopter moves by an ordinary reviewed PR to the exact
`{twin_tag, hub_commit}` pair and `tag_cut: true`; tag and resolved commit must
agree. Preserve its split read-only twin/writer jobs, rung gate, overlay, signed
forward-intel artifacts and observations. A clock does not edit this pin. Those
three adoptions and their actual original CI/conservation are a separate
delivery phase, not an outcome supplied by authoring this publisher route.
