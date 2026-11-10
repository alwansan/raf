#!/usr/bin/env python3
"""GFX-MULTI-019: exact original Shader48 register -> vkd3d SPIR-V name/binding proof.

vkd3d-shader assigns OpName to descriptor variables from original DX11 register
identifiers (e.g. tN, sN, cbN_size). Compare those generated names strictly
against privately decoded original SHDR declaration index sets. Material/CB
semantics and actual Android GPU rendering remain independently UNVERIFIED.

NEVER export original register indices, OpName strings, shader program code,
keyword names, GUIDs, PPtrs, material property identifiers, or raw SPIR-V.
"""
from __future__ import annotations
import argparse,json,re,tempfile
from pathlib import Path
from collections import Counter
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots,GROUPS
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

# Only vkd3d-generated register name grammar, NOT arbitrary words or names.
# The tSPACE_SLOT convention is valid only with source register space zero
# for this original Shader Model 5.0 legacy DXBC program.
_PATTERNS={
    "constant_buffer":(re.compile(r"^cb([0-9]+)_(?:[0-9]+)$"),re.compile(r"^cb([0-9]+)$")),
    "resource":(re.compile(r"^t([0-9]+)$"),re.compile(r"^t0_([0-9]+)$")),
    "sampler":(re.compile(r"^s([0-9]+)$"),re.compile(r"^s0_([0-9]+)$")),
}
_MAX_SLOT=65535

def private_register_from_name(family,name):
    """Parse private generated vkd3d debug name. Never log the input/return."""
    if family not in _PATTERNS or not isinstance(name,str) or len(name)>100:
        return None
    for pattern in _PATTERNS[family]:
        found=pattern.fullmatch(name)
        if found:
            value=int(found.group(1))
            return value if 0<=value<=_MAX_SLOT else None
    return None

def symbolic_binding_evidence(source_registers,reflection,family):
    """Infer a private register->descriptor candidate map, emit only aggregates."""
    if family not in _PATTERNS or not isinstance(source_registers,set):
        raise ValueError("INVALID_PRIVATE_SOURCE_REGISTER_GROUP")
    if not isinstance(reflection,list):
        raise ValueError("INVALID_PRIVATE_REFLECTION_GROUP")
    if any(type(x)!=int or x<0 or x>_MAX_SLOT for x in source_registers):
        raise ValueError("INVALID_PRIVATE_SOURCE_REGISTER_SLOT")
    mappings={};seen_pairs=set()
    counters=Counter()
    for entry in reflection:
        if not isinstance(entry,dict):
            raise ValueError("INVALID_PRIVATE_REFLECTION_RECORD")
        b=entry.get("binding");st=entry.get("set",0)
        if type(b)!=int or type(st)!=int or b<0 or st<0:
            counters["invalid_descriptor_coordinates"]+=1
            continue
        pair=(st,b)
        if pair in seen_pairs:counters["duplicate_descriptor_coordinates"]+=1
        seen_pairs.add(pair)
        slot=private_register_from_name(family,entry.get("name"))
        if slot is None:
            counters["generated_names_unrecognized"]+=1
            continue
        counters["generated_names_recognized"]+=1
        if slot not in source_registers:
            counters["generated_names_outside_original_source_group"]+=1
            continue
        if slot in mappings:
            counters["duplicate_generated_source_slot_names"]+=1
            continue
        mappings[slot]=pair
        if b!=slot or st!=0:
            counters["renumbered_source_slot_mappings"]+=1
        if st!=0:counters["nonzero_descriptor_set_mappings"]+=1
    complete=(len(source_registers)==len(reflection)==len(mappings)
              and not any(counters[k] for k in
                  ("invalid_descriptor_coordinates","duplicate_descriptor_coordinates",
                   "generated_names_unrecognized",
                   "generated_names_outside_original_source_group",
                   "duplicate_generated_source_slot_names")))
    # Do not serialize private mappings or matching slot IDs.
    return {"family":family,"original_register_count":len(source_registers),
        "reflected_resource_count":len(reflection),
        "vkd3d_symbolically_matched_registers":len(mappings),
        "numeric_binding_remapped_registers":counters["renumbered_source_slot_mappings"],
        "nonzero_descriptor_set_mappings":counters["nonzero_descriptor_set_mappings"],
        "unrecognized_generated_resource_names":counters["generated_names_unrecognized"],
        "out_of_source_generated_names":counters["generated_names_outside_original_source_group"],
        "duplicate_generated_register_names":counters["duplicate_generated_source_slot_names"],
        "duplicate_descriptor_bindings":counters["duplicate_descriptor_coordinates"],
        "bad_descriptor_coordinates":counters["invalid_descriptor_coordinates"],
        "all_original_registers_matched_by_vkd3d_name":bool(complete),
        "exact_material_texture_property_parity_verified":False,
        "cb_layout_byte_offset_equivalence_verified":False,
        "original_register_ids_or_opnames_exported":False}

def audit(stage):
    compiled,passes=source_pair(stage)
    if len(passes)!=7:raise ValueError("ORIGINAL_SHADER48_PASS_TOPOLOGY_CHANGED")
    reports=[]
    for pass_record in passes:
        if not pass_record["pairs"]:raise ValueError("NO_ORIGINAL_MATCHED_PAIR")
        vmeta,fmeta=pass_record["pairs"][0]
        with tempfile.TemporaryDirectory(prefix="gfxlab-vkd3d-private-map-") as tmp:
            base=Path(tmp)
            original={"vertex":code_from_ref(vmeta,compiled,"Vertex"),
                      "fragment":code_from_ref(fmeta,compiled,"Pixel")}
            source={stage_name:private_source_slots(source_shader_chunk(data))[0]
                    for stage_name,data in original.items()}
            converted=translate_pair(original["vertex"],original["fragment"],base)
            reflected={}
            for stage_name in ("vertex","fragment"):
                if not converted[stage_name]["vulkan11_spirv_validation_success"]:
                    raise ValueError("REAL_ORIGINAL_SPIRV_VALIDATION_REGRESSION")
                ok,payload=run_quiet(["spirv-cross",str(base/(stage_name+".spv")),"--reflect"])
                if not ok:raise ValueError("PRIVATE_SPIRV_CROSS_REFLECTION_FAILED")
                try:reflected[stage_name]=json.loads(payload.decode("utf8"))
                except (ValueError,UnicodeDecodeError):
                    raise ValueError("PRIVATE_SPIRV_REFLECTION_JSON_INVALID") from None
            per_stage={}
            for stage_name in ("vertex","fragment"):
                per_stage[stage_name]={}
                for family,spv_key in GROUPS.items():
                    per_stage[stage_name][family]=symbolic_binding_evidence(
                        source[stage_name][family],reflected[stage_name].get(spv_key,[]),family)
        reports.append({"subshader":pass_record["subshader"],"pass":pass_record["pass"],
                        "stages":per_stage})
    totals=Counter()
    for p in reports:
        for stage in p["stages"].values():
            for group in stage.values():
                totals["source_to_spv_resource_groups"]+=1
                totals["groups_complete_generated_name_identity"]+=int(
                    group["all_original_registers_matched_by_vkd3d_name"])
                totals["original_registers_total"]+=group["original_register_count"]
                totals["named_registers_matched_total"]+=group["vkd3d_symbolically_matched_registers"]
                totals["renumbered_registers_total"]+=group["numeric_binding_remapped_registers"]
                totals["unrecognized_names_total"]+=group["unrecognized_generated_resource_names"]
                totals["source_name_outliers_total"]+=group["out_of_source_generated_names"]
    return {"experiment":"GFX-MULTI-019","source_sha":ZIP2_SHA,
        "original_shader_passes":7,"source_stages":14,
        "vkd3d_generated_symbolic_binding_evidence":dict(totals),
        "per_pass":reports,
        "source_register_to_spv_descriptor_symbolic_coverage_verified":bool(
            totals["groups_complete_generated_name_identity"]==42
            and totals["named_registers_matched_total"]==122),
        "independent_original_material_texenv_to_binding_verified":False,
        "original_cb_byte_layout_offsets_verified":False,
        "sampler_texture_use_site_semantics_verified":False,
        "original_android_shader_gpu_tested":False,
        "all_524_variants_covered":False,
        "original_shader_restored":False,
        "raw_shaders_or_original_register_names_exported":False,
        "stage_closed":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--stage",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();r=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI019_SAFE_SYMBOLIC_REGISTER_MAPPING "+json.dumps(r,sort_keys=True))
if __name__=="__main__":main()
