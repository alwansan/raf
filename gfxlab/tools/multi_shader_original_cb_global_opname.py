#!/usr/bin/env python3
"""GFX052 private original DXBC b slots vs SPIR-V OpName on real Uniform globals.
Source register identities and shader contents never leave the CI runner.
Compiler register provenance is not Material semantics or member byte offsets.
"""
import argparse,json,re,tempfile
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_vkd3d_symbolic_register_map import private_register_from_name
from gfxlab.tools.multi_shader_original_cb_spv_blocksize import numeric_cb_coordinate_candidate
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

VAR=re.compile(r"^\s*(%[0-9]+)\s*=\s*OpVariable\s+%[0-9]+\s+Uniform(?:\s|$)")
DEC=re.compile(r"^\s*OpDecorate\s+(%[0-9]+)\s+(Binding|DescriptorSet)\s+([0-9]+)\s*$")
NAME=re.compile(r'^\s*OpName\s+(%[0-9]+)\s+"([^"]{1,100})"\s*$')
SFX=re.compile(r"^cb[0-9]+_([0-9]+)$")

def global_cb_evidence(dis,original,reflected):
    if (not isinstance(dis,bytes) or not 0<len(dis)<16*1024*1024
        or not isinstance(original,dict) or not isinstance(reflected,list)
        or len(original)>1024 or len(reflected)>1024):
        raise ValueError("GFX052_INPUT_INVALID")
    if any(type(k)!=int or type(v)!=int or not 0<=k<=65535 or
           not 0<v<=65535 for k,v in original.items()):
        raise ValueError("GFX052_SOURCE_CB_INVALID")
    try:lines=dis.decode("utf8","strict").splitlines()
    except UnicodeDecodeError:raise ValueError("GFX052_SPIRV_UTF8_INVALID") from None
    if len(lines)>300000:raise ValueError("GFX052_SPIRV_TOO_LONG")
    globals_=set();names={};bindings={};sets={}
    for line in lines:
        line=line.split(";",1)[0].strip()
        v=VAR.fullmatch(line)
        if v:
            if v.group(1) in globals_:raise ValueError("GFX052_DUPLICATE_GLOBAL")
            globals_.add(v.group(1));continue
        n=NAME.fullmatch(line)
        if n:
            if n.group(1) in names:raise ValueError("GFX052_DUPLICATE_OPNAME_ID")
            names[n.group(1)]=n.group(2);continue
        d=DEC.fullmatch(line)
        if d:
            x,kind,v=d.groups();target=bindings if kind=="Binding" else sets
            if x in target:raise ValueError("GFX052_DUPLICATE_DECORATION")
            target[x]=int(v)
    refcoords={}
    for row in reflected:
        if not isinstance(row,dict):raise ValueError("GFX052_REFLECTION_ROW_INVALID")
        slot=row.get("binding");s=row.get("set",0)
        if type(slot)!=int or type(s)!=int or slot<0 or s<0:
            raise ValueError("GFX052_REFLECTION_BINDING_INVALID")
        if (s,slot) in refcoords:raise ValueError("GFX052_DUPLICATE_REFLECTION_BINDING")
        refcoords[s,slot]=row.get("block_size")
    roots={}
    for var in globals_:
        if var not in bindings:raise ValueError("GFX052_UNIFORM_GLOBAL_MISSING_BINDING")
        coordinate=(sets.get(var,0),bindings[var])
        if coordinate in roots:raise ValueError("GFX052_DUPLICATE_UNIFORM_BINDING")
        roots[coordinate]=var
    c=Counter({
      "original_dxbc_CB_declarations":len(original),
      "translated_spv_reflected_ubos":len(refcoords),
      "actual_spv_Uniform_globals_with_binding":len(roots),
      "opname_labels_on_non_Uniform_global_ids_ignored":sum(x not in globals_ for x in names),
      "reflected_ubo_coordinates_without_global":sum(x not in roots for x in refcoords),
      "actual_reflected_ubo_globals_with_opname":0,
      "actual_reflected_ubo_globals_missing_opname":0,
      "actual_reflected_ubo_globals_unrecognized_CB_register_grammar":0,
      "actual_reflected_ubo_globals_with_cb_grammar":0,
      "global_cb_grammar_names_outside_original_b_set":0,
      "real_ubo_global_name_duplicates":0,
      "actual_global_name_source_b_slot_match":0,
      "actual_global_name_source_b_and_numeric_binding_match":0,
      "actual_global_name_source_b_binding_and_block_bytes_match":0,
      "actual_global_name_source_b_binding_block_bytes_mismatch":0,
      "actual_global_name_source_b_binding_missing_block_size":0,
      "source_cb_vec4_suffix_match":0,
      "source_cb_vec4_suffix_mismatch":0,
    })
    seen=set()
    for coordinate,var in roots.items():
        if coordinate not in refcoords:continue
        name=names.get(var)
        if name is None:
            c["actual_reflected_ubo_globals_missing_opname"]+=1
            continue
        c["actual_reflected_ubo_globals_with_opname"]+=1
        slot=private_register_from_name("constant_buffer",name)
        if slot is None:
            c["actual_reflected_ubo_globals_unrecognized_CB_register_grammar"]+=1
            continue
        c["actual_reflected_ubo_globals_with_cb_grammar"]+=1
        if name in seen:
            c["real_ubo_global_name_duplicates"]+=1
            continue
        seen.add(name)
        if slot not in original:
            c["global_cb_grammar_names_outside_original_b_set"]+=1
            continue
        c["actual_global_name_source_b_slot_match"]+=1
        if coordinate!=(0,slot):continue
        c["actual_global_name_source_b_and_numeric_binding_match"]+=1
        size=refcoords[coordinate]
        if type(size)!=int or size<=0:
            c["actual_global_name_source_b_binding_missing_block_size"]+=1
        elif original[slot]*16==size:
            c["actual_global_name_source_b_binding_and_block_bytes_match"]+=1
        else:
            c["actual_global_name_source_b_binding_block_bytes_mismatch"]+=1
        suffix=SFX.fullmatch(name)
        if suffix:
            if int(suffix.group(1))==original[slot]:c["source_cb_vec4_suffix_match"]+=1
            else:c["source_cb_vec4_suffix_mismatch"]+=1
    strict=(bool(original) and
        c["actual_global_name_source_b_binding_and_block_bytes_match"]==len(original) and
        len(original)==len(refcoords)==len(roots) and
        c["real_ubo_global_name_duplicates"]==0 and
        c["reflected_ubo_coordinates_without_global"]==0)
    return {**dict(c),
      "all_original_CB_registers_symbolically_correlated_with_actual_spv_UBO_globals":bool(strict),
      "original_Material_property_or_member_byte_layout_verified":False,
      "private_CB_register_ID_or_original_program_data_exported":False}

def audit(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=7 or any(not p["pairs"] for p in passes):
        raise ValueError("GFX052_PASS_TOPOLOGY_INVALID")
    totals=Counter();perpass=[]
    for row in passes:
        v,f=row["pairs"][0]
        data={"vertex":code_from_ref(v,programs,"Vertex"),
              "fragment":code_from_ref(f,programs,"Pixel")}
        p={}
        with tempfile.TemporaryDirectory(prefix="gfxlab052-private-") as tmp:
            folder=Path(tmp)
            out=translate_pair(data["vertex"],data["fragment"],folder)
            for kind,source in data.items():
                if not out[kind]["vulkan11_spirv_validation_success"]:
                    raise ValueError("GFX052_SPIRV_VALIDATION_FAILED")
                original=private_source_slots(source_shader_chunk(source))[1]
                spv=folder/(kind+".spv")
                ok,r=run_quiet(["spirv-cross",str(spv),"--reflect"])
                if not ok:raise ValueError("GFX052_REFLECTION_TOOL_FAILED")
                try:ref=json.loads(r.decode("utf8","strict"))
                except (UnicodeDecodeError,ValueError):
                    raise ValueError("GFX052_REFLECTION_FORMAT_INVALID") from None
                if not isinstance(ref,dict):
                    raise ValueError("GFX052_REFLECTION_NOT_OBJECT")
                candidate=numeric_cb_coordinate_candidate(original,ref.get("ubos",[]))
                ok,dis=run_quiet(["spirv-dis","--raw-id","--no-color",str(spv)])
                if not ok:raise ValueError("GFX052_SPV_DISASSEMBLY_FAILED")
                c=global_cb_evidence(dis,original,ref.get("ubos",[]))
                c["provisional_numeric_binding_CB_blocksize_complete"]=candidate["all_original_b_numbers_match_spirv_ubo_numeric_binding_and_block_byte_size_as_candidate_only"]
                p[kind]=c
                totals["source_stages_compared"]+=1
                totals["stages_complete_numeric_binding_candidates"]+=int(c["provisional_numeric_binding_CB_blocksize_complete"])
                totals["stages_complete_global_name_CB_register_provenance"]+=int(c["all_original_CB_registers_symbolically_correlated_with_actual_spv_UBO_globals"])
                for k in ("original_dxbc_CB_declarations","translated_spv_reflected_ubos",
                          "actual_spv_Uniform_globals_with_binding",
                          "opname_labels_on_non_Uniform_global_ids_ignored",
                          "reflected_ubo_coordinates_without_global",
                          "actual_reflected_ubo_globals_with_opname",
                          "actual_reflected_ubo_globals_missing_opname",
                          "actual_reflected_ubo_globals_unrecognized_CB_register_grammar",
                          "actual_reflected_ubo_globals_with_cb_grammar",
                          "real_ubo_global_name_duplicates",
                          "actual_global_name_source_b_slot_match",
                          "actual_global_name_source_b_and_numeric_binding_match",
                          "actual_global_name_source_b_binding_and_block_bytes_match"):
                    totals[k]+=c[k]
        perpass.append({"subshader_public_position":row["subshader"],
                        "pass_public_position":row["pass"],
                        "stage_safe_UBO_global_symbol_counts":p})
    if len(perpass)!=7 or totals["source_stages_compared"]!=14:
        raise ValueError("GFX052_STAGE_COUNT_INVALID")
    return {
      "experiment":"GFX-MULTI-052","original_zip2_sha":ZIP2_SHA,
      "evidence_level":"ORIGINAL_SOURCE_AND_TRANSLATED_SPV_UBO_GLOBAL_OPNAME_CPU_ONLY",
      "original_shader48_passes":7,"source_stages":14,"per_pass":perpass,
      "global_safe_counts":dict(totals),
      "all_14_original_CB_global_names_authentic":totals["stages_complete_global_name_CB_register_provenance"]==14,
      "all_524_original_variants_translated":False,
      "source_to_Material_property_register_mapping_proven":False,
      "original_CB_member_byte_offsets_proven":False,
      "original_android_shader48_GPU_runtime_proven":False,
      "PC_to_Adreno_original_pixel_parity_proven":False,
      "originalShaderRestored":False,
      "private_shader_names_code_b_registers_CB_offsets_exported":False,
      "phase_closed":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("GFX052_SAFE_ORIGINAL_CB_GLOBAL_NAME_COUNTS "+json.dumps(d,sort_keys=True))
if __name__=="__main__":main()
