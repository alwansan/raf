"""Build exact original Depth Copy ShaderLab privately; publish aggregate evidence only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

from scripts.verify_targeted_lfs_compute_sources import verify_sources
from scripts.w1_recover_graphics_programs import OWNERS, decoded_platforms, records, translate, command
from scripts.w1_recover_depth_passes import TARGET, OBJECT_SHA256, linked_program, stage_variants, variant_key, digest
from scripts.w1_rebind_depth_resources import rebind, signature_inputs
from scripts.run_original_dxbc_translation_probe import version_tokens
from scripts.w1_depth_shaderlab import decode_empty_parameters, stage_body, wrapper


def build(root, out):
    verify_sources(root, expected=OWNERS)
    import UnityPy
    env = UnityPy.load(str(root / 'sharedassets0.assets'))
    original = env.file.objects[2407]
    if original.type.name != 'Shader' or hashlib.sha256(original.get_raw_data()).hexdigest() != OBJECT_SHA256:
        raise ValueError('Original Depth Copy input identity changed')
    tree = original.read_typetree()
    parsed = tree['m_ParsedForm']
    if parsed['m_Name'] != TARGET:
        raise ValueError('Original exact shader identity changed')
    tables = [(p, records(s)) for p, s in decoded_platforms(tree) if p == 4]
    if len(tables) != 1:
        raise ValueError('Original D3D11 source table unavailable')
    entries = tables[0][1]
    counts = [len(s['m_Passes']) for s in parsed['m_SubShaders']]
    report = {'source_sha': os.environ.get('GITHUB_SHA'), 'original_object_sha256': OBJECT_SHA256,
              'original_parsed_form_sha256': digest(parsed), 'subshader_pass_counts': counts,
              'parameter_records': {}, 'stages': [], 'pass_state_commitments': [],
              'private_shaderlab_constructed': False, 'unity_compiled': False,
              'software_vulkan_executed': False, 'numeric_or_visual_equivalence': False,
              'installed_shader_or_original_guid_changed': False}
    try:
        with tempfile.TemporaryDirectory(prefix='w1-depth-wrapper-private-') as folder:
            private = Path(folder)
            sources = {}
            for si, sub in enumerate(parsed['m_SubShaders']):
                for pi, shader_pass in enumerate(sub['m_Passes']):
                    pair = {}
                    target_versions = []
                    permutations = []
                    for field, stage in (('progVertex', 1), ('progFragment', 0)):
                        program = shader_pass[field]
                        variants = stage_variants(program)
                        if len(variants) != 1:
                            raise ValueError('Original wrapper needs explicitly recovered single variant')
                        bucket, vi, metadata = variants[0]
                        if metadata.get('m_KeywordIndices'):
                            raise ValueError('Nonempty keyword permutation needs explicit ShaderLab variant recovery')
                        permutations.append((bucket, variant_key(metadata)))
                        indices = program['m_ParameterBlobIndices']
                        if len(indices) != len(program['m_PlayerSubPrograms']) or len(indices[bucket]) != len(program['m_PlayerSubPrograms'][bucket]):
                            raise ValueError('Original parameter/program table dimensions disagree')
                        index = indices[bucket][vi]
                        if type(index) is not int or not 0 <= index < len(entries):
                            raise ValueError('Invalid original parameter-table index')
                        segment, raw_params = entries[index]
                        parameters = decode_empty_parameters(raw_params)
                        report['parameter_records'][str(index)] = {**parameters,
                            'sha256': hashlib.sha256(raw_params).hexdigest(), 'segment_index': segment}
                        code, link = linked_program(metadata, entries, stage)
                        target_versions.append(version_tokens(code)[0]['shader_model'])
                        destination = private / ('s%d-p%d-stage%d' % (si, pi, stage))
                        destination.mkdir()
                        result = translate(code, stage, destination)
                        if not result['hlsl_recovered'] or not result['roundtrip_vulkan11_valid']:
                            raise ValueError('Recovered original stage failed compilation')
                        rebound, binding = rebind((destination / 'private.hlsl').read_text(), program,
                            shader_pass['m_NameIndices'], original_inputs=signature_inputs(code) if stage == 1 else None)
                        pair[stage] = rebound
                        report['stages'].append({**result, **link, **binding,
                            'subshader': si, 'pass_index': pi, 'parameter_blob_index': index})
                    if permutations[0] != permutations[1]:
                        raise ValueError('Original paired-stage permutations differ')
                    shader_model = '.'.join(map(str, max(target_versions)))
                    sources[(si, pi)] = (pair[1], pair[0], shader_model)
                    body = stage_body(pair[1], pair[0])
                    body_path = private / ('s%d-p%d-combined.hlsl' % (si, pi))
                    body_path.write_text(body)
                    for stage, macro in ((1, 'VERTEX'), (0, 'FRAGMENT')):
                        output = private / ('s%d-p%d-stage%d-wrapped.spv' % (si, pi, stage))
                        valid = command(['glslangValidator', '-V', '-D', '-DSHADER_STAGE_' + macro + '=1',
                                         '-S', 'vert' if stage == 1 else 'frag', '-e', 'main', '-o', str(output), str(body_path)]) and command([
                                         'spirv-val', '--target-env', 'vulkan1.1', str(output)])
                        report['stages'][-2 if stage == 1 else -1]['wrapped_stage_vulkan11_valid'] = valid
                    report['pass_state_commitments'].append({'subshader': si, 'pass_index': pi,
                                                              'state_sha256': digest(shader_pass['m_State'])})
            source = wrapper(parsed, sources)
            (private / 'DepthCopy.shader').write_text(source)
            report.update(private_shaderlab_constructed=True,
                          shaderlab_sha256=hashlib.sha256(source.encode()).hexdigest(), shaderlab_bytes=len(source.encode()),
                          preserved_subshader_count=len(counts), preserved_pass_count=sum(counts),
                          all_wrapped_stages_valid=all(r['wrapped_stage_vulkan11_valid'] for r in report['stages']))
            if not report['all_wrapped_stages_valid']:
                raise ValueError('Combined ShaderLab stage body failed validation')
    except Exception as exc:
        report['failure_type'] = type(exc).__name__
        # These errors are authored aggregate diagnostics, never compiler output
        # or original asset property/program text.
        report['failure_reason'] = str(exc) if isinstance(exc, ValueError) else 'Private recovery failed; inspect source step'
        out.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
        print('RAFT_W1_DEPTH_WRAPPER ' + json.dumps(report, sort_keys=True))
        raise
    out.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
    print('RAFT_W1_DEPTH_WRAPPER ' + json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    build(args.source, args.out)
