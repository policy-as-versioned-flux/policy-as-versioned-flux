#!/usr/bin/env bash
# Beat (eco-system ticket 89): "deny is not a rung."
#
# The owner, 2026-09-02 (ticket 75 Q5): "something could find itself unable to run, but that's
# only because it doesn't fit the cage, not because we deliberately deny it. So, in Kubernetes
# Parlance, we've built a Mutating admission controller more than a Approving admission and
# control." NORTH-STAR principle 2 and CONTEXT.md's Cage entry carry that sentence. The served
# policy did not: the 2026-09-02 review found Deny-shaped rules shipping in platform's
# ResourceSet, in every served version directory and in all three adopters' composed artefacts.
#
# WHAT THIS GRADES. Every Deny-shaped rule the hub and the estate clone carry, joined to
# verify/deny-is-not-a-rung/register.yaml, which records per rule whether it was re-expressed as
# a cage constraint or retired, and why. Two shapes count as Deny-shaped: the CEL
# ValidatingPolicy's `spec.validationActions` carrying `Deny` (ADR-0003) and the 2022
# ClusterPolicy's `validationFailureAction: enforce`. The scan is line-based, not
# document-based, because three of the estate's Denys live inside a ResourceSet's
# `resourcesTemplate` STRING, where a YAML-document walk sees a ResourceSet and no policy at all.
#
#   PASS (exit 0)  every Deny-shaped rule is recorded with a choice and a reason, and none is
#                  left in a served copy
#   FAIL (exit 1)  a Deny no register row claims; a row that says converted while a copy
#                  survives; a row that says a copy survives when none does; a row whose source
#                  no longer emits the Deny while the row still says `waiting`; a row with no
#                  reason, no `awaits`, or a choice that is not one of the two the ticket allows
#   SKIP (exit 3)  a recorded choice is made and the copies that carry it are composed under a
#                  PINNED, SIGNED tag that has not been cut, so they cannot honestly change yet;
#                  the line names each rule and the tag it waits for. Also when there is no
#                  .estate-clone to read, which is most of the surface.
#
# It never edits a policy and never asserts a tag exists. A conversion becomes true in the estate
# when the owner merges the platform branch, `cut-release.yml` cuts the signed tag and each
# adopter's pin bump re-composes; until then this exits 3 and NAMES what it waits for.
#
#   verify-deny-is-not-a-rung.sh             selfcheck first, then grade the hub and the estate
#   verify-deny-is-not-a-rung.sh --selfcheck selfcheck only: the grader's own asserts, plus a
#                                            planted undeclared Deny that must FAIL
#   verify-deny-is-not-a-rung.sh --inventory the inventory, one row per finding (item 1's record)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
REG="$HERE/register.yaml"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

selfcheck() {
  local t good=1 rc=0
  python3 "$HERE/deny_register.py" --selfcheck || return 1
  # The grader must fail on a Deny nobody recorded. Plant one in a throwaway root with the real
  # register, and require exit 1 -- so a grader that stopped grading fails the gate here rather
  # than shipping a quiet PASS over a real refusal.
  t="$(mktemp -d)"
  mkdir -p "$t/planted"
  cat > "$t/planted/deny.yaml" <<'YAML'
apiVersion: policies.kyverno.io/v1alpha1
kind: ValidatingPolicy
metadata:
  name: a-refusal-nobody-recorded
spec:
  validationActions: [Deny]
YAML
  python3 "$HERE/deny_register.py" --root "$t" --register "$REG" >/dev/null 2>&1; rc=$?
  rm -rf "$t"
  if [ "$rc" != 1 ]; then
    echo "FAIL: selfcheck: a planted, unrecorded Deny graded $rc (want 1) -- the grader does not grade"
    good=0
  fi
  [ "$good" = 1 ] || return 1
  echo "  ok   selfcheck: the grader fails an undeclared Deny, fails a dirty source, fails a register that is behind the code, and could-not-looks with the tag named"
}

case "${1:-}" in
  --selfcheck)
    selfcheck || exit 1
    echo "PASS: selfcheck: an unrecorded Deny fails, a source that still emits one fails, a register behind the code fails, and an outstanding copy could-not-looks with its tag named"
    exit 0 ;;
  --inventory)
    exec python3 "$HERE/deny_register.py" --root "$ROOT" --register "$REG" --inventory ;;
esac

say "0. the grader can fail"
selfcheck || exit 1

if [ ! -d "$ROOT/.estate-clone" ]; then
  echo "SKIP: no .estate-clone (run clone-estate.sh), so only the hub's own tree was read and the served policy copies -- platform's version directories and the three adopters' composed artefacts -- were never looked at"
  exit 3
fi

say "1. every Deny-shaped rule in the hub and the estate, against the recorded choices"
python3 "$HERE/deny_register.py" --root "$ROOT" --register "$REG" --inventory | sed 's/^/  /'
python3 "$HERE/deny_register.py" --root "$ROOT" --register "$REG"
exit $?
