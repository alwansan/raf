"""Recover and exercise original two-pass Blur named uniforms, privately.

Publishes only hashes and aggregate metrics. Does not install a game shader or
claim Unity/Adreno uniform upload, filtering, every variant or full water proof.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import tempfile

from scripts.a12_build_original_blur_wrapper import OBJECT_SHA256, PARSED_SHA256, wrapper
from scripts.a12_probe_original_blur_passes import original_shader
from scripts.a12r_190657_blur_cb_reflection import crosscheck_unity_cb, serialized_groups
from scripts.blur_private_binding_plan import build as named_plan, public_summary
from scripts.probe_original_fft_software_vulkan import private_command
from scripts.w1_depth_raster_numeric import (
    canary, compare, interface_rows, normalize_bindings, reflection, supported_state,
)
from scripts.w1_depth_shaderlab import stage_body
from scripts.w1_rebind_depth_resources import rebind as rebind_resources, signature_inputs
from scripts.w1_recover_depth_passes import interfaces_match, linked_program, stage_variants
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate
from scripts.w5_blur_uniform_rebinding import rebind as rebind_uniforms


def normalize_uniforms(binary, reflected, plan, stage, rebuilt):
    """Join by original slot symbol or exact named CB identity, never table order."""
    words = list(struct.unpack('<%dI' % (len(binary) // 4), binary))
    if len(words) < 5 or words[0] != 0x07230203:
        raise ValueError('Invalid SPIR-V uniform module')
    names, pointers, variables, instructions = {}, {}, {}, []
    position = 5
    while position < len(words):
        count, opcode = words[position] >> 16, words[position] & 65535
        if not count or position + count > len(words):
            raise ValueError('Invalid SPIR-V uniform instruction')
        row = words[position:position + count]
        instructions.append((position, count, opcode))
        if opcode == 5 and count >= 3:
            names[row[1]] = struct.pack('<%dI' % (count - 2), *row[2:]).split(b'\0', 1)[0].decode()
        if opcode == 32 and count == 4 and row[2] == 2:
            pointers[row[1]] = row[3]
        if opcode == 59 and count >= 4 and row[3] == 2:
            variables[row[2]] = row[1]
        position += count
    original_slots_by_type = {}
    for variable, pointer in variables.items():
        match = re.fullmatch(r'cb(\d+)_0', names.get(variable, ''))
        if not rebuilt and pointer in pointers and match:
            type_id = pointers[pointer]
            if type_id in original_slots_by_type:
                raise ValueError('Ambiguous translated uniform type')
            original_slots_by_type[type_id] = int(match[1])
    slots = {buffer['slot']: buffer for buffer in plan['buffers']}
    wanted_types, seen = {}, set()
    for resource in reflected.get('ubos', []):
        members = reflected['types'][resource['type']]['members']
        if rebuilt:
            possible = [slot for slot, buffer in slots.items()
                        if resource['name'] == ('__raft_w5_Globals' if buffer['name'] == '$Globals' else buffer['name'])]
        else:
            # SPIRV-Cross JSON names the struct member `_m0`, NOT the HLSL
            # flattened `cb0_0_m0`. Original slot belongs to OpName of the
            # actual Uniform variable; resolve through its pointer/struct ID.
            type_match = re.fullmatch(r'_(\d+)', resource['type'])
            slot = original_slots_by_type.get(int(type_match[1])) if type_match else None
            possible = [slot] if slot is not None else []
        if len(possible) != 1 or possible[0] not in slots or possible[0] in seen:
            raise ValueError('Original uniform descriptor identity unresolved')
        slot = possible[0]
        seen.add(slot)
        expected = slots[slot]['allocation_bytes']
        if (resource['block_size'] != expected if rebuilt else not 0 < resource['block_size'] <= expected):
            raise ValueError('Original uniform allocation not preserved')
        if rebuilt:
            by_name = {member['name']: member for member in members}
            for member in slots[slot]['members']:
                actual = by_name.get(member['name'], {})
                wanted_type = 'mat4' if member['kind'] == 'matrix' else (
                    'float' if member['serialized_dimension'] == 1 else 'vec' + str(member['serialized_dimension']))
                if actual.get('offset') != member['serialized_index'] or actual.get('type') != wanted_type:
                    raise ValueError('Original named uniform offset or type changed')
                if member['kind'] == 'matrix' and actual.get('matrix_stride') != 16:
                    raise ValueError('Original matrix register stride changed')
        if not re.fullmatch(r'_\d+', resource['type']):
            raise ValueError('Unsupported reflected SPIR-V type identity')
        wanted_types[int(resource['type'][1:])] = 4 + slot if stage == 1 else 6 + slot
    if seen != set(slots):
        raise ValueError('Original uniform slots not fully mapped')
    pointer_types, targets = {}, {}
    for position, count, opcode in instructions:
        row = words[position:position + count]
        if opcode == 32 and count == 4 and row[2] == 2 and row[3] in wanted_types:
            pointer_types[row[1]] = wanted_types[row[3]]
    for position, count, opcode in instructions:
        if opcode == 59 and count >= 4 and words[position + 1] in pointer_types:
            targets[words[position + 2]] = pointer_types[words[position + 1]]
    if len(targets) != len(slots) or len(set(targets.values())) != len(slots):
        raise ValueError('Original uniform variables not uniquely resolved')
    changed = set()
    for position, count, opcode in instructions:
        if opcode == 71 and count == 4 and words[position + 1] in targets and words[position + 2] in (33, 34):
            key = (words[position + 1], words[position + 2])
            if key in changed:
                raise ValueError('Duplicate uniform descriptor decoration')
            changed.add(key)
            words[position + 3] = targets[key[0]] if key[1] == 33 else 0
    if changed != {(target, kind) for target in targets for kind in (33, 34)}:
        raise ValueError('Incomplete uniform descriptor decorations')
    return struct.pack('<%dI' % len(words), *words)


def recover(root, repo, runner, private, progress=None):
    progress = {} if progress is None else progress
    progress['phase'] = 'authenticate_original'
    _, digest, tree = original_shader(root, repo)
    parsed = tree['m_ParsedForm']
    parsed_hash = hashlib.sha256(json.dumps(parsed, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()
    if digest != OBJECT_SHA256 or parsed_hash != PARSED_SHA256:
        raise ValueError('Original Blur object or parsed-form fingerprint changed')
    tables = [records(segments) for platform, segments in decoded_platforms(tree) if platform == 4]
    if len(tables) != 1:
        raise ValueError('Original Blur platform ambiguous')
    entries = tables[0]
    generated, stages, raster = {}, [], []
    progress.update(stages=stages, raster=raster, phase='independent_host_canary')
    canary_result = canary(runner, private)
    for pass_index, shader_pass in enumerate(parsed['m_SubShaders'][0]['m_Passes']):
        pair, binaries, interfaces = {}, {}, {}
        for field, stage, suffix in [('progVertex', 1, 'vert'), ('progFragment', 0, 'frag')]:
            progress.update(phase='stage_recovery', pass_index=pass_index, stage_code=stage)
            program = shader_pass[field]
            variants = stage_variants(program)
            if len(variants) != 1:
                raise ValueError('Original Blur permutation count changed')
            bucket, index, meta = variants[0]
            if meta.get('m_KeywordIndices'):
                raise ValueError('Original Blur keyword permutation unsupported')
            raw_params = entries[program['m_ParameterBlobIndices'][bucket][index]][1]
            crosscheck_unity_cb(shader_pass['m_NameIndices'], program['m_CommonParameters'], serialized_groups(raw_params))
            code, _ = linked_program(meta, entries, stage)
            folder = private / f'p{pass_index}s{stage}'
            folder.mkdir()
            translated = translate(code, stage, folder)
            if not translated['roundtrip_vulkan11_valid']:
                raise ValueError('Original Blur translation did not validate')
            plan = named_plan(program['m_CommonParameters'], shader_pass['m_NameIndices'])
            source, uniform_summary = rebind_uniforms((folder / 'private.hlsl').read_text(), plan)
            texture_program = copy.deepcopy(program)
            for key in ('m_ConstantBuffers', 'm_ConstantBufferBindings'):
                texture_program['m_CommonParameters'][key] = []
            source, resources = rebind_resources(source, texture_program, shader_pass['m_NameIndices'],
                original_inputs=signature_inputs(code) if stage == 1 else None)
            hlsl, compiled = folder / 'rebound.hlsl', folder / 'rebound.spv'
            hlsl.write_text(source)
            private_command(['glslangValidator', '-V', '-D', '-S', suffix, '-e', 'main', '-o', str(compiled), str(hlsl)])
            private_command(['spirv-val', '--target-env', 'vulkan1.1', str(compiled)])
            pair[stage] = source
            for path, rebuilt in [(folder / 'original.spv', False), (compiled, True)]:
                ref = reflection(path)
                sampled_ref = copy.deepcopy(ref)
                sampled_ref.pop('ubos', None)
                normalized, _ = normalize_bindings(path.read_bytes(), sampled_ref, texture_program, shader_pass['m_NameIndices'], rebuilt)
                normalized = normalize_uniforms(normalized, ref, plan, stage, rebuilt)
                output = folder / ('rebuilt-normalized.spv' if rebuilt else 'original-normalized.spv')
                output.write_bytes(normalized)
                private_command(['spirv-val', '--target-env', 'vulkan1.1', str(output)])
                binaries[(stage, rebuilt)] = output
                interfaces[(stage, rebuilt)] = {key: interface_rows(ref, key) for key in ('inputs', 'outputs')}
            stages.append({**uniform_summary, **public_summary(plan),
                'pass_index': pass_index, 'stage_code': stage, 'resources': resources,
                'original_dxbc_sha256': translated['dxbc_sha256'],
                'rebound_hlsl_sha256': hashlib.sha256(source.encode()).hexdigest(), 'vulkan11_valid': True})
        for rebuilt in (False, True):
            if not interfaces_match(interfaces[(1, rebuilt)], interfaces[(0, rebuilt)]):
                raise ValueError('Original/reconstructed varying interface mismatch')
        generated[(0, pass_index)] = (pair[1], pair[0], '5.0')
        combined = private / f'pass{pass_index}-combined.hlsl'
        combined.write_text(stage_body(pair[1], pair[0]))
        for suffix, macro in [('vert', 'VERTEX'), ('frag', 'FRAGMENT')]:
            compiled = private / f'pass{pass_index}-combined-{suffix}.spv'
            private_command(['glslangValidator', '-V', '-D', '-DSHADER_STAGE_' + macro + '=1', '-S', suffix,
                             '-e', 'main', '-o', str(compiled), str(combined)])
            private_command(['spirv-val', '--target-env', 'vulkan1.1', str(compiled)])
        state = supported_state(shader_pass['m_State'])
        files = [binaries[(stage, rebuilt)] for rebuilt in (False, True) for stage in (1, 0)]
        progress.update(phase='raster_numerical_comparison', stage_code=None)
        positive = [compare(runner, files, state, seed, 0, 1) for seed in (0, 19, 257)]
        negative = {str(mode): not compare(runner, files, state, 19, mode, 1)['within_tolerance']
                    for mode in (1, 2, 4, 5, 6, 7)}
        raster.append(dict(pass_index=pass_index, positive=positive, negative=negative))
        if not all(row['within_tolerance'] for row in positive) or not all(negative.values()):
            raise ValueError('Original Blur numerical match or negative control failed')
    text = wrapper(parsed, generated)
    (private / 'candidate.shader').write_text(text)
    return dict(source_sha=os.environ.get('GITHUB_SHA'), original_object_sha256=digest,
                stages=stages, raster=raster, canary=canary_result,
                shaderlab_sha256=hashlib.sha256(text.encode()).hexdigest(),
                shaderlab_bytes=len(text.encode()), shaderlab_passes=len(generated),
                private_shaderlab_constructed=True, installed=False, unity_or_adreno_verified=False,
                sampler_state_or_original_uniform_upload_verified=False,
                authentic_water_kernel_identity_verified=False, private_payload_published=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'repo', 'runner', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    progress = {}
    try:
        with tempfile.TemporaryDirectory(prefix='w5-private-blur-', dir=args.out.parent) as folder:
            result = recover(args.source, args.repo, args.runner, Path(folder), progress)
    except Exception as exc:
        # Compiler/translator messages and arbitrary exception details may contain
        # source/names; retain only an explicit failure class in public output.
        result = dict(status='failed', failure_type=type(exc).__name__, source_sha=os.environ.get('GITHUB_SHA'),
                      private_payload_published=False, installed=False, unity_or_adreno_verified=False,
                      progress=progress)
        args.out.write_text(json.dumps(result, sort_keys=True) + '\n')
        print('RAFT_W5_BLUR ' + json.dumps(result, sort_keys=True))
        raise SystemExit(1)
    result['status'] = 'passed_bounded_cpu_raster'
    args.out.write_text(json.dumps(result, sort_keys=True) + '\n')
    print('RAFT_W5_BLUR ' + json.dumps(result, sort_keys=True))
