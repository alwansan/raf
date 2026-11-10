#!/usr/bin/env python3
"""GFX-MULTI-014: numeric original DXBC RDEF source resource census vs SPIR-V.

No raw proprietary DXBC/SPIR-V/GLSL, keywords, bindings, names, coordinates,
source pointers, shader programs or images are exported. Register vs SPIR-V
descriptor semantic mapping remains unverified until explicitly checked.
"""
import argparse,json,struct,tempfile
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_gles_stage_io import resource_counters,run_quiet

def rdef_summary(dx):
    if not isinstance(dx,bytes) or len(dx)<36 or dx[:4]!=b"DXBC":
        raise ValueError("BAD_AUTHENTIC_DXBC_CONTAINER")
    total=struct.unpack_from("<I",dx,24)[0]
    n=struct.unpack_from("<I",dx,28)[0]
    if total!=len(dx) or not 1<=n<=64 or 32+4*n>len(dx):
        raise ValueError("BAD_AUTHENTIC_DXBC_HEADER")
    sections=[]
    for i in range(n):
        off=struct.unpack_from("<I",dx,32+4*i)[0]
        if off+8>len(dx):raise ValueError("DXBC_CHUNK_OUTSIDE_CONTAINER")
        size=struct.unpack_from("<I",dx,off+4)[0]
        if off+8+size>len(dx):raise ValueError("DXBC_CHUNK_TRUNCATED")
        if dx[off:off+4]==b"RDEF":
            data=dx[off+8:off+8+size]
            if len(data)<16:raise ValueError("RDEF_TRUNCATED_HEADER")
            cb_count,cb_off,binding_count,binding_off=struct.unpack_from("<4I",data,0)
            if cb_count>4096 or binding_count>4096:
                raise ValueError("RDEF_RESOURCE_COUNT_UNREASONABLE")
            if cb_count and cb_off+cb_count*24>len(data):
                raise ValueError("RDEF_CB_TABLE_TRUNCATED")
            if binding_count and binding_off+binding_count*32>len(data):
                raise ValueError("RDEF_BINDING_TABLE_TRUNCATED")
            sections.append({"constant_buffers":cb_count,
                "resource_binding_descriptors":binding_count,
                "rdef_structures_bounds_checked":True})
    if len(sections)>1:raise ValueError("AMBIGUOUS_MULTIPLE_RDEF_CHUNKS")
    return sections[0] if sections else dict(
        constant_buffers=0,resource_binding_descriptors=0,
        rdef_structures_bounds_checked=False,rdef_missing_in_source=True)

def audit(stage):
    programs,pass_rows=source_pair(stage)
    if len(pass_rows)!=7 or not pass_rows[0]["pairs"]:
        raise ValueError("SOURCE_PASS_VARIANT_DRIFT")
    source_vertex,source_fragment=pass_rows[0]["pairs"][0]
    vs=code_from_ref(source_vertex,programs,"Vertex")
    fs=code_from_ref(source_fragment,programs,"Pixel")
    info={"vertex":rdef_summary(vs),"fragment":rdef_summary(fs)}
    with tempfile.TemporaryDirectory(prefix="gfxlab-private-rdef-") as root:
        t=Path(root);translated=translate_pair(vs,fs,t)
        reflection={}
        for stage in ("vertex","fragment"):
            if not translated[stage]["vulkan11_spirv_validation_success"]:
                raise ValueError("SOURCE_TRANSLATION_PILOT_REGRESSED")
            ok,bytes_=run_quiet(["spirv-cross",str(t/(stage+".spv")),"--reflect"])
            if not ok:raise ValueError("SPIRV_REFLECTION_FAILED")
            try:reflection[stage]=json.loads(bytes_.decode("utf-8"))
            except (ValueError,UnicodeDecodeError):raise ValueError("REFLECTION_JSON_MALFORMED") from None
        results={stage:resource_counters(reflection[stage]) for stage in ("vertex","fragment")}
    return dict(experiment="GFX-MULTI-014",source_sha=ZIP2_SHA,
        original_source_mesh_material_shader_graph_verified=True,
        original_dxbc_vulkan11_pair_validated=True,
        original_dxbc_rdef=info,
        translated_spirv_resource_counts=results,
        source_texture_material_bound_count_for_M00=3,
        actual_original_cb_register_offsets_mapped_to_spirv=False,
        original_shader_to_material_binding_equivalence=False,
        original_normal_dxt5nm_and_tangent_parity_verified=False,
        actual_glsl_sampler_binding_verified=False,
        original_unity_android_shader_restored=False,
        private_gpu_program_bytes_exported=False,
        phase_closed=False)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--stage",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();d=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI014_SAFE_DXBC_RDEF_RESOURCE_SHAPE "+json.dumps(d,sort_keys=True))
if __name__=="__main__":main()
