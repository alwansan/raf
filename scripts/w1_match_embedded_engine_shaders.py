"""Compare authenticated original shader keys to exact private exporter engine DB."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from scripts.w1_stage_zip2_owners import PINS, fingerprint


def index_records(rows, reader):
    if (reader.get('release_name_copy_verified') is not True or
            reader.get('editor_name_copy_verified') is not True or
            reader.get('selected_unity_version') != '2021.3.45f2' or
            not re.fullmatch('[0-9a-f]{64}', reader.get('generated_assembly_sha256', ''))):
        raise ValueError('Exact original reader contract unverified')
    if not isinstance(rows, list) or not 1 <= len(rows) <= 2048:
        raise ValueError('Invalid private engine dataset')
    expected = reader['default_shader_records'] + reader['extra_shader_records']
    if len(rows) != expected:
        raise ValueError('Private dataset count mismatch')
    result = defaultdict(list)
    seen = set()
    for row in rows:
        if set(row) != {'name', 'properties', 'file_id', 'engine_kind'}:
            raise ValueError('Private engine record schema mismatch')
        if (not isinstance(row['name'], str) or not row['name'] or
                not isinstance(row['properties'], list) or
                not all(isinstance(x, str) for x in row['properties']) or
                type(row['file_id']) is not int or row['engine_kind'] not in ('default', 'extra')):
            raise ValueError('Private engine record values invalid')
        pointer = (row['engine_kind'], row['file_id'])
        if pointer in seen:
            raise ValueError('Duplicate original engine pointer')
        seen.add(pointer)
        result[(row['name'], tuple(row['properties']))].append(pointer)
    return result


def classify(keys, table, vendor_names):
    counts = Counter()
    for name, properties in keys:
        choices = table.get((name, properties), [])
        counts['original_shader_objects'] += 1
        if name in vendor_names:
            counts['original_official_vendor_name_objects'] += 1
            counts['vendor_keys_uniquely_mapped' if len(choices) == 1 else 'vendor_keys_unresolved_or_ambiguous'] += 1
        if len(choices) == 1:
            counts['exact_engine_keys_uniquely_mapped'] += 1
            # Adding an absent property and changing the name must not be
            # accepted as the same exact engine identity. Never drop properties.
            if table.get((name, properties + ('__w1_wrong_property__',))) or table.get(('__w1_wrong_name__' + name, properties)):
                raise ValueError('Original engine identity negative control failed')
            counts['wrong_name_and_property_controls_detected'] += 2
        elif choices:
            counts['ambiguous_engine_keys'] += 1
        else:
            counts['nonmatching_engine_keys'] += 1
    return dict(counts)


def main(source, private_database, reader_summary, out):
    import UnityPy
    from scripts.restore_builtin_shaders import archive_sources, download
    reader = json.loads(reader_summary.read_text())
    table = index_records(json.loads(private_database.read_text()), reader)
    official, _, _ = archive_sources(download())
    keys = []
    for relative, pin in PINS.items():
        if '/Resources/' in relative:
            continue
        path = source / relative
        if fingerprint(path) != pin:
            raise ValueError('Original shader owner fingerprint mismatch')
        env = UnityPy.load(str(path))
        for obj in env.objects:
            if obj.type.name == 'Shader':
                parsed = obj.read_typetree()['m_ParsedForm']
                keys.append((parsed['m_Name'], tuple(p['m_Name'] for p in parsed['m_PropInfo']['m_Props'])))
    if len(keys) != 105:
        raise ValueError('Original two-owner shader inventory mismatch')
    result = {**classify(keys, table, set(official)),
              'reader_contract': reader, 'private_engine_names_or_ids_published': False,
              'actual_export_material_engine_ptrs_verified': False,
              'strict_zero_match_gate_changed': False, 'unity_or_android_executed': False}
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('RAFT_W1_ORIGINAL_ENGINE_KEY_MAPPING ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--private-database', required=True, type=Path)
    p.add_argument('--reader-summary', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    main(a.source, a.private_database, a.reader_summary, a.out)
