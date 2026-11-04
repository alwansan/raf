"""B15 source/export texture sampler audit: synthetic ONLY, no Raft payload."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest import mock

from scripts import b15_texture_sampler_parity as audit


class SamplerFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "original"
        self.assets = self.root / "project" / "Assets"
        self.source.mkdir()
        self.assets.mkdir(parents=True)
        self.owner = "synthetic.assets"
        self.raw = b"synthetic-only-not-raft"
        (self.source / self.owner).write_bytes(self.raw)
        self.digest = hashlib.sha256(self.raw).hexdigest()
        self.guid = "abcdef0123456789abcdef0123456789"
        self.settings = {
            "m_FilterMode": 2, "m_Aniso": 4, "m_MipBias": 0.25,
            "m_WrapU": 1, "m_WrapV": 2, "m_WrapW": 0,
        }
        self.asset = self.assets / "image.png"
        self.asset.write_bytes(b"exported-fixture")
        self.write_meta()
        self.sidecar = {
            "schema_version": 1, "source_commit": audit.ZIP2_COMMIT,
            "export_instance": "1" * 32,
            "textures": [{
                "source_owner": self.owner, "source_path_id": 17,
                "source_bytes": len(self.raw), "source_sha256": self.digest,
                "export_asset": "image.png", "export_guid": self.guid
            }]
        }
        self.obj = SimpleNamespace(
            path_id=17, type=SimpleNamespace(name="Texture2D"),
            read_typetree=lambda: {"m_TextureSettings": self.settings}
        )

    def write_meta(self, **overrides):
        out = {
            "filterMode": 2, "aniso": 4, "mipBias": 0.25,
            "wrapU": 1, "wrapV": 2, "wrapW": 0,
        }
        out.update(overrides)
        fields = "\n".join("    " + k + ": " + str(v) for k,v in out.items())
        (self.assets / "image.png.meta").write_text(
            "fileFormatVersion: 2\nguid: " + self.guid +
            "\nTextureImporter:\n  textureSettings:\n" + fields + "\n",
            encoding="utf-8"
        )

    def run_audit(self):
        module = SimpleNamespace(load=lambda _: SimpleNamespace(objects=[self.obj]))
        with mock.patch.dict(audit.SOURCE_PINS, {self.owner: (len(self.raw), self.digest)}), \
             mock.patch.dict(sys.modules, {"UnityPy": module}):
            return audit.inspect(self.source, self.assets.parent, self.sidecar)

    def test_exact_sampler_preserved_structurally(self):
        result = self.run_audit()
        self.assertTrue(result["metadata_fields_faithful"])
        self.assertEqual(result["linked_textures_compared"], 1)
        self.assertEqual(result["source_owners_authenticated"], 1)
        self.assertFalse(result["same_export_provenance_independently_verified"])
        self.assertFalse(result["unity_or_android_pixels_verified"])
        self.assertFalse(result["modified_assets"])
        self.assertNotIn(self.owner, json.dumps(result))
        self.assertNotIn(self.guid, json.dumps(result))

    def test_wrap_filter_aniso_and_bias_drift_each_reported(self):
        self.write_meta(filterMode=1, aniso=6, mipBias=0.5, wrapU=2, wrapV=1, wrapW=3)
        result = self.run_audit()
        self.assertFalse(result["metadata_fields_faithful"])
        self.assertEqual(result["field_mismatches"], {field: 1 for field, _ in audit.FIELDS})

    def test_sentinel_is_unknown_not_equivalent(self):
        self.write_meta(filterMode=-1, wrapU=-1)
        result = self.run_audit()
        self.assertEqual(result["unresolved_importer_defaults"]["m_FilterMode"], 1)
        self.assertEqual(result["unresolved_importer_defaults"]["m_WrapU"], 1)
        self.assertFalse(result["metadata_fields_faithful"])
        self.assertEqual(sum(result["field_mismatches"].values()), 0)

    def test_unset_minus_100_mip_bias_is_unknown_not_proven_drift(self):
        self.write_meta(mipBias=-100.0)
        report = self.run_audit()
        self.assertEqual(report["unresolved_importer_defaults"]["m_MipBias"], 1)
        self.assertEqual(report["field_mismatches"]["m_MipBias"], 0)
        self.assertFalse(report["metadata_fields_faithful"])
        self.assertFalse(report["same_export_provenance_independently_verified"])

    def test_non_sentinel_negative_mip_bias_remains_drift(self):
        self.write_meta(mipBias=-0.5)
        report = self.run_audit()
        self.assertEqual(report["unresolved_importer_defaults"]["m_MipBias"], 0)
        self.assertEqual(report["field_mismatches"]["m_MipBias"], 1)

    def test_w1_companion_matching_instance_with_real_trace_schema(self):
        texture = self.make_trace()
        companion = {
            "schema_version": 1, "export_instance": texture["export_instance"],
            "objects": [
                {"class_id": 21, "source": {"owner": self.owner, "path_id": 41},
                 "exportable": True, "collection_type": "synthetic Material"},
                {"class_id": 48, "source": {"owner": self.owner, "path_id": 42},
                 "exportable": True, "collection_type": "synthetic Shader"},
            ],
        }
        audit.validate_export_pair(texture, companion)
        self.assertEqual(self.generate_from_trace(texture)["export_instance"], companion["export_instance"])

    def test_w1_companion_different_export_instance_fails_closed(self):
        texture = self.make_trace()
        companion = {
            "schema_version": 1, "export_instance": "2" * 32,
            "objects": [{"class_id": 21, "source": {"owner": self.owner, "path_id": 41}}],
        }
        with self.assertRaisesRegex(ValueError, "different export instances"):
            audit.validate_export_pair(texture, companion)
        companion["export_instance"] = texture["export_instance"]
        companion["objects"][0]["class_id"] = 28
        with self.assertRaisesRegex(ValueError, "non-W1"):
            audit.validate_export_pair(texture, companion)
        companion["objects"][0]["class_id"] = 21
        companion["objects"][0]["source"]["path_id"] = True
        with self.assertRaisesRegex(ValueError, "malformed W1"):
            audit.validate_export_pair(texture, companion)

    def test_w1_companion_bad_schema_or_missing_objects_fails_closed(self):
        texture = self.make_trace()
        companion = {"schema_version": 0, "export_instance": texture["export_instance"], "objects": []}
        with self.assertRaisesRegex(ValueError, "schemas"):
            audit.validate_export_pair(texture, companion)
        companion["schema_version"] = 1
        with self.assertRaisesRegex(ValueError, "missing W1"):
            audit.validate_export_pair(texture, companion)

    def test_private_trace_file_symlink_refused(self):
        target = self.root / "trace.json"
        target.write_text(json.dumps(self.make_trace()), encoding="utf-8")
        linked = self.root / "linked.json"
        linked.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "linked"):
            audit.read_private_trace(linked)
        self.assertEqual(audit.read_private_trace(target)["schema_version"], 1)

    def test_source_bytes_tampering_rejected(self):
        (self.source / self.owner).write_bytes(self.raw[::-1])
        with self.assertRaisesRegex(ValueError, "SHA256"):
            self.run_audit()

    def test_source_pin_tampering_rejected(self):
        self.sidecar["textures"][0]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "pinned"):
            self.run_audit()

    def test_wrong_source_commit_or_instance_rejected(self):
        self.sidecar["source_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "sidecar"):
            self.run_audit()
        self.sidecar["source_commit"] = audit.ZIP2_COMMIT
        self.sidecar["export_instance"] = "unknown"
        with self.assertRaisesRegex(ValueError, "sidecar"):
            self.run_audit()

    def test_forged_export_identity_rejected(self):
        self.sidecar["textures"][0]["export_guid"] = "e" * 32
        with self.assertRaisesRegex(ValueError, "GUID"):
            self.run_audit()

    def test_symlinked_meta_rejected(self):
        meta = self.assets / "image.png.meta"
        meta.unlink()
        outside = self.root / "outside.meta"
        outside.write_text("not a real importer")
        meta.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "linked"):
            self.run_audit()

    def test_path_escape_and_duplicated_identity_rejected(self):
        self.sidecar["textures"][0]["export_asset"] = "../escape.png"
        with self.assertRaisesRegex(ValueError, "unsafe"):
            self.run_audit()
        self.sidecar["textures"][0]["export_asset"] = "image.png"
        self.sidecar["textures"].append(self.sidecar["textures"][0].copy())
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.run_audit()

    def test_missing_duplicate_and_nonfinite_fields_rejected(self):
        meta = self.assets / "image.png.meta"
        data = meta.read_text()
        meta.write_text(data.replace("    wrapV: 2\n", ""))
        with self.assertRaisesRegex(ValueError, "absent"):
            self.run_audit()
        meta.write_text(data + "  textureSettings:\n    wrapV: 2\n")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.run_audit()
        self.write_meta(mipBias=".nan")
        with self.assertRaisesRegex(ValueError, "non-finite"):
            self.run_audit()

    def test_non_texture_and_missing_path_id_rejected(self):
        self.obj.type.name = "Material"
        with self.assertRaisesRegex(ValueError, "Texture2D"):
            self.run_audit()
        self.obj.type.name = "Texture2D"
        self.obj.path_id = 99
        with self.assertRaisesRegex(ValueError, "missing original"):
            self.run_audit()

    def test_no_private_sampler_values_in_stdout_result(self):
        self.write_meta(wrapU=0)
        result = self.run_audit()
        self.assertNotIn("0.25", json.dumps(result))
        self.assertNotIn("synthetic.assets", json.dumps(result))


    def make_trace(self):
        return {
            "schema_version": 1, "export_instance": "1" * 32,
            "objects": [{
                "class_id": 28,
                "source": {"owner": "Raft_Data/" + self.owner, "path_id": 17},
                "export": {"file_id": 2800000, "guid": self.guid, "type": 3},
            }]
        }

    def generate_from_trace(self, trace=None):
        with mock.patch.dict(audit.SOURCE_PINS, {self.owner: (len(self.raw), self.digest)}):
            return audit.sidecar_from_export_trace(self.assets.parent, trace or self.make_trace())

    def test_exact_same_export_trace_maps_guid_to_file(self):
        sidecar = self.generate_from_trace()
        self.assertEqual(sidecar["textures"], self.sidecar["textures"])
        self.assertEqual(sidecar["export_instance"], self.sidecar["export_instance"])
        with mock.patch.dict(audit.SOURCE_PINS, {self.owner: (len(self.raw), self.digest)}), \
             mock.patch.dict(sys.modules, {"UnityPy": SimpleNamespace(
                 load=lambda _: SimpleNamespace(objects=[self.obj]))}):
            result = audit.inspect(self.source, self.assets.parent, sidecar)
        self.assertTrue(result["metadata_fields_faithful"])
        self.assertFalse(result["same_export_provenance_independently_verified"])

    def test_trace_wrong_target_or_unsupported_pptr_rejected(self):
        trace = self.make_trace()
        trace["objects"][0]["export"]["guid"] = "c" * 32
        with self.assertRaisesRegex(ValueError, "missing exact"):
            self.generate_from_trace(trace)
        trace = self.make_trace()
        trace["objects"][0]["export"]["type"] = 99
        with self.assertRaisesRegex(ValueError, "PPtr"):
            self.generate_from_trace(trace)

    def test_trace_duplicate_source_and_export_rejected(self):
        trace = self.make_trace()
        trace["objects"].append(trace["objects"][0].copy())
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            with mock.patch.dict(audit.SOURCE_PINS, {self.owner: (len(self.raw), self.digest)}):
                audit.check_rows(audit.sidecar_from_export_trace(self.assets.parent, trace))

    def test_trace_unsafe_source_and_wrong_export_meta_rejected(self):
        trace = self.make_trace()
        trace["objects"][0]["source"]["owner"] = "../" + self.owner
        with self.assertRaisesRegex(ValueError, "unsafe trace"):
            self.generate_from_trace(trace)
        trace = self.make_trace()
        meta = self.assets / "image.png.meta"
        meta.write_text("fileFormatVersion: 2\nguid: " + self.guid + "\nDefaultImporter: {}\n")
        with self.assertRaisesRegex(ValueError, "TextureImporter"):
            self.generate_from_trace(trace)



if __name__ == "__main__":
    unittest.main()
