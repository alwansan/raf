"""B46 synthetic positive and negative Material texture-reference fixtures."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
source=Path(__file__).resolve().parents[1]/"scripts"/"verify_exported_material_texture_links.py"
spec=importlib.util.spec_from_file_location("b46_exported_tex",source)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
A,B,C="a"*32,"b"*32,"c"*32

def material(ptr):
    return ("%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n"
            "  m_Shader: {fileID: 4800000, guid: "+"d"*32+", type: 3}\n"
            "  m_SavedProperties:\n    serializedVersion: 3\n    m_TexEnvs:\n"
            "    - _MainTex:\n        m_Texture: "+ptr+"\n"
            "        m_Scale: {x: 1, y: 1}\n        m_Offset: {x: 0, y: 0}\n"
            "    m_Ints: []\n    m_Floats: []\n    m_Colors: []\n")

class ExportedTextureLinks(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name); self.assets=self.root/"Assets"; self.assets.mkdir()
        (self.assets/"m.mat").write_text(material("{fileID: 2800000, guid: "+B+", type: 3}"))
        (self.assets/"m.mat.meta").write_text("guid: "+A+"\nNativeFormatImporter:\n")
        (self.assets/"t.png").write_bytes(b"synthetic-only image fixture")
        (self.assets/"t.png.meta").write_text("guid: "+B+"\nTextureImporter:\n")
    def ptr(self,p):
        (self.assets/"m.mat").write_text(material(p))
    def reject(self,reason):
        with self.assertRaises(mod.GuardError) as ctx: mod.audit(self.root)
        self.assertEqual(str(ctx.exception),reason)
    def test_valid_reference(self):
        r=mod.audit(self.root,1)
        self.assertEqual((r["texture_slots"],r["resolved_local_texture_refs"]),(1,1))
        self.assertFalse(r["ready_for_build"]); self.assertFalse(r["device_render_verified"])
        self.assertNotIn(B,str(r))
    def test_explicit_null(self):
        self.ptr("{fileID: 0}")
        self.assertEqual(mod.audit(self.root)["null_slots"],1)
    def test_builtin_unverified(self):
        self.ptr("{fileID: 10302, guid: 0000000000000000f000000000000000, type: 0}")
        self.assertEqual(mod.audit(self.root)["builtin_unverified_refs"],1)
    def test_local_embedded_requires_texture_class(self):
        self.ptr("{fileID: 2800000}")
        self.reject("unresolved_local_texture")
        with (self.assets/"m.mat").open("a") as fp: fp.write("--- !u!28 &2800000\nTexture2D:\n")
        self.assertEqual(mod.audit(self.root)["local_embedded_texture_refs"],1)
    def test_missing_target_guid(self):
        self.ptr("{fileID: 2800000, guid: "+C+", type: 3}")
        self.reject("missing_texture_guid")
    def test_wrong_asset_target(self):
        (self.assets/"t.png").rename(self.assets/"t.wav")
        (self.assets/"t.png.meta").rename(self.assets/"t.wav.meta")
        self.reject("reference_target_not_verified_texture")
    def test_wrong_importer(self):
        (self.assets/"t.png.meta").write_text("guid: "+B+"\nAudioImporter:\n")
        self.reject("reference_target_not_verified_texture")
    def test_duplicate_guid(self):
        (self.assets/"extra.png").write_bytes(b"x")
        (self.assets/"extra.png.meta").write_text("guid: "+B+"\nTextureImporter:\n")
        self.reject("duplicate_or_reserved_meta_guid")
    def test_negative_file_id(self):
        self.ptr("{fileID: -5, guid: "+B+", type: 3}")
        self.reject("negative_texture_file_id")
    def test_duplicate_pointer_keys(self):
        self.ptr("{fileID: 1, fileID: 2, guid: "+B+", type: 3}")
        self.reject("bad_texture_pointer")
    def test_valid_guid_wrong_texture_fileid_fails(self):
        self.ptr("{fileID: 2800001, guid: "+B+", type: 3}")
        self.reject("reference_target_not_verified_texture")
    def test_serialized_asset_texture_subobject_fileid(self):
        target=self.assets/"tex.asset"
        (self.assets/"t.png").rename(target)
        (self.assets/"t.png.meta").rename(self.assets/"tex.asset.meta")
        target.write_text("--- !u!28 &2800000\nTexture2D:\n")
        self.assertEqual(mod.audit(self.root)["resolved_local_texture_refs"],1)
        self.ptr("{fileID: 2800001, guid: "+B+", type: 3}")
        self.reject("reference_target_not_verified_texture")
    def test_wrong_pointer_type(self):
        self.ptr("{fileID: 2800000, guid: "+B+", type: 0}")
        self.reject("invalid_external_texture_type")
    def test_missing_texture_field(self):
        p=self.assets/"m.mat"; p.write_text(p.read_text().replace("m_Texture:","m_Broken:"))
        self.reject("missing_or_duplicate_texture_pointer")
    def test_duplicate_texture_field(self):
        p=self.assets/"m.mat"; p.write_text(p.read_text().replace("        m_Scale:","        m_Texture: {fileID: 0}\n        m_Scale:"))
        self.reject("missing_or_duplicate_texture_pointer")
    def test_explicit_empty_list(self):
        p=self.assets/"m.mat"; s=p.read_text()
        p.write_text(s[:s.index("    m_TexEnvs:")]+"    m_TexEnvs: []\n"+s[s.index("    m_Ints: []"):])
        self.assertEqual(mod.audit(self.root)["texture_slots"],0)
    def test_explicit_empty_array_with_child_slot_is_rejected(self):
        # A textual [] must not silently hide a nested - _MainTex entry.
        p=self.assets/"m.mat"; s=p.read_text()
        p.write_text(s.replace("    m_TexEnvs:\n", "    m_TexEnvs: []\n", 1))
        self.reject("unexpected_texenv_content")
    def test_nonempty_array_with_unrecognized_prefix_is_rejected(self):
        # A stray YAML key before the first texture slot cannot be ignored.
        p=self.assets/"m.mat"; s=p.read_text()
        p.write_text(s.replace("    m_TexEnvs:\n", "    m_TexEnvs:\n    bogus_member: invalid\n", 1))
        self.reject("unrecognized_texenv_prefix")
    def test_texture_field_at_wrong_indentation_is_rejected(self):
        # Previously a field outside the exact 8-space slot scope could
        # be mistaken for the actual Unity Material texture pointer.
        p=self.assets/"m.mat"; s=p.read_text()
        p.write_text(s.replace("        m_Texture: ", "      m_Texture: ", 1))
        self.reject("missing_or_duplicate_texture_pointer")

    def test_asset_ripper_mapping_style_texenv_restores_actual_texture_pointer(self):
        # Real AssetRipper can serialize m_TexEnvs as a mapping rather than a
        # sequence; fail closed on bad pointers in either representation.
        p=self.assets/"m.mat"
        p.write_text(p.read_text().replace("    - _MainTex:\n", "      _MainTex:\n"))
        r=mod.audit(self.root,1)
        self.assertEqual(r["texture_slots"],1)
        self.assertEqual(r["resolved_local_texture_refs"],1)
        self.assertTrue(r["export_texture_guid_target_integrity_verified"])
        self.ptr("{fileID: 2800000, guid: "+C+", type: 3}")
        p.write_text(p.read_text().replace("    - _MainTex:\n", "      _MainTex:\n"))
        self.reject("missing_texture_guid")

    def test_mapping_style_explicit_empty_mapping_and_malformed_child(self):
        p=self.assets/"m.mat"
        s=p.read_text()
        p.write_text(s[:s.index("    m_TexEnvs:")]+"    m_TexEnvs: {}\n"
            +s[s.index("    m_Ints: []"):])
        self.assertEqual(mod.audit(self.root)["texture_slots"],0)
        p.write_text(p.read_text().replace("    m_TexEnvs: {}\n",
            "    m_TexEnvs: {}\n      _MainTex:\n        m_Texture: {fileID: 0}\n"))
        self.reject("unexpected_texenv_content")

    def test_texenv_mixed_mapping_and_sequence_refused(self):
        p=self.assets/"m.mat"
        p.write_text(p.read_text().replace(
            "    - _MainTex:\n",
            "    - _MainTex:\n"
            "      _Extra:\n        m_Texture: {fileID: 0}\n"))
        self.reject("mixed_texenv_slot_encodings")

    def test_implicit_empty_rejected(self):
        p=self.assets/"m.mat"; s=p.read_text()
        p.write_text(s[:s.index("    m_TexEnvs:")]+"    m_TexEnvs:\n"+s[s.index("    m_Ints: []"):])
        self.reject("empty_or_unrecognized_texenv")
    def test_wrong_material_count(self):
        with self.assertRaises(mod.GuardError) as ctx: mod.audit(self.root,2)
        self.assertEqual(str(ctx.exception),"expected_material_count_mismatch")
    def test_symlink_rejected(self):
        (self.assets/"escape.png").symlink_to(self.root/"outside")
        self.reject("unsafe_or_excessive_export")
    def test_invalid_saved_properties(self):
        p=self.assets/"m.mat"; p.write_text(p.read_text().replace("m_SavedProperties:","m_BrokenProperties:"))
        self.reject("invalid_saved_properties")
    def test_error_output_excludes_guid_and_path(self):
        import io,contextlib
        self.ptr("{fileID: 2800000, guid: "+C+", type: 3}")
        out=io.StringIO()
        with contextlib.redirect_stdout(out): self.assertEqual(mod.main(["--project",str(self.root)]),2)
        self.assertNotIn(C,out.getvalue()); self.assertNotIn("m.mat",out.getvalue())

if __name__=="__main__": unittest.main()
