"""Replay restricted boolean expressions extracted from SHA-pinned WindWaves."""
import argparse, ast, hashlib, itertools, json, re
from pathlib import Path
PIN="fd145a6bc3344a0089e608d365df534bb3e4ad0b499d372c963d302620644f2f"
def evaluate(expression, values):
    replacements={"_Data.HighPrecision":"requested",
      "quality.AllowHighPrecisionTextures":"quality",
      "SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.RGFloat)":"rg",
      "SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBFloat)":"argb"}
    for a,b in replacements.items(): expression=expression.replace(a,b)
    expression=expression.replace("&&"," and ").replace("||"," or ").replace("!"," not ")
    node=ast.parse(expression.strip(),mode="eval").body
    def walk(n):
        if isinstance(n,ast.Name) and n.id in values: return values[n.id]
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.Not): return not walk(n.operand)
        if isinstance(n,ast.BoolOp) and isinstance(n.op,(ast.And,ast.Or)):
            result=[walk(v) for v in n.values]
            return all(result) if isinstance(n.op,ast.And) else any(result)
        raise ValueError("Unsupported source expression")
    return walk(node)
def inspect(path):
    raw=Path(path).read_text(encoding="utf-8-sig").replace("\r\n","\n")
    if hashlib.sha256(raw.encode()).hexdigest()!=PIN: raise ValueError("Unknown original WindWaves source")
    final=re.findall(r"bool flag2 = ([^;]+);",raw)
    initial=re.findall(r"if \((_Data.HighPrecision && .*?)\)\s*\{\s*_FinalHighPrecision = false;",raw)
    if len(final)!=1 or len(initial)!=1: raise ValueError("Ambiguous source conditions")
    mismatches=[]
    for bits in itertools.product((False,True),repeat=4):
        v=dict(zip(("requested","quality","rg","argb"),bits))
        if evaluate(initial[0],v) and evaluate(final[0],v): mismatches.append(v)
    if len(mismatches)!=1: raise ValueError("Unexpected capability policy")
    return {"source_sha256":PIN,"policy_cases":16,"mismatches":mismatches,
      "conditions_extracted_from_original_source":True,
      "original_csharp_or_gpu_executed":False,"actual_unity_fallback_verified":False}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    print(json.dumps(inspect(p.parse_args().source),sort_keys=True))
