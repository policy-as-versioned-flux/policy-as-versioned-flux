#!/usr/bin/env bash
# Runnable check: does one Renovate customManager (git-refs datasource) bump
# BOTH the fleet's nested {version,commit} array (PRD §6.4) and a consumer's
# flat {tag,commit} pin pair, off a real upstream tag it doesn't know about
# yet? (PRD §10, issue 01 — the one unexercised risk before P1.)
#
# Prereqs: git, node/npx. ~30s.
set -euo pipefail
cd "$(dirname "$0")"
WORK=./.work   # gitignored: fixture repos + generated renovate config
rm -rf "$WORK"
mkdir -p "$WORK"

echo "== 1. Upstream fixture (simulates the policy repo), tagged 1.0.0 =="
UPSTREAM="$(pwd)/$WORK/upstream"
mkdir -p "$UPSTREAM"
git -C "$UPSTREAM" init -q -b main
git -C "$UPSTREAM" config user.email test@example.com
git -C "$UPSTREAM" config user.name test
echo v1 > "$UPSTREAM/VERSION"
git -C "$UPSTREAM" add . && git -C "$UPSTREAM" commit -q -m 1.0.0
git -C "$UPSTREAM" tag -a 1.0.0 -m 1.0.0
SHA_100=$(git -C "$UPSTREAM" rev-parse 1.0.0)
echo "   1.0.0 = $SHA_100"

echo "== 2. Fleet fixture, pinned at 1.0.0 (nested array + flat consumer pin) =="
FLEET="$(pwd)/$WORK/fleet"
mkdir -p "$FLEET"
git -C "$FLEET" init -q -b main
git -C "$FLEET" config user.email test@example.com
git -C "$FLEET" config user.name test
cat > "$FLEET/fleet-resourceset-input.yaml" <<EOF
apiVersion: fluxcd.controlplane.io/v1
kind: ResourceSetInputProvider
metadata:
  name: policy-versions
spec:
  # PRD §6.4: a single {version, commit} array, one nested field of one
  # input, the ResourceSet templates range over -- the shape under test.
  defaultValues:
    policyVersions:
      - version: "1.0.0"
        commit: $SHA_100
EOF
cat > "$FLEET/consumer-pin.yaml" <<EOF
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: policy
spec:
  # A consumer's flat {tag, commit} pin pair (§6.1) -- same shape, no array.
  ref:
    tag: "1.0.0"
    commit: $SHA_100
EOF
git -C "$FLEET" add . && git -C "$FLEET" commit -q -m "pin policy 1.0.0"

echo "== 3. New upstream tag 1.1.0 lands (fleet/consumer are now behind) =="
echo v1.1 > "$UPSTREAM/VERSION"
git -C "$UPSTREAM" add . && git -C "$UPSTREAM" commit -q -m 1.1.0
git -C "$UPSTREAM" tag -a 1.1.0 -m 1.1.0
SHA_110=$(git -C "$UPSTREAM" rev-parse 1.1.0)
echo "   1.1.0 = $SHA_110"

echo "== 4. One customManager (git-refs datasource) for both files =="
# Quoted heredoc: no shell backslash-collapsing/expansion inside the regex.
# The one dynamic value (the upstream fixture path) is a placeholder, filled
# in by sed afterward.
cat > "$WORK/renovate-config.json" <<'JSONEOF'
{
  "customManagers": [
    {
      "customType": "regex",
      "managerFilePatterns": ["/^(fleet-resourceset-input|consumer-pin)\\.yaml$/"],
      "matchStrings": [
        "(?:version|tag): [\"']?(?<currentValue>[0-9.]+)[\"']?\\s*\\n\\s*commit: [\"']?(?<currentDigest>[a-f0-9]{40})[\"']?"
      ],
      "datasourceTemplate": "git-refs",
      "depNameTemplate": "file://__UPSTREAM__",
      "versioningTemplate": "semver"
    }
  ],
  "onboarding": false,
  "requireConfig": "optional"
}
JSONEOF
sed -i '' "s#__UPSTREAM__#$UPSTREAM#" "$WORK/renovate-config.json"

echo "== 5. Renovate dry run (platform=local -- preview only, writes nothing) =="
(
  cd "$FLEET"
  # Fresh cache dir every run: the fixture repo is mutated in place at a
  # fixed path across runs, and Renovate's package cache otherwise serves a
  # stale git-refs lookup keyed on that path.
  RENOVATE_CONFIG_FILE="../renovate-config.json" RENOVATE_CACHE_DIR="../renovate-cache" LOG_LEVEL=debug \
    npx --yes -p renovate renovate --platform=local
) > "$WORK/renovate.log" 2>&1 || { echo "renovate run failed:"; tail -60 "$WORK/renovate.log"; exit 1; }

echo "== 6. Verdict =="
python3 - "$WORK/renovate.log" "$SHA_100" "$SHA_110" <<'PY'
import json, sys
log, sha_old, sha_new = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(log).read()
# pull the "packageFiles with updates" JSON object logged by renovate debug
# output -- brace-count from the first '{' after the marker line, since the
# blob is pretty-printed (indentation, no surrounding quotes to regex off).
i = text.index("packageFiles with updates")
start = text.index("{", i)
depth, end = 0, start
for j in range(start, len(text)):
    depth += (text[j] == "{") - (text[j] == "}")
    if depth == 0:
        end = j + 1
        break
blob = json.loads(text[start:end])
found = {}
for entry in blob["regex"]:
    f = entry["packageFile"]
    dep = entry["deps"][0]
    upd = dep["updates"][0]
    found[f] = (dep["currentValue"], dep["currentDigest"], upd["newValue"], upd["newDigest"])

ok = True
for f in ("consumer-pin.yaml", "fleet-resourceset-input.yaml"):
    cur_v, cur_d, new_v, new_d = found[f]
    good = cur_v == "1.0.0" and cur_d == sha_old and new_v == "1.1.0" and new_d == sha_new
    ok &= good
    print(f"   {f}: {cur_v}@{cur_d[:8]} -> {new_v}@{new_d[:8]}  {'OK' if good else 'FAIL'}")

sys.exit(0 if ok else 1)
PY
