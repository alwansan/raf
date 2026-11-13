#!/usr/bin/env python3
"""GT Particle108: source-bound Unity HLSL naming experiment (private only).

Moves translated HLSL *symbol names* to the exact serialized original Shader48
common and variant parameter records. Original DXBC bytecode, input texture
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
from scripts.a12_shader_parameter_decode import parse_parameter_blob
from scripts.b25_foam_cb_namebridge import original_name_registry
from scripts.gt_original_921_cb_hlsl import verify_named_constant_buffers
from scripts.gt_original_921_cb_layout import bind_constant_buffers, constant_buffer_lanes
from scripts.gt_particle108_source_sampling_pairs import sample_operand_pairs
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_rebind_depth_resources import IDENT
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.t3_particle108_original_dxbc_rdef import source_rdef, BIND_FAMILIES

# SPIRV-Cross HLSL may emit register(sN, space0) while older
# recovered code uses register(sN). Zero-space is explicit D3D11's
# default descriptor register space; no reassignment or guessing.
RESOURCE = re.compile(
    r'\b(Texture\w*(?:\s*<[^;{}>]+>)?|SamplerState|SamplerComparisonState)'
    r'\s+([A-Za-z_]\w*)\s*:\s*register\(\s*([ts])(\d+)'
    r'\s*(?:,\s*space0\s*)?\)\s*;'
)
SAMPLER_DECL = re.compile(r'\b(?:SamplerState|SamplerComparisonState)\s+[A-Za-z_]\w*\b')
SAMPLER_SPACE0 = re.compile(
    r'\b(?:SamplerState|SamplerComparisonState)\s+[A-Za-z_]\w*'
    r'\s*:\s*register\(\s*s\d+\s*,\s*space0\s*\)'
)
SAMPLER_UNSUPPORTED_SPACE = re.compile(
    r'\b(?:SamplerState|SamplerComparisonState)\s+[A-Za-z_]\w*'
    r'\s*:\s*register\(\s*s\d+\s*,\s*space[1-9]\d*\s*\)'
)
BUFFER=re.compile(r'\bcb\d+_\d+_m\d+\b')
MAX_HLSL=1024*1024
SAFE_FAILURE=frozenset((
    "SOURCE_ORIGINAL_MISMATCH", "SOURCE_TEXTURE_MAPPING_UNRESOLVED",
    "ORIGINAL_TEXTURE_NAME_INDEX_MISSING", "ORIGINAL_TEXTURE_REGISTER_DUPLICATED",
    "ORIGINAL_SAMPLER_REGISTER_AMBIGUOUS", "TRANSLATOR_NO_SOURCE_SAMPLER_DECLARATIONS",
    "TRANSLATOR_SAMPLER_DECLARATION_UNBOUND", "TRANSLATOR_SAMPLER_SPACE_NOT_ZERO",
    "TRANSLATOR_RESOURCE_REGISTER_UNPROVEN", "TRANSLATOR_RESOURCE_COLLISION",
    "ORIGINAL_DXBC_RDEF_SLOT_UNPROVEN", "ORIGINAL_DXBC_RDEF_AMBIGUOUS",
    "TRANSLATOR_SYMBOL_SOURCE_REGISTER_ID_MISSING",
    "TRANSLATOR_SYMBOL_REGISTER_ID_DRIFT",
    "TRANSLATOR_SOURCE_REGISTER_SLOT_MISSING",
    "TRANSLATOR_SOURCE_TEXTURE_SLOT_MISSING", "TRANSLATOR_SOURCE_SAMPLER_SLOT_MISSING",
    "TRANSLATOR_SOURCE_READ_FAILED", "ORIGINAL_STAGE_LAYOUT_UNSUPPORTED",
    "ORIGINAL_STAGE_COMMON_PARAMETERS_MISSING", "ORIGINAL_NAME_INDEX_TABLE_MISSING",
    "ORIGINAL_NAME_INDEX_ENTRY_UNSUPPORTED", "ORIGINAL_NAME_INDEX_INVALID",
    "ORIGINAL_NAME_INDEX_VALUE_TYPE", "ORIGINAL_NAME_INDEX_KEY_TYPE",
    "ORIGINAL_NAME_INDEX_COLLISION", "ORIGINAL_NAME_INDEX_NONIDENTIFIER",
    "ORIGINAL_TEXTURE_PARAMETER_NAME_NOT_IDENTIFIER",
    "ORIGINAL_TEXTURE_PARAMETER_TABLE_MISSING", "ORIGINAL_TEXTURE_PARAMETER_ENTRY_INVALID",
    "ORIGINAL_VULKAN_STAGE_REVALIDATION_FAILED",
    "ORIGINAL_VARIANT_PARAMETER_BLOB_INVALID", "ORIGINAL_VARIANT_TEXTURE_SLOT_DUPLICATED",
    "ORIGINAL_DXBC_SAMPLE_BINDING_MISMATCH", "ORIGINAL_CONSTANT_BUFFER_LAYOUT_UNPROVEN",
))
class BridgeError(ValueError):
    def __init__(self,reason):
        if reason not in SAFE_FAILURE: raise ValueError("unknown_private_shader_reason")
        self.reason=reason
        super().__init__(reason)


def original_names_and_registers(program,name_indices,variant_resources=()):
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
    texture_slots={}
    for row in raw:
        if not isinstance(row,dict) or not {"m_Index","m_NameIndex","m_SamplerIndex"}<=set(row):
            raise BridgeError("ORIGINAL_TEXTURE_PARAMETER_ENTRY_INVALID")
        t,n,s=row["m_Index"],row["m_NameIndex"],row["m_SamplerIndex"]
        if type(t) is not int or t<0 or t in texture_slots:
            raise BridgeError("ORIGINAL_TEXTURE_REGISTER_DUPLICATED")
        if n not in names:
            raise BridgeError("ORIGINAL_TEXTURE_NAME_INDEX_MISSING")
        texture_slots[t]=(names[n],s)
    variant_slots=set()
    for row in variant_resources:
        if row["kind"] != 0:
            continue
        slot=row["index"]
        if type(slot) is not int or slot<0 or slot in variant_slots:
            raise BridgeError("ORIGINAL_VARIANT_TEXTURE_SLOT_DUPLICATED")
        variant_slots.add(slot)
        texture_slots[slot]=(row["name"],row["extra_value"])
    textures,samplers={},{}
    for t,(name,s) in texture_slots.items():
        if not IDENT.fullmatch(name):
            raise BridgeError("ORIGINAL_TEXTURE_PARAMETER_NAME_NOT_IDENTIFIER")
        textures[t]=name
        if type(s) is int and 0<=s<65535:
            if s in samplers and samplers[s]!="sampler"+name:
                raise BridgeError("ORIGINAL_SAMPLER_REGISTER_AMBIGUOUS")
            samplers[s]="sampler"+name
    return textures,samplers


def variant_parameter_layout(program,table,bucket,ordinal):
    indices=program.get("m_ParameterBlobIndices")
    if type(indices) is not list or type(bucket) is not int or not 0<=bucket<len(indices):
        raise BridgeError("ORIGINAL_VARIANT_PARAMETER_BLOB_INVALID")
    rows=indices[bucket]
    if type(rows) is not list or type(ordinal) is not int or not 0<=ordinal<len(rows):
        raise BridgeError("ORIGINAL_VARIANT_PARAMETER_BLOB_INVALID")
    index=rows[ordinal]
    if type(index) is not int or not 0<=index<len(table):
        raise BridgeError("ORIGINAL_VARIANT_PARAMETER_BLOB_INVALID")
    layout={}
    try:
        parse_parameter_blob(table[index][1],private_layout=layout)
    except (IndexError,TypeError,ValueError):
        raise BridgeError("ORIGINAL_VARIANT_PARAMETER_BLOB_INVALID") from None
    return layout


def verify_sample_bindings(original_dxbc,textures,samplers):
    try:
        samples=sample_operand_pairs(original_dxbc)
    except ValueError:
        raise BridgeError("ORIGINAL_DXBC_SAMPLE_BINDING_MISMATCH") from None
    for texture,sampler,_ in samples:
        if texture not in textures or samplers.get(sampler)!="sampler"+textures[texture]:
            raise BridgeError("ORIGINAL_DXBC_SAMPLE_BINDING_MISMATCH")
    return len(samples)


def authenticated_original_dxbc_registers(original_dxbc):
    """Prove original compiled D3D11 sampler/SRV register classes and slots.

    RDEF is parsed from SHA-authenticated original VS/FS source. No vendor
    descriptor/array order and no inferred sampler policy may replace it.
    """
    if type(original_dxbc) is not bytes or len(original_dxbc)<36:
        raise BridgeError("ORIGINAL_DXBC_RDEF_SLOT_UNPROVEN")
    try:
        rows=source_rdef(original_dxbc)
    except ValueError as exc:
        # All eight SHA-original Particle108 stages in CI 43228860357 have
        # NO RDEF chunk. The independent source_rdef() parser authenticates
        # the DXBC container first. An absent ORIGINAL chunk is not corrupt
        # input, and is not a license to fabricate register identities.
        # A special sentinel requires real vkd3d source-register suffixes
        # plus original Unity serialized m_TextureParams for any mapping.
        if str(exc)=="DXBC_ORIGINAL_RDEF_ABSENT":
            return {"s":None,"t":None}
        raise BridgeError("ORIGINAL_DXBC_RDEF_SLOT_UNPROVEN") from None
    except TypeError:
        raise BridgeError("ORIGINAL_DXBC_RDEF_SLOT_UNPROVEN") from None
    slots={"s":set(),"t":set()}
    for kind,index,length in rows:
        family=BIND_FAMILIES[kind]
        category="s" if family=="sampler" else ("t" if family=="srv" else None)
        if category is None:
            continue
        for slot in range(index,index+length):
            if slot in slots[category]:
                raise BridgeError("ORIGINAL_DXBC_RDEF_AMBIGUOUS")
            slots[category].add(slot)
    return slots


def rebind_stage(hlsl,program,name_indices,stage,*,original_dxbc=None,variant_resources=None):
    if (type(hlsl) is not str or not 0<len(hlsl.encode())<=MAX_HLSL
        or type(stage) is not int or stage not in (0,1)):
        raise BridgeError("TRANSLATOR_SOURCE_READ_FAILED")
    textures,samplers=original_names_and_registers(program,name_indices,variant_resources or ())
    sample_count=0
    if variant_resources is not None:
        sample_count=verify_sample_bindings(original_dxbc,textures,samplers)
    authenticated_rdef=(None if original_dxbc is None else
                        authenticated_original_dxbc_registers(original_dxbc))
    # Reject a nonzero descriptor space even if ANOTHER sampler happens to
    # have a valid source mapping. This is originally compiled D3D11, not a
    # license to silently rewrite unsupported register spaceN.
    if SAMPLER_UNSUPPORTED_SPACE.search(hlsl):
        raise BridgeError("TRANSLATOR_SAMPLER_SPACE_NOT_ZERO")
    mapping={}
    used={"t":set(),"s":set()}
    translated_used={"t":set(),"s":set()}
    source_vs_translated_drift=0
    for match in RESOURCE.finditer(hlsl):
        cls,translated_num,variable=match[3],int(match[4]),match[2]
        table=textures if cls=="t" else samplers
        # vkd3d retains ORIGINAL DXBC resource register identities in the
        # recovered symbolic suffix. SPIRV-Cross HLSL register(tN/sN) may
        # renumber emitted descriptors. Never conflate the two namespaces.
        found=re.search(r'(?:^|_)'+cls+r'(\d+)$',variable)
        if found is None:
            found=re.search(r'(?:texture|sampler)'+cls+r'(\d+)$',variable,re.I)
        if found is None:
            # Anonymous translated symbol: only the source RDEF and same
            # original serialized register permit using a translated slot.
            if authenticated_rdef is None or authenticated_rdef[cls] is None:
                raise BridgeError("TRANSLATOR_SYMBOL_SOURCE_REGISTER_ID_MISSING")
            original_num=translated_num
        else:
            original_num=int(found[1])
        if original_num not in table:
            # Only the class is disclosed; source names/slots/keyword values
            # remain private to the disposable CI runner.
            raise BridgeError("TRANSLATOR_SOURCE_TEXTURE_SLOT_MISSING" if cls=="t"
                              else "TRANSLATOR_SOURCE_SAMPLER_SLOT_MISSING")
        if (authenticated_rdef is not None and authenticated_rdef[cls] is not None
            and original_num not in authenticated_rdef[cls]):
            raise BridgeError("ORIGINAL_DXBC_RDEF_SLOT_UNPROVEN")
        if original_num!=translated_num:
            if authenticated_rdef is None:
                raise BridgeError("TRANSLATOR_SYMBOL_REGISTER_ID_DRIFT")
            source_vs_translated_drift+=1
        if (original_num in used[cls] or translated_num in translated_used[cls]
            or variable in mapping):
            raise BridgeError("TRANSLATOR_RESOURCE_COLLISION")
        mapping[variable]=table[original_num]
        used[cls].add(original_num)
        translated_used[cls].add(translated_num)
    if not used["s"]:
        if SAMPLER_UNSUPPORTED_SPACE.search(hlsl):
            raise BridgeError("TRANSLATOR_SAMPLER_SPACE_NOT_ZERO")
        if SAMPLER_DECL.search(hlsl):
            raise BridgeError("TRANSLATOR_SAMPLER_DECLARATION_UNBOUND")
        # A vertex-only stage genuinely may have no texture/sampler inputs.
        # Permit that ONLY if the SHA-original program metadata also declares
        # no texture/sampler registers and the translated stage does not
        # advertise or sample a texture. Fragment source still needs a proved
        # sampled resource; no fabricated dummy sampler or register mapping.
        if not (stage == 1 and not textures and not samplers and
                not used["t"] and
                not re.search(r'\b(?:Texture\w*|sampler2D|Sample|SampleLevel|SampleBias)\b', hlsl)):
            raise BridgeError("TRANSLATOR_NO_SOURCE_SAMPLER_DECLARATIONS")
    # Every emitted sampler declaration must be covered by an exact source
    # register match. Partial proof can still give Unity "unrecognized sampler".
    if len(SAMPLER_DECL.findall(hlsl)) != len(used["s"]):
        raise BridgeError("TRANSLATOR_SAMPLER_DECLARATION_UNBOUND")
    if len(set(mapping.values()))!=len(mapping):
        raise BridgeError("TRANSLATOR_RESOURCE_COLLISION")
    # HLSL macro names and register numbers are preserved. Uniform backing
    # arrays in Vertex and Fragment can have DIFFERENT source dimensions:
    # disjoint stage-local identifiers prevent Unity's glslang linker from
    # incorrectly treating two different original stage layouts as one.
    buffers=sorted(set(BUFFER.findall(hlsl)))
    stage_prefix="GT_ORIGINAL_VS_" if stage==1 else "GT_ORIGINAL_PS_"
    mapping.update({name:stage_prefix+name for name in buffers})
    names=re.compile(r'\b(?:'+ '|'.join(re.escape(k) for k in sorted(mapping,key=len,reverse=True))+r')\b') if mapping else None
    # Only variable identifiers are replaced; binding register(tN/sN) is not
    # rewritten, as it is the compiled-program contract, not a variable.
    fixed=names.sub(lambda m:mapping[m.group()],hlsl) if names is not None else hlsl
    # Do not touch the translated graphics API register annotations: the
    # recovered source identity comes exclusively from original RDEF and
    # original Unity Shader metadata.
    register_pattern=re.compile(r'\bregister\s*\([^)]*\)')
    if register_pattern.findall(fixed)!=register_pattern.findall(hlsl):
        raise BridgeError("TRANSLATOR_RESOURCE_COLLISION")
    if len(fixed)>MAX_HLSL or (fixed==hlsl and variant_resources is None):
        raise BridgeError("TRANSLATOR_RESOURCE_COLLISION")
    return fixed,{"original_texture_registers_mapped":len(used["t"]),
                  "original_sampler_registers_mapped":len(used["s"]),
                  "original_DXBC_sample_operand_pairs_verified":sample_count,
                  "source_to_translator_descriptor_register_drifts_authenticated":source_vs_translated_drift,
                  "source_DXBC_original_RDEF_verified_absent":int(authenticated_rdef is not None and authenticated_rdef["s"] is None),
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
    if len(original_tables)!=1:
        raise BridgeError("SOURCE_ORIGINAL_MISMATCH")
    if set(private_source.glob("keyword-*-private.shader"))==set():
        raise BridgeError("TRANSLATOR_SOURCE_READ_FAILED")
    private_dest.mkdir(mode=0o700)
    counts=Counter()
    try:
        table=original_tables[0]
        names=original_name_registry(p["m_NameIndices"])
        pairs=translation.exact_four_stage_links(parsed,table)
        for n,(vs,fs) in enumerate(pairs):
            pieces={}
            for stage,(dxbc,bucket,ordinal) in ((1,vs),(0,fs)):
                path=private_source/("keyword-%d-stage-%d/private.hlsl"%(n,stage))
                if path.is_symlink() or not path.is_file():
                    raise BridgeError("TRANSLATOR_SOURCE_READ_FAILED")
                text=path.read_text(encoding="utf-8")
                program=p["progVertex" if stage==1 else "progFragment"]
                layout=variant_parameter_layout(program,table,bucket,ordinal)
                # Name the uniform fields first so the legacy compile-only
                # backing array disambiguation does not replace original CBs.
                try:
                    buffers=bind_constant_buffers(text,program["m_CommonParameters"],names,layout)
                    for buffer in buffers:
                        buffer["original_named_lanes"]=constant_buffer_lanes(buffer)
                    scratch=private_dest/f"constant-buffers-{n}-{stage}"
                    scratch.mkdir(mode=0o700)
                    (scratch/"resource-bound.hlsl").write_text(text,encoding="utf-8")
                    counts["named_constant_buffer_offsets"]+=verify_named_constant_buffers(scratch,stage,buffers)
                    named=(scratch/"named-constant-buffers.hlsl").read_text(encoding="utf-8")
                except (KeyError,ValueError):
                    raise BridgeError("ORIGINAL_CONSTANT_BUFFER_LAYOUT_UNPROVEN") from None
                fixed,stats=rebind_stage(named,program,p["m_NameIndices"],stage,
                                         original_dxbc=dxbc,variant_resources=layout["resources"])
                pieces[stage]=fixed
                counts["named_constant_buffer_layouts"]+=len(buffers)
                counts.update(stats)
            model=variants.source_models(vs[0],fs[0])
            candidate,_=variants.assemble(parsed,pieces[1],pieces[0],model)
            (private_dest/("keyword-%d-private.shader"%n)).write_text(candidate)
        result=router.verify(private_dest,parsed)
        (private_dest/"routing-safe.json").write_text(json.dumps(result),encoding="utf-8")
        if (result["status"]!=router.STATUS or
            result["private_combination_stage_Vulkan11_SPIRV_valid"]!=8):
            raise BridgeError("ORIGINAL_VULKAN_STAGE_REVALIDATION_FAILED")
    except BaseException:
        shutil.rmtree(private_dest)
        raise
    return {"schema":"GT_ORIGINAL_PARTICLE108_UNITY_RESOURCE_BRIDGE_V2",
            "status":"SOURCE_NAMED_STAGE_LOCAL_PRIVATE_HLSL_RECOMPILED_8_OF_8",
            "source_original_particle_shader_108_uses_SHA_verified":True,
            "original_source_four_variant_pairs_recovered":4,
            "private_original_programs_shipped_to_game":False,
            "private_vulkan11_recompiled_stage_branches":8,
            "private_source_mapped_original_texture_parameter_links":counts["original_texture_registers_mapped"],
            "private_source_mapped_original_sampler_parameter_links":counts["original_sampler_registers_mapped"],
            "private_original_DXBC_sample_operand_pairs_verified":counts["original_DXBC_sample_operand_pairs_verified"],
            "private_original_named_constant_buffer_layouts":counts["named_constant_buffer_layouts"],
            "private_original_named_constant_buffer_reflected_offsets":counts["named_constant_buffer_offsets"],
            "source_DXBC_original_RDEF_absent_stages":counts["source_DXBC_original_RDEF_verified_absent"],
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
        report={"schema":"GT_ORIGINAL_PARTICLE108_UNITY_RESOURCE_BRIDGE_V2",
                "status":"INCONCLUSIVE","failure_code":reason,
                "original_names_HLSL_DXBC_SPV_Guids_or_private_values_published":False,
                "Unity_Editor_compilation_proven":False}
    a.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_ORIGINAL_PARTICLE108_UNITY_RESOURCE_BRIDGE_SAFE "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]=="SOURCE_NAMED_STAGE_LOCAL_PRIVATE_HLSL_RECOMPILED_8_OF_8" else 2

if __name__=="__main__":
    raise SystemExit(main())
