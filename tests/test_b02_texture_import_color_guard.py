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
            f"fileFormatVersion: 2\nguid: {self.guid}\nTextureImporter:\n"
            f"  mipmaps:\n    sRGBTexture: {srgb}\n"
            "  textureSettings:\n    filterMode: 2\n    aniso: 2\n    mipBias: 0.0\n"
            "    wrapU: 0\n    wrapV: 0\n    wrapW: 0\n" + extra,
            encoding="utf-8",
        )

    def run_audit(self, **kw):
        return m.inspect(self.root / "export", self.map, **kw)

    def test_opposing_policies_reported_without_repair(self):
        r = self.run_audit()
        self.assertEqual((r["rows"], r["assetripper_pinned_policy_matches"],
                          r["gamma_semantic_hypothesis_mismatches"]), (1, 1, 1))
        self.assertFalse(r["semantic_policy_verified_for_original"])
        self.assertFalse(r["same_export_linkage_independently_verified"])
        self.assertFalse(r["repair_available"])
        self.assertIn("    sRGBTexture: 0", self.meta.read_text())

    def test_pinned_assetripper_linear_true_gamma_false_baseline(self):
        self.set_meta(1)
        self.assertEqual(self.run_audit()["assetripper_pinned_policy_mismatches"], 1)
        self.assertEqual(self.run_audit()["gamma_semantic_hypothesis_matches"], 1)
        self.map["textures"][0]["source_color_space"] = 1
        self.set_meta(1)
        self.assertEqual(self.run_audit()["assetripper_pinned_policy_matches"], 1)
        self.set_meta(0)
        self.assertEqual(self.run_audit()["gamma_semantic_hypothesis_matches"], 1)

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
            with self.assertRaisesRegex(ValueError, "invalid original"):
                self.run_audit(original=source)

    def test_missing_and_duplicate_importer_flags_are_rejected(self):
        self.meta.write_text(f"fileFormatVersion: 2\nguid: {self.guid}\nTextureImporter:\n")
        with self.assertRaises(ValueError):
            self.run_audit()
        self.set_meta(1, "  mipmaps: {}\n")
        with self.assertRaises(ValueError):
            self.run_audit()

    def test_top_level_srgb_is_not_authentic_nested_mipmaps(self):
        self.meta.write_text(
            f"fileFormatVersion: 2\nguid: {self.guid}\nTextureImporter:\n  sRGBTexture: 1\n",
            encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "top-level"):
            self.run_audit()

    def test_nested_srgb_boolean_and_alias_rejected(self):
        self.set_meta("true")
        with self.assertRaisesRegex(ValueError, "mipmaps.sRGBTexture"):
            self.run_audit()
        self.set_meta(0, "  mipmaps: {}\n")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.run_audit()

    def test_reuse_b15_trace_reads_original_color_from_verified_bytes(self):
        source = self.root / "source"
        source.mkdir()
        (source / "source.assets").write_bytes(b"original")
        obj = types.SimpleNamespace(path_id=123, type=types.SimpleNamespace(name="Texture2D"),
                                    read_typetree=lambda: {"m_ColorSpace": 1})
        module = types.SimpleNamespace(load=lambda path: types.SimpleNamespace(objects=[obj]))
        trace = {
            "schema_version": 1, "export_instance": "b" * 32,
            "objects": [{
                "class_id": 28,
                "source": {"owner": "Raft_Data/source.assets", "path_id": 123},
                "export": {"file_id": 2800000, "guid": self.guid, "type": 3},
            }],
        }
        with mock.patch.dict(sys.modules, {"UnityPy": module}):
            derived = m.map_from_export_trace(self.root / "export", source, trace)
            self.assertEqual(derived["textures"][0]["source_color_space"], 1)
            report = m.inspect(self.root / "export", derived, source)
        self.assertEqual(report["assetripper_pinned_policy_mismatches"], 1)
        self.assertFalse(report["same_export_linkage_independently_verified"])
        self.assertFalse(report["semantic_policy_verified_for_original"])
        self.assertFalse(report["repair_available"])
        self.assertIn("    sRGBTexture: 0", self.meta.read_text())
        trace["objects"][0]["source"]["owner"] = "forged/source.assets"
        with self.assertRaisesRegex(ValueError, "collection path"):
            m.map_from_export_trace(self.root / "export", source, trace)

    def test_trace_bad_guid_cannot_be_guessed_by_filename(self):
        source = self.root / "source"
        source.mkdir()
        (source / "source.assets").write_bytes(b"original")
        trace = {
            "schema_version": 1, "export_instance": "b" * 32,
            "objects": [{
                "class_id": 28,
                "source": {"owner": "Raft_Data/source.assets", "path_id": 123},
                "export": {"file_id": 2800000, "guid": "c" * 32, "type": 3},
            }],
        }
        with self.assertRaisesRegex(ValueError, "missing exact"):
            m.map_from_export_trace(self.root / "export", source, trace)

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

    def test_even_authenticated_fixture_cannot_repair_unproven_semantics(self):
        source = self.root / "source"
        source.mkdir()
        (source / "source.assets").write_bytes(b"original")
        obj = types.SimpleNamespace(path_id=123, type=types.SimpleNamespace(name="Texture2D"),
                                    read_typetree=lambda: {"m_ColorSpace": 0})
        module = types.SimpleNamespace(load=lambda path: types.SimpleNamespace(objects=[obj]))
        before = self.meta.read_bytes()
        with mock.patch.dict(sys.modules, {"UnityPy": module}):
            with self.assertRaisesRegex(ValueError, "disabled"):
                self.run_audit(original=source, repair=True)
        self.assertEqual(self.meta.read_bytes(), before)

    def test_strict_cannot_prove_same_export_lineage_or_color_semantics(self):
        r = self.run_audit()
        self.assertFalse(r["same_export_linkage_independently_verified"])
        self.assertFalse(r["semantic_policy_verified_for_original"])
        self.assertEqual(r["repaired"], 0)

    def test_output_aggregate_only(self):
        r = self.run_audit()
        blob = json.dumps(r)
        for secret in ("Textures/", self.guid, "source.assets", "one.png"):
            self.assertNotIn(secret, blob)


if __name__ == "__main__":
    main()
