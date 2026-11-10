#!/usr/bin/env python3
"""Validate material/pass identity before comparing private render-state summaries.

No source authenticity or Android visual correctness is established by this tool.
"""
import argparse
import json
import re
from pathlib import Path
from t3_render_state_pair_diff import compare, _unique_object_pairs

HEX64 = re.compile(r"[0-9a-f]{64}\Z")
GUID = re.compile(r"[0-9a-f]{32}\Z")
FIELDS = frozenset(('material_guid', 'shader_guid', 'pass_index', 'source_sha256', 'states'))


def check_record(record):
    if type(record) is not dict or set(record) != FIELDS:
        raise ValueError('invalid_envelope_fields')
    for key in ('material_guid', 'shader_guid'):
        if type(record[key]) is not str or not GUID.fullmatch(record[key]):
            raise ValueError('invalid_' + key)
    if type(record['pass_index']) is not int or not 0 <= record['pass_index'] <= 4095:
        raise ValueError('invalid_pass_index')
    digest = record['source_sha256']
    if type(digest) is not str or not HEX64.fullmatch(digest):
        raise ValueError('invalid_source_sha256')
    if type(record['states']) is not dict:
        raise ValueError('invalid_states')


def pair(original, exported):
    check_record(original)
    check_record(exported)
    keys = ('material_guid', 'shader_guid', 'pass_index')
    different = [key for key in keys if original[key] != exported[key]]
    if different:
        raise ValueError('identity_mismatch:' + ','.join(different))
    result = compare(original['states'], exported['states'])
    result['pair_identity_checked'] = True
    result['source_digests_format_checked'] = True
    result['source_digests_content_verified'] = False
    return result


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'),
                      object_pairs_hook=_unique_object_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite_json_value')))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('original', type=Path)
    p.add_argument('exported', type=Path)
    args = p.parse_args()
    print(json.dumps(pair(load(args.original), load(args.exported)), sort_keys=True))


if __name__ == '__main__':
    main()
