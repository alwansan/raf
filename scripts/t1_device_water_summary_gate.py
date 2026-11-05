"""Fail-closed LogRaft water root-accounting gate; no runtime provenance claims."""
import argparse
import json
import re
from pathlib import Path

MATERIALS = ('spectrum', 'foam_global', 'subsurface_blur', 'utility_noise', 'other_ultimate_water')

def summarize(s):
    breakdown = s['final_render_failure_breakdown']
    materials = breakdown['ultimate_water_invalid_pass_by_material']
    kernels = breakdown['invalid_kernel_index_root_lines']
    if set(materials) != set(MATERIALS) or set(kernels) != {'index_6', 'other_index'}:
        raise ValueError('unrecognized root breakdown')
    categories = s['final_error_category_breakdown']
    def valid(n):
        if type(n) is not int or n < 0:
            raise ValueError('invalid count')
        return n
    passes = valid(categories['ultimate_water_invalid_pass']['count'])
    kernel_total = valid(categories['water_fft_invalid_compute_kernel']['count'])
    if sum(valid(v) for v in materials.values()) != passes or sum(valid(v) for v in kernels.values()) != kernel_total:
        raise ValueError('root count mismatch')
    keys = ('final_shader_pass_errors_total', 'final_compute_kernel_errors_total')
    stop_info = s.get('stop_time_android_process_exit_info', {})
    if not isinstance(stop_info, dict):
        raise ValueError('invalid stop-time counters')
    locations = [section for section in (s, stop_info) if any(key in section for key in keys)]
    if not locations:
        raise ValueError('missing final counters')
    for section in locations:
        if tuple(valid(section.get(key)) for key in keys) != (passes, kernel_total):
            raise ValueError('counter mismatch')
    session = s['session']
    if not isinstance(session, str) or not re.fullmatch(r'(?:LogRaft-)?[0-9]{8}-[0-9]{6}-[0-9]{3}', session):
        raise ValueError('invalid session identifier')
    session = 'LogRaft-' + session.removeprefix('LogRaft-')
    return {'session': session, 'invalid_pass_total': passes,
            'invalid_pass_by_material': materials, 'invalid_kernel_total': kernel_total,
            'invalid_kernel_by_index': kernels, 'kernel_index_6_is_fft_proven': False,
            'source_to_unity_kernel_mapping_proven': False,
            'android_water_rendering_restored': False,
            'scope': 'observed game-UID root lines; OS ring losses unknown'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('summaries', type=Path, nargs='+')
    a = p.parse_args()
    results = []
    for f in a.summaries:
        if f.is_symlink() or not f.is_file() or f.stat().st_size > 2_000_000:
            p.error('invalid input')
        results.append(summarize(json.loads(f.read_text(encoding='utf-8'))))
    print(json.dumps(results, sort_keys=True))

if __name__ == '__main__':
    main()
