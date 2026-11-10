#!/usr/bin/env python3
"""GFX-MULTI-013: source-authentic 7/7 Shader48 passes, one variant pair each.

DXBC, HLSL, SPIRV, GLSL, and reflection names remain ephemeral inside runner.
Only aggregate booleans and numeric resource counts are reported, no original
Shaders/Textures are published. Offline syntax is not Android GPU validation.
"""
import argparse,json,tempfile
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_gles_stage_io import public_interfaces,resource_counters,run_quiet

def one_pass(variants,programs,directory):
    report={"source_exact_variant_pairs":len(variants),
            "pair_rejected_before_translation":0,
            "original_dxbc_pair_extract_verified":False,
            "vertex_spirv_vulkan11_valid":False,
            "fragment_spirv_vulkan11_valid":False,
            "vertex_glsl_es310_offline_compiled":False,
            "fragment_glsl_es310_offline_compiled":False,
            "vertex_fragment_location_type_parity":False,
            "source_vs_fragment_resource_binding_equivalence_verified":False}
    for vmeta,fmeta in variants[:12]:
        try:
            vs=code_from_ref(vmeta,programs,"Vertex")
            fs=code_from_ref(fmeta,programs,"Pixel")
        except ValueError:
            report["pair_rejected_before_translation"]+=1
            continue
        report["original_dxbc_pair_extract_verified"]=True
        translated=translate_pair(vs,fs,directory)
        for stage in ("vertex","fragment"):
            report[stage+"_spirv_vulkan11_valid"]=bool(
                translated[stage]["vulkan11_spirv_validation_success"])
        if not all(report[k+"_spirv_vulkan11_valid"] for k in ("vertex","fragment")):
            return report
        reflection={}
        for stage,glslang in (("vertex","vert"),("fragment","frag")):
            spv=directory/(stage+".spv")
            ok,payload=run_quiet(["spirv-cross",str(spv),"--reflect"])
            if not ok: return report
            try:reflection[stage]=json.loads(payload.decode("utf8"))
            except (ValueError,UnicodeDecodeError):return report
            glsl=directory/(stage+".glsl")
            ok,_=run_quiet(["spirv-cross",str(spv),"--version","310","--es","--output",str(glsl)])
            if ok and glsl.exists() and glsl.stat().st_size>10:
                syntax,_=run_quiet(["glslangValidator","-S",glslang,str(glsl)])
                report[stage+"_glsl_es310_offline_compiled"]=bool(syntax)
        iface=public_interfaces(reflection["vertex"],reflection["fragment"])
        report["vertex_fragment_location_type_parity"]=iface["location_type_parity"]
        report["vs_output_slots"]=iface["vertex_output_slots"]
        report["fs_input_slots"]=iface["fragment_input_slots"]
        report["interface_missing"]=iface["fragment_input_missing_vertex_output"]
        report["interface_type_mismatch"]=iface["different_type_same_location"]
        report["resource_counts"]={
          k:resource_counters(reflection[k]) for k in ("vertex","fragment")}
        return report
    return report

def all_seven_complete(rows):
    if len(rows)!=7:return False
    tests=("original_dxbc_pair_extract_verified","vertex_spirv_vulkan11_valid",
        "fragment_spirv_vulkan11_valid","vertex_glsl_es310_offline_compiled",
        "fragment_glsl_es310_offline_compiled","vertex_fragment_location_type_parity")
    return all(all(row.get(key) is True for key in tests) for row in rows)

def audit(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=7:raise ValueError("ORIGINAL_7_PASS_STRUCTURE_DRIFT")
    rows=[]
    for pass_data in passes:
        with tempfile.TemporaryDirectory(prefix="gfxlab-original-pass-") as t:
            info=one_pass(pass_data["pairs"],programs,Path(t))
        info.update(subshader_ordinal=pass_data["subshader"],pass_ordinal=pass_data["pass"])
        rows.append(info)
    return dict(experiment="GFX-MULTI-013",source_sha=ZIP2_SHA,
        original_source_shader48_verified=True,
        source_subshaders=2,source_passes=len(rows),
        all_seven_source_passes_spirv_and_gles_es_offline_valid=all_seven_complete(rows),
        pass_results=rows,compiled_android_gles3_device=False,
        exact_original_sampler_cb_keyword_bindings_verified=False,
        full_524_variants_translated=False,original_shader_restored=False,
        original_shader_bytes_published=False,stage_closed=False)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI013_SOURCE_7PASS_OFFLINE_PARITY "+json.dumps(r,sort_keys=True))
if __name__=="__main__":main()
