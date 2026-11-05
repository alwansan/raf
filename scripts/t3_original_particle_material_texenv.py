#!/usr/bin/env python3
"""T3: exact original 108-use ParticleShader48 Material21 TexEnv source census.

Six immutable ZIP2 scenes and four SHA-verified original owners establish the
private shader->Renderer->Material scope; B05's strict original TexEnv parser
then classifies texture PPtr shape/UV. No names, IDs, property labels, source
bytecode, texture bytes or private owner pointers are printed or written.
Source pointer coverage is NOT native export texture/alpha/pixel evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from scripts import t3_original_renderer_shader_impact as source
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs
from scripts.w1_probe_original_shader_links import resolve_pointer
from scripts.w1_stage_zip2_owners import fingerprint

EXPECTED_RANKS=[108,34,34,20,16,3]
STATUS="SHA_ORIGINAL_PARTICLE_108_MATERIAL_TEXENV_SOURCE_BOUND_VERIFIED"


def census(materials:dict, expected_keys:set, *, renderer_slots:int=108):
    """Pure source object census; material data stays in private caller memory.

    materials maps original private (owner, pathID) -> (B05 normalized TexEnvs,
    original external owner count). Never expose the input in result or logs.
    """
    if (type(materials) is not dict or type(expected_keys) is not set
        or not expected_keys or set(materials)!=expected_keys
        or type(renderer_slots) is not int or renderer_slots<len(expected_keys)):
        raise ValueError("incomplete_exact_particle_material_source_scope")
    stats=Counter()
    texture_targets=set()
    for key,row in materials.items():
        if (type(key) is not tuple or len(key)!=2
            or key[0] not in source.MATERIAL_OWNERS
            or type(key[1]) is not int or key[1]<=0
            or type(row) is not tuple or len(row)!=2
            or type(row[0]) is not dict
            or type(row[1]) is not int or row[1]<0):
            raise ValueError("invalid_original_particle_material_row")
        texenvs,external_count=row
        stats["original_particle_material_objects"]+=1
        if not texenvs:
            stats["original_particle_materials_with_no_texenv_slots"]+=1
        any_bound=False
        for label,entry in texenvs.items():
            if (type(label) is not str or not label
                or type(entry) is not tuple or len(entry)!=2):
                raise ValueError("invalid_original_particle_texture_slot_record")
            ptr,uv=entry
            if (type(ptr) is not tuple or len(ptr)!=2
                or type(ptr[0]) is not int or type(ptr[1]) is not int
                or ptr[0]<0 or ptr[0]>external_count or ptr[1]<0
                or (ptr[1]==0 and ptr[0]!=0)):
                raise ValueError("invalid_original_particle_texture_pointer")
            fid,pid=ptr
            stats["original_particle_texenv_slots"]+=1
            if pid==0:
                stats["original_particle_texenv_null_texture_slots"]+=1
            elif fid==0:
                stats["original_particle_texenv_local_texture_pointers"]+=1
                texture_targets.add((key[0],fid,pid))
                any_bound=True
            else:
                stats["original_particle_texenv_external_texture_pointers"]+=1
                texture_targets.add((key[0],fid,pid))
                any_bound=True
            if uv is None:
                stats["original_particle_texenv_uv_unrecorded"]+=1
            elif (type(uv) is not tuple or len(uv)!=4
                  or any(type(n) is not float or n!=n or n in (float("inf"),-float("inf"))
                         for n in uv)):
                raise ValueError("invalid_original_particle_texenv_uv")
            else:
                stats["original_particle_texenv_uv_complete"]+=1
        if any_bound:
            stats["original_particle_material_objects_with_bound_textures"]+=1
    if (stats["original_particle_texenv_slots"]!=sum(stats[k] for k in (
        "original_particle_texenv_null_texture_slots",
        "original_particle_texenv_local_texture_pointers",
        "original_particle_texenv_external_texture_pointers"))
        or stats["original_particle_texenv_slots"]!=(
            stats["original_particle_texenv_uv_unrecorded"]+
            stats["original_particle_texenv_uv_complete"])):
        raise ValueError("original_particle_material_TexEnv_accounting_mismatch")
    return {
        "schema_version":1,"status":STATUS,
        "original_particle_renderer_material_slot_references":renderer_slots,
        **{k:stats[k] for k in (
            "original_particle_material_objects",
            "original_particle_materials_with_no_texenv_slots",
            "original_particle_material_objects_with_bound_textures",
            "original_particle_texenv_slots",
            "original_particle_texenv_null_texture_slots",
            "original_particle_texenv_local_texture_pointers",
            "original_particle_texenv_external_texture_pointers",
            "original_particle_texenv_uv_unrecorded",
            "original_particle_texenv_uv_complete")},
        "original_particle_distinct_texture_PPtr_shapes_in_material_owners":len(texture_targets),
        "bound_Texture2D_asset_type_or_payload_verified":False,
        "same_instance_export_or_Android_device_texture_binding_verified":False,
        "private_original_Shader_and_material_names_PathIDs_or_labels_disclosed":False,
    }


def run(original:Path, manifest:Path):
    import UnityPy
    private_counts={}
    private_materials={}
    original_report=source.load_original(
        original,manifest,private_particle_slot_counts=private_counts,
        private_particle_materials=private_materials)
    if (original_report.get("status")!=source.STATUS
        or original_report.get("six_original_scenes_sha_verified") is not True
        or original_report.get("original_particle_Shader48_ranked_material_slot_use_no_identity")!=EXPECTED_RANKS
        or original_report.get("original_particle_highest_Shader48_unique") is not True
        or original_report.get("original_particle_highest_Shader48_nonparticle_renderer_slots")!=0
        or sorted(private_counts.values(),reverse=True)!=EXPECTED_RANKS
        or set(private_materials)!=set(private_counts)):
        raise ValueError("untrusted_real_original_particle_material_scope")
    keys=[key for key,uses in private_counts.items() if uses==108]
    if len(keys)!=1:
        raise ValueError("ambiguous_108_original_particle_shader_identity")
    target=keys[0]
    selected=private_materials[target]
    if not selected:
        raise ValueError("no_original_Material21_for_108_particle_Shader48")
    grouped={}
    for owner,pid in selected:
        if owner not in source.MATERIAL_OWNERS:
            raise ValueError("unexpected_original_particle_Material_owner")
        grouped.setdefault(owner,set()).add(pid)
    rows={}
    for owner,expected in grouped.items():
        path=original/"Raft_Data"/owner
        if path.is_symlink() or fingerprint(path)!=SHADER_OWNERS[owner]:
            raise ValueError("original_particle_Material_owner_modified")
        file=UnityPy.load(str(path)).file
        external=[x.path for x in file.externals]
        for obj in file.objects.values():
            if obj.path_id not in expected:continue
            identity=(owner,obj.path_id)
            if (obj.type.name!="Material" or identity in rows
                or identity not in selected):
                raise ValueError("original_particle_Material_class_identity_mismatch")
            tree=obj.read_typetree()
            if resolve_pointer(owner,external,tree.get("m_Shader"))!=target:
                raise ValueError("original_particle_Material_shader_source_pointer_changed")
            saved=tree.get("m_SavedProperties")
            if not isinstance(saved,dict) or "m_TexEnvs" not in saved:
                raise ValueError("original_particle_Material_missing_TexEnvs")
            rows[identity]=(normalize_texenvs(saved["m_TexEnvs"],exported=False),
                            len(external))
    out=census(rows,selected)
    out["six_original_scene_SHA_verified"]=True
    out["four_original_shader_Material_owner_SHA_verified"]=True
    out["original_108_use_ParticleShader48_reference_authenticated"]=True
    return out


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for flag in ("original","manifest","out"):
        p.add_argument("--"+flag,required=True,type=Path)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_original_particle_texture_report_path")
    try:
        result=run(a.original,a.manifest)
    except Exception as exc:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "same_instance_export_or_Android_device_texture_binding_verified":False,
                "private_original_Shader_and_material_names_PathIDs_or_labels_disclosed":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("T3_ORIGINAL_PARTICLE108_MATERIAL_TEXENV "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
