# verify/provenance — every actor, one root, end to end

> *Every actor — commit, workload, human, device — is attestable to one root,
> so the **whole chain verifies** rather than being trusted.* (spec user story 5;
> ticket 24)

The auditor's closing beat. One walk from a **signed feed** to a **signed
release**, then the **runtime identities** that release resolves to — with every
link naming **who** acted (an AI agent or a human), **what** they did, **when**,
and **from which evidence**. Nothing here re-derives the estate: it stitches the
seams that tickets 15 (posture SVID), 18 (device SVID), 22 (war-gamer PR) already
built, and asserts they compose.

## The chain

```mermaid
flowchart LR
  F["feed<br/><i>publisher</i><br/>ed25519-signed"] -->
  S["scenario<br/><i>AI</i> war-gamer<br/>derive"] -->
  P["PR<br/><i>AI</i> war-gamer<br/><b>propose</b> · gitsign→Rekor"] -->
  R["review<br/><i>human</i><br/>OIDC login"] -->
  M["merge<br/><i>human</i><br/><b>dispose</b> · gitsign→Rekor"] -->
  Rel["release<br/><i>human</i><br/>signed tag v2.0.0→Rekor"]
  Rel -.converges on v2.0.0.-> W

  subgraph runtime [runtime identities — one root]
    W["workload SVID<br/>spiffe://acme.internal/<b>posture/2.0.0</b>/…"]
    D["device SVID<br/>spiffe://acme.internal/<b>device/</b>… · tpm_devid"]
    H["commit/human<br/>OIDC→Fulcio→Rekor"]
  end
```

**The AI proposes, humans dispose** — the two disposition links (merge, release)
are human *by construction*; the war-gamer never merges. That is
propose-never-dispose made auditable.

**The closure:** the version the change chain terminates at (`v2.0.0`, the latest
element of `platform/distribution/versions.yaml`) is the *same* version a
compliant workload then carries in its SPIFFE SVID posture path
(`spiffe://acme.internal/posture/2.0.0/…`). Runtime identity traces back through
release → merge → PR → scenario → feed. End to end, not asserted.

## What's here

| file | role |
|------|------|
| `provenance.py` | walks + asserts the chain; reuses `wargamer.py` (feed→scenario→PR) and reads the committed SPIRE manifests (workload + device SVID). `chain` / `walk` / `selfcheck`. |
| `verify-provenance.sh` | the beat — the chain asserts, the **one link that verifies cryptographically right here** (the ed25519 feed signature + a forgery refused), and optional Rekor / SPIRE live tails. |

## Run it

```sh
./verify-provenance.sh      # offline core: python3 (+PyYAML), openssl
python3 provenance.py walk  # just the narration the auditor reads
```

Exits non-zero if the beat would fail on stage.

### Offline vs live

- **Offline (runs here):** the full 6-link chain with every actor + evidence, the
  end-to-end version closure, and one *real* cryptographic check — the v3 feed's
  ed25519 signature verifies and a forged feed is refused.
- **Live tail (skipped, never faked, when infra is absent):**
  - **Rekor** — `rekor-cli`/`cosign` search the transparency log for the
    war-gamer's keyless-signed commit. Needs a commit actually signed via
    `gitsign` and a reachable Rekor. The offline proof is that the merge + release
    links carry the `gitsign→Rekor` root.
  - **SPIRE** — `spire-server entry show` on `kind-driftwood` lists the real
    workload + device registration entries. Needs SPIRE up
    (`platform/posture/up.sh`, `platform/access/up.sh`). The offline proof is that
    both manifests root to `spiffe://acme.internal`, the workload carries
    `posture/<vN>` and the device is `tpm_devid`-pinned.

Reuses `platform/wargamer/wargamer.py` (→ `fair`/`enforce`/`tcor`) for the
change-path links and the committed `platform/posture` + `platform/access` SPIRE
manifests for the runtime identities — no chain fixture is invented here.
(Post-split: `platform` is the real `policy-as-versioned-platform` repo,
fetched locally into `../../.estate-clone/platform` by
[`../../clone-estate.sh`](../../clone-estate.sh).)
