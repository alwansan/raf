"""Prepare nine private material-pointer controls for a bounded Unity probe."""
import argparse
import json
from pathlib import Path

from scripts.w1_match_embedded_engine_shaders import index_records
from scripts.w1_stage_zip2_owners import PINS, fingerprint


def material(name, pointer):
    kind, file_id = pointer
    guid = {'default': '0000000000000000e000000000000000',
            'extra': '0000000000000000f000000000000000'}[kind]
    return ('%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n'
            '  serializedVersion: 6\n  m_ObjectHideFlags: 0\n  m_Name: ' + name + '\n'
            '  m_Shader: {fileID: ' + str(file_id) + ', guid: ' + guid + ', type: 0}\n'
            '  m_ShaderKeywords: \n  m_LightmapFlags: 4\n  m_EnableInstancingVariants: 0\n'
            '  m_DoubleSidedGI: 0\n  m_CustomRenderQueue: -1\n  stringTagMap: {}\n'
            '  disabledShaderPasses: []\n  m_SavedProperties:\n    serializedVersion: 3\n'
            '    m_TexEnvs: []\n    m_Floats: []\n    m_Colors: []\n')


def prepare(source, database, summary, project):
    import UnityPy
    table = index_records(json.loads(database.read_text()), json.loads(summary.read_text()))
    selected = {}
    for relative, pin in PINS.items():
        if '/Resources/' in relative:
            continue
        path = source / relative
        if fingerprint(path) != pin:
            raise ValueError('Original shader owner changed')
        for obj in UnityPy.load(str(path)).objects:
            if obj.type.name != 'Shader':
                continue
            parsed = obj.read_typetree()['m_ParsedForm']
            key = (parsed['m_Name'], tuple(p['m_Name'] for p in parsed['m_PropInfo']['m_Props']))
            choices = table.get(key, [])
            if len(choices) == 1:
                selected[key] = choices[0]
            elif choices:
                raise ValueError('Ambiguous original engine pointer')
    if len(selected) != 9:
        raise ValueError('Authenticated nine-shader engine intersection changed')
    if project.exists():
        raise ValueError('Refusing to overwrite probe project')
    (project / 'Assets/Editor').mkdir(parents=True)
    (project / 'Assets/EngineMaterials').mkdir()
    (project / 'Assets/NegativeControls').mkdir()
    (project / 'Packages').mkdir()
    (project / 'ProjectSettings').mkdir()
    (project / 'Packages/manifest.json').write_text('{"dependencies":{}}\n')
    (project / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 2021.3.45f2\n')
    rows = sorted(selected.items())
    expected = []
    for i, ((name, properties), pointer) in enumerate(rows):
        positive = 'Assets/EngineMaterials/Probe%d.mat' % i
        negative = 'Assets/NegativeControls/Probe%d.mat' % i
        (project / positive).write_text(material('W1EnginePointer%d' % i, pointer))
        # Different valid engine shader pointer; must not satisfy this key.
        (project / negative).write_text(material('W1WrongPointer%d' % i, rows[(i + 1) % len(rows)][1]))
        expected.append({'assetPath': positive, 'wrongAssetPath': negative,
                         'shaderName': name, 'properties': list(properties)})
    (project / 'engine-expected-private.json').write_text(json.dumps({'items': expected}))
    print('RAFT_W1_ENGINE_UNITY_PREPARE positiveMaterials=9 wrongPointerControls=9 gameProjectModified=false')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--private-database', type=Path, required=True)
    p.add_argument('--reader-summary', type=Path, required=True)
    p.add_argument('--project', type=Path, required=True)
    a = p.parse_args()
    prepare(a.source, a.private_database, a.reader_summary, a.project)
