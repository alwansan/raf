"""T2 WATER-001: SHA-original four-owner Material.m_Shader PPtr graph.

Read only four immutable original Unity owner files. Output only bounded counts
and public provider tags, never private PPtr paths/GUIDs/names/asset bodies.
A serialized external filename + PathID is a *candidate* asset link, not proof
of Unity runtime dereferencing, original GUID identity, or Foam CB0 upload.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.w1_stage_zip2_owners import PINS, fingerprint, safe

FOAM_OWNER = "Raft_Data/sharedassets0.assets"
FOAM_PATHID = 2420
FOAM_RAW_SHA256 = "67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1"
OWNERS = tuple(PINS)
MAX_MATERIALS = 50000
MAX_SHADERS = 8192
MAX_EXTERNALS = 256
MAX_OBJECTS = 300000
OWNER_TAGS = {
    "Raft_Data/resources.assets": "resources",
    "Raft_Data/sharedassets0.assets": "sharedassets0",
    "Raft_Data/Resources/unity default resources": "unity_default_resources",
    "Raft_Data/Resources/unity_builtin_extra": "unity_builtin_extra",
}


def external_provider_key(path):
    """Private path to unique pinned filename, not a GUID authentication."""
    if not isinstance(path, str) or not 0 < len(path) <= 1024 or "\x00" in path:
        return None
    basename = path.replace("\\", "/").rsplit("/", 1)[-1].casefold()
    matched = [name for name in OWNERS
               if name.replace("\\", "/").rsplit("/", 1)[-1].casefold() == basename]
    return matched[0] if len(matched) == 1 else None


def classify_owner_graph(graph):
    """Bounded source-free-or-real catalog with no private data in result."""
    if not isinstance(graph, dict) or set(graph) != set(OWNERS):
        raise ValueError("owner_graph_complete_source_pins_required")
    for owner, item in graph.items():
        if not isinstance(item, dict) or set(item) != {
            "shaders", "materials", "unparsed", "externals", "object_count"
        }:
            raise ValueError("owner_graph_object_shape")
        shaders, materials, externals = (
            item["shaders"], item["materials"], item["externals"]
        )
        if (not isinstance(shaders, set) or not isinstance(materials, list)
                or not isinstance(externals, list) or
                len(shaders) > MAX_SHADERS or len(materials) > MAX_MATERIALS
                or len(externals) > MAX_EXTERNALS or
                type(item["unparsed"]) is not int or item["unparsed"] < 0 or
                type(item["object_count"]) is not int or
                not 0 <= item["object_count"] <= MAX_OBJECTS or
                len(shaders) + len(materials) > item["object_count"]):
            raise ValueError("owner_graph_counts_unbounded")
        if any(type(v) is not int or v <= 0 for v in shaders):
            raise ValueError("owner_graph_shader_pathid_invalid")
        if any(not isinstance(path, str) or len(path) > 1024 for path in externals):
            raise ValueError("owner_graph_external_path_shape")
    if FOAM_PATHID not in graph[FOAM_OWNER]["shaders"]:
        raise ValueError("pinned_original_Foam_shader_object_absent")

    results = []
    totals = {
        "material_objects_examined": 0,
        "material_pointer_unparsed": 0,
        "material_external_pointer_count": 0,
        "material_null_Shader_pointer_count": 0,
        "same_owner_Foam_shader_direct_refs": 0,
        "other_owner_local_same_PathID_not_Foam_count": 0,
        "external_basename_and_PathID_Foam_candidates": 0,
        "external_known_pinned_typed_Shader_PPtr_candidates": 0,
        "external_unresolved_or_unpinned_target_count": 0,
        "external_malformed_fileID_count": 0,
    }
    for owner in OWNERS:
        item = graph[owner]
        stats = {
            "owner_tag": OWNER_TAGS[owner],
            "shader_count": len(item["shaders"]),
            "material_count": len(item["materials"]),
            "material_unparsed": item["unparsed"],
            "external_table_entries": len(item["externals"]),
            "local_original_Foam_Shader_ref_count": 0,
            "foreign_local_same_PathID_not_Foam": 0,
            "external_original_Foam_basename_candidate": 0,
            "external_to_known_pinned_typed_Shader_candidate": 0,
            "external_unresolved_or_unpinned": 0,
        }
        if item["unparsed"] > len(item["materials"]):
            raise ValueError("owner_unparsed_materials_inconsistent")
        totals["material_objects_examined"] += len(item["materials"])
        totals["material_pointer_unparsed"] += item["unparsed"]
        for pointer in item["materials"]:
            if pointer is None:
                continue
            if (not isinstance(pointer, (list, tuple)) or len(pointer) != 2
                    or any(type(x) is not int for x in pointer) or
                    any(x < 0 for x in pointer)):
                raise ValueError("owner_pointer_not_guarded")
            file_id, path_id = pointer
            if path_id == 0:
                totals["material_null_Shader_pointer_count"] += 1
            elif file_id == 0:
                if path_id == FOAM_PATHID:
                    if owner == FOAM_OWNER:
                        stats["local_original_Foam_Shader_ref_count"] += 1
                        totals["same_owner_Foam_shader_direct_refs"] += 1
                    else:
                        stats["foreign_local_same_PathID_not_Foam"] += 1
                        totals["other_owner_local_same_PathID_not_Foam_count"] += 1
            else:
                totals["material_external_pointer_count"] += 1
                if file_id > len(item["externals"]):
                    totals["external_malformed_fileID_count"] += 1
                    stats["external_unresolved_or_unpinned"] += 1
                    totals["external_unresolved_or_unpinned_target_count"] += 1
                    continue
                # fileID is one-indexed for SerializedFile.externals. Never
                # treat same PathID in an arbitrary file as original Foam.
                candidate = external_provider_key(item["externals"][file_id - 1])
                if candidate is None:
                    stats["external_unresolved_or_unpinned"] += 1
                    totals["external_unresolved_or_unpinned_target_count"] += 1
                    continue
                if path_id in graph[candidate]["shaders"]:
                    stats["external_to_known_pinned_typed_Shader_candidate"] += 1
                    totals["external_known_pinned_typed_Shader_PPtr_candidates"] += 1
                if candidate == FOAM_OWNER and path_id == FOAM_PATHID:
                    stats["external_original_Foam_basename_candidate"] += 1
                    totals["external_basename_and_PathID_Foam_candidates"] += 1
        results.append(stats)
    if (totals["same_owner_Foam_shader_direct_refs"] !=
        next(r["local_original_Foam_Shader_ref_count"]
             for r in results if r["owner_tag"] == "sharedassets0")):
        raise ValueError("same_owner_Foam_link_inconsistent")
    if totals["material_external_pointer_count"] < (
        totals["external_known_pinned_typed_Shader_PPtr_candidates"] +
        totals["external_unresolved_or_unpinned_target_count"]):
        raise ValueError("owner_graph_resolution_counts_inconsistent")
    return {
        "status": "source_original_four_SHA_owner_external_Shader_PPtr_census",
        "original_pinned_owner_count": len(OWNERS),
        "foam_original_owner_pathid_object_authenticated": True,
        "per_owner_public_tags_only": results,
        **totals,
        "external_file_basename_is_actual_Shader_GUID_identity_verified": False,
        "material_PPtr_runtime_resolution_verified": False,
        "original_Foam_host_CB0_upload_verified": False,
        "Android_Adreno_water_pixels_verified": False,
        "private_external_paths_or_GUID_published": False,
    }


def load_pinned_owner_catalog(root):
    import UnityPy
    if not isinstance(root, Path) or not root.is_dir():
        raise ValueError("source_root_invalid")
    safe(root)
    graph = {}
    for owner in OWNERS:
        path = root / owner
        safe(path)
        if not path.is_file() or fingerprint(path) != PINS[owner]:
            raise ValueError("source_owner_size_SHA_mismatch")
        env = UnityPy.load(str(path))
        file = env.file
        objs = list(file.objects.values())
        if len(objs) > MAX_OBJECTS or len(file.externals) > MAX_EXTERNALS:
            raise ValueError("source_owner_object_or_external_table_unbounded")
        shaders = set()
        materials = []
        unparsed = 0
        for obj in objs:
            if obj.type.name == "Shader":
                if len(shaders) >= MAX_SHADERS:
                    raise ValueError("source_owner_Shader_objects_unbounded")
                path_id = int(obj.path_id)
                if path_id in shaders or path_id <= 0:
                    raise ValueError("source_owner_Shader_PathID_ambiguous")
                if owner == FOAM_OWNER and path_id == FOAM_PATHID:
                    if hashlib.sha256(obj.get_raw_data()).hexdigest() != FOAM_RAW_SHA256:
                        raise ValueError("original_Foam_Shader_object_SHA_mismatch")
                shaders.add(path_id)
            elif obj.type.name == "Material":
                if len(materials) >= MAX_MATERIALS:
                    raise ValueError("source_owner_Material_objects_unbounded")
                try:
                    tree = obj.read_typetree()
                    ptr = tree["m_Shader"]
                    a, b = ptr["m_FileID"], ptr["m_PathID"]
                    if type(a) is not int or type(b) is not int or a < 0 or b < 0:
                        raise ValueError("invalid_internal_PPtr")
                    materials.append((a, b))
                except Exception:
                    materials.append(None)
                    unparsed += 1
        # External paths are private source data; kept only in local graph.
        externals = [x.path for x in file.externals]
        graph[owner] = {
            "shaders": shaders, "materials": materials,
            "unparsed": unparsed, "externals": externals,
            "object_count": len(objs),
        }
        del env
    return classify_owner_graph(graph)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    import os
    root, out = a.source.absolute(), a.out.absolute()
    status, phase = 0, "input_guard"
    try:
        safe(out)
        if (not out.parent.is_dir() or out.exists() or
                out.is_relative_to(root) or not root.is_dir()):
            raise ValueError("unsafe_source_or_output")
        phase = "original_sha_and_external_file_graph"
        result = load_pinned_owner_catalog(root)
        phase = "safe_result_write"
        out.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf8")
        print("T2_FOAM_FOUR_OWNER_PPTR_SAFE " + json.dumps(result, sort_keys=True))
    except BaseException:
        # Privacy: never expose original Unity names, GUID, paths, exception
        # message or tracebacks; no raw data or private scratch artifacts.
        print("T2_FOAM_FOUR_OWNER_PPTR_SAFE " + json.dumps({
            "status": "source_original_graph_blocked",
            "safe_phase": phase,
            "private_source_data_disclosed": False,
        }, sort_keys=True))
        status = 2
    return status


if __name__ == "__main__":
    raise SystemExit(main())
