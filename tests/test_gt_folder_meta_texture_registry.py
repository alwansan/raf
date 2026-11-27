"""Authored physical folder and file GUID namespace fixtures; no game data."""
import io
import contextlib
from pathlib import Path
import tempfile
import unittest

from scripts.verify_exported_material_texture_links import audit, GuardError, main

A,B,C,D=("a"*32,"b"*32,"c"*32,"d"*32)
PLACEHOLDER="0000000deadbeef15deadf00d0000000"


def material(guid=B):
    return ("%YAML 1.1\n--- !u!21 &2100000\nMaterial:\n"
            "  m_SavedProperties:\n    m_TexEnvs:\n    - _MainTex:\n"
            "        m_Texture: {fileID: 2800000, guid: "+guid+", type: 3}\n"
            "        m_Scale: {x: 1, y: 1}\n        m_Offset: {x: 0, y: 0}\n"
            "    m_Ints: []\n    m_Floats: []\n")


class FolderRegistry(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.assets=self.root/"Assets"
        self.assets.mkdir()
        self.mat=self.assets/"Material.mat"
        self.mat.write_text(material())
        self.texture=self.assets/"Texture.asset"
        self.texture.write_text("--- !u!28 &2800000\nTexture2D:\n")
        self.meta(self.mat,A)
        self.meta(self.texture,B)

    def sidecar(self,path):
        return Path(str(path)+".meta")

    def meta(self,path,guid,extra=""):
        self.sidecar(path).write_text("fileFormatVersion: 2\nguid: "+guid+"\n"+extra)

    def folder(self,name,guid=C,extra="folderAsset: yes\nDefaultImporter:\n"):
        path=self.assets/name
        path.mkdir(parents=True)
        self.meta(path,guid,extra)
        return path

    def rejects(self,reason):
        with self.assertRaises(GuardError) as exc:
            audit(self.root)
        self.assertEqual(str(exc.exception),reason)

    def test_valid_nested_folders_preserve_real_texture_target(self):
        parent=self.folder("Textures",C)
        nested=self.folder("Textures/World",D)
        for path in (self.texture,self.sidecar(self.texture)):
            path.rename(nested/path.name)
        with self.sidecar(parent).open("a") as fp:
            fp.write("  externalObjects:\n    item:\n      guid: "+B+"\n")
        result=audit(self.root,1)
        self.assertEqual(result["resolved_local_texture_refs"],1)
        self.assertEqual(result["registered_folder_guids"],2)
        self.assertEqual(result["registered_asset_guids"],2)
        self.assertFalse(result["source_export_equivalence_verified"])
        self.assertFalse(result["texture_pixel_color_verified"])
        self.assertFalse(result["ready_for_build"])
        self.assertNotIn(C,str(result))

    def test_valid_folder_with_texture_suffix_not_referenced(self):
        self.folder("Authored.png")
        result=audit(self.root)
        self.assertEqual(result["registered_folder_guids"],1)
        self.assertEqual(result["resolved_local_texture_refs"],1)

    def test_folder_bom_crlf_metadata(self):
        path=self.folder("CRLF")
        self.sidecar(path).write_bytes(b"\xef\xbb\xbf"+self.sidecar(path).read_bytes().replace(b"\n",b"\r\n"))
        self.assertEqual(audit(self.root)["registered_folder_guids"],1)

    def test_folder_marker_on_regular_texture_file(self):
        self.meta(self.texture,B,"folderAsset: yes\nNativeFormatImporter:\n")
        self.rejects("folder_meta_targets_file")

    def test_duplicate_malformed_root_guid_on_file(self):
        with self.sidecar(self.texture).open("a") as fp:
            fp.write("guid: invalid\n")
        self.rejects("missing_or_duplicate_meta_guid")

    def test_placeholder_identity_on_file_rejected(self):
        self.meta(self.texture,PLACEHOLDER)
        self.mat.write_text(material(PLACEHOLDER))
        self.rejects("duplicate_or_reserved_meta_guid")

    def test_directory_requires_folder_flag(self):
        self.folder("Unmarked",extra="DefaultImporter:\n")
        self.rejects("folder_meta_flag_required")

    def test_directory_cannot_declare_folder_no(self):
        self.folder("Wrong",extra="folderAsset: no\n")
        self.rejects("folder_meta_flag_required")

    def test_duplicate_folder_flag_rejected(self):
        self.folder("Duplicate",extra="folderAsset: yes\nfolderAsset: no\n")
        self.rejects("invalid_folder_meta_flag")

    def test_malformed_folder_flag_rejected(self):
        self.folder("Wrong",extra="folderAsset: maybe\n")
        self.rejects("invalid_folder_meta_flag")

    def test_nested_folder_flag_is_not_root_flag(self):
        self.folder("Nested",extra="DefaultImporter:\n  folderAsset: yes\n")
        self.rejects("folder_meta_flag_required")

    def test_orphan_folder_sidecar_rejected(self):
        self.meta(self.assets/"Missing",C,"folderAsset: yes\n")
        self.rejects("orphan_asset_meta")

    def test_folder_vs_texture_guid_collision(self):
        self.folder("Collision",B.upper())
        self.rejects("duplicate_or_reserved_meta_guid")

    def test_folder_vs_folder_guid_collision(self):
        self.folder("First",C)
        self.folder("Second",C.upper())
        self.rejects("duplicate_or_reserved_meta_guid")

    def test_reserved_folder_guids_rejected(self):
        for guid in ("0"*32,"0000000000000000e000000000000000",
                     "0000000000000000f000000000000000",PLACEHOLDER):
            with self.subTest(guid_class=guid[:8]):
                folder=self.folder("Reserved",guid)
                try:
                    self.rejects("duplicate_or_reserved_meta_guid")
                finally:
                    self.sidecar(folder).unlink()
                    folder.rmdir()

    def test_folder_never_resolves_as_texture(self):
        folder=self.folder("Pretend.png",C,"folderAsset: yes\nTextureImporter:\n")
        self.mat.write_text(material(C))
        self.rejects("reference_target_not_verified_texture")
        folder.rename(self.assets/"Pretend.asset")
        self.sidecar(folder).rename(self.assets/"Pretend.asset.meta")
        self.rejects("reference_target_not_verified_texture")

    def test_linked_directory_rejected(self):
        outside=self.root/"outside"
        outside.mkdir()
        path=self.assets/"Linked"
        path.symlink_to(outside,target_is_directory=True)
        self.meta(path,C,"folderAsset: yes\n")
        self.rejects("unsafe_or_excessive_export")

    def test_meta_directory_not_a_sidecar(self):
        (self.assets/"Fake.meta").mkdir()
        self.rejects("unsafe_or_excessive_export")

    def test_noncanonical_meta_suffix_rejected(self):
        path=self.folder("Case")
        self.sidecar(path).rename(self.assets/"Case.META")
        self.rejects("noncanonical_meta_suffix")

    def test_file_with_explicit_no_still_eligible(self):
        self.meta(self.texture,B,"folderAsset: no\nNativeFormatImporter:\n")
        self.assertEqual(audit(self.root)["resolved_local_texture_refs"],1)

    def test_cli_rejection_is_private(self):
        self.folder("SensitiveAuthoredName",B)
        buf=io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(main(["--project",str(self.root)]),2)
        self.assertIn("duplicate_or_reserved_meta_guid",buf.getvalue())
        self.assertNotIn(B,buf.getvalue())
        self.assertNotIn("SensitiveAuthoredName",buf.getvalue())


if __name__=="__main__":
    unittest.main()
