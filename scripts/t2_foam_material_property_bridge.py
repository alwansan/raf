"""T2: SHA-pinned original Foam Shader property ↔ direct Material TexEnv evidence.

Match private source m_TextureParams resolved names to authored Shader
m_PropInfo texture property names, and only locally owned original Material
m_Shader PPtrs to those same source names. Reuse B05 original TexEnv/PPtr/UV
decoder and B25 pass name registry. No private names, IDs, texture values,
serialized shader bytes or Unity material property strings are published.

This is STATIC serialized data evidence, not runtime upload, ShaderLab import,
GPU sampler filter/wrap or Adreno pixel acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.b05_verify_material_texenv_bindings import (
    normalize_texenvs, _original_pointer,
)
from scripts.b20_private_foam_packet import ORIGINAL_STAGE_SHA
from scripts.b24_original_foam_stage_translation import (
    OWNER, TARGET, OBJECT_ID, ORIGINAL_OBJECT_SHA256,
)
from scripts.b25_foam_cb_namebridge import original_name_registry, inspect_parsed
from scripts.t2_foam_texture_identity import original_texture_rows
from scripts.t2_foam_original_dxbc_registers import source_texture_registers
from scripts.t2_foam_resource_abi import ORIGINAL_TEXTURES_PER_STAGE
from scripts.t2_foam_member_abi import STAGES, _physical
from scripts.w1_stage_zip2_owners import PINS, fingerprint

MAX_PROPERTIES = 256
MAX_MATERIALS = 10000
MAX_TEXENVS = 256
ALLOWED_LOCAL_TEXTURE_CLASSES = frozenset({
    "Texture2D", "Texture3D", "Texture2DArray", "Cubemap",
    "CubemapArray", "RenderTexture",
})


def shader_authored_texture_props(parsed):
    """Private exact authored Shader property strings; no reporting of names."""
    if not isinstance(parsed, dict):
        raise ValueError("Original parsed Shader absent")
    propinfo = parsed.get("m_PropInfo")
    if not isinstance(propinfo, dict) or not isinstance(propinfo.get("m_Props"), list):
        raise ValueError("Original Shader authored property table missing")
    entries = propinfo["m_Props"]
    if len(entries) > MAX_PROPERTIES:
        raise ValueError("Original authored property table unbounded")
    all_names, texture_names = set(), set()
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("Original authored property malformed")
        name, value_type = item.get("m_Name"), item.get("m_Type")
        if (not isinstance(name, str) or not 0 < len(name) <= 256
                or "\x00" in name or type(value_type) is not int
                or value_type < 0 or value_type > 8 or name in all_names):
            raise ValueError("Duplicate or malformed authored shader property")
        all_names.add(name)
        if value_type == 4:
            texture_names.add(name)
    return texture_names, all_names


def original_stage_shader_property_join(parsed):
    """Keep source t/s and property names only temporarily for subsequent joins."""
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Original Foam Shader identity changed")
    cb = inspect_parsed(parsed)
    if (cb.get("authenticated_stage_count") != 4 or
            cb.get("matched_constant_buffer_bindings") != 8):
        raise ValueError("B25 original source CB/pass name prerequisite absent")
    textures, all_props = shader_authored_texture_props(parsed)
    subs = parsed.get("m_SubShaders")
    if not isinstance(subs, list) or len(subs) != 1:
        raise ValueError("Foam original subshader missing")
    passes = subs[0].get("m_Passes")
    if not isinstance(passes, list) or len(passes) != 2:
        raise ValueError("Foam original two-pass source changed")
    seen, out = set(), []
    for pi, stage in STAGES:
        if (pi,stage) in seen:
            raise ValueError("Original pass/stage repeated")
        seen.add((pi,stage))
        p = passes[pi]
        registry = original_name_registry(p.get("m_NameIndices"))
        prog = p["progVertex" if stage == 1 else "progFragment"]
        count = ORIGINAL_TEXTURES_PER_STAGE[(pi,stage)]
        original = original_texture_rows(prog,registry,count)
        register_rows = source_texture_registers(prog,count)
        expected_pairs = {(i,i) for i in range(count)}
        paired = {tuple(x["_private_numeric_pair"]) for x in original}
        native_pairs = {
            (x["original_texture_index"],x["original_sampler_index"])
            for x in register_rows
        }
        if paired!=native_pairs or paired!=expected_pairs or len(original)!=count:
            raise ValueError("Original SHA-pinned Foam source t/s register slots changed")
        source_names = [x["_private_name"] for x in original]
        if len(set(source_names))!=count:
            raise ValueError("Original stage texture property names ambiguous")
        out.append({"pass":pi,"stage_code":stage,"_source_names":source_names,
                    "source_rows":count,
                    "source_names_in_authored_shader_texture_properties":
                        len(set(source_names)&textures),
                    "source_names_in_authored_non_texture_property_types":
                        len(set(source_names)&(all_props-textures)),
                    "source_texture_names_without_authored_texture_property":
                        len(set(source_names)-textures)})
    if seen!=set(STAGES) or sum(row["source_rows"] for row in out)!=6:
        raise ValueError("Original Foam source texture coverage incomplete")
    return {
        "_private_authored_textures":textures,
        "_private_all_authored_props":all_props,
        "_private_stage_rows":out,
        "original_authored_properties":len(all_props),
        "original_authored_texture_properties":len(textures),
        "original_source_texture_rows":6,
        "original_texture_name_to_shader_texture_property_matches":sum(
            x["source_names_in_authored_shader_texture_properties"] for x in out),
    }


def direct_material_target(tree, shader_path_id=OBJECT_ID):
    """Null, external or unrelated Shader pointer is NOT a local Foam match."""
    if not isinstance(tree,dict) or type(shader_path_id) is not int:
        raise ValueError("Original Material/shader target invalid")
    ptr=_original_pointer(tree.get("m_Shader"))
    return ptr==(0,shader_path_id)


def original_foam_material_links(material_trees, source_profile, local_types):
    """Read true original Material saved TexEnvs and typed local texture edges."""
    if (not isinstance(material_trees,list) or len(material_trees)>MAX_MATERIALS
            or not isinstance(source_profile,dict)
            or not isinstance(local_types,dict)):
        raise ValueError("Original Material scan input unbounded")
    original_names=source_profile.get("_private_authored_textures")
    stage_rows=source_profile.get("_private_stage_rows")
    if not isinstance(original_names,set) or not isinstance(stage_rows,list):
        raise ValueError("Source-authentic shader property evidence missing")
    counts={key:0 for key in (
        "original_materials_in_this_single_owner",
        "original_materials_directly_referencing_local_foam_shader",
        "original_foam_material_texenv_slots",
        "original_foam_material_texenvs_matching_authored_texture_properties",
        "original_foam_material_texenvs_matching_sampled_source_names",
        "original_foam_matched_texenvs_with_null_texture",
        "original_foam_matched_texenvs_with_local_typed_texture",
        "original_foam_matched_texenvs_with_external_texture_unresolved",
        "original_foam_matched_texenvs_with_uv_transform",
        "original_foam_materials_with_at_least_one_actual_sampled_texenv",
    )}
    private_sample_names=set().union(
        *(set(s["_source_names"]) for s in stage_rows))
    for tree in material_trees:
        counts["original_materials_in_this_single_owner"]+=1
        if not direct_material_target(tree):
            continue
        counts["original_materials_directly_referencing_local_foam_shader"]+=1
        props=tree.get("m_SavedProperties")
        if not isinstance(props,dict):
            raise ValueError("Original Foam Material saved properties absent")
        slots=normalize_texenvs(props.get("m_TexEnvs"))
        if len(slots)>MAX_TEXENVS:
            raise ValueError("Original Foam Material TexEnv count unbounded")
        counts["original_foam_material_texenv_slots"]+=len(slots)
        any_sampled=False
        for name,(pointer,uv) in slots.items():
            if name in original_names:
                counts["original_foam_material_texenvs_matching_authored_texture_properties"]+=1
            if name not in private_sample_names:
                continue
            any_sampled=True
            counts["original_foam_material_texenvs_matching_sampled_source_names"]+=1
            file_id,path_id=pointer
            if path_id==0 and file_id==0:
                counts["original_foam_matched_texenvs_with_null_texture"]+=1
            elif file_id==0:
                if local_types.get(path_id) not in ALLOWED_LOCAL_TEXTURE_CLASSES:
                    raise ValueError("Original local Material TexEnv source texture type unverified")
                counts["original_foam_matched_texenvs_with_local_typed_texture"]+=1
            else:
                counts["original_foam_matched_texenvs_with_external_texture_unresolved"]+=1
            if uv is not None:
                counts["original_foam_matched_texenvs_with_uv_transform"]+=1
        if any_sampled:
            counts["original_foam_materials_with_at_least_one_actual_sampled_texenv"]+=1
    if (sum(counts[key] for key in (
            "original_foam_matched_texenvs_with_null_texture",
            "original_foam_matched_texenvs_with_local_typed_texture",
            "original_foam_matched_texenvs_with_external_texture_unresolved"))
            != counts["original_foam_material_texenvs_matching_sampled_source_names"]):
        raise ValueError("Original Foam Material texture PPtr classification incomplete")
    return counts


def inspect_original(root):
    source=Path(root).absolute()
    path=source/OWNER
    if (not source.is_dir() or not _physical(source) or
            not path.is_file() or not _physical(path) or
            fingerprint(path)!=PINS[OWNER]):
        raise ValueError("Original Foam ZIP2 owner SHA/bytes unavailable")
    import UnityPy
    env=UnityPy.load(str(path))
    objects=env.file.objects
    hits=[o for o in objects.values()
          if o.type.name=="Shader" and int(o.path_id)==OBJECT_ID]
    if len(hits)!=1:
        raise ValueError("Foam original shader source missing/ambiguous")
    if hashlib.sha256(hits[0].get_raw_data()).hexdigest()!=ORIGINAL_OBJECT_SHA256:
        raise ValueError("Foam original Shader raw object fingerprint changed")
    tree=hits[0].read_typetree()
    parsed=tree.get("m_ParsedForm")
    profile=original_stage_shader_property_join(parsed)
    material_trees=[]
    local_types={int(o.path_id):o.type.name for o in objects.values()}
    for obj in objects.values():
        if obj.type.name!="Material":
            continue
        if len(material_trees)>=MAX_MATERIALS:
            raise ValueError("Original Foam Material source owner too large")
        material_trees.append(obj.read_typetree())
    matched=original_foam_material_links(material_trees,profile,local_types)
    source_rows=[
        {k:v for k,v in row.items() if not k.startswith("_")}
        for row in profile["_private_stage_rows"]]
    return {
        "status":"original_foam_authored_texture_properties_and_direct_material_texenvs_scoped",
        "original_owner_sha256":PINS[OWNER][1],
        "original_shader_raw_object_sha256":ORIGINAL_OBJECT_SHA256,
        "original_stage_DXBC_SHA_authenticated_by_previous_experiment":True,
        "original_stages":4,
        "original_source_texture_rows":profile["original_source_texture_rows"],
        "original_shader_authored_properties":profile["original_authored_properties"],
        "original_shader_authored_texture_properties":profile["original_authored_texture_properties"],
        "original_texture_name_to_shader_texture_property_matches":
            profile["original_texture_name_to_shader_texture_property_matches"],
        "stages":source_rows,
        **matched,
        "original_shader_property_name_link_verified":
            profile["original_texture_name_to_shader_texture_property_matches"]>0,
        "original_local_material_saved_texenv_link_verified":
            matched["original_foam_material_texenvs_matching_sampled_source_names"]>0,
        "original_all_game_material_providers_examined":False,
        "original_material_runtime_property_upload_verified":False,
        "original_sampler_textureimporter_wrap_filter_verified":False,
        "shaderlab_unity_import_or_adreno_pixels_verified":False,
        "private_shader_material_texture_names_ids_values_published":False,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    try:
        out=args.out.absolute()
        source=args.source.absolute()
        if (out.exists() or not out.parent.is_dir() or not _physical(out)
                or out.is_relative_to(source)):
            raise ValueError("Unsafe original Material aggregate report output")
        report=inspect_original(source)
        out.write_text(json.dumps(report,sort_keys=True)+"\n",encoding="utf-8")
        print("T2_FOAM_MATERIAL_PROPERTY "+json.dumps({
            "status":report["status"],
            "original_source_texture_rows":6,
            "matched_authored_texture_properties":
                report["original_texture_name_to_shader_texture_property_matches"],
            "direct_local_material_count":
                report["original_materials_directly_referencing_local_foam_shader"],
            "matched_material_texenvs":
                report["original_foam_material_texenvs_matching_sampled_source_names"],
            "unity_runtime_verified":False,
            "private_data_published":False,
        }))
        return 0
    except BaseException as ex:
        # Do not print private game names, paths, source data or UnityPy errors.
        print("T2_FOAM_MATERIAL_PROPERTY "+json.dumps({
            "status":"blocked","reason_class":type(ex).__name__,
            "source_to_material_upload_verified":False,"private_data_published":False,
        }))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
