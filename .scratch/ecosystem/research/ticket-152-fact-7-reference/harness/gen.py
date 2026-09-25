import json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
IMAGE = "ghcr.io/acme/coraza-waf:cage"   # CAGE_PROBE_IMAGE, drift-sample.yml
POD = "cage-probe"
# candidate -> (namespace name, extra ns labels, claim or None)
C = {
 "F":   ("cage-probe-fallclosed", {"policy-as-versioned.dev/governed": "true"}, "5.0.0"),
 "OLD": ("cage-probe-control",    {}, "5.0.0"),
 "RA":  ("cage-probe-fallclosed", {"policy-as-versioned.dev/governed": "true", "posture.acme.io/tier": "baseline"}, "5.0.0"),
 "RB":  ("cage-probe-control",    {}, None),
 "RC":  ("cage-probe-control",    {"posture.acme.io/tier": "baseline"}, "5.0.0"),
}
for k, (ns, extra, claim) in C.items():
    d = os.path.join(H, k); os.makedirs(d, exist_ok=True)
    labels = {"app.kubernetes.io/managed-by": "drift-five-facts"}; labels.update(extra)
    nsobj = {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": ns, "labels": labels}}
    podlabels = {"policy-as-versioned.dev/policy-version": claim} if claim else {}
    pod = {"apiVersion": "v1", "kind": "Pod",
           "metadata": {"name": POD, "namespace": ns, "labels": podlabels},
           "spec": {"securityContext": {"runAsNonRoot": True, "runAsUser": 65532},
                    "containers": [{"name": "app", "image": IMAGE, "imagePullPolicy": "IfNotPresent",
                                    "securityContext": {"readOnlyRootFilesystem": True}}]}}
    json.dump(pod, open(os.path.join(d, "pod.json"), "w"), indent=1)
    values = {"apiVersion": "cli.kyverno.io/v1alpha1", "kind": "Value", "metadata": {"name": "values"},
              "namespaces": [nsobj],
              "namespaceSelector": [{"name": ns, "labels": labels}]}
    json.dump(values, open(os.path.join(d, "values.json"), "w"), indent=1)
print("ok")
# sanity controls (harness only, not candidates)
d = os.path.join(H, "SANE-govnoclaim"); os.makedirs(d, exist_ok=True)
labels = {"app.kubernetes.io/managed-by": "drift-five-facts", "policy-as-versioned.dev/governed": "true"}
ns = "cage-probe-fallclosed"
pod = {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": POD, "namespace": ns, "labels": {}},
       "spec": {"securityContext": {"runAsNonRoot": True, "runAsUser": 65532},
                "containers": [{"name": "app", "image": IMAGE, "imagePullPolicy": "IfNotPresent",
                                "securityContext": {"readOnlyRootFilesystem": True}}]}}
json.dump(pod, open(os.path.join(d, "pod.json"), "w"), indent=1)
json.dump({"apiVersion": "cli.kyverno.io/v1alpha1", "kind": "Value", "metadata": {"name": "values"},
           "namespaces": [{"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": ns, "labels": labels}}],
           "namespaceSelector": [{"name": ns, "labels": labels}]},
          open(os.path.join(d, "values.json"), "w"), indent=1)
d = os.path.join(H, "SANE-RA-nonsobj"); os.makedirs(d, exist_ok=True)
ra = json.load(open(os.path.join(H, "RA", "values.json")))
del ra["namespaces"]
json.dump(ra, open(os.path.join(d, "values.json"), "w"), indent=1)
import shutil; shutil.copy(os.path.join(H, "RA", "pod.json"), os.path.join(d, "pod.json"))
