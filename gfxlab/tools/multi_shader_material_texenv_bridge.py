#!/usr/bin/env python3
"""GFX-MULTI-020: verify authentic Unity 2021.3 Shader48 texture metadata to Material TexEnv.

Examines original SerializedPass m_NameIndices, matched SerializedSubProgram
m_Parameters.m_TextureParams (m_NameIndex/m_Index/m_SamplerIndex), source DX11
DCL t#/s# registers and seven original Material.m_SavedProperties.m_TexEnvs.

This creates private *candidate source bridges*, NOT proof that a property or
texture has correct GPU output, sampler state or original shader execution.
Never serialize source property names, register values, pointers, shader binary.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_source_select import selected_five
from gfxlab.tools.shears_texture_readiness import select_exact_renderer,pairs,classify_standard
from gfxlab.tools.shears_provenance_probe import resolve_pptr
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots

def pass_name_table(raw):
    """Private reverse map of Unity pass m_NameIndices: int -> property name."""
    if isinstance(raw,dict):
        items=list(raw.items())
    elif isinstance(raw,list):
        items=[]
        for entry in raw:
            if isinstance(entry,(list,tuple)) and len(entry)==2:
                pair=(entry[0],entry[1])
            elif isinstance(entry,dict) and set(entry)=={"first","second"}:
                pair=(entry["first"],entry["second"])
            elif isinstance(entry,dict) and set(entry)=={"m_First","m_Second"}:
                pair=(entry["m_First"],entry["m_Second"])
            elif isinstance(entry,dict) and set(entry)=={"key","value"}:
                pair=(entry["key"],entry["value"])
            elif isinstance(entry,dict) and len(entry)==1:
                pair=next(iter(entry.items()))
            else:raise ValueError("PASS_NAME_INDEX_SHAPE_UNSUPPORTED")
            items.append(pair)
    else:raise ValueError("PASS_NAME_INDICES_MISSING_OR_INVALID")
    result={}
    for name,index in items:
        if not isinstance(name,str) or not name or len(name)>256:
            raise ValueError("PASS_NAME_INDEX_NAME_INVALID")
        if type(index)!=int or index<0 or index>1000000:
            raise ValueError("PASS_NAME_INDEX_NUMBER_INVALID")
        if index in result and result[index]!=name:
            raise ValueError("AMBIGUOUS_PASS_PROPERTY_NAME_INDEX")
        result[index]=name
    return result

def original_material_texenv_sets(stage,types):
    private,_=selected_five(stage)
    keys=[(m["owner"],m["material_pid"])
          for entry in private["selected"] for m in entry["materials"]]
    envs,_,owner,renderer=select_exact_renderer(stage)
    refs=renderer.get("m_Materials")
    if not isinstance(refs,list) or len(refs)!=1:
        raise ValueError("SHEARS_MATERIAL_SLOT_DRIFT")
    externals=[x.path for x in envs[owner].file.externals]
    shears_key=resolve_pptr(refs[0],owner,externals)[1]
    if shears_key is None:raise ValueError("SHEARS_MATERIAL_PPTR_MISSING")
    keys.insert(0,shears_key)
    if len(keys)!=7:raise ValueError("EXPECTED_SEVEN_MATERIAL_SLOTS")
    material_sets=[]
    bound_sets=[]
    for key in keys:
        obj=types[key[0]].get(key[1])
        if obj is None or obj.type.name!="Material":
            raise ValueError("ORIGINAL_TYPED_MATERIAL_MISSING")
        mat=obj.read_typetree(check_read=False)
        saved=mat.get("m_SavedProperties")
        if not isinstance(saved,dict):raise ValueError("MATERIAL_SAVED_PROPERTIES_MISSING")
        envs=pairs(saved.get("m_TexEnvs",[]))
        present=set();bound=set()
        for name,val in envs:
            if not isinstance(val,dict):raise ValueError("ORIGINAL_TEXENV_UNEXPECTED")
            present.add(name)
            ptr=val.get("m_Texture")
            if not isinstance(ptr,dict):raise ValueError("ORIGINAL_TEXENV_POINTER_MISSING")
            path_id=ptr.get("m_PathID")
            if type(path_id)==int and path_id!=0:bound.add(name)
        material_sets.append(present)
        bound_sets.append(bound)
    return material_sets,bound_sets

def compare_one_program(meta,source,reverse,material_sets,bound_sets,shader_props):
    params=meta.get("m_Parameters")
    if not isinstance(params,dict):
        return {"parameters_block_present":False,
            "original_shader_texture_param_count":0,
            "exact_source_texture_slot_matches":0,
            "source_property_names_resolved":0,
            "original_material_texenv_name_matches":0,
            "bound_material_texenv_name_matches":0,
            "exact_source_property_t_sampler_to_material_bridges":0,
            "program_metadata_full_property_resolution":False}
    raw=params.get("m_TextureParams")
    if not isinstance(raw,list):raise ValueError("ORIGINAL_TEXTURE_PARAMETERS_NOT_ARRAY")
    counts=Counter()
    seen_slots=set();source_samplers=source["sampler"]
    for t in raw:
        if not isinstance(t,dict):raise ValueError("ORIGINAL_TEXTURE_PARAMETER_NOT_RECORD")
        counts["original_shader_texture_param_count"]+=1
        idx=t.get("m_Index");name_index=t.get("m_NameIndex")
        sampler=t.get("m_SamplerIndex")
        if type(idx)!=int or idx<0 or idx>65535 or type(name_index)!=int:
            raise ValueError("ORIGINAL_TEXTURE_PARAMETER_BAD_INDICES")
        if idx in seen_slots:counts["duplicate_shader_texture_param_slots"]+=1
        seen_slots.add(idx)
        is_source=idx in source["resource"]
        counts["exact_source_texture_slot_matches"]+=int(is_source)
        name=reverse.get(name_index)
        if name is None:
            counts["unresolved_pass_property_name_indices"]+=1
            continue
        counts["source_property_names_resolved"]+=1
        counts["source_shader_properties_declared"]+=int(name in shader_props)
        material_slots=sum(name in s for s in material_sets)
        bound_slots=sum(name in s for s in bound_sets)
        counts["original_material_texenv_name_matches"]+=material_slots
        counts["bound_material_texenv_name_matches"]+=bound_slots
        original_s=(type(sampler)==int and sampler in source_samplers)
        counts["exact_source_sampler_slot_matches"]+=int(original_s)
        counts["exact_source_property_t_sampler_to_material_bridges"]+=int(
            is_source and original_s and material_slots>0 and bound_slots>0)
        role=classify_standard(name)
        if is_source and bound_slots>0 and role in ("basecolor","normal","metallic"):
            counts["bridge_supported_material_role_"+role]+=1
        if not original_s:counts["unverified_or_missing_original_sampler_slot"]+=1
    cbs=params.get("m_ConstantBufferBindings",[])
    if not isinstance(cbs,list):raise ValueError("ORIGINAL_CB_BINDINGS_NOT_ARRAY")
    counts["original_shader_cb_binding_metadata_count"]=len(cbs)
    for b in cbs:
        if not isinstance(b,dict) or type(b.get("m_Index"))!=int:
            raise ValueError("ORIGINAL_CB_BINDING_METADATA_MALFORMED")
        counts["exact_source_cb_binding_slot_matches"]+=int(
            b["m_Index"] in source["constant_buffer"])
    result={key:int(counts[key]) for key in (
        "original_shader_texture_param_count",
        "duplicate_shader_texture_param_slots",
        "exact_source_texture_slot_matches",
        "source_property_names_resolved",
        "unresolved_pass_property_name_indices",
        "source_shader_properties_declared",
        "original_material_texenv_name_matches",
        "bound_material_texenv_name_matches",
        "exact_source_sampler_slot_matches",
        "unverified_or_missing_original_sampler_slot",
        "exact_source_property_t_sampler_to_material_bridges",
        "bridge_supported_material_role_basecolor",
        "bridge_supported_material_role_normal",
        "bridge_supported_material_role_metallic",
        "original_shader_cb_binding_metadata_count",
        "exact_source_cb_binding_slot_matches",
        )}
    result["parameters_block_present"]=True
    result["program_metadata_full_property_resolution"]=(
        len(raw)>0 and result["unresolved_pass_property_name_indices"]==0 and
        result["duplicate_shader_texture_param_slots"]==0 and
        result["exact_source_texture_slot_matches"]==len(raw))
    result["original_shader_texture_values_exported"]=False
    result["source_material_to_gpu_texture_semantics_verified"]=False
    return result

def audit(stage):
    entries,types,_=all_model_entries(stage)
    if len(entries)!=6 or sum(len(e["materials"]) for e in entries)!=7:
        raise ValueError("SOURCE_SELECTED_MATERIAL_COUNT_DRIFT")
    identity={(m["shader_owner"],m["shader_pid"]) for e in entries for m in e["materials"]}
    if len(identity)!=1:raise ValueError("SOURCE_SHADER48_IDENTITY_DRIFT")
    key=next(iter(identity))
    shader_obj=types[key[0]].get(key[1])
    if shader_obj is None or shader_obj.type.name!="Shader":
        raise ValueError("AUTHENTIC_CLASS48_NOT_FOUND")
    d=shader_obj.read_typetree(check_read=False).get("m_ParsedForm")
    if not isinstance(d,dict):raise ValueError("PARSED_SOURCE_SHADER_FORM_MISSING")
    prop=d.get("m_PropInfo",{}).get("m_Props",[])
    if not isinstance(prop,list):raise ValueError("SHADER_SOURCE_PROPERTIES_MISSING")
    shader_props={x["m_Name"] for x in prop
                  if isinstance(x,dict) and isinstance(x.get("m_Name"),str)}
    material_sets,bound_sets=original_material_texenv_sets(stage,types)
    compiled,original_passes=source_pair(stage)
    psubs=d.get("m_SubShaders",[])
    if len(psubs)!=2 or len(original_passes)!=7:raise ValueError("ORIGINAL_PASS_STRUCTURE_CHANGED")
    rows=[]
    for item in original_passes:
        si,pi=item["subshader"],item["pass"]
        shader_pass=psubs[si].get("m_Passes",[])[pi]
        reverse=pass_name_table(shader_pass.get("m_NameIndices"))
        if not item["pairs"]:raise ValueError("NO_EXACT_AUTHENTIC_STAGE_PAIR")
        v,f=item["pairs"][0]
        stages={}
        for stage_name,meta,kind in (("vertex",v,"Vertex"),("fragment",f,"Pixel")):
            src,cb_sizes=private_source_slots(source_shader_chunk(
                code_from_ref(meta,compiled,kind)))
            stages[stage_name]=compare_one_program(meta,src,reverse,material_sets,bound_sets,shader_props)
        rows.append({"subshader_ordinal":si,"pass_ordinal":pi,
                     "shader_private_name_index_entries":len(reverse),
                     "stages":stages})
    totals=Counter()
    for item in rows:
        for stage in item["stages"].values():
            for k,v in stage.items():
                if isinstance(v,int) and not isinstance(v,bool):
                    totals[k]+=v
            totals["stages_with_serialized_parameters"]+=int(stage["parameters_block_present"])
            totals["stages_with_all_texture_names_resolved"]+=int(
                stage["program_metadata_full_property_resolution"])
    return {"experiment":"GFX-MULTI-020","source_sha":ZIP2_SHA,
        "source_original_shader48_verified":True,
        "model_count":6,"original_material_slot_count":7,
        "source_shader_passes":7,"source_stages":14,
        "material_stored_texenv_slots":sum(map(len,material_sets)),
        "material_bound_texenv_slots":sum(map(len,bound_sets)),
        "source_property_name_count":len(shader_props),
        "original_shader_program_parameter_metadata_totals":dict(totals),
        "per_pass":rows,
        "one_source_material_texture_parameter_t_sampler_bridge_proven":(
            totals["exact_source_property_t_sampler_to_material_bridges"]>0),
        "all_shader_material_bindings_verified":False,
        "all_original_material_slots_gpu_verified":False,
        "original_CB_memory_offsets_verified":False,
        "original_GLES_shader_executed_on_Adreno":False,
        "original_shader_restored":False,
        "source_names_register_ids_textures_exported":False,
        "stage_closed":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();d=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI020_SAFE_ORIGINAL_MATERIAL_TEXENV_BRIDGE "+json.dumps(d,sort_keys=True))
if __name__=="__main__":main()
