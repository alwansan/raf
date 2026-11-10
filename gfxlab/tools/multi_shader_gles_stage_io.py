#!/usr/bin/env python3
"""GFX-MULTI-012: one source-exact shader pair SPIR-V -> GLSL ES and stage IO check.

All proprietary binary, GLSL/HLSL text and reflection names stay in private
temporary files. Only numerical summary and booleans are emitted. This is
not a Unity shader or a successful phone GPU test.
"""
from __future__ import annotations
import argparse,json,subprocess,tempfile
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair

def run_quiet(args):
    try:
        r=subprocess.run(args,capture_output=True,timeout=90)
        return r.returncode==0,r.stdout
    except (OSError,subprocess.TimeoutExpired):return False,b""

def public_interfaces(vertex_doc,fragment_doc):
    def mapping(doc,key):
        rows=doc.get(key,[])
        if not isinstance(rows,list):raise ValueError("REFLECTION_VARIABLES_NOT_ARRAY")
        out={};dups=0;ignored=0
        for row in rows:
            if not isinstance(row,dict):raise ValueError("MALFORMED_REFLECTED_VARIABLE")
            loc=row.get("location")
            if type(loc)!=int:
                ignored+=1
                continue
            slot=(loc,row.get("component",0))
            if slot in out:dups+=1
            else:out[slot]=str(row.get("type","unknown"))
        return out,dups,ignored
    vs,vd,vi=mapping(vertex_doc,"outputs")
    fs,fd,fi=mapping(fragment_doc,"inputs")
    common=set(vs)&set(fs)
    type_equal=sum(vs[k]==fs[k] for k in common)
    type_diff=len(common)-type_equal
    missing=set(fs)-set(vs)
    vs_extra=set(vs)-set(fs)
    return dict(vertex_output_slots=len(vs),fragment_input_slots=len(fs),
        matched_locations=len(common),matched_locations_and_types=type_equal,
        different_type_same_location=type_diff,fragment_input_missing_vertex_output=len(missing),
        vertex_output_unused_by_fragment=len(vs_extra),
        duplicate_location_slots=vd+fd,reflection_builtin_or_nonlocation=vi+fi,
        location_type_parity=(len(missing)==0 and type_diff==0 and vd+fd==0),
        semantics_and_interpolation_verified=False)

def resource_counters(doc):
    allow=("ubos","ssbos","textures","separate_images","separate_samplers",
           "images","push_constants","inputs","outputs","subpass_inputs")
    return {k:len(doc[k]) if isinstance(doc.get(k),list) else 0 for k in allow}

def audit(stage):
    programs,perpass=source_pair(stage)
    exact=perpass[0]["pairs"]
    if not exact:raise ValueError("PASS_ZERO_NO_EXACT_SOURCE_PAIR")
    vmeta,fmeta=exact[0]
    vs=code_from_ref(vmeta,programs,"Vertex")
    fs=code_from_ref(fmeta,programs,"Pixel")
    with tempfile.TemporaryDirectory(prefix="gfxlab-private-gles-stage-") as td:
        folder=Path(td)
        translated=translate_pair(vs,fs,folder)
        if not all(translated[x]["vulkan11_spirv_validation_success"] for x in ("vertex","fragment")):
            raise ValueError("PREVIOUS_SPIRV_PAIR_VALIDATION_REGRESSED")
        reflection={}
        es_status={}
        for stage,glslang in (("vertex","vert"),("fragment","frag")):
            spv=folder/(stage+".spv")
            success,output=run_quiet(["spirv-cross",str(spv),"--reflect"])
            if not success:raise ValueError("PRIVATE_SPIRV_REFLECTION_FAILED")
            try:reflection[stage]=json.loads(output.decode("utf-8"))
            except (ValueError,UnicodeDecodeError):raise ValueError("MALFORMED_PRIVATE_SPIRV_REFLECTION") from None
            target=folder/(stage+".glsl")
            success,_=run_quiet(["spirv-cross",str(spv),"--version","310","--es","--output",str(target)])
            syntax=success and target.is_file() and target.stat().st_size>10 and run_quiet(
                ["glslangValidator","-S",glslang,str(target)])[0]
            es_status[stage]={"spirv_cross_glsl_es_310_emitted":success,
                "glslang_offline_es_syntax_compiled":bool(syntax),
                "unity_android_gles_runtime_compiled":False}
        iface=public_interfaces(reflection["vertex"],reflection["fragment"])
        resources={stage:resource_counters(reflection[stage]) for stage in ("vertex","fragment")}
    return {"experiment":"GFX-MULTI-012","source_sha":ZIP2_SHA,
      "original_pair_select":"same_pass_same_keywords_and_hardware_bucket",
      "source_original_dxbc_verified":True,
      "vulkan11_spirv_both_stages_validated":True,
      "gles310_offline_translation":es_status,
      "spirv_stage_interface":iface,"spirv_resource_declarations":resources,
      "all_7_passes_restored":False,"original_shaderlab_restored":False,
      "original_shader_on_adreno_verified":False,"pc_pixel_equivalence":False,
      "original_shaders_exported_to_git":False,"phase_closed":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--stage",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    d=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI012_SAFE_GLES_STAGE_IO "+json.dumps(d,sort_keys=True))
if __name__=="__main__":main()
