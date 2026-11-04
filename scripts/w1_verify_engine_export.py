"""Authenticate engine PPtr coverage without accepting a readiness receipt.

Original files and exact exporter metadata are read again. Reports contain only
counts and digests. This experiment does not relax the production shader gates.
Use --project at the complete export boundary BEFORE shader restorers add files.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from scripts.w1_match_embedded_engine_shaders import index_records
from scripts.w1_audit_export_material_shaders import inventory
from scripts.w1_stage_zip2_owners import fingerprint

READER_PINS = {
    'sourcegenerated_version': '1.3.2.0',
    'generated_assembly_sha256': '7aedba39a03b7d3fa4837a4a47fb2795780c1670a71b2c4dbca88613b8d231fd',
    'selected_shader_type': 'AssetRipper.SourceGenerated.Classes.ClassID_48.Shader_2021_3_35',
    'selected_unity_version': '2021.3.45f2',
    'release_name_copy_verified': True,
    'editor_name_copy_verified': True,
    'engine_dataset_version': '2021.2.0b14',
    'tpk_sha256': 'be9863e90b424b3cbe42caea675e5ae36179d62df2c55d41ef19d217992a8b12',
    'dataset_json_sha256': '72370e5ba37150a4cba193a5c5eca7ebfaece93f97730b5405e9152100c4fc93',
    'default_shader_records': 6,
    'extra_shader_records': 190,
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def exact_table(rows, reader):
    # A syntactically valid hash or a true receipt is not sufficient.
    if any(type(reader.get(k)) is not type(v) or reader.get(k) != v for k, v in READER_PINS.items()):
        raise ValueError('Exact generated reader or engine dataset fingerprint changed')
    kinds = Counter(row.get('engine_kind') for row in rows)
    if kinds != Counter(default=6, extra=190):
        raise ValueError('Exact engine dataset partition changed')
    return index_records(rows, reader)


def original_keys(source):
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS, ORIGINAL_SHADER_OBJECTS
    keys = []
    for name, pin in SHADER_OWNERS.items():
        path = source / 'Raft_Data' / name
        if path.is_symlink() or fingerprint(path) != pin:
            raise ValueError('Original shader owner fingerprint changed')
        for obj in UnityPy.load(str(path)).objects:
            if obj.type.name == 'Shader':
                parsed = obj.read_typetree()['m_ParsedForm']
                keys.append((parsed['m_Name'], tuple(p['m_Name'] for p in parsed['m_PropInfo']['m_Props'])))
    if len(keys) != ORIGINAL_SHADER_OBJECTS:
        raise ValueError('Original full shader inventory changed')
    return keys


def original_binding_map(keys, table):
    engine = {}
    custom = []
    seen = set()
    for key in keys:
        if not key[0] or key in seen:
            raise ValueError('Empty or duplicate original shader key')
        seen.add(key)
        choices = table.get(key, [])
        if len(choices) > 1:
            raise ValueError('Ambiguous original engine identity')
        if choices:
            if choices[0] in engine:
                raise ValueError('Original keys alias one engine pointer')
            engine[choices[0]] = key
        else:
            custom.append(key)
    return engine, custom


def verify_histogram(graph, engine):
    rows = graph.get('internal_pointer_histogram')
    if not isinstance(rows, list) or not rows:
        raise ValueError('No observed engine pointers')
    seen = set()
    total = 0
    for row in rows:
        if set(row) != {'engine_kind', 'file_id', 'references'}:
            raise ValueError('Unexpected engine histogram schema')
        if (row['engine_kind'] not in ('default', 'extra') or
                type(row['file_id']) is not int or type(row['references']) is not int or row['references'] <= 0):
            raise ValueError('Invalid engine histogram values')
        pointer = (row['engine_kind'], row['file_id'])
        if pointer in seen or pointer not in engine:
            raise ValueError('Duplicate or unmapped original engine pointer')
        seen.add(pointer)
        total += row['references']
    if (graph.get('counts', {}).get('internal_engine_references') != total or
            type(graph['counts']['internal_engine_references']) is not int):
        raise ValueError('Engine histogram count mismatch')
    return {'source_mapped_internal_references': total, 'source_mapped_unique_engine_pointers': len(seen)}


def verify_export(project, engine, custom):
    from scripts.restore_builtin_shaders import exported_shader_identity
    graph = inventory(project)
    if not graph['reference_inventory_complete']:
        raise ValueError('Actual export shader references or original metadata incomplete')
    names = defaultdict(list)
    for path in (project / 'Assets').rglob('*.shader'):
        name = exported_shader_identity(path.read_text(encoding='utf-8-sig'))
        if name:
            names[name].append(path)
    for name, _ in custom:
        if len(names.get(name, [])) != 1:
            raise ValueError('Original non-engine Shader export missing or ambiguous')
    return {**verify_histogram(graph, engine), 'original_non_engine_exports_covered': len(custom),
            'actual_export_reference_closure_verified': True,
            'actual_export_material_documents': graph['counts']['material_documents'],
            'actual_export_exported_shader_references': graph['counts'].get('resolved_exported_shader_references', 0)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--private-database', type=Path, required=True)
    p.add_argument('--reader-summary', type=Path, required=True)
    p.add_argument('--observed-evidence', type=Path, required=True)
    p.add_argument('--project', type=Path)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.project and a.out.resolve().is_relative_to(a.project.resolve()):
        raise ValueError('Aggregate report must stay outside original export')
    rows = json.loads(a.private_database.read_text())
    table = exact_table(rows, json.loads(a.reader_summary.read_text()))
    keys = original_keys(a.source)
    engine, custom = original_binding_map(keys, table)
    if len(engine) != 25 or len(custom) != 140:
        raise ValueError('Original165 shader classification changed')
    evidence = json.loads(a.observed_evidence.read_text())
    result = {**verify_histogram(evidence['inventory'], engine),
              'original_shader_objects': len(keys), 'original_engine_shader_keys': len(engine),
              'original_non_engine_shader_keys': len(custom), 'exact_engine_records': len(rows),
              'observed_run_id': evidence['run_id'], 'observed_source_sha': evidence['source_sha'],
              'observed_inventory_errors': evidence['inventory']['errors'],
              'exact_engine_records_digest': digest(rows),
              'original_engine_binding_digest': digest(sorted((kind, pointer, name, props)
                                                          for (kind, pointer), (name, props) in engine.items())),
              'actual_export_reference_closure_verified': False,
              'original_material_associations_verified': False,
              'compiled_program_equivalence_verified': False,
              'production_gates_changed': False, 'unity_or_device_executed': False}
    if a.project:
        result.update(verify_export(a.project, engine, custom))
    a.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('RAFT_W1_SOURCE_LINKED_ENGINE_EXPORT ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
