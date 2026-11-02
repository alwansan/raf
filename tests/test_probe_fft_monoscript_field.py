"""Synthetic name SHA to original managed field identity, no Raft source."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from scripts.probe_fft_monoscript_field import inspect


class OriginalMonoScriptFieldTests(unittest.TestCase):
    def test_resolves_only_name_sha_and_redacts_all_class_field_names(self):
        code = 'namespace Custom.Water { public class WaterBridge { public UnityEngine.ComputeShader originalFFT; private int x; } }'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "WaterBridge.cs"
            path.write_text(code)
            expected = hashlib.sha256(b"Custom.Water.WaterBridge").hexdigest()
            result = inspect(Path(tmp), expected)
            self.assertTrue(result["original_managed_type_matched"])
            self.assertEqual(result["matches"][0]["original_field_type_compute_shader_declarations"], 1)
            self.assertNotIn("WaterBridge", str(result))
            self.assertNotIn("originalFFT", str(result))
            self.assertFalse(result["serialized_compute_field_offset_verified"])

    def test_mismatch_is_not_fabricated(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "Missing.cs").write_text("class Missing {}")
            self.assertFalse(inspect(Path(tmp), "0" * 64)["original_managed_type_matched"])


if __name__ == "__main__":
    unittest.main()
