"""B48 SHA-authenticated FFT selector/program *candidate* compatibility gate.

Join the already proven original C# inherited FFT selector (n, bank) with the
original serialized DXBC compiled-slot workgroup table, *without* equating
serialized compiled slots with Unity FindKernel/Dispatch runtime kernel IDs.
Private source, bytecode, material values and pixels never enter output.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.probe_original_fft_inherited_seed import inspect as inspect_original_seed
from scripts.probe_fft_variant_table import (
    correlate_original_variant_bytecode, EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT,
)
from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS,
)
from scripts.probe_original_compute_containers import scan_blob
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

SOURCE_FORMULA = '((n-5)<<1) + (fourth_bool ? 10 : 0)'


def verify_candidate_pair_contract(seed, compiled):
    """Fail closed on any source/serialized contract drift, not infer kernel IDs."""
    if not isinstance(seed, dict) or not isinstance(compiled, dict):
        raise ValueError('FFT selector/compiled input must be records')
    if (seed.get('inherited_seed_dataflow_verified') is not True
            or seed.get('derived_second_int_forwarded_to_base_first_int') is not True
            or seed.get('first_pass_source_selector') != SOURCE_FORMULA
            or seed.get('second_pass_relative_offset') != 1
            or seed.get('unity_runtime_kernel_lookup_mapping_verified') is not False):
        raise ValueError('Original FFT source selector proof absent or changed')
    if (compiled.get('authentic_compiled_variants_verified_in_original_order')
            != EXPECTED_CONTAINERS
            or compiled.get('original_compiled_program_order_sha256_correlated') is not True
            or compiled.get('original_workgroup_mapping_correlated') is not True
            or compiled.get('unity_runtime_kernel_index_mapping_verified') is not False):
        raise ValueError('Original compiled slot identity proof absent or changed')
    programs = compiled.get('ordered_compiled_programs')
    if not isinstance(programs, list) or len(programs) != EXPECTED_CONTAINERS:
        raise ValueError('Expected exactly 20 authenticated FFT compiled slots')
    for i, item in enumerate(programs):
        if (not isinstance(item, dict)
                or item.get('compiled_variant_position') != i
                or item.get('original_runtime_kernel_index_proven') is not False
                or type(item.get('original_dxbc_byte_count')) is not int
                or item['original_dxbc_byte_count'] <= 0
                or type(item.get('original_dxbc_sha256')) is not str
                or len(item['original_dxbc_sha256']) != 64):
            raise ValueError('Unproven, missing, or reordered original compiled slot')
    examples = seed.get('algebraic_examples_only')
    if not isinstance(examples, list) or len(examples) != 5:
        raise ValueError('Original inherited selector has incomplete bounded examples')
    pairs, occupied = [], set()
    for n in range(5, 10):
        row = examples[n-5]
        resolution = 1 << n
        if (not isinstance(row, dict) or row.get('n') != n
                or row.get('r') != resolution):
            raise ValueError('Source-proven FFT resolution exponent drift')
        for bank in (0, 1):
            first = (n - 5) * 2 + (10 if bank else 0)
            second = first + 1
            if row.get('bank' + str(bank)) != [first, second]:
                raise ValueError('Source-proven original bank or pass selector drift')
            expected_group = [2 * resolution, 1, 1]
            for slot in (first, second):
                if slot in occupied or slot >= len(programs):
                    raise ValueError('FFT selector collision/out of range')
                occupied.add(slot)
                if programs[slot].get('original_serialized_workgroup_xyz') != expected_group:
                    raise ValueError('Original FFT compiled workgroup mismatches source resolution')
            pairs.append({
                'source_n_exponent': n,
                'source_fft_resolution': resolution,
                'source_boolean_bank': bank,
                'compiled_candidate_first_slot': first,
                'compiled_candidate_second_slot': second,
                'serialized_threads_per_group': expected_group,
                'unity_runtime_kernel_ids_proven': False,
            })
    if occupied != set(range(EXPECTED_CONTAINERS)):
        raise ValueError('Source selector does not cover each compiled slot exactly once')
    return {
        'source_inherited_seed_verified': True,
        'original_compiled_program_sha_and_order_verified': True,
        'proven_candidate_selector_workgroup_compatibility': True,
        'source_selectors_checked': len(pairs),
        'authentic_compiled_slots_checked': len(occupied),
        'candidate_groups': pairs,
        'actual_unity_kernel_index_to_compiled_slot_proven': False,
        'authored_compute_source_restored': False,
        'native_unity_compilation_or_android_gpu_execution': False,
        'private_shader_or_managed_source_disclosed': False,
    }


def inspect(root: Path, managed: Path):
    """Only after independent original byte/SHA checks and private ILSpy."""
    auth = verify_sources(root, expected={OWNER: EXPECTED[OWNER]})
    if auth.get('authenticated_owners') != 1:
        raise ValueError('Original FFT owner authentication failed')
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    objects = [obj for obj in env.file.objects.values()
               if obj.type.name == 'ComputeShader' and int(obj.path_id) == PATH_ID]
    if len(objects) != 1:
        raise ValueError('Original FFT ComputeShader missing/ambiguous')
    obj = objects[0]
    raw = obj.get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError('Original FFT object byte hash mismatch')
    scanned = scan_blob(raw)['valid_dxbc_containers']
    if len(scanned) != EXPECTED_CONTAINERS:
        raise ValueError('Original FFT program count changed')
    compiled = correlate_original_variant_bytecode(
        obj.read_typetree(), scanned, EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT)
    seed = inspect_original_seed(managed)
    report = verify_candidate_pair_contract(seed, compiled)
    return {'owner_sha256': EXPECTED[OWNER][1],
            'original_fft_compute_object_sha256': ORIGINAL_OBJECT_SHA256,
            'original_derived_source_sha256': seed['derived_source_sha256'],
            'original_base_source_sha256': seed['base_source_sha256'],
            'zip2_owner_source_authenticated': True,
            **report}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--managed', type=Path, required=True)
    a = p.parse_args()
    print('RAFT_B48_AUTHENTIC_FFT_SELECTOR_PROGRAM_CANDIDATES ' +
          json.dumps(inspect(a.source, a.managed), sort_keys=True))
