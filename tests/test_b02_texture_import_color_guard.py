#!/usr/bin/env python3
"""Isolated B02 positive/negative TextureImporter sRGB source-fidelity controls."""
import hashlib
import json
from pathlib import Path
import tempfile
import types
import sys
from unittest import TestCase, main, mock

from scripts import b02_texture_import_color_guard as m

SHA = hashlib.sha256(b"original").hexdigest()


class TestB02TextureImport(TestCase):
    def setUp(self):
        self.pinned = mock.patch.dict(m.PINNED_SOURCE, {"source.assets": (8, SHA)})
        self.pinned.start()
        self.addCleanup(self.pinned.stop)
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        self.assets = self.root / "export" / "Assets" / "Textures"
        self.assets.mkdir(parents=True)
        (self.assets / "one.png").write_bytes(b"pixel-fixture")
        self.guid = "a" * 32
        self.meta = self.assets / "one.png.meta"
        self.set_meta(0)
        self.map = {
            "schema_version": 1,
            "source_commit": m.ZIP2_SHA,
            "textures": [{
                "source_owner": "source.assets",
                "source_owner_bytes": 8,
                "source_owner_sha256": SHA,
                "source_path_id": 123,
                "source_color_space": 0,
                "export_asset": "Textures/one.png",
                "export_guid": self.guid,
            }],
        }

    def set_meta(self, srgb, extra=""):
        self.meta.write_text(
            f"fileFormatVersion: 2\nguid: {self.guid}\nTextureImporter:\n  sRGBTexture: {srgb}\n" + extra,
            encoding="utf-8",
        )

    def run_audit(self, **kw):
        return m.inspect(self.root / "export", self.map, **kw)

    def test_mismatch_is_reported_not_silently_normalized(self):
        r = self.run_audit()
        self.assertEqual((r["rows"], r["matching_before"], r["mismatched_before"]), (1, 0, 1))
        self.assertFalse(r["source_bytes_and_colorspace_verified"])
        self.assertFalse(r["same_export_linkage_independently_verified"])
        self.assertIn("sRGBTexture: 0", self.meta.read_text())

    def test_gamma_expected_srgb_linear_expected_false(self):
        self.set_meta(1)
        self.assertEqual(self.run_audit()["matching_before"], 1)
        self.map["textures"][0]["source_color_space"] = 1
        self.set_meta(0)
        self.assertEqual(self.run_audit()["matching_before"], 1)

    def test_unpinned_source_digest_and_owner_are_rejected(self):
        self.map["textures"][0]["source_owner_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "trusted pinset"):
            self.run_audit()
        self.map["textures"][0]["source_owner_sha256"] = SHA
        self.map["textures"][0]["source_owner"] = "unknown.assets"
        with self.assertRaisesRegex(ValueError, "trusted pinset"):
            self.run_audit()

    def test_source_color_boolean_is_not_valid_integer_enum(self):
        source = self.root / "source"
        source.mkdir()
        (source / "source.assets").write_bytes(b"original")
        obj = types.SimpleNamespace(path_id=123, type=types.SimpleNamespace(name="Texture2D"),
                                    read_typetree=lambda: {"m_ColorSpace": False})
        module = types.SimpleNamespace(load=lambda path: types.SimpleNamespace(objects=[obj]))
        with mock.patch.dict(sys.modules, {"UnityPy": module}):
            with self.assertRaisesRegex(ValueError, "disagrees"):
                self.run_audit(original=source)

    def test_missing_and_duplicate_importer_flags_are_rejected(self):
        self.meta.write_text(f"fileFormatVersion: 2\nguid: {self.guid}\nTextureImporter:\n")
        with self.assertRaises(ValueError):
            self.run_audit()
        self.set_meta(1, "  sRGBTexture: 0\n")
        with self.assertRaises(ValueError):
            self.run_audit()

    def test_untrusted_mapping_guid_and_duplicate_source_rejected(self):
        self.map["textures"][0]["export_guid"] = "b" * 32
        with self.assertRaises(ValueError):
            self.run_audit()
        self.map["textures"][0]["export_guid"] = self.guid
        self.map["textures"].append(dict(self.map["textures"][0]))
        with self.assertRaises(ValueError):
            self.run_audit()

    def test_path_traversal_and_symlink_refused(self):
        self.map["textures"][0]["export_asset"] = "../outside.png"
        with self.assertRaises(ValueError):
            self.run_audit()
        self.map["textures"][0]["export_asset"] = "Textures/one.png"
        (self.assets / "one.png").unlink()
        (self.assets / "one.png").symlink_to(self.meta)
        with self.assertRaises(ValueError):
            self.run_audit()

    def test_never_repair_without_original_verification(self):
        with self.assertRaises(ValueError):
            self.run_audit(repair=True)
        self.assertIn("sRGBTexture: 0", self.meta.read_text())

    def test_original_bytes_and_path_id_control_reject_false_claims(self):
        source = self.root / "source"
        source.mkdir()
        (source / "source.assets").write_bytes(b"original")
        obj = types.SimpleNamespace(path_id=123, type=types.SimpleNamespace(name="Texture2D"),
                                    read_typetree=lambda: {"m_ColorSpace": 0})
        module = types.SimpleNamespace(load=lambda path: types.SimpleNamespace(objects=[obj]))
        with mock.patch.dict(sys.modules, {"UnityPy": module}):
            self.assertTrue(self.run_audit(original=source)["source_bytes_and_colorspace_verified"])
            self.map["textures"][0]["source_color_space"] = 1
            with self.assertRaises(ValueError):
                self.run_audit(original=source)
            self.map["textures"][0]["source_color_space"] = 0
            self.map["textures"][0]["source_owner_sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                self.run_audit(original=source)

    def test_source_authenticated_repair_keeps_guid_and_other_meta(self):
        source = self.root / "source"
        source.mkdir()
        (source / "source.assets").write_bytes(b"original")
        obj = types.SimpleNamespace(path_id=123, type=types.SimpleNamespace(name="Texture2D"),
                                    read_typetree=lambda: {"m_ColorSpace": 0})
        module = types.SimpleNamespace(load=lambda path: types.SimpleNamespace(objects=[obj]))
        with mock.patch.dict(sys.modules, {"UnityPy": module}):
            r = self.run_audit(original=source, repair=True)
        self.assertEqual((r["repaired"], r["mismatched_before"]), (1, 1))
        self.assertEqual(m._parse_importer(self.meta.read_text())[:2], (self.guid, 1))

    def test_output_aggregate_only(self):
        r = self.run_audit()
        blob = json.dumps(r)
        for secret in ("Textures/", self.guid, "source.assets", "one.png"):
            self.assertNotIn(secret, blob)


if __name__ == "__main__":
    main()
