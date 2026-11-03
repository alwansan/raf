"""Prepare full original-shader engine identity coverage, no game source export."""
import argparse
import json
from pathlib import Path

from scripts.a12_probe_original_blur_passes import SHADER_OWNERS, ORIGINAL_SHADER_OBJECTS
from scripts.w1_match_embedded_engine_shaders import index_records, classify
from scripts.w1_prepare_engine_unity import material
from scripts.w1_stage_zip2_owners import fingerprint


def prepare(source, database, summary, project, out):
    import UnityPy
    from scripts.restore_builtin_shaders import archive_sources, download
    reader = json.loads(summary.read_text())
    table = index_records(json.loads(database.read_text()), reader)
    official, _, _ = archive_sources(download())
    keys = []
    for name, pin in SHADER_OWNERS.items():
        path = source / 'Raft_Data' / name
        if fingerprint(path) != pin:
            raise ValueError('Original full shader owner changed')
        for obj in UnityPy.load(str(path)).objects:
            if obj.type.name == 'Shader':
                parsed = obj.read_typetree()['m_ParsedForm']
                keys.append((parsed['m_Name'], tuple(p['m_Name'] for p in parsed['m_PropInfo']['m_Props'])))
    if len(keys) != ORIGINAL_SHADER_OBJECTS:
        raise ValueError('Full original shader inventory mismatch')
    counts = classify(keys, table, set(official))
    # Retain aggregate evidence even if a genuine remaining identity is
    # unsupported. Never omit it merely to prepare a successful Unity project.
    out.write_text(json.dumps({**counts, 'original_owner_count': len(SHADER_OWNERS),
                               'private_project_prepared': False}, sort_keys=True) + '\n')
    if counts.get('vendor_keys_unresolved_or_ambiguous', 0) or counts.get('ambiguous_engine_keys', 0):
        raise ValueError('Original built-in shader key unresolved')
    selected = {key: table[key][0] for key in keys if len(table.get(key, [])) == 1}
    if not 9 <= len(selected) <= 165:
        raise ValueError('Full original engine intersection outside expected bounds')
    if project.exists():
        raise ValueError('Refusing to overwrite private probe project')
    for directory in ('Assets/Editor', 'Assets/EngineMaterials', 'Assets/NegativeControls', 'Packages', 'ProjectSettings'):
        (project / directory).mkdir(parents=True, exist_ok=True)
    (project / 'Packages/manifest.json').write_text('{"dependencies":{}}\n')
    (project / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 2021.3.45f2\n')
    rows = sorted(selected.items())
    expected = []
    for i, ((name, properties), pointer) in enumerate(rows):
        other = next(value for (other_name, _), value in rows if other_name != name)
        positive = 'Assets/EngineMaterials/Probe%d.mat' % i
        negative = 'Assets/NegativeControls/Probe%d.mat' % i
        (project / positive).write_text(material('W1FullEngine%d' % i, pointer))
        (project / negative).write_text(material('W1WrongFullEngine%d' % i, other))
        expected.append({'assetPath': positive, 'wrongAssetPath': negative, 'shaderName': name,
                         'properties': list(properties)})
    (project / 'engine-expected-private.json').write_text(json.dumps({'items': expected}))
    result = {**counts, 'original_owner_count': len(SHADER_OWNERS),
              'original_verified_bytes': sum(pin[0] for pin in SHADER_OWNERS.values()),
              'unique_private_positive_materials': len(selected), 'wrong_pointer_controls': len(selected),
              'unity_binding_verified': False, 'actual_complete_export_graph_verified': False,
              'original_names_or_ids_published': False}
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('RAFT_W1_FULL_ENGINE_MAP ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--private-database', type=Path, required=True)
    p.add_argument('--reader-summary', type=Path, required=True)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    prepare(a.source, a.private_database, a.reader_summary, a.project, a.out)
