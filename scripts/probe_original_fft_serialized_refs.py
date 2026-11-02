"""Bounded original Unity PPtr-link search for authenticated FFT candidate owners.

Search only serialized script/material references in the original owner files;
a raw byte match is NOT proof of a Unity pointer, so require parsed PPtr fields.
No shader sources, game logic, object names, or bytecode emitted. No Unity.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import struct
from scripts.verify_targeted_lfs_compute_sources import verify_sources

TARGETS = {"sharedassets0.assets": 2456, "resources.assets": 905}
SOURCE_TYPES = {"MonoBehaviour", "Material", "Shader", "GameObject", "ScriptableObject"}
MAX_SOURCE_OBJECTS = 100_000
MAX_RAW_OBJECT_BYTES = 4 * 1024 * 1024
MAX_TREE_NODES = 40_000
MAX_MATCHES_PER_OWNER = 24


def candidate_offsets(raw: bytes, target: int):
    """Find possible local PPtr<ComputeShader>: LE i32 fileID=0, i64 pathID."""
    if not isinstance(raw, bytes) or len(raw) > MAX_RAW_OBJECT_BYTES:
        raise ValueError("Original object exceeds bounded PPtr scan limit")
    needle = struct.pack("<iq", 0, target)
    start = 0
    offsets = []
    while True:
        offset = raw.find(needle, start)
        if offset < 0:
            break
        if len(offsets) >= MAX_MATCHES_PER_OWNER:
            raise ValueError("Too many possible local PPtr byte patterns")
        offsets.append(offset)
        start = offset + 1
    return offsets


def typed_reference_paths(tree, target):
    """Return only structural field paths containing a typed 0/target PPtr."""
    matches = []
    nodes = 0
    stack = [(tree, "$", 0)]
    while stack:
        current, path, depth = stack.pop()
        nodes += 1
        if nodes > MAX_TREE_NODES or depth > 18:
            raise ValueError("Unbounded original Unity typed PPtr tree")
        if isinstance(current, dict):
            if (type(current.get("m_FileID")) is int
                    and type(current.get("m_PathID")) is int
                    and current["m_FileID"] == 0
                    and current["m_PathID"] == target):
                matches.append(path)
                if len(matches) > MAX_MATCHES_PER_OWNER:
                    raise ValueError("Too many typed PPtr matches")
            for key, child in current.items():
                if isinstance(child, (list, dict)):
                    if not isinstance(key, str) or len(key) > 100:
                        raise ValueError("Unsafe serialized field name")
                    stack.append((child, path + "/" + key, depth + 1))
        elif isinstance(current, list):
            if len(current) > MAX_TREE_NODES:
                raise ValueError("Serialized list exceeds PPtr scan limit")
            for child in current:
                if isinstance(child, (dict, list)):
                    stack.append((child, path + "[]", depth + 1))
    return matches


def probe(root: Path):
    verify_sources(root)
    import UnityPy
    reports = []
    for owner, target in sorted(TARGETS.items()):
        env = UnityPy.load(str(root / owner))
        examined = 0
        raw_candidates = 0
        verified = []
        types = Counter()
        objects = env.file.objects.values()
        for obj in objects:
            if obj.type.name not in SOURCE_TYPES:
                continue
            examined += 1
            if examined > MAX_SOURCE_OBJECTS:
                raise ValueError("Too many source objects in local PPtr scan")
            if getattr(obj, "byte_size", 0) > MAX_RAW_OBJECT_BYTES:
                continue
            data = obj.get_raw_data()
            if len(data) > MAX_RAW_OBJECT_BYTES:
                continue
            offsets = candidate_offsets(data, target)
            if not offsets:
                continue
            raw_candidates += 1
            parsed = typed_reference_paths(obj.read_typetree(), target)
            if parsed:
                if len(verified) >= MAX_MATCHES_PER_OWNER:
                    raise ValueError("Exceeded original typed link report scope")
                types[obj.type.name] += 1
                # Only structural paths, no program data or object names.
                verified.append({"source_type": obj.type.name,
                                 "source_path_id": int(obj.path_id),
                                 "typed_field_paths": sorted(set(parsed))})
        reports.append({"original_owner": owner, "original_compute_path_id": target,
                        "examined_source_objects": examined,
                        "raw_candidate_source_objects": raw_candidates,
                        "verified_local_typed_pptr_sources": verified,
                        "verified_source_types": dict(sorted(types.items())),
                        "nonlocal_or_dynamic_references_examined": False})
    return {"targets": reports, "same_file_typed_references_only": True,
            "runtime_fft_owner_confirmed": False,
            "game_sources_modified": False, "android_gpu_tested": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    print("RAFT_AUTHENTIC_FFT_PPTR_LINKS " + json.dumps(probe(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
