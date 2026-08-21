#!/usr/bin/env bash
# THE AUDITOR'S BEAT. "Every actor — commit, workload, human, device — is
# attestable to one root, so the WHOLE chain verifies rather than being trusted."
# One walk from a signed feed to a signed release, then the runtime identities the
# release resolves to. Each link names WHO acted (AI agent or human), WHAT, WHEN,
# and FROM WHICH EVIDENCE — and the chain CONVERGES on the exact version a running
# workload then carries in its SPIFFE SVID.
#
# Exits non-zero if the beat would fail on stage. OFFLINE core (python3 [+PyYAML];
# openssl for the one link that verifies cryptographically right here). Optional
# LIVE tail: Rekor (rekor-cli/cosign) for the commit/PR, SPIRE (spire-server) for
# the workload + device SVIDs — skipped, not faked, when that infra is absent.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

have python3 || fail "python3 required"
# Post-split (mo-12): platform is a real, separate GitHub repo, not a sibling
# directory. Fetched by clone-estate.sh into .estate-clone/ first if absent.
[ -d "$HERE/../../.estate-clone/platform" ] || bash "$HERE/../../clone-estate.sh" \
  || fail "could not assemble .estate-clone/ (needs network — see clone-estate.sh)"
PLATFORM="$(cd "$HERE/../../.estate-clone/platform" && pwd)"
WG="$PLATFORM/wargamer"

say "1. the whole chain: feed->scenario->PR->review->merge->release, every actor named"
timeout 90 python3 "$HERE/provenance.py" selfcheck || fail "provenance chain selfcheck failed"

say "2. the head of the chain VERIFIES CRYPTOGRAPHICALLY, right here (the signed feed)"
# The one link whose signature we can check offline with no infra: the ed25519
# detached signature on the v3 feed that drove the whole change. If this doesn't
# verify, link 1 is trusted, not attested — the beat is a lie.
if have openssl; then
  key="$PLATFORM/feeds/keys/feeds-signing-key.pub.pem"
  feed="$WG/fixtures/threat-register/v3/register.json"
  timeout 30 openssl pkeyutl -verify -pubin -inkey "$key" -rawin -in "$feed" -sigfile "$feed.sig" >/dev/null \
    || fail "the v3 feed signature did not verify — the chain's head is not attestable"
  echo "  ok   feed link attested: v3 threat-register signature verifies (ed25519)"
  # and a forged feed is refused — the signature is load-bearing, not decorative.
  tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT
  python3 -c "import json,sys;d=json.load(open('$feed'));d['institutions']['driftwood']['lef']=[1,1,1];json.dump(d,open('$tmp','w'))"
  if timeout 30 openssl pkeyutl -verify -pubin -inkey "$key" -rawin -in "$tmp" -sigfile "$feed.sig" >/dev/null 2>&1; then
    fail "a forged feed still verified — the head of the chain is forgeable"
  fi
  echo "  ok   a forged feed is refused (the signature actually guards the link)"
else
  echo "  (openssl absent — offline crypto proof of the feed link skipped)"
fi

say "3. commit/PR attestable in REKOR (the human disposition links)"
# OFFLINE: the merge + release links carry the gitsign-keyless->Rekor root
# (asserted in step 1). LIVE: if rekor-cli/cosign is here AND the repo has a
# keyless-signed commit, verify it in the transparency log. Absent -> skip.
if have rekor-cli; then
  say "3-live. rekor-cli present — searching the transparency log for the HEAD commit"
  if have git && git -C "$HERE" rev-parse HEAD >/dev/null 2>&1; then
    sha="$(git -C "$HERE" rev-parse HEAD)"
    if timeout 30 rekor-cli search --sha "$sha" >/dev/null 2>&1; then
      echo "  ok   HEAD commit $sha found in Rekor"
    else
      echo "  note: HEAD commit not in Rekor (this repo's commits aren't keyless-signed here;"
      echo "        the war-gamer's PRs are, once opened via propose-policy-pr.sh -> git commit --gitsign)"
    fi
  fi
elif have gitsign; then
  echo "  offline: merge+release links carry the Rekor root (verified in step 1);"
  echo "  gitsign present [$(gitsign --version 2>&1 | head -1)] but no rekor-cli/cosign to query the log."
else
  echo "  offline: merge+release links carry the Rekor root (verified in step 1);"
  echo "  no rekor-cli/cosign/gitsign here to query the live transparency log."
fi

say "4. workload + device SVIDs verify against SPIRE (one root, distinct actor classes)"
# OFFLINE: the committed SPIRE manifests root both to spiffe://acme.internal, the
# workload carries posture/<vN> and the device is tpm_devid-pinned (asserted in
# step 1). LIVE: if a SPIRE server is reachable, show the real registration entries.
CTX="${CTX:-kind-driftwood}"
live_spire=0
if have kubectl && timeout 10 kubectl --context "$CTX" -n spire-server get statefulset spire-server >/dev/null 2>&1; then
  say "4-live. SPIRE server reachable on $CTX — listing registration entries"
  if timeout 30 kubectl --context "$CTX" -n spire-server exec statefulset/spire-server -- \
       /opt/spire/bin/spire-server entry show 2>/dev/null | tee /dev/stderr | grep -q "spiffe://acme.internal"; then
    echo "  ok   live SPIRE entries root to spiffe://acme.internal"
    live_spire=1
  else
    echo "  note: SPIRE reachable but no acme.internal entries yet (apply posture/ + access/ up.sh)"
  fi
fi
[ "$live_spire" = 1 ] || echo "  offline: workload (posture/vN) + device (/device/, tpm_devid) SVIDs share one root — manifests asserted in step 1"

say "5. the walk — who proposed what, when, from which evidence (the auditor reads this)"
timeout 90 python3 "$HERE/provenance.py" walk

echo
echo "PASS: the whole chain walks feed->scenario->PR->review->merge->release; the AI"
echo "war-gamer PROPOSES (never merges), humans DISPOSE; workload+device+commit+human all"
echo "root to one attestation, and the chain converges on the exact version a running"
echo "workload carries in its SVID. Provenance for every actor, end to end."
