"""GFX138 source-free coverage regressions; no original game binary included."""
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from gfxlab.tools.gfx138_warp_cross_pass import audit, SIZE, FORWARD, DEFERRED


class WarpCrossPassTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.forward = self.root / "forward"
        self.deferred = self.root / "deferred"
        self.forward.mkdir()
        self.deferred.mkdir()
        self.source = self.root / "forward-safe.json"
        self.mesa = self.root / "mesa-safe.json"
        self.mask = bytes([255] * 2008 + [0] * (SIZE * SIZE - 2008))
        self.raw = self.encode(self.mask)
        for name in FORWARD:
            (self.forward / (name + ".rgba")).write_bytes(self.raw)
        for name in DEFERRED:
            (self.deferred / (name + ".rgba")).write_bytes(self.raw)
        self.source.write_text(json.dumps({
            "experiment": "GFX121", "source_dxbc_draw_completed": True,
            "captures": {name: {"coverage_sha256": sha256(self.mask).hexdigest(),
                                "covered_pixels": 2008} for name in FORWARD},
        }))
        self.mesa.write_text(json.dumps({
            "covered_pixels": 2008,
            "deferred": {"same_coverage_as_forward": True, "covered_pixels": 2008},
        }))

    @staticmethod
    def encode(mask):
        return b"".join(bytes((6, 9, 12, alpha)) for alpha in mask)

    def run_audit(self):
        return audit(self.forward, self.deferred, self.source, self.mesa)

    def test_exact_all_passes_and_controls(self):
        result = self.run_audit()
        self.assertEqual(result["covered_pixels"], 2008)
        self.assertEqual(len(result["cases_checked"]), 7)
        self.assertTrue(result["original_dxbc_forward_deferred_mask_exact"])
        self.assertFalse(result["phase_closed"])

    def test_deferred_same_count_different_pixels_rejected(self):
        path = self.deferred / "native-rt0.rgba"
        mask = bytearray(self.mask)
        mask[0], mask[2008] = 0, 255
        path.write_bytes(self.encode(mask))
        with self.assertRaisesRegex(ValueError, "pixel-location"):
            self.run_audit()

    def test_deferred_flat_mask_change_rejected(self):
        mask = bytearray(self.mask)
        mask[1], mask[3000] = 0, 255
        (self.deferred / "flat-rt0.rgba").write_bytes(self.encode(mask))
        with self.assertRaisesRegex(ValueError, "pixel-location"):
            self.run_audit()

    def test_forward_dark_mask_change_rejected(self):
        mask = bytearray(self.mask)
        mask[0], mask[3000] = 0, 255
        (self.forward / "dark.rgba").write_bytes(self.encode(mask))
        with self.assertRaisesRegex(ValueError, "reference changed"):
            self.run_audit()

    def test_missing_capture_rejected(self):
        (self.forward / "flat.rgba").unlink()
        with self.assertRaises(FileNotFoundError):
            self.run_audit()

    def test_wrong_length_rejected(self):
        (self.deferred / "native-rt0.rgba").write_bytes(self.raw[:-4])
        with self.assertRaisesRegex(ValueError, "length"):
            self.run_audit()

    def test_fractional_alpha_rejected(self):
        data = bytearray(self.raw)
        data[3] = 128
        (self.deferred / "native-rt0.rgba").write_bytes(data)
        with self.assertRaisesRegex(ValueError, "Nonbinary"):
            self.run_audit()

    def test_wrong_source_capture_hash_rejected(self):
        source = json.loads(self.source.read_text())
        source["captures"]["light"]["coverage_sha256"] = "0" * 64
        self.source.write_text(json.dumps(source))
        with self.assertRaisesRegex(ValueError, "reference changed"):
            self.run_audit()

    def test_wrong_mesa_count_rejected(self):
        mesa = json.loads(self.mesa.read_text())
        mesa["deferred"]["covered_pixels"] = 2007
        self.mesa.write_text(json.dumps(mesa))
        with self.assertRaisesRegex(ValueError, "count drift"):
            self.run_audit()

    def test_untrusted_reference_identity_rejected(self):
        source = json.loads(self.source.read_text())
        source["experiment"] = "GFX000"
        self.source.write_text(json.dumps(source))
        with self.assertRaisesRegex(ValueError, "Wrong original"):
            self.run_audit()
