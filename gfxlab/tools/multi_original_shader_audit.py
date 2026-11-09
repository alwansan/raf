#!/usr/bin/env python3
"""GFX-MULTI-004: exact source Shader48 pass topology for six selected models.

No proprietary shader names, PPtrs, bytecode or render states leave runner.
A non-Dummy original Shader in ZIP2 does NOT imply Unity Android compilation,
variant fidelity or actual original Pass execution. Source-only audit.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries

def audit(source:Path):
    entries,types,_=all_model_entries(source)
    per=[]
    original_shader_ids=set()
    for model in entries:
        rows=[]
        for m in model["materials"]:
            o=types[m["shader_owner"]].get(m["shader_pid"])
            if o is None or o.type.name!="Shader":
                raise ValueError("Original shader reference not typed Class48")
            private=(m["shader_owner"],m["shader_pid"])
            original_shader_ids.add(private)
            d=o.read_typetree(check_read=False)
            parsed=d.get("m_ParsedForm")
            if not isinstance(parsed,dict):raise ValueError("Original shader parsed form absent")
            sub=parsed.get("m_SubShaders",[])
            if not isinstance(sub,list) or not sub:raise ValueError("Original shader has no SubShaders")
            passes=[]
            for s in sub:
                ps=s.get("m_Passes",[]) if isinstance(s,dict) else None
                if not isinstance(ps,list):raise ValueError("Malformed original shader pass array")
                passes.append(len(ps))
            if sum(passes)<1:raise ValueError("Original source pass count zero")
            name=d.get("m_Name",parsed.get("m_Name",""))
            family_standard=(name=="Standard")
            rows.append({"subshaders":len(sub),"passes":sum(passes),
                "source_shader_is_named_unity_standard":family_standard,
                "passes_by_subshader":passes,
                "original_type_verified":True,
                "source_real_shader_to_android_program_mapped":False,
                "source_shader_variant_parity_verified":False})
        per.append({"id":model["id"],"source_material_slots":len(rows),
            "original_shaders":rows,"all_original_shader_passes_verified":True,
            "source_to_unity_original_pass_equivalence":False})
    return {"schema":1,"source_sha":ZIP2_SHA,"source_model_count":6,
      "source_material_count":sum(len(e["materials"]) for e in entries),
      "distinct_original_shader_objects":len(original_shader_ids),
      "models":per,"all_source_shader48_types_verified":True,
      "native_Unity_shader_programs_restored":False,
      "Android_device_exact_shader_pixels_verified":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--stage",required=True,type=Path)
    p.add_argument("--safe-report",required=True,type=Path)
    a=p.parse_args()
    stage=stage_originals(a.zip2,a.stage)
    result=audit(stage)
    a.safe_report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI004_ORIGINAL_SHADER_TOPOLOGY "+json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
