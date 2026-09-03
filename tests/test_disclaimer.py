"""Ticket 82: every party artefact and README carries the demonstration disclaimer, the
regulators carry a DISCLAIMER.md, nist's NOTICE cites the catalogue it attributes, and the
hub is licensed. The seam is verify/disclaimer/disclaimer.py's pure functions over a
directory; the real estate is graded by `verify/disclaimer/verify-disclaimer.sh`, not here."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "disclaimer", ROOT / "verify" / "disclaimer" / "disclaimer.py")
assert _spec and _spec.loader
disclaimer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(disclaimer)

LINE = disclaimer.DISCLAIMER


def _unit(tmp: Path, name: str, *, party_line: str | None = f"# {LINE}",
          readme_line: str | None = LINE) -> Path:
    d = tmp / name
    d.mkdir()
    body = f"party: {name}\nroles: [publisher]\ninherits: []\noverlay: {{add: [], restate: []}}\n"
    (d / "party.yaml").write_text((party_line + "\n" if party_line else "") + body)
    (d / "README.md").write_text(f"# {name}\n\n" + (readme_line or "") + "\n")
    return d


def _nist(tmp: Path) -> Path:
    d = _unit(tmp, "nist")
    cat = d / "catalog"
    cat.mkdir()
    (cat / "CATALOG_VERSION.json").write_text(json.dumps({
        "file": "catalog.json", "sha256": hashlib.sha256(b"cat").hexdigest(),
        "source": {"url": "https://example.test/catalog.json", "nistMetadataVersion": "5.2.0"}}))
    (cat / "BASELINE_VERSIONS.json").write_text(json.dumps({
        "baselines": {n: {"file": f"{n}.json", "sha256": hashlib.sha256(n.encode()).hexdigest()}
                      for n in ("LOW", "MODERATE", "HIGH")}}))
    (d / "NOTICE").write_text(disclaimer.render_notice(d))
    (d / "DISCLAIMER.md").write_text(f"# Disclaimer\n\n{LINE}\n")
    return d


def test_the_line_names_the_two_facts_the_ticket_asks_for():
    assert "demonstration party" in LINE
    assert "not affiliated" in LINE
    assert "\n" not in LINE


def test_party_yaml_line_must_be_a_comment_not_a_key(tmp_path: Path):
    ok = _unit(tmp_path, "ok")
    assert disclaimer.party_yaml_problems(ok / "party.yaml") == []
    missing = _unit(tmp_path, "missing", party_line=None)
    assert any("no disclaimer comment" in p for p in disclaimer.party_yaml_problems(missing / "party.yaml"))
    as_key = _unit(tmp_path, "askey", party_line=f"disclaimer: {LINE}")
    problems = disclaimer.party_yaml_problems(as_key / "party.yaml")
    assert problems and "comment" in problems[0]
    absent = disclaimer.party_yaml_problems(tmp_path / "nowhere" / "party.yaml")
    assert absent and "missing" in absent[0]


def test_readme_must_carry_the_line(tmp_path: Path):
    ok = _unit(tmp_path, "ok")
    assert disclaimer.readme_problems(ok / "README.md") == []
    bare = _unit(tmp_path, "bare", readme_line="A README that says nothing about being a demo.")
    assert disclaimer.readme_problems(bare / "README.md")


def test_notice_must_cite_the_catalogue_it_attributes(tmp_path: Path):
    nist = _nist(tmp_path)
    assert disclaimer.notice_problems(nist) == []
    # a drifted NOTICE: the sha256 it cites is not the one CATALOG_VERSION.json records
    text = (nist / "NOTICE").read_text()
    cat = json.loads((nist / "catalog" / "CATALOG_VERSION.json").read_text())
    (nist / "NOTICE").write_text(text.replace(cat["sha256"], "0" * 64))
    problems = disclaimer.notice_problems(nist)
    assert problems and "sha256" in problems[0]
    (nist / "NOTICE").unlink()
    assert any("NOTICE" in p and "missing" in p for p in disclaimer.notice_problems(nist))


def test_disclaimer_md_required_of_the_regulators_only(tmp_path: Path):
    nist = _nist(tmp_path)
    assert disclaimer.disclaimer_md_problems(nist) == []
    (nist / "DISCLAIMER.md").write_text("# Disclaimer\n\nnothing of substance\n")
    assert disclaimer.disclaimer_md_problems(nist)
    assert set(disclaimer.REGULATORS) == {"ico", "nist"}


def test_hub_license_is_apache_2(tmp_path: Path):
    hub = tmp_path / "hub"
    hub.mkdir()
    (hub / "README.md").write_text("# hub\n")
    assert any("LICENSE" in p for p in disclaimer.hub_problems(hub))
    (hub / "LICENSE").write_text("Apache License\nVersion 2.0, January 2004\n")
    assert any("README" in p for p in disclaimer.hub_problems(hub))
    (hub / "README.md").write_text("# hub\n\n**Licence:** [Apache-2.0](LICENSE)\n")
    assert disclaimer.hub_problems(hub) == []


def test_check_all_walks_every_declared_party_and_refuses_one_planted_violation(tmp_path: Path):
    estate = tmp_path / "estate"
    estate.mkdir()
    hub = tmp_path / "hub"
    hub.mkdir()
    (hub / "LICENSE").write_text("Apache License\nVersion 2.0, January 2004\n")
    (hub / "README.md").write_text("**Licence:** [Apache-2.0](LICENSE)\n")
    parties = ["ico", "nist", "feeds"]
    _nist(estate)
    ico = _unit(estate, "ico")
    (ico / "DISCLAIMER.md").write_text(f"# Disclaimer\n\n{LINE}\n")
    _unit(estate, "feeds")
    assert disclaimer.check_all(parties, estate_dir=estate, hub_root=hub) == []
    (estate / "feeds" / "party.yaml").write_text("party: feeds\nroles: [publisher]\ninherits: []\noverlay: {add: [], restate: []}\n")
    problems = disclaimer.check_all(parties, estate_dir=estate, hub_root=hub)
    assert len(problems) == 1 and problems[0].startswith("feeds/party.yaml")
    # a party roles.json declares but the estate does not hold is a refusal, not a silent pass
    problems = disclaimer.check_all(parties + ["ghost"], estate_dir=estate, hub_root=hub)
    assert any(p.startswith("ghost/party.yaml") for p in problems)


@pytest.mark.parametrize("unit", ["platform", "driftwood", "tuppence", "ludlow", "nist", "ico", "feeds", "insurer"])
def test_the_real_estate_when_cloned(unit: str):
    """The same fact the gate grades, readable from pytest when the clone is present."""
    d = ROOT / ".estate-clone" / unit
    if not (d / "party.yaml").is_file():
        pytest.skip(f"no .estate-clone/{unit}: run ./clone-estate.sh")
    assert disclaimer.party_yaml_problems(d / "party.yaml") == []
    assert disclaimer.readme_problems(d / "README.md") == []
