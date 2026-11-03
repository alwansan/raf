"""Recover exact original Depth Copy pass/stage programs into a private packet.

Retains serialized pass state, properties and resource metadata verbatim in a
temporary packet. Reports only indices/counts/hashes and stage-link checks.
This does not install ShaderLab or claim shader numerical equivalence.
"""
import argparse
from collections import Counter
import gc
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from scripts.w1_recover_graphics_programs import OWNERS, decoded_platforms, records, translate
from scripts.verify_targeted_lfs_compute_sources import verify_sources
from scripts.probe_original_compute_containers import scan_blob
from scripts.run_original_dxbc_translation_probe import version_tokens

TARGET = 'UltimateWater/Depth/Depth Copy'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def linked_program(metadata, entries, stage):
    index = metadata.get('m_BlobIndex')
    if type(index) is not int or not 0 <= index < len(entries):
        raise ValueError('Original pass has invalid program-table index')
    segment, entry = entries[index]
    rows = scan_blob(entry)['valid_dxbc_containers']
    if len(rows) != 1:
        raise ValueError('Linked pass record lacks exactly one original DXBC')
    row = rows[0]
    start = row['offset_in_original_object']
    code = entry[start:start + row['bytes']]
    versions = version_tokens(code)
    if len(versions) != 1 or versions[0]['shader_stage_code'] != stage:
        raise ValueError('Original pass-stage/bytecode mismatch')
    return code, {'blob_index': index, 'segment_index': segment,
                  'metadata_sha256': digest(metadata), 'entry_sha256': hashlib.sha256(entry).hexdigest()}


def reflection(path):
    result = subprocess.run(['spirv-cross', str(path), '--reflect'], capture_output=True, timeout=30)
    if result.returncode or len(result.stdout) > 1024 * 1024:
        raise ValueError('Private stage reflection unavailable')
    parsed = json.loads(result.stdout)
    # Public schema fields and scalar/vector types only, no original identifiers.
    def interface(key):
        return sorted(({'location': r['location'], 'type': r['type']} for r in parsed.get(key, [])
                       if 'location' in r), key=lambda r: r['location'])
    def resources():
        return {k: sorted([[r.get('set'), r.get('binding')] for r in parsed.get(k, [])])
                for k in ('ubos', 'ssbos', 'textures', 'separate_images', 'separate_samplers', 'images')
                if parsed.get(k)}
    return {'inputs': interface('inputs'), 'outputs': interface('outputs'), 'resource_slots': resources()}


def interfaces_match(vertex, fragment):
    outputs = {r['location']: r['type'] for r in vertex['outputs']}
    return all(outputs.get(r['location']) == r['type'] for r in fragment['inputs'])


def variant_key(metadata):
    # Require an identical serialized permutation when pairing stages. Do not
    # infer equality from their list order or arbitrarily select first entries.
    return tuple((key, json.dumps(metadata.get(key), sort_keys=True)) for key in (
        'm_ShaderHardwareTier', 'm_KeywordIndices', 'm_GlobalKeywordIndices', 'm_LocalKeywordIndices'))


def recover(root, out):
    verify_sources(root, expected=OWNERS)
    import UnityPy
    selected = []
    for owner in OWNERS:
        env = UnityPy.load(str(root / owner))
        for obj in env.file.objects.values():
            if obj.type.name != 'Shader':
                continue
            tree = obj.read_typetree()
            if tree.get('m_ParsedForm', {}).get('m_Name') == TARGET:
                selected.append((owner, int(obj.path_id), hashlib.sha256(obj.get_raw_data()).hexdigest(), tree))
        del env
        gc.collect()
    if len(selected) != 1:
        raise ValueError('Exact original Depth Copy shader is missing or ambiguous')
    owner, path_id, object_sha, tree = selected[0]
    tables = [(p, records(s)) for p, s in decoded_platforms(tree) if p == 4]
    if len(tables) != 1:
        raise ValueError('Original D3D11 graphics table is ambiguous')
    entries = tables[0][1]
    parsed = tree['m_ParsedForm']
    passes, stages = [], []
    with tempfile.TemporaryDirectory(prefix='w1-private-depth-passes-') as folder:
        packet = Path(folder)
        # Preserve actual metadata privately alongside reconstructed programs.
        (packet / 'original-parsed-form.json').write_text(json.dumps(parsed, sort_keys=True))
        for si, sub in enumerate(parsed['m_SubShaders']):
            for pi, shader_pass in enumerate(sub['m_Passes']):
                if shader_pass['m_Type'] != 0:
                    raise ValueError('Depth Copy has non-normal pass needing explicit resolution')
                pass_report = {'subshader': si, 'pass_index': pi,
                               'state_sha256': digest(shader_pass['m_State']),
                               'state_schema': sorted(shader_pass['m_State']),
                               'variants': {}, 'linked_pairs': []}
                reflected = {1: [], 0: []}
                for field, stage in (('progVertex', 1), ('progFragment', 0)):
                    variants = shader_pass[field]['m_SubPrograms']
                    pass_report['variants'][str(stage)] = len(variants)
                    if not 0 < len(variants) <= 24:
                        raise ValueError('Depth Copy stage variant count exceeds bounded recovery')
                    for vi, metadata in enumerate(variants):
                        code, link = linked_program(metadata, entries, stage)
                        target = packet / ('s%d-p%d-stage%d-v%d' % (si, pi, stage, vi))
                        target.mkdir()
                        result = translate(code, stage, target)
                        result.update(link, subshader=si, pass_index=pi, variant_index=vi,
                                      metadata_schema=sorted(metadata))
                        (target / 'original-stage-metadata.json').write_text(json.dumps(metadata, sort_keys=True))
                        if result['hlsl_recovered'] and result['roundtrip_vulkan11_valid']:
                            original = reflection(target / 'original.spv')
                            rebuilt = reflection(target / 'roundtrip.spv')
                            result.update(original_reflection=original, roundtrip_reflection=rebuilt,
                                          resource_slots_preserved=original['resource_slots'] == rebuilt['resource_slots'],
                                          stage_interface_preserved=original['inputs'] == rebuilt['inputs'] and original['outputs'] == rebuilt['outputs'])
                            reflected[stage].append((metadata, vi, original, rebuilt))
                        stages.append(result)
                for vm, vi, original_v, rebuilt_v in reflected[1]:
                    for fm, fi, original_f, rebuilt_f in reflected[0]:
                        if variant_key(vm) != variant_key(fm):
                            continue
                        pass_report['linked_pairs'].append({'vertex_variant': vi, 'fragment_variant': fi,
                            'original_location_types_match': interfaces_match(original_v, original_f),
                            'roundtrip_location_types_match': interfaces_match(rebuilt_v, rebuilt_f),
                            'permutation_metadata_sha256': digest(variant_key(vm))})
                passes.append(pass_report)
        packet_manifest = {str(p.relative_to(packet)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(packet.rglob('*')) if p.is_file()}
        report = {'source_sha': os.environ.get('GITHUB_SHA'), 'owner': owner, 'path_id': path_id,
                  'original_object_sha256': object_sha, 'original_parsed_form_sha256': digest(parsed),
                  'original_property_count': len(parsed.get('m_PropInfo', {}).get('m_Props', [])),
                  'original_pass_count': len(passes), 'passes': passes, 'stages': stages,
                  'private_packet_files': len(packet_manifest), 'private_packet_manifest_sha256': digest(packet_manifest),
                  'all_stages_recovered': all(r['hlsl_recovered'] and r['roundtrip_vulkan11_valid'] for r in stages),
                  'all_passes_have_matching_permutation_pair': all(p['linked_pairs'] for p in passes),
                  'shaderlab_installed': False, 'original_materials_or_guids_changed': False,
                  'gpu_or_numeric_or_phone_equivalence': False}
    out.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
    print('RAFT_W1_DEPTH_PASS_RECOVERY ' + json.dumps(report, sort_keys=True))
    if len(passes) < 4 or not report['all_stages_recovered'] or not report['all_passes_have_matching_permutation_pair']:
        raise ValueError('Actual original Depth Copy pass recovery incomplete; inspect aggregate result')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    recover(a.source, a.out)
