#!/usr/bin/env bash
# Beat (eco-system ticket 83): "the TRUTH line says what it measured."
#
# `pass=57 fail=7 skip=18 total=84` cannot tell a loosely coupled eco-system from one party
# testing itself. talk/verify-manifest.txt classes every script the gate discovers and declares
# the could-not-look each is allowed; talk/verify-all.sh prints the split of passes by class,
# the split of skips by kind, and the ceiling. This script is the gate asking whether that
# instrument is still whole and still honest.
#
# WHAT THIS GRADES, and what it does not. It grades the RECORD-KEEPING: that the manifest covers
# the surface in both directions, that the loader still refuses a bad line, that verify-all.sh
# still turns an undeclared skip red and a stale `never` red, that the arithmetic on the last
# recorded TRUTH line adds up, and that the sentence the deck publishes under that line counts
# the same population the ceiling was cut from. It does not grade whether any class assignment is
# the right one -- a judgement no script can make -- and it does not re-run the estate.
#
# It is deliberately NOT the same question as verify/every-green/ (ticket 76). That one reads
# the SHAPE of every discovered script and refuses a printed SKIP that reaches exit 0: whether a
# green was honestly reached. This one reads the MANIFEST: what a green rests on, and whether a
# could-not-look was expected. A script can be honest in shape and unplaced in the manifest, or
# placed and dishonest. Neither net catches the other's fish, and neither reruns the other.
#
#   PASS (exit 0)  the manifest covers every discovered script, the loader and the gate's own
#                  selfchecks bite, and the last recorded TRUTH line's arithmetic holds
#   FAIL (exit 1)  one of those is false, named
#   SKIP (exit 3)  no .estate-clone to discover (half the surface is missing, so coverage
#                  cannot be observed), or no python3
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT" || { echo "FAIL: cannot enter the hub root"; exit 1; }
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY=python3
command -v "$PY" >/dev/null 2>&1 || { echo "SKIP: no python3 to read the manifest with"; exit 3; }
[ -d "$ROOT/.estate-clone" ] || { echo "SKIP: no .estate-clone (run clone-estate.sh); only the hub's own verify/ is discoverable, which is not the surface the manifest claims to cover"; exit 3; }

bad=0
note() { echo "  !! $*"; bad=$((bad + 1)); }

say "1. the manifest loader refuses what it should: bad class, bad skip kind, uncompilable pattern, duplicate"
"$PY" talk/truth_manifest.py selfcheck || note "talk/truth_manifest.py selfcheck did not pass"

say "2. the gate's own instrument grades a planted pass, skip, fail, undeclared skip, unlisted script, exclusion and stale never as documented"
bash talk/verify-all.sh --selfcheck || note "talk/verify-all.sh --selfcheck did not pass"

say "3. the manifest covers every script the gate discovers right now, in both directions"
scripts="$(mktemp)"; trap 'rm -f "$scripts"' EXIT
find -L .estate-clone verify -name 'verify*.sh' -not -path '*/.work/*' -not -path '*/.git/*' | sort >"$scripts"
n="$(grep -c . "$scripts" | tr -d ' ')"
cover="$("$PY" talk/truth_manifest.py check talk/verify-manifest.txt \
           --exclusions talk/verify-exclusions.txt --scripts "$scripts")"
crc=$?
[ -n "$cover" ] && printf '%s\n' "$cover"
[ "$crc" -eq 0 ] || note "talk/verify-manifest.txt does not cover the $n discovered scripts (above)"

say "4. the last TRUTH line talk/truth.log recorded still adds up"
arith="$("$PY" - <<'EOF'
import sys
sys.path.insert(0, "talk")
from truth_manifest import SKIP_KINDS, SPLIT_KEYS, parse_truth

lines = [l for l in open("talk/truth.log", encoding="utf-8") if l.startswith("TRUTH ")]
if not lines:
    print("no TRUTH line in talk/truth.log yet")
    raise SystemExit(0)
t = parse_truth(lines[-1])
if t["split"] is None:
    print(f"run {t['run']} predates the manifest: it carries no split and no ceiling, so there "
          f"is no arithmetic to check yet -- the first line with one comes from the next "
          f"scheduled run")
    raise SystemExit(0)
problems = []
if sum(t["split"].get(k, 0) for k in SPLIT_KEYS) != t["pass"]:
    problems.append(f"the split {t['split']} does not sum to pass={t['pass']}")
if t["skip_split"] is None or sum(t["skip_split"].get(k, 0) for k in SKIP_KINDS) != t["skip"]:
    problems.append(f"the skip split {t['skip_split']} does not sum to skip={t['skip']}")
if not 0 <= t["ceiling"] <= t["total"]:
    problems.append(f"ceiling={t['ceiling']} is not between 0 and total={t['total']}")
if t["pass"] > t["ceiling"]:
    problems.append(f"pass={t['pass']} is above the ceiling of {t['ceiling']}, which means the "
                    f"manifest calls a script `never` that passed")
print("\n".join(problems) if problems else
      f"run {t['run']}: {t['pass']} passes split {t['split']}, ceiling {t['ceiling']} of "
      f"{t['total']}, skips {t['skip_split']}")
raise SystemExit(1 if problems else 0)
EOF
)"; arc=$?
printf '  %s\n' "$arith"
[ "$arc" -eq 0 ] || note "the last recorded TRUTH line does not add up"

say "5. the sentence the deck publishes counts the same 'can never pass' population the ceiling does"
# Two different never numbers exist and only one of them is the ceiling's. The skip split's
# `never` counts the never-classed scripts that SKIPPED; the ceiling subtracts every non-excluded
# never-classed script, whatever it exited. A never-classed script that FAILS makes them diverge,
# and a sentence quoting the skip split then stops adding up. Graded on a fixture line built to
# diverge (this leg fails on any measured() that reads the skip split) and on the real last line.
pop="$("$PY" - <<'EOF'
import re
import sys
sys.path.insert(0, "talk")
from truth_manifest import measured, parse_truth

STATED = re.compile(r"\((\d+) excluded, (\d+) can never pass on this runner\)")


def check(label, line):
    t = parse_truth(line)
    if t["ceiling"] is None:
        return [f"{label}: carries no ceiling, nothing to add up"]
    m = STATED.search(measured(line))
    if not m:
        return [f"{label}: measured() does not state the excluded and never-pass counts"]
    excluded, stated = int(m.group(1)), int(m.group(2))
    want = t["total"] - t["excluded"] - t["ceiling"]
    out = []
    if excluded != t["excluded"]:
        out.append(f"{label}: the sentence says {excluded} excluded, the line says {t['excluded']}")
    if stated != want:
        out.append(f"{label}: the sentence says {stated} can never pass, but the ceiling was cut "
                   f"from a population of total {t['total']} - excluded {t['excluded']} - ceiling "
                   f"{t['ceiling']} = {want}; measured() is counting the skip split's never "
                   f"({(t['skip_split'] or {}).get('never')}), not the ceiling's")
    return out


problems = []
# a planted line where a never-classed script failed instead of skipping: never-classed
# population is 11 - 1 - 7 = 3, the skip split's never is 1
problems += check("the planted divergent line",
                  "TRUTH 2026-09-04T12:00Z run=fixture hub=0000000 units=[platform=46cd775] "
                  "pass=5 [observed=2 self=2 simulated=1 meta=0] fail=3 skip=2 [never=1 waits=1] "
                  "excluded=1 total=11 ceiling=7")
lines = [l for l in open("talk/truth.log", encoding="utf-8") if l.startswith("TRUTH ")]
if lines and parse_truth(lines[-1])["ceiling"] is not None:
    problems += check(f"run {parse_truth(lines[-1])['run']}", lines[-1])
    print(measured(lines[-1]))
else:
    print("the last recorded TRUTH line carries no ceiling; only the planted line is graded here")
print("\n".join(problems), end="" if not problems else "\n")
raise SystemExit(1 if problems else 0)
EOF
)"; prc=$?
printf '  %s\n' "$pop"
[ "$prc" -eq 0 ] || note "the published 'can never pass' count is not the ceiling's population"

if [ "$bad" -eq 0 ]; then
  echo "PASS: talk/verify-manifest.txt places every one of the $n verify scripts this checkout discovers, the loader refuses a malformed or stale line, talk/verify-all.sh turns an undeclared could-not-look and a stale ceiling red, the last TRUTH line talk/truth.log recorded adds up, and the published 'can never pass' count is the population the ceiling was cut from"
  exit 0
fi
echo "FAIL: $bad truth-line check(s) observed false (named above): the split, the ceiling or the manifest behind them cannot be trusted"
exit 1
