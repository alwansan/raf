#!/usr/bin/env python3
"""T3: actual original linked Texture2D sampler -> Unity TextureImporter parity.

Select ONLY typed texture identities genuinely referenced by SHA-verified
sharedassets6 Material TexEnv PPtrs, including two authenticated external
provider files. Reuse B15's original/metadata verifier with a private B02
Texture2D28 same-export trace. No raw asset IDs, GUIDs or values published.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

from scripts import b15_texture_sampler_parity as b15
from scripts import b05_verify_material_texenv_bindings as b05
from scripts import t3_external_texture_lineage as dep
from scripts import t3_external_texture_export as linked
from scripts import t3_same_export_material_texenv as t3
from scripts.b03_original_renderer_materials import manifest_provider_basename_counts

OWNER = dep.SOURCE_OWNER
PINS = {"sharedassets6.assets", "sharedassets0.assets", "sharedassets1.assets"}
EXPECTED_BOUND = 114
EXPECTED_EXTERNAL = 25
FIELDS = tuple(field for field, _ in b15.FIELDS)


def source_targets(materials, external_paths, manifest):
    if not isinstance(materials, dict) or not isinstance(external_paths, list):
        raise ValueError("untrusted_original_texenv_source_shape")
    dep.dependencies(materials, external_paths, manifest)
    found=set()
    bound=local=external=0
    for mid, slots in materials.items():
        if not isinstance(mid,tuple) or mid[0]!=OWNER:
            raise ValueError("unexpected_original_material_owner")
        for slot in slots.values():
            (fid,pid),_uv=b05._slot(slot)
            if pid==0:
                if fid!=0: raise ValueError("invalid_null_texenv_source")
                continue
            bound+=1
            if fid==0:
                name=OWNER
                local+=1
            else:
                if fid>len(external_paths): raise ValueError("untrusted_original_external_index")
                name=linked.owner_name(external_paths[fid-1])
                external+=1
            if name not in PINS:
                raise ValueError("unexpected_cross_owner_Texture2D_target")
            if type(pid) is not int or pid<=0:
                raise ValueError("invalid_Texture2D_source_id")
            found.add((name,pid))
    if bound!=EXPECTED_BOUND or local!=89 or external!=EXPECTED_EXTERNAL:
        raise ValueError("material_source_bound_texture_counts_changed")
    return found,{"source_texenv_bound_occurrences":bound,
                  "original_local_texture_slots":local,
                  "original_external_texture_slots":external,
                  "unique_linked_source_Texture2D_candidates":len(found)}


def subset_same_export(source_set, w1, b02):
    if not isinstance(source_set,set) or not source_set:
        raise ValueError("empty_authenticated_texture_scope")
    t3.combine_same_export(w1,b02)
    chosen=[];seen=set()
    for row in b02["objects"]:
        src=row.get("source")
        if not isinstance(src,dict) or set(src)!={"owner","path_id"}:
            raise ValueError("malformed_private_Texture2D_source")
        owner=src["owner"]
        if not isinstance(owner,str) or not owner:
            raise ValueError("malformed_private_source_owner")
        name=linked.owner_name(owner)
        if (owner not in (name,"Raft_Data/"+name)):
            raise ValueError("unrecognized_untrusted_source_owner_path")
        key=(name,src["path_id"])
        if key not in source_set: continue
        if key in seen: raise ValueError("duplicated_target_source_texture_trace")
        seen.add(key)
        chosen.append(row)
    if seen!=source_set or len(chosen)!=len(source_set):
        raise ValueError("missing_exact_original_linked_Texture2D_trace")
    result={"schema_version":1,"export_instance":b02["export_instance"],
            "objects":chosen}
    b15.validate_export_pair(result,w1)
    return result


def output_aggregate(actual,counts):
    if not isinstance(actual,dict) or not actual.get("linked_textures_compared"):
        raise ValueError("no_original_TextureImporter_comparison")
    if type(actual["linked_textures_compared"]) is not int or actual["linked_textures_compared"]!=counts["unique_linked_source_Texture2D_candidates"]:
        raise ValueError("not_all_linked_Texture2D_importers_compared")
    mismatches=actual.get("field_mismatches")
    defaults=actual.get("unresolved_importer_defaults")
    if (not isinstance(mismatches,dict) or not isinstance(defaults,dict)
        or set(mismatches)!=set(FIELDS) or set(defaults)!=set(FIELDS)
        or any(type(v) is not int or v<0 for d in (mismatches,defaults) for v in d.values())):
        raise ValueError("unexpected_B15_sampler_verifier_report")
    totalbad=sum(mismatches.values());unknown=sum(defaults.values())
    return {
        "schema_version":1, "experiment":"T3-authentic-linked-original-TextureImporter-samplers",
        "original_source_commit":b15.ZIP2_COMMIT,
        **counts,
        "original_owner_byte_SHA_verified":3,
        "linked_TextureImporter_documents_compared":actual["linked_textures_compared"],
        "sampler_field_mismatches":dict(sorted(mismatches.items())),
        "unknown_importer_defaults":dict(sorted(defaults.items())),
        "sampler_fields_with_drift":totalbad,
        "unresolved_importer_default_fields":unknown,
        "single_observed_export_W1_B02_trace_pair":True,
        "original_pixel_content_or_device_shader_verified":False,
        "modifications_to_game_assets":0,
        "status":("SCOPED_SAMPLER_MISMATCH" if totalbad
            else "SCOPED_SAMPLER_DEFAULTS_UNRESOLVED" if unknown
            else "SCOPED_SAMPLER_FIELDS_MATCH"),
    }


# All exposed reasons are literal, reviewed source code's fixed error strings.
# Never copy an arbitrary third-party exception: it could contain game names,
# raw property values, original paths, or transient private export GUIDs.
SAFE_REASONS = frozenset((
    "no pinned Texture2D identities in exporter trace",
    "invalid same-instance exporter trace",
    "missing exact exported TextureImporter GUID target",
    "missing unique TextureImporter/GUID",
    "missing TextureImporter.textureSettings",
    "absent/ambiguous exported sampler field",
    "original sampler field missing",
    "original Texture2D has no sampler settings",
    "missing original Texture2D pathID",
    "missing unique original Texture2D identity",
    "original owner byte size mismatch",
    "original owner SHA256 mismatch",
    "ambiguous target export metadata GUID",
    "duplicate/wrong TextureImporter GUID mapping",
    "sampler enum must be integer",
    "non-finite sampler mip bias",
    "not Unity importer meta",
    "unexpected_selected_original_material_scope",
    "missing_exact_original_linked_Texture2D_trace",
    "unrecognized_untrusted_source_owner_path",
    "material_source_bound_texture_counts_changed",
    "not_all_linked_Texture2D_importers_compared",
))

class StageFailure(ValueError):
    def __init__(self, stage, original):
        super().__init__("source-to-importer-comparison-inconclusive")
        self.stage=stage
        self.category=type(original).__name__
        raw=str(original)
        self.reason=raw if raw in SAFE_REASONS else "unclassified_safe_reason"


def run(root:Path, manifest:Path, project:Path, w1path:Path, b02path:Path):
    stage="original_SHA_pinned_material_source"
    try:
        import UnityPy
        material=b05.original_texenvs(root,owner_names={OWNER})
        src=root/"Raft_Data"/OWNER
        env=UnityPy.load(str(src))
        paths=[x.path for x in env.file.externals]
        stage="original_dependency_and_linked_Texture2D_selection"
        source_set,counts=source_targets(material,paths,manifest_provider_basename_counts(manifest))
        stage="same_export_W1_B02_exact_target_trace_selection"
        w1=json.loads(w1path.read_text(encoding="utf8"))
        b02=json.loads(b02path.read_text(encoding="utf8"))
        trace=subset_same_export(source_set,w1,b02)
        stage="actual_TextureImporter_guid_asset_mapping"
        sidecar=b15.sidecar_from_export_trace(project,trace)
        stage="actual_original_Texture2D_sampler_importer_field_compare"
        # Under B15's original contract original_root is the directory holding
        # serialized owner .assets files, not the ZIP2 transport root.
        result=b15.inspect(root/"Raft_Data",project,sidecar)
        stage="safe_six_sampler_field_result"
        return output_aggregate(result,counts)
    except Exception as ex:
        raise StageFailure(stage,ex) from None


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original","manifest","project","w1-trace","b02-trace","out"):
        ap.add_argument("--"+key,required=True,type=Path)
    a=ap.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())
        or a.out.resolve().is_relative_to(a.project.resolve())):
        raise ValueError("public_aggregate_path_cannot_be_inside_original_assets")
    stage="original_source_and_trace"
    try:
        report=run(a.original,a.manifest,a.project,a.w1_trace,a.b02_trace)
    except StageFailure as ex:
        report={"schema_version":1,
                "experiment":"T3-authentic-linked-original-TextureImporter-samplers",
                "status":"INCONCLUSIVE","phase":ex.stage,"exception_type":ex.category,
                "safe_failure_reason":ex.reason,
                "original_sampler_or_phone_pixels_verified":False}
    except Exception as ex:
        report={"schema_version":1,
                "experiment":"T3-authentic-linked-original-TextureImporter-samplers",
                "status":"INCONCLUSIVE","phase":"unclassified","exception_type":type(ex).__name__,
                "original_sampler_or_phone_pixels_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("T3_LINKED_TEXTURE_IMPORTER_SAMPLER_PARITY "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]=="SCOPED_SAMPLER_FIELDS_MATCH" else 2


if __name__=="__main__": raise SystemExit(main())
