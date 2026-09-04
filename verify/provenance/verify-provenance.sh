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
# the workload + device SVIDs — not faked when that infra is absent: what was not looked at is
# named and the script exits 3 (ecosystem ticket 76; this used to print a note and then PASS).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

# could_not_look / pass_or_skip / selfcheck_absent: a live tail's third outcome.
. "$HERE/../lib-observation.sh"
SELF="$HERE/${BASH_SOURCE##*/}"
# The live tails: Rekor for the commit link, SPIRE (through kubectl) for the SVIDs, openssl for
# the one signature this script verifies itself. --selfcheck runs the could-not-look branch alone.
TAILS="rekor-cli cosign gitsign kubectl openssl"
# shellcheck disable=SC2086
if [ "${1:-}" = "--selfcheck" ]; then selfcheck_absent "$SELF" $TAILS; exit 0; fi

have python3 || fail "python3 required"
# Post-split (mo-12): platform is a real, separate GitHub repo, not a sibling
# directory. Fetched by clone-estate.sh into .estate-clone/ first if absent.
[ -d "$HERE/../../.estate-clone/platform" ] || bash "$HERE/../../clone-estate.sh" \
  || fail "could not assemble .estate-clone/ (needs network — see clone-estate.sh)"
PLATFORM="$(cd "$HERE/../../.estate-clone/platform" && pwd)"
WG="$PLATFORM/wargamer"

# Run this script's own could-not-look branch before looking at anything, so it is exercised on
# a machine that HAS the instruments rather than only on one that lacks them.
# shellcheck disable=SC2086
selfcheck_absent "$SELF" $TAILS

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
  could_not_look "openssl absent: the v3 feed's ed25519 signature, the one link this script can verify offline, was not verified"
fi

say "3. commit/PR attestable in REKOR (the human disposition links)"
# OFFLINE: the merge + release links carry the gitsign-keyless->Rekor root
# (asserted in step 1). LIVE: if rekor-cli/cosign is here AND the repo has a
# keyless-signed commit, verify it in the transparency log. Absent -> skip.
if ! have rekor-cli; then
  could_not_look "no rekor-cli here to query the transparency log, so the commit link was read from the committed chain only, never confirmed against Rekor$(have gitsign && echo " (gitsign is installed [$(gitsign --version 2>&1 | head -1)], but it signs, it does not query)")"
elif ! have git || ! git -C "$HERE" rev-parse HEAD >/dev/null 2>&1; then
  could_not_look "rekor-cli is here but this is not a git work tree, so there was no commit to look up"
else
  say "3-live. rekor-cli present — searching the transparency log for the HEAD commit"
  sha="$(git -C "$HERE" rev-parse HEAD)"
  if timeout 30 rekor-cli search --sha "$sha" >/dev/null 2>&1; then
    echo "  ok   HEAD commit $sha found in Rekor"
  else
    # Not a failure and not a pass: this repo's own commits are not keyless-signed, so there is
    # no entry to find. The war-gamer's PRs are, once opened via propose-policy-pr.sh. Either
    # way this run did not observe a commit in Rekor, and must not report that it did.
    could_not_look "HEAD ($sha) has no Rekor entry -- this repo's commits are not keyless-signed here, so the live commit-in-log link had nothing to verify"
  fi
fi

say "4. workload + device SVIDs verify against SPIRE (one root, distinct actor classes)"
# OFFLINE: the committed SPIRE manifests root both to spiffe://acme.internal, the
# workload carries posture/<vN> and the device is tpm_devid-pinned (asserted in
# step 1). LIVE: if a SPIRE server is reachable, show the real registration entries.
CTX="${CTX:-kind-driftwood}"
if ! have kubectl; then
  could_not_look "no kubectl here, so no SPIRE server was reached and no live SVID was seen (the committed manifests are asserted offline in step 1)"
elif ! timeout 10 kubectl --context "$CTX" -n spire-server get statefulset spire-server >/dev/null 2>&1; then
  could_not_look "no SPIRE server on $CTX, so no live SVID was seen (the committed manifests are asserted offline in step 1)"
else
  say "4-live. SPIRE server reachable on $CTX — listing registration entries"
  entries="$(timeout 30 kubectl --context "$CTX" -n spire-server exec statefulset/spire-server -- \
      /opt/spire/bin/spire-server entry show 2>/dev/null || true)"
  if [ -z "$(printf '%s' "$entries" | tr -d '[:space:]')" ]; then
    # Nothing registered is nothing to look at, not a false root: could-not-look, not FAIL.
    could_not_look "SPIRE on $CTX has no registration entries at all (apply posture/ + access/ up.sh), so no live SVID's trust domain was read"
  elif printf '%s\n' "$entries" | grep -q "spiffe://acme.internal"; then
    echo "$entries"
    echo "  ok   live SPIRE entries root to spiffe://acme.internal"
  else
    # Entries exist and none root to the domain: that IS an observation, and it is false.
    echo "$entries"
    fail "SPIRE on $CTX has registration entries and none root to spiffe://acme.internal -- the actors do not share one root"
  fi
fi

say "5. the walk — who proposed what, when, from which evidence (the auditor reads this)"
timeout 90 python3 "$HERE/provenance.py" walk

echo
pass_or_skip "the whole chain walks feed->scenario->PR->review->merge->release; the AI war-gamer PROPOSES (never merges), humans DISPOSE; workload+device+commit+human all root to one attestation, and the chain converges on the exact version a running workload carries in its SVID. Provenance for every actor, end to end."
