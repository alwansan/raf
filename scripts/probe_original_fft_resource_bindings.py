"""Correlate authentic FFT resource registers with original two-pass CSharp calls.

Only structural roles/hashes leave CI. No shader/source/program bytes exported.
This does not claim Unity index enumeration, image-format or numeric equivalence.
"""
import argparse
import hashlib
import json
from pathlib import Path
from scripts.probe_original_fft_kernel_callsites import analyze_source, CALL, parse_original_args, sha, mask_noncode
from scripts.probe_original_fft_inherited_seed import inspect as inspect_seed
from scripts.probe_original_water_compute import ORIGINAL_SOURCE_SHA256
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources
from scripts.verify_original_fft_array_provenance import OWNER, FFT_PATH_ID, FFT_SHA
from scripts.probe_fft_variant_table import (
    correlate_original_variant_bytecode, EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT,
)
from scripts.probe_original_compute_containers import scan_blob


def resource_rows(tree):
    variants = tree.get('variants') if isinstance(tree, dict) else None
    if not isinstance(variants, list) or len(variants) != 1:
        raise ValueError('Original FFT variant set changed')
    kernels = variants[0].get('kernels')
    if not isinstance(kernels, list) or len(kernels) != 20:
        raise ValueError('Original FFT compiled slot count changed')
    rows = []
    for index, kernel in enumerate(kernels):
        vm = kernel.get('variantMap')
        if not isinstance(vm, list) or len(vm) != 1 or not isinstance(vm[0], (list, tuple)) or len(vm[0]) != 2:
            raise ValueError('Original FFT variant resource map ambiguous')
        entry = vm[0][1]
        if not isinstance(entry, dict) or any(entry.get(k) != [] for k in ('cbs', 'inBuffers', 'builtinSamplers')):
            raise ValueError('Unexpected original FFT extra resources')
        reads, writes = entry.get('textures'), entry.get('outBuffers')
        if not isinstance(reads, list) or not isinstance(writes, list) or len(reads) != 2 or len(writes) != 1:
            raise ValueError('Original FFT requires two input images and one output image')
        slots = {}
        for kind, resources in (('input', reads), ('output', writes)):
            for resource in resources:
                name, register = resource.get('name'), resource.get('bindPoint')
                if not isinstance(name, str) or not 0 < len(name) <= 256 or type(register) is not int:
                    raise ValueError('Original FFT resource identity invalid')
                if resource.get('texDimension') != 2 or resource.get('samplerBindPoint') != -1:
                    raise ValueError('Original FFT image dimension or sampler contract changed')
                key = (kind, register)
                if key in slots: raise ValueError('Duplicate original FFT resource register')
                slots[key] = sha(name)
        if set(slots) != {('input', 0), ('input', 1), ('output', 0)} or len(set(slots.values())) != 3:
            raise ValueError('Original FFT resource registers/names changed')
        group = entry.get('threadGroupSize')
        if group != [EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT[index], 1, 1]:
            raise ValueError('Original FFT workgroup sequence changed')
        rows.append({'compiled_slot': index, 'source_image_name_sha256': slots[('input',0)],
                     'butterfly_image_name_sha256': slots[('input',1)],
                     'target_image_name_sha256': slots[('output',0)], 'workgroup_xyz': group})
    signatures = {(row['source_image_name_sha256'], row['butterfly_image_name_sha256'], row['target_image_name_sha256']) for row in rows}
    if len(signatures) != 1:
        raise ValueError('Original FFT resources differ between compiled slots')
    return rows


def correlate(tree, source, expected_source_sha):
    rows = resource_rows(tree)
    calls = analyze_source(source, expected_source_sha)['compute_api_callsites']
    textures = [c for c in calls if c['call_kind'] == 'SetTexture']
    dispatches = [c for c in calls if c['call_kind'] == 'Dispatch']
    if len(textures) != 6 or len(dispatches) != 2 or len({c['receiver_identifier_sha256'] for c in textures + dispatches}) != 1:
        raise ValueError('Original FFT two-pass shader receiver or call count changed')
    if dispatches[0]['receiver_identifier_sha256'] is None or [c['kernel_index_affine_offset_from_first_dispatch'] for c in dispatches] != [0,1]:
        raise ValueError('Original FFT dispatch indices are not the two verified adjacent passes')
    roles = {role: rows[0][role + '_image_name_sha256'] for role in ('source', 'butterfly', 'target')}
    passes = []
    for offset in (0,1):
        chosen = [c for c in textures if c['kernel_index_affine_offset_from_first_dispatch'] == offset]
        if len(chosen) != 3 or any(c['argument_count'] != 3 or c['second_arg']['kind'] != 'literal_string' for c in chosen):
            raise ValueError('Original FFT pass texture calls changed')
        by_name = {c['second_arg']['sha256']: c['last_arg'] for c in chosen}
        if len(by_name) != 3 or set(by_name) != set(roles.values()):
            raise ValueError('Original CSharp image names do not match compiled resource metadata')
        passes.append({role: by_name[digest] for role, digest in roles.items()})
    if passes[0]['butterfly'] != passes[1]['butterfly'] or passes[0]['target'] != passes[1]['source']:
        raise ValueError('Original FFT intermediate or butterfly dataflow changed')
    if passes[0]['source'] == passes[0]['target'] or passes[1]['target'] == passes[1]['source']:
        raise ValueError('Original FFT pass aliases intermediate with original input/output')
    raw_calls = []
    # This secondary shape validator must use the same executable-only offsets\n    # as analyze_source. A Dispatch token in comments/strings is not a call.\n    for match in CALL.finditer(mask_noncode(source)):
        args, _ = parse_original_args(source, match.end()-1)
        if match.group(1) == 'Dispatch': raw_calls.append(args)
    for args in raw_calls:
        if len(args) != 4 or args[1].strip() != '1' or args[3].strip() != '1' or not args[2].strip().endswith('.height'):
            raise ValueError('Original FFT row dispatch shape changed')
    if raw_calls[0][2].strip() != raw_calls[1][2].strip():
        raise ValueError('Original FFT passes dispatch different source row counts')
    return {
        'compiled_slots_with_csharp_resource_names_matched': len(rows),
        'resource_roles': {'source_image': {'register_kind':'t','register':0,'name_sha256':roles['source']},
                           'butterfly_image': {'register_kind':'t','register':1,'name_sha256':roles['butterfly']},
                           'target_image': {'register_kind':'u','register':0,'name_sha256':roles['target']}},
        'two_pass_intermediate_output_to_input_matched': True,
        'same_butterfly_image_both_passes': True,
        'dispatch_x_groups': 1, 'dispatch_z_groups': 1,
        'dispatch_y_same_original_texture_height_expression': True,
        'workgroup_xyz_by_compiled_slot': [row['workgroup_xyz'] for row in rows],
        'texture_runtime_object_aliasing_verified': False,
        'unity_runtime_kernel_indices_verified': False,
        'image_formats_and_numeric_outputs_verified': False,
        'private_names_source_or_bytecode_published': False,
        'unity_or_android_execution': False,
    }


def inspect(root, managed):
    verify_sources(root, expected={OWNER: EXPECTED[OWNER]})
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    objects = [o for o in env.file.objects.values() if o.type.name == 'ComputeShader' and int(o.path_id) == FFT_PATH_ID]
    if len(objects) != 1: raise ValueError('Original FFT compute missing or ambiguous')
    obj = objects[0]; raw = obj.get_raw_data()
    if hashlib.sha256(raw).hexdigest() != FFT_SHA: raise ValueError('Original FFT object fingerprint mismatch')
    paths = list(managed.rglob('Dx11FFT.cs'))
    if len(paths) != 1 or paths[0].is_symlink(): raise ValueError('Original Dx11FFT source ambiguous')
    source = paths[0].read_text(encoding='utf-8-sig').replace('\r\n','\n')
    tree = obj.read_typetree()
    bytecode = correlate_original_variant_bytecode(tree, scan_blob(raw)['valid_dxbc_containers'], EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT)
    result = correlate(tree, source, ORIGINAL_SOURCE_SHA256['Dx11FFT'])
    return {'owner': OWNER, 'object_path_id': FFT_PATH_ID, 'object_sha256': FFT_SHA,
            'source_sha256': ORIGINAL_SOURCE_SHA256['Dx11FFT'],
            'ordered_programs_authenticated': bytecode['authentic_compiled_variants_verified_in_original_order'],
            'inherited_selector_dataflow': inspect_seed(managed), **result}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--managed-source', type=Path, required=True)
    a = p.parse_args()
    print('RAFT_ORIGINAL_FFT_RESOURCE_BINDINGS ' + json.dumps(inspect(a.source, a.managed_source), sort_keys=True))
