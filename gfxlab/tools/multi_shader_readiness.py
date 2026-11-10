#!/usr/bin/env python3
"""GFX-MULTI-005: inspect real Shader48 typed metadata without publishing source."""
import argparse,json
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries

def shader_summary(tree):
    form=tree.get("m_ParsedForm") if isinstance(tree,dict) else None
    if not isinstance(form,dict):raise ValueError("MISSING_TYPED_SHADER")
    subs=form.get("m_SubShaders")
    if not isinstance(subs,list) or not subs:raise ValueError("MISSING_SUBSHADERS")
    per=[];state=mask=vert=frag=0
    for sub in subs:
        passes=sub.get("m_Passes") if isinstance(sub,dict) else None
        if not isinstance(passes,list):raise ValueError("MALFORMED_PASSES")
        per.append(len(passes))
        for p in passes:
            if not isinstance(p,dict):raise ValueError("MALFORMED_PASS")
            state+=isinstance(p.get("m_State"),dict)
            mask+=p.get("m_ProgramMask") is not None
            vert+=any(bool(p.get(k)) for k in ("progVertex","m_ProgVertex","m_VertexProgram"))
            frag+=any(bool(p.get(k)) for k in ("progFragment","m_ProgFragment","m_FragmentProgram"))
    if not sum(per):raise ValueError("ZERO_PASSES")
    return dict(subshaders=len(subs),passes=sum(per),per_subshader=per,
        state_metadata_passes=state,program_mask_passes=mask,
        vertex_metadata_passes=vert,fragment_metadata_passes=frag,
        original_android_compiled_program_verified=False,
        pass_render_state_equivalence_verified=False,
        original_shader_variant_cb_sampler_parity_verified=False)
def audit(stage):
    entries,types,_=all_model_entries(stage);unique={};rows=[];slots=0
    if [e["id"] for e in entries]!=["M00","M01","M02","M03","M04","M05"]:
        raise ValueError("MODEL_SELECTION_DRIFT")
    for e in entries:
        mats=e["materials"];slots+=len(mats)
        for m in mats:
            key=(m["shader_owner"],m["shader_pid"])
            obj=types[key[0]].get(key[1])
            if obj is None or obj.type.name!="Shader":raise ValueError("NON_TYPED_SHADER")
            if key not in unique:unique[key]=shader_summary(obj.read_typetree(check_read=False))
        rows.append(dict(model=e["id"],material_slots=len(mats),original_shader_runtime_verified=False))
    if slots!=7 or len(unique)!=1:raise ValueError("SHADER_IDENTITY_DRIFT")
    shader=next(iter(unique.values()))
    if (shader["subshaders"],shader["passes"])!=(2,7):
        raise ValueError("SOURCE_PASS_TOPOLOGY_DRIFT")
    return dict(experiment="GFX-MULTI-005",source_sha=ZIP2_SHA,models=rows,
        source_model_count=6,source_material_slots=7,distinct_source_shader48=1,
        original_shader_metadata=shader,original_shader_restored=False,
        android_original_shader_pixels_verified=False,original_rig_restored=False,
        ready_to_close=False)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();result=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI005_SOURCE_METADATA_ONLY "+json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
