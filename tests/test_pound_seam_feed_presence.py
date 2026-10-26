"""TEST_ONLY: declared ICO feed presence through the real estate/document seam.

Only unrelated estate-wide financial checks and non-regime context readers are stubbed.
Party/feed files, run(), _parties(), _regime_weights() and check_doc() are real.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def grader() -> ModuleType:
    spec = importlib.util.spec_from_file_location("pound_feed_presence", ROOT / "verify/pound-seam/pound_seam.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _estate(tmp_path: Path, grader: ModuleType, *, declared: bool = True,
            feed_available: bool = True) -> tuple[Path, dict]:
    estate = tmp_path / "estate"
    for name in ("driftwood", "ico", "nist", "platform"):
        party: dict = {}
        if name == "driftwood":
            party = {"roles": ["adopter"], "size": {"customers": 100},
                     "publishes": [{"name": "forward-intel"}],
                     "inherits": ([{"party": "ico", "kind": "feed", "name": "penalty-schema", "version": "v3"}]
                                  if declared else [])}
        if name == "ico":
            party = {"publishes": [{"name": "penalty-schema", "path": "penalty-schema"}]}
        folder = estate / name
        folder.mkdir(parents=True)
        (folder / "party.yaml").write_text(json.dumps(party))
    if feed_available:
        feed = estate / "ico/penalty-schema/v3/feed.json"
        feed.parent.mkdir(parents=True)
        feed.write_text(json.dumps({"payload": {"control_weights": {"ac-6": 1.0}}}))
    policy = estate / "driftwood/selection-policy/VERSION"
    policy.parent.mkdir()
    policy.write_text("1.0.0\n")
    doc, _ = grader._good()
    return estate, doc


def _run(estate: Path, doc: dict, grader: ModuleType, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    evidence = estate / "driftwood/composed/evidence.json"
    evidence.parent.mkdir(exist_ok=True)
    evidence.write_text(json.dumps(doc))
    # These checks/readers do not decide whether a declared regime feed was priced.
    # Their financial/native routes are deliberately outside this document regression.
    for name in ("check_appetite", "check_curve_agreement", "check_residual_basis", "check_engine_agreement",
                 "check_fx_bridge", "check_ordinal_and_aggregate", "check_agent_cage"):
        monkeypatch.setattr(grader, name, lambda *args: None)
    _, ctx = grader._good()
    monkeypatch.setattr(grader, "_agent_register", lambda *args: ctx["agent_register"])
    monkeypatch.setattr(grader, "_agent_reach", lambda *args: ctx["agent_reach"])
    monkeypatch.setattr(grader, "_gate_window", lambda: ctx["gate_window"])
    grader.LINES.clear()
    grader.run(str(estate))
    return list(grader.LINES)


def _without_feed(doc: dict) -> None:
    doc["prices"] = [e for e in doc["prices"] if not (e.get("source") == "ico" and e.get("kind") == "feed")]


@pytest.mark.parametrize("feed_available", [True, False])
def test_declared_feed_cannot_disappear_even_without_weights(tmp_path, grader, monkeypatch, capsys, feed_available):
    estate, doc = _estate(tmp_path, grader, feed_available=feed_available)
    _without_feed(doc)
    assert "FAIL" in _run(estate, doc, grader, monkeypatch)
    output = capsys.readouterr().out
    assert "penalty-schema" in output and "named absence" not in output


@pytest.mark.parametrize("derivatives", [("switching",), ("supersede",), ("switching", "supersede")])
def test_derivatives_cannot_substitute_for_declared_feed(tmp_path, grader, monkeypatch, derivatives):
    estate, doc = _estate(tmp_path, grader)
    _without_feed(doc)
    for kind in derivatives:
        doc["prices"].append(grader._switching("ico", 300.0) if kind == "switching" else grader._supersede("ico", 0.0))
    assert "FAIL" in _run(estate, doc, grader, monkeypatch)


def test_no_subscription_is_still_a_named_absence(tmp_path, grader, monkeypatch, capsys):
    estate, doc = _estate(tmp_path, grader, declared=False)
    _without_feed(doc)
    lines = _run(estate, doc, grader, monkeypatch)
    assert "FAIL" not in lines and "SKIP" not in lines
    assert "declares no ico regime edge" in capsys.readouterr().out


def test_present_feed_keeps_existing_hole_arithmetic(tmp_path, grader, monkeypatch, capsys):
    estate, doc = _estate(tmp_path, grader)
    before = json.dumps(doc, sort_keys=True)
    lines = _run(estate, doc, grader, monkeypatch)
    assert "FAIL" not in lines and "SKIP" not in lines
    assert "2 priced hole(s) sum to its total 300.00 GBP" in capsys.readouterr().out
    assert json.dumps(doc, sort_keys=True) == before


@pytest.mark.parametrize("damage", ["wrong-name", "duplicate"])
def test_declared_feed_requires_its_own_single_price(tmp_path, grader, monkeypatch, damage):
    estate, doc = _estate(tmp_path, grader)
    if damage == "wrong-name":
        doc["prices"][0]["name"] = "other-regime"
    else:
        doc["prices"].append(dict(doc["prices"][0]))
    assert "FAIL" in _run(estate, doc, grader, monkeypatch)


def test_explicit_could_not_look_remains_a_skip(tmp_path, grader, monkeypatch, capsys):
    estate, doc = _estate(tmp_path, grader)
    doc["prices"][0].update(amount=None, per_customer=None, could_not_look="missing instrument: ICO feed unavailable")
    lines = _run(estate, doc, grader, monkeypatch)
    assert lines.count("SKIP") == 1 and "FAIL" not in lines
    assert "could not be priced, and says why: missing instrument: ICO feed unavailable" in capsys.readouterr().out


@pytest.mark.parametrize("unknown", ["missing", None, {}, "unreadable", [None],
                                      [{"party": "ico", "kind": "feed"}]])
def test_unknown_declaration_context_cannot_claim_absence(grader, capsys, unknown):
    doc, ctx = grader._good()
    _without_feed(doc)
    if unknown == "missing":
        ctx.pop("inherits", None)
    else:
        ctx["inherits"] = unknown
    grader.LINES.clear()
    grader.check_doc(doc, ctx)
    assert "FAIL" in grader.LINES
    assert "named absence" not in capsys.readouterr().out


def test_unreadable_party_does_not_become_no_subscription(tmp_path, grader, monkeypatch, capsys):
    estate, doc = _estate(tmp_path, grader)
    _without_feed(doc)
    (estate / "driftwood/party.yaml").write_text("inherits: [unclosed")
    with pytest.raises(yaml.YAMLError):
        _run(estate, doc, grader, monkeypatch)
    assert "named absence" not in capsys.readouterr().out


@pytest.mark.parametrize("inherits", [
    "MISSING_REQUIRED_INHERITS",
    [{}],
    [{"party": "ico", "version": "v3", "name": "penalty-schema"}],
    [{"kind": "feed", "version": "v3", "name": "penalty-schema"}],
    [{"party": 7, "kind": "controls", "version": "v1"}],
    [{"party": "", "kind": "controls", "version": "v1"}],
    [{"party": "ico", "kind": "Feed", "version": "v3", "name": "penalty-schema"}],
    [{"party": "nist", "kind": "controls"}],
    [{"party": "nist", "kind": "controls", "version": None}],
    [{"party": "nist", "kind": "controls", "version": 3}],
    [{"party": "nist", "kind": "controls", "version": ""}],
    [{"party": "feeds", "kind": "feed", "version": "v1"}],
])
def test_malformed_parent_pins_cannot_establish_absence_through_run(tmp_path, grader, monkeypatch, capsys, inherits):
    estate, doc = _estate(tmp_path, grader, declared=False)
    _without_feed(doc)
    party_path = estate / "driftwood/party.yaml"
    party = json.loads(party_path.read_text())
    if inherits == "MISSING_REQUIRED_INHERITS":
        party.pop("inherits")
    else:
        party["inherits"] = inherits
    party_path.write_text(json.dumps(party))
    assert "FAIL" in _run(estate, doc, grader, monkeypatch)
    assert "named absence" not in capsys.readouterr().out


def test_valid_other_parent_pins_do_not_require_an_ico_price(tmp_path, grader, monkeypatch, capsys):
    estate, doc = _estate(tmp_path, grader, declared=False)
    _without_feed(doc)
    party_path = estate / "driftwood/party.yaml"
    party = json.loads(party_path.read_text())
    party["inherits"] = [{"party": "nist", "kind": "controls", "version": "v1"},
                         {"party": "feeds", "kind": "feed", "name": "threat-register", "version": "v4"}]
    party_path.write_text(json.dumps(party))
    lines = _run(estate, doc, grader, monkeypatch)
    assert "FAIL" not in lines and "SKIP" not in lines
    assert "declares no ico regime edge" in capsys.readouterr().out
