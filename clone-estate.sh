#!/usr/bin/env bash
# Assembles a local, disposable copy of the six real policy-as-versioned-* unit
# repos so talk/up.sh and talk/verify-all.sh can run against real content, the
# same way they did when estate/ was one committed tree in this hub.
#
# This IS the "cross-org verify arrangement" ticket 07 asked about (it
# considered the name clone-estate.sh directly) and mo-12 settles: the hub no
# longer holds a copy of the six units, so anything that needs to see more
# than one unit at once (talk/up.sh's bring-up order, talk/verify-all.sh's
# beat sweep, verify/party's cross-party filesystem check) clones them fresh
# into .estate-clone/ instead. .estate-clone/ is git-ignored: it is a build
# artifact of the six real repos, never a second copy of their content.
#
# Each unit repo also carries its OWN verify-reconcile.sh / up.sh / lib.sh —
# ticket 07's "each repo consumes the verify tooling exactly as it consumes
# policy" — this script's only job is fetching them, not reimplementing them.
#
# Idempotent by default: skips a unit already cloned. Pass --refresh to
# re-clone every unit from scratch (e.g. after a new tag lands).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$ROOT/.estate-clone"
UNITS=(platform driftwood tuppence ludlow nist ico feeds insurer)
REFRESH=0; [ "${1:-}" = "--refresh" ] && REFRESH=1

mkdir -p "$DEST"
for u in "${UNITS[@]}"; do
  org="policy-as-versioned-$u"
  dir="$DEST/$u"
  if [ "$REFRESH" = 1 ]; then rm -rf "$dir"; fi
  if [ -d "$dir/.git" ]; then
    echo "==> $u: already cloned (pass --refresh to re-clone)"
    continue
  fi
  rm -rf "$dir"
  echo "==> cloning $org/$u"
  # No signed tag exists yet (ticket 09/12: known, accepted partial state) so
  # this clones the default branch. Once a signed v1.0.0 lands, pin it here
  # (--branch v1.0.0) so the offline harness matches what Flux actually runs.
  # A FULL clone. Neither shortcut works here, and both were tried:
  #
  #   --depth 1          leaves the tag objects out, and several checks need tag
  #                      history. release_integrity rule 1 reads a released tree
  #                      from its own tag; tuppence's adopter-gate scenario D
  #                      resolves `v1.0.0^{commit}`. Under a shallow clone that
  #                      scenario failed with "could not find or fetch platform
  #                      tag 'v1.0.0'" while passing on a deep one, so the gate's
  #                      answer depended on how this script happened to fetch.
  #   --filter=blob:none keeps every ref but no file contents, and several
  #                      scenarios `git clone --local` from this copy. A clone of
  #                      a partial clone cannot reach the promisor remote, so it
  #                      comes out missing files that are plainly committed.
  #
  # These repositories are small -- the whole estate is tens of megabytes -- so
  # the honest fetch is the cheap one. A gate that grades differently depending
  # on how its inputs were fetched is not a gate.
  git clone --quiet "https://github.com/$org/$u" "$dir"
done

# Every clone (fresh or kept) verifies x509 signatures with gitsign, where gitsign is installed.
# five-facts.py's sample_provenance reads `git log --format=%G?` on the observation-lane commit;
# without this config git hands the x509 signature to gpgsm and the grade honestly SKIPs as
# unattributable (its own ponytail note: "configure gitsign on the truth runner to close it").
# The truth runner installs pinned gitsign; a machine without it still gets the honest SKIP.
for u in "${UNITS[@]}"; do
  git -C "$DEST/$u" config gpg.x509.program gitsign
done
echo "OK: ${#UNITS[@]} units in $DEST"
