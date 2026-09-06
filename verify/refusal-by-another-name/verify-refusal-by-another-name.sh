#!/usr/bin/env bash
# Beat (eco-system ticket 98): "a refusal by another name is graded by nothing."
#
# It was graded by nothing until this script. The estate's doctrine is that nothing is denied and
# a workload that does not fit its cage runs on a tighter rung; ticket 89 built the register that
# grades every Deny-shaped rule. A MUTATION carries no Deny-shaped text at all and can stop a
# workload just as dead -- and this estate has produced four of them, every one found by RUNNING
# a policy and none by reading one:
#
#   1. 2026-08-28 (ticket 26)   the priority trio, and a WAF sidecar appended twice
#   2. 2026-09-05 (ticket 89)   a PriorityClass name no cluster has
#   3. 2026-09-05 (ticket 89)   the full cage body on UPDATE, over a running pod
#   4. LIVE TODAY (ticket 89 S3, decided rather than fixed) -- adding a served-version claim to a
#      bottom-rung pod makes cage-tier rewrite priorityClassName and priority, and the API server
#      refuses. That refusal is the CORRECT outcome; the remediation is a recreate.
#
# WHAT THIS GRADES, four legs, and what each one caught:
#   A  every name a mutation writes into a REFERENCE field is one the SAME RELEASE ships    (2)
#   B  an UPDATE-scoped mutation is identical applied to its own output -- EXECUTED, on every
#      rung of the ladder, because reading a body has never once caught one of these         (1b)
#   C  a field a mutation writes is one the resource allows to change on that OPERATION,
#      joined to register.yaml, which records the refusals the estate has DECIDED to accept (3,4)
#   D  a mutation that writes priorityClassName writes the whole priority trio               (1a)
#
#   PASS (exit 0)  every mutation on the SERVED surface passes all four legs, and every write a
#                  running pod forbids is recorded in register.yaml with a reason, a remediation
#                  and the check that bounds it. The accepted ones are printed on every run
#   FAIL (exit 1)  a dangling reference name; a broken priority trio; a mutation that rewrites
#                  its own output; a write on UPDATE no register row records; a register row
#                  that no longer describes the code, in either direction; or a leg that could
#                  not make anything apply -- a step that passes because NOTHING applied is the
#                  exact defect this ticket exists to catch
#   SKIP (exit 3)  no .estate-clone, so the served copies were never looked at; or a reference
#                  name this scan could not resolve offline, which is a could-not-look and never
#                  a pass
#
# THE HARD PART, stated where it is done rather than in a footnote. `kyverno apply` (1.18.2) has
# NO UPDATE MODE. Measured here on every run, not disclosed: against an UPDATE-scoped policy it
# prints "Mutation has been applied successfully", writes an UNMUTATED <name>-mutated.yaml and
# counts `pass: 0`. So a beat that reads the file's existence, or greps that sentence, measures
# nothing and calls it a pass. Leg B therefore asserts operation scoping STRUCTURALLY from the
# manifest, rewrites the operations on a THROWAWAY copy before executing the body, prints every
# difference between that copy and the served one, reads the PASS COUNT rather than the file, and
# fails outright when nothing applied. The day the CLI grows an UPDATE mode, step 0's probe goes
# red and says to rewrite this -- which is the only way a disclosed limit does not go stale.
#
# WHAT IT CANNOT SEE is refusal_scan.BLIND_SPOTS, printed on every run, every line DATED. The
# first is the live half: whether the API SERVER accepts the mutated object. That belongs where a
# cluster is -- ../../.estate-clone/platform/graded/verify-graded.sh's cluster tail, which this
# ticket extended and which has never had a cluster on a citable run (review finding P2-6).
#
#   verify-refusal-by-another-name.sh             the four replays, then grade the estate
#   verify-refusal-by-another-name.sh --selfcheck the graders' own asserts and planted defects
#   verify-refusal-by-another-name.sh --inventory every mutation found, and what is not graded
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
PY="${PYTHON:-python3}"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

selfcheck() {
  "$PY" "$HERE/refusal_scan.py" --selfcheck || return 1
  "$PY" "$HERE/refusal_probe.py" --selfcheck || return 1
}

case "${1:-}" in
  --selfcheck)
    say "0. the graders can fail"
    selfcheck || { echo "FAIL: selfcheck: a grader did not go red on a planted defect"; exit 1; }
    echo "PASS: selfcheck: the CEL body is read for what it writes, an unrecorded write on UPDATE fails, an accepted one is reported with its reason, a stale or narrowed register row fails, a dangling reference name fails, the 2026-08-28 sidecar body is caught by execution, a policy that applies to nothing refuses to pass, and the kyverno CLI's missing UPDATE mode is measured rather than disclosed"
    exit 0 ;;
  --inventory)
    exec "$PY" "$HERE/refusal_scan.py" --root "$ROOT" --inventory ;;
esac

command -v kyverno >/dev/null 2>&1 || {
  echo "FAIL: the kyverno CLI is not on PATH, so leg B could not execute a single mutation and the only leg that has ever caught one of these measured nothing. A runner that has lost its instrument goes red rather than shrugging"
  exit 1; }

say "0. the graders can fail (planted defects, and the CLI's missing UPDATE mode, measured)"
selfcheck || { echo "FAIL: selfcheck: a grader did not go red on a planted defect"; exit 1; }

if [ ! -d "$ROOT/.estate-clone" ]; then
  echo "SKIP: no .estate-clone (run clone-estate.sh), so no served policy copy was read at all -- the mutations that reach a cluster live in platform's version trees and the three adopters' composed artefacts, and none of them was looked at"
  exit 3
fi

say "1. what this scan cannot see (dated, because a disclosed limit goes stale like any other)"
"$PY" - "$HERE" <<'BS'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("rs", sys.argv[1] + "/refusal_scan.py")
rs = importlib.util.module_from_spec(spec); sys.modules["rs"] = rs; spec.loader.exec_module(rs)
for b in rs.BLIND_SPOTS:
    print(f"  ??   blind spot: {b}")
BS

say "2. the four instances, replayed against the estate's own bodies -- each must go RED"
"$PY" "$HERE/replays.py" || {
  echo "FAIL: an instance this estate really produced was NOT caught by the check built to catch it"
  exit 1; }

say "3. every mutating policy, and which surface it is on"
"$PY" "$HERE/refusal_scan.py" --root "$ROOT" --inventory | sed 's/^/  /'

say "4. legs A, C and D over the served surface"
"$PY" "$HERE/refusal_scan.py" --root "$ROOT" --register "$HERE/register.yaml"
static=$?

say "5. leg B: every UPDATE-scoped mutation applied to its own output, on every rung it reaches"
# Only UPDATE-scoped mutations are probed: a CREATE-only mutation never meets its own output,
# because the object it writes does not exist until it has written it.
"$PY" "$HERE/refusal_probe.py" --root "$ROOT"
functional=$?

if [ "$static" != 0 ] && [ "$static" != 3 ]; then exit "$static"; fi
if [ "$functional" != 0 ]; then exit "$functional"; fi
if [ "$static" = 3 ]; then
  # The could-not-look has to be the LAST line, because that is the line the manifest judges --
  # and step 5 ran after step 4 and printed over it.
  echo "SKIP: a name a mutation writes into a reference field could not be resolved offline (named in step 4), so this run could not look at every name -- an unresolved name is never a pass"
  exit 3
fi
echo "PASS: every mutation the estate SERVES was graded four ways -- every name written into a reference field is one its own release ships, every priority trio is whole, every UPDATE-scoped mutation was EXECUTED against its own output on every rung it reaches and came back identical, and every write a running pod forbids is recorded in register.yaml with a reason, a remediation and the leg that bounds it. The one live refusal (ticket 89 S3: a served-version claim added to a bottom-rung pod) is reported with its remediation rather than called a defect, and the row is graded in both directions so it cannot outlive the code. The four instances the estate has produced were replayed against its own bodies and every one went red. The authoring tree, the pruned version directories and the renderers' fixture directory were named and NOT graded, because a file on disk is not a policy on a cluster."
exit 0
