#!/usr/bin/env python3
"""GFX-MULTI-043: authentic Raft managed literal Shader48 provenance census.

Pinned original ZIP2: original six models, 27 Shader48 serialized properties,
7 Material TexEnv property sets and two SHA-pinned managed PE assemblies.
Only count exact ECMA-335 #US literal property string matches; do not present
the original property names as source, or assert any DXBC register/CB binding.
Private CI runner deletes ZIP2/assembled assets/PEs after safe count report.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA,read_manifest
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_reflection_sweep import _locate_shader
from gfxlab.tools.multi_shader_material_texenv_bridge import original_material_texenv_sets

EXPECTED_MATERIAL_SLOTS=7
EXPECTED_SHADER_PROPERTIES=27
EXPECTED_TEXTURE_PROPERTIES=9
MAX_ASSEMBLY_BYTES=8*1024*1024
MAX_US_HEAP=8*1024*1024
MAX_US_ENTRIES=150000
MAX_LITERAL_LENGTH=2048

# Expected official original PC SHA pins from the source ZIP2 manifest.
ASSEMBLIES={
    "Assembly-CSharp":{
        "path":"Raft_Data/Managed/Assembly-CSharp.dll",
        "sha":"0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e",
        "bytes":3211776,
    },
    "Custom":{
        "path":"Custom.dll",
        "sha":"a2f736a38e3d1840a088c1af2aecc0fb99a49fa3abe28fce7fc094658d7f7ce9",
        "bytes":2202624,
    }
}
SOURCE_EXTENSIONS={
    ".shader",".shaderlab",".hlsl",".cginc",".compute",
    ".glsl",".vert",".frag",".spv",".dxbc",".dxil",".fx"
}
API_METHOD_NAMES={
    "Material.SetTexture","Material.SetFloat","Material.SetColor",
    "Material.SetVector","Material.SetMatrix","Material.EnableKeyword",
    "Material.DisableKeyword","Shader.PropertyToID","MaterialPropertyBlock.SetTexture",
    "MaterialPropertyBlock.SetColor","MaterialPropertyBlock.SetFloat",
}
# Use method-name-only reference as weak signal; declaring type not resolved.
WEAK_METHOD_NAMES={
    "SetTexture","SetFloat","SetColor","SetVector","SetMatrix",
    "EnableKeyword","DisableKeyword","PropertyToID"
}


def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        while chunk:=f.read(1024*1024):h.update(chunk)
    return h.hexdigest()


def validate_manifest(manifest):
    if not isinstance(manifest,dict):
        raise ValueError("GFX043_ORIGINAL_MANIFEST_MISSING")
    if len(manifest)!=366:
        raise ValueError("GFX043_ORIGINAL_MANIFEST_ENTRY_COUNT_DRIFT")
    source_candidate_count=0
    for rel,meta in manifest.items():
        if not isinstance(rel,str) or not isinstance(meta,dict) or not rel:
            raise ValueError("GFX043_MANIFEST_RECORD_INVALID")
        if Path(rel).suffix.lower() in SOURCE_EXTENSIONS:
            source_candidate_count+=1
    for a in ASSEMBLIES.values():
        meta=manifest.get(a["path"])
        if not meta or meta.get("kind")!="plain" or meta.get("sha256")!=a["sha"] or int(meta.get("bytes",0))!=a["bytes"]:
            raise ValueError("GFX043_AUTHENTIC_MANAGED_MANIFEST_PIN_FAILED")
    return source_candidate_count


def bound_source_names(stage):
    entries,types,_=all_model_entries(stage)
    shader=_locate_shader(entries,types)
    parsed=shader.read_typetree(check_read=False).get("m_ParsedForm")
    if not isinstance(parsed,dict):
        raise ValueError("GFX043_ORIGINAL_SHADER_PARSED_FORM_MISSING")
    props=parsed.get("m_PropInfo",{}).get("m_Props")
    if not isinstance(props,list) or len(props)!=EXPECTED_SHADER_PROPERTIES:
        raise ValueError("GFX043_ORIGINAL_PROPERTY_COUNT_DRIFT")
    names=set()
    textures=set()
    for prop in props:
        if not isinstance(prop,dict) or not isinstance(prop.get("m_Name"),str):
            raise ValueError("GFX043_SOURCE_PROPERTY_RECORD_BAD")
        name=prop["m_Name"]
        if not re.fullmatch(r"[_a-zA-Z][_a-zA-Z0-9]{0,127}",name):
            raise ValueError("GFX043_PRIVATE_PROPERTY_IDENTIFIER_UNSUPPORTED")
        names.add(name)
        if prop.get("m_Type")==4:textures.add(name)
    if len(names)!=EXPECTED_SHADER_PROPERTIES or len(textures)!=EXPECTED_TEXTURE_PROPERTIES:
        raise ValueError("GFX043_ORIGINAL_SHADER_PROPERTY_TYPE_DRIFT")
    material,real=original_material_texenv_sets(stage,types)
    if len(material)!=EXPECTED_MATERIAL_SLOTS or len(real)!=EXPECTED_MATERIAL_SLOTS:
        raise ValueError("GFX043_ORIGINAL_MATERIAL_COUNT_DRIFT")
    material_all=set().union(*material)
    bound=set().union(*real)
    if not material_all.issubset(names) or not bound.issubset(material_all):
        raise ValueError("GFX043_ORIGINAL_MATERIAL_TO_SHADER_PROPERTY_RELATION_INVALID")
    return names,textures,material_all,bound,[
        sum(len(s) for s in material),
        sum(len(s) for s in real),
    ]


def literal_heap_values(pe):
    """Strict #US heap iteration per dnfile's official dnstrings example."""
    stream=pe.net.user_strings if pe.net is not None else None
    if stream is None:
        return set(),0,False
    size=stream.sizeof()
    if not 1<=size<=MAX_US_HEAP:
        raise ValueError("GFX043_MANAGED_USER_STRING_HEAP_UNBOUNDED")
    offset=1
    found=set()
    count=0
    while offset<size:
        if offset+4>=size and pe.get_data(stream.rva+offset,1)==b"\0":
            break
        item=stream.get(offset,errors="surrogatepass")
        if item is None or type(item.raw_size) is not int or item.raw_size<=0:
            raise ValueError("GFX043_MANAGED_USER_STRING_RECORD_UNDECODABLE")
        if offset+item.raw_size>size:
            raise ValueError("GFX043_MANAGED_USER_STRING_RECORD_OVERRUN")
        raw=item.value
        if raw is None or not isinstance(raw,str):
            raise ValueError("GFX043_MANAGED_USER_STRING_NOT_TEXT")
        count+=1
        if count>MAX_US_ENTRIES:
            raise ValueError("GFX043_MANAGED_USER_STRING_COUNT_UNBOUNDED")
        if len(raw)<=MAX_LITERAL_LENGTH:
            found.add(raw)
        offset+=item.raw_size
    return found,count,True


def member_reference_name_counts(pe):
    """Weak *method-name presence* only; not a verified API call site."""
    table=pe.net.mdtables.MemberRef if pe.net and pe.net.mdtables else None
    counts=Counter({name:0 for name in WEAK_METHOD_NAMES})
    total=0
    if table is None:return counts,total
    rows=table.rows
    if len(rows)>150000:
        raise ValueError("GFX043_MANAGED_MEMBERREF_TABLE_UNBOUNDED")
    for row in rows:
        total+=1
        name=str(row.Name)
        if name in counts:counts[name]+=1
    return counts,total


def private_assembly_audit(path,shader_props,texture_props,material_props,bound_props):
    import dnfile
    if not path.is_file() or not 0<path.stat().st_size<=MAX_ASSEMBLY_BYTES:
        raise ValueError("GFX043_AUTHENTIC_PE_SOURCE_SIZE_INVALID")
    pe=dnfile.dnPE(str(path))
    if pe.net is None or pe.net.metadata is None:
        raise ValueError("GFX043_SOURCE_NOT_MANAGED_DOTNET_ASSEMBLY")
    values,count,has_heap=literal_heap_values(pe)
    weak,member_refs=member_reference_name_counts(pe)
    return {
        "managed_user_string_heap_present":has_heap,
        "managed_literal_entry_count":count,
        "distinct_managed_literals_count":len(values),
        "original_shader_property_literals_exact_count":len(values&shader_props),
        "original_texture_property_literals_exact_count":len(values&texture_props),
        "original_material_texenv_property_literals_exact_count":len(values&material_props),
        "original_bound_texture_property_literals_exact_count":len(values&bound_props),
        "weak_member_reference_name_counts":dict(weak),
        "weak_member_reference_entries_total":member_refs,
        "member_names_or_literals_do_not_prove_call_site":True,
        "original_source_literals_or_managed_bytes_published":False,
    }


def audit(root,stage):
    manifest=read_manifest(root)
    sidecars=validate_manifest(manifest)
    shader_props,texture_props,material_props,bound_props,slots=bound_source_names(stage)
    result={}
    union={s:set() for s in ("shader","texture","material","bound")}
    for label,info in ASSEMBLIES.items():
        src=root/"Raft"/info["path"]
        if not src.is_file() or src.is_symlink() or (
            src.stat().st_size!=info["bytes"] or sha256_file(src)!=info["sha"]):
            raise ValueError("GFX043_SOURCE_PE_SHA_PIN_MISMATCH")
        # Reparse independently for deduplicated union across two assemblies.
        import dnfile
        pe=dnfile.dnPE(str(src))
        strings,_,_=literal_heap_values(pe)
        union["shader"].update(strings&shader_props)
        union["texture"].update(strings&texture_props)
        union["material"].update(strings&material_props)
        union["bound"].update(strings&bound_props)
        result[label]=private_assembly_audit(src,shader_props,texture_props,material_props,bound_props)
    return {
        "experiment":"GFX-MULTI-043",
        "source_zip2_sha":ZIP2_SHA,
        "source_manifest_entries":len(manifest),
        "standalone_shader_source_extension_candidate_files":sidecars,
        "authentic_managed_assemblies_checked":len(result),
        "original_shader48_property_count":len(shader_props),
        "original_shader48_texture_property_count":len(texture_props),
        "original_distinct_material_texenv_names":len(material_props),
        "original_distinct_bound_texture_texenv_names":len(bound_props),
        "original_material_texenv_slots":slots[0],
        "original_material_bound_texture_slots":slots[1],
        "managed_assembly_private_literal_counts":result,
        "union_across_assemblies":{
            "original_shader_property_literal_names_exact":len(union["shader"]),
            "original_shader_texture_property_literal_names_exact":len(union["texture"]),
            "original_material_property_literal_names_exact":len(union["material"]),
            "original_bound_material_texture_literal_names_exact":len(union["bound"]),
        },
        "property_name_to_DX11_t_s_cb_register_mapping_verified":False,
        "managed_string_presence_proves_material_api_call_site":False,
        "exact_shader_property_to_CB_byte_offsets_verified":False,
        "original_shader48_restored":False,
        "android_original_shader48_execution_verified":False,
        "original_pc_adreno_pixels_verified":False,
        "proprietary_source_strings_shaders_binaries_or_named_members_exported":False,
        "phase_closed":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--stage",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    report=audit(a.zip2,stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI043_SAFE_MANAGED_PROVENANCE_CENSUS "+json.dumps(report,sort_keys=True))


if __name__=="__main__":main()
