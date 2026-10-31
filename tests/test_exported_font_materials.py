from pathlib import Path
import tempfile
import unittest
from scripts.audit_exported_font_materials import audit,require_valid


class FontMaterialTests(unittest.TestCase):
    def test_strict_gate_refuses_incomplete_count_or_any_unresolved_material(self):
        require_valid({'counts':{'font_assets':13,'resolved_material_assets':13}},13)
        for counts in [{}, {'font_assets':13,'resolved_material_assets':12}, {'font_assets':12,'resolved_material_assets':12}]:
            with self.assertRaises(ValueError):require_valid({'counts':counts},13)
    def test_resolves_actual_material_and_distinguishes_null_missing_wrong_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); assets = root / 'Assets'; assets.mkdir()
            guid = 'a' * 32
            (assets/'mat.mat').write_text('--- !u!21 &2100000\nMaterial:\n')
            (assets/'mat.mat.meta').write_text('guid: '+guid+'\n')
            refs = ['  material: {fileID: 2100000, guid: '+guid+', type: 2}\n', '  material: {fileID: 0}\n', '  m_Material: {fileID: 0}\n']
            paths = []
            for i, text in enumerate(refs):
                name = str(i)+'.asset';paths.append(name);(assets/name).write_text(text)
            manifest = {'scripts': [{'fullTypeName': 'TMPro.TMP_FontAsset', 'usagePaths': paths}]}
            counts = audit(root, manifest)['counts']
            self.assertEqual(counts, {'font_assets': 3, 'resolved_material_assets': 1, 'null_material_reference': 1, 'missing_or_ambiguous_original_material_field': 1})
            (assets/'mat.mat').write_text('--- !u!114 &1\nMonoBehaviour:\n')
            self.assertEqual(audit(root, manifest)['counts']['reference_target_is_not_material'], 1)

    def test_rejects_path_outside_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);(root/'Assets').mkdir()
            with self.assertRaises(ValueError):
                audit(root, {'scripts': [{'fullTypeName': 'TMPro.TMP_FontAsset', 'usagePaths': ['../outside.asset']}]})

