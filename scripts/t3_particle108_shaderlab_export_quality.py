#!/usr/bin/env python3
"""T3 genuine original 108-particle Shader48 → exact AssetRipper ShaderLab quality.

Authenticates six original scenes and four SHA-pinned serialized Shader owners,
selects only the UNIQUE 108-use ParticleSystemRenderer Shader48 source identity,
then joins it by a SAME-INSTANCE W1 Shader48 trace to the exact output .shader
GUID and actual file, or a verified Unity builtin shader pointer.

Reports only allowlisted counters/flags. Source names, PathIDs, GUIDs,
exported ShaderLab/HLSL, private errors and original textures are never emitted.
One bounded AssetRipper result is NOT a phone emitter/Android pixel proof.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import t3_original_renderer_shader_impact as source
from scripts import t3_original_particle_shader_state as particle
from scripts import t3_same_export_material_texenv as sameexport
from scripts.b05_verify_material_texenv_bindings import _trace_source,_trace_export
from scripts.probe_a13_exported_material_shader_guids import GUID,BUILTIN
from scripts.b49_shaderlab_pass_contract import pass_coverage

STATUS="T3_ORIGINAL_PARTICLE108_REAL_SAMEEXPORT_SHADERLAB_CLASSIFIED"
RANKS=(108,34,34,20,16,3)
LIMIT_ITEMS=150000
LIMIT_SHADER=8_000_000


def classify(shader_key:tuple,w1:dict,b02:dict,assets:Path)->dict:
    """Pure source-owned identity join, never text-name-based identity lookup."""
    if (type(shader_key) is not tuple or len(shader_key)!=2
        or shader_key[0] not in source.SHADER_OWNERS_SELECTED
        or type(shader_key[1]) is not int or shader_key[1]<=0
        or not isinstance(assets,Path) or not assets.is_dir() or assets.is_symlink()):
        raise ValueError("untrusted_original_particle_shader48_source_identity")
    sameexport.combine_same_export(w1,b02)
    if type(w1.get("objects")) is not list:
        raise ValueError("invalid_same_instance_W1_objects")
    rows=[row for row in w1["objects"]
          if row.get("class_id")==48 and _trace_source(row)==shader_key]
    if len(rows)!=1:
        raise ValueError("one_original_particle_Shader48_export_trace_required")
    ptr=_trace_export(rows[0])
    if ptr[0]<=0:
        raise ValueError("null_original_particle_Shader48_export_pointer")
    basic={"schema_version":1,"status":STATUS,
           "original_particle_use_slots":108,"source_original_one_Pass":True,
           "same_export_instance_W1_B02_verified":True,
           "source_to_export_Shader48_trace_verified":True,
           "original_private_Shader48_name_owner_id_export_guid_not_published":True,
           "original_program_vs_output_bytecode_equivalence_proven":False,
           "native_Unity_Android_GPU_pixels_verified":False,
           "source_particle108_is_phone_square_emitter_verified":False,
           "exported_shader_builtin_reference":False,
           "exported_shader_custom_reference":False,
           "selected_shader_meta_found":False,
           "selected_shaderlab_file_present":False,
           "selected_shaderlab_dummy_exporter_marker":False,
           "selected_shaderlab_no_subprogram_marker":False,
           "selected_shaderlab_complete_program_passes":0,
           "selected_shaderlab_total_passes":0,
           "selected_shaderlab_balanced_braces":False,
           "selected_shaderlab_subshader_count":0,
           "selected_shaderlab_one_pass_per_subshader":False,
           "selected_shaderlab_all_subshaders_programmed":False,
           "selected_shaderlab_active_subshader_runtime_verified":False}
    if ptr[1] in BUILTIN:
        if ptr[2]!=0:
            raise ValueError("invalid_builtin_original_particle_Shader48_export_type")
        basic["exported_shader_builtin_reference"]=True
        basic["exported_ShaderLab_source_status"]="UNITY_BUILTIN_REFERENCE_NO_CUSTOM_SHADER_FILE"
        return basic
    if ptr[2] not in (2,3):
        raise ValueError("invalid_original_particle_custom_Shader48_export_type")
    basic["exported_shader_custom_reference"]=True
    files=list(assets.rglob("*"))
    if len(files)>LIMIT_ITEMS or any(f.is_symlink() for f in files):
        raise ValueError("unsafe_large_or_linked_original_particle_export_asset_tree")
    metas=[]
    for f in files:
        if not f.is_file() or not f.name.endswith(".shader.meta"):
            continue
        if f.stat().st_size>256000:
            raise ValueError("oversized_exported_ShaderImporter_meta")
        text=f.read_text(encoding="utf-8-sig")
        hits=GUID.findall(text)
        if len(hits)!=1:
            raise ValueError("invalid_exported_ShaderImporter_meta_guid_shape")
        if hits[0].lower()==ptr[1]:
            metas.append(f)
    if len(metas)>1:
        raise ValueError("duplicate_custom_original_particle_Shader48_export_GUID")
    if not metas:
        basic["exported_ShaderLab_source_status"]="CUSTOM_SHADER_META_MISSING"
        return basic
    basic["selected_shader_meta_found"]=True
    path=Path(str(metas[0])[:-5])
    if not path.is_file() or path.is_symlink():
        basic["exported_ShaderLab_source_status"]="CUSTOM_SHADER_TEXT_MISSING"
        return basic
    if path.stat().st_size>LIMIT_SHADER:
        raise ValueError("oversized_exact_original_particle_ShaderLab")
    code=path.read_text("utf-8-sig")
    coverage=pass_coverage(code)
    if (type(coverage) is not dict
        or type(coverage.get("pass_count")) is not int
        or type(coverage.get("passes_with_complete_program")) is not int
        or type(coverage.get("pass_braces_balanced")) is not bool
        or type(coverage.get("subshader_pass_counts")) is not list
        or type(coverage.get("subshader_programmed_pass_counts")) is not list
        or type(coverage.get("all_subshaders_programmed")) is not bool
        or coverage.get("active_subshader_runtime_verified") is not False):
        raise ValueError("untrusted_exact_source_export_ShaderLab_parser")
    count=coverage["pass_count"];good=coverage["passes_with_complete_program"]
    sub_counts=coverage["subshader_pass_counts"]
    sub_good=coverage["subshader_programmed_pass_counts"]
    if (type(count) is not int or type(good) is not int
        or count<0 or good<0 or good>count
        or len(sub_counts)!=len(sub_good) or len(sub_counts)>128
        or any(type(n) is not int or n<0 for n in sub_counts)
        or any(type(n) is not int or n<0 for n in sub_good)
        or any(complete>total for complete,total in zip(sub_good,sub_counts))
        or sum(sub_counts)!=count or sum(sub_good)!=good):
        raise ValueError("nonsensical_original_particle_ShaderLab_pass_count")
    basic["selected_shaderlab_file_present"]=True
    basic["selected_shaderlab_dummy_exporter_marker"]="//DummyShaderTextExporter" in code
    basic["selected_shaderlab_no_subprogram_marker"]="// No subprograms found" in code
    basic["selected_shaderlab_complete_program_passes"]=good
    basic["selected_shaderlab_total_passes"]=count
    basic["selected_shaderlab_balanced_braces"]=coverage["pass_braces_balanced"]
    basic["selected_shaderlab_subshader_count"]=len(sub_counts)
    basic["selected_shaderlab_one_pass_per_subshader"]=bool(sub_counts) and all(
        n==1 for n in sub_counts)
    basic["selected_shaderlab_all_subshaders_programmed"]=coverage["all_subshaders_programmed"]
    basic["selected_shaderlab_active_subshader_runtime_verified"]=False
    if basic["selected_shaderlab_dummy_exporter_marker"]:
        basic["exported_ShaderLab_source_status"]="ACTUAL_DUMMY_SHADER_TEXT_EXPORTER"
    elif basic["selected_shaderlab_no_subprogram_marker"]:
        basic["exported_ShaderLab_source_status"]="NO_PROGRAM_SUBPROGRAMS_EXPORTED"
    elif (not coverage["pass_braces_balanced"] or count==0 or good==0
          or not sub_counts):
        basic["exported_ShaderLab_source_status"]="INCOMPLETE_OR_UNPROGRAMMED_CUSTOM_SHADER"
    elif not basic["selected_shaderlab_one_pass_per_subshader"]:
        # Preserve original mismatch precedence when one SubShader truly
        # has two Passes, even if its second Pass is also unprogrammed.
        # Alternate SubShaders are fallbacks, not sequential Passes.
        basic["exported_ShaderLab_source_status"]="CUSTOM_PASS_COUNT_DIFFERS_FROM_ORIGINAL"
    elif not coverage["all_subshaders_programmed"]:
        # One Pass per alternative is structurally correct, but an
        # unprogrammed fallback cannot be accepted as a viable shader.
        basic["exported_ShaderLab_source_status"]="INCOMPLETE_OR_UNPROGRAMMED_CUSTOM_SHADER"
    else:
        basic["exported_ShaderLab_source_status"]="STRUCTURAL_ONE_PASS_PROGRAM_PRESENT_NOT_EQUIVALENCE"
    return basic


def run(original:Path,manifest:Path,project:Path,w1path:Path,b02path:Path):
    private={}
    report=source.load_original(original,manifest,
        private_particle_slot_counts=private)
    if (report.get("status")!=source.STATUS
        or report.get("six_original_scenes_sha_verified") is not True
        or report.get("original_particle_highest_Shader48_unique") is not True
        or report.get("original_particle_highest_Shader48_original_pass_count")!=1
        or report.get("original_particle_highest_Shader48_nonparticle_renderer_slots")!=0
        or tuple(report.get("original_particle_Shader48_ranked_material_slot_use_no_identity",[]))!=RANKS
        or sorted(private.values(),reverse=True)!=list(RANKS)):
        raise ValueError("untrusted_sha_original_particle108_Shader_source_graph")
    selected=[key for key,count in private.items() if count==108]
    if len(selected)!=1:
        raise ValueError("ambiguous_real_original_particle108_shader_target")
    w1=json.loads(w1path.read_text(encoding="utf-8"))
    b02=json.loads(b02path.read_text(encoding="utf-8"))
    out=classify(selected[0],w1,b02,project/"Assets")
    out["original_six_scene_SHA_verified"]=True
    out["original_four_shader_owner_SHA_verified"]=True
    return out


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for field in ("original","manifest","project","w1-trace","b02-trace","out"):
        parser.add_argument("--"+field,required=True,type=Path)
    args=parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink()
        or args.out.resolve().is_relative_to(args.original.resolve())
        or args.out.resolve().is_relative_to(args.project.resolve())):
        raise ValueError("unsafe_original_particle_shaderlab_report_destination")
    try:
        result=run(args.original,args.manifest,args.project,args.w1_trace,args.b02_trace)
    except Exception as exc:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "original_program_vs_output_bytecode_equivalence_proven":False,
                "native_Unity_Android_GPU_pixels_verified":False,
                "source_particle108_is_phone_square_emitter_verified":False,
                "original_private_Shader48_name_owner_id_export_guid_not_published":True}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("T3_ORIGINAL_PARTICLE108_SHADERLAB_OUTPUT "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
