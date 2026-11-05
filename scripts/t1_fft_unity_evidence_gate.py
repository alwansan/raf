"""Fail-closed classification of sanitized Unity FFT candidate observations.

Synthetic candidate main kernels are never original game runtime identities.
"""
import json

FIELDS = {'editor_invoked', 'editor_supports_compute', 'candidate_assets_imported',
          'candidate_main_kernels_resolved', 'expected_threadgroups_matched',
          'observed_errors', 'original_authored_compute_restored',
          'original_runtime_kernel_mapping_proven', 'android_gpu_or_pixels_verified'}
COUNTS = ('candidate_assets_imported', 'candidate_main_kernels_resolved',
          'expected_threadgroups_matched', 'observed_errors')


def classify(record):
    if not isinstance(record, dict) or set(record) != FIELDS:
        raise ValueError('missing or unexpected Unity evidence fields')
    if type(record['editor_invoked']) is not bool or type(record['editor_supports_compute']) is not bool:
        raise ValueError('invalid boolean evidence')
    if any(type(record[k]) is not int or not 0 <= record[k] <= 20 for k in COUNTS):
        raise ValueError('invalid aggregate count')
    if any(record[k] is not False for k in ('original_authored_compute_restored',
            'original_runtime_kernel_mapping_proven', 'android_gpu_or_pixels_verified')):
        raise ValueError('source-derived probe cannot assert original/device proof')
    imported, resolved, groups, errors = (record[k] for k in COUNTS)
    if resolved > imported or groups > resolved:
        raise ValueError('impossible Unity observation counts')
    if not record['editor_invoked'] and (imported or resolved or groups):
        raise ValueError('observation without editor invocation')
    if not record['editor_supports_compute'] and (resolved or groups):
        raise ValueError('kernel probe without compute support')
    return {
        'candidate_import_proven': bool(record['editor_invoked'] and imported == 20 and errors == 0),
        'synthetic_main_runtime_probe_proven': bool(record['editor_invoked'] and record['editor_supports_compute'] and imported == resolved == groups == 20 and errors == 0),
        'original_game_kernel_mapping_proven': False,
        'android_device_proven': False,
    }


def main():
    import argparse
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument('sanitized_json', type=Path)
    args = p.parse_args()
    if args.sanitized_json.is_symlink() or args.sanitized_json.stat().st_size > 4096:
        p.error('invalid evidence file')
    print(json.dumps(classify(json.loads(args.sanitized_json.read_text())), sort_keys=True))


if __name__ == '__main__':
    main()
