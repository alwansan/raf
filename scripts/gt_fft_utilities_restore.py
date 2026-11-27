"""Restore authentic FFT Utilities programs privately from SHA-owned ZIP2 data.

No source program, names, IDs or private compiler logs enter the safe receipt.
Compilation is source recovery evidence, not Unity or device rendering proof.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil

from scripts.gt_original_921_all_variants import enumerate_all, stage_parameter_records
from scripts.gt_original_921_keyword_routes import keyword_routes, shaderlab_layout
from scripts.gt_original_921_shaderlab import (
    combine_stages, paired_uniform_layouts, unity_resource_bindings,
    unity_varying_semantics, verify_entrypoints,
)
from scripts.gt_original_921_cb_hlsl import rebind_constant_buffers
from scripts.gt_original_921_semantics import pin_varying_locations, restore_vertex_inputs
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate
from scripts.w1_stage_zip2_owners import PINS, fingerprint

TARGET = 'UltimateWater/Utilities/FFT Utilities'
STATUS = 'GT_FFT_UTILITIES_AUTHENTIC_SEVEN_PASS_SOURCE_COMPILED'
FAILED_DXC_CANDIDATE_SHA256 = 'f8575ebd855cff193c9fdb506b5f2b2d427d4c583eb9c5c7af0d6ff39c948b23'


def compiler_control(shader, mode):
    # Deliberately bounded compiler-lowering control: no HLSL expressions,
    # resource bindings, properties or source render states change.
    pragma = '#pragma use_dxc vulkan\n'
    if mode not in ('dxc', 'hlslcc') or shader.count(pragma) != 7:
        raise ValueError('fft_utilities_unverified_compiler_control')
    return shader if mode == 'dxc' else shader.replace(pragma, '')


def validate_routes(routes):
    if len(routes) != 7:
        raise ValueError('fft_utilities_seven_source_routes_required')
    for index, row in enumerate(routes):
        if (row['subshader'] != 0 or row['pass'] != index
                or len(row['routes']) != 1 or row['routes'][0]['enabled']
                or row['unmatched_vertex_keywords'] or row['keyword_universe']):
            raise ValueError('fft_utilities_source_route_topology_drift')
    return 7


def attach_programs(layout, programs):
    pieces = layout.split('// Original stage programs attach here')
    if len(programs) != 7 or len(pieces) != 8:
        raise ValueError('fft_utilities_source_pass_population_drift')
    output = [pieces[0]]
    for source, tail in zip(programs, pieces[1:]):
        output.extend(('\n'.join(['HLSLPROGRAM', '#pragma target 5.0',
            '#pragma vertex gt_vs_main', '#pragma fragment gt_fs_main',
            '#pragma use_dxc vulkan', source, 'ENDHLSL']), tail))
    return ''.join(output)


def original_shader(original):
    import UnityPy
    matches = []
    # Authenticate both shader-owning serialized files before selecting by exact
    # original public lookup name. Object IDs never come from the dummy export.
    for owner in ('resources.assets', 'sharedassets0.assets'):
        source = original / owner
        if source.is_symlink() or fingerprint(source) != PINS['Raft_Data/' + owner]:
            raise ValueError('fft_utilities_original_owner_SHA_mismatch')
        env = UnityPy.load(str(source))
        for obj in env.objects:
            if obj.type.name == 'Shader':
                tree = obj.read_typetree()
                if tree.get('m_ParsedForm', {}).get('m_Name') == TARGET:
                    matches.append(tree)
    if len(matches) != 1:
        raise ValueError('fft_utilities_original_source_identity_ambiguous')
    return matches[0]


def compose(private, pairs, stage_records, layout):
    if len(stage_records) != 14 or len(pairs) != 7:
        raise ValueError('fft_utilities_incomplete_named_stage_records')
    programs = []
    for index, pair in enumerate(pairs):
        layouts = paired_uniform_layouts(stage_records[index*2:index*2+2])
        sources = []
        for offset, stage in enumerate(('vs', 'fs')):
            source = rebind_constant_buffers(
                (private / ('bound-stage-%03d' % (index*2+offset)) / 'resource-bound.hlsl').read_text(),
                layouts[offset])
            if stage == 'vs':
                source, _ = restore_vertex_inputs(source,
                    (private / pair[stage]['program_ref'] / 'source.dxbc').read_bytes())
            source = unity_varying_semantics(pin_varying_locations(source, 1-offset))
            source, amount = re.subn(r'\bmain(?=\s*\()', 'gt_'+stage+'_main', source)
            if amount != 1:
                raise ValueError('fft_utilities_original_entrypoint_ambiguous')
            sources.append(unity_resource_bindings(source, stage))
        programs.append(combine_stages(*sources))
    return attach_programs(layout, programs)


def recover(original, private, *, compiler_mode="dxc"):
    for binary in ('vkd3d-compiler', 'spirv-val', 'spirv-cross', 'glslangValidator'):
        if shutil.which(binary) is None:
            raise ValueError('fft_utilities_translation_tool_unavailable')
    if (private.exists() or any(p.is_symlink() for p in (private, *private.parents))
            or private.resolve().is_relative_to(original.resolve())):
        raise ValueError('fft_utilities_unsafe_private_destination')
    tree = original_shader(original)
    parsed = tree['m_ParsedForm']
    tables = [records(parts) for platform, parts in decoded_platforms(tree) if platform == 4]
    if len(tables) != 1:
        raise ValueError('fft_utilities_original_D3D11_table_ambiguous')
    table = tables[0]
    pairs, orphans, passes, distinct = enumerate_all(parsed, table,
        variants=stage_variants, permutation=variant_key, linker=linked_program,
        topology=(7, 7, 0, 12))
    routes, _ = keyword_routes(parsed, pairs, orphans, passes)
    validate_routes(routes)
    if (len(parsed["m_SubShaders"]) != 1
            or len(parsed["m_SubShaders"][0]["m_Passes"]) != 7
            or any(type(p.get("m_Type")) is not int or p["m_Type"] != 0
                   for p in parsed["m_SubShaders"][0]["m_Passes"])):
        raise ValueError("fft_utilities_original_normal_passes_required")
    layout, counts = shaderlab_layout(parsed, passes,
        expected_property_count=len(parsed['m_PropInfo']['m_Props']))
    private.mkdir(mode=0o700)
    folders = {}
    for index, (ident, record) in enumerate(distinct.items()):
        folder = private / ('program-%03d' % index)
        folder.mkdir(mode=0o700)
        folders[ident] = folder.name
        result = translate(record['source_code'], record['stage'], folder)
        if not all(result.get(key) is True for key in (
                'vulkan11_valid', 'hlsl_recovered', 'roundtrip_vulkan11_valid')):
            raise ValueError('fft_utilities_authentic_stage_translation_failed')
    stage_parameter_records(pairs, orphans, passes, table, private, folders)
    named = json.loads((private/'original-private-parameter-records.json').read_text())['stage_records']
    materialized = [dict(pair, **{stage: dict(pair[stage], program_ref=folders[pair[stage]['program_ref']])
                    for stage in ('vs','fs')}) for pair in pairs]
    dxc_shader = compose(private, materialized, named, layout)
    shader = compiler_control(dxc_shader, compiler_mode)
    (private/'fft-utilities-dxc-private.shader').write_text(dxc_shader)
    (private/'fft-utilities-private.shader').write_text(shader)
    verify_entrypoints(shader, private, routes=[[[]] for _ in range(7)])
    return dict(status=STATUS, candidate_shader_sha256=sha256(shader.encode()).hexdigest(),
        candidate_shader_bytes=len(shader.encode()), original_normal_passes=7,
        original_empty_keyword_routes_verified=True,
        compiler_control=compiler_mode,
        compiler_control_only_dxc_pragma_removed=compiler_mode == "hlslcc",
        dxc_candidate_shader_sha256=sha256(dxc_shader.encode()).hexdigest(),
        historical_failed_dxc_candidate_sha256=FAILED_DXC_CANDIDATE_SHA256,
        original_SHA_owned_serialized_files=2,
        original_passes=7, original_keyword_pairs=7, original_orphan_stages=0,
        original_distinct_D3D11_programs=12, original_stages_roundtrip_validated=12,
        named_ShaderLab_entrypoints_compiled=14,
        original_properties=counts['original_authored_property_count'],
        source_bytes_or_IDs_published=False, Unity_import_proven=False,
        Android_device_pixels_proven=False, APK_OBB_XAPK_created=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('original','private','out'):
        parser.add_argument('--'+key, type=Path, required=True)
    parser.add_argument("--compiler-control", choices=("dxc", "hlslcc"), default="dxc")
    args = parser.parse_args()
    if (args.out.exists() or args.out.is_symlink()
            or args.out.resolve().is_relative_to(args.original.resolve())
            or args.out.resolve().is_relative_to(args.private.resolve())):
        raise ValueError('fft_utilities_unsafe_safe_receipt_path')
    try:
        result = recover(args.original, args.private, compiler_mode=args.compiler_control)
    except Exception as exc:
        result = dict(status='INCONCLUSIVE', error_type=type(exc).__name__,
            source_bytes_or_IDs_published=False, Unity_import_proven=False,
            Android_device_pixels_proven=False, APK_OBB_XAPK_created=False)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print('GT_FFT_UTILITIES_SOURCE_SAFE '+json.dumps(result,sort_keys=True))
    return 0 if result['status'] == STATUS else 2

if __name__ == '__main__':
    raise SystemExit(main())
