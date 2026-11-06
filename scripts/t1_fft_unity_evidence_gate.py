"""Fail-closed classification of sanitized Unity FFT candidate observations.

Synthetic candidate main kernels are never original game runtime identities.
"""
import json
import os
import stat

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
    if not record['editor_invoked'] and record['editor_supports_compute']:
        raise ValueError('compute support claimed without editor invocation')
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



def parse_sanitized_json(raw):
    """Reject duplicate keys before classifying an untrusted evidence record."""
    def unique_pairs(pairs):
        record = {}
        for key, value in pairs:
            if key in record:
                raise ValueError('duplicate Unity evidence field')
            record[key] = value
        return record
    return classify(json.loads(raw, object_pairs_hook=unique_pairs))


def read_sanitized_evidence(path):
    """Read at most 4096 bytes from one regular file descriptor, without following symlinks."""
    flags = os.O_RDONLY | getattr(os, 'O_CLOEXEC', 0)
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    else:
        # On platforms without O_NOFOLLOW, reject links before opening.
        if path.is_symlink():
            raise ValueError('invalid evidence file')
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > 4096:
            raise ValueError('invalid evidence file')
        data = os.read(fd, 4097)
        if len(data) > 4096:
            raise ValueError('invalid evidence file')
        return parse_sanitized_json(data.decode('utf-8', errors='strict'))
    finally:
        os.close(fd)


def main():
    import argparse
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument('sanitized_json', type=Path)
    args = p.parse_args()
    try:
        result = read_sanitized_evidence(args.sanitized_json)
    except (OSError, UnicodeError, ValueError) as exc:
        p.error('invalid evidence file: ' + type(exc).__name__)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
