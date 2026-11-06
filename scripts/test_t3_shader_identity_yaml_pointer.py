#!/usr/bin/env python3
"""Regression checks for the fail-closed post-restoration material pointer parser."""
import unittest
from t3_shader_identity_gate import PPTR

GUID = "a" * 32

class MaterialPointerYamlTests(unittest.TestCase):
    def test_real_pointer(self):
        self.assertEqual(PPTR.findall(f"m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}"), [GUID])

    def test_comment_is_not_pointer(self):
        self.assertEqual(PPTR.findall(f"# m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}"), [])

    def test_spacing_and_trailing_comment(self):
        self.assertEqual(PPTR.findall(f"  m_Shader: {{ fileID: 4800000 , guid: {GUID} , type: 3 }} # valid"), [GUID])

    def test_trailing_garbage_rejected(self):
        self.assertEqual(PPTR.findall(f"m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}garbage"), [])

    def test_duplicate_pointer_rejected_by_gate_contract(self):
        text = "\n".join([f"m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}"] * 2)
        self.assertNotEqual(PPTR.findall(text), [GUID])

if __name__ == "__main__":
    unittest.main()
