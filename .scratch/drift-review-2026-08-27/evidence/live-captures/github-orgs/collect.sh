#!/bin/zsh
set -o pipefail
D=/private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/417e2917-726b-46c9-9117-7b880114f08b/scratchpad/live/github-orgs
ORGS=(policy-as-versioned-flux policy-as-versioned-platform policy-as-versioned-driftwood policy-as-versioned-tuppence policy-as-versioned-ludlow policy-as-versioned-nist policy-as-versioned-ico)
for org in "${ORGS[@]}"; do
  repos=($(jq -r '.[].name' "$D/raw/${org}-repos.json"))
  for repo in "${repos[@]}"; do
    R="$org/$repo"
    OUT="$D/raw/repos/${org}__${repo}"
    mkdir -p "$OUT"
    echo "collecting $R"
    gh api "repos/$R" > "$OUT/repo.json" 2>"$OUT/repo.err"
    gh api "repos/$R/tags" > "$OUT/tags.json" 2>"$OUT/tags.err"
    gh release list -R "$R" --limit 20 --json tagName,name,isDraft,isPrerelease,publishedAt > "$OUT/releases.json" 2>"$OUT/releases.err"
    gh pr list -R "$R" --state open --limit 50 --json number,title,author,createdAt > "$OUT/prs.json" 2>"$OUT/prs.err"
    gh run list -R "$R" --limit 5 --json displayTitle,conclusion,status,createdAt,headBranch,workflowName > "$OUT/runs.json" 2>"$OUT/runs.err"
    gh api "repos/$R/rulesets" > "$OUT/rulesets.json" 2>"$OUT/rulesets.err"
    gh api "repos/$R/contents/renovate.json" > "$OUT/renovate.json" 2>"$OUT/renovate.err"
    gh api "repos/$R/readme" -H "Accept: application/vnd.github.raw" > "$OUT/readme.md" 2>"$OUT/readme.err"
    gh api "repos/$R/git/refs/tags" > "$OUT/refs_tags.json" 2>"$OUT/refs_tags.err"
  done
done
echo DONE
