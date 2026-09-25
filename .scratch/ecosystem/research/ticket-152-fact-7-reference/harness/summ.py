import sys, yaml, json, os
H = os.path.dirname(os.path.abspath(__file__))
def sel(np, pod):
    ml = ((np.get("spec") or {}).get("podSelector") or {}).get("matchLabels") or {}
    pl = pod["metadata"].get("labels") or {}
    return np["metadata"].get("namespace") == pod["metadata"]["namespace"] and all(pl.get(k) == v for k, v in ml.items())
for A in sys.argv[1:]:
  for C in ["F","OLD","RA","RB","RC","SANE-govnoclaim","SANE-RA-nonsobj"]:
    o = f"{H}/out/{A}-{C}"
    pod = json.load(open(o + "/final-pod.json"))
    L = pod["metadata"].get("labels") or {}; S = pod["spec"]
    ctrs = [(c["name"], (c.get("resources") or {}).get("limits"), c.get("securityContext")) for c in S["containers"]]
    nps = []
    if os.path.exists(o + "/gen.yaml"):
        nps = [d for d in yaml.safe_load_all(open(o + "/gen.yaml")) if d and d.get("kind") == "NetworkPolicy"]
    uniq = {}
    for n in nps: uniq[(n["metadata"]["namespace"], n["metadata"]["name"])] = n
    print(f"== {A} {C}: tier={L.get('posture.acme.io/tier')} caged={L.get('posture.acme.io/caged')} version={L.get('posture.acme.io/version')} pc={S.get('priorityClassName')} prio={S.get('priority')} preempt={S.get('preemptionPolicy')} hostNet={S.get('hostNetwork')}")
    for c in ctrs: print("   ctr", c[0], json.dumps(c[1]), json.dumps(c[2], sort_keys=True))
    print(f"   gen.yaml docs={len(nps)} unique NPs={len(uniq)}")
    for (ns, nm), n in sorted(uniq.items()):
        sp = n["spec"]
        print(f"   NP {ns}/{nm} podSelector={json.dumps(sp.get('podSelector'))} types={sp.get('policyTypes')} ingress={json.dumps(sp.get('ingress'))} egress={json.dumps(sp.get('egress'))} SELECTS_POD={sel(n, pod)}")
