"""Read-only summary of original serialized ComputeShader metadata.

Run only with privately hydrated, SHA-verified, original Unity 2021 sources.
Print no compiled bytecode, decompiled shader text or serialized tree payload.
Original sources and .meta remain untouched. This is a preparation diagnostic;
it does NOT recover Android-compatible compute program source.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from scripts.mesh_source_files import serialized_sources, owned_objects

MAX_OBJECTS = 64
MAX_NODES = 100_000
MAX_DEPTH = 12
MAX_SCALARS = 128
INTERESTING = re.compile(r"kernel|platform|variant|program|compiled", re.I)


def summarize_tree(tree):
    if not isinstance(tree, dict):
        raise ValueError("Original compute shader type tree is not a dictionary")
    seen = 0
    nodes = Counter()
    list_lengths = Counter()
    platform_codes = Counter()
    paths = set()
    stack = [(tree, "", 0)]
    while stack:
        value, trail, depth = stack.pop()
        seen += 1
        if seen > MAX_NODES:
            raise ValueError("Original compute metadata exceeds bounded read scope")
        if isinstance(value, (dict, list)) and depth > MAX_DEPTH:
            raise ValueError("Compute metadata exceeds safe nesting depth")
        if isinstance(value, dict):
            for key, child in value.items():
                if not isinstance(key, str) or len(key) > MAX_SCALARS:
                    raise ValueError("Unusual original compute metadata key")
                next_trail = (trail + "/" + key) if trail else key
                # Print only canonical metadata field names and list lengths.
                # In particular, never emit actual program bytes or name values.
                if INTERESTING.search(key):
                    nodes[key] += 1
                    paths.add(next_trail)
                    if isinstance(child, list):
                        list_lengths[key] += len(child)
                        if key.lower() in ("m_platforms", "platforms") and all(
                                type(item) is int and 0 <= item <= 4096 for item in child):
                            # Do not interpret unknown Unity backend enums as
                            # Android compatibility without independent proof.
                            platform_codes.update(child)
                if isinstance(child, (dict, list)):
                    if depth >= MAX_DEPTH:
                        raise ValueError("Compute metadata exceeds safe nesting depth")
                    stack.append((child, next_trail, depth + 1))
            continue
        if isinstance(value, list):
            # Do not walk binary byte arrays or individually traverse very
            # large backend program arrays; their byte contents are private.
            if len(value) > MAX_NODES:
                raise ValueError("Suspicious original compute array length")
            for entry in reversed(value):
                if isinstance(entry, (dict, list)):
                    stack.append((entry, trail + "[]", depth + 1))
    return {
        "metadata_fields": dict(sorted(nodes.items())),
        "metadata_array_totals": dict(sorted(list_lengths.items())),
        "original_platform_numeric_codes": dict(sorted(platform_codes.items())),
        "platform_code_meanings_verified": False,
        "metadata_field_paths": sorted(paths)[:MAX_SCALARS],
        "field_paths_truncated": len(paths) > MAX_SCALARS,
        "node_count": seen,
        "private_shader_programs_emitted": False,
    }


def inspect(root: Path, *, expected_objects=9):
    if not root.is_dir():
        raise ValueError("Original Unity source directory absent")
    import UnityPy
    objects = []
    for source in serialized_sources(root):
        if source.is_symlink() or not source.is_file():
            raise ValueError("Unsafe original Unity source path")
        with source.open("rb") as stream:
            if stream.read(48).startswith(b"version https://git-lfs.github.com/spec/v1"):
                raise ValueError("Original Unity source is only a Git LFS pointer: " + source.name)
        env = UnityPy.load(str(source))
        for obj in owned_objects(env):
            if obj.type.name != "ComputeShader":
                continue
            if len(objects) >= MAX_OBJECTS:
                raise ValueError("Original compute object inventory unexpectedly large")
            tree = obj.read_typetree()
            objects.append({
                "owner": source.name,
                "object_path_id": int(obj.path_id),
                "original_object_sha256": hashlib.sha256(obj.get_raw_data()).hexdigest(),
                "metadata": summarize_tree(tree),
            })
    if len(objects) != expected_objects:
        raise ValueError("Expected " + str(expected_objects) + " original compute objects; saw " + str(len(objects)))
    if len({(o["owner"], o["object_path_id"]) for o in objects}) != len(objects):
        raise ValueError("Duplicate original compute object identity")
    return {
        "compute_objects": objects,
        "original_objects": len(objects),
        "source_mutated": False,
        "decoded_compute_sources": 0,
        "android_compute_runtime_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--expected-objects", type=int, default=9)
    args = parser.parse_args()
    if args.expected_objects < 1 or args.expected_objects > MAX_OBJECTS:
        raise ValueError("Invalid expected compute object count")
    result = inspect(args.source, expected_objects=args.expected_objects)
    print("RAFT_ORIGINAL_COMPUTE_METADATA " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
