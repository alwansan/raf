"""Read-only original Settings MonoBehaviour candidate pointer evidence.

Exact original non-LFS scenes/mono scripts and private original Settings.cs
SHA pin. Raw <i32 fileID,i64 pathID> byte matches are only CANDIDATES, never
typed Unity field references. Emit aggregates only, no proprietary byte data.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

from scripts.probe_a2_scene_ui_layout import SCENE_BLOBS, verified_scene, local_pptr
from scripts.probe_a2_canvas_scaler_monoscript import SCRIPT_SOURCE, ORIGINAL_SCRIPTS_BLOB, script_registry, resolve_script

SETTINGS_SHA = "904c52b337fe951f711e2efc15bfafc4fc77f2a8d2cc9c5bee2f7d14075103ad"
SETTINGS_CATEGORY = "matching_original_game_class_unverified_Settings"
SCALER_CATEGORY = "verified_unity_ui_canvas_scaler"
MAX_RECORD_BYTES = 1024 * 1024
MAX_MATCHES = 256


def source_pin(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe original CSharp root")
    files = list(root.rglob("Settings.cs"))
    if len(files) != 1:
        raise ValueError("Original Settings source missing or ambiguous")
    p = files[0]
    if p.is_symlink() or not p.is_file() or p.stat().st_size > 300000:
        raise ValueError("Unsafe original Settings source")
    code = p.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    if hashlib.sha256(code.encode()).hexdigest() != SETTINGS_SHA:
        raise ValueError("Original Settings SHA drift")
    return {"settings_cs_sha256": SETTINGS_SHA, "decompiled_source_emitted": False}


def scan_candidates(raw, available):
    if not isinstance(raw, bytes) or not 32 <= len(raw) <= MAX_RECORD_BYTES:
        raise ValueError("Unsafe original Settings record length")
    if len(available) > 50000:
        raise ValueError("Unbounded scene object inventory")
    matches = []
    for offset in range(32, len(raw) - 11, 4):
        fid, path_id = struct.unpack_from("<iq", raw, offset)
        if fid == 0 and path_id > 0 and path_id in available:
            matches.append((offset, path_id))
            if len(matches) > MAX_MATCHES:
                raise ValueError("Unbounded original raw PPtr matches")
    return matches



def strict_pointer_stride_shape(raw, candidates):
    """Verify 48 packed local PPtrs + 4 trailing bytes, not their CSharp field names."""
    if not isinstance(raw, bytes):
        raise ValueError("Expected original Settings raw bytes")
    if len(raw) != 612:
        return {"exact_48_pointer_stride": False,
                "record_length_612": False,
                "tail_is_bool_plus_zero_padding": False}
    expected = list(range(32, 32 + 48 * 12, 12))
    positions = sorted(i for i, _ in candidates)
    tail = raw[608:]
    return {
        "exact_48_pointer_stride": positions == expected,
        "pointer_stride_after_four_byte_prefix": positions == list(range(36, 36 + 48 * 12, 12)),
        "first_candidate_offset": positions[0] if positions else None,
        "last_candidate_offset": positions[-1] if positions else None,
        "candidate_delta_histogram": dict(sorted(Counter(b - a for a, b in zip(positions, positions[1:])).items())),
        "prefix_int32_equals_48": struct.unpack_from("<i", raw, 32)[0] == 48,
        "record_length_612": True,
        "tail_is_bool_plus_zero_padding": tail[0] in (0, 1)
                                      and tail[1:] == b"\x00\x00\x00",
        "tail_scalar_is_true": tail[0] == 1
                               if tail[1:] == b"\x00\x00\x00" else None,
        "source_declared_field_names_mapped": False,
        "array_or_field_boundary_proven": False,
    }


def native_graph(objects, externals, local_scripts, global_scripts):
    kinds, component_owner, transform_of_go, parent, canvases, scalers = {}, {}, {}, {}, set(), set()
    for obj in objects:
        kind, pid = str(obj.type.name), int(obj.path_id)
        if pid in kinds:
            raise ValueError("Duplicate source path ID")
        kinds[pid] = kind
        if kind not in ("RectTransform", "Transform", "Canvas", "MonoBehaviour"):
            continue
        tree = obj.read_typetree(check_read=False)
        if not isinstance(tree, dict):
            continue
        go = local_pptr(tree.get("m_GameObject"))
        if go is not None:
            component_owner[pid] = go
        if kind in ("RectTransform", "Transform"):
            if go is not None:
                transform_of_go[go] = pid if go not in transform_of_go else "ambiguous"
            father = tree.get("m_Father")
            if (isinstance(father, dict) and type(father.get("m_FileID")) is int
                    and type(father.get("m_PathID")) is int
                    and father["m_FileID"] == father["m_PathID"] == 0):
                parent[pid] = None
            else:
                parent[pid] = local_pptr(father) or "unknown"
        elif kind == "Canvas":
            if go is not None:
                canvases.add(go)
        elif kind == "MonoBehaviour" and go is not None:
            if resolve_script(tree.get("m_Script"), externals,
                              local_scripts, global_scripts) == SCALER_CATEGORY:
                scalers.add(go)
    return kinds, component_owner, transform_of_go, parent, canvases, scalers


def ancestry(pid, graph):
    kinds, owners, trans, parents, canvases, scalers = graph
    go = pid if kinds.get(pid) == "GameObject" else owners.get(pid)
    if go is None:
        return "target_has_no_native_gameobject_owner"
    tr = trans.get(go)
    if type(tr) is not int:
        return "target_transform_missing"
    visited = set()
    for _ in range(256):
        if tr in visited or tr not in parents:
            return "unknown_ancestry"
        visited.add(tr)
        owner = owners.get(tr)
        if owner is None:
            return "unknown_ancestry"
        if owner in scalers and owner in canvases:
            return "candidate_with_verified_scaler_ancestor"
        if owner in canvases:
            return "candidate_under_native_canvas_without_scaler_here"
        father = parents[tr]
        if father is None:
            return "candidate_with_no_native_canvas_ancestor_in_this_scene"
        if type(father) is not int:
            return "unknown_ancestry"
        tr = father
    return "unknown_ancestry"


def audit_scene(owner_file, global_scripts):
    objects = list(owner_file.objects.values())
    if len(objects) > 50000:
        raise ValueError("Unbounded original scene")
    externals = [e.path for e in owner_file.externals]
    local_scripts, _ = script_registry(objects)
    graph = native_graph(objects, externals, local_scripts, global_scripts)
    kinds, owners, trans, parents, canvases, scalers = graph
    settings, counts_by_kind, counts_by_ancestry, sizes = 0, Counter(), Counter(), Counter()
    stride_results = []
    for obj in objects:
        if str(obj.type.name) != "MonoBehaviour":
            continue
        base = obj.read_typetree(check_read=False)
        if resolve_script(base.get("m_Script"), externals, local_scripts,
                          global_scripts) != SETTINGS_CATEGORY:
            continue
        settings += 1
        raw = obj.get_raw_data()
        for pos, field in ((0, "m_GameObject"), (16, "m_Script")):
            expected = base.get(field)
            if (not isinstance(expected, dict)
                    or type(expected.get("m_FileID")) is not int
                    or type(expected.get("m_PathID")) is not int
                    or struct.unpack_from("<iq", raw, pos)
                       != (expected["m_FileID"], expected["m_PathID"])):
                raise ValueError("Typed original Settings base PPtr mismatch")
        sizes[len(raw)] += 1
        matches = scan_candidates(raw, kinds)
        stride_results.append(strict_pointer_stride_shape(raw, matches))
        for offset, target in matches:
            kind = kinds[target]
            counts_by_kind[kind if kind in ("GameObject", "RectTransform", "Transform", "Canvas", "MonoBehaviour") else "other"] += 1
            counts_by_ancestry[ancestry(target, graph)] += 1
    if settings != 1:
        raise ValueError("Expected one original Settings MonoBehaviour per scene")
    return {"settings_owner_count": settings,
            "raw_settings_record_size_histogram": dict(sorted(sizes.items())),
            "raw_local_pptr_candidate_count": sum(counts_by_kind.values()),
            "candidate_target_types": dict(sorted(counts_by_kind.items())),
            "candidate_native_ancestry": dict(sorted(counts_by_ancestry.items())),
            "authentic_scaler_canvas_owners": len(scalers & canvases),
            "full_uniform_48_local_pptrs_and_bool_tail": bool(stride_results) and
                all(v["exact_48_pointer_stride"] and
                    v["tail_is_bool_plus_zero_padding"] for v in stride_results),
            "dense_candidate_structural_profiles": stride_results,
            "candidate_custom_field_typing_verified": False,
            "displayed_settings_panel_to_canvas_proven": False}


def run(root, decompiled, loader=None):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe original scene directory")
    verified_scene(root / SCRIPT_SOURCE, ORIGINAL_SCRIPTS_BLOB)
    for name in ("level0", "level1"):
        verified_scene(root / name, SCENE_BLOBS[name])
    source = source_pin(decompiled)
    if loader is None:
        import UnityPy
        loader = lambda p: UnityPy.load(str(p))
    global_scripts, _ = script_registry(loader(root / SCRIPT_SOURCE).file.objects.values())
    scenes = {n: audit_scene(loader(root / n).file, global_scripts)
              for n in ("level0", "level1")}
    return {"original_source": source, "scenes": scenes,
            "source_scenes_verified": True, "candidate_links_are_typed_fields": False,
            "settings_aspect_cause_proven": False, "unity_or_android_ran": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--decompiled", type=Path, required=True)
    x = p.parse_args()
    print("RAFT_A2_SETTINGS_OWNER_LINKS " + json.dumps(run(x.source, x.decompiled), sort_keys=True))


if __name__ == "__main__":
    main()
