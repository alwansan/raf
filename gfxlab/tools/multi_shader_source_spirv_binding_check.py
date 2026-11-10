#!/usr/bin/env python3
"""GFX-MULTI-018: private original DX11 b/t/s registers vs SPIR-V binding sets.

Each exact original Shader48 VS/FS pair is translated privately, then its
source DCL register-slot sets are compared numerically against SPIR-V reflected
descriptor binding values.  Numeric equality is NOT semantic equivalence.
No source slot values, shader code, names, keywords, CB sizes or private shader
binary are exported.
"""
from __future__ import annotations
import argparse,json,struct,tempfile
from pathlib import Path
from collections import Counter
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_register_operand_shape import declaration_operand,DECL
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

GROUPS={"constant_buffer":"ubos","resource":"separate_images","sampler":"separate_samplers"}

def private_source_slots(blob:bytes)->dict:
    if not isinstance(blob,bytes) or len(blob)<12 or len(blob)%4:
        raise ValueError("SOURCE_SHDR_BINARY_INVALID")
    words=struct.unpack("<%dI"%(len(blob)//4),blob)
    if words[1]!=len(words):raise ValueError("SOURCE_SHDR_DECLARED_LENGTH_INVALID")
    slots={k:set() for k in GROUPS}
    cb_sizes={}
    i=2
    while i<len(words):
        t=words[i];op=t&2047
        if op==53:
            if i+1>=len(words):raise ValueError("CUSTOM_TOKEN_LENGTH_MISSING")
            n=words[i+1]
            if n<2:raise ValueError("CUSTOM_TOKEN_LENGTH_INVALID")
        else:
            n=(t>>24)&127
            if n<1:raise ValueError("ORIGINAL_SHADER_INSTRUCTION_ZERO_LENGTH")
        if i+n>len(words):raise ValueError("ORIGINAL_SHADER_TOKEN_OVERRUN")
        if op in DECL:
            kind,indices=declaration_operand(op,words[i:i+n])
            if indices[0] in slots[kind]:raise ValueError("DUPLICATE_ORIGINAL_SHADER_REGISTER")
            slots[kind].add(indices[0])
            if kind=="constant_buffer":cb_sizes[indices[0]]=indices[1]
        i+=n
    if i!=len(words):raise ValueError("ORIGINAL_SHADER_TOKEN_TERMINATION")
    return slots,cb_sizes

def private_compare(source_slots,reflect_rows):
    if not isinstance(reflect_rows,list):raise ValueError("SPIRV_REFLECTION_GROUP_MALFORMED")
    descriptor_pairs=set();descriptor_bindings=set()
    missing=duplicate=0; sets_nonzero=0
    for row in reflect_rows:
        if not isinstance(row,dict):raise ValueError("SPIRV_REFLECTION_RECORD_NOT_OBJECT")
        b=row.get("binding");descriptor_set=row.get("set",0)
        if type(b)!=int or type(descriptor_set)!=int:
            missing+=1;continue
        if b<0 or descriptor_set<0:raise ValueError("SPIRV_REFLECTED_BINDING_NEGATIVE")
        pair=(descriptor_set,b)
        if pair in descriptor_pairs:duplicate+=1
        descriptor_pairs.add(pair)
        descriptor_bindings.add(b)
        sets_nonzero+=int(descriptor_set!=0)
    # All source slot numbers are used transiently only inside this function.
    count_equal=len(source_slots)==len(reflect_rows)
    slot_overlap=len(source_slots & descriptor_bindings)
    return {
      "source_original_dcl_count":len(source_slots),
      "spirv_reflection_resource_count":len(reflect_rows),
      "source_and_spirv_counts_equal":count_equal,
      "spirv_reflection_entries_without_binding":missing,
      "spirv_duplicate_descriptor_set_binding_pairs":duplicate,
      "spirv_nonzero_descriptor_set_entry_count":sets_nonzero,
      "same_numeric_slot_overlap_count":slot_overlap,
      "same_numeric_binding_set":(len(source_slots)==len(descriptor_bindings)
                                and source_slots==descriptor_bindings and missing==0),
      "original_dx11_register_to_spirv_semantic_equivalence":False}

def audit(stage):
    table,passes=source_pair(stage)
    if len(passes)!=7:raise ValueError("SOURCE_ORIGINAL_SHADER_PASS_DRIFT")
    per_pass=[]
    for entry in passes:
        if not entry["pairs"]:raise ValueError("PASS_MISSING_AUTHENTIC_MATCHED_VARIANT")
        vmeta,fmeta=entry["pairs"][0]
        with tempfile.TemporaryDirectory(prefix="gfxlab-private-bindings-") as td:
            folder=Path(td)
            original={s:code_from_ref(m,table,k) for s,m,k in
                (("vertex",vmeta,"Vertex"),("fragment",fmeta,"Pixel"))}
            src={s:private_source_slots(source_shader_chunk(d))[0]
                 for s,d in original.items()}
            translation=translate_pair(original["vertex"],original["fragment"],folder)
            reflected={}
            for stage_name in ("vertex","fragment"):
                if not translation[stage_name]["vulkan11_spirv_validation_success"]:
                    raise ValueError("ORIGINAL_SOURCE_SPIRV_TRANSLATION_REGRESSED")
                ok,out=run_quiet(["spirv-cross",str(folder/(stage_name+".spv")),"--reflect"])
                if not ok:raise ValueError("SPIRV_REFLECTION_FAILED")
                try:reflected[stage_name]=json.loads(out.decode("utf8"))
                except (ValueError,UnicodeDecodeError):
                    raise ValueError("SPIRV_REFLECTION_JSON_INVALID") from None
            compared={}
            for stage_name in ("vertex","fragment"):
                groups={}
                for family,spvkey in GROUPS.items():
                    rows=reflected[stage_name].get(spvkey,[])
                    groups[family]=private_compare(src[stage_name][family],rows)
                compared[stage_name]=groups
        per_pass.append({"subshader":entry["subshader"],"pass":entry["pass"],
                         "source_group_comparisons":compared,
                         "original_texture_to_spirv_sampler_identity_verified":False})
    summary=Counter()
    for entry in per_pass:
        for groups in entry["source_group_comparisons"].values():
            for result in groups.values():
                summary["groups_examined"]+=1
                summary["count_equal_groups"]+=int(result["source_and_spirv_counts_equal"])
                summary["same_numeric_binding_set_groups"]+=int(result["same_numeric_binding_set"])
                summary["source_total_resource_declarations"]+=result["source_original_dcl_count"]
                summary["spirv_total_reflected_resources"]+=result["spirv_reflection_resource_count"]
                summary["spirv_missing_binding_entries"]+=result["spirv_reflection_entries_without_binding"]
                summary["spirv_duplicate_set_binding_pairs"]+=result["spirv_duplicate_descriptor_set_binding_pairs"]
    return {"experiment":"GFX-MULTI-018","source_sha":ZIP2_SHA,
        "source_original_passes":7,"source_programs_checked":14,
        "private_source_vs_spirv_binding_numeric_summary":dict(summary),
        "per_pass":per_pass,
        "register_identity_to_material_texenv_verified":False,
        "cb_memory_layout_and_byte_offsets_verified":False,
        "normal_dxt5nm_srgb_metallic_semantics_verified":False,
        "actual_android_original_shader_execution_verified":False,
        "original_shader_bytes_or_register_ids_exported":False,
        "stage_closed":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();x=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI018_SAFE_SOURCE_SPIRV_BINDING_DIFFERENCES "+json.dumps(x,sort_keys=True))
if __name__=="__main__":main()
