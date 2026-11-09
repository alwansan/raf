#!/usr/bin/env python3
"""Fail-closed comparison of sanitized original/export smoke Shader48 evidence.

Input JSON is a metadata-only report; never pass proprietary shader sources.
"""
import argparse
import json
from pathlib import Path

FIELDS = ('blend_enabled', 'alpha_test', 'alpha_blend', 'program_present')

def audit(data):
    if data.get('schema') != 't3-smoke-render-state-v1':
        raise ValueError('unsupported_schema')
    original, exported = data['original'], data['exported']
    for side in (original, exported):
        if side.get('identity_role') != 'smoke_linked_34_use_shader48':
            raise ValueError('wrong_shader_identity')
        if side.get('smoke_named_renderer_count') != 17 or side.get('material_slot_count') != 34:
            raise ValueError('graph_count_not_verified')
        if not side.get('source_sha256') or len(side['source_sha256']) != 64:
            raise ValueError('missing_source_fingerprint')
        for key in FIELDS:
            if type(side.get(key)) is not bool:
                raise ValueError('unknown_render_state:' + key)
    if original['source_sha256'] != exported['source_sha256']:
        raise ValueError('different_original_source')
    mismatches = [key for key in FIELDS if original[key] != exported[key]]
    return {'status': 'STATE_MISMATCH' if mismatches else 'SCOPED_STATE_MATCH',
            'mismatches': mismatches, 'device_pixels_proven': False,
            'shader_program_authenticity_proven': False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('metadata_json', type=Path)
    args = p.parse_args()
    print(json.dumps(audit(json.loads(args.metadata_json.read_text())), sort_keys=True))

if __name__ == '__main__':
    main()
