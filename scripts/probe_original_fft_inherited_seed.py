"""Prove the original FFT selector seed through its inherited constructor field.

Read SHA-pinned private CSharp9 only; report hashes and algebra, never game code.
Does not restore shaders or establish Unity runtime kernel lookup semantics.
"""
import argparse
import json
from pathlib import Path
import re
from scripts.probe_original_water_compute import ORIGINAL_SOURCE_SHA256
from scripts.probe_original_fft_index_derivation import index_source_links
from scripts.probe_original_fft_caller_graph import source_declarations
from scripts.probe_original_fft_kernel_callsites import parse_original_args, sha

BASE_SHA256 = '2f866cbe58836da8260461fe6406793f35d868eba94e816e593209544b4ba704'


def prove(derived, base, expected_derived, expected_base):
    if len(derived) > 100000 or len(base) > 100000 or sha(derived) != expected_derived or sha(base) != expected_base:
        raise ValueError('Original inherited FFT source fingerprint mismatch')
    if not re.search(r'\bclass\s+Dx11FFT\s*:\s*GpuFFT\b', derived):
        raise ValueError('Original FFT inheritance edge changed')
    report = index_source_links(derived, expected_derived)
    seed_hash = report['source_proven_original_kernel_index_formula_seed_lineage']['first_formula_seed_identifier_sha256']
    fields = re.findall(r'\bprotected\s+int\s+([A-Za-z_]\w*)\s*;', base)
    matching = [field for field in fields if sha(field) == seed_hash]
    if len(matching) != 1:
        raise ValueError('Original protected inherited selector field not unique')
    seed = matching[0]
    constructors = [d for d in source_declarations(derived) if d['name'] == 'Dx11FFT']
    base_constructors = [d for d in source_declarations(base) if d['name'] == 'GpuFFT']
    if len(constructors) != 1 or len(base_constructors) != 1:
        raise ValueError('Original FFT constructors ambiguous')
    derived_params, base_params = constructors[0]['params'], base_constructors[0]['params']
    if len(derived_params) != 4 or len(base_params) != 4:
        raise ValueError('Original FFT constructor arity changed')
    actual = re.fullmatch(r'int\s+([A-Za-z_]\w*)', derived_params[1].strip())
    formal = re.fullmatch(r'int\s+([A-Za-z_]\w*)', base_params[0].strip())
    if not actual or not formal:
        raise ValueError('Original FFT constructor size type changed')
    initializers = list(re.finditer(r':\s*base\s*\(', derived))
    if len(initializers) != 1:
        raise ValueError('Original FFT base initializer ambiguous')
    args, _ = parse_original_args(derived, initializers[0].end() - 1)
    if len(args) != 4 or args[0].strip() != actual.group(1):
        raise ValueError('Original FFT size is not forwarded unchanged')
    assignments = re.findall(r'\b' + re.escape(seed) + r'\s*=\s*([^;]+);', base)
    math = (r'\(int\)\s*\(\s*Mathf\.Log\(\s*' + re.escape(formal.group(1))
            + r'\s*\)\s*/\s*Mathf\.Log\(\s*2f\s*\)\s*\)')
    if len(assignments) != 1 or not re.fullmatch(math, assignments[0].strip()):
        raise ValueError('Original inherited seed assignment is not the verified logarithm ratio')
    writes = r'\b' + re.escape(seed) + r'\s*(?:=(?!=)|\+=|-=|\*=|/=|\+\+|--)'
    if len(re.findall(writes, base)) != 1 or re.search(writes, derived):
        raise ValueError('Additional original selector-seed writes found')
    bank = report['source_proven_original_constructor_kernel_bank_formula']
    if not bank['bank_stride_guard_matches_fourth_bool_parameter']:
        raise ValueError('Original FFT bank selector changed')
    return {
        'derived_source_sha256': expected_derived, 'base_source_sha256': expected_base,
        'protected_inherited_seed_identifier_sha256': seed_hash,
        'derived_second_int_forwarded_to_base_first_int': True,
        'seed_source_expression': 'n=truncate(log(r)/log(2)) using original Mathf float arithmetic',
        'first_pass_source_selector': '((n-5)<<1) + (fourth_bool ? 10 : 0)',
        'second_pass_relative_offset': 1,
        'inherited_seed_dataflow_verified': True,
        'algebraic_examples_only': [dict(n=n, r=1 << n, bank0=[(n-5)*2, (n-5)*2+1], bank1=[(n-5)*2+10, (n-5)*2+11]) for n in range(5,10)],
        'actual_resolution_range_or_float_results_verified': False,
        'unity_runtime_kernel_lookup_mapping_verified': False,
        'shader_or_game_source_modified': False,
        'private_source_or_field_names_published': False,
        'unity_or_device_execution': False,
    }


def inspect(root):
    texts = {}
    for name in ('Dx11FFT', 'GpuFFT'):
        paths = list(root.rglob(name + '.cs'))
        if len(paths) != 1 or paths[0].is_symlink():
            raise ValueError('Original inherited FFT source missing or ambiguous')
        texts[name] = paths[0].read_text(encoding='utf-8-sig').replace('\r\n', '\n')
    return prove(texts['Dx11FFT'], texts['GpuFFT'], ORIGINAL_SOURCE_SHA256['Dx11FFT'], BASE_SHA256)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    a = p.parse_args()
    print('RAFT_ORIGINAL_FFT_INHERITED_SEED ' + json.dumps(inspect(a.source), sort_keys=True))
