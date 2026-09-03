#!/usr/bin/env bash
# The signed release evidence reaches main (eco-system ticket 53). OFFLINE once the clone exists.
#
# 2026-08-31, cutting two platform releases in sequence for the first time: cut-release.yml
# committed the signed release-gate evidence (N.json and its cosign N.json.bundle) onto the
# checked-out branch, then pushed the tags alone. The evidence was reachable only from the tag;
# main carried 4.0.0.json with no bundle; v2.0.0, cut minutes later from that main, inherited
# the hole; driftwood, tuppence and ludlow refused it, correctly. The repair (platform b83eba1)
# pushes HEAD:refs/heads/<branch> in the same atomic push as the tags.
#
# This check reads what the adopters read -- platform's published origin/main and the tags they
# pin -- and grades three things:
#   1. every computed-semver/evidence/N.json on origin/main has its N.json.bundle beside it;
#   2. cut-release-push.sh on origin/main pushes the branch and the tags in one --atomic push;
#   3. the platform tag each adopter pins (gitops/platform/platform-pin.yaml) carries every
#      bundle, so the adopter's own gate cannot refuse for the 2026-08-31 reason.
# The mechanics of the push itself (branch and tags land together or not at all) are proven by
# platform's own offline twin, verify-cut-release-tags.sh case 8. This script proves the outcome.
#
# Exit 0 PASS, 1 FAIL, 3 SKIP when the platform clone or its origin/main cannot be read.
#
#   verify-release-evidence-reaches-main.sh            selfcheck first, then grade the clone
#   verify-release-evidence-reaches-main.sh selfcheck  selfcheck only: a tree with a bundle-less
#                                                      N.json must fail the pairing; the pre-repair
#                                                      push line must fail the push-line grader;
#                                                      and the real, immutable v2.0.0 tag (which
#                                                      carries the hole) must fail the pairing
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PLATFORM="${RELEASE_EVIDENCE_PLATFORM:-$ROOT/.estate-clone/platform}"   # overridden only by the selfcheck
ADOPTERS="${RELEASE_EVIDENCE_ADOPTERS:-driftwood tuppence ludlow}"
EVIDENCE_DIR="computed-semver/evidence"
PUSH_SCRIPT=".github/scripts/cut-release-push.sh"
bad=0; skipped=0
ok()   { printf '  ok   %s\n' "$*"; }
fail() { printf '  FAIL %s\n' "$*"; bad=$((bad+1)); }
note() { printf '  note %s\n' "$*"; }

# --- graders: pure functions of a repo path and a ref, so the selfcheck can point them at a
# --- scratch repo and at real history alike. Each prints its own ok/FAIL lines; the selfcheck
# --- calls them in subshells so its deliberate failures never count against the real grade.

# every N.json under EVIDENCE_DIR at <ref> has a sibling N.json.bundle; at least one pair exists
grade_pairing() {   # <repo> <ref> <label>
  local repo="$1" ref="$2" label="$3" names json n missing=0 pairs=0
  names="$(git -C "$repo" ls-tree --name-only "$ref" "$EVIDENCE_DIR/" 2>/dev/null)" || { fail "$label: cannot list $EVIDENCE_DIR at $ref"; return 1; }
  for json in $(printf '%s\n' "$names" | grep -E '/[^/]+\.json$'); do
    n="${json##*/}"; n="${n%.json}"
    if printf '%s\n' "$names" | grep -qx "$json.bundle"; then pairs=$((pairs+1))
    else fail "$label: $EVIDENCE_DIR/$n.json has no $n.json.bundle beside it at $ref (the 2026-08-31 hole)"; missing=$((missing+1)); fi
  done
  [ "$pairs" -gt 0 ] || { fail "$label: no evidence pair at all under $EVIDENCE_DIR at $ref"; return 1; }
  [ "$missing" -eq 0 ] || return 1
  ok "$label: $pairs evidence document(s) at $ref, each with its cosign bundle"
}

# the push line at <ref> carries the branch and the tags in one --atomic push: exactly one
# non-comment push line, and that one line carries all three tokens. Two pushes are two
# transactions (one can land without the other, the 2026-08-31 shape), whatever flags each has.
grade_push_line() {   # <repo> <ref> <label>
  local repo="$1" ref="$2" label="$3" src line n
  src="$(git -C "$repo" show "$ref:$PUSH_SCRIPT" 2>/dev/null)" || { fail "$label: no $PUSH_SCRIPT at $ref"; return 1; }
  line="$(printf '%s\n' "$src" | grep -E '^[[:space:]]*git push ')"   # a comment line starts with #, so it never matches
  [ -n "$line" ] || { fail "$label: $PUSH_SCRIPT at $ref has no git push line"; return 1; }
  n="$(printf '%s\n' "$line" | grep -c .)"
  [ "$n" -eq 1 ] || { fail "$label: $PUSH_SCRIPT at $ref has $n git push lines; the branch and the tags must go in one push, not one each: $(printf '%s' "$line" | tr '\n' ';')"; return 1; }
  printf '%s\n' "$line" | grep -Eq -- '(^|[[:space:]])(--dry-run|-n)([[:space:]]|$)' && { fail "$label: the push at $ref is a dry run, it lands nothing: $line"; return 1; }
  printf '%s\n' "$line" | grep -q -- '--atomic' || { fail "$label: the push at $ref is not --atomic: $line"; return 1; }
  printf '%s\n' "$line" | grep -qF 'HEAD:refs/heads/${branch}' || { fail "$label: the push at $ref carries the tags but not the branch: $line"; return 1; }
  printf '%s\n' "$line" | grep -qF '"${tags[@]}"' || { fail "$label: the push at $ref carries the branch but not the tags: $line"; return 1; }
  ok "$label: $PUSH_SCRIPT at $ref pushes HEAD:refs/heads/\${branch} and the tags in one --atomic push"
}

selfcheck() {
  local t good=1
  t="$(mktemp -d)"
  # a scratch repo whose main has 1.0.0.json+bundle and a bare 2.0.0.json, and an old-style push
  git init -q -b main "$t/r" && git -C "$t/r" config user.email s@example.invalid && git -C "$t/r" config user.name s
  git -C "$t/r" config core.hooksPath /dev/null   # scratch repo: no global hooks, no noise
  mkdir -p "$t/r/$EVIDENCE_DIR" "$t/r/.github/scripts"
  echo '{}' >"$t/r/$EVIDENCE_DIR/1.0.0.json"; echo 'b' >"$t/r/$EVIDENCE_DIR/1.0.0.json.bundle"
  echo '{}' >"$t/r/$EVIDENCE_DIR/2.0.0.json"
  printf '#!/usr/bin/env bash\n# git push --atomic "$remote" "HEAD:refs/heads/${branch}" "${tags[@]}"\ngit push --atomic "$remote" "${tags[@]}"\n' >"$t/r/$PUSH_SCRIPT"
  git -C "$t/r" add -A && git -C "$t/r" commit -q -m hole
  (grade_pairing "$t/r" main selfcheck) >/dev/null 2>&1 && { echo "selfcheck: a bundle-less 2.0.0.json passed the pairing"; good=0; }
  (grade_push_line "$t/r" main selfcheck) >/dev/null 2>&1 && { echo "selfcheck: the pre-repair tags-only push line passed (a comment carrying the right line must not count)"; good=0; }
  # ...a split push (branch in one push, tags in another) is the 2026-08-31 shape with extra
  # steps: the tags can land and the branch be rejected, or the reverse. Both lines carry
  # --atomic and between them every token; only the same line carrying all three counts
  printf '#!/usr/bin/env bash\ngit push --atomic "$remote" "HEAD:refs/heads/${branch}"\ngit push --atomic "$remote" "${tags[@]}"\n' >"$t/r/$PUSH_SCRIPT"
  git -C "$t/r" add -A && git -C "$t/r" commit -q -m split
  (grade_push_line "$t/r" main selfcheck) >/dev/null 2>&1 && { echo "selfcheck: a split push (branch and tags in two pushes) passed as one atomic push"; good=0; }
  # ...and a --dry-run pushes nothing, however complete its ref list
  printf '#!/usr/bin/env bash\ngit push --atomic --dry-run "$remote" "HEAD:refs/heads/${branch}" "${tags[@]}"\n' >"$t/r/$PUSH_SCRIPT"
  git -C "$t/r" add -A && git -C "$t/r" commit -q -m dry-run
  (grade_push_line "$t/r" main selfcheck) >/dev/null 2>&1 && { echo "selfcheck: a --dry-run push line passed"; good=0; }
  # ...and the repaired shapes pass, so the graders are not merely always-red
  echo 'b' >"$t/r/$EVIDENCE_DIR/2.0.0.json.bundle"
  printf '#!/usr/bin/env bash\ngit push --atomic "$remote" "HEAD:refs/heads/${branch}" "${tags[@]}"\n' >"$t/r/$PUSH_SCRIPT"
  git -C "$t/r" add -A && git -C "$t/r" commit -q -m repaired
  (grade_pairing "$t/r" main selfcheck) >/dev/null 2>&1 || { echo "selfcheck: a fully paired tree failed the pairing"; good=0; }
  (grade_push_line "$t/r" main selfcheck) >/dev/null 2>&1 || { echo "selfcheck: the repaired push line failed"; good=0; }
  # ...and a branch that has never pushed evidence is not a pass by vacancy
  git -C "$t/r" checkout -q --orphan empty && git -C "$t/r" rm -rfq . && git -C "$t/r" commit -q --allow-empty -m empty
  (grade_pairing "$t/r" empty selfcheck) >/dev/null 2>&1 && { echo "selfcheck: a tree with no evidence at all passed the pairing"; good=0; }
  rm -rf "$t"
  # real history, when it is here: v2.0.0 is immutable and carries the hole that started this
  if git -C "$PLATFORM" rev-parse -q --verify 'refs/tags/v2.0.0^{commit}' >/dev/null 2>&1; then
    if (grade_pairing "$PLATFORM" v2.0.0 selfcheck) >/dev/null 2>&1; then
      echo "selfcheck: platform v2.0.0 passed the pairing, but that tag is the one that shipped 4.0.0.json without its bundle"; good=0
    else
      ok "selfcheck: the real, immutable platform v2.0.0 fails the pairing (4.0.0.json without its bundle), as it did for three adopters on 2026-08-31"
    fi
  else
    note "selfcheck: platform tag v2.0.0 not in the clone; real-history leg of the selfcheck not run"
  fi
  if [ "$good" = 1 ]; then ok "selfcheck: a bundle-less evidence tree fails, a tags-only push line fails, a split push fails, a --dry-run fails, an empty tree fails; the repaired shapes pass"; return 0; fi
  echo "FAIL: selfcheck: the grader does not grade"; return 1
}

if [ "${1:-}" = selfcheck ]; then
  selfcheck || exit 1
  echo "PASS: selfcheck: the pairing and push-line graders bite on the 2026-08-31 shapes and pass the repaired ones"; exit 0
fi

echo "==> 0. selfcheck: the graders grade"
selfcheck || exit 1

echo "==> 1. can this check look? (platform clone with an origin/main)"
# talk/verify-all.sh assembles .estate-clone/ before any script runs; this script never clones on
# its own (a clone into a worktree whose .estate-clone/ is symlinked would replace the links).
if ! git -C "$PLATFORM" rev-parse -q --verify origin/main >/dev/null 2>&1; then
  echo "SKIP: no platform clone with an origin/main at $PLATFORM (run clone-estate.sh; needs network)"; exit 3
fi
ok "platform origin/main is $(git -C "$PLATFORM" rev-parse --short origin/main)"

echo "==> 2. every evidence document on platform origin/main has its cosign bundle beside it"
grade_pairing "$PLATFORM" origin/main "origin/main" || true

echo "==> 3. the release pushes the branch with the tags, atomically (platform b83eba1)"
grade_push_line "$PLATFORM" origin/main "origin/main" || true

echo "==> 4. the platform tag each adopter pins carries every bundle"
for a in $ADOPTERS; do
  pin="$ROOT/.estate-clone/$a/gitops/platform/platform-pin.yaml"
  if [ ! -f "$pin" ]; then note "$a: no platform-pin.yaml in the clone; not graded"; skipped=$((skipped+1)); continue; fi
  tag="$(grep -E '^[[:space:]]+tag:[[:space:]]*' "$pin" | head -1 | sed -E 's/^[[:space:]]+tag:[[:space:]]*//; s/[[:space:]]+#.*$//; s/["'"'"']//g')"
  [ -n "$tag" ] || { fail "$a: platform-pin.yaml names no tag"; continue; }
  if ! git -C "$PLATFORM" rev-parse -q --verify "refs/tags/$tag^{commit}" >/dev/null 2>&1; then
    note "$a pins platform $tag, which is not in the clone; not graded (clone-estate.sh --refresh)"; skipped=$((skipped+1)); continue
  fi
  grade_pairing "$PLATFORM" "$tag" "$a pins $tag" || true
done

echo
if [ "$bad" -gt 0 ]; then echo "FAIL: $bad finding(s): signed release evidence is not reaching what the adopters read"; exit 1; fi
if [ "$skipped" -gt 0 ]; then echo "SKIP: origin/main and its push line pass, but $skipped adopter pin(s) could not be graded (see notes above)"; exit 3; fi
echo "PASS: every evidence document on platform origin/main has its cosign bundle, the release pushes"
echo "the branch and the tags in one atomic push, and the tag each adopter pins carries every bundle (ticket 53)."
