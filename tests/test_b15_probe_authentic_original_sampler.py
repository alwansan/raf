"""B15 synthetic safety controls for authentic ZIP2 original sampler intake."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import sys
import unittest
from unittest import mock

from scripts import b15_probe_authentic_original_sampler as probe


class OriginalSamplerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / probe.OWNER
        self.data = b"synthetic-only-owner-not-game-content"
        self.path.write_bytes(self.data)
        self.pin = (len(self.data), hashlib.sha256(self.data).hexdigest())

    def obj(self, pid, *, bias=0.0, filt=1, wrap=0, aniso=1, typ="Texture2D"):
        def fields():
            return {"m_TextureSettings": {
                "m_FilterMode": filt, "m_Aniso": aniso, "m_MipBias": bias,
                "m_WrapU": wrap, "m_WrapV": wrap, "m_WrapW": wrap,
            }}
        return SimpleNamespace(path_id=pid, type=SimpleNamespace(name=typ), read_typetree=fields)

    def run_probe(self, objects=None, count=2):
        env = SimpleNamespace(objects=objects if objects is not None else [self.obj(7), self.obj(8)])
        with mock.patch.dict(sys.modules, {"UnityPy": SimpleNamespace(load=lambda _: env)}):
            return probe.inspect_original(self.path, expected_pin=self.pin, expected_textures=count)

    def test_typed_original_samplers_decoded_without_payload(self):
        r = self.run_probe()
        self.assertEqual(r["selected_original_texture_count"], 2)
        self.assertEqual(r["filter_enum_slots_checked"], 2)
        self.assertEqual(r["wrap_enum_slots_checked"], 6)
        self.assertTrue(r["selected_original_owner_sha256_verified"])
        self.assertFalse(r["same_export_identity_verified"])
        self.assertFalse(r["exported_importer_compared"])
        self.assertFalse(r["unity_or_android_pixels_verified"])
        self.assertFalse(r["full_original_game_coverage"])
        self.assertNotIn("synthetic", json.dumps(r))
        self.assertNotIn("7", json.dumps(r))

    def test_original_same_size_byte_tamper_is_rejected(self):
        self.path.write_bytes(self.data[::-1])
        with self.assertRaisesRegex(ValueError, "SHA256"):
            self.run_probe()

    def test_wrong_expected_texture_count_rejected(self):
        with self.assertRaisesRegex(ValueError, "count differed"):
            self.run_probe(count=3)

    def test_nonzero_mip_bias_fail_closed_against_w2_original_baseline(self):
        with self.assertRaisesRegex(ValueError, "mip bias"):
            self.run_probe(objects=[self.obj(7, bias=0.5), self.obj(8)])

    def test_sampler_enum_drift_rejected_not_silently_clamped(self):
        with self.assertRaisesRegex(ValueError, "sampler enum"):
            self.run_probe(objects=[self.obj(7, filt=99), self.obj(8)])

    def test_duplicate_and_invalid_pathids_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity"):
            self.run_probe(objects=[self.obj(7), self.obj(7)])
        with self.assertRaisesRegex(ValueError, "identity"):
            self.run_probe(objects=[self.obj(True), self.obj(8)])

    def test_non_texture_objects_do_not_inflate_count(self):
        r = self.run_probe(objects=[self.obj(7), self.obj(8), self.obj(10, typ="Material")])
        self.assertEqual(r["selected_original_texture_count"], 2)

    def test_linked_source_owner_path_rejected(self):
        real = self.root / "real-original.assets"
        real.write_bytes(self.data)
        self.path.unlink()
        self.path.symlink_to(real)
        with self.assertRaisesRegex(ValueError, "redirected"):
            self.run_probe()


if __name__ == "__main__":
    unittest.main()
