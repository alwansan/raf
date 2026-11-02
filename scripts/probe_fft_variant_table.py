"""Read original compute variant structure without leaking names or DXBC.

A compiled variant entry is not necessarily a user addressable Unity kernel.
Read after authenticating the exact original LFS serialized owner/object SHA.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.verify_targeted_lfs_compute_sources import verify_sources, EXPECTED
from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS,
)

MAX_VARIANTS = 12
MAX_KERNELS = 128


def summarize_variant_tree(tree, expected_kernels=EXPECTED_CONTAINERS):
    if not isinstance(tree, dict):
        raise ValueError("Original compute type tree absent")
    variants = tree.get("variants")
    if not isinstance(variants, list) or not 0 < len(variants) <= MAX_VARIANTS:
        raise ValueError("Unexpected serialized compute variants")
    results = []
    total = 0
    for variant_idx, variant in enumerate(variants):
        if not isinstance(variant, dict):
            raise ValueError("Unexpected serialized compute variant")
        kernels = variant.get("kernels")
        if not isinstance(kernels, list) or len(kernels) > MAX_KERNELS:
            raise ValueError("Missing or excessive original compiled kernel entries")
        name_hashes = []
        maps = []
        schemas = set()
        for k in kernels:
            if not isinstance(k, dict):
                raise ValueError("Malformed serialized kernel entry")
            schema = tuple(sorted(k.keys()))
            if any(not isinstance(key, str) or len(key) > 90 for key in schema):
                raise ValueError("Unsafe original kernel field key")
            schemas.add(schema)
            original_name = k.get("name")
            if not isinstance(original_name, str) or not 0 < len(original_name) <= 256:
                raise ValueError("Original compiled kernel entry lacks name")
            name_hashes.append(hashlib.sha256(original_name.encode()).hexdigest())
            variant_map = k.get("variantMap")
            if not isinstance(variant_map, list) or len(variant_map) > 64:
                raise ValueError("Original kernel variant map invalid")
            maps.append({
                "variant_map_entries": len(variant_map),
                "variant_map_schema_types": sorted(set(type(item).__name__ for item in variant_map)),
                "variant_map_sha256": hashlib.sha256(repr(variant_map).encode()).hexdigest(),
            })
        total += len(kernels)
        results.append({
            "original_variant_position": variant_idx,
            "compiled_entry_count": len(kernels),
            "unique_compiled_kernel_name_hashes": len(set(name_hashes)),
            "serialized_kernel_names_sha256_by_entry": name_hashes,
            "original_compiled_kernel_entry_field_keys": sorted(set(key for s in schemas for key in s)),
            "kernel_entry_schema_count": len(schemas),
            "variant_map_by_compiled_entry": maps,
            "unique_variant_map_digests": len(set(x["variant_map_sha256"] for x in maps)),
            "runtime_kernels_from_compiled_entry_count_verified": False,
        })
    if total != expected_kernels:
        raise ValueError("Original compiled entry count changed from pinned object")
    return {
        "original_serialized_variant_sets": len(variants),
        "original_compiled_entries": total,
        "variants": results,
        "original_kernel_lookup_index_order_verified": False,
        "android_gpu_execution_verified": False,
        "original_names_or_bytecode_published": False,
    }


def inspect(root: Path):
    verify_sources(root, expected={OWNER: EXPECTED[OWNER]})
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    items = [obj for obj in env.file.objects.values()
             if obj.type.name == "ComputeShader" and int(obj.path_id) == PATH_ID]
    if len(items) != 1:
        raise ValueError("Authentic original FFT ComputeShader absent")
    obj = items[0]
    if hashlib.sha256(obj.get_raw_data()).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Authentic original FFT ComputeShader SHA mismatch")
    return summarize_variant_tree(obj.read_typetree())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    args = p.parse_args()
    print("RAFT_ORIGINAL_FFT_SERIALIZED_VARIANT_LAYOUT " + json.dumps(
        inspect(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
