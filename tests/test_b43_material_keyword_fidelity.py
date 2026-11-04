"""B43 bounded positive and negative controls; synthetic data only."""
import unittest
from scripts.b43_material_keyword_fidelity import GuardError, parse_fields, compare, scalar
S=("sharedassets0.assets",14)
D=(2100000,"b"*32)
K=(("BAR","FOO"),("OLD",),())
T={"schema_version":1,"export_instance":"a"*32,"objects":[
    {"class_id":21,"source":{"owner":S[0],"path_id":S[1]},
     "export":{"file_id":D[0],"guid":D[1],"type":2},"exportable":True}]}

class KeywordFidelity(unittest.TestCase):
    def test_multiline(self):
        self.assertEqual(parse_fields("  m_ValidKeywords:\n  - FOO\n  - BAR\n"
                         "  m_InvalidKeywords:\n  - OLD\n  disabledShaderPasses: []\n  m_SavedProperties:\n"),K)
    def test_empty_base(self):
        self.assertEqual(parse_fields("  m_ValidKeywords: []\n  m_InvalidKeywords: []\n"
                                      "  disabledShaderPasses: []\n"),((),(),()))
    def test_success_not_pixel_proof(self):
        r=compare(T,{S:K},{D:K})
        self.assertTrue(r["keyword_state_equal"])
        self.assertFalse(r["unity_or_device_verified"])
        self.assertFalse(r["ready_for_build"])
    def test_loss_enabled(self):
        with self.assertRaisesRegex(GuardError,"mismatch"):
            compare(T,{S:K},{D:(("FOO",),("OLD",),())})
    def test_loss_invalid(self):
        with self.assertRaisesRegex(GuardError,"mismatch"):
            compare(T,{S:K},{D:(("BAR","FOO"),(),())})
    def test_disabled_pass(self):
        with self.assertRaisesRegex(GuardError,"mismatch"):
            compare(T,{S:K},{D:(("BAR","FOO"),("OLD",),("ShadowCaster",))})
    def test_wrong_export_guid(self):
        with self.assertRaisesRegex(GuardError,"identity"):
            compare(T,{S:K},{(D[0],"c"*32):K})
    def test_duplicate_source(self):
        with self.assertRaisesRegex(GuardError,"duplicate"):
            compare(dict(T,objects=T["objects"]*2),{S:K},{D:K})
    def test_missing_source(self):
        with self.assertRaisesRegex(GuardError,"missing"):
            compare(dict(T,objects=[]),{S:K},{})
    def test_bad_session(self):
        with self.assertRaisesRegex(GuardError,"instance"):
            compare(dict(T,export_instance="x"),{S:K},{D:K})
    def test_redirect(self):
        row=dict(T["objects"][0],exportable=False,
                 export={"file_id":2100000,"guid":"0000000000000000e000000000000000","type":0})
        self.assertEqual(compare(dict(T,objects=[row]),{S:K},{})["predefined_redirects"],1)
    def test_false_redirect(self):
        with self.assertRaisesRegex(GuardError,"redirect"):
            compare(dict(T,objects=[dict(T["objects"][0],exportable=False)]),{S:K},{})
    def test_field_failures(self):
        for body in ("  m_ValidKeywords: []\n  m_InvalidKeywords: []\n",
                     "  m_ValidKeywords: []\n  m_ValidKeywords: []\n"
                     "  m_InvalidKeywords: []\n  disabledShaderPasses: []\n",
                     "  m_ValidKeywords:\n  m_InvalidKeywords: []\n"
                     "  disabledShaderPasses: []\n"):
            with self.subTest(body=body),self.assertRaises(GuardError): parse_fields(body)
    def test_unsafe_scalars(self):
        for text in ("!obj","FOO BAR","FOO # comment"):
            with self.subTest(text=text),self.assertRaises(GuardError): scalar(text)

class ExportedYamlFileControls(unittest.TestCase):
    def test_real_yaml_path_and_same_instance_document_key(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from scripts.b43_material_keyword_fidelity import exported_materials
        with TemporaryDirectory() as td:
            assets=Path(td)/"Assets"
            assets.mkdir()
            mat=assets/"unit.mat"
            mat.write_text("%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n"
                           "  m_ValidKeywords:\n  - FOO\n  - BAR\n"
                           "  m_InvalidKeywords:\n  - OLD\n"
                           "  disabledShaderPasses: []\n  m_SavedProperties:\n",encoding="utf-8")
            (assets/"unit.mat.meta").write_text("fileFormatVersion: 2\nguid: "+"b"*32+"\n",encoding="utf-8")
            self.assertEqual(exported_materials(Path(td)),{D:K})
            self.assertTrue(compare(T,{S:K},exported_materials(Path(td)))["keyword_state_equal"])

    def test_yaml_loss_of_keyword_fails_after_parsing_actual_document(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from scripts.b43_material_keyword_fidelity import exported_materials
        with TemporaryDirectory() as td:
            assets=Path(td)/"Assets"
            assets.mkdir()
            mat=assets/"unit.mat"
            mat.write_text("%YAML 1.1\n--- !u!21 &2100000\nMaterial:\n"
                           "  m_ValidKeywords:\n  - FOO\n"
                           "  m_InvalidKeywords:\n  - OLD\n"
                           "  disabledShaderPasses: []\n  m_SavedProperties:\n",encoding="utf-8")
            (assets/"unit.mat.meta").write_text("fileFormatVersion: 2\nguid: "+"b"*32+"\n",encoding="utf-8")
            with self.assertRaisesRegex(GuardError,"mismatch"):
                compare(T,{S:K},exported_materials(Path(td)))

    def test_unsafe_export_symlink_is_rejected(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from scripts.b43_material_keyword_fidelity import exported_materials
        with TemporaryDirectory() as td:
            project=Path(td)
            (project/"Assets").mkdir()
            (project/"Assets"/"dangling.mat").symlink_to(project/"missing.mat")
            with self.assertRaisesRegex(GuardError,"symlink"):
                exported_materials(project)

if __name__=="__main__":unittest.main()
