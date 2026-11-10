#!/usr/bin/env python3
"""GFX-MULTI-053: source b#/vec4 -> vkd3d SPIR-V UBO byte-address audit.

Source-private, CPU-only. Requires original DXBC CB declaration, actual SPIR-V
Uniform global OpName b# provenance, same binding/byte-length, exactly one
reflected vec4 array member at offset 0 with stride 16 and literal extent,
plus an actually loaded strict SPIR-V OpAccessChain. No original shader bytes,
register indices, private offsets or material property values are exported.
The original DXBC access decoder covers only nine arithmetic opcode families.
"""
from __future__ import annotations
import argparse,json,re,tempfile
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_original_cb_access_shapes import scan_known_dxbc_cb_operands
from gfxlab.tools.multi_shader_original_cb_global_opname import global_cb_evidence, VAR, DEC, NAME
from gfxlab.tools.multi_shader_vkd3d_symbolic_register_map import private_register_from_name
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

MAX_TEXT=16*1024*1024
MAX_LINES=300000
ASSIGN=re.compile(r"^\s*(%[0-9]+)\s*=\s*(Op[A-Za-z0-9_]+)(?:\s+(.*))?$")
INT_TYPE=re.compile(r"^\s*(%[0-9]+)\s*=\s*OpTypeInt\s+32\s+[01]\s*$")

def private_authenticated_ubo_layouts(dis,source_cb,reflection):
    """Return private UBO global id -> (source b, member offset, stride, length).

    This is compiler-generated register identity and compiler UBO layout only.
    One non-vec4 member, a missing literal array bound, a non-16 stride, or
    a nonzero base offset is unresolved, never inferred from block_size.
    """
    if (not isinstance(dis,bytes) or not 0<len(dis)<=MAX_TEXT
            or not isinstance(source_cb,dict) or not isinstance(reflection,dict)):
        raise ValueError("GFX053_PRIVATE_INPUT_INVALID")
    lines=dis.decode("utf8","strict").splitlines()
    if len(lines)>MAX_LINES:raise ValueError("GFX053_PRIVATE_TEXT_TOO_LONG")
    types=reflection.get("types",{})
    ubos=reflection.get("ubos",[])
    if not isinstance(types,dict) or not isinstance(ubos,list) or len(ubos)>1024:
        raise ValueError("GFX053_REFLECTION_INVALID")
    globals_=set(); names={}; binding={};descriptor_set={}
    for line in lines:
        clean=line.split(";",1)[0].strip()
        v=VAR.fullmatch(clean)
        if v:
            if v.group(1) in globals_:raise ValueError("GFX053_DUPLICATE_UBO_GLOBAL")
            globals_.add(v.group(1))
        n=NAME.fullmatch(clean)
        if n:
            if n.group(1) in names:raise ValueError("GFX053_DUPLICATE_OPNAME_ID")
            names[n.group(1)]=n.group(2)
        d=DEC.fullmatch(clean)
        if d:
            ident,kind,value=d.groups()
            table=binding if kind=="Binding" else descriptor_set
            if ident in table:raise ValueError("GFX053_DUPLICATE_RESOURCE_DECORATION")
            table[ident]=int(value)
    reflection_by_coord={}
    for row in ubos:
        if not isinstance(row,dict):raise ValueError("GFX053_UBO_RECORD_INVALID")
        coordinate=(row.get("set",0),row.get("binding"))
        if any(type(x)!=int or x<0 for x in coordinate):
            raise ValueError("GFX053_INVALID_DESCRIPTOR_COORD")
        if coordinate in reflection_by_coord:raise ValueError("GFX053_DUPLICATE_REFLECTION_COORD")
        reflection_by_coord[coordinate]=row
    counts=Counter({
      "source_dxbc_cb_registers":len(source_cb),
      "spv_real_uniform_resource_globals":len(globals_),
      "spv_reflected_ubo_count":len(ubos),
      "proven_name_binding_size_CB_globals":0,
      "UBO_globals_strict_single_vec4_array_member_layout":0,
      "UBO_globals_without_supported_layout":0,
      "UBO_globals_with_missing_or_invalid_type_members":0,
      "UBO_globals_with_multiple_reflected_members":0,
      "UBO_globals_with_nonzero_or_missing_member_offset":0,
      "UBO_globals_with_non16_array_stride":0,
      "UBO_globals_with_missing_or_wrong_array_extent":0,
      "UBO_globals_with_unexpected_member_type":0,
    })
    eligible={}
    seen_b=set()
    for ident in globals_:
        name=names.get(ident)
        b=private_register_from_name("constant_buffer",name)
        coordinate=(descriptor_set.get(ident,0),binding.get(ident))
        if b not in source_cb or coordinate!=(0,b) or coordinate not in reflection_by_coord:
            continue
        r=reflection_by_coord[coordinate]
        if type(r.get("block_size"))!=int or r["block_size"]!=source_cb[b]*16:
            continue
        if b in seen_b:raise ValueError("GFX053_DUPLICATE_AUTHENTICATED_SOURCE_B")
        seen_b.add(b);counts["proven_name_binding_size_CB_globals"]+=1
        t=types.get(r.get("type"))
        if not isinstance(t,dict) or not isinstance(t.get("members"),list):
            counts["UBO_globals_with_missing_or_invalid_type_members"]+=1
            counts["UBO_globals_without_supported_layout"]+=1
            continue
        members=t["members"]
        if len(members)!=1:
            counts["UBO_globals_with_multiple_reflected_members"]+=1
            counts["UBO_globals_without_supported_layout"]+=1
            continue
        m=members[0]
        if not isinstance(m,dict):
            counts["UBO_globals_with_missing_or_invalid_type_members"]+=1
            counts["UBO_globals_without_supported_layout"]+=1
            continue
        if m.get("offset")!=0 or type(m.get("offset"))!=int:
            counts["UBO_globals_with_nonzero_or_missing_member_offset"]+=1
            counts["UBO_globals_without_supported_layout"]+=1
            continue
        if type(m.get("array_stride"))!=int or m.get("array_stride")!=16:
            counts["UBO_globals_with_non16_array_stride"]+=1
            counts["UBO_globals_without_supported_layout"]+=1
            continue
        extent=m.get("array")
        # Only accept one literal dimension equal to source vec4 DCL size.
        if (not isinstance(extent,list) or len(extent)!=1 or
            type(extent[0])!=int or extent[0]!=source_cb[b] or
            m.get("array_size_is_literal") not in (None,[True])):
            counts["UBO_globals_with_missing_or_wrong_array_extent"]+=1
            counts["UBO_globals_without_supported_layout"]+=1
            continue
        if m.get("type")!="vec4":
            counts["UBO_globals_with_unexpected_member_type"]+=1
            counts["UBO_globals_without_supported_layout"]+=1
            continue
        eligible[ident]=(b,0,16,source_cb[b])
        counts["UBO_globals_strict_single_vec4_array_member_layout"]+=1
    if counts["proven_name_binding_size_CB_globals"]>len(source_cb):
        raise ValueError("GFX053_LAYOUT_ACCOUNTING_INVALID")
    return eligible,dict(counts)

def spv_used_literal_byte_addresses(dis,authenticated):
    """Compute real OpLoad-used literal byte addresses from strict UBO globals.

    Only one-level OpAccessChain root, [struct_member=0, vector_index] are
    supported. Index types must be 32-bit OpTypeInt and literal OpConstant.
    Dynamic, pointer aliasing and opaque access remain UNKNOWN.
    """
    if not isinstance(dis,bytes) or not 0<len(dis)<=MAX_TEXT:
        raise ValueError("GFX053_SPV_USE_INPUT_INVALID")
    lines=dis.decode("utf8","strict").splitlines()
    if len(lines)>MAX_LINES:raise ValueError("GFX053_SPV_USE_TEXT_BOUNDS")
    typed_int=set();constants={}
    for line in lines:
        clean=line.split(";",1)[0].strip()
        m=INT_TYPE.fullmatch(clean)
        if m:typed_int.add(m.group(1))
    for line in lines:
        m=ASSIGN.fullmatch(line.split(";",1)[0].strip())
        if not m:continue
        ident,op,raw=m.groups();args=(raw or "").split()
        if op=="OpConstant" and len(args)==2 and args[0] in typed_int:
            try:v=int(args[1],10)
            except ValueError:continue
            if 0<=v<=65535:constants[ident]=v
    pointers={}
    stats=Counter({
      "SPV_access_chains_from_authenticated_CB_global":0,
      "SPV_access_chains_supported_literal_layout":0,
      "SPV_access_chains_dynamic_or_unsupported":0,
      "SPV_access_chains_literal_index_out_of_bounds":0,
      "SPV_pointer_loads_from_supported_access_chains":0,
      "SPV_distinct_loaded_CB_vec4_byte_addresses":0,
    })
    addresses={}
    loaded=set()
    for line in lines:
        m=ASSIGN.fullmatch(line.split(";",1)[0].strip())
        if not m:continue
        ident,op,raw=m.groups();args=(raw or "").split()
        if op in ("OpAccessChain","OpInBoundsAccessChain") and len(args)>=3:
            root=args[1]
            if root not in authenticated:continue
            stats["SPV_access_chains_from_authenticated_CB_global"]+=1
            b,base,stride,n=authenticated[root]
            if len(args)!=4 or args[2] not in constants or args[3] not in constants:
                stats["SPV_access_chains_dynamic_or_unsupported"]+=1
                continue
            member,vector=constants[args[2]],constants[args[3]]
            if member!=0 or vector>=n:
                stats["SPV_access_chains_literal_index_out_of_bounds"]+=1
                continue
            addr=base+stride*vector
            if addr!=vector*16:
                raise ValueError("GFX053_COMPILER_BYTE_ADDRESS_DISAGREES_WITH_DXBC_VEC4")
            pointers[ident]=(b,vector,addr)
            stats["SPV_access_chains_supported_literal_layout"]+=1
        elif op=="OpLoad" and len(args)>=2 and args[1] in pointers:
            # Only actually loaded addresses are counted as observed.
            stats["SPV_pointer_loads_from_supported_access_chains"]+=1
            loaded.add(pointers[args[1]])
        elif op=="OpCopyObject" and len(args)>=2 and args[1] in pointers:
            pointers[ident]=pointers[args[1]]
    for b,v,addr in loaded:addresses.setdefault(b,set()).add(addr)
    stats["SPV_distinct_loaded_CB_vec4_byte_addresses"]=len(loaded)
    return addresses,dict(stats)

def compare_source_to_translated_byte_addresses(source_vectors,spv_addresses):
    """Private source b#/index map to literal offset 16*vec; publish counts."""
    if not isinstance(source_vectors,dict) or not isinstance(spv_addresses,dict):
        raise ValueError("GFX053_SOURCE_SPV_ADDRESS_MAP_INVALID")
    src={(b,16*v) for b,vs in source_vectors.items() for v in vs}
    got={(b,a) for b,values in spv_addresses.items() for a in values}
    shared=src&got
    return {
      "source_subset_distinct_DXBC_CB_vec4_byte_addresses":len(src),
      "translated_SPV_distinct_loaded_CB_byte_addresses":len(got),
      "source_subset_byte_addresses_matched_in_translated_SPV":len(shared),
      "source_subset_byte_addresses_not_found_in_translated_SPV":len(src-got),
      "translated_SPV_byte_addresses_not_in_covered_DXBC_opcode_subset":len(got-src),
      "source_to_translated_address_overlap_is_original_Material_member_semantics":False,
      "private_CB_offsets_or_registers_exported":False,
    }

def audit(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=7 or any(not p["pairs"] for p in passes):
        raise ValueError("GFX053_SOURCE_PASS_DRIFT")
    totals=Counter();results=[]
    for passrow in passes:
        vertex,fragment=passrow["pairs"][0]
        binaries={"vertex":code_from_ref(vertex,programs,"Vertex"),
                  "fragment":code_from_ref(fragment,programs,"Pixel")}
        stages={}
        with tempfile.TemporaryDirectory(prefix="gfxlab053-private-") as tmp:
            folder=Path(tmp)
            translated=translate_pair(binaries["vertex"],binaries["fragment"],folder)
            for kind,binary in binaries.items():
                if not translated[kind]["vulkan11_spirv_validation_success"]:
                    raise ValueError("GFX053_SPIRV_VALIDATION_FAILED")
                shdr=source_shader_chunk(binary)
                source_cb=private_source_slots(shdr)[1]
                source_vectors,counts=scan_known_dxbc_cb_operands(shdr,source_cb)
                spv=folder/(kind+".spv")
                ok,payload=run_quiet(["spirv-cross",str(spv),"--reflect"])
                if not ok:raise ValueError("GFX053_REFLECTION_FAILED")
                try:reflect=json.loads(payload.decode("utf8","strict"))
                except (ValueError,UnicodeDecodeError):
                    raise ValueError("GFX053_REFLECTION_FORMAT_INVALID") from None
                if not isinstance(reflect,dict):raise ValueError("GFX053_REFLECTION_OBJECT_INVALID")
                ok,dis=run_quiet(["spirv-dis","--raw-id","--no-color",str(spv)])
                if not ok:raise ValueError("GFX053_DISASSEMBLY_FAILED")
                auth=global_cb_evidence(dis,source_cb,reflect.get("ubos",[]))
                if not auth["all_original_CB_registers_symbolically_correlated_with_actual_spv_UBO_globals"]:
                    raise ValueError("GFX053_GFX052_CB_GLOBAL_PROVENANCE_REGRESSION")
                root,layout=private_authenticated_ubo_layouts(dis,source_cb,reflect)
                addresses,usage=spv_used_literal_byte_addresses(dis,root)
                diff=compare_source_to_translated_byte_addresses(source_vectors,addresses)
                safe={**layout,**usage,**diff,
                    "source_DXBC_static_CB_operand_occurrences_in_supported_9_opcodes":counts["source_static_CB_vector_accesses_in_covered_arithmetic"],
                    "source_dynamic_CB_operands_in_supported_9_opcodes":counts["source_dynamic_or_extended_CB_accesses_in_covered_arithmetic"],
                    "source_DXBC_opcode_coverage_complete":False,
                    "original_CB_member_property_name_or_value_mapping_proven":False,
                    "shader48_original_Android_GPU_pixel_parity_proven":False}
                stages[kind]=safe
                totals["source_stages"]=totals.get("source_stages",0)+1
                for key in ("source_dxbc_cb_registers","proven_name_binding_size_CB_globals",
                            "UBO_globals_strict_single_vec4_array_member_layout",
                            "UBO_globals_without_supported_layout",
                            "SPV_access_chains_from_authenticated_CB_global",
                            "SPV_access_chains_supported_literal_layout",
                            "SPV_access_chains_dynamic_or_unsupported",
                            "SPV_access_chains_literal_index_out_of_bounds",
                            "SPV_pointer_loads_from_supported_access_chains",
                            "source_subset_distinct_DXBC_CB_vec4_byte_addresses",
                            "translated_SPV_distinct_loaded_CB_byte_addresses",
                            "source_subset_byte_addresses_matched_in_translated_SPV",
                            "source_subset_byte_addresses_not_found_in_translated_SPV",
                            "translated_SPV_byte_addresses_not_in_covered_DXBC_opcode_subset",
                            "source_dynamic_CB_operands_in_supported_9_opcodes"):
                    totals[key]+=safe[key]
        results.append({"subshader_public_position":passrow["subshader"],
                        "pass_public_position":passrow["pass"],
                        "safe_stage_layout_and_use_counts":stages})
    if len(results)!=7 or totals["source_stages"]!=14:
        raise ValueError("GFX053_STAGE_ACCOUNTING_INVALID")
    return {"experiment":"GFX-MULTI-053","zip2_sha":ZIP2_SHA,
        "evidence_level":"ORIGINAL_SOURCE_TO_TRANSLATED_SPIRV_AUTHENTICATED_CB_GLOBAL_AND_REFLECTED_LAYOUT_CPU_ONLY",
        "original_passes":7,"source_pair_representatives":7,"source_stages":14,
        "aggregate":dict(totals),"per_pass":results,
        "all_524_original_variants_covered":False,
        "all_source_DXBC_CB_using_opcodes_decoded":False,
        "source_to_original_ShaderLab_Material_property_member_mapping_proven":False,
        "original_Shader48_Android_GPU_execution_verified":False,
        "PC_to_Adreno_original_pixel_parity_proven":False,
        "originalShaderRestored":False,"phase_closed":False,
        "private_source_shader_CB_register_indexes_offsets_or_raw_spv_exported":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print("GFX053_SAFE_SOURCE_CB_BYTE_ADDRESS_OVERLAP "+json.dumps(r,sort_keys=True))
if __name__=="__main__":main()
