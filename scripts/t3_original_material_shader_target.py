#!/usr/bin/env python3
"""T3 original SHA-authenticated 41 Material->Shader external fileID census.

Single original Material owner sharedassets6.assets. PPtrs use original
one-based externals. Unknown owner/PathID or builtin Unity engine references
cannot be renamed or treated as Shader objects without an authenticated
source owner. Safe aggregate only, no Material/Shader names or object IDs.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path,PurePosixPath

from scripts.b05_verify_material_texenv_bindings import B05_SMALL_OWNER_PINS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.b03_original_renderer_materials import manifest_provider_basename_counts
from scripts.t3_external_texture_export import owner_name

OWNER="sharedassets6.assets"
EXPECTED_MATERIALS=41
PIN=B05_SMALL_OWNER_PINS[OWNER]
ENGINE_BASES=frozenset(("unity_builtin_extra","unity default resources","unity_default_resources"))


def census(materials, external_table, manifest_counts):
    if not isinstance(materials,dict) or len(materials)!=EXPECTED_MATERIALS:
        raise ValueError("untrusted_original_41_materials")
    if not isinstance(external_table,list) or not isinstance(manifest_counts,dict):
        raise ValueError("invalid_original_dependency_table")
    counts=Counter()
    targets=defaultdict(set)
    for identity,ptr in materials.items():
        if (not isinstance(identity,tuple) or len(identity)!=2 or identity[0]!=OWNER
            or type(identity[1]) is not int or identity[1]<=0
            or not isinstance(ptr,dict) or set(ptr)!={"m_FileID","m_PathID"}):
            raise ValueError("untrusted_original_material_shader_record")
        fileid,pathid=ptr["m_FileID"],ptr["m_PathID"]
        if type(fileid) is not int or type(pathid) is not int or fileid<0 or pathid<0:
            raise ValueError("untrusted_original_material_shader_pptr")
        if pathid==0:
            if fileid:raise ValueError("invalid_source_null_shader_pptr")
            counts["original_null_shader"]+=1;continue
        counts["original_bound_shader"]+=1
        if fileid==0:
            owner=OWNER
            counts["original_local_shader"]+=1
        else:
            if fileid>len(external_table):raise ValueError("external_fileid_outside_authentic_source_table")
            owner=owner_name(external_table[fileid-1])
            counts["original_external_shader"]+=1
            if owner.lower() in ENGINE_BASES:
                counts["source_engine_resource_shader_refs"]+=1
        targets[owner].add(pathid)
        counts["owner_"+owner]+=1
        if owner.lower() not in ENGINE_BASES and manifest_counts.get(owner,0)!=1:
            counts["source_shader_owner_unlisted_or_ambiguous_in_manifest"]+=1
    if sum(counts[k] for k in ("original_null_shader","original_bound_shader"))!=EXPECTED_MATERIALS:
        raise ValueError("missing_original_shader_target_scope")
    per={owner:counts["owner_"+owner] for owner in sorted(targets)}
    return {"schema_version":1,"experiment":"T3-original-41-Material-Shader-typed-dependency",
            "original_materials":EXPECTED_MATERIALS,
            "shader_pointer_kind_counts":{k:counts[k] for k in (
                "original_null_shader","original_bound_shader","original_local_shader",
                "original_external_shader","source_engine_resource_shader_refs",
                "source_shader_owner_unlisted_or_ambiguous_in_manifest")},
            "original_shader_owner_link_occurrences":per,
            "original_shader_distinct_target_counts":{n:len(v) for n,v in sorted(targets.items())},
            "source_shader_pointer_values_or_shader_names_disclosed":False,
            "source_shader_owner_object_types_verified":False,
            "shader_export_identity_or_device_pixels_verified":False,
            "status":"SCOPED_SHA_AUTHENTIC_ORIGINAL_SHADER_DEPENDENCIES_ONLY"}


def real(root,manifest):
    import UnityPy
    path=root/"Raft_Data"/OWNER
    if (root.is_symlink() or path.is_symlink() or not path.is_file()
        or fingerprint(path)!=PIN):
        raise ValueError("unverified_selected_material_original_owner")
    env=UnityPy.load(str(path))
    source={}
    for obj in env.file.objects.values():
        if obj.type.name!="Material":continue
        key=(OWNER,obj.path_id)
        if key in source:raise ValueError("duplicate_original_material")
        original=obj.read_typetree()
        if "m_Shader" not in original:raise ValueError("missing_original_Material_shader")
        source[key]=original["m_Shader"]
    external=[r.path for r in env.file.externals]
    from scripts.b03_original_renderer_materials import manifest_provider_basename_counts
    return census(source,external,manifest_provider_basename_counts(manifest))


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original","manifest","out"):
        p.add_argument("--"+key,type=Path,required=True)
    a=p.parse_args(argv)
    if a.out.exists() or a.out.is_symlink() or a.out.resolve().is_relative_to(a.original.resolve()):
        raise ValueError("unsafe_original_or_exported_output")
    try:report=real(a.original,a.manifest)
    except Exception as e:
        report={"schema_version":1,"experiment":"T3-original-41-Material-Shader-typed-dependency",
                "status":"INCONCLUSIVE","exception_type":type(e).__name__,
                "shader_export_identity_or_device_pixels_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("T3_ORIGINAL_41_MATERIAL_SHADER_DEPENDENCIES "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]=="SCOPED_SHA_AUTHENTIC_ORIGINAL_SHADER_DEPENDENCIES_ONLY" else 2
if __name__=="__main__":raise SystemExit(main())
