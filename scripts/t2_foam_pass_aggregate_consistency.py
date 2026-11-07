"""Validate original Foam two-pass Blit aggregate consistency, without leaking IL."""
import json
import sys
from scripts.t2_foam_shaderfind_return_report import validate as validate_original
P = "field_api_Graphics_Blit_"
S = ("Texture", "RenderTexture", "unknown")
D = ("RenderTexture", "null", "unknown")
def check_counts(r):
    def n(k):
        v = r[P+k]
        if type(v) is not int or v < 0: raise ValueError("bad_count")
        return v
    if (n("explicit_sites_pass_literal0"),n("explicit_sites_pass_literal1")) != (1,1):
        raise ValueError("pass_identity_drift")
    if any(n("explicit_sites_pass_"+v) for v in ("other_literal","unknown","mixed")):
        raise ValueError("ambiguous_pass")
    result = {"classification_only": True}
    for label,variants in (("source",S),("destination",D)):
        totals=[n("explicit_"+label+"_"+v) for v in variants]
        a=[n("pass0_"+label+"_"+v) for v in variants]
        b=[n("pass1_"+label+"_"+v) for v in variants]
        if sum(totals)!=2 or sum(a)!=1 or sum(b)!=1 or any(t!=x+y for t,x,y in zip(totals,a,b)):
            raise ValueError("aggregate_partition_mismatch")
        for idx,arr in enumerate((a,b)):
            result.setdefault("pass"+str(idx),{})[label]=variants[arr.index(1)]
    return result
def unique(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise ValueError("duplicate_json_key")
        out[k]=v
    return out
def main():
    if len(sys.argv)!=2: raise SystemExit("usage: python -m scripts.t2_foam_pass_aggregate_consistency report.json")
    with open(sys.argv[1],encoding="utf-8") as f: report=json.load(f,object_pairs_hook=unique)
    validate_original(report)
    print(json.dumps(check_counts(report),sort_keys=True))
if __name__=="__main__": main()
