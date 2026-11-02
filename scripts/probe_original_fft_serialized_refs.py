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




def raw_tail_array_shape(raw, offsets):
    """Report byte-level tail hypotheses; never call them confirmed typed fields."""
    if not isinstance(raw, bytes):
        raise ValueError("Expected original serialized raw bytes")
    findings = []
    for at in offsets:
        if not 4 <= at <= len(raw) - 12:
            raise ValueError("Out-of-range raw PPtr offset")
        preceding = struct.unpack_from("<i", raw, at - 4)[0]
        at_end = at + 12 == len(raw)
        findings.append({
            "raw_pptr_offset": at,
            "preceding_four_bytes_as_int32": preceding,
            "pointer_at_end_of_object": at_end,
            "one_item_array_tail_shape_only": at_end and preceding == 1,
            "typed_array_field_verified": False,
        })
    return findings


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


def summarize_monobehaviour_script(partial, original_file, root=None):
    """Inspect exact MonoScript PPtr from partial head, no private type names."""
    import hashlib
    import re
    import UnityPy
    result = {"original_monobehaviour_script_link_verified": False,
              "original_monoscript_class_name_sha256": None,
              "class_or_namespace_mentions_water": False,
              "class_or_namespace_mentions_fft": False}
    if not isinstance(partial, dict):
        return result
    result["original_partial_head_field_keys"] = sorted(
        key for key in partial if isinstance(key, str) and key.startswith("m_")
    )[:32]
    script_ptr = partial.get("m_Script")
    result["original_script_pointer_key_present"] = isinstance(script_ptr, dict)
    if not isinstance(script_ptr, dict):
        return result
    file_id, path_id = script_ptr.get("m_FileID"), script_ptr.get("m_PathID")
    if type(file_id) is not int or type(path_id) is not int:
        return result
    result["original_script_pointer_file_id"] = file_id
    result["original_script_pointer_path_id"] = path_id
    owner = original_file
    if file_id != 0:
        result["original_script_pointer_external"] = True
        if not (1 <= file_id <= len(original_file.externals)):
            return result
        external_path = original_file.externals[file_id - 1].path
        if not isinstance(external_path, str):
            return result
        basename = external_path.replace("\\", "/").rsplit("/", 1)[-1]
        if not re.fullmatch(r"(?:globalgamemanagers(?:\.assets)?|sharedassets[0-9]+\.assets|resources\.assets)", basename):
            # Do not follow arbitrary archive paths or remote URLs.
            result["external_original_owner_unsupported"] = True
            return result
        result["external_original_owner_basename"] = basename
        if root is None:
            return result
        source = Path(root) / basename
        if source.is_symlink() or not source.is_file() or source.stat().st_size > 130_000_000:
            return result
        with source.open("rb") as stream:
            if stream.read(48).startswith(b"version https://git-lfs.github.com/spec/v1"):
                return result
        owner = UnityPy.load(str(source)).file
    script = owner.objects.get(path_id)
    if script is None or script.type.name != "MonoScript":
        return result
    tree = script.read_typetree()
    name = tree.get("m_ClassName")
    namespace = tree.get("m_Namespace", "")
    if not isinstance(name, str) or not name or len(name) > 256:
        return result
    if not isinstance(namespace, str) or len(namespace) > 256:
        return result
    full = namespace + "." + name
    result.update({
        "original_monobehaviour_script_link_verified": True,
        "original_monoscript_path_id": int(path_id),
        "original_monoscript_raw_sha256": hashlib.sha256(script.get_raw_data()).hexdigest(),
        "original_monoscript_class_name_sha256": hashlib.sha256(full.encode()).hexdigest(),
        "class_or_namespace_mentions_water": "water" in full.casefold(),
        "class_or_namespace_mentions_fft": "fft" in full.casefold(),
    })
    return result


def probe(root: Path):
    verify_sources(root)
    import UnityPy
    reports = []
    for owner, target in sorted(TARGETS.items()):
        env = UnityPy.load(str(root / owner))
        examined = 0
        raw_candidates = 0
        verified = []
        unreadable = []
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
            try:
                parsed = typed_reference_paths(obj.read_typetree(), target)
            except ValueError as error:
                # UnityPy may have a structurally incomplete MonoBehaviour type tree
                # even with the *correct* original bytes. Never count an unreadable
                # raw PPtr candidate as either a confirmed link or proven absence.
                if not ("Expected to read" in str(error) and "bytes" in str(error)):
                    raise
                if len(unreadable) >= MAX_MATCHES_PER_OWNER:
                    raise ValueError("Too many unparsed original PPtr candidates")
                partial = obj.read_typetree(check_read=False)
                # This is only the base MonoBehaviour head (often 56 bytes),
                # NOT proof that its remaining custom fields have typed links.
                mono_script = summarize_monobehaviour_script(partial, env.file, root)
                unreadable.append({"source_type": obj.type.name,
                                   "source_path_id": int(obj.path_id),
                                   "raw_pptr_pattern_count": len(offsets),
                                   "original_object_sha256": hashlib.sha256(data).hexdigest(),
                                   "possible_raw_pptr_offsets": offsets,
                                   "raw_tail_array_shape": raw_tail_array_shape(data, offsets),
                                   "typed_tree_parse_incomplete": True,
                                   "partial_monobehaviour_script": mono_script})
                continue
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
                        "unparsed_candidate_sources": unreadable,
                        "typed_reference_coverage_complete": not unreadable,
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
