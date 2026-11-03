"""SHA-pinned original WindWaves precision capability policy model (CPU only)."""
import argparse, hashlib, itertools, json
from pathlib import Path
PIN="fd145a6bc3344a0089e608d365df534bb3e4ad0b499d372c963d302620644f2f"
def inspect(path):
    raw=Path(path).read_text(encoding="utf-8-sig").replace("\r\n","\n")
    if hashlib.sha256(raw.encode()).hexdigest()!=PIN:
        raise ValueError("Unknown original WindWaves source")
    rows=[]
    for requested,quality,rg,argb in itertools.product((False,True),repeat=4):
        rejected=requested and (not rg or not argb)
        final=requested and quality and argb
        rows.append({"requested_high":requested,"quality_allows_high":quality,
          "supports_rgfloat":rg,"supports_argbfloat":argb,
          "initial_high_precision_rejected":rejected,
          "resolver_high_precision":final,
          "resolver_reenables_without_rgfloat":bool(rejected and final)})
    mismatches=[r for r in rows if r["resolver_reenables_without_rgfloat"]]
    assert len(rows)==16 and len(mismatches)==1
    return {"source_sha256":PIN,"policy_cases":16,"mismatches":mismatches,
      "known_phone_capability_failure":False,"original_csharp_executed":False,
      "hypothesis":"Initial RGFloat rejection can be overwritten by resolver which checks ARGBFloat only",
      "automatic_fallback_behavior_or_gpu_execution_verified":False}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    print(json.dumps(inspect(p.parse_args().source),sort_keys=True))
