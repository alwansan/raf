#!/usr/bin/env python3
"""T3: classify missing source-linked TextureImporter GUIDs in a REAL export.

B15's strict original sampler checker rightfully refuses to compare settings
when the exported Texture2D GUID is not uniquely tied to TextureImporter
metadata. This diagnostic scans only on-run exported .meta FILES and reports
aggregate categories, never names, GUIDs, PathIDs, source assets or raw pixels.
A metadata-presence result is NOT source/importer sampler fidelity.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from scripts import t3_linked_texture_sampler_export as linked
from scripts import b05_verify_material_texenv_bindings as b05
from scripts.b03_original_renderer_materials import manifest_provider_basename_counts

GUID_LINE = re.compile(r"(?m)^guid:[ \t]*([0-9a-fA-F]{32})[ \t]*$")
IMPORTER_KIND = re.compile(r"(?m)^([A-Za-z_][A-Za-z0-9_]*Importer):[ \t]*(?:\{\})?[ \t]*$")
MAX_FILES = 150_000
MAX_META_BYTES = 256_000


def safe_kind(content: str) -> str:
    hits = IMPORTER_KIND.findall(content)
    if len(hits) != 1:
        return "invalid_or_ambiguous_importer"
    tag = hits[0]
    if tag == "TextureImporter":
        return "TextureImporter"
    if tag == "NativeFormatImporter":
        return "NativeFormatImporter"
    if tag == "DefaultImporter":
        return "DefaultImporter"
    if tag == "ScriptedImporter":
        return "ScriptedImporter"
    return "other_importer"


def inventory(assets: Path, trace: dict):
    """Scan verified same-instance GUID targets; classify, do not fabricate paths."""
    if (not assets.is_dir() or assets.is_symlink()
        or any(p.is_symlink() for p in assets.parents)):
        raise ValueError("untrusted_Unity_export_Assets_root")
    rows = trace.get("objects") if isinstance(trace,dict) else None
    if not isinstance(rows,list) or not rows:
        raise ValueError("no_original_selected_Texture2D_trace")
    targets=Counter()
    for row in rows:
        if not isinstance(row,dict) or row.get("class_id")!=28:
            raise ValueError("non_Texture2D_target_in_selected_trace")
        target=row.get("export")
        if (not isinstance(target,dict) or set(target)!={"file_id","guid","type"}
            or type(target["file_id"]) is not int or target["file_id"]<=0
            or type(target["type"]) is not int or target["type"] not in (2,3)
            or not isinstance(target["guid"],str)
            or not re.fullmatch("[0-9a-f]{32}",target["guid"])):
            raise ValueError("invalid_selected_source_exported_Texture2D_pointer")
        targets[target["guid"]]+=1
    files=sorted(assets.rglob("*"))
    if len(files)>MAX_FILES or any(p.is_symlink() for p in files):
        raise ValueError("unsafe_or_oversize_Unity_export_inventory")
    refs=defaultdict(list)
    for path in files:
        if not path.is_file() or path.suffix!=".meta":
            continue
        if path.stat().st_size>MAX_META_BYTES:
            raise ValueError("oversized_Unity_export_meta_candidate")
        text=path.read_text(encoding="utf-8-sig")
        found=GUID_LINE.findall(text)
        # Inspect target hints only. Other unrelated meta anomalies need not
        # invalidate the *selected* original Texture2D GUID classification.
        candidates={g.lower() for g in found if g.lower() in targets}
        for guid in candidates:
            rel=path.relative_to(assets).as_posix()
            corresponding=assets/rel[:-5]
            has_asset=corresponding.is_file() and not corresponding.is_symlink()
            refs[guid].append((safe_kind(text),has_asset,len(found)==1))
    counts=Counter()
    for guid, occurrences in targets.items():
        if occurrences>1:
            counts["source_Texture2D_objects_sharing_export_GUID"] += occurrences
        meta=refs.get(guid,[])
        if not meta:
            counts["export_target_GUID_absent_from_meta_files"]+=1
        elif len(meta)!=1:
            counts["multiple_meta_files_claim_same_GUID"]+=1
        else:
            kind, asset_exists, unambiguous = meta[0]
            if not unambiguous:
                counts["ambiguous_GUID_inside_target_meta"]+=1
            if not asset_exists:
                counts["target_meta_without_exported_asset"]+=1
            counts["found_"+kind]+=1
    countkeys=(
        "source_Texture2D_objects_sharing_export_GUID",
        "export_target_GUID_absent_from_meta_files",
        "multiple_meta_files_claim_same_GUID",
        "ambiguous_GUID_inside_target_meta",
        "target_meta_without_exported_asset",
        "found_TextureImporter",
        "found_NativeFormatImporter",
        "found_DefaultImporter",
        "found_ScriptedImporter",
        "found_other_importer",
        "found_invalid_or_ambiguous_importer",
    )
    return {
        "schema_version":1,
        "experiment":"T3-real-sameexport-linked-Texture2D-metadata-class",
        "selected_original_linked_Texture2D_trace_objects":len(rows),
        "distinct_exported_Texture2D_GUIDs":len(targets),
        "matched_meta_GUID_categories":{k:counts[k] for k in countkeys},
        "observed_exact_same_export_GUID_dataset":True,
        "original_sampler_sRGB_or_pixels_verified":False,
        "device_game_color_recovery_verified":False,
        "only_public_aggregate_categories":True,
        "status":"METADATA_PRESENCE_CLASSIFIED_NOT_IMPORTER_PARITY",
    }


def real(root:Path, manifest:Path, project:Path, w1path:Path, b02path:Path):
    import UnityPy
    source=b05.original_texenvs(root,owner_names={linked.OWNER})
    env=UnityPy.load(str(root/"Raft_Data"/linked.OWNER))
    external=[x.path for x in env.file.externals]
    ids,scope=linked.source_targets(source,external,manifest_provider_basename_counts(manifest))
    w1=json.loads(w1path.read_text(encoding="utf8"))
    b02=json.loads(b02path.read_text(encoding="utf8"))
    trace=linked.subset_same_export(ids,w1,b02)
    result=inventory(project/"Assets",trace)
    if result["selected_original_linked_Texture2D_trace_objects"]!=scope["unique_linked_source_Texture2D_candidates"]:
        raise ValueError("same_export_selected_source_Texture2D_coverage_mismatch")
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for k in ("original","project","manifest","w1-trace","b02-trace","out"):
        p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())
        or a.out.resolve().is_relative_to(a.project.resolve())):
        raise ValueError("report_inside_game_source_or_export_refused")
    try:
        data=real(a.original,a.manifest,a.project,a.w1_trace,a.b02_trace)
    except Exception as e:
        data={"schema_version":1,"experiment":"T3-real-sameexport-linked-Texture2D-metadata-class",
              "status":"INCONCLUSIVE","error_type":type(e).__name__,
              "device_game_color_recovery_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("T3_ORIGINAL_TEXTURE_IMPORTED_GUID_CLASSIFICATION "+json.dumps(data,sort_keys=True))
    return 0 if data["status"]=="METADATA_PRESENCE_CLASSIFIED_NOT_IMPORTER_PARITY" else 2


if __name__=="__main__": raise SystemExit(main())
