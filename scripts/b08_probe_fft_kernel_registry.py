"""Authenticated original FFT ComputeShader kernel *name* registry alias proof.

Original serialized compiled entries are not necessarily Unity runtime kernels.
Report only name multiplicities and slot aliases; no shader names, bytes or
native runtime kernel mapping are asserted or disclosed.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

# Synthetic checks do not import private providers/UnityPy.
EXPECTED_COMPILED_ENTRIES = 20
MAX_VARIANTS = 4
MAX_COMPILED_ENTRIES = 128
MAX_NAME_LENGTH = 256


def summarize_kernel_registry(tree, expected_entries=EXPECTED_COMPILED_ENTRIES):
    if not isinstance(tree, dict):
        raise ValueError('ComputeShader serialized type tree must be a dict')
    variants = tree.get('variants')
    if not isinstance(variants, list) or not 0 < len(variants) <= MAX_VARIANTS:
        raise ValueError('Original ComputeShader variants absent or unbounded')
    names, positions, lengths = [], {}, []
    total = 0
    for variant in variants:
        if not isinstance(variant, dict):
            raise ValueError('Invalid original serialized compute variant')
        entries = variant.get('kernels')
        if not isinstance(entries, list) or len(entries) > MAX_COMPILED_ENTRIES:
            raise ValueError('Invalid compiled kernel entries')
        lengths.append(len(entries))
        for row in entries:
            if not isinstance(row, dict):
                raise ValueError('Invalid compiled kernel record')
            name = row.get('name')
            if not isinstance(name, str) or not (0 < len(name) <= MAX_NAME_LENGTH):
                raise ValueError('Missing or unsafe original compiled kernel name')
            if any(not isinstance(row.get(k), list) or len(row[k]) > 64
                   for k in ('globalKeywords', 'localKeywords')):
                raise ValueError('Original keyword bundle missing or unbounded')
            mapping = row.get('variantMap')
            if not isinstance(mapping, list) or len(mapping) != 1:
                raise ValueError('Original compiled kernel variant map not singular')
            digest = hashlib.sha256(name.encode('utf-8')).hexdigest()
            positions.setdefault(digest, []).append(total)
            names.append(digest)
            total += 1
            if total > MAX_COMPILED_ENTRIES:
                raise ValueError('Compiled kernel entries unbounded')
    if total != expected_entries:
        raise ValueError('Serialized compiled kernel count changed')
    counts = Counter(names)
    aliases = sorted((len(v) for v in positions.values()), reverse=True)
    alias_positions = sorted((v for v in positions.values() if len(v) > 1),
                             key=lambda a: a[0])
    return {
        'serialized_variant_sets': len(variants),
        'compiled_entries_per_variant': lengths,
        'authenticated_compiled_entry_count': total,
        'distinct_original_compiled_kernel_names': len(counts),
        'kernel_name_alias_group_sizes': aliases,
        'aliased_compiled_positions': alias_positions,
        'all_compiled_names_unique': len(counts) == total,
        'compiled_entry_count_is_runtime_kernel_count': False,
        'compiled_entry_position_is_runtime_kernel_id': False,
        'unity_findkernel_name_to_runtime_id_verified': False,
        'unity_runtime_kernel_id_to_program_verified': False,
        'private_names_or_shader_programs_disclosed': False,
    }


def verify_registry_with_compiled_report(registry, compiled):
    if (not isinstance(compiled, dict)
            or compiled.get('original_compiled_program_order_sha256_correlated') is not True
            or compiled.get('authentic_compiled_variants_verified_in_original_order') != EXPECTED_COMPILED_ENTRIES
            or compiled.get('unity_runtime_kernel_index_mapping_verified') is not False):
        raise ValueError('Original compiled program authentication not established')
    entries = compiled.get('ordered_compiled_programs')
    if (not isinstance(entries, list) or len(entries) != EXPECTED_COMPILED_ENTRIES
            or any(not isinstance(row, dict)
                   or row.get('compiled_variant_position') != i
                   or row.get('original_runtime_kernel_index_proven') is not False
                   for i, row in enumerate(entries))):
        raise ValueError('Compiled positions not exactly correlated or falsely certified')
    if registry['authenticated_compiled_entry_count'] != len(entries):
        raise ValueError('Registry and program identity disagree')
    return {**registry,
            'same_slot_compiled_bytecode_sha_verified': True,
            'source_or_project_modified': False,
            'unity_gpu_or_android_tested': False}


def inspect(root: Path):
    from scripts.probe_authentic_fft_dxbc_translation import (
        OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS,
    )
    from scripts.probe_fft_variant_table import (
        correlate_original_variant_bytecode,
        EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT,
    )
    from scripts.probe_original_compute_containers import scan_blob
    from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources
    if EXPECTED_CONTAINERS != EXPECTED_COMPILED_ENTRIES:
        raise ValueError('Authentic FFT compiled count pin changed')
    verified = verify_sources(root, expected={OWNER: EXPECTED[OWNER]})
    if verified.get('authenticated_owners') != 1:
        raise ValueError('Original FFT owner SHA not authenticated')
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    objects = [o for o in env.file.objects.values()
               if o.type.name == 'ComputeShader' and int(o.path_id) == PATH_ID]
    if len(objects) != 1:
        raise ValueError('Original FFT ComputeShader missing or ambiguous')
    obj = objects[0]
    raw = obj.get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError('Original FFT serialized object SHA mismatch')
    tree = obj.read_typetree()
    registry = summarize_kernel_registry(tree)
    compiled = correlate_original_variant_bytecode(
        tree, scan_blob(raw)['valid_dxbc_containers'],
        EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT)
    return {
        'zip2_source_commit': '15964ea8f246b6e076ce26b60931ee2e1a9a2385',
        'original_owner_sha256': EXPECTED[OWNER][1],
        'original_compute_object_sha256': ORIGINAL_OBJECT_SHA256,
        **verify_registry_with_compiled_report(registry, compiled),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    print('RAFT_B08_ORIGINAL_FFT_KERNEL_REGISTRY ' + json.dumps(
        inspect(args.source), sort_keys=True))


if __name__ == '__main__':
    main()
