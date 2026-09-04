#!/usr/bin/env bash
# NORTH-STAR §4 step 6: "Provenance: every step above is verifiable in Rekor and in the
# artefact sidecars."
#
# Three parts, all real today:
#
#   1. OFFLINE, reachability. verify/feed-contract/feed_contract.py already resolves every
#      published artefact in the slice to a tag on the publisher's REAL remote. This step
#      re-grades its output for step 6's question: a FAIL is a fail; "waiting for tag ..." is
#      the honest "queued" the ticket allows; any other SKIP is a could-not-look.
#   2. OFFLINE, the identity pin. Every unit's release.yml verifies its tag with
#      `gitsign verify-tag --certificate-identity-regexp`. That regexp must be ANCHORED at both
#      ends, must escape its literal dots, and must name the unit's OWN org/repo -- taken from
#      that unit's git remote, never from a list in this file. Foreign-org, foreign-workflow and
#      prefix/suffix shapes must not match. gitsign's matcher is RE2; these patterns use only
#      anchors, escaped dots, classes and alternation, which grep -E evaluates identically, so
#      grep is a faithful stand-in on the NEGATIVE cases.
#   3. LIVE, Rekor. For every unit that already has a signed tag, run the real gitsign binary
#      against that unit's own regexp and issuer, and require both "Good signature from
#      [<identity>]" and "Validated Rekor entry: true". That is what proves the anchored regexp
#      matches the REAL cert subject rather than a subject this script invented. No gitsign, or
#      no Rekor, is a could-not-look, never a pass.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 6 "provenance"

[ -d "$ESTATE" ] || skip "no .estate-clone (run clone-estate.sh)"
bad=0; unlooked=()
note() { echo "  $*"; }
bad()  { echo "  BAD  $*"; bad=$((bad+1)); }

# --- 1. every published artefact reaches a signed tag, or is honestly queued --------------
"$PY" -c 'import jsonschema, yaml' 2>/dev/null || skip "python lacks jsonschema/pyyaml (cannot resolve the slice's artefacts)"
fc="$(mktemp)"; trap 'rm -f "$fc"' EXIT
timeout 300 "$PY" "$ROOT/verify/feed-contract/feed_contract.py" check >"$fc" 2>&1
nfail=$(grep -c '^FAIL:' "$fc" || true)
nq=$(grep -c '^SKIP:.*waiting for tag' "$fc" || true)
nok=$(grep -c '^PASS:' "$fc" || true)
nskip=$(grep '^SKIP:' "$fc" | grep -vc 'waiting for tag' || true)
[ "$nfail" -eq 0 ] || { grep '^FAIL:' "$fc" | sed 's/^/  BAD  /'; bad=$((bad+nfail)); }
note "ok   $nok published artefacts resolve to a tag on the publisher's real remote; $nq honestly queued for cut-release.yml"
if [ "$nskip" -gt 0 ]; then
  while IFS= read -r line; do
    echo "  ??   $line"
    unlooked+=("${line#SKIP: }")
  done < <(grep '^SKIP:' "$fc" | grep -v 'waiting for tag')
fi

# --- 2. the identity regexps are anchored and are the unit's own ---------------------------
units=0
for wf in "$ESTATE"/*/.github/workflows/release.yml; do
  u="$(basename "$(dirname "$(dirname "$(dirname "$wf")")")")"
  re="$(sed -nE 's/^ *EXPECTED_IDENTITY_REGEXP: *//p' "$wf" | head -1)"
  iss="$(sed -nE 's/^ *EXPECTED_ISSUER: *//p' "$wf" | head -1)"
  [ -n "$re" ] || { bad "$u: release.yml sets no EXPECTED_IDENTITY_REGEXP"; continue; }
  [ "$iss" = "https://token.actions.githubusercontent.com" ] \
    || bad "$u: EXPECTED_ISSUER is '$iss', not the Actions OIDC issuer"
  slug="$(git -C "$ESTATE/$u" remote get-url origin 2>/dev/null | sed -E 's#.*github\.com[:/]##; s/\.git$//')"
  [ -n "$slug" ] || { unlooked+=("$u has no git remote to derive its own identity from"); continue; }
  want="^https://github\\.com/$slug/\\.github/workflows/cut-release\\.yml@refs/heads/"
  case "$re" in
    "$want"*) ;;
    *) bad "$u: regexp is not anchored on its own repo; wants to start '$want', is '$re'";;
  esac
  case "$re" in *'$') ;; *) bad "$u: regexp has no trailing \$ -- a suffix attack matches";; esac
  # positive and negative shapes through the same matcher release.yml uses.
  ok_id="https://github.com/$slug/.github/workflows/cut-release.yml@refs/heads/main"
  echo "$ok_id" | grep -qE "$re" || bad "$u: its own cut-release identity does not match its regexp"
  for nope in \
    "https://github.com/policy-as-versioned-evil/$(basename "$slug")/.github/workflows/cut-release.yml@refs/heads/main" \
    "https://github.com/$slug/.github/workflows/other.yml@refs/heads/main" \
    "https://evil.com/$ok_id" \
    "$ok_id.evil.com" \
    "https://github.com/$slug/.github/workflows/cut-release.yml@refs/heads/release/x.y.x"; do
    ! echo "$nope" | grep -qE "$re" || bad "$u: regexp matches a foreign identity: $nope"
  done
  units=$((units+1))
done
[ "$units" -gt 0 ] || bad "no unit ships a release.yml -- nothing pins an identity"
note "ok   $units release workflows pin an anchored, own-repo identity regexp at the Actions OIDC issuer"

# --- 3. the regexp matches the REAL cert subject, and the entry is in Rekor -----------------
#
# The tag shape is each unit's OWN. A bare three-number glob was typed into `git tag -l` here,
# and feeds tags `threat-register/v2.0.0`, so feeds matched nothing and this step said feeds had
# no signed tag
# about a publisher whose tag is in Rekor -- an absence inferred from a lookup that could not
# have succeeded. Every line in a unit's party.yaml publishes[] now resolves its own newest tag
# through feed_contract.newest_tag_per_line (`<line>/vX.Y.Z` or bare `vX.Y.Z`, the same two forms
# the feed contract admits), and a line with no tag says what shapes were looked for among how
# many real tags. Ticket 76.
lines="$(mktemp)"; trap 'rm -f "$fc" "$lines"' EXIT
"$PY" - "$ESTATE" "$ROOT/verify/feed-contract/feed_contract.py" >"$lines" <<'PY' || bad "could not resolve published lines to tags"
import importlib.util, pathlib, subprocess, sys
import yaml

estate, fc_path = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("feed_contract", fc_path)
fc = importlib.util.module_from_spec(spec); spec.loader.exec_module(fc)

for party in sorted(estate.glob("*/party.yaml")):
    unit = party.parent.name
    if not (party.parent / ".github/workflows/release.yml").exists():
        continue
    doc = yaml.safe_load(party.read_text()) or {}
    tags = set(subprocess.run(["git", "-C", str(party.parent), "tag", "-l"],
                              capture_output=True, text=True).stdout.split())
    for name, tag in sorted(fc.newest_tag_per_line(doc, tags).items()):
        # "|", not a tab: tab is IFS whitespace, so `read` collapses two of them and an
        # untagged line's empty field would silently shift the columns along.
        print(f"{unit}|{name}|{tag or ''}|{len(tags)}")
PY
if ! command -v gitsign >/dev/null; then
  unlooked+=("gitsign absent: the anchored regexps were never run against a real Fulcio cert")
else
  verified=0; untagged=0
  while IFS='|' read -r u name tag ntags; do
    [ -n "$u" ] || continue
    wf="$ESTATE/$u/.github/workflows/release.yml"
    if [ -z "$tag" ]; then
      # Observed, not inferred: the unit's real tag list was read and neither of this line's
      # own two shapes is in it. Queued for cut-release.yml, and said so with what was looked for.
      note "ok   $u/$name has no tag yet: looked for '$name/vX.Y.Z' and 'vX.Y.Z' among $ntags real tags -- queued for cut-release.yml"
      untagged=$((untagged+1))
      continue
    fi
    re="$(sed -nE 's/^ *EXPECTED_IDENTITY_REGEXP: *//p' "$wf" | head -1)"
    iss="$(sed -nE 's/^ *EXPECTED_ISSUER: *//p' "$wf" | head -1)"
    out="$(cd "$ESTATE/$u" && timeout 90 gitsign verify-tag "$tag" \
             --certificate-identity-regexp="$re" --certificate-oidc-issuer="$iss" 2>&1)"
    if printf '%s' "$out" | grep -q 'Validated Rekor entry: true' \
       && printf '%s' "$out" | grep -q 'Good signature from'; then
      note "ok   $u/$name newest tag $tag: real cert subject matches the anchored regexp, Rekor entry validated"
      verified=$((verified+1))
    elif printf '%s' "$out" | grep -qiE 'connection refused|no such host|timeout|context deadline|i/o timeout|dial tcp'; then
      unlooked+=("Rekor/Fulcio unreachable while verifying $u/$name's newest tag $tag")
    elif printf '%s' "$out" | grep -qi 'error resolving tag reference'; then
      # `git tag -l` in this checkout listed the tag, so it exists; gitsign's own git layer
      # could not open it. That is what a LINKED WORKTREE looks like to gitsign (`.git` is a
      # file, not a directory): a builder running against .work/ trees sees this, the
      # integrator's real checkout does not. Could-not-look, never a false claim either way.
      unlooked+=("gitsign could not resolve $u/$name's newest tag $tag in this checkout (a linked worktree is opaque to it), so the cert subject was not read")
    else
      bad "$u/$name newest tag $tag: gitsign verify-tag failed against release.yml's own regexp -- $(printf '%s' "$out" | tail -1)"
    fi
  done <"$lines"
  [ "$verified" -gt 0 ] || unlooked+=("no published line had a tag to check against Rekor")
fi

verified="${verified:-0}"; untagged="${untagged:-0}"
nlines="$(grep -c . "$lines" || true)"
[ "$bad" -eq 0 ] || fail "$bad provenance claim(s) are false (see BAD lines above)"
if [ ${#unlooked[@]} -gt 0 ]; then
  msg="$(printf '; %s' "${unlooked[@]}")"
  skip "the offline provenance holds, but part of step 6 could not be looked at:${msg#;}"
fi
# $verified, not $units: $units counts release.yml FILES (part 2), and using it here
# claimed a Rekor check for every one of them the moment the last unrelated SKIP
# cleared -- 8 asserted against 6 actually verified (review, 2026-08-28). $nlines counts
# PUBLISHED LINES, which is what a tag signs, and every one of them was resolved in its own
# shape: $verified verified against Rekor, $untagged read as genuinely untagged (ticket 76).
pass "every artefact the slice publishes reaches a signed tag or is honestly queued; of the $nlines lines the $units release-shipping units declare in their own party.yaml publishes[], $verified newest tags matched a real Fulcio cert subject with its Rekor entry validated and $untagged lines have no tag of their own shape yet"
