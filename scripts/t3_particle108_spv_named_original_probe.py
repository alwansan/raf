#!/usr/bin/env python3
"""SHA-original Particle108 four VS/FS pairs: VKD3D SPIR-V debug-name candidates.

This is deliberately NOT a genuine DXBC-register↔Vulkan-descriptor proof:
SPIR-V OpName is debug metadata; matching its spelling cannot authenticate
binding semantics. Original program bytes, shader names, actual register
indices, SPV set/binding values and intermediate files stay ephemeral.
No Unity .shader or .meta files are created or edited.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile

from scripts import t3_particle108_dcl_spv_family_census as census
from scripts import t3_particle108_spirv_opname_candidates as names

STATUS="T3_ORIGINAL_PARTICLE108_VKD3D_SPIRV_DEBUG_NAME_CANDIDATES"
PAIRS=4
FIELDS=(
    "original_source_dcl_resource_rows",
    "spirv_debug_name_resource_candidates",
    "spirv_debug_candidates_matching_original_source_name_keys",
    "original_source_dcl_without_typed_debug_candidate",
    "spirv_named_candidate_not_in_source_dcl",
    "spirv_debug_named_family_or_type_unsupported",
    "spirv_debug_name_without_binding_or_set",
    "duplicate_candidate_descriptor_targets",
)
def classify(pairs,temp,*,translator=census.translate,
             dcl=census.dx._private_stage_layout,
             match=names.candidate_counts):
    """Private exact stage bytes -> strictly aggregate debug-name candidates."""
    if (type(pairs) is not list or len(pairs)!=PAIRS
        or any(type(pair) is not tuple or len(pair)!=2
               or any(type(code) is not bytes or
                      not 0<len(code)<=census.origin.MAX_PRIVATE_STAGE_BYTES
                      for code in pair) for pair in pairs)
        or not isinstance(temp,Path) or not temp.is_dir() or temp.is_symlink()):
        raise ValueError("T3_PRIVATE_STAGE_CANDIDATE_SCOPE")
    total=Counter()
    for i,(vs,ps) in enumerate(pairs):
        for stage,code in ((1,vs),(0,ps)):
            private_dir=temp/("pair-%d-stage-%d"%(i,stage))
            private_dir.mkdir(exist_ok=False)
            result=translator(code,stage,private_dir)
            if (type(result) is not dict
                or result.get("stage")!=stage
                or result.get("vulkan11_valid") is not True):
                raise ValueError("T3_PRIVATE_TRANSLATOR_STAGE_FAILURE")
            path=private_dir/"original.spv"
            if (not path.is_file() or path.is_symlink()
                or not 20<=path.stat().st_size<=names.MAX_SPIRV_BYTES):
                raise ValueError("T3_PRIVATE_TRANSLATOR_SPV_MISSING")
            evidence=match(dcl(code,stage),path.read_bytes(),stage)
            if (type(evidence) is not dict or
                set(FIELDS)-evidence.keys() or
                any(type(evidence[field]) is not int
                    or not 0<=evidence[field]<=1024 for field in FIELDS)
                or evidence.get("original_to_SPIRV_register_provenance_proven") is not False
                or evidence.get("debug_names_are_not_authoritative_binding_provenance") is not True
                or evidence.get("private_SPIRV_descriptor_sets_bindings_DXBC_registers_names_published") is not False):
                raise ValueError("T3_PRIVATE_SPV_DEBUG_CANDIDATE_RESULT_INVALID")
            total.update({k:evidence[k] for k in FIELDS})
            total["source_stages_analyzed"]+=1
            total["source_stages_with_all_debug_name_candidates"]+=int(
                evidence["all_original_resource_names_have_debug_candidates"])
        total["source_original_vsfs_keyword_pairs_analyzed"]+=1
    if (total["source_stages_analyzed"]!=2*PAIRS or
        total["source_original_vsfs_keyword_pairs_analyzed"]!=PAIRS):
        raise ValueError("T3_PRIVATE_SPV_CANDIDATE_COUNT_INCOMPLETE")
    return {
        "schema_version":1,"status":STATUS,"counts":dict(sorted(total.items())),
        "source_original_eight_stage_pairs_analyzed":True,
        "debug_names_are_only_non_authoritative_candidates":True,
        "source_register_to_vulkan_descriptor_equivalence_proven":False,
        "original_shader_Unity_compile_or_Android_pixels_proven":False,
        "source_original_register_shader_bytecode_or_spirv_names_published":False,
    }

def probe(original,manifest):
    for binary in census.origin.TOOLS:
        if shutil.which(binary) is None:
            raise ValueError("T3_PRIVATE_TRANSLATOR_TOOL_UNAVAILABLE")
    import UnityPy
    selected={}
    evidence=census.rb.identity.source.load_original(
        original,manifest,private_particle_slot_counts=selected)
    owner,pid=census.rb.identity.select(selected,evidence)
    source_path=original/"Raft_Data"/owner
    if (any(p.is_symlink() for p in (source_path,*source_path.parents))
        or census.fingerprint(source_path)!=census.SHADER_OWNERS[owner]):
        raise ValueError("T3_PRIVATE_ORIGINAL_OWNER_SHA_MISMATCH")
    originals=[o for o in UnityPy.load(str(source_path)).file.objects.values()
               if o.path_id==pid]
    if len(originals)!=1 or originals[0].type.name!="Shader":
        raise ValueError("T3_PRIVATE_ORIGINAL_SHADER_IDENTITY_MISSING")
    tree=originals[0].read_typetree()
    _,shape=census.serialize_properties(tree["m_ParsedForm"])
    if (shape["original_authored_property_count"]!=13 or
        shape["original_authored_texture_property_count"]!=2):
        raise ValueError("T3_PRIVATE_ORIGINAL_AUTHORED_PROPS_CHANGED")
    shader_tables=[census.records(s) for platform,s in census.decoded_platforms(tree)
                   if platform==4]
    if len(shader_tables)!=1:
        raise ValueError("T3_PRIVATE_ORIGINAL_D3D11_TABLE_MISSING")
    original_table=census.rb.identity.inspect(tree["m_ParsedForm"],
                                               shader_tables[0])
    if (original_table.get("status")!=census.rb.identity.STATUS or
        original_table.get("matched_vertex_fragment_permutation_pairs")!=PAIRS
        or original_table.get("original_D3D11_program_table_records")!=16):
        raise ValueError("T3_PRIVATE_ORIGINAL_KEYWORD_PAIRS_MISMATCH")
    pairs=census.origin.exact_four_pairs(tree["m_ParsedForm"],shader_tables[0])
    with tempfile.TemporaryDirectory(prefix="t3-private-spv-named-original-") as tmp:
        result=classify(pairs,Path(tmp))
    result["source_original_six_scenes_SHA_verified"]=True
    result["source_original_four_owners_SHA_verified"]=True
    result["source_original_renderer_material_use_slots"]=108
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for k in ("original","manifest","out"):
        parser.add_argument("--"+k,required=True,type=Path)
    a=parser.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("T3_PRIVATE_UNSAFE_OUTPUT_DESTINATION")
    try:
        report=probe(a.original,a.manifest)
    except Exception as exc:
        report={
            "schema_version":1,"status":"INCONCLUSIVE",
            "failure_type":type(exc).__name__,
            "debug_names_are_only_non_authoritative_candidates":True,
            "source_register_to_vulkan_descriptor_equivalence_proven":False,
            "original_shader_Unity_compile_or_Android_pixels_proven":False,
            "source_original_register_shader_bytecode_or_spirv_names_published":False,
        }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("T3_PRIVATE_SPV_DEBUG_CANDIDATES_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
