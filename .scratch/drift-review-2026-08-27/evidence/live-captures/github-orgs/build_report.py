import json, os, glob

D = os.path.dirname(os.path.abspath(__file__))
repos_dir = os.path.join(D, "raw", "repos")

def load(path, default=None):
    try:
        with open(path) as f:
            content = f.read()
            if not content.strip():
                return default
            return json.loads(content)
    except Exception:
        return default

def load_text(path):
    try:
        with open(path) as f:
            return f.read()
    except Exception:
        return ""

rows = []
result = {"orgs": {}}

for repo_dir in sorted(glob.glob(os.path.join(repos_dir, "*"))):
    base = os.path.basename(repo_dir)
    org, repo = base.split("__", 1)
    repo_json = load(os.path.join(repo_dir, "repo.json"), {})
    tags = load(os.path.join(repo_dir, "tags.json"), [])
    releases = load(os.path.join(repo_dir, "releases.json"), [])
    prs = load(os.path.join(repo_dir, "prs.json"), [])
    runs = load(os.path.join(repo_dir, "runs.json"), [])
    rulesets = load(os.path.join(repo_dir, "rulesets.json"), [])
    renovate_err = load_text(os.path.join(repo_dir, "renovate.err"))
    renovate_present = "Not Found" not in renovate_err and renovate_err.strip() == ""
    readme = load_text(os.path.join(repo_dir, "readme.md"))
    readme_h1 = ""
    for line in readme.splitlines():
        if line.strip().startswith("#"):
            readme_h1 = line.strip()
            break
    default_branch = repo_json.get("default_branch", "?")
    pushed_at = repo_json.get("pushed_at", "?")
    archived = repo_json.get("archived", False)
    tag_names = [t.get("name") for t in tags] if isinstance(tags, list) else []
    release_summaries = [f"{r.get('tagName')}{' (draft)' if r.get('isDraft') else ''}{' (pre)' if r.get('isPrerelease') else ''}" for r in releases] if isinstance(releases, list) else []
    pr_summaries = [f"#{p.get('number')} {p.get('title')!r} by {p.get('author',{}).get('login')} ({p.get('createdAt')})" for p in prs] if isinstance(prs, list) else []
    run_summaries = [f"{r.get('workflowName')}: {r.get('conclusion') or r.get('status')} ({r.get('createdAt')})" for r in runs] if isinstance(runs, list) else []
    ruleset_summaries = [f"{r.get('name')} ({r.get('target')})" for r in rulesets] if isinstance(rulesets, list) else []

    entry = {
        "org": org, "repo": repo,
        "default_branch": default_branch,
        "pushed_at": pushed_at,
        "archived": archived,
        "tags": tag_names,
        "releases": release_summaries,
        "open_prs": pr_summaries,
        "last_5_runs": run_summaries,
        "rulesets": ruleset_summaries,
        "renovate_json_present": renovate_present,
        "readme_h1": readme_h1,
    }
    result["orgs"].setdefault(org, []).append(entry)
    rows.append(entry)

with open(os.path.join(D, "report_data.json"), "w") as f:
    json.dump(result, f, indent=2)

# markdown
lines = ["# GitHub orgs live state — captured 2026-08-27\n"]
for org, entries in result["orgs"].items():
    lines.append(f"\n## {org}\n")
    lines.append("| repo | default branch | last push | archived | tags | releases | open PRs | last 5 runs | rulesets | renovate.json | README H1 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for e in entries:
        lines.append("| " + " | ".join([
            e["repo"], e["default_branch"], e["pushed_at"], str(e["archived"]),
            ", ".join(e["tags"]) or "-",
            "; ".join(e["releases"]) or "-",
            "; ".join(e["open_prs"]) or "-",
            "; ".join(e["last_5_runs"]) or "-",
            "; ".join(e["rulesets"]) or "-",
            "yes" if e["renovate_json_present"] else "no",
            e["readme_h1"] or "-",
        ]) + " |")

with open(os.path.join(D, "state.md"), "w") as f:
    f.write("\n".join(lines) + "\n")

print("wrote", os.path.join(D, "state.md"))
print("wrote", os.path.join(D, "report_data.json"))
print("total repos:", len(rows))
