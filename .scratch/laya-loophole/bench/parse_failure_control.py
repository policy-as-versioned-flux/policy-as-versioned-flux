import os, sys, json
sys.path.insert(0, os.environ["LOOPHOLE_SRC"])
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from loophole.agents.loophole_finder import _parse_scenarios
from loophole.models import LegalCode, SessionState
from loophole_round import parse_audit

state = SessionState(session_id="nc", domain="nc", moral_principles="nc",
                     current_code=LegalCode(version=1, text="nc"))

cases = {
 "A well-formed, 3 scenarios": "<scenario><description>d1</description><explanation>e1</explanation></scenario>"*3,
 "B truncated: tag opened, never closed": "<scenario><description>d1</description><explanation>e1</explanation></scenario>"
     "<scenario><description>d2</description><explanation>e2",
 "C wrong inner tags (weak model)": "<scenario><desc>d1</desc><why>e1</why></scenario>"*3,
 "D prose only, no tags at all": "Here are three loopholes: first, ... second, ... third, ...",
 "E markdown fence round the XML": "```xml\n<scenario><description>d1</description><explanation>e1</explanation></scenario>\n```",
}
print(f"{'input':42s} {'parsed':>6s} {'opens':>6s} {'parse_failures':>15s} {'under_production':>17s}")
for name, raw in cases.items():
    parsed = _parse_scenarios(raw, state)
    a = parse_audit(raw, len(parsed), 3)
    print(f"{name:42s} {a['cases_parsed']:6d} {a['scenario_open_tags']:6d} "
          f"{a['parse_failures']:15d} {a['under_production']:17d}")
