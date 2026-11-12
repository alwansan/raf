#!/usr/bin/env python3
"""GT Particle108: source-bound Unity HLSL naming experiment (private only).

Moves translated HLSL *symbol names* to the exact serialized original Shader48
m_TextureParams name/index contract. Original DXBC bytecode, input texture
payloads, Material/GUID bindings, values and register annotations are untouched.
Source metadata mismatch is a hard error, never guessed or auto-filled.
The candidate is NOT evidence of Android pixels, original keyword routing or
shader numerical equivalence until real Unity/Adreno tests succeed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil

from scripts import t3_original_renderer_shader_impact as impact
from scripts import t3_original_particle108_dxbc_feasibility as source_identity
from scripts import t3_original_particle108_spirv_translation as translation
from scripts import t3_particle108_private_shaderlab_variants as variants
from scripts import t3_particle108_private_keyword_routed_shaderlab as router
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_rebind_depth_resources import RESOURCE, IDENT
from scripts.w1_recover_graphics_programs import decoded_platforms, records

TOKENS=re.compile(r'\b(?:register\s*\([^)]*\)|[A-Za-z_]\w*)\b')
BUFFER=re.compile(r'\bcb\d+_\d+_m\d+\b')
MAX_HLSL=1024*1024
SAFE_FAILURE=frozenset((
    "SOURCE_ORIGINAL_MISMATCH", "SOURCE_TEXTURE_MAPPING_UNRESOLVED",
    "TRANSLATOR_RESOURCE_REGISTER_UNPROVEN", "TRANSLATOR_RESOURCE_COLLISION",
    "TRANSLATOR_SOURCE_READ_FAILED", "ORIGINAL_STAGE_LAYOUT_UNSUPPORTED",
    "ORIGINAL_STAGE_COMMON_PARAMETERS_MISSING", "ORIGINAL_NAME_INDEX_TABLE_MISSING",
    "ORIGINAL_NAME_INDEX_ENTRY_UNSUPPORTED", "ORIGINAL_NAME_INDEX_INVALID",
    "ORIGINAL_NAME_INDEX_VALUE_TYPE", "ORIGINAL_NAME_INDEX_KEY_TYPE",
    "ORIGINAL_NAME_INDEX_COLLISION", "ORIGINAL_NAME_INDEX_NONIDENTIFIER",
    "ORIGINAL_TEXTURE_PARAMETER_NAME_NOT_IDENTIFIER",
    "ORIGINAL_TEXTURE_PARAMETER_TABLE_MISSING", "ORIGINAL_TEXTURE_PARAMETER_ENTRY_INVALID",
    "ORIGINAL_VULKAN_STAGE_REVALIDATION_FAILED",
))
class BridgeError(ValueError):
    def __init__(self,reason):
        if reason not in SAFE_FAILURE: raise ValueError("unknown_private_shader_reason")
        self.reason=reason
        super().__init__(reason)


def original_names_and_registers(program,name_indices):
    common=program.get("m_CommonParameters")
    if not isinstance(common,dict):
        raise BridgeError("ORIGINAL_STAGE_COMMON_PARAMETERS_MISSING")
    if not isinstance(name_indices,list):
        raise BridgeError("ORIGINAL_NAME_INDEX_TABLE_MISSING")
    names={}
    for pair in name_indices:
        if not isinstance(pair,(tuple,list)) or len(pair)!=2:
            raise BridgeError("ORIGINAL_NAME_INDEX_ENTRY_UNSUPPORTED")
        name,index=pair
        if type(index) is not int:
            raise BridgeError("ORIGINAL_NAME_INDEX_VALUE_TYPE")
        if type(name) is not str:
            raise BridgeError("ORIGINAL_NAME_INDEX_KEY_TYPE")
        if index in names:
            if names[index]!=name:
                raise BridgeError("ORIGINAL_NAME_INDEX_COLLISION")
            # Identical repeated source table row retains original identity.
            continue
        # The complete Unity name-index table contains non-HLSL identifiers
        # (keyword/engine/display metadata). Validate identifier syntax ONLY
        # when this exact index is used as a serialized Texture m_NameIndex.
        names[index]=name
    raw=common.get("m_TextureParams")
    if type(raw) is not list: raise BridgeError("ORIGINAL_TEXTURE_PARAMETER_TABLE_MISSING")
    textures,samplers={},{}
    for row in raw:
        if not isinstance(row,dict) or not {"m_Index","m_NameIndex","m_SamplerIndex"}<=set(row):
            raise BridgeError("ORIGINAL_TEXTURE_PARAMETER_ENTRY_INVALID")
        t,n,s=row["m_Index"],row["m_NameIndex"],row["m_SamplerIndex"]
        if type(t) is not int or t<0 or t in textures or n not in names:
            raise BridgeError("SOURCE_TEXTURE_MAPPING_UNRESOLVED")
        name=names[n]
        if not IDENT.fullmatch(name):
            raise BridgeError("ORIGINAL_TEXTURE_PARAMETER_NAME_NOT_IDENTIFIER")
        textures[t]=name
        if type(s) is int and 0<=s<65535:
            if s in samplers and samplers[s]!="sampler"+name:
                raise BridgeError("SOURCE_TEXTURE_MAPPING_UNRESOLVED")
            samplers[s]="sampler"+name
    return textures,samplers


def rebind_stage(hlsl,program,name_indices,stage):
    if (type(hlsl) is not str or not 0<len(hlsl.encode())<=MAX_HLSL
        or type(stage) is not int or stage not in (0,1)):
        raise BridgeError("TRANSLATOR_SOURCE_READ_FAILED")
    textures,samplers=original_names_and_registers(program,name_indices)
    mapping={}
    used={"t":set(),"s":set()}
    for match in RESOURCE.finditer(hlsl):
        cls,num,variable=match[3],int(match[4]),match[2]
        table=textures if cls=="t" else samplers
        # SPIRV-Cross may reorder descriptor numbers. Require original DXBC
        # register numbering explicitly embedded in translated symbol name,
        # AND equal to HLSL register slot; otherwise no proof, do not guess.
        found=re.search(r'(?:^|_)'+cls+r'(\d+)$',variable)
        if found is None:
            found=re.search(r'(?:texture|sampler)'+cls+r'(\d+)$',variable,re.I)
        if found is None or int(found[1])!=num or num not in table:
            raise BridgeError("TRANSLATOR_RESOURCE_REGISTER_UNPROVEN")
        if num in used[cls] or (variable in mapping and mapping[variable]!=table[num]):
            raise BridgeError("TRANSLATOR_RESOURCE_COLLISION")
        mapping[variable]=table[num]
        used[cls].add(num)
    if not used["s"]:
        raise BridgeError("SOURCE_TEXTURE_MAPPING_UNRESOLVED")
    if len(set(mapping.values()))!=len(mapping):
        raise BridgeError("TRANSLATOR_RESOURCE_COLLISION")
    # HLSL macro names and register numbers are preserved. Uniform backing
    # arrays in Vertex and Fragment can have DIFFERENT source dimensions:
    # disjoint stage-local identifiers prevent Unity's glslang linker from
    # incorrectly treating two different original stage layouts as one.
    buffers=sorted(set(BUFFER.findall(hlsl)))
    stage_prefix="GT_ORIGINAL_VS_" if stage==1 else "GT_ORIGINAL_PS_"
    mapping.update({name:stage_prefix+name for name in buffers})
    names=re.compile(r'\b(?:'+ '|'.join(re.escape(k) for k in sorted(mapping,key=len,reverse=True))+r')\b')
    # Only variable identifiers are replaced; binding register(tN/sN) is not
    # rewritten, as it is the compiled-program contract, not a variable.
    fixed=names.sub(lambda m:mapping[m.group()],hlsl)
    if len(fixed)>MAX_HLSL or fixed==hlsl:
        raise BridgeError("TRANSLATOR_RESOURCE_COLLISION")
    return fixed,{"original_texture_registers_mapped":len(used["t"]),
                  "original_sampler_registers_mapped":len(used["s"]),
                  "stage_local_original_cbuffer_symbols_disambiguated":len(buffers),
                  "original_register_annotations_preserved":True}


def recover(root:Path,manifest:Path,private_source:Path,private_dest:Path):
    if (not root.is_dir() or root.is_symlink() or
        not private_source.is_dir() or private_source.is_symlink() or
        private_dest.exists() or private_dest.is_symlink() or
        not private_dest.parent.is_dir()):
        raise BridgeError("SOURCE_ORIGINAL_MISMATCH")
    selected={}
    result=impact.load_original(root,manifest,private_particle_slot_counts=selected)
    owner,pid=source_identity.select(selected,result)
    path=root/"Raft_Data"/owner
    if path.is_symlink() or fingerprint(path)!=SHADER_OWNERS[owner]:
        raise BridgeError("SOURCE_ORIGINAL_MISMATCH")
    import UnityPy
    records_found=[o for o in UnityPy.load(str(path)).file.objects.values()
                   if o.path_id==pid and o.type.name=="Shader"]
    if len(records_found)!=1:raise BridgeError("SOURCE_ORIGINAL_MISMATCH")
    tree=records_found[0].read_typetree()
    parsed=tree["m_ParsedForm"]
    if (len(parsed["m_SubShaders"])!=1 or
        len(parsed["m_SubShaders"][0]["m_Passes"])!=1):
        raise BridgeError("ORIGINAL_STAGE_LAYOUT_UNSUPPORTED")
    p=parsed["m_SubShaders"][0]["m_Passes"][0]
    original_tables=[records(parts) for platform,parts in decoded_platforms(tree) if platform==4]
    if len(original_tables)!=1 or len(translation.exact_four_pairs(parsed,original_tables[0]))!=4:
        raise BridgeError("SOURCE_ORIGINAL_MISMATCH")
    if set(private_source.glob("keyword-*-private.shader"))==set():
        raise BridgeError("TRANSLATOR_SOURCE_READ_FAILED")
    private_dest.mkdir()
    counts=Counter()
    try:
        pairs=translation.exact_four_pairs(parsed,original_tables[0])
        for n,(vs,fs) in enumerate(pairs):
            pieces={}
            for stage in (1,0):
                path=private_source/("keyword-%d-stage-%d/private.hlsl"%(n,stage))
                if path.is_symlink() or not path.is_file():
                    raise BridgeError("TRANSLATOR_SOURCE_READ_FAILED")
                text=path.read_text(encoding="utf-8")
                fixed,stats=rebind_stage(text,p["progVertex" if stage==1 else "progFragment"],
                                         p["m_NameIndices"],stage)
                pieces[stage]=fixed
                counts.update(stats)
            model=variants.source_models(vs,fs)
            candidate,_=variants.assemble(parsed,pieces[1],pieces[0],model)
            (private_dest/("keyword-%d-private.shader"%n)).write_text(candidate)
        result=router.verify(private_dest,parsed)
        if (result["status"]!=router.STATUS or
            result["private_combination_stage_Vulkan11_SPIRV_valid"]!=8):
            raise BridgeError("ORIGINAL_VULKAN_STAGE_REVALIDATION_FAILED")
    except BaseException:
        shutil.rmtree(private_dest)
        raise
    return {"schema":"GT_ORIGINAL_PARTICLE108_UNITY_RESOURCE_BRIDGE_V1",
            "status":"SOURCE_NAMED_STAGE_LOCAL_PRIVATE_HLSL_RECOMPILED_8_OF_8",
            "source_original_particle_shader_108_uses_SHA_verified":True,
            "original_source_four_variant_pairs_recovered":4,
            "private_original_programs_shipped_to_game":False,
            "private_vulkan11_recompiled_stage_branches":8,
            "private_source_mapped_original_texture_parameter_links":counts["original_texture_registers_mapped"],
            "private_source_mapped_original_sampler_parameter_links":counts["original_sampler_registers_mapped"],
            "private_stage_buffer_symbols_disambiguated":counts["stage_local_original_cbuffer_symbols_disambiguated"],
            "original_program_DXBC_bytes_or_values_modified":False,
            "original_HLSL_register_annotations_preserved":True,
            "original_material_GUID_ShaderOrGameAsset_modified":False,
            "Unity_Editor_compilation_proven":False,
            "original_ShaderLab_keyword_runtime_or_Adreno_pixels_proven":False,
            "original_names_HLSL_DXBC_SPV_Guids_or_private_values_published":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("original","manifest","private-source","private-dest","report"):
        p.add_argument("--"+arg,type=Path,required=True)
    a=p.parse_args()
    if (a.report.exists() or a.report.is_symlink()
        or a.report.resolve().is_relative_to(a.original.resolve())
        or a.report.resolve().is_relative_to(a.private_dest.resolve())):
        raise BridgeError("SOURCE_ORIGINAL_MISMATCH")
    try:
        report=recover(a.original,a.manifest,a.private_source,a.private_dest)
    except Exception as e:
        reason=e.reason if isinstance(e,BridgeError) else "UNCLASSIFIED_ORIGINAL_SOURCE"
        report={"schema":"GT_ORIGINAL_PARTICLE108_UNITY_RESOURCE_BRIDGE_V1",
                "status":"INCONCLUSIVE","failure_code":reason,
                "original_names_HLSL_DXBC_SPV_Guids_or_private_values_published":False,
                "Unity_Editor_compilation_proven":False}
    a.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_ORIGINAL_PARTICLE108_UNITY_RESOURCE_BRIDGE_SAFE "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]=="SOURCE_NAMED_STAGE_LOCAL_PRIVATE_HLSL_RECOMPILED_8_OF_8" else 2

if __name__=="__main__":
    raise SystemExit(main())
