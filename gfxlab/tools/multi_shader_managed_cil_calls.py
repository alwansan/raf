#!/usr/bin/env python3
"""GFX-MULTI-044 authentic original Shader48 managed IL API-use candidates.

Use dnfile to resolve .NET metadata and dncil to parse real IL MethodDef.
Real UnityEngine Material/Shader API MethodRef owner + exact source Shader48
property ldstr literal can occur within the same private method / a short
instruction window. This is *not* argument dataflow, runtime execution,
DX11 register/CB identity, Android shader equivalence or pixel parity.

Private source never logged; only totals and booleans exported.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA,read_manifest
from gfxlab.tools.multi_shader_managed_literal_sidecar import (
    bound_source_names,validate_manifest,ASSEMBLIES,sha256_file,
)

MAX_METHODS=50000
MAX_METHOD_INSTRUCTIONS=100000
MAX_TOTAL_IL_INSTRUCTIONS=2500000
CALL_WINDOW=12
OWNERS=("Material","Shader","MaterialPropertyBlock")
UNITY_NS="UnityEngine"
METHODS={
 "Material":{"SetTexture","SetFloat","SetColor","SetVector","SetMatrix",
             "EnableKeyword","DisableKeyword","SetTextureOffset","SetTextureScale"},
 "Shader":{"PropertyToID","SetGlobalTexture","SetGlobalFloat","SetGlobalColor"},
 "MaterialPropertyBlock":{"SetTexture","SetFloat","SetColor","SetVector","SetMatrix"},
}


def classify_method_events(insns,props,texture_names,bound_names):
    """Source-private events: (opcode_index, kind, property-string|api-kind).

    Output count-only; a 12-instruction adjacency is a weak candidate, not IL
    stack-dataflow proof. Method co-occurrence is weaker still.
    """
    if not isinstance(insns,list) or len(insns)>MAX_METHOD_INSTRUCTIONS:
        raise ValueError("GFX044_METHOD_EVENTS_UNBOUNDED")
    strings=[]
    api=[]
    previous=-1
    for row in insns:
        if not isinstance(row,tuple) or len(row)!=3:
            raise ValueError("GFX044_EVENT_RECORD_BAD")
        index,kind,value=row
        if type(index) is not int or index<0 or index<previous:
            raise ValueError("GFX044_EVENT_INSTRUCTION_ORDER_INVALID")
        previous=index
        if kind=="property" and value in props:
            strings.append((index,value))
        elif kind=="api" and value in ("Material","Shader","MaterialPropertyBlock"):
            api.append((index,value))
        elif kind not in ("property","api"):
            raise ValueError("GFX044_EVENT_KIND_INVALID")
    if not strings and not api:return None
    has_both=bool(strings and api)
    nearby=sum(any(0<j-i<=CALL_WINDOW for j,_ in api) for i,_ in strings)
    nearby_distinct={name for i,name in strings
                     if any(0<j-i<=CALL_WINDOW for j,_ in api)}
    all_literal_names={name for i,name in strings}
    return {
      "has_exact_property_literal":bool(strings),
      "has_UnityEngine_Material_Shader_API_call":bool(api),
      "method_has_both_literal_and_API_call":has_both,
      "property_ldstr_instruction_count":len(strings),
      "UnityEngine_Material_Shader_API_call_instruction_count":len(api),
      "property_ldstr_with_later_API_call_in_12_instructions":nearby,
      "distinct_exact_Shader48_property_strings_in_method":len(all_literal_names),
      "distinct_exact_bound_texenv_strings_in_method":len(all_literal_names&bound_names),
      "distinct_exact_texture_property_strings_in_method":len(all_literal_names&texture_names),
      "private_literal_names_used_in_same_method":all_literal_names if has_both else set(),
      "private_literal_names_with_nearby_API_call":nearby_distinct,
    }


def inspect_assembly(path,props,texture_names,bound_names):
    import dnfile
    from dncil.cil.body import CilMethodBody
    from dncil.cil.error import MethodBodyFormatError
    from dncil.cil.body.reader import CilMethodBodyReaderBase
    from dncil.clr.token import StringToken,Token

    pe=dnfile.dnPE(str(path))
    if pe.net is None or pe.net.metadata is None or pe.net.mdtables is None:
        raise ValueError("GFX044_AUTHENTIC_ASSEMBLY_NO_DOTNET_METADATA")
    defs=pe.net.mdtables.MethodDef
    refs=pe.net.mdtables.MemberRef
    if defs is None or len(defs.rows)>MAX_METHODS:
        raise ValueError("GFX044_SOURCE_METHOD_DEFINITIONS_UNBOUNDED")
    class Reader(CilMethodBodyReaderBase):
        def __init__(self,row):
            self.pe=pe
            self.offset=pe.get_offset_from_rva(row.Rva)
        def read(self,n):
            if type(n) is not int or not 0<=n<=10*1024*1024:
                raise ValueError("GFX044_CIL_READ_LENGTH_INVALID")
            data=self.pe.get_data(self.pe.get_rva_from_offset(self.offset),n)
            if len(data)!=n:raise ValueError("GFX044_CIL_READ_TRUNCATED")
            self.offset+=n
            return data
        def tell(self):return self.offset
        def seek(self,offset):
            self.offset=offset
            return self.offset
    counts=Counter({
        "eligible_method_definitions":0,
        "successfully_parsed_CIL_methods":0,
        "failed_source_method_body_parse":0,
        "total_parsed_IL_instructions":0,
        "methods_with_Shader48_property_ldstr":0,
        "methods_with_exact_UnityEngine_material_shader_API_call":0,
        "methods_with_both_Shader48_literal_and_UnityEngine_API_call":0,
        "property_ldstr_instructions":0,
        "exact_UnityEngine_Material_Shader_API_call_instructions":0,
        "property_ldstr_with_following_12_instruction_API_call":0,
        "method_level_Shader48_bound_texture_candidate_count":0,
    })
    private_both=set();private_near=set()
    private_all_strings=set()
    api_owner_counts=Counter({k:0 for k in OWNERS})
    for row in defs.rows:
        if not row.ImplFlags.miIL or row.Flags.mdAbstract or row.Flags.mdPinvokeImpl or row.Rva==0:
            continue
        counts["eligible_method_definitions"]+=1
        try:
            body=CilMethodBody(Reader(row))
        except (MethodBodyFormatError,ValueError,IndexError,EOFError):
            counts["failed_source_method_body_parse"]+=1
            continue
        instructions=body.instructions
        if len(instructions)>MAX_METHOD_INSTRUCTIONS:
            raise ValueError("GFX044_SOURCE_CIL_METHOD_INSTRUCTIONS_UNBOUNDED")
        counts["successfully_parsed_CIL_methods"]+=1
        counts["total_parsed_IL_instructions"]+=len(instructions)
        if counts["total_parsed_IL_instructions"]>MAX_TOTAL_IL_INSTRUCTIONS:
            raise ValueError("GFX044_TOTAL_SOURCE_IL_INSTRUCTIONS_UNBOUNDED")
        events=[]
        for index,instr in enumerate(instructions):
            operand=instr.operand
            if instr.mnemonic=="ldstr" and isinstance(operand,StringToken):
                if pe.net.user_strings is None:
                    raise ValueError("GFX044_SOURCE_LDSTR_WITHOUT_US_HEAP")
                item=pe.net.user_strings.get(operand.rid)
                if item is None or not isinstance(item.value,str):
                    raise ValueError("GFX044_SOURCE_LDSTR_METADATA_UNRESOLVED")
                name=item.value
                if name in props:
                    private_all_strings.add(name)
                    events.append((index,"property",name))
            elif instr.mnemonic in ("call","callvirt") and isinstance(operand,Token):
                if operand.table!=10 or refs is None or not 1<=operand.rid<=len(refs.rows):
                    continue
                mr=refs.rows[operand.rid-1]
                parent=getattr(mr.Class,"row",None)
                ns=str(getattr(parent,"TypeNamespace",""))
                owner=str(getattr(parent,"TypeName",""))
                method=str(mr.Name)
                if ns==UNITY_NS and owner in METHODS and method in METHODS[owner]:
                    events.append((index,"api",owner))
                    api_owner_counts[owner]+=1
        result=classify_method_events(events,props,texture_names,bound_names)
        if result is None:continue
        counts["methods_with_Shader48_property_ldstr"]+=int(result["has_exact_property_literal"])
        counts["methods_with_exact_UnityEngine_material_shader_API_call"]+=int(
            result["has_UnityEngine_Material_Shader_API_call"])
        counts["methods_with_both_Shader48_literal_and_UnityEngine_API_call"]+=int(
            result["method_has_both_literal_and_API_call"])
        counts["property_ldstr_instructions"]+=result["property_ldstr_instruction_count"]
        counts["exact_UnityEngine_Material_Shader_API_call_instructions"]+=result[
            "UnityEngine_Material_Shader_API_call_instruction_count"]
        counts["property_ldstr_with_following_12_instruction_API_call"]+=result[
            "property_ldstr_with_later_API_call_in_12_instructions"]
        counts["method_level_Shader48_bound_texture_candidate_count"]+=int(
            result["method_has_both_literal_and_API_call"] and
            result["distinct_exact_bound_texenv_strings_in_method"]>0)
        private_both.update(result["private_literal_names_used_in_same_method"])
        private_near.update(result["private_literal_names_with_nearby_API_call"])
    return {
        **dict(counts),
        "exact_UnityEngine_API_call_owner_counts":dict(api_owner_counts),
        "distinct_Shader48_exact_property_strings_in_CIL_ldstr":len(private_all_strings),
        "distinct_Shader48_exact_property_strings_in_methods_with_Material_Shader_API":len(private_both),
        "distinct_Shader48_property_strings_followed_by_real_API_call_within_12_IL_instructions":len(private_near),
        "co_presence_or_nearby_instructions_prove_actual_material_argument_dataflow":False,
        "original_source_method_names_literal_names_IL_tokens_or_operands_exported":False,
    }


def audit(root,stage):
    manifest=read_manifest(root)
    validate_manifest(manifest)
    shader_props,tex_props,_,bound_props,_=bound_source_names(stage)
    original=ASSEMBLIES["Assembly-CSharp"]
    src=root/"Raft"/original["path"]
    if (not src.is_file() or src.is_symlink() or src.stat().st_size!=original["bytes"]
        or sha256_file(src)!=original["sha"]):
        raise ValueError("GFX044_ORIGINAL_ASSEMBLY_SHA_DRIFT")
    results=inspect_assembly(src,shader_props,tex_props,bound_props)
    return {
        "experiment":"GFX-MULTI-044",
        "original_zip2_sha":ZIP2_SHA,
        "original_shader48_properties":len(shader_props),
        "original_shader48_texture_properties":len(tex_props),
        "original_bound_material_texture_names":len(bound_props),
        "authentic_assembly":"Assembly-CSharp (SHA_PINNED)",
        "original_CIL_method_level_count_only_evidence":results,
        "original_material_property_to_t_s_b_register_bridge_proven":False,
        "original_CB_byte_offset_mapping_proven":False,
        "original_Shader48_Android_runtime_proven":False,
        "original_shader48_restored":False,
        "owner_original_PC_vs_Adreno_pixels_proven":False,
        "private_Managed_IL_literals_methods_or_assembly_bytes_exported":False,
        "phase_closed":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip2",type=Path,required=True)
    parser.add_argument("--stage",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    d=audit(a.zip2,stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI044_SAFE_MANAGED_CIL_CALL_CANDIDATES "+json.dumps(d,sort_keys=True))

if __name__=="__main__":main()
