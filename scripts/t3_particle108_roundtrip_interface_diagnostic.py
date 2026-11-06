#!/usr/bin/env python3
"""Private authentic Particle108 four-pair DXBC->Vulkan->HLSL->Vulkan VS/FS diagnostic.

Report ONLY allow-listed aggregate counts. SPIR-V reflections, HLSL, original
shader programs, names, IDs, PathIDs, per-pair locations and all bytecode stay
inside the ephemeral CI runner. Numeric Location is NOT original semantic ID.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile

from scripts import t3_original_particle108_spirv_translation as tr
from scripts.t3_original_921_dxbc_semantic_join import read_original_dxbc_signatures
from scripts.t3_stage_io_drift import classify_stage_io
from scripts.w1_recover_depth_passes import reflection, interfaces_match
from scripts.w1_recover_graphics_programs import translate

STATUS="T3_AUTHENTIC_PARTICLE108_HLSL_ROUNDTRIP_VSFS_MISMATCH_CLASSIFIED"
PAIRS=4
COUNTERS=(
    "original_pairs_valid",
    "roundtrip_pairs_valid",
    "original_pairs_with_missing_fragment_location",
    "roundtrip_pairs_with_missing_fragment_location",
    "roundtrip_pairs_with_same_location_type_mismatch",
    "original_fragment_missing_vertex_location_records",
    "roundtrip_fragment_missing_vertex_location_records",
    "roundtrip_fragment_same_location_type_mismatch_records",
    "source_vertex_outputs_total",
    "source_fragment_inputs_total",
    "roundtrip_vertex_outputs_total",
    "roundtrip_fragment_inputs_total",
    "roundtrip_vertex_output_removed_locations_vs_source",
    "roundtrip_vertex_output_added_locations_vs_source",
    "roundtrip_vertex_output_same_location_type_changes",
    "roundtrip_fragment_input_removed_locations_vs_source",
    "roundtrip_fragment_input_added_locations_vs_source",
    "roundtrip_fragment_input_same_location_type_changes",
    "pairs_with_roundtrip_vertex_output_location_or_type_changed",
    "pairs_with_roundtrip_fragment_input_location_or_type_changed",
    "pairs_with_only_vertex_side_change",
    "pairs_with_only_fragment_side_change",
    "pairs_with_both_interface_sides_changed",
    "pairs_with_no_interface_side_change",
    "original_fragment_compiled_user_inputs",
    "original_fragment_compiled_used_mask_nonzero",
    "original_fragment_compiled_used_mask_zero",
    "original_compiled_active_fragment_inputs_source_numeric_located",
    "original_compiled_active_fragment_inputs_source_numeric_absent",
    "original_compiled_unread_fragment_inputs_source_numeric_absent",
    "original_compiled_active_fragment_inputs_roundtrip_same_numeric_location",
)

def _stage(stage):
    return tr._validate_reflection(stage)

def _indexed(stage,side):
    return {r["location"]:r["type"] for r in stage[side]}

def _join(vertex,fragment):
    v=_indexed(vertex,"outputs")
    f=_indexed(fragment,"inputs")
    missing=sum(loc not in v for loc in f)
    type_changed=sum(loc in v and typ!=v[loc] for loc,typ in f.items())
    return missing,type_changed

def classify_pair(vsource,fsource,vround,fround,original_fragment):
    """Bounded structural counts, no private reflection values returned."""
    vsource,fsource,vround,fround=map(_stage,(vsource,fsource,vround,fround))
    if type(original_fragment) is not dict or type(original_fragment.get("input")) is not list:
        raise ValueError("invalid_original_compiled_fragment_signature")
    orig_missing,orig_type=_join(vsource,fsource)
    rt_missing,rt_type=_join(vround,fround)
    if orig_missing or orig_type or not interfaces_match(vsource,fsource):
        raise ValueError("unexpected_original_source_spirv_pair_incompatibility")
    source_out=_indexed(vsource,"outputs")
    round_out=_indexed(vround,"outputs")
    source_in=_indexed(fsource,"inputs")
    round_in=_indexed(fround,"inputs")
    source_locs=set(source_in)
    round_locs=set(round_in)
    a=classify_stage_io(vsource,vround)
    b=classify_stage_io(fsource,fround)
    vc=(source_out!=round_out)
    fc=(source_in!=round_in)
    result=Counter({
        "original_pairs_valid":1,
        "roundtrip_pairs_valid":int(not (rt_missing or rt_type)),
        "original_pairs_with_missing_fragment_location":int(orig_missing>0),
        "roundtrip_pairs_with_missing_fragment_location":int(rt_missing>0),
        "roundtrip_pairs_with_same_location_type_mismatch":int(rt_type>0),
        "original_fragment_missing_vertex_location_records":orig_missing,
        "roundtrip_fragment_missing_vertex_location_records":rt_missing,
        "roundtrip_fragment_same_location_type_mismatch_records":rt_type,
        "source_vertex_outputs_total":len(source_out),
        "source_fragment_inputs_total":len(source_in),
        "roundtrip_vertex_outputs_total":len(round_out),
        "roundtrip_fragment_inputs_total":len(round_in),
        "roundtrip_vertex_output_removed_locations_vs_source":a["outputs_removed_locations"],
        "roundtrip_vertex_output_added_locations_vs_source":a["outputs_added_locations"],
        "roundtrip_vertex_output_same_location_type_changes":a["outputs_same_location_type_changes"],
        "roundtrip_fragment_input_removed_locations_vs_source":b["inputs_removed_locations"],
        "roundtrip_fragment_input_added_locations_vs_source":b["inputs_added_locations"],
        "roundtrip_fragment_input_same_location_type_changes":b["inputs_same_location_type_changes"],
        "pairs_with_roundtrip_vertex_output_location_or_type_changed":int(vc),
        "pairs_with_roundtrip_fragment_input_location_or_type_changed":int(fc),
        "pairs_with_only_vertex_side_change":int(vc and not fc),
        "pairs_with_only_fragment_side_change":int(fc and not vc),
        "pairs_with_both_interface_sides_changed":int(vc and fc),
        "pairs_with_no_interface_side_change":int(not vc and not fc),
    })
    for item in original_fragment["input"]:
        if type(item) is not dict:
            raise ValueError("invalid_original_DXBC_signature_record")
        if (type(item.get("system_value")) is not int or
            type(item.get("register")) is not int or
            type(item.get("mask")) is not int or
            type(item.get("used_mask")) is not int or
            not 0<=item["used_mask"]<=15 or not 1<=item["mask"]<=15 or
            item["used_mask"] & ~item["mask"]):
            raise ValueError("invalid_original_fragment_used_mask_record")
        if item["system_value"]:
            continue
        reg=item["register"]
        if not 0<=reg<=4095:
            raise ValueError("unbounded_original_fragment_register")
        active=bool(item["used_mask"])
        result["original_fragment_compiled_user_inputs"]+=1
        result["original_fragment_compiled_used_mask_nonzero"]+=active
        result["original_fragment_compiled_used_mask_zero"]+=not active
        result["original_compiled_active_fragment_inputs_source_numeric_located"]+=int(active and reg in source_locs)
        result["original_compiled_active_fragment_inputs_source_numeric_absent"]+=int(active and reg not in source_locs)
        result["original_compiled_unread_fragment_inputs_source_numeric_absent"]+=int(not active and reg not in source_locs)
        # Numeric coincidence in generated HLSL roundtrip is NOT identity.
        result["original_compiled_active_fragment_inputs_roundtrip_same_numeric_location"]+=int(active and reg in round_locs)
    if set(result)-set(COUNTERS):
        raise ValueError("invalid_roundtrip_aggregate_schema")
    return {key:int(result[key]) for key in COUNTERS}

def evaluate(pairs,workspace,*,translator=translate,reflector=reflection,
             dxbc_reader=read_original_dxbc_signatures):
    if (type(pairs) is not list or len(pairs)!=PAIRS or
        any(type(p) is not tuple or len(p)!=2 or
            any(type(code) is not bytes or not 0<len(code)<=4*1024*1024
                for code in p) for p in pairs) or
        not isinstance(workspace,Path) or not workspace.is_dir()
        or workspace.is_symlink()):
        raise ValueError("untrusted_original_fourpair_scope")
    totals=Counter()
    for index,pair in enumerate(pairs):
        stages={}
        for stage,code in ((1,pair[0]),(0,pair[1])):
            folder=workspace/f"variant-{index}-stage-{stage}"
            folder.mkdir(exist_ok=False)
            # The translator report includes original program SHA; never print it.
            flags=translator(code,stage,folder)
            if (type(flags) is not dict or
                any(flags.get(k) is not True for k in
                    ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid"))):
                raise ValueError("original_HLSL_roundtrip_translation_incomplete")
            source=_stage(reflector(folder/"original.spv"))
            roundtrip=_stage(reflector(folder/"roundtrip.spv"))
            stages[stage]=(source,roundtrip)
        row=classify_pair(stages[1][0],stages[0][0],stages[1][1],
                          stages[0][1],dxbc_reader(pair[1]))
        for key in COUNTERS: totals[key]+=row[key]
    if totals["original_pairs_valid"]!=PAIRS:
        raise ValueError("original_fourpair_source_incomplete")
    # Do not assert expected 2/4 roundtrip compatibility: measure genuine code.
    return {
        "schema_version":1,"status":STATUS,
        "original_keyword_pairs":PAIRS,"original_DXBC_stage_programs":2*PAIRS,
        "counts":{key:int(totals[key]) for key in COUNTERS},
        "original_semantic_to_SPIRV_location_identity_proven":False,
        "roundtrip_HLSL_variable_semantic_identity_proven":False,
        "source_original_game_assets_modified":False,
        "private_shader_source_names_program_bytes_hashes_and_locations_published":False,
        "native_Unity_Android_Adreno_pixels_verified":False,
    }

def probe(original,manifest):
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    from scripts.w1_recover_graphics_programs import decoded_platforms,records
    for tool in tr.TOOLS:
        if shutil.which(tool) is None:
            raise ValueError("required_original_translation_tool_missing")
    selection={}
    source_report=tr.source.source.load_original(
        original,manifest,private_particle_slot_counts=selection)
    owner,pid=tr.source.select(selection,source_report)
    path=original/"Raft_Data"/owner
    if any(p.is_symlink() for p in (path,*path.parents)) or fingerprint(path)!=SHADER_OWNERS[owner]:
        raise ValueError("original_particle_shader_owner_SHA_drift")
    matched=[o for o in UnityPy.load(str(path)).file.objects.values()
             if o.path_id==pid]
    if len(matched)!=1 or matched[0].type.name!="Shader":
        raise ValueError("original_particle_Shader48_identity_drift")
    parsed=matched[0].read_typetree()
    tables=[records(parts) for platform,parts in decoded_platforms(parsed) if platform==4]
    if len(tables)!=1:
        raise ValueError("original_D3D11_table_ambiguous")
    source_baseline=tr.source.inspect(parsed["m_ParsedForm"],tables[0])
    if (source_baseline.get("status")!=tr.source.STATUS or
        source_baseline.get("original_D3D11_program_table_records")!=16 or
        source_baseline.get("matched_vertex_fragment_permutation_pairs")!=PAIRS):
        raise ValueError("original_shader_original_fourpair_stage_identity_drift")
    pairs=tr.exact_four_pairs(parsed["m_ParsedForm"],tables[0])
    with tempfile.TemporaryDirectory(prefix="t3-private-roundtrip-vf-") as folder:
        report=evaluate(pairs,Path(folder))
    report["source_original_six_scenes_SHA_verified"]=True
    report["source_original_four_Shader_Material_owner_SHA_verified"]=True
    return report

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original","manifest","out"):
        parser.add_argument("--"+name,type=Path,required=True)
    args=parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_private_roundtrip_report_path")
    try:
        result=probe(args.original,args.manifest)
    except Exception as exc:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "private_shader_source_names_program_bytes_hashes_and_locations_published":False,
                "native_Unity_Android_Adreno_pixels_verified":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("T3_AUTHENTIC_PARTICLE108_HLSL_ROUNDTRIP_VSFS "+
          json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
