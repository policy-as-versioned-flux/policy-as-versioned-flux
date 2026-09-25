"""Ticket 87 item 1: every branch an accepted identity pattern admits is protected on the forge.

The pin and the protection must not drift apart. `verify/forge-review/forge_review.py` reads the
anchored identity patterns the estate serves, works out which branches each one admits, and grades
the forge's own answer for each of those branches (GitHub's `rules/branches/<name>`), plus a floor
on every one of the nine repositories and a tag ruleset over every release tag.
"""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(ROOT, "verify", "forge-review", "forge_review.py")
WRAPPER = os.path.join(ROOT, "verify", "forge-review", "verify-forge-review.sh")


def _load():
    spec = importlib.util.spec_from_file_location("forge_review", MOD)
    assert spec and spec.loader, f"no module at {MOD}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules["forge_review"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def fr():
    return _load()


PIN = (r"^https://github\.com/policy-as-versioned-platform/platform/\.github/workflows/"
       r"cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$")
PROPOSAL = (r"^https://github\.com/policy-as-versioned-driftwood/driftwood/\.github/workflows/"
            r"propose-tier\.yml@refs/heads/main$")

REVIEWED: list[dict] = [{"type": "creation"}, {"type": "deletion"}, {"type": "non_fast_forward"},
            {"type": "pull_request", "parameters": {"required_approving_review_count": 1}}]
MAIN_REVIEWED: list[dict] = [r for r in REVIEWED if r["type"] != "creation"]
FLOOR = [{"type": "deletion"}, {"type": "non_fast_forward"}]
TAG_RULESET = {"id": 3, "name": "release-tags-hold", "target": "tag", "enforcement": "active",
               "conditions": {"ref_name": {"include": ["~ALL"], "exclude": []}},
               "rules": [{"type": "update"}, {"type": "deletion"}]}


def test_parse_reads_repo_and_workflow_out_of_an_escaped_pattern(fr):
    p = fr.parse_pattern(PIN)
    assert (p.repo, p.workflow) == ("policy-as-versioned-platform/platform", "cut-release.yml")


def test_parse_ignores_a_pattern_that_is_not_anchored(fr):
    assert fr.parse_pattern(PIN.lstrip("^")) is None


def test_the_release_pin_admits_main_and_every_maintenance_shape_and_nothing_else(fr):
    p = fr.parse_pattern(PIN)
    got = fr.admitted(p, live=["main", "release/2.0.x", "ticket-9-x", "release/2.0"])
    assert "main" in got and "release/2.0.x" in got and "release/10.20.x" in got
    assert "ticket-9-x" not in got and "release/2.0" not in got and "master" not in got


def test_the_proposal_pin_admits_main_only(fr):
    assert fr.admitted(fr.parse_pattern(PROPOSAL), live=["main", "release/1.0.x"]) == ["main"]


def test_a_scan_finds_the_served_pattern_and_skips_captures_and_fixtures(fr, tmp_path):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "release.yml").write_text(
        f"env:\n  EXPECTED_IDENTITY_REGEXP: {PIN}\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "t.py").write_text(
        'X = r"^https://github\\.com/policy-as-versioned-platform/platform/'
        '\\.github/workflows/cut-release\\.yml@refs/heads/.*$"\n')
    subprocess.run(["git", "-c", f"core.hooksPath={tmp_path / 'nohooks'}", "init", "-q",
                    str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    found = fr.scan(str(tmp_path))
    assert [p.text for p in found] == [PIN]


def _facts(fr, main_rules, release_rules, tag_rulesets=(TAG_RULESET,), extra=None):
    repo = {"remote": "policy-as-versioned-platform/platform", "default_branch": "main",
            "branches": ["main", "release/2.0.x"], "tags": ["v1.0.0", "policy/v2.0.0"],
            "rulesets": [{"id": 1, "name": "x", "target": "branch", "enforcement": "active"},
                         *tag_rulesets],
            "branch_rules": {b: (main_rules if b == "main" else release_rules)
                             for b in ["main", *fr.PROBES, "release/2.0.x"]}}
    repo.update(extra or {})
    return {"collector": "test", "repos": {"platform": repo}}


def _grade(fr, facts):
    return fr.grade(facts, {"platform": [fr.parse_pattern(PIN)]}, env={})


def test_everything_protected_passes(fr):
    lines = _grade(fr, _facts(fr, MAIN_REVIEWED, REVIEWED))
    assert not [l for l in lines if l[0] == "FAIL"], lines
    assert [l for l in lines if l[0] == "PASS"]


def test_main_without_a_review_rule_is_red_because_the_pin_admits_main(fr):
    lines = _grade(fr, _facts(fr, FLOOR, REVIEWED))
    fails = [l[1] for l in lines if l[0] == "FAIL"]
    assert any("main" in f and "pull_request" in f for f in fails), lines


def test_an_admitted_release_branch_anyone_may_create_is_red(fr):
    no_creation = [r for r in REVIEWED if r["type"] != "creation"]
    fails = [l[1] for l in _grade(fr, _facts(fr, MAIN_REVIEWED, no_creation)) if l[0] == "FAIL"]
    assert any("release/" in f and "creation" in f for f in fails), fails


def test_a_review_count_of_zero_is_not_a_review(fr):
    zero = [dict(r, parameters={"required_approving_review_count": 0})
            if r["type"] == "pull_request" else r for r in MAIN_REVIEWED]
    fails = [l[1] for l in _grade(fr, _facts(fr, zero, REVIEWED)) if l[0] == "FAIL"]
    assert any("main" in f for f in fails), fails


def test_a_tag_no_ruleset_holds_is_red(fr):
    narrow = dict(TAG_RULESET, conditions={"ref_name": {"include": ["refs/tags/v*"],
                                                        "exclude": []}})
    fails = [l[1] for l in _grade(fr, _facts(fr, MAIN_REVIEWED, REVIEWED, (narrow,)))
             if l[0] == "FAIL"]
    assert any("policy/v2.0.0" in f for f in fails), fails


def test_a_disabled_tag_ruleset_holds_nothing(fr):
    off = dict(TAG_RULESET, enforcement="disabled")
    fails = [l[1] for l in _grade(fr, _facts(fr, MAIN_REVIEWED, REVIEWED, (off,)))
             if l[0] == "FAIL"]
    assert any("v1.0.0" in f for f in fails), fails


def test_a_bypass_actor_that_is_read_and_present_is_red(fr):
    facts = _facts(fr, MAIN_REVIEWED, REVIEWED)
    facts["repos"]["platform"]["rulesets"][0]["bypass_actors"] = [
        {"actor_id": 1, "actor_type": "OrganizationAdmin", "bypass_mode": "always"}]
    fails = [l[1] for l in _grade(fr, facts) if l[0] == "FAIL"]
    assert any("bypass" in f for f in fails), fails


def test_a_branch_the_collector_did_not_ask_about_is_a_could_not_look_not_a_pass(fr):
    facts = _facts(fr, MAIN_REVIEWED, REVIEWED)
    del facts["repos"]["platform"]["branch_rules"]["release/2.0.x"]
    lines = _grade(fr, facts)
    assert any(l[0] == "SKIP" and "release/2.0.x" in l[1] for l in lines), lines


def test_a_file_from_another_run_is_refused(fr):
    facts = _facts(fr, MAIN_REVIEWED, REVIEWED)
    facts["run_id"] = "1"
    lines = fr.grade(facts, {"platform": [fr.parse_pattern(PIN)]}, env={"GITHUB_RUN_ID": "2"})
    assert lines and all(l[0] == "SKIP" for l in lines), lines


def test_glob_matches_github_semantics(fr):
    assert fr.ref_matches("refs/tags/policy/v2.0.0", ["~ALL"], [], "main")
    assert not fr.ref_matches("refs/tags/policy/v2.0.0", ["refs/tags/v*"], [], "main")
    assert fr.ref_matches("refs/tags/policy/v2.0.0", ["refs/tags/**/v*"], [], "main")
    assert fr.ref_matches("refs/heads/main", ["~DEFAULT_BRANCH"], [], "main")
    assert not fr.ref_matches("refs/heads/release/1.0.x", ["refs/heads/release/**"],
                              ["refs/heads/release/1.*"], "main")


def test_selfcheck_bites(fr):
    assert fr.selfcheck() == 0


def test_the_wrapper_selfcheck_passes():
    done = subprocess.run(["bash", WRAPPER, "--selfcheck"], capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.strip().splitlines()[-1].startswith("PASS:")


def test_the_committed_declarations_are_what_the_check_demands(fr):
    """The files under .github/rulesets/ are what was applied; each must satisfy the rule set
    the check grades for the refs it covers, so a declaration and the grader cannot drift."""
    d = os.path.join(ROOT, ".github", "rulesets")
    decl = {n[:-5]: json.load(open(os.path.join(d, n))) for n in os.listdir(d)
            if n.endswith(".json") and n != "observation-lane.json"}
    assert {"main-is-reviewed", "release-branches-are-reviewed", "release-tags-hold",
            "main-keeps-its-history"} <= set(decl)
    types = lambda n: {r["type"] for r in decl[n]["rules"]}
    assert fr.REVIEW_RULES <= types("main-is-reviewed")
    assert fr.REVIEW_RULES | {"creation"} <= types("release-branches-are-reviewed")
    assert fr.TAG_RULES <= types("release-tags-hold")
    assert fr.FLOOR_RULES <= types("main-keeps-its-history")
    assert all(x["bypass_actors"] == [] for x in decl.values())


def test_one_repository_unread_is_a_could_not_look_even_beside_passes(fr):
    facts = _facts(fr, MAIN_REVIEWED, REVIEWED)
    facts["repos"]["nist"] = {"remote": "policy-as-versioned-nist/nist", "error": "rate limited"}
    lines = _grade(fr, facts)
    assert any(l[0] == "PASS" for l in lines)
    assert fr._exit(lines) == 3


def test_two_review_rules_on_one_branch_count_as_the_strictest(fr):
    weak = {"type": "pull_request", "parameters": {"required_approving_review_count": 0}}
    lines = _grade(fr, _facts(fr, [weak, *MAIN_REVIEWED], REVIEWED))
    assert not [l for l in lines if l[0] == "FAIL"], lines


# --- review round: the nine are a fixed set, never whatever the facts file or the clone carries --

NINE_REMOTES = {
    "hub": "policy-as-versioned-flux/policy-as-versioned-flux",
    "platform": "policy-as-versioned-platform/platform",
    "driftwood": "policy-as-versioned-driftwood/driftwood",
    "tuppence": "policy-as-versioned-tuppence/tuppence",
    "ludlow": "policy-as-versioned-ludlow/ludlow",
    "nist": "policy-as-versioned-nist/nist",
    "ico": "policy-as-versioned-ico/ico",
    "feeds": "policy-as-versioned-feeds/feeds",
    "insurer": "policy-as-versioned-insurer/insurer",
}


def _nine(fr):
    """Facts and pins for all nine, every one protected: the shape that must pass."""
    one = _facts(fr, MAIN_REVIEWED, REVIEWED)["repos"]["platform"]
    repos = {n: dict(one, remote=r) for n, r in NINE_REMOTES.items()}
    pats = {n: [] for n in NINE_REMOTES}
    pats["platform"] = [fr.parse_pattern(PIN)]
    return {"collector": "test", "repos": repos}, pats


def test_the_estate_is_the_nine_the_ticket_names(fr):
    assert fr.ESTATE == NINE_REMOTES


def test_the_fixed_nine_match_the_clones_where_they_exist(fr):
    estate = os.path.join(ROOT, ".estate-clone")
    if not os.path.isdir(estate):
        pytest.skip("no .estate-clone to compare against")
    for unit, remote in NINE_REMOTES.items():
        d = os.path.join(estate, unit)
        if unit == "hub" or not os.path.isdir(d):
            continue
        url = subprocess.run(["git", "-C", d, "remote", "get-url", "origin"],
                             capture_output=True, text=True).stdout.strip()
        assert url.removesuffix(".git").endswith(remote), (unit, url)


def test_all_nine_protected_is_a_pass_with_nine_pass_lines(fr):
    facts, pats = _nine(fr)
    lines = fr.grade(facts, pats, env={})
    assert fr._exit(lines) == 0, lines
    assert len([l for l in lines if l[0] == "PASS"]) == 9


def test_a_facts_file_naming_fewer_repositories_skips_each_absent_one_by_name(fr):
    facts, pats = _nine(fr)
    for gone in ["platform", "driftwood", "tuppence", "ludlow", "nist", "ico", "insurer"]:
        del facts["repos"][gone]
    lines = fr.grade(facts, pats, env={})
    assert fr._exit(lines) == 3, lines
    skipped = " ".join(l[1] for l in lines if l[0] == "SKIP")
    assert "platform" in skipped and "insurer" in skipped, lines


def test_a_facts_file_naming_the_wrong_remote_for_a_unit_is_not_graded_as_it(fr):
    facts, pats = _nine(fr)
    facts["repos"]["nist"]["remote"] = "policy-as-versioned-nist/elsewhere"
    lines = fr.grade(facts, pats, env={})
    assert fr._exit(lines) == 3, lines
    assert any(l[0] == "SKIP" and l[1].startswith("nist:") for l in lines), lines


def test_a_repository_whose_checkout_was_not_read_is_a_could_not_look(fr):
    facts, pats = _nine(fr)
    del pats["platform"]
    lines = fr.grade(facts, pats, env={})
    assert fr._exit(lines) == 3, lines
    assert any(l[0] == "SKIP" and l[1].startswith("platform:") for l in lines), lines


def test_patterns_by_repo_leaves_out_a_unit_with_no_clone_or_the_wrong_remote(fr, tmp_path):
    estate = tmp_path / "estate"
    hooks = tmp_path / "nohooks"
    hooks.mkdir()
    for unit, url in [("platform", "https://github.com/policy-as-versioned-platform/platform"),
                      ("nist", "https://github.com/policy-as-versioned-nist/elsewhere")]:
        d = estate / unit
        d.mkdir(parents=True)
        subprocess.run(["git", "-c", f"core.hooksPath={hooks}", "init", "-q", str(d)], check=True)
        subprocess.run(["git", "-C", str(d), "remote", "add", "origin", url], check=True)
    (estate / "ico").mkdir()  # a directory that is not a checkout
    got = fr.patterns_by_repo(ROOT, str(estate))
    assert "platform" in got and "hub" in got
    assert "nist" not in got and "ico" not in got and "feeds" not in got, sorted(got)
