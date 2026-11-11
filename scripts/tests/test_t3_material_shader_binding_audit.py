"""Synthetic-only regressions for material-to-shader GUID owner census."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from t3_material_shader_binding_audit import audit

G = 'a' * 32

class MaterialShaderAuditTest(unittest.TestCase):
    def test_unique_duplicate_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'a.shader.meta').write_text('guid: ' + G + '\n')
            (p / 'one.mat').write_text('Material:\n  m_Shader: {fileID: 4800000, guid: ' + G + ', type: 3}\n')
            self.assertEqual(audit(p)['counts']['shader_guid_unique_in_supplied_tree'], 1)
            (p / 'b.shader.meta').write_text('guid: ' + G + '\n')
            self.assertEqual(audit(p)['counts']['shader_guid_ambiguous_duplicate_meta'], 1)
            (p / 'one.mat').write_text('m_Shader: {fileID: 4800000, guid: ' + 'b' * 32 + ', type: 3}\n')
            self.assertEqual(audit(p)['counts']['shader_guid_not_in_supplied_tree'], 1)

    def test_null_and_builtin(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'null.mat').write_text('m_Shader: {fileID: 0}\n')
            (p / 'builtin.mat').write_text('m_Shader: {fileID: 48}\n')
            c = audit(p)['counts']
            self.assertEqual(c['shader_null_reference'], 1)
            self.assertEqual(c['shader_builtin_or_local_reference'], 1)

if __name__ == '__main__':
    unittest.main()
