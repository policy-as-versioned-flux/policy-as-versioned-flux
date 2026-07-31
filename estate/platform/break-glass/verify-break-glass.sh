#!/usr/bin/env bash
# Assert the posture-gated human-access (break-glass) beat holds. OFFLINE only —
# this is pure decision logic (no cluster resources of its own; it rides on the
# access plane, ticket 18). Two layers:
#   1. the decision engine's asserts pass (the exact talk behaviours);
#   2. structural invariants: the engine reuses the estate's £ + factor engines
#      (no second risk model), the bands are ordered, and every scenario lands in
#      the tier its note claims — so the proportionality is real, not narrated.
# Exits non-zero if any invariant the talk relies on is broken.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== offline: decision-engine asserts =="
python3 "$HERE/break-glass.py" selfcheck

echo "== offline: structural invariants =="
python3 - "$HERE" <<'PY'
import json, os, sys
here = sys.argv[1]
sys.path.insert(0, here)
import importlib.util
spec = importlib.util.spec_from_file_location("bg", os.path.join(here, "break-glass.py"))
bg = importlib.util.module_from_spec(spec); spec.loader.exec_module(bg)

fails = []
def check(cond, msg):
    if not cond: fails.append(msg)
    print(("  ok   " if cond else "  FAIL ") + msg)

# The engine reuses the estate's two load-bearing modules — not a parallel model.
import fair, access
check(bg.fair is fair, "reuses ../fair/fair.py for the £ (no second risk engine)")
check(bg.CAGE not in (access.DENY, access.STEP_UP, access.ALLOW)
      and bg.DENY == access.DENY and bg.ALLOW == access.ALLOW,
      "reuses access.py's decision vocabulary, adds only the CAGE rung")

bands = bg.load_bands()
check(bands["step_up_at"] < bands["attest_at"] < bands["no_cage_at"],
      "assurance bands strictly ordered (step_up < attest < no_cage)")

# Every scenario lands in the tier + decision family its note advertises.
sc = lambda n: fair.load(os.path.join(here, "scenarios", n))
read, write = sc("driftwood-read.json"), sc("tuppence-write.json")
export, patient = sc("driftwood-bulk-export.json"), sc("ludlow-patient-data.json")
gbp = bg.carried_gbp
check(bg.required_tier(gbp(read), bands) == 1, "driftwood-read -> tier 1 (OIDC floor)")
check(bg.required_tier(gbp(write), bands) == 2, "tuppence-write -> tier 2 (+WebAuthn)")
check(bg.required_tier(gbp(export), bands) == 3, "driftwood-bulk-export -> tier 3 (+attested device)")
check(bg.required_tier(gbp(patient), bands) == 3, "ludlow-patient-data -> tier 3 (+attested device)")

# The two acceptance behaviours, asserted here too (belt and braces vs selfcheck).
dec = lambda s, **k: bg.decide(s, k.get("oidc", True), k.get("webauthn", False), k.get("device", "none"), bands)["decision"]
check(dec(patient, webauthn=True, device="fresh") == "ALLOW",
      "AC1: risky op ALLOWED with fresh attested device + step-up passkey")
check(dec(patient, webauthn=False, device="fresh") == "STEP_UP",
      "AC1: same op, no passkey -> STEP_UP (proportionate)")
check(dec(export, webauthn=True, device="stale") == "CAGE",
      "AC2: stale device on a tier-3 op -> dropped to read-only/scoped (CAGE)")
check(dec(patient, webauthn=True, device="stale") == "DENY",
      "AC2: stale device on patient data -> DENY (proportional to the higher £)")
check(dec(patient, webauthn=True, device="none") == "DENY",
      "AC2: unattested/unmanaged laptop -> DENY")

if fails:
    sys.exit(f"\n{len(fails)} invariant(s) broken")
print("  -- all offline invariants hold --")
PY

echo "verify-break-glass: done (offline; rides on the access plane — see ../access/verify-access.sh for the live IAP checks)"
